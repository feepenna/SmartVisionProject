# tests/test_inventory_client.py
"""Testes unitários para as funções de inventário e conciliação do xano_client (Change 03).

Cobre validações de entrada, chamadas de API para inventários, contagens,
conciliação, divergências, decisões do gestor e aplicação de ajustes,
todas com requisições HTTP mockadas (sem depender do Xano real).
"""

import os
import unittest
from unittest.mock import MagicMock, patch

import requests

from services import xano_client


class TestInventoryClient(unittest.TestCase):

    def setUp(self):
        self.mock_base_url = "https://mock.xano.io/api"
        self.env_patcher = patch.dict(os.environ, {"XANO_BASE_URL": self.mock_base_url})
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    # ------------------------------------------------------------------ #
    # list_inventories / get_inventory
    # ------------------------------------------------------------------ #
    @patch("requests.get")
    def test_list_inventories_success(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "status": "Aberto", "scope": "completo", "opened_by": 1, "opened_at": "2026-10-15T10:00:00"}
        ]
        mock_get.return_value = mock_response

        result = xano_client.list_inventories()

        mock_get.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/inventories",
            params={},
            timeout=10,
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["status"], "Aberto")

    @patch("requests.get")
    def test_get_inventory_passes_id_param(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 3, "status": "EmContagem"}
        mock_get.return_value = mock_response

        result = xano_client.get_inventory(3)

        mock_get.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/inventory",
            params={"id": 3},
            timeout=10,
        )
        self.assertEqual(result["id"], 3)

    def test_get_inventory_missing_id(self):
        with self.assertRaises(ValueError) as ctx:
            xano_client.get_inventory(None)
        self.assertIn("inventory_id", str(ctx.exception))

    # ------------------------------------------------------------------ #
    # create_inventory
    # ------------------------------------------------------------------ #
    @patch("requests.post")
    def test_create_inventory_success(self, mock_post):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 7, "status": "Aberto", "scope": "completo", "opened_by": 1, "opened_at": "2026-10-15T10:00:00"
        }
        mock_post.return_value = mock_response

        payload = {"scope": "completo", "opened_by": 1, "notes": "Inventário mensal outubro"}
        result = xano_client.create_inventory(payload)

        mock_post.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/inventories",
            json=payload,
            timeout=10,
        )
        self.assertEqual(result["status"], "Aberto")
        self.assertEqual(result["id"], 7)

    def test_create_inventory_validation(self):
        with self.assertRaises(ValueError) as ctx:
            xano_client.create_inventory({"opened_by": 1})
        self.assertIn("escopo", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            xano_client.create_inventory({"scope": "completo"})
        self.assertIn("opened_by", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            xano_client.create_inventory({"scope": "completo", "opened_by": 1, "status": "Invalido"})
        self.assertIn("Status inválido", str(ctx.exception))

    # ------------------------------------------------------------------ #
    # transition_inventory_status
    # ------------------------------------------------------------------ #
    @patch("requests.patch")
    def test_transition_inventory_status_success(self, mock_patch):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "status": "EmContagem"}
        mock_patch.return_value = mock_response

        result = xano_client.transition_inventory_status(1, "EmContagem", 2)

        mock_patch.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/inventories/status",
            json={"id": 1, "status": "EmContagem", "user_id": 2},
            timeout=10,
        )
        self.assertEqual(result["status"], "EmContagem")

    def test_transition_inventory_status_validation(self):
        with self.assertRaises(ValueError):
            xano_client.transition_inventory_status(None, "EmContagem", 1)
        with self.assertRaises(ValueError):
            xano_client.transition_inventory_status(1, "Invalido", 1)
        with self.assertRaises(ValueError):
            xano_client.transition_inventory_status(1, "EmContagem", None)

    # ------------------------------------------------------------------ #
    # record_inventory_count / list_inventory_counts
    # ------------------------------------------------------------------ #
    @patch("requests.post")
    def test_record_inventory_count_success(self, mock_post):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 11, "inventory_id": 1, "product_id": 2, "quantity_counted": 8,
            "counted_by": 1, "is_recount": False,
        }
        mock_post.return_value = mock_response

        payload = {
            "inventory_id": 1, "product_id": 2, "quantity_counted": 8,
            "counted_by": 1, "is_recount": False,
        }
        result = xano_client.record_inventory_count(payload)

        mock_post.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/inventories/counts",
            json=payload,
            timeout=10,
        )
        self.assertEqual(result["quantity_counted"], 8)
        self.assertFalse(result["is_recount"])

    @patch("requests.post")
    def test_record_inventory_count_validation(self, mock_post):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 11, "inventory_id": 1, "product_id": 2, "quantity_counted": 5, "counted_by": 1}
        mock_post.return_value = mock_response
        # Entrada válida não deve lançar ValueError (prossegue para a API)
        xano_client.record_inventory_count({"inventory_id": 1, "product_id": 2, "quantity_counted": 5, "counted_by": 1})
        # Campos obrigatórios ausentes
        with self.assertRaises(ValueError) as ctx:
            xano_client.record_inventory_count({"product_id": 2, "quantity_counted": 5, "counted_by": 1})
        self.assertIn("inventory_id", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            xano_client.record_inventory_count({"inventory_id": 1, "product_id": 2, "quantity_counted": -1, "counted_by": 1})
        self.assertIn("maior ou igual a zero", str(ctx.exception))

    @patch("requests.get")
    def test_list_inventory_counts(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 11, "inventory_id": 1, "product_id": 2, "quantity_counted": 8}]
        mock_get.return_value = mock_response

        result = xano_client.list_inventory_counts(1)

        mock_get.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/inventories/counts",
            params={"inventory_id": "1"},
            timeout=10,
        )
        self.assertEqual(len(result), 1)

    # ------------------------------------------------------------------ #
    # reconcile_inventory
    # ------------------------------------------------------------------ #
    @patch("requests.post")
    def test_reconcile_inventory_success(self, mock_post):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"inventory_id": 1, "status": "AguardandoAprovacao"}
        mock_post.return_value = mock_response

        result = xano_client.reconcile_inventory(1, 2)

        mock_post.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/inventories/reconcile",
            json={"inventory_id": 1, "user_id": 2},
            timeout=10,
        )
        self.assertEqual(result["status"], "AguardandoAprovacao")

    def test_reconcile_inventory_validation(self):
        with self.assertRaises(ValueError):
            xano_client.reconcile_inventory(None, 1)
        with self.assertRaises(ValueError):
            xano_client.reconcile_inventory(1, None)

    # ------------------------------------------------------------------ #
    # list_discrepancies
    # ------------------------------------------------------------------ #
    @patch("requests.get")
    def test_list_discrepancies(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "inventory_id": 1, "product_id": 2, "divergence_type": "shortage", "status": "pending"}
        ]
        mock_get.return_value = mock_response

        result = xano_client.list_discrepancies(1, status="pending")

        mock_get.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/inventories/discrepancies",
            params={"inventory_id": "1", "status": "pending"},
            timeout=10,
        )
        self.assertEqual(result[0]["divergence_type"], "shortage")

    def test_list_discrepancies_validation(self):
        with self.assertRaises(ValueError):
            xano_client.list_discrepancies(None)

    # ------------------------------------------------------------------ #
    # decide_discrepancy
    # ------------------------------------------------------------------ #
    @patch("requests.post")
    def test_decide_discrepancy_approved(self, mock_post):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "status": "approved", "reviewed_by": 2}
        mock_post.return_value = mock_response

        payload = {
            "inventory_id": 1, "discrepancy_id": 1, "action": "approved",
            "decided_by": 2, "justification": "Conferido e confirmado.",
        }
        result = xano_client.decide_discrepancy(payload)

        mock_post.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/inventories/discrepancies/decision",
            json=payload,
            timeout=10,
        )
        self.assertEqual(result["status"], "approved")

    def test_decide_discrepancy_validation(self):
        with self.assertRaises(ValueError) as ctx:
            xano_client.decide_discrepancy({"inventory_id": 1, "discrepancy_id": 1, "action": "approved"})
        self.assertIn("decided_by", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            xano_client.decide_discrepancy({"inventory_id": 1, "discrepancy_id": 1, "action": "aprovar", "decided_by": 2})
        self.assertIn("Ação inválida", str(ctx.exception))

    # ------------------------------------------------------------------ #
    # apply_adjustments
    # ------------------------------------------------------------------ #
    @patch("requests.post")
    def test_apply_adjustments_success(self, mock_post):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "inventory_id": 1, "applied": 2, "skipped": 0,
            "message": "Ajustes aplicados com idempotência e tratamento de concorrência.",
        }
        mock_post.return_value = mock_response

        result = xano_client.apply_adjustments(1, 2)

        mock_post.assert_called_once_with(
            "https://mock.xano.io/api/smart_vision/inventories/apply-adjustments",
            json={"inventory_id": 1, "user_id": 2},
            timeout=10,
        )
        self.assertEqual(result["applied"], 2)
        self.assertEqual(result["skipped"], 0)

    def test_apply_adjustments_validation(self):
        with self.assertRaises(ValueError):
            xano_client.apply_adjustments(None, 1)
        with self.assertRaises(ValueError):
            xano_client.apply_adjustments(1, None)


if __name__ == "__main__":
    unittest.main()
