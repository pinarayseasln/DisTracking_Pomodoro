from database.db import get_db


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