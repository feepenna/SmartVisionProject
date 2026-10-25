// Criar um novo inventário físico (Change 03)
// Permissão: qualquer usuário autenticado; opened_by é sempre $auth.id. Não altera saldo.
// Status inicial obrigatório: Aberto. Escopo: completo | categoria | localizacao.
// Valida o usuário responsável e exige o filtro correspondente ao escopo.
query inventories verb=POST {
  api_group = "Smart Vision"
  auth = "user"

  input {
    text? status? filters=trim
    text scope filters=trim
    text? category_filter? filters=trim
    text? location_filter? filters=trim
    int? opened_by?
    text? notes? filters=trim
  }

  stack {
    // 0. O responsável é sempre o usuário autenticado (não confiar no cliente).
    precondition ($input.opened_by == null || $input.opened_by == $auth.id) {
      error_type = "accessdenied"
      error = "O responsável pela abertura deve ser o usuário autenticado."
    }

    // 1. Escopo e status inicial
    precondition ($input.scope == "completo" || $input.scope == "categoria" || $input.scope == "localizacao") {
      error_type = "inputerror"
      error = "Escopo inválido. Use: completo, categoria ou localizacao."
    }

    precondition ($input.status == null || $input.status == "" || $input.status == "Aberto") {
      error_type = "inputerror"
      error = "Um inventário deve ser criado com status Aberto."
    }

    // 2. Filtro obrigatório conforme o escopo
    conditional {
      if ($input.scope == "categoria") {
        precondition ($input.category_filter != null && $input.category_filter != "") {
          error_type = "inputerror"
          error = "Informe a categoria do inventário quando o escopo for categoria."
        }
      }
    }

    conditional {
      if ($input.scope == "localizacao") {
        precondition ($input.location_filter != null && $input.location_filter != "") {
          error_type = "inputerror"
          error = "Informe a localização do inventário quando o escopo for localizacao."
        }
      }
    }

    // 3. Responsável pela abertura deve existir (sempre o usuário autenticado)
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "name", "role"]
    } as $responsible

    precondition ($responsible != null) {
      error_type = "notfound"
      error = "Usuário responsável não encontrado."
    }

    // 4. Inserir o inventário
    db.add inventory {
      data = {
        status: "Aberto"
        scope: $input.scope
        category_filter: $input.category_filter
        location_filter: $input.location_filter
        opened_by: $auth.id
        opened_at: "now"
        closed_at: null
        notes: $input.notes
      }
    } as $inventory
  }

  response = $inventory
  tags = ["smart-vision"]
  guid = "inventory_create_guid_001"
}
