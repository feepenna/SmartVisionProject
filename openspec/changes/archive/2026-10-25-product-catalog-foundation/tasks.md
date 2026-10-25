# Tasks

## 1. Modelagem e Endpoints no Xano

- [x] 1.1 Criar a tabela `product` no Xano com campos gerais (`sku`, `name`, `category`, `brand`, `model`, `cost_price`, `sale_price`, `current_stock`, `min_stock`, `location`) e campos ópticos (`sphere_power`, `cylinder_power`, `axis`, `addition`, `lens_type`, `treatment`, `material`), adicionando índice único para `sku` e verificando schema ativo.
  - Verificado no workspace live: tabela `product` ativa com os campos desta change e índice `btree|unique` em `sku`. Os campos `target_stock`, `inactivity_days` e `alerts_enabled` existem apenas no arquivo local e pertencem à Change 05 (não foram publicados aqui).
- [x] 1.2 Criar endpoints `GET /products` (listagem com filtros) e `POST /products` (criação com validação de campos obrigatórios e condicional de lentes) no Xano, verificando resposta via requisição de teste.
  - `GET` aceita ausência de filtros, categoria isolada, busca isolada e ambos. `POST` rejeita SKU duplicado, preço/estoque negativo, lente sem atributos técnicos e eixo fora de 0–180; cria com saldo inicial 0.
- [x] 1.3 Executar `xano workspace pull -d ./xano` e verificar se os arquivos locais `xano/table/product.xs` e endpoints foram atualizados corretamente no repositório.
  - Pull executado em diretório temporário (`/tmp/opencode/xano_pull`) para não sobrescrever alterações locais pendentes de outras changes. `products_GET.xs` e `products_POST.xs` conferem com o live (apenas diferenças de formatação/quebra de linha); a tabela live contém o schema desta change. O pull direto no workspace local não foi feito para preservar mudanças ainda não publicadas da Change 04/05.

## 2. Camada de Serviço e Dependências no Frontend

- [x] 2.1 Adicionar `requests` ao arquivo `requirements.txt`, instalar no ambiente virtual `.venv` e verificar importação bem-sucedida.
  - `requirements.txt` já contém `requests`; importação validada no `.venv`.
- [x] 2.2 Criar o módulo `services/xano_client.py` com funções para listar e criar produtos integrados à URL da API do Xano, verificando tratamento de erros de conexão e resposta.
  - `list_products(filters)` envia somente filtros informados e `create_product(payload)` publica no Xano. Erros HTTP são propagados com o corpo da resposta. Regras de UX/filtros ficam em `services/product_catalog.py`.

## 3. Interface no Streamlit

- [x] 3.1 Atualizar o layout no Streamlit ([`app.py`](file:///home/zerotrust/Documents/project_innovation/meu-projeto/app.py)) para incluir navegação para "Catálogo de Produtos" com tabela interativa e filtros por categoria e busca textual.
  - Nova opção `📋 Catálogo de Produtos` no menu, aba de consulta com busca por SKU/nome, filtro por categoria, métricas e tabela.
- [x] 3.2 Criar o formulário de cadastro de produtos com renderização dinâmica de campos técnicos para categorias de lentes e validações de tela, verificando feedback visual de sucesso ou erro.
  - Formulário com campos gerais obrigatórios e campos ópticos renderizados apenas para `Lente Oftálmica`/`Lente de Contato`. Validação de tela para obrigatórios, preço/estoque e atributos de lentes; sucesso exibe ID e recarrega a consulta.

## 4. Validação Ponta a Ponta

- [x] 4.1 Cadastrar uma armação de teste e uma lente oftálmica com parâmetros de grau pela interface do Streamlit e verificar que ambos aparecem corretamente na tabela e foram persistidos no Xano.
  - E2E live via API e Streamlit AppTest: armação ID 4 (`E2E-ARM-20261025155155`) e lente ID 5 (`E2E-LEN-20261025155155`, esf. -2.50, cil. -0.75, eixo 180) persistidas com saldo 0; cadastro adicional pela UI (IDs 6 e 7, `E2E-UI-20261025155312` e `E2E-AUTH-20261025160403`) confirmou o caminho completo do formulário, inclusive com token real. Consultas por busca e categoria retornaram os registros. Após a correção de auth, `GET/POST` sem token retornam 401; com token `member`/`admin` autenticam e o `POST` mantém as validações. Os dados E2E permanecem no catálogo para rastreabilidade.

## Notas de escopo

- **Correção de segurança pós-arquivo (2026-10-25)**: `GET/POST /products` agora exigem `auth = "user"` no Xano. O `POST` valida o perfil do usuário no backend e permite `Gestor`, `Gerente`, `Supervisor`, `Estoquista`, `admin` e `member` legado; `Vendedor` e `Técnico` são bloqueados. A normalização fina dos perfis e o RBAC granular continuam previstos na Change 07.
- A publicação foi limitada aos dois endpoints do catálogo para não enviar mudanças pendentes de outras features.
