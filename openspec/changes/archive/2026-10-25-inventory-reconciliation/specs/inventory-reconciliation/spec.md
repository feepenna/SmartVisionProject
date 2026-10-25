# Specification: Inventory Reconciliation (Change 03)

## Purpose

Implementar o fluxo completo de inventário físico e conciliação de estoque, permitindo registros de contagens físicas, comparação com saldos do sistema, classificação de divergências, aprovação/rejeição por gestor e aplicação de ajustes por meio do ledger existente (`stock_movement`), reutilizando o catálogo de produtos (Change 01) e a infraestrutura de movimentação e auditoria (Change 02).

## ADDED Requirements

### Requirement: Criação e listagem de inventários
O sistema SHALL permitir criar um inventário físico com identificador, data de abertura, responsável, escopo (completo/categoria/localização) e status `Aberto`.
O sistema SHALL listar inventários com status, responsável, datas e progresso.

#### Scenario: Criar inventário com sucesso
- **WHEN** um usuário autorizado submete o formulário com escopo "completo" e responsável válido
- **THEN** o sistema persiste o inventário com status `Aberto` e retorna o ID gerado

#### Scenario: Listar inventários
- **WHEN** o usuário consulta a listagem de inventários
- **THEN** o sistema retorna todos os inventários com status, responsável, data de abertura e progresso

### Requirement: Transições de estado do inventário
O sistema SHALL gerenciar o ciclo de vida com os estados `Aberto`, `EmContagem`, `AguardandoAprovacao`, `Concluido` e as transições permitidas:
- `Aberto` → `EmContagem`
- `EmContagem` → `Aberto`
- `EmContagem` → `AguardandoAprovacao`
- `AguardandoAprovacao` → `EmContagem`
- `AguardandoAprovacao` → `Concluido`
O sistema SHALL impedir transições inválidas e alterações retroativas em inventários `Concluido`.

#### Scenario: Transição inválida é rejeitada
- **WHEN** se tenta ir de `Aberto` diretamente para `AguardandoAprovacao`
- **THEN** o sistema rejeita com erro de validação

#### Scenario: Inventário concluído não pode ser alterado
- **WHEN** se tenta registrar contagem em inventário com status `Concluido`
- **THEN** o sistema rejeita a operação

### Requirement: Registro de contagem física e recontagem
O sistema SHALL registrar, para cada produto de um inventário: quantidade física contada, usuário responsável, data/hora, observações e vínculo ao inventário.
O sistema SHALL permitir salvar o progresso e retomar a contagem posteriormente.
O sistema SHALL impedir registros duplicados indevidos para o mesmo produto e inventário.
O sistema SHALL permitir recontagens preservando os registros anteriores (não sobrescrever destrutivamente).
O sistema SHALL não alterar o saldo de estoque durante a contagem.

#### Scenario: Registrar contagem de produto
- **WHEN** um usuário registra a quantidade física de um produto em um inventário `EmContagem`
- **THEN** o sistema cria o registro de contagem vinculado ao inventário e produto, sem alterar `current_stock`

#### Scenario: Recontagem preserva histórico
- **WHEN** já existe uma contagem para o produto e se registra uma recontagem
- **THEN** o sistema cria um novo registro com `is_recount = true` vinculado ao anterior, preservando o registro original

### Requirement: Conciliação de estoque
O sistema SHALL comparar a quantidade física contada com o saldo de referência do sistema para cada produto, apresentando quantidade contada, quantidade de referência, diferença absoluta, classificação da divergência (sem divergência / falta / sobra), impacto e situação da análise.
O sistema SHALL preservar os valores originais utilizados na conciliação.

#### Scenario: Classificar falta de estoque
- **WHEN** quantidade contada (3) é inferior à quantidade de referência (5)
- **THEN** a divergência é classificada como `shortage` com diferença -2

#### Scenario: Classificar sobra de estoque
- **WHEN** quantidade contada (7) é superior à quantidade de referência (5)
- **THEN** a divergência é classificada como `overage` com diferença +2

#### Scenario: Sem divergência
- **WHEN** quantidade contada é igual à quantidade de referência
- **THEN** a divergência é classificada como `none`

### Requirement: Aprovação e rejeição de divergências (gestor)
O sistema SHALL permitir que um gestor visualize divergências, aprove ajustes, rejeite com justificativa e solicite recontagem.
O sistema SHALL validar permissão de gestor no backend.
O sistema SHALL impedir que o responsável pela contagem aprove a própria divergência (separação de funções).
O sistema SHALL registrar usuário, data, ação e justificativa de cada decisão.
O sistema SHALL impedir que uma divergência rejeitada gere movimentação de ajuste.
O sistema SHALL preservar o histórico de decisões (não sobrescrever).

#### Scenario: Gestor aprova divergência
- **WHEN** um gestor aprova uma divergência pendente com justificativa
- **THEN** o status da divergência passa para `approved` e é registrado o decision log

#### Scenario: Usuário não-gestor não pode aprovar
- **WHEN** um usuário sem perfil de gestor tenta aprovar uma divergência
- **THEN** o sistema rejeita com erro de permissão

#### Scenario: Divergência rejeitada não gera ajuste
- **WHEN** uma divergência é rejeitada
- **THEN** não é criada movimentação de estoque para essa divergência

### Requirement: Aplicação de ajustes de estoque
O sistema SHALL aplicar ajustes aprovados por meio do mecanismo de movimentação existente na Change 02 (`stock_movement`, `movement_type = "adjustment"`).
O sistema SHALL associar cada movimentação ao inventário e à divergência correspondente.
O sistema SHALL registrar saldo anterior, quantidade ajustada e saldo resultante.
O sistema SHALL impedir a aplicação duplicada de um mesmo ajuste (idempotência).
O sistema SHALL garantir atomicidade: se falhar, não deixa o inventário parcialmente atualizado.
O sistema SHALL respeitar as regras de saldo mínimo, saldo negativo e demais restrições já implementadas.

#### Scenario: Aplicar ajuste aprovado (sobra)
- **WHEN** uma divergência `overage` aprovada é aplicada
- **THEN** é criada movimentação `adjustment` em `stock_movement` e `current_stock` do produto é atualizado para o valor contado

#### Scenario: Impedir aplicação duplicada
- **WHEN** o ajuste de uma divergência já foi aplicado e a requisição é repetida
- **THEN** o sistema não cria nova movimentação e informa que o ajuste já foi aplicado

### Requirement: Tratamento de movimentações concorrentes
O sistema SHALL comparar o saldo atual com o saldo de referência antes de aplicar o ajuste.
O sistema SHALL recalcular a conciliação quando houver movimentações posteriores relevantes.
O sistema SHALL solicitar nova contagem quando não for possível determinar a quantidade correta com segurança.

#### Scenario: Saldo mudou entre contagem e aprovação
- **WHEN** o `current_stock` do produto difere do `reference_quantity` da conciliação no momento de aplicar o ajuste
- **THEN** o sistema recalcula a divergência e, se não for possível aplicar com segurança, solicita recontagem ou rejeita a aplicação
