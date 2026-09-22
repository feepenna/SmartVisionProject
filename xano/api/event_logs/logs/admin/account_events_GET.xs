// See all user events for a given account. Admin only
query "logs/admin/account_events" verb=GET {
  api_group = "Event Logs"
  auth = "user"

  input {
  }

  stack {
    // Get the authenticated user record
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $user
  
    // Ensure only admin users can access this endpoint.
    precondition ($user.role == "admin") {
      error_type = "accessdenied"
      error = "Access Denied: Only administrators can view account events."
    }
  
    // Retrieve all events for the specified account.
    db.query event_log {
      where = $db.event_log.account_id == $user.account_id
      sort = {event_log.created_at: "desc"}
      return = {type: "list"}
      addon = [
        {
          name : "user"
          input: {user_id: $output.user_id}
          as   : "_user"
        }
      ]
    } as $account_events
  }

  response = $account_events
  tags = ["xano:quick-start"]
  guid = "BgWg9wS5JqapDGM8fc-_I_eUYHo"
}