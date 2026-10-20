# services/auth_service.py
"""Autenticação (Change 06: Login e Autenticação) — Smart Vision.

Centraliza em um único lugar testável:

- Validação de campos obrigatórios (mensagens oficiais da change).
- Classificação de falhas de login (credenciais inválidas × falha de
  comunicação), sempre a partir da resposta real do backend.
- Proteção contra tentativas repetidas (rate limiting por sessão).
- Orquestração ``autenticar()``: valida → verifica rate limit → chama o
  backend Xano → classifica erros → retorna token + dados do usuário.

Regras de segurança (AGENTS.md §2.1 e §3.3):

- A senha nunca é armazenada, registrada ou devolvida por esta camada.
- Nenhuma autenticação é simulada: sem backend acessível, o erro classificado
  é ``MSG_FALHA_COMUNICACAO`` (a mensagem obrigatória da change), nunca
  sucesso.
- A classificação usa somente o que o backend retornou — não há bypass local.
"""

import time
from typing import Optional, Tuple

import requests

from services import xano_client

# ---------------------------------------------------------------------------
# Mensagens oficiais da Change 06
# ---------------------------------------------------------------------------
MSG_USUARIO_VAZIO = "Informe seu usuário."
MSG_SENHA_VAZIA = "Informe sua senha."
MSG_CREDENCIAIS_INVALIDAS = (
    "Usuário ou senha inválidos. Verifique suas credenciais e tente novamente."
)
MSG_FALHA_COMUNICACAO = "Não foi possível realizar o login agora. Tente novamente."

# Mensagem adicional da proteção contra tentativas repetidas.
MSG_BLOQUEIO_TEMPORARIO = (
    "Muitas tentativas de acesso. Aguarde alguns minutos e tente novamente."
)

# Padrões no corpo/status do erro que indicam credenciais rejeitadas pelo backend.
_CREDENCIAIS_INVALIDAS_MARKERS = (
    "accessdenied",
    "access_denied",
    "invalid credentials",
    "401",
    "403",
)

# Marcador do bloqueio por tentativas repetidas imposto pelo backend
# (throw {name = "ratelimit"} em auth/login_POST.xs). Verificado ANTES dos
# marcadores de credenciais para não mascarar o lockout como "credencial
# inválida".
_LOCKOUT_MARKERS = (
    "muitas tentativas",
    "ratelimit",
    "rate limit",
    "too many",
)


def validar_campos(usuario: Optional[str], senha: Optional[str]) -> Optional[str]:
    """Valida os campos obrigatórios do formulário de login.

    Returns:
        A mensagem de erro obrigatória da change, ou ``None`` se válido.
    """
    if not usuario or not str(usuario).strip():
        return MSG_USUARIO_VAZIO
    if not senha or not str(senha):
        return MSG_SENHA_VAZIA
    return None


def classificar_erro_login(exc: Exception) -> str:
    """Classifica uma exceção de login na mensagem obrigatória correspondente.

    - Bloqueio por tentativas repetidas imposto pelo backend →
      ``MSG_BLOQUEIO_TEMPORARIO``.
    - Rejeição explícita de credenciais pelo backend (401/403/accessdenied/
      "Invalid Credentials") → ``MSG_CREDENCIAIS_INVALIDAS``.
    - Qualquer outra falha (rede, timeout, backend indisponível, 5xx,
      configuração ausente) → ``MSG_FALHA_COMUNICACAO``.
    """
    if isinstance(exc, requests.HTTPError):
        msg = str(exc).lower()
        if any(marker in msg for marker in _LOCKOUT_MARKERS):
            return MSG_BLOQUEIO_TEMPORARIO
        if any(marker in msg for marker in _CREDENCIAIS_INVALIDAS_MARKERS):
            return MSG_CREDENCIAIS_INVALIDAS
    return MSG_FALHA_COMUNICACAO


class RateLimiter:
    """Proteção contra tentativas repetidas de login (por sessão).

    Após ``max_tentativas`` falhas de credenciais dentro da janela de
    ``janela_segundos``, novas tentativas são bloqueadas temporariamente.
    Falhas de comunicação **não** contam como tentativa (não é culpa do
    usuário). Um login bem-sucedido zera o contador.

    Args:
        max_tentativas: Falhas de credenciais permitidas na janela.
        janela_segundos: Duração da janela de contagem em segundos.
        agora: Injetável para testes (``time.time`` por padrão).
    """

    def __init__(
        self,
        max_tentativas: int = 5,
        janela_segundos: int = 900,
        agora=time.time,
    ):
        self.max_tentativas = max_tentativas
        self.janela_segundos = janela_segundos
        self._agora = agora
        self._falhas = 0
        self._janela_inicio: Optional[float] = None

    def bloqueado(self) -> Tuple[bool, int]:
        """Verifica se o acesso está temporariamente bloqueado.

        Returns:
            Tupla ``(bloqueado, segundos_restantes)``.
        """
        if self._janela_inicio is None or self._falhas < self.max_tentativas:
            return False, 0
        decorrido = self._agora() - self._janela_inicio
        restante = int(self.janela_segundos - decorrido)
        if restante <= 0:
            # Janela expirou: libera e reinicia a contagem.
            self._falhas = 0
            self._janela_inicio = None
            return False, 0
        return True, restante

    def registrar_falha(self) -> None:
        """Registra uma rejeição de credenciais (não falhas de comunicação)."""
        agora = self._agora()
        if self._janela_inicio is None or agora - self._janela_inicio >= self.janela_segundos:
            self._janela_inicio = agora
            self._falhas = 0
        self._falhas += 1

    def registrar_sucesso(self) -> None:
        """Zera o contador após autenticação bem-sucedida."""
        self._falhas = 0
        self._janela_inicio = None


def autenticar(usuario: str, senha: str, rate_limiter: RateLimiter):
    """Autentica no backend Xano com validação, rate limit e classificação.

    Args:
        usuario: Usuário digitado (e-mail/login).
        senha: Senha digitada (texto plano — jamais persistida).
        rate_limiter: Instância de proteção contra tentativas repetidas.

    Returns:
        Tupla ``(auth_token, user_data)`` — dados vêm exclusivamente do
        backend via ``auth/me`` (perfil incluso).

    Raises:
        ValueError: Campo vazio ou credenciais inválidas (mensagem oficial).
        RuntimeError: Tentativas repetidas bloqueadas temporariamente.
        Exception: Qualquer outra falha — o chamador deve exibir
            ``MSG_FALHA_COMUNICACAO``.
    """
    erro_campo = validar_campos(usuario, senha)
    if erro_campo:
        raise ValueError(erro_campo)

    bloqueado, restante = rate_limiter.bloqueado()
    if bloqueado:
        raise RuntimeError(MSG_BLOQUEIO_TEMPORARIO)

    try:
        auth_result = xano_client.login(str(usuario).strip(), senha)
    except Exception as exc:
        mensagem = classificar_erro_login(exc)
        if mensagem == MSG_CREDENCIAIS_INVALIDAS:
            rate_limiter.registrar_falha()
            raise ValueError(mensagem) from exc
        if mensagem == MSG_BLOQUEIO_TEMPORARIO:
            # O backend já está impondo o bloqueio: não duplica a punição
            # no contador local (a validação real é sempre server-side).
            raise RuntimeError(mensagem) from exc
        raise Exception(mensagem) from exc

    auth_token = auth_result.get("authToken")
    if not auth_token:
        raise Exception(MSG_FALHA_COMUNICACAO)

    try:
        user_data = xano_client.get_me(auth_token)
    except Exception as exc:
        # O login foi aceito mas não conseguimos confirmar a sessão:
        # falha de comunicação, sem assumir sucesso (sem bypass).
        raise Exception(MSG_FALHA_COMUNICACAO) from exc

    rate_limiter.registrar_sucesso()
    return auth_token, user_data
