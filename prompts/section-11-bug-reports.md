# Section 11 — API Bug Reports with AI

## Course reference
| Prompt | Used in clip |
|--------|-------------|
| Prompt 1 — Generate Bug Reports from pytest Output | **Section 11, Clip 2** — Antigravity IDE Writes the Bug Reports |
| Prompt 2 — Generate Bug Reports from Newman Output | **Section 11, Clip 2** — Antigravity IDE Writes the Bug Reports |
| Prompt 3 — Format as Jira Tickets | **Section 11, Clip 2** — Antigravity IDE Writes the Bug Reports |

---

## Prompt 1: Generate Bug Reports from pytest Output
*Used in: Section 11, Clip 2 — "Antigravity IDE Writes the Bug Reports"*

Paste this prompt into the Antigravity IDE chat along with your pytest failure output.

```
I am going to paste the output from a failed pytest run against the TechShop API.

For each failing test, write a structured bug report with the following fields:

  Title: one sentence describing what is wrong
  Environment: TechShop API broken-app v1.0.0, localhost:3000
  Steps to reproduce: the exact HTTP request (method, URL, headers, body)
  Expected result: what the API spec says should happen
  Actual result: what the API actually returned (status code + body)
  Severity: Critical / High / Medium / Low with one-line justification

Use this severity guide:
  Critical — security issue (auth bypass, data exposure)
  High — wrong status code on a core operation
  Medium — missing input validation
  Low — incorrect response body field, cosmetic issue

Important: if the steps to reproduce require credentials, write them as
placeholder variables (e.g. {{TEST_EMAIL}}, {{TEST_PASSWORD}}) —
never include real credentials in a bug report.

Here is the pytest output:
[PASTE YOUR PYTEST OUTPUT HERE]
```

---

## Prompt 2: Generate Bug Reports from Newman Output
*Used in: Section 11, Clip 2 — "Antigravity IDE Writes the Bug Reports"*

```
I am going to paste the output from a Newman CLI run against the TechShop API.

For each failing assertion, write a structured bug report with:
  Title, Environment, Steps to Reproduce, Expected Result, Actual Result, Severity

If the steps to reproduce require credentials, use placeholder variables
(e.g. {{TEST_EMAIL}}, {{TEST_PASSWORD}}) rather than real values.

Newman output:
[PASTE YOUR NEWMAN OUTPUT HERE]
```

---

## Prompt 3: Format as Jira Tickets
*Used in: Section 11, Clip 2 — "Antigravity IDE Writes the Bug Reports"*

```
Take the five bug reports we just created and reformat each one as a
Jira-style ticket with these fields:
  Summary (max 80 characters)
  Description
  Steps to Reproduce (numbered list)
  Expected Behaviour
  Actual Behaviour
  Severity
  Labels: api-testing, techshop-api

Output as markdown, one ticket per section.
Do not include any credentials or secrets in the tickets.
```

---

## Example: Bug Report Output for B1

The following shows what a well-formed bug report looks like for Bug B1.
Note that the request body uses a placeholder for the email — not a real address.

```
Title
POST /auth/login returns 200 with valid token when wrong password is supplied

Environment
TechShop API — broken-app v1.0.0
Running locally on http://localhost:3000

Steps to Reproduce
1. Send the following HTTP request:
   POST http://localhost:3000/auth/login
   Content-Type: application/json
   Body: { "email": "{{TEST_EMAIL}}", "password": "any-wrong-password" }

Expected Result
HTTP 401 Unauthorized
Body: { "error": "Invalid credentials" }

Actual Result
HTTP 200 OK
Body: { "token": "<jwt>", "user": { "id": 1, ... } }
A valid JWT token is returned despite the incorrect password.

Severity
Critical — This is an authentication bypass. Any user who knows a valid
email address can log in without the password and receive a fully
authenticated session token.
```
