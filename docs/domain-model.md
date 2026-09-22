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
    
- **Atributos**: SKU/Código, Nome, Categoria, Marca, Modelo, Preço de Custo/Venda, Saldo Atual, Estoque Mínimo e Localização Física.
    
- **Relacionamentos**: Possui Atributos Técnicos, participa de Entradas/Saídas, gera Alertas e registra Histórico de Movimentações.
    
- **Regras**: Saldo não pode ficar negativo sem justificativa; definição de estoque mínimo é obrigatória.
    

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
    
- **Responsabilidade**: Conciliar o estoque real com o sistema e autorizar correções de divergências.
    
- **Atributos**: Período (Início/Fim), Status, Quantidade no Sistema, Quantidade Contada, Divergência e Justificativa.
    
- **Relacionamentos**: Conduzido por Usuário; gera Movimentações de Ajuste ao ser concluído.
    
- **Regras**: Atualiza o saldo do sistema para bater com o físico e lança histórico de auditoria.
    

**Alerta de Reposição**

- **Descrição**: Notificação automática sobre níveis de estoque.
    
- **Responsabilidade**: Sinalizar necessidade de compra (estoque mínimo) ou itens parados sem giro.
    
- **Atributos**: Tipo de Alerta, Urgência e Data de Detecção.
    
- **Relacionamentos**: Associado a um Produto Óptico.
    
- **Regras**: Disparado sempre que o saldo for menor ou igual ao Estoque Mínimo.
    

**Pedido / Receita (Referência Externa)**

- **Descrição**: Vínculo operacional com a ordem de venda ou prescrição médica.
    
- **Responsabilidade**: Rastrear a destinação do produto baixado para o cliente ou laboratório.
    
- **Atributos**: Identificador do Pedido/Receita, Nome do Cliente e Data de Atendimento.
    
- **Relacionamentos**: Vincula-se opcionalmente a uma Saída de Estoque.
    

**Usuário / Perfil**

- **Descrição**: Operador do sistema com credenciais de acesso.
    
- **Responsabilidade**: Autenticar ações e definir permissões na loja.
    
- **Atributos**: Nome, E-mail/Login, Perfil (Gestor, Estoquista, Vendedor, Técnico) e Status.
    
- **Relacionamentos**: Executa e assina Entradas, Saídas, Inventários e Históricos.
    
- **Regras**: Ajustes manuais de saldo e aprovação de inventário exigem perfil autorizado.