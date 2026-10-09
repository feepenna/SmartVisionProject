# Proposal: product-catalog-foundation

## Why

O Smart Vision necessita de uma estrutura para catalogar e gerenciar produtos ópticos (armações, lentes oftálmicas, lentes de contato, acessórios e limpeza) antes de permitir movimentações de estoque, auditoria e controle de reposição.
Esta mudança estabelece o modelo de dados de produtos no Xano, endpoints para CRUD/consulta e a interface no Streamlit para cadastro e visualização de estoque, permitindo a operação essencial da ótica sem ainda acoplar fluxos de entrada/saída de lotes.

## What Changes

- **Backend & Banco no Xano:**
  - Criação da tabela `product` no Xano com campos gerais (`sku`, `name`, `category`, `brand`, `model`, `cost_price`, `sale_price`, `current_stock`, `min_stock`, `location`, `created_at`).
  - Criação de campos/atributos técnicos específicos para lentes (`sphere_power`, `cylinder_power`, `axis`, `addition`, `lens_type`, `treatment`, `material`).
  - Endpoints no Xano para listagem (`GET /api:smart_vision/products`), busca por SKU/nome/categoria e criação de produto (`POST /api:smart_vision/products`).
- **Frontend no Streamlit:**
  - Tela de consulta e busca rápida de produtos com tabela interativa, filtros por categoria e busca textual.
  - Formulário intuitivo de cadastro de produtos, exibindo condicionalmente os atributos técnicos quando a categoria selecionada for "Lente Oftálmica" ou "Lente de Contato".
  - Comunicação via API REST direta entre o Streamlit e o Xano.
- **Não-Objetivos (Non-goals / Fora de escopo desta Change):**
  - Não inclui entrada formal de mercadorias com fornecedor e nota fiscal (escopo da Change 3).
  - Não inclui baixa de estoque (venda/perda) nem regras de auditoria avançada (escopo da Change 2 e 4).
  - Não inclui inventário físico ou conciliação periódica (escopo futuro).

## Capabilities

### New Capabilities
- `product-catalog`: Cadastro, parametrização técnica e consulta do catálogo de produtos ópticos no Xano com interface operacional no Streamlit.

### Modified Capabilities
<!-- Nenhuma especificação existente modificada (primeira change do projeto). -->

## Impact

- **Xano / XanoScript:** Novas tabelas e endpoints criados no workspace Xano e sincronizados localmente na pasta `xano/`.
- **Streamlit:** Atualização de `app.py` ou módulos de página para navegação entre Dashboard e Catálogo de Produtos.
- **Dependências:** Inclusão de biblioteca de requisições HTTP (`requests`) para o Streamlit consumir as APIs do Xano.
