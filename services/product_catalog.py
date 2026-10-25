# services/product_catalog.py
"""Regras de apresentação e validação do catálogo de produtos.

A validação definitiva continua no backend Xano. Este módulo concentra as
regras de UX (campos obrigatórios e filtros) para evitar duplicação na tela.
"""

from typing import Any, Dict, List, Optional

LENS_CATEGORIES = ("Lente Oftálmica", "Lente de Contato")
PRODUCT_CATEGORIES = (
    "Armação",
    "Lente Oftálmica",
    "Lente de Contato",
    "Acessórios",
    "Limpeza",
)

REQUIRED_TEXT_FIELDS = {
    "sku": "SKU",
    "name": "Nome",
    "category": "Categoria",
    "brand": "Marca",
    "model": "Modelo",
    "location": "Localização",
}

REQUIRED_TECHNICAL_FIELDS = {
    "sphere_power": "grau esférico",
    "cylinder_power": "grau cilíndrico",
    "lens_type": "tipo de lente",
}

OPTIONAL_TEXT_FIELDS = ("lens_type", "treatment", "material")


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def filter_params(category: Optional[str] = None, search: Optional[str] = None) -> Dict[str, str]:
    """Montar os query params apenas com filtros realmente informados."""
    params: Dict[str, str] = {}
    if category and category.strip() and category.strip() != "Todas":
        params["category"] = category.strip()
    if search and search.strip():
        params["search"] = search.strip()
    return params


def validate_product_payload(payload: Dict[str, Any]) -> List[str]:
    """Validar o formulário antes de enviar ao Xano.

    Retorna uma lista de mensagens legíveis; lista vazia significa válido.
    """
    errors: List[str] = []

    for field, label in REQUIRED_TEXT_FIELDS.items():
        if _is_blank(payload.get(field)):
            errors.append(f"{label} é obrigatório.")

    sale_price = payload.get("sale_price")
    try:
        if sale_price is None or float(sale_price) < 0:
            errors.append("O preço de venda deve ser maior ou igual a zero.")
    except (TypeError, ValueError):
        errors.append("O preço de venda deve ser um número válido.")

    min_stock = payload.get("min_stock")
    try:
        if min_stock is None or int(min_stock) < 0:
            errors.append("O estoque mínimo deve ser um inteiro maior ou igual a zero.")
    except (TypeError, ValueError):
        errors.append("O estoque mínimo deve ser um número inteiro válido.")

    category = str(payload.get("category") or "").strip()
    if category in LENS_CATEGORIES:
        for field, label in REQUIRED_TECHNICAL_FIELDS.items():
            if _is_blank(payload.get(field)):
                errors.append(f"O {label} é obrigatório para lentes.")

        axis = payload.get("axis")
        if axis is not None:
            try:
                axis_value = int(axis)
            except (TypeError, ValueError):
                errors.append("O eixo deve ser um número inteiro entre 0 e 180.")
            else:
                if axis_value < 0 or axis_value > 180:
                    errors.append("O eixo deve estar entre 0 e 180 graus.")

    return errors


def build_product_payload(values: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizar os valores do formulário no payload aceito pelo Xano."""
    category = str(values.get("category") or "").strip()
    payload: Dict[str, Any] = {
        "sku": str(values.get("sku") or "").strip(),
        "name": str(values.get("name") or "").strip(),
        "category": category,
        "brand": str(values.get("brand") or "").strip(),
        "model": str(values.get("model") or "").strip(),
        "sale_price": values.get("sale_price"),
        "min_stock": values.get("min_stock"),
        "location": str(values.get("location") or "").strip(),
    }

    for field in ("cost_price",):
        value = values.get(field)
        if value is not None and value != "":
            payload[field] = value

    if category in LENS_CATEGORIES:
        for field in ("sphere_power", "cylinder_power", "axis", "addition"):
            value = values.get(field)
            if value is not None and value != "":
                payload[field] = value
        for field in OPTIONAL_TEXT_FIELDS:
            value = values.get(field)
            if not _is_blank(value):
                payload[field] = str(value).strip()

    return payload
