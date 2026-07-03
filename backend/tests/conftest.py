import os

# Set a stable signing key for the test process before any auth code runs.
os.environ.setdefault("SECRET_KEY", "test-secret")

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import create_app
from app.seed import DEMO_USERNAME, seed_if_empty


@pytest.fixture
def db_url(tmp_path) -> Iterator[str]:
    url = f"sqlite:///{tmp_path / 'pm.db'}"
    database.configure(url)
    yield url


@pytest.fixture
def app(db_url):
    return create_app(static_dir=None)


@pytest.fixture
def client(app) -> Iterator[TestClient]:
    # Run the startup event so init_db + seed run once per app instance.
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def authed_client(client: TestClient) -> TestClient:
    response = client.post(
        "/api/login",
        json={"username": DEMO_USERNAME, "password": "password"},
    )
    assert response.status_code == 200
    return client
