// Transição de estado do inventário (Change 03)
// Valida as transições permitidas do ciclo de vida.
// Aberto -> EmContagem | EmContagem -> Aberto | EmContagem -> AguardandoAprovacao
// AguardandoAprovacao -> EmContagem | AguardandoAprovacao -> Concluido
query inventory_status verb=PATCH {
  api_group = "Smart Vision"

  input {
    int id
    text status filters=trim
    int user_id
  }

  stack {
    // 1. Buscar o inventário
    db.get inventory {
      field_name = "id"
      field_value = $input.id
    } as $inventory

    precondition ($inventory != null) {
      error_type = "notfound"
      error = "Inventário não encontrado."
    }

    // 2. Inventário concluído não pode ser alterado retroativamente
    precondition ($inventory.status != "Concluido") {
      error_type = "badrequest"
      error = "Inventário já concluído não pode ser alterado retroativamente."
    }

    // 3. Validar status destino
    precondition ($input.status == "Aberto" || $input.status == "EmContagem" || $input.status == "AguardandoAprovacao" || $input.status == "Concluido") {
      error_type = "inputerror"
      error = "Status destino inválido."
    }

    // 4. Validar transição permitida
    var $allowed {
      value = false
    }

    conditional {
      if ($inventory.status == "Aberto" && $input.status == "EmContagem") {
        value = true
      }
      if ($inventory.status == "EmContagem" && $input.status == "Aberto") {
        value = true
      }
      if ($inventory.status == "EmContagem" && $input.status == "AguardandoAprovacao") {
        value = true
      }
      if ($inventory.status == "AguardandoAprovacao" && $input.status == "EmContagem") {
        value = true
      }
      if ($inventory.status == "AguardandoAprovacao" && $input.status == "Concluido") {
        value = true
      }
    }

    precondition ($allowed) {
      error_type = "badrequest"
      error = "Transição de estado não permitida de " + $inventory.status + " para " + $input.status + "."
    }

    // 5. Validar conclusão: só permite Concluido quando não houver divergências pendentes sem decisão
    conditional {
      if ($input.status == "Concluido") {
        db.query inventory_discrepancy {
          where = ($db.inventory_discrepancy.inventory_id == $input.id) && ($db.inventory_discrepancy.status == "pending")
          return = {type: "list"}
        } as $pending_discrepancies
        precondition (($pending_discrepancies == null) || ($pending_discrepancies == 0)) {
          error_type = "badrequest"
          error = "Não é possível concluir: existem divergências pendentes de decisão do gestor."
        }
      }
    }

    // 6. Aplicar transição
    var $closed_at {
      value = null
      if ($input.status == "Concluido") {
        value = "now"
      }
    }

    db.edit inventory {
      field_name = "id"
      field_value = $input.id
      data = {
        status: $input.status
        closed_at: $closed_at
      }
    } as $updated

    response = $updated
    tags = ["smart-vision"]
    guid = "inventory_status_guid_001"
  }
}
