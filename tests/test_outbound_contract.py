import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTBOUND_DIR = ROOT / "xano" / "api" / "smart_vision"
TABLE = ROOT / "xano" / "table" / "stock_outbound.xs"


class TestOutboundEndpointContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.get_source = (OUTBOUND_DIR / "outbound_GET.xs").read_text(encoding="utf-8")
        cls.post_source = (OUTBOUND_DIR / "outbound_POST.xs").read_text(encoding="utf-8")
        cls.status_source = (OUTBOUND_DIR / "outbound_status_PATCH.xs").read_text(encoding="utf-8")
        cls.process_source = (OUTBOUND_DIR / "outbound_process_POST.xs").read_text(encoding="utf-8")
        cls.table_source = TABLE.read_text(encoding="utf-8")

    def test_routes_and_verbs(self):
        self.assertRegex(self.get_source, r"(?m)^query outbound verb=GET")
        self.assertRegex(self.post_source, r"(?m)^query outbound verb=POST")
        self.assertRegex(self.status_source, r'(?m)^query "outbound/status" verb=PATCH')
        self.assertRegex(self.process_source, r'(?m)^query "outbound/process" verb=POST')

    def test_all_endpoints_require_authentication(self):
        for name, source in [
            ("GET", self.get_source),
            ("POST", self.post_source),
            ("PATCH status", self.status_source),
            ("POST process", self.process_source),
        ]:
            with self.subTest(endpoint=name):
                self.assertIn('auth = "user"', source)

    def test_identity_comes_from_auth_not_payload(self):
        self.assertIn("user_id: $auth.id", self.post_source)
        self.assertIn("user_id: $auth.id", self.process_source)
        self.assertIn("approved_by: $auth.id", self.status_source)
        self.assertIn("approved_by: $auth.id", self.process_source)
        for source in [self.post_source, self.status_source, self.process_source]:
            self.assertNotIn("$input.user_id", source)

    def test_create_validates_type_quantity_and_loss(self):
        for outbound_type in ["SALE", "LAB_SHIPMENT", "LOSS", "OPERATIONAL"]:
            self.assertIn(f'$input.type == "{outbound_type}"', self.post_source)
        self.assertIn("$input.quantity > 0", self.post_source)
        self.assertIn("Justificativa obrigatória", self.post_source)
        self.assertIn('$initial_status {\n      value = "Pendente"', self.post_source)
        self.assertIn('value = "AguardandoAprovacao"', self.post_source)
        self.assertNotIn("text? status", self.post_source)

    def test_create_is_idempotent_and_checks_product(self):
        self.assertIn("idempotency_key", self.post_source)
        self.assertIn("Operação já registrada", self.post_source)
        self.assertIn("db.get product", self.post_source)
        self.assertIn("Produto não encontrado", self.post_source)
        self.assertIn("btree|unique", self.table_source)
        self.assertIn("idempotency_key", self.table_source)

    def test_get_supports_period_filters_and_authentication(self):
        self.assertIn("timestamp? from_date?", self.get_source)
        self.assertIn("timestamp? to_date?", self.get_source)
        self.assertIn("$db.stock_outbound.created_at >=? $input.from_date", self.get_source)
        self.assertIn("$db.stock_outbound.created_at <=? $input.to_date", self.get_source)

    def test_status_endpoint_controls_transitions(self):
        self.assertIn('$input.status != "Concluida"', self.status_source)
        self.assertIn('$input.status == "AguardandoAprovacao"', self.status_source)
        self.assertIn('$input.status == "Rejeitada"', self.status_source)
        self.assertIn('$input.status == "Cancelada"', self.status_source)
        self.assertIn("$outbound.status == \"AguardandoAprovacao\"", self.status_source)
        self.assertIn("$outbound.status == \"Pendente\"", self.status_source)
        self.assertIn("$is_manager", self.status_source)
        self.assertIn("db.transaction", self.status_source)

    def test_process_is_authenticated_atomic_and_idempotent(self):
        self.assertIn("db.transaction", self.process_source)
        self.assertIn("$outbound.stock_movement_id == null", self.process_source)
        self.assertIn("$locked_product.current_stock >= $outbound.quantity", self.process_source)
        self.assertIn('movement_type: "exit"', self.process_source)
        self.assertIn("stock_movement_id: $audit.id", self.process_source)
        self.assertIn('$outbound.status == "AguardandoAprovacao"', self.process_source)
        self.assertIn("Apenas gestor", self.process_source)
        self.assertNotIn("field_value:", self.process_source)

    def test_table_has_required_columns_and_indexes(self):
        for column in [
            "type",
            "status",
            "product_id",
            "quantity",
            "user_id",
            "approved_by",
            "approved_at",
            "stock_movement_id",
            "processed_at",
            "idempotency_key",
        ]:
            self.assertRegex(self.table_source, rf"(?m)^\s+\w+\?? {column}\b")
        for index in ["type", "status", "product_id", "user_id", "created_at"]:
            self.assertIn(f'name: "{index}"', self.table_source)


class TestOutboundSourceHygiene(unittest.TestCase):
    def test_no_empty_field_value_typo(self):
        for path in OUTBOUND_DIR.glob("outbound_*.xs"):
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertNotIn("field_value:", source)
                self.assertNotIn("field_name:", source)

    def test_braces_are_balanced(self):
        for path in [
            OUTBOUND_DIR / "outbound_GET.xs",
            OUTBOUND_DIR / "outbound_POST.xs",
            OUTBOUND_DIR / "outbound_status_PATCH.xs",
            OUTBOUND_DIR / "outbound_process_POST.xs",
            TABLE,
        ]:
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertEqual(source.count("{"), source.count("}"))

    def test_no_forbidden_error_type(self):
        for path in OUTBOUND_DIR.glob("outbound_*.xs"):
            with self.subTest(path=path.name):
                self.assertNotIn('error_type = "forbidden"', path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
