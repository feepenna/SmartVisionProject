// Processar operacao de saida: efetiva baixa via logica equivalente a stock_exit (Change 04)
// Reutiliza validacoes de saldo negativo e grava em stock_movement (auditoria previa)
query outbound_process verb=POST {
  api_group = "Smart Vision"

  input {
    int id
    int user_id
  }

  stack {
    db.get stock_outbound {
      field_name = "id"
      field_value = $input.id
    } as $outbound

    precondition ($outbound != null) {
      error_type = "notfound"
      error = "Operacao nao encontrada."
    }

    precondition ($outbound.status != "Concluida") {
      error_type = "badrequest"
      error = "Operacao ja concluida."
    }

    precondition ($outbound.status != "Rejeitada" && $outbound.status != "Cancelada") {
      error_type = "badrequest"
      error = "Nao e possivel processar operacao rejeitada ou cancelada."
    }

    conditional {
      if ($outbound.stock_movement_id != null) {
        precondition (false) {
          error_type = "badrequest"
          error = "Operacao ja possui movimentacao vinculada (idempotencia)."
        }
      }
    }

    db.get product {
      field_name = "id"
      field_value = $outbound.product_id
    } as $product

    precondition ($product != null) {
      error_type = "notfound"
      error = "Produto nao encontrado."
    }

    precondition ($product.current_stock >= $outbound.quantity) {
      error_type = "badrequest"
      error = "Estoque insuficiente. Saida deixaria saldo negativo."
    }

    var $new_stock {
      value = $product.current_stock - $outbound.quantity
    }

    // Grava movimentacao de saida (reutiliza ledger Change 02)
    db.add stock_movement {
      data = {
        product_id: $outbound.product_id
        movement_type: "exit"
        quantity: $outbound.quantity
        previous_stock: $product.current_stock
        new_stock: $new_stock
        reason: $outbound.reason
        user_id: $input.user_id
        justification: $outbound.justification
        reference_text: "outbound:" + $outbound.id
      }
    } as $audit

    db.edit product {
      field_name = "id"
      field_value = $outbound.product_id
      data = { current_stock: $new_stock }
    } as $updated_product

    db.edit stock_outbound {
      field_name = "id"
      field_value = $input.id
      data = {
        status: "Concluida"
        stock_movement_id: $audit.id
        processed_at: "now"
        approved_by: $input.user_id
        approved_at: "now"
      }
    } as $updated_outbound
  }

  response = { outbound: $updated_outbound, movement: $audit, product: $updated_product }
  tags = ["smart-vision"]
  guid = "outbound_process_guid_001"
}
