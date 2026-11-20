from database.db import get_db
import sqlite3
import database.db as db_module
from concurrent.futures import ThreadPoolExecutor


def test_task_catalog(client):
    response = client.get("/api/tasks")

    assert response.status_code == 200

    data = response.get_json()

    assert "categories" in data
    assert data["task_count"] > 0


def test_task_recommendation(client):
    response = client.post(
        "/api/tasks/recommend",
        json={
            "need": "mentally_tired",
            "max_duration": 3
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert "task" in data
    assert data["task"]["duration"] <= 3


def test_task_completion(client):
    # Görevi tamamla
    response = client.post(
        "/api/tasks/complete",
        json={"task_id": "MR01"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["earned_xp"] == 20
    assert data["points"] == 20

    # Veritabanındaki kayıtları kontrol et
    conn = get_db()

    user = conn.execute(
        "SELECT points FROM user_data WHERE id = 1"
    ).fetchone()

    completion = conn.execute(
        "SELECT * FROM task_completions WHERE task_id = ?",
        ("MR01",)
    ).fetchone()

    conn.close()

    assert user["points"] == 20
    assert completion is not None


def test_repeated_task_completion_does_not_award_xp(client):
    first = client.post("/api/tasks/complete", json={"task_id": "MR01"})
    second = client.post("/api/tasks/complete", json={"task_id": "MR01"})

    assert first.status_code == 200
    assert first.json["earned_xp"] == 20
    assert second.status_code == 409
    assert second.json["earned_xp"] == 0

    conn = get_db()
    try:
        user = conn.execute("SELECT points FROM user_data WHERE id = 1").fetchone()
        completions = conn.execute(
            "SELECT COUNT(*) AS count FROM task_completions WHERE task_id = ?",
            ("MR01",)
        ).fetchone()
    finally:
        conn.close()

    assert user["points"] == 20
    assert completions["count"] == 1


def test_concurrent_task_completion_awards_xp_once(client):
    def complete_once():
        with client.application.test_client() as concurrent_client:
            return concurrent_client.post(
                "/api/tasks/complete", json={"task_id": "MR01"}
            )

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(lambda _: complete_once(), range(2)))

    assert sorted(response.status_code for response in responses) == [200, 409]
    assert sum(response.json["earned_xp"] for response in responses) == 20

    conn = get_db()
    try:
        points = conn.execute("SELECT points FROM user_data WHERE id = 1").fetchone()[0]
        count = conn.execute(
            "SELECT COUNT(*) FROM task_completions WHERE task_id = 'MR01'"
        ).fetchone()[0]
    finally:
        conn.close()
    assert points == 20
    assert count == 1


def test_task_completion_unique_constraint_exists(client):
    conn = get_db()
    try:
        indexes = conn.execute("PRAGMA index_list(task_completions)").fetchall()
        unique_task_id = False
        for index in indexes:
            if index["unique"]:
                columns = conn.execute(
                    f"PRAGMA index_info('{index['name']}')"
                ).fetchall()
                if [column["name"] for column in columns] == ["task_id"]:
                    unique_task_id = True
        assert unique_task_id
    finally:
        conn.close()


def test_init_db_preserves_balance_and_archives_legacy_duplicates(tmp_path, monkeypatch):
    database_path = tmp_path / "legacy.db"
    monkeypatch.setattr(db_module, "DATABASE_PATH", database_path)
    conn = sqlite3.connect(database_path)
    conn.executescript("""
        CREATE TABLE user_data (
            id INTEGER PRIMARY KEY,
            points INTEGER NOT NULL DEFAULT 0,
            completed_sessions INTEGER NOT NULL DEFAULT 0
        );
        INSERT INTO user_data (id, points, completed_sessions) VALUES (1, 77, 4);
        CREATE TABLE task_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            category TEXT NOT NULL,
            xp INTEGER NOT NULL,
            completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO task_completions (task_id, category, xp) VALUES
            ('MR01', 'mindfulness_relaxation', 20),
            ('MR01', 'mindfulness_relaxation', 20),
            ('PR01', 'physical_reset', 10);
    """)
    conn.commit()
    conn.close()

    db_module.init_db()

    conn = sqlite3.connect(database_path)
    try:
        assert conn.execute("SELECT points FROM user_data WHERE id = 1").fetchone()[0] == 77
        assert conn.execute("SELECT COUNT(*) FROM task_completions").fetchone()[0] == 2
        assert conn.execute(
            "SELECT COUNT(*) FROM task_completion_legacy_duplicates"
        ).fetchone()[0] == 1
        assert conn.execute(
            "SELECT COUNT(*) FROM task_completions UNION ALL "
            "SELECT COUNT(*) FROM task_completion_legacy_duplicates"
        ).fetchall() == [(2,), (1,)]
        indexes = conn.execute("PRAGMA index_list(task_completions)").fetchall()
        unique_index = next(row for row in indexes if row[1] == "idx_task_completions_task_id")
        assert unique_index[2] == 1
    finally:
        conn.close()

def test_invalid_task_recommendation(client):
    response = client.post(
        "/api/tasks/recommend",
        json={
            "need": "invalid_state",
            "max_duration": 3
        }
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_invalid_task_completion(client):
    response = client.post(
        "/api/tasks/complete",
        json={"task_id": "INVALID_TASK"}
    )

    assert response.status_code == 404
    assert response.get_json()["success"] is False

def test_tasks_page(client):
    response = client.get("/tasks")

    assert response.status_code == 200


def test_invalid_break_duration(client):
    response = client.post(
        "/api/tasks/recommend",
        json={
            "need": "mentally_tired",
            "max_duration": "abc"
        }
    )

    assert response.status_code == 400
    assert response.json["success"] is False


def test_exclude_ids_wrong_type(client):
    response = client.post(
        "/api/tasks/recommend",
        json={
            "need": "mentally_tired",
            "max_duration": 3,
            "exclude_ids": "MR01"
        }
    )

    assert response.status_code == 200
    assert response.json["success"] is True
