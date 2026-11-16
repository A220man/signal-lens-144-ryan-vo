import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.workflow import Provider, Reviewer, Review, ReviewStatus, WorkflowStatus


@pytest.mark.asyncio
async def test_effectiveness_metrics_after_ingest():
    """Test that effectiveness metrics are computed after ingesting transcripts."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Ingest transcript entries
        await client.post(
            "/api/hooks/ingest",
            json=[
                {
                    "prompt_id": "p1",
                    "session_type": "main",
                    "event_type": "open",
                },
                {
                    "prompt_id": "p2",
                    "session_type": "main",
                    "event_type": "router",
                },
                {
                    "prompt_id": "p3",
                    "session_type": "main",
                    "event_type": "open",
                },
                {
                    "prompt_id": "p4",
                    "session_type": "subagent",
                    "event_type": "open",
                },
                {
                    "prompt_id": "p5",
                    "session_type": "subagent",
                    "event_type": "open",
                },
                {
                    "prompt_id": "p6",
                    "session_type": "subagent",
                    "event_type": "playbook",
                },
            ],
        )

        # Get effectiveness metrics
        response = await client.get("/api/hooks/effectiveness")
        assert response.status_code == 200
        data = response.json()

        # Main session: 2 opens out of 3 prompts = 66.67 per 100
        main_metrics = next(m for m in data if m["session_type"] == "main")
        assert main_metrics["total_prompts"] == 3
        assert main_metrics["open_count"] == 2
        assert main_metrics["opens_per_100"] == pytest.approx(66.67, abs=0.1)

        # Subagent session: 2 opens out of 3 prompts = 66.67 per 100
        subagent_metrics = next(m for m in data if m["session_type"] == "subagent")
        assert subagent_metrics["total_prompts"] == 3
        assert subagent_metrics["open_count"] == 2
        assert subagent_metrics["opens_per_100"] == pytest.approx(66.67, abs=0.1)

        # Subagent has 1 playbook, main has 0
        assert subagent_metrics["playbook_count"] == 1
        assert main_metrics["playbook_count"] == 0


@pytest.mark.asyncio
async def test_effectiveness_no_data():
    """Test effectiveness metrics with no ingested data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/hooks/effectiveness")
        assert response.status_code == 200
        data = response.json()
        assert data == []


@pytest.mark.asyncio
async def test_effectiveness_rounding():
    """Test that opens_per_100 is properly rounded to 2 decimal places."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1 open in 4 prompts = 25.0 per 100
        await client.post(
            "/api/hooks/ingest",
            json=[
                {"prompt_id": "1", "session_type": "main", "event_type": "open"},
                {"prompt_id": "2", "session_type": "main", "event_type": "router"},
                {"prompt_id": "3", "session_type": "main", "event_type": "principle"},
                {"prompt_id": "4", "session_type": "main", "event_type": "router"},
            ],
        )

        response = await client.get("/api/hooks/effectiveness")
        assert response.status_code == 200
        data = response.json()

        main_metrics = next(m for m in data if m["session_type"] == "main")
        assert main_metrics["opens_per_100"] == pytest.approx(25.0, abs=0.01)
