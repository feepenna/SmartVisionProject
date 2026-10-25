// Transição de estado do inventário (Change 03)
// Permissão: qualquer usuário autenticado; Concluido exige Gestor/admin. Não movimenta estoque.
// Valida as transições permitidas do ciclo de vida.
// Aberto -> EmContagem | EmContagem -> Aberto | EmContagem -> AguardandoAprovacao
// AguardandoAprovacao -> EmContagem | AguardandoAprovacao -> Concluido
// Conclusão exige que não existam divergências pendentes nem ajustes aprovados sem aplicação.
query "inventories/status" verb=PATCH {
  api_group = "Smart Vision"
  auth = "user"

  input {
    int id
    text status filters=trim
    int? user_id?
  }

  stack {
    // 0. O ator é sempre o usuário autenticado (não confiar no cliente).
    precondition ($input.user_id == null || $input.user_id == $auth.id) {
      error_type = "accessdenied"
      error = "O usuário da transição deve ser o usuário autenticado."
    }

    // 1. Validar usuário responsável pela transição
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "name", "role"]
    } as $actor

    precondition ($actor != null) {
      error_type = "notfound"
      error = "Usuário não encontrado."
    }

    // 1.1. Conclusão é restrita a gestor/admin (validação no backend).
    conditional {
      if ($input.status == "Concluido") {
        precondition ($actor.role == "Gestor" || $actor.role == "admin") {
          error_type = "accessdenied"
          error = "Apenas usuários com perfil de gestor podem concluir um inventário."
        }
      }
    }

    // 2. Buscar o inventário
    db.get inventory {
      field_name = "id"
      field_value = $input.id
    } as $inventory

    precondition ($inventory != null) {
      error_type = "notfound"
      error = "Inventário não encontrado."
    }

    // 3. Inventário concluído não pode ser alterado retroativamente
    precondition ($inventory.status != "Concluido") {
      error_type = "badrequest"
      error = "Inventário já concluído não pode ser alterado retroativamente."
    }

    // 4. Validar status destino
    precondition ($input.status == "Aberto" || $input.status == "EmContagem" || $input.status == "AguardandoAprovacao" || $input.status == "Concluido") {
      error_type = "inputerror"
      error = "Status destino inválido."
    }

    // 5. Validar transição permitida
    var $allowed {
      value = false
    }

    conditional {
      if (($inventory.status == "Aberto" && $input.status == "EmContagem") || ($inventory.status == "EmContagem" && ($input.status == "Aberto" || $input.status == "AguardandoAprovacao")) || ($inventory.status == "AguardandoAprovacao" && ($input.status == "EmContagem" || $input.status == "Concluido"))) {
        var.update $allowed {
          value = true
        }
      }
    }

    precondition ($allowed) {
      error_type = "badrequest"
      error = "Transição de estado não permitida de " ~ $inventory.status ~ " para " ~ $input.status ~ "."
    }

    // 6. Validar conclusão: sem pendências e sem ajustes aprovados não aplicados
    conditional {
      if ($input.status == "Concluido") {
        db.query inventory_discrepancy {
          where = ($db.inventory_discrepancy.inventory_id == $input.id) && ($db.inventory_discrepancy.status == "pending")
          return = {type: "count"}
        } as $pending_discrepancies

        precondition ($pending_discrepancies == 0) {
          error_type = "badrequest"
          error = "Não é possível concluir: existem divergências pendentes de decisão do gestor."
        }

        db.query inventory_discrepancy {
          where = ($db.inventory_discrepancy.inventory_id == $input.id) && ($db.inventory_discrepancy.status == "approved") && ($db.inventory_discrepancy.adjustment_applied == false)
          return = {type: "count"}
        } as $unapplied_adjustments

        precondition ($unapplied_adjustments == 0) {
          error_type = "badrequest"
          error = "Não é possível concluir: existem ajustes aprovados pendentes de aplicação."
        }
      }
    }

    // 7. Aplicar transição
    var $closed_at {
      value = null
    }

    conditional {
      if ($input.status == "Concluido") {
        var.update $closed_at {
          value = "now"
        }
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

  }

  response = $updated
  tags = ["smart-vision"]
  guid = "inventory_status_guid_001"
}
