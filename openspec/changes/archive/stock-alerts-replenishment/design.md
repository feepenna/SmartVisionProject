# Design: stock-alerts-replenishment (Change 05)

## Arquitetura

Tudo é calculado e persistido no backend Xano. O frontend Streamlit apenas consulta
endpoints e exibe/aciona; nenhuma regra de saldo, criticidade, sugestão ou inatividade
é calculada na interface. A avaliação é um endpoint síncrono e idempotente
(`POST /alerts/evaluate`), sem tarefas assíncronas: o Xano atual não possui tasks
agendadas no projeto e o resumo ao vivo (`GET /alerts/summary`) cobre a visualização
sem depender de execução periódica.

Não existe saldo paralelo: o saldo consultado é sempre `product.current_stock`,
alimentado pela Change 02/03/04. Alertas são derivados e nunca escrevem em estoque.

## 1. Persistência

### 1.1 Extensão da tabela `product` (colunas novas, `min_stock` intacto)

- `int? target_stock` — estoque alvo para reposição (null = parâmetro não configurado).
- `int? inactivity_days` — janela de inatividade em dias (null = usar 30 dias).
- `bool alerts_enabled?=true` — monitoramento ativo/desativado por produto.

Migração: adição de colunas nullable/ com default — não quebra queries existentes;
linhas antigas ficam com `target_stock = null` (sinalizado como "falta de parâmetros")
e `alerts_enabled = true`. A alteração de schema é declarada no `.xs` e aplicada pelo
push do Xano CLI (não há SQL manual); reversível removendo as colunas.

### 1.2 Tabela `stock_alert` (nova)

- `int id`
- `timestamp created_at?=now`
- `int product_id` — FK lógica → `product`
- `text alert_type` — `LOW_STOCK` | `INACTIVE`
- `text status` — `Ativo` | `EmAcompanhamento` | `Resolvido`
- `text criticality` — snapshot `critico` | `insuficiente` | `regular` na detecção
- `int? observed_stock` — saldo observado na detecção
- `int? observed_min_stock` — mínimo observado na detecção (contexto histórico)
- `timestamp? detected_at`
- `timestamp? status_updated_at`
- `timestamp? resolved_at`
- `text? resolution` — `condicao_normalizada` | `movimentacao_registrada` | `manual`
- `timestamp? condition_cleared_at` — quando a condição deixou de valer por avaliação
- `int? opened_by` — usuário que disparou a avaliação que abriu o alerta
- `int? updated_by` — usuário que mudou o status manualmente (null = sistema)
- `text? notes` — acompanhamento/observações

Índices: `primary(id)`, `btree product_id`, `btree status`, `btree alert_type`,
`btree created_at desc`.

**Unicidade:** no máximo **um alerta aberto** (`status != "Resolvido"`) por
(`product_id`, `alert_type`) — garantida pela avaliação idempotente (a avaliação só
cria quando não existe alerta aberto do mesmo tipo/produto), e reforçada no cliente.
Não se usa índice único composto porque múltiplos históricos resolvidos do mesmo
produto/tipo são legítimos.

## 2. Regras de negócio

### 2.1 Classificação de criticidade (faixas disjuntas)

O documento original trazia `crítico = saldo ≤ min` e `insuficiente = saldo < min`,
que se sobrepõem. Decisão aprovada: usar faixas disjuntas com o estoque alvo.

```
se current_stock <= min_stock                -> "critico"
senão se target_stock != null
     e current_stock < target_stock          -> "insuficiente"
senão                                         -> "regular"
```

- `critico`: ponto de pedido atingido (domínio: alerta sempre que `saldo <= estoque mínimo`).
- `insuficiente`: acima do mínimo, mas ainda abaixo do alvo (só existe quando há alvo).
- `regular`: acima do mínimo e, se há alvo, já no/além do alvo.
- Produto sem `target_stock` nunca é `insuficiente` e é sinalizado
  `parametros_incompletos = true` nas consultas de sugestão.

### 2.2 Condições de alerta

- `LOW_STOCK`: `current_stock <= min_stock` e `alerts_enabled = true`.
- `INACTIVE`: `alerts_enabled = true`, produto **tem histórico** em `stock_movement` e a
  última movimentação é anterior a `now - inactivity_days` (default 30).
  - Produtos **sem histórico** não geram alerta: são exibidos como `SemHistorico`
    no endpoint de inatividade (sem histórico ≠ inativo).

### 2.3 Sugestão de reposição

```
se target_stock != null: sugestao = max(0, target_stock - current_stock)
senão:                   sugestao = null + parametros_incompletos = true
```

`custo_estimado = sugestao * cost_price` quando houver custo. A sugestão **não**
gera compra, pedido nem entrada — é somente recomendação consultável.

### 2.4 Ciclo de vida (idempotência e reabertura)

Transições manuais permitidas (`POST /alerts/status`):

- `Ativo` → `EmAcompanhamento`
- `Ativo` → `Resolvido` (`resolution = "manual"`, `updated_by = usuário`)
- `EmAcompanhamento` → `Resolvido` (`resolution = "manual"`, `updated_by = usuário`)
- `Resolvido` → estado final (não reabre; histórico nunca é apagado nem sobrescrito)

Auto-resolução na avaliação (`resolution` distinto, `updated_by = null` = sistema):

- condição normalizou (saldo subiu / movimentação recente) e há alerta aberto →
  `Resolvido` com `resolution = "condicao_normalizada"` ou `"movimentacao_registrada"`
  e `condition_cleared_at = now`.

Silenciamento (evita "duplicar" alerta recém-resolvido manualmente):

- avaliação com condição **ainda valendo** e sem alerta aberto: cria novo alerta,
  **exceto** se o alerta mais recente do par (produto, tipo) foi resolvido
  `manual` e ainda não tem `condition_cleared_at` (respeita a decisão humana).
- avaliação com condição **não valendo** e sem alerta aberto: se o alerta mais recente
  está `Resolvido` sem `condition_cleared_at`, grava `condition_cleared_at = now`
  (prepara a reabertura futura). Idempotente: só escreve quando o campo está nulo.

Assim: no máximo um alerta aberto por par; re-executar a avaliação não duplica;
condição que oscila gera um novo ciclo rastreável, sempre acrescentando registros.

### 2.5 Autorização (validada no backend; frontend só esconde botões)

| Ação | Gestor | Estoquista | Vendedor | Técnico | `admin` (legado) | `member` (legado) |
| --- | --- | --- | --- | --- | --- | --- |
| Ler (summary, alerts, inactive, replenishment) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Avaliar (`alerts/evaluate`) | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| Mudar status (`alerts/status`) | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| Alterar parâmetros (`stock-parameters`) | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |

`member` mantém apenas leitura (equivalente a Vendedor) para não regredir usuários
existentes. Toda chamada valida `db.get user` + `role` antes de executar e devolve
`forbidden` legível quando o perfil não permite.

## 3. Endpoints

| Endpoint | Verb | Entrada principal | Saída |
| --- | --- | --- | --- |
| `/smart_vision/alerts/evaluate` | POST | `user_id` | contadores: avaliados, criados, resolvidos, silenciados, por tipo |
| `/smart_vision/alerts/summary` | GET | `user_id` | KPIs + contagem por criticidade + inativos + `parametros_incompletos` + `actor.role` |
| `/smart_vision/alerts` | GET | `user_id`, `status?`, `alert_type?`, `product_id?` | lista de alertas (mais recente primeiro) |
| `/smart_vision/alerts/inactive` | GET | `user_id`, `inactivity_days?`, `incluir_sem_historico?` | por produto: `situacao` (`Inativo`/`Ativo`/`SemHistorico`), última movimentação, janela |
| `/smart_vision/alerts/status` | POST | `alert_id`, `status`, `notes?`, `user_id` | alerta atualizado (ou transição inválida → 400) |
| `/smart_vision/replenishment` | GET | `user_id`, `category?`, `product_id?` | por produto: saldo, mín., alvo, criticidade, sugestão, `parametros_incompletos`, custo estimado |
| `/smart_vision/stock-parameters` | PATCH | `product_id`, `min_stock?`, `target_stock?`, `inactivity_days?`, `alerts_enabled?`, `user_id` | produto atualizado |

Validações de entrada (400 `inputerror`): `product_id`/`user_id` obrigatórios,
`target_stock >= 0`, `target_stock >= min_stock` quando ambos enviados,
`inactivity_days >= 1`, `min_stock >= 0`, `status` válido, `alerts_enabled` booleano.
Produto/usuário inexistente → 404 `notfound`; perfil insuficiente → 403 `forbidden`.

### 3.1 Desempenho

`alerts/evaluate`, `alerts/summary` e `alerts/inactive` fazem uma consulta de
movimentação por produto (índice `stock_movement.product_id`), além das consultas de
produto/alerta. Adequado ao catálogo da loja (dezenas/centenas de SKUs) e mantém a
regra no backend. Se crescer, evoluir para agregação no banco/task agendada — fora
do escopo atual.

## 4. Cliente (`services/xano_client.py`)

Novas funções no padrão existente (validação local + `_handle_response`):

`list_alerts`, `get_alerts_summary`, `list_inactive_products`, `evaluate_alerts`,
`update_alert_status`, `list_replenishment`, `update_stock_parameters`.

Validações locais antes do request (mensagens em pt-BR): status permitidos, IDs
obrigatórios, `target_stock >= min_stock`, `inactivity_days >= 1`. Erros HTTP sobem
como `requests.HTTPError` com corpo, tratados pela UI com mensagem clara.

## 5. Frontend (`app.py`)

Novo item no menu lateral: **"🔔 Alertas & Reposição (Change 05)"**.

- **Dashboard**: KPIs do `summary` (alertas ativos, críticos, inativos, sugestão total,
  parâmetros incompletos) usando as classes do design system (`metric-widget`, e as
  classes `main-header`/`sub-header`/`kpi-card` que já eram usadas e estavam sem CSS).
- **Abas**: Alertas (filtros por status/tipo/produto + transições de status),
  Sem Movimentação, Sugestões de Reposição (filtros + ordenação), Parâmetros de Estoque
  (edição por produto).
- **Estados**: `st.spinner` no carregamento, `st.error` com a mensagem do backend,
  `st.info` para vazio e aviso de `parametros_incompletos`.
- **Sem dados simulados**: diferente das seções antigas, não existe fallback com dados
  mock — backend indisponível vira estado de erro explícito.
- **Perfil**: a UI usa `summary.actor.role` para esconder botões que o backend vai
  rejeitar (UX, não segurança); o backend continua validando.
- A aba "🚨 Alertas & Reposição" da seção da Change 02 deixa de calcular sugestões no
  cliente e passa a apontar para esta seção (elimina regra de negócio duplicada na UI).

## 6. Testes

- `tests/test_alert_rules.py` — espelha as regras do XanoScript em Python puro:
  classificação (faixas disjuntas), fórmula da sugestão e falta de parâmetros,
  transições permitidas, silenciamento/auto-resolução, inatividade vs. sem histórico,
  matriz de autorização.
- `tests/test_alerts_client.py` — contrato do cliente com `unittest` + `mock`
  (URL/verb/payload, validações e erros), no estilo de `test_outbound_client.py`.

## 7. Riscos e limitações documentados

- Os endpoints do `smart_vision` não usam `auth = "user"`: a autorização segue o padrão
  do projeto (`user_id` de entrada + `db.get user`), que é spoofável. Mantido por
  consistência arquitetural; a mitigação real exige autenticação por token (fora do escopo).
- Comparação temporal usa `now|add_secs_to_timestamp` e comparação de `timestamp`;
  a quantidade de dias decorridos é formatada no frontend a partir da data retornada.
- Push para o Xano **não** é feito por este agente: os `.xs` são gerados e validados
  localmente (`xano workspace push --dry-run`), e o push é responsabilidade do Felipe.
