from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentInstruction(BaseModel):
    agent: str
    system_prompt: str
    user_message: str
    action_required: str
    session_id: str
    step: str
    context: dict[str, Any] = Field(default_factory=dict)
