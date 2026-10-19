// Decisão do gestor sobre uma divergência (Change 03)
// Ações: approved | rejected | recount_requested
// Regras: somente gestor, não aprovar própria contagem (separação de funções),
// rejeição não gera ajuste, histórico de decisões preservado.
query inventory_discrepancy_decision verb=POST {
  api_group = "Smart Vision"

  input {
    int inventory_id
    int discrepancy_id
    text action filters=trim
    int decided_by
    text? justification filters=trim
  }

  stack {
    // 1. Validar ação
    precondition ($input.action == "approved" || $input.action == "rejected" || $input.action == "recount_requested") {
      error_type = "inputerror"
      error = "Ação inválida. Use: approved, rejected ou recount_requested."
    }

    // 2. Validar que o decisor é um gestor (perfis de gestão: Gestor ou o legado admin)
    db.get user {
      field_name = "id"
      field_value = $input.decided_by
    } as $decider

    precondition ($decider != null) {
      error_type = "notfound"
      error = "Usuário decisor não encontrado."
    }

    precondition ($decider.role == "Gestor" || $decider.role == "admin") {
      error_type = "forbidden"
      error = "Apenas usuários com perfil de gestor podem aprovar, rejeitar ou solicitar recontagem de divergências."
    }

    // 3. Buscar a divergência
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
      error = "A divergência já possui uma decisão registrada (status: " + $discrepancy.status + ")."
    }

    // 4. Separação de funções: o responsável pela contagem não aprova a própria divergência
    db.query inventory_count {
      where = ($db.inventory_count.inventory_id == $input.inventory_id) && ($db.inventory_count.product_id == $discrepancy.product_id)
      sort = {counted_at: "desc"}
      return = {type: "object"}
    } as $latest_count

    conditional {
      if ($latest_count != null && $latest_count.counted_by == $input.decided_by) {
        precondition (false) {
          error_type = "forbidden"
          error = "O responsável pela contagem não pode aprovar a própria divergência (separação de funções)."
        }
      }
    }

    var $new_status {
      value = $discrepancy.status
      if ($input.action == "approved") { value = "approved" }
      if ($input.action == "rejected") { value = "rejected" }
      if ($input.action == "recount_requested") { value = "recount_requested" }
    }

    // 5. Registrar a decisão no histórico (audit log de decisões)
    db.add inventory_decision {
      data = {
        inventory_id: $input.inventory_id
        product_id: $discrepancy.product_id
        discrepancy_id: $input.discrepancy_id
        action: $input.action
        decided_by: $input.decided_by
        decided_at: "now"
        justification: $input.justification
        previous_status: $discrepancy.status
        notes: null
      }
    } as $decision_record

    // 6. Atualizar o status da divergência
    db.edit inventory_discrepancy {
      field_name = "id"
      field_value = $input.discrepancy_id
      data = {
        status: $new_status
        reviewed_by: $input.decided_by
        reviewed_at: "now"
        review_notes: $input.justification
      }
    } as $updated_discrepancy

    // 7. Se recontagem solicitada, reabrir o inventário para contagem
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

    response = $updated_discrepancy
    tags = ["smart-vision"]
    guid = "inventory_discrepancy_decision_guid_001"
  }
}
