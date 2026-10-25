import os
import unittest
from unittest.mock import MagicMock, patch

import requests

from services import xano_client


class TestOutboundClient(unittest.TestCase):
    def setUp(self):
        self.env_patcher = patch.dict(
            os.environ,
            {"XANO_BASE_URL": "https://mock.xano.io/api"},
            clear=False,
        )
        self.env_patcher.start()
        self.addCleanup(self.env_patcher.stop)

    @staticmethod
    def _response(payload):
        response = MagicMock(spec=requests.Response)
        response.status_code = 200
        response.json.return_value = payload
        response.raise_for_status.return_value = None
        return response

    @patch("services.xano_client.requests.post")
    def test_create_outbound_sale(self, mock_post):
        payload = {
            "type": "SALE",
            "product_id": 1,
            "quantity": 2,
            "reason": "Venda",
        }
        mock_post.return_value = self._response(
            {"id": 1, "type": "SALE", "status": "Pendente"}
        )

        result = xano_client.create_outbound(payload, auth_token="token-123")

        self.assertEqual(result["type"], "SALE")
        mock_post.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/outbound",
            json=payload,
            headers={"Authorization": "Bearer token-123"},
            timeout=10,
        )

    def test_create_outbound_loss_requires_justification(self):
        with self.assertRaises(ValueError):
            xano_client.create_outbound(
                {
                    "type": "LOSS",
                    "product_id": 1,
                    "quantity": 1,
                    "reason": "Perda",
                }
            )

    def test_create_outbound_rejects_invalid_type(self):
        with self.assertRaises(ValueError):
            xano_client.create_outbound(
                {
                    "type": "INVALID",
                    "product_id": 1,
                    "quantity": 1,
                    "reason": "Teste",
                }
            )

    def test_create_outbound_rejects_non_positive_quantity(self):
        with self.assertRaises(ValueError):
            xano_client.create_outbound(
                {
                    "type": "SALE",
                    "product_id": 1,
                    "quantity": 0,
                    "reason": "Teste",
                }
            )

    @patch("services.xano_client.requests.get")
    def test_list_outbounds_with_auth_and_filters(self, mock_get):
        mock_get.return_value = self._response([])

        result = xano_client.list_outbounds(
            {"status": "Pendente", "from_date": 1000},
            auth_token="token-123",
        )

        self.assertEqual(result, [])
        mock_get.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/outbound",
            params={"status": "Pendente", "from_date": 1000},
            headers={"Authorization": "Bearer token-123"},
            timeout=10,
        )

    @patch("services.xano_client.requests.get")
    def test_get_outbound(self, mock_get):
        mock_get.return_value = self._response({"id": 7, "status": "Pendente"})

        result = xano_client.get_outbound(7, auth_token="token-123")

        self.assertEqual(result["id"], 7)
        mock_get.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/outbound",
            params={"id": 7},
            headers={"Authorization": "Bearer token-123"},
            timeout=10,
        )

    @patch("services.xano_client.requests.patch")
    def test_reject_outbound(self, mock_patch):
        mock_patch.return_value = self._response({"id": 1, "status": "Rejeitada"})

        result = xano_client.update_outbound_status(
            1, "Rejeitada", auth_token="token-123"
        )

        self.assertEqual(result["status"], "Rejeitada")
        mock_patch.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/outbound/status",
            json={"id": 1, "status": "Rejeitada"},
            headers={"Authorization": "Bearer token-123"},
            timeout=10,
        )

    def test_update_status_cannot_conclude_without_process(self):
        with self.assertRaises(ValueError):
            xano_client.update_outbound_status(1, "Concluida")

    @patch("services.xano_client.requests.post")
    def test_process_outbound(self, mock_post):
        mock_post.return_value = self._response(
            {"outbound": {"id": 1, "status": "Concluida"}}
        )

        result = xano_client.process_outbound(1, auth_token="token-123")

        self.assertEqual(result["outbound"]["status"], "Concluida")
        mock_post.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/outbound/process",
            json={"id": 1},
            headers={"Authorization": "Bearer token-123"},
            timeout=10,
        )

    def test_process_outbound_requires_id(self):
        with self.assertRaises(ValueError):
            xano_client.process_outbound(0)


if __name__ == "__main__":
    unittest.main()
