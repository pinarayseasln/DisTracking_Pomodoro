
from database.db import get_db


def complete_task(task):
    conn = get_db()

    try:
        completion = conn.execute(
            """
            INSERT OR IGNORE INTO task_completions (task_id, category, xp)
            VALUES (?, ?, ?)
            """,
            (task["id"], task["category"], task["xp"])
        )

        if completion.rowcount == 0:
            conn.rollback()
            return {
                "success": False,
                "earned_xp": 0,
                "error": "Task has already been completed."
            }, 409

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
