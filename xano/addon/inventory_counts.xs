// Addon: total de contagens registradas em um inventário (Change 03).
addon inventory_counts {
  input {
    int inventory_id? {
      table = "inventory"
    }
  }

  stack {
    db.query inventory_count {
      where = $db.inventory_count.inventory_id == $input.inventory_id
      return = {type: "count"}
    }
  }

  guid = "inventory_counts_addon_guid_001"
}
