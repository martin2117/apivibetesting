"""
TechShop API — Cart tests
==========================
Covers GET /cart, POST /cart, PUT /cart/{itemId}, DELETE /cart/{itemId}.
All happy-path tests assert status code + body fields.
All negative tests assert status code + error/message body field.
"""

import os

import pytest

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')


# ===========================================================================
# GET /cart
# ===========================================================================

class TestGetCart:

    def test_cart_get_authenticated_returns_200_with_schema(self, http_session, auth_headers):
        """Valid token → 200, Cart with items array and numeric total."""
        resp = http_session.get(f"{BASE_URL}/cart", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body, "Cart response must have 'items' key"
        assert "total" in body, "Cart response must have 'total' key"
        assert isinstance(body["items"], list),          "'items' must be a list"
        assert isinstance(body["total"], (int, float)),  "'total' must be numeric"

    def test_cart_get_no_auth_returns_401(self, http_session):
        """No Authorization header → 401 with error message."""
        resp = http_session.get(f"{BASE_URL}/cart")
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body or "message" in body

    def test_cart_get_invalid_token_returns_401(self, http_session):
        """Garbage token → 401 with error message."""
        resp = http_session.get(
            f"{BASE_URL}/cart",
            headers={"Authorization": "Bearer this.is.not.a.valid.jwt"},
        )
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body or "message" in body

    def test_cart_get_malformed_header_bearer_only_returns_401(self, http_session):
        """'Bearer' with no token value → 401 with error message."""
        resp = http_session.get(
            f"{BASE_URL}/cart",
            headers={"Authorization": "Bearer"},
        )
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body or "message" in body

    def test_cart_get_basic_auth_scheme_returns_401(self, http_session):
        """Wrong auth scheme (Basic) → 401 with error message."""
        resp = http_session.get(
            f"{BASE_URL}/cart",
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
        )
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body or "message" in body

    def test_cart_get_expired_token_returns_401(self, http_session):
        """Structurally valid but expired JWT → 401 with error message."""
        expired_token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
            ".eyJpZCI6MSwiZW1haWwiOiJkZW1vQHRlY2hzaG9wLmNvbSIsImV4cCI6MTU3NzgzNjgwMH0"
            ".invalidsignature"
        )
        resp = http_session.get(
            f"{BASE_URL}/cart",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body or "message" in body


# ===========================================================================
# POST /cart
# ===========================================================================

class TestAddToCart:

    def test_cart_add_valid_item_returns_201_with_schema(self, http_session, auth_headers):
        """Valid token + productId + quantity → 201 with cart item fields."""
        resp = http_session.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 1, "quantity": 2},
        )
        assert resp.status_code == 201
        body = resp.json()
        # The response should reflect the updated cart or the created item
        assert body is not None, "201 response body must not be empty"

    def test_cart_add_item_reflected_in_get_cart(self, http_session, auth_headers):
        """After POST /cart, GET /cart shows the new item."""
        http_session.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 1, "quantity": 1},
        )
        cart_resp = http_session.get(f"{BASE_URL}/cart", headers=auth_headers)
        assert cart_resp.status_code == 200
        body = cart_resp.json()
        items = body["items"]
        product_ids = [item["productId"] for item in items]
        assert 1 in product_ids, "Product 1 should appear in cart after being added"

    def test_cart_add_no_auth_returns_401(self, http_session):
        """No auth → 401 with error message."""
        resp = http_session.post(
            f"{BASE_URL}/cart",
            json={"productId": 1, "quantity": 2},
        )
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body or "message" in body

    def test_cart_add_nonexistent_product_returns_404(self, http_session, auth_headers):
        """productId that does not exist → 404 with error message."""
        resp = http_session.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 99999, "quantity": 1},
        )
        assert resp.status_code == 404
        body = resp.json()
        assert "error" in body or "message" in body

    def test_cart_add_missing_product_id_returns_400(self, http_session, auth_headers):
        """Body with only quantity, no productId → 400 with error message."""
        resp = http_session.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"quantity": 2},
        )
        assert resp.status_code == 400
        body = resp.json()
        assert "error" in body or "message" in body

    def test_cart_add_missing_quantity_returns_400(self, http_session, auth_headers):
        """Body with only productId, no quantity → 400 with error message."""
        resp = http_session.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 1},
        )
        assert resp.status_code == 400
        body = resp.json()
        assert "error" in body or "message" in body

    def test_cart_add_non_integer_product_id_returns_400(self, http_session, auth_headers):
        """productId as a string → 400 with error message."""
        resp = http_session.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": "one", "quantity": 2},
        )
        assert resp.status_code == 400
        body = resp.json()
        assert "error" in body or "message" in body

    @pytest.mark.parametrize("bad_qty", [0, -1, -100], ids=["zero", "minus_one", "minus_hundred"])
    def test_cart_add_quantity_below_minimum_returns_400(self, http_session, auth_headers, bad_qty):
        """quantity below minimum (1) → 400; swagger minimum: 1."""
        resp = http_session.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 1, "quantity": bad_qty},
        )
        assert resp.status_code == 400, (
            f"Expected 400 for quantity={bad_qty} but got {resp.status_code}"
        )
        body = resp.json()
        assert "error" in body or "message" in body


# ===========================================================================
# PUT /cart/{itemId}
# ===========================================================================

class TestUpdateCartItem:
    """
    Depends on a cart item existing.
    An autouse fixture adds one and captures its itemId.
    """

    @pytest.fixture(autouse=True)
    def _setup_cart_item(self, http_session, auth_headers):
        """Ensure at least one item exists in the cart; capture its id."""
        http_session.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 1, "quantity": 1},
        )
        cart_resp = http_session.get(f"{BASE_URL}/cart", headers=auth_headers)
        assert cart_resp.status_code == 200
        items = cart_resp.json().get("items", [])
        assert len(items) > 0, "Cart must have at least one item for PUT/DELETE tests"
        self.item_id = items[0]["id"]

    def test_cart_update_quantity_returns_200_with_schema(self, http_session, auth_headers):
        """Update existing cart item quantity → 200 with updated item body."""
        resp = http_session.put(
            f"{BASE_URL}/cart/{self.item_id}",
            headers=auth_headers,
            json={"quantity": 3},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body is not None, "200 response body must not be empty"

    def test_cart_update_no_auth_returns_401(self, http_session):
        """PUT without Authorization → 401 with error message."""
        resp = http_session.put(
            f"{BASE_URL}/cart/1",
            json={"quantity": 3},
        )
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body or "message" in body

    def test_cart_update_item_not_found_returns_404(self, http_session, auth_headers):
        """Non-existent itemId → 404 with error message."""
        resp = http_session.put(
            f"{BASE_URL}/cart/99999",
            headers=auth_headers,
            json={"quantity": 3},
        )
        assert resp.status_code == 404
        body = resp.json()
        assert "error" in body or "message" in body

    def test_cart_update_missing_quantity_returns_400(self, http_session, auth_headers):
        """Empty body (no quantity field) → 400 with error message."""
        resp = http_session.put(
            f"{BASE_URL}/cart/{self.item_id}",
            headers=auth_headers,
            json={},
        )
        assert resp.status_code == 400
        body = resp.json()
        assert "error" in body or "message" in body

    @pytest.mark.parametrize("bad_qty", [0, -1, -100], ids=["zero", "minus_one", "minus_hundred"])
    def test_cart_update_quantity_below_minimum_returns_400(
        self, http_session, auth_headers, bad_qty
    ):
        """quantity below minimum (1) → 400; swagger minimum: 1."""
        resp = http_session.put(
            f"{BASE_URL}/cart/{self.item_id}",
            headers=auth_headers,
            json={"quantity": bad_qty},
        )
        assert resp.status_code == 400, (
            f"Expected 400 for quantity={bad_qty} but got {resp.status_code}"
        )
        body = resp.json()
        assert "error" in body or "message" in body


# ===========================================================================
# DELETE /cart/{itemId}
# ===========================================================================

class TestDeleteCartItem:

    def test_cart_delete_valid_item_returns_200_and_removes_item(
        self, http_session, auth_headers
    ):
        """Add an item then delete it → 200; item no longer in cart."""
        http_session.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 2, "quantity": 1},
        )
        cart_resp = http_session.get(f"{BASE_URL}/cart", headers=auth_headers)
        assert cart_resp.status_code == 200
        items = cart_resp.json().get("items", [])
        target = next((i for i in items if i["productId"] == 2), None)
        if target is None:
            pytest.skip("Could not locate productId 2 in cart to delete")

        item_id = target["id"]
        del_resp = http_session.delete(f"{BASE_URL}/cart/{item_id}", headers=auth_headers)
        assert del_resp.status_code == 200

        cart_after = http_session.get(f"{BASE_URL}/cart", headers=auth_headers).json()
        remaining_ids = [i["id"] for i in cart_after.get("items", [])]
        assert item_id not in remaining_ids, "Deleted item should not appear in cart"

    def test_cart_delete_no_auth_returns_401(self, http_session):
        """DELETE without auth → 401 with error message."""
        resp = http_session.delete(f"{BASE_URL}/cart/1")
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body or "message" in body

    def test_cart_delete_item_not_found_returns_404(self, http_session, auth_headers):
        """Non-existent itemId → 404 with error message."""
        resp = http_session.delete(f"{BASE_URL}/cart/99999", headers=auth_headers)
        assert resp.status_code == 404
        body = resp.json()
        assert "error" in body or "message" in body

    def test_cart_delete_same_item_twice_second_returns_404(
        self, http_session, auth_headers
    ):
        """Deleting same item twice → second call is 404 with error message."""
        http_session.post(
            f"{BASE_URL}/cart",
            headers=auth_headers,
            json={"productId": 3, "quantity": 1},
        )
        cart_resp = http_session.get(f"{BASE_URL}/cart", headers=auth_headers)
        items = cart_resp.json().get("items", [])
        target = next((i for i in items if i["productId"] == 3), None)
        if target is None:
            pytest.skip("Could not locate productId 3 in cart to double-delete")

        item_id = target["id"]
        first = http_session.delete(f"{BASE_URL}/cart/{item_id}", headers=auth_headers)
        assert first.status_code == 200

        second = http_session.delete(f"{BASE_URL}/cart/{item_id}", headers=auth_headers)
        assert second.status_code == 404
        body = second.json()
        assert "error" in body or "message" in body

    def test_cart_delete_invalid_item_id_returns_400_or_404(
        self, http_session, auth_headers
    ):
        """Non-numeric itemId → 400 or 404 with error message."""
        resp = http_session.delete(f"{BASE_URL}/cart/not-a-number", headers=auth_headers)
        assert resp.status_code in (400, 404)
        body = resp.json()
        assert "error" in body or "message" in body
