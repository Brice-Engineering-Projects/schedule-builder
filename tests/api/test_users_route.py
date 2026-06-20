def test_get_me_requires_auth(client) -> None:
    response = client.get("/v1/users/me")

    assert response.status_code == 401


def test_get_me_returns_authenticated_user(client) -> None:
    # Register and log in to obtain a token
    client.post(
        "/auth/register",
        json={"email": "me@example.com", "password": "securepass1", "full_name": "Me User"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "me@example.com", "password": "securepass1"},
    )
    token = login.json()["tokens"]["access_token"]

    response = client.get("/v1/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["full_name"] == "Me User"
    assert data["is_active"] is True
    assert "id" in data
