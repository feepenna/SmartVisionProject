// Stores information about accounts that users belong to
table account {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // The name of the company.
    text name? filters=trim
  
    // A brief description of the company.
    text description? filters=trim
  
    text location? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "gin", field: [{name: "xdo", op: "jsonb_path_op"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["xano:quick-start"]
  guid = "ny8yWAEDvYG_siNE6ohJbNk3Cqw"
}