````
# Domain Model — Smart Vision

Este documento apresenta o modelo conceitual consolidado do sistema **Smart Vision**, descrevendo seus conceitos fundamentais e relacionamentos sem dependência de fornecedores.

---

## 1. Visão Geral do Domínio

```text
               ┌───────────────────────┐
               │    Usuário / Perfil   │
               └───────────┬───────────┘
                           │ (realiza / auditado por)
                           ▼
               ┌───────────────────────┐
               │ Movimentação Est. (H) │
               └───────────▲───────────┘
                           │ (origina registro)
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────┴──────┐   ┌───────┴──────┐   ┌───────┴──────────────┐
│  EntradaEst. │   │   SaídaEst.  │   │  InventárioFísico    │
└───────┬──────┘   └───────┬──────┘   └───────┬──────────────┘
        │                  │                  │ (avalia / ajusta)
        ▼                  ▼                  │
┌──────────────┐   ┌──────────────┐           │
│ ItemEntrada  │   │  ItemSaída   │           │
└───────┬──────┘   └───────┬──────┘           │
        │                  │                  │
        └──────────┬───────┴──────────────────┘
                   │
                   ▼
        ┌─────────────────────┐       ┌──────────────────────┐
        │   Produto Óptico    ├──────►│  Atributos Técnicos  │
        └──────────┬──────────┘       └──────────────────────┘
                   │
    ┌──────────────┴──────────────────────┐
    ▼                                     ▼
┌──────────────────┐          ┌──────────────────────────┐
│ Alerta Reposição │          │ Pedido / Receita (Ref.)  │
└──────────────────┘          └──────────────────────────┘
````

## 2. Entidades do Domínio

**Produto Óptico**

- **Descrição**: Item comercializado ou mantido em loja (armações, lentes, acessórios e produtos de limpeza).
    
- **Responsabilidade**: Controlar saldo em tempo real, preços e localização na loja.
    
- **Atributos**: SKU/Código, Nome, Categoria, Marca, Modelo, Preço de Custo/Venda, Saldo Atual, Estoque Mínimo, Estoque Alvo (`target_stock`), Janela de Inatividade (`inactivity_days`) e Monitoramento de Alertas (`alerts_enabled`).
    
- **Relacionamentos**: Possui Atributos Técnicos, participa de Entradas/Saídas, gera Alertas e Sugestões de Reposição e registra Histórico de Movimentações.
    
- **Regras**: Saldo não pode ficar negativo sem justificativa; definição de estoque mínimo é obrigatória. Produto recém-cadastrado nasce com `alerts_enabled = true`, sem alvo (`target_stock` nulo) e janela padrão de 30 dias; `target_stock`, quando definido, deve ser maior ou igual ao estoque mínimo.
    

**Atributos Técnicos do Produto**

- **Descrição**: Especificações técnicas inerentes a lentes oftálmicas e de contato.
    
- **Responsabilidade**: Armazenar parâmetros ópticos para montagem de óculos e conferência com receitas.
    
- **Atributos**: Grau Esférico, Grau Cilíndrico, Eixo, Adição, Tipo de Lente, Tratamento e Material.
    
- **Relacionamentos**: Pertence a um Produto Óptico.
    
- **Regras**: Obrigatório para lentes; ausente/opcional para demais categorias.
    

**Entrada de Estoque (e Item de Entrada)**

- **Descrição**: Registro formal de recebimento e incorporação de novas mercadorias.
    
- **Responsabilidade**: Incrementar a quantidade disponível no estoque e registrar o valor de custo.
    
- **Atributos**: Nº do Documento/Nota, Data de Recebimento, Valor Total, Quantidade Recebida e Custo Unitário.
    
- **Relacionamentos**: Registrada por Usuário; vincula-se ao Produto Óptico e gera Histórico.
    
- **Regras**: Confirmação atualiza o saldo imediatamente; não permite exclusão direta (exige movimentação de ajuste ou estorno).
    

**Saída de Estoque (e Item de Saída)**

- **Descrição**: Registro de retirada de produtos por venda, montagem, avaria ou perda.
    
- **Responsabilidade**: Decrementar o saldo em estoque e manter a justificativa da baixa.
    
- **Atributos**: Motivo da Saída, Data, Observações, Quantidade Baixada e Preço Praticado.
    
- **Relacionamentos**: Registrada por Usuário; pode associar-se a um Pedido de Cliente ou Receita.
    
- **Regras**: Exige motivo obrigatoriamente classificado.
    

**Movimentação de Estoque / Histórico (Audit Ledger)**

- **Descrição**: Registro cronológico de auditoria de qualquer variação de saldo.
    
- **Responsabilidade**: Garantir rastreabilidade total (quem, quando, quantidade e motivo).
    
- **Atributos**: Data/Hora, Tipo de Movimentação, Quantidade, Saldo Anterior, Saldo Resultante e Motivo.
    
- **Relacionamentos**: Vincula-se a Produto Óptico, Usuário, Entrada, Saída ou Inventário.
    
- **Regras**: Imutável (proibida a alteração ou exclusão de registros).
    

**Inventário Físico (e Item de Inventário)**

- **Descrição**: Processo periódico de contagem física de itens na loja.
    
- **Responsabilidade**: Conciliar o estoque real com o sistema e autorizar correções de divergências por meio de um fluxo controlado.

- **Atributos**: Identificador, data de abertura, responsável, escopo (completo / categoria / localização), filtros de categoria e localização, status, data de abertura e data de encerramento.

- **Estados e transições**: `Aberto` → `EmContagem` → `AguardandoAprovacao` → `Concluido`, com possibilidade de `EmContagem` → `Aberto` e `AguardandoAprovacao` → `EmContagem` (recontagem). Um inventário `Concluido` não pode ser alterado retroativamente.

- **Relacionamentos**: Conduzido por Usuário; gera Contagens Físicas, Divergências de Conciliação, Decisões do Gestor e Movimentações de Ajuste ao ser concluído.

- **Regras**: Não altera o saldo durante a contagem; impede inventários conflitantes sobre o mesmo escopo (salvo regra explícita); somente gestores aprovam/rejeitam divergências; o responsável pela contagem não aprova a própria divergência (separação de funções); ajustes são aplicados por meio da tabela `stock_movement` (movement_type = "adjustment") com auditoria prévia e idempotência.

**Contagem Física (Item de Inventário)**

- **Descrição**: Registro da quantidade física encontrada para um produto dentro de um inventário.
    
- **Responsabilidade**: Capturar o estoque real produto a produto, permitindo salvar o progresso e retomar posteriormente.

- **Atributos**: Inventário associado, produto contado, quantidade física encontrada, usuário responsável, data/hora do registro, indicador de recontagem, vínculo ao registro anterior (para preservar histórico de recontagens) e observações.

- **Relacionamentos**: Pertence a um Inventário e a um Produto; registrado por um Usuário.

- **Regras**: Não cria registros duplicados indevidos para o mesmo produto e inventário (uma nova contagem não-recount atualiza a existente); recontagens criam um novo registro vinculado ao anterior sem sobrescrevê-lo; o saldo de estoque não é alterado durante a contagem.

**Divergência de Conciliação**

- **Descrição**: Resultado da comparação entre a quantidade física contada e o saldo de referência do sistema para um produto.

- **Responsabilidade**: Classificar a divergência e rastrear a decisão do gestor até a aplicação do ajuste.

- **Atributos**: Quantidade física contada, quantidade de referência (preservada), diferença absoluta, classificação (`sem divergência` / `falta de estoque` / `sobra de estoque`), impacto no saldo, situação da análise (pendente / aprovada / rejeitada / recontagem solicitada), usuário e data da decisão, justificativa, indicador de ajuste aplicado e vínculo à movimentação de auditoria.

- **Relacionamentos**: Pertence a um Inventário e a um Produto; vinculada a uma ou mais Decisões e, quando aprovada, a uma Movimentação de Estoque.

- **Regras**: Os valores de referência utilizados na conciliação são preservados para rastreabilidade; uma divergência rejeitada não gera movimentação de ajuste; o ajuste é aplicado uma única vez (idempotência); movimentações concorrentes entre a contagem e a aprovação são tratadas comparando o saldo atual com a referência.

**Decisão de Divergência (Auditoria de Decisões)**

- **Descrição**: Registro de cada decisão tomada por um gestor sobre uma divergência (aprovação, rejeição ou solicitação de recontagem).

- **Responsabilidade**: Preservar o histórico de decisões para rastreabilidade e conformidade.

- **Atributos**: Divergência associada, ação (`approved` / `rejected` / `recount_requested`), usuário gestor, data/hora da decisão, justificativa e status anterior da divergência.

- **Relacionamentos**: Pertence a um Inventário, a um Produto e a uma Divergência; decidido por um Usuário.

- **Regras**: Somente usuários autorizados (perfil Gestor) podem decidir; toda decisão registra usuário, data, ação e justificativa; o histórico não é sobrescrito.
    

**Alerta de Estoque**

- **Descrição**: Notificação rastreável sobre níveis de estoque, aberta por avaliação idempotente das condições por produto (Change 05).
    
- **Responsabilidade**: Sinalizar ruptura (`LOW_STOCK`, saldo ≤ mínimo) e produtos parados sem giro (`INACTIVE`, sem movimentação além da janela), controlando o ciclo de vida de cada condição.
    
- **Atributos**: Produto, Tipo (`LOW_STOCK` / `INACTIVE`), Status (`Ativo` / `EmAcompanhamento` / `Resolvido`), Criticidade (`critico` / `insuficiente` / `regular`), Saldo e Mínimo Observados na abertura, data de detecção, data da última mudança de status, data de resolução, origem da resolução (`manual` / `condicao_normalizada`), data em que a condição normalizou, usuários de abertura/atualização e observações.
    
- **Estados e transições**: `Ativo` → `EmAcompanhamento`; `Ativo`/`EmAcompanhamento` → `Resolvido`. `Resolvido` é estado final; nenhum registro é apagado.
    
- **Relacionamentos**: Associado a um Produto Óptico e aberto/atualizado por um Usuário.
    
- **Regras**: No máximo um alerta aberto por par (produto, tipo); a avaliação é idempotente (reavaliar sem mudança não duplica); quando a condição normaliza, o alerta aberto é auto-resolvido com `resolution = "condicao_normalizada"` e `condition_cleared_at` registrado; uma resolução manual com a condição ainda valendo silencia a reabertura do alerta até a condição normalizar; produto sem histórico nunca gera alerta `INACTIVE`; nenhum alerta altera saldo.

**Sugestão de Reposição**

- **Descrição**: Recomendação de quantidade a repor por produto, derivada exclusivamente do cadastro (não persistida como documento).
    
- **Responsabilidade**: Orientar a decisão de compra do gestor sem gerar compras, pedidos ou entradas.
    
- **Atributos**: Produto, Saldo atual, Estoque mínimo, Estoque alvo, Classificação de criticidade, Quantidade sugerida (`max(0, alvo − saldo)`), sinalizador de parâmetros incompletos e custo estimado.
    
- **Relacionamentos**: Derivada do Produto Óptico.
    
- **Regras**: Sem estoque alvo, a sugestão é vazia e o produto é sinalizado como parâmetros incompletos; a sugestão nunca é negativa e nunca provoca movimentação de estoque.

    

**Pedido / Receita (Referência Externa)**

- **Descrição**: Vínculo operacional com a ordem de venda ou prescrição médica.
    
- **Responsabilidade**: Rastrear a destinação do produto baixado para o cliente ou laboratório.
    
- **Atributos**: Identificador do Pedido/Receita, Nome do Cliente e Data de Atendimento.
    
- **Relacionamentos**: Vincula-se opcionalmente a uma Saída de Estoque.
    

**Usuário / Perfil**

- **Descrição**: Operador do sistema com credenciais de acesso.
    
- **Responsabilidade**: Autenticar ações e definir permissões na loja.
    
- **Atributos**: Nome, E-mail/Login, Perfil (Gestor, Supervisor, Estoquista, Vendedor, Técnico — além dos perfis legados `admin`, equivalente a Gestor, e `member`, equivalente a leitura) e Status.
    
- **Relacionamentos**: Executa e assina Entradas, Saídas, Inventários, Históricos, Alertas e Parâmetros de Estoque.
    
- **Regras**: Ajustes manuais de saldo e aprovação de inventário exigem perfil autorizado. No módulo de alertas (Change 05): leitura para todos os perfis; avaliação de alertas e mudança de status para Gestor, Estoquista e `admin`; configuração de parâmetros de estoque somente para Gestor e `admin`. A permissão é sempre validada no backend. Change 06: o perfil **Supervisor** foi incluído no enum `role` da tabela `user` (aprovação de Felipe) e na hierarquia de permissões do backend — abaixo de Gestor/`admin` (atribuição de roles exige Gestor/`admin`) e no mesmo nível de Estoquista/Técnico para demais operações administrativas; o login busca o perfil exclusivamente do backend e o frontend apenas adapta a UI (a validação real é server-side).