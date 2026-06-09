---
name: refactor-ci-pipeline
description: Updates .github/workflows/api-tests.yml to match the refactored test suite structure — new pytest directory layout, split Robot Framework files, updated artifact paths. Verifies the pipeline runs correctly after changes.
---

You are a senior DevOps and test automation engineer. The test suites in this project have been refactored — file locations, directory structure, and command arguments may have changed. Update the GitHub Actions pipeline to match the current structure.

**STEP 1 — Discover the current test structure**
Before touching the YAML, read the project to understand what exists:
- Find all pytest files: where are they? Is there a `tests/` directory with subdirectories, or a single `test_techshop.py` in the root?
- Find all Robot Framework files: one `.robot` file or multiple split by resource in a `tests/` folder?
- Find the Bruno collection folder name and location
- Find the Postman collection JSON file name and location
- Read `.github/workflows/api-tests.yml` to see what commands it currently runs

**STEP 2 — Update the pytest command**
If pytest files have been moved into a `tests/` directory structure, update the pytest step:

Old (single file):
```yaml
- name: Run pytest
  run: pytest test_techshop.py -v --html=pytest-report.html --self-contained-html
```

New (directory structure):
```yaml
- name: Run pytest
  run: pytest tests/ -v --html=pytest-report.html --self-contained-html
```

If there are now `conftest.py` files in subdirectories, confirm pytest discovers them correctly with the new path.

**STEP 3 — Update the Robot Framework command**
If Robot Framework tests have been split into multiple `.robot` files in a `tests/` directory:

Old (single file):
```yaml
- name: Run Robot Framework
  run: robot --variable BASE_URL:http://localhost:3000 techshop.robot
```

New (directory):
```yaml
- name: Run Robot Framework
  run: robot --variable BASE_URL:http://localhost:3000 --outputdir robot-results tests/
```

**STEP 4 — Update Bruno command if folder was renamed**
If the Bruno collection folder was renamed or restructured during refactoring, update:
```yaml
- name: Run Bruno
  run: bru run techshop-bruno/ --env local
```
Adjust the folder name to match the current structure.

**STEP 5 — Update artifact paths**
Check that the artifact upload steps still reference the correct report file paths after any directory changes:
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: pytest-report
    path: pytest-report.html  # confirm this path still exists after refactoring
```

**STEP 6 — Update the fail-on-failure step**
Ensure the step IDs referenced in the final failure check (`steps.pytest.outcome`, `steps.robot.outcome`) still match the step IDs in the updated YAML.

**STEP 7 — Commit and verify**
After updating the YAML:
1. Stage all changes: `git add .`
2. Commit: `git commit -m "Update CI pipeline to match refactored test structure"`
3. Push: `git push origin main`
4. Tell me to open the GitHub Actions tab to confirm the pipeline runs correctly with the new structure.

If any step fails after the push, read the error output and fix it before finishing.
