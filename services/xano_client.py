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
    """Retrieve base URL from environment; raise a clear error if not set."""
    base_url = os.getenv("XANO_BASE_URL")
    if not base_url:
        raise EnvironmentError("Environment variable XANO_BASE_URL must be set to the Xano API base URL.")
    return base_url.rstrip("/")


def _format_endpoint(path: str) -> str:
    """Resolve endpoint URL supporting both standard and canonical group paths."""
    base = get_base_url()
    clean_path = path.lstrip("/")
    if ":SzoTJegm" in base or ":smart_vision" in base or base.endswith("/smart_vision"):
        return f"{base}/{clean_path}"
    return f"{base}/smart_vision/{clean_path}"


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


def list_products(filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    """Retrieve a list of products.

    Args:
        filters: Optional dictionary with query parameters (e.g. ``{"category": "lens"}``).

    Returns:
        A list of product dictionaries as returned by Xano.
    """
    params = filters or {}
    response = requests.get(_get_products_endpoint(), params=params, timeout=10)
    return _handle_response(response)


def create_product(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new product in Xano.

    Args:
        payload: Dictionary matching the fields defined in the Xano ``product`` table.

    Returns:
        The created product record as returned by Xano.
    """
    response = requests.post(_get_products_endpoint(), json=payload, timeout=10)
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
_VALID_DISCREPANCY_ACTIONS = ["approved", "rejected", "recount_requested"]


def list_inventories(filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    """Listar inventários físicos.

    Args:
        filters: Filtros opcionais (ex: ``{"status": "Aberto", "opened_by": "1"}``).

    Returns:
        Lista de inventários conforme retornado pelo Xano.
    """
    params = filters or {}
    response = requests.get(_get_inventories_endpoint(), params=params, timeout=10)
    return _handle_response(response)


def get_inventory(inventory_id: int) -> Dict[str, Any]:
    """Consultar detalhes de um inventário, incluindo progresso da contagem.

    Args:
        inventory_id: ID do inventário.

    Returns:
        Detalhe do inventário com progresso de contagem.
    """
    if not inventory_id:
        raise ValueError("inventory_id é obrigatório.")
    response = requests.get(
        _get_inventory_endpoint(),
        params={"id": int(inventory_id)},
        timeout=10,
    )
    return _handle_response(response)


def create_inventory(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Criar um novo inventário físico com status ``Aberto``.

    Args:
        payload: Dicionário com ``scope``, ``opened_by`` e opcionais
        ``status``, ``category_filter``, ``location_filter``, ``notes``.

    Returns:
        Registro do inventário criado.
    """
    scope = payload.get("scope")
    if not scope or not str(scope).strip():
        raise ValueError("O escopo do inventário é obrigatório.")
    if not payload.get("opened_by"):
        raise ValueError("O responsável pela abertura (opened_by) é obrigatório.")
    status = payload.get("status", "Aberto")
    if status not in _VALID_INVENTORY_STATUSES:
        raise ValueError("Status inválido. Use: " + ", ".join(_VALID_INVENTORY_STATUSES) + ".")

    response = requests.post(_get_inventories_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


def transition_inventory_status(inventory_id: int, status: str, user_id: int) -> Dict[str, Any]:
    """Efetuar uma transição de estado do ciclo de vida do inventário.

    Args:
        inventory_id: ID do inventário.
        status: Status destino (``Aberto``, ``EmContagem``,
            ``AguardandoAprovacao`` ou ``Concluido``).
        user_id: Usuário que solicita a transição.

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
    response = requests.patch(_get_inventory_status_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


def record_inventory_count(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Registrar ou retomar a contagem física de um produto em um inventário.

    Args:
        payload: Dicionário com ``inventory_id``, ``product_id``,
        ``quantity_counted``, ``counted_by`` e opcionais ``is_recount``,
        ``previous_count_id``, ``notes``.

    Returns:
        Registro da contagem criada ou atualizada.
    """
    for field in ["inventory_id", "product_id", "counted_by"]:
        if not payload.get(field):
            raise ValueError("O campo " + field + " é obrigatório.")
    quantity = payload.get("quantity_counted")
    if quantity is None or not isinstance(quantity, int) or quantity < 0:
        raise ValueError("A quantidade contada deve ser um número inteiro maior ou igual a zero.")

    response = requests.post(_get_inventory_counts_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


def list_inventory_counts(inventory_id: int) -> List[Dict[str, Any]]:
    """Listar as contagens físicas de um inventário.

    Args:
        inventory_id: ID do inventário.

    Returns:
        Lista de contagens, mais recente primeiro.
    """
    if not inventory_id:
        raise ValueError("inventory_id é obrigatório.")
    response = requests.get(
        _get_inventory_counts_endpoint(),
        params={"inventory_id": str(int(inventory_id))},
        timeout=10,
    )
    return _handle_response(response)


def reconcile_inventory(inventory_id: int, user_id: int) -> Dict[str, Any]:
    """Executar a conciliação de estoque de um inventário.

    Compara as contagens físicas com os saldos do sistema e gera as divergências.

    Args:
        inventory_id: ID do inventário.
        user_id: Usuário que solicita a conciliação.

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
    response = requests.post(_get_inventory_reconcile_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


def list_discrepancies(inventory_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Listar as divergências de conciliação de um inventário.

    Args:
        inventory_id: ID do inventário.
        status: Filtrar por status da divergência (opcional).

    Returns:
        Lista de divergências.
    """
    if not inventory_id:
        raise ValueError("inventory_id é obrigatório.")
    params: Dict[str, str] = {"inventory_id": str(int(inventory_id))}
    if status:
        params["status"] = status
    response = requests.get(_get_inventory_discrepancies_endpoint(), params=params, timeout=10)
    return _handle_response(response)


def decide_discrepancy(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Registrar a decisão de um gestor sobre uma divergência.

    Ações: ``approved``, ``rejected`` ou ``recount_requested``.

    Args:
        payload: Dicionário com ``inventory_id``, ``discrepancy_id``, ``action``,
        ``decided_by`` e opcional ``justification``.

    Returns:
        Divergência atualizada com a decisão.
    """
    for field in ["inventory_id", "discrepancy_id", "action", "decided_by"]:
        if not payload.get(field):
            raise ValueError("O campo " + field + " é obrigatório.")
    action = payload.get("action")
    if action not in _VALID_DISCREPANCY_ACTIONS:
        raise ValueError("Ação inválida. Use: " + ", ".join(_VALID_DISCREPANCY_ACTIONS) + ".")

    response = requests.post(_get_inventory_discrepancy_decision_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


def apply_adjustments(inventory_id: int, user_id: int) -> Dict[str, Any]:
    """Aplicar os ajustes de estoque aprovados de um inventário.

    Reutiliza o ledger de auditoria existente (tabela ``stock_movement``,
    ``movement_type = "adjustment"``) da Change 02.

    Args:
        inventory_id: ID do inventário.
        user_id: Usuário gestor que aplica os ajustes.

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
    response = requests.post(_get_inventory_apply_adjustments_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


# ---------------------------------------------------------------------------
# Operações de saída de estoque (Change 04)
# ---------------------------------------------------------------------------

_OUTBOUND_TYPES = ["SALE", "LAB_SHIPMENT", "LOSS", "OPERATIONAL"]
_OUTBOUND_STATUSES = ["Pendente", "AguardandoAprovacao", "Concluida", "Rejeitada", "Cancelada", "FalhaNoProcessamento"]


def _get_outbound_endpoint() -> str:
    return _format_endpoint("outbound")


def _get_outbound_status_endpoint() -> str:
    return _format_endpoint("outbound/status")


def _get_outbound_process_endpoint() -> str:
    return _format_endpoint("outbound/process")


def create_outbound(payload: Dict[str, Any]) -> Dict[str, Any]:
    type_op = payload.get("type")
    if not type_op or str(type_op).strip() not in _OUTBOUND_TYPES:
        raise ValueError("Tipo de saída inválido. Use: " + ", ".join(_OUTBOUND_TYPES) + ".")
    for field in ["product_id", "quantity", "user_id", "reason"]:
        if not payload.get(field):
            raise ValueError("Campo obrigatório ausente: " + field)
    if not isinstance(payload.get("quantity"), int) or payload.get("quantity") <= 0:
        raise ValueError("Quantidade deve ser > 0")
    if payload.get("type") == "LOSS" and not (payload.get("justification") or "").strip():
        raise ValueError("Justificativa obrigatória para LOSS")
    response = requests.post(_get_outbound_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


def list_outbounds(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    params = filters or {}
    response = requests.get(_get_outbound_endpoint(), params=params, timeout=10)
    return _handle_response(response)


def get_outbound(outbound_id: int) -> Dict[str, Any]:
    if not outbound_id:
        raise ValueError("outbound_id é obrigatório")
    response = requests.get(_get_outbound_endpoint(), params={"id": int(outbound_id)}, timeout=10)
    return _handle_response(response)


def update_outbound_status(outbound_id: int, status: str, user_id: Optional[int] = None) -> Dict[str, Any]:
    if not outbound_id or not status:
        raise ValueError("outbound_id e status são obrigatórios")
    if status not in _OUTBOUND_STATUSES:
        raise ValueError("Status inválido")
    payload = {"id": int(outbound_id), "status": status}
    if user_id:
        payload["user_id"] = int(user_id)
    response = requests.patch(_get_outbound_status_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


def process_outbound(outbound_id: int, user_id: int) -> Dict[str, Any]:
    if not outbound_id or not user_id:
        raise ValueError("outbound_id e user_id são obrigatórios")
    payload = {"id": int(outbound_id), "user_id": int(user_id)}
    response = requests.post(_get_outbound_process_endpoint(), json=payload, timeout=10)
    return _handle_response(response)
