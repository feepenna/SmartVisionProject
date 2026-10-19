// Sugestões de reposição calculadas no backend (Change 05)
// sugestao = max(0, target_stock - current_stock) quando há alvo;
// sem alvo: sugestao nula + parametros_incompletos = true (nada é estimado no frontend).
// custo_estimado = sugestao * cost_price quando houver custo.
// A sugestão é SOMENTE recomendação consultável: não gera compra, pedido, entrada
// nem altera saldo. Criticidade vem da regra única Smart Vision/classificar_produto.
// Permissões: leitura para todos os perfis.
query replenishment verb=GET {
  api_group = "Smart Vision"

  input {
    int user_id
    text category? filters=trim
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
      error = "Seu perfil não tem permissão para consultar sugestões de reposição."
    }

    // 2. Produtos monitorados com filtros opcionais
    db.query product {
      where = ($db.product.alerts_enabled == true)
        && (($input.category == null) || ($db.product.category == $input.category))
        && (($input.product_id == null) || ($db.product.id == $input.product_id))
      sort = {id: "asc"}
      return = {type: "list"}
    } as $produtos

    var $resultado {
      value = []
    }

    conditional {
      if ($produtos != null) {
        foreach $p in $produtos {
          // Classificação pela regra única (nunca recalculada no frontend)
          function.run "Smart Vision/classificar_produto" {
            input = {
              current_stock: $p.current_stock
              min_stock    : $p.min_stock
              target_stock : $p.target_stock
            }
          } as $classificacao

          var $parametros_incompletos {
            value = true
            if ($p.target_stock != null) {
              value = false
            }
          }

          var $sugestao {
            value = null
          }

          var $custo_estimado {
            value = null
          }

          conditional {
            if ($p.target_stock != null) {
              // max(0, alvo - saldo): nunca sugere quantidade negativa
              var $diferenca {
                value = $p.target_stock|subtract:$p.current_stock
              }

              var.update $sugestao { value = $diferenca|max:0 }

              conditional {
                if (($p.cost_price != null) && ($sugestao > 0)) {
                  var.update $custo_estimado { value = $sugestao|multiply:$p.cost_price }
                }
              }
            }
          }

          var $item {
            value = {}
              |set:"product_id":$p.id
              |set:"sku":$p.sku
              |set:"nome":$p.name
              |set:"categoria":$p.category
              |set:"saldo":$p.current_stock
              |set:"min_stock":$p.min_stock
              |set:"target_stock":$p.target_stock
              |set:"classificacao":$classificacao
              |set:"sugestao":$sugestao
              |set:"parametros_incompletos":$parametros_incompletos
              |set:"custo_estimado":$custo_estimado
          }

          array.push $resultado {
            value = $item
          }
        }
      }
    }

    response = $resultado
    tags = ["smart-vision"]
    guid = "replenishment_guid_001"
  }
}
