# Design: stock-alerts-live-deployment

## Mapeamento de Correções de Sintaxe

### 1. Rotas com barra `/` ou traço `-` exigem aspas duplas

O compilador XanoScript interpreta `/` como divisão aritmética quando não há aspas,
causando erro de parse na declaração da query.

| Arquivo | Antes | Depois |
|---|---|---|
| `alerts_summary_GET.xs` | `query alerts/summary verb=GET` | `query "alerts/summary" verb=GET` |
| `alerts_evaluate_POST.xs` | `query alerts/evaluate verb=POST` | `query "alerts/evaluate" verb=POST` |
| `alerts_status_POST.xs` | `query alerts/status verb=POST` | `query "alerts/status" verb=POST` |
| `alerts_inactive_GET.xs` | `query alerts/inactive verb=GET` | `query "alerts/inactive" verb=GET` |
| `stock_parameters_PATCH.xs` | `query stock-parameters verb=PATCH` | `query "stock-parameters" verb=PATCH` |

### 2. Tipo de erro HTTP 403

O Xano não reconhece `"forbidden"` como tipo de erro válido. O valor correto para HTTP 403 é `"accessdenied"`.
Afeta todos os 7 endpoints do módulo (`alerts_*`, `replenishment_GET`, `stock_parameters_PATCH`).

### 3. Comentários dentro de `var {}`

O parser do Xano não aceita linhas de comentário `//` dentro do corpo de `var {}`.
Esses comentários devem ser movidos para antes do bloco `var` ou para antes do `if`.

Arquivo afetado: `xano/function/smart_vision/classificar_produto.xs`

### 4. Ordem de Publicação (resolvida automaticamente pelo CLI)

O Xano CLI resolve as dependências automaticamente:
1. Tabelas (`stock_alert` criada, `product` com 3 novos campos)
2. Funções (`Smart Vision/classificar_produto`, `Smart Vision/avaliar_alerta`)
3. Endpoints de API que consomem tabelas e funções acima
