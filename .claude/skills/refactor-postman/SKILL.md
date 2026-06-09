---
name: refactor-postman
description: Refactors a Postman collection to follow professional best practices — folder structure, collection variables, token management, assertion depth, test naming. Uses Postman MCP. Verifies with Newman.
---

You are a senior API testing engineer. Use the Postman MCP to refactor the Postman collection in this project to follow professional best practices. Apply all changes via MCP tools and confirm each one after applying.

**STEP 1 — Organise into resource folders**
Create or reorganise folders inside the collection to match API resource groups:
- Auth (login, wrong password, missing fields)
- Products (list, get by ID, not found)
- Cart (add item, negative quantity, no auth)
- Orders (create, expired card, missing fields)

Both positive and negative tests must be in each folder.

**STEP 2 — Centralise variable management**
- Set `{{base_url}}` as a collection variable (default: `http://localhost:3000`)
- Set `{{TEST_EMAIL}}` and `{{TEST_PASSWORD}}` as collection variables
- Replace all hardcoded URLs with `{{base_url}}/path`
- Replace hardcoded credentials in request bodies with collection variables

**STEP 3 — Fix token management**
In the login request Tests script:
```javascript
const token = pm.response.json().token;
pm.collectionVariables.set("authToken", token);
```
Remove any `pm.globals.set` usage. Update all authenticated requests to use `{{authToken}}`.

**STEP 4 — Deepen assertions**
For every request that only checks status code, add a body assertion:
```javascript
pm.test("Response has expected structure", function() {
  const json = pm.response.json();
  pm.expect(json).to.have.property("token"); // adjust per endpoint
});
```
For negative tests, add an error message assertion:
```javascript
pm.test("Response contains error message", function() {
  const json = pm.response.json();
  pm.expect(json).to.have.property("error");
  pm.expect(json.error).to.be.a("string").and.not.empty;
});
```

**STEP 5 — Fix test names**
- Bad: `pm.test("Status is 200", ...)`
- Good: `pm.test("POST /auth/login with valid credentials returns 200 with token", ...)`

**STEP 6 — Export and verify**
Export the updated collection, then run:
```
newman run techshop.postman_collection.json --env-var base_url=http://localhost:3000 --reporters cli
```
Report how many tests passed and failed.
