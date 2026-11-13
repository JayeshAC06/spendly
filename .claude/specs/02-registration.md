# Spec: Registration

## Overview
Make the existing `/register` page functional. Currently `GET /register` only renders `register.html`; the form posts to `/register` but the route accepts no POST. This step adds form handling: validate input, create a user row with a hashed password. On success, the user is shown with a success message and then send the new user to the login page. It builds directly on the Step 1 data layer and is the prerequisite for login/logout (Step 3).

## Depends on
- Step 1 — Database setup (`users` table, `get_db()`, `init_db()`).

## Routes
- `GET /register` — render the registration form (already exists; unchanged behaviour) — public
- `POST /register` — validate form, create user, redirect to `/login?registered=1` on success; re-render form with an error message (HTTP 400) on failure — public
- `GET /login` — now reads the `registered` query arg and shows a success banner when it equals `1` (no `secret_key`/`flash`) — public

No other new routes.

## Database changes
No database changes. The existing `users` table already has `name`, `email` (UNIQUE, NOT NULL), `password_hash` and `created_at`.

New helpers in `database/db.py` (DB logic must not live in routes):
- `get_user_by_email(email)` — return the matching `sqlite3.Row` or `None`.
- `create_user(name, email, password_hash)` — insert a user and return the new id. Must let `sqlite3.IntegrityError` propagate (or return `None`) so the route can handle a duplicate-email race.

## Templates
- **Create:** none
- **Modify:** `templates/register.html`
  - Change `action="/register"` to `action="{{ url_for('register') }}"` (no hardcoded URLs).
  - Re-populate `name` and `email` inputs with submitted values after a validation error (never re-populate the password).
  - Keep the existing `{% if error %}` block for displaying errors.
- **Modify:** `templates/login.html` — show an `.auth-success` banner when `registered` is true; form action via `url_for('login')`.

## Files to change
- `app.py` — allow `POST` on `/register`, add form handling, import new db helpers; `login()` passes `registered`
- `database/db.py` — add `get_user_by_email()` and `create_user()`
- `templates/register.html` — form action via `url_for`, retain entered values on error
- `templates/login.html` — success banner
- `static/css/style.css` — add `.auth-success` (CSS variables only)

## Files to create
- `.claude/specs/02-registration.md` (this spec)
- Optionally `tests/test_registration.py` — pytest-flask tests covering the checklist below

## New dependencies
No new dependencies. Use `werkzeug.security.generate_password_hash` (already installed).

## Validation rules
- `name`: required, trimmed, non-empty
- `email`: required, trimmed, lower-cased, must contain `@` with text on both sides
- `password`: required, minimum 8 characters (matches the form placeholder)
- Email must not already exist → error "An account with that email already exists."
- On any failure: return the template with an `error` string and HTTP 400; never return a raw string.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders), no f-strings in SQL
- Passwords hashed with werkzeug (`generate_password_hash`); never store or log plaintext
- Use CSS variables — never hardcode hex values (only new CSS is `.auth-success`; reuse `.auth-error`, `.form-input`, etc.)
- All templates extend `base.html`
- Use `url_for()` for every internal link and redirect
- DB logic only in `database/db.py`; the route fetches input, calls helpers, renders or redirects
- Use `abort()` for HTTP errors, not bare strings
- Do not implement other stub routes (`/logout`, `/profile`, expenses) and do not add sessions/`secret_key` — that is Step 3
- Do not change the port (5001)

## Definition of done
- [ ] `GET /register` still renders the form with no errors
- [ ] Submitting valid name, email and password (8+ chars) creates a row in `users` and redirects to `/login`
- [ ] `/login?registered=1` shows a success banner; `/login` without the flag shows none
- [ ] The stored `password_hash` is a werkzeug hash, not the plaintext password
- [ ] Registering the same email again (any letter case) shows "An account with that email already exists." and creates no second row
- [ ] Empty name, invalid email, or password under 8 characters re-renders the form with a clear error and creates no row
- [ ] After an error, the name and email fields keep the submitted values and the password field is empty
- [ ] The form action uses `url_for('register')`, not a hardcoded path
- [ ] All SQL uses parameterised queries
- [ ] App starts with `python app.py` on port 5001 with no errors, and the demo user from seeding is unaffected
