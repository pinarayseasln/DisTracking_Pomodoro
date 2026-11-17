
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "distracking.db"


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()

    try:
        # Kullanıcı hesapları
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Kullanıcı puanları ve Pomodoro bilgileri
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY,
                points INTEGER NOT NULL DEFAULT 0,
                completed_sessions INTEGER NOT NULL DEFAULT 0
            )
        """)

        # Eski veritabanına user_id sütununu ekle
        columns = [
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(user_data)"
            ).fetchall()
        ]

        if "user_id" not in columns:
            conn.execute("""
                ALTER TABLE user_data
                ADD COLUMN user_id INTEGER
            """)

        conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_user_data_user_id
            ON user_data(user_id)
        """)

        # Eski tek kullanıcılı kayıt korunur
        conn.execute("""
            INSERT OR IGNORE INTO user_data
            (id, points, completed_sessions)
            VALUES (1, 0, 0)
        """)

        # Şehirler
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                owner_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users(id)
            )
        """)

        # Şehir üyeleri
        conn.execute("""
            CREATE TABLE IF NOT EXISTS city_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL DEFAULT 'member',
                joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(city_id, user_id),
                FOREIGN KEY (city_id) REFERENCES cities(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Arkadaşlık sistemi
        conn.execute("""
            CREATE TABLE IF NOT EXISTS friendships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(sender_id, receiver_id),
                CHECK(sender_id <> receiver_id),
                CHECK(status IN ('pending', 'accepted', 'rejected')),
                FOREIGN KEY (sender_id) REFERENCES users(id),
                FOREIGN KEY (receiver_id) REFERENCES users(id)
            )
        """)

        # Şehirdeki binalar
        # Aynı binadan birden fazla yapılabilir.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS city_buildings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_id INTEGER NOT NULL,
                building_type TEXT NOT NULL,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                level INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (city_id) REFERENCES cities(id)
            )
        """)


        # Şehrin ortak kaynakları
        conn.execute("""
            CREATE TABLE IF NOT EXISTS city_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_id INTEGER NOT NULL,
                resource_type TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                UNIQUE(city_id, resource_type),
                FOREIGN KEY (city_id) REFERENCES cities(id)
            )
        """)

        # Şehrin genel durumu
        conn.execute("""
            CREATE TABLE IF NOT EXISTS city_stats (
                city_id INTEGER PRIMARY KEY,
                happiness INTEGER NOT NULL DEFAULT 100,
                hunger INTEGER NOT NULL DEFAULT 0,
                health INTEGER NOT NULL DEFAULT 100,
                education INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (city_id) REFERENCES cities(id)
            )
        """)

        # Yeni şehir oluşturulunca başlangıç değerlerini otomatik ekle
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS initialize_city_data
            AFTER INSERT ON cities
            BEGIN
                INSERT INTO city_stats (city_id)
                VALUES (NEW.id);

                INSERT INTO city_resources
                    (city_id, resource_type, quantity)
                VALUES
                    (NEW.id, 'food', 0),
                    (NEW.id, 'water', 0),
                    (NEW.id, 'electricity', 0),
                    (NEW.id, 'natural_gas', 0);
            END;
        """)


        # Kullanıcıların kişisel kaynakları
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                resource_type TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                UNIQUE(user_id, resource_type),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Mevcut binalar tablosu korunur
        conn.execute("""
            CREATE TABLE IF NOT EXISTS buildings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                building_type TEXT NOT NULL UNIQUE,
                cost INTEGER NOT NULL
            )
        """)

        # Görev kayıtları
        conn.execute("""
            CREATE TABLE IF NOT EXISTS task_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                category TEXT NOT NULL,
                xp INTEGER NOT NULL,
                completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Günlük görevler
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_quests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_text TEXT NOT NULL,
                category TEXT NOT NULL,
                required_pomodoros INTEGER NOT NULL,
                completed_pomodoros INTEGER NOT NULL DEFAULT 0,
                reward_claimed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
