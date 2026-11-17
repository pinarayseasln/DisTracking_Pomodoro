def test_user_info(client):
    response = client.get("/api/user")

    assert response.status_code == 200

    data = response.get_json()

    assert "points" in data
    assert "completed_sessions" in data

    assert data["points"] == 0
    assert data["completed_sessions"] == 0


def test_random_challenge(client):
    response = client.get("/api/challenge/random")

    assert response.status_code == 200

    data = response.get_json()

    assert "soru" in data
    assert "secenekler" in data
    assert "cevap" in data

    assert data["cevap"] in data["secenekler"]

def test_homepage(client):
    response = client.get("/")

    assert response.status_code == 200
