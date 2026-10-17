# tests/test_outbound_client.py
import os
import unittest
from unittest.mock import MagicMock, patch
import requests
from services import xano_client


class TestOutboundClient(unittest.TestCase):
    def setUp(self):
        self.mock_base_url = "https://mock.xano.io/api"
        self.env_patcher = patch.dict(os.environ, {"XANO_BASE_URL": self.mock_base_url})
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    @patch("requests.post")
    def test_create_outbound_sale(self, mock_post):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "type": "SALE", "status": "Pendente"}
        mock_post.return_value = mock_response
        payload = {"type": "SALE", "product_id": 1, "quantity": 2, "user_id": 1, "reason": "Venda"}
        res = xano_client.create_outbound(payload)
        self.assertEqual(res["type"], "SALE")

    def test_create_outbound_loss_requires_justification(self):
        with self.assertRaises(ValueError):
            xano_client.create_outbound({"type": "LOSS", "product_id": 1, "quantity": 1, "user_id": 1, "reason": "Perda"})

    @patch("requests.get")
    def test_list_outbounds(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        res = xano_client.list_outbounds()
        self.assertEqual(res, [])

    @patch("requests.patch")
    def test_update_status(self, mock_patch):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "status": "Concluida"}
        mock_patch.return_value = mock_response
        res = xano_client.update_outbound_status(1, "Concluida", 2)
        self.assertEqual(res["status"], "Concluida")

    @patch("requests.post")
    def test_process_outbound(self, mock_post):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"outbound": {"id": 1, "status": "Concluida"}}
        mock_post.return_value = mock_response
        res = xano_client.process_outbound(1, 1)
        self.assertEqual(res["outbound"]["status"], "Concluida")
