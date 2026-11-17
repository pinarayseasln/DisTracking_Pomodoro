from database.db import get_db


def get_user_data():
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM user_data WHERE id = 1"
        ).fetchone()
    finally:
        conn.close()


def get_user_buildings():
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM buildings ORDER BY id"
        ).fetchall()
    finally:
        conn.close()


def get_user_points():
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT points FROM user_data WHERE id = 1"
        ).fetchone()
        return user["points"] if user else 0
    finally:
        conn.close()