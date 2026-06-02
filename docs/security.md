# Security

## Security model

The MVP is read-only. It can read pull request metadata, changed files and
patches, but it cannot write comments, approve PRs, request changes, merge code
or modify repository settings.

## GitHub token

Use a token with the minimum permissions needed to read pull requests.

Recommended:

- Fine-grained token.
- Read-only access to selected repositories.
- No organization-wide access unless required.
- No write permissions for the MVP.

Never commit `.env` or real tokens.

## Repository allowlist

Use `ALLOWED_REPOSITORIES` to restrict access:

```txt
ALLOWED_REPOSITORIES=Cosmess/mcp-github-pr-reviewer,Cosmess/another-repo
```

When the allowlist is empty, the server accepts any repository visible to the
configured GitHub token.

For portfolio demos, keep the allowlist enabled.

## Patch limits

Large patches can consume too much context and make reviews noisy. The server
uses `MAX_PATCH_CHARS` to truncate file patches before returning them.

```txt
MAX_PATCH_CHARS=120000
```

## Error responses

Tools should return structured error responses instead of exposing raw stack
traces. GitHub API messages are truncated before being surfaced.

## Future write actions

If comment-on-PR support is added later, it should require:

- Separate GitHub token permission.
- `dry-run` by default.
- Explicit tool argument such as `confirm=true`.
- Clear audit logging.
- Tests proving comments are not posted accidentally.

## Operational checklist

- Keep `.env` out of Git.
- Use a read-only GitHub token.
- Configure `ALLOWED_REPOSITORIES`.
- Keep logs free of secrets.
- Review generated Markdown before posting it manually.
- Avoid sending private diffs to external LLM providers unless approved.
