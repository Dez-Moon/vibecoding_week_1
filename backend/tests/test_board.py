from fastapi.testclient import TestClient


def test_get_board_requires_auth(client: TestClient):
    response = client.get("/api/board")
    assert response.status_code == 401


def test_get_board_returns_full_structure(authed_client: TestClient):
    response = authed_client.get("/api/board")
    assert response.status_code == 200
    payload = response.json()

    assert "columns" in payload and "cards" in payload
    titles = [c["title"] for c in payload["columns"]]
    assert titles == ["Backlog", "Discovery", "In Progress", "Review", "Done"]

    all_card_ids: list[str] = []
    for c in payload["columns"]:
        all_card_ids.extend(c["card_ids"])
    assert all(card_id in payload["cards"] for card_id in all_card_ids)
    assert len(payload["cards"]) == 8
    for card in payload["cards"].values():
        assert {"id", "title", "details", "position", "column_id"} <= card.keys()
