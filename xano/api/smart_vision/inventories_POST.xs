// Criar um novo inventário físico (Change 03)
// Status inicial: Aberto. Reutiliza usuário existente (Change 02: user_id como parâmetro).
query inventories verb=POST {
  api_group = "Smart Vision"

  input {
    text? status filters=trim
    text scope filters=trim
    text? category_filter filters=trim
    text? location_filter filters=trim
    int opened_by
    text? notes filters=trim
  }

  stack {
    // 1. Validar responsável pela abertura
    precondition ($input.opened_by != null) {
      error_type = "inputerror"
      error = "O responsável pela abertura do inventário é obrigatório."
    }

    // 2. Validar escopo
    precondition ($input.scope != null && $input.scope != "") {
      error_type = "inputerror"
      error = "O escopo do inventário é obrigatório (completo, categoria ou localizacao)."
    }

    // 3. Validar status, se informado
    conditional {
      if ($input.status != null && $input.status != "") {
        precondition ($input.status == "Aberto" || $input.status == "EmContagem" || $input.status == "AguardandoAprovacao" || $input.status == "Concluido") {
          error_type = "inputerror"
          error = "Status inválido. Use: Aberto, EmContagem, AguardandoAprovacao ou Concluido."
        }
      }
    }

    var $effective_status {
      value = $input.status
      if ($effective_status == null || $effective_status == "") {
        value = "Aberto"
      }
    }

    // 4. Inserir o inventário
    db.add inventory {
      data = {
        status: $effective_status
        scope: $input.scope
        category_filter: $input.category_filter
        location_filter: $input.location_filter
        opened_by: $input.opened_by
        opened_at: "now"
        closed_at: null
        notes: $input.notes
      }
    } as $inventory
  }

  response = $inventory
  tags = ["smart-vision"]
  guid = "inventory_create_guid_001"
}
