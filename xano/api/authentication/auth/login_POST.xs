// Login and retrieve an authentication token
query "auth/login" verb=POST {
  api_group = "Authentication"

  input {
    email email? filters=trim|lower
    text password?
  }

  stack {
    // Get the user record via email
    db.get user {
      field_name = "email"
      field_value = $input.email
      output = [
        "id"
        "created_at"
        "name"
        "email"
        "password"
        "account_id"
        "role"
      ]
    } as $user
  
    // Check to make sure a user with that email exists
    precondition ($user != null) {
      error_type = "accessdenied"
      error = "Invalid Credentials."
    }
  
    // Change 06: proteção contra tentativas repetidas (rate limit server-side).
    // Conta rejeições de senha ("login_failed") deste usuário nos últimos
    // 15 minutos usando a tabela event_log existente — sem nova tabela nem
    // migration (AGENTS.md §4.1/§4.2). Janela igual à do frontend (5 falhas
    // em 900s). Falhas são registradas antes de qualquer resposta de erro.
    db.query event_log {
      where = ($db.event_log.action == "login_failed" && $db.event_log.user_id == $user.id && $db.event_log.created_at >= ("now"|timestamp_add_seconds:-900))
    } as $tentativas_falhas
  
    conditional {
      if (($tentativas_falhas|count) >= 5) {
        throw {
          name = "ratelimit"
          value = "Muitas tentativas de acesso. Aguarde alguns minutos e tente novamente."
        }
      }
    }
  
    // Check that the password matches the hashed password
    security.check_password {
      text_password = $input.password
      hash_password = $user.password
    } as $pass_result
  
    // Audita a rejeição (antes de abortar) para alimentar o rate limit acima.
    conditional {
      if (!$pass_result) {
        function.run "Getting Started Template/create_event_log" {
          input = {
            user_id   : $user.id
            account_id: $user.account_id
            action    : "login_failed"
            metadata  : {email: $user.email}
          }
        }
      }
    }
  
    // Verify that the password check passed
    precondition ($pass_result) {
      error_type = "accessdenied"
      error = "Invalid Credentials."
    }
  
    // Create an authentication token
    security.create_auth_token {
      table = "user"
      extras = {}
      expiration = 86400
      id = $user.id
    } as $authToken
  
    // Create an event log for login
    function.run "Getting Started Template/create_event_log" {
      input = {
        user_id   : $user.id
        account_id: $user.account_id
        action    : "login"
        metadata  : $user
      }
    } as $event_log
  }

  response = {authToken: $authToken, user_id: $user.id}
  tags = ["xano:quick-start"]
  guid = "g6E8E2wr8FPWccUg-4Qqxu2csFg"
}