// Registrar ou retomar a contagem física de um produto em um inventário (Change 03)
// Permissão: qualquer usuário autenticado; counted_by é sempre $auth.id. Não altera saldo.
// - Primeira contagem: cria registro.
// - Salvar progresso / retomar: atualiza o registro existente (não duplica).
// - Recontagem (is_recount = true): cria novo registro preservando o anterior via previous_count_id.
// Não altera o saldo de estoque durante a contagem.
query "inventories/counts" verb=POST {
  api_group = "Smart Vision"
  auth = "user"

  input {
    int inventory_id
    int product_id
    int quantity_counted
    int? counted_by?
    bool? is_recount?
    int? previous_count_id?
    text? notes? filters=trim
  }

  stack {
    // 0. O contador é sempre o usuário autenticado (não confiar no cliente).
    precondition ($input.counted_by == null || $input.counted_by == $auth.id) {
      error_type = "accessdenied"
      error = "O contador deve ser o usuário autenticado."
    }

    // 1. Validar quantidade não negativa
    precondition ($input.quantity_counted >= 0) {
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

    precondition ($inventory.status == "EmContagem") {
      error_type = "badrequest"
      error = "A contagem só pode ser registrada em inventário com status EmContagem."
    }

    // 3. Validar produto e usuário contador
    db.get product {
      field_name = "id"
      field_value = $input.product_id
    } as $product

    precondition ($product != null) {
      error_type = "notfound"
      error = "Produto não encontrado."
    }

    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "name", "role"]
    } as $counter

    precondition ($counter != null) {
      error_type = "notfound"
      error = "Usuário contador não encontrado."
    }

    // 4. Buscar a contagem mais recente do produto neste inventário
    db.query inventory_count {
      where = ($db.inventory_count.inventory_id == $input.inventory_id) && ($db.inventory_count.product_id == $input.product_id)
      sort = {counted_at: "desc"}
      return = {type: "single"}
    } as $latest_count

    var $effective_recount {
      value = false
    }

    conditional {
      if ($input.is_recount != null) {
        var.update $effective_recount {
          value = $input.is_recount
        }
      }
    }

    var $saved_count {
      value = null
    }

    // 5. Se já existe contagem e não é recontagem: atualizar (salvar progresso / retomar)
    conditional {
      if ($latest_count != null && $effective_recount == false) {
        db.edit inventory_count {
          field_name = "id"
          field_value = $latest_count.id
          data = {
            quantity_counted: $input.quantity_counted
            counted_by: $auth.id
            counted_at: "now"
            notes: $input.notes
            is_recount: false
            previous_count_id: null
          }
        } as $updated_count

        var.update $saved_count {
          value = $updated_count
        }
      }
    }

    // 6. Se não existe contagem ou é recontagem: criar novo registro
    conditional {
      if ($latest_count == null || $effective_recount) {
        var $prev_id {
          value = $input.previous_count_id
        }

        conditional {
          if ($latest_count != null && $effective_recount) {
            var.update $prev_id {
              value = $latest_count.id
            }
          }
        }

        db.add inventory_count {
          data = {
            inventory_id: $input.inventory_id
            product_id: $input.product_id
            quantity_counted: $input.quantity_counted
            counted_by: $auth.id
            counted_at: "now"
            is_recount: $effective_recount
            previous_count_id: $prev_id
            notes: $input.notes
          }
        } as $created_count

        var.update $saved_count {
          value = $created_count
        }
      }
    }

  }

  response = $saved_count
  tags = ["smart-vision"]
  guid = "inventory_count_create_guid_001"
}
