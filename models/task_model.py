
from database.db import get_db


def complete_task(task):
    conn = get_db()

    try:
        conn.execute(
            """
            INSERT INTO task_completions (task_id, category, xp)
            VALUES (?, ?, ?)
            """,
            (task["id"], task["category"], task["xp"])
        )

        conn.execute(
            """
            UPDATE user_data
            SET points = points + ?
            WHERE id = 1
            """,
            (task["xp"],)
        )

        conn.commit()

        user = conn.execute(
            "SELECT points FROM user_data WHERE id = 1"
        ).fetchone()

        return {
            "success": True,
            "earned_xp": task["xp"],
            "points": user["points"]
        }, 200

    finally:
        conn.close()
