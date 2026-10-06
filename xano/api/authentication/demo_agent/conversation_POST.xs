// This is the demo agent endpoint used to connect to the Xano Demo AI Agent that answers questions about Xano by referencing documentation. You can access your Xano Demo AI Agent in AI > Agents. 
query "demo-agent/conversation" verb=POST {
  api_group = "Authentication"
  auth = "user"

  input {
    // The ID of the conversation from the conversation table.
    int? conversation_id?
  
    json message?
  }

  stack {
    var $conversation_id {
      value = $input.conversation_id
    }
  
    var $messages {
      value = {}
    }
  
    // This condition handles the logic between new and existing conversations.
    conditional {
      if ($input.conversation_id == null || $input.conversation_id == 0) {
        // Create a new conversation if one doesn't exist.
        db.add agent_conversation {
          enforce_hidden_fields = false
          data = {created_at: "now", owner_user: $auth.id}
        } as $conversation1
      
        // Update conversation_id variable
        var.update $conversation_id {
          value = $conversation1.id
        }
      
        // Save the current user message to the database
        db.add agent_message {
          enforce_hidden_fields = false
          data = {
            created_at  : "now"
            conversation: $conversation_id
            role        : "user"
            content     : $input.message.content
          }
        } as $message1
      
        // Update messages variable
        var.update $messages {
          value = $input.message
        }
      }
    
      else {
        // Save the current user message to the database
        db.add agent_message {
          enforce_hidden_fields = false
          data = {
            created_at  : "now"
            conversation: $conversation_id
            role        : "user"
            content     : $input.message.content
          }
        } as $message1
      
        // Retrieve the existing messages within the conversation
        db.query agent_message {
          where = $db.agent_message.conversation == $input.conversation_id
          return = {type: "list"}
          output = ["role", "content"]
        } as $all_messages
      
        var.update $messages {
          value = $all_messages
        }
      }
    }
  
    // Add your agent statement here.
    group {
      stack {
        ai.agent.run "Xano Example Agent" {
          args = {}|set:"messages":$messages
          allow_tool_execution = true
        } as $Simple_Agent1
      }
    }
  
    // Update the value of the variable to be your Agent statement.
    var $agent_response {
      value = $Simple_Agent1.result
    }
  
    // Add a new record to the message table
    db.add agent_message {
      enforce_hidden_fields = false
      data = {
        created_at  : "now"
        conversation: $conversation_id
        role        : "assistant"
        content     : []|push:({}|set:"type":"text"|set:"text":$agent_response)
      }
    } as $message2
  }

  response = {
    result         : $agent_response
    conversation_id: $conversation_id
  }

  tags = ["xano:quick-start"]
  guid = "LYqXnGO64tr4WUspM1asR9k0VCA"
}