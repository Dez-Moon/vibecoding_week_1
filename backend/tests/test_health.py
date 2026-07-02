from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def test_health() -> None:
    client = TestClient(create_app())
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_does_not_require_static_dir() -> None:
    client = TestClient(create_app(static_dir=Path("/nonexistent")))
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
