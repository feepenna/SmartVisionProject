# tests/test_auth_client.py
"""Testes do cliente de autenticação no xano_client (Change 06).

Valida endpoints, payloads, headers de sessão (Bearer) e validação de entrada
das funções ``login`` e ``get_me`` — com o backend sempre mockado.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

import requests

from services import xano_client


class TestAuthEndpoints(unittest.TestCase):

    def setUp(self):
        self.env_patcher = patch.dict(
            os.environ, {"XANO_BASE_URL": "https://mock.xano.io/api"}
        )
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    def test_login_endpoint_na_raiz(self):
        """Grupo Authentication é servido na raiz do base URL (não smart_vision/)."""
        self.assertEqual(
            xano_client._get_auth_login_endpoint(),
            "https://mock.xano.io/api/auth/login",
        )

    def test_me_endpoint_na_raiz(self):
        self.assertEqual(
            xano_client._get_auth_me_endpoint(),
            "https://mock.xano.io/api/auth/me",
        )

    def test_endpoints_sem_barra_final(self):
        with patch.dict(os.environ, {"XANO_BASE_URL": "https://mock.xano.io/api/"}):
            self.assertEqual(
                xano_client._get_auth_login_endpoint(),
                "https://mock.xano.io/api/auth/login",
            )


class TestLoginFunction(unittest.TestCase):

    def setUp(self):
        self.env_patcher = patch.dict(
            os.environ, {"XANO_BASE_URL": "https://mock.xano.io/api"}
        )
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    def test_usuario_vazio_raises(self):
        with self.assertRaises(ValueError) as ctx:
            xano_client.login("   ", "Senha123!")
        self.assertIn("Informe seu usuário.", str(ctx.exception))

    def test_senha_vazia_raises(self):
        with self.assertRaises(ValueError) as ctx:
            xano_client.login("user@x.com", "")
        self.assertIn("Informe sua senha.", str(ctx.exception))

    @patch("requests.post")
    def test_login_envia_payload_normalizado(self, mock_post):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"authToken": "tok-abc", "user_id": 7}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = xano_client.login("  USER@SmartVision.COM ", "Senha123!")

        self.assertEqual(result["authToken"], "tok-abc")
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://mock.xano.io/api/auth/login")
        # E-mail normalizado para trim + lower; senha em claro apenas no payload.
        self.assertEqual(
            kwargs["json"],
            {"email": "user@smartvision.com", "password": "Senha123!"},
        )
        self.assertEqual(kwargs["timeout"], 10)

    @patch("requests.post")
    def test_login_401_propaga_http_error(self, mock_post):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.HTTPError("401 Client Error")
        mock_response.text = '{"error_type":"accessdenied"}'
        mock_post.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            xano_client.login("user@x.com", "Errada123!")

    def test_login_sem_base_url_raises_environment_error(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(EnvironmentError):
                xano_client.login("user@x.com", "Senha123!")


class TestGetMeFunction(unittest.TestCase):

    def setUp(self):
        self.env_patcher = patch.dict(
            os.environ, {"XANO_BASE_URL": "https://mock.xano.io/api"}
        )
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    @patch("requests.get")
    def test_get_me_envia_bearer_token(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 7, "role": "Gestor"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = xano_client.get_me("tok-abc")

        self.assertEqual(result["role"], "Gestor")
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://mock.xano.io/api/auth/me")
        self.assertEqual(kwargs["headers"], {"Authorization": "Bearer tok-abc"})
        self.assertEqual(kwargs["timeout"], 10)

    @patch("requests.get")
    def test_get_me_token_invalido_propaga_erro(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.HTTPError("401 Client Error")
        mock_response.text = '{"message":"invalid token"}'
        mock_get.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            xano_client.get_me("token-invalido")


if __name__ == "__main__":
    unittest.main()
