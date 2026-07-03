from fastapi.testclient import TestClient

PROTECTED_PATHS = [
    ("GET", "/api/board"),
    ("PATCH", "/api/board"),
    ("POST", "/api/board/cards"),
    ("PATCH", "/api/board/cards/abc"),
    ("DELETE", "/api/board/cards/abc"),
    ("POST", "/api/board/cards/abc/move"),
]


def test_unauthenticated_requests_get_401(client: TestClient):
    for method, path in PROTECTED_PATHS:
        if method == "GET":
            response = client.get(path)
        elif method == "PATCH":
            response = client.patch(path, json={})
        elif method == "POST":
            response = client.post(path, json={})
        elif method == "DELETE":
            response = client.delete(path)
        else:
            raise AssertionError(f"unhandled method {method}")
        assert response.status_code == 401, f"{method} {path} should be 401, got {response.status_code}"


def test_logged_in_request_with_invalid_card_id_returns_404(client: TestClient):
    client.post("/api/login", json={"username": "user", "password": "password"})
    response = client.patch(
        "/api/board/cards/does-not-exist",
        json={"title": "Whatever"},
    )
    assert response.status_code == 404
