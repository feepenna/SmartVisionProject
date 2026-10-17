// Tabela de contagens físicas de inventário (Smart Vision - Change 03)
// Registra a quantidade física encontrada por produto, com suporte a recontagens
// que preservam o histórico anterior (não sobrescreve destrutivamente).
table inventory_count {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    int inventory_id
    int product_id
    int quantity_counted
    int counted_by
    timestamp counted_at?=now
    bool is_recount
    int? previous_count_id
    text? notes filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "inventory_id", op: "asc"}]}
    {type: "btree", field: [{name: "product_id", op: "asc"}]}
    {type: "btree", field: [{name: "counted_at", op: "desc"}]}
  ]

  tags = ["smart-vision"]
  guid = "inventory_count_guid_001"
}
