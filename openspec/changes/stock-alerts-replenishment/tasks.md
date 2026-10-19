# Tasks: stock-alerts-replenishment (Change 05)

## Backend (Xano / XanoScript)

1. [x] Estender `xano/table/product.xs` com `target_stock`, `inactivity_days`, `alerts_enabled`
2. [x] Estender `enum role` em `xano/table/user.xs` com os perfis do domain-model
3. [x] Criar tabela `xano/table/stock_alert.xs` (ciclo de vida, sem apagar histórico)
4. [x] Criar `alerts_evaluate_POST.xs` (avaliação idempotente: abre, auto-resolve, silencia)
5. [x] Criar `alerts_summary_GET.xs` (resumo ao vivo + perfil do usuário)
6. [x] Criar `alerts_GET.xs` (lista com filtros)
7. [x] Criar `alerts_inactive_GET.xs` (inativos vs. sem histórico)
8. [x] Criar `alerts_status_POST.xs` (transições manuais validadas)
9. [x] Criar `replenishment_GET.xs` (sugestão `max(0, alvo - saldo)` + falta de parâmetros)
10. [x] Criar `stock_parameters_PATCH.xs` (parâmetros por produto, somente Gestor)
11. [x] Ajustar precondições de perfil dos endpoints existentes (decision, apply_adjustments, outbound_status) para aceitar `Gestor`
12. [x] Validar sintaxe dos `.xs` com `xano workspace push --dry-run` (sem push) — exit 0, sem erros

## Frontend e cliente Python

13. [x] Expandir `services/xano_client.py` com funções de alertas, sugestões e parâmetros
14. [x] Adicionar seção "🔔 Alertas & Reposição (Change 05)" no `app.py` (dashboard, abas, filtros, estados de erro/vazio, ações por perfil)
15. [x] Remover o cálculo de reposição duplicado no cliente (aba da Change 02) apontando para a nova seção
16. [x] Adicionar CSS das classes usadas (`main-header`, `sub-header`, `kpi-card`, `metric-label`, `status-badge`)

## Testes e documentação

17. [x] Criar `tests/test_alert_rules.py` (classificação, sugestão, ciclo de vida, inatividade, autorização)
18. [x] Criar `tests/test_alerts_client.py` (contrato e validações do cliente)
19. [x] Atualizar `docs/domain-model.md` (Alerta de Estoque, Sugestão de Reposição, Produto, Usuário/Perfil)
20. [x] Rodar a suíte completa (`pytest`) e registrar resultado — 110 passed (54 baseline + 56 novos)
21. [x] Revisar diff e documentar decisões/limitações

## Notas / limitações

- As funções Xano `Smart Vision/classificar_produto` e `Smart Vision/avaliar_alerta` concentram a regra
  única de classificação e o ciclo de vida; o endpoint `alerts/evaluate` apenas itera os produtos monitorados.
- A avaliação é síncrona e idempotente; não há tarefa agendada nesta change.
- O `target_stock` não pode ser limpo (voltar a nulo) via `PATCH /stock-parameters`, pois `null` significa
  "não alterar"; a UI usa a caixa "Definir/Atualizar estoque alvo" para controlar o envio.
- Os alertas cobrem apenas `LOW_STOCK` e `INACTIVE`; a faixa `insuficiente` aparece em criticidade e
  sugestões, mas não abre alerta (decisão do design/spec).
- Nenhum push foi executado; a validação foi feita apenas com `--dry-run`.
