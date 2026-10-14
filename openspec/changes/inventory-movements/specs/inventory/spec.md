# Specification: Inventory Movements & Audit

## Purpose
Garantir rastreabilidade imutável e auditoria prévia para todas as entradas e saídas de estoque no Smart Vision, prevenindo saldos negativos não autorizados.

## Requirements

### Requirement 1: Audit Trail Before Balance Update
- Toda movimentação de estoque (`entry`, `exit`) deve gravar um registro na tabela `stock_movement` antes de atualizar o saldo do produto correspondente.
- Os campos mínimos gravados na auditoria são: `product_id`, `movement_type`, `quantity`, `previous_stock`, `new_stock`, `reason`, `created_at`.

### Requirement 2: Negative Stock Prevention
- O endpoint de saída de estoque (`POST /smart_vision/stock_exit`) deve verificar se `current_stock - quantity >= 0`.
- Caso o resultado seja negativo, a operação deve ser rejeitada com código de erro HTTP apropriado (400 Bad Request) e mensagem descritiva.

### Requirement 3: Input Validation
- Quantidades devem ser estritamente maiores que zero (`quantity > 0`).
- O motivo (`reason`) deve ser fornecido.
