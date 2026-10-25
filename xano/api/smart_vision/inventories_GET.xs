// Listar inventários físicos (Change 03)
// Permissão: qualquer usuário autenticado. Leitura; não altera estoque.
// Filtros opcionais: status, opened_by.
// Retorna também o progresso da contagem por inventário:
// counts_recorded (contagens registradas) e products_in_scope (produtos no escopo).
// O percentual detalhado também está disponível em GET /inventory?id=.
query inventories verb=GET {
  api_group = "Smart Vision"
  auth = "user"

  input {
    text? status? filters=trim
    int? opened_by?
  }

  stack {
    db.query inventory {
      where = (($input.status == null) || ($db.inventory.status == $input.status)) && (($input.opened_by == null) || ($db.inventory.opened_by == $input.opened_by))
      sort = {created_at: "desc"}
      return = {type: "list"}
      addon = [
        {
          name : "inventory_counts"
          input: {inventory_id: $output.id}
          as   : "counts_recorded"
        }
        {
          name : "inventory_scope"
          input: {category_filter: $output.category_filter, location_filter: $output.location_filter}
          as   : "products_in_scope"
        }
      ]
    } as $inventories

  }

  response = $inventories
  tags = ["smart-vision"]
  guid = "inventory_list_guid_001"
}
