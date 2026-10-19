# tests/test_auth_service.py
"""Testes do serviço de autenticação (Change 06 — Login e Autenticação).

Cobre as mensagens obrigatórias da change, a classificação de erros
(credenciais inválidas × falha de comunicação), a proteção contra tentativas
repetidas e a orquestração ``autenticar()`` — sempre sem simular sucesso.
"""

import os
import unittest
from unittest.mock import patch

import requests

from services import auth_service
from services.auth_service import (
    MSG_BLOQUEIO_TEMPORARIO,
    MSG_CREDENCIAIS_INVALIDAS,
    MSG_FALHA_COMUNICACAO,
    MSG_SENHA_VAZIA,
    MSG_USUARIO_VAZIO,
    RateLimiter,
    autenticar,
    classificar_erro_login,
    validar_campos,
)


def _http_error(status: int, body: str = "") -> requests.HTTPError:
    """Constrói um requests.HTTPError com a mensagem gerada pelo _handle_response."""
    response = requests.Response()
    response.status_code = status
    response._content = body.encode("utf-8")
    return requests.HTTPError(
        f"Xano request failed: {status} Error\nResponse body: {body}"
    )


class TestValidarCampos(unittest.TestCase):
    """Mensagens obrigatórias para campos vazios."""

    def test_usuario_vazio(self):
        self.assertEqual(validar_campos("", "Senha123!"), MSG_USUARIO_VAZIO)

    def test_usuario_so_espacos(self):
        self.assertEqual(validar_campos("   ", "Senha123!"), MSG_USUARIO_VAZIO)

    def test_usuario_none(self):
        self.assertEqual(validar_campos(None, "Senha123!"), MSG_USUARIO_VAZIO)

    def test_senha_vazia(self):
        self.assertEqual(validar_campos("gerente@smartvision.com", ""), MSG_SENHA_VAZIA)

    def test_senha_none(self):
        self.assertEqual(validar_campos("gerente@smartvision.com", None), MSG_SENHA_VAZIA)

    def test_campos_validos_retorna_none(self):
        self.assertIsNone(validar_campos("gerente@smartvision.com", "Senha123!"))


class TestClassificarErroLogin(unittest.TestCase):
    """Credenciais rejeitadas × falha de comunicação — sem sucesso simulado."""

    def test_accessdenied_e_credenciais_invalidas(self):
        exc = _http_error(401, '{"error_type":"accessdenied","error":"Invalid Credentials."}')
        self.assertEqual(classificar_erro_login(exc), MSG_CREDENCIAIS_INVALIDAS)

    def test_status_401_e_credenciais_invalidas(self):
        exc = _http_error(401)
        self.assertEqual(classificar_erro_login(exc), MSG_CREDENCIAIS_INVALIDAS)

    def test_status_403_e_credenciais_invalidas(self):
        exc = _http_error(403)
        self.assertEqual(classificar_erro_login(exc), MSG_CREDENCIAIS_INVALIDAS)

    def test_500_e_falha_comunicacao(self):
        exc = _http_error(500, '{"code":"ERROR_FATAL","message":"Invalid api query"}')
        self.assertEqual(classificar_erro_login(exc), MSG_FALHA_COMUNICACAO)

    def test_timeout_e_falha_comunicacao(self):
        self.assertEqual(
            classificar_erro_login(requests.Timeout("timed out")), MSG_FALHA_COMUNICACAO
        )

    def test_connection_error_e_falha_comunicacao(self):
        self.assertEqual(
            classificar_erro_login(requests.ConnectionError("refused")),
            MSG_FALHA_COMUNICACAO,
        )

    def test_env_ausente_e_falha_comunicacao(self):
        self.assertEqual(
            classificar_erro_login(EnvironmentError("XANO_BASE_URL must be set")),
            MSG_FALHA_COMUNICACAO,
        )

    def test_excecao_generica_e_falha_comunicacao(self):
        self.assertEqual(classificar_erro_login(RuntimeError("boom")), MSG_FALHA_COMUNICACAO)


class TestRateLimiter(unittest.TestCase):
    """Proteção contra tentativas repetidas."""

    def setUp(self):
        self.relogio = [1_000_000.0]
        self.rl = RateLimiter(max_tentativas=5, janela_segundos=900, agora=lambda: self.relogio[0])

    def test_inicia_desbloqueado(self):
        self.assertEqual(self.rl.bloqueado(), (False, 0))

    def test_bloqueia_apos_max_tentativas(self):
        for _ in range(5):
            self.rl.registrar_falha()
        bloqueado, restante = self.rl.bloqueado()
        self.assertTrue(bloqueado)
        self.assertGreater(restante, 0)
        self.assertLessEqual(restante, 900)

    def test_nao_bloqueia_antes_do_max(self):
        for _ in range(4):
            self.rl.registrar_falha()
        self.assertEqual(self.rl.bloqueado(), (False, 0))

    def test_janela_expira_e_libera(self):
        for _ in range(5):
            self.rl.registrar_falha()
        self.relogio[0] += 901
        self.assertEqual(self.rl.bloqueado(), (False, 0))

    def test_sucesso_zera_contador(self):
        for _ in range(5):
            self.rl.registrar_falha()
        self.rl.registrar_sucesso()
        self.assertEqual(self.rl.bloqueado(), (False, 0))

    def test_nova_janela_apos_expiracao(self):
        for _ in range(5):
            self.rl.registrar_falha()
        self.relogio[0] += 901
        self.rl.registrar_falha()
        # Reiniciou a janela: 1 falha não bloqueia.
        self.assertEqual(self.rl.bloqueado(), (False, 0))


class TestAutenticar(unittest.TestCase):
    """Orquestração completa — backend real (mockado), nunca simulação local."""

    def setUp(self):
        self.rl = RateLimiter(max_tentativas=5, janela_segundos=900)
        self.env_patcher = patch.dict(
            os.environ, {"XANO_BASE_URL": "https://mock.xano.io/api"}
        )
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    def test_usuario_vazio_raises_mensagem_oficial(self):
        with self.assertRaises(ValueError) as ctx:
            autenticar("", "Senha123!", self.rl)
        self.assertEqual(str(ctx.exception), MSG_USUARIO_VAZIO)

    def test_senha_vazia_raises_mensagem_oficial(self):
        with self.assertRaises(ValueError) as ctx:
            autenticar("gerente@smartvision.com", "", self.rl)
        self.assertEqual(str(ctx.exception), MSG_SENHA_VAZIA)

    @patch("services.auth_service.xano_client.get_me")
    @patch("services.auth_service.xano_client.login")
    def test_login_valido_retorna_token_e_usuario(self, mock_login, mock_me):
        mock_login.return_value = {"authToken": "tok-123", "user_id": 7}
        mock_me.return_value = {"id": 7, "name": "Gerente Demo", "role": "Gestor"}
        token, user = autenticar("  Gerente@SmartVision.com ", "Senha123!", self.rl)
        self.assertEqual(token, "tok-123")
        self.assertEqual(user["role"], "Gestor")
        # Usuário é normalizado (trim) antes de ir ao backend.
        mock_login.assert_called_once_with("Gerente@SmartVision.com", "Senha123!")
        # Senha nunca passa pelo retorno.
        self.assertNotIn("Senha123!", str(user))

    @patch("services.auth_service.xano_client.login")
    def test_credenciais_invalidas_raises_e_conta_tentativa(self, mock_login):
        mock_login.side_effect = _http_error(401, '{"error_type":"accessdenied"}')
        with self.assertRaises(ValueError) as ctx:
            autenticar("gerente@smartvision.com", "Errada123!", self.rl)
        self.assertEqual(str(ctx.exception), MSG_CREDENCIAIS_INVALIDAS)
        bloqueado, _ = self.rl.bloqueado()
        self.assertFalse(bloqueado)  # 1 de 5

    @patch("services.auth_service.xano_client.login")
    def test_falha_comunicacao_nao_conta_tentativa(self, mock_login):
        mock_login.side_effect = requests.ConnectionError("offline")
        with self.assertRaises(Exception) as ctx:
            autenticar("gerente@smartvision.com", "Senha123!", self.rl)
        self.assertNotIsInstance(ctx.exception, ValueError)
        self.assertEqual(str(ctx.exception), MSG_FALHA_COMUNICACAO)
        # Falha de comunicação não é culpa do usuário: não conta no rate limit.
        for _ in range(4):
            with self.assertRaises(Exception):
                autenticar("gerente@smartvision.com", "Senha123!", self.rl)
        self.assertEqual(self.rl.bloqueado(), (False, 0))

    @patch("services.auth_service.xano_client.login")
    def test_bloqueio_temporario_nao_chama_backend(self, mock_login):
        for _ in range(5):
            mock_login.side_effect = _http_error(401, '{"error_type":"accessdenied"}')
            with self.assertRaises(ValueError):
                autenticar("gerente@smartvision.com", "Errada123!", self.rl)
        mock_login.reset_mock()
        mock_login.side_effect = None
        with self.assertRaises(RuntimeError) as ctx:
            autenticar("gerente@smartvision.com", "Senha123!", self.rl)
        self.assertEqual(str(ctx.exception), MSG_BLOQUEIO_TEMPORARIO)
        mock_login.assert_not_called()

    @patch("services.auth_service.xano_client.get_me")
    @patch("services.auth_service.xano_client.login")
    def test_sem_auth_token_e_falha_comunicacao(self, mock_login, mock_me):
        mock_login.return_value = {}
        with self.assertRaises(Exception) as ctx:
            autenticar("gerente@smartvision.com", "Senha123!", self.rl)
        self.assertEqual(str(ctx.exception), MSG_FALHA_COMUNICACAO)
        mock_me.assert_not_called()

    @patch("services.auth_service.xano_client.get_me")
    @patch("services.auth_service.xano_client.login")
    def test_falha_no_auth_me_nao_assume_sucesso(self, mock_login, mock_me):
        """Sem sessão confirmada pelo backend, não há login (sem bypass)."""
        mock_login.return_value = {"authToken": "tok-123", "user_id": 7}
        mock_me.side_effect = requests.ConnectionError("offline")
        with self.assertRaises(Exception) as ctx:
            autenticar("gerente@smartvision.com", "Senha123!", self.rl)
        self.assertEqual(str(ctx.exception), MSG_FALHA_COMUNICACAO)

    @patch("services.auth_service.xano_client.get_me")
    @patch("services.auth_service.xano_client.login")
    def test_sucesso_zera_rate_limiter(self, mock_login, mock_me):
        mock_login.return_value = {"authToken": "tok", "user_id": 1}
        mock_me.return_value = {"id": 1, "role": "Vendedor"}
        for _ in range(4):
            mock_login.side_effect = _http_error(401, '{"error_type":"accessdenied"}')
            with self.assertRaises(ValueError):
                autenticar("vendedor@smartvision.com", "Errada123!", self.rl)
        mock_login.side_effect = None
        mock_login.return_value = {"authToken": "tok", "user_id": 1}
        autenticar("vendedor@smartvision.com", "Senha123!", self.rl)
        self.assertEqual(self.rl.bloqueado(), (False, 0))


if __name__ == "__main__":
    unittest.main()
