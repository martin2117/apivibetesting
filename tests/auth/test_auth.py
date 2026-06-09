"""
TechShop API — Auth tests
==========================
Covers POST /auth/login happy-path and all documented negative scenarios.
"""

import os

import pytest

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")


# ===========================================================================
# POST /auth/login
# ===========================================================================

class TestAuthLogin:

    # -----------------------------------------------------------------------
    # Happy path
    # -----------------------------------------------------------------------

    def test_auth_login_valid_credentials_returns_200(self, http_session):
        """Valid email + password → 200 with token and user object."""
        email = os.getenv("TEST_EMAIL")
        password = os.getenv("TEST_PASSWORD")

        if not email or not password:
            pytest.skip("TEST_EMAIL / TEST_PASSWORD not set; skipping login happy path")

        resp = http_session.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "token" in body, "Response must include a 'token' field"
        assert "user" in body, "Response must include a 'user' field"
        user = body["user"]
        assert "id" in user,    "user object must include 'id'"
        assert "email" in user, "user object must include 'email'"
        assert "name" in user,  "user object must include 'name'"

    # -----------------------------------------------------------------------
    # Negative: credential errors
    # -----------------------------------------------------------------------

    def test_auth_login_wrong_password_returns_401(self, http_session):
        """Correct email, wrong password → 401 with error message."""
        email = os.getenv("TEST_EMAIL", "demo@techshop.com")
        resp = http_session.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": "this-is-definitely-wrong"},
        )
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body or "message" in body, \
            "401 response should include an error or message field"

    def test_auth_login_unknown_user_returns_401(self, http_session):
        """Well-formed email that doesn't exist → 401 with error message."""
        resp = http_session.post(
            f"{BASE_URL}/auth/login",
            json={"email": "nobody@unknown-domain-xyz.com", "password": "password123"},
        )
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body or "message" in body, \
            "401 response should include an error or message field"

    # -----------------------------------------------------------------------
    # Negative: missing / empty fields
    # -----------------------------------------------------------------------

    def test_auth_login_missing_email_returns_400(self, http_session):
        """Body has password but no email → 400 with error message."""
        resp = http_session.post(
            f"{BASE_URL}/auth/login",
            json={"password": "password123"},
        )
        assert resp.status_code == 400
        body = resp.json()
        assert "error" in body or "message" in body, \
            "400 response should include an error or message field"

    def test_auth_login_missing_password_returns_400(self, http_session):
        """Body has email but no password → 400 with error message."""
        resp = http_session.post(
            f"{BASE_URL}/auth/login",
            json={"email": "demo@techshop.com"},
        )
        assert resp.status_code == 400
        body = resp.json()
        assert "error" in body or "message" in body, \
            "400 response should include an error or message field"

    def test_auth_login_empty_body_returns_400(self, http_session):
        """Empty JSON body → 400 with error message."""
        resp = http_session.post(
            f"{BASE_URL}/auth/login",
            json={},
        )
        assert resp.status_code == 400
        body = resp.json()
        assert "error" in body or "message" in body, \
            "400 response should include an error or message field"
