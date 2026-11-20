from database.db import get_db


def add_stock(item_id, quantity):
    conn = get_db()
    conn.execute(
        """INSERT INTO user_inventory (user_data_id, item_id, quantity)
           VALUES (1, ?, ?)
           ON CONFLICT(user_data_id, item_id)
           DO UPDATE SET quantity = excluded.quantity""",
        (item_id, quantity),
    )
    conn.commit()
    conn.close()


def test_green_valley_rebuild_requires_tools_and_consumables(client):
    response = client.post("/api/cities/green-valley/rebuild/complete")
    assert response.status_code == 400
    assert "Weed Tool" in response.get_json()["message"]

    add_stock("weed_tool", 1)
    add_stock("weed", 10)
    response = client.post("/api/cities/green-valley/rebuild/complete")
    assert response.status_code == 200
    assert response.get_json()["task_id"] == "clear-weeds"

    state = client.get("/api/cities/green-valley/rebuild").get_json()
    assert state["stage"] == 1
    assert state["inventory"]["weed"] == 0
    assert state["inventory"]["weed_tool"] == 1
    assert [task["task_id"] for task in state["completed_tasks"]] == ["clear-weeds"]


def test_rebuild_stages_are_ordered_and_consume_only_required_materials(client):
    add_stock("weed_tool", 1)
    add_stock("weed", 10)
    add_stock("shovel", 1)
    add_stock("debris", 5)
    add_stock("wood", 10)
    add_stock("brick", 10)

    for expected_stage, task_id in enumerate(
        ("clear-weeds", "remove-debris", "rebuild-shelter"), start=1
    ):
        response = client.post("/api/cities/green-valley/rebuild/complete")
        assert response.status_code == 200
        assert response.get_json()["stage"] == expected_stage
        assert response.get_json()["task_id"] == task_id

    state = client.get("/api/cities/green-valley/rebuild").get_json()
    assert state["stage"] == 3
    assert state["inventory"]["weed_tool"] == 1
    assert state["inventory"]["shovel"] == 1
    assert state["inventory"]["wood"] == 0
    assert state["inventory"]["brick"] == 0


def test_market_unique_tools_cannot_be_bought_twice(client):
    conn = get_db()
    conn.execute("UPDATE user_data SET points = 500 WHERE id = 1")
    conn.commit()
    conn.close()

    first = client.post("/api/market/items/buy", json={"item_id": "weed_tool"})
    second = client.post("/api/market/items/buy", json={"item_id": "weed_tool"})
    assert first.status_code == 200
    assert second.status_code == 400

    conn = get_db()
    state = conn.execute("SELECT points FROM user_data WHERE id = 1").fetchone()
    owned = conn.execute(
        "SELECT quantity FROM user_inventory WHERE user_data_id = 1 AND item_id = 'weed_tool'"
    ).fetchone()
    conn.close()
    assert state["points"] == 450
    assert owned["quantity"] == 1


def test_decorations_unlock_after_shelter_and_use_fixed_slots(client):
    conn = get_db()
    conn.execute("UPDATE user_data SET points = 500 WHERE id = 1")
    conn.commit()
    conn.close()
    locked_purchase = client.post(
        "/api/market/items/buy",
        json={"item_id": "tree"},
    )
    assert locked_purchase.status_code == 400

    before_rebuild = client.post(
        "/api/cities/green-valley/decorations/place",
        json={"slot_id": "west-garden", "decoration_id": "tree"},
    )
    assert before_rebuild.status_code == 400

    add_stock("weed_tool", 1)
    add_stock("weed", 10)
    add_stock("shovel", 1)
    add_stock("debris", 5)
    add_stock("wood", 10)
    add_stock("brick", 10)
    add_stock("tree", 1)
    for _ in range(3):
        assert client.post("/api/cities/green-valley/rebuild/complete").status_code == 200
    market = client.get("/api/market/catalog").get_json()
    tree_item = next(item for item in market["items"] if item["item_id"] == "tree")
    assert tree_item["unlocked"] is True

    placed = client.post(
        "/api/cities/green-valley/decorations/place",
        json={"slot_id": "west-garden", "decoration_id": "tree"},
    )
    duplicate = client.post(
        "/api/cities/green-valley/decorations/place",
        json={"slot_id": "west-garden", "decoration_id": "fountain"},
    )
    invalid_slot = client.post(
        "/api/cities/green-valley/decorations/place",
        json={"slot_id": "free-placement", "decoration_id": "tree"},
    )
    assert placed.status_code == 200
    assert duplicate.status_code == 409
    assert invalid_slot.status_code == 400

    state = client.get("/api/cities/green-valley/rebuild").get_json()
    assert state["decorations"] == [
        {"slot_id": "west-garden", "decoration_id": "tree"}
    ]
    assert state["inventory"]["tree"] == 0


def test_other_cities_are_not_rebuilt_in_this_mvp(client):
    response = client.get("/api/cities/crystal-village/rebuild")
    assert response.status_code == 404
