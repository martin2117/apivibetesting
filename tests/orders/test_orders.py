"""
TechShop API — Orders tests
=============================
Covers GET /orders and POST /orders (checkout).
All happy-path tests assert status code + body fields.
All negative tests assert status code + error/message body field.
"""

import os

import pytest

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')


# ---------------------------------------------------------------------------
# Shared valid order payload used across multiple test classes
# ---------------------------------------------------------------------------

_VALID_ORDER = {
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


# ===========================================================================
# GET /orders
# ===========================================================================

class TestGetOrders:

    def test_orders_get_authenticated_returns_200_with_array(
        self, http_session, auth_headers
    ):
        """Valid token → 200, array of Order objects."""
        resp = http_session.get(f"{BASE_URL}/orders", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list), "GET /orders should return a JSON array"

    def test_orders_get_schema_when_not_empty(self, http_session, auth_headers):
        """When orders exist each Order contains all swagger-required fields."""
        # Place an order to guarantee a non-empty response
        http_session.post(
            f"{BASE_URL}/orders",
            headers=auth_headers,
            json=_VALID_ORDER,
        )
        resp = http_session.get(f"{BASE_URL}/orders", headers=auth_headers)
        assert resp.status_code == 200
        orders = resp.json()
        for order in orders:
            assert "id" in order,        "Order must have 'id'"
            assert "userId" in order,    "Order must have 'userId'"
            assert "items" in order,     "Order must have 'items'"
            assert "total" in order,     "Order must have 'total'"
            assert "status" in order,    "Order must have 'status'"
            assert "createdAt" in order, "Order must have 'createdAt'"
            assert "shipping" in order,  "Order must have 'shipping'"
            assert "payment" in order,   "Order must have 'payment'"
            assert "last4" in order["payment"], "payment must include 'last4'"

    def test_orders_get_no_auth_returns_401(self, http_session):
        """No Authorization header → 401 with error message."""
        resp = http_session.get(f"{BASE_URL}/orders")
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body or "message" in body

    def test_orders_get_tampered_token_returns_401(self, http_session):
        """Tampered JWT → 401 with error message."""
        resp = http_session.get(
            f"{BASE_URL}/orders",
            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.tampered.signature"},
        )
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body or "message" in body

    def test_orders_get_returns_list_regardless_of_order_count(
        self, http_session, auth_headers
    ):
        """200 response is always a list, whether empty or not."""
        resp = http_session.get(f"{BASE_URL}/orders", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


# ===========================================================================
# POST /orders (checkout)
# ===========================================================================

class TestPlaceOrder:

    def test_orders_post_valid_body_returns_201_with_schema(
        self, http_session, auth_headers
    ):
        """Complete valid body + valid token → 201, Order object with all fields."""
        resp = http_session.post(
            f"{BASE_URL}/orders",
            headers=auth_headers,
            json=_VALID_ORDER,
        )
        assert resp.status_code == 201
        order = resp.json()
        assert "id" in order,        "Order must have 'id'"
        assert "status" in order,    "Order must have 'status'"
        assert "total" in order,     "Order must have 'total'"
        assert "payment" in order,   "Order must have 'payment'"
        assert "last4" in order["payment"], "payment must be masked to last4"

    def test_orders_post_order_id_has_ord_prefix(self, http_session, auth_headers):
        """swagger.json: Order.id example is 'ORD-<timestamp>' → must start with 'ORD-'."""
        resp = http_session.post(
            f"{BASE_URL}/orders",
            headers=auth_headers,
            json=_VALID_ORDER,
        )
        assert resp.status_code == 201
        order_id = resp.json().get("id", "")
        assert order_id.startswith("ORD-"), (
            f"Order id should start with 'ORD-' but got: '{order_id}'"
        )

    def test_orders_post_no_auth_returns_401(self, http_session):
        """Checkout without authentication → 401 with error message."""
        resp = http_session.post(f"{BASE_URL}/orders", json=_VALID_ORDER)
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body or "message" in body

    # -----------------------------------------------------------------------
    # Missing top-level fields
    # -----------------------------------------------------------------------

    def test_orders_post_missing_items_returns_400(self, http_session, auth_headers):
        """Body without 'items' key → 400 with error message."""
        payload = {
            "shipping": _VALID_ORDER["shipping"],
            "payment":  _VALID_ORDER["payment"],
        }
        resp = http_session.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400
        body = resp.json()
        assert "error" in body or "message" in body

    def test_orders_post_missing_shipping_returns_400(self, http_session, auth_headers):
        """Body without 'shipping' key → 400 with error message."""
        payload = {
            "items":   _VALID_ORDER["items"],
            "payment": _VALID_ORDER["payment"],
        }
        resp = http_session.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400
        body = resp.json()
        assert "error" in body or "message" in body

    def test_orders_post_missing_payment_returns_400(self, http_session, auth_headers):
        """Body without 'payment' key → 400 with error message."""
        payload = {
            "items":    _VALID_ORDER["items"],
            "shipping": _VALID_ORDER["shipping"],
        }
        resp = http_session.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400
        body = resp.json()
        assert "error" in body or "message" in body

    # -----------------------------------------------------------------------
    # items array boundary
    # -----------------------------------------------------------------------

    @pytest.mark.parametrize("bad_items,label", [
        ([], "empty_array"),
        (None, "null_value"),
    ], ids=["empty_array", "null_value"])
    def test_orders_post_items_below_min_items_returns_400(
        self, http_session, auth_headers, bad_items, label
    ):
        """items minItems:1 — empty array and null must both be rejected → 400."""
        payload = {**_VALID_ORDER, "items": bad_items}
        resp = http_session.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400, (
            f"Expected 400 for items={label!r} but got {resp.status_code}"
        )
        body = resp.json()
        assert "error" in body or "message" in body

    # -----------------------------------------------------------------------
    # Shipping sub-field validation
    # -----------------------------------------------------------------------

    def test_orders_post_missing_shipping_first_name_returns_400(
        self, http_session, auth_headers
    ):
        """shipping.firstName is required — omitting it → 400."""
        bad_shipping = {k: v for k, v in _VALID_ORDER["shipping"].items()
                        if k != "firstName"}
        payload = {**_VALID_ORDER, "shipping": bad_shipping}
        resp = http_session.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400
        assert "error" in resp.json() or "message" in resp.json()

    def test_orders_post_missing_shipping_last_name_returns_400(
        self, http_session, auth_headers
    ):
        """shipping.lastName is required — omitting it → 400."""
        bad_shipping = {k: v for k, v in _VALID_ORDER["shipping"].items()
                        if k != "lastName"}
        payload = {**_VALID_ORDER, "shipping": bad_shipping}
        resp = http_session.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400
        assert "error" in resp.json() or "message" in resp.json()

    def test_orders_post_invalid_email_returns_400(self, http_session, auth_headers):
        """shipping.email not a valid email format → 400."""
        bad_shipping = {**_VALID_ORDER["shipping"], "email": "not-an-email"}
        payload = {**_VALID_ORDER, "shipping": bad_shipping}
        resp = http_session.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400
        assert "error" in resp.json() or "message" in resp.json()

    @pytest.mark.parametrize("bad_phone", [
        "041234567",    # 9 digits — one short
        "04123456789",  # 11 digits — one over
        "041234567a",   # non-digit char
        "",             # empty string
        "abcdefghij",   # 10 letters
    ], ids=["9_digits", "11_digits", "9_digits_plus_letter", "empty", "10_letters"])
    def test_orders_post_invalid_phone_pattern_returns_400(
        self, http_session, auth_headers, bad_phone
    ):
        """shipping.phone pattern ^\\d{10}$ — non-conforming values → 400."""
        bad_shipping = {**_VALID_ORDER["shipping"], "phone": bad_phone}
        payload = {**_VALID_ORDER, "shipping": bad_shipping}
        resp = http_session.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400, (
            f"Expected 400 for phone={bad_phone!r} but got {resp.status_code}"
        )
        assert "error" in resp.json() or "message" in resp.json()

    # -----------------------------------------------------------------------
    # Payment sub-field validation
    # -----------------------------------------------------------------------

    @pytest.mark.parametrize("bad_card", [
        "411111111111111",    # 15 digits — one short
        "41111111111111111",  # 17 digits — one long
        "411111111111111a",   # 15 digits + letter
        "",                   # empty
    ], ids=["15_digits", "17_digits", "15_plus_letter", "empty"])
    def test_orders_post_invalid_card_number_pattern_returns_400(
        self, http_session, auth_headers, bad_card
    ):
        """payment.cardNumber pattern ^\\d{16}$ — non-conforming values → 400."""
        bad_payment = {**_VALID_ORDER["payment"], "cardNumber": bad_card}
        payload = {**_VALID_ORDER, "payment": bad_payment}
        resp = http_session.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400, (
            f"Expected 400 for cardNumber={bad_card!r} but got {resp.status_code}"
        )
        assert "error" in resp.json() or "message" in resp.json()

    def test_orders_post_past_expiry_date_returns_400(self, http_session, auth_headers):
        """expiryDate in the past → 400."""
        bad_payment = {**_VALID_ORDER["payment"], "expiryDate": "01/20"}
        payload = {**_VALID_ORDER, "payment": bad_payment}
        resp = http_session.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400
        assert "error" in resp.json() or "message" in resp.json()

    @pytest.mark.parametrize("bad_expiry", [
        "00/28",   # month 00
        "13/28",   # month 13
        "1228",    # missing slash
        "12-28",   # hyphen separator
        "2028/12", # reversed format
        "",        # empty
        "abc",     # garbage
    ], ids=["month_00", "month_13", "no_slash", "hyphen_sep",
            "reversed_format", "empty", "garbage"])
    def test_orders_post_invalid_expiry_date_pattern_returns_400(
        self, http_session, auth_headers, bad_expiry
    ):
        """payment.expiryDate pattern ^(0[1-9]|1[0-2])\\/\\d{2}$ violations → 400."""
        bad_payment = {**_VALID_ORDER["payment"], "expiryDate": bad_expiry}
        payload = {**_VALID_ORDER, "payment": bad_payment}
        resp = http_session.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400, (
            f"Expected 400 for expiryDate={bad_expiry!r} but got {resp.status_code}"
        )
        assert "error" in resp.json() or "message" in resp.json()

    @pytest.mark.parametrize("bad_cvv", [
        "12",   # 2 digits — one short
        "1234", # 4 digits — one long
        "12a",  # 2 digits + letter
        "",     # empty
    ], ids=["2_digits", "4_digits", "2_digits_plus_letter", "empty"])
    def test_orders_post_invalid_cvv_pattern_returns_400(
        self, http_session, auth_headers, bad_cvv
    ):
        """payment.cvv pattern ^\\d{3}$ — non-conforming values → 400."""
        bad_payment = {**_VALID_ORDER["payment"], "cvv": bad_cvv}
        payload = {**_VALID_ORDER, "payment": bad_payment}
        resp = http_session.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400, (
            f"Expected 400 for cvv={bad_cvv!r} but got {resp.status_code}"
        )
        assert "error" in resp.json() or "message" in resp.json()

    # -----------------------------------------------------------------------
    # Item quantity boundary
    # -----------------------------------------------------------------------

    @pytest.mark.parametrize("bad_qty", [0, -1, -100], ids=["zero", "minus_one", "minus_hundred"])
    def test_orders_post_item_quantity_below_minimum_returns_400(
        self, http_session, auth_headers, bad_qty
    ):
        """items[].quantity minimum:1 — values below minimum → 400."""
        payload = {**_VALID_ORDER, "items": [{"productId": 1, "quantity": bad_qty}]}
        resp = http_session.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code == 400, (
            f"Expected 400 for item quantity={bad_qty} but got {resp.status_code}"
        )
        assert "error" in resp.json() or "message" in resp.json()

    def test_orders_post_nonexistent_product_id_returns_400_or_404(
        self, http_session, auth_headers
    ):
        """productId that doesn't exist → 400 or 404 with error message."""
        payload = {**_VALID_ORDER, "items": [{"productId": 99999, "quantity": 1}]}
        resp = http_session.post(f"{BASE_URL}/orders", headers=auth_headers, json=payload)
        assert resp.status_code in (400, 404)
        body = resp.json()
        assert "error" in body or "message" in body
