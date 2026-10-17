// Listar inventários físicos (Change 03)
// Filtros opcionais: status, opened_by.
// Retorna status, responsável, datas e contagens registradas por inventário.
query inventories verb=GET {
  api_group = "Smart Vision"

  input {
    text? status
    int? opened_by
  }

  stack {
    db.query inventory {
      where = (($input.status == null) || ($db.inventory.status == $input.status))
        && (($input.opened_by == null) || ($db.inventory.opened_by == $input.opened_by))
      sort = {created_at: "desc"}
      return = {type: "list"}
    } as $inventories

    response = (($inventories != null) ? $inventories : [])
    tags = ["smart-vision"]
    guid = "inventory_list_guid_001"
  }
}
