from database.db import get_db
from models.market import MARKET_ITEMS


GREEN_VALLEY_ID = "green-valley"

REBUILD_STAGES = (
    {
    "task_id": "clear-weeds",
    "name": "Clear Weeds",
    "requirements": {},
    "tools": {
        "shovel": 1,
        "scythe": 1,
        "scissors": 1,
    },
},
    {
        "task_id": "remove-debris",
        "name": "Remove Debris",
        "requirements": {"debris": 5},
        "tools": {"shovel": 1},
    },
    {
        "task_id": "rebuild-shelter",
        "name": "Rebuild Shelter",
        "requirements": {"wood": 10, "brick": 10},
        "tools": {},
    },
)

DECORATION_SLOTS = {
    "west-garden": {"label": "West Garden", "x": 28, "y": 58},
    "central-square": {"label": "Central Square", "x": 51, "y": 72},
    "east-garden": {"label": "East Garden", "x": 73, "y": 59},
}

DECORATION_IDS = {
    item_id for item_id, item in MARKET_ITEMS.items()
    if item["group"] == "Decorations"
}


def _valid_city(city_id):
    return city_id == GREEN_VALLEY_ID


def get_city_state(city_id, user_data_id=1):
    if not _valid_city(city_id):
        return None

    conn = get_db()
    try:
        progress = conn.execute(
            """SELECT stage FROM city_rebuild_progress
               WHERE user_data_id = ? AND city_id = ?""",
            (user_data_id, city_id),
        ).fetchone()
        stage = progress["stage"] if progress else 0
        completed = conn.execute(
            """SELECT task_id, completed_at FROM city_rebuild_tasks
               WHERE user_data_id = ? AND city_id = ? ORDER BY id""",
            (user_data_id, city_id),
        ).fetchall()
        inventory_rows = conn.execute(
            """SELECT item_id, quantity FROM user_inventory
               WHERE user_data_id = ?""",
            (user_data_id,),
        ).fetchall()
        decorations = conn.execute(
            """SELECT slot_id, decoration_id FROM city_decorations
               WHERE user_data_id = ? AND city_id = ?""",
            (user_data_id, city_id),
        ).fetchall()

        return {
            "city_id": city_id,
            "stage": stage,
            "stages": len(REBUILD_STAGES),
            "completed_tasks": [dict(row) for row in completed],
            "inventory": {row["item_id"]: row["quantity"] for row in inventory_rows},
            "decorations": [dict(row) for row in decorations],
            "slots": {
                slot_id: {"label": slot["label"], "x": slot["x"], "y": slot["y"]}
                for slot_id, slot in DECORATION_SLOTS.items()
            },
            "current_task": (
                {
                    "task_id": REBUILD_STAGES[stage]["task_id"],
                    "name": REBUILD_STAGES[stage]["name"],
                    "requirements": REBUILD_STAGES[stage]["requirements"],
                    "tools": REBUILD_STAGES[stage]["tools"],
                }
                if stage < len(REBUILD_STAGES)
                else None
            ),
        }
    finally:
        conn.close()


def complete_city_stage(city_id, user_data_id=1):
    if not _valid_city(city_id):
        return {"success": False, "message": "This city is not available yet."}, 404

    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            """INSERT OR IGNORE INTO city_rebuild_progress
               (user_data_id, city_id, stage) VALUES (?, ?, 0)""",
            (user_data_id, city_id),
        )
        progress = conn.execute(
            """SELECT stage FROM city_rebuild_progress
               WHERE user_data_id = ? AND city_id = ?""",
            (user_data_id, city_id),
        ).fetchone()
        stage_number = progress["stage"]
        if stage_number >= len(REBUILD_STAGES):
            conn.rollback()
            return {"success": False, "message": "Green Valley has been rebuilt."}, 409

        stage = REBUILD_STAGES[stage_number]
        requirements = {**stage["requirements"], **stage["tools"]}
        quantities = {
            row["item_id"]: row["quantity"]
            for row in conn.execute(
                """SELECT item_id, quantity FROM user_inventory
                   WHERE user_data_id = ?""",
                (user_data_id,),
            ).fetchall()
        }
        missing = [
            f"{MARKET_ITEMS[item_id]['name']} ({quantity - quantities.get(item_id, 0)} more)"
            for item_id, quantity in requirements.items()
            if quantities.get(item_id, 0) < quantity
        ]
        if missing:
            conn.rollback()
            return {
                "success": False,
                "message": "You need " + ", ".join(missing) + ".",
                "missing": missing,
            }, 400

        for item_id, quantity in stage["requirements"].items():
            conn.execute(
                """UPDATE user_inventory SET quantity = quantity - ?
                   WHERE user_data_id = ? AND item_id = ?""",
                (quantity, user_data_id, item_id),
            )
        conn.execute(
            """INSERT INTO city_rebuild_tasks (user_data_id, city_id, task_id)
               VALUES (?, ?, ?)""",
            (user_data_id, city_id, stage["task_id"]),
        )
        conn.execute(
            """UPDATE city_rebuild_progress SET stage = ?,
                       updated_at = CURRENT_TIMESTAMP
               WHERE user_data_id = ? AND city_id = ?""",
            (stage_number + 1, user_data_id, city_id),
        )
        conn.commit()
        return {
            "success": True,
            "message": f"{stage['name']} completed!",
            "stage": stage_number + 1,
            "task_id": stage["task_id"],
        }, 200
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def place_city_decoration(city_id, slot_id, decoration_id, user_data_id=1):
    if not _valid_city(city_id):
        return {"success": False, "message": "This city is not available yet."}, 404
    if slot_id not in DECORATION_SLOTS:
        return {"success": False, "message": "Choose an available city spot."}, 400
    if decoration_id not in DECORATION_IDS:
        return {"success": False, "message": "Invalid decoration."}, 400

    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        progress = conn.execute(
            """SELECT stage FROM city_rebuild_progress
               WHERE user_data_id = ? AND city_id = ?""",
            (user_data_id, city_id),
        ).fetchone()
        if progress is None or progress["stage"] < len(REBUILD_STAGES):
            conn.rollback()
            return {"success": False, "message": "Rebuild the Shelter before decorating."}, 400

        occupied = conn.execute(
            """SELECT 1 FROM city_decorations
               WHERE user_data_id = ? AND city_id = ? AND slot_id = ?""",
            (user_data_id, city_id, slot_id),
        ).fetchone()
        if occupied:
            conn.rollback()
            return {"success": False, "message": "That city spot is already occupied."}, 409

        stock = conn.execute(
            """SELECT quantity FROM user_inventory
               WHERE user_data_id = ? AND item_id = ?""",
            (user_data_id, decoration_id),
        ).fetchone()
        if stock is None or stock["quantity"] < 1:
            conn.rollback()
            return {"success": False, "message": "Buy this decoration in the Market first."}, 400

        conn.execute(
            """UPDATE user_inventory SET quantity = quantity - 1
               WHERE user_data_id = ? AND item_id = ?""",
            (user_data_id, decoration_id),
        )
        conn.execute(
            """INSERT INTO city_decorations
               (user_data_id, city_id, slot_id, decoration_id)
               VALUES (?, ?, ?, ?)""",
            (user_data_id, city_id, slot_id, decoration_id),
        )
        conn.commit()
        return {
            "success": True,
            "message": f"{MARKET_ITEMS[decoration_id]['name']} placed in {DECORATION_SLOTS[slot_id]['label']}.",
            "slot_id": slot_id,
            "decoration_id": decoration_id,
        }, 200
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
