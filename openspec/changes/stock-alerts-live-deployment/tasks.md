# Tasks: stock-alerts-live-deployment

## 1. Correções de Sintaxe XanoScript

- [x] 1.1 `alerts_summary_GET.xs` — aspas na rota + `accessdenied`
- [x] 1.2 `alerts_GET.xs` — `accessdenied`
- [x] 1.3 `alerts_evaluate_POST.xs` — aspas na rota + `accessdenied`
- [x] 1.4 `alerts_status_POST.xs` — aspas na rota + `accessdenied`
- [x] 1.5 `alerts_inactive_GET.xs` — aspas na rota + `accessdenied`
- [x] 1.6 `replenishment_GET.xs` — `accessdenied`
- [x] 1.7 `stock_parameters_PATCH.xs` — aspas na rota + `accessdenied`
- [x] 1.8 `classificar_produto.xs` — remover comentários inline dentro de `var {}`
- [x] 1.9 Migrar para o dialeto atual do XanoScript (`foreach ($lista) { each as $x {`, `conditional { if (...) { } }`, `var.update`) nos 7 endpoints e nas 2 funções — necessário porque `if` dentro de `var {}` e `foreach $x in $lista` também quebram o parser.

## 2. Validação Local

- [x] 2.1 Validar os 7 endpoints e 2 funções via `xano workspace push --dry-run` — os 9 documentos foram parseados sem erro (equivalente ao `xano_validate_xanoscript`).
- [x] 2.2 Executar suíte `pytest meu-projeto/tests/` — **222 passed + 137 subtests**, sem regressões.
- [x] 2.3 Criar `tests/test_alerts_contract.py` para travar as regressões de sintaxe (rotas com `/`/`-` entre aspas, `error_type` válido, `foreach`/`each as`, sem `if` dentro de `var {}`, `response` fora do `stack`).

## 3. Publicação no Xano

- [x] 3.1 Executar `xano workspace push --dry-run --include <11 arquivos do módulo>` e revisar relatório: `CREATE table stock_alert`, `ADD_FIELD product` (3 campos), `CREATE` 2 funções, `CREATE` 7 endpoints, sem referências não resolvidas.
- [ ] 3.2 Executar `xano workspace push` — publicar na instância live (**aguardando confirmação explícita: cria tabela e altera schema de `product`**).
- [ ] 3.3 Publicar somente os endpoints/funções após a tabela existir, se o push for feito em etapas.

## 4. Validação E2E

- [ ] 4.1 Confirmar que `GET /alerts/summary?user_id=<id>` retorna HTTP 200
- [ ] 4.2 Confirmar que a aba "Alertas & Reposição" carrega sem erro 404
- [ ] 4.3 Confirmar que `POST /alerts/evaluate` e `GET /replenishment` respondem corretamente

## Notas

- Nenhuma lógica de negócio é alterada — são correções de sintaxe que impediam o push.
- Os arquivos corrigidos residem em `xano/api/smart_vision/` e `xano/function/smart_vision/`.
- O push escopado inclui a tabela `stock_alert` (CREATE) e 3 campos novos em `product` (ADD_FIELD); sem eles os endpoints de alertas ficam com referências não resolvidas.
- Um push completo (`--sync` ou sem `--include`) afetaria também 6 tabelas e 13 endpoints fora do escopo: usar sempre o recorte de 11 arquivos acima.
- Comando de push escopado validado no dry-run:

```bash
xano workspace push -w 154752 \
  -i 'xano/table/stock_alert.xs' \
  -i 'xano/table/product.xs' \
  -i 'xano/function/smart_vision/*.xs' \
  -i 'xano/api/smart_vision/alerts_**' \
  -i 'xano/api/smart_vision/replenishment_GET.xs' \
  -i 'xano/api/smart_vision/stock_parameters_PATCH.xs'
```
