from database.db import get_db


def test_buy_building_success(client):
    conn = get_db()
    conn.execute("UPDATE user_data SET points = 50 WHERE id = 1")
    conn.commit()
    conn.close()

    response = client.post(
        "/api/building/buy",
        json={"building_type": "cabin"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["points"] == 0

    conn = get_db()
    building = conn.execute(
        "SELECT * FROM buildings WHERE building_type = ?",
        ("cabin",),
    ).fetchone()
    conn.close()
    assert building is not None


def test_buy_building_without_points(client):
    response = client.post(
        "/api/building/buy",
        json={"building_type": "cabin"},
    )
    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_buy_building_already_owned(client):
    conn = get_db()
    conn.execute("UPDATE user_data SET points = 50 WHERE id = 1")
    conn.execute(
        """
        INSERT INTO buildings (name, building_type, cost)
        VALUES (?, ?, ?)
        """,
        ("Cabin", "cabin", 50),
    )
    conn.commit()
    conn.close()

    response = client.post(
        "/api/building/buy",
        json={"building_type": "cabin"},
    )
    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_shelter_is_no_longer_available_for_purchase(client):
    catalog = client.get("/api/market/catalog").get_json()
    assert all(item["building_type"] != "shelter" for item in catalog["buildings"])

    response = client.post(
        "/api/building/buy",
        json={"building_type": "shelter"},
    )
    assert response.status_code == 404
    assert response.get_json()["success"] is False
