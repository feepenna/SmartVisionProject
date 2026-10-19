// Atualizar status da operacao de saida (Change 04)
// Aprovacao, rejeicao ou cancelamento por gestor quando aplicavel
query outbound_status verb=PATCH {
  api_group = "Smart Vision"

  input {
    int id
    text status filters=trim
    int? user_id
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
      error = "Operacao ja concluida nao pode ser alterada."
    }

    var $new_status {
      value = $input.status
    }

    conditional {
      if ($new_status == "Concluida" || $new_status == "Rejeitada" || $new_status == "AguardandoAprovacao") {
        precondition ($input.user_id != null) {
          error_type = "inputerror"
          error = "user_id do gestor e obrigatorio para esta transicao."
        }

        db.get user {
          field_name = "id"
          field_value = $input.user_id
        } as $actor

        precondition ($actor != null && ($actor.role == "Gestor" || $actor.role == "admin")) {
          error_type = "accessdenied"
          error = "Apenas gestor (Gestor/admin) pode aprovar/rejeitar/alterar status desta operacao."
        }
      }
    }

    db.edit stock_outbound {
      field_name = "id"
      field_value = $input.id
      data = {
        status: $new_status
        approved_by: $input.user_id
        approved_at: "now"
      }
    } as $updated
  }

  response = $updated
  tags = ["smart-vision"]
  guid = "outbound_status_guid_001"
}
