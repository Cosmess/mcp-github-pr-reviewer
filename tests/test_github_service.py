import httpx

from mcp_github_pr_reviewer.config import Settings
from mcp_github_pr_reviewer.services.github_service import GitHubService


def test_rate_limit_from_response() -> None:
    service = GitHubService(Settings(GITHUB_TOKEN=""))
    response = httpx.Response(
        200,
        headers={
            "X-RateLimit-Remaining": "42",
            "X-RateLimit-Reset": "1780425600",
        },
    )

    rate_limit = service._rate_limit_from_response(response)

    assert rate_limit.remaining == 42
    assert rate_limit.reset_epoch == 1780425600


def test_next_page_path_from_link_header() -> None:
    service = GitHubService(Settings(GITHUB_TOKEN=""))
    response = httpx.Response(
        200,
        headers={
            "Link": (
                '<https://api.github.com/repos/Cosmess/example/pulls/1/files?page=2>; rel="next"'
            )
        },
    )

    assert service._next_page_path(response) == "/repos/Cosmess/example/pulls/1/files?page=2"
