import os
import tempfile
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRODUCTION_DATABASE_PATH = (PROJECT_ROOT / "distracking.db").resolve()

# Fail fast instead of silently redirecting an explicitly unsafe test setting.
configured_database = os.environ.get("DISTRACKING_DATABASE_PATH")
if configured_database:
    configured_path = Path(configured_database).expanduser().resolve()
    if configured_path == PRODUCTION_DATABASE_PATH:
        raise RuntimeError(
            "Pytest is configured to use the production distracking.db. "
            "Choose a temporary path with DISTRACKING_DATABASE_PATH."
        )

os.environ["DISTRACKING_TESTING"] = "1"

# app.py initializes its schema when imported, so its import-time database
# must also be isolated before importing the app or database module.
_pytest_database_dir = tempfile.TemporaryDirectory(prefix="distracking-pytest-")
os.environ["DISTRACKING_DATABASE_PATH"] = str(
    Path(_pytest_database_dir.name) / "bootstrap.db"
)

import database.db as db
from app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_database = (tmp_path / "test.db").resolve()
    monkeypatch.setattr(db, "DATABASE_PATH", test_database)

    if db.DATABASE_PATH == PRODUCTION_DATABASE_PATH:
        raise RuntimeError("Test fixture resolved to the production database.")

    db.init_db()
    app.config.update(TESTING=True)

    with app.test_client() as test_client:
        yield test_client
