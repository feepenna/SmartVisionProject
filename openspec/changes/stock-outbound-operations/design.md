# Design: stock-outbound-operations (Change 04)

## Arquitetura

Reutiliza o mecanismo de movimentação existente (Change 02): o processamento efetivo da baixa ocorre chamando/replicando a lógica válida de `stock_exit` que já grava em `stock_movement` com auditoria prévia e bloqueio de saldo negativo.

## 1. Tabela de persistência

### `stock_outbound`
- `id` (int, PK)
- `created_at` (timestamp, now)
- `type` (text): `SALE` | `LAB_SHIPMENT` | `LOSS` | `OPERATIONAL`
- `status` (text): `Pendente` | `AguardandoAprovacao` | `Concluida` | `Rejeitada` | `Cancelada` | `FalhaNoProcessamento`
- `product_id` (int, FK → product)
- `quantity` (int, > 0)
- `user_id` (int, responsável)
- `approved_by` (int?, gestor que aprovou/rejeitou)
- `approved_at` (timestamp?)
- `reason` (text, motivo da saída)
- `justification` (text?, obrigatório para LOSS)
- `reference_type` (text?, SALE/ORDER/OS)
- `reference_id` (text?, ID da referência)
- `destination` (text?, laboratório/destino p/ LAB_SHIPMENT)
- `notes` (text?)
- `stock_movement_id` (int?, FK → stock_movement)
- `processed_at` (timestamp?)
- `failure_reason` (text?)
- `idempotency_key` (text?, para evitar duplicados)

## 2. Estados e transições

- `Pendente` → `AguardandoAprovacao` (quando exige aprovação: LOSS geralmente; configurável por política)
- `Pendente` → `Concluida` (via process, se permitido)
- `AguardandoAprovacao` → `Concluida` (após aprovação por gestor)
- `AguardandoAprovacao` → `Rejeitada` (rejeição por gestor)
- `Pendente`/`AguardandoAprovacao` → `Cancelada` (antes de concluída)
- Qualquer estado não-concluído pode ir para `FalhaNoProcessamento` em caso de erro
- `Concluida`/`Rejeitada`/`Cancelada` são estados finais (não devem alterar estoque retroativamente)

## 3. Endpoints

- `POST /smart_vision/outbound` — cria operação (status inicial `Pendente`)
- `GET /smart_vision/outbound` — lista com filtros: type, status, product_id, user_id, from_date, to_date
- `GET /smart_vision/outbound/{id}` — detalhe
- `PATCH /smart_vision/outbound/{id}/status` — atualiza status com validações
- `POST /smart_vision/outbound/{id}/process` — efetiva baixa: valida saldo, chama lógica equivalente a `stock_exit`, grava `stock_movement`, atualiza saldo, marca `Concluida`

## 4. Regras

- Quantidade > 0, produto existe, validações conforme Change 02.
- Idempotência: rejeita requisições repetidas com mesma `idempotency_key` ou mesmo contexto.
- Concorrência: valida saldo no momento do `process`.
- Permissões: apenas gestor aprova/rejeita operações em `AguardandoAprovacao` (quando aplicável).
- Operações `Concluida` não podem ser reprocessadas ou alteradas.
- Não remove `stock_movement` existente; correções usam estorno/movimentação compensatória se necessário.
