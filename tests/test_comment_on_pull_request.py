import asyncio

from mcp_github_pr_reviewer.config import Settings
from mcp_github_pr_reviewer.services.github_service import GitHubService


def test_comment_on_pull_request_dry_run_does_not_require_write_enabled() -> None:
    service = GitHubService(Settings(ENABLE_GITHUB_WRITE_ACTIONS=False))

    result = asyncio.run(
        service.comment_on_pull_request(
            owner="Cosmess",
            repo="mcp-github-pr-reviewer",
            pull_number=1,
            body="Review body",
            dry_run=True,
            confirm=False,
        )
    )

    assert result == {
        "dry_run": True,
        "would_comment": True,
        "target": "Cosmess/mcp-github-pr-reviewer#1",
        "body": "Review body",
    }
