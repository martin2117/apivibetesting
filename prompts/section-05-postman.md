# Section 5 — Postman + Newman

## Course reference
| Prompt | Used in clip |
|--------|-------------|
| Prompt 1 — Create Postman Collection via MCP | **Section 5, Clip 3** — Cursor Creates the Collection via MCP |
| Prompt 2 — Export Collection for Newman | **Section 5, Clip 5** — Newman CLI |
| Prompt 3 — Fix a Failing Test | **Section 5, Clip 4** — Running the Collection and Reading Results |
| Prompt 4 — Set Up Postman MCP Config | **Section 5, Clip 2** — Setting Up the Postman MCP Server |
| Prompt 5 — Install Newman and Run Collection | **Section 5, Clip 5** — Newman CLI |

---

## Prompt 1: Create Postman Collection via MCP
*Used in: Section 5, Clip 3 — "Cursor Creates the Collection via MCP"*

Use this prompt after configuring the Postman MCP server (Prompt 4 below).
Make sure `swagger.json` and `test-ideas.md` are in your project folder.

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get {"status":"ok"...} — the server is up, continue.
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

Use the Postman MCP to create a new collection in my Postman workspace
called "TechShop API Tests".

Read two files:
- swagger.json — the full API spec with all endpoints, schemas, required
  fields, authentication requirements, and documented response codes
- test-ideas.md — the test strategy we derived from the spec in Section 4,
  listing happy paths, negative tests, and auth requirements per endpoint

Use both files as your source of truth. swagger.json defines the contract.
test-ideas.md defines what to test. Together they give you complete coverage.

Based on these files:
- Create a folder for each tag (Auth, Products, Cart, Orders)
- For each endpoint, generate requests covering every scenario listed
  in test-ideas.md, verified against the response codes in swagger.json
- Write pm.test assertions for each request checking the expected status code
- After the login request, save the token from the response body
  into a collection variable called authToken
- Use {{authToken}} in the Authorization header for all endpoints
  that require bearerAuth
- Use {{base_url}} as the base URL variable throughout
```

---

## Prompt 2: Export Collection for Newman
*Used in: Section 5, Clip 5 — "Newman CLI"*

```
Use the Postman MCP to fetch the TechShop API Tests collection from my
Postman workspace and save it as techshop.postman_collection.json in the
project root.

Steps:
1. Use the Postman MCP to find the collection named "TechShop API Tests"
   in my workspace and retrieve its full JSON.
2. Write the JSON to techshop.postman_collection.json in the project root.
3. Confirm the file was created and show me the path.
```

---

## Prompt 3: Fix a Failing Test
*Used in: Section 5, Clip 4 — "Running the Collection and Reading Results"*

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

The test for [endpoint] is failing with status [actual] but asserting [expected].
Read swagger.json and check what response code the spec defines for this scenario.
Update the pm.test assertion to match the spec.
```

---

## Prompt 4: Set Up Postman MCP Config
*Used in: Section 5, Clip 2 — "Setting Up the Postman MCP Server"*

The `POSTMAN_API_KEY` environment variable was already set in Section 3.
Paste this prompt into the Cursor chat — do not type or paste the key itself.

```
Help me configure the Postman MCP server. The API key is already stored
as a system environment variable called POSTMAN_API_KEY — do not ask me
for it and do not echo it.

1. Verify the key is available in the environment (without revealing it):
   Run in the terminal:
   - Mac/Linux: [ -n "$POSTMAN_API_KEY" ] && echo "Key is set" || echo "Key is NOT set"
   - Windows PowerShell: if ($env:POSTMAN_API_KEY) { "Key is set" } else { "Key is NOT set" }
   If the result is "Key is NOT set", stop and tell me to go back to
   Section 3 and complete the environment variables setup first.

2. Detect which AI IDE I am using and create the MCP config file:
   - Cursor: create or update ~/.cursor/mcp.json
   - VS Code: create or update .vscode/mcp.json in the project root

   Write this config — no secrets inside, the key is read from the environment:
   {
     "mcpServers": {
       "postman": {
         "command": "npx",
         "args": ["-y", "@postman/mcp-server"],
         "env": {
           "POSTMAN_API_KEY": "${POSTMAN_API_KEY}"
         }
       }
     }
   }

3. Confirm the config file was written and show me the path.

4. Tell me to fully restart my AI IDE so it picks up the environment.

5. After I confirm I have restarted, tell me to verify in two ways:
   - Open my AI IDE Settings → MCP and confirm the Postman server
     shows a green status indicator
   - In this chat, type: what MCP tools do you have available?
     and confirm the Postman tools appear in the response
```

---

## Prompt 5: Install Newman and Run Collection
*Used in: Section 5, Clip 5 — "Newman CLI"*

Make sure `techshop.postman_collection.json` is in the project root before running.

```
First, check if the TechShop API is running on localhost:3000:
  curl -s http://localhost:3000/health
If you get a connection error — start it:
  cd techshop-api/broken-app && npm start &
Wait 3 seconds, then verify: curl -s http://localhost:3000/health
If it still fails, stop and tell me.

Once the server is confirmed running:

Help me install Newman and run the Postman collection from the terminal.
Run each step and wait for my confirmation before continuing.

1. Install Newman and the HTML reporter globally:
   npm install -g newman newman-reporter-html

2. Verify the install:
   newman --version

3. Run the collection against the local API:
   newman run techshop.postman_collection.json \
     --env-var base_url=http://localhost:3000 \
     --reporters cli,html \
     --reporter-html-export newman-report.html

4. Tell me how many tests passed and failed from the summary output

5. Confirm that newman-report.html was created in the project folder
```
