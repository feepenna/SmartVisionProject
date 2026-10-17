// Tabela de auditoria de decisões de divergência (Smart Vision - Change 03)
// Registra cada decisão (aprovação, rejeição, solicitação de recontagem) com
// usuário, data, ação e justificativa, preservando o histórico de decisões.
table inventory_decision {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    int inventory_id
    int product_id
    int discrepancy_id
    text action filters=trim
    int decided_by
    timestamp decided_at?=now
    text? justification filters=trim
    text? previous_status filters=trim
    text? notes filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "inventory_id", op: "asc"}]}
    {type: "btree", field: [{name: "discrepancy_id", op: "asc"}]}
    {type: "btree", field: [{name: "decided_at", op: "desc"}]}
  ]

  tags = ["smart-vision"]
  guid = "inventory_decision_guid_001"
}
