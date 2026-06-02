# Segurança

## Modelo De Segurança

O modo padrão é focado em leitura. O servidor pode ler metadados de Pull
Requests, arquivos alterados e patches. A tool de comentário existe, mas roda
com `dry_run=true` por padrão, e ações de escrita no GitHub ficam desabilitadas
até serem explicitamente habilitadas.

## Token GitHub

Use um token com as menores permissões possíveis.

Recomendado para uso somente leitura:

- Fine-grained token.
- Acesso de leitura apenas aos repositórios selecionados.
- Sem acesso amplo à organização, exceto quando necessário.
- Sem permissões de escrita.

Para publicar comentários reais em PRs, o token também precisa de permissão para
escrever comentários em issues/PRs.

Nunca commite `.env` ou tokens reais.

## Allowlist De Repositórios

Use `ALLOWED_REPOSITORIES` para restringir acesso:

```txt
ALLOWED_REPOSITORIES=Cosmess/mcp-github-pr-reviewer,Cosmess/another-repo
```

Quando a allowlist está vazia, o servidor aceita qualquer repositório visível ao
token GitHub configurado.

Para demos de portfólio, mantenha a allowlist habilitada.

## Limites De Patch

Patches grandes podem consumir contexto demais e deixar a revisão ruidosa. O
servidor usa `MAX_PATCH_CHARS` para truncar patches antes de retorná-los.

```txt
MAX_PATCH_CHARS=120000
```

O analisador LLM opcional tem um limite próprio, menor:

```txt
LLM_MAX_PATCH_CHARS=40000
```

## Privacidade Do LLM Opcional

O analisador LLM opcional pode enviar metadados do PR e contexto de patch para o
provedor OpenAI-compatible configurado. Mantenha essa opção desabilitada em
repositórios privados, a menos que a equipe aprove explicitamente o envio desse
código para o provedor.

Controles recomendados:

- Manter `LLM_ANALYZER_ENABLED=false` por padrão.
- Usar `LLM_MAX_PATCH_CHARS` para limitar o tamanho do contexto.
- Não enviar secrets, credenciais ou diffs privados para provedores não aprovados.
- Preferir provedores locais para repositórios sensíveis.

## Dry-Run De Comentário

`comment_on_pull_request` é seguro por padrão:

```json
{
  "owner": "Cosmess",
  "repo": "mcp-github-pr-reviewer",
  "pull_number": 42,
  "body": "## Resumo técnico...",
  "dry_run": true,
  "confirm": false
}
```

Com `dry_run=true`, o servidor não chama o endpoint de escrita do GitHub. Ele
apenas retorna o alvo e o corpo do comentário que seria publicado.

Para publicar um comentário real, todas as condições abaixo precisam ser
verdadeiras:

- `ENABLE_GITHUB_WRITE_ACTIONS=true`
- `dry_run=false`
- `confirm=true`

## Respostas De Erro

As tools retornam erros estruturados em vez de stack traces:

```json
{
  "ok": false,
  "error": {
    "code": "write_action_disabled",
    "message": "GitHub write actions are disabled."
  }
}
```

## Checklist Operacional

- Manter `.env` fora do Git.
- Usar token GitHub somente leitura no uso normal.
- Configurar `ALLOWED_REPOSITORIES`.
- Não registrar secrets em logs.
- Revisar o Markdown gerado antes de publicar.
- Não enviar diffs privados para LLM externo sem aprovação.
