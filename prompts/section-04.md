# Section 4 — Meet the TechShop API

## Course reference
| Prompt | Used in clip |
|--------|-------------|
| Prompt 1 — Start the TechShop API | **Section 4, Clip 1** — Running the TechShop API Locally |
| Prompt 2 — Download the OpenAPI Spec | **Section 4, Clip 2** — Reading the OpenAPI Spec |
| Prompt 3 — Map Endpoints to Test Ideas | **Section 4, Clip 3** — Using Cursor to Map the Spec to Test Ideas |

---

## Prompt 1: Start the TechShop API
*Used in: Section 4, Clip 1 — "Running the TechShop API Locally"*

Open the Cursor terminal (Ctrl+` on Windows/Linux, Cmd+` on Mac) and paste this prompt into the Cursor chat:

```
Help me start the TechShop API locally. Run each step in the terminal
and wait for my confirmation before continuing.

1. Navigate into the broken-app folder:
   cd techshop-api/broken-app

2. Install the Node.js dependencies:
   npm install

3. Start the API server:
   npm start
   The terminal should print three lines:
   - TechShop API (broken) running on http://localhost:3000
   - Swagger UI: http://localhost:3000/docs
   - OpenAPI spec: http://localhost:3000/swagger.json

4. Verify the API is running by calling the health endpoint:
   curl http://localhost:3000/health
   Expected response: {"status":"ok","version":"1.0.0","environment":"broken"}

If npm is not installed, tell me to install Node.js from nodejs.org first.
```

---

## Prompt 2: Download the OpenAPI Spec
*Used in: Section 4, Clip 2 — "Reading the OpenAPI Spec"*

Make sure the API is running on port 3000 before using this prompt.

```
The TechShop API is running on http://localhost:3000.
Run this command in the terminal to download the OpenAPI spec
into the root of the project folder:

curl http://localhost:3000/swagger.json -o swagger.json

Then confirm the file was created by running:
ls -lh swagger.json

It should show a file of roughly 5-10 KB.
```

---

## Prompt 3: Map Endpoints to Test Ideas
*Used in: Section 4, Clip 3 — "Using Cursor to Map the Spec to Test Ideas"*

Use this prompt after `swagger.json` has been downloaded to the project root.

```
Read the swagger.json file in this project. List all the API endpoints and for each one identify:
- The happy path test
- At least two negative tests
- Any authentication requirements

Format it as a plain test ideas list, one endpoint per block.

Save the output to a file called test-ideas.md in the project root.
```

### Expected output structure

```
POST /auth/login
  Happy path: valid email and password → 200 with token
  Negative: wrong password → 401
  Negative: missing email field → 400
  Auth: none required

GET /products
  Happy path: returns 200 with array of products
  Negative: invalid category filter → 200 with empty array (or 400)
  Auth: none required

GET /products/{id}
  Happy path: valid ID → 200 with product object
  Negative: non-existent ID (e.g. 999) → 404
  Auth: none required

POST /cart
  Happy path: valid token + productId + quantity → 201
  Negative: negative quantity → 400
  Negative: no token → 401
  Negative: out-of-stock product → 400
  Auth: Bearer token required

PUT /cart/{itemId}
  Happy path: valid token + valid itemId + quantity → 200
  Negative: quantity less than 1 → 400
  Negative: non-existent itemId → 404
  Auth: Bearer token required

DELETE /cart/{itemId}
  Happy path: valid token + valid itemId → 200
  Negative: no token → 401
  Negative: non-existent itemId → 404
  Auth: Bearer token required

POST /orders
  Happy path: valid token + items + shipping + payment → 201
  Negative: expired card expiry date → 400
  Negative: invalid card number (not 16 digits) → 400
  Negative: missing shipping fields → 400
  Auth: Bearer token required
```
