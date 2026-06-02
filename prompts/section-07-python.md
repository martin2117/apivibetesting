# Section 7 — Python + pytest + requests

## Course reference
| Prompt | Used in clip |
|--------|-------------|
| Prompt 1 — Generate the Full Test Suite | **Section 7, Clip 2** — Antigravity IDE Writes the Test Suite |
| Prompt 2 — Add Parametrize for Boundary Values | **Section 7, Clip 4** — Fixtures, Parametrize, and How Antigravity IDE Structures the Code |
| Prompt 3 — Fix a Failing Test | **Section 7, Clip 3** — Running pytest and Reading the Output |
| Prompt 4 — Check Coverage Against the Spec | **Section 7, Clip 4** — Fixtures, Parametrize, and How Antigravity IDE Structures the Code |
| Prompt 5 — Run pytest and Capture Output | **Section 7, Clip 3** — Running pytest and Reading the Output |

---

## Prompt 1: Generate the Full Test Suite
*Used in: Section 7, Clip 2 — "Antigravity IDE Writes the Test Suite"*

Make sure `swagger.json` and `test-ideas.md` are in your project folder and environment variables are set up (see `snippets/env-setup.md`).

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

Read two files:
- swagger.json — the full API spec with all endpoints, schemas, required
  fields, authentication requirements, and documented response codes
- test-ideas.md — the test strategy derived from the spec in Section 4,
  listing happy paths, negative tests, and auth requirements per endpoint

Use both files as your source of truth. swagger.json defines the contract.
test-ideas.md defines what to test. Together they give you complete coverage.

Generate a pytest test suite in a file called test_techshop.py
using the requests library.

Requirements:
- Set BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
  (variables come from the system environment — no .env file, no dotenv import)
- Write a pytest fixture called auth_token that:
    - reads credentials from environment variables:
        email = os.getenv("TEST_EMAIL")
        password = os.getenv("TEST_PASSWORD")
    - raises a clear error if either variable is not set
    - posts to the login endpoint with those credentials
    - asserts the response is 200
    - returns the token string from the response JSON
- For each endpoint, write test functions covering every scenario listed
  in test-ideas.md, verified against the response codes in swagger.json
- Use the auth_token fixture in any test that requires authentication
- Name test functions descriptively, e.g.:
    test_login_valid_credentials
    test_login_wrong_password_returns_401
    test_get_product_not_found_returns_404
- Never hardcode credentials, tokens, or secrets anywhere in the test file
```

---

## Prompt 2: Add Parametrize for Boundary Values
*Used in: Section 7, Clip 4 — "Fixtures, Parametrize, and How Antigravity IDE Structures the Code"*

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

Read swagger.json and look at the minimum/maximum constraints defined
in the request schemas (e.g. quantity minimum: 1).

For any field with a minimum or maximum constraint, add a
@pytest.mark.parametrize test that runs the same negative test with
multiple boundary values (e.g. 0, -1, -100 for a field with minimum 1).
```

---

## Prompt 3: Fix a Failing Test
*Used in: Section 7, Clip 3 — "Running pytest and Reading the Output"*

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

The test [test_name] in test_techshop.py has a failing assertion.
Read swagger.json to check what status code and response shape the spec
defines for this scenario, then update the assertion in the test function
to match the spec exactly.
```

---

## Prompt 4: Check Coverage Against the Spec
*Used in: Section 7, Clip 4 — "Fixtures, Parametrize, and How Antigravity IDE Structures the Code"*

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

Read swagger.json and test-ideas.md, then compare both against the
test functions in test_techshop.py.

List any scenarios from test-ideas.md or response codes from swagger.json
that are not yet covered by a test function, and generate the missing ones.
```

---

## Prompt 5: Run pytest and Capture Output
*Used in: Section 7, Clip 3 — "Running pytest and Reading the Output"*

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

Help me run the pytest test suite and review the results.
Run each step in the terminal and wait for my confirmation before continuing.

1. Confirm the virtual environment is active (should see (venv) in the prompt).
   If not, activate it:
   - Mac/Linux: source venv/bin/activate
   - Windows: venv\Scripts\activate

2. Run the tests with verbose output:
   pytest test_techshop.py -v

3. After the run, summarise:
   - How many tests passed
   - How many tests failed
   - The names of any failing tests

4. Run again with the HTML report:
   pytest test_techshop.py -v --html=pytest-report.html --self-contained-html

5. Confirm pytest-report.html was created in the project folder
```
