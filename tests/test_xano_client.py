# tests/test_xano_client.py
"""Testes unitários para o serviço xano_client (Smart Vision).

Cobre a validação de entradas, chamadas de API para entrada e saída de estoque,
bloqueio de saldo negativo e auditoria.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

import requests

from services import xano_client


class TestXanoClient(unittest.TestCase):

    def setUp(self):
        self.mock_base_url = "https://mock.xano.io/api"
        self.env_patcher = patch.dict(os.environ, {"XANO_BASE_URL": self.mock_base_url})
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    def test_get_base_url_success(self):
        """Valida obtenção correta da URL base com remoção de barra final."""
        with patch.dict(os.environ, {"XANO_BASE_URL": "https://test.xano.io/api/"}):
            url = xano_client.get_base_url()
            self.assertEqual(url, "https://test.xano.io/api")

    def test_get_base_url_missing_raises_error(self):
        """Valida que ausência de XANO_BASE_URL lança EnvironmentError explicativo."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(EnvironmentError) as ctx:
                xano_client.get_base_url()
            self.assertIn("XANO_BASE_URL must be set", str(ctx.exception))

    @patch("requests.post")
    def test_record_stock_entry_success(self, mock_post):
        """Valida fluxo de sucesso ao registrar entrada de estoque com auditoria."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "audit": {
                "id": 1,
                "product_id": 10,
                "movement_type": "entry",
                "quantity": 5,
                "previous_stock": 2,
                "new_stock": 7,
                "reason": "NF 1234 - Compra de fornecedor",
                "user_id": 1,
                "unit_cost": 15.50,
                "supplier_id": "SUPP-001",
                "invoice": "NF-1234",
                "batch_id": "BATCH-001",
            },
            "product": {
                "id": 10,
                "name": "Armação Acetato Classic",
                "current_stock": 7,
            },
        }
        mock_post.return_value = mock_response

        payload = {
            "product_id": 10,
            "quantity": 5,
            "reason": "NF 1234 - Compra de fornecedor",
            "unit_cost": 15.50,
            "supplier_id": "SUPP-001",
            "invoice": "NF-1234",
            "batch_id": "BATCH-001",
            "user_id": 1,
        }
        result = xano_client.record_stock_entry(payload)

        mock_post.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/stock_entry",
            json=payload,
            timeout=10,
        )
        self.assertIn("audit", result)
        self.assertIn("product", result)
        self.assertEqual(result["product"]["current_stock"], 7)

    def test_record_stock_entry_validation_errors(self):
        """Valida rejeição de entradas inválidas: quantidade <= 0, sem produto ou sem motivo."""
        # Sem product_id
        with self.assertRaises(ValueError) as ctx:
            xano_client.record_stock_entry({"product_id": None, "quantity": 5, "reason": "Teste"})
        self.assertIn("product_id", str(ctx.exception))

        # Quantidade zero ou negativa
        with self.assertRaises(ValueError) as ctx:
            xano_client.record_stock_entry({"product_id": 1, "quantity": 0, "reason": "Teste", "unit_cost": 10})
        self.assertIn("maior que zero", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            xano_client.record_stock_entry({"product_id": 1, "quantity": -3, "reason": "Teste", "unit_cost": 10})
        self.assertIn("maior que zero", str(ctx.exception))

        # Motivo vazio ou somente espaços
        with self.assertRaises(ValueError) as ctx:
            xano_client.record_stock_entry({"product_id": 1, "quantity": 2, "reason": "   ", "unit_cost": 10})
        self.assertIn("motivo", str(ctx.exception).lower())

        # unit_cost missing
        with self.assertRaises(ValueError) as ctx:
            xano_client.record_stock_entry({"product_id": 1, "quantity": 2, "reason": "Teste"})
        self.assertIn("unit_cost", str(ctx.exception).lower())

        # unit_cost negative
        with self.assertRaises(ValueError) as ctx:
            xano_client.record_stock_entry({"product_id": 1, "quantity": 2, "reason": "Teste", "unit_cost": -5})
        self.assertIn("maior ou igual a zero", str(ctx.exception))

    @patch("requests.post")
    def test_record_stock_exit_success(self, mock_post):
        """Valida fluxo de saída de estoque com atualização de saldo e auditoria."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "audit": {
                "id": 2,
                "product_id": 10,
                "movement_type": "exit",
                "quantity": 2,
                "previous_stock": 7,
                "new_stock": 5,
                "reason": "Venda Balcão Pedido #402",
                "user_id": 2,
            },
            "product": {
                "id": 10,
                "name": "Armação Acetato Classic",
                "current_stock": 5,
            },
        }
        mock_post.return_value = mock_response

        payload = {
            "product_id": 10,
            "quantity": 2,
            "reason": "Venda Balcão Pedido #402",
            "user_id": 2,
        }
        result = xano_client.record_stock_exit(payload)

        mock_post.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/stock_exit",
            json=payload,
            timeout=10,
        )
        self.assertEqual(result["product"]["current_stock"], 5)
        self.assertEqual(result["audit"]["movement_type"], "exit")

    @patch("requests.post")
    def test_record_stock_exit_success_with_justification(self, mock_post):
        """Valida fluxo de saída com justificativa para LOSS ou DAMAGE."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "audit": {
                "id": 3,
                "product_id": 10,
                "movement_type": "exit",
                "quantity": 1,
                "previous_stock": 3,
                "new_stock": 2,
                "reason": "DAMAGE",
                "justification": "Quebra acidental durante manuseio",
                "reference_text": "NF-5678",
                "user_id": 1,
            },
            "product": {
                "id": 10,
                "name": "Armação Acetato Classic",
                "current_stock": 2,
            },
        }
        mock_post.return_value = mock_response

        payload = {
            "product_id": 10,
            "quantity": 1,
            "reason": "DAMAGE",
            "justification": "Quebra acidental durante manuseio",
            "reference_text": "NF-5678",
            "user_id": 1,
        }
        result = xano_client.record_stock_exit(payload)

        mock_post.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/stock_exit",
            json=payload,
            timeout=10,
        )
        self.assertEqual(result["product"]["current_stock"], 2)
        self.assertEqual(result["audit"]["reason"], "DAMAGE")
        self.assertEqual(result["audit"]["justification"], "Quebra acidental durante manuseio")
        self.assertEqual(result["audit"]["reference_text"], "NF-5678")

    @patch("requests.post")
    def test_record_stock_exit_insufficient_stock_error(self, mock_post):
        """Valida que saldo insuficiente (tentativa de saldo negativo) retorna erro HTTP 400 do backend."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 400
        mock_response.text = '{"message": "Estoque insuficiente. A saída deixaria o saldo negativo."}'
        http_error = requests.HTTPError("400 Client Error: Bad Request", response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        payload = {
            "product_id": 10,
            "quantity": 999,
            "reason": "Venda grande",
        }
        with self.assertRaises(requests.HTTPError) as ctx:
            xano_client.record_stock_exit(payload)

        self.assertIn("Estoque insuficiente", str(ctx.exception))

    @patch("requests.post")
    def test_record_stock_exit_insufficient_stock_with_justification_error(self, mock_post):
        """Valida que saída com LOSS/DAMAGE sem justificativa lança ValueError antes da chamada HTTP."""
        mock_post.return_value = MagicMock(spec=requests.Response)
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"audit": {}, "product": {}}

        payload = {
            "product_id": 10,
            "quantity": 1,
            "reason": "DAMAGE",
            # justificativa faltando
        }
        with self.assertRaises(ValueError) as ctx:
            xano_client.record_stock_exit(payload)
        self.assertIn("justificativa", str(ctx.exception).lower())

    def test_record_stock_exit_validation_errors(self):
        """Valida rejeição de saídas com dados inválidos."""
        with self.assertRaises(ValueError):
            xano_client.record_stock_exit({"product_id": None, "quantity": 1, "reason": "Baixa"})

        with self.assertRaises(ValueError):
            xano_client.record_stock_exit({"product_id": 1, "quantity": 0, "reason": "Baixa"})

        with self.assertRaises(ValueError):
            xano_client.record_stock_exit({"product_id": 1, "quantity": 1, "reason": ""})

        with self.assertRaises(ValueError):
            xano_client.record_stock_exit({"product_id": 1, "quantity": 1, "reason": "DAMAGE"})

    @patch("requests.post")
    def test_record_stock_exit_damage_without_justification_rejected(self, mock_post):
        """Valida que saída com reason DAMAGE sem justification lança ValueError no cliente."""
        mock_post.return_value = MagicMock(spec=requests.Response)
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"audit": {}, "product": {}}

        payload = {
            "product_id": 10,
            "quantity": 1,
            "reason": "DAMAGE",
            # sem justification
        }
        with self.assertRaises(ValueError) as ctx:
            xano_client.record_stock_exit(payload)
        self.assertIn("justificativa", str(ctx.exception).lower())

    @patch("requests.post")
    def test_record_stock_exit_sale_no_justification_needed(self, mock_post):
        """Valida que saída com reason SALE não exige justification."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "audit": {
                "id": 4,
                "product_id": 10,
                "movement_type": "exit",
                "quantity": 3,
                "previous_stock": 10,
                "new_stock": 7,
                "reason": "SALE",
                "user_id": 1,
            },
            "product": {
                "id": 10,
                "name": "Armação Acetato Classic",
                "current_stock": 7,
            },
        }
        mock_post.return_value = mock_response

        payload = {
            "product_id": 10,
            "quantity": 3,
            "reason": "SALE",
            "user_id": 1,
        }
        result = xano_client.record_stock_exit(payload)

        self.assertEqual(result["audit"]["reason"], "SALE")
        self.assertNotIn("justification", result["audit"])

    @patch("requests.post")
    def test_record_stock_exit_insufficient_stock_no_call_to_ledger(self, mock_post):
        """Valida que saldo insuficiente bloqueia transação sem chamar ledger."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 400
        mock_response.text = '{"message": "Estoque insuficiente. A saída deixaria o saldo negativo."}'
        http_error = requests.HTTPError("400 Client Error: Bad Request", response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        payload = {
            "product_id": 10,
            "quantity": 15,
            "reason": "Venda",
        }
        with self.assertRaises(requests.HTTPError) as ctx:
            xano_client.record_stock_exit(payload)
        # Verify the endpoint was called (validation happens server-side)
        mock_post.assert_called_once()

    def test_record_stock_exit_validation_negative_quantity(self):
        """Valida rejeição de saída com quantidade negativa."""
        with self.assertRaises(ValueError) as ctx:
            xano_client.record_stock_exit({"product_id": 1, "quantity": -5, "reason": "Teste"})
        self.assertIn("maior que zero", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()