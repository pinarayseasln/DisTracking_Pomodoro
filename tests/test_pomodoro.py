from concurrent.futures import ThreadPoolExecutor

from database.db import get_db
from models.user import get_user_data
import models.pomodoro_model as pomodoro_model


class Clock:
    def __init__(self, now=1_800_000_000.0):
        self.now = now

    def time(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def start_focus(client, quest_id=None):
    response = client.post("/api/pomodoro/start", json={
        "mode": "focus",
        "duration_seconds": 60,
        "quest_id": quest_id,
    })
    assert response.status_code == 201
    return response.json["session"]


def advance_session(client, clock, session_id, seconds):
    for _ in range(seconds // 5):
        clock.advance(5)
        response = client.post(
            "/api/pomodoro/heartbeat", json={"session_id": session_id}
        )
        assert response.status_code == 200
    remainder = seconds % 5
    if remainder:
        clock.advance(remainder)
        response = client.post(
            "/api/pomodoro/heartbeat", json={"session_id": session_id}
        )
        assert response.status_code == 200


def test_early_completion_does_not_award_xp(client, monkeypatch):
    clock = Clock()
    monkeypatch.setattr(pomodoro_model.time, "time", clock.time)
    before = get_user_data()
    session = start_focus(client)

    response = client.post(
        "/api/pomodoro/complete", json={"session_id": session["id"]}
    )

    assert response.status_code == 409
    assert get_user_data()["points"] == before["points"]
    assert get_user_data()["completed_sessions"] == before["completed_sessions"]


def test_client_supplied_focus_minutes_cannot_award_xp(client):
    before = get_user_data()
    response = client.post("/api/pomodoro/complete", json={"focus_minutes": 180})
    assert response.status_code == 404
    assert get_user_data()["points"] == before["points"]


def test_pause_excludes_time_and_resume_continues_from_remaining(client, monkeypatch):
    clock = Clock()
    monkeypatch.setattr(pomodoro_model.time, "time", clock.time)
    session = start_focus(client)
    advance_session(client, clock, session["id"], 20)

    paused = client.post(
        "/api/pomodoro/pause", json={"session_id": session["id"]}
    )
    assert paused.status_code == 200
    assert paused.json["session"]["elapsed_seconds"] == 20

    clock.advance(300)
    still_paused = client.get("/api/pomodoro/session").json["session"]
    assert still_paused["status"] == "paused"
    assert still_paused["remaining_seconds"] == 40

    resumed = client.post(
        "/api/pomodoro/resume", json={"session_id": session["id"]}
    )
    assert resumed.status_code == 200
    advance_session(client, clock, session["id"], 40)
    completed = client.post(
        "/api/pomodoro/complete", json={"session_id": session["id"]}
    )
    assert completed.status_code == 200
    assert completed.json["earned_points"] == 1


def test_browser_close_pause_and_page_refresh_restore_session(client, monkeypatch):
    clock = Clock()
    monkeypatch.setattr(pomodoro_model.time, "time", clock.time)
    session = start_focus(client)
    advance_session(client, clock, session["id"], 10)

    # pagehide sends this pause request; the server persists it independently
    # of browser memory and does not award time while paused.
    pagehide_pause = client.post(
        "/api/pomodoro/pause", json={"session_id": session["id"]}
    )
    assert pagehide_pause.status_code == 200
    clock.advance(120)

    with client.application.test_client() as refreshed_client:
        restored = refreshed_client.get("/api/pomodoro/session").json["session"]
    assert restored["id"] == session["id"]
    assert restored["status"] == "paused"
    assert restored["elapsed_seconds"] == 10
    assert restored["remaining_seconds"] == 50


def test_missing_browser_heartbeat_auto_pauses_without_crediting_gap(client, monkeypatch):
    clock = Clock()
    monkeypatch.setattr(pomodoro_model.time, "time", clock.time)
    session = start_focus(client)
    advance_session(client, clock, session["id"], 10)
    clock.advance(pomodoro_model.HEARTBEAT_LEASE_SECONDS + 1)

    restored = client.get("/api/pomodoro/session").json["session"]
    assert restored["status"] == "paused"
    assert restored["elapsed_seconds"] == 10
    assert restored["remaining_seconds"] == 50


def test_page_reload_without_pagehide_freezes_at_last_server_heartbeat(client, monkeypatch):
    clock = Clock()
    monkeypatch.setattr(pomodoro_model.time, "time", clock.time)
    session = start_focus(client)
    advance_session(client, clock, session["id"], 10)
    clock.advance(4)

    with client.application.test_client() as refreshed_client:
        restored = refreshed_client.get("/api/pomodoro/session").json["session"]

    assert restored["status"] == "paused"
    assert restored["elapsed_seconds"] == 10
    assert restored["remaining_seconds"] == 50


def test_reset_cancels_session_without_xp(client, monkeypatch):
    clock = Clock()
    monkeypatch.setattr(pomodoro_model.time, "time", clock.time)
    before = get_user_data()
    session = start_focus(client)
    advance_session(client, clock, session["id"], 20)
    reset = client.post("/api/pomodoro/reset", json={"session_id": session["id"]})
    assert reset.status_code == 200
    complete = client.post(
        "/api/pomodoro/complete", json={"session_id": session["id"]}
    )
    assert complete.status_code == 409
    assert get_user_data()["points"] == before["points"]


def test_repeated_completion_cannot_award_twice(client, monkeypatch):
    clock = Clock()
    monkeypatch.setattr(pomodoro_model.time, "time", clock.time)
    before = get_user_data()
    session = start_focus(client)
    advance_session(client, clock, session["id"], 60)
    first = client.post(
        "/api/pomodoro/complete", json={"session_id": session["id"]}
    )
    second = client.post(
        "/api/pomodoro/complete", json={"session_id": session["id"]}
    )
    assert first.status_code == 200
    assert second.status_code == 409
    assert get_user_data()["points"] == before["points"] + 1


def test_concurrent_completion_awards_focus_xp_once(client, monkeypatch):
    clock = Clock()
    monkeypatch.setattr(pomodoro_model.time, "time", clock.time)
    before = get_user_data()
    session = start_focus(client)
    advance_session(client, clock, session["id"], 60)

    def complete_once(_):
        with client.application.test_client() as concurrent_client:
            return concurrent_client.post(
                "/api/pomodoro/complete", json={"session_id": session["id"]}
            )

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(complete_once, range(2)))
    assert sorted(response.status_code for response in responses) == [200, 409]
    assert sum(response.json.get("earned_points", 0) for response in responses) == 1
    assert get_user_data()["points"] == before["points"] + 1


def test_quest_progress_updates_only_for_completed_focus_session(client, monkeypatch):
    clock = Clock()
    monkeypatch.setattr(pomodoro_model.time, "time", clock.time)
    quest_response = client.post("/api/quests", json={
        "task_text": "Finish a chapter",
        "category": "study",
        "required_pomodoros": 1,
    })
    quest_id = quest_response.json["quest_id"]

    early_session = start_focus(client, quest_id)
    early = client.post(
        "/api/pomodoro/complete", json={"session_id": early_session["id"]}
    )
    assert early.status_code == 409
    quest = client.get("/api/quests").json["quests"][0]
    assert quest["completed_pomodoros"] == 0
    client.post("/api/pomodoro/reset", json={"session_id": early_session["id"]})

    completed_session = start_focus(client, quest_id)
    advance_session(client, clock, completed_session["id"], 60)
    completed = client.post(
        "/api/pomodoro/complete", json={"session_id": completed_session["id"]}
    )
    assert completed.status_code == 200
    assert completed.json["quest_id"] == quest_id
    assert completed.json["quest_progress"] == 1
    assert completed.json["quest_reward"] == 10
    quest = client.get("/api/quests").json["quests"][0]
    assert quest["completed_pomodoros"] == 1


def test_break_sessions_never_award_xp_or_quest_progress(client, monkeypatch):
    clock = Clock()
    monkeypatch.setattr(pomodoro_model.time, "time", clock.time)
    before = get_user_data()
    response = client.post("/api/pomodoro/start", json={
        "mode": "short", "duration_seconds": 60, "quest_id": 1234,
    })
    assert response.status_code == 201
    session = response.json["session"]
    advance_session(client, clock, session["id"], 60)
    completed = client.post(
        "/api/pomodoro/complete", json={"session_id": session["id"]}
    )
    assert completed.status_code == 200
    assert completed.json["earned_points"] == 0
    assert get_user_data()["points"] == before["points"]


def test_start_rejects_invalid_quest(client):
    response = client.post("/api/pomodoro/start", json={
        "mode": "focus", "duration_seconds": 60, "quest_id": 999999,
    })
    assert response.status_code == 404


def test_session_is_persisted_in_database(client, monkeypatch):
    clock = Clock()
    monkeypatch.setattr(pomodoro_model.time, "time", clock.time)
    session = start_focus(client)
    conn = get_db()
    try:
        stored = conn.execute(
            "SELECT status, mode, duration_seconds FROM pomodoro_sessions WHERE id = ?",
            (session["id"],),
        ).fetchone()
        assert tuple(stored) == ("running", "focus", 60)
    finally:
        conn.close()
