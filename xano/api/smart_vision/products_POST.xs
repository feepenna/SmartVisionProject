// Cadastrar um novo produto no catálogo
query products verb=POST {
  api_group = "Smart Vision"

  input {
    text sku filters=trim
    text name filters=trim
    text category filters=trim
    text? brand filters=trim
    text? model filters=trim
    decimal? cost_price
    decimal sale_price
    int min_stock
    text? location filters=trim
  
    // Atributos ópticos (lentes)
    decimal? sphere_power
  
    decimal? cylinder_power
    int? axis
    decimal? addition
    text? lens_type filters=trim
    text? treatment filters=trim
    text? material filters=trim
  }

  stack {
    // 1. Validar estoque mínimo não negativo
    precondition ($input.min_stock >= 0) {
      error_type = "inputerror"
      error = "O estoque mínimo deve ser maior ou igual a zero."
    }
  
    // 2. Validar obrigatoriedade de campos ópticos quando for lente
    conditional {
      if ($input.category == "Lente Oftálmica" || $input.category == "Lente de Contato") {
        precondition ($input.sphere_power != null) {
          error_type = "inputerror"
          error = "O grau esférico é obrigatório para lentes."
        }
      }
    }
  
    // 3. Validar se o SKU já existe
    db.has product {
      field_name = "sku"
      field_value = $input.sku
    } as $sku_exists
  
    precondition (!$sku_exists) {
      error_type = "badrequest"
      error = "O SKU informado já está em uso por outro produto."
    }
  
    // 4. Inserir o produto
    db.add product {
      data = {
        sku           : $input.sku
        name          : $input.name
        category      : $input.category
        brand         : $input.brand
        model         : $input.model
        cost_price    : $input.cost_price
        sale_price    : $input.sale_price
        current_stock : 0
        min_stock     : $input.min_stock
        location      : $input.location
        sphere_power  : $input.sphere_power
        cylinder_power: $input.cylinder_power
        axis          : $input.axis
        addition      : $input.addition
        lens_type     : $input.lens_type
        treatment     : $input.treatment
        material      : $input.material
        created_at    : "now"
      }
    } as $new_product
  }

  response = $new_product
  tags = ["smart-vision"]
  guid = "CmgIQXv3OLXYUpTrBg9QU0KLUpE"
}