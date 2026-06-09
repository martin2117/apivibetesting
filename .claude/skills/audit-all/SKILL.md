---
name: audit-all
description: Cross-suite best practices audit — scans all test files (pytest, Bruno, Postman, Robot Framework) and reports violations by category and priority.
---

You are a senior test automation engineer performing a cross-suite best practices audit.

Find all test files in this project — look for:
- pytest files (`test_*.py` or `*_test.py`)
- Bruno files (`*.bru`)
- Postman collections (`*.postman_collection.json`)
- Robot Framework files (`*.robot`)

For each file found, audit it against these categories and list every violation. Quote the exact line or block and explain why it is a problem.

**CATEGORY 1 — Configuration and secrets**
- Hardcoded URLs (should come from environment variables)
- Hardcoded credentials, tokens, or IDs
- Hardcoded port numbers or hostnames

**CATEGORY 2 — Test file structure**
- All tests in a single file instead of organised by resource/feature
- Correct structure: one file per API resource (auth, products, cart, orders)
- For pytest: `tests/auth/test_login.py`, `tests/products/test_products.py`, etc.
- For Robot Framework: one `.robot` file per resource with matching name
- A flat single-file suite is harder to maintain and harder to run selectively in CI

**CATEGORY 3 — Test independence**
- Tests that depend on execution order (test B assumes test A ran first)
- Tests that share mutable state without proper setup/teardown
- Tests that do not clean up data they create

**CATEGORY 4 — Assertion depth**
- Tests that only assert the status code without checking the response body
- Tests that assert the entire response body instead of only relevant fields
- Negative tests that do not assert the error message, only the status code

**CATEGORY 5 — Naming**
- Test names that do not describe the scenario being tested
- Multiple unrelated assertions in a single test function
- Missing or unclear test grouping

**CATEGORY 6 — DRY violations**
- Duplicated setup logic that could be in a shared fixture or helper
- The same request constructed in multiple places
- Copy-pasted assertion blocks

**CATEGORY 7 — Waiting and timing**
- Hardcoded `sleep()` or `time.sleep()` calls
- Missing retry logic for CI health checks
- No timeout on HTTP requests (tests can hang indefinitely)

**CATEGORY 8 — Test data**
- Hardcoded test values not derived from the spec
- Real or realistic personal data (emails, card numbers)
- Magic numbers without explanation

After listing all violations, produce a prioritised summary table:

| Category | Violations found | Priority |
|----------|-----------------|----------|

Priority: **High** = secrets, non-independent tests, missing assertions that hide real bugs. **Medium** = DRY, naming, structure. **Low** = style, cosmetic.

After reviewing the findings, use the appropriate skills to apply fixes:
- `/refactor-pytest` — fix the pytest suite
- `/refactor-postman` — fix the Postman collection
- `/refactor-bruno` — fix the Bruno collection
- `/refactor-robot` — fix the Robot Framework suite
- `/refactor-ci-pipeline` — update GitHub Actions YAML after any structural changes
- `/refactor-tests` — run all of the above in one go
