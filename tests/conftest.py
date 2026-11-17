import pytest
import database.db as db

from app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Gerçek veritabanı yerine geçici test veritabanı kullan
    test_database = tmp_path / "test.db"

    monkeypatch.setattr(db, "DATABASE_PATH", test_database)

    # Test veritabanını oluştur
    db.init_db()

    # Flask test ayarları
    app.config.update(TESTING=True)

    # Test istemcisini hazırla
    with app.test_client() as client:
        yield client