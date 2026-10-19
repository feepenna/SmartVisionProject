# tests/test_alerts_client.py
"""Testes do cliente Python para alertas e reposição (Change 05).

Validam, com ``unittest.mock``, que ``services.xano_client`` monta as requisições
corretas (URL, método, parâmetros) e faz a validação de entrada local antes de
chamar o backend. Não há rede real: as respostas são simuladas.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

import requests

from services import xano_client


class TestAlertsClient(unittest.TestCase):
    def setUp(self):
        self.mock_base_url = "https://mock.xano.io/api"
        self.env_patcher = patch.dict(os.environ, {"XANO_BASE_URL": self.mock_base_url})
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    # ------------------------------------------------------------------ #
    # list_alerts
    # ------------------------------------------------------------------ #
    @patch("requests.get")
    def test_list_alerts_sem_filtros(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "status": "Ativo"}]
        mock_get.return_value = mock_response

        res = xano_client.list_alerts(1)

        self.assertEqual(res[0]["status"], "Ativo")
        called_url = mock_get.call_args[0][0]
        self.assertIn("/smart_vision/alerts", called_url)
        self.assertNotIn("alerts/evaluate", called_url)
        params = mock_get.call_args[1]["params"]
        self.assertEqual(params["user_id"], "1")
        self.assertNotIn("status", params)
        self.assertNotIn("alert_type", params)

    @patch("requests.get")
    def test_list_alerts_com_filtros(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        xano_client.list_alerts(3, status="EmAcompanhamento", alert_type="LOW_STOCK", product_id=7)

        params = mock_get.call_args[1]["params"]
        self.assertEqual(params["user_id"], "3")
        self.assertEqual(params["status"], "EmAcompanhamento")
        self.assertEqual(params["alert_type"], "LOW_STOCK")
        self.assertEqual(params["product_id"], "7")

    def test_list_alerts_user_id_obrigatorio(self):
        with self.assertRaises(ValueError):
            xano_client.list_alerts(0)

    def test_list_alerts_status_invalido(self):
        with self.assertRaises(ValueError):
            xano_client.list_alerts(1, status="Inexistente")

    def test_list_alerts_tipo_invalido(self):
        with self.assertRaises(ValueError):
            xano_client.list_alerts(1, alert_type="OUTRO")

    # ------------------------------------------------------------------ #
    # get_alerts_summary
    # ------------------------------------------------------------------ #
    @patch("requests.get")
    def test_get_alerts_summary(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"alertas_ativos": 4, "actor_role": "Gestor"}
        mock_get.return_value = mock_response

        res = xano_client.get_alerts_summary(1)

        self.assertEqual(res["alertas_ativos"], 4)
        self.assertIn("/smart_vision/alerts/summary", mock_get.call_args[0][0])

    def test_get_alerts_summary_user_id_obrigatorio(self):
        with self.assertRaises(ValueError):
            xano_client.get_alerts_summary(0)

    # ------------------------------------------------------------------ #
    # list_inactive_products
    # ------------------------------------------------------------------ #
    @patch("requests.get")
    def test_list_inactive_products_default(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        xano_client.list_inactive_products(1)

        self.assertIn("/smart_vision/alerts/inactive", mock_get.call_args[0][0])
        params = mock_get.call_args[1]["params"]
        self.assertEqual(params["incluir_sem_historico"], "1")
        self.assertNotIn("inactivity_days", params)

    @patch("requests.get")
    def test_list_inactive_products_janela_e_sem_historico(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        xano_client.list_inactive_products(1, inactivity_days=15, incluir_sem_historico=False)

        params = mock_get.call_args[1]["params"]
        self.assertEqual(params["inactivity_days"], "15")
        self.assertEqual(params["incluir_sem_historico"], "0")

    def test_list_inactive_products_janela_invalida(self):
        with self.assertRaises(ValueError):
            xano_client.list_inactive_products(1, inactivity_days=0)

    # ------------------------------------------------------------------ #
    # evaluate_alerts
    # ------------------------------------------------------------------ #
    @patch("requests.post")
    def test_evaluate_alerts(self, mock_post):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"avaliados": 5, "criados": 2, "resolvidos": 1}
        mock_post.return_value = mock_response

        res = xano_client.evaluate_alerts(1)

        self.assertEqual(res["criados"], 2)
        self.assertIn("/smart_vision/alerts/evaluate", mock_post.call_args[0][0])
        self.assertEqual(mock_post.call_args[1]["json"]["user_id"], 1)

    def test_evaluate_alerts_user_id_obrigatorio(self):
        with self.assertRaises(ValueError):
            xano_client.evaluate_alerts(0)

    # ------------------------------------------------------------------ #
    # update_alert_status
    # ------------------------------------------------------------------ #
    @patch("requests.post")
    def test_update_alert_status_resolver(self, mock_post):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "status": "Resolvido"}
        mock_post.return_value = mock_response

        res = xano_client.update_alert_status(1, "Resolvido", 2, notes="Reposto")

        self.assertEqual(res["status"], "Resolvido")
        self.assertIn("/smart_vision/alerts/status", mock_post.call_args[0][0])
        payload = mock_post.call_args[1]["json"]
        self.assertEqual(payload["alert_id"], 1)
        self.assertEqual(payload["status"], "Resolvido")
        self.assertEqual(payload["user_id"], 2)
        self.assertEqual(payload["notes"], "Reposto")

    def test_update_alert_status_status_invalido(self):
        with self.assertRaises(ValueError):
            xano_client.update_alert_status(1, "EmAberto", 2)

    def test_update_alert_status_alert_id_obrigatorio(self):
        with self.assertRaises(ValueError):
            xano_client.update_alert_status(0, "Resolvido", 2)

    def test_update_alert_status_user_id_obrigatorio(self):
        with self.assertRaises(ValueError):
            xano_client.update_alert_status(1, "Resolvido", 0)

    def test_update_alert_status_notas_vazias(self):
        with self.assertRaises(ValueError):
            xano_client.update_alert_status(1, "Resolvido", 2, notes="   ")

    # ------------------------------------------------------------------ #
    # list_replenishment
    # ------------------------------------------------------------------ #
    @patch("requests.get")
    def test_list_replenishment(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"product_id": 1, "sugestao": 13, "parametros_incompletos": False}
        ]
        mock_get.return_value = mock_response

        res = xano_client.list_replenishment(1, category="Armação", product_id=1)

        self.assertEqual(res[0]["sugestao"], 13)
        self.assertIn("/smart_vision/replenishment", mock_get.call_args[0][0])
        params = mock_get.call_args[1]["params"]
        self.assertEqual(params["category"], "Armação")
        self.assertEqual(params["product_id"], "1")

    def test_list_replenishment_user_id_obrigatorio(self):
        with self.assertRaises(ValueError):
            xano_client.list_replenishment(0)

    # ------------------------------------------------------------------ #
    # update_stock_parameters
    # ------------------------------------------------------------------ #
    @patch("requests.patch")
    def test_update_stock_parameters(self, mock_patch):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "min_stock": 5, "target_stock": 20}
        mock_patch.return_value = mock_response

        res = xano_client.update_stock_parameters(
            1, 2, min_stock=5, target_stock=20, inactivity_days=45, alerts_enabled=True
        )

        self.assertEqual(res["target_stock"], 20)
        self.assertIn("/smart_vision/stock-parameters", mock_patch.call_args[0][0])
        payload = mock_patch.call_args[1]["json"]
        self.assertEqual(payload["product_id"], 1)
        self.assertEqual(payload["user_id"], 2)
        self.assertEqual(payload["min_stock"], 5)
        self.assertEqual(payload["target_stock"], 20)
        self.assertEqual(payload["inactivity_days"], 45)
        # Booleanos são convertidos para 1/0 (input do Xano não aceita bool)
        self.assertEqual(payload["alerts_enabled"], 1)

    @patch("requests.patch")
    def test_update_stock_parameters_apenas_campos_enviados(self, mock_patch):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1}
        mock_patch.return_value = mock_response

        xano_client.update_stock_parameters(1, 2, alerts_enabled=False)

        payload = mock_patch.call_args[1]["json"]
        self.assertNotIn("min_stock", payload)
        self.assertNotIn("target_stock", payload)
        self.assertNotIn("inactivity_days", payload)
        self.assertEqual(payload["alerts_enabled"], 0)

    def test_update_stock_parameters_alvo_menor_que_minimo(self):
        with self.assertRaises(ValueError):
            xano_client.update_stock_parameters(1, 2, min_stock=10, target_stock=5)

    def test_update_stock_parameters_negativos(self):
        with self.assertRaises(ValueError):
            xano_client.update_stock_parameters(1, 2, min_stock=-1)
        with self.assertRaises(ValueError):
            xano_client.update_stock_parameters(1, 2, target_stock=-1)

    def test_update_stock_parameters_janela_invalida(self):
        with self.assertRaises(ValueError):
            xano_client.update_stock_parameters(1, 2, inactivity_days=0)

    def test_update_stock_parameters_alerts_enabled_tipo_invalido(self):
        with self.assertRaises(ValueError):
            xano_client.update_stock_parameters(1, 2, alerts_enabled="sim")

    def test_update_stock_parameters_identificadores_obrigatorios(self):
        with self.assertRaises(ValueError):
            xano_client.update_stock_parameters(0, 2)
        with self.assertRaises(ValueError):
            xano_client.update_stock_parameters(1, 0)


if __name__ == "__main__":
    unittest.main()
