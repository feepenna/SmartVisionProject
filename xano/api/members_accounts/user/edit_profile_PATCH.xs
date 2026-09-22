// Update a user's profile
query "user/edit_profile" verb=PATCH {
  api_group = "Members & Accounts"
  auth = "user"

  input {
    // The user's updated name.
    text name?
  
    // The user's updated email address.
    email email?
  }

  stack {
    // Retrieve user record based on auth ID
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "created_at", "name", "email", "phone", "account_id", "role"]
    } as $user
  
    // Get the inputs in an object
    util.get_all_input as $inputs
  
    // Check that the user record matches the auth ID
    precondition ($user.id == $auth.id) {
      error_type = "accessdenied"
      error = "You don't have access to edit this!"
    }
  
    // Update the user info with the provided information
    db.patch user {
      field_name = "id"
      field_value = $user.id
      data = $inputs|filter_empty_text:""
    } as $updated_user_info
  
    // Create an event log for updated user info
    function.run "Getting Started Template/create_event_log" {
      input = {
        user_id   : $user.id
        account_id: $user.account_id
        action    : "updated_user_information"
        metadata  : {}|set:"updated_info":$updated_user_info|set:"previous_info":$user
      }
    } as $event_log
  }

  response = $updated_user_info
  tags = ["xano:quick-start"]
  guid = "xG1CprVqq4oD9mrmomplyisTE2Y"
}