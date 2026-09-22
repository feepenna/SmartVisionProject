// Allows the authenticated user to create an account. The user creating it, becomes the admin/owner of the account
query account verb=POST {
  api_group = "Members & Accounts"
  auth = "user"

  input {
    // The name of the new account.
    text name
  
    // A brief description of the new account (optional).
    text description?
  
    // The primary location of the new account (optional).
    text location?
  }

  stack {
    // Create a new account record in the database.
    db.add account {
      enforce_hidden_fields = false
      data = {
        name       : $input.name
        description: $input.description
        location   : $input.location
        created_at : "now"
      }
    } as $new_account
  
    // Update the user record to link them to the new account and assign 'admin' role.
    db.edit user {
      field_name = "id"
      field_value = $auth.id
      enforce_hidden_fields = false
      data = {account_id: $new_account.id, role: "admin"}
    } as $updated_user
  
    // Log event for new account created
    function.run "Getting Started Template/create_event_log" {
      input = {
        user_id   : $updated_user.id
        account_id: $new_account.id
        action    : "new_account_created"
        metadata  : {}|set:"account":$new_account|set:"user":$updated_user
      }
    } as $event_log
  }

  response = {account: $new_account}
  tags = ["xano:quick-start"]
  guid = "3zhHIndQP6C0CS8SbCHuMeoK2nI"
}