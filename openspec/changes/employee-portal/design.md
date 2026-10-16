# Design: employee-portal

## 1. UI Architecture & Design System

### Design Tokens
- `--primary-color: #3942F6;` (Azul SmartVision: menus, botões primários, cabeçalhos, barras de progresso base).
- `--secondary-color: #F8B807;` (Amarelo Ouro: badges de notificações, destaques de patamares, estados ativos, avisos urgentes).
- `--bg-color: #F8FAFC;` (Neutro claro / Slate 50 para fundo e contrastes).
- Cartões em estilo glassmorphic/flat moderno com bordas sutis `rgba(57, 66, 246, 0.12)`.

### Componentes de Interface
1. **Header Component**:
   - Logomarca SmartVision e saudação contextual.
   - Campo de busca global para avisos e manuais.
   - Notificações com badge contador em `#F8B807`.
   - Card de perfil do colaborador: Avatar, Nome ("Carlos Eduardo Silveira"), Cargo ("Consultor Ótico Senior"), Unidade ("Loja Matriz — Centro").

2. **Sidebar Navigation**:
   - Menu estilizado com seletor de visualização:
     - `O Meu Painel` (Visão geral integrada)
     - `As Minhas Metas & Comissões` (Métricas e simulação)
     - `Mural do RH & Comunicação` (Avisos e aniversários)
     - `Documentos & Horários` (Holerites, ponto, solicitações)
     - `Academia SmartVision` (Guia de lentes e cursos)
     - `Atalhos Operacionais` (PDV, Receitas, OS)
     - `Gestão de Estoque` (Módulo anterior de entradas/saídas auditadas)

## 2. Modelagem de Dados & Fluxos por Módulo

### CHANGE 2: Metas & Performance
- Estrutura de Meta Mensal:
  - Meta individual: R$ 60.000,00.
  - Vendas acumuladas: R$ 46.800,00 (78%).
  - Patamares de superação: Bronze (R$ 50k, 2% comissão), Prata (R$ 60k, 3%), Ouro (R$ 70k+, 4.5%).
- Métricas Diárias:
  - Vendas Hoje: R$ 3.850,00 (6 atendimentos).
  - Ticket Médio: R$ 641,66.
  - Taxa de Conversão: 75% (6 vendas em 8 orçamentos).

### CHANGE 3: Comunicação & RH
- Avisos Oficiais estruturados com ID, data, título, categoria, conteúdo e indicador de urgente/prioritário.
- Estado de confirmação de leitura mantido em `st.session_state` por usuário.
- Destaque do Colaborador do Mês e lista de aniversariantes.

### CHANGE 4: Central do Colaborador
- Histórico de 12 meses de folha de pagamento (competência, salário base, comissões, descontos, valor líquido) com gerador/mock para download.
- Ponto digital: saldo do banco de horas (ex: +12h30min) e horas registradas na semana.
- Formulários com validação para solicitação de férias, troca de turno e upload de atestado com feedback visual.

### CHANGE 5: Academia SmartVision
- Matriz técnica de lentes oftálmicas:
  - 1.50 (CR-39), 1.56 (Médio Índice), 1.59 (Policarbonato), 1.67 (Alto Índice), 1.74 (Ultra Alto Índice).
  - Tratamentos: Crizal Rock/Sapphire (Essilor), DuraVision Platinum (Zeiss), Hi-Vision LongLife (Hoya).
- Microlearning:
  - Curso "Como vender lentes multifocais premium" (85% completo).
  - Curso "Ajuste e alinhamento de armações de titânio" (100% completo, certificado emitido).

### CHANGE 6: Atalhos Operacionais
- Ações rápidas para emissão de orçamentos, abertura de ficha de prescrição óptica (OD/OE esférico, cilíndrico, eixo, adição) e verificação de ordens de serviço em laboratório.
