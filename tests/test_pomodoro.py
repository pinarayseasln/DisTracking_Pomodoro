from models.user import get_user_data


def test_pomodoro_completion(client):
    # Başlangıç kullanıcı bilgilerini al
    user_before = get_user_data()

    initial_points = user_before["points"]
    initial_sessions = user_before["completed_sessions"]

    # Pomodoro tamamlanma isteği gönder
    response = client.post(
        "/api/pomodoro/complete",
        json={"focus_minutes": 10}
    )

    # İstek başarılı mı?
    assert response.status_code == 200

    # Güncel kullanıcı bilgilerini al
    user_after = get_user_data()

    # Puan 10 artmış mı?
    assert user_after["points"] == initial_points + 10

    # Tamamlanan oturum sayısı 1 artmış mı?
    assert user_after["completed_sessions"] == initial_sessions + 1
