from database.db import get_db


def test_buy_building_success(client):
    # Test kullanıcısına 20 puan ver
    conn = get_db()
    conn.execute(
        "UPDATE user_data SET points = 20 WHERE id = 1"
    )
    conn.commit()
    conn.close()

    # Bina satın alma isteği gönder
    response = client.post("/api/building/buy")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["points"] == 0

    # Binanın veritabanına kaydedildiğini kontrol et
    conn = get_db()

    building = conn.execute(
        "SELECT * FROM buildings WHERE building_type = ?",
        ("shelter",)
    ).fetchone()

    conn.close()

    assert building is not None


def test_buy_building_without_points(client):
    # Kullanıcının 0 puanı var
    response = client.post("/api/building/buy")

    assert response.status_code == 400
    assert response.get_json()["success"] is False

def test_buy_building_already_owned(client):
    from database.db import get_db

    # Kullanıcıya 20 puan ver
    conn = get_db()
    conn.execute(
        "UPDATE user_data SET points = 20 WHERE id = 1"
    )

    # Kullanıcının zaten sahip olduğu binayı ekle
    conn.execute(
        """
        INSERT INTO buildings (name, building_type, cost)
        VALUES (?, ?, ?)
        """,
        ("Shelter", "shelter", 20)
    )

    conn.commit()
    conn.close()

    # Aynı binayı tekrar satın almaya çalış
    response = client.post(
        "/api/building/buy",
        json={"building_type": "shelter"}
    )

    assert response.status_code == 400
    assert response.json["success"] is False