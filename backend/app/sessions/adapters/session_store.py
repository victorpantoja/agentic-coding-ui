from __future__ import annotations

from app.mcp.models import AgentInstruction
from app.sessions.models import SessionRecord, SessionStatus

_STEP_STATUS: dict[str, SessionStatus] = {
    "plan": SessionStatus.active,
    "test": SessionStatus.testing,
    "implement": SessionStatus.implementing,
    "review": SessionStatus.reviewing,
}


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}

    def create(self, session_id: str, request: str) -> SessionRecord:
        record = SessionRecord(session_id=session_id, request=request)
        self._sessions[session_id] = record
        return record

    def get(self, session_id: str) -> SessionRecord | None:
        return self._sessions.get(session_id)

    def list_all(self) -> list[SessionRecord]:
        return list(self._sessions.values())

    def append_instruction(
        self, session_id: str, instruction: AgentInstruction
    ) -> SessionRecord:
        record = self._sessions[session_id]
        record.instructions.append(instruction)
        record.status = _STEP_STATUS.get(instruction.step, record.status)
        return record

    def set_status(self, session_id: str, status: SessionStatus) -> SessionRecord:
        record = self._sessions[session_id]
        record.status = status
        return record

    def delete(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False


session_store = SessionStore()
