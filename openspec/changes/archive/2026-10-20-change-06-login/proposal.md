# Proposal: change-06-login

## Why

O Smart Vision precisa de um sistema de autenticação seguro e integrado para controlar o acesso dos usuários aos dashboards e módulos da plataforma. Sem login, nenhum usuário consegue acessar o sistema, e não há controle de perfil (Gestor, Supervisor, Vendedor) para direcionamento adequado das páginas internas. Além disso, não há proteção contra tentativas repetidas de login, nem rastreabilidade de auditoria para as operações de acesso.

O sistema já tinha uma estrutura parcial de autenticação (services/auth_service.py, services/xano_client.py com endpoints login e get_me), mas a tela de login no frontend (app.py) precisava ser moderna, mínima e visualmente consistente com a identidade visual da marca, e as credenciais de demonstração precisavam ser configuradas para ambiente de desenvolvimento, passando pelo fluxo real de autenticação sem bypass de segurança.

## What Changes

- **Frontend (Streamlit - app.py):**
  - Tela de login redesenhada com fundo cinza-claro `#F1F2F4`, card centralizado com bordas arredondadas 18px, sombra suave.
  - Logotipo SMARTVISION com SMART em `#3942F6` e VISION em `#F8B807`.
  - Campos de usuário e senha com labels, placeholders e input estilizados.
  - Botão "ENTRAR" ocupando largura total, com estados loading, hover e desabilitado.
  - Toggle de visibilidade/ocultação da senha com rótulo em texto (sem emojis).
  - Validação de campos obrigatórios no frontend com mensagens oficiais da Change 06.
  - Área discreta de credenciais para ambiente de desenvolvimento, visível somente quando configurada.
  - Indicador de carregamento durante autenticação.
  - Preservação do username digitado após erros de login.

- **Backend (services/auth_service.py e services/xano_client.py):**
  - Serviço de autenticação centralizado com validação de campos, rate limiter contra tentativas repetidas, classificação de erros (credenciais inválidas vs falha de comunicação), proteção contra lockout backend.
  - Integração com Xano Authentication group (canonical RRY0Pj3A) via login(email, password) e get_me(auth_token).
  - Perfis obtidos exclusivamente do backend: Gestor, Supervisor, Vendedor.
  - Rate limiter por sessão que conta apenas falhas de credenciais (não falhas de comunicação).
  - Zera contador após login bem-sucedido.

- **Segurança:**
  - Senhas nunca armazenadas em texto puro ou registradas em logs.
  - Hash seguro no backend (Xano trata a autenticação).
  - Proteção contra tentativas repetidas de login (rate limiter).
  - Consultas parametrizadas via requests library.
  - Validação de perfil no backend, não confiando em dados enviados pelo frontend.

- **Fluxo de navegação:**
  - Após login válido, usuário direcionado ao dashboard correspondente ao perfil (Gestor → Estoque, Supervisor → Estoque, Vendedor → Saídas).
  - Páginas internas protegidas por `_require_auth()` — `st.stop()` se não autenticado.
  - Logout seguro que limpa token, usuário e estado da sessão.

## Capabilities

### New Capabilities

- `login`: Autenticação de usuário via Xano Authentication group, retorno de token e dados do usuário (incluindo perfil).
- `logout`: Encerramento seguro da sessão, limpeza de estado.
- Tela de login UI: interface moderna, responsiva e coerente com o design system do Smart Vision.

## Non-goals (Fora de Escopo Desta Change)

- Criação de novo banco de dados de usuários (já existente no Xano).
- Recuperação de senha/esqueci minha senha.
- Cadastro público de novos usuários.
- MFA (autenticação multifator).
- Integração com provedores OAuth externos.

## Impact

- **Streamlit (app.py):** Tela de login substituída por versão moderna; estado de sessão gerenciado; validações e mensagens de erro alinhadas.
- **Python (services/):** Serviço auth_service refinado com rate limiter e classificação de erros; xano_client login/get_me já existiam e foram preservados.
- **Tests (tests/):** 155 testes existentes continuam passando; novos testes de interface não são necessários (foco em backend).
- **OpenSpec:** Novo artefato `openspec/changes/change-06-login/` criado com proposal, design e tasks.

## References

- AGENTS.md — Seção 2 (Permissões e Controle de Acesso), Seção 3 (Backend), Seção 4 (Banco de Dados e Schema), Seção 5 (Frontend), Seção 6 (Desenvolvimento e Testes).
- services/auth_service.py — Serviço de autenticação Change 06.
- services/xano_client.py — Endpoints login e get_me Change 06.
- tests/test_auth_service.py — Testes automatizados Change 06.
- tests/test_auth_client.py — Testes de endpoints de autenticação.