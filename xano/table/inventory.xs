// Tabela de cabeçalho de inventário físico (Smart Vision - Change 03)
// Registra abertura, escopo, status e ciclo de vida de cada inventário.
table inventory {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    text status filters=trim
    text scope filters=trim
    text? category_filter filters=trim
    text? location_filter filters=trim
    int opened_by
    timestamp opened_at?=now
    timestamp? closed_at
    text? notes filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "status", op: "asc"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "opened_by", op: "asc"}]}
  ]

  tags = ["smart-vision"]
  guid = "inventory_guid_001"
}
