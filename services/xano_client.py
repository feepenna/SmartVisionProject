# services/xano_client.py
"""Xano client service.

Provides helper functions to interact with the Xano backend for the product catalog.

Environment Variables:
- ``XANO_BASE_URL``: Base URL of the Xano API (e.g. ``https://example.xano.io/api``).

The functions raise ``requests.HTTPError`` for non‑2xx responses so that callers can handle errors
appropriately.
"""

import os
from typing import Any, Dict, List, Optional

import requests

# Retrieve base URL from environment; raise a clear error if not set.
_BASE_URL = os.getenv("XANO_BASE_URL")
if not _BASE_URL:
    raise EnvironmentError("Environment variable XANO_BASE_URL must be set to the Xano API base URL.")

# Endpoints derived from the OpenSpec definitions.
_PRODUCTS_ENDPOINT = f"{_BASE_URL}/smart_vision/products"


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
    response = requests.get(_PRODUCTS_ENDPOINT, params=params, timeout=10)
    return _handle_response(response)


def create_product(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new product in Xano.

    Args:
        payload: Dictionary matching the fields defined in the Xano ``product`` table.

    Returns:
        The created product record as returned by Xano.
    """
    response = requests.post(_PRODUCTS_ENDPOINT, json=payload, timeout=10)
    return _handle_response(response)
