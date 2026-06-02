from mcp.server.fastmcp import FastMCP

from mcp_github_pr_reviewer.config import get_settings
from mcp_github_pr_reviewer.services.diff_analyzer import DiffAnalyzer
from mcp_github_pr_reviewer.services.github_service import GitHubService

mcp = FastMCP("mcp-github-pr-reviewer")


def _github_service() -> GitHubService:
    return GitHubService(get_settings())


def _diff_analyzer() -> DiffAnalyzer:
    return DiffAnalyzer()


@mcp.tool()
async def list_open_pull_requests(owner: str, repo: str, limit: int = 10) -> list[dict]:
    """List open pull requests for an allowed GitHub repository."""
    pull_requests = await _github_service().list_open_pull_requests(owner, repo, limit)
    return [pull_request.model_dump() for pull_request in pull_requests]


@mcp.tool()
async def get_pull_request_summary(owner: str, repo: str, pull_number: int) -> dict:
    """Return metadata for a specific pull request."""
    pull_request = await _github_service().get_pull_request(owner, repo, pull_number)
    return pull_request.model_dump()


@mcp.tool()
async def get_pull_request_files(owner: str, repo: str, pull_number: int) -> list[dict]:
    """Return changed files for a specific pull request."""
    files = await _github_service().get_pull_request_files(owner, repo, pull_number)
    return [file.model_dump(exclude={"patch"}) for file in files]


@mcp.tool()
async def get_pull_request_diff(owner: str, repo: str, pull_number: int) -> list[dict]:
    """Return changed files including patches for a specific pull request."""
    files = await _github_service().get_pull_request_files(owner, repo, pull_number)
    return [file.model_dump() for file in files]


@mcp.tool()
async def analyze_pull_request(owner: str, repo: str, pull_number: int) -> dict:
    """Analyze a pull request and return summary, risks, tests and review Markdown."""
    service = _github_service()
    pull_request = await service.get_pull_request(owner, repo, pull_number)
    files = await service.get_pull_request_files(owner, repo, pull_number)
    analysis = _diff_analyzer().analyze(pull_request, files)
    return analysis.model_dump()


@mcp.tool()
async def suggest_unit_tests(owner: str, repo: str, pull_number: int) -> list[str]:
    """Suggest tests for a specific pull request."""
    service = _github_service()
    pull_request = await service.get_pull_request(owner, repo, pull_number)
    files = await service.get_pull_request_files(owner, repo, pull_number)
    return _diff_analyzer().analyze(pull_request, files).suggested_tests


@mcp.tool()
async def generate_markdown_review(owner: str, repo: str, pull_number: int) -> str:
    """Generate a Markdown review for a specific pull request."""
    service = _github_service()
    pull_request = await service.get_pull_request(owner, repo, pull_number)
    files = await service.get_pull_request_files(owner, repo, pull_number)
    return _diff_analyzer().analyze(pull_request, files).markdown_review


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
