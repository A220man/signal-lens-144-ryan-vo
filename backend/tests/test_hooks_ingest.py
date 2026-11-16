import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.workflow import Provider, Reviewer, Review, ReviewStatus, WorkflowStatus, WorkflowRun


@pytest.mark.asyncio
async def test_ingest_transcript_entries():
    """Test ingesting transcript JSONL entries."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/hooks/ingest",
            json=[
                {
                    "prompt_id": "prompt-001",
                    "session_type": "main",
                    "event_type": "open",
                    "prompt_text": "Write a function to sort an array",
                    "model_name": "gpt-4o",
                },
                {
                    "prompt_id": "prompt-002",
                    "session_type": "subagent",
                    "event_type": "router",
                    "prompt_text": "Analyze the codebase",
                    "model_name": "claude-3-opus",
                },
                {
                    "prompt_id": "prompt-003",
                    "session_type": "main",
                    "event_type": "open",
                    "prompt_text": "Design the API schema",
                    "model_name": "gpt-4o",
                },
            ],
        )
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert data["entries_ingested"] == 3


@pytest.mark.asyncio
async def test_ingest_transcript_empty():
    """Test ingesting empty transcript list."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/hooks/ingest",
            json=[],
        )
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert data["entries_ingested"] == 0
