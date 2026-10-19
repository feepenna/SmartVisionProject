// Avalia UMA condição (LOW_STOCK ou INACTIVE) de UM produto e aplica o ciclo de vida
// do alerta (Change 05): cria, auto-resolve ou registra a normalização da condição.
// Idempotente: reexecutar sem mudança de saldo/movimentação não duplica alertas.
// Regras:
//   - no máximo UM alerta aberto por (produto, tipo);
//   - resolução manual enquanto a condição persiste silencia a reabertura até a
//     condição normalizar (condition_cleared_at nulo);
//   - auto-resolução grava resolution + condition_cleared_at (histórico preservado);
//   - produtos sem histórico nunca geram INACTIVE.
// Não escreve em estoque: deriva de product.current_stock e stock_movement.
function "Smart Vision/avaliar_alerta" {
  input {
    int product_id
    text alert_type filters=trim
    int actor_id?
  }

  stack {
    // 1. Tipo de condição válido
    precondition ($input.alert_type == "LOW_STOCK" || $input.alert_type == "INACTIVE") {
      error_type = "inputerror"
      error = "Tipo de alerta inválido. Use: LOW_STOCK ou INACTIVE."
    }

    // 2. Produto monitorado
    db.get product {
      field_name = "id"
      field_value = $input.product_id
    } as $product

    precondition ($product != null) {
      error_type = "notfound"
      error = "Produto não encontrado."
    }

    // 3. Classificação atual pela regra única
    function.run "Smart Vision/classificar_produto" {
      input = {
        current_stock: $product.current_stock
        min_stock    : $product.min_stock
        target_stock : $product.target_stock
      }
    } as $classificacao

    // 4. Condição atual para o tipo avaliado
    var $condicao {
      value = false
      // LOW_STOCK: saldo dentro do estoque mínimo
      if (($input.alert_type == "LOW_STOCK") && ($product.current_stock <= $product.min_stock)) {
        value = true
      }
    }

    var $janela_dias {
      value = 30
      if ($product.inactivity_days != null) {
        value = $product.inactivity_days
      }
    }

    var $limite {
      value = now|add_secs_to_timestamp:($janela_dias|multiply:86400)
    }

    db.query stock_movement {
      where = ($db.stock_movement.product_id == $input.product_id)
      sort = {created_at: "desc"}
      return = {type: "single"}
    } as $ultima_mov

    var $tem_historico {
      value = false
      if ($ultima_mov != null) {
        value = true
      }
    }

    conditional {
      // INACTIVE: somente com histórico existente (sem histórico ≠ inativo)
      if (($input.alert_type == "INACTIVE") && $tem_historico && ($ultima_mov.created_at < $limite)) {
        var.update $condicao { value = true }
      }
    }

    // 5. Monitoramento desativado não cria nem resolve: apenas informa
    var $acao {
      value = "nenhuma"
      if ($product.alerts_enabled == false) {
        value = "ignorado"
      }
    }

    // 6. Último alerta deste par (produto, tipo) — base do ciclo de vida
    db.query stock_alert {
      where = ($db.stock_alert.product_id == $input.product_id) && ($db.stock_alert.alert_type == $input.alert_type)
      sort = {created_at: "desc"}
      return = {type: "single"}
    } as $ultimo

    var $aberto {
      value = false
      if (($ultimo != null) && ($ultimo.status != "Resolvido")) {
        value = true
      }
    }

    conditional {
      // A. Condição valendo e nenhum alerta aberto: cria (respeitando silenciamento)
      if ($condicao && !$aberto && ($product.alerts_enabled != false)) {
        var $silenciado {
          value = false
          if (($ultimo != null) && ($ultimo.status == "Resolvido") && ($ultimo.resolution == "manual") && ($ultimo.condition_cleared_at == null)) {
            value = true
          }
        }

        conditional {
          if ($silenciado) {
            var.update $acao { value = "silenciado" }
          }
          else {
            db.add stock_alert {
              data = {
                product_id         : $product.id
                alert_type         : $input.alert_type
                status             : "Ativo"
                criticality        : $classificacao
                observed_stock     : $product.current_stock
                observed_min_stock : $product.min_stock
                detected_at        : "now"
                status_updated_at  : "now"
                opened_by          : $input.actor_id
              }
            } as $novo_alerta

            var.update $acao { value = "criado" }
          }
        }
      }

      // B. Condição normalizada com alerta aberto: auto-resolução registrada
      if (!$condicao && $aberto) {
        db.edit stock_alert {
          field_name = "id"
          field_value = $ultimo.id
          data = {
            status              : "Resolvido"
            resolution          : "condicao_normalizada"
            condition_cleared_at: "now"
            resolved_at         : "now"
            status_updated_at   : "now"
          }
        } as $alerta_resolvido

        var.update $acao { value = "resolvido" }
      }

      // C. Sem alerta aberto e o último resolvido ainda sem registro de normalização:
      //    grava condition_cleared_at para permitir um novo ciclo rastreável depois
      if (!$condicao && !$aberto && ($ultimo != null) && ($ultimo.status == "Resolvido") && ($ultimo.condition_cleared_at == null)) {
        db.edit stock_alert {
          field_name = "id"
          field_value = $ultimo.id
          data = {
            condition_cleared_at: "now"
            status_updated_at   : "now"
          }
        } as $condicao_registrada

        var.update $acao { value = "condicao_normalizada" }
      }
    }
  }

  response = {}
    |set:"product_id":$product.id
    |set:"alert_type":$input.alert_type
    |set:"classificacao":$classificacao
    |set:"condicao":$condicao
    |set:"tem_historico":$tem_historico
    |set:"acao":$acao
  tags = ["smart-vision"]
  guid = "sv_avaliar_alerta_guid_001"
}
