// Listar produtos do catálogo com filtros opcionais por categoria e busca
query products verb=GET {
  api_group = "Smart Vision"

  input {
    text category? filters=trim
    text search? filters=trim
  }

  stack {
    db.query product {
      where = ($db.product.category ==? $input.category) && (($input.search == null) || ($db.product.name includes $input.search) || ($db.product.sku includes $input.search))
      sort = {created_at: "desc"}
      return = {type: "list"}
    } as $products
  }

  response = $products
  tags = ["smart-vision"]
  guid = "ucePZpfA6J5Mf0MkaTeeosisgYA"
}