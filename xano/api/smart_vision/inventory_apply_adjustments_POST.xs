// Aplicar ajustes de estoque aprovados (Change 03)
// Permissão: somente Gestor/admin; grava stock_movement (adjustment) antes de atualizar o saldo.
// Reutiliza o ledger de auditoria existente (tabela stock_movement,
// movement_type = "adjustment") da Change 02. Não cria ledger paralelo.
// A auditoria é gravada antes de atualizar o saldo do produto.
// Idempotente: cada divergência é aplicada no máximo uma vez.
// Concorrência: se o saldo atual divergir da referência da contagem, o ajuste
// não é aplicado e a divergência volta para recontagem.
query "inventories/apply-adjustments" verb=POST {
  api_group = "Smart Vision"
  auth = "user"

  input {
    int inventory_id
    int? user_id?
  }

  stack {
    // 0. O aplicador é sempre o usuário autenticado (não confiar no cliente).
    precondition ($input.user_id == null || $input.user_id == $auth.id) {
      error_type = "accessdenied"
      error = "O aplicador deve ser o usuário autenticado."
    }

    // 1. Validar que o aplicador é um gestor
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "name", "role"]
    } as $applier

    precondition ($applier != null) {
      error_type = "notfound"
      error = "Usuário aplicador não encontrado."
    }

    precondition ($applier.role == "Gestor" || $applier.role == "admin") {
      error_type = "accessdenied"
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

    precondition ($inventory.status == "AguardandoAprovacao") {
      error_type = "badrequest"
      error = "A aplicação de ajustes só pode ocorrer com o inventário em AguardandoAprovacao."
    }

    // 3. Buscar divergências aprovadas ainda não aplicadas
    db.query inventory_discrepancy {
      where = ($db.inventory_discrepancy.inventory_id == $input.inventory_id) && ($db.inventory_discrepancy.status == "approved") && ($db.inventory_discrepancy.adjustment_applied == false)
      return = {type: "list"}
    } as $to_apply

    // Idempotência: informa quantos ajustes já foram aplicados anteriormente.
    db.query inventory_discrepancy {
      where = ($db.inventory_discrepancy.inventory_id == $input.inventory_id) && ($db.inventory_discrepancy.adjustment_applied == true)
      return = {type: "count"}
    } as $already_applied

    var $to_apply_list {
      value = []
    }
    var $applied_count {
      value = 0
    }
    var $skipped_count {
      value = 0
    }

    conditional {
      if ($to_apply != null) {
        var.update $to_apply_list {
          value = $to_apply
        }
      }
    }

    foreach ($to_apply_list) {
      each as $d {
        db.get product {
          field_name = "id"
          field_value = $d.product_id
        } as $product

        conditional {
          if ($product == null) {
            var.update $skipped_count {
              value = $skipped_count + 1
            }
          }
        }

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
            var $difference {
              value = $counted - $reference
            }
            var $new_stock {
              value = $current_stock + $difference
            }
            var $adj_quantity {
              value = $difference
            }

            conditional {
              if ($difference < 0) {
                var.update $adj_quantity {
                  value = 0 - $difference
                }
              }
            }

            // Sem movimentações concorrentes: saldo atual igual ao da contagem
            conditional {
              if ($current_stock == $reference) {
                // Saldo nunca fica negativo: a quantidade final é a contagem física
                precondition ($new_stock >= 0) {
                  error_type = "badrequest"
                  error = "Saldo insuficiente para aplicar ajuste de falta do produto " ~ $d.product_id ~ "."
                }

                conditional {
                  if ($difference == 0) {
                    // Contagem igual ao saldo: apenas marca como resolvida, sem movimento
                    db.edit inventory_discrepancy {
                      field_name = "id"
                      field_value = $d.id
                      data = {
                        adjustment_applied: true
                        adjustment_movement_id: null
                      }
                    } as $discrepancy_resolved

                    var.update $applied_count {
                      value = $applied_count + 1
                    }
                  }
                  else {
                    // Transação atômica: auditoria + saldo + marcação da divergência.
                    // Se qualquer etapa falhar, tudo é revertido (AGENTS 1.3).
                    db.transaction {
                      stack {
                        // Auditoria primeiro (ledger imutável da Change 02)
                        db.add stock_movement {
                          data = {
                            product_id: $d.product_id
                            movement_type: "adjustment"
                            quantity: $adj_quantity
                            previous_stock: $current_stock
                            new_stock: $new_stock
                            reason: ("Ajuste de inventário #" ~ $input.inventory_id ~ " - divergência #" ~ $d.id ~ " (" ~ $d.divergence_type ~ ")")
                            user_id: $auth.id
                            reference_text: ("inventory:" ~ $input.inventory_id)
                            justification: ("Conciliação de inventário físico - divergência " ~ $d.divergence_type)
                          }
                        } as $movement

                        // Depois da auditoria, atualiza o saldo
                        db.edit product {
                          field_name = "id"
                          field_value = $d.product_id
                          data = {
                            current_stock: $new_stock
                          }
                        } as $updated_product

                        // Marca a divergência como aplicada (idempotência)
                        db.edit inventory_discrepancy {
                          field_name = "id"
                          field_value = $d.id
                          data = {
                            adjustment_applied: true
                            adjustment_movement_id: $movement.id
                          }
                        } as $discrepancy_marked
                      }
                    }

                    var.update $applied_count {
                      value = $applied_count + 1
                    }
                  }
                }
              }
              elseif ($current_stock != $reference) {
                // Houve movimentação concorrente: recalcular com o saldo atual
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

                    var.update $applied_count {
                      value = $applied_count + 1
                    }
                  }
                  else {
                    // Não é possível aplicar com segurança: solicitar recontagem
                    db.edit inventory_discrepancy {
                      field_name = "id"
                      field_value = $d.id
                      data = {
                        status: "recount_requested"
                        review_notes: ("Ajuste não aplicado: saldo mudou entre a contagem e a aprovação (referência " ~ $reference ~ ", atual " ~ $current_stock ~ "). Solicitada recontagem.")
                      }
                    } as $discrepancy_conflict

                    var.update $skipped_count {
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

    // Se algum ajuste precisou de recontagem, reabre o inventário
    conditional {
      if ($skipped_count > 0) {
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

  response = {
    inventory_id: $input.inventory_id
    applied: $applied_count
    skipped: $skipped_count
    already_applied: $already_applied
    message: "Ajustes aplicados com idempotência e tratamento de concorrência."
  }
  tags = ["smart-vision"]
  guid = "inventory_apply_adjustments_guid_001"
}
