# Specification: Employee Portal

## Purpose
Estabelecer a interface integrada do Portal do Colaborador SmartVision para consultores ópticos e equipe de loja, englobando metas, RH, comunicação, academia e atalhos operacionais.

## ADDED Requirements

### Requirement: Layout Branding and Shell Navigation
The system MUST provide a unified shell utilizing primary color `#3942F6`, secondary highlight color `#F8B807`, and background `#F8FAFC`. The header MUST display the SmartVision logo, search bar, notification badge in `#F8B807`, and employee profile card. The sidebar MUST provide navigation across all portal sections.

#### Scenario: Display portal shell and header
- **WHEN** o colaborador acessa a aplicação
- **THEN** o sistema exibe o cabeçalho superior com perfil ("Consultor Ótico Senior"), contador de avisos e a navegação lateral nas cores especificadas

### Requirement: Goals and KPI Performance Tracking
The system MUST calculate and display monthly goal progress with visual tiers (50%, 75%, 100%), accumulated sales, remaining balance, commission simulation with super-goal tiers (Bronze, Prata, Ouro), and daily performance metrics (sales today, ticket médio, conversion rate).

#### Scenario: View monthly goal and commission simulation
- **WHEN** o usuário visualiza o painel de metas
- **THEN** a barra de progresso exibe a evolução percentual e o simulador calcula a comissão projetada conforme os patamares atingidos

### Requirement: Internal Communication and Notice Board
The system MUST render company notices organized by category, highlight priority banners with `#F8B807` borders, allow employees to mark notices as acknowledged, and feature monthly birthdays and employee recognition.

#### Scenario: Acknowledge company notice
- **WHEN** o colaborador clica em "Marcar como Lido / Ciente" em um comunicado
- **THEN** o status do aviso é atualizado para ciente e o contador de não lidos é decrementado

### Requirement: Employee Central HR and Time Tracking
The system MUST provide paystub history with preview/download, time tracking balance summary, and self-service request forms for vacation scheduling, medical certificate submission with file upload, and shift change.

#### Scenario: Submit medical certificate
- **WHEN** o usuário anexa um atestado e envia o formulário
- **THEN** o sistema valida os dados obrigatórios e confirma a submissão com recibo

### Requirement: SmartVision Academy and Product Guide
The system MUST include a comparative matrix of optical lenses, refractive indices, and coatings, alongside microlearning training modules with progress tracking and digital certificate issuance.

#### Scenario: Check optical lens specifications
- **WHEN** o consultor consulta o guia de materiais
- **THEN** a matriz exibe as características de espessura, proteção e marcas parceiras (Essilor, Zeiss, Hoya)

### Requirement: Operational Shortcuts
The system MUST provide quick-access launchers for Point of Sale (PDV), Optical Prescription Entry, and Order Service (OS) tracking.

#### Scenario: Launch optical prescription shortcut
- **WHEN** o usuário seleciona o atalho de receita
- **THEN** os campos de parâmetros ópticos para conferência e lançamento são disponibilizados
