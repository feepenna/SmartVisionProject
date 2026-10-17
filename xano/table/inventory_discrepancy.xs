// Tabela de divergências de conciliação (Smart Vision - Change 03)
// Armazena o resultado da comparação entre quantidade física contada e saldo
// de referência, a decisão do gestor e o vínculo com a movimentação de ajuste.
// Os valores de referência (counted_quantity, reference_quantity) são preservados
// para garantir rastreabilidade.
table inventory_discrepancy {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    int inventory_id
    int product_id
    int counted_quantity
    int reference_quantity
    int difference
    text divergence_type filters=trim
    text impact filters=trim
    text status filters=trim
    int? reviewed_by
    timestamp? reviewed_at
    text? review_notes filters=trim
    bool adjustment_applied
    int? adjustment_movement_id
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "inventory_id", op: "asc"}]}
    {type: "btree", field: [{name: "product_id", op: "asc"}]}
    {type: "btree", field: [{name: "status", op: "asc"}]}
  ]

  tags = ["smart-vision"]
  guid = "inventory_discrepancy_guid_001"
}
