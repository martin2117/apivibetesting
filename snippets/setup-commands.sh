#!/bin/bash
# Section 3 — Setup Commands
# Run these in your terminal to install all Python dependencies.
# Copy each block as needed — do not run the whole file at once.

# ─── Python virtual environment ───────────────────────────────────────────────

# Check Python version (need 3.8+)
python3 --version

# Create virtual environment
python3 -m venv venv

# Activate — Mac / Linux
source venv/bin/activate

# Activate — Windows (Command Prompt)
# venv\Scripts\activate.bat

# Activate — Windows (PowerShell)
# venv\Scripts\Activate.ps1

# ─── pytest + requests ────────────────────────────────────────────────────────

pip install pytest requests pytest-html

# Verify
pytest --version
python3 -c "import requests; print('requests', requests.__version__)"

# Note: python-dotenv is NOT installed — all environment variables are set
# in your shell profile (~/.zshrc / ~/.bashrc), not in a .env file.
# See snippets/shell-env-setup.sh and snippets/env-setup.md.

# ─── Robot Framework ──────────────────────────────────────────────────────────

pip install robotframework robotframework-requests

# Verify
robot --version

# ─── Newman (Postman CLI runner) ──────────────────────────────────────────────

npm install -g newman newman-reporter-html

# Verify
newman --version

# ─── Bruno CLI ────────────────────────────────────────────────────────────────

npm install -g @usebruno/cli

# Verify
bru --version
