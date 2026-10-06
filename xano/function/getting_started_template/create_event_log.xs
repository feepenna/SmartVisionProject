// Creates a record in the event log table
// 
function "Getting Started Template/create_event_log" {
  input {
    // Unique identifier for the user who performed the action.
    int user_id
  
    // Unique identifier for the account associated with the event.
    int account_id
  
    // A description of the action performed by the user (e.g., 'login', 'created_invoice').
    text action
  
    // Additional data related to the event, such as resource IDs or old/new values.
    json metadata?
  }

  stack {
    // Add a new user event log entry
    db.add event_log {
      enforce_hidden_fields = false
      data = {
        created_at: "now"
        user_id   : $input.user_id
        account_id: $input.account_id
        action    : $input.action
        metadata  : $input.metadata
      }
    } as $new_log_entry
  }

  response = null
  tags = ["xano:quick-start"]
  guid = "qn6tsHnk4r38shx6w7fsOrQ2R_8"
}