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


def _get_products_endpoint() -> str:
    return f"{get_base_url()}/smart_vision/products"


def _get_stock_entry_endpoint() -> str:
    return f"{get_base_url()}/smart_vision/stock_entry"


def _get_stock_exit_endpoint() -> str:
    return f"{get_base_url()}/smart_vision/stock_exit"


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
        payload: Dictionary containing ``product_id``, ``quantity``, ``reason``, and optional ``user_id``.

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

    response = requests.post(_get_stock_entry_endpoint(), json=payload, timeout=10)
    return _handle_response(response)


def record_stock_exit(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Record a stock exit (subtraction) with mandatory audit log and negative stock validation in Xano.

    Args:
        payload: Dictionary containing ``product_id``, ``quantity``, ``reason``, and optional ``user_id``.

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

    response = requests.post(_get_stock_exit_endpoint(), json=payload, timeout=10)
    return _handle_response(response)
