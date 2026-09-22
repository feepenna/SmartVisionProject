// Use this endpoint to send a welcome email to a user
query "message/send_welcome_email" verb=POST {
  api_group = "Authentication"

  input {
    // The ID of the user to send the welcome email to.
    int user_id
  }

  stack {
    // Retrieve the user record for the given user ID.
    db.get user {
      field_name = "id"
      field_value = $input.user_id
    } as $user_record
  
    // Ensure the user record exists before proceeding.
    precondition ($user_record != null) {
      error_type = "notfound"
      error = "User not found."
    }
  
    // Set the subject line for the welcome email.
    var $email_subject {
      value = "Welcome to Our Service, " ~ $user_record.name ~ "!"
    }
  
    // Construct the HTML body of the welcome email.
    var $email_body {
      value = "<html><body><h1>Welcome, " ~ $user_record.name ~ "!</h1><p>Thank you for joining our service. We're excited to have you!</p><p>Best regards,<br>The Team</p></body></html>"
    }
  
    // Send Email Function will ONLY send to the instance owner email with the free credits. Provide your own Resend API key and account for additional capability.
  
    // Send welcome email
    util.send_email {
      service_provider = "xano"
      subject = $email_subject
      message = $email_body
    } as $send_email
  
    // Log welcome email sent for user
    function.run "Getting Started Template/create_event_log" {
      input = {
        user_id   : $input.user_id
        account_id: $user_record.account_id
        action    : "welcome_email_sent"
        metadata  : {}
      }
    } as $event_log
  }

  response = $send_email
  tags = ["xano:quick-start"]
  guid = "I7iJyrF1g20uB84_1NxGpfzLOjc"
}