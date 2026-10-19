// Produtos sem movimentação (Change 05)
// Diferencia Inativo (tem histórico antigo) de SemHistorico (nunca movimentado):
// sem histórico NÃO gera alerta INACTIVE, apenas é exibido para acompanhamento.
// A janela vem do parâmetro inactivity_days do endpoint, depois do produto,
// e por fim o padrão de 30 dias. A quantidade de dias decorridos é formatada
// no frontend a partir de ultima_movimentacao (timestamp).
// Permissões: leitura para todos os perfis.
query alerts/inactive verb=GET {
  api_group = "Smart Vision"

  input {
    int user_id
    int inactivity_days?
    int incluir_sem_historico?
  }

  stack {
    // 1. Autorização de leitura validada no backend
    db.get user {
      field_name = "id"
      field_value = $input.user_id
    } as $actor

    precondition ($actor != null) {
      error_type = "notfound"
      error = "Usuário não encontrado."
    }

    precondition ($actor.role == "Gestor" || $actor.role == "Estoquista" || $actor.role == "Vendedor" || $actor.role == "Técnico" || $actor.role == "admin" || $actor.role == "member") {
      error_type = "forbidden"
      error = "Seu perfil não tem permissão para consultar produtos sem movimentação."
    }

    // 2. Validar janela quando enviada
    precondition ($input.inactivity_days == null || $input.inactivity_days >= 1) {
      error_type = "inputerror"
      error = "A janela de inatividade deve ser maior ou igual a 1 dia."
    }

    // 3. Exibir SemHistorico por padrão; incluir_sem_historico = 0 oculta
    var $incluir_sem_historico {
      value = true
      if ($input.incluir_sem_historico == 0) {
        value = false
      }
    }

    // 4. Produtos monitorados
    db.query product {
      where = ($db.product.alerts_enabled == true)
      sort = {id: "asc"}
      return = {type: "list"}
    } as $produtos

    var $resultado {
      value = []
    }

    conditional {
      if ($produtos != null) {
        foreach $p in $produtos {
          // Prioridade da janela: parâmetro do request > produto > 30 dias
          var $janela_dias {
            value = 30
            if ($p.inactivity_days != null) {
              value = $p.inactivity_days
            }
            if ($input.inactivity_days != null) {
              value = $input.inactivity_days
            }
          }

          var $limite {
            value = now|add_secs_to_timestamp:($janela_dias|multiply:86400)
          }

          db.query stock_movement {
            where = ($db.stock_movement.product_id == $p.id)
            sort = {created_at: "desc"}
            return = {type: "single"}
          } as $ultima_mov

          var $situacao {
            value = "Ativo"
          }

          conditional {
            if ($ultima_mov == null) {
              var.update $situacao { value = "SemHistorico" }
            }
            else {
              if ($ultima_mov.created_at < $limite) {
                var.update $situacao { value = "Inativo" }
              }
            }
          }

          var $exibir {
            value = true
            if (!$incluir_sem_historico && ($situacao == "SemHistorico")) {
              value = false
            }
          }

          conditional {
            if ($exibir) {
              var $item {
                value = {}
                  |set:"product_id":$p.id
                  |set:"sku":$p.sku
                  |set:"nome":$p.name
                  |set:"categoria":$p.category
                  |set:"saldo":$p.current_stock
                  |set:"situacao":$situacao
                  |set:"ultima_movimentacao":$ultima_mov.created_at
                  |set:"janela_dias":$janela_dias
              }

              array.push $resultado {
                value = $item
              }
            }
          }
        }
      }
    }

    response = $resultado
    tags = ["smart-vision"]
    guid = "alerts_inactive_guid_001"
  }
}
