from fastapi import FastAPI
from fastapi.testclient import TestClient

from schedule_builder.core.exceptions import NotFoundError, register_exception_handlers


def _build_test_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/raise-not-found")
    async def raise_not_found() -> None:
        raise NotFoundError("User not found", details={"user_id": "123"})

    @app.get("/raise-unexpected")
    async def raise_unexpected() -> None:
        raise RuntimeError("boom")

    @app.get("/items/{item_id}")
    async def get_item(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    return app


def test_app_exception_returns_consistent_payload() -> None:
    app = _build_test_app()
    client = TestClient(app)

    response = client.get("/raise-not-found")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": "User not found",
            "details": {"user_id": "123"},
        }
    }


def test_unhandled_exception_returns_500_payload() -> None:
    app = _build_test_app()
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/raise-unexpected")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "internal_server_error",
            "message": "An unexpected error occurred",
            "details": {},
        }
    }


def test_validation_exception_returns_422_payload() -> None:
    app = _build_test_app()
    client = TestClient(app)

    response = client.get("/items/not-an-int")

    payload = response.json()
    assert response.status_code == 422
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["message"] == "Request validation failed"
    assert isinstance(payload["error"]["details"]["errors"], list)
