// Aplicar ajustes de estoque aprovados (Change 03)
// Reutiliza o ledger de auditoria existente (tabela stock_movement, movement_type = "adjustment")
// da Change 02. Não cria ledger paralelo.
// Garante idempotência (um ajuste é aplicado uma vez por divergência) e trata
// movimentações concorrentes ocorridas entre a contagem e a aprovação.
query inventory_apply_adjustments verb=POST {
  api_group = "Smart Vision"

  input {
    int inventory_id
    int user_id
  }

  stack {
    // 1. Validar que o aplicador é um gestor
    db.get user {
      field_name = "id"
      field_value = $input.user_id
    } as $applier

    precondition ($applier != null) {
      error_type = "notfound"
      error = "Usuário aplicador não encontrado."
    }

    precondition ($applier.role == "Gestor" || $applier.role == "admin") {
      error_type = "forbidden"
      error = "Apenas usuários com perfil de gestor podem aplicar ajustes de estoque."
    }

    // 2. Validar inventário
    db.get inventory {
      field_name = "id"
      field_value = $input.inventory_id
    } as $inventory

    precondition ($inventory != null) {
      error_type = "notfound"
      error = "Inventário não encontrado."
    }

    // 3. Buscar divergências aprovadas ainda não aplicadas
    db.query inventory_discrepancy {
      where = ($db.inventory_discrepancy.inventory_id == $input.inventory_id) && ($db.inventory_discrepancy.status == "approved") && ($db.inventory_discrepancy.adjustment_applied == false)
      return = {type: "list"}
    } as $to_apply

    conditional {
      if ($to_apply != null) {
        foreach $d in $to_apply {
          // Buscar saldo atual do produto
          db.get product {
            field_name = "id"
            field_value = $d.product_id
          } as $product

          conditional {
            if ($product != null) {
              var $current_stock {
                value = $product.current_stock
              }
              var $reference {
                value = $d.reference_quantity
              }
              var $counted {
                value = $d.counted_quantity
              }

              // Tratamento de concorrência: comparar saldo atual com saldo de referência
              conditional {
                if ($current_stock == $reference) {
                  // Sem movimentações concorrentes: aplicar ajuste diretamente
                  var $difference {
                    value = $counted - $reference
                  }
                  var $new_stock {
                    value = $current_stock + $difference
                  }
                  var $adj_quantity {
                    value = ($difference < 0) ? (0 - $difference) : $difference
                  }

                  // Respeitar regra de saldo negativo para saídas (shortage)
                  conditional {
                    if ($difference < 0 && $current_stock < $adj_quantity) {
                      precondition (false) {
                        error_type = "badrequest"
                        error = "Saldo insuficiente para aplicar ajuste de falta do produto " + $d.product_id + "."
                      }
                    }
                  }

                  // Gravar movimentação de ajuste no ledger existente (Change 02)
                  db.add stock_movement {
                    data = {
                      product_id: $d.product_id
                      movement_type: "adjustment"
                      quantity: $adj_quantity
                      previous_stock: $current_stock
                      new_stock: $new_stock
                      reason: "Ajuste de inventário #" + $input.inventory_id + " - divergência #" + $d.id + " (" + $d.divergence_type + ")"
                      user_id: $input.user_id
                      reference_text: "inventory:" + $input.inventory_id
                      justification: "Conciliação de inventário físico - divergência " + $d.divergence_type
                    }
                  } as $movement

                  // Atualizar saldo do produto
                  db.edit product {
                    field_name = "id"
                    field_value = $d.product_id
                    data = {
                      current_stock: $new_stock
                    }
                  } as $updated_product

                  // Marcar divergência como aplicada
                  db.edit inventory_discrepancy {
                    field_name = "id"
                    field_value = $d.id
                    data = {
                      adjustment_applied: true
                      adjustment_movement_id: $movement.id
                    }
                  } as $discrepancy_marked

                  var $applied_count {
                    value = $applied_count + 1
                  }
                }
              }

              conditional {
                if ($current_stock != $reference) {
                  // Houve movimentação concorrente: recalcular
                  var $difference_now {
                    value = $counted - $current_stock
                  }
                  conditional {
                    if ($difference_now == 0) {
                      // Movimentações posteriores zeraram a divergência: nada a ajustar
                      db.edit inventory_discrepancy {
                        field_name = "id"
                        field_value = $d.id
                        data = {
                          adjustment_applied: true
                          adjustment_movement_id: null
                        }
                      } as $discrepancy_resolved
                      var $applied_count {
                        value = $applied_count + 1
                      }
                    } else {
                      // Não é possível determinar com segurança: solicitar recontagem
                      db.edit inventory_discrepancy {
                        field_name = "id"
                        field_value = $d.id
                        data = {
                          status: "recount_requested"
                          review_notes: "Ajuste não aplicado: saldo mudou entre a contagem e a aprovação (referência " + $reference + ", atual " + $current_stock + "). Solicitada recontagem."
                        }
                      } as $discrepancy_conflict
                      var $skipped_count {
                        value = $skipped_count + 1
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }

    response = {
      inventory_id: $input.inventory_id
      applied: $applied_count
      skipped: $skipped_count
      message: "Ajustes aplicados com idempotência e tratamento de concorrência."
    }
    tags = ["smart-vision"]
    guid = "inventory_apply_adjustments_guid_001"
  }
}
