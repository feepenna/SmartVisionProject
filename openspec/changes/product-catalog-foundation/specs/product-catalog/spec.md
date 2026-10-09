# Spec Delta

## Purpose

Gerenciar o catálogo de produtos ópticos (armações, lentes oftálmicas, lentes de contato e acessórios), permitindo cadastro, parametrização técnica e consulta estruturada de itens em estoque.

## ADDED Requirements

### Requirement: Cadastro de Produto Geral
O sistema SHALL permitir o cadastro de novos produtos no catálogo com os campos obrigatórios: SKU, nome, categoria, marca, modelo, preço de venda, localização física e estoque mínimo.

#### Scenario: Cadastro de armação com sucesso
- **WHEN** o usuário submete o formulário com SKU único "ARM-001", nome "Armação RayBan Aviador", categoria "Armação", marca "RayBan", preço de venda 450.00 e estoque mínimo 5
- **THEN** o sistema SHALL persistir o produto no banco de dados e retornar status de sucesso com o ID gerado

#### Scenario: Rejeição por campos obrigatórios ausentes
- **WHEN** o usuário tenta cadastrar um produto sem informar o SKU ou o nome
- **THEN** o sistema SHALL rejeitar o cadastro informando mensagem de erro clara indicando os campos faltantes

### Requirement: Atributos Técnicos Obrigatórios para Lentes
O sistema SHALL exigir o preenchimento de atributos técnicos (grau esférico, grau cilíndrico, tipo de lente) quando a categoria do produto for "Lente Oftálmica" ou "Lente de Contato".

#### Scenario: Cadastro de lente oftálmica com parâmetros ópticos válidos
- **WHEN** o usuário seleciona a categoria "Lente Oftálmica" e preenche grau esférico "-2.50", cilíndrico "-0.75", eixo "180", tipo "Monofocal" e material "Resina 1.67"
- **THEN** o sistema SHALL salvar o produto vinculando todos os atributos técnicos informados

#### Scenario: Rejeição de lente sem parâmetros ópticos
- **WHEN** o usuário tenta salvar um item da categoria "Lente Oftálmica" sem preencher o grau esférico
- **THEN** o sistema SHALL bloquear o salvamento e alertar que o grau esférico é obrigatório para lentes

### Requirement: Unicidade de SKU
O sistema SHALL garantir que cada produto possua um SKU único em todo o sistema.

#### Scenario: Tentativa de cadastro com SKU duplicado
- **WHEN** o usuário submete um produto cujo SKU já existe cadastrado na base de dados
- **THEN** o sistema SHALL rejeitar a operação informando que o SKU já está em uso

### Requirement: Estoque Mínimo Obrigatório e Não Negativo
O sistema SHALL exigir a definição de um nível de estoque mínimo maior ou igual a zero para todo produto cadastrado.

#### Scenario: Validação de valor inválido de estoque mínimo
- **WHEN** o usuário informa um valor negativo para o estoque mínimo (ex: -1)
- **THEN** o sistema SHALL rejeitar o formulário exigindo um número inteiro não negativo

### Requirement: Consulta e Filtragem de Produtos
O sistema SHALL disponibilizar consulta paginada ou filtrada por termo de busca (SKU/nome) e por categoria de produto na interface.

#### Scenario: Filtragem por categoria
- **WHEN** o operador seleciona o filtro de categoria "Armação" na tela de consulta
- **THEN** a tabela de resultados SHALL exibir apenas produtos pertencentes à categoria "Armação"
