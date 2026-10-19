# Proposal: stock-alerts-replenishment (Change 05)

## Why

O Smart Vision já controla catálogo (Change 01), saldo auditado em `stock_movement` (Change 02), inventário físico (Change 03) e saídas (Change 04), mas ainda não possui um mecanismo formal de **prevenção de ruptura**: não existem parâmetros de reposição por produto, nem classificação de criticidade, nem um ciclo de vida para os alertas de estoque, nem uma visão de produtos parados sem giro. O painel de reposição existente no frontend calcula sugestões com uma fórmula ad-hoc e dados simulados no cliente, em violação à regra de que o backend é a fonte das regras de negócio.

## What Changes

- **Backend & Banco no Xano (XanoScript):**
  - Extensão da tabela `product` com parâmetros de reposição: `target_stock` (estoque alvo), `inactivity_days` (janela de inatividade) e `alerts_enabled` (monitoramento on/off). `min_stock` permanece intacto.
  - Extensão do enum `role` da tabela `user` com os perfis do `domain-model.md` (`Gestor`, `Estoquista`, `Vendedor`, `Técnico`), preservando os valores legados `admin`/`member`.
  - Nova tabela `stock_alert` (ciclo de vida Ativo → EmAcompanhamento → Resolvido, sem apagar histórico).
  - Endpoints XanoScript (todos exigem `user_id` e validam perfil no backend):
    - `POST /smart_vision/alerts/evaluate` — avaliação idempotente de todas as condições (abre, auto-resolva e silencia alertas).
    - `GET /smart_vision/alerts/summary` — resumo ao vivo (KPIs, criticidade, parâmetros incompletos, inativos) + perfil do usuário para a UI.
    - `GET /smart_vision/alerts` — lista de alertas com filtros (status, tipo, produto).
    - `GET /smart_vision/alerts/inactive` — produtos sem movimentação na janela configurada (diferenciando `Inativo` de `SemHistorico`).
    - `POST /smart_vision/alerts/status` — transições manuais de status com registro de responsável.
    - `GET /smart_vision/replenishment` — sugestões calculadas no backend: `max(0, target_stock - current_stock)` e sinalização de falta de parâmetros.
    - `PATCH /smart_vision/stock-parameters` — configuração de parâmetros por produto (somente Gestor).
  - Ajuste das precondições de perfil dos endpoints existentes (`inventory_discrepancy_decision`, `inventory_apply_adjustments`, `outbound_status`) para aceitar `Gestor` além de `admin`.
- **Cliente Python (`services/xano_client.py`):** funções de consulta/ação de alertas, sugestões e parâmetros, com validação local de entrada e erros legíveis.
- **Frontend Streamlit (`app.py`):** nova seção "🔔 Alertas & Reposição (Change 05)" com dashboard, abas (alertas, sem movimentação, sugestões, parâmetros), filtros, estados de loading/erro/vazio e ações condicionadas ao perfil retornado pelo backend. O painel de reposição duplicado na seção da Change 02 deixa de calcular regras no cliente.
- **Testes automatizados:** regras de negócio (classificação, sugestão, ciclo de vida, inatividade, autorização) e contrato do cliente.
- **Documentação:** `docs/domain-model.md` atualizado na mesma mudança.

## Capabilities

### New Capabilities
- `stock-alerts`: monitoramento de níveis de estoque e inatividade com parâmetros por produto, classificação de criticidade, ciclo de vida de alertas, sugestões de reposição, autorização por perfil e dashboard.

## Non-goals (Fora de Escopo)
- Gerar compras, pedidos ou entradas a partir das sugestões (sugestão é apenas recomendação consultável).
- Criar saldo paralelo ao `product.current_stock` ou ledger paralelo ao `stock_movement`.
- Alertas por e-mail/WhatsApp/push ou tarefas assíncronas agendadas (avaliação é síncrona, sob demanda).
- Alterar `min_stock`, saldo, auditoria ou histórico existente; apagar registros.
- Login/autenticação por token no frontend (mantém o padrão atual de `user_id`).
- Novas tecnologias de frontend ou de backend.

## Impact
- **Xano / XanoScript:** 1 tabela nova + 3 colunas novas em `product` + enum `role` estendido + 7 endpoints novos + 3 endpoints existentes ajustados (perfil).
- **Python / Streamlit:** expansão do cliente e nova seção de UI; remoção do cálculo de reposição duplicado no cliente.
- **Testes:** 2 novos arquivos de teste (regras + cliente).
- **Documentação:** `docs/domain-model.md` (Alerta de Reposição, Produto, Usuário/Perfil).
