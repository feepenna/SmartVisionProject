// Tabela de operações de saída de estoque (Smart Vision - Change 04)
// Registra solicitações/processamento de saídas com tipos (SALE, LAB_SHIPMENT, LOSS, OPERATIONAL)
// e controle de estados. Integra com stock_movement (ledger existente da Change 02).
table stock_outbound {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    text type filters=trim
    text status filters=trim
    int product_id
    int quantity
    int user_id
    int? approved_by
    timestamp? approved_at
    text reason filters=trim
    text? justification filters=trim
    text? reference_type filters=trim
    text? reference_id filters=trim
    text? destination filters=trim
    text? notes filters=trim
    int? stock_movement_id
    timestamp? processed_at
    text? failure_reason filters=trim
    text? idempotency_key filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "type", op: "asc"}]}
    {type: "btree", field: [{name: "status", op: "asc"}]}
    {type: "btree", field: [{name: "product_id", op: "asc"}]}
    {type: "btree", field: [{name: "user_id", op: "asc"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "idempotency_key", op: "asc"}]}
  ]

  tags = ["smart-vision"]
  guid = "stock_outbound_guid_001"
}
