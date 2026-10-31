from fastapi import APIRouter, HTTPException
from uuid import UUID

from app.models.workflow import WorkflowCreate, WorkflowRunResponse
from app.services.workflow import create_workflow, get_workflow


router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("", response_model=WorkflowRunResponse, status_code=201)
async def create_workflow_endpoint(data: WorkflowCreate):
    """Create a workflow run with provider-qualified reviewers."""
    workflow = await create_workflow(data)
    return WorkflowRunResponse.model_validate(workflow.model_dump())


@router.get("/{workflow_id}", response_model=WorkflowRunResponse)
async def get_workflow_endpoint(workflow_id: UUID):
    """Get workflow status and collected reviews."""
    workflow = await get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowRunResponse.model_validate(workflow.model_dump())
