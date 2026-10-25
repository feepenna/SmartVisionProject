// Decisão do gestor sobre uma divergência (Change 03)
// Permissão: somente Gestor/admin; registra decisão em inventory_decision. Não movimenta estoque.
// Ações: approved | rejected | recount_requested
// Regras: somente gestor/admin; não aprovar a própria contagem (separação de
// funções); aprovação e rejeição exigem justificativa; rejeição não gera ajuste;
// histórico de decisões preservado em inventory_decision.
query "inventories/discrepancies/decision" verb=POST {
  api_group = "Smart Vision"
  auth = "user"

  input {
    int inventory_id
    int discrepancy_id
    text action filters=trim
    int? decided_by?
    text? justification? filters=trim
  }

  stack {
    // 0. O decisor é sempre o usuário autenticado (não confiar no cliente).
    precondition ($input.decided_by == null || $input.decided_by == $auth.id) {
      error_type = "accessdenied"
      error = "O decisor deve ser o usuário autenticado."
    }

    // 1. Validar ação
    precondition ($input.action == "approved" || $input.action == "rejected" || $input.action == "recount_requested") {
      error_type = "inputerror"
      error = "Ação inválida. Use: approved, rejected ou recount_requested."
    }

    // 2. Validar que o decisor é um gestor (perfis de gestão: Gestor ou o legado admin)
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "name", "role"]
    } as $decider

    precondition ($decider != null) {
      error_type = "notfound"
      error = "Usuário decisor não encontrado."
    }

    precondition ($decider.role == "Gestor" || $decider.role == "admin") {
      error_type = "accessdenied"
      error = "Apenas usuários com perfil de gestor podem aprovar, rejeitar ou solicitar recontagem de divergências."
    }

    // 3. Justificativa obrigatória para aprovação e rejeição
    conditional {
      if ($input.action == "approved" || $input.action == "rejected") {
        precondition ($input.justification != null && $input.justification != "") {
          error_type = "inputerror"
          error = "Justificativa é obrigatória para aprovar ou rejeitar uma divergência."
        }
      }
    }

    // 4. Buscar inventário e divergência
    db.get inventory {
      field_name = "id"
      field_value = $input.inventory_id
    } as $inventory

    precondition ($inventory != null) {
      error_type = "notfound"
      error = "Inventário não encontrado."
    }

    precondition ($inventory.status == "AguardandoAprovacao") {
      error_type = "badrequest"
      error = "A decisão só pode ser registrada com o inventário em AguardandoAprovacao."
    }

    db.get inventory_discrepancy {
      field_name = "id"
      field_value = $input.discrepancy_id
    } as $discrepancy

    precondition ($discrepancy != null) {
      error_type = "notfound"
      error = "Divergência não encontrada."
    }

    precondition ($discrepancy.inventory_id == $input.inventory_id) {
      error_type = "badrequest"
      error = "A divergência não pertence ao inventário informado."
    }

    precondition ($discrepancy.status == "pending") {
      error_type = "badrequest"
      error = "A divergência já possui uma decisão registrada (status: " ~ $discrepancy.status ~ ")."
    }

    // 5. Separação de funções: o responsável pela contagem não aprova a própria
    // divergência. Rejeitar ou solicitar recontagem é permitido.
    db.query inventory_count {
      where = ($db.inventory_count.inventory_id == $input.inventory_id) && ($db.inventory_count.product_id == $discrepancy.product_id)
      sort = {counted_at: "desc"}
      return = {type: "single"}
    } as $latest_count

    precondition ($input.action != "approved" || $latest_count == null || $latest_count.counted_by != $auth.id) {
      error_type = "accessdenied"
      error = "O responsável pela contagem não pode aprovar a própria divergência (separação de funções)."
    }

    var $new_status {
      value = $discrepancy.status
    }

    conditional {
      if ($input.action == "approved") {
        var.update $new_status {
          value = "approved"
        }
      }
      elseif ($input.action == "rejected") {
        var.update $new_status {
          value = "rejected"
        }
      }
      elseif ($input.action == "recount_requested") {
        var.update $new_status {
          value = "recount_requested"
        }
      }
    }

    // 6. Registrar a decisão no histórico (audit log de decisões)
    db.add inventory_decision {
      data = {
        inventory_id: $input.inventory_id
        product_id: $discrepancy.product_id
        discrepancy_id: $input.discrepancy_id
        action: $input.action
        decided_by: $auth.id
        decided_at: "now"
        justification: $input.justification
        previous_status: $discrepancy.status
        notes: null
      }
    } as $decision_record

    // 7. Atualizar o status da divergência
    db.edit inventory_discrepancy {
      field_name = "id"
      field_value = $input.discrepancy_id
      data = {
        status: $new_status
        reviewed_by: $auth.id
        reviewed_at: "now"
        review_notes: $input.justification
      }
    } as $updated_discrepancy

    // 8. Se recontagem solicitada, reabrir o inventário para contagem
    conditional {
      if ($input.action == "recount_requested") {
        db.edit inventory {
          field_name = "id"
          field_value = $input.inventory_id
          data = {
            status: "EmContagem"
          }
        } as $inventory_reopened
      }
    }

  }

  response = $updated_discrepancy
  tags = ["smart-vision"]
  guid = "inventory_discrepancy_decision_guid_001"
}
