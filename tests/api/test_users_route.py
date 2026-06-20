def test_get_user_success(client) -> None:
    response = client.get("/v1/users/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "admin@schedulebuilder.com",
        "full_name": "Schedule Builder Admin",
        "status": "active",
    }


def test_get_user_not_found_uses_app_exception_shape(client) -> None:
    response = client.get("/v1/users/999")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": "User not found",
            "details": {"user_id": 999},
        }
    }


def test_get_user_bad_request_uses_app_exception_shape(client) -> None:
    response = client.get("/v1/users/0")

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "bad_request",
            "message": "User ID must be a positive integer",
            "details": {"user_id": 0},
        }
    }
