import asyncio
from unittest.mock import patch, MagicMock
import pytest
from httpx import AsyncClient, ASGITransport
from uuid import UUID
from app.main import app
from app.models.workflow import WorkflowRun, Reviewer, Provider, Review, ReviewStatus, WorkflowStatus
from app.services.workflow import execute_workflow, workflow_store_instance


@pytest.mark.asyncio
async def test_execute_workflow_success():
    """Test workflow execution with successful reviews."""
    workflow = WorkflowRun(
        initial_prompt="Test prompt",
        reviews=[
            Review(reviewer=Reviewer(provider=Provider.CLAUDE, prompt="Review this")),
            Review(reviewer=Reviewer(provider=Provider.CODEX, prompt="Analyze this")),
        ],
    )
    workflow_store_instance.create(workflow)

    with patch("app.services.workflow.subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Review completed successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        await execute_workflow(workflow)

        assert workflow.status == WorkflowStatus.COMPLETED
        assert len(workflow.reviews) == 2
        for review in workflow.reviews:
            assert review.status == ReviewStatus.COMPLETED
            assert review.output == "Review completed successfully"
            assert review.error is None
            assert review.started_at is not None
            assert review.completed_at is not None

        assert mock_run.call_count == 2
        calls = mock_run.call_args_list
        assert calls[0][0][0] == ["claude", "-p", "Review this"]
        assert calls[1][0][0] == ["codex", "exec", "Analyze this"]


@pytest.mark.asyncio
async def test_execute_workflow_failure():
    """Test workflow execution with one failed review."""
    workflow = WorkflowRun(
        initial_prompt="Test prompt",
        reviews=[
            Review(reviewer=Reviewer(provider=Provider.CLAUDE, prompt="Review this")),
            Review(reviewer=Reviewer(provider=Provider.CODEX, prompt="Analyze this")),
        ],
    )
    workflow_store_instance.create(workflow)

    with patch("app.services.workflow.subprocess.run") as mock_run:
        success_result = MagicMock()
        success_result.returncode = 0
        success_result.stdout = "Success"
        success_result.stderr = ""

        fail_result = MagicMock()
        fail_result.returncode = 1
        fail_result.stdout = ""
        fail_result.stderr = "Error occurred"

        mock_run.side_effect = [success_result, fail_result]

        await execute_workflow(workflow)

        assert workflow.status == WorkflowStatus.INCOMPLETE
        assert len(workflow.reviews) == 2

        assert workflow.reviews[0].status == ReviewStatus.COMPLETED
        assert workflow.reviews[0].output == "Success"

        assert workflow.reviews[1].status == ReviewStatus.FAILED
        assert workflow.reviews[1].error == "Error occurred"


@pytest.mark.asyncio
async def test_execute_workflow_timeout():
    """Test workflow execution with timeout."""
    workflow = WorkflowRun(
        initial_prompt="Test prompt",
        reviews=[
            Review(reviewer=Reviewer(provider=Provider.CLAUDE, prompt="Review this")),
        ],
    )
    workflow_store_instance.create(workflow)

    with patch("app.services.workflow.subprocess.run") as mock_run:
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude -p Review this", timeout=120)

        await execute_workflow(workflow)

        assert workflow.status == WorkflowStatus.INCOMPLETE
        assert workflow.reviews[0].status == ReviewStatus.FAILED
        assert "timed out" in workflow.reviews[0].error.lower()


@pytest.mark.asyncio
async def test_execute_workflow_cli_not_found():
    """Test workflow execution when CLI is not found."""
    workflow = WorkflowRun(
        initial_prompt="Test prompt",
        reviews=[
            Review(reviewer=Reviewer(provider=Provider.CLAUDE, prompt="Review this")),
        ],
    )
    workflow_store_instance.create(workflow)

    with patch("app.services.workflow.subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError("claude not found")

        await execute_workflow(workflow)

        assert workflow.status == WorkflowStatus.INCOMPLETE
        assert workflow.reviews[0].status == ReviewStatus.FAILED
        assert "not found" in workflow.reviews[0].error.lower()


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
