# Tasks

## 1. Modelagem e Endpoints no Xano

- [ ] 1.1 Criar a tabela `product` no Xano com campos gerais (`sku`, `name`, `category`, `brand`, `model`, `cost_price`, `sale_price`, `current_stock`, `min_stock`, `location`) e campos ópticos (`sphere_power`, `cylinder_power`, `axis`, `addition`, `lens_type`, `treatment`, `material`), adicionando índice único para `sku` e verificando schema ativo.
- [ ] 1.2 Criar endpoints `GET /products` (listagem com filtros) e `POST /products` (criação com validação de campos obrigatórios e condicional de lentes) no Xano, verificando resposta via requisição de teste.
- [ ] 1.3 Executar `xano workspace pull -d ./xano` e verificar se os arquivos locais `xano/table/product.xs` e endpoints foram atualizados corretamente no repositório.

## 2. Camada de Serviço e Dependências no Frontend

- [ ] 2.1 Adicionar `requests` ao arquivo `requirements.txt`, instalar no ambiente virtual `.venv` e verificar importação bem-sucedida.
- [ ] 2.2 Criar o módulo `services/xano_client.py` com funções para listar e criar produtos integrados à URL da API do Xano, verificando tratamento de erros de conexão e resposta.

## 3. Interface no Streamlit

- [ ] 3.1 Atualizar o layout no Streamlit ([`app.py`](file:///home/zerotrust/Documents/project_innovation/meu-projeto/app.py)) para incluir navegação para "Catálogo de Produtos" com tabela interativa e filtros por categoria e busca textual.
- [ ] 3.2 Criar o formulário de cadastro de produtos com renderização dinâmica de campos técnicos para categorias de lentes e validações de tela, verificando feedback visual de sucesso ou erro.

## 4. Validação Ponta a Ponta

- [ ] 4.1 Cadastrar uma armação de teste e uma lente oftálmica com parâmetros de grau pela interface do Streamlit e verificar que ambos aparecem corretamente na tabela e foram persistidos no Xano.
