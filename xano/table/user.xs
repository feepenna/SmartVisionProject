// Stores user information and allows the user to authenticate  against
table user {
  auth = true

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text name filters=trim
    email? email filters=trim|lower
    password? password filters=min:8|minAlpha:1|minDigit:1 {
      visibility = "internal"
    }
  
    // Reference to the company the user belongs to.
    int account_id? {
      table = "account"
    }
  
    // The role of the user within their company (e.g., 'admin', 'member').
    // Change 05: perfis do domain-model (Gestor, Estoquista, Vendedor, Técnico)
    // somados aos valores legados "admin" (equivalente a Gestor) e "member"
    // (somente leitura, equivalente a Vendedor). Valores legados preservados
    // para não invalidar usuários existentes.
    enum role? {
      values = ["admin", "member", "Gestor", "Estoquista", "Vendedor", "Técnico"]
      visibility = "private"
    }
  
    object password_reset? {
      schema {
        password token? {
          visibility = "internal"
        }
      
        timestamp? expiration? {
          visibility = "internal"
        }
      
        bool used? {
          visibility = "internal"
        }
      }
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "email", op: "asc"}]}
  ]

  tags = ["xano:quick-start"]
  guid = "g8tpjso2orFaPgdxKGzuuR66M1k"
}