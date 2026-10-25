// Listar produtos do catálogo com filtros opcionais por categoria e busca.
// Sem autenticação por escopo desta Change; a integração de auth/RBAC está
// prevista na Change 07. A leitura não altera estoque.
query products verb=GET {
  api_group = "Smart Vision"

  input {
    text? category? filters=trim
    text? search? filters=trim
  }

  stack {
    db.query product {
      where = (($input.category == null) || ($input.category == "") || ($db.product.category == $input.category)) && (($input.search == null) || ($input.search == "") || ($db.product.name includes $input.search) || ($db.product.sku includes $input.search))
      sort = {created_at: "desc"}
      return = {type: "list"}
    } as $products
  }

  response = $products
  tags = ["smart-vision"]
  guid = "ucePZpfA6J5Mf0MkaTeeosisgYA"
}
