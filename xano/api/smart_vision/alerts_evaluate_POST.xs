// Avaliação idempotente de alertas de estoque (Change 05)
// Para cada produto monitorado, avalia LOW_STOCK e INACTIVE pela função reutilizável
// Smart Vision/avaliar_alerta: abre alerta quando a condição passa a valer, auto-resolve
// quando normaliza e respeita resolução manual (silenciamento). Não altera saldo nem
// gera movimentação — alertas derivam de product.current_stock e stock_movement.
// Permissões: Gestor, Estoquista ou admin (legado). Retorna contadores da execução.
query alerts/evaluate verb=POST {
  api_group = "Smart Vision"

  input {
    int user_id
  }

  stack {
    // 1. Autorização validada no backend (Gestor, Estoquista ou admin legado)
    db.get user {
      field_name = "id"
      field_value = $input.user_id
    } as $actor

    precondition ($actor != null) {
      error_type = "notfound"
      error = "Usuário não encontrado."
    }

    precondition ($actor.role == "Gestor" || $actor.role == "Estoquista" || $actor.role == "admin") {
      error_type = "forbidden"
      error = "Apenas gestores e estoquistas podem executar a avaliação de alertas."
    }

    // 2. Produtos com monitoramento ativo
    db.query product {
      where = ($db.product.alerts_enabled == true)
      sort = {id: "asc"}
      return = {type: "list"}
    } as $produtos

    var $avaliados {
      value = 0
    }

    var $criados {
      value = 0
    }

    var $resolvidos {
      value = 0
    }

    var $silenciados {
      value = 0
    }

    var $criados_low_stock {
      value = 0
    }

    var $criados_inactive {
      value = 0
    }

    conditional {
      if ($produtos != null) {
        foreach $p in $produtos {
          var.update $avaliados { value = $avaliados|add:1 }

          function.run "Smart Vision/avaliar_alerta" {
            input = {
              product_id: $p.id
              alert_type: "LOW_STOCK"
              actor_id  : $input.user_id
            }
          } as $resultado_low

          function.run "Smart Vision/avaliar_alerta" {
            input = {
              product_id: $p.id
              alert_type: "INACTIVE"
              actor_id  : $input.user_id
            }
          } as $resultado_inactive

          if ($resultado_low.acao == "criado") {
            var.update $criados { value = $criados|add:1 }
            var.update $criados_low_stock { value = $criados_low_stock|add:1 }
          }

          if ($resultado_low.acao == "resolvido") {
            var.update $resolvidos { value = $resolvidos|add:1 }
          }

          if ($resultado_low.acao == "silenciado") {
            var.update $silenciados { value = $silenciados|add:1 }
          }

          if ($resultado_inactive.acao == "criado") {
            var.update $criados { value = $criados|add:1 }
            var.update $criados_inactive { value = $criados_inactive|add:1 }
          }

          if ($resultado_inactive.acao == "resolvido") {
            var.update $resolvidos { value = $resolvidos|add:1 }
          }

          if ($resultado_inactive.acao == "silenciado") {
            var.update $silenciados { value = $silenciados|add:1 }
          }
        }
      }
    }

    response = {}
      |set:"avaliados":$avaliados
      |set:"criados":$criados
      |set:"resolvidos":$resolvidos
      |set:"silenciados":$silenciados
      |set:"criados_low_stock":$criados_low_stock
      |set:"criados_inactive":$criados_inactive
      |set:"executed_by":$input.user_id
    tags = ["smart-vision"]
    guid = "alerts_evaluate_guid_001"
  }
}
