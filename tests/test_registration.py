import re
import sqlite3

import pytest
from werkzeug.security import check_password_hash

import database.db as db

VALID = {"name": "Test User", "email": "test@example.com", "password": "password123"}
DUPLICATE_MSG = "An account with that email already exists."


def user_count():
    conn = db.get_db()
    try:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    finally:
        conn.close()


def test_get_register_ok(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"auth-error" not in response.data


def test_register_success_redirects(client):
    before = user_count()
    response = client.post("/register", data=VALID)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login?registered=1")
    assert user_count() == before + 1


def test_password_is_hashed(client):
    client.post("/register", data=VALID)
    row = db.get_user_by_email(VALID["email"])
    assert row["password_hash"] != VALID["password"]
    assert check_password_hash(row["password_hash"], VALID["password"])


def test_login_success_banner(client):
    assert b"auth-success" in client.get("/login?registered=1").data
    assert b"auth-success" not in client.get("/login").data
    assert b"auth-success" not in client.get("/login?registered=0").data


@pytest.mark.parametrize("email", ["test@example.com", "TEST@Example.COM"])
def test_duplicate_email_rejected(client, email):
    client.post("/register", data=VALID)
    before = user_count()
    response = client.post("/register", data={**VALID, "email": email})
    assert response.status_code == 400
    assert DUPLICATE_MSG.encode() in response.data
    assert user_count() == before


def test_email_stored_lowercase(client):
    client.post("/register", data={**VALID, "email": "  Mixed@Example.COM "})
    assert db.get_user_by_email("mixed@example.com")["email"] == "mixed@example.com"


def test_integrity_error_race(client, monkeypatch):
    client.post("/register", data=VALID)
    before = user_count()
    import app as app_module

    monkeypatch.setattr(app_module, "get_user_by_email", lambda email: None)
    response = client.post("/register", data=VALID)
    assert response.status_code == 400
    assert DUPLICATE_MSG.encode() in response.data
    assert user_count() == before


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"name": ""}, "Name is required."),
        ({"name": "   "}, "Name is required."),
        ({"email": ""}, "Enter a valid email address."),
        ({"email": "x"}, "Enter a valid email address."),
        ({"email": "@x.com"}, "Enter a valid email address."),
        ({"email": "x@"}, "Enter a valid email address."),
        ({"email": "a b@c.com"}, "Enter a valid email address."),
        ({"password": "1234567"}, "Password must be at least 8 characters."),
        ({"password": ""}, "Password must be at least 8 characters."),
    ],
)
def test_validation_errors(client, overrides, message):
    before = user_count()
    response = client.post("/register", data={**VALID, **overrides})
    assert response.status_code == 400
    assert message.encode() in response.data
    assert user_count() == before


def test_missing_fields(client):
    before = user_count()
    response = client.post("/register", data={})
    assert response.status_code == 400
    assert user_count() == before


def test_values_retained_and_password_not(client):
    response = client.post("/register", data={**VALID, "password": "short"})
    html = response.get_data(as_text=True)
    assert 'value="Test User"' in html
    assert 'value="test@example.com"' in html
    password_tag = re.search(r'<input[^>]*name="password"[^>]*>', html).group(0)
    assert "value=" not in password_tag


def test_html_in_name_escaped(client):
    response = client.post(
        "/register", data={**VALID, "name": "<script>x</script>", "password": "short"}
    )
    assert b"<script>x</script>" not in response.data
    assert b"&lt;script&gt;" in response.data


def test_demo_user_unaffected(client):
    client.post("/register", data=VALID)
    demo = db.get_user_by_email("demo@spendly.com")
    assert demo is not None and demo["name"] == "Demo User"


def test_unique_constraint_backs_up_helper(app):
    db.create_user("A", "dup@example.com", "hash")
    with pytest.raises(sqlite3.IntegrityError):
        db.create_user("B", "dup@example.com", "hash")
