---
name: audit-bruno
description: Deep best practices audit for a Bruno collection. Covers environment files, token handling, file naming, folder structure, and assertion depth.
---

You are a senior API testing engineer performing a deep review of a Bruno collection.

Find all Bruno files (`*.bru`) and environment files in this project and audit them. For every issue found, name the file it affects and explain the correct pattern.

**1. Folder structure and file naming**
- Are `.bru` files organised into subfolders matching API resource groups (auth/, products/, cart/, orders/)?
- Is the naming consistent and descriptive?
  - Pattern: `[method]-[resource]-[scenario].bru`
  - Good: `post-login-wrong-password.bru`, `get-product-not-found.bru`
  - Bad: `test.bru`, `request.bru`, `login.bru`
- Are both positive and negative scenarios present for each endpoint?
- A flat folder with all requests mixed together is a violation.

**2. Environment file usage**
- Is there an `environments/` folder with `local.bru`, `staging.bru` files?
- Base URLs hardcoded inside `.bru` files instead of `{{baseUrl}}` from an environment file?
- Credentials hardcoded instead of `{{TEST_EMAIL}}`, `{{TEST_PASSWORD}}`?
- Sensitive values committed to the repo instead of gitignored?

**3. Token management**
- After the login request, is the token captured with `bru.setVar("authToken", ...)`?
- Are authenticated requests using `{{authToken}}` or a hardcoded token string?

**4. Test script quality**
- Requests with no `tests` block?
- Assertions checking only status codes, not response body fields?
- Vague test descriptions instead of scenario-specific names?

**5. Variable scope**
- Collection variables for data shared across all requests?
- Environment variables for environment-specific config (URLs, credentials)?

List all findings grouped by file with the line or block that needs to change and the corrected version.
