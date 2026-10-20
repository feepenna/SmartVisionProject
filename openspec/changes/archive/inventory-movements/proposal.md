# Proposal: inventory-movements

## Why
O Smart Vision exige rigor absoluto na integridade de estoque de ótica. Toda entrada, saída, ajuste ou baixa deve possuir rastreabilidade imutável (auditoria) gravada antes da alteração do saldo, validação estrita contra saldo negativo e transações atômicas no banco de dados. Esta mudança implementa a tabela de movimentações/auditoria e os endpoints de entrada e saída de estoque.

## What Changes

- **Backend & Banco no Xano:**
  - Criação da tabela `stock_movement` (ou `inventory_audit`) registrando: `product_id`, `movement_type` (entry, exit, adjustment), `quantity`, `previous_stock`, `new_stock`, `reason`, `user_id` e `created_at`.
  - Endpoint `POST /api:smart_vision/stock_entry` para entrada de mercadorias com registro de auditoria prévio.
  - Endpoint `POST /api:smart_vision/stock_exit` para saída/venda/perda de estoque com bloqueio estrito de saldo negativo.
- **Cliente Python / Streamlit:**
  - Funções no `xano_client.py` (`record_stock_entry`, `record_stock_exit`) para registrar entradas e saídas.

## Capabilities

### New Capabilities
- `inventory-movements`: Rastreabilidade e auditoria obrigatória de entradas e saídas de estoque, impedindo saldos negativos indevidos.

## Non-goals (Fora de Escopo Desta Change)
- Validação avançada de RBAC/tokens de perfil via cabeçalho JWT no backend (user_id recebido como parâmetro; RBAC estrito será acoplado no módulo de autenticação).

## Impact
- **Xano / XanoScript:** Nova tabela `stock_movement` e endpoints de movimentação de estoque (`stock_entry`, `stock_exit`).
- **Python / Streamlit:** Expansão do cliente `xano_client.py`.

