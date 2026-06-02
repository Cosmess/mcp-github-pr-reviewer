import pytest

from mcp_github_pr_reviewer.config import Settings
from mcp_github_pr_reviewer.security.policies import (
    RepositoryNotAllowedError,
    WriteActionDisabledError,
    WriteActionNotConfirmedError,
    assert_repository_allowed,
    assert_write_action_allowed,
    truncate_patch,
)


def test_repository_allowlist_allows_configured_repository() -> None:
    settings = Settings(
        GITHUB_TOKEN="",
        ALLOWED_REPOSITORIES="Cosmess/mcp-github-pr-reviewer",
    )

    assert_repository_allowed("Cosmess", "mcp-github-pr-reviewer", settings)


def test_repository_allowlist_blocks_unknown_repository() -> None:
    settings = Settings(
        GITHUB_TOKEN="",
        ALLOWED_REPOSITORIES="Cosmess/mcp-github-pr-reviewer",
    )

    with pytest.raises(RepositoryNotAllowedError):
        assert_repository_allowed("Cosmess", "private-repo", settings)


def test_empty_repository_allowlist_allows_any_repository() -> None:
    settings = Settings(GITHUB_TOKEN="", ALLOWED_REPOSITORIES="")

    assert_repository_allowed("any", "repo", settings)


def test_truncate_patch_keeps_small_patch() -> None:
    assert truncate_patch("abc", 10) == "abc"


def test_truncate_patch_truncates_large_patch() -> None:
    result = truncate_patch("abcdef", 3)

    assert result.startswith("abc")
    assert "patch truncated" in result


def test_write_action_requires_enabled_setting() -> None:
    settings = Settings(ENABLE_GITHUB_WRITE_ACTIONS=False)

    with pytest.raises(WriteActionDisabledError):
        assert_write_action_allowed(settings, confirm=True)


def test_write_action_requires_confirmation() -> None:
    settings = Settings(ENABLE_GITHUB_WRITE_ACTIONS=True)

    with pytest.raises(WriteActionNotConfirmedError):
        assert_write_action_allowed(settings, confirm=False)


def test_write_action_allows_enabled_and_confirmed_request() -> None:
    settings = Settings(ENABLE_GITHUB_WRITE_ACTIONS=True)

    assert_write_action_allowed(settings, confirm=True)
