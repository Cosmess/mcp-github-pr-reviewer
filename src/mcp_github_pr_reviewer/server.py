from mcp.server.fastmcp import FastMCP

from mcp_github_pr_reviewer.config import get_settings
from mcp_github_pr_reviewer.models import ErrorDetail, ToolResponse
from mcp_github_pr_reviewer.security.policies import (
    RepositoryNotAllowedError,
    WriteActionDisabledError,
    WriteActionNotConfirmedError,
)
from mcp_github_pr_reviewer.services.diff_analyzer import DiffAnalyzer
from mcp_github_pr_reviewer.services.github_service import GitHubAPIError, GitHubService
from mcp_github_pr_reviewer.services.llm_service import LLMAnalyzerService, LLMServiceError

mcp = FastMCP("mcp-github-pr-reviewer")


def _github_service() -> GitHubService:
    return GitHubService(get_settings())


def _diff_analyzer() -> DiffAnalyzer:
    return DiffAnalyzer()


def _llm_analyzer() -> LLMAnalyzerService:
    return LLMAnalyzerService(get_settings())


def _ok(
    data: object,
    service: GitHubService | None = None,
    warnings: list[str] | None = None,
) -> dict:
    return ToolResponse(
        ok=True,
        data=data,
        rate_limit=service.last_rate_limit if service else None,
        warnings=warnings or [],
    ).model_dump()


def _error(code: str, message: str, service: GitHubService | None = None) -> dict:
    return ToolResponse(
        ok=False,
        error=ErrorDetail(code=code, message=message),
        rate_limit=service.last_rate_limit if service else None,
    ).model_dump()


def _rate_limit_warnings(service: GitHubService) -> list[str]:
    rate_limit = service.last_rate_limit
    if rate_limit and rate_limit.remaining is not None and rate_limit.remaining <= 10:
        return ["GitHub API rate limit is low."]
    return []


def _handle_error(error: Exception, service: GitHubService | None = None) -> dict:
    if isinstance(error, RepositoryNotAllowedError):
        return _error("repository_not_allowed", str(error), service)
    if isinstance(error, WriteActionDisabledError):
        return _error("write_action_disabled", str(error), service)
    if isinstance(error, WriteActionNotConfirmedError):
        return _error("write_action_not_confirmed", str(error), service)
    if isinstance(error, GitHubAPIError):
        return _error("github_api_error", str(error), service)
    if isinstance(error, LLMServiceError):
        return _error("llm_api_error", str(error), service)
    return _error("internal_error", str(error), service)


@mcp.tool()
async def list_open_pull_requests(owner: str, repo: str, limit: int = 10) -> dict:
    """List open pull requests for an allowed GitHub repository."""
    service = _github_service()
    try:
        pull_requests = await service.list_open_pull_requests(owner, repo, limit)
        data = [pull_request.model_dump() for pull_request in pull_requests]
        return _ok(data, service, _rate_limit_warnings(service))
    except Exception as error:
        return _handle_error(error, service)


@mcp.tool()
async def get_pull_request_summary(owner: str, repo: str, pull_number: int) -> dict:
    """Return metadata for a specific pull request."""
    service = _github_service()
    try:
        pull_request = await service.get_pull_request(owner, repo, pull_number)
        return _ok(pull_request.model_dump(), service, _rate_limit_warnings(service))
    except Exception as error:
        return _handle_error(error, service)


@mcp.tool()
async def get_pull_request_files(owner: str, repo: str, pull_number: int) -> dict:
    """Return changed files for a specific pull request."""
    service = _github_service()
    try:
        files = await service.get_pull_request_files(owner, repo, pull_number)
        data = [file.model_dump(exclude={"patch"}) for file in files]
        return _ok(data, service, _rate_limit_warnings(service))
    except Exception as error:
        return _handle_error(error, service)


@mcp.tool()
async def get_pull_request_diff(owner: str, repo: str, pull_number: int) -> dict:
    """Return changed files including patches for a specific pull request."""
    service = _github_service()
    try:
        files = await service.get_pull_request_files(owner, repo, pull_number)
        return _ok([file.model_dump() for file in files], service, _rate_limit_warnings(service))
    except Exception as error:
        return _handle_error(error, service)


@mcp.tool()
async def analyze_pull_request(owner: str, repo: str, pull_number: int) -> dict:
    """Analyze a pull request and return summary, risks, tests and review Markdown."""
    service = _github_service()
    try:
        pull_request = await service.get_pull_request(owner, repo, pull_number)
        files = await service.get_pull_request_files(owner, repo, pull_number)
        analysis = _diff_analyzer().analyze(pull_request, files)
        analysis = await _llm_analyzer().enhance_review(pull_request, files, analysis)
        return _ok(analysis.model_dump(), service, _rate_limit_warnings(service))
    except Exception as error:
        return _handle_error(error, service)


@mcp.tool()
async def suggest_unit_tests(owner: str, repo: str, pull_number: int) -> dict:
    """Suggest tests for a specific pull request."""
    service = _github_service()
    try:
        pull_request = await service.get_pull_request(owner, repo, pull_number)
        files = await service.get_pull_request_files(owner, repo, pull_number)
        data = _diff_analyzer().analyze(pull_request, files).suggested_tests
        return _ok(data, service, _rate_limit_warnings(service))
    except Exception as error:
        return _handle_error(error, service)


@mcp.tool()
async def generate_markdown_review(owner: str, repo: str, pull_number: int) -> dict:
    """Generate a Markdown review for a specific pull request."""
    service = _github_service()
    try:
        pull_request = await service.get_pull_request(owner, repo, pull_number)
        files = await service.get_pull_request_files(owner, repo, pull_number)
        analysis = _diff_analyzer().analyze(pull_request, files)
        analysis = await _llm_analyzer().enhance_review(pull_request, files, analysis)
        data = analysis.markdown_review
        return _ok(data, service, _rate_limit_warnings(service))
    except Exception as error:
        return _handle_error(error, service)


@mcp.tool()
async def comment_on_pull_request(
    owner: str,
    repo: str,
    pull_number: int,
    body: str,
    dry_run: bool = True,
    confirm: bool = False,
) -> dict:
    """Comment on a pull request, using dry-run by default for safety."""
    service = _github_service()
    try:
        data = await service.comment_on_pull_request(
            owner=owner,
            repo=repo,
            pull_number=pull_number,
            body=body,
            dry_run=dry_run,
            confirm=confirm,
        )
        return _ok(data, service, _rate_limit_warnings(service))
    except Exception as error:
        return _handle_error(error, service)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
