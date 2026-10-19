// Tabela central de produtos e atributos técnicos do Smart Vision
table product {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    text sku filters=trim
    text name filters=trim
    text category filters=trim
    text? brand filters=trim
    text? model filters=trim
    decimal? cost_price
    decimal sale_price
    int current_stock
    int min_stock
    text? location filters=trim

    // Parâmetros de reposição e alertas (Change 05)
    // target_stock nulo = sem alvo definido (sinalizado como falta de parâmetros)
    int? target_stock
    // inactivity_days nulo = janela padrão de 30 dias
    int? inactivity_days
    bool alerts_enabled?=true
  
    // Atributos técnicos ópticos (obrigatórios conceitualmente para lentes)
    decimal? sphere_power
  
    decimal? cylinder_power
    int? axis
    decimal? addition
    text? lens_type filters=trim
    text? treatment filters=trim
    text? material filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "sku", op: "asc"}]}
    {type: "btree", field: [{name: "category", op: "asc"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["smart-vision"]
  guid = "oUMjsWsf_9ZUSFCLzyTZUhO89hI"
}