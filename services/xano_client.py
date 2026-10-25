# services/xano_client.py
"""Xano client service.

Provides helper functions to interact with the Xano backend for the product catalog.

Environment Variables:
- ``XANO_BASE_URL``: Base URL of the Xano API (e.g. ``https://example.xano.io/api``).

The functions raise ``requests.HTTPError`` for non-2xx responses so that callers can handle errors
appropriately.
"""

import os
from typing import Any, Dict, List, Optional

import requests


def get_base_url() -> str:
    """Retrieve base URL from environment or st.secrets; raise a clear error if not set."""
    base_url = os.getenv("XANO_BASE_URL")
    if not base_url:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "XANO_BASE_URL" in st.secrets:
                base_url = str(st.secrets["XANO_BASE_URL"])
        except Exception:
            pass
    if not base_url:
        raise EnvironmentError(
            "Environment variable XANO_BASE_URL must be set to the Xano API base URL."
        )
    return base_url.rstrip("/")


def _format_endpoint(path: str) -> str:
    """Resolve endpoint URL supporting both standard and canonical group paths."""
    base = get_base_url()
    clean_path = path.lstrip("/")
    if ":SzoTJegm" in base or ":smart_vision" in base or base.endswith("/smart_vision"):
        return f"{base}/{clean_path}"
    return f"{base}/smart_vision/{clean_path}"


def _auth_headers(auth_token: Optional[str]) -> Dict[str, str]:
    """Montar o header de autenticação quando um token estiver disponível."""
    if not auth_token:
        return {}
    return {"Authorization": f"Bearer {auth_token}"}


def _get_products_endpoint() -> str:
    return _format_endpoint("products")


def _get_stock_entry_endpoint() -> str:
    return _format_endpoint("stock_entry")


def _get_stock_exit_endpoint() -> str:
    return _format_endpoint("stock_exit")


def _get_inventories_endpoint() -> str:
    return _format_endpoint("inventories")


def _get_inventory_endpoint() -> str:
    return _format_endpoint("inventory")


def _get_inventory_status_endpoint() -> str:
    return _format_endpoint("inventories/status")


def _get_inventory_counts_endpoint() -> str:
    return _format_endpoint("inventories/counts")


def _get_inventory_reconcile_endpoint() -> str:
    return _format_endpoint("inventories/reconcile")


def _get_inventory_discrepancies_endpoint() -> str:
    return _format_endpoint("inventories/discrepancies")


def _get_inventory_discrepancy_decision_endpoint() -> str:
    return _format_endpoint("inventories/discrepancies/decision")


def _get_inventory_apply_adjustments_endpoint() -> str:
    return _format_endpoint("inventories/apply-adjustments")


def _handle_response(response: requests.Response) -> Any:
    """Internal helper to raise for HTTP errors and return JSON payload."""
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        # Attach response content for easier debugging.
        raise requests.HTTPError(f"Xano request failed: {exc}\nResponse body: {response.text}") from exc
    # Xano typically returns JSON.
    return response.json()


def list_products(
    filters: Optional[Dict[str, str]] = None,
    auth_token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve a list of products.

    Args:
        filters: Optional dictionary with query parameters (e.g. ``{"category": "lens"}``).
        auth_token: Token Bearer do usuário autenticado (obrigatório no backend).

    Returns:
        A list of product dictionaries as returned by Xano.
    """
    params = filters or {}
    response = requests.get(
        _get_products_endpoint(),
        params=params,
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def create_product(
    payload: Dict[str, Any],
    auth_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new product in Xano.

    Args:
        payload: Dictionary matching the fields defined in the Xano ``product`` table.
        auth_token: Token Bearer do usuário autenticado (obrigatório no backend).

    Returns:
        The created product record as returned by Xano.
    """
    response = requests.post(
        _get_products_endpoint(),
        json=payload,
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def record_stock_entry(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Record a stock entry (addition) with mandatory audit log in Xano.

    Args:
        payload: Dictionary containing ``product_id``, ``quantity``, ``reason``,
                 ``unit_cost``, and optional ``supplier_id``, ``invoice``, ``batch_id``, ``user_id``.

    Returns:
        Dictionary containing ``audit`` and ``product`` records.
    """
    if not payload.get("product_id"):
        raise ValueError("product_id é obrigatório.")
    quantity = payload.get("quantity")
    if quantity is None or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("A quantidade de entrada deve ser um número inteiro maior que zero.")
    reason = payload.get("reason")
    if not reason or not str(reason).strip():
        raise ValueError("O motivo da movimentação é obrigatório.")
    # Validate unit_cost
    unit_cost = payload.get("unit_cost")
    if unit_cost is None:
        raise ValueError("O campo unit_cost é obrigatório.")
    if not isinstance(unit_cost, (int, float)) or unit_cost < 0:
        raise ValueError("O unit_cost deve ser um número maior ou igual a zero.")

    response = requests.post(_get_stock_entry_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


def record_stock_exit(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Record a stock exit (subtraction) with mandatory audit log and negative stock validation in Xano.

    Args:
        payload: Dictionary containing ``product_id``, ``quantity``, ``reason``,
                 ``justification`` (required for LOSS/DAMAGE), and optional ``reference_text``,
                 ``user_id``.

    Returns:
        Dictionary containing ``audit`` and ``product`` records.
    """
    if not payload.get("product_id"):
        raise ValueError("product_id é obrigatório.")
    quantity = payload.get("quantity")
    if quantity is None or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("A quantidade de saída deve ser um número inteiro maior que zero.")
    reason = payload.get("reason")
    if not reason or not str(reason).strip():
        raise ValueError("O motivo da movimentação é obrigatório.")
    # Validate justification for LOSS or DAMAGE
    if reason in ["LOSS", "DAMAGE"]:
        justification = payload.get("justification")
        if not justification or not str(justification).strip():
            raise ValueError("A justificativa é obrigatória quando o motivo é LOSS ou DAMAGE.")

    response = requests.post(_get_stock_exit_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


# ---------------------------------------------------------------------------
# Inventário físico e conciliação (Change 03)
# ---------------------------------------------------------------------------

_VALID_INVENTORY_STATUSES = ["Aberto", "EmContagem", "AguardandoAprovacao", "Concluido"]
_VALID_INVENTORY_SCOPES = ["completo", "categoria", "localizacao"]
_VALID_DISCREPANCY_ACTIONS = ["approved", "rejected", "recount_requested"]


def list_inventories(
    filters: Optional[Dict[str, str]] = None,
    auth_token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Listar inventários físicos.

    Args:
        filters: Filtros opcionais (ex: ``{"status": "Aberto", "opened_by": "1"}``).
        auth_token: Token Bearer do usuário autenticado (obrigatório no backend).

    Returns:
        Lista de inventários conforme retornado pelo Xano.
    """
    params = filters or {}
    response = requests.get(
        _get_inventories_endpoint(),
        params=params,
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def get_inventory(
    inventory_id: int,
    auth_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Consultar detalhes de um inventário, incluindo progresso da contagem.

    Args:
        inventory_id: ID do inventário.
        auth_token: Token Bearer do usuário autenticado (obrigatório no backend).

    Returns:
        Detalhe do inventário com progresso de contagem.
    """
    if not inventory_id:
        raise ValueError("inventory_id é obrigatório.")
    response = requests.get(
        _get_inventory_endpoint(),
        params={"id": int(inventory_id)},
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def create_inventory(
    payload: Dict[str, Any],
    auth_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Criar um novo inventário físico com status ``Aberto``.

    Args:
        payload: Dicionário com ``scope``, ``opened_by`` e opcionais
        ``status``, ``category_filter``, ``location_filter``, ``notes``.
        auth_token: Token Bearer do usuário autenticado (obrigatório no backend).

    Returns:
        Registro do inventário criado.
    """
    scope = payload.get("scope")
    if not scope or not str(scope).strip():
        raise ValueError("O escopo do inventário é obrigatório.")
    if scope not in _VALID_INVENTORY_SCOPES:
        raise ValueError("Escopo inválido. Use: " + ", ".join(_VALID_INVENTORY_SCOPES) + ".")
    if not payload.get("opened_by"):
        raise ValueError("O responsável pela abertura (opened_by) é obrigatório.")
    status = payload.get("status", "Aberto")
    if status != "Aberto":
        raise ValueError("O inventário deve ser criado com status Aberto.")
    if scope == "categoria" and not str(payload.get("category_filter") or "").strip():
        raise ValueError("Informe a categoria (category_filter) quando o escopo for categoria.")
    if scope == "localizacao" and not str(payload.get("location_filter") or "").strip():
        raise ValueError("Informe a localização (location_filter) quando o escopo for localizacao.")

    response = requests.post(
        _get_inventories_endpoint(),
        json=payload,
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def transition_inventory_status(
    inventory_id: int,
    status: str,
    user_id: int,
    auth_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Efetuar uma transição de estado do ciclo de vida do inventário.

    Args:
        inventory_id: ID do inventário.
        status: Status destino (``Aberto``, ``EmContagem``,
            ``AguardandoAprovacao`` ou ``Concluido``).
        user_id: Usuário que solicita a transição (deve ser o autenticado).
        auth_token: Token Bearer do usuário autenticado (obrigatório no backend).

    Returns:
        Inventário atualizado.
    """
    if not inventory_id:
        raise ValueError("inventory_id é obrigatório.")
    if status not in _VALID_INVENTORY_STATUSES:
        raise ValueError("Status inválido. Use: " + ", ".join(_VALID_INVENTORY_STATUSES) + ".")
    if not user_id:
        raise ValueError("user_id é obrigatório.")

    payload = {
        "id": int(inventory_id),
        "status": status,
        "user_id": int(user_id),
    }
    response = requests.patch(
        _get_inventory_status_endpoint(),
        json=payload,
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def record_inventory_count(
    payload: Dict[str, Any],
    auth_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Registrar ou retomar a contagem física de um produto em um inventário.

    Args:
        payload: Dicionário com ``inventory_id``, ``product_id``,
        ``quantity_counted``, ``counted_by`` e opcionais ``is_recount``,
        ``previous_count_id``, ``notes``.
        auth_token: Token Bearer do usuário autenticado (obrigatório no backend).

    Returns:
        Registro da contagem criada ou atualizada.
    """
    for field in ["inventory_id", "product_id", "counted_by"]:
        if not payload.get(field):
            raise ValueError("O campo " + field + " é obrigatório.")
    quantity = payload.get("quantity_counted")
    if quantity is None or not isinstance(quantity, int) or quantity < 0:
        raise ValueError("A quantidade contada deve ser um número inteiro maior ou igual a zero.")

    response = requests.post(
        _get_inventory_counts_endpoint(),
        json=payload,
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def list_inventory_counts(
    inventory_id: int,
    auth_token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Listar as contagens físicas de um inventário.

    Args:
        inventory_id: ID do inventário.
        auth_token: Token Bearer do usuário autenticado (obrigatório no backend).

    Returns:
        Lista de contagens, mais recente primeiro.
    """
    if not inventory_id:
        raise ValueError("inventory_id é obrigatório.")
    response = requests.get(
        _get_inventory_counts_endpoint(),
        params={"inventory_id": str(int(inventory_id))},
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def reconcile_inventory(
    inventory_id: int,
    user_id: int,
    auth_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Executar a conciliação de estoque de um inventário.

    Compara as contagens físicas com os saldos do sistema e gera as divergências.

    Args:
        inventory_id: ID do inventário.
        user_id: Usuário que solicita a conciliação (deve ser o autenticado).
        auth_token: Token Bearer do usuário autenticado (obrigatório no backend).

    Returns:
        Resultado da conciliação.
    """
    if not inventory_id:
        raise ValueError("inventory_id é obrigatório.")
    if not user_id:
        raise ValueError("user_id é obrigatório.")

    payload = {
        "inventory_id": int(inventory_id),
        "user_id": int(user_id),
    }
    response = requests.post(
        _get_inventory_reconcile_endpoint(),
        json=payload,
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def list_discrepancies(
    inventory_id: int,
    status: Optional[str] = None,
    auth_token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Listar as divergências de conciliação de um inventário.

    Args:
        inventory_id: ID do inventário.
        status: Filtrar por status da divergência (opcional).
        auth_token: Token Bearer do usuário autenticado (obrigatório no backend).

    Returns:
        Lista de divergências.
    """
    if not inventory_id:
        raise ValueError("inventory_id é obrigatório.")
    params: Dict[str, str] = {"inventory_id": str(int(inventory_id))}
    if status:
        params["status"] = status
    response = requests.get(
        _get_inventory_discrepancies_endpoint(),
        params=params,
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def decide_discrepancy(
    payload: Dict[str, Any],
    auth_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Registrar a decisão de um gestor sobre uma divergência.

    Ações: ``approved``, ``rejected`` ou ``recount_requested``.

    Args:
        payload: Dicionário com ``inventory_id``, ``discrepancy_id``, ``action``,
        ``decided_by`` e opcional ``justification``.
        auth_token: Token Bearer do usuário autenticado (obrigatório no backend).

    Returns:
        Divergência atualizada com a decisão.
    """
    for field in ["inventory_id", "discrepancy_id", "action", "decided_by"]:
        if not payload.get(field):
            raise ValueError("O campo " + field + " é obrigatório.")
    action = payload.get("action")
    if action not in _VALID_DISCREPANCY_ACTIONS:
        raise ValueError("Ação inválida. Use: " + ", ".join(_VALID_DISCREPANCY_ACTIONS) + ".")
    if action in ["approved", "rejected"]:
        if not str(payload.get("justification") or "").strip():
            raise ValueError("Justificativa é obrigatória para aprovar ou rejeitar uma divergência.")

    response = requests.post(
        _get_inventory_discrepancy_decision_endpoint(),
        json=payload,
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def apply_adjustments(
    inventory_id: int,
    user_id: int,
    auth_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Aplicar os ajustes de estoque aprovados de um inventário.

    Reutiliza o ledger de auditoria existente (tabela ``stock_movement``,
    ``movement_type = "adjustment"``) da Change 02.

    Args:
        inventory_id: ID do inventário.
        user_id: Usuário gestor que aplica os ajustes (deve ser o autenticado).
        auth_token: Token Bearer do usuário autenticado (obrigatório no backend).

    Returns:
        Resumo dos ajustes aplicados e ignorados (concorrência).
    """
    if not inventory_id:
        raise ValueError("inventory_id é obrigatório.")
    if not user_id:
        raise ValueError("user_id é obrigatório.")

    payload = {
        "inventory_id": int(inventory_id),
        "user_id": int(user_id),
    }
    response = requests.post(
        _get_inventory_apply_adjustments_endpoint(),
        json=payload,
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


# ---------------------------------------------------------------------------
# Operações de saída de estoque (Change 04)
# ---------------------------------------------------------------------------

_OUTBOUND_TYPES = ["SALE", "LAB_SHIPMENT", "LOSS", "OPERATIONAL"]
_OUTBOUND_STATUSES = ["Pendente", "AguardandoAprovacao", "Concluida", "Rejeitada", "Cancelada", "FalhaNoProcessamento"]
_OUTBOUND_TRANSITION_STATUSES = ["AguardandoAprovacao", "Rejeitada", "Cancelada"]


def _get_outbound_endpoint() -> str:
    return _format_endpoint("outbound")


def _get_outbound_status_endpoint() -> str:
    return _format_endpoint("outbound/status")


def _get_outbound_process_endpoint() -> str:
    return _format_endpoint("outbound/process")


def create_outbound(
    payload: Dict[str, Any],
    auth_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Registrar uma saída. O backend define status inicial e solicitante via auth."""
    type_op = payload.get("type")
    if not type_op or str(type_op).strip() not in _OUTBOUND_TYPES:
        raise ValueError("Tipo de saída inválido. Use: " + ", ".join(_OUTBOUND_TYPES) + ".")
    for field in ["product_id", "quantity", "reason"]:
        if not payload.get(field):
            raise ValueError("Campo obrigatório ausente: " + field)
    if not isinstance(payload.get("quantity"), int) or payload.get("quantity") <= 0:
        raise ValueError("Quantidade deve ser > 0")
    if payload.get("type") == "LOSS" and not (payload.get("justification") or "").strip():
        raise ValueError("Justificativa obrigatória para LOSS")
    response = requests.post(
        _get_outbound_endpoint(),
        json=payload,
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def list_outbounds(
    filters: Optional[Dict[str, Any]] = None,
    auth_token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    params = filters or {}
    response = requests.get(
        _get_outbound_endpoint(),
        params=params,
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def get_outbound(outbound_id: int, auth_token: Optional[str] = None) -> Dict[str, Any]:
    if not outbound_id:
        raise ValueError("outbound_id é obrigatório")
    response = requests.get(
        _get_outbound_endpoint(),
        params={"id": int(outbound_id)},
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def update_outbound_status(
    outbound_id: int,
    status: str,
    auth_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Rejeitar/cancelar/solicitar aprovação. Conclusão usa ``process_outbound``."""
    if not outbound_id or not status:
        raise ValueError("outbound_id e status são obrigatórios")
    if status not in _OUTBOUND_TRANSITION_STATUSES:
        raise ValueError(
            "Status inválido para transição. Use: "
            + ", ".join(_OUTBOUND_TRANSITION_STATUSES)
            + ". Para concluir, use process_outbound."
        )
    payload = {"id": int(outbound_id), "status": status}
    response = requests.patch(
        _get_outbound_status_endpoint(),
        json=payload,
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


def process_outbound(
    outbound_id: int,
    auth_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Processar a baixa. O operador é sempre o usuário autenticado no backend."""
    if not outbound_id:
        raise ValueError("outbound_id é obrigatório")
    payload = {"id": int(outbound_id)}
    response = requests.post(
        _get_outbound_process_endpoint(),
        json=payload,
        headers=_auth_headers(auth_token),
        timeout=10,
    )
    return _handle_response(response)


# ---------------------------------------------------------------------------
# Alertas de estoque e reposição (Change 05)
# ---------------------------------------------------------------------------

_ALERT_STATUSES = ["Ativo", "EmAcompanhamento", "Resolvido"]
_ALERT_TYPES = ["LOW_STOCK", "INACTIVE"]


def _get_alerts_endpoint() -> str:
    return _format_endpoint("alerts")


def _get_alerts_evaluate_endpoint() -> str:
    return _format_endpoint("alerts/evaluate")


def _get_alerts_summary_endpoint() -> str:
    return _format_endpoint("alerts/summary")


def _get_alerts_inactive_endpoint() -> str:
    return _format_endpoint("alerts/inactive")


def _get_alerts_status_endpoint() -> str:
    return _format_endpoint("alerts/status")


def _get_replenishment_endpoint() -> str:
    return _format_endpoint("replenishment")


def _get_stock_parameters_endpoint() -> str:
    return _format_endpoint("stock-parameters")


def list_alerts(
    user_id: int,
    status: Optional[str] = None,
    alert_type: Optional[str] = None,
    product_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Listar alertas de estoque com filtros opcionais (mais recente primeiro).

    Args:
        user_id: Usuário requisitante (obrigatório; o backend valida o perfil).
        status: Filtrar por status (``Ativo``, ``EmAcompanhamento`` ou ``Resolvido``).
        alert_type: Filtrar por tipo (``LOW_STOCK`` ou ``INACTIVE``).
        product_id: Filtrar por produto.

    Returns:
        Lista de alertas com dados do produto para exibição.
    """
    if not user_id:
        raise ValueError("user_id é obrigatório.")
    if status is not None and status not in _ALERT_STATUSES:
        raise ValueError("Status inválido. Use: " + ", ".join(_ALERT_STATUSES) + ".")
    if alert_type is not None and alert_type not in _ALERT_TYPES:
        raise ValueError("Tipo de alerta inválido. Use: " + ", ".join(_ALERT_TYPES) + ".")

    params: Dict[str, str] = {"user_id": str(int(user_id))}
    if status:
        params["status"] = status
    if alert_type:
        params["alert_type"] = alert_type
    if product_id:
        params["product_id"] = str(int(product_id))
    response = requests.get(_get_alerts_endpoint(), params=params, timeout=10)
    return _handle_response(response)


def get_alerts_summary(user_id: int) -> Dict[str, Any]:
    """Consultar o resumo ao vivo do painel de alertas (KPIs e perfil do usuário).

    Args:
        user_id: Usuário requisitante (obrigatório; o backend valida o perfil).

    Returns:
        Dicionário com contagens de alertas, cobertura de parâmetros,
        inativos ao vivo e ``actor_role`` para a UI esconder botões.
    """
    if not user_id:
        raise ValueError("user_id é obrigatório.")
    response = requests.get(
        _get_alerts_summary_endpoint(),
        params={"user_id": str(int(user_id))},
        timeout=10,
    )
    return _handle_response(response)


def list_inactive_products(
    user_id: int,
    inactivity_days: Optional[int] = None,
    incluir_sem_historico: bool = True,
) -> List[Dict[str, Any]]:
    """Listar produtos monitorados com a situação de movimentação.

    Diferencia ``Inativo`` (histórico antigo) de ``SemHistorico`` (nunca
    movimentado). A janela enviada prevalece sobre a do produto.

    Args:
        user_id: Usuário requisitante (obrigatório; o backend valida o perfil).
        inactivity_days: Janela opcional em dias (>= 1).
        incluir_sem_historico: Incluir produtos nunca movimentados (padrão True).

    Returns:
        Lista de produtos com ``situacao``, última movimentação (timestamp) e janela.
    """
    if not user_id:
        raise ValueError("user_id é obrigatório.")
    if inactivity_days is not None and (not isinstance(inactivity_days, int) or inactivity_days < 1):
        raise ValueError("A janela de inatividade deve ser um número inteiro maior ou igual a 1 dia.")

    params: Dict[str, str] = {
        "user_id": str(int(user_id)),
        "incluir_sem_historico": "1" if incluir_sem_historico else "0",
    }
    if inactivity_days is not None:
        params["inactivity_days"] = str(int(inactivity_days))
    response = requests.get(_get_alerts_inactive_endpoint(), params=params, timeout=10)
    return _handle_response(response)


def evaluate_alerts(user_id: int) -> Dict[str, Any]:
    """Executar a avaliação idempotente de alertas (LOW_STOCK e INACTIVE).

    Abre alertas quando a condição passa a valer, auto-resolve quando normaliza
    e respeita resoluções manuais (silenciamento). Não altera saldo nem cria
    movimentação. Requer perfil Gestor/Estoquista (validado no backend).

    Args:
        user_id: Usuário requisitante (obrigatório).

    Returns:
        Contadores da execução: ``avaliados``, ``criados``, ``resolvidos``,
        ``silenciados`` e criações por tipo.
    """
    if not user_id:
        raise ValueError("user_id é obrigatório.")
    response = requests.post(
        _get_alerts_evaluate_endpoint(),
        json={"user_id": int(user_id)},
        timeout=30,
    )
    return _handle_response(response)


def update_alert_status(
    alert_id: int,
    status: str,
    user_id: int,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Transição manual de status de um alerta (ciclo de vida do Change 05).

    Transições permitidas: ``Ativo -> EmAcompanhamento``, ``Ativo -> Resolvido``
    e ``EmAcompanhamento -> Resolvido``. ``Resolvido`` é estado final.

    Args:
        alert_id: ID do alerta.
        status: Status destino (``Ativo``, ``EmAcompanhamento`` ou ``Resolvido``).
        user_id: Usuário responsável pela transição (obrigatório ao resolver).
        notes: Observação opcional de acompanhamento.

    Returns:
        Alerta atualizado.
    """
    if not alert_id:
        raise ValueError("alert_id é obrigatório.")
    if status not in _ALERT_STATUSES:
        raise ValueError("Status inválido. Use: " + ", ".join(_ALERT_STATUSES) + ".")
    if not user_id:
        raise ValueError("user_id é obrigatório.")

    payload: Dict[str, Any] = {
        "alert_id": int(alert_id),
        "status": status,
        "user_id": int(user_id),
    }
    if notes is not None:
        if not str(notes).strip():
            raise ValueError("As notas não podem ser vazias.")
        payload["notes"] = str(notes).strip()
    response = requests.post(_get_alerts_status_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


def list_replenishment(
    user_id: int,
    category: Optional[str] = None,
    product_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Consultar sugestões de reposição calculadas no backend.

    A sugestão é ``max(0, target_stock - current_stock)``; sem alvo configurado
    vem ``None`` com ``parametros_incompletos=True``. É apenas recomendação:
    nenhuma compra, pedido ou entrada é criado.

    Args:
        user_id: Usuário requisitante (obrigatório; o backend valida o perfil).
        category: Filtrar por categoria (opcional).
        product_id: Filtrar por produto (opcional).

    Returns:
        Lista por produto com saldo, mínimo, alvo, classificação, sugestão,
        sinalização de falta de parâmetros e custo estimado.
    """
    if not user_id:
        raise ValueError("user_id é obrigatório.")

    params: Dict[str, str] = {"user_id": str(int(user_id))}
    if category:
        params["category"] = str(category).strip()
    if product_id:
        params["product_id"] = str(int(product_id))
    response = requests.get(_get_replenishment_endpoint(), params=params, timeout=10)
    return _handle_response(response)


def update_stock_parameters(
    product_id: int,
    user_id: int,
    min_stock: Optional[int] = None,
    target_stock: Optional[int] = None,
    inactivity_days: Optional[int] = None,
    alerts_enabled: Optional[bool] = None,
) -> Dict[str, Any]:
    """Configurar os parâmetros de estoque e alertas de um produto.

    Somente os campos enviados são alterados; os demais preservam o valor atual.
    Requer perfil Gestor (validado no backend).

    Args:
        product_id: ID do produto.
        user_id: Usuário gestor responsável (obrigatório).
        min_stock: Estoque mínimo (>= 0).
        target_stock: Estoque alvo (>= 0 e >= min_stock efetivo).
        inactivity_days: Janela de inatividade em dias (>= 1).
        alerts_enabled: Ativar/desativar monitoramento do produto.

    Returns:
        Produto atualizado.
    """
    if not product_id:
        raise ValueError("product_id é obrigatório.")
    if not user_id:
        raise ValueError("user_id é obrigatório.")
    if min_stock is not None and (not isinstance(min_stock, int) or min_stock < 0):
        raise ValueError("O estoque mínimo deve ser um número inteiro maior ou igual a zero.")
    if target_stock is not None and (not isinstance(target_stock, int) or target_stock < 0):
        raise ValueError("O estoque alvo deve ser um número inteiro maior ou igual a zero.")
    if min_stock is not None and target_stock is not None and target_stock < min_stock:
        raise ValueError("O estoque alvo deve ser maior ou igual ao estoque mínimo.")
    if inactivity_days is not None and (not isinstance(inactivity_days, int) or inactivity_days < 1):
        raise ValueError("A janela de inatividade deve ser um número inteiro maior ou igual a 1 dia.")
    if alerts_enabled is not None and not isinstance(alerts_enabled, bool):
        raise ValueError("alerts_enabled deve ser True ou False.")

    payload: Dict[str, Any] = {
        "product_id": int(product_id),
        "user_id": int(user_id),
    }
    if min_stock is not None:
        payload["min_stock"] = int(min_stock)
    if target_stock is not None:
        payload["target_stock"] = int(target_stock)
    if inactivity_days is not None:
        payload["inactivity_days"] = int(inactivity_days)
    if alerts_enabled is not None:
        # O backend não aceita booleano em input: envia 1/0.
        payload["alerts_enabled"] = 1 if alerts_enabled else 0
    response = requests.patch(_get_stock_parameters_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


# ---------------------------------------------------------------------------
# Autenticação (Change 06: Login e Autenticação)
# ---------------------------------------------------------------------------

# Canonical do grupo Authentication (xano/api/authentication/authentication.xs).
# A URL pública de um grupo Xano é {origem}/api:{canonical}/{query} — confirmado
# por sondagem ao workspace: o Authentication não responde em {base}/auth/...
# nem sob o prefixo smart_vision/. Derivar da origem evita depender do base
# conter o canonical de outro grupo (Smart Vision = SzoTJegm).
AUTH_GROUP_CANONICAL = "RRY0Pj3A"


def _get_auth_base_url() -> str:
    """Base do grupo Authentication: ``{origem}/api:RRY0Pj3A``.

    Override opcional via ``XANO_AUTH_BASE_URL`` (ex.: proxy próprio).
    """
    override = os.getenv("XANO_AUTH_BASE_URL")
    if not override:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "XANO_AUTH_BASE_URL" in st.secrets:
                override = str(st.secrets["XANO_AUTH_BASE_URL"])
        except Exception:
            pass
    if override and override.strip():
        return override.strip().rstrip("/")
    base = get_base_url()
    origin = "/".join(base.split("/")[:3])  # scheme://host[:port]
    return f"{origin}/api:{AUTH_GROUP_CANONICAL}"


def _get_auth_login_endpoint() -> str:
    """Resolve endpoint de login do Xano Authentication group."""
    return f"{_get_auth_base_url()}/auth/login"


def _get_auth_me_endpoint() -> str:
    """Resolve endpoint auth/me do Xano Authentication group."""
    return f"{_get_auth_base_url()}/auth/me"


def login(email: str, password: str) -> Dict[str, Any]:
    """Autenticar usuário no backend Xano e retornar token e dados do usuário.

    Args:
        email: E-mail/login do usuário.
        password: Senha em texto plano (nunca armazenada localmente).

    Returns:
        Dicionário com ``authToken`` e ``user_id`` retornados pelo Xano.

    Raises:
        ValueError: Se email ou senha estiverem vazios.
        requests.HTTPError: Se as credenciais forem inválidas ou houver falha de comunicação.
    """
    if not email or not str(email).strip():
        raise ValueError("Informe seu usuário.")
    if not password or not str(password):
        raise ValueError("Informe sua senha.")

    payload = {
        "email": str(email).strip().lower(),
        "password": str(password),
    }
    response = requests.post(_get_auth_login_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


def get_me(auth_token: str) -> Dict[str, Any]:
    """Obter dados do usuário autenticado a partir do token de sessão.

    Args:
        auth_token: Token de autenticação gerado pelo Xano no login.

    Returns:
        Dicionário com dados do usuário (id, name, email, account_id, role, etc.).

    Raises:
        requests.HTTPError: Se o token for inválido ou expirado.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(_get_auth_me_endpoint(), headers=headers, timeout=10)
    return _handle_response(response)


# ---------------------------------------------------------------------------
# Gestão de Colaboradores e Equipe (Members & Accounts / Authentication)
# ---------------------------------------------------------------------------

MEMBERS_GROUP_CANONICAL = "NCs6_YME"


def _get_members_base_url() -> str:
    """Base do grupo Members & Accounts: ``{origem}/api:NCs6_YME``.

    Override opcional via ``XANO_MEMBERS_BASE_URL``.
    """
    override = os.getenv("XANO_MEMBERS_BASE_URL")
    if not override:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "XANO_MEMBERS_BASE_URL" in st.secrets:
                override = str(st.secrets["XANO_MEMBERS_BASE_URL"])
        except Exception:
            pass
    if override and override.strip():
        return override.strip().rstrip("/")
    base = get_base_url()
    origin = "/".join(base.split("/")[:3])
    return f"{origin}/api:{MEMBERS_GROUP_CANONICAL}"


def _get_auth_signup_endpoint() -> str:
    """Resolve endpoint de signup do Xano Authentication group."""
    return f"{_get_auth_base_url()}/auth/signup"


def _get_members_team_endpoint() -> str:
    """Resolve endpoint account/my_team_members do Xano Members group."""
    return f"{_get_members_base_url()}/account/my_team_members"


def _get_admin_role_endpoint() -> str:
    """Resolve endpoint admin/user_role do Xano Members group."""
    return f"{_get_members_base_url()}/admin/user_role"


def signup_user(name: str, email: str, password: str) -> Dict[str, Any]:
    """Cadastra um novo usuário no backend Xano via auth/signup.

    Args:
        name: Nome completo do usuário.
        email: E-mail para login.
        password: Senha em texto plano (mínimo 8 caracteres, 1 letra, 1 número).

    Returns:
        Dicionário com ``authToken`` e ``user_id`` gerados pelo Xano.

    Raises:
        ValueError: Se algum campo for inválido.
        requests.HTTPError: Se houver erro de validação ou conflito no Xano.
    """
    if not name or not str(name).strip():
        raise ValueError("Informe o nome do colaborador.")
    if not email or not str(email).strip() or "@" not in str(email):
        raise ValueError("Informe um e-mail válido para o colaborador.")
    if not password or len(str(password)) < 8:
        raise ValueError("A senha deve conter no mínimo 8 caracteres.")

    payload = {
        "name": str(name).strip(),
        "email": str(email).strip().lower(),
        "password": str(password),
    }
    response = requests.post(_get_auth_signup_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


def list_team_members(auth_token: str) -> List[Dict[str, Any]]:
    """Lista colaboradores vinculados à conta da ótica no Xano.

    Args:
        auth_token: Token de autenticação da sessão.

    Returns:
        Lista de membros com id, name, email, created_at, account_id.

    Raises:
        ValueError: Se auth_token não for informado.
        requests.HTTPError: Se houver erro de permissão ou conexão.
    """
    if not auth_token:
        raise ValueError("auth_token é obrigatório.")
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(_get_members_team_endpoint(), headers=headers, timeout=10)
    return _handle_response(response)


def update_user_role(target_user_id: int, new_role: str, auth_token: str) -> Dict[str, Any]:
    """Atualiza o papel/cargo do usuário via admin/user_role no Xano.

    Args:
        target_user_id: ID do usuário a atualizar.
        new_role: Novo cargo/perfil (ex: Gestor, Supervisor, Vendedor, Estoquista, Técnico).
        auth_token: Token de autenticação da sessão.

    Returns:
        Resposta da API Xano com os dados atualizados.
    """
    if not target_user_id:
        raise ValueError("target_user_id é obrigatório.")
    if not new_role or not str(new_role).strip():
        raise ValueError("new_role é obrigatório.")
    if not auth_token:
        raise ValueError("auth_token é obrigatório.")

    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "user_id": int(target_user_id),
        "new_role": str(new_role).strip(),
    }
    response = requests.post(_get_admin_role_endpoint(), json=payload, headers=headers, timeout=10)
    return _handle_response(response)
