
from database.db import get_db


def complete_pomodoro(quest_id=None, focus_minutes=None):
    try:
        focus_minutes = int(focus_minutes)
    except (TypeError, ValueError):
        return {"success": False, "error": "Invalid focus duration."}, 400

    if not 1 <= focus_minutes <= 180:
        return {"success": False, "error": "Focus duration must be between 1 and 180 minutes."}, 400

    conn = get_db()

    try:
        quest_progress = None
        quest_reward = 0

        if quest_id is not None:
            try:
                quest_id = int(quest_id)
            except (TypeError, ValueError):
                return {
                    "success": False,
                    "error": "Invalid quest ID."
                }, 400

            quest = conn.execute(
                """
                SELECT * FROM daily_quests
                WHERE id = ?
                """,
                (quest_id,)
            ).fetchone()

            if quest is None:
                return {
                    "success": False,
                    "error": "Quest not found."
                }, 404

            if not quest["reward_claimed"]:
                new_progress = min(
                    quest["completed_pomodoros"] + 1,
                    quest["required_pomodoros"]
                )

                if new_progress >= quest["required_pomodoros"]:
                    quest_reward = 10

                conn.execute(
                    """
                    UPDATE daily_quests
                    SET completed_pomodoros = ?,
                        reward_claimed = ?
                    WHERE id = ?
                    """,
                    (
                        new_progress,
                        1 if quest_reward else 0,
                        quest_id
                    )
                )

                quest_progress = new_progress
            else:
                quest_progress = quest["completed_pomodoros"]

        conn.execute(
            """
            UPDATE user_data
            SET points = points + ?,
                completed_sessions = completed_sessions + 1
            WHERE id = 1
            """,
            (focus_minutes + quest_reward,)
        )

        conn.commit()

        user = conn.execute(
            "SELECT * FROM user_data WHERE id = 1"
        ).fetchone()

        return {
            "success": True,
            "points": user["points"],
            "completed_sessions": user["completed_sessions"],
            "quest_progress": quest_progress,
            "quest_reward": quest_reward,
            "earned_points": focus_minutes + quest_reward,
        }, 200

    finally:
        conn.close()
