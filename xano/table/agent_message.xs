// Stores individual messages within conversation threads.
table agent_message {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // Reference to the parent conversation thread.
    int conversation? {
      table = "agent_conversation"
    }
  
    // The role of the message sender (e.g., system, user, assistant, tool).
    enum role? {
      values = ["system", "user", "assistant", "tool"]
    }
  
    // The content of the message, compatible with AI SDK.
    json content?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "gin", field: [{name: "xdo", op: "jsonb_path_op"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["xano:quick-start"]
  guid = "VdEsQc83wPbKHXGP-C9S-xCuShI"
}