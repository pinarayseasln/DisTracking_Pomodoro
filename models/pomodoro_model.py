import time
import uuid

from database.db import get_db


# A running session earns time only while the browser confirms it is alive.
# Missing heartbeats therefore cannot add an unbounded closed-tab interval.
HEARTBEAT_LEASE_SECONDS = 15


def _session_payload(session):
    if session is None:
        return None
    data = dict(session)
    data["elapsed_seconds"] = min(
        data["duration_seconds"], max(0, int(data["elapsed_seconds"]))
    )
    data["remaining_seconds"] = max(
        0, data["duration_seconds"] - data["elapsed_seconds"]
    )
    return data


def _checkpoint(conn, session, now):
    """Persist server-measured time since the last browser heartbeat."""
    if session["status"] != "running":
        return session, False

    last_heartbeat = session["heartbeat_at"] or now
    delta = max(0, now - last_heartbeat)
    credited_delta = delta if delta <= HEARTBEAT_LEASE_SECONDS else 0
    elapsed = min(session["duration_seconds"], session["elapsed_seconds"] + credited_delta)
    stale = delta > HEARTBEAT_LEASE_SECONDS
    status = "paused" if stale else "running"
    heartbeat_at = None if stale else now
    conn.execute(
        """UPDATE pomodoro_sessions
           SET elapsed_seconds = ?, heartbeat_at = ?, status = ?
           WHERE id = ? AND status = 'running'""",
        (elapsed, heartbeat_at, status, session["id"]),
    )
    updated = conn.execute(
        "SELECT * FROM pomodoro_sessions WHERE id = ?", (session["id"],)
    ).fetchone()
    return updated, stale


def _get_active(conn):
    return conn.execute(
        """SELECT * FROM pomodoro_sessions
           WHERE user_data_id = 1 AND status IN ('running', 'paused')
           ORDER BY created_at DESC LIMIT 1"""
    ).fetchone()


def get_current_session():
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        session = _get_active(conn)
        if session is not None and session["status"] == "running":
            # A page load cannot prove that the previous page remained open.
            # Freeze at the last accepted heartbeat and require an explicit resume.
            conn.execute(
                """UPDATE pomodoro_sessions
                   SET status = 'paused', heartbeat_at = NULL WHERE id = ?""",
                (session["id"],),
            )
            session = _get_owned_session(conn, session["id"])
        conn.commit()
        return {"success": True, "session": _session_payload(session)}, 200
    finally:
        conn.close()


def start_session(mode, duration_seconds, quest_id=None):
    if mode not in ("focus", "short", "long"):
        return {"success": False, "error": "Invalid timer mode."}, 400
    try:
        duration_seconds = int(duration_seconds)
    except (TypeError, ValueError):
        return {"success": False, "error": "Invalid timer duration."}, 400
    if not 60 <= duration_seconds <= 10800:
        return {"success": False, "error": "Timer duration must be between 1 and 180 minutes."}, 400

    if mode != "focus":
        quest_id = None
    elif quest_id is not None:
        try:
            quest_id = int(quest_id)
        except (TypeError, ValueError):
            return {"success": False, "error": "Invalid quest ID."}, 400

    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        active = _get_active(conn)
        if active is not None:
            active, _ = _checkpoint(conn, active, time.time())
            conn.commit()
            return {
                "success": False,
                "error": "An active timer session already exists.",
                "session": _session_payload(active),
            }, 409

        if quest_id is not None:
            quest = conn.execute(
                "SELECT id FROM daily_quests WHERE id = ?", (quest_id,)
            ).fetchone()
            if quest is None:
                conn.rollback()
                return {"success": False, "error": "Quest not found."}, 404

        now = time.time()
        session_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO pomodoro_sessions
               (id, user_data_id, mode, status, duration_seconds,
                elapsed_seconds, heartbeat_at, quest_id, created_at)
               VALUES (?, 1, ?, 'running', ?, 0, ?, ?, ?)""",
            (session_id, mode, duration_seconds, now, quest_id, now),
        )
        session = conn.execute(
            "SELECT * FROM pomodoro_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        conn.commit()
        return {"success": True, "session": _session_payload(session)}, 201
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _get_owned_session(conn, session_id):
    if not session_id:
        return None
    return conn.execute(
        "SELECT * FROM pomodoro_sessions WHERE id = ? AND user_data_id = 1",
        (str(session_id),),
    ).fetchone()


def heartbeat_session(session_id):
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        session = _get_owned_session(conn, session_id)
        if session is None:
            conn.rollback()
            return {"success": False, "error": "Session not found."}, 404
        session, stale = _checkpoint(conn, session, time.time())
        conn.commit()
        if stale:
            return {
                "success": False,
                "error": "Session paused after its heartbeat expired.",
                "session": _session_payload(session),
            }, 409
        return {"success": True, "session": _session_payload(session)}, 200
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def pause_session(session_id):
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        session = _get_owned_session(conn, session_id)
        if session is None:
            conn.rollback()
            return {"success": False, "error": "Session not found."}, 404
        session, _ = _checkpoint(conn, session, time.time())
        if session["status"] == "running":
            conn.execute(
                """UPDATE pomodoro_sessions
                   SET status = 'paused', heartbeat_at = NULL WHERE id = ?""",
                (session_id,),
            )
            session = _get_owned_session(conn, session_id)
        conn.commit()
        return {"success": True, "session": _session_payload(session)}, 200
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def resume_session(session_id):
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        session = _get_owned_session(conn, session_id)
        if session is None:
            conn.rollback()
            return {"success": False, "error": "Session not found."}, 404
        if session["status"] != "paused":
            conn.rollback()
            return {"success": False, "error": "Only a paused session can resume."}, 409
        now = time.time()
        conn.execute(
            """UPDATE pomodoro_sessions
               SET status = 'running', heartbeat_at = ? WHERE id = ?""",
            (now, session_id),
        )
        session = _get_owned_session(conn, session_id)
        conn.commit()
        return {"success": True, "session": _session_payload(session)}, 200
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def cancel_session(session_id):
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        session = _get_owned_session(conn, session_id)
        if session is None:
            conn.rollback()
            return {"success": False, "error": "Session not found."}, 404
        if session["status"] in ("completed", "cancelled"):
            conn.rollback()
            return {"success": False, "error": "Session is already closed."}, 409
        conn.execute(
            """UPDATE pomodoro_sessions
               SET status = 'cancelled', heartbeat_at = NULL WHERE id = ?""",
            (session_id,),
        )
        conn.commit()
        return {"success": True}, 200
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def complete_pomodoro(session_id):
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        session = _get_owned_session(conn, session_id)
        if session is None:
            conn.rollback()
            return {"success": False, "error": "Session not found."}, 404
        if session["status"] != "running" or session["rewarded"]:
            conn.rollback()
            return {"success": False, "error": "Session is not eligible for completion."}, 409

        session, stale = _checkpoint(conn, session, time.time())
        if stale:
            conn.commit()
            return {
                "success": False,
                "error": "Session paused after its heartbeat expired.",
                "session": _session_payload(session),
            }, 409
        if session["elapsed_seconds"] < session["duration_seconds"]:
            conn.commit()
            return {
                "success": False,
                "error": "Focus session has not reached its required duration.",
                "session": _session_payload(session),
            }, 409

        quest_progress = None
        quest_reward = 0
        earned_points = 0
        if session["mode"] == "focus":
            earned_points = session["duration_seconds"] // 60
            quest_id = session["quest_id"]
            if quest_id is not None:
                quest = conn.execute(
                    "SELECT * FROM daily_quests WHERE id = ?", (quest_id,)
                ).fetchone()
                if quest is not None:
                    quest_progress = quest["completed_pomodoros"]
                    if not quest["reward_claimed"]:
                        quest_progress = min(
                            quest["completed_pomodoros"] + 1,
                            quest["required_pomodoros"],
                        )
                        if quest_progress >= quest["required_pomodoros"]:
                            quest_reward = 10
                        conn.execute(
                            """UPDATE daily_quests
                               SET completed_pomodoros = ?, reward_claimed = ?
                               WHERE id = ?""",
                            (quest_progress, 1 if quest_reward else 0, quest_id),
                        )
            conn.execute(
                """UPDATE user_data
                   SET points = points + ?, completed_sessions = completed_sessions + 1
                   WHERE id = 1""",
                (earned_points + quest_reward,),
            )
        conn.execute(
            """UPDATE pomodoro_sessions
               SET status = 'completed', rewarded = ?, completed_at = ?, heartbeat_at = NULL
               WHERE id = ? AND status = 'running' AND rewarded = 0""",
            (1 if session["mode"] == "focus" else 0, time.time(), session_id),
        )
        conn.commit()

        user = conn.execute("SELECT * FROM user_data WHERE id = 1").fetchone()
        return {
            "success": True,
            "points": user["points"],
            "completed_sessions": user["completed_sessions"],
            "quest_id": session["quest_id"],
            "quest_progress": quest_progress,
            "quest_reward": quest_reward,
            "earned_points": earned_points + quest_reward,
        }, 200
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
