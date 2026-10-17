// Listar contagens físicas de um inventário (Change 03)
query inventory_counts verb=GET {
  api_group = "Smart Vision"

  input {
    int inventory_id
  }

  stack {
    // 1. Validar inventário
    db.get inventory {
      field_name = "id"
      field_value = $input.inventory_id
    } as $inventory

    precondition ($inventory != null) {
      error_type = "notfound"
      error = "Inventário não encontrado."
    }

    // 2. Listar contagens, mais recente primeiro
    db.query inventory_count {
      where = ($db.inventory_count.inventory_id == $input.inventory_id)
      sort = {counted_at: "desc"}
      return = {type: "list"}
    } as $counts

    response = (($counts != null) ? $counts : [])
    tags = ["smart-vision"]
    guid = "inventory_count_list_guid_001"
  }
}
