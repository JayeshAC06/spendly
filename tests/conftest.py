import importlib

import pytest

import database.db as db


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Flask app wired to a throwaway SQLite file (never the real DB)."""
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))

    import app as app_module

    app_module = importlib.reload(app_module)  # re-run init_db/seed_db on temp DB
    app_module.app.config["TESTING"] = True
    return app_module.app
