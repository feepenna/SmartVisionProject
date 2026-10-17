// Consultar divergências de conciliação de um inventário (Change 03)
query inventory_discrepancies verb=GET {
  api_group = "Smart Vision"

  input {
    int inventory_id
    text? status
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

    // 2. Listar divergências, mais recente primeiro
    db.query inventory_discrepancy {
      where = ($db.inventory_discrepancy.inventory_id == $input.inventory_id)
        && (($input.status == null) || ($db.inventory_discrepancy.status == $input.status))
      sort = {created_at: "desc"}
      return = {type: "list"}
    } as $discrepancies

    response = (($discrepancies != null) ? $discrepancies : [])
    tags = ["smart-vision"]
    guid = "inventory_discrepancy_list_guid_001"
  }
}
