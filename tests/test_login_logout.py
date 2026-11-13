import re

import pytest

import database.db as db

DEMO = {"email": "demo@spendly.com", "password": "demo123"}
USER = {"name": "Test User", "email": "test@example.com", "password": "password123"}
INVALID_MSG = b"Invalid email or password."


def register(client):
    client.post("/register", data=USER)


def login(client, email, password):
    return client.post("/login", data={"email": email, "password": password})


def session_user_id(client):
    with client.session_transaction() as sess:
        return sess.get("user_id")


def test_get_login_ok(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"auth-error" not in response.data
    assert b"auth-success" not in response.data


def test_registered_banner_shown(client):
    response = client.get("/login?registered=1")
    assert b"auth-success" in response.data


def test_demo_login_redirects_to_profile(client):
    response = login(client, **DEMO)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/profile")
    assert session_user_id(client) is not None


@pytest.mark.parametrize(
    "email", ["test@example.com", "TEST@EXAMPLE.COM", "  Test@Example.com  "]
)
def test_registered_user_can_login_any_case(client, email):
    register(client)
    response = login(client, email, USER["password"])
    assert response.status_code == 302
    assert session_user_id(client) == db.get_user_by_email(USER["email"])["id"]


@pytest.mark.parametrize(
    "email, password",
    [
        ("demo@spendly.com", "wrong-password"),
        ("nobody@example.com", "demo123"),
        ("", "demo123"),
        ("demo@spendly.com", ""),
        ("' OR 1=1 --", "x"),
    ],
)
def test_failed_login_is_generic_400(client, email, password):
    response = login(client, email, password)
    assert response.status_code == 400
    assert INVALID_MSG in response.data
    assert session_user_id(client) is None


def test_email_retained_password_not(client):
    response = login(client, "demo@spendly.com", "wrong-password")
    assert b'value="demo@spendly.com"' in response.data
    assert b"wrong-password" not in response.data
    tag = re.search(rb'<input[^>]*name="password"[^>]*>', response.data).group(0)
    assert b"value=" not in tag


def test_navbar_signed_in_and_out(client):
    anon = client.get("/login")
    assert b"Sign in" in anon.data and b"Get started" in anon.data
    assert b"Sign out" not in anon.data

    login(client, **DEMO)
    # /profile is a stub string, so check the navbar on a template page
    page = client.get("/terms")
    assert b"Demo User" in page.data
    assert b"Sign out" in page.data
    assert b'href="/logout"' in page.data
    assert b"Get started" not in page.data


def test_login_redirects_when_signed_in(client):
    login(client, **DEMO)
    response = client.get("/login")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/profile")


def test_stale_user_id_treated_as_signed_out(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 9999
    response = client.get("/login")
    assert response.status_code == 200
    assert session_user_id(client) is None


def test_logout_clears_session(client):
    login(client, **DEMO)
    response = client.get("/logout")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    assert session_user_id(client) is None
    page = client.get("/login")
    assert page.status_code == 200
    assert b"Sign in" in page.data
    assert b"Sign out" not in page.data


def test_logout_when_not_signed_in(client):
    response = client.get("/logout")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_second_login_switches_account(client):
    register(client)
    login(client, **DEMO)
    demo_id = session_user_id(client)
    login(client, USER["email"], USER["password"])
    assert session_user_id(client) != demo_id


def test_login_form_uses_url_for(client):
    assert b'action="/login"' in client.get("/login").data


def test_get_user_by_id():
    demo = db.get_user_by_email(DEMO["email"])
    assert db.get_user_by_id(demo["id"])["email"] == DEMO["email"]
    assert db.get_user_by_id(9999) is None
