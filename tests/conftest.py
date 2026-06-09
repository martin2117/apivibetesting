"""
TechShop API — Shared pytest fixtures
======================================
All fixtures live here so every sub-suite can import them automatically.

Environment variables (no .env / no dotenv):
  BASE_URL      – defaults to http://localhost:3000
  TEST_EMAIL    – email for the demo account  (required for auth tests)
  TEST_PASSWORD – password for the demo account (required for auth tests)
"""

import os

import pytest
import requests


# ---------------------------------------------------------------------------
# Base URL
# ---------------------------------------------------------------------------

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")


# ---------------------------------------------------------------------------
# HTTP session with a 10-second timeout applied to every request
# ---------------------------------------------------------------------------

class _TimeoutSession(requests.Session):
    """A requests.Session that enforces a default timeout on every call."""

    DEFAULT_TIMEOUT = 10  # seconds

    def request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", self.DEFAULT_TIMEOUT)
        return super().request(method, url, **kwargs)


@pytest.fixture(scope="session")
def http_session():
    """Session-scoped requests.Session with a 10-second timeout."""
    with _TimeoutSession() as session:
        yield session


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def auth_token(http_session):
    """
    Obtain a JWT from POST /auth/login using env-var credentials.

    Raises ValueError immediately if TEST_EMAIL or TEST_PASSWORD are not set,
    so the developer knows exactly what is missing before a single test runs.
    """
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    if not email:
        raise ValueError(
            "Environment variable TEST_EMAIL is not set. "
            "Export it before running the suite: export TEST_EMAIL=demo@techshop.com"
        )
    if not password:
        raise ValueError(
            "Environment variable TEST_PASSWORD is not set. "
            "Export it before running the suite: export TEST_PASSWORD=password123"
        )

    response = http_session.post(
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
