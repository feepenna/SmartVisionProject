// Stores conversation threads for agents/chatbots.
table agent_conversation {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // The user who owns this conversation thread.
    int owner_user? {
      table = "user"
    }
  
    // The title or subject of the conversation.
    text title? filters=trim
  
    // Timestamp of the last message in the conversation.
    timestamp last_message_at?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "gin", field: [{name: "xdo", op: "jsonb_path_op"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["xano:quick-start"]
  guid = "WVFPqdMu4fHnDs2MFeJ6vn1aGkU"
}