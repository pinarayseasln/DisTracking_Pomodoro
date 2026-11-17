
from database.db import get_db


def create_quest(task_text, category, required_pomodoros):
    conn = get_db()

    try:
        cursor = conn.execute(
            """
            INSERT INTO daily_quests (
                task_text,
                category,
                required_pomodoros
            )
            VALUES (?, ?, ?)
            """,
            (task_text, category, required_pomodoros)
        )

        conn.commit()
        return cursor.lastrowid

    finally:
        conn.close()


def get_quests():
    conn = get_db()

    try:
        quests = conn.execute(
            """
            SELECT *
            FROM daily_quests
            ORDER BY id DESC
            """
        ).fetchall()

        return [dict(quest) for quest in quests]

    finally:
        conn.close()


def delete_quest(quest_id):
    conn = get_db()

    try:
        cursor = conn.execute(
            """
            DELETE FROM daily_quests
            WHERE id = ?
            """,
            (quest_id,)
        )

        conn.commit()
        return cursor.rowcount > 0

    finally:
        conn.close()
