// Processar operação de saída: efetiva a baixa via ledger stock_movement (Change 02).
// Permissão:
// - Pendente/FalhaNoProcessamento: solicitante ou Gestor/admin
// - AguardandoAprovacao: somente Gestor/admin (aprovação + baixa)
// A identidade do operador é sempre $auth.id, nunca o user_id enviado pelo cliente.
// A transação garante auditoria + saldo + status da operação de forma atômica.
query "outbound/process" verb=POST {
  api_group = "Smart Vision"
  auth = "user"

  input {
    int id
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

    // Estados finais são imutáveis
    precondition ($outbound.status != "Concluida") {
      error_type = "badrequest"
      error = "Operação já concluída."
    }

    precondition ($outbound.status != "Rejeitada" && $outbound.status != "Cancelada") {
      error_type = "badrequest"
      error = "Não é possível processar operação rejeitada ou cancelada."
    }

    precondition ($outbound.status == "Pendente" || $outbound.status == "AguardandoAprovacao" || $outbound.status == "FalhaNoProcessamento") {
      error_type = "badrequest"
      error = "Status da operação não permite processamento."
    }

    // LOSS exige aprovação prévia de gestor (não pode ficar Pendente)
    conditional {
      if ($outbound.type == "LOSS") {
        precondition ($outbound.status == "AguardandoAprovacao" || $outbound.status == "FalhaNoProcessamento") {
          error_type = "badrequest"
          error = "Perdas devem estar AguardandoAprovacao para serem processadas."
        }
      }
    }

    // Idempotência: uma operação só pode gerar uma movimentação
    precondition ($outbound.stock_movement_id == null) {
      error_type = "badrequest"
      error = "Operação já possui movimentação vinculada (idempotência)."
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

    var $movement_id {
      value = null
    }

    // Aprovação de operação AguardandoAprovacao exige gestor.
    // LOSS exige gestor em qualquer status processável (inclusive falha/retry).
    conditional {
      if ($outbound.status == "AguardandoAprovacao" || $outbound.type == "LOSS") {
        precondition ($is_manager) {
          error_type = "accessdenied"
          error = "Apenas gestor (Gestor/admin) pode aprovar e processar esta operação."
        }
      }
      else {
        precondition ($is_manager || $outbound.user_id == $auth.id) {
          error_type = "accessdenied"
          error = "Apenas o solicitante ou um gestor pode processar esta operação."
        }
      }
    }

    // Transação atômica: relê o saldo, grava auditoria, atualiza saldo e status.
    db.transaction {
      stack {
        db.get product {
          field_name = "id"
          field_value = $outbound.product_id
        } as $locked_product

        precondition ($locked_product != null) {
          error_type = "notfound"
          error = "Produto não encontrado."
        }

        precondition ($locked_product.current_stock >= $outbound.quantity) {
          error_type = "badrequest"
          error = "Estoque insuficiente. A saída deixaria saldo negativo."
        }

        var $new_stock {
          value = $locked_product.current_stock - $outbound.quantity
        }

        // Auditoria primeiro (ledger imutável da Change 02)
        db.add stock_movement {
          data = {
            product_id: $outbound.product_id
            movement_type: "exit"
            quantity: $outbound.quantity
            previous_stock: $locked_product.current_stock
            new_stock: $new_stock
            reason: ("Saída #" ~ $outbound.id ~ " - " ~ $outbound.reason)
            user_id: $auth.id
            justification: $outbound.justification
            reference_text: ("outbound:" ~ $outbound.id)
            created_at: "now"
          }
        } as $audit

        var.update $movement_id {
          value = $audit.id
        }

        // Atualizar saldo somente depois da auditoria
        db.edit product {
          field_name = "id"
          field_value = $outbound.product_id
          data = {
            current_stock: $new_stock
          }
        } as $updated_product

        db.edit stock_outbound {
          field_name = "id"
          field_value = $input.id
          data = {
            status: "Concluida"
            stock_movement_id: $audit.id
            processed_at: "now"
          }
        } as $updated_outbound

        // Registrar aprovação explícita somente quando havia aprovação pendente
        conditional {
          if ($outbound.status == "AguardandoAprovacao") {
            db.edit stock_outbound {
              field_name = "id"
              field_value = $input.id
              data = {
                approved_by: $auth.id
                approved_at: "now"
              }
            } as $approved_outbound
          }
        }
      }
    }

    db.get stock_outbound {
      field_name = "id"
      field_value = $input.id
    } as $final_outbound

    db.get product {
      field_name = "id"
      field_value = $outbound.product_id
    } as $final_product

    db.get stock_movement {
      field_name = "id"
      field_value = $movement_id
    } as $final_movement
  }

  response = {
    outbound: $final_outbound
    movement: $final_movement
    product: $final_product
  }
  tags = ["smart-vision"]
  guid = "outbound_process_guid_001"
}
