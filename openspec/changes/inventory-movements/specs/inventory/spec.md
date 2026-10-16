# Specification: Inventory Movements & Audit

## Purpose
Garantir rastreabilidade imutável e auditoria prévia para todas as entradas e saídas de estoque no Smart Vision, prevenindo saldos negativos não autorizados.

## ADDED Requirements

### Requirement: Audit Trail Before Balance Update
The system MUST record an audit entry in the `stock_movement` table prior to updating the product stock balance for any stock movement (`entry`, `exit`).
Os campos gravados na auditoria são: `product_id`, `movement_type`, `quantity`, `previous_stock`, `new_stock`, `reason`, `created_at`.

#### Scenario: Successful audit logging on stock entry
- **WHEN** uma entrada de estoque válida é submetida
- **THEN** o sistema grava primeiro a movimentação na tabela `stock_movement` e em seguida atualiza `current_stock`

### Requirement: Negative Stock Prevention
The system MUST reject any stock exit request (`POST /smart_vision/stock_exit`) if `current_stock - quantity < 0`.
A operação DEVE retornar erro HTTP 400 Bad Request com mensagem descritiva sem atualizar o saldo do produto.

#### Scenario: Block stock exit when insufficient stock
- **WHEN** uma saída com quantidade maior que o saldo atual é solicitada
- **THEN** a operação é rejeitada com erro 400 e nenhum registro de movimentação altera o saldo

### Requirement: Input Validation
The system MUST validate that `quantity > 0` and that `reason` is non-empty.

#### Scenario: Reject non-positive quantity or empty reason
- **WHEN** uma movimentação é enviada com quantidade <= 0 ou motivo vazio
- **THEN** o sistema rejeita a solicitação com erro de validação
