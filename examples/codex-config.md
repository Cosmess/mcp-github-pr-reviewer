# Codex MCP configuration example

Use este servidor como um MCP local apontando para o comando instalado:

```json
{
  "mcpServers": {
    "github-pr-reviewer": {
      "command": "mcp-github-pr-reviewer",
      "env": {
        "GITHUB_TOKEN": "ghp_replace_with_a_readonly_token",
        "ALLOWED_REPOSITORIES": "Cosmess/mcp-github-pr-reviewer",
        "LLM_ANALYZER_ENABLED": "false",
        "ENABLE_GITHUB_WRITE_ACTIONS": "false"
      }
    }
  }
}
```

Prompt de teste:

```txt
Analise o PR #1 do repositório Cosmess/mcp-github-pr-reviewer.

Quero resumo técnico, arquivos principais, riscos e testes sugeridos.
```
