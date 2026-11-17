
from database.db import get_db


BUILDINGS = {
    "shelter": {
        "name": "Shelter",
        "cost": 20
    },
    "cabin": {
        "name": "Cabin",
        "cost": 50
    },
    "house": {
        "name": "House",
        "cost": 100
    },
    "watchtower": {
        "name": "Watchtower",
        "cost": 150
    }
}


def get_market_items():
    conn = get_db()

    try:
        owned = conn.execute(
            "SELECT building_type FROM buildings"
        ).fetchall()

        owned_types = {row["building_type"] for row in owned}

        return [
            {
                "building_type": building_type,
                "name": item["name"],
                "cost": item["cost"],
                "owned": building_type in owned_types
            }
            for building_type, item in BUILDINGS.items()
        ]
    finally:
        conn.close()


def buy_building(building_type="shelter"):
    item = BUILDINGS.get(building_type)

    if item is None:
        return {
            "success": False,
            "message": "Invalid building."
        }, 404

    conn = get_db()

    try:
        user = conn.execute(
            "SELECT points FROM user_data WHERE id = 1"
        ).fetchone()

        if user is None or user["points"] < item["cost"]:
            return {
                "success": False,
                "message": "You don't have enough points."
            }, 400

        existing = conn.execute(
            "SELECT id FROM buildings WHERE building_type = ?",
            (building_type,)
        ).fetchone()

        if existing:
            return {
                "success": False,
                "message": "You already own this building."
            }, 400

        conn.execute(
            "UPDATE user_data SET points = points - ? WHERE id = 1",
            (item["cost"],)
        )

        conn.execute(
            """
            INSERT INTO buildings (name, building_type, cost)
            VALUES (?, ?, ?)
            """,
            (item["name"], building_type, item["cost"])
        )

        conn.commit()

        updated_user = conn.execute(
            "SELECT points FROM user_data WHERE id = 1"
        ).fetchone()

        return {
            "success": True,
            "message": f"{item['name']} added to your city!",
            "points": updated_user["points"],
            "building_type": building_type
        }, 200

    finally:
        conn.close()
