// Consultar detalhes de um inventário físico (Change 03)
// Parâmetro: id (query). Retorna o inventário e o progresso da contagem
// (produtos contados vs. produtos no escopo).
query inventory verb=GET {
  api_group = "Smart Vision"

  input {
    int id
  }

  stack {
    // 1. Buscar o inventário
    db.get inventory {
      field_name = "id"
      field_value = $input.id
    } as $inventory

    precondition ($inventory != null) {
      error_type = "notfound"
      error = "Inventário não encontrado."
    }

    // 2. Contagens registradas neste inventário
    db.query inventory_count {
      where = ($db.inventory_count.inventory_id == $input.id)
      return = {type: "list"}
    } as $counts

    // 3. Produtos no escopo (filtro de categoria, se definido)
    db.query product {
      where = (($inventory.category_filter == null) || ($db.product.category == $inventory.category_filter))
        && (($inventory.location_filter == null) || ($db.product.location == $inventory.location_filter))
      return = {type: "list"}
    } as $scope_products

    var $counted_products {
      value = ($counts != null) ? $counts : 0
    }
    var $products_in_scope {
      value = ($scope_products != null) ? $scope_products : 0
    }
    var $progress {
      value = 0
      if ($products_in_scope > 0) {
        value = ($counted_products / $products_in_scope * 100)
      }
    }

    response = {
      inventory: $inventory
      counts_recorded: $counted_products
      products_in_scope: $products_in_scope
      progress_percent: $progress
    }
    tags = ["smart-vision"]
    guid = "inventory_detail_guid_001"
  }
}
