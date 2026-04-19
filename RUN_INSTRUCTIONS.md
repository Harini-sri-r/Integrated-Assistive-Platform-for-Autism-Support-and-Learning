# ALP PRO — Run instructions

## What this is

A local **Autism Learning Platform** (Flask) with games, learning modules, a journal, family-friendly progress views, and an optional AI chat companion. **Wellness labels in the app are informal** (from journal + in-app scores), not medical assessments.

## Requirements

- **Python 3.10–3.12** recommended (avoid experimental 3.14+ for class projects).
- A modern browser; allow **camera** if you use face-related features (if enabled in your build).

## Project folder

Use the folder that contains `app.py` and this file, for example:

`c:\Users\harin\OneDrive\Documents\copied folder autism`

(If you moved the project, use your actual path.)

## Setup

1. **Open a terminal** in the project directory.

2. **Create/activate a virtual environment** (recommended):

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration (optional, for real use / sharing):**

   - Copy `.env.example` to `.env` in the same folder as `app.py`.
   - Set a long random `SECRET_KEY` (do not share it or commit `.env`).
   - Optional: `GEMINI_API_KEY` for the chatbot’s LLM assistant; without it, the rule-based chat still works.
   - Optional: `DATABASE_URL` to override the default SQLite file (see below).

## Database file (SQLite)

By default the app uses:

- **Path:** `instance/platform_v3.db` (the `instance` folder is created automatically).

**Troubleshooting DB errors:** stop the app, back up or remove `instance/platform_v3.db`, and start again to recreate empty tables.

**If you have an old database** in the project root named `platform_v3.db` from a previous version, either:

- Move it to `instance/platform_v3.db`, or  
- Start fresh and re-register (simpler for a clean “final” build).

## Run the server

```bash
python app.py
```

Open: **http://127.0.0.1:5000**

Debug mode is on by default for local work. For production, set `FLASK_DEBUG=false` in the environment and use a proper WSGI server (e.g. gunicorn) and HTTPS.

## Optional: Face / emotion features

If your build includes them, use your browser’s camera permission. Model files, if any, should live under `static/models` (see your project’s file layout).

## What we fixed in the “final” pack

- **SECRET_KEY** and database path are **environment-driven** (see `.env.example`).
- **No duplicate** `/learning/magic-storybook` route.
- **Wellness copy** makes clear the app is **not** giving a clinical diagnosis.
- **Family insights** UI text and **accessibility** (skip link to main content).
- **Stray duplicate** `*-Harini_Sri.*` files removed in favor of the main templates.

If something still fails, check the terminal for import errors and ensure you used the same Python that has the venv activated.
