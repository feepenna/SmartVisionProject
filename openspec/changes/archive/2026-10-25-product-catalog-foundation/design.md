# Design: product-catalog-foundation

## Context

Conforme alinhado na exploração inicial e confirmado pelo usuário, **o backend e a persistência de dados serão centralizados diretamente no Xano** (PostgreSQL na nuvem do Xano, sincronizado localmente via arquivos `.xs` com o Xano CLI). O frontend é implementado exclusivamente em **Streamlit**, comunicando-se com o Xano via requisições HTTP REST.

## Goals / Non-Goals

**Goals:**
- Modelar e criar a tabela `product` no Xano com todos os campos gerais e atributos ópticos.
- Criar endpoints REST no Xano para listagem, filtro e criação de produtos com validação de SKU único.
- Implementar camada de serviço no Streamlit (`services/xano_client.py` ou similar) para encapsular chamadas de API.
- Criar a interface de usuário no Streamlit com visualização de catálogo e formulário de cadastro dinâmico para lentes e armações.

**Non-Goals:**
- Movimentação de estoque (débito/crédito de saldo) — será implementado com motor de auditoria nas Changes subsequentes.
- Autenticação complexa com login screen — para esta Change inicial, utilizaremos uma identificação de operador simplificada via `st.session_state` para assinar o criador do registro.

## Decisions

### 1. Persistência e Backend 100% no Xano
* **Decisão:** A tabela `product` e os endpoints de catálogo residem no Xano (`xano/table/product.xs` e `xano/api/...`).
* **Alternativa considerada:** Criar backend intermediário em FastAPI com SQL Server.
* **Justificativa:** Reduz complexidade operacional e atende diretamente ao setup acadêmico do Xano já autenticado (`x8ki-letl-twmt.n7.xano.io`, workspace Pinguimworks).

### 2. Atributos Técnicos Integrados na Tabela `product` (Desnormalização Pragmática)
* **Decisão:** Os atributos específicos de lentes (`sphere_power`, `cylinder_power`, `axis`, `addition`, `lens_type`, `treatment`, `material`) serão colunas opcionais/nullable na própria tabela `product`, validados condicionalmente pela API com base no campo `category`.
* **Alternativa considerada:** Tabela separada `product_technical_attribute` vinculada 1:1.
* **Justificativa:** Simplifica consultas, paginação e cadastros na primeira versão, mantendo alto desempenho e flexibilidade.

### 3. Comunicação Streamlit ➔ Xano via REST
* **Decisão:** O Streamlit utilizará a biblioteca `requests` para consumir a API pública/autenticada do Xano. A URL base da API será obtida das configurações do workspace (`https://x8ki-letl-twmt.n7.xano.io/api:smart_vision`).

## Risks / Trade-offs

- **[Dependência de Conexão com o Xano]** → Mitigação: Tratamento de exceções e timeout no cliente HTTP do Streamlit com exibição de mensagens amigáveis em caso de falha de conexão.
- **[Concorrência na Criação de SKU]** → Mitigação: Criação de índice único no Xano para o campo `sku` para garantir unicidade a nível de banco de dados.

## Migration Plan

1. Criar a tabela `product` no Xano (via painel/XanoScript).
2. Criar o grupo de API `smart_vision` e os endpoints de produtos no Xano.
3. Executar `xano workspace pull -d ./xano` para sincronizar os arquivos `.xs` localmente.
4. Implementar a tela do Streamlit e validar o fluxo completo.
