from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def _client() -> TestClient:
    return TestClient(create_app(static_dir=Path("/nonexistent")))


def test_login_success_returns_cookie_and_username() -> None:
    client = _client()
    response = client.post(
        "/api/login", json={"username": "user", "password": "password"}
    )
    assert response.status_code == 200
    assert response.json() == {"username": "user"}
    assert "pm_session" in response.cookies


def test_login_failure_returns_401() -> None:
    client = _client()
    response = client.post(
        "/api/login", json={"username": "user", "password": "wrong"}
    )
    assert response.status_code == 401
    assert "pm_session" not in response.cookies


def test_whoami_without_cookie_returns_401() -> None:
    client = _client()
    response = client.get("/api/whoami")
    assert response.status_code == 401


def test_whoami_with_cookie_returns_username() -> None:
    client = _client()
    client.post("/api/login", json={"username": "user", "password": "password"})
    response = client.get("/api/whoami")
    assert response.status_code == 200
    assert response.json() == {"username": "user"}


def test_logout_clears_cookie() -> None:
    client = _client()
    client.post("/api/login", json={"username": "user", "password": "password"})
    response = client.post("/api/logout")
    assert response.status_code == 204
    pm_session = response.cookies.get("pm_session")
    assert pm_session is None or pm_session == ""
