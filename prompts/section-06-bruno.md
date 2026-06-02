# Section 6 — Bruno

## Course reference
| Prompt | Used in clip |
|--------|-------------|
| Prompt 1 — Generate Bruno Collection | **Section 6, Clip 2** — Cursor Writes .bru Files Directly |
| Prompt 2 — Add a Missing Test | **Section 6, Clip 3** — Running Bruno Tests and Reading Results |
| Prompt 3 — Fix a .bru Assertion | **Section 6, Clip 3** — Running Bruno Tests and Reading Results |
| Prompt 4 — Install Bruno CLI and Run Collection | **Section 6, Clip 4** — Bruno CLI |

---

## Prompt 1: Generate Bruno Collection
*Used in: Section 6, Clip 2 — "Cursor Writes .bru Files Directly"*

Use this prompt with your project folder open in Cursor. Make sure `swagger.json` and `test-ideas.md` are present.

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

Generate a Bruno collection as .bru files based on these files.

Create the folder structure:
  techshop-bruno/
    auth/
    products/
    cart/
    orders/
    environments/

In the environments folder, create a file called local.bru that sets:
  baseUrl = http://localhost:3000
  authToken = (empty — will be populated after login)

For each endpoint, generate one .bru file per test scenario listed in
test-ideas.md, verified against the response codes in swagger.json.

Use {{baseUrl}} for the base URL and {{authToken}} for auth headers.

In the login happy-path .bru file, add a post-request script that
reads the token from the response body and sets it as the authToken
environment variable so subsequent requests can use it automatically.

Name each file descriptively, e.g. login-valid.bru, login-wrong-password.bru,
get-product-not-found.bru.
```

---

## Prompt 2: Add a Missing Test
*Used in: Section 6, Clip 3 — "Running Bruno Tests and Reading Results"*

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

Read swagger.json and test-ideas.md, then check if there are any scenarios
from test-ideas.md or endpoints from swagger.json that do not yet have a
corresponding .bru file in the techshop-bruno folder.
Generate the missing .bru files.
```

---

## Prompt 3: Fix a .bru Assertion
*Used in: Section 6, Clip 3 — "Running Bruno Tests and Reading Results"*

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

The file [filename].bru has a failing assertion. Read swagger.json to check
what status code and response shape the spec defines for this scenario,
then rewrite the test block in the .bru file to match the spec exactly.
```

---

## Prompt 4: Install Bruno CLI and Run Collection
*Used in: Section 6, Clip 4 — "Bruno CLI"*

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

Help me install the Bruno CLI and run the test collection from the terminal.
Run each step and wait for my confirmation before continuing.

1. Install the Bruno CLI globally:
   npm install -g @usebruno/cli

2. Verify the install:
   bru --version

3. Run the full collection against the local API:
   bru run techshop-bruno/ --env local

4. Tell me how many tests passed and failed from the summary output

5. Also show me how to run just one subfolder (auth only) as an example:
   bru run techshop-bruno/auth/ --env local
```
