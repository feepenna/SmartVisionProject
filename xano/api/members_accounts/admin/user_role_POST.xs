// For admin to update the role of a user on the same account
query "admin/user_role" verb=POST {
  api_group = "Members & Accounts"
  auth = "user"

  input {
    // The ID of the user whose role is to be updated
    int user_id
  
    // The new role to assign to the user
    text new_role
  }

  stack {
    // Retrieve the authenticated user's details
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "account_id", "role"]
    } as $admin_user
  
    // Verify the authenticated user has the 'admin' role
    function.run "Getting Started Template/role-based access control" {
      input = {user_id: $admin_user.id, required_role: "admin"}
    } as $role_check
  
    // Retrieve the target user's details to be updated
    db.get user {
      field_name = "id"
      field_value = $input.user_id
      output = ["id", "created_at", "name", "email", "account_id", "role"]
    } as $target_user
  
    // Verify that the target user exists
    precondition ($target_user != null) {
      error_type = "notfound"
      error = "Target user not found."
    }
  
    // Ensure the admin user and target user belong to the same account
    precondition ($admin_user.account_id == $target_user.account_id) {
      error_type = "accessdenied"
      error = "Admin can only update roles for users within their own account."
    }
  
    // Update the target user's role
    db.edit user {
      field_name = "id"
      field_value = $input.user_id
      enforce_hidden_fields = false
      data = {role: $input.new_role}
    } as $updated_user
  
    // Log the role update event
    function.run "Getting Started Template/create_event_log" {
      input = {
        user_id   : $admin_user.id
        account_id: $admin_user.account_id
        action    : "updated_user_role"
        metadata  : $updated_user|set:"previous_role":$target_user.role
      }
    } as $event_log
  }

  response = $updated_user
  tags = ["xano:quick-start"]
  guid = "jvlktR0WjNVq3h10_UFzYuV8F8Q"
}