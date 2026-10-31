import pytest
from httpx import AsyncClient, ASGITransport
from uuid import UUID
from app.main import app


@pytest.mark.asyncio
async def test_create_workflow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/workflows",
            json={
                "initial_prompt": "Test prompt",
                "reviewers": [
                    {"provider": "claude", "prompt": "Review this code"},
                    {"provider": "codex", "prompt": "Analyze this code"},
                ],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "running"
        assert data["initial_prompt"] == "Test prompt"
        assert len(data["reviews"]) == 2
        assert UUID(data["id"])


@pytest.mark.asyncio
async def test_get_workflow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create workflow first
        create_response = await client.post(
            "/api/workflows",
            json={
                "initial_prompt": "Test prompt",
                "reviewers": [
                    {"provider": "claude", "prompt": "Review this code"},
                ],
            },
        )
        assert create_response.status_code == 201
        workflow_id = create_response.json()["id"]

        # Get workflow
        get_response = await client.get(f"/api/workflows/{workflow_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == workflow_id
        assert data["status"] == "running"
        assert len(data["reviews"]) == 1


@pytest.mark.asyncio
async def test_get_nonexistent_workflow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/workflows/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
