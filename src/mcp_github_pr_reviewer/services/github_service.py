from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx

from mcp_github_pr_reviewer.config import Settings
from mcp_github_pr_reviewer.models import ChangedFile, GitHubRateLimit, PullRequest
from mcp_github_pr_reviewer.security.policies import (
    assert_repository_allowed,
    assert_write_action_allowed,
    truncate_patch,
)


class GitHubServiceError(RuntimeError):
    """Raised when GitHub returns an unexpected response."""


class GitHubAPIError(GitHubServiceError):
    def __init__(self, status_code: int, message: str, rate_limit: GitHubRateLimit | None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.rate_limit = rate_limit


class GitHubService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.last_rate_limit: GitHubRateLimit | None = None

    @asynccontextmanager
    async def _client(self) -> AsyncIterator[httpx.AsyncClient]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "mcp-github-pr-reviewer",
        }
        if self._settings.github_token:
            headers["Authorization"] = f"Bearer {self._settings.github_token}"

        async with httpx.AsyncClient(
            base_url=str(self._settings.github_api_base_url).rstrip("/"),
            headers=headers,
            timeout=self._settings.github_timeout_seconds,
        ) as client:
            yield client

    async def list_open_pull_requests(
        self, owner: str, repo: str, limit: int = 10
    ) -> list[PullRequest]:
        assert_repository_allowed(owner, repo, self._settings)
        safe_limit = min(max(limit, 1), 50)

        data = await self._get_json(
            f"/repos/{owner}/{repo}/pulls",
            params={"state": "open", "per_page": safe_limit},
        )
        return [self._map_pull_request(item) for item in data]

    async def get_pull_request(self, owner: str, repo: str, pull_number: int) -> PullRequest:
        assert_repository_allowed(owner, repo, self._settings)
        data = await self._get_json(f"/repos/{owner}/{repo}/pulls/{pull_number}")
        return self._map_pull_request(data)

    async def get_pull_request_files(
        self, owner: str, repo: str, pull_number: int
    ) -> list[ChangedFile]:
        assert_repository_allowed(owner, repo, self._settings)
        data = await self._get_paginated_json(
            f"/repos/{owner}/{repo}/pulls/{pull_number}/files",
            params={"per_page": 100},
        )
        return [self._map_changed_file(item) for item in data]

    async def comment_on_pull_request(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        body: str,
        dry_run: bool = True,
        confirm: bool = False,
    ) -> dict[str, Any]:
        assert_repository_allowed(owner, repo, self._settings)
        target = f"{owner}/{repo}#{pull_number}"

        if dry_run:
            return {
                "dry_run": True,
                "would_comment": True,
                "target": target,
                "body": body,
            }

        assert_write_action_allowed(self._settings, confirm)
        data = await self._post_json(
            f"/repos/{owner}/{repo}/issues/{pull_number}/comments",
            json={"body": body},
        )
        return {
            "dry_run": False,
            "commented": True,
            "target": target,
            "comment_url": data.get("html_url"),
        }

    async def _get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        async with self._client() as client:
            response = await client.get(path, params=params)

        self.last_rate_limit = self._rate_limit_from_response(response)
        if response.status_code >= 400:
            raise GitHubAPIError(
                response.status_code,
                f"GitHub API returned {response.status_code}: {response.text[:500]}",
                self.last_rate_limit,
            )

        return response.json()

    async def _post_json(self, path: str, json: dict[str, Any]) -> Any:
        async with self._client() as client:
            response = await client.post(path, json=json)

        self.last_rate_limit = self._rate_limit_from_response(response)
        if response.status_code >= 400:
            raise GitHubAPIError(
                response.status_code,
                f"GitHub API returned {response.status_code}: {response.text[:500]}",
                self.last_rate_limit,
            )

        return response.json()

    async def _get_paginated_json(
        self, path: str, params: dict[str, Any] | None = None, max_pages: int = 10
    ) -> list[Any]:
        items: list[Any] = []
        next_path: str | None = path
        next_params = params
        pages_read = 0

        async with self._client() as client:
            while next_path and pages_read < max_pages:
                response = await client.get(next_path, params=next_params)
                self.last_rate_limit = self._rate_limit_from_response(response)
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        response.status_code,
                        f"GitHub API returned {response.status_code}: {response.text[:500]}",
                        self.last_rate_limit,
                    )

                payload = response.json()
                if not isinstance(payload, list):
                    raise GitHubServiceError("Expected a list response from GitHub API.")

                items.extend(payload)
                next_path = self._next_page_path(response)
                next_params = None
                pages_read += 1

        return items

    def _next_page_path(self, response: httpx.Response) -> str | None:
        next_url = response.links.get("next", {}).get("url")
        if not next_url:
            return None

        parsed = httpx.URL(next_url)
        path = parsed.path
        query = parsed.query.decode("utf-8")
        return path + (f"?{query}" if query else "")

    def _rate_limit_from_response(self, response: httpx.Response) -> GitHubRateLimit:
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        return GitHubRateLimit(
            remaining=int(remaining) if remaining and remaining.isdigit() else None,
            reset_epoch=int(reset) if reset and reset.isdigit() else None,
        )

    def _map_pull_request(self, data: dict[str, Any]) -> PullRequest:
        return PullRequest(
            number=data["number"],
            title=data.get("title") or "",
            state=data.get("state") or "",
            author=(data.get("user") or {}).get("login") or "",
            url=data.get("html_url") or "",
            body=data.get("body") or "",
            base_branch=(data.get("base") or {}).get("ref") or "",
            head_branch=(data.get("head") or {}).get("ref") or "",
            changed_files=data.get("changed_files") or 0,
            additions=data.get("additions") or 0,
            deletions=data.get("deletions") or 0,
        )

    def _map_changed_file(self, data: dict[str, Any]) -> ChangedFile:
        patch = truncate_patch(data.get("patch") or "", self._settings.max_patch_chars)
        return ChangedFile(
            filename=data.get("filename") or "",
            status=data.get("status") or "",
            additions=data.get("additions") or 0,
            deletions=data.get("deletions") or 0,
            changes=data.get("changes") or 0,
            patch=patch,
        )
