from database.db import get_db
from database.db import init_db


def test_market_catalog_has_buildings_and_rebuild_items(client):
    response = client.get("/api/market/catalog")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert {item["building_type"] for item in data["buildings"]} == {
        "cabin", "house", "watchtower"
    }
    assert "shelter" not in {item["building_type"] for item in data["buildings"]}
    assert {
        "wood", "brick", "weed", "debris", "weed_tool", "shovel",
        "stone", "nails", "hammer", "saw", "repair_kit",
        "fountain", "tree", "flower_bed",
    } == {item["item_id"] for item in data["items"]}
    assert all(item["quantity"] == 0 for item in data["items"])


def test_buy_market_item_updates_inventory_and_points(client):
    conn = get_db()
    conn.execute("UPDATE user_data SET points = 30 WHERE id = 1")
    conn.commit()
    conn.close()

    response = client.post(
        "/api/market/items/buy",
        json={"item_id": "wood"},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["quantity"] == 1
    assert data["points"] == 15

    repeated = client.post(
        "/api/market/items/buy",
        json={"item_id": "wood"},
    )
    assert repeated.status_code == 200
    assert repeated.get_json()["quantity"] == 2


def test_market_item_purchase_rejects_insufficient_points(client):
    response = client.post(
        "/api/market/items/buy",
        json={"item_id": "wood"},
    )
    assert response.status_code == 400
    assert response.get_json()["success"] is False

    conn = get_db()
    quantity = conn.execute(
        """SELECT quantity FROM user_inventory
           WHERE user_data_id = 1 AND item_id = ?""",
        ("wood",),
    ).fetchone()
    conn.close()
    assert quantity is None


def test_market_item_purchase_rejects_unknown_item(client):
    response = client.post(
        "/api/market/items/buy",
        json={"item_id": "shelter"},
    )
    assert response.status_code == 404
    assert response.get_json()["success"] is False


def test_existing_market_inventory_is_copied_without_deleting_legacy_rows(client):
    conn = get_db()
    conn.execute(
        "INSERT INTO market_inventory (item_id, quantity) VALUES ('timber', 3)"
    )
    conn.commit()
    conn.close()

    init_db()

    conn = get_db()
    old_row = conn.execute(
        "SELECT quantity FROM market_inventory WHERE item_id = 'timber'"
    ).fetchone()
    new_row = conn.execute(
        """SELECT quantity FROM user_inventory
           WHERE user_data_id = 1 AND item_id = 'wood'"""
    ).fetchone()
    conn.close()
    assert old_row["quantity"] == 3
    assert new_row["quantity"] == 3
