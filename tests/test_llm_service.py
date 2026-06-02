import asyncio

from mcp_github_pr_reviewer.config import Settings
from mcp_github_pr_reviewer.models import ChangedFile, PullRequest
from mcp_github_pr_reviewer.services.diff_analyzer import DiffAnalyzer
from mcp_github_pr_reviewer.services.llm_service import LLMAnalyzerService


def test_llm_analyzer_is_disabled_without_api_key() -> None:
    service = LLMAnalyzerService(Settings(LLM_ANALYZER_ENABLED=True, LLM_API_KEY=""))

    assert service.enabled is False


def test_disabled_llm_returns_baseline_analysis() -> None:
    settings = Settings(LLM_ANALYZER_ENABLED=False, LLM_API_KEY="")
    service = LLMAnalyzerService(settings)
    pull_request = PullRequest(
        number=1,
        title="Update docs",
        state="open",
        author="cosme",
        url="https://github.com/Cosmess/example/pull/1",
        base_branch="main",
        head_branch="docs",
    )
    files = [ChangedFile(filename="README.md", status="modified", changes=5)]
    baseline = DiffAnalyzer().analyze(pull_request, files)

    result = asyncio.run(service.enhance_review(pull_request, files, baseline))

    assert result == baseline


def test_extract_content_from_openai_compatible_payload() -> None:
    service = LLMAnalyzerService(Settings(LLM_API_KEY="token", LLM_ANALYZER_ENABLED=True))

    content = service._extract_content(
        {"choices": [{"message": {"content": "## Review\n\nLooks good."}}]}
    )

    assert content == "## Review\n\nLooks good."
