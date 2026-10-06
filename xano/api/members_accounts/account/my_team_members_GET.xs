// See the users that belong to the same account as the authenticated user
query "account/my_team_members" verb=GET {
  api_group = "Members & Accounts"
  auth = "user"

  input {
  }

  stack {
    // Get the authenticated user record
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "created_at", "name", "email", "phone", "account_id", "role"]
    } as $user
  
    // Check that the user record matches the authenticated user
    precondition ($user.id == $auth.id) {
      error_type = "accessdenied"
    }
  
    // Get the users that belong to the same account as the authenticated user
    db.query user {
      where = $db.user.account_id == $user.account_id
      return = {type: "list"}
      output = ["id", "created_at", "name", "email", "phone", "account_id"]
    } as $team_members
  }

  response = $team_members
  tags = ["xano:quick-start"]
  guid = "XfCH9jMx3zO8RLyPZUbSkFseGec"
}