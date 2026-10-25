# Tasks: stock-outbound-operations (Change 04)

1. [x] Criar especificação OpenSpec (proposal, design, spec, tasks)
2. [x] Criar tabela `stock_outbound` no Xano
3. [x] Implementar endpoints XanoScript (create/list/detail/status/process)
4. [x] Expandir `services/xano_client.py` com funções de outbound autenticadas
5. [x] Adicionar seção "Saídas de Estoque" no Streamlit (`app.py`)
6. [x] Criar testes automatizados (cliente + contrato XanoScript)
7. [x] Atualizar `docs/domain-model.md`
8. [x] Executar validações, E2E live, revisar diff e registrar resultados

## Resultados dos testes

### Automatizados

- Suíte completa: **210 passed, 107 subtests passed**.
- `tests/test_outbound_client.py`: payloads, validações, `auth_token` e endpoints.
- `tests/test_outbound_contract.py`: rotas, `auth = "user"`, identidade via `$auth.id`, status inicial, idempotência, transação, RBAC e filtros de período.
- `python -m py_compile app.py services/xano_client.py tests/test_outbound_client.py tests/test_outbound_contract.py`: OK.
- AppTest da página “Saídas de Estoque” com sessão admin real: 3 abas carregadas, sem exceções e sem erros de backend; produto inicial com saldo selecionado automaticamente.
- `openspec validate stock-outbound-operations --strict`: **valid**.

### Integração ao vivo (Xano — workspace 154752)

- Publicação via Xano CLI (`xano workspace push`) de 1 tabela e 4 endpoints:
  - `POST /outbound`
  - `GET /outbound` (lista e detalhe via `?id=`)
  - `PATCH /outbound/status`
  - `POST /outbound/process`
- `GET /outbound` sem token: **401**; com token: **200**.
- Criação de `SALE`: **200**, status inicial `Pendente`, `user_id` derivado de `$auth.id`.
- Duplicidade de `idempotency_key`: **400**, sem segunda operação.
- Processamento de venda: **200**, `stock_movement` do tipo `exit`, saldo decrementado, operação `Concluida` e `stock_movement_id` preenchido.
- `LOSS` com justificativa: **200**, status `AguardandoAprovacao`.
- Vendedor tentando processar `LOSS`: **403**; admin aprovando/processando: **200**, `approved_by` preenchido e baixa efetivada.
- Rejeição por admin: **200**, sem movimentação de estoque; tentativa de processar rejeitada: **400**.
- Cancelamento pelo solicitante: **200**, sem movimentação de estoque.
- Saldo insuficiente: **400**, sem movimentação, sem alteração de saldo e operação preservada.
- `PATCH` direto para `Concluida`: **400**; conclusão somente por `/outbound/process`.
- Filtro de período com `from_date`/`to_date`: **200**; período futuro retorna lista vazia.

### Dados E2E

- Produto 3 (`CON-ACUV-03`): estoque **25 → 23**.
- Operações E2E: 2 `Concluida`, 1 `Rejeitada`, 3 `Cancelada` (6 registros).
- A operação pendente do primeiro teste (id 1) foi cancelada; nenhum dado E2E foi removido.

### Decisões técnicas

- Todas as rotas exigem `auth = "user"`; a identidade é sempre `$auth.id`.
- Status inicial é decidido no backend; o cliente não envia `status` na criação.
- `Concluida` só é alcançada por `POST /outbound/process`; `PATCH` aceita apenas `AguardandoAprovacao`, `Rejeitada` e `Cancelada`.
- `LOSS` exige gestor em qualquer estado processável, inclusive retry; `AguardandoAprovacao` também exige gestor.
- Perfis de gestão: `Gestor` e `admin`. O usuário `gerente@smartvision.com` live ainda está como `member`; o E2E de aprovação usou `e2e-admin@smartvision.com` (`admin`). A normalização de perfis pertence à Change 07.
- Processamento usa `db.transaction` com auditoria antes do saldo, relê o produto e bloqueia saldo negativo.
- `idempotency_key` vazia é normalizada para `null`; índice único e guarda por `stock_movement_id` protegem contra duplicidade.
- Filtros opcionais no Xano exigem `tipo? nome?`; `int? id` é nullable obrigatório. `from_date`/`to_date` usam `timestamp?` e comparações null-safe.
- A UI de saídas não mantém estado local nem simula baixa; consome o backend com token e exibe apenas o resultado retornado.
- Erros de permissão usam `error_type = "accessdenied"` (HTTP 403); `"forbidden"` não é aceito pelo Xano.
