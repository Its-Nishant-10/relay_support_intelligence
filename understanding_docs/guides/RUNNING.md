# Running Relay: Beginner Guide

This guide shows how to run Relay on your own computer. Relay is a Streamlit
web application that predicts a support ticket's category, priority, queue, and
sentiment. You do not need an API key or Docker.

## What you need

Install these two programs before starting:

1. **Python 3.10 or newer**: download it from [python.org](https://www.python.org/downloads/).
2. **Git**: install it from [git-scm.com](https://git-scm.com/downloads) if you are downloading the project from GitHub.

On Windows, select **Add Python to PATH** during the Python installation.

## Step 1: Get the project

If the project is already on your computer, open a terminal in the project
folder. This is the folder that contains `app.py`.

To download it from GitHub, replace the URL with your repository URL:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Check that you are in the correct folder:

```bash
# macOS/Linux
ls

# Windows PowerShell
dir
```

You should see `app.py`, `requirements.txt`, `relay`, and `models`.

## Step 2: Create a virtual environment

Run this once from the project folder:

```bash
python -m venv .venv
```

A virtual environment keeps Relay's packages separate from other Python
projects on your computer.

## Step 3: Activate the environment

Run the command for your operating system every time you open a new terminal.

### macOS or Linux

```bash
source .venv/bin/activate
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```bat
.venv\Scripts\activate.bat
```

When activation works, you will usually see `(.venv)` at the beginning of the
terminal line.

## Step 4: Install the packages

With the environment activated, run:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

This may take a few minutes. The packages include Streamlit, the machine
learning libraries, and the test tools.

## Step 5: Check the model files

Relay needs these four saved models in the `models/` folder:

```text
models/category_model.joblib
models/priority_model.joblib
models/queue_model.joblib
models/sentiment_model.joblib
```

If they are already present, continue to the next step. If they are missing,
download the training data and build the models:

```bash
python scripts/download_dataset.py
python scripts/train.py
```

This optional process needs an internet connection and can take some time. You
do not need to repeat it every time you run the application.

## Step 6: Start the web application

Run:

```bash
streamlit run app.py
```

Streamlit prints a local address in the terminal. Open this address in your
browser, usually:

```text
http://localhost:8501
```

Try the application by opening **Tickets -> New Ticket** and entering a
subject and description. For example:

```text
Subject: Payment failed
Description: My card payment was declined twice and I need help.
```

To stop the application, return to the terminal and press `Ctrl+C`.

## Start the application later

After the first-time setup, open a terminal in the project folder and run:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1

streamlit run app.py
```

## Run the tests

Tests are optional, but useful after making code changes:

```bash
python -m pytest -q
```

A successful run ends with a message such as `7 passed`.

## Publish on GitHub and Streamlit

You do not need a `Dockerfile` for Streamlit Community Cloud. Push the project
to GitHub, then create an app at [share.streamlit.io](https://share.streamlit.io/).

Use these settings:

- **Repository**: your GitHub repository
- **Branch**: usually `main`
- **Main file path**: `app.py`

Make sure the four files in `models/` are included in GitHub. The application
cannot start without them. Do not commit `.venv/`, `.env` files, passwords,
API keys, or `triage_logs.jsonl`.

## Optional: Run the API

Relay also includes a FastAPI service. Start it in a second terminal after
activating the virtual environment:

```bash
uvicorn api:app --reload
```

Open the interactive API page at
`http://127.0.0.1:8000/docs`. The health check is available at
`http://127.0.0.1:8000/health`.

To test a prediction from macOS/Linux or Windows with `curl`:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"subject":"Payment failed","description":"My card payment failed twice."}'
```

## Common problems

### `python` is not recognized

Python is not installed or is not on your PATH. Install Python again and select
**Add Python to PATH** on Windows. You can also try `python3` on macOS/Linux.

### `No module named streamlit` or another missing package

Activate the virtual environment and install the packages again:

```bash
python -m pip install -r requirements.txt
```

### `Missing trained artifacts`

The model files are missing from `models/`. Download the data and train the
models, or restore the four `.joblib` files from the project repository.

### Port 8501 is already in use

Start Streamlit on another port:

```bash
streamlit run app.py --server.port 8502
```

### The dashboard has no activity yet

The dashboard shows tickets analyzed during the current workspace session. Go
to **Tickets -> New Ticket** and analyze a ticket first.

## Where the important files are

- `app.py`: the Streamlit screens
- `relay/predictor.py`: loads models and makes predictions
- `relay/policy.py`: applies business rules after prediction
- `config/business_rules.json`: routing policy settings
- `models/`: saved model files required at runtime
- `api.py`: optional FastAPI service
- `scripts/`: optional dataset download and model training
- `tests/`: automated tests
