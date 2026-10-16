# Proposal: employee-portal

## Why
O Smart Vision necessita de uma plataforma unificada e engajadora voltada aos colaboradores das lojas óticas — o **Portal do Colaborador**. Esta plataforma visa centralizar o acompanhamento de metas individuais e comissões, comunicação interna oficial do RH e diretoria, autoatendimento de RH (holerites, espelho de ponto, solicitações), capacitação técnica com microlearning de produtos ópticos (lentes e armações), e atalhos rápidos para operações cotidianas da loja (PDV, receitas, ordens de serviço e estoque).

## What Changes

- **CHANGE 1: Estrutura Base de Layout e Navegação (Branding & Shell)**
  - Identidade visual com paleta definida: Primária `#3942F6`, Secundária `#F8B807` e Fundo `#F8FAFC`.
  - Header Superior completo com branding SmartVision, pesquisa rápida, central de notificações com badge amarelo (`#F8B807`) de não lidos e card de perfil (Consultor Ótico Senior, loja/filial).
  - Sidebar com navegação intuitiva: "O Meu Painel", "As Minhas Metas", "Mural do RH", "Documentos & Vencimentos", "Treinos SmartVision", "Atalhos do Sistema" e "Gestão de Estoque".

- **CHANGE 2: Painel Dinâmico de Metas e Performance Individual (KPIs)**
  - Barra de progresso visual de meta mensal com patamares visuais (50%, 75%, 100%) em `#3942F6` e `#F8B807`.
  - Exibição de Valor Vendido Acumulado, Meta Individual e Valor Restante.
  - Simulador e extrato de comissões com faixas e projeção de super-metas (Bronze, Prata, Ouro).
  - Métricas diárias: Total Vendido Hoje (valor e quantidade), Ticket Médio e Taxa de Conversão.

- **CHANGE 3: Feed de Comunicação Interna e Mural do RH / Direção**
  - Mural de avisos categorizados (RH, Operacional, Novos Produtos, Formação) com botão de confirmação de leitura ("Marcar como Lido / Ciente").
  - Alertas prioritários e urgentes no topo com destaque em `#F8B807`.
  - Bloco de aniversariantes do mês e destaque do colaborador do mês.

- **CHANGE 4: Central do Colaborador (RH, Documentos e Horários)**
  - Lista expansível de holerites/recibos dos últimos 12 meses com visualização e download simulado.
  - Espelho de ponto digital com banco de horas e horas extras.
  - Formulários de autoatendimento para agendamento de férias, atestados médicos com upload e troca de turno.

- **CHANGE 5: Academia SmartVision (Treinos e Guia Rápido de Produtos)**
  - Guia técnico de lentes oftálmicas: índices de refração, tratamentos antirreflexo e fabricantes parceiros (Essilor, Zeiss, Hoya).
  - Cursos de microlearning com acompanhamento de progresso e emissão de certificados digitais.

- **CHANGE 6: Atalhos de Acesso Rápido ao Sistema Operacional**
  - Acesso rápido a "Nova Venda / PDV", "Ficha de Receita Ótica", "Consultar Estado de OS" e módulo de Estoque integrado.

## Capabilities

### New Capabilities
- `employee-portal`: Portal unificado de colaboração, gestão de metas, comunicação interna e suporte ao consultor óptico.

## Non-goals
- Emissão fiscal de notas ou integração com SEFAZ direta (pertence ao módulo fiscal/PDV backend).
- Assinatura ICP-Brasil de holerites (aqui provê-se visualização e download).

## Impact
- **Frontend Streamlit ([app.py](file:///c:/Users/Matheus%20Alexandre/Desktop/SmartVisionProject/app.py))**: Nova arquitetura modular e estética alinhada com as cores e especificações do projeto.
