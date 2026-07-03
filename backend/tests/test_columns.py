from fastapi.testclient import TestClient


def _column_ids(payload, *titles):
    return {c["id"]: c["title"] for c in payload["columns"] if c["title"] in titles}


def test_patch_board_renames_columns(authed_client: TestClient):
    initial = authed_client.get("/api/board").json()
    by_title = {c["title"]: c["id"] for c in initial["columns"]}
    rename_targets = [
        {"id": by_title["Backlog"], "title": "Ideas"},
        {"id": by_title["Discovery"], "title": "Research"},
    ]

    response = authed_client.patch(
        "/api/board", json={"columns": rename_targets}
    )
    assert response.status_code == 200
    updated = response.json()
    after = {c["title"] for c in updated["columns"]}
    assert {"Ideas", "Research"}.issubset(after)
    assert "Backlog" not in after and "Discovery" not in after

    # Untouched columns stayed put.
    assert "In Progress" in after and "Review" in after and "Done" in after


def test_patch_board_only_renames_specified_columns(authed_client: TestClient):
    initial = authed_client.get("/api/board").json()
    target = next(c for c in initial["columns"] if c["title"] == "Backlog")

    response = authed_client.patch(
        "/api/board",
        json={"columns": [{"id": target["id"], "title": "Queue"}]},
    )
    assert response.status_code == 200
    updated = response.json()
    titles = [c["title"] for c in updated["columns"]]
    assert titles == ["Queue", "Discovery", "In Progress", "Review", "Done"]


def test_patch_board_rejects_unknown_column_id(authed_client: TestClient):
    response = authed_client.patch(
        "/api/board",
        json={"columns": [{"id": "not-a-real-id", "title": "Nope"}]},
    )
    assert response.status_code == 200  # unknown ids are silently ignored
    # Nothing should have changed.
    titles = [c["title"] for c in response.json()["columns"]]
    assert titles == ["Backlog", "Discovery", "In Progress", "Review", "Done"]


def test_patch_board_rejects_empty_title(authed_client: TestClient):
    initial = authed_client.get("/api/board").json()
    target = next(c for c in initial["columns"] if c["title"] == "Backlog")
    response = authed_client.patch(
        "/api/board",
        json={"columns": [{"id": target["id"], "title": ""}]},
    )
    assert response.status_code == 422
