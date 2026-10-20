# Tasks: change-06-login (Change 06)

1. [x] Criar especificação OpenSpec (proposal, design, tasks) — Concluído
2. [x] Implementar tela de login no frontend (app.py) — Concluído
   - Fundo cinza-claro `#F1F2F4`, card centralizado, bordas 18px, sombra suave
   - Logotipo SMARTVISION (SMART `#3942F6`, VISION `#F8B807`)
   - Campos usuário e senha com labels, placeholders, validação frontend
   - Botão ENTRAR largura total, estados loading/hover/desabilitado
   - Toggle visibilidade da senha com rótulo "Mostrar"/"Ocultar" (sem emojis)
   - Área credenciais desenvolvimento condicional
   - Responsividade (desktop, notebook, tablet, celular)
3. [x] Integrar autenticação real no backend (services/auth_service.py)
   - Validação de campos com mensagens oficiais
   - Rate limiter contra tentativas repetidas
   - Classificação de erros (credenciais inválidas × falha de comunicação)
   - Integração xano_client.login() e xano_client.get_me()
   - Perfis obtidos exclusivamente do backend (Gestor, Supervisor, Vendedor)
4. [x] Implementar direcionamento por perfil após login
   - `_perfil_para_pagina_inicial()` mapeia perfil → índice do menu
   - Gestor/Supervisor → Estoque; Vendedor → Saídas
   - Usuário não escolhe perfil na login screen
5. [x] Proteger páginas internas com `_require_auth()`
   - `st.stop()` se não autenticado
   - Verificação de perfil no backend, não no frontend
6. [x] Implementar logout seguro
   - Limpa auth_token, auth_user, authenticated, login_error, login_username, login_show_password, menu_index_set
   - Botão "Sair / Logout" na sidebar
7. [x] Testes automatizados — executar e verificar
   - `python -m pytest tests/` — 155 testes passando
8. [x] Verificar CSS e cores conforme especificação visual
   - Cores de fundo, bordas, textos e botões atualizados
   - Variáveis CSS `--bg-color`, `--text-main`, `--text-secondary`, `--border-color`, `--primary-color`, `--text-placeholder` usadas corretamente
9. [x] Documentar mudança no OpenSpec (proposal.md, design.md, tasks.md)
10. [x] Revisar diff com mudanças anteriores (inventory-reconciliation, product-catalog-foundation, stock-outbound-operations)
11. [x] Confirmar que nenhuma senha é registrada em logs ou armazenada indevidamente
12. [x] Executar aplicação `streamlit run app.py` e conferir tela de login visualmente