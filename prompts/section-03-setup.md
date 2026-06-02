# Section 3 — Setup

## Course reference
| Prompt | Used in clip |
|--------|-------------|
| Prompt 1 — SSH Setup and Clone | **Section 3, Clip 2** — Fork and Clone the Course Repo |
| Prompt 2 — Python + pytest Setup | **Section 3, Clip 4** — Install Python + pytest + requests |
| Prompt 3 — Robot Framework Setup | **Section 3, Clip 5** — Install Robot Framework + RequestsLibrary |

---

## Prompt 1: SSH Setup and Clone
*Used in: Section 3, Clip 2 — "Fork and Clone the Course Repo"*

Open Cursor with any empty folder. Open the terminal (Ctrl+` on Windows/Linux, Cmd+` on Mac) and paste this prompt into the Cursor chat:

```
I have already forked the course repo on GitHub. Now I need to set up SSH
authentication and clone my fork. Help me do this step by step in the terminal.

1. Check if I already have an SSH key at ~/.ssh/id_ed25519.pub
2. If not, generate one with: ssh-keygen -t ed25519 -C "my-email"
3. Show me the command to copy my public key to the clipboard
   (use pbcopy on Mac, clip on Windows, xclip on Linux)
4. Remind me to add the key to GitHub at:
   github.com → Settings → SSH and GPG keys → New SSH key
5. Test the connection with: ssh -T git@github.com
6. Clone MY fork using SSH (I will provide my GitHub username):
   git clone git@github.com:MY-USERNAME/apivibetesting.git
7. Navigate into the cloned folder and confirm the three folders exist:
   techshop-api, prompts, snippets

Run each step one at a time and wait for my confirmation before continuing.
```

The full command reference is also available at `snippets/ssh-github-setup.sh` if you prefer to follow along without the prompt.

---

## Prompt 2: Python + pytest Setup
*Used in: Section 3, Clip 4 — "Install Python + pytest + requests"*

Open the Cursor terminal (Ctrl+` on Windows/Linux, Cmd+` on Mac) and paste this prompt into the Cursor chat:

```
Help me set up Python and the pytest testing environment for this project.
Run each step in the terminal and wait for my confirmation before continuing.

1. Check if Python is installed and confirm the version is 3.8 or higher:
   python3 --version
   If Python is not installed, tell me to go to python.org and install it first.

2. Create a virtual environment in the current project folder:
   python3 -m venv venv

3. Activate the virtual environment:
   - Mac/Linux: source venv/bin/activate
   - Windows: venv\Scripts\activate
   Confirm the (venv) prefix appears in the terminal prompt.

4. Install all required packages:
   pip install pytest requests pytest-html

5. Verify the installation:
   pytest --version
   python3 -c "import requests; print('requests', requests.__version__)"
   Both should print version numbers without errors.
   Note: python-dotenv is not needed — all environment variables are set
   in the shell profile, not in a .env file.

Run each step one at a time and wait for my confirmation before continuing.
```

---

## Prompt 3: Robot Framework Setup
*Used in: Section 3, Clip 5 — "Install Robot Framework + RequestsLibrary"*

Make sure your virtual environment is still active (you should see `(venv)` in your terminal prompt) then paste this prompt into the Cursor chat:

```
Help me install Robot Framework and its HTTP testing library.
Run each step in the terminal and wait for my confirmation before continuing.

1. Confirm the virtual environment is active by checking the terminal prompt
   shows (venv). If not, activate it first:
   - Mac/Linux: source venv/bin/activate
   - Windows: venv\Scripts\activate

2. Install Robot Framework and RequestsLibrary:
   pip install robotframework robotframework-requests

3. Verify the installation:
   robot --version
   python3 -c "from robot.libraries.Collections import Collections; print('Robot ok')"
   python3 -c "from RequestsLibrary import RequestsLibrary; print('RequestsLibrary ok')"
   All three should succeed without errors.

4. Confirm the full list of installed packages looks correct:
   pip list | grep -i -E "robot|requests|pytest"

Run each step one at a time and wait for my confirmation before continuing.
```

