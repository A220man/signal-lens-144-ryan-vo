import asyncio
import subprocess
import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.models.workflow import (
    Provider,
    Review,
    ReviewStatus,
    Reviewer,
    WorkflowRun,
    WorkflowCreate,
    WorkflowStatus,
)


class InMemoryWorkflowStore:
    """In-memory workflow store for development."""

    def __init__(self):
        self._workflows: dict[UUID, WorkflowRun] = {}

    def create(self, workflow: WorkflowRun) -> WorkflowRun:
        self._workflows[workflow.id] = workflow
        return workflow

    def get(self, workflow_id: UUID) -> Optional[WorkflowRun]:
        return self._workflows.get(workflow_id)

    def update(self, workflow: WorkflowRun) -> WorkflowRun:
        self._workflows[workflow.id] = workflow
        return workflow


workflow_store_instance = InMemoryWorkflowStore()


async def execute_review(review: Review) -> Review:
    """Execute a single review using the appropriate provider CLI."""
    review.started_at = datetime.utcnow()
    review.status = ReviewStatus.COMPLETED

    provider = review.reviewer.provider
    prompt = review.reviewer.prompt

    try:
        if provider == Provider.CLAUDE:
            result = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=120,
            )
        elif provider == Provider.CODEX:
            result = subprocess.run(
                ["codex", "exec", prompt],
                capture_output=True,
                text=True,
                timeout=120,
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

        if result.returncode == 0:
            review.output = result.stdout.strip()
        else:
            review.status = ReviewStatus.FAILED
            review.error = result.stderr.strip() or f"Process exited with code {result.returncode}"
    except subprocess.TimeoutExpired:
        review.status = ReviewStatus.FAILED
        review.error = "Review timed out after 120 seconds"
    except FileNotFoundError:
        review.status = ReviewStatus.FAILED
        review.error = f"Provider CLI not found: {provider.value}"
    except Exception as e:
        review.status = ReviewStatus.FAILED
        review.error = str(e)

    review.completed_at = datetime.utcnow()
    return review


async def execute_workflow(workflow: WorkflowRun) -> None:
    """Execute all reviews for a workflow."""
    reviews = workflow.reviews

    # Run all reviews concurrently
    updated_reviews = await asyncio.gather(
        *[execute_review(review) for review in reviews],
        return_exceptions=True,
    )

    # Handle any exceptions from gather
    final_reviews = []
    for i, result in enumerate(updated_reviews):
        if isinstance(result, Exception):
            review = reviews[i]
            review.status = ReviewStatus.FAILED
            review.error = str(result)
            review.completed_at = datetime.utcnow()
            final_reviews.append(review)
        else:
            final_reviews.append(result)

    # Determine overall workflow status
    failed_reviews = [r for r in final_reviews if r.status == ReviewStatus.FAILED]
    if failed_reviews:
        workflow.status = WorkflowStatus.INCOMPLETE
    else:
        workflow.status = WorkflowStatus.COMPLETED

    workflow.reviews = final_reviews
    workflow.updated_at = datetime.utcnow()
    workflow.completed_at = datetime.utcnow()

    workflow_store_instance.update(workflow)


async def create_workflow(data: WorkflowCreate) -> WorkflowRun:
    """Create a new workflow run."""
    reviews = [
        Review(
            reviewer=reviewer,
            status=ReviewStatus.PENDING,
        )
        for reviewer in data.reviewers
    ]

    workflow = WorkflowRun(
        initial_prompt=data.initial_prompt,
        reviews=reviews,
    )
    workflow_store_instance.create(workflow)

    # Execute asynchronously
    asyncio.create_task(execute_workflow(workflow))

    return workflow


async def get_workflow(workflow_id: UUID) -> Optional[WorkflowRun]:
    """Get workflow by ID."""
    return workflow_store_instance.get(workflow_id)
