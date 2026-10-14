// Registrar entrada de mercadoria no estoque com auditoria obrigatória
query stock_entry verb=POST {
  api_group = "Smart Vision"

  input {
    int product_id
    int quantity
    text reason filters=trim
    int? user_id
  }

  stack {
    // 1. Validar quantidade positiva
    precondition ($input.quantity > 0) {
      error_type = "inputerror"
      error = "A quantidade de entrada deve ser maior que zero."
    }

    // 2. Buscar o produto
    db.get product {
      field_name = "id"
      field_value = $input.product_id
    } as $product

    precondition ($product != null) {
      error_type = "notfound"
      error = "Produto não encontrado."
    }

    // 3. Gravar auditoria (stock_movement) ANTES de atualizar o saldo
    db.add stock_movement {
      data = {
        product_id     : $input.product_id
        movement_type  : "entry"
        quantity       : $input.quantity
        previous_stock : $product.current_stock
        new_stock      : $product.current_stock + $input.quantity
        reason         : $input.reason
        user_id        : $input.user_id
        created_at     : "now"
      }
    } as $audit_record

    // 4. Atualizar o saldo do produto
    db.edit product {
      field_name = "id"
      field_value = $input.product_id
      data = {
        current_stock : $product.current_stock + $input.quantity
      }
    } as $updated_product
  }

  response = {
    audit: $audit_record,
    product: $updated_product
  }
  tags = ["smart-vision"]
  guid = "stock_entry_guid_001"
}
