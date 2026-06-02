# Usage

## Install locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## Configure environment

Copy `.env.example` to `.env` and set:

```txt
GITHUB_TOKEN=ghp_replace_with_a_readonly_token
ALLOWED_REPOSITORIES=Cosmess/mcp-github-pr-reviewer
```

## Run tests

```bash
python -m pytest
```

## Run the MCP server

```bash
mcp-github-pr-reviewer
```

## Run with Docker Compose

```bash
docker compose build
docker compose run --rm mcp-github-pr-reviewer
```

## Configure an MCP client

See:

- `examples/claude-desktop-config.json`
- `examples/cursor-config.json`
- `examples/codex-config.md`

## Example prompt

```txt
Analise o PR #42 do repositório Cosmess/minha-api.

Quero:
1. Resumo técnico.
2. Arquivos mais importantes.
3. Possíveis riscos.
4. Sugestões de testes unitários.
5. Comentário final em Markdown para publicar no GitHub.
```
