# mcp-github-pr-reviewer

MCP Server em Python para análise read-only de Pull Requests no GitHub.

O projeto permite que um agente conectado via Model Context Protocol consulte
PRs, leia arquivos alterados, identifique riscos e gere uma revisão técnica em
Markdown sem conceder acesso direto do agente ao GitHub.

## Por que existe

Revisões de PR exigem contexto, atenção a risco e bons testes. Este servidor
organiza os dados do GitHub e entrega uma análise inicial consistente para apoiar
o engenheiro durante a revisão.

O MVP é determinístico e não depende de LLM. Uma integração com LLM pode ser
adicionada depois sem acoplar o provedor às tools MCP.

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

## Arquitetura

```txt
MCP Client -> FastMCP Server -> GitHub Service -> GitHub REST API
                              -> Diff Analyzer -> Markdown Review
```

Veja [docs/architecture.md](docs/architecture.md).

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

## Docker

```bash
docker compose build
docker compose run --rm mcp-github-pr-reviewer
```

## Exemplos

- [Claude Desktop](examples/claude-desktop-config.json)
- [Cursor](examples/cursor-config.json)
- [Codex](examples/codex-config.md)
- [Sample PR analysis](examples/sample-pr-analysis.md)

## Segurança

- O MVP é somente leitura.
- Repositórios podem ser restringidos por allowlist.
- Patches grandes são truncados por `MAX_PATCH_CHARS`.
- Secrets não devem ser enviados em logs ou respostas.
- Ações de escrita, como comentar no PR, não fazem parte do MVP.

Veja [docs/security.md](docs/security.md).

## Documentação

- [Usage](docs/usage.md)
- [Architecture](docs/architecture.md)
- [Security](docs/security.md)
- [Roadmap](docs/roadmap.md)
