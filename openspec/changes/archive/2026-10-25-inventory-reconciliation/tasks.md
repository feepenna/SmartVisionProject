# Tasks: inventory-reconciliation (Change 03)

1. [x] Criar especificação OpenSpec (proposal, design, spec, tasks)
2. [x] Implementar tabelas Xano: inventory, inventory_count, inventory_discrepancy, inventory_decision
3. [x] Implementar endpoints XanoScript: inventários, contagens, conciliação, divergências, decisão do gestor, aplicação de ajuste
4. [x] Expandir services/xano_client.py com funções de inventário
5. [x] Implementar telas Streamlit em app.py (listagem, criação, contagem, divergências, aprovação, histórico)
6. [x] Criar testes automatizados (cliente, regras de negócio, concorrência, idempotência)
7. [x] Executar testes e verificar build
8. [x] Atualizar docs/domain-model.md com as novas entidades
9. [x] Revisar diff (duplicações, regressões, escopo)
10. [x] Registrar resultados dos testes e decisões técnicas

## Resultados dos testes

### Automatizados

- `pytest`: **164 passed, 62 subtests passed**.
- `tests/test_inventory_client.py`: valida payloads e envio de `Authorization: Bearer`.
- `tests/test_inventory_contract.py`: rotas, sintaxe XanoScript, `auth = "user"`, identidade via `$auth.id`, inputs opcionais (`nome?`), addons de progresso.
- `tests/test_inventory_rules.py`: classificação de divergências, transições, separação de funções, idempotência e concorrência.

### Integração ao vivo (Xano)

- Sem token: `GET /inventories` → **401**; com token válido → **200**.
- Criação, transição `Aberto → EmContagem`, contagem, conciliação e listagem de divergências: **200**.
- Tentativas de falsificar `opened_by` e `counted_by`: **403**.
- `member`/vendedor tentando aprovar, aplicar ou concluir: **403**.
- Gestor/admin aprovando, aplicando e concluindo: **200**.
- Aplicação de ajuste: saldo atualizado, `stock_movement` de ajuste criado (`adjustment_movement_id` preenchido).
- Segunda aplicação: `applied = 0`, `already_applied = 1`, saldo inalterado (idempotência).
- Conclusão bloqueada com divergência pendente e com ajuste aprovado não aplicado.
- Recontagem: histórico preservado (`is_recount = true`, `previous_count_id`), divergência recalculada e ajuste aplicado.
- Separação de funções: contador não aprova a própria divergência (**403**).
- Rejeição não gera movimentação e não altera o saldo; inventário pode ser concluído.
- Inventário concluído não aceita nova contagem nem reabertura (**400**).
- Listagem retorna `counts_recorded` e `products_in_scope` via addons; detalhe retorna `progress_percent`.

### Decisões técnicas

- `auth = "user"` em todos os endpoints; identidade sempre por `$auth.id`. Inputs de identidade são opcionais e, se enviados, precisam coincidir com o usuário autenticado.
- Erros de permissão usam `error_type = "accessdenied"` (HTTP 403); `"forbidden"` não é aceito pelo Xano.
- Inputs opcionais usam `tipo? nome?`; `tipo? nome` é obrigatório e nullable.
- Aprovação, aplicação e conclusão exigem Gestor/admin; abertura, contagem e conciliação permitem qualquer usuário autenticado.
- Aplicação de ajustes usa `db.transaction` (auditoria + saldo + marcação da divergência).
- A listagem usa addons `inventory_counts` e `inventory_scope` (um `db.query` cada) para atender ao requisito de progresso.
- O fluxo E2E de gestor usou um usuário de teste dedicado promovido via endpoint existente de conta, sem alterar os usuários demo.
