import sqlite3

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db

app = Flask(__name__)

with app.app_context():
    init_db()
    seed_db()

DUPLICATE_EMAIL_ERROR = "An account with that email already exists."


def _validate_registration(name, email, password):
    if not name:
        return "Name is required."
    local, sep, domain = email.partition("@")
    if not (sep and local and domain) or any(ch.isspace() for ch in email):
        return "Enter a valid email address."
    if len(password) < 8:
        return "Password must be at least 8 characters."
    return None


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    raw_email = request.form.get("email", "").strip()
    email = raw_email.lower()
    password = request.form.get("password", "")

    def render_error(message):
        return (
            render_template(
                "register.html", error=message, name=name, email=raw_email
            ),
            400,
        )

    error = _validate_registration(name, email, password)
    if error:
        return render_error(error)

    if get_user_by_email(email):
        return render_error(DUPLICATE_EMAIL_ERROR)

    try:
        create_user(name, email, generate_password_hash(password))
    except sqlite3.IntegrityError:
        return render_error(DUPLICATE_EMAIL_ERROR)

    return redirect(url_for("login", registered=1))


@app.route("/login")
def login():
    registered = request.args.get("registered") == "1"
    return render_template("login.html", registered=registered)


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
