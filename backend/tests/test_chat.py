import json
from unittest.mock import MagicMock, patch

import pytest

from app import schemas
from app.services.chat import apply_operations, build_system_prompt


class TestChatEndpoint:
    @pytest.fixture
    def client(self, app):
        from fastapi.testclient import TestClient
        return TestClient(app)

    def test_chat_requires_auth(self, client):
        response = client.post("/api/ai/chat", json={"message": "hello"})
        assert response.status_code == 401

    def test_chat_returns_response_only(self, authed_client):
        mock_response = json.dumps({"response": "Hello! How can I help?"})

        with patch("app.main.call_ai") as mock_call:
            mock_call.return_value = mock_response

            response = authed_client.post(
                "/api/ai/chat",
                json={"message": "Hello", "conversation_history": None},
            )

            assert response.status_code == 200
            data = response.json()
            assert "Hello! How can I help?" in data["response"]
            assert data["board_update"] is None
            assert "board" in data

    def test_chat_includes_conversation_history(self, authed_client):
        mock_response = json.dumps({"response": "Continuing our conversation"})

        with patch("app.main.call_ai") as mock_call:
            mock_call.return_value = mock_response

            history = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]
            response = authed_client.post(
                "/api/ai/chat",
                json={"message": "Continue", "conversation_history": history},
            )

            assert response.status_code == 200
            calls = mock_call.call_args[0][0]
            assert len(calls) == 4  # system + 2 history + user
            assert calls[1]["content"] == "Hello"
            assert calls[2]["content"] == "Hi"
            assert calls[3]["content"] == "Continue"

    def test_chat_create_card_operation(self, authed_client):
        # Get the actual board to find real column IDs
        board_response = authed_client.get("/api/board")
        board_data = board_response.json()
        backlog_col = next(c for c in board_data["columns"] if c["title"] == "Backlog")

        mock_response = json.dumps({
            "response": "Created a card!",
            "board_update": {
                "operations": [
                    {"op": "create_card", "column_id": backlog_col["id"], "title": "New Card", "details": "Details"}
                ]
            }
        })

        with patch("app.main.call_ai") as mock_call:
            mock_call.return_value = mock_response

            response = authed_client.post(
                "/api/ai/chat",
                json={"message": "Create a card"},
            )

            assert response.status_code == 200
            data = response.json()
            assert "Created a card!" in data["response"]
            assert data["board_update"] is not None
            # Verify card was created in the board
            cards = data["board"]["cards"]
            new_card = next((c for c in cards.values() if c["title"] == "New Card"), None)
            assert new_card is not None
            assert new_card["column_id"] == backlog_col["id"]

    def test_chat_invalid_operation_rejected(self, authed_client):
        mock_response = json.dumps({
            "response": "I tried to update a non-existent card.",
            "board_update": {
                "operations": [
                    {"op": "update_card", "card_id": "non-existent-id", "title": "Updated"}
                ]
            }
        })

        with patch("app.main.call_ai") as mock_call:
            mock_call.return_value = mock_response

            response = authed_client.post(
                "/api/ai/chat",
                json={"message": "Update non-existent card"},
            )

            assert response.status_code == 200
            data = response.json()
            # Invalid op should cause board_update to be None
            assert data["board_update"] is None

    def test_chat_move_card_operation(self, authed_client):
        # Get the actual board to find real IDs
        board_response = authed_client.get("/api/board")
        board_data = board_response.json()
        first_col = board_data["columns"][0]
        second_col = board_data["columns"][1]
        first_card_id = first_col["card_ids"][0] if first_col["card_ids"] else None

        if not first_card_id:
            pytest.skip("No cards on board for move test")

        mock_response = json.dumps({
            "response": "Moved the card!",
            "board_update": {
                "operations": [
                    {"op": "move_card", "card_id": first_card_id, "column_id": second_col["id"], "position": 0}
                ]
            }
        })

        with patch("app.main.call_ai") as mock_call:
            mock_call.return_value = mock_response

            response = authed_client.post(
                "/api/ai/chat",
                json={"message": "Move card to column 2"},
            )

            assert response.status_code == 200
            data = response.json()
            card = data["board"]["cards"].get(first_card_id)
            assert card is not None
            assert card["column_id"] == second_col["id"]

    def test_chat_rename_column_operation(self, authed_client):
        # Get the actual board to find real column IDs
        board_response = authed_client.get("/api/board")
        board_data = board_response.json()
        first_col = board_data["columns"][0]

        mock_response = json.dumps({
            "response": "Renamed the column!",
            "board_update": {
                "operations": [
                    {"op": "rename_column", "column_id": first_col["id"], "title": "New Column Name"}
                ]
            }
        })

        with patch("app.main.call_ai") as mock_call:
            mock_call.return_value = mock_response

            response = authed_client.post(
                "/api/ai/chat",
                json={"message": "Rename column"},
            )

            assert response.status_code == 200
            data = response.json()
            col = next((c for c in data["board"]["columns"] if c["id"] == first_col["id"]), None)
            assert col is not None
            assert col["title"] == "New Column Name"

    def test_chat_delete_card_operation(self, authed_client):
        # Get the actual board to find real card IDs
        board_response = authed_client.get("/api/board")
        board_data = board_response.json()
        first_card_id = board_data["columns"][0]["card_ids"][0] if board_data["columns"][0]["card_ids"] else None

        if not first_card_id:
            pytest.skip("No cards on board for delete test")

        mock_response = json.dumps({
            "response": "Deleted the card!",
            "board_update": {
                "operations": [
                    {"op": "delete_card", "card_id": first_card_id}
                ]
            }
        })

        with patch("app.main.call_ai") as mock_call:
            mock_call.return_value = mock_response

            response = authed_client.post(
                "/api/ai/chat",
                json={"message": "Delete card"},
            )

            assert response.status_code == 200
            data = response.json()
            assert first_card_id not in data["board"]["cards"]

    def test_chat_non_json_response_falls_back(self, authed_client):
        with patch("app.main.call_ai") as mock_call:
            mock_call.return_value = "I don't understand, but here is my thoughts..."

            response = authed_client.post(
                "/api/ai/chat",
                json={"message": "Something weird"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "I don't understand, but here is my thoughts..."


class TestChatIntegration:
    @pytest.fixture
    def client(self, app):
        from fastapi.testclient import TestClient
        return TestClient(app)

    def test_chat_smoke_test_with_real_api(self, client):
        api_key = __import__("os").environ.get("OPENROUTER_API_KEY")
        if not api_key or api_key == "test-key":
            pytest.skip("OPENROUTER_API_KEY not set")

        # Login first
        client.post("/api/login", json={"username": "user", "password": "password"})

        response = client.post(
            "/api/ai/chat",
            json={
                "message": "Create a card titled 'Smoke test card' in the Backlog column.",
                "conversation_history": None,
            },
        )

        assert response.status_code == 200
        data = response.json()
        cards = data["board"]["cards"]
        assert any(c["title"] == "Smoke test card" for c in cards.values())

        # Cleanup: delete the test card
        test_card = next(
            (cid for cid, c in data["board"]["cards"].items() if c["title"] == "Smoke test card"),
            None
        )
        if test_card:
            client.delete(f"/api/board/cards/{test_card}")
