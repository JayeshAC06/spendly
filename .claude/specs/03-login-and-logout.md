# Spec: Login and Logout

## Overview
Make the `/login` page functional and implement `/logout`. Currently `GET /login` only renders the form (with a success banner after registration) and `/logout` returns a placeholder string. This step adds credential checking against the `users` table, a Flask session to remember the signed-in user, and a logout that clears it. It also makes the shared navbar session-aware. It builds on Step 2 (users can now exist) and is the prerequisite for the profile page and all expense routes (Steps 4+), which need to know who is signed in.

## Depends on
- Step 1 — Database setup (`users` table, `get_db()`).
- Step 2 — Registration (`get_user_by_email()`, werkzeug-hashed passwords, `/login?registered=1` banner).

## Routes
- `GET /login` — render the sign-in form; if already signed in, redirect to `/profile` — public
- `POST /login` — validate credentials; on success store `user_id` in the session and redirect to `/profile`; on failure re-render the form with a generic error (HTTP 400) — public
- `GET /logout` — clear the session and redirect to `/login` — logged-in (harmless if not signed in; still redirects to `/login`)

No other new routes. `/profile` remains a stub (Step 4) and is only used as the redirect target.

## Database changes
No database changes. The existing `users` table has `email` (UNIQUE) and `password_hash`.

New helper in `database/db.py` (DB logic must not live in routes):
- `get_user_by_id(user_id)` — return the matching `sqlite3.Row` or `None`. Used to resolve the signed-in user for templates.

`get_user_by_email()` (from Step 2) is reused for credential lookup.

## Templates
- **Create:** none
- **Modify:** `templates/login.html`
  - Re-populate the `email` input with the submitted value after a failed attempt (never the password).
  - Keep the existing `{% if error %}` and `{% if registered %}` blocks.
- **Modify:** `templates/base.html`
  - Navbar: when a user is signed in, show their name and a "Sign out" link (`url_for('logout')`) instead of "Sign in" / "Get started". When signed out, keep the current links.

## Files to change
- `app.py` — set `app.secret_key`; allow `POST` on `/login`; add credential check and session handling; implement `/logout`; add a context processor exposing `current_user` to templates; import new db helper and `check_password_hash`, `session`
- `database/db.py` — add `get_user_by_id()`
- `templates/login.html` — retain entered email on error
- `templates/base.html` — session-aware navbar
- `static/css/style.css` — only if the navbar user/sign-out link needs styling (CSS variables only)

## Files to create
- `.claude/specs/03-login-and-logout.md` (this spec)
- `tests/test_login_logout.py` — pytest-flask tests covering the checklist below

## New dependencies
No new dependencies. Use `werkzeug.security.check_password_hash` and Flask's built-in `session`.

## Validation and behaviour rules
- `email`: trimmed and lower-cased before lookup
- `password`: taken as-is (not trimmed)
- Unknown email **or** wrong password → the same generic error "Invalid email or password." (HTTP 400) so accounts cannot be enumerated
- Missing email or password fields → same generic error
- On success: `session.clear()` first (avoid session fixation), then `session["user_id"] = user["id"]`
- `secret_key` is read from the `SECRET_KEY` environment variable, falling back to a clearly-named dev default so the app still starts locally
- Logout must use the session only; it must not touch the database
- If `session["user_id"]` refers to a user that no longer exists, treat the visitor as signed out

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders), no f-strings in SQL
- Passwords verified with werkzeug (`check_password_hash`); never log or echo plaintext
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `url_for()` for every internal link and redirect
- DB logic only in `database/db.py`; routes fetch input, call helpers, render or redirect
- Use `abort()` for HTTP errors, not bare strings; never return a raw string from `/login` or `/logout`
- Do not implement other stub routes (`/profile`, expenses) and do not add login-required decorators beyond what this step needs
- Do not change the port (5001)

## Definition of done
- [ ] `GET /login` renders the form with no error; `/login?registered=1` still shows the success banner
- [ ] Logging in as the seeded demo user (`demo@spendly.com` / `demo123`) redirects to `/profile`
- [ ] A user registered in Step 2 can log in with their email (any letter case) and password
- [ ] Wrong password and unknown email both show "Invalid email or password." with HTTP 400 and no session is created
- [ ] After a failed attempt, the email field keeps the submitted value and the password field is empty
- [ ] After login, the navbar shows the user's name and a "Sign out" link, and no "Sign in" / "Get started" links
- [ ] Visiting `/login` while signed in redirects to `/profile`
- [ ] `GET /logout` clears the session, redirects to `/login`, and the navbar shows "Sign in" again
- [ ] After logout, the session cookie no longer authenticates the user (navbar is signed-out)
- [ ] The login form action and the Sign out link use `url_for`, not hardcoded paths
- [ ] All SQL uses parameterised queries
- [ ] App starts with `python app.py` on port 5001 with no errors; registration still works
