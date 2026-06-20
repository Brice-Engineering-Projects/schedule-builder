from schedule_builder.config.settings import settings


def test_admin_ping_requires_token(client) -> None:
    response = client.get("/v1/admin/ping")

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Missing admin token",
            "details": {},
        }
    }


def test_admin_ping_rejects_invalid_token(client) -> None:
    response = client.get(
        "/v1/admin/ping",
        headers={"x-admin-token": "wrong-token"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "error": {
            "code": "forbidden",
            "message": "Invalid admin token",
            "details": {},
        }
    }


def test_admin_ping_accepts_valid_token(client) -> None:
    response = client.get(
        "/v1/admin/ping",
        headers={"x-admin-token": settings.admin_api_token},
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "admin access granted",
    }
