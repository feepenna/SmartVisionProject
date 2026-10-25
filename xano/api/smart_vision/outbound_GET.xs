// Listar operações de saída (Change 04)
// Permissão: qualquer usuário autenticado (consulta/histórico).
query outbound verb=GET {
  api_group = "Smart Vision"
  auth = "user"

  input {
    int? id?
    text? type?
    text? status?
    int? product_id?
    int? user_id?
    timestamp? from_date?
    timestamp? to_date?
  }

  stack {
    var $result {
      value = []
    }

    conditional {
      if ($input.id != null) {
        db.get stock_outbound {
          field_name = "id"
          field_value = $input.id
        } as $single_outbound
        precondition ($single_outbound != null) {
          error_type = "notfound"
          error = "Operação de saída não encontrada."
        }

        var.update $result {
          value = $single_outbound
        }
      }
      else {
        db.query stock_outbound {
          where = ($db.stock_outbound.type ==? $input.type) && ($db.stock_outbound.status ==? $input.status) && ($db.stock_outbound.product_id ==? $input.product_id) && ($db.stock_outbound.user_id ==? $input.user_id) && ($db.stock_outbound.created_at >=? $input.from_date) && ($db.stock_outbound.created_at <=? $input.to_date)
          sort = {created_at: "desc"}
          return = {type: "list"}
        } as $outbounds

        var.update $result {
          value = $outbounds
        }
      }
    }
  }

  response = $result
  tags = ["smart-vision"]
  guid = "outbound_list_guid_001"
}
