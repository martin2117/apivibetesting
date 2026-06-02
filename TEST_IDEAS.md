# TechShop API — Test Ideas

Based on `swagger.json`. Base URL: `http://localhost:3000`

---

## GET /products

**Authentication:** None (public)

**Happy path**
- GET `/products` with no query params → 200, JSON array of products; each item matches Product schema (id, name, price, category, stock, inStock).

**Negative tests**
- GET `/products?category=invalid-category` → empty array or 400 (verify actual API behavior).
- GET `/products` with unsupported query params (e.g. `?limit=10`) → ignored or 400; response still valid.

**Additional negative**
- GET `/products` with wrong HTTP method (e.g. POST) → 405 Method Not Allowed.

---

## GET /products/{id}

**Authentication:** None (public)

**Happy path**
- GET `/products/1` (or any known valid ID) → 200, single Product object with expected fields.

**Negative tests**
- GET `/products/99999` (non-existent ID) → 404, "Product not found".
- GET `/products/abc` or `/products/-1` (invalid path ID) → 400 or 404.

**Additional negative**
- GET `/products/` (missing ID) → 404 or routing error.

---

## POST /auth/login

**Authentication:** None (issues JWT for protected routes)

**Happy path**
- POST `/auth/login` with valid `email` and `password` (e.g. `demo@techshop.com` / `password123`) → 200, body contains `token` (JWT) and `user` (id, email, name).

**Negative tests**
- POST with wrong password → 401, "Invalid credentials".
- POST with missing `email` or `password` → 400, "Missing email or password".

**Additional negative**
- POST with empty body `{}` → 400.
- POST with valid email format but unknown user → 401.

---

## GET /cart

**Authentication:** Bearer JWT (`Authorization: Bearer <token>`)

**Happy path**
- GET `/cart` with valid token after login → 200, Cart with `items` array and `total` number.

**Negative tests**
- GET `/cart` with no `Authorization` header → 401 Unauthorized.
- GET `/cart` with invalid or expired token → 401 Unauthorized.

**Additional negative**
- GET `/cart` with malformed header (e.g. `Bearer` only, or `Basic ...`) → 401.

---

## POST /cart

**Authentication:** Bearer JWT

**Happy path**
- POST `/cart` with valid token and body `{ "productId": 1, "quantity": 2 }` → 201, item added; GET `/cart` reflects new line item.

**Negative tests**
- POST without auth → 401 Unauthorized.
- POST with `productId` that does not exist → 404 Product not found.

**Additional negative**
- POST with `quantity: 0` or negative → 400 Invalid productId or quantity.
- POST with missing `productId` or `quantity` → 400.
- POST with non-integer `productId` → 400.

---

## PUT /cart/{itemId}

**Authentication:** Bearer JWT

**Happy path**
- PUT `/cart/{itemId}` with valid token and `{ "quantity": 3 }` for an existing cart line → 200, quantity updated.

**Negative tests**
- PUT without auth → 401 Unauthorized.
- PUT `/cart/99999` with valid token but unknown `itemId` → 404 Cart item not found.

**Additional negative**
- PUT with `quantity: 0` or below minimum (1) → 400 Invalid quantity.
- PUT with missing `quantity` in body → 400.

---

## DELETE /cart/{itemId}

**Authentication:** Bearer JWT

**Happy path**
- DELETE `/cart/{itemId}` with valid token for an existing cart item → 200, item removed; GET `/cart` no longer includes that item.

**Negative tests**
- DELETE without auth → 401 Unauthorized.
- DELETE `/cart/99999` (non-existent item) → 404 Cart item not found.

**Additional negative**
- DELETE same `itemId` twice → second call 404.
- DELETE with invalid `itemId` (non-numeric) → 400 or 404.

---

## GET /orders

**Authentication:** Bearer JWT

**Happy path**
- GET `/orders` with valid token → 200, array of Order objects for the current user (id, userId, items, shipping, payment.last4, total, status, createdAt).

**Negative tests**
- GET without `Authorization` → 401 Unauthorized.
- GET with expired or tampered JWT → 401 Unauthorized.

**Additional negative**
- GET with valid token for user with no orders → 200 and empty array `[]`.

---

## POST /orders (checkout)

**Authentication:** Bearer JWT

**Happy path**
- POST `/orders` with valid token and complete body:
  - `items`: `[{ "productId": 1, "quantity": 1 }]` (min 1 item)
  - `shipping`: firstName, lastName, email, phone (10 digits, e.g. `0412345678`)
  - `payment`: 16-digit cardNumber, MM/YY expiryDate (future), 3-digit cvv
  → 201, Order with status (e.g. `confirmed`), masked payment (`last4`), total.

**Negative tests**
- POST without auth → 401 Unauthorized.
- POST with missing required top-level fields (`items`, `shipping`, or `payment`) → 400 Validation error.

**Additional negative**
- POST with empty `items: []` → 400 (minItems: 1).
- POST with invalid shipping `phone` (not 10 digits) → 400.
- POST with invalid `payment.cardNumber` (not 16 digits) → 400.
- POST with past `expiryDate` → 400.
- POST with invalid `cvv` (not 3 digits) → 400.
- POST with invalid shipping `email` format → 400.
- POST with `quantity: 0` on line item → 400.
- POST referencing non-existent `productId` → 400 (if enforced at checkout).

---

## Summary: auth by endpoint

| Endpoint | Auth |
|----------|------|
| GET /products | None |
| GET /products/{id} | None |
| POST /auth/login | None |
| GET /cart | Bearer JWT |
| POST /cart | Bearer JWT |
| PUT /cart/{itemId} | Bearer JWT |
| DELETE /cart/{itemId} | Bearer JWT |
| GET /orders | Bearer JWT |
| POST /orders | Bearer JWT |

**Typical flow for protected tests:** `POST /auth/login` → use `token` in `Authorization: Bearer <token>` for cart and order endpoints.
