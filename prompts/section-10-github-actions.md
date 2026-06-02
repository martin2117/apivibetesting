# Section 10 — GitHub Actions Pipeline

## Course reference
| Prompt | Used in clip |
|--------|-------------|
| Prompt 1 — Generate the Full CI Workflow | **Section 10, Clip 2** — Antigravity IDE Writes the .yml File |
| Prompt 2 — Fix Pipeline from GitHub Annotations | **Section 10, Clip 3** — Debugging the Pipeline |
| Prompt 3 — Switch to Fixed App in CI | **Section 10, Clip 6** — Running on the Fixed App in CI |
| Prompt 4 — Commit and Push Workflow to GitHub | **Section 10, Clip 2** — Antigravity IDE Writes the .yml File |
| Prompt 5 — Add GitHub Secrets for Credentials | **Section 10, Clip 3** — Debugging the Pipeline |
| Prompt 6 — Add Fail-on-Failure Check and Summary | **Section 10, Clip 4** — Making the Pipeline Fail on Test Failures |
| Prompt 7 — Verify All Suites Locally Against Fixed App | **Section 10, Clip 5** — Verifying Locally Before Touching the Pipeline |

---

## Prompt 1: Generate the Full CI Workflow
*Used in: Section 10, Clip 2 — "Antigravity IDE Writes the .yml File"*

```
Create a GitHub Actions workflow file at .github/workflows/api-tests.yml.

Requirements:
- Trigger on: push and pull_request to the main branch
- Run on: ubuntu-latest
- Job name: api-tests

Steps in order:

1. Checkout repository
   uses: actions/checkout@v4

2. Set up Node.js 20
   uses: actions/setup-node@v4

3. Install TechShop API dependencies
   run: npm install inside techshop-api/broken-app

4. Start the TechShop API in the background
   run: node techshop-api/broken-app/server.js &
   (background process, continues to next step)

5. Wait for the server to be ready
   run: sleep 5 then curl --retry 5 --retry-delay 2 http://localhost:3000/health

6. Install Newman and the HTML reporter
   run: npm install -g newman newman-reporter-html

7. Run Postman collection with Newman
   run: newman run techshop.postman_collection.json
        --env-var base_url=http://localhost:3000
        --reporters cli,html
        --reporter-html-export newman-report.html
   continue-on-error: true
   id: newman

8. Install Bruno CLI
   run: npm install -g @usebruno/cli

9. Run Bruno collection
   run: bru run techshop-bruno/ --env local
   continue-on-error: true
   id: bruno

10. Set up Python 3.11
    uses: actions/setup-python@v5

11. Install Python dependencies
    run: pip install pytest requests pytest-html python-dotenv

12. Run pytest
    run: pytest test_techshop.py -v --html=pytest-report.html --self-contained-html
    env:
      BASE_URL: http://localhost:3000
      TEST_EMAIL: ${{ secrets.TEST_EMAIL }}
      TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
    continue-on-error: true
    id: pytest

13. Install Robot Framework dependencies
    run: pip install robotframework robotframework-requests

14. Run Robot Framework
    run: robot --variable BASE_URL:http://localhost:3000
              --outputdir robot-results techshop.robot
    env:
      TEST_EMAIL: ${{ secrets.TEST_EMAIL }}
      TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
    continue-on-error: true
    id: robot

    Note: add TEST_EMAIL and TEST_PASSWORD as GitHub repository secrets:
    Settings → Secrets and variables → Actions → New repository secret
    Never hardcode credentials in the workflow file.

15. Upload pytest HTML report as artifact
    uses: actions/upload-artifact@v4
    if: always()
    with name: pytest-report, path: pytest-report.html

16. Upload Robot Framework report as artifact
    uses: actions/upload-artifact@v4
    if: always()
    with name: robot-report, path: robot-results/

17. Upload Newman report as artifact
    uses: actions/upload-artifact@v4
    if: always()
    with name: newman-report, path: newman-report.html

18. Final status check — fail the job if any test step failed
    if: always()
    run: |
      if [ "${{ steps.newman.outcome }}" = "failure" ] ||
         [ "${{ steps.bruno.outcome }}" = "failure" ] ||
         [ "${{ steps.pytest.outcome }}" = "failure" ] ||
         [ "${{ steps.robot.outcome }}" = "failure" ]; then
        echo "One or more test suites failed"
        exit 1
      fi
```

---

## Prompt 2: Fix Pipeline from GitHub Annotations
*Used in: Section 10, Clip 3 — "Debugging the Pipeline"*

```
I have a failing GitHub Actions run. Here are the error annotations
from the failed run:

[PASTE YOUR ANNOTATIONS HERE]

Read the errors and fix .github/workflows/api-tests.yml so the pipeline
runs correctly. Tell me if I also need to add any GitHub Secrets or
repository variables, and what values they should have.
```

---

## Prompt 3: Switch to Fixed App in CI
*Used in: Section 10, Clip 6 — "Running on the Fixed App in CI"*

```
Update .github/workflows/api-tests.yml to run against the fixed app instead
of the broken app. Change the npm install path and the server start command
to use techshop-api/fixed-app instead of techshop-api/broken-app.
All other steps stay the same.
```

---

## Prompt 4: Commit and Push Workflow to GitHub
*Used in: Section 10, Clip 2 — "Antigravity IDE Writes the .yml File"*

```
Help me commit the new GitHub Actions workflow file and push it to GitHub.
Run each step in the terminal and wait for my confirmation before continuing.

1. Check what files have changed:
   git status

2. Stage the workflow file:
   git add .github/workflows/api-tests.yml

3. Commit with a clear message:
   git commit -m "Add GitHub Actions workflow to run all API test suites"

4. Push to the main branch:
   git push origin main

5. Tell me to open the Actions tab on my GitHub repository to watch
   the first workflow run trigger automatically
```

---

## Prompt 5: Add GitHub Secrets for Credentials
*Used in: Section 10, Clip 3 — "Debugging the Pipeline"*

```
Guide me through adding the test credentials as GitHub repository secrets
so the CI pipeline can authenticate with the TechShop API securely.

1. Explain that I need to add two secrets to my GitHub repository:
   - TEST_EMAIL  (the email used to log into the TechShop API)
   - TEST_PASSWORD  (the password for that account)

2. Give me the exact navigation path in GitHub:
   Repository → Settings → Secrets and variables → Actions → New repository secret

3. Tell me to add TEST_EMAIL first, then TEST_PASSWORD

4. Confirm that secrets are never visible in logs or workflow output
   once they are saved — GitHub masks them automatically

5. Show me how they are referenced in the workflow file:
   env:
     TEST_EMAIL: ${{ secrets.TEST_EMAIL }}
     TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
```

---

## Prompt 6: Add Fail-on-Failure Check and Pipeline Summary
*Used in: Section 10, Clip 4 — "Making the Pipeline Fail on Test Failures"*

```
Update .github/workflows/api-tests.yml to do two things:

1. Add a final step that fails the overall job if any test suite failed.
   Each runner step (newman, bruno, pytest, robot) uses continue-on-error: true
   so they all run even if one fails. The final step should check the outcome
   of each and exit 1 if any returned failure:

   - name: Fail job if any suite failed
     if: always()
     run: |
       if [ "${{ steps.newman.outcome }}" = "failure" ] ||
          [ "${{ steps.bruno.outcome }}" = "failure" ] ||
          [ "${{ steps.pytest.outcome }}" = "failure" ] ||
          [ "${{ steps.robot.outcome }}" = "failure" ]; then
         echo "One or more test suites failed"
         exit 1
       fi

2. Add a summary step that runs before the fail check (if: always()) and
   writes a clean status table to the GitHub Actions job summary panel:

   - name: Pipeline summary
     if: always()
     run: |
       echo "## Test Suite Results" >> $GITHUB_STEP_SUMMARY
       echo "| Suite | Result |" >> $GITHUB_STEP_SUMMARY
       echo "|-------|--------|" >> $GITHUB_STEP_SUMMARY
       echo "| Newman | ${{ steps.newman.outcome }} |" >> $GITHUB_STEP_SUMMARY
       echo "| Bruno | ${{ steps.bruno.outcome }} |" >> $GITHUB_STEP_SUMMARY
       echo "| pytest | ${{ steps.pytest.outcome }} |" >> $GITHUB_STEP_SUMMARY
       echo "| Robot Framework | ${{ steps.robot.outcome }} |" >> $GITHUB_STEP_SUMMARY
```

---

## Prompt 7: Verify All Suites Locally Against Fixed App
*Used in: Section 10, Clip 5 — "Verifying Locally Before Touching the Pipeline"*

```
Help me switch from the broken app to the fixed app and verify all four
test suites pass locally before I update the pipeline.
Run each step in the terminal and wait for my confirmation before continuing.

1. Stop the running broken app server (kill the background process):
   pkill -f "node.*broken-app" || true

2. Start the fixed app:
   cd techshop-api/fixed-app && npm install && npm start &
   Wait 3 seconds, then verify it is up:
   curl -s http://localhost:3000/health
   The response should show "environment":"fixed" — if not, stop and tell me.

3. Run Newman:
   newman run techshop.postman_collection.json \
     --env-var base_url=http://localhost:3000 \
     --reporters cli
   Report how many tests passed and failed.

4. Run Bruno:
   bru run techshop-bruno/ --env local
   Report how many tests passed and failed.

5. Run pytest:
   pytest test_techshop.py -v
   Report how many tests passed and failed.

6. Run Robot Framework:
   robot --variable BASE_URL:http://localhost:3000 techshop.robot
   Report how many tests passed and failed.

7. Give me a final summary table:
   | Suite | Passed | Failed |
   If any suite has failures, show me the failing test names and
   what the assertion expected versus what it got, so I can debug
   before touching the pipeline.
```
