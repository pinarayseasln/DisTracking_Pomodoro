
import sqlite3
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PRODUCTION_DATABASE_PATH = (BASE_DIR / "distracking.db").resolve()
DATABASE_PATH = Path(
    os.environ.get("DISTRACKING_DATABASE_PATH", PRODUCTION_DATABASE_PATH)
).expanduser().resolve()


def _is_test_environment():
    test_flag = os.environ.get("DISTRACKING_TESTING", "").strip().lower()
    return test_flag in {"1", "true", "yes", "on"} or "pytest" in sys.modules


def get_db():
    if _is_test_environment() and DATABASE_PATH.resolve() == PRODUCTION_DATABASE_PATH:
        raise RuntimeError(
            "Tests cannot open the production database. Set "
            "DISTRACKING_DATABASE_PATH to a temporary test database."
        )
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

        # Persistent quantities for newly purchased Market materials and tools.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS market_inventory (
                item_id TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0)
            )
        """)

        # Account-owned Market stock. Copy old shared inventory once and keep
        # the legacy rows intact; timber is the previous name for wood.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_inventory (
                user_data_id INTEGER NOT NULL,
                item_id TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
                PRIMARY KEY (user_data_id, item_id),
                FOREIGN KEY (user_data_id) REFERENCES user_data(id)
            )
        """)
        conn.execute("""
            INSERT OR IGNORE INTO user_inventory (user_data_id, item_id, quantity)
            SELECT 1,
                   CASE WHEN item_id = 'timber' THEN 'wood' ELSE item_id END,
                   SUM(quantity)
            FROM market_inventory
            GROUP BY CASE WHEN item_id = 'timber' THEN 'wood' ELSE item_id END
        """)

        # Green Valley MVP progress is scoped by account and a stable city key.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS city_rebuild_progress (
                user_data_id INTEGER NOT NULL,
                city_id TEXT NOT NULL,
                stage INTEGER NOT NULL DEFAULT 0 CHECK(stage BETWEEN 0 AND 3),
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_data_id, city_id),
                FOREIGN KEY (user_data_id) REFERENCES user_data(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS city_rebuild_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_data_id INTEGER NOT NULL,
                city_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_data_id, city_id, task_id),
                FOREIGN KEY (user_data_id) REFERENCES user_data(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS city_decorations (
                user_data_id INTEGER NOT NULL,
                city_id TEXT NOT NULL,
                slot_id TEXT NOT NULL,
                decoration_id TEXT NOT NULL,
                placed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_data_id, city_id, slot_id),
                FOREIGN KEY (user_data_id) REFERENCES user_data(id)
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

        # Preserve any historical duplicate completions before enforcing the
        # one-reward-per-task rule. The earliest row remains canonical.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS task_completion_legacy_duplicates (
                id INTEGER PRIMARY KEY,
                task_id TEXT NOT NULL,
                category TEXT NOT NULL,
                xp INTEGER NOT NULL,
                completed_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            INSERT OR IGNORE INTO task_completion_legacy_duplicates
                (id, task_id, category, xp, completed_at)
            SELECT id, task_id, category, xp, completed_at
            FROM task_completions AS old
            WHERE EXISTS (
                SELECT 1 FROM task_completions AS earlier
                WHERE earlier.task_id = old.task_id AND earlier.id < old.id
            )
        """)
        conn.execute("""
            DELETE FROM task_completions
            WHERE EXISTS (
                SELECT 1 FROM task_completions AS earlier
                WHERE earlier.task_id = task_completions.task_id
                  AND earlier.id < task_completions.id
            )
        """)
        conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_task_completions_task_id
            ON task_completions(task_id)
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

        # Server-tracked focus and break timer sessions. Existing balances,
        # quests, and task completion records are left untouched.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id TEXT PRIMARY KEY,
                user_data_id INTEGER NOT NULL DEFAULT 1,
                mode TEXT NOT NULL CHECK(mode IN ('focus', 'short', 'long')),
                status TEXT NOT NULL CHECK(status IN ('running', 'paused', 'completed', 'cancelled')),
                duration_seconds INTEGER NOT NULL CHECK(duration_seconds BETWEEN 60 AND 10800),
                elapsed_seconds REAL NOT NULL DEFAULT 0 CHECK(elapsed_seconds >= 0),
                heartbeat_at REAL,
                quest_id INTEGER,
                rewarded INTEGER NOT NULL DEFAULT 0 CHECK(rewarded IN (0, 1)),
                created_at REAL NOT NULL,
                completed_at REAL
            )
        """)
        conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_pomodoro_one_active_session
            ON pomodoro_sessions(user_data_id)
            WHERE status IN ('running', 'paused')
        """)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
