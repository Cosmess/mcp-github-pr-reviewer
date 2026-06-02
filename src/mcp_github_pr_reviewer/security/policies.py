from mcp_github_pr_reviewer.config import Settings


class RepositoryNotAllowedError(ValueError):
    """Raised when a repository is outside the configured allowlist."""


def assert_repository_allowed(owner: str, repo: str, settings: Settings) -> None:
    allowlist = settings.repository_allowlist
    if not allowlist:
        return

    full_name = f"{owner}/{repo}".lower()
    if full_name not in allowlist:
        raise RepositoryNotAllowedError(
            f"Repository '{owner}/{repo}' is not in ALLOWED_REPOSITORIES."
        )


def truncate_patch(patch: str, max_chars: int) -> str:
    if len(patch) <= max_chars:
        return patch

    return patch[:max_chars] + "\n\n[patch truncated by MAX_PATCH_CHARS]"
