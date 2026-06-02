#!/bin/bash
# All environment variables needed for this course.
# Follow the section for your operating system below.

# ══════════════════════════════════════════════════════════════════════════════
# MAC / LINUX
# ══════════════════════════════════════════════════════════════════════════════
#
# Step 1 — Run these commands to permanently append variables to your profile.
# zsh (default on Mac):

echo 'export BASE_URL=http://localhost:3000' >> ~/.zshrc
echo 'export TEST_EMAIL=demo@techshop.com' >> ~/.zshrc
echo 'export TEST_PASSWORD=password123' >> ~/.zshrc
echo 'export POSTMAN_API_KEY=' >> ~/.zshrc   # fill in the value after Postman setup in Section 5

# bash (Linux / some Mac setups) — replace ~/.zshrc with ~/.bashrc in all lines above

# Step 2 — REQUIRED: reload the profile in the current terminal session.
# The variables are written to the file but the current session does not
# know about them yet until you run this:

source ~/.zshrc     # or source ~/.bashrc for bash users

# Step 3 — Verify each variable prints its value:

echo $BASE_URL
echo $TEST_EMAIL
echo $TEST_PASSWORD


# ══════════════════════════════════════════════════════════════════════════════
# WINDOWS
# ══════════════════════════════════════════════════════════════════════════════
#
# Option A — GUI (System Properties)
# 1. Press Win + S, search for "Edit the system environment variables", open it
# 2. Click "Environment Variables"
# 3. Under "User variables", click "New" for each variable below:
#
#    Variable name        Variable value
#    BASE_URL             http://localhost:3000
#    TEST_EMAIL           demo@techshop.com
#    TEST_PASSWORD        password123
#    POSTMAN_API_KEY      (fill in after Postman setup in Section 5)
#
# 4. Click OK on all dialogs, then restart your terminal and IDE
#
# Verify — run in Command Prompt or PowerShell:
#    echo %BASE_URL%          (Command Prompt)
#    echo $env:BASE_URL       (PowerShell)
#
#
# Option B — PowerShell (run each line, no administrator needed)
#
# [System.Environment]::SetEnvironmentVariable("BASE_URL", "http://localhost:3000", "User")
# [System.Environment]::SetEnvironmentVariable("TEST_EMAIL", "demo@techshop.com", "User")
# [System.Environment]::SetEnvironmentVariable("TEST_PASSWORD", "password123", "User")
# [System.Environment]::SetEnvironmentVariable("POSTMAN_API_KEY", "", "User")
#
# Restart your terminal after running, then verify:
# echo $env:BASE_URL
# echo $env:TEST_EMAIL
# echo $env:TEST_PASSWORD
