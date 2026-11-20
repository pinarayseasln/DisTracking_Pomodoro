from database.db import get_db


MARKET_ITEMS = {
    "wood": {
        "name": "Wood", "group": "Raw materials", "icon": "🪵",
        "description": "Shelter rebuilding material.", "cost": 15,
    },
    "brick": {
        "name": "Brick", "group": "Raw materials", "icon": "🧱",
        "description": "Shelter rebuilding material.", "cost": 20,
    },
    "weed": {
        "name": "Weed", "group": "Raw materials", "icon": "🌿",
        "description": "Required to clear Green Valley.", "cost": 5,
    },
    "debris": {
        "name": "Debris", "group": "Raw materials", "icon": "🪨",
        "description": "Required to clear the damaged area.", "cost": 8,
    },
    "weed_tool": {
        "name": "Weed Tool", "group": "Construction tools", "icon": "🪓",
        "description": "A permanent tool for clearing weeds.", "cost": 50,
        "unique": True,
    },
    "shovel": {
        "name": "Shovel", "group": "Construction tools", "icon": "🪏",
        "description": "A permanent tool for clearing debris.", "cost": 60,
        "unique": True,
    },
    "stone": {
        "name": "Stone", "group": "Raw materials", "icon": "🪨",
        "description": "A building material for future projects.", "cost": 20,
    },
    "nails": {
        "name": "Nails", "group": "Raw materials", "icon": "🔩",
        "description": "Fasteners for future construction projects.", "cost": 10,
    },
    "hammer": {
        "name": "Hammer", "group": "Construction tools", "icon": "🔨",
        "description": "A construction tool for future projects.", "cost": 35,
    },
    "saw": {
        "name": "Saw", "group": "Construction tools", "icon": "🪚",
        "description": "A tool for preparing construction materials.", "cost": 45,
    },
    "repair_kit": {
        "name": "Repair Kit", "group": "Rebuild supplies", "icon": "🧰",
        "description": "Supplies for restoring damaged areas.", "cost": 60,
    },
    "fountain": {
        "name": "Fountain", "group": "Decorations", "icon": "⛲",
        "description": "A decoration for your rebuilt city.", "cost": 100,
    },
    "tree": {
        "name": "Tree", "group": "Decorations", "icon": "🌳",
        "description": "A decoration for your rebuilt city.", "cost": 45,
    },
    "flower_bed": {
        "name": "Flower Bed", "group": "Decorations", "icon": "🌷",
        "description": "A decoration for your rebuilt city.", "cost": 35,
    },
}


def get_market_inventory(user_data_id=1):
    conn = get_db()
    try:
        progress = conn.execute(
            """SELECT stage FROM city_rebuild_progress
               WHERE user_data_id = ? AND city_id = 'green-valley'""",
            (user_data_id,),
        ).fetchone()
        decorations_unlocked = bool(progress and progress["stage"] >= 3)
        quantities = {
            row["item_id"]: row["quantity"]
            for row in conn.execute(
                "SELECT item_id, quantity FROM user_inventory WHERE user_data_id = ?",
                (user_data_id,),
            ).fetchall()
        }
        return [
            {
                "item_id": item_id,
                **item,
                "unique": item.get("unique", False),
                "unlocked": item["group"] != "Decorations" or decorations_unlocked,
                "quantity": quantities.get(item_id, 0),
            }
            for item_id, item in MARKET_ITEMS.items()
        ]
    finally:
        conn.close()


def buy_market_item(item_id, user_data_id=1):
    item = MARKET_ITEMS.get(item_id)
    if item is None:
        return {"success": False, "message": "Invalid Market item."}, 404

    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        user = conn.execute(
            "SELECT points FROM user_data WHERE id = ?", (user_data_id,)
        ).fetchone()
        if user is None:
            conn.rollback()
            return {"success": False, "message": "User not found."}, 404

        if item["group"] == "Decorations":
            progress = conn.execute(
                """SELECT stage FROM city_rebuild_progress
                   WHERE user_data_id = ? AND city_id = 'green-valley'""",
                (user_data_id,),
            ).fetchone()
            if progress is None or progress["stage"] < 3:
                conn.rollback()
                return {
                    "success": False,
                    "message": "Rebuild the Shelter to unlock decorations.",
                }, 400

        existing = conn.execute(
            "SELECT quantity FROM user_inventory WHERE user_data_id = ? AND item_id = ?",
            (user_data_id, item_id),
        ).fetchone()
        if item.get("unique") and existing and existing["quantity"] > 0:
            conn.rollback()
            return {"success": False, "message": "You already own this tool."}, 400
        if user["points"] < item["cost"]:
            conn.rollback()
            return {"success": False, "message": "You don't have enough points."}, 400

        conn.execute(
            "UPDATE user_data SET points = points - ? WHERE id = ?",
            (item["cost"], user_data_id),
        )
        conn.execute(
            """INSERT INTO user_inventory (user_data_id, item_id, quantity)
               VALUES (?, ?, 1)
               ON CONFLICT(user_data_id, item_id) DO UPDATE SET quantity = quantity + 1""",
            (user_data_id, item_id),
        )
        quantity = conn.execute(
            "SELECT quantity FROM user_inventory WHERE user_data_id = ? AND item_id = ?",
            (user_data_id, item_id),
        ).fetchone()["quantity"]
        points = conn.execute(
            "SELECT points FROM user_data WHERE id = ?", (user_data_id,)
        ).fetchone()["points"]
        conn.commit()
        return {
            "success": True,
            "message": f"{item['name']} added to your inventory.",
            "item_id": item_id,
            "quantity": quantity,
            "points": points,
        }, 200
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
