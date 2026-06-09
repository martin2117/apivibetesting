---
name: refactor-robot
description: Refactors a Robot Framework suite to follow professional best practices — file structure per resource, shared resource file, env variables, Suite Setup, tags, assertion depth, naming. Verifies by running the suite.
---

You are a senior Robot Framework expert. Refactor the Robot Framework suite in this project to follow professional best practices. Apply all changes, explain each one, then run the suite to confirm nothing broke.

**STEP 1 — Split into one file per resource**
If all tests are in a single `.robot` file, split them:
```
tests/
  auth.robot
  products.robot
  cart.robot
  orders.robot
  techshop_keywords.resource
```
Move each test case to the matching file. This allows selective CI runs (`robot tests/auth.robot`).

**STEP 2 — Create a shared resource file**
Create `techshop_keywords.resource`. Move into it:
- Get Auth Token keyword (or equivalent login keyword)
- Create Session With Base URL keyword
- Any keyword that appears in more than one `.robot` file

Update all `.robot` files to import it:
```robot
Resource    techshop_keywords.resource
```

**STEP 3 — Fix variable definitions**
In every `.robot` file Variables section, replace hardcoded values:
```robot
*** Variables ***
${BASE_URL}       %{BASE_URL}
${TEST_EMAIL}     %{TEST_EMAIL}
${TEST_PASSWORD}  %{TEST_PASSWORD}
```
Do NOT add fallback values for required variables — missing env vars must raise a clear error.

**STEP 4 — Add Suite Setup**
In each `.robot` file, add Suite Setup to create the HTTP session once:
```robot
Suite Setup    Create Session    techshop    ${BASE_URL}
```

**STEP 5 — Add tags**
Add `Test Tags` to each suite and specific tags to individual tests:
```robot
*** Settings ***
Test Tags    regression    api

*** Test Cases ***
Login With Wrong Password Returns 401
    [Tags]    auth    smoke
```

**STEP 6 — Deepen assertions**
After `Status Should Be`, add response body field checks:
```robot
${body}=    Set Variable    ${response.json()}
Should Not Be Empty    ${body}[token]
```
For negative tests, assert the error field:
```robot
Should Contain    str(${body})    error
```

**STEP 7 — Fix test case naming**
Pattern: `[Resource] [Scenario] Returns [Expected Status]`
- Bad:  `Test Login`, `Negative Test`
- Good: `Login With Wrong Password Returns 401`

**STEP 8 — Run the suite**
```
robot --variable BASE_URL:http://localhost:3000 tests/
```
Report how many tests passed and failed. Fix any regressions before finishing.
