// Tabela de alertas de estoque e reposição (Smart Vision - Change 05)
// Ciclo de vida: Ativo -> EmAcompanhamento -> Resolvido.
// Registros são preservados (histórico nunca é apagado); a avaliação idempotente
// garante no máximo UM alerta aberto por (product_id, alert_type).
// Não cria saldo paralelo: deriva de product.current_stock e stock_movement.
table stock_alert {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    int product_id
    // LOW_STOCK (saldo <= min_stock) | INACTIVE (sem movimentação na janela)
    text alert_type filters=trim
    // Ativo | EmAcompanhamento | Resolvido
    text status filters=trim
    // Classificação do produto no momento da detecção: critico | insuficiente | regular
    text criticality filters=trim
    int? observed_stock
    int? observed_min_stock
    timestamp? detected_at
    timestamp? status_updated_at
    timestamp? resolved_at
    // condicao_normalizada | movimentacao_registrada | manual
    text? resolution filters=trim
    // Quando a condição deixou de valer por avaliação (permite novo ciclo depois)
    timestamp? condition_cleared_at
    int? opened_by
    // Usuário da última mudança manual de status (null = mudança automática)
    int? updated_by
    text? notes filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "product_id", op: "asc"}]}
    {type: "btree", field: [{name: "status", op: "asc"}]}
    {type: "btree", field: [{name: "alert_type", op: "asc"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["smart-vision"]
  guid = "stock_alert_guid_001"
}
