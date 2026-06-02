from mcp_github_pr_reviewer.config import Settings


class RepositoryNotAllowedError(ValueError):
    """Raised when a repository is outside the configured allowlist."""


class WriteActionDisabledError(ValueError):
    """Raised when a GitHub write action is attempted while writes are disabled."""


class WriteActionNotConfirmedError(ValueError):
    """Raised when a GitHub write action is attempted without explicit confirmation."""


def assert_repository_allowed(owner: str, repo: str, settings: Settings) -> None:
    allowlist = settings.repository_allowlist
    if not allowlist:
        return

    full_name = f"{owner}/{repo}".lower()
    if full_name not in allowlist:
        raise RepositoryNotAllowedError(
            f"Repository '{owner}/{repo}' is not in ALLOWED_REPOSITORIES."
        )


def assert_write_action_allowed(settings: Settings, confirm: bool) -> None:
    if not settings.enable_github_write_actions:
        raise WriteActionDisabledError(
            "GitHub write actions are disabled. Set ENABLE_GITHUB_WRITE_ACTIONS=true."
        )

    if not confirm:
        raise WriteActionNotConfirmedError(
            "GitHub write actions require confirm=true."
        )


def truncate_patch(patch: str, max_chars: int) -> str:
    if len(patch) <= max_chars:
        return patch

    return patch[:max_chars] + "\n\n[patch truncated by MAX_PATCH_CHARS]"
