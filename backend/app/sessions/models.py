from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.mcp.models import AgentInstruction


class SessionStatus(str, Enum):
    active = "active"
    testing = "testing"
    implementing = "implementing"
    reviewing = "reviewing"
    approved = "approved"
    rejected = "rejected"
    abandoned = "abandoned"


class SessionRecord(BaseModel):
    session_id: str
    request: str
    status: SessionStatus = SessionStatus.active
    instructions: list[AgentInstruction] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StartSessionRequest(BaseModel):
    request: str
    project_context: str | None = None
    review_feedback: str | None = None


class GetTestSpecRequest(BaseModel):
    plan: str
    scenario: str | None = None
    existing_code: str | None = None
    project_context: str | None = None


class ImplementRequest(BaseModel):
    test_code: str
    test_file_path: str
    error_output: str | None = None
    existing_code: str | None = None


class ReviewRequest(BaseModel):
    diff: str
    changed_files: list[str] | None = None
    plan: str | None = None
    project_context: str | None = None


class FetchContextRequest(BaseModel):
    query: str
    limit: int = 10


class WsEvent(BaseModel):
    type: str
    payload: dict[str, Any]
