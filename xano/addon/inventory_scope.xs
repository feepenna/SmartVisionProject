// Addon: total de produtos no escopo do inventário (Change 03).
// Escopo completo (sem filtros) conta todos os produtos; categoria/localização
// aplicam o filtro correspondente, igual ao detalhe do inventário.
addon inventory_scope {
  input {
    text? category_filter?
    text? location_filter?
  }

  stack {
    db.query product {
      where = (($input.category_filter == null) || ($db.product.category == $input.category_filter)) && (($input.location_filter == null) || ($db.product.location == $input.location_filter))
      return = {type: "count"}
    }
  }

  guid = "inventory_scope_addon_guid_001"
}
