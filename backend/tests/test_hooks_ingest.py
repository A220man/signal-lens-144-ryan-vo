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


@pytest.mark.asyncio
async def test_ingest_local_jsonl_file():
    """Test ingesting a local transcript JSONL upload with blank lines."""
    transcript = b'{"prompt_id":"file-1","session_type":"main","event_type":"open"}\n\n{"prompt_id":"file-2","session_type":"subagent","event_type":"router"}\n'
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/hooks/ingest-file",
            files={"file": ("transcript.jsonl", transcript, "application/x-ndjson")},
        )
        assert response.status_code == 202
        assert response.json() == {"status": "accepted", "entries_ingested": 2}

        metrics = await client.get("/api/hooks/effectiveness")
        assert metrics.status_code == 200
        by_type = {item["session_type"]: item for item in metrics.json()}
        assert by_type["main"]["total_prompts"] == 1
        assert by_type["main"]["opens_per_100"] == 100.0
        assert by_type["subagent"]["router_count"] == 1
