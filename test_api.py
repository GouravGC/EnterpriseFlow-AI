
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from main import app
from ai_service import AIServiceError


def test_root():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["docs"] == "/docs"


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_ask_requires_ai_configuration():
    with TestClient(app) as client:
        app.state.ai_service = None
        response = client.post(
            "/ask",
            json={"question": "How do I reset my password?"},
        )
        assert response.status_code == 503


def test_ask_rejects_short_question():
    with TestClient(app) as client:
        response = client.post("/ask", json={"question": "Hi"})
        assert response.status_code == 422


def test_ask_success_with_mocked_ai():
    with TestClient(app) as client:
        mock_service = AsyncMock()
        mock_service.answer.return_value = "Follow the password reset SOP."
        app.state.ai_service = mock_service

        response = client.post(
            "/ask",
            json={"question": "How do I reset my password?"},
        )

        assert response.status_code == 200
        assert response.json()["answer"] == "Follow the password reset SOP."


def test_ask_handles_provider_failure():
    with TestClient(app) as client:
        mock_service = AsyncMock()
        mock_service.answer.side_effect = AIServiceError(
            "The AI provider request failed."
        )
        app.state.ai_service = mock_service

        response = client.post(
            "/ask",
            json={"question": "How do I reset my password?"},
        )

        assert response.status_code == 502
