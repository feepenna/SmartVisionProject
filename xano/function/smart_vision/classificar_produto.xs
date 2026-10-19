// Regra única de classificação de criticidade (Change 05) — faixas disjuntas:
//   critico:     saldo <= estoque mínimo (ponto de pedido atingido)
//   insuficiente: acima do mínimo, mas abaixo do estoque alvo (só com alvo definido)
//   regular:     acima do mínimo e, havendo alvo, no/além do alvo
// Reutilizada pela avaliação de alertas, pelo resumo e pela sugestão de reposição,
// garantindo que a classificação nunca seja calculada em mais de um lugar.
function "Smart Vision/classificar_produto" {
  input {
    int current_stock
    int min_stock
    int target_stock?
  }

  stack {
    var $classificacao {
      value = "regular"
      // crítico tem precedência (faixa mais grave)
      if ($input.current_stock <= $input.min_stock) {
        value = "critico"
      }
      // insuficiente só entra fora da faixa crítica e com alvo configurado
      if (($input.current_stock > $input.min_stock) && ($input.target_stock != null) && ($input.current_stock < $input.target_stock)) {
        value = "insuficiente"
      }
    }
  }

  response = $classificacao
  tags = ["smart-vision"]
  guid = "sv_classificar_produto_guid_001"
}
