// Resumo ao vivo do painel de alertas (Change 05)
// Contagens de alertas abertos por tipo/status/criticidade, cobertura de parâmetros
// e inatividade calculada em tempo de consulta (não depende de avaliação prévia).
// Permissões: leitura para todos os perfis. Retorna actor.role para o frontend
// esconder botões fora do perfil (UX; a segurança continua no backend).
query alerts/summary verb=GET {
  api_group = "Smart Vision"

  input {
    int user_id
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
      error = "Seu perfil não tem permissão para consultar o resumo de alertas."
    }

    // 2. Contagens de alertas (abertos = status diferente de Resolvido)
    db.query stock_alert {
      where = ($db.stock_alert.status != "Resolvido")
      return = {type: "count"}
    } as $ativos

    db.query stock_alert {
      where = ($db.stock_alert.status == "Ativo")
      return = {type: "count"}
    } as $contagem_ativo

    db.query stock_alert {
      where = ($db.stock_alert.status == "EmAcompanhamento")
      return = {type: "count"}
    } as $contagem_acompanhamento

    db.query stock_alert {
      where = ($db.stock_alert.status != "Resolvido") && ($db.stock_alert.alert_type == "LOW_STOCK")
      return = {type: "count"}
    } as $ativos_low_stock

    db.query stock_alert {
      where = ($db.stock_alert.status != "Resolvido") && ($db.stock_alert.alert_type == "INACTIVE")
      return = {type: "count"}
    } as $ativos_inactive

    db.query stock_alert {
      where = ($db.stock_alert.status != "Resolvido") && ($db.stock_alert.criticality == "critico")
      return = {type: "count"}
    } as $criticos

    // 3. Cobertura de parâmetros de reposição
    db.query product {
      where = ($db.product.alerts_enabled == true)
      return = {type: "count"}
    } as $monitorados

    db.query product {
      where = ($db.product.alerts_enabled == true) && ($db.product.target_stock == null)
      return = {type: "count"}
    } as $parametros_incompletos

    // 4. Inatividade ao vivo (janela por produto, default 30 dias)
    db.query product {
      where = ($db.product.alerts_enabled == true)
      sort = {id: "asc"}
      return = {type: "list"}
    } as $lista_produtos

    var $inativos {
      value = 0
    }

    var $sem_historico {
      value = 0
    }

    conditional {
      if ($lista_produtos != null) {
        foreach $p in $lista_produtos {
          var $janela_dias {
            value = 30
            if ($p.inactivity_days != null) {
              value = $p.inactivity_days
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

          conditional {
            // Sem histórico nunca é tratado como inativo
            if ($ultima_mov == null) {
              var.update $sem_historico { value = $sem_historico|add:1 }
            }
            else {
              if ($ultima_mov.created_at < $limite) {
                var.update $inativos { value = $inativos|add:1 }
              }
            }
          }
        }
      }
    }

    response = {}
      |set:"alertas_ativos":$ativos
      |set:"alertas_em_acompanhamento":$contagem_acompanhamento
      |set:"alertas_em_aberto_status_ativo":$contagem_ativo
      |set:"alertas_criticos":$criticos
      |set:"ativos_low_stock":$ativos_low_stock
      |set:"ativos_inactive":$ativos_inactive
      |set:"produtos_monitorados":$monitorados
      |set:"parametros_incompletos":$parametros_incompletos
      |set:"produtos_inativos":$inativos
      |set:"produtos_sem_historico":$sem_historico
      |set:"actor_id":$actor.id
      |set:"actor_role":$actor.role
    tags = ["smart-vision"]
    guid = "alerts_summary_guid_001"
  }
}
