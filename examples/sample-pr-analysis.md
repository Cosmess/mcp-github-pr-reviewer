## Resumo técnico

PR #42 altera 4 arquivo(s), com 180 adição(ões) e 45 remoção(ões). Título:
Update settlement flow

## Arquivos principais

- src/payments/settlement_service.py
- src/payments/reconciliation_handler.py
- migrations/202606021200_add_settlement_status.sql

## Riscos encontrados

- Mudanças em schema/migrations podem exigir validação de rollback e dados.
- Mudanças em fluxo financeiro podem impactar conciliação ou liquidação.
- Nenhum arquivo de teste foi alterado no PR.

## Testes sugeridos

- Executar a suíte automatizada relacionada aos módulos alterados.
- Adicionar testes unitários para regras de negócio e cenários de borda.
- Validar migration em base local e cenário de rollback.
- Cobrir cenários financeiros de sucesso, falha, duplicidade e divergência.
