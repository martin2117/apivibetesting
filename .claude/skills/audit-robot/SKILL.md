---
name: audit-robot
description: Deep best practices audit for a Robot Framework suite. Covers file structure, resource extraction, variables, Suite Setup, tags, and assertion depth.
---

You are a senior Robot Framework expert performing a code review.

Find all Robot Framework files (`*.robot` and `*.resource`) in this project and audit each one. For every issue found, name the file and the test case or keyword it affects.

**1. File structure**
- Is there one `.robot` file per API resource (auth.robot, products.robot, cart.robot, orders.robot)?
- Putting all test cases in a single `.robot` file is a violation — it cannot be run selectively in CI.
- Is there a shared `.resource` file for common keywords?

**2. Resource file and keyword extraction**
- Is there a shared `*.resource` file for common keywords (Get Auth Token, Create Session, etc.)?
- Is the auth/login keyword duplicated across multiple `.robot` files? It should be in the shared resource.
- Any keyword that appears more than once should be extracted to the resource file.

**3. Variables section**
- Hardcoded values instead of reading from OS environment?
  - Correct: `${BASE_URL}    %{BASE_URL}`
  - Wrong:   `${BASE_URL}    http://localhost:3000`
- Required variables must NOT have fallback values — missing env vars should raise a clear error.

**4. Suite Setup and Teardown**
- Is HTTP session created once in `Suite Setup` or recreated for every test?
  - Creating a new session per test is a violation — use `Suite Setup    Create Session    ...`
- Is there a `Suite Teardown` that cleans up created data?

**5. Tags**
- Do test cases have meaningful tags for selective CI runs (smoke, regression, auth, products)?
- Is `Test Tags` or `Force Tags` set in each suite?

**6. Assertion depth**
- Is `Status Should Be` always followed by response body field checks?
- Do negative tests assert the error message content, not just the status code?

**7. Test case naming**
- Pattern: `[Resource] [Scenario] Returns [Expected Status]`
- Good: `Login With Wrong Password Returns 401`
- Bad: `Test Login Negative`, `Test 3`

List all findings by file and priority with the specific test case or keyword name and recommended fix.
