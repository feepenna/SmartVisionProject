// Listar alertas de estoque com filtros (Change 05)
// Inclui nome/SKU/categoria do produto na resposta para exibição no dashboard.
// Permissões: leitura para todos os perfis (Gestor, Estoquista, Vendedor, Técnico,
// admin e member legados). Histórico nunca é apagado: resolvidos aparecem quando pedidos.
query alerts verb=GET {
  api_group = "Smart Vision"

  input {
    int user_id
    text status? filters=trim
    text alert_type? filters=trim
    int product_id?
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
      error = "Seu perfil não tem permissão para consultar alertas."
    }

    // 2. Validar filtros quando enviados
    precondition ($input.status == null || $input.status == "Ativo" || $input.status == "EmAcompanhamento" || $input.status == "Resolvido") {
      error_type = "inputerror"
      error = "Status inválido. Use: Ativo, EmAcompanhamento ou Resolvido."
    }

    precondition ($input.alert_type == null || $input.alert_type == "LOW_STOCK" || $input.alert_type == "INACTIVE") {
      error_type = "inputerror"
      error = "Tipo de alerta inválido. Use: LOW_STOCK ou INACTIVE."
    }

    // 3. Listar alertas (mais recente primeiro), com filtros opcionais
    db.query stock_alert {
      where = (($input.status == null) || ($db.stock_alert.status == $input.status))
        && (($input.alert_type == null) || ($db.stock_alert.alert_type == $input.alert_type))
        && (($input.product_id == null) || ($db.stock_alert.product_id == $input.product_id))
      sort = {created_at: "desc"}
      return = {type: "list"}
    } as $alertas

    // 4. Enriquecer com dados do produto (apresentação, sem regra de negócio)
    var $resultado {
      value = []
    }

    conditional {
      if ($alertas != null) {
        foreach $a in $alertas {
          db.get product {
            field_name = "id"
            field_value = $a.product_id
          } as $produto

          var $item {
            value = {}
              |set:"id":$a.id
              |set:"product_id":$a.product_id
              |set:"produto_nome":$produto.name
              |set:"produto_sku":$produto.sku
              |set:"categoria":$produto.category
              |set:"alert_type":$a.alert_type
              |set:"status":$a.status
              |set:"criticality":$a.criticality
              |set:"observed_stock":$a.observed_stock
              |set:"observed_min_stock":$a.observed_min_stock
              |set:"detected_at":$a.detected_at
              |set:"status_updated_at":$a.status_updated_at
              |set:"resolved_at":$a.resolved_at
              |set:"resolution":$a.resolution
              |set:"condition_cleared_at":$a.condition_cleared_at
              |set:"opened_by":$a.opened_by
              |set:"updated_by":$a.updated_by
              |set:"notes":$a.notes
          }

          array.push $resultado {
            value = $item
          }
        }
      }
    }

    response = $resultado
    tags = ["smart-vision"]
    guid = "alerts_list_guid_001"
  }
}
