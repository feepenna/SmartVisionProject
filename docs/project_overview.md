# Project Overview — Smart Vision

## 1. Visão geral

Smart Vision é um sistema de gerenciamento de estoque desenvolvido especificamente para óticas.  
Ele permite controlar o ciclo completo 
de produtos ópticos (armações, lentes oftálmicas, lentes de contato, acessórios e produtos de limpeza), desde a entrada de mercadorias até a saída por venda ou ajuste, com rastreabilidade, alertas de reposição e visão clara do estoque em tempo real.

O sistema prioriza simplicidade operacional no dia a dia da loja, ao mesmo tempo em que oferece controle suficiente para evitar rupturas, perdas e divergências de inventário.

## 2. Problema

Óticas enfrentam desafios específicos de estoque que sistemas genéricos raramente resolvem bem:

- Grande variedade de produtos com atributos técnicos (graus, eixo, adição, tipo de lente, tratamento, marca, modelo).
- Itens de alto valor unitário que exigem controle mais rigoroso.
- Necessidade de vincular produtos a pedidos de clientes e receitas oftalmológicas.
- Risco de ruptura de itens populares e excesso de estoque parado.
- Dificuldade de conciliar estoque físico com registros manuais ou planilhas.
- Falta de visibilidade rápida sobre o que precisa ser comprado e o que está parado.

Sem um controle adequado, a ótica perde vendas, amarra capital em estoque ocioso e sofre com erros de inventário.

## 3. Objetivos

- Manter o estoque atualizado e confiável em tempo real.
- Reduzir rupturas de produtos de alta rotatividade.
- Facilitar a identificação de produtos parados e a necessidade de reposição.
- Permitir rastreabilidade básica de entradas, saídas e ajustes.
- Apoiar a operação diária da loja com telas simples e ágeis.
- Fornecer informações claras para decisões de compra e gestão.

## 4. Público-alvo / usuários

- **Proprietário / gestor da ótica**: visão geral do estoque, indicadores e decisões de compra.
- **Responsável pelo estoque / almoxarifado**: entradas, saídas, inventários e ajustes.
- **Vendedores / atendentes**: consulta rápida de disponibilidade e baixa de estoque vinculada a vendas.
- **Eventualmente optometrista ou técnico**: consulta de produtos técnicos (lentes) para montagem.

O sistema deve ser utilizável por pessoas com pouco conhecimento técnico, priorizando clareza e velocidade de operação.

## 5. Escopo

**Incluído:**
- Cadastro e controle de produtos ópticos e seus atributos relevantes.
- Entrada de mercadorias (compras / recebimentos).
- Saída de estoque (vendas, montagens, perdas e ajustes).
- Controle de níveis mínimos e alertas de reposição.
- Consulta de estoque atual e histórico de movimentações.
- Inventário físico e correção de divergências.
- Relatórios básicos de posição de estoque, giro e necessidade de compra.

**Fora do escopo (nesta versão):**
- Sistema completo de PDV ou emissão fiscal.
- Gestão financeira avançada (contas a pagar/receber, fluxo de caixa).
- Integração com laboratórios de lentes ou sistemas de receita oftalmológica externa.
- App mobile nativo (pode ser considerado futuramente).
- Multi-empresas / multi-filiais complexas (pode ser evolutivo).

## 6. Principais funcionalidades

- Cadastro de produtos com atributos específicos de ótica (tipo, marca, modelo, grau, tratamentos, etc.).
- Registro de entradas de estoque (com fornecedor, nota e quantidades).
- Registro de saídas (venda, montagem, perda, ajuste).
- Consulta rápida de disponibilidade e localização de itens.
- Alertas de estoque mínimo e produtos parados.
- Realização de inventário físico e ajuste de divergências.
- Histórico de movimentações por produto.
- Relatórios simples de posição de estoque e necessidade de reposição.
- Controle de usuários e permissões básicas (consulta vs. movimentação).

## 7. Requisitos e restrições importantes

- O sistema deve funcionar bem em ambiente de loja (uso diário, com possíveis interrupções de internet).
- Interface simples e rápida, priorizando operação por teclado e poucos cliques.
- Controle de permissões: nem todos os usuários podem fazer ajustes de inventário ou excluir movimentações.
- Os dados de estoque devem ser consistentes (não permitir saldo negativo sem justificativa controlada).
- O sistema deve registrar quem realizou cada movimentação relevante.
- Deve ser possível exportar dados básicos para análise externa (planilhas).

## 8. Arquitetura tecnológica

- Aplicação web (acesso via navegador).
- Backend em Python.
- Frontend moderno e responsivo.
- Banco de dados relacional.
- Autenticação de usuários com controle de sessão.
- Possibilidade de deploy em servidor próprio ou cloud.

A arquitetura deve permitir evolução futura (novos módulos, integrações e eventual app mobile) sem reescrita completa.

## 9. Princípios de desenvolvimento

- Simplicidade primeiro: preferir soluções claras e manuteníveis.
- Estoque confiável: toda movimentação deve deixar rastros auditáveis.
- Experiência do usuário da loja: telas rápidas e com baixo risco de erro operacional.
- Evolução incremental: começar com o núcleo de estoque e expandir conforme necessidade real.
- Código legível e documentado o suficiente para manutenção futura.

## 10. Segurança e integridade

- Controle de acesso por usuário e perfil.
- Registro de auditoria das principais operações de estoque (quem, quando e o que foi alterado).
- Proteção contra exclusão acidental de movimentações históricas.
- Backup regular dos dados.
- Boas práticas de autenticação e proteção de dados sensíveis da operação.

## 11. Estratégia de desenvolvimento

- Entrega incremental por módulos (cadastro → movimentações → alertas → inventário → relatórios).
- Validação contínua com usuários reais da ótica (feedback rápido).
- Priorização do que gera valor operacional imediato (evitar over-engineering).
- Manter o núcleo de estoque estável antes de adicionar funcionalidades periféricas.

## 12. Fonte de verdade e documentação

- Este documento (`project-overview.md`) é a referência de visão e escopo do projeto.
- Decisões importantes de produto e arquitetura devem ser registradas e mantidas atualizadas.
- Documentação técnica detalhada (APIs, modelo de dados, fluxos específicos) será mantida separadamente e evoluírá conforme o sistema for implementado.
- O overview deve permanecer relativamente estável; mudanças de escopo significativas devem ser refletidas aqui de forma consciente.