// Transição manual de status de um alerta (Change 05)
// Transições permitidas: Ativo -> EmAcompanhamento, Ativo -> Resolvido,
// EmAcompanhamento -> Resolvido. Resolvido é estado final (não reabre, não apaga).
// Resolver exige responsável (updated_by), grava resolved_at e resolution="manual";
// condition_cleared_at só é preenchido quando a condição já normalizou — se ainda
// vale, a avaliação não recria o alerta até a condição normalizar (silenciamento).
// Permissões: Gestor, Estoquista ou admin (legado).
query alerts/status verb=POST {
  api_group = "Smart Vision"

  input {
    int alert_id
    text status filters=trim
    text notes?
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
      error = "Apenas gestores e estoquistas podem alterar o status de alertas."
    }

    // 2. Status destino válido
    precondition ($input.status == "Ativo" || $input.status == "EmAcompanhamento" || $input.status == "Resolvido") {
      error_type = "inputerror"
      error = "Status destino inválido. Use: Ativo, EmAcompanhamento ou Resolvido."
    }

    // 3. Buscar o alerta
    db.get stock_alert {
      field_name = "id"
      field_value = $input.alert_id
    } as $alerta

    precondition ($alerta != null) {
      error_type = "notfound"
      error = "Alerta não encontrado."
    }

    // 4. Resolvido é estado final: histórico preservado, sem reabertura
    precondition ($alerta.status != "Resolvido") {
      error_type = "badrequest"
      error = "Alerta já resolvido não pode mudar de status (estado final, histórico preservado)."
    }

    // 5. Validar transição permitida
    var $transicao_valida {
      value = false
      if (($alerta.status == "Ativo") && ($input.status == "EmAcompanhamento")) {
        value = true
      }
      if (($alerta.status == "Ativo") && ($input.status == "Resolvido")) {
        value = true
      }
      if (($alerta.status == "EmAcompanhamento") && ($input.status == "Resolvido")) {
        value = true
      }
    }

    precondition ($transicao_valida) {
      error_type = "badrequest"
      error = "Transição de estado não permitida de " + $alerta.status + " para " + $input.status + "."
    }

    // 6. Ao resolver, registrar se a condição já normalizou (define silenciamento)
    var $condicao_normalizada {
      value = false
    }

    conditional {
      if ($input.status == "Resolvido") {
        db.get product {
          field_name = "id"
          field_value = $alerta.product_id
        } as $produto

        var $condicao_ainda_vale {
          value = false
          // LOW_STOCK: saldo ainda dentro do mínimo
          if (($alerta.alert_type == "LOW_STOCK") && ($produto != null) && ($produto.current_stock <= $produto.min_stock)) {
            value = true
          }
        }

        conditional {
          // INACTIVE: última movimentação ainda além da janela (com histórico)
          if (($alerta.alert_type == "INACTIVE") && ($produto != null)) {
            var $janela_dias {
              value = 30
              if ($produto.inactivity_days != null) {
                value = $produto.inactivity_days
              }
            }

            var $limite {
              value = now|add_secs_to_timestamp:($janela_dias|multiply:86400)
            }

            db.query stock_movement {
              where = ($db.stock_movement.product_id == $alerta.product_id)
              sort = {created_at: "desc"}
              return = {type: "single"}
            } as $ultima_mov

            conditional {
              if (($ultima_mov != null) && ($ultima_mov.created_at < $limite)) {
                var.update $condicao_ainda_vale { value = true }
              }
            }
          }
        }

        var.update $condicao_normalizada {
          value = !$condicao_ainda_vale
        }
      }
    }

    // 7. Montar a atualização preservando campos históricos
    //    (notes só é gravado quando informado no request)
    var $notas {
      value = $alerta.notes
      if ($input.notes != null) {
        value = $input.notes
      }
    }

    var $novo_resolved_at {
      value = $alerta.resolved_at
    }

    var $nova_resolution {
      value = $alerta.resolution
    }

    var $novo_condition_cleared {
      value = $alerta.condition_cleared_at
    }

    conditional {
      if ($input.status == "Resolvido") {
        var.update $novo_resolved_at { value = "now" }
        var.update $nova_resolution { value = "manual" }
      }
      // Condição já normalizada no momento da resolução manual
      if (($input.status == "Resolvido") && $condicao_normalizada) {
        var.update $novo_condition_cleared { value = "now" }
      }
    }

    var $atualizacao {
      value = {}
        |set:"status":$input.status
        |set:"status_updated_at":"now"
        |set:"updated_by":$input.user_id
        |set:"notes":$notas
        |set:"resolved_at":$novo_resolved_at
        |set:"resolution":$nova_resolution
        |set:"condition_cleared_at":$novo_condition_cleared
    }

    db.edit stock_alert {
      field_name = "id"
      field_value = $input.alert_id
      data = $atualizacao
    } as $alerta_atualizado

    response = $alerta_atualizado
    tags = ["smart-vision"]
    guid = "alerts_status_guid_001"
  }
}
