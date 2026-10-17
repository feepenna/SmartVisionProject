# Proposal: stock-outbound-operations (Change 04)

## Why

O Smart Vision precisa consolidar o fluxo formal de saída de estoque para cobrir vendas, envios para laboratório, perdas e saídas operacionais. Embora a Change 02 tenha implementado a base `stock_exit` com auditoria e bloqueio de saldo negativo, falta o gerenciamento completo do ciclo de vida das operações de saída (registro, solicitação, aprovação, vínculo com pedidos/OS e consulta filtrada), integrando-se perfeitamente ao ledger existente sem criar mecanismos paralelos.

## What Changes

- **Backend & Banco no Xano:**
  - Nova tabela `stock_outbound` para registrar operações de saída com tipos (`SALE`, `LAB_SHIPMENT`, `LOSS`, `OPERATIONAL`), status (`Pendente`, `AguardandoAprovacao`, `Concluida`, `Rejeitada`, `Cancelada`, `FalhaNoProcessamento`), referências (venda/pedido/OS), usuário responsável e vínculo com o movimento de estoque gerado (`stock_movement_id`).
  - Endpoints XanoScript:
    - `POST /smart_vision/outbound` — Registrar/solicitar saída.
    - `GET /smart_vision/outbound` — Listar e filtrar saídas.
    - `GET /smart_vision/outbound/{id}` — Detalhes da operação.
    - `PATCH /smart_vision/outbound/{id}/status` — Transição de estado (aprovação, rejeição, conclusão, cancelamento).
    - `POST /smart_vision/outbound/{id}/process` — Processar a operação (efetiva a baixa via `stock_exit`).
- **Cliente Python (`services/xano_client.py`):**
  - Funções para registrar, listar, consultar, atualizar status e processar operações de saída.
- **Frontend Streamlit (`app.py`):**
  - Seção dedicada com abas para registro por tipo, listagem com filtros, aprovação e histórico.
- **Testes Automatizados:**
  - Testes para cliente e regras de negócio (validação, permissões, idempotência, concorrência).

## Capabilities

### New Capabilities
- `stock-outbound-operations`: Gestão completa de operações de saída de estoque com controle de estados, aprovação, auditoria e integração com o ledger existente.

## Non-goals (Fora de Escopo)
- ERP/PDV completo.
- Novo ledger (reutiliza `stock_movement`/`stock_exit`).
- Retorno automático de laboratório para estoque.

## Impact
- **Xano / XanoScript:** 1 nova tabela + 5 endpoints.
- **Python / Streamlit:** Expansão de cliente e UI.
- **Documentação:** `docs/domain-model.md` atualizado.
