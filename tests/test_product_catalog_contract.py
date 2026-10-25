"""Contrato dos arquivos XanoScript do catálogo de produtos."""

import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SMART_VISION_DIR = PROJECT_ROOT / "xano" / "api" / "smart_vision"
TABLE_DIR = PROJECT_ROOT / "xano" / "table"

GET_FILE = SMART_VISION_DIR / "products_GET.xs"
POST_FILE = SMART_VISION_DIR / "products_POST.xs"
TABLE_FILE = TABLE_DIR / "product.xs"


class TestProductEndpointContract(unittest.TestCase):
    def setUp(self):
        self.get_source = GET_FILE.read_text(encoding="utf-8")
        self.post_source = POST_FILE.read_text(encoding="utf-8")
        self.table_source = TABLE_FILE.read_text(encoding="utf-8")

    def test_routes(self):
        self.assertRegex(self.get_source, r"(?m)^query products verb=GET")
        self.assertRegex(self.post_source, r"(?m)^query products verb=POST")

    def test_get_filters_are_truly_optional(self):
        self.assertIn("text? category? filters=trim", self.get_source)
        self.assertIn("text? search? filters=trim", self.get_source)
        self.assertIn("$input.category == null", self.get_source)
        self.assertIn("$input.search == null", self.get_source)
        self.assertNotIn("==?", self.get_source)

    def test_post_requires_general_fields(self):
        for field in ["sku", "name", "category", "brand", "model", "location"]:
            with self.subTest(field=field):
                self.assertRegex(
                    self.post_source,
                    rf"(?m)^\s*text {field} filters=trim$",
                )
        self.assertIn("Preencha os campos obrigatórios", self.post_source)

    def test_post_validates_numbers(self):
        self.assertIn("$input.sale_price >= 0", self.post_source)
        self.assertIn("$input.min_stock >= 0", self.post_source)
        self.assertIn("O estoque mínimo deve ser maior ou igual a zero.", self.post_source)

    def test_post_requires_lens_technical_fields(self):
        self.assertIn("$input.sphere_power != null", self.post_source)
        self.assertIn("$input.cylinder_power != null", self.post_source)
        self.assertIn("$input.lens_type != null", self.post_source)
        self.assertIn("$input.axis == null ||", self.post_source)

    def test_post_validates_unique_sku(self):
        self.assertIn("db.has product", self.post_source)
        self.assertIn('field_name = "sku"', self.post_source)
        self.assertIn("O SKU informado já está em uso", self.post_source)

    def test_post_starts_stock_at_zero(self):
        self.assertIn("current_stock : 0", self.post_source)

    def test_error_types_are_valid(self):
        allowed = {
            "standard", "notfound", "accessdenied", "toomanyrequests",
            "unauthorized", "badrequest", "inputerror",
        }
        for name, source in [("GET", self.get_source), ("POST", self.post_source)]:
            with self.subTest(endpoint=name):
                for error_type in re.findall(r'error_type\s*=\s*"([^"]+)"', source):
                    self.assertIn(error_type, allowed)
                self.assertNotIn('error_type = "forbidden"', source)

    def test_table_has_unique_sku_index(self):
        self.assertIn("table product", self.table_source)
        self.assertIn('type: "btree|unique"', self.table_source)
        self.assertIn('name: "sku"', self.table_source)

    def test_table_has_required_columns(self):
        for column in [
            "int id", "text sku", "text name", "text category", "text? brand",
            "text? model", "decimal? cost_price", "decimal sale_price",
            "int current_stock", "int min_stock", "text? location",
            "decimal? sphere_power", "decimal? cylinder_power", "int? axis",
            "decimal? addition", "text? lens_type", "text? treatment",
            "text? material",
        ]:
            with self.subTest(column=column):
                self.assertIn(column, self.table_source)


if __name__ == "__main__":
    unittest.main()
