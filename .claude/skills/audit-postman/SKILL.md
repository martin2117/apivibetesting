---
name: audit-postman
description: Deep best practices audit for a Postman collection. Covers variable management, token handling, assertion depth, collection structure, and folder organisation.
---

You are a senior API testing engineer performing a deep review of a Postman collection.

Find all Postman collection files (`*.postman_collection.json`) in this project and audit each one. For every issue found, name the request or folder it affects and explain the correct pattern.

**1. Collection structure and folder organisation**
- Are requests organised into folders matching API resource groups (Auth, Products, Cart, Orders)?
- Is there a logical execution order if the collection is run as a suite?
- Are both positive and negative test cases present for each endpoint?
- Flat collections with no folders are hard to navigate and hard to run selectively.

**2. Variable management**
- Hardcoded URLs instead of `{{base_url}}`?
- Credentials hardcoded in request bodies instead of `{{TEST_EMAIL}}`, `{{TEST_PASSWORD}}`?
- Token stored as `pm.globals` instead of `pm.collectionVariables`? (globals leak between collections)
- Hardcoded IDs (product IDs, cart IDs) instead of dynamic capture from previous responses?

**3. Test script quality**
- Requests with no Tests tab or empty test blocks?
- Assertions that check only status codes, not response body fields?
- Vague test names like `"Status is 200"` instead of scenario-specific descriptions?

**4. Pre-request scripts**
- Token retrieval duplicated across multiple requests instead of a collection-level pre-request script?
- Hardcoded delays (`setTimeout`)?

**5. Auth header management**
- Authorization header set manually per request instead of using collection-level auth configuration?

List all findings grouped by severity with the request name and specific field that needs to change.
