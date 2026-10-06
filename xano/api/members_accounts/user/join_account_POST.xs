// Allows the user to join an existing account
query "user/join_account" verb=POST {
  api_group = "Members & Accounts"
  auth = "user"

  input {
    // The ID of the account the user wants to join.
    int account_id
  }

  stack {
    // Retrieve the authenticated user's record.
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $user
  
    // Ensure the authenticated user exists.
    precondition ($user != null) {
      error_type = "notfound"
      error = "Authenticated user not found."
    }
  
    // Retrieve the account record to ensure it exists.
    db.get account {
      field_name = "id"
      field_value = $input.account_id
    } as $account
  
    // Ensure the target account exists.
    precondition ($account != null) {
      error_type = "notfound"
      error = "Account not found."
    }
  
    // Associate the user with the specified account.
    db.edit user {
      field_name = "id"
      field_value = $user.id
      enforce_hidden_fields = false
      data = {account_id: $input.account_id}
    } as $updated_user
  
    // Log event for user joining account
    function.run "Getting Started Template/create_event_log" {
      input = {
        user_id   : $updated_user.id
        account_id: $account.id
        action    : "user_joins_account"
        metadata  : $updated_user
      }
    } as $event_log
  }

  response = $updated_user
  tags = ["xano:quick-start"]
  guid = "8MPACwyjNWLTF-tnWuKYpLV2V5Q"
}