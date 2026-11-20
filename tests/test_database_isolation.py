import pytest

import database.db as db


def test_test_environment_rejects_production_database_path(monkeypatch):
    monkeypatch.setattr(db, "DATABASE_PATH", db.PRODUCTION_DATABASE_PATH)

    with pytest.raises(RuntimeError, match="Tests cannot open the production database"):
        db.get_db()
