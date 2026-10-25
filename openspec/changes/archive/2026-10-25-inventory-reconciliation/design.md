# Design: inventory-reconciliation

## Arquitetura e Fluxo de Dados

O fluxo segue o ciclo de vida do inventário e reutiliza a tabela `stock_movement` (Change 02) como ledger único de ajustes.

### 1. Tabelas de persistência

#### `inventory` (cabeçalho do inventário)
- `id` (int, PK)
- `created_at` (timestamp, now)
- `status` (text): `Aberto`, `EmContagem`, `AguardandoAprovacao`, `Concluido`
- `scope` (text): `completo`, `categoria`, `localizacao`
- `category_filter` (text?), filtro de categoria quando scope = categoria
- `location_filter` (text?), filtro de localização quando scope = localizacao
- `opened_by` (int, usuário que abriu)
- `opened_at` (timestamp, now)
- `closed_at` (timestamp?)
- `notes` (text?)

#### `inventory_count` (contagem física)
- `id` (int, PK)
- `created_at` (timestamp, now)
- `inventory_id` (int, FK → inventory)
- `product_id` (int, FK → product)
- `quantity_counted` (int, >= 0)
- `counted_by` (int, usuário que contou)
- `counted_at` (timestamp, now)
- `is_recount` (bool, default false)
- `previous_count_id` (int?, link ao registro anterior em recontagem)
- `notes` (text?)
- Regra de negócio: não criar um segundo registro não-recount para o mesmo (inventory_id, product_id). Uma recontagem cria novo registro com `is_recount = true` e `previous_count_id` apontando ao anterior, preservando o histórico.

#### `inventory_discrepancy` (conciliação + decisão)
- `id` (int, PK)
- `created_at` (timestamp, now)
- `inventory_id` (int, FK → inventory)
- `product_id` (int, FK → product)
- `counted_quantity` (int, quantidade física contada — valor de referência preservado)
- `reference_quantity` (int, saldo do sistema no momento da conciliação — preservado)
- `difference` (int, counted - reference, com sinal)
- `divergence_type` (text): `none`, `shortage` (falta), `overage` (sobra)
- `impact` (text): descrição do impacto no saldo
- `status` (text): `pending`, `approved`, `rejected`, `recount_requested`
- `reviewed_by` (int?, gestor que decidiu)
- `reviewed_at` (timestamp?)
- `review_notes` (text?, justificativa da decisão)
- `adjustment_applied` (bool, default false)
- `adjustment_movement_id` (int?, link ao registro em stock_movement)

#### `inventory_decision` (audit log de decisões)
- `id` (int, PK)
- `created_at` (timestamp, now)
- `inventory_id` (int, FK → inventory)
- `product_id` (int, FK → product)
- `discrepancy_id` (int, FK → inventory_discrepancy)
- `action` (text): `approved`, `rejected`, `recount_requested`
- `decided_by` (int, gestor)
- `decided_at` (timestamp, now)
- `justification` (text?, justificativa da decisão)
- `previous_status` (text?, status anterior da divergência)
- `notes` (text?)

### 2. Endpoints (grupo "Smart Vision", canonical `SzoTJegm`)

| Endpoint | Método | Descrição |
|---|---|---|
| `/smart_vision/inventories` | POST | Cria inventário (status `Aberto`) |
| `/smart_vision/inventories` | GET | Lista inventários com status, responsável, datas, progresso |
| `/smart_vision/inventories/{id}` | GET | Detalhe do inventário |
| `/smart_vision/inventories/{id}/status` | PATCH | Transição de estado (valida transições permitidas) |
| `/smart_vision/inventories/{id}/counts` | POST | Registra/recontagem de um produto |
| `/smart_vision/inventories/{id}/counts` | GET | Lista contagens do inventário |
| `/smart_vision/inventories/{id}/reconcile` | POST | Calcula divergências vs saldo de referência |
| `/smart_vision/inventories/{id}/discrepancies` | GET | Lista divergências do inventário |
| `/smart_vision/inventories/{id}/discrepancies/{did}/decision` | POST | Gestor aprova/rejeita/solicita recontagem |
| `/smart_vision/inventories/{id}/apply-adjustments` | POST | Aplica ajustes aprovados via `stock_movement` (idempotente) |
| `/smart_vision/stock_adjustment` | POST | Aplica um ajuste unitário (movement_type = "adjustment") |

### 3. Estados e transições permitidas

- `Aberto` → `EmContagem`: iniciar contagem.
- `EmContagem` → `Aberto`: pausar/interromper temporariamente.
- `EmContagem` → `AguardandoAprovacao`: enviar contagem para análise.
- `AguardandoAprovacao` → `EmContagem`: solicitar recontagem / reabrir.
- `AguardandoAprovacao` → `Concluido`: concluir após processar decisões obrigatórias.
- Inventário `Concluido` não pode ser alterado retroativamente.

### 4. Conciliação

Para cada produto com contagem no inventário:
- `counted_quantity` = quantidade física (última contagem do produto)
- `reference_quantity` = `current_stock` do produto no momento da conciliação
- `difference` = counted - reference
- `divergence_type`: `none` se diff == 0; `shortage` se diff < 0; `overage` se diff > 0
- Valores originais (counted, reference) são preservados para rastreabilidade.

### 5. Tratamento de concorrência (movimentações entre contagem e aprovação)

Antes de aplicar um ajuste, o endpoint compara `current_stock` atual do produto com o `reference_quantity` usado na conciliação:
- Se iguais: aplica o ajuste normalmente.
- Se diferentes: recalcula a divergência com o saldo atual; se a nova divergência for diferente da registrada, solicita recontagem ou rejeita a aplicação até nova análise, evitando sobrescrever movimentações legítimas posteriores.

### 6. Idempotência

Um ajuste só é aplicado uma vez por divergência (`adjustment_applied` + `adjustment_movement_id`). Requisições repetidas para a mesma divergência já aplicada não geram nova movimentação.

### 7. Controle de acesso

- Qualquer usuário autenticado pode abrir/contar (Escopo: Estoquista, Vendedor, Gestor).
- Somente Gestor pode aprovar/rejeitar divergências e aplicar ajustes.
- O responsável pela contagem não aprova a própria divergência (separação de funções).
- Validação feita no backend (XanoScript), não apenas na UI.

### 8. Reutilização do ledger da Change 02

A aplicação de ajuste grava em `stock_movement` com `movement_type = "adjustment"`, preenchendo `reason` com referência ao inventário e à divergência, `user_id` do gestor, e `reference_text` com o ID do inventário. O saldo do produto é atualizado atômicamente (auditoria primeiro, saldo depois), respeitando a regra de saldo negativo.
