# AGENTS.md — Smart Vision

## Princípio Geral

Este documento define regras obrigatórias para o desenvolvimento do Smart Vision.
Agentes de IA e desenvolvedores devem respeitar essas regras.
Violações deliberadas exigem aprovação explícita de Felipe antes de merged.

---

## 1. Integridade de Estoque (CRÍTICO)

### 1.1 Auditoria é obrigatória
Toda movimentação de estoque — entrada, saída, inventário, ajuste — **deve**:
- Criar um registro de auditoria **antes** de atualizar o saldo no banco.
- Registrar: quem fez, quando, quantidade anterior, quantidade nova, motivo e tipo de movimentação.
- Ser imutável (auditoria não pode ser deletada ou editada).

Se o código não cria auditoria, está errado.

### 1.2 Saldo nunca fica negativo sem controle
- Saldo de um produto não pode ser atualizado para valor negativo sem um registro explícito de ajuste com justificativa.
- Se uma saída tentaria deixar o saldo negativo, deve rejeitar a operação ou exigir aprovação explícita.

### 1.3 Transações atômicas no banco
- Toda operação que afeta saldo e auditoria deve ser uma transação única (begin/commit ou rollback).
- Se a auditoria falhar, a movimentação falha também.
- Nunca deixar saldo atualizado sem auditoria registrada no banco.

---

## 2. Permissões e Controle de Acesso

### 2.1 Backend valida permissões, não confie no frontend
- Toda chamada de API que realiza ação (entrada, saída, ajuste, inventário, mudança de permissão de usuário) **deve validar permissão no backend antes de executar**.
- Não confie em tokens do frontend ou em "o usuário já passou pela tela de permissão".
- Se o código no backend não valida, está errado.

### 2.2 Permissões por perfil
Respeitar os perfis definidos no domain-model.md:
- **Gestor**: acesso a tudo (leitura, movimentações, ajustes, aprovação de inventário).
- **Estoquista**: entradas, saídas, inventário (não aprova, não deleta histórico).
- **Vendedor**: consulta de estoque e baixa de saída vinculada a venda.
- **Técnico**: consulta de produtos técnicos e atributos (leitura).

Não introduzir novos perfis sem aprovação explícita.

### 2.3 Não replicar validação de permissão no frontend
A tela Streamlit pode **esconder** botões se o usuário não tiver permissão, mas isso é UX, não segurança.
A real validação é no backend.

---

## 3. Backend (Python / API)

### 3.1 Respeitar o contrato de API
Se uma rota já existe (mesmo que não totalmente implementada), não mudar assinatura sem coordenação explícita.
Se precisa mudar, abrir um issue/discussion antes de fazer.

### 3.2 Validação de entrada
Todo parâmetro de entrada (body, query, path) deve ser validado:
- Tipo correto (int, string, date, etc).
- Valores dentro do range esperado (quantidade > 0, datas sensatas).
- Campos obrigatórios preenchidos.

Se chegar lixo no backend, devolver erro 400 com mensagem clara, não deixar a validação passar silenciosa.

### 3.3 Erros devem ser legíveis
Exceções e erros devem ser capturados e retornados de forma clara pro frontend.
Não deixar stack trace vazar pro cliente.
Mensagens de erro devem indicar qual campo está errado e por quê.

### 3.4 Logging de operações críticas
Entradas, saídas, ajustes, mudanças de permissão de usuário devem ser logadas (não só auditados no banco, mas também em logs de aplicação).
Se algo deu errado, precisa ser rastreável.

---

## 4. Banco de Dados e Schema

### 4.1 Schema é contrato
Toda mudança no schema (adicionar coluna, deletar tabela, renomear campo) exige aprovação de Felipe antes de executada.
Razão: pode quebrar queries existentes, relatórios ou auditoria.

### 4.2 Migrations são obrigatórias
Se precisa mudar schema, criar uma migration versionada (ex: `001_add_justificativa_to_audit.sql`).
Não executar ALTER TABLE manualmente no banco.
Migrations devem poder rodar incrementalmente (não podem assumir estado anterior).

### 4.3 Dados históricos são sagrados
Nunca deletar registros de `auditoria`, `movimentacao_estoque`, `histórico_inventario` ou qualquer tabela de histórico.
Se precisa "desfazer" algo, criar uma entrada de ajuste/correção que deixe tudo rastreável.

---

## 5. Frontend (Streamlit)

### 5.1 Chamar endpoints corretos
Cada tela Streamlit deve chamar o endpoint certo para a operação.
Validar que a resposta tem o formato esperado antes de usar.

### 5.2 Não duplicar lógica de negócio
Lógica de saldo, cálculo de estoque mínimo, validações de auditoria — tudo fica no backend.
O Streamlit é UI, não lógica.

Se você tá duplicando validação no frontend, está errado.

### 5.3 Tratar erros do backend
Se um endpoint retorna erro, mostrar mensagem clara pro usuário.
Não deixar silent failures ou comportamentos inesperados.

### 5.4 Respeitar permissões do usuário logado
Saber qual é o perfil do usuário atual e adequar a tela:
- Esconder botões que ele não tem permissão.
- Redirecionar pra tela "sem acesso" se ele tentar acessar URL diretamente.

Mas a segurança real é no backend (item 2.1).

---

## 6. Desenvolvimento e Testes

### 6.1 Toda mudança funcional precisa de verificação
Antes de passar pro professor, a mudança precisa ser testada:
- Se é novo endpoint: fazer requisição manualmente ou com script de teste.
- Se é nova tela: validar que chama endpoint correto e trata resposta.
- Se é mudança no banco: validar que dados anteriores ainda funcionam.

Teste automatizado é ideal; se não tiver tempo, teste manual documentado é aceitável (ex: "verificado que entrada com quantidade negativa é rejeitada").

### 6.2 Mudanças críticas exigem code review de Felipe
Crítico = toca backend, banco de dados, permissões, auditoria ou contrato de API.

Não-crítico = ajuste de UI, novo campo cosmético, reorganização de componente Streamlit que não toca lógica.

Se tem dúvida, avise Felipe antes de mexer.

### 6.3 Commits devem ser descritivos
Mensagem deve indicar **o que mudou e por quê**.
Exemplo bom: `"Adicionar auditoria a ajuste de inventário — garante rastreabilidade de correções"`.
Exemplo ruim: `"Fix bug"` ou `"Update".

### 6.4 Não deixar código comentado ou debug no main
Se é código pra debug/teste, deletar antes de merged.
Se é funcionalidade pra depois, abrir um issue — não deixar commented code.

---

## 7. Tecnologias e Restrições

### 7.1 Frontend é Streamlit, ponto final
Não introduzir React, Vue, HTML puro ou outra framework de frontend sem aprovação explícita de Felipe e professor.
Se Streamlit não consegue fazer o que precisa, conversa primeiro.

### 7.2 Backend é Python
Não adicionar Node.js, Go, C# ou outra linguagem pro backend sem aprovação.

### 7.3 Banco é SQL Server
Não mudar pra PostgreSQL, MySQL, SQLite ou outro.
Usar T-SQL conforme necessário.

### 7.4 Dependências novas exigem justificativa
Antes de adicionar novo package (pip install algo), avisar Felipe.
Razão: aumenta complexidade, pode trazer vulnerabilidades, pode conflitar com outras deps.

---

## 8. Documentação e Comunicação

### 8.1 Mudanças no domain-model devem ser explícitas
Se você tá criando uma nova entidade ou mudando relacionamento, atualizar `domain-model.md` **na mesma PR/commit**.
Nunca deixar código e documentação desincronizados.

### 8.2 APIs novas devem ter documentação mínima
Endpoint novo (ex: `POST /api/entrada/`) deve ter comentário no código explicando:
- O que faz.
- Quais parâmetros espera.
- Quais permissões são necessárias.
- Qual auditoria é criada.

### 8.3 Issues/discussões antes de começar
Se algo está vago (ex: "como exatamente o inventário ajusta saldo negativo?"), abra uma discussion no GitHub/Discord antes de implementar.
Não adianta implementar e descobrir depois que era pra ser diferente.

---

## 9. O que NÃO fazer

- ❌ Commitar credentials, senhas, tokens (usar `.env` e `.gitignore`).
- ❌ Fazer `git push -f` (force push) sem avisar Felipe.
- ❌ Deletar branches sem deixar claro por quê.
- ❌ Mexer direto no banco de produção sem backup.
- ❌ Deixar print() ou debug statements no código final.
- ❌ Ignorar erros ("try: ... except: pass" — nunca).
- ❌ Assumir que "se passou no meu PC, está certo" (testar de verdade).

---

## 10. Processo de Review (Felipe)

Quando Felipe revisar seu código:

1. Vai verificar se auditoria foi criada (se mudou estoque).
2. Vai verificar se permissões foram validadas no backend.
3. Vai verificar se esquema do banco foi alterado (deve vir com migration).
4. Vai rodar testes manuais pra garantir que funciona.
5. Vai olhar pra legibilidade e documentação.

Se algo não passar, volta pra você consertar.

---

## 11. Dúvidas?

Se tá em dúvida se algo é crítico, avise Felipe antes de começar a implementar.
Melhor perder 5 minutos perguntando do que gastar 2 horas num código que depois precisa ser refatorado.
