// Registrar ou retomar a contagem física de um produto em um inventário (Change 03)
// - Primeira contagem: cria registro.
// - Salvar progresso / retomar: atualiza o registro existente (não duplica).
// - Recontagem (is_recount = true): cria novo registro preservando o anterior via previous_count_id.
// Não altera o saldo de estoque durante a contagem.
query inventory_counts verb=POST {
  api_group = "Smart Vision"

  input {
    int inventory_id
    int product_id
    int quantity_counted
    int counted_by
    bool? is_recount
    int? previous_count_id
    text? notes filters=trim
  }

  stack {
    // 1. Validar quantidade não negativa
    precondition ($input.quantity_counted != null && $input.quantity_counted >= 0) {
      error_type = "inputerror"
      error = "A quantidade contada deve ser um número maior ou igual a zero."
    }

    // 2. Validar inventário existe e está em contagem
    db.get inventory {
      field_name = "id"
      field_value = $input.inventory_id
    } as $inventory

    precondition ($inventory != null) {
      error_type = "notfound"
      error = "Inventário não encontrado."
    }

    precondition ($inventory.status == "EmContagem" || $inventory.status == "Aberto") {
      error_type = "badrequest"
      error = "A contagem só pode ser registrada em inventário com status EmContagem (ou Aberto para iniciar)."
    }

    // 3. Validar produto existe
    db.get product {
      field_name = "id"
      field_value = $input.product_id
    } as $product

    precondition ($product != null) {
      error_type = "notfound"
      error = "Produto não encontrado."
    }

    // 4. Buscar a contagem mais recente do produto neste inventário
    db.query inventory_count {
      where = ($db.inventory_count.inventory_id == $input.inventory_id) && ($db.inventory_count.product_id == $input.product_id)
      sort = {counted_at: "desc"}
      return = {type: "object"}
    } as $latest_count

    var $effective_recount {
      value = $input.is_recount
      if ($effective_recount == null) {
        value = false
      }
    }

    // 5. Se já existe contagem e não é recontagem: atualizar (salvar progresso / retomar)
    conditional {
      if ($latest_count != null && !$effective_recount) {
        db.edit inventory_count {
          field_name = "id"
          field_value = $latest_count.id
          data = {
            quantity_counted: $input.quantity_counted
            counted_by: $input.counted_by
            counted_at: "now"
            notes: $input.notes
            is_recount: false
            previous_count_id: null
          }
        } as $saved_count
      }
    }

    // 6. Se não existe contagem ou é recontagem: criar novo registro
    conditional {
      if ($latest_count == null || $effective_recount) {
        var $prev_id {
          value = $input.previous_count_id
          if ($latest_count != null && $effective_recount) {
            value = $latest_count.id
          }
        }
        db.add inventory_count {
          data = {
            inventory_id: $input.inventory_id
            product_id: $input.product_id
            quantity_counted: $input.quantity_counted
            counted_by: $input.counted_by
            counted_at: "now"
            is_recount: $effective_recount
            previous_count_id: $prev_id
            notes: $input.notes
          }
        } as $saved_count
      }
    }

    response = $saved_count
    tags = ["smart-vision"]
    guid = "inventory_count_create_guid_001"
  }
}
