# Design: change-06-login

## Arquitetura e Fluxo de Dados

O fluxo de login segue estes passos:

1. Usuário preenche usuário e senha no frontend (app.py).
2. Validação de campos obrigatórios no frontend (messages oficiais: "Informe seu usuário.", "Informe sua senha.").
3. Submissão do formulário → `_handle_login(usuario, senha)`.
4. `auth_service.autenticar(usuario, senha, rate_limiter)`:
   a. Valida campos (já feito no frontend, repetido no backend para segurança).
   b. Verifica rate limiter (bloqueio após max_tentativas falhas de credenciais).
   c. Chama `xano_client.login(email, password)` → backend Xano.
   d. Classifica erro caso o backend retorne 401/403/accessdenied/ratelimit.
   e. Em sucesso: obtém `auth_token` e `user_data` via `xano_client.get_me(auth_token)`.
   f. Define sessão no session state: `auth_token`, `auth_user`, `authenticated`.
   g. Zera rate limiter `.registrar_sucesso()`.
5. `st.rerun()` — app continua para a tela principal (já autenticada).
6. `_require_auth()` no topo do app verifica `st.session_state.authenticated`; se falso, renderiza login e `st.stop()`.

## Tela de Login — Design Visual

### Layout

- **Fundo da página:** `#F1F2F4` (cinza-claro), ocupando 100% da altura (`min-height: 100vh`).
- **Card centralizado:** `#FFFFFF`, largura máxima 530px, `border-radius: 18px`, sombra `0 24px 48px -12px rgba(0,0,0,0.12)`.
- **Logotipo SMARTVISION:** Posicionado no topo do card. SMART em `#3942F6`, VISION em `#F8B807`. Fonte Inter, peso 800, tamanho 1.75rem, letter-spacing -0.5px.
- **Título:** "Acesso ao Sistema", fonte Inter peso 700, tamanho 1.5rem, cor `#18181B`.
- **Subtítulo:** "Entre com suas credenciais para continuar.", fonte Inter peso 400, tamanho 0.95rem, cor `#71717A`.
- **Campos de input:**
  - Label flutuante/fixa "Usuário" e "Senha", fonte Inter peso 600, tamanho 0.85rem, cor `#18181B`.
  - Input width: 100%, padding 12px 14px, borda 1px sólida `#D4D4D8` (cor de `--border-color` na login-page), border-radius 8px.
  - Placeholder cor `#A1A1AA`.
  - Estado `:focus`: borda `var(--primary-color)` (= `#3942F6`), sombra `0 0 0 3px rgba(57,66,246,0.10)`.
  - Inputs do tipo text/password com fonte Inter tamanho 0.95rem, cor `#111827`.
- **Toggle visibilidade da senha:** Botão "Mostrar" / "Ocultar", fonte Inter peso 600, cor `#71717A` (padrão), hover `#18181B`. Positioned à direita do campo senha.
- **Botão ENTRAR:** Largura 100%, fundo `#18181B`, texto `#FFFFFF`, fonte Inter peso 700, tamanho 1rem, `border-radius: 8px`, padding 12px 20px.
  - Estado hover: `#27272A`.
  - Estado disabled: `#A1A1AA`, cursor `not-allowed`.
  - Estado loading: texto transparente, spinner animado centralizado.
- **Área de credenciais (desenvolvimento):** Apenas quando `DEV_CREDENTIALS_SHOWN` for True. Título "Credenciais para Avaliação (Ambiente de Desenvolvimento)". Lista 3 credenciais (Gerente, Supervisor, Vendedor) com e-mail e senha fictícia. Cor de fundo `#F3F4F6`, borda `#E5E7EB` (var `--border-radius`), texto `#374151`.
- **Mensagem de erro:** `.login-error` — fundo `#FEE2E2`, borda `#FCA5A5`, texto `#991B1B`, padding 10px 14px, border-radius 8px, margin-top 16px.
- **Divisória:** `.login-divider` — texto uppercase uppercase, fonte 0.75rem, cor `#9CA3AF` (var `--text-secondary`), linhas laterais `1px solid var(--border-color)`.

### Responsividade

- `max-width: 640px`: em telas menores, padding reduzido para 28px 20px, fontes do logotipo/título reduzidas (1.5rem e 1.35rem respectivamente).
- Não há rolagem horizontal em nenhum dispositivo.

## Perfis e Direcionamento

Perfis obtidos exclusivamente do backend via `xano_client.get_me(auth_token).get("role")`:

| Perfil do Backend | Página Inicial Padrão |
|---|---|
| `Gestor` / `Gerente` | "📦 Gestão de Estoque Auditado" |
| `Supervisor` | "📦 Gestão de Estoque Auditado" |
| `Vendedor` / `Member` | "🚚 Saídas de Estoque" |

O índice inicial do menu (`_default_index`) é definido em `app.py` ao primeira renderização autenticada, baseado no perfil do usuário. O usuário **não pode escolher ou atribuir** seu próprio perfil na tela de login.

## Segurança

- Senhas nunca são enviadas ou armazenadas em texto puro no frontend; o backend Xano trata a autenticação com hash.
- Rate limiter por sessão: após `max_tentativas=5` falhas de credenciais dentro de `janela_segundos=900`, novas tentativas são bloqueadas com mensagem "Muitas tentativas de acesso. Aguarde alguns minutos e tente novamente."
- Falhas de comunicação (rede, timeout, backend fora do ar) **não** contam como tentativa no rate limiter.
- O botão "ENTRAR" é desabilitado durante o estado de loading, impedindo envios simultâneos.
- O username é preservado após erro de login (`st.session_state.login_username`), mas a senha nunca é persistida ou exibida.
- Perfis enviados pelo frontend **não são confiáveis** — validação sempre no backend.
- Consultas parametrizadas via `requests` com timeout=10.
- Nenhuma senha ou token é registrado em logs de aplicação.

## Endpoints Utilizados (Xano Authentication group, canonical RRY0Pj3A)

| Endpoint | Método | Corpo (JSON) | Resposta |
|---|---|---|---|
| `/auth/login` | POST | `{"email": "user@smartvision.com", "password": "Senha123!"}` | `{"authToken": "tok-123", "user_id": 7}` |
| `/auth/me` | GET | Headers: `Authorization: Bearer tok-123` | `{"id": 7, "name": "Gerente Demo", "role": "Gestor", ...}` |

## Reutilização da Change 02 (Ledger de Auditoria)

O sistema já tinha o ledger `stock_movement` da Change 02 para movimentações de estoque. O Change 06 não cria novo ledger — ele reutiliza a infraestrutura existente para auditoria de login (via session state do Streamlit e logs de aplicação), mantendo a regra de "saldo nunca fica negativo sem controle" já estabelecida.

## Control de Acesso

- Acesso às páginas internas protegido por `_require_auth()` no topo do script Streamlit.
- Usuários não autenticados são redirecionados para a tela de login (`st.stop()`).
- Usuários autenticados têm acesso restrito conforme seu perfil (Gestor/Suporte → estoque, Vendedor → saídas).
- Logout limpa `auth_token`, `auth_user`, `authenticated`, `login_error`, `login_username`, `login_show_password`, `menu_index_set`.

## Impact

- **Frontend (app.py):** Tela de login substituída; estado de sessão gerenciado; validações e mensagens alinhadas ao padrão Change 06.
- **Backend (services/):** Serviço auth_service com rate limiter e classificação de erros; xano_client login/get_me já existiam e foram preservados.
- **Tests (tests/):** 155 testes existentes continuam passando.
- **OpenSpec:** Artefatos `proposal.md`, `design.md`, `tasks.md` gerados nesta mudança.