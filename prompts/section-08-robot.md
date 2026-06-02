# Section 8 — Robot Framework

## Course reference
| Prompt | Used in clip |
|--------|-------------|
| Prompt 1 — Generate the Full Test Suite | **Section 8, Clip 2** — Antigravity IDE Generates the Test Suite |
| Prompt 2 — Override BASE_URL from Command Line | **Section 8, Clip 3** — Running Robot Framework and Reading the Report |
| Prompt 3 — Extract Keywords to a Resource File | **Section 8, Clip 4** — When Robot Framework Fits and When It Does Not |
| Prompt 4 — Check Coverage Against the Spec | **Section 8, Clip 2** — Antigravity IDE Generates the Test Suite |
| Prompt 5 — Run Robot Framework Suite | **Section 8, Clip 3** — Running Robot Framework and Reading the Report |

---

## Prompt 1: Generate the Full Robot Framework Test Suite
*Used in: Section 8, Clip 2 — "Antigravity IDE Generates the Test Suite"*

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

Generate a Robot Framework test suite in a file called techshop.robot
using RequestsLibrary.

Requirements:
- Settings section: import RequestsLibrary, Collections, and OperatingSystem
- Variables section (no default credential values — read from environment):
    ${BASE_URL}    %{BASE_URL}
    ${EMAIL}       %{TEST_EMAIL}
    ${PASSWORD}    %{TEST_PASSWORD}
- Keywords section: define a keyword called Get Auth Token that:
    - POSTs to the login endpoint with ${EMAIL} and ${PASSWORD}
    - Asserts status is 200
    - Returns the token value from the response JSON body
- Test Cases section: for each endpoint, write test cases covering every
  scenario listed in test-ideas.md, verified against swagger.json
- Use Suite Setup to create the HTTP session once before all tests
- Use Suite Teardown to delete the session after all tests
- Name test cases in plain readable English, e.g.:
    Login With Valid Credentials Returns Token
    Login With Wrong Password Returns 401
    Get Product With Unknown ID Returns 404
- Never hardcode credentials or secrets inside the .robot file
```

---

## Prompt 2: Override BASE_URL from Command Line
*Used in: Section 8, Clip 3 — "Running Robot Framework and Reading the Report"*

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

Modify techshop.robot so that BASE_URL can be overridden from the
command line using --variable BASE_URL:http://staging.techshop.com
without changing the file itself.
```

---

## Prompt 3: Extract Keywords to a Resource File
*Used in: Section 8, Clip 4 — "When Robot Framework Fits and When It Does Not"*

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

Refactor techshop.robot to move the Get Auth Token keyword and the
session setup/teardown into a separate resource file called
techshop_keywords.robot. Import it in techshop.robot with:
  Resource    techshop_keywords.robot
Keep the Test Cases section in techshop.robot unchanged.
```

---

## Prompt 4: Check Coverage Against the Spec
*Used in: Section 8, Clip 2 — "Antigravity IDE Generates the Test Suite"*

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

Read swagger.json and test-ideas.md, then compare both against the
test cases in techshop.robot.

List any scenarios from test-ideas.md or response codes from swagger.json
that are not yet covered by a test case, and generate the missing ones.
```

---

## Prompt 5: Run Robot Framework Suite
*Used in: Section 8, Clip 3 — "Running Robot Framework and Reading the Report"*

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

Help me run the Robot Framework test suite and review the results.
Run each step in the terminal and wait for my confirmation before continuing.

1. Confirm the virtual environment is active (should see (venv) in the prompt).
   If not, activate it:
   - Mac/Linux: source venv/bin/activate
   - Windows: venv\Scripts\activate

2. Run the full test suite and save reports to a robot-results folder:
   robot --outputdir robot-results techshop.robot

3. After the run, summarise:
   - How many tests passed
   - How many tests failed
   - The names of any failing tests

4. Confirm that robot-results/report.html and robot-results/log.html
   were created — tell me to open report.html in my browser

5. Show me how to run a single test by name as an example:
   robot --test "Login With Wrong Password" techshop.robot
```
