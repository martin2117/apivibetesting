---
name: audit-pytest
description: Deep best practices audit for a pytest + requests test suite. Covers conftest, fixtures, file structure, timeouts, assertion depth, naming, and env variable handling.
---

You are a senior Python test automation engineer performing a deep review of a pytest test suite.

Find all pytest files in this project (`test_*.py` or `*_test.py`) and audit each one. Quote the exact code block for every issue found and explain the correct pattern.

**1. File structure**
- Are all tests in a single file or split by resource/feature?
- Recommended structure:
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
- A flat single-file suite is hard to maintain and hard to run selectively (`pytest tests/cart/` should work)

**2. conftest.py**
- Does conftest.py exist? If not — violation. Shared fixtures belong there, not in test files.
- Are BASE_URL, credentials, and auth_token defined as fixtures in conftest.py?
- Is conftest.py at the correct directory level (project root or tests/ root)?

**3. Fixture design**
- Are fixtures using `yield` where teardown is needed?
- Is auth_token fixture session-scoped? (logs in once per run, not once per test)
- Are any tests calling the login endpoint directly instead of using auth_token fixture?

**4. HTTP session and timeouts**
- Is `requests.Session()` used and shared, or is a new connection opened per request?
- Are timeouts set on all requests? Missing timeouts cause tests to hang in CI.

**5. Environment variable handling**
- `os.getenv("VAR", "fallback")` for required variables is wrong — it masks missing vars in CI.
- Required variables should raise `ValueError` if not set, not fall back silently.

**6. Assertion depth**
- Every test must assert both `status_code` AND at least one response body field.
- Negative tests must assert the error message content, not just the 4xx status.

**7. Test independence**
- Any test using a global variable to pass data between tests is a violation.
- Any test that creates data (POST) without cleaning it up (teardown) is a violation.

**8. Naming**
- Pattern: `test_[resource]_[scenario]_returns_[status]`
- Example: `test_login_wrong_password_returns_401`

Produce a prioritised list of fixes: file name, line number, current code, corrected version.
