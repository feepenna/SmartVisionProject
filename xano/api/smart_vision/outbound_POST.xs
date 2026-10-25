// Registrar ou solicitar operação de saída de estoque (Change 04)
// Permissão: qualquer usuário autenticado; o solicitante é sempre $auth.id.
// O status inicial é definido pelo backend:
// - LOSS: AguardandoAprovacao (exige gestor para processar)
// - SALE/LAB_SHIPMENT/OPERATIONAL: Pendente (processável pelo solicitante/gestor)
query outbound verb=POST {
  api_group = "Smart Vision"
  auth = "user"

  input {
    text type filters=trim
    int product_id
    int quantity
    text reason filters=trim
    text? justification? filters=trim
    text? reference_type? filters=trim
    text? reference_id? filters=trim
    text? destination? filters=trim
    text? notes? filters=trim
    text? idempotency_key? filters=trim
  }

  stack {
    // 0. Validar tipo, quantidade, motivo e existência do produto
    precondition ($input.type == "SALE" || $input.type == "LAB_SHIPMENT" || $input.type == "LOSS" || $input.type == "OPERATIONAL") {
      error_type = "inputerror"
      error = "Tipo de saída inválido. Use: SALE, LAB_SHIPMENT, LOSS ou OPERATIONAL."
    }

    precondition ($input.quantity > 0) {
      error_type = "inputerror"
      error = "A quantidade deve ser maior que zero."
    }

    precondition ($input.reason != null && $input.reason != "") {
      error_type = "inputerror"
      error = "O motivo é obrigatório."
    }

    db.get product {
      field_name = "id"
      field_value = $input.product_id
    } as $product

    precondition ($product != null) {
      error_type = "notfound"
      error = "Produto não encontrado."
    }

    conditional {
      if ($input.type == "LOSS") {
        precondition ($input.justification != null && $input.justification != "") {
          error_type = "inputerror"
          error = "Justificativa obrigatória para perda (LOSS)."
        }
      }
    }

    // 1. Normalizar idempotency_key vazia para null (não ocupar índice único)
    var $idempotency_key {
      value = null
    }

    conditional {
      if ($input.idempotency_key != null && $input.idempotency_key != "") {
        var.update $idempotency_key {
          value = $input.idempotency_key
        }
      }
    }

    // 2. Idempotência: rejeitar repetição explícita da mesma chave
    conditional {
      if ($idempotency_key != null) {
        db.query stock_outbound {
          where = ($db.stock_outbound.idempotency_key == $idempotency_key)
          return = {type: "single"}
        } as $existing

        precondition ($existing == null) {
          error_type = "badrequest"
          error = "Operação já registrada com esta idempotency_key."
        }
      }
    }

    // 3. Status inicial decidido pelo backend, nunca pelo cliente
    var $initial_status {
      value = "Pendente"
    }

    conditional {
      if ($input.type == "LOSS") {
        var.update $initial_status {
          value = "AguardandoAprovacao"
        }
      }
    }

    // 4. Persistir a operação (sem alterar estoque nesta etapa)
    db.add stock_outbound {
      data = {
        type: $input.type
        status: $initial_status
        product_id: $input.product_id
        quantity: $input.quantity
        user_id: $auth.id
        reason: $input.reason
        justification: $input.justification
        reference_type: $input.reference_type
        reference_id: $input.reference_id
        destination: $input.destination
        notes: $input.notes
        idempotency_key: $idempotency_key
      }
    } as $outbound
  }

  response = $outbound
  tags = ["smart-vision"]
  guid = "outbound_create_guid_001"
}
