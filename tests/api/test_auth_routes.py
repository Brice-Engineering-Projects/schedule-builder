def test_register_and_login_and_me_flow(client) -> None:
    register_response = client.post(
        "/auth/register",
        json={
            "email": "new.user@example.com",
            "password": "S3curePassw0rd!",
            "full_name": "New User",
        },
    )

    assert register_response.status_code == 201
    registered_user = register_response.json()
    assert registered_user["email"] == "new.user@example.com"
    assert registered_user["full_name"] == "New User"

    login_response = client.post(
        "/auth/login",
        json={
            "email": "new.user@example.com",
            "password": "S3curePassw0rd!",
        },
    )

    assert login_response.status_code == 200
    login_payload = login_response.json()
    assert login_payload["tokens"]["token_type"] == "bearer"
    access_token = login_payload["tokens"]["access_token"]

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "new.user@example.com"


def test_register_duplicate_email_returns_conflict(client) -> None:
    payload = {
        "email": "duplicate@example.com",
        "password": "S3curePassw0rd!",
        "full_name": "Duplicate User",
    }

    first = client.post("/auth/register", json=payload)
    second = client.post("/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "conflict"


def test_login_invalid_credentials_returns_unauthorized(client) -> None:
    client.post(
        "/auth/register",
        json={
            "email": "invalid-login@example.com",
            "password": "S3curePassw0rd!",
            "full_name": "Invalid Login",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "invalid-login@example.com",
            "password": "WrongPassword1!",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"
