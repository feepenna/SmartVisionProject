// Registrar entrada de mercadoria no estoque com auditoria obrigatória
query stock_entry verb=POST {
  api_group = "Smart Vision"

  input {
    int product_id
    int quantity
    decimal unit_cost
    text supplier_id? filters=trim
    text invoice? filters=trim
    text batch_id? filters=trim
    text reason filters=trim
    int user_id?
  }

  stack {
    // 1. Validar quantidade positiva, custo e motivo obrigatório
    precondition ($input.quantity > 0) {
      error_type = "inputerror"
      error = "A quantidade de entrada deve ser maior que zero."
    }

    precondition ($input.unit_cost >= 0) {
      error_type = "inputerror"
      error = "O custo unitário deve ser maior ou igual a zero."
    }

    precondition ($input.reason != null && $input.reason != "") {
      error_type = "inputerror"
      error = "O motivo da movimentação é obrigatório."
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

    // 3. Calcular novos valores
    var $new_stock {
      value = $product.current_stock + $input.quantity
    }

    // 4. Gravar auditoria (stock_movement) ANTES de atualizar o saldo
    db.add stock_movement {
      data = {
        product_id     : $input.product_id
        movement_type  : "entry"
        quantity       : $input.quantity
        previous_stock : $product.current_stock
        new_stock      : $new_stock
        reason         : $input.reason
        user_id        : $input.user_id
        created_at     : "now"
        unit_cost      : $input.unit_cost
        supplier_id    : $input.supplier_id
        invoice        : $input.invoice
        batch_id       : $input.batch_id
      }
    } as $audit_record

    // 5. Atualizar o saldo do produto
    db.edit product {
      field_name = "id"
      field_value = $input.product_id
      data = {
        current_stock : $new_stock
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
