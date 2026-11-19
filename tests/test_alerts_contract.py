# tests/test_alerts_contract.py
"""Testes de contrato entre os endpoints XanoScript de alertas e o client Python.

Cobrem o módulo de alertas/reposição (Change 05) e travam os padrões de sintaxe
XanoScript que impediam a publicação na instância live:

* rotas com ``/`` ou ``-`` precisam estar entre aspas;
* ``error_type = "forbidden"`` não é aceito (o correto é ``accessdenied``);
* ``foreach $x in $lista`` não existe (usar ``foreach ($lista) { each as $x {``);
* ``response``/``tags``/``guid`` ficam fora do bloco ``stack``.
"""

import os
import re
import unittest
from pathlib import Path
from unittest.mock import patch

from services import xano_client


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SMART_VISION_DIR = PROJECT_ROOT / "xano" / "api" / "smart_vision"
FUNCTION_DIR = PROJECT_ROOT / "xano" / "function" / "smart_vision"

ALERTS_FILES = sorted(SMART_VISION_DIR.glob("alerts_*.xs"))
ALERTS_FILES += [
    SMART_VISION_DIR / "replenishment_GET.xs",
    SMART_VISION_DIR / "stock_parameters_PATCH.xs",
]
ALERTS_FUNCTIONS = [
    FUNCTION_DIR / "avaliar_alerta.xs",
    FUNCTION_DIR / "classificar_produto.xs",
]

QUERY_RE = re.compile(
    r'^query\s+(?:"([^"]+)"|([A-Za-z0-9_/-]+))\s+verb=(GET|POST|PATCH|PUT|DELETE)',
    re.MULTILINE,
)

EXPECTED_ROUTES = {
    ("alerts", "GET"),
    ("alerts/summary", "GET"),
    ("alerts/inactive", "GET"),
    ("alerts/evaluate", "POST"),
    ("alerts/status", "POST"),
    ("replenishment", "GET"),
    ("stock-parameters", "PATCH"),
}


def _read_sources():
    return {path.name: path.read_text(encoding="utf-8") for path in ALERTS_FILES}


class TestAlertsEndpointContract(unittest.TestCase):

    def setUp(self):
        self.sources = _read_sources()
        self.routes = set()
        for content in self.sources.values():
            for match in QUERY_RE.finditer(content):
                route = match.group(1) or match.group(2)
                self.routes.add((route, match.group(3)))

    def test_all_expected_routes_are_declared(self):
        self.assertEqual(EXPECTED_ROUTES, self.routes)

    def test_client_endpoint_paths_match_declared_routes(self):
        with patch.dict(os.environ, {"XANO_BASE_URL": "https://mock.xano.io/api"}):
            helpers = {
                xano_client._get_alerts_endpoint: "alerts",
                xano_client._get_alerts_summary_endpoint: "alerts/summary",
                xano_client._get_alerts_inactive_endpoint: "alerts/inactive",
                xano_client._get_alerts_evaluate_endpoint: "alerts/evaluate",
                xano_client._get_alerts_status_endpoint: "alerts/status",
                xano_client._get_replenishment_endpoint: "replenishment",
                xano_client._get_stock_parameters_endpoint: "stock-parameters",
            }
            declared = {route for route, _ in self.routes}
            for helper, route in helpers.items():
                url = helper()
                self.assertTrue(
                    url.endswith("/smart_vision/" + route),
                    msg=f"{helper.__name__} aponta para {url}, esperado sufixo {route}",
                )
                self.assertIn(route, declared)

    def test_routes_with_separators_are_quoted(self):
        """`/` sem aspas é lido como divisão; `-` também quebra o parser."""
        for name, content in self.sources.items():
            for match in re.finditer(r"^query\s+([^\s]+)\s+verb=", content, re.MULTILINE):
                identifier = match.group(1)
                if "/" in identifier or "-" in identifier:
                    with self.subTest(file=name, route=identifier):
                        self.assertTrue(
                            identifier.startswith('"') and identifier.endswith('"'),
                            msg=f'{name}: a rota "{identifier}" precisa estar entre aspas.',
                        )

    def test_no_invalid_foreach_syntax(self):
        for name, content in self.sources.items():
            with self.subTest(file=name):
                self.assertNotRegex(
                    content,
                    r"foreach\s+\$[A-Za-z0-9_]+\s+in\s+",
                    msg="Use foreach ($lista) { each as $item { ... } }",
                )

    def test_no_conditionals_inside_var_blocks(self):
        """O parser do Xano rejeita `if` aninhado no corpo de `var {}`."""
        for name, content in self.sources.items():
            inside = False
            depth = 0
            for line in content.splitlines():
                stripped = line.strip()
                if not inside and re.match(r"var\s+\$[A-Za-z0-9_]+\s*\{", stripped):
                    inside = True
                    depth = 1
                    continue
                if inside:
                    depth += stripped.count("{") - stripped.count("}")
                    if re.match(r"(if|conditional)\b", stripped):
                        with self.subTest(file=name):
                            self.fail(
                                f"{name}: use `conditional {{ if (...) {{ ... }} }}` "
                                f"e `var.update` em vez de `if` dentro de `var {{}}`."
                            )
                    if depth <= 0:
                        inside = False

    def test_response_declared_outside_stack(self):
        for name, content in self.sources.items():
            with self.subTest(file=name):
                match = re.search(r"^[ \t]*response[ \t]*=", content, re.MULTILINE)
                self.assertIsNotNone(match, msg=f"{name}: response ausente.")
                line = content[: match.start()].count("\n")
                indent = len(match.group(0)) - len(match.group(0).lstrip())
                self.assertEqual(
                    indent,
                    2,
                    msg=f"{name}: `response` deve ficar fora do `stack` (linha {line + 1}).",
                )

    def test_error_types_are_valid(self):
        allowed = {
            "standard",
            "notfound",
            "accessdenied",
            "toomanyrequests",
            "unauthorized",
            "badrequest",
            "inputerror",
        }
        sources = dict(self.sources)
        for path in ALERTS_FUNCTIONS:
            sources[path.name] = path.read_text(encoding="utf-8")
        for name, content in sources.items():
            with self.subTest(file=name):
                for error_type in re.findall(r'error_type\s*=\s*"([^"]+)"', content):
                    self.assertIn(
                        error_type,
                        allowed,
                        msg=f"{name}: error_type inválido '{error_type}' (403 = accessdenied).",
                    )

    def test_functions_use_var_update_for_reassignment(self):
        """Valores condicionais são atribuídos com `var.update`, não no bloco `var`."""
        for path in ALERTS_FUNCTIONS:
            with self.subTest(file=path.name):
                content = path.read_text(encoding="utf-8")
                self.assertNotRegex(
                    content,
                    r"var\s+\$[A-Za-z0-9_]+\s*\{\s*value\s*=[^}]*\n\s*if\s",
                    msg=f"{path.name}: use `conditional {{ if (...) {{ var.update ... }} }}`.",
                )
