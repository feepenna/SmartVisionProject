# Design: stock-outbound-operations (Change 04)

## Context

A Change 02 consolidou o ledger imutável `stock_movement` e a operação de baixa com bloqueio de saldo negativo. A Change 04 adiciona o ciclo de vida formal da saída (`stock_outbound`) sem criar um ledger paralelo: o processamento da saída gera uma movimentação `exit` no ledger existente.

O backend Xano é a autoridade de autenticação, autorização, status, idempotência e auditoria. O Streamlit apenas consome a API e apresenta o estado retornado.

## Goals

- Registrar saídas `SALE`, `LAB_SHIPMENT`, `LOSS` e `OPERATIONAL` com referências operacionais opcionais.
- Controlar aprovação de perdas e operações que exigem gestor.
- Efetivar a baixa de forma atômica, idempotente e auditável.
- Oferecer consulta filtrada e histórico por usuário, produto, tipo, status e período.
- Integrar a seção de saídas ao Streamlit com autenticação real.

## Non-Goals

- ERP/PDV completo.
- Um segundo ledger de estoque.
- Retorno automático de laboratório.
- Normalização dos perfis dos usuários demo (Change 07).

## 1. Persistência

### Tabela `stock_outbound`

- `id` (int, PK)
- `created_at` (timestamp, default `now`)
- `type` (text): `SALE`, `LAB_SHIPMENT`, `LOSS`, `OPERATIONAL`
- `status` (text): `Pendente`, `AguardandoAprovacao`, `Concluida`, `Rejeitada`, `Cancelada`, `FalhaNoProcessamento`
- `product_id` (int, FK lógica para `product`)
- `quantity` (int, > 0)
- `user_id` (int, solicitante derivado de `$auth.id`)
- `approved_by` (int?, gestor que aprovou/rejeitou)
- `approved_at` (timestamp?)
- `reason` (text, obrigatório)
- `justification` (text?, obrigatório para `LOSS`)
- `reference_type` (text?): `SALE`, `ORDER`, `OS`, etc.
- `reference_id` (text?)
- `destination` (text?)
- `notes` (text?)
- `stock_movement_id` (int?, vínculo com o ledger)
- `processed_at` (timestamp?)
- `failure_reason` (text?)
- `idempotency_key` (text?, índice único)

Índices: `type`, `status`, `product_id`, `user_id`, `created_at` (desc) e índice único em `idempotency_key`.

## 2. Autenticação e autorização

- Todos os endpoints usam `auth = "user"`.
- A identidade é sempre `$auth.id`; não existe `user_id` de identidade no payload de processamento/status.
- Perfis de gestão: `Gestor` ou `admin`.
- `POST /outbound`: qualquer usuário autenticado; o solicitante é `$auth.id`.
- `GET /outbound`: qualquer usuário autenticado.
- `PATCH /outbound/status`: solicitante ou gestor para solicitar aprovação/cancelar; somente gestor para rejeitar.
- `POST /outbound/process`: solicitante ou gestor para `Pendente`/`FalhaNoProcessamento`; somente gestor para `AguardandoAprovacao` e para qualquer `LOSS`.

## 3. Status e transições

Status inicial definido pelo backend:

- `LOSS` → `AguardandoAprovacao`
- `SALE`, `LAB_SHIPMENT`, `OPERATIONAL` → `Pendente`

Transições permitidas:

- `Pendente` → `AguardandoAprovacao` por `PATCH` (solicitante ou gestor)
- `Pendente` → `Cancelada` por `PATCH` (solicitante ou gestor)
- `AguardandoAprovacao` → `Rejeitada` por `PATCH` (somente gestor)
- `AguardandoAprovacao` → `Cancelada` por `PATCH` (solicitante ou gestor)
- `Pendente`/`AguardandoAprovacao` → `Concluida` somente por `POST /outbound/process`
- `FalhaNoProcessamento` → `Concluida` por `POST /outbound/process` (retry; `LOSS` exige gestor)

`Concluida`, `Rejeitada` e `Cancelada` são finais. `FalhaNoProcessamento` é um estado de retry reservado; o fluxo normal não o produz nesta change.

## 4. Endpoints

- `POST /outbound` — cria a operação, valida tipo/produto/quantidade/motivo/justificativa e define o status inicial.
- `GET /outbound` — lista com filtros opcionais `type`, `status`, `product_id`, `user_id`, `from_date` e `to_date`; com `id`, retorna o detalhe e HTTP 404 se não existir.
- `PATCH /outbound/status` — solicita aprovação, rejeita ou cancela; nunca conclui nem movimenta estoque.
- `POST /outbound/process` — efetiva a baixa e conclui a operação.

As rotas aninhadas são `outbound/process` e `outbound/status`; o detalhe usa `GET /outbound?id=<id>`.

## 5. Processamento transacional

`POST /outbound/process` executa dentro de `db.transaction`:

1. Relê a operação e valida o estado, o tipo e a permissão.
2. Exige `stock_movement_id == null`.
3. Relê o produto e exige `current_stock >= quantity`.
4. Cria `stock_movement` com `movement_type = "exit"`, `previous_stock`, `new_stock`, quantidade, motivo, justificativa, operador e `reference_text = "outbound:<id>"`.
5. Atualiza `current_stock`.
6. Marca a operação como `Concluida`, grava `stock_movement_id` e `processed_at`.
7. Se o status anterior era `AguardandoAprovacao`, grava `approved_by` e `approved_at`.

Qualquer falha reverte a transação. O saldo nunca fica negativo.

## 6. Idempotência e concorrência

- `idempotency_key` vazio é normalizado para `null`; chaves não vazias são únicas.
- Repetir a criação com a mesma chave retorna HTTP 400.
- O processamento exige `stock_movement_id` nulo; uma segunda tentativa retorna HTTP 400.
- O saldo é relido dentro da transação, evitando duas baixas concorrentes sobre o mesmo saldo.
- O vínculo `stock_movement_id` é a prova de que a operação já gerou movimentação.

## 7. Consulta e filtros

- `from_date` e `to_date` são timestamps em milissegundos e usam comparação null-safe (`>=?`, `<=?`).
- Todos os filtros são opcionais; a ausência de filtros retorna a listagem completa.
- A ordenação é `created_at` decrescente.
- O detalhe é retornado quando `id` é informado; operação inexistente retorna HTTP 404.

## 8. Frontend Streamlit

A seção de saídas usa o cliente autenticado e não mantém estado local de outbounds:

- Registro por tipo, com justificativa condicional para `LOSS`.
- Histórico com filtros e detalhes retornados pelo backend.
- Central de aprovação para `AguardandoAprovacao` e `Pendente`, com botões exibidos somente para `Gestor`/`admin`.
- Mensagens de sucesso/erro são exibidas após o rerun com `st.session_state`.
- Nenhuma baixa é simulada localmente; erros do backend são exibidos ao usuário.

## 9. Testes e evidências

- Contrato XanoScript: autenticação, rotas, transação, idempotência, RBAC, status e filtros.
- Cliente Python: payloads, `auth_token`, validações e endpoints.
- Suíte completa: `210 passed + 107 subtests` (validada após os ajustes finais).
- E2E live: venda, duplicidade de idempotência, perda com aprovação admin, rejeição, cancelamento, saldo insuficiente e filtros de período.
- Dados E2E: produto 3 passou de 25 para 23; operação pendente do primeiro teste foi cancelada; ficaram 2 `Concluida`, 1 `Rejeitada` e 3 `Cancelada`.
