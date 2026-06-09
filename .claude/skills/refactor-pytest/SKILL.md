---
name: refactor-pytest
description: Refactors a pytest + requests test suite to follow professional best practices — file structure, conftest, fixtures, timeouts, assertion depth, naming. Runs tests after to confirm nothing broke.
---

You are a senior Python test automation engineer. Refactor the pytest suite in this project to follow professional best practices. Apply every step below, explain what you changed and why, then run the tests to confirm nothing broke.

**STEP 1 — Restructure test files by resource**
If all tests are in a single file, split them into a `tests/` directory organised by API resource:
```
tests/
  conftest.py
  auth/
    test_login.py
  products/
    test_products.py
  cart/
    test_cart.py
  orders/
    test_orders.py
```
Move each test function to the matching file. Keep the test logic unchanged — only move it.

**STEP 2 — Create or improve conftest.py**
Create `tests/conftest.py` if it does not exist. Move into it:
- `BASE_URL` — read from `os.environ["BASE_URL"]`, raise `ValueError` if missing
- Session-scoped `auth_token` fixture: reads `TEST_EMAIL` and `TEST_PASSWORD` from environment, calls login, asserts 200, returns the token string
- Session-scoped `http_session` fixture using `requests.Session()` with a 10s default timeout

Remove these definitions from individual test files — pytest finds `conftest.py` automatically.

**STEP 3 — Fix environment variable handling**
Replace every `os.getenv("VAR", "fallback")` for required variables:
```python
value = os.environ.get("VAR")
if not value:
    raise ValueError("VAR environment variable is not set")
```
Keep fallbacks only for genuinely optional variables.

**STEP 4 — Add timeouts to all HTTP requests**
In the `http_session` fixture:
```python
import functools
session = requests.Session()
session.request = functools.partial(session.request, timeout=10)
```

**STEP 5 — Deepen assertions**
For every test that only asserts `status_code`, add at least one body assertion:
- Positive tests: assert a key field exists with expected type or value
- Negative tests: assert the error message field exists and is a non-empty string
- Do NOT assert the entire response — assert only the fields that matter for this scenario

**STEP 6 — Fix test naming**
Pattern: `test_[resource]_[scenario]_returns_[status]`
- `test_login` → `test_login_valid_credentials_returns_200_with_token`
- `test_product_not_found` → `test_get_product_invalid_id_returns_404`

**STEP 7 — Run the tests**
```
pytest tests/ -v
```
Report how many passed and failed. If anything that was passing before is now failing, identify and fix the regression before finishing.
