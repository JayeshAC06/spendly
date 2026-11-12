# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Spendly — a Flask expense tracker (rupee-oriented copy) structured as a step-by-step student project. The landing, register/login pages and legal pages are done; the database layer and all feature logic are still stubs marked with "Step N" comments.

## Commands

```powershell
python -m venv venv; venv\Scripts\activate   # venv/ is gitignored
pip install -r requirements.txt
python app.py                                 # dev server, debug on, http://localhost:5001
pytest                                        # pytest + pytest-flask are installed
pytest path/to/test_file.py::test_name        # single test
```

No tests, linter, or formatter config exist yet.

## Architecture

- `app.py` — single Flask app with all routes inline. `/`, `/register`, `/login`, `/terms`, `/privacy` only render templates (no form handling yet). The remaining routes return placeholder strings tagged with their step: `/logout` (3), `/profile` (4), `/expenses/add` (7), `/expenses/<id>/edit` (8), `/expenses/<id>/delete` (9). Implement these in place by replacing the placeholder.
- `database/db.py` — comment-only stub. Spec: `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (`CREATE TABLE IF NOT EXISTS`), `seed_db()` (sample dev data). Nothing imports it yet.
- No sessions, `secret_key`, or auth exist yet; add them when implementing login/logout (Step 3).
- `templates/` — every page extends `base.html` (blocks: `title`, `head`, `content`, `scripts`). Use `url_for(...)` for links and static assets. `landing.html` carries its own inline JS in the `scripts` block.
- `static/css/style.css` — the single stylesheet (fonts: DM Serif Display / DM Sans from Google Fonts). `static/js/main.js` is an empty placeholder.
