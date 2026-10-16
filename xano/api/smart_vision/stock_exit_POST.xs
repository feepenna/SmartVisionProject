// Registrar saída de estoque (venda, perda, ajuste) com bloqueio de saldo negativo e auditoria prévia
query stock_exit verb=POST {
  api_group = "Smart Vision"

  input {
    int product_id
    int quantity
    text reason filters=trim
    text? justification filters=trim
    text? reference_text filters=trim
    int? user_id
  }

  stack {
    // 1. Validar quantidade positiva e motivo obrigatório
    precondition ($input.quantity > 0) {
      error_type = "inputerror"
      error = "A quantidade de saída deve ser maior que zero."
    }

    precondition ($input.reason != null && $input.reason != "") {
      error_type = "inputerror"
      error = "O motivo da movimentação é obrigatório."
    }

    // 2. Validar justificativa para reasons LOSS ou DAMAGE
    conditional {
      if ($input.reason == "LOSS" || $input.reason == "DAMAGE") {
        precondition ($input.justification != null && $input.justification != "") {
          error_type = "inputerror"
          error = "A justificativa é obrigatória quando o motivo é LOSS ou DAMAGE."
        }
      }
    }

    // 3. Buscar o produto
    db.get product {
      field_name = "id"
      field_value = $input.product_id
    } as $product

    precondition ($product != null) {
      error_type = "notfound"
      error = "Produto não encontrado."
    }

    // 4. Validar se há saldo suficiente (evitar saldo negativo sem controle)
    precondition ($product.current_stock >= $input.quantity) {
      error_type = "badrequest"
      error = "Estoque insuficiente. A saída deixaria o saldo negativo."
    }

    // 5. Calcular novos valores
    var $new_stock {
      value = $product.current_stock - $input.quantity
    }

    // 6. Gravar auditoria (stock_movement) ANTES de atualizar o saldo
    db.add stock_movement {
      data = {
        product_id     : $input.product_id
        movement_type  : "exit"
        quantity       : $input.quantity
        previous_stock : $product.current_stock
        new_stock      : $new_stock
        reason         : $input.reason
        user_id        : $input.user_id
        created_at     : "now"
        justification  : $input.justification
        reference_text : $input.reference_text
      }
    } as $audit_record

    // 7. Atualizar o saldo do produto
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
  guid = "stock_exit_guid_001"
}
