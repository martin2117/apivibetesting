"""
TechShop API — Products tests
==============================
Covers GET /products and GET /products/{id} — happy paths, schema checks,
negative cases, category filtering, and boundary values.
"""

import os

import pytest

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')


# ===========================================================================
# GET /products
# ===========================================================================

class TestGetProducts:

    def test_products_get_all_returns_200_with_array(self, http_session):
        """GET /products with no params → 200, non-empty JSON array."""
        resp = http_session.get(f"{BASE_URL}/products")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list), "Response body should be a JSON array"
        assert len(body) > 0, "Expected at least one product in the catalogue"

    def test_products_get_all_schema_matches_swagger(self, http_session):
        """Every product item contains all fields defined in the swagger schema."""
        resp = http_session.get(f"{BASE_URL}/products")
        assert resp.status_code == 200
        products = resp.json()
        for product in products:
            assert "id" in product,          "Product must have 'id'"
            assert "name" in product,        "Product must have 'name'"
            assert "description" in product, "Product must have 'description'"
            assert "price" in product,       "Product must have 'price'"
            assert "category" in product,    "Product must have 'category'"
            assert "stock" in product,       "Product must have 'stock'"
            assert "inStock" in product,     "Product must have 'inStock'"

    def test_products_filter_by_computers_returns_200(self, http_session):
        """Filter by 'computers' category → 200, list of matching products."""
        resp = http_session.get(f"{BASE_URL}/products", params={"category": "computers"})
        assert resp.status_code == 200
        products = resp.json()
        assert isinstance(products, list)

    def test_products_filter_by_audio_returns_200(self, http_session):
        """Filter by 'audio' category → 200, list."""
        resp = http_session.get(f"{BASE_URL}/products", params={"category": "audio"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_products_filter_by_accessories_returns_200(self, http_session):
        """Filter by 'accessories' category → 200, list."""
        resp = http_session.get(f"{BASE_URL}/products", params={"category": "accessories"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_products_filter_by_peripherals_returns_200(self, http_session):
        """Filter by 'peripherals' category → 200, list."""
        resp = http_session.get(f"{BASE_URL}/products", params={"category": "peripherals"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_products_filter_invalid_category_returns_200_or_400(self, http_session):
        """Unknown category → empty array (200) or 400."""
        resp = http_session.get(f"{BASE_URL}/products", params={"category": "invalid-category"})
        assert resp.status_code in (200, 400), (
            f"Expected 200 (empty list) or 400 but got {resp.status_code}"
        )
        if resp.status_code == 200:
            body = resp.json()
            assert isinstance(body, list), "200 response must still be a list"

    def test_products_unsupported_query_param_ignored_or_400(self, http_session):
        """Unsupported query param → ignored (200) or 400; response body stays valid."""
        resp = http_session.get(f"{BASE_URL}/products", params={"limit": 10})
        assert resp.status_code in (200, 400)
        if resp.status_code == 200:
            assert isinstance(resp.json(), list)

    def test_products_wrong_method_returns_405(self, http_session):
        """POST on /products → 405 Method Not Allowed."""
        resp = http_session.post(f"{BASE_URL}/products")
        assert resp.status_code == 405

    def test_products_missing_id_segment_returns_200_or_404(self, http_session):
        """GET /products/ (trailing slash) → Express routes to /products (200) or 404."""
        resp = http_session.get(f"{BASE_URL}/products/")
        assert resp.status_code in (200, 404)


# ===========================================================================
# GET /products/{id}
# ===========================================================================

class TestGetProductById:

    def test_product_get_by_id_returns_200_with_schema(self, http_session):
        """GET /products/1 → 200, single product with all swagger schema fields."""
        resp = http_session.get(f"{BASE_URL}/products/1")
        assert resp.status_code == 200
        product = resp.json()
        assert "id" in product,          "Product must have 'id'"
        assert "name" in product,        "Product must have 'name'"
        assert "description" in product, "Product must have 'description'"
        assert "price" in product,       "Product must have 'price'"
        assert "category" in product,    "Product must have 'category'"
        assert "stock" in product,       "Product must have 'stock'"
        assert "inStock" in product,     "Product must have 'inStock'"

    def test_product_get_by_id_field_types_match_swagger(self, http_session):
        """Field types on a single product match the swagger schema."""
        resp = http_session.get(f"{BASE_URL}/products/1")
        assert resp.status_code == 200
        p = resp.json()
        assert isinstance(p["id"],       int),        "id must be an integer"
        assert isinstance(p["name"],     str),        "name must be a string"
        assert isinstance(p["price"],    (int, float)), "price must be numeric"
        assert isinstance(p["category"], str),        "category must be a string"
        assert isinstance(p["stock"],    int),        "stock must be an integer"
        assert isinstance(p["inStock"],  bool),       "inStock must be a boolean"

    def test_product_get_not_found_returns_404(self, http_session):
        """Non-existent product ID → 404 with error message."""
        resp = http_session.get(f"{BASE_URL}/products/99999")
        assert resp.status_code == 404
        body = resp.json()
        assert "error" in body or "message" in body, \
            "404 response should include an error or message field"

    def test_product_get_invalid_id_string_returns_400_or_404(self, http_session):
        """Non-numeric path segment → 400 or 404 with error message."""
        resp = http_session.get(f"{BASE_URL}/products/abc")
        assert resp.status_code in (400, 404)
        body = resp.json()
        assert "error" in body or "message" in body, \
            "Error response should include an error or message field"

    def test_product_get_negative_id_returns_400_or_404(self, http_session):
        """Negative integer ID → 400 or 404 with error message."""
        resp = http_session.get(f"{BASE_URL}/products/-1")
        assert resp.status_code in (400, 404)
        body = resp.json()
        assert "error" in body or "message" in body, \
            "Error response should include an error or message field"
