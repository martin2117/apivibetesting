# Environment Variables Setup

All secrets and configuration values are stored as shell environment variables —
never in any file inside the project folder.

**Why not .env?** Cursor indexes your entire project folder. Any file inside it,
including .env, is visible to the AI. Shell profiles live in your home directory,
outside the project — Cursor cannot read them.

---

## All variables used in this course

Copy the exports from `snippets/shell-env-setup.sh` into your shell profile.

| Variable | What it is |
|----------|-----------|
| `BASE_URL` | TechShop API base URL (default: http://localhost:3000) |
| `TEST_EMAIL` | Login email for the TechShop API |
| `TEST_PASSWORD` | Login password for the TechShop API |
| `POSTMAN_API_KEY` | Postman API key for the MCP server (Section 5) |

---

## Mac / Linux

Open your shell profile:

```bash
# zsh (default on Mac)
open ~/.zshrc

# bash
open ~/.bashrc
```

Paste all exports from `snippets/shell-env-setup.sh` at the bottom, fill in real values, save, then reload:

```bash
source ~/.zshrc   # or source ~/.bashrc
```

Verify:

```bash
echo $BASE_URL
echo $TEST_EMAIL
echo $TEST_PASSWORD
echo $POSTMAN_API_KEY
```

---

## Windows

1. Open **Start → Edit the system environment variables**
2. Click **Environment Variables**
3. Under **User variables**, add each variable:
   - `BASE_URL` = `http://localhost:3000`
   - `TEST_EMAIL` = your email
   - `TEST_PASSWORD` = your password
   - `POSTMAN_API_KEY` = your Postman API key
4. Click OK, then restart your terminal and IDE

---

## GitHub Actions (CI)

In CI, variables come from GitHub Secrets — not from shell profiles or files.

1. Go to your repository → **Settings → Secrets and variables → Actions**
2. Add each as a repository secret:
   - `TEST_EMAIL`
   - `TEST_PASSWORD`

`BASE_URL` is set directly in the workflow file (`http://localhost:3000`) since
the test server runs inside the CI job and is not a secret.
`POSTMAN_API_KEY` is not needed in CI — Newman uses the exported collection file.

---

## How each tool reads variables

### Python (pytest)

Variables are read directly from the environment — no .env file, no dotenv:

```python
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")

@pytest.fixture
def auth_token():
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    if not email or not password:
        raise ValueError("TEST_EMAIL and TEST_PASSWORD must be set as environment variables")
    ...
```

### Robot Framework

```robot
*** Variables ***
${BASE_URL}    %{BASE_URL}
${EMAIL}       %{TEST_EMAIL}
${PASSWORD}    %{TEST_PASSWORD}
```

### Postman MCP config

The config file references the variable from the environment — no value stored in the file:

```json
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
```
