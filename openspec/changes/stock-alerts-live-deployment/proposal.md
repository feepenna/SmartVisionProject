# Proposal: stock-alerts-live-deployment

## Why

A aba **Alertas & Reposição** no frontend Streamlit falha com HTTP 404 em produção:

```
Xano request failed: 404 Client Error: Not Found for url:
https://x8ki-letl-twmt.n7.xano.io/api:SzoTJegm/alerts/summary?user_id=7
Response body: {"code":"ERROR_CODE_NOT_FOUND","message":"Unable to locate request."}
```

O módulo de alertas e reposição (Change 05) não foi publicado na instância live do Xano (`api:SzoTJegm`, workspace `154752`). A publicação estava retida por incompatibilidades de sintaxe XanoScript documentadas como pendência no `MEMORY.md`:

1. **`error_type = "forbidden"`** (inválido) — o compilador do Xano exige `"accessdenied"` para HTTP 403.
2. **Nomes de rota com barra sem aspas** — `query alerts/summary` deve ser `query "alerts/summary"`.
3. **Comentários inline dentro de blocos `var {}`** em `classificar_produto.xs` quebram o parser do Xano.

## What Changes

- **Correções de Sintaxe XanoScript (sem alteração de lógica):**
  - Envolver em aspas os identificadores de rotas com `/` ou `-` nos 5 endpoints afetados.
  - Substituir `error_type = "forbidden"` por `error_type = "accessdenied"` nos 7 endpoints do módulo.
  - Mover comentários inline para fora dos blocos `var {}` em `classificar_produto.xs`.
- **Validação:**
  - Validar todos os `.xs` corrigidos via `xano_validate_xanoscript`.
  - Executar `xano workspace push --dry-run` e confirmar diff.
  - Executar o push na instância `x8ki-letl-twmt.n7.xano.io` workspace `154752`.
- **Confirmação de UI:**
  - Confirmar que a aba "🔔 Alertas & Reposição" carrega os KPIs sem HTTP 404.

## Capabilities

- `stock-alerts`: ativação em produção dos 7 endpoints de monitoramento de ruptura, inatividade e sugestões de reposição da Change 05.

## Non-goals

- Alterar regras de negócio, cálculos de sugestão ou critérios de classificação de criticidade.
- Modificar o frontend Streamlit ou os contratos do cliente Python.
- Qualquer mudança em tabelas, índices ou dados existentes.
