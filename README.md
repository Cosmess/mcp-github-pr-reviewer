# mcp-github-pr-reviewer

MCP Server em Python para análise read-only de Pull Requests no GitHub.

O servidor expõe tools MCP para listar PRs, buscar metadados, ler arquivos
alterados, analisar riscos e gerar uma revisão técnica em Markdown.

## Tools

```txt
list_open_pull_requests
get_pull_request_summary
get_pull_request_files
get_pull_request_diff
analyze_pull_request
suggest_unit_tests
generate_markdown_review
```

## Requisitos

- Python 3.12+
- Token GitHub com permissão mínima de leitura

## Configuração

Copie `.env.example` para `.env` e configure:

```txt
GITHUB_TOKEN=ghp_replace_with_a_readonly_token
ALLOWED_REPOSITORIES=Cosmess/mcp-github-pr-reviewer
```

`ALLOWED_REPOSITORIES` é opcional. Quando preenchido, apenas os repositórios
listados podem ser consultados.

## Desenvolvimento

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest
ruff check .
```

## Execução

```bash
mcp-github-pr-reviewer
```

## Segurança

- O MVP é somente leitura.
- Repositórios podem ser restringidos por allowlist.
- Patches grandes são truncados por `MAX_PATCH_CHARS`.
- Secrets não devem ser enviados em logs ou respostas.
- Ações de escrita, como comentar no PR, não fazem parte do MVP.
