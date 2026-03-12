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


class ContextEvent(BaseModel):
    id: str
    event_type: str
    data: dict[str, Any]
    summary: str
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
