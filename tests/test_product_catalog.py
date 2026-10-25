"""Testes do catálogo de produtos: cliente Xano e validações de domínio."""

import os
import unittest
from unittest.mock import patch

import requests

from services import product_catalog
from services import xano_client


VALID_FRAME = {
    "sku": "ARM-TEST-01",
    "name": "Armação de Teste",
    "category": "Armação",
    "brand": "TestBrand",
    "model": "TestModel",
    "sale_price": 450.0,
    "min_stock": 5,
    "location": "Vitrine A1",
}

VALID_LENS = {
    **VALID_FRAME,
    "sku": "LEN-TEST-01",
    "name": "Lente de Teste",
    "category": "Lente Oftálmica",
    "sphere_power": -2.5,
    "cylinder_power": -0.75,
    "axis": 180,
    "lens_type": "Monofocal",
}


class TestProductCatalogClient(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(
            os.environ,
            {"XANO_BASE_URL": "https://example.xano.io/api:SzoTJegm"},
            clear=False,
        )
        self.env.start()
        self.addCleanup(self.env.stop)

    @patch("services.xano_client.requests.get")
    def test_list_products_without_filters(self, mock_get):
        mock_get.return_value.json.return_value = []
        mock_get.return_value.raise_for_status.return_value = None

        result = xano_client.list_products()

        self.assertEqual(result, [])
        mock_get.assert_called_once_with(
            "https://example.xano.io/api:SzoTJegm/products",
            params={},
            timeout=10,
        )

    @patch("services.xano_client.requests.get")
    def test_list_products_with_filters(self, mock_get):
        mock_get.return_value.json.return_value = [{"id": 1}]
        mock_get.return_value.raise_for_status.return_value = None

        result = xano_client.list_products({"category": "Armação", "search": "Ray"})

        self.assertEqual(result, [{"id": 1}])
        mock_get.assert_called_once_with(
            "https://example.xano.io/api:SzoTJegm/products",
            params={"category": "Armação", "search": "Ray"},
            timeout=10,
        )

    @patch("services.xano_client.requests.post")
    def test_create_product_posts_payload(self, mock_post):
        mock_post.return_value.json.return_value = {"id": 10, **VALID_FRAME}
        mock_post.return_value.raise_for_status.return_value = None

        result = xano_client.create_product(VALID_FRAME)

        self.assertEqual(result["id"], 10)
        mock_post.assert_called_once_with(
            "https://example.xano.io/api:SzoTJegm/products",
            json=VALID_FRAME,
            timeout=10,
        )

    @patch("services.xano_client.requests.post")
    def test_create_product_propagates_http_error_with_body(self, mock_post):
        response = mock_post.return_value
        response.raise_for_status.side_effect = requests.HTTPError("400 Client Error")
        response.text = '{"message": "SKU já está em uso"}'

        with self.assertRaises(requests.HTTPError) as ctx:
            xano_client.create_product({"sku": "DUPLICADO"})

        self.assertIn("SKU já está em uso", str(ctx.exception))


class TestProductCatalogFilters(unittest.TestCase):
    def test_empty_filters(self):
        self.assertEqual(product_catalog.filter_params("Todas", "   "), {})

    def test_filters_are_trimmed(self):
        self.assertEqual(
            product_catalog.filter_params(" Armação ", " Ray "),
            {"category": "Armação", "search": "Ray"},
        )


class TestProductCatalogValidation(unittest.TestCase):
    def test_valid_frame_has_no_errors(self):
        self.assertEqual(product_catalog.validate_product_payload(VALID_FRAME), [])

    def test_valid_lens_has_no_errors(self):
        self.assertEqual(product_catalog.validate_product_payload(VALID_LENS), [])

    def test_missing_required_fields(self):
        errors = product_catalog.validate_product_payload({"category": "Armação"})
        joined = " ".join(errors)
        for label in ["SKU", "Nome", "Marca", "Modelo", "Localização"]:
            self.assertIn(label, joined)

    def test_negative_min_stock(self):
        errors = product_catalog.validate_product_payload({**VALID_FRAME, "min_stock": -1})
        self.assertTrue(any("estoque mínimo" in e.lower() for e in errors))

    def test_negative_sale_price(self):
        errors = product_catalog.validate_product_payload({**VALID_FRAME, "sale_price": -1})
        self.assertTrue(any("preço de venda" in e.lower() for e in errors))

    def test_lens_requires_technical_fields(self):
        errors = product_catalog.validate_product_payload({
            **VALID_LENS,
            "sphere_power": None,
            "cylinder_power": None,
            "lens_type": "",
        })
        joined = " ".join(errors).lower()
        self.assertIn("esférico", joined)
        self.assertIn("cilíndrico", joined)
        self.assertIn("tipo de lente", joined)

    def test_axis_out_of_range(self):
        errors = product_catalog.validate_product_payload({**VALID_LENS, "axis": 181})
        self.assertTrue(any("eixo" in e.lower() for e in errors))


class TestProductCatalogPayload(unittest.TestCase):
    def test_frame_payload_omits_technical_fields(self):
        payload = product_catalog.build_product_payload({
            **VALID_FRAME,
            "cost_price": 100.0,
            "sphere_power": -2.0,
            "lens_type": "Monofocal",
        })
        self.assertEqual(payload["sku"], "ARM-TEST-01")
        self.assertEqual(payload["cost_price"], 100.0)
        self.assertNotIn("sphere_power", payload)
        self.assertNotIn("lens_type", payload)

    def test_lens_payload_includes_technical_fields(self):
        payload = product_catalog.build_product_payload({
            **VALID_LENS,
            "treatment": " Crizal ",
            "material": " Resina 1.67 ",
        })
        self.assertEqual(payload["sphere_power"], -2.5)
        self.assertEqual(payload["cylinder_power"], -0.75)
        self.assertEqual(payload["axis"], 180)
        self.assertEqual(payload["lens_type"], "Monofocal")
        self.assertEqual(payload["treatment"], "Crizal")
        self.assertEqual(payload["material"], "Resina 1.67")

    def test_blank_optional_fields_are_omitted(self):
        payload = product_catalog.build_product_payload({
            **VALID_LENS,
            "cost_price": None,
            "addition": None,
            "treatment": "",
            "material": "   ",
        })
        for field in ["cost_price", "addition", "treatment", "material"]:
            self.assertNotIn(field, payload)


if __name__ == "__main__":
    unittest.main()
