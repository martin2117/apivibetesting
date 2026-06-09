---
name: refactor-tests
description: Full test suite refactoring workflow — runs all tool-specific audits, applies all refactoring skills in the correct order, then updates the CI pipeline to match. Run this when you want to refactor everything in one go.
---

You are a senior test automation engineer performing a complete refactoring of all API test suites in this project.

Run the following steps in order. Do not skip a step. After each step, confirm the tests still pass before moving to the next.

**STEP 1 — Full audit across all suites**
Read all test files in the project:
- pytest files (`test_*.py`, `*_test.py`)
- Bruno files (`*.bru`)
- Postman collections (`*.postman_collection.json`)
- Robot Framework files (`*.robot`)

For each suite, produce a summary of the top violations:
- Hardcoded config or credentials
- Missing file structure (all in one file)
- Status-code-only assertions
- Missing conftest / shared resource / collection variables
- No timeouts
- Poor naming

Present the summary and wait for confirmation before proceeding.

**STEP 2 — Refactor pytest suite**
Apply all pytest best practices:
- Split into `tests/auth/`, `tests/products/`, `tests/cart/`, `tests/orders/`
- Create `tests/conftest.py` with BASE_URL, auth_token (session-scoped), http_session with 10s timeout
- Fix env var handling — raise ValueError for missing required variables
- Deepen assertions — status code + body field on every test
- Fix naming — `test_[resource]_[scenario]_returns_[status]`
- Run `pytest tests/ -v` and confirm all tests pass

**STEP 3 — Refactor Bruno collection**
Apply Bruno best practices:
- Create `environments/local.bru` and `environments/staging.bru`
- Replace hardcoded values with `{{baseUrl}}`, `{{TEST_EMAIL}}`, `{{TEST_PASSWORD}}`
- Fix token capture with `bru.setVar("authToken", ...)`
- Organise into resource subfolders with descriptive file names
- Deepen assertions — body fields on every request
- Run `bru run techshop-bruno/ --env local` and confirm all tests pass

**STEP 4 — Refactor Postman collection**
Apply Postman best practices via Postman MCP:
- Set `{{base_url}}`, `{{TEST_EMAIL}}`, `{{TEST_PASSWORD}}` as collection variables
- Fix token storage — `pm.collectionVariables.set("authToken", ...)`
- Deepen assertions — body fields and descriptive test names
- Export and run with Newman to confirm all tests pass

**STEP 5 — Refactor Robot Framework suite**
Apply Robot Framework best practices:
- Split into `tests/auth.robot`, `tests/products.robot`, `tests/cart.robot`, `tests/orders.robot`
- Create `techshop_keywords.resource` with shared keywords
- Fix Variables section — read from `%{BASE_URL}`, `%{TEST_EMAIL}`, `%{TEST_PASSWORD}`
- Add Suite Setup for session creation, tags on all test cases
- Deepen assertions — body field checks after Status Should Be
- Run `robot --variable BASE_URL:http://localhost:3000 tests/` and confirm all tests pass

**STEP 6 — Update the CI pipeline**
Now that all test file locations and commands have changed, update `.github/workflows/api-tests.yml`:
- Update pytest command: `pytest tests/ -v ...`
- Update Robot Framework command: `robot ... tests/`
- Confirm Bruno and Newman commands still match current file/folder names
- Update artifact paths if any report file locations changed
- Commit: `git add . && git commit -m "Refactor all test suites to best practices + update CI" && git push origin main`

**STEP 7 — Verify CI**
Tell me to open the GitHub Actions tab and confirm the pipeline goes green with the refactored structure. If it fails, read the annotations and fix the issue.
