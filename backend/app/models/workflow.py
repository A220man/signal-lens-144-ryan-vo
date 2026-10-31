from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4


class Provider(str, Enum):
    CLAUDE = "claude"
    CODEX = "codex"


class ReviewStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"


class Reviewer(BaseModel):
    provider: Provider
    prompt: str


class Review(BaseModel):
    reviewer: Reviewer
    status: ReviewStatus = ReviewStatus.PENDING
    output: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowCreate(BaseModel):
    reviewers: list[Reviewer] = Field(min_length=1)
    initial_prompt: str


class WorkflowRun(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: WorkflowStatus = WorkflowStatus.RUNNING
    initial_prompt: str
    reviews: list[Review] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class WorkflowRunResponse(BaseModel):
    id: UUID
    status: WorkflowStatus
    initial_prompt: str
    reviews: list[Review]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
