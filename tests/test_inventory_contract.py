# tests/test_inventory_contract.py
"""Testes de contrato entre os endpoints XanoScript e o client Python (Change 03).

Garantem que as rotas declaradas nos arquivos ``.xs`` são exatamente as rotas
chamadas pelo ``services.xano_client``. Também detectam padrões de sintaxe
XanoScript que não são válidos no servidor (ex.: ``foreach $x in $lista`` e
``return = {type: "object"}``), que já causaram endpoints não publicáveis.
"""

import os
import re
import unittest
from pathlib import Path
from unittest.mock import patch

from services import xano_client


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SMART_VISION_DIR = PROJECT_ROOT / "xano" / "api" / "smart_vision"
ADDON_DIR = PROJECT_ROOT / "xano" / "addon"

INVENTORY_FILES = sorted(SMART_VISION_DIR.glob("inventor*.xs"))

NULLABLE_INPUT_RE = re.compile(
    r"^\s*(?:text|int|bool|decimal)\?\s+([A-Za-z0-9_]+)(\?)?(?:\s|$)",
    re.MULTILINE,
)

QUERY_RE = re.compile(
    r'^query\s+(?:"([^"]+)"|([A-Za-z0-9_/-]+))\s+verb=(GET|POST|PATCH|PUT|DELETE)',
    re.MULTILINE,
)

EXPECTED_ROUTES = {
    ("inventories", "GET"),
    ("inventories", "POST"),
    ("inventory", "GET"),
    ("inventories/status", "PATCH"),
    ("inventories/counts", "GET"),
    ("inventories/counts", "POST"),
    ("inventories/reconcile", "POST"),
    ("inventories/discrepancies", "GET"),
    ("inventories/discrepancies/decision", "POST"),
    ("inventories/apply-adjustments", "POST"),
}


def _read_inventory_sources():
    return {path.name: path.read_text(encoding="utf-8") for path in INVENTORY_FILES}


class TestInventoryEndpointContract(unittest.TestCase):

    def setUp(self):
        self.sources = _read_inventory_sources()
        self.routes = set()
        for name, content in self.sources.items():
            for match in QUERY_RE.finditer(content):
                route = match.group(1) or match.group(2)
                self.routes.add((route, match.group(3)))

    def test_all_expected_routes_are_declared(self):
        self.assertEqual(EXPECTED_ROUTES, self.routes)

    def test_client_endpoint_paths_match_declared_routes(self):
        with patch.dict(os.environ, {"XANO_BASE_URL": "https://mock.xano.io/api"}):
            helpers = {
                xano_client._get_inventories_endpoint: "inventories",
                xano_client._get_inventory_endpoint: "inventory",
                xano_client._get_inventory_status_endpoint: "inventories/status",
                xano_client._get_inventory_counts_endpoint: "inventories/counts",
                xano_client._get_inventory_reconcile_endpoint: "inventories/reconcile",
                xano_client._get_inventory_discrepancies_endpoint: "inventories/discrepancies",
                xano_client._get_inventory_discrepancy_decision_endpoint: "inventories/discrepancies/decision",
                xano_client._get_inventory_apply_adjustments_endpoint: "inventories/apply-adjustments",
            }
            for helper, route in helpers.items():
                url = helper()
                self.assertTrue(
                    url.endswith("/smart_vision/" + route),
                    msg=f"{helper.__name__} aponta para {url}, esperado sufixo {route}",
                )
                self.assertIn(route, {r for r, _ in self.routes})

    def test_no_invalid_foreach_syntax(self):
        for name, content in self.sources.items():
            with self.subTest(file=name):
                self.assertNotRegex(
                    content,
                    r"foreach\s+\$[A-Za-z0-9_]+\s+in\s+",
                    msg="Use foreach ($lista) { each as $item { ... } }",
                )

    def test_no_object_return_type(self):
        # O retorno válido para um registro único é "single"; "object" não existe.
        for name, content in self.sources.items():
            with self.subTest(file=name):
                self.assertNotIn('return = {type: "object"}', content)

    def test_no_self_referencing_counter_declaration(self):
        for name, content in self.sources.items():
            with self.subTest(file=name):
                self.assertNotRegex(
                    content,
                    r"var\s+\$([A-Za-z0-9_]+)\s*\{\s*value\s*=\s*\$\1\s*\+",
                    msg="Inicialize o contador antes do loop e use var.update.",
                )

    def test_all_endpoints_require_authenticated_user(self):
        """Toda operação de inventário deve exigir auth e não confiar no cliente."""
        for name, content in self.sources.items():
            with self.subTest(file=name):
                self.assertIn(
                    '  auth = "user"',
                    content,
                    msg='O endpoint deve declarar auth = "user".',
                )
                for field in ["user_id", "counted_by", "decided_by", "opened_by"]:
                    self.assertNotRegex(
                        content,
                        rf"field_value\s*=\s*\$input\.{field}\b",
                        msg=f"Não use $input.{field} para identificar o usuário.",
                    )
                    self.assertNotRegex(
                        content,
                        rf"\b{field}:\s*\$input\.{field}\b",
                        msg=f"Não grave $input.{field} como identidade; use $auth.id.",
                    )

    def test_error_types_are_valid(self):
        """O Xano rejeita tipos de erro fora da lista suportada (ex.: 'forbidden')."""
        allowed = {"standard", "notfound", "accessdenied", "toomanyrequests", "unauthorized", "badrequest", "inputerror"}
        for name, content in self.sources.items():
            with self.subTest(file=name):
                for error_type in re.findall(r'error_type\s*=\s*"([^"]+)"', content):
                    self.assertIn(
                        error_type,
                        allowed,
                        msg=f"{name}: error_type inválido '{error_type}'.",
                    )

    def test_nullable_inputs_are_truly_optional(self):
        """`text? nome` é obrigatório e nullable; opcional de verdade usa `nome?`."""
        for name, content in self.sources.items():
            with self.subTest(file=name):
                for match in NULLABLE_INPUT_RE.finditer(content):
                    field, optional = match.group(1), match.group(2)
                    self.assertEqual(
                        optional,
                        "?",
                        msg=f"{name}: o input nullable '{field}' deve ser opcional ('{field}?').",
                    )

    def test_inventory_list_exposes_progress_addons(self):
        """A listagem deve trazer progresso via addons, conforme a spec."""
        list_source = (SMART_VISION_DIR / "inventories_GET.xs").read_text(encoding="utf-8")
        self.assertIn("addon = [", list_source)
        self.assertIn("inventory_counts", list_source)
        self.assertIn("inventory_scope", list_source)
        for addon_name in ["inventory_counts.xs", "inventory_scope.xs"]:
            path = ADDON_DIR / addon_name
            with self.subTest(addon=addon_name):
                self.assertTrue(path.exists(), msg=f"Addon ausente: {path}")
                addon_source = path.read_text(encoding="utf-8")
                self.assertEqual(addon_source.count("db.query"), 1, msg="Addons devem ter um único db.query.")
                self.assertIn("return = {type: \"count\"}", addon_source)


if __name__ == "__main__":
    unittest.main()
