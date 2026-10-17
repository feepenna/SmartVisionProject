// Registrar ou solicitar operacao de saida de estoque (Change 04)
query outbound verb=POST {
  api_group = "Smart Vision"

  input {
    text type filters=trim
    int product_id
    int quantity
    int user_id
    text reason filters=trim
    text? justification filters=trim
    text? reference_type filters=trim
    text? reference_id filters=trim
    text? destination filters=trim
    text? notes filters=trim
    text? idempotency_key filters=trim
    text? status filters=trim
  }

  stack {
    precondition ($input.quantity > 0) {
      error_type = "inputerror"
      error = "A quantidade deve ser maior que zero."
    }

    precondition ($input.reason != null && $input.reason != "") {
      error_type = "inputerror"
      error = "O motivo e obrigatorio."
    }

    db.get product {
      field_name = "id"
      field_value = $input.product_id
    } as $product

    precondition ($product != null) {
      error_type = "notfound"
      error = "Produto nao encontrado."
    }

    conditional {
      if ($input.type == "LOSS") {
        precondition ($input.justification != null && $input.justification != "") {
          error_type = "inputerror"
          error = "Justificativa obrigatoria para perda (LOSS)."
        }
      }
    }

    conditional {
      if ($input.idempotency_key != null && $input.idempotency_key != "") {
        db.query stock_outbound {
          where = ($db.stock_outbound.idempotency_key == $input.idempotency_key)
          return = {type: "single"}
        } as $existing

        precondition ($existing == null) {
          error_type = "badrequest"
          error = "Operacao ja registrada com esta idempotency_key."
        }
      }
    }

    var $initial_status {
      value = (($input.status != null && $input.status != "") ? $input.status : "Pendente")
    }

    db.add stock_outbound {
      data = {
        type: $input.type
        status: $initial_status
        product_id: $input.product_id
        quantity: $input.quantity
        user_id: $input.user_id
        reason: $input.reason
        justification: $input.justification
        reference_type: $input.reference_type
        reference_id: $input.reference_id
        destination: $input.destination
        notes: $input.notes
        idempotency_key: $input.idempotency_key
      }
    } as $outbound
  }

  response = $outbound
  tags = ["smart-vision"]
  guid = "outbound_create_guid_001"
}
