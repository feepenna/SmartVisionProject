# Specification: Stock Alerts & Replenishment (Change 05)

## Purpose

Prevenir ruptura de estoque: parâmetros de reposição por produto, classificação de
criticidade, ciclo de vida de alertas (Ativo/EmAcompanhamento/Resolvido), detecção de
produtos sem movimentação, sugestões de reposição calculadas no backend, dashboard com
filtros e autorização por perfil — reutilizando catálogo, `stock_movement`, inventário
e saídas das Changes 01–04.

## ADDED Requirements

### Requirement: Parâmetros de estoque por produto
O sistema SHALL armazenar por produto `target_stock`, `inactivity_days` e
`alerts_enabled`, preservando `min_stock` e o saldo auditado existentes.

#### Scenario: Produto recém-cadastrado é monitorado por padrão
- WHEN um produto é criado sem informar parâmetros de alerta
- THEN ele nasce com `alerts_enabled = true`, sem alvo (`target_stock` nulo) e janela padrão de 30 dias

#### Scenario: Parâmetros inválidos são rejeitados
- WHEN um usuário envia `target_stock` negativo, `target_stock < min_stock` ou `inactivity_days < 1`
- THEN o backend responde 400 `inputerror` e nada é alterado

### Requirement: Classificação de criticidade (faixas disjuntas)
O sistema SHALL classificar cada produto como `critico` (saldo ≤ mínimo), `insuficiente`
(saldo > mínimo e < alvo, apenas com alvo definido) ou `regular` (demais casos).

#### Scenario: Saldo igual ao mínimo é crítico
- WHEN `current_stock == min_stock`
- THEN a classificação é `critico`

#### Scenario: Produto sem alvo não é insuficiente
- WHEN `target_stock` é nulo e o saldo está acima do mínimo
- THEN a classificação é `regular` e a consulta de sugestão sinaliza `parametros_incompletos`

### Requirement: Detecção de alertas por avaliação idempotente
O sistema SHALL avaliar as condições `LOW_STOCK` (saldo ≤ mínimo) e `INACTIVE` (última
movimentação anterior à janela, com histórico existente) em `POST /alerts/evaluate`,
abrindo alertas apenas quando não há um alerta aberto para o mesmo produto e tipo.

#### Scenario: Reavaliar não duplica alertas
- WHEN a avaliação é executada duas vezes seguidas sem mudança de saldo
- THEN a segunda execução não cria novos alertas e os contadores refletem zero criações

#### Scenario: Saldo normalizado resolve o alerta
- WHEN um alerta `Ativo`/`EmAcompanhamento` tem a condição normalizada na avaliação
- THEN o alerta passa a `Resolvido` com `resolution = "condicao_normalizada"` e `condition_cleared_at` registrado, sem apagar o histórico

#### Scenario: Resolução manual é respeitada enquanto a condição persistir
- WHEN um alerta é resolvido manualmente com a condição ainda valendo
- THEN a avaliação não recria alerta para aquele par até que a condição normalize

#### Scenario: Produto sem histórico não gera alerta de inatividade
- WHEN um produto nunca teve movimentação registrada
- THEN a avaliação não cria alerta `INACTIVE` e a consulta o exibe como `SemHistorico`

### Requirement: Sugestão de reposição calculada no backend
O sistema SHALL calcular a sugestão como `max(0, target_stock - current_stock)` quando
há alvo, e sinalizar `parametros_incompletos` quando não há.

#### Scenario: Sugestão com alvo configurado
- WHEN `target_stock = 20` e `current_stock = 7`
- THEN a sugestão é `13`

#### Scenario: Saldo acima do alvo não gera sugestão
- WHEN `target_stock = 20` e `current_stock = 25`
- THEN a sugestão é `0`

#### Scenario: Sugestão nunca gera movimentação
- WHEN a sugestão é consultada
- THEN nenhuma compra, pedido ou entrada de estoque é criada e nenhum saldo é alterado

### Requirement: Produtos sem movimentação
O sistema SHALL listar produtos com última movimentação além da janela configurada,
diferenciando `Inativo` (tem histórico antigo) de `SemHistorico` (nunca movimentado).

#### Scenario: Produto movimentado dentro da janela não aparece como inativo
- WHEN a última movimentação ocorreu dentro de `inactivity_days`
- THEN a situação é `Ativo`

### Requirement: Ciclo de vida de alertas
O sistema SHALL permitir somente as transições `Ativo → EmAcompanhamento`,
`Ativo → Resolvido` e `EmAcompanhamento → Resolvido`, registrando usuário, data,
notas e `resolution`; `Resolvido` é estado final e nenhum registro é apagado.

#### Scenario: Transição inválida é rejeitada
- WHEN se tenta alterar um alerta já `Resolvido` ou usar status inexistente
- THEN o backend responde 400 `inputerror` e o alerta permanece inalterado

#### Scenario: Resolver exige responsável
- WHEN um usuário com perfil autorizado resolve um alerta
- THEN `updated_by`, `status_updated_at`, `resolved_at` e `resolution = "manual"` são gravados

### Requirement: Autorização validada no backend
O sistema SHALL exigir `user_id` em todos os endpoints da Change 05 e validar o perfil
antes de executar: leitura para Gestor/Estoquista/Vendedor/Técnico (e legados),
avaliação e mudança de status para Gestor/Estoquista, parâmetros somente para Gestor.

#### Scenario: Vendedor não altera parâmetros
- WHEN um usuário com perfil `Vendedor` envia `PATCH /stock-parameters`
- THEN o backend responde 403 `forbidden` e nada é alterado

#### Scenario: Técnico é somente leitura
- WHEN um usuário com perfil `Técnico` chama `POST /alerts/evaluate`
- THEN o backend responde 403 `forbidden`

### Requirement: Dashboard com filtros e estados de erro
O sistema SHALL exibir no frontend um dashboard com KPIs do resumo, listas de alertas,
produtos sem movimentação e sugestões com filtros (status, tipo, produto, categoria,
classificação), além de configuração de parâmetros, com estados de carregamento,
erro e vazio — sem dados simulados de fallback.

#### Scenario: Backend indisponível
- WHEN um endpoint retorna erro ou `XANO_BASE_URL` não está configurado
- THEN a interface mostra mensagem de erro/vazia clara e não exibe dados inventados

#### Scenario: Botões fora do perfil são ocultados
- WHEN o perfil retornado pelo backend não permite uma ação
- THEN a interface não exibe o botão correspondente (o backend ainda valida)
