// Cadastrar um novo produto no catálogo.
// Permissão: usuário autenticado com perfil de gestão/estoque. O saldo inicial
// é sempre 0 e só muda via movimentação auditada.
query products verb=POST {
  api_group = "Smart Vision"
  auth = "user"

  input {
    text sku filters=trim
    text name filters=trim
    text category filters=trim
    text brand filters=trim
    text model filters=trim
    decimal cost_price?
    decimal sale_price
    int min_stock
    text location filters=trim

    // Atributos ópticos (obrigatórios para lentes)
    decimal sphere_power?
    decimal cylinder_power?
    int axis?
    decimal addition?
    text lens_type? filters=trim
    text treatment? filters=trim
    text material? filters=trim
  }

  stack {
    // 0. Validar perfil do usuário autenticado no backend.
    // "member" é o perfil legado dos usuários demo; a normalização fina de
    // perfis fica para a Change 07. Vendedor/Técnico não cadastram produtos.
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "role"]
    } as $current_user

    precondition ($current_user != null) {
      error_type = "notfound"
      error = "Usuário autenticado não encontrado."
    }

    precondition ($current_user.role == "Gestor" || $current_user.role == "Gerente" || $current_user.role == "Supervisor" || $current_user.role == "Estoquista" || $current_user.role == "admin" || $current_user.role == "member") {
      error_type = "accessdenied"
      error = "Seu perfil não tem permissão para cadastrar produtos."
    }

    // 1. Validar campos gerais obrigatórios
    precondition ($input.sku != "" && $input.name != "" && $input.category != "" && $input.brand != "" && $input.model != "" && $input.location != "") {
      error_type = "inputerror"
      error = "Preencha os campos obrigatórios: SKU, nome, categoria, marca, modelo e localização."
    }

    // 2. Validar preço e estoque mínimo não negativos
    precondition ($input.sale_price >= 0) {
      error_type = "inputerror"
      error = "O preço de venda deve ser maior ou igual a zero."
    }

    precondition ($input.min_stock >= 0) {
      error_type = "inputerror"
      error = "O estoque mínimo deve ser maior ou igual a zero."
    }

    // 3. Validar atributos técnicos quando for lente
    conditional {
      if ($input.category == "Lente Oftálmica" || $input.category == "Lente de Contato") {
        precondition ($input.sphere_power != null && $input.cylinder_power != null && $input.lens_type != null && $input.lens_type != "") {
          error_type = "inputerror"
          error = "Para lentes, informe grau esférico, grau cilíndrico e tipo de lente."
        }

        precondition ($input.axis == null || ($input.axis >= 0 && $input.axis <= 180)) {
          error_type = "inputerror"
          error = "O eixo deve estar entre 0 e 180 graus."
        }
      }
    }

    // 4. Validar se o SKU já existe
    db.has product {
      field_name = "sku"
      field_value = $input.sku
    } as $sku_exists

    precondition (!$sku_exists) {
      error_type = "badrequest"
      error = "O SKU informado já está em uso por outro produto."
    }

    // 5. Inserir o produto (saldo inicial 0; alterações somente via auditoria)
    db.add product {
      data = {
        sku           : $input.sku
        name          : $input.name
        category      : $input.category
        brand         : $input.brand
        model         : $input.model
        cost_price    : $input.cost_price
        sale_price    : $input.sale_price
        current_stock : 0
        min_stock     : $input.min_stock
        location      : $input.location
        sphere_power  : $input.sphere_power
        cylinder_power: $input.cylinder_power
        axis          : $input.axis
        addition      : $input.addition
        lens_type     : $input.lens_type
        treatment     : $input.treatment
        material      : $input.material
        created_at    : "now"
      }
    } as $new_product
  }

  response = $new_product
  tags = ["smart-vision"]
  guid = "CmgIQXv3OLXYUpTrBg9QU0KLUpE"
}
