# stock-outbound Specification

## Purpose
Implementar o fluxo completo de saída de estoque: registro, processamento, aprovação (quando exigida), consulta e auditoria, reutilizando o ledger `stock_movement` da Change 02. A baixa efetiva é atômica, idempotente e bloqueia saldo negativo.

## Requirements

### Requirement: Autenticação e identidade das operações
O sistema SHALL exigir autenticação de usuário em todos os endpoints de saída.
O sistema SHALL derivar o solicitante, aprovador e operador de `$auth.id`, ignorando qualquer identidade de usuário enviada pelo cliente.

#### Scenario: Acesso sem autenticação é bloqueado
- **WHEN** uma requisição `GET /outbound`, `POST /outbound`, `PATCH /outbound/status` ou `POST /outbound/process` é enviada sem token válido
- **THEN** o backend responde com HTTP 401 e não retorna nem altera operações

#### Scenario: Solicitante é o usuário autenticado
- **WHEN** um usuário autenticado registra uma saída
- **THEN** o campo `user_id` da operação é igual ao `$auth.id`, mesmo que o payload tente informar outro usuário

### Requirement: Registrar saída
O sistema SHALL permitir registrar saídas com os tipos `SALE`, `LAB_SHIPMENT`, `LOSS` e `OPERATIONAL`.
O sistema SHALL definir o status inicial no backend: `LOSS` inicia em `AguardandoAprovacao`; os demais tipos iniciam em `Pendente`.
O sistema SHALL exigir justificativa para operações do tipo `LOSS`.

#### Scenario: Registrar venda
- **WHEN** um usuário autenticado registra uma saída `SALE` com produto, quantidade maior que zero e motivo
- **THEN** a operação é persistida com status `Pendente`, vinculada ao usuário autenticado e sem alterar o estoque

#### Scenario: Registrar perda com justificativa
- **WHEN** um usuário autenticado registra uma saída `LOSS` com quantidade maior que zero e justificativa válida
- **THEN** a operação é persistida com status `AguardandoAprovacao` e sem alterar o estoque até a aprovação

#### Scenario: Perda sem justificativa é rejeitada
- **WHEN** um usuário tenta registrar uma saída `LOSS` sem justificativa ou com justificativa vazia
- **THEN** o backend rejeita a criação com erro de validação e nenhuma operação é criada

### Requirement: Validação de produtos e quantidades
O sistema SHALL validar que o tipo de saída pertence ao conjunto permitido, que a quantidade é maior que zero, que o motivo foi informado e que o produto existe.
O sistema SHALL rejeitar a criação sem persistir dados quando qualquer validação falhar.

#### Scenario: Tipo de saída inválido
- **WHEN** um usuário tenta registrar uma saída com tipo diferente de `SALE`, `LAB_SHIPMENT`, `LOSS` ou `OPERATIONAL`
- **THEN** o backend responde com erro de validação e não cria a operação

#### Scenario: Quantidade inválida
- **WHEN** um usuário tenta registrar uma saída com quantidade zero ou negativa
- **THEN** o backend responde com erro de validação e não cria a operação

#### Scenario: Produto inexistente
- **WHEN** um usuário tenta registrar uma saída para um `product_id` que não existe
- **THEN** o backend responde com HTTP 404 e não cria a operação

### Requirement: Processamento efetiva baixa
O sistema SHALL efetivar a baixa de estoque exclusivamente por `POST /outbound/process`.
O sistema SHALL, em uma única transação, criar uma movimentação `exit` em `stock_movement`, atualizar `current_stock`, marcar a operação como `Concluida` e gravar `stock_movement_id` e `processed_at`.
O sistema SHALL registrar saldo anterior, quantidade, saldo resultante e operador na movimentação de auditoria.

#### Scenario: Processar saída com saldo suficiente
- **WHEN** o solicitante ou um gestor processa uma operação `SALE` em `Pendente` e o saldo atual cobre a quantidade
- **THEN** o sistema cria a movimentação `exit`, decrementa o saldo e retorna a operação `Concluida` com o vínculo da movimentação

#### Scenario: Bloquear saldo negativo
- **WHEN** se tenta processar uma saída cuja quantidade é maior que o saldo atual do produto
- **THEN** o backend responde com HTTP 400, não cria movimentação, não altera o saldo e mantém a operação sem conclusão

#### Scenario: Conclusão direta pelo status é proibida
- **WHEN** se tenta atualizar o status diretamente para `Concluida` via `PATCH /outbound/status`
- **THEN** o backend rejeita a transição e orienta o uso de `POST /outbound/process`

### Requirement: Idempotência e concorrência
O sistema SHALL aceitar `idempotency_key` opcional e normalizar chave vazia para `null`.
O sistema SHALL impedir a criação de duas operações com a mesma `idempotency_key`.
O sistema SHALL impedir que uma operação gere mais de uma movimentação de estoque.
O sistema SHALL reler o saldo dentro da transação de processamento para evitar baixa concorrente incorreta.

#### Scenario: Chave de idempotência duplicada
- **WHEN** se tenta registrar outra operação com uma `idempotency_key` já existente
- **THEN** o backend responde com HTTP 400 e não cria uma segunda operação

#### Scenario: Reprocessamento é bloqueado
- **WHEN** se tenta processar novamente uma operação que já possui `stock_movement_id`
- **THEN** o backend responde com HTTP 400 e não cria nova movimentação nem altera o saldo

#### Scenario: Concorrência por saldo insuficiente
- **WHEN** duas operações disputam o mesmo saldo e a segunda encontra saldo insuficiente ao reler o produto na transação
- **THEN** a segunda é rejeitada sem movimentação e sem alterar o saldo ou o status da primeira

### Requirement: Aprovação e rejeição por gestor
O sistema SHALL exigir perfil `Gestor` ou `admin` para processar operações em `AguardandoAprovacao` e qualquer operação `LOSS`.
O sistema SHALL permitir que gestor rejeite operação em `AguardandoAprovacao`, registrando `approved_by` e `approved_at`.
O sistema SHALL impedir que usuário sem perfil de gestor aprove, rejeite ou processe operações que exigem aprovação.

#### Scenario: Vendedor não aprova a própria perda
- **WHEN** o solicitante com perfil `member` tenta processar sua operação `LOSS` em `AguardandoAprovacao`
- **THEN** o backend responde com HTTP 403 e o estoque permanece inalterado

#### Scenario: Gestor aprova e processa perda
- **WHEN** um usuário `Gestor` ou `admin` processa uma operação `LOSS` em `AguardandoAprovacao`
- **THEN** a baixa é efetivada, a operação vira `Concluida` e o aprovador é registrado em `approved_by`

#### Scenario: Gestor rejeita perda
- **WHEN** um usuário `Gestor` ou `admin` atualiza uma operação `AguardandoAprovacao` para `Rejeitada`
- **THEN** a operação fica `Rejeitada`, o aprovador e a data são registrados e nenhuma movimentação de estoque é criada

### Requirement: Cancelamento de operação
O sistema SHALL permitir que o solicitante ou um gestor cancele operação em `Pendente` ou `AguardandoAprovacao`.
O sistema SHALL manter o saldo inalterado ao cancelar.

#### Scenario: Solicitante cancela operação pendente
- **WHEN** o solicitante cancela uma operação em `Pendente` ou `AguardandoAprovacao`
- **THEN** a operação fica `Cancelada` e o saldo permanece inalterado

### Requirement: Estados e imutabilidade
O sistema SHALL gerenciar os estados `Pendente`, `AguardandoAprovacao`, `Concluida`, `Rejeitada`, `Cancelada` e `FalhaNoProcessamento`.
O sistema SHALL tratar `Concluida`, `Rejeitada` e `Cancelada` como estados finais, sem alteração ou reprocessamento.
O sistema SHALL permitir `FalhaNoProcessamento` apenas como estado de retry processável; o fluxo normal desta change não o produz.

#### Scenario: Operação concluída é imutável
- **WHEN** se tenta alterar o status ou processar novamente uma operação `Concluida`
- **THEN** o backend rejeita a operação e mantém o saldo e a movimentação existentes

#### Scenario: Operação rejeitada não é processável
- **WHEN** se tenta processar uma operação `Rejeitada` ou `Cancelada`
- **THEN** o backend responde com HTTP 400 e não movimenta estoque

### Requirement: Consulta e histórico
O sistema SHALL listar operações de saída com filtros opcionais por `type`, `status`, `product_id`, `user_id`, período (`from_date`/`to_date`) e `id`.
O sistema SHALL retornar detalhe quando `id` for informado e HTTP 404 quando a operação não existir.
O sistema SHALL ordenar a listagem por `created_at` decrescente.

#### Scenario: Listar e filtrar saídas
- **WHEN** um usuário autenticado consulta `GET /outbound` com filtros de tipo, status, produto, responsável ou período
- **THEN** o backend retorna somente as operações compatíveis, ordenadas da mais recente para a mais antiga

#### Scenario: Consultar operação por identificador
- **WHEN** um usuário autenticado consulta `GET /outbound?id=<id>` para uma operação existente
- **THEN** o backend retorna a operação com status, produto, quantidade, solicitante, aprovação e vínculo de movimentação

#### Scenario: Operação inexistente
- **WHEN** um usuário autenticado consulta um `id` de operação que não existe
- **THEN** o backend responde com HTTP 404 sem alterar dados

#### Scenario: Filtro de período usa timestamps
- **WHEN** o usuário informa `from_date` e/ou `to_date` em milissegundos
- **THEN** o backend compara esses valores com `created_at` usando os limites informados, sem exigir os dois campos
