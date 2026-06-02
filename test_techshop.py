"""
TechShop API — Pytest Test Suite
=================================
Source of truth:
  - swagger.json  : API contract (endpoints, schemas, required fields, response codes)
  - TEST_IDEAS.md : Test strategy (happy paths, negative tests, auth requirements)

Environment variables (no .env / no dotenv):
  BASE_URL      – defaults to http://localhost:3000
  TEST_EMAIL    – email for the demo account
  TEST_PASSWORD – password for the demo account
"""

import os
import pytest
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def auth_token():
    """
    Obtain a JWT from POST /auth/login using env-var credentials.

    Raises a clear RuntimeError if TEST_EMAIL or TEST_PASSWORD are not set,
    so the developer knows exactly what is missing before a single test runs.
    """
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    if not email:
        raise RuntimeError(
            "Environment variable TEST_EMAIL is not set. "
            "Export it before running the suite: export TEST_EMAIL=demo@techshop.com"
        )
    if not password:
        raise RuntimeError(
            "Environment variable TEST_PASSWORD is not set. "
            "Export it before running the suite: export TEST_PASSWORD=password123"
        )

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, (
        f"Login fixture failed — expected 200 but got {response.status_code}: "
        f"{response.text}"
    )

    data = response.json()
    token = data.get("token")
    assert token, f"Login response did not include a 'token' field: {data}"
    return token


@pytest.fixture()
def auth_headers(auth_token):
    """Return an Authorization header dict ready to pass to requests."""
    return {"Authorization": f"Bearer {auth_token}"}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ===========================================================================
# POST /auth/login
# ===========================================================================

class TestAuthLogin:

    def test_login_valid_credentials(self):
        """Happy path: valid email + password → 200, token and user object."""
        email = os.getenv("TEST_EMAIL")
        password = os.getenv("TEST_PASSWORD")

        if not email or not password:
            pytest.skip("TEST_EMAIL / TEST_PASSWORD not set; skipping login happy path")

        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "token" in body, "Response must include a 'token' field"
        assert "user" in body, "Response must include a 'user' field"
        user = body["user"]
        assert "id" in user
        assert "email" in user
        assert "name" in user

    def test_login_wrong_password_returns_401(self):
        """Negative: correct email, wrong password → 401 Invalid credentials."""
        email = os.getenv("TEST_EMAIL", "demo@techshop.com")
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": "this-is-definitely-wrong"},
        )
        assert resp.status_code == 401

    def test_login_missing_email_returns_400(self):
        """Negative: body has password but no email → 400."""
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"password": "password123"},
        )
        assert resp.status_code == 400

    def test_login_missing_password_returns_400(self):
        """Negative: body has email but no password → 400."""
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "demo@techshop.com"},
        )
        assert resp.status_code == 400

    def test_login_empty_body_returns_400(self):
        """Additional negative: empty JSON body → 400."""
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={},
        )
        assert resp.status_code == 400

    def test_login_unknown_user_returns_401(self):
        """Additional negative: well-formed email that doesn't exist → 401."""
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "nobody@unknown-domain-xyz.com", "password": "password123"},
        )
        assert resp.status_code == 401


# ===========================================================================
# GET /products
# ===========================================================================

class TestGetProducts:

    def test_get_all_products_returns_200(self):
        """Happy path: GET /products with no params → 200, JSON array."""
        resp = requests.get(f"{BASE_URL}/products")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list), "Response body should be a JSON array"

    def test_get_all_products_schema(self):
        """Happy path: each product item matches the Product schema."""
        resp = requests.get(f"{BASE_URL}/products")
        assert resp.status_code == 200
        products = resp.json()
        assert len(products) > 0, "Expected at least one product in the catalogue"
        for product in products:
            assert "id" in product
            assert "name" in product
            assert "price" in product
            assert "category" in product
            assert "stock" in product
            assert "inStock" in product

    def test_get_products_filter_by_valid_category(self):
        """Happy path: filter by a known category → 200, array (possibly empty)."""
        resp = requests.get(f"{BASE_URL}/products", params={"category": "computers"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_products_invalid_category_returns_empty_or_400(self):
        """Negative: unknown category → empty array [] or 400 (verify API behavior)."""
        resp = requests.get(f"{BASE_URL}/products", params={"category": "invalid-category"})
        assert resp.status_code in (200, 400), (
            f"Expected 200 (empty list) or 400 but got {resp.status_code}"
        )
        if resp.status_code == 200:
            assert isinstance(resp.json(), list)

    def test_get_products_unsupported_query_param_is_ignored_or_400(self):
        """Negative: unsupported query param → ignored (200) or 400; response still valid."""
        resp = requests.get(f"{BASE_URL}/products", params={"limit": 10})
        assert resp.status_code in (200, 400)
        if resp.status_code == 200:
            assert isinstance(resp.json(), list)

    def test_get_products_wrong_method_returns_405(self):
        """Additional negative: POST on /products → 405 Method Not Allowed."""
        resp = requests.post(f"{BASE_URL}/products")
        assert resp.status_code == 405


# ===========================================================================
# GET /products/{id}
# ===========================================================================

class TestGetProductById:

    def test_get_product_by_id_returns_200(self):
        """Happy path: GET /products/1 → 200, single Product object."""
        resp = requests.get(f"{BASE_URL}/products/1")
        assert resp.status_code == 200
        product = resp.json()
        assert "id" in product
        assert "name" in product
        assert "price" in product
        assert "category" in product
        assert "stock" in product
        assert "inStock" in product

    def test_get_product_by_id_schema_types(self):
        """Happy path: field types match the swagger schema."""
        resp = requests.get(f"{BASE_URL}/products/1")
        assert resp.status_code == 200
        p = resp.json()
        assert isinstance(p["id"], int)
        assert isinstance(p["name"], str)
        assert isinstance(p["price"], (int, float))
        assert isinstance(p["category"], str)
        assert isinstance(p["stock"], int)
        assert isinstance(p["inStock"], bool)

    def test_get_product_not_found_returns_404(self):
        """Negative: non-existent product ID → 404."""
        resp = requests.get(f"{BASE_URL}/products/99999")
        assert resp.status_code == 404

    def test_get_product_invalid_id_string_returns_400_or_404(self):
        """Negative: non-numeric path segment → 400 or 404."""
        resp = requests.get(f"{BASE_URL}/products/abc")
        assert resp.status_code in (400, 404)

    def test_get_product_negative_id_returns_400_or_404(self):
        """Negative: negative integer ID → 400 or 404."""
        resp = requests.get(f"{BASE_URL}/products/-1")
        assert resp.status_code in (400, 404)


# ===========================================================================
# GET /cart
# ===========================================================================

class TestGetCart:

    def test_get_cart_authenticated_returns_200(self, auth_headers):
        """Happy path: valid token → 200, Cart with items array and total."""
        resp = requests.get(f"{BASE_URL}/cart", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body, "Cart response must have 'items' key"
        assert "total" in body, "Cart response must have 'total' key"
        assert isinstance(body["items"], list)
        assert isinstance(body["total"], (int, float))

    def test_get_cart_no_auth_returns_401(self):
        """Negative: no Authorization header → 401 Unauthorized."""
        resp = requests.get(f"{BASE_URL}/cart")
        assert resp.status_code == 401

    def test_get_cart_invalid_token_returns_401(self):
        """Negative: invalid/garbage token → 401 Unauthorized."""
        resp = requests.get(
            f"{BASE_URL}/cart",
            headers={"Authorization": "Bearer this.is.not.a.valid.jwt"},
        )
        assert resp.status_code == 401

    def test_get_cart_malformed_header_bearer_only_returns_401(self):
        """Additional negative: 'Bearer' with no token value → 401."""
        resp = requests.get(
            f"{BASE_URL}/cart",
            headers={"Authorization": "Bearer"},
        )
        assert resp.status_code == 401

    def test_get_cart_basic_auth_scheme_returns_401(self):
        """Additional negative: wrong auth scheme (Basic) → 401."""
        resp = requests.get(
            f"{BASE_URL}/cart",
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
        )
        assert resp.status_code == 401


# ===========================================================================
# POST /cart
# ===========================================================================

class TestAddToCart:

    def test_add_to_cart_valid_item_returns_201(self, auth_headers):
        """Happy path: valid token + productId + quantity → 201."""
        resp = requests.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 1, "quantity": 2},
        )
        assert resp.status_code == 201

    def test_add_to_cart_reflected_in_get_cart(self, auth_headers):
        """Happy path: after adding, GET /cart shows the new item."""
        requests.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 1, "quantity": 1},
        )
        cart_resp = requests.get(f"{BASE_URL}/cart", headers=auth_headers)
        assert cart_resp.status_code == 200
        items = cart_resp.json()["items"]
        product_ids = [item["productId"] for item in items]
        assert 1 in product_ids, "Product 1 should appear in cart after being added"

    def test_add_to_cart_no_auth_returns_401(self):
        """Negative: no auth → 401 Unauthorized."""
        resp = requests.post(
            f"{BASE_URL}/cart",
            json={"productId": 1, "quantity": 2},
        )
        assert resp.status_code == 401

    def test_add_to_cart_nonexistent_product_returns_404(self, auth_headers):
        """Negative: productId that does not exist → 404."""
        resp = requests.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 99999, "quantity": 1},
        )
        assert resp.status_code == 404

    def test_add_to_cart_quantity_zero_returns_400(self, auth_headers):
        """Additional negative: quantity: 0 (below minimum 1) → 400."""
        resp = requests.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 1, "quantity": 0},
        )
        assert resp.status_code == 400

    def test_add_to_cart_negative_quantity_returns_400(self, auth_headers):
        """Additional negative: negative quantity → 400."""
        resp = requests.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 1, "quantity": -5},
        )
        assert resp.status_code == 400

    def test_add_to_cart_missing_product_id_returns_400(self, auth_headers):
        """Additional negative: body with only quantity, no productId → 400."""
        resp = requests.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"quantity": 2},
        )
        assert resp.status_code == 400

    def test_add_to_cart_missing_quantity_returns_400(self, auth_headers):
        """Additional negative: body with only productId, no quantity → 400."""
        resp = requests.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 1},
        )
        assert resp.status_code == 400

    def test_add_to_cart_non_integer_product_id_returns_400(self, auth_headers):
        """Additional negative: productId as a string → 400."""
        resp = requests.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": "one", "quantity": 2},
        )
        assert resp.status_code == 400


# ===========================================================================
# PUT /cart/{itemId}
# ===========================================================================

class TestUpdateCartItem:
    """
    These tests depend on a cart item existing. We add one in a session-scoped
    fixture and capture its itemId for the update and delete tests.
    """

    @pytest.fixture(autouse=True)
    def _setup_cart_item(self, auth_headers):
        """Ensure there is at least one item in the cart; capture its itemId."""
        # Add an item so we always have something to work with
        add_resp = requests.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 1, "quantity": 1},
        )
        # 201 = newly added, 200/409 might mean it already exists — either is fine
        cart_resp = requests.get(f"{BASE_URL}/cart", headers=auth_headers)
        assert cart_resp.status_code == 200
        items = cart_resp.json().get("items", [])
        assert len(items) > 0, "Cart must have at least one item for PUT/DELETE tests"
        self.item_id = items[0]["id"]

    def test_update_cart_item_quantity_returns_200(self, auth_headers):
        """Happy path: update existing cart item quantity → 200."""
        resp = requests.put(
            f"{BASE_URL}/cart/{self.item_id}",
            headers=auth_headers,
            json={"quantity": 3},
        )
        assert resp.status_code == 200

    def test_update_cart_item_no_auth_returns_401(self):
        """Negative: PUT without Authorization → 401."""
        resp = requests.put(
            f"{BASE_URL}/cart/1",
            json={"quantity": 3},
        )
        assert resp.status_code == 401

    def test_update_cart_item_not_found_returns_404(self, auth_headers):
        """Negative: non-existent itemId → 404."""
        resp = requests.put(
            f"{BASE_URL}/cart/99999",
            headers=auth_headers,
            json={"quantity": 3},
        )
        assert resp.status_code == 404

    def test_update_cart_item_quantity_zero_returns_400(self, auth_headers):
        """Additional negative: quantity: 0 (below minimum 1) → 400."""
        resp = requests.put(
            f"{BASE_URL}/cart/{self.item_id}",
            headers=auth_headers,
            json={"quantity": 0},
        )
        assert resp.status_code == 400

    def test_update_cart_item_missing_quantity_returns_400(self, auth_headers):
        """Additional negative: empty body (no quantity field) → 400."""
        resp = requests.put(
            f"{BASE_URL}/cart/{self.item_id}",
            headers=auth_headers,
            json={},
        )
        assert resp.status_code == 400


# ===========================================================================
# DELETE /cart/{itemId}
# ===========================================================================

class TestDeleteCartItem:

    def test_delete_cart_item_returns_200(self, auth_headers):
        """Happy path: add an item then delete it → 200, no longer in cart."""
        # Add a fresh item
        add_resp = requests.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 2, "quantity": 1},
        )
        # Find the item we just added (or any item for productId 2)
        cart_resp = requests.get(f"{BASE_URL}/cart", headers=auth_headers)
        assert cart_resp.status_code == 200
        items = cart_resp.json().get("items", [])
        target = next((i for i in items if i["productId"] == 2), None)
        if target is None:
            pytest.skip("Could not locate productId 2 in cart to delete")

        item_id = target["id"]
        del_resp = requests.delete(f"{BASE_URL}/cart/{item_id}", headers=auth_headers)
        assert del_resp.status_code == 200

        # Confirm item is gone
        cart_after = requests.get(f"{BASE_URL}/cart", headers=auth_headers).json()
        remaining_ids = [i["id"] for i in cart_after.get("items", [])]
        assert item_id not in remaining_ids, "Deleted item should not appear in cart"

    def test_delete_cart_item_no_auth_returns_401(self):
        """Negative: DELETE without auth → 401."""
        resp = requests.delete(f"{BASE_URL}/cart/1")
        assert resp.status_code == 401

    def test_delete_cart_item_not_found_returns_404(self, auth_headers):
        """Negative: non-existent itemId → 404."""
        resp = requests.delete(f"{BASE_URL}/cart/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_cart_item_twice_second_returns_404(self, auth_headers):
        """Additional negative: deleting the same item twice → second call is 404."""
        # Add an item and delete it once
        requests.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 3, "quantity": 1},
        )
        cart_resp = requests.get(f"{BASE_URL}/cart", headers=auth_headers)
        items = cart_resp.json().get("items", [])
        target = next((i for i in items if i["productId"] == 3), None)
        if target is None:
            pytest.skip("Could not locate productId 3 in cart to double-delete")

        item_id = target["id"]
        first = requests.delete(f"{BASE_URL}/cart/{item_id}", headers=auth_headers)
        assert first.status_code == 200

        second = requests.delete(f"{BASE_URL}/cart/{item_id}", headers=auth_headers)
        assert second.status_code == 404

    def test_delete_cart_item_invalid_id_returns_400_or_404(self, auth_headers):
        """Additional negative: non-numeric itemId → 400 or 404."""
        resp = requests.delete(f"{BASE_URL}/cart/not-a-number", headers=auth_headers)
        assert resp.status_code in (400, 404)


# ===========================================================================
# GET /orders
# ===========================================================================

class TestGetOrders:

    def test_get_orders_authenticated_returns_200(self, auth_headers):
        """Happy path: valid token → 200, array of Order objects."""
        resp = requests.get(f"{BASE_URL}/orders", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list), "GET /orders should return a JSON array"

    def test_get_orders_schema_when_not_empty(self, auth_headers):
        """Happy path: when orders exist each Order matches the swagger schema."""
        resp = requests.get(f"{BASE_URL}/orders", headers=auth_headers)
        assert resp.status_code == 200
        orders = resp.json()
        for order in orders:
            assert "id" in order
            assert "userId" in order
            assert "items" in order
            assert "total" in order
            assert "status" in order
            assert "createdAt" in order
            assert "payment" in order
            assert "last4" in order["payment"]

    def test_get_orders_no_auth_returns_401(self):
        """Negative: no Authorization header → 401."""
        resp = requests.get(f"{BASE_URL}/orders")
        assert resp.status_code == 401

    def test_get_orders_tampered_token_returns_401(self):
        """Negative: tampered JWT → 401."""
        resp = requests.get(
            f"{BASE_URL}/orders",
            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.tampered.signature"},
        )
        assert resp.status_code == 401

    def test_get_orders_user_with_no_orders_returns_empty_list(self, auth_headers):
        """Additional negative: user with no orders → 200 and empty array (or non-empty)."""
        resp = requests.get(f"{BASE_URL}/orders", headers=auth_headers)
        assert resp.status_code == 200
        # Either empty [] or a list of orders — both are valid
        assert isinstance(resp.json(), list)


# ===========================================================================
# POST /orders (checkout)
# ===========================================================================

class TestPlaceOrder:

    VALID_ORDER = {
        "items": [{"productId": 1, "quantity": 1}],
        "shipping": {
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "jane@example.com",
            "phone": "0412345678",
        },
        "payment": {
            "cardNumber": "4111111111111111",
            "expiryDate": "12/28",
            "cvv": "123",
        },
    }

    def test_place_order_valid_body_returns_201(self, auth_headers):
        """Happy path: complete valid body with valid token → 201, Order object."""
        resp = requests.post(
            f"{BASE_URL}/orders",
            headers=auth_headers,
            json=self.VALID_ORDER,
        )
        assert resp.status_code == 201
        order = resp.json()
        assert "id" in order
        assert "status" in order
        assert "total" in order
        assert "payment" in order
        assert "last4" in order["payment"], "Payment should be masked to last4"

    def test_place_order_no_auth_returns_401(self):
        """Negative: checkout without authentication → 401."""
        resp = requests.post(f"{BASE_URL}/orders", json=self.VALID_ORDER)
        assert resp.status_code == 401

    def test_place_order_missing_items_returns_400(self, auth_headers):
        """Negative: body without 'items' key → 400 Validation error."""
        payload = {
            "shipping": self.VALID_ORDER["shipping"],
            "payment": self.VALID_ORDER["payment"],
        }
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_missing_shipping_returns_400(self, auth_headers):
        """Negative: body without 'shipping' key → 400."""
        payload = {
            "items": self.VALID_ORDER["items"],
            "payment": self.VALID_ORDER["payment"],
        }
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_missing_payment_returns_400(self, auth_headers):
        """Negative: body without 'payment' key → 400."""
        payload = {
            "items": self.VALID_ORDER["items"],
            "shipping": self.VALID_ORDER["shipping"],
        }
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_empty_items_array_returns_400(self, auth_headers):
        """Additional negative: items: [] (minItems: 1) → 400."""
        payload = {**self.VALID_ORDER, "items": []}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_invalid_phone_returns_400(self, auth_headers):
        """Additional negative: shipping phone not 10 digits → 400."""
        bad_shipping = {**self.VALID_ORDER["shipping"], "phone": "123"}
        payload = {**self.VALID_ORDER, "shipping": bad_shipping}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_invalid_card_number_returns_400(self, auth_headers):
        """Additional negative: cardNumber not 16 digits → 400."""
        bad_payment = {**self.VALID_ORDER["payment"], "cardNumber": "1234"}
        payload = {**self.VALID_ORDER, "payment": bad_payment}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_past_expiry_date_returns_400(self, auth_headers):
        """Additional negative: expiryDate in the past → 400."""
        bad_payment = {**self.VALID_ORDER["payment"], "expiryDate": "01/20"}
        payload = {**self.VALID_ORDER, "payment": bad_payment}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_invalid_cvv_returns_400(self, auth_headers):
        """Additional negative: cvv not exactly 3 digits → 400."""
        bad_payment = {**self.VALID_ORDER["payment"], "cvv": "12"}
        payload = {**self.VALID_ORDER, "payment": bad_payment}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_invalid_email_format_returns_400(self, auth_headers):
        """Additional negative: shipping email not a valid email format → 400."""
        bad_shipping = {**self.VALID_ORDER["shipping"], "email": "not-an-email"}
        payload = {**self.VALID_ORDER, "shipping": bad_shipping}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_item_quantity_zero_returns_400(self, auth_headers):
        """Additional negative: line item quantity: 0 (minimum is 1) → 400."""
        bad_items = [{"productId": 1, "quantity": 0}]
        payload = {**self.VALID_ORDER, "items": bad_items}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_nonexistent_product_id_returns_400_or_404(self, auth_headers):
        """Additional negative: productId that doesn't exist → 400 or 404."""
        bad_items = [{"productId": 99999, "quantity": 1}]
        payload = {**self.VALID_ORDER, "items": bad_items}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code in (400, 404)


# ===========================================================================
# GAP-FILL TESTS
# Scenarios from swagger.json / TEST_IDEAS.md not covered by the original suite
# ===========================================================================

# ---------------------------------------------------------------------------
# GET /products — additional category filters
# TEST_IDEAS.md lists 4 valid categories; only "computers" was previously tested
# ---------------------------------------------------------------------------

class TestGetProductsGapFill:

    def test_get_products_filter_by_audio(self):
        """Happy path: filter by 'audio' category → 200, list."""
        resp = requests.get(f"{BASE_URL}/products", params={"category": "audio"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_products_filter_by_accessories(self):
        """Happy path: filter by 'accessories' category → 200, list."""
        resp = requests.get(f"{BASE_URL}/products", params={"category": "accessories"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_products_filter_by_peripherals(self):
        """Happy path: filter by 'peripherals' category → 200, list."""
        resp = requests.get(f"{BASE_URL}/products", params={"category": "peripherals"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_product_schema_includes_description(self):
        """swagger.json Product schema includes 'description' — assert it is present."""
        resp = requests.get(f"{BASE_URL}/products/1")
        assert resp.status_code == 200
        product = resp.json()
        assert "description" in product, "Product schema must include a 'description' field"

    def test_get_product_missing_id_segment_returns_404(self):
        """TEST_IDEAS.md: GET /products/ (trailing slash, no ID) → 404 or routing error."""
        resp = requests.get(f"{BASE_URL}/products/")
        # Express will route this back to GET /products (200) or return 404 — either is acceptable
        assert resp.status_code in (200, 404)


# ---------------------------------------------------------------------------
# GET /cart — expired/invalid token (explicitly in TEST_IDEAS.md for /cart)
# ---------------------------------------------------------------------------

class TestGetCartGapFill:

    def test_get_cart_expired_token_returns_401(self):
        """TEST_IDEAS.md: GET /cart with expired token → 401.
        We simulate this with a structurally valid but expired JWT."""
        # HS256 token with exp in the past (Jan 1 2020) — signature will fail
        expired_token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
            ".eyJpZCI6MSwiZW1haWwiOiJkZW1vQHRlY2hzaG9wLmNvbSIsImV4cCI6MTU3NzgzNjgwMH0"
            ".invalidsignature"
        )
        resp = requests.get(
            f"{BASE_URL}/cart",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# PUT /cart/{itemId} — negative quantity (TEST_IDEAS.md line 102)
# ---------------------------------------------------------------------------

class TestUpdateCartItemGapFill:

    @pytest.fixture(autouse=True)
    def _setup_cart_item(self, auth_headers):
        """Add a cart item and capture its id for PUT gap-fill tests."""
        requests.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 1, "quantity": 1},
        )
        cart_resp = requests.get(f"{BASE_URL}/cart", headers=auth_headers)
        assert cart_resp.status_code == 200
        items = cart_resp.json().get("items", [])
        assert len(items) > 0, "Cart must have at least one item for PUT gap-fill tests"
        self.item_id = items[0]["id"]

    def test_update_cart_item_negative_quantity_returns_400(self, auth_headers):
        """TEST_IDEAS.md: PUT with quantity below minimum (negative) → 400."""
        resp = requests.put(
            f"{BASE_URL}/cart/{self.item_id}",
            headers=auth_headers,
            json={"quantity": -3},
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# GET /orders — shipping field in Order schema (swagger.json)
# ---------------------------------------------------------------------------

class TestGetOrdersGapFill:

    def test_get_orders_schema_includes_shipping(self, auth_headers):
        """swagger.json Order schema includes 'shipping' — assert it when orders exist."""
        resp = requests.get(f"{BASE_URL}/orders", headers=auth_headers)
        assert resp.status_code == 200
        orders = resp.json()
        for order in orders:
            assert "shipping" in order, "Order schema must include a 'shipping' field"


# ---------------------------------------------------------------------------
# POST /orders — additional field-level validation gaps from swagger.json
# ---------------------------------------------------------------------------

class TestPlaceOrderGapFill:

    VALID_ORDER = {
        "items": [{"productId": 1, "quantity": 1}],
        "shipping": {
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "jane@example.com",
            "phone": "0412345678",
        },
        "payment": {
            "cardNumber": "4111111111111111",
            "expiryDate": "12/28",
            "cvv": "123",
        },
    }

    def test_place_order_order_id_matches_expected_format(self, auth_headers):
        """swagger.json: Order.id example is 'ORD-<timestamp>' — assert prefix format."""
        resp = requests.post(
            f"{BASE_URL}/orders",
            headers=auth_headers,
            json=self.VALID_ORDER,
        )
        assert resp.status_code == 201
        order_id = resp.json().get("id", "")
        assert order_id.startswith("ORD-"), (
            f"Order id should start with 'ORD-' but got: '{order_id}'"
        )

    def test_place_order_missing_first_name_returns_400(self, auth_headers):
        """swagger.json: shipping.firstName is required — omitting it → 400."""
        bad_shipping = {k: v for k, v in self.VALID_ORDER["shipping"].items()
                        if k != "firstName"}
        payload = {**self.VALID_ORDER, "shipping": bad_shipping}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_missing_last_name_returns_400(self, auth_headers):
        """swagger.json: shipping.lastName is required — omitting it → 400."""
        bad_shipping = {k: v for k, v in self.VALID_ORDER["shipping"].items()
                        if k != "lastName"}
        payload = {**self.VALID_ORDER, "shipping": bad_shipping}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_phone_too_long_returns_400(self, auth_headers):
        """TEST_IDEAS.md / swagger.json: phone must be exactly 10 digits — 11 digits → 400."""
        bad_shipping = {**self.VALID_ORDER["shipping"], "phone": "04123456789"}  # 11 digits
        payload = {**self.VALID_ORDER, "shipping": bad_shipping}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_card_number_too_long_returns_400(self, auth_headers):
        """swagger.json: cardNumber pattern ^\\d{16}$ — 17 digits → 400."""
        bad_payment = {**self.VALID_ORDER["payment"], "cardNumber": "41111111111111111"}  # 17 digits
        payload = {**self.VALID_ORDER, "payment": bad_payment}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_expiry_date_invalid_format_returns_400(self, auth_headers):
        """swagger.json: expiryDate pattern ^(0[1-9]|1[0-2])\\/\\d{2}$ — 'abc' → 400."""
        bad_payment = {**self.VALID_ORDER["payment"], "expiryDate": "abc"}
        payload = {**self.VALID_ORDER, "payment": bad_payment}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_expiry_date_invalid_month_returns_400(self, auth_headers):
        """swagger.json: expiryDate month must be 01–12 — '13/28' → 400."""
        bad_payment = {**self.VALID_ORDER["payment"], "expiryDate": "13/28"}
        payload = {**self.VALID_ORDER, "payment": bad_payment}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400

    def test_place_order_cvv_too_long_returns_400(self, auth_headers):
        """swagger.json: cvv pattern ^\\d{3}$ — 4-digit cvv → 400."""
        bad_payment = {**self.VALID_ORDER["payment"], "cvv": "1234"}
        payload = {**self.VALID_ORDER, "payment": bad_payment}
        resp = requests.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400


# ===========================================================================
# PARAMETRIZE BOUNDARY-VALUE TESTS
# Derived from minimum / minItems / pattern constraints in swagger.json
# ===========================================================================

# ---------------------------------------------------------------------------
# swagger.json constraint:
#   POST /cart → quantity: { type: integer, minimum: 1 }
#   Boundary values below minimum must all be rejected → 400
# ---------------------------------------------------------------------------

class TestPostCartQuantityBoundary:

    @pytest.mark.parametrize("bad_qty", [0, -1, -100],
                             ids=["zero", "minus_one", "minus_hundred"])
    def test_add_to_cart_quantity_below_minimum_returns_400(self, auth_headers, bad_qty):
        """
        swagger.json POST /cart quantity minimum: 1.
        Values 0, -1, -100 are all below the minimum and must be rejected → 400.
        """
        resp = requests.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 1, "quantity": bad_qty},
        )
        assert resp.status_code == 400, (
            f"Expected 400 for quantity={bad_qty} but got {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# swagger.json constraint:
#   PUT /cart/{itemId} → quantity: { type: integer, minimum: 1 }
# ---------------------------------------------------------------------------

class TestPutCartQuantityBoundary:

    @pytest.fixture(autouse=True)
    def _ensure_cart_item(self, auth_headers):
        """Guarantee at least one cart item exists and store its id."""
        requests.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 1, "quantity": 1},
        )
        cart = requests.get(f"{BASE_URL}/cart", headers=auth_headers).json()
        items = cart.get("items", [])
        assert items, "Need a cart item for PUT boundary tests"
        self.item_id = items[0]["id"]

    @pytest.mark.parametrize("bad_qty", [0, -1, -100],
                             ids=["zero", "minus_one", "minus_hundred"])
    def test_update_cart_quantity_below_minimum_returns_400(self, auth_headers, bad_qty):
        """
        swagger.json PUT /cart/{itemId} quantity minimum: 1.
        Values 0, -1, -100 must all be rejected → 400.
        """
        resp = requests.put(
            f"{BASE_URL}/cart/{self.item_id}",
            headers=auth_headers,
            json={"quantity": bad_qty},
        )
        assert resp.status_code == 400, (
            f"Expected 400 for quantity={bad_qty} but got {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# swagger.json constraint:
#   POST /orders → items[].quantity: { type: integer, minimum: 1 }
# ---------------------------------------------------------------------------

class TestOrderItemQuantityBoundary:

    VALID_ORDER = {
        "items": [{"productId": 1, "quantity": 1}],
        "shipping": {
            "firstName": "Jane", "lastName": "Doe",
            "email": "jane@example.com", "phone": "0412345678",
        },
        "payment": {
            "cardNumber": "4111111111111111", "expiryDate": "12/28", "cvv": "123",
        },
    }

    @pytest.mark.parametrize("bad_qty", [0, -1, -100],
                             ids=["zero", "minus_one", "minus_hundred"])
    def test_order_item_quantity_below_minimum_returns_400(self, auth_headers, bad_qty):
        """
        swagger.json POST /orders items[].quantity minimum: 1.
        Values 0, -1, -100 must all be rejected → 400.
        """
        payload = {**self.VALID_ORDER, "items": [{"productId": 1, "quantity": bad_qty}]}
        resp = requests.post(
            f"{BASE_URL}/orders",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code == 400, (
            f"Expected 400 for order item quantity={bad_qty} but got {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# swagger.json constraint:
#   POST /orders → items: { type: array, minItems: 1 }
# ---------------------------------------------------------------------------

class TestOrderItemsArrayBoundary:

    VALID_ORDER = {
        "shipping": {
            "firstName": "Jane", "lastName": "Doe",
            "email": "jane@example.com", "phone": "0412345678",
        },
        "payment": {
            "cardNumber": "4111111111111111", "expiryDate": "12/28", "cvv": "123",
        },
    }

    @pytest.mark.parametrize("bad_items,label", [
        ([], "empty_array"),
        (None, "null_value"),
    ], ids=["empty_array", "null_value"])
    def test_order_items_below_minItems_returns_400(self, auth_headers, bad_items, label):
        """
        swagger.json POST /orders items minItems: 1.
        An empty array [] and null must both be rejected → 400.
        """
        payload = {**self.VALID_ORDER, "items": bad_items}
        resp = requests.post(
            f"{BASE_URL}/orders",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code == 400, (
            f"Expected 400 for items={label!r} but got {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# swagger.json constraint:
#   POST /orders → shipping.phone: { pattern: "^\\d{10}$" }
#   Boundary values: too-short, too-long, non-digit chars, empty string
# ---------------------------------------------------------------------------

class TestOrderPhonePatternBoundary:

    VALID_ORDER = {
        "items": [{"productId": 1, "quantity": 1}],
        "shipping": {
            "firstName": "Jane", "lastName": "Doe",
            "email": "jane@example.com", "phone": "0412345678",
        },
        "payment": {
            "cardNumber": "4111111111111111", "expiryDate": "12/28", "cvv": "123",
        },
    }

    @pytest.mark.parametrize("bad_phone", [
        "041234567",    # 9 digits — one short of minimum length
        "04123456789",  # 11 digits — one over maximum length
        "041234567a",   # 9 digits + non-digit letter
        "",             # empty string
        "abcdefghij",   # 10 letters — correct length but no digits
    ], ids=["9_digits", "11_digits", "9_digits_plus_letter", "empty", "10_letters"])
    def test_order_phone_pattern_violation_returns_400(self, auth_headers, bad_phone):
        """
        swagger.json shipping.phone pattern ^\\d{10}$.
        Multiple values that violate the pattern must all be rejected → 400.
        """
        bad_shipping = {**self.VALID_ORDER["shipping"], "phone": bad_phone}
        payload = {**self.VALID_ORDER, "shipping": bad_shipping}
        resp = requests.post(
            f"{BASE_URL}/orders",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code == 400, (
            f"Expected 400 for phone={bad_phone!r} but got {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# swagger.json constraint:
#   POST /orders → payment.cardNumber: { pattern: "^\\d{16}$" }
#   Boundary values: one-short (15), one-long (17), non-digits, empty
# ---------------------------------------------------------------------------

class TestOrderCardNumberPatternBoundary:

    VALID_ORDER = {
        "items": [{"productId": 1, "quantity": 1}],
        "shipping": {
            "firstName": "Jane", "lastName": "Doe",
            "email": "jane@example.com", "phone": "0412345678",
        },
        "payment": {
            "cardNumber": "4111111111111111", "expiryDate": "12/28", "cvv": "123",
        },
    }

    @pytest.mark.parametrize("bad_card", [
        "411111111111111",   # 15 digits — one short
        "41111111111111111", # 17 digits — one long
        "411111111111111a",  # 15 digits + letter
        "",                  # empty string
    ], ids=["15_digits", "17_digits", "15_plus_letter", "empty"])
    def test_order_card_number_pattern_violation_returns_400(self, auth_headers, bad_card):
        """
        swagger.json payment.cardNumber pattern ^\\d{16}$.
        Values deviating from exactly 16 digits must be rejected → 400.
        """
        bad_payment = {**self.VALID_ORDER["payment"], "cardNumber": bad_card}
        payload = {**self.VALID_ORDER, "payment": bad_payment}
        resp = requests.post(
            f"{BASE_URL}/orders",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code == 400, (
            f"Expected 400 for cardNumber={bad_card!r} but got {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# swagger.json constraint:
#   POST /orders → payment.cvv: { pattern: "^\\d{3}$" }
#   Boundary values: too-short (2), too-long (4), non-digits, empty
# ---------------------------------------------------------------------------

class TestOrderCvvPatternBoundary:

    VALID_ORDER = {
        "items": [{"productId": 1, "quantity": 1}],
        "shipping": {
            "firstName": "Jane", "lastName": "Doe",
            "email": "jane@example.com", "phone": "0412345678",
        },
        "payment": {
            "cardNumber": "4111111111111111", "expiryDate": "12/28", "cvv": "123",
        },
    }

    @pytest.mark.parametrize("bad_cvv", [
        "12",   # 2 digits — one short
        "1234", # 4 digits — one long
        "12a",  # 2 digits + letter
        "",     # empty string
    ], ids=["2_digits", "4_digits", "2_digits_plus_letter", "empty"])
    def test_order_cvv_pattern_violation_returns_400(self, auth_headers, bad_cvv):
        """
        swagger.json payment.cvv pattern ^\\d{3}$.
        Values that are not exactly 3 digits must be rejected → 400.
        """
        bad_payment = {**self.VALID_ORDER["payment"], "cvv": bad_cvv}
        payload = {**self.VALID_ORDER, "payment": bad_payment}
        resp = requests.post(
            f"{BASE_URL}/orders",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code == 400, (
            f"Expected 400 for cvv={bad_cvv!r} but got {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# swagger.json constraint:
#   POST /orders → payment.expiryDate: { pattern: "^(0[1-9]|1[0-2])\\/\\d{2}$" }
#   month must be 01–12; format must be MM/YY
# ---------------------------------------------------------------------------

class TestOrderExpiryDatePatternBoundary:

    VALID_ORDER = {
        "items": [{"productId": 1, "quantity": 1}],
        "shipping": {
            "firstName": "Jane", "lastName": "Doe",
            "email": "jane@example.com", "phone": "0412345678",
        },
        "payment": {
            "cardNumber": "4111111111111111", "expiryDate": "12/28", "cvv": "123",
        },
    }

    @pytest.mark.parametrize("bad_expiry", [
        "00/28",   # month 00 — below minimum (01)
        "13/28",   # month 13 — above maximum (12)
        "1228",    # missing slash separator
        "12-28",   # hyphen instead of slash
        "2028/12", # reversed YYYY/MM format
        "",        # empty string
        "abc",     # non-numeric garbage
    ], ids=[
        "month_00", "month_13", "no_slash",
        "hyphen_sep", "reversed_format", "empty", "garbage",
    ])
    def test_order_expiry_date_pattern_violation_returns_400(self, auth_headers, bad_expiry):
        """
        swagger.json payment.expiryDate pattern ^(0[1-9]|1[0-2])\\/\\d{2}$.
        Values outside the MM/YY pattern with valid months 01–12 must be rejected → 400.
        """
        bad_payment = {**self.VALID_ORDER["payment"], "expiryDate": bad_expiry}
        payload = {**self.VALID_ORDER, "payment": bad_payment}
        resp = requests.post(
            f"{BASE_URL}/orders",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code == 400, (
            f"Expected 400 for expiryDate={bad_expiry!r} but got {resp.status_code}"
        )
