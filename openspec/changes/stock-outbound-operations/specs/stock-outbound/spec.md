# Specification: Stock Outbound Operations (Change 04)

## Purpose

Implementar fluxo completo de saída de estoque: registro, processamento, aprovação (quando exigida), consulta e auditoria, reutilizando `stock_movement`/`stock_exit` (Change 02).

## ADDED Requirements

### Requirement: Registrar saída
O sistema SHALL permitir registrar saídas com tipos `SALE`, `LAB_SHIPMENT`, `LOSS`, `OPERATIONAL`.

#### Scenario: Registrar perda com justificativa
- WHEN usuário registra LOSS com quantidade > 0 e justificativa válida
- THEN operação é criada com status apropriado e vinculada ao contexto

### Requirement: Validação de produtos e quantidades
O sistema SHALL validar existência do produto, quantidade > 0, elegibilidade e autorização.

### Requirement: Processamento efetiva baixa
Ao processar operação válida, o sistema SHALL gerar movimentação `exit` em `stock_movement` e atualizar `current_stock` do produto.

#### Scenario: Bloquear saldo negativo
- WHEN tentar processar saída maior que saldo
- THEN operação NÃO altera estoque e retorna erro 400

### Requirement: Idempotência e concorrência
O sistema SHALL impedir duplicação de baixa e tratar concorrência validando saldo no momento da efetivação.

### Requirement: Aprovação por gestor
Para operações que exigem aprovação, apenas gestor autorizado pode aprovar/rejeitar.

### Requirement: Consulta e histórico
O sistema SHALL listar e filtrar saídas por tipo/status/período/produto/responsável com detalhes.
