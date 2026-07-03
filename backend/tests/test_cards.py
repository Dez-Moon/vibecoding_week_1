from fastapi.testclient import TestClient


def _column(payload, title):
    for c in payload["columns"]:
        if c["title"] == title:
            return c
    raise AssertionError(f"column {title} missing")


def _card_by_title(payload, title):
    for card in payload["cards"].values():
        if card["title"] == title:
            return card
    raise AssertionError(f"card {title} missing")


def test_create_card_appends_to_column(authed_client: TestClient):
    initial = authed_client.get("/api/board").json()
    target = _column(initial, "Backlog")
    initial_count = len(target["card_ids"])

    response = authed_client.post(
        "/api/board/cards",
        json={
            "column_id": target["id"],
            "title": "Playwright created card",
            "details": "Hello",
        },
    )
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "Playwright created card"
    assert created["position"] == initial_count

    after = authed_client.get("/api/board").json()
    after_column = next(c for c in after["columns"] if c["id"] == target["id"])
    assert len(after_column["card_ids"]) == initial_count + 1
    assert after_column["card_ids"][-1] == created["id"]


def test_update_card_changes_title_and_details(authed_client: TestClient):
    initial = authed_client.get("/api/board").json()
    card = next(iter(initial["cards"].values()))

    response = authed_client.patch(
        f"/api/board/cards/{card['id']}",
        json={"title": "Renamed", "details": "Updated body"},
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "Renamed"
    assert updated["details"] == "Updated body"
    assert updated["id"] == card["id"]


def test_update_card_partial_keeps_omitted_fields(authed_client: TestClient):
    initial = authed_client.get("/api/board").json()
    card = next(iter(initial["cards"].values()))
    original_details = card["details"]

    response = authed_client.patch(
        f"/api/board/cards/{card['id']}", json={"title": "Only title"}
    )
    assert response.status_code == 200
    assert response.json()["details"] == original_details


def test_delete_card_renumbers_source_column(authed_client: TestClient):
    initial = authed_client.get("/api/board").json()
    in_progress = _column(initial, "In Progress")
    target = in_progress["card_ids"][0]
    remaining_count = len(in_progress["card_ids"]) - 1

    response = authed_client.delete(f"/api/board/cards/{target}")
    assert response.status_code == 204

    after = authed_client.get("/api/board").json()
    after_column = next(c for c in after["columns"] if c["id"] == in_progress["id"])
    assert target not in after_column["card_ids"]
    assert len(after_column["card_ids"]) == remaining_count
    positions = [after["cards"][cid]["position"] for cid in after_column["card_ids"]]
    assert positions == list(range(remaining_count))


def test_move_card_to_other_column_renumbers_both(authed_client: TestClient):
    initial = authed_client.get("/api/board").json()
    backlog = _column(initial, "Backlog")
    review = _column(initial, "Review")
    moving = backlog["card_ids"][0]
    initial_backlog = len(backlog["card_ids"]) - 1
    initial_review = len(review["card_ids"]) + 1

    response = authed_client.post(
        f"/api/board/cards/{moving}/move",
        json={"column_id": review["id"], "position": 0},
    )
    assert response.status_code == 200

    after = authed_client.get("/api/board").json()
    after_backlog = next(c for c in after["columns"] if c["id"] == backlog["id"])
    after_review = next(c for c in after["columns"] if c["id"] == review["id"])
    assert moving not in after_backlog["card_ids"]
    assert after_review["card_ids"][0] == moving
    assert len(after_backlog["card_ids"]) == initial_backlog
    assert len(after_review["card_ids"]) == initial_review
    # Positions in both columns are 0..N-1.
    for column in (after_backlog, after_review):
        positions = [after["cards"][cid]["position"] for cid in column["card_ids"]]
        assert positions == list(range(len(column["card_ids"])))


def test_move_card_within_same_column_reorders(authed_client: TestClient):
    initial = authed_client.get("/api/board").json()
    in_progress = _column(initial, "In Progress")
    cards_in_column = list(in_progress["card_ids"])
    if len(cards_in_column) < 2:
        # Seed leaves 2 cards in In Progress; if it didn't, the test is meaningless.
        raise AssertionError("Test requires at least 2 cards in In Progress")

    moving = cards_in_column[0]
    response = authed_client.post(
        f"/api/board/cards/{moving}/move",
        json={"column_id": in_progress["id"], "position": len(cards_in_column) - 1},
    )
    assert response.status_code == 200

    after = authed_client.get("/api/board").json()
    after_column = next(c for c in after["columns"] if c["id"] == in_progress["id"])
    assert after_column["card_ids"][-1] == moving
    positions = [after["cards"][cid]["position"] for cid in after_column["card_ids"]]
    assert positions == list(range(len(after_column["card_ids"])))


def test_move_card_rejects_unknown_column(authed_client: TestClient):
    initial = authed_client.get("/api/board").json()
    card = next(iter(initial["cards"].values()))
    response = authed_client.post(
        f"/api/board/cards/{card['id']}/move",
        json={"column_id": "no-such-column", "position": 0},
    )
    assert response.status_code == 404


def test_move_card_clamps_position_above_max(authed_client: TestClient):
    initial = authed_client.get("/api/board").json()
    backlog = _column(initial, "Backlog")
    discovery = _column(initial, "Discovery")
    moving = backlog["card_ids"][0]

    response = authed_client.post(
        f"/api/board/cards/{moving}/move",
        json={"column_id": discovery["id"], "position": 999},
    )
    assert response.status_code == 200

    after = authed_client.get("/api/board").json()
    after_discovery = next(c for c in after["columns"] if c["id"] == discovery["id"])
    assert after_discovery["card_ids"][-1] == moving


def test_create_card_rejects_empty_title(authed_client: TestClient):
    initial = authed_client.get("/api/board").json()
    target = _column(initial, "Backlog")
    response = authed_client.post(
        "/api/board/cards",
        json={"column_id": target["id"], "title": "", "details": ""},
    )
    assert response.status_code == 422
