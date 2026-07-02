from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def _make_static_dir(tmp_path: Path) -> Path:
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "index.html").write_text("<html><head><title>Kanban Studio</title></head><body>hi</body></html>")
    assets = static_dir / "_next" / "static"
    assets.mkdir(parents=True)
    (assets / "test.js").write_text("// test asset")
    return static_dir


def test_frontend_served(tmp_path: Path) -> None:
    app = create_app(static_dir=_make_static_dir(tmp_path))
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Kanban Studio" in response.text


def test_static_assets(tmp_path: Path) -> None:
    app = create_app(static_dir=_make_static_dir(tmp_path))
    client = TestClient(app)
    response = client.get("/_next/static/test.js")
    assert response.status_code == 200
    assert response.text == "// test asset"
