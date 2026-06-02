from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx

from mcp_github_pr_reviewer.config import Settings
from mcp_github_pr_reviewer.models import ChangedFile, PullRequest
from mcp_github_pr_reviewer.security.policies import assert_repository_allowed, truncate_patch


class GitHubServiceError(RuntimeError):
    """Raised when GitHub returns an unexpected response."""


class GitHubService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

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
        data = await self._get_json(
            f"/repos/{owner}/{repo}/pulls/{pull_number}/files",
            params={"per_page": 100},
        )
        return [self._map_changed_file(item) for item in data]

    async def _get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        async with self._client() as client:
            response = await client.get(path, params=params)

        if response.status_code >= 400:
            raise GitHubServiceError(
                f"GitHub API returned {response.status_code}: {response.text[:500]}"
            )

        return response.json()

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
