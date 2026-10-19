// Configurar parâmetros de estoque e alertas de um produto (Change 05)
// Altera apenas os campos enviados; os demais preservam o valor atual do produto.
// Validações: min_stock >= 0, target_stock >= 0 e >= min_stock (valor efetivo),
// inactivity_days >= 1, alerts_enabled 0/1. alerta aberto nunca é apagado por aqui.
// Permissões: somente Gestor (ou admin legado).
query stock-parameters verb=PATCH {
  api_group = "Smart Vision"

  input {
    int product_id
    int min_stock?
    int target_stock?
    int inactivity_days?
    int alerts_enabled?
    int user_id
  }

  stack {
    // 1. Autorização: somente gestão (Gestor ou admin legado)
    db.get user {
      field_name = "id"
      field_value = $input.user_id
    } as $actor

    precondition ($actor != null) {
      error_type = "notfound"
      error = "Usuário não encontrado."
    }

    precondition ($actor.role == "Gestor" || $actor.role == "admin") {
      error_type = "forbidden"
      error = "Apenas gestores podem alterar os parâmetros de estoque dos produtos."
    }

    // 2. Validar faixas dos valores enviados
    precondition ($input.min_stock == null || $input.min_stock >= 0) {
      error_type = "inputerror"
      error = "O estoque mínimo deve ser maior ou igual a zero."
    }

    precondition ($input.target_stock == null || $input.target_stock >= 0) {
      error_type = "inputerror"
      error = "O estoque alvo deve ser maior ou igual a zero."
    }

    precondition ($input.inactivity_days == null || $input.inactivity_days >= 1) {
      error_type = "inputerror"
      error = "A janela de inatividade deve ser maior ou igual a 1 dia."
    }

    precondition ($input.alerts_enabled == null || $input.alerts_enabled == 0 || $input.alerts_enabled == 1) {
      error_type = "inputerror"
      error = "alerts_enabled deve ser 1 (ativo) ou 0 (inativo)."
    }

    // 3. Buscar o produto
    db.get product {
      field_name = "id"
      field_value = $input.product_id
    } as $produto

    precondition ($produto != null) {
      error_type = "notfound"
      error = "Produto não encontrado."
    }

    // 4. Resolver valores efetivos (enviados sobrescrevem; resto preserva)
    var $novo_min {
      value = $produto.min_stock
      if ($input.min_stock != null) {
        value = $input.min_stock
      }
    }

    var $novo_target {
      value = $produto.target_stock
      if ($input.target_stock != null) {
        value = $input.target_stock
      }
    }

    var $nova_janela {
      value = $produto.inactivity_days
      if ($input.inactivity_days != null) {
        value = $input.inactivity_days
      }
    }

    var $novos_alertas {
      value = $produto.alerts_enabled
      if ($input.alerts_enabled == 1) {
        value = true
      }
      if ($input.alerts_enabled == 0) {
        value = false
      }
    }

    // 5. Coerência entre mínimo e alvo com os valores efetivos
    conditional {
      if ($novo_target != null) {
        precondition ($novo_target >= $novo_min) {
          error_type = "inputerror"
          error = "O estoque alvo deve ser maior ou igual ao estoque mínimo."
        }
      }
    }

    // 6. Aplicar a configuração (nenhuma movimentação é criada aqui)
    db.edit product {
      field_name = "id"
      field_value = $input.product_id
      data = {
        min_stock      : $novo_min
        target_stock   : $novo_target
        inactivity_days: $nova_janela
        alerts_enabled : $novos_alertas
      }
    } as $produto_atualizado

    response = $produto_atualizado
    tags = ["smart-vision"]
    guid = "stock_parameters_guid_001"
  }
}
