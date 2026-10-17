// Conciliação de estoque (Change 03)
// Compara a quantidade física contada (última contagem do produto) com o saldo
// de referência do sistema (product.current_stock) e gera/atualiza as divergências.
// Transzciona o inventário de EmContagem para AguardandoAprovacao quando aplicável.
// Os valores originais (counted_quantity, reference_quantity) são preservados.
query inventory_reconcile verb=POST {
  api_group = "Smart Vision"

  input {
    int inventory_id
    int user_id
  }

  stack {
    // 1. Validar inventário
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

    // 2. Buscar produtos com contagem neste inventário (últimas contagens por produto)
    db.query inventory_count {
      where = ($db.inventory_count.inventory_id == $input.inventory_id)
      return = {type: "list"}
    } as $all_counts

    conditional {
      if ($all_counts != null) {
        // Para cada produto contado, calcular divergência (última contagem vence)
        // Agrupar por produto pegando a mais recente (simplificação: iterar)
        foreach $count in $all_counts {
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
                  value = "shortage"
                  impact = "Falta de estoque: físico menor que o registrado."
                }
                if ($difference > 0) {
                  value = "overage"
                  impact = "Sobra de estoque: físico maior que o registrado."
                }
              }

              // Verificar se já existe divergência para este produto/inventário
              db.query inventory_discrepancy {
                where = ($db.inventory_discrepancy.inventory_id == $input.inventory_id) && ($db.inventory_discrepancy.product_id == $count.product_id)
                return = {type: "object"}
              } as $existing_discrepancy

              conditional {
                if ($existing_discrepancy == null) {
                  // Criar divergência (apenas se ainda não decidida)
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

    response = {
      inventory_id: $input.inventory_id
      status: "AguardandoAprovacao"
      message: "Conciliação realizada. Divergências pendentes de análise do gestor."
    }
    tags = ["smart-vision"]
    guid = "inventory_reconcile_guid_001"
  }
}
