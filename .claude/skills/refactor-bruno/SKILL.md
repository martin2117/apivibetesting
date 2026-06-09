---
name: refactor-bruno
description: Refactors a Bruno collection to follow professional best practices — folder structure, file naming, environment files, token management, assertion depth. Verifies with Bruno CLI.
---

You are a senior API testing engineer. Refactor the Bruno collection in this project to follow professional best practices. Apply all changes and run `bru run` at the end to verify nothing broke.

**STEP 1 — Reorganise into resource subfolders**
Create or reorganise the collection into subfolders matching API resource groups:
```
techshop-bruno/
  auth/
    post-login-valid.bru
    post-login-wrong-password.bru
  products/
    get-products.bru
    get-product-valid-id.bru
    get-product-not-found.bru
  cart/
    post-cart-add-item.bru
    post-cart-negative-quantity.bru
    post-cart-no-auth.bru
  orders/
    post-order-valid.bru
    post-order-expired-card.bru
```

**STEP 2 — Create environment files**
Create `environments/local.bru` inside the Bruno collection folder:
```
vars {
  baseUrl: http://localhost:3000
  TEST_EMAIL: demo@techshop.com
  TEST_PASSWORD: password123
}
```
Create `environments/staging.bru` with the same keys and empty values as a template.

**STEP 3 — Replace hardcoded values**
In every `.bru` file:
- Replace hardcoded base URLs with `{{baseUrl}}`
- Replace hardcoded credentials with `{{TEST_EMAIL}}` and `{{TEST_PASSWORD}}`
- Replace hardcoded auth tokens with `{{authToken}}`

**STEP 4 — Fix token management**
In the login request post-response script:
```javascript
bru.setVar("authToken", res.getBody().token);
```
In all authenticated requests, set the Authorization header to: `Bearer {{authToken}}`

**STEP 5 — Deepen assertions**
For every request with only a status assertion, add body assertions:
```javascript
test("Response contains expected fields", function() {
  const data = res.getBody();
  expect(data).to.have.property("token"); // adjust per endpoint
});
```
For negative tests:
```javascript
test("Response contains error message", function() {
  const data = res.getBody();
  expect(data).to.have.property("error");
  expect(data.error).to.be.a("string").and.not.empty;
});
```

**STEP 6 — Verify**
```
bru run techshop-bruno/ --env local
```
Report how many tests passed and failed.
