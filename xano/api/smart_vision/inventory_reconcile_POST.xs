// Conciliação de estoque (Change 03)
// Permissão: qualquer usuário autenticado. Não altera saldo; gera/atualiza divergências.
// Compara a quantidade física contada (última contagem de cada produto) com o
// saldo de referência do sistema (product.current_stock) e gera/atualiza as
// divergências. Recontagens são preservadas na tabela inventory_count e a
// contagem mais recente vence (ordem ascendente; a última sobrescreve).
// Transiciona o inventário de EmContagem para AguardandoAprovacao.
query "inventories/reconcile" verb=POST {
  api_group = "Smart Vision"
  auth = "user"

  input {
    int inventory_id
    int? user_id?
  }

  stack {
    // 0. O ator é sempre o usuário autenticado (não confiar no cliente).
    precondition ($input.user_id == null || $input.user_id == $auth.id) {
      error_type = "accessdenied"
      error = "O usuário da conciliação deve ser o usuário autenticado."
    }

    // 1. Validar usuário e inventário
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "name", "role"]
    } as $actor

    precondition ($actor != null) {
      error_type = "notfound"
      error = "Usuário não encontrado."
    }

    db.get inventory {
      field_name = "id"
      field_value = $input.inventory_id
    } as $inventory

    precondition ($inventory != null) {
      error_type = "notfound"
      error = "Inventário não encontrado."
    }

    precondition ($inventory.status == "EmContagem" || $inventory.status == "AguardandoAprovacao") {
      error_type = "badrequest"
      error = "A conciliação só pode ser executada em inventário EmContagem ou AguardandoAprovacao."
    }

    // 2. Buscar todas as contagens, da mais antiga para a mais recente.
    // Assim, a última contagem de cada produto prevalece ao final do loop,
    // inclusive quando houve recontagem.
    db.query inventory_count {
      where = ($db.inventory_count.inventory_id == $input.inventory_id)
      sort = {counted_at: "asc"}
      return = {type: "list"}
    } as $all_counts

    precondition ($all_counts != null && ($all_counts|count) > 0) {
      error_type = "badrequest"
      error = "Nenhuma contagem registrada. Registre ao menos uma contagem antes de conciliar."
    }

    foreach ($all_counts) {
      each as $count {
        db.get product {
          field_name = "id"
          field_value = $count.product_id
        } as $product

        conditional {
          if ($product != null) {
            var $counted {
              value = $count.quantity_counted
            }
            var $reference {
              value = $product.current_stock
            }
            var $difference {
              value = $counted - $reference
            }
            var $divergence_type {
              value = "none"
            }
            var $impact {
              value = "Sem divergência"
            }

            conditional {
              if ($difference < 0) {
                var.update $divergence_type {
                  value = "shortage"
                }
                var.update $impact {
                  value = "Falta de estoque: físico menor que o registrado."
                }
              }
              elseif ($difference > 0) {
                var.update $divergence_type {
                  value = "overage"
                }
                var.update $impact {
                  value = "Sobra de estoque: físico maior que o registrado."
                }
              }
            }

            // Buscar divergência existente para o produto/inventário
            db.query inventory_discrepancy {
              where = ($db.inventory_discrepancy.inventory_id == $input.inventory_id) && ($db.inventory_discrepancy.product_id == $count.product_id)
              sort = {created_at: "desc"}
              return = {type: "single"}
            } as $existing_discrepancy

            conditional {
              if ($existing_discrepancy == null || $existing_discrepancy.adjustment_applied == true) {
                db.add inventory_discrepancy {
                  data = {
                    inventory_id: $input.inventory_id
                    product_id: $count.product_id
                    counted_quantity: $counted
                    reference_quantity: $reference
                    difference: $difference
                    divergence_type: $divergence_type
                    impact: $impact
                    status: "pending"
                    reviewed_by: null
                    reviewed_at: null
                    review_notes: null
                    adjustment_applied: false
                    adjustment_movement_id: null
                  }
                } as $new_discrepancy
              }
            }

            // Recontagem: atualiza a divergência existente com a contagem mais
            // recente e devolve para pendente. Nunca altera um ajuste já aplicado.
            conditional {
              if ($existing_discrepancy != null && $existing_discrepancy.adjustment_applied == false) {
                db.edit inventory_discrepancy {
                  field_name = "id"
                  field_value = $existing_discrepancy.id
                  data = {
                    counted_quantity: $counted
                    reference_quantity: $reference
                    difference: $difference
                    divergence_type: $divergence_type
                    impact: $impact
                    status: "pending"
                    reviewed_by: null
                    reviewed_at: null
                    review_notes: null
                  }
                } as $updated_discrepancy
              }
            }
          }
        }
      }
    }

    // 3. Transição para AguardandoAprovacao se estava em EmContagem
    conditional {
      if ($inventory.status == "EmContagem") {
        db.edit inventory {
          field_name = "id"
          field_value = $input.inventory_id
          data = {
            status: "AguardandoAprovacao"
          }
        } as $inventory_updated
      }
    }

  }

  response = {
    inventory_id: $input.inventory_id
    status: "AguardandoAprovacao"
    message: "Conciliação realizada. Divergências pendentes de análise do gestor."
  }
  tags = ["smart-vision"]
  guid = "inventory_reconcile_guid_001"
}
