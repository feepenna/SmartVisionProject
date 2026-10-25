// Atualizar status da operação de saída (Change 04)
// Aprovação/rejeição/cancelamento. A baixa de estoque NÃO é feita aqui:
// a transição para Concluida ocorre exclusivamente em POST /outbound/process.
// Permissões:
// - AguardandoAprovacao: solicitante ou Gestor/admin
// - Rejeitada: somente Gestor/admin, a partir de AguardandoAprovacao
// - Cancelada: solicitante ou Gestor/admin, antes da conclusão
query "outbound/status" verb=PATCH {
  api_group = "Smart Vision"
  auth = "user"

  input {
    int id
    text status filters=trim
  }

  stack {
    db.get stock_outbound {
      field_name = "id"
      field_value = $input.id
    } as $outbound

    precondition ($outbound != null) {
      error_type = "notfound"
      error = "Operação de saída não encontrada."
    }

    // Estados finais não podem ser alterados
    precondition ($outbound.status != "Concluida" && $outbound.status != "Rejeitada" && $outbound.status != "Cancelada") {
      error_type = "badrequest"
      error = "Operação em estado final não pode ser alterada."
    }

    precondition ($input.status != "Concluida") {
      error_type = "badrequest"
      error = "Use POST /outbound/process para concluir e baixar o estoque."
    }

    precondition ($input.status == "AguardandoAprovacao" || $input.status == "Rejeitada" || $input.status == "Cancelada") {
      error_type = "inputerror"
      error = "Status inválido. Use AguardandoAprovacao, Rejeitada ou Cancelada."
    }

    precondition ($input.status != $outbound.status) {
      error_type = "badrequest"
      error = "A operação já está neste status."
    }

    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "role"]
    } as $actor

    precondition ($actor != null) {
      error_type = "notfound"
      error = "Usuário autenticado não encontrado."
    }

    var $is_manager {
      value = $actor.role == "Gestor" || $actor.role == "admin"
    }

    // AguardandoAprovacao: solicitante ou gestor pode solicitar
    conditional {
      if ($input.status == "AguardandoAprovacao") {
        precondition ($outbound.status == "Pendente") {
          error_type = "badrequest"
          error = "Só é possível solicitar aprovação para operação Pendente."
        }

        precondition ($is_manager || $outbound.user_id == $auth.id) {
          error_type = "accessdenied"
          error = "Apenas o solicitante ou um gestor pode solicitar aprovação."
        }
      }
    }

    // Rejeitada: apenas gestor, a partir de AguardandoAprovacao
    conditional {
      if ($input.status == "Rejeitada") {
        precondition ($outbound.status == "AguardandoAprovacao") {
          error_type = "badrequest"
          error = "Só é possível rejeitar operação AguardandoAprovacao."
        }

        precondition ($is_manager) {
          error_type = "accessdenied"
          error = "Apenas gestor (Gestor/admin) pode rejeitar operações."
        }
      }
    }

    // Cancelada: solicitante ou gestor, antes da conclusão
    conditional {
      if ($input.status == "Cancelada") {
        precondition ($outbound.status == "Pendente" || $outbound.status == "AguardandoAprovacao") {
          error_type = "badrequest"
          error = "Só é possível cancelar operação Pendente ou AguardandoAprovacao."
        }

        precondition ($is_manager || $outbound.user_id == $auth.id) {
          error_type = "accessdenied"
          error = "Apenas o solicitante ou um gestor pode cancelar a operação."
        }
      }
    }

    // Atualizar status (e registrar aprovação somente na rejeição)
    db.transaction {
      stack {
        db.edit stock_outbound {
          field_name = "id"
          field_value = $input.id
          data = {
            status: $input.status
          }
        } as $updated_status

        conditional {
          if ($input.status == "Rejeitada") {
            db.edit stock_outbound {
              field_name = "id"
              field_value = $input.id
              data = {
                approved_by: $auth.id
                approved_at: "now"
              }
            } as $updated_approval
          }
        }
      }
    }

    db.get stock_outbound {
      field_name = "id"
      field_value = $input.id
    } as $final_outbound
  }

  response = $final_outbound
  tags = ["smart-vision"]
  guid = "outbound_status_guid_001"
}
