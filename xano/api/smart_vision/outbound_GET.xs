// Listar operacoes de saida (Change 04)
query outbound verb=GET {
  api_group = "Smart Vision"

  input {
    int? id
    text? type
    text? status
    int? product_id
    int? user_id
    text? from_date
    text? to_date
  }

  stack {
    conditional {
      if ($input.id != null) {
        db.get stock_outbound {
          field_name = "id"
          field_value = $input.id
        } as $single_outbound
        precondition ($single_outbound != null) {
          error_type = "notfound"
          error = "Operacao de saida nao encontrada."
        }
      }
    }

    conditional {
      if ($input.id == null) {
        db.query stock_outbound {
          where = ($db.stock_outbound.type ==? $input.type) && ($db.stock_outbound.status ==? $input.status) && ($db.stock_outbound.product_id ==? $input.product_id) && ($db.stock_outbound.user_id ==? $input.user_id)
          sort = {created_at: "desc"}
          return = {type: "list"}
        } as $outbounds
      }
    }
  }

  response = (($input.id != null) ? $single_outbound : (($outbounds != null) ? $outbounds : []))
  tags = ["smart-vision"]
  guid = "outbound_list_guid_001"
}
