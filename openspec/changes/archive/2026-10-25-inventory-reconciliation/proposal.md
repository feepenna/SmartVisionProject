# Proposal: inventory-reconciliation

## Why

O Smart Vision precisa garantir que o estoque registrado no sistema corresponda à quantidade efetivamente disponível na operação. Hoje o sistema suporta entradas e saídas auditadas (Change 02) e catálogo de produtos (Change 01), mas não há fluxo de contagem física, conciliação de divergências, aprovação de ajustes nem rastreabilidade do inventário. Sem isso, faltas e sobras não são detectadas nem corrigidas de forma controlada.

## What Changes

- **Backend & Banco no Xano:**
  - Novas tabelas: `inventory` (cabeçalho do inventário), `inventory_count` (contagens e recontagens), `inventory_discrepancy` (resultado da conciliação + decisão de ajuste), `inventory_decision` (audit log de decisões do gestor).
  - Endpoints: criação/listagem/detalhe de inventário, transição de estados, registro de contagem, conciliação, consulta de divergências, decisão do gestor (aprovar/rejeitar/solicitar recontagem) e aplicação de ajustes de estoque.
  - Os ajustes são gravados na mesma tabela `stock_movement` da Change 02 (`movement_type = "adjustment"`), reutilizando o ledger existente. Não há ledger paralelo.
- **Cliente Python / Streamlit:**
  - Novas funções em `services/xano_client.py` para inventários, contagens, divergências, decisões e ajustes.
  - Telas Streamlit em `app.py` para listagem, criação, contagem física (modo cego), divergências, aprovação e histórico.

## Capabilities

### New Capabilities
- `inventory-reconciliation`: Inventário físico de ponta a ponta — abertura, contagem, conciliação, análise de divergências, aprovação/rejeição, aplicação de ajuste e consulta de histórico, com controle de acesso e rastreabilidade.

## Non-goals (Fora de Escopo Desta Change)
- Novo mecanismo de movimentação de estoque paralelo a `stock_movement`.
- RBAC estrito via JWT (mantém-se o padrão da Change 02: `user_id` recebido como parâmetro; regras de perfil documentadas e validadas no backend).
- Integração com PDV, notas fiscais ou múltiplas filiais.

## Impact
- **Xano / XanoScript:** 4 novas tabelas e endpoints de inventário/reconciliação.
- **Python / Streamlit:** Expansão de `xano_client.py` e de `app.py`.
- **Documentação:** `openspec/changes/inventory-reconciliation/`, `docs/domain-model.md`.
