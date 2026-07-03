import os
from unittest.mock import MagicMock, patch

import pytest

from app.services.ai import FALLBACK_MODEL, PRIMARY_MODEL, call_ai

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")


class TestCallAI:
    def test_primary_response_returned_when_successful(self):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="4"))]

        with patch("app.services.ai.OpenAI") as mock_client:
            mock_instance = MagicMock()
            mock_instance.chat.completions.create.return_value = mock_response
            mock_client.return_value = mock_instance

            result = call_ai([{"role": "user", "content": "What is 2+2?"}])

            assert result == "4"
            mock_instance.chat.completions.create.assert_called_once_with(
                model=PRIMARY_MODEL,
                messages=[{"role": "user", "content": "What is 2+2?"}],
            )

    def test_fallback_used_when_primary_fails(self):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="4"))]

        with patch("app.services.ai.OpenAI") as mock_client:
            mock_instance = MagicMock()
            mock_instance.chat.completions.create.side_effect = [
                Exception("Primary model unavailable"),
                mock_response,
            ]
            mock_client.return_value = mock_instance

            result = call_ai([{"role": "user", "content": "What is 2+2?"}])

            assert result == "4"
            assert mock_instance.chat.completions.create.call_count == 2
            mock_instance.chat.completions.create.assert_any_call(
                model=PRIMARY_MODEL,
                messages=[{"role": "user", "content": "What is 2+2?"}],
            )
            mock_instance.chat.completions.create.assert_any_call(
                model=FALLBACK_MODEL,
                messages=[{"role": "user", "content": "What is 2+2?"}],
            )


class TestAIEndpoint:
    @pytest.fixture
    def client(self, app):
        from fastapi.testclient import TestClient
        return TestClient(app)

    def test_ai_test_endpoint(self, client):
        mock_response = "4"
        with patch("app.services.ai.OpenAI") as mock_client:
            mock_instance = MagicMock()
            mock_instance.chat.completions.create.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content=mock_response))]
            )
            mock_client.return_value = mock_instance

            response = client.post("/api/ai/test")

            assert response.status_code == 200
            assert "4" in response.json()["response"]


class TestAIIntegration:
    @pytest.fixture
    def client(self, app):
        from fastapi.testclient import TestClient
        return TestClient(app)

    def test_ai_test_with_real_api(self, client):
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key or api_key == "test-key":
            pytest.skip("OPENROUTER_API_KEY not set")

        response = client.post("/api/ai/test")

        assert response.status_code == 200
        assert "4" in response.json()["response"]
