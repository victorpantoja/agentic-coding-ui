from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class SessionSummary(BaseModel):
    id: str
    request: str
    status: str
    created_at: datetime
    updated_at: datetime


class SessionStep(BaseModel):
    id: str
    step_name: str
    status: str
    scheduled_at: datetime
    started_at: datetime | None = None
    ended_at: datetime | None = None
    error_details: str | None = None


class ContextEvent(BaseModel):
    id: str
    event_type: str
    data: dict[str, Any]
    summary: str
    agent: str | None = None
    duration_ms: int | None = None
    created_at: datetime


class TaskHistoryEntry(BaseModel):
    iteration: int
    reviewer_critique: str
    diff: str
    lint_output: dict[str, Any]
    arch_output: dict[str, Any]
    is_approved: bool
    lessons_learned: str
    created_at: datetime


class SessionDetail(BaseModel):
    id: str
    request: str
    status: str
    plan: dict[str, Any] | None = None
    test_spec: dict[str, Any] | None = None
    implementation: dict[str, Any] | None = None
    review: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
    context: list[ContextEvent] = []
    steps: list[SessionStep] = []
    task_history: list[TaskHistoryEntry] = []
