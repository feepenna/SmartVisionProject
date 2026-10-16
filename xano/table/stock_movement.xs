// Tabela de auditoria e registro de movimentações de estoque (Smart Vision)
table stock_movement {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    int product_id
    text movement_type filters=trim
    int quantity
    int previous_stock
    int new_stock
    text reason filters=trim
    int? user_id
    decimal? unit_cost
    text? supplier_id filters=trim
    text? invoice filters=trim
    text? batch_id filters=trim
    text? justification filters=trim
    text? reference_text filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "product_id", op: "asc"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["smart-vision"]
  guid = "stock_movement_guid_001"
}
