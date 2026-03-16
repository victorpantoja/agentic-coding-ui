from __future__ import annotations

from dataclasses import dataclass

import asyncpg

from app.common.features import BaseFeature
from app.db import queries
from app.sessions.exceptions import SessionNotFoundError
from app.sessions.models import (
    ContextEvent,
    SessionDetail,
    SessionStep,
    SessionSummary,
    TaskHistoryEntry,
)


class ListSessionsFeature(BaseFeature):
    @dataclass
    class Command:
        search: str = ""
        date_from: str = ""
        date_to: str = ""
        page: int = 1
        page_size: int = 20

    @dataclass
    class Result:
        sessions: list[SessionSummary]
        total: int

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def handle(self, command: Command) -> Result:
        rows, total = await queries.list_sessions(
            self._pool,
            search=command.search,
            date_from=command.date_from,
            date_to=command.date_to,
            page=command.page,
            page_size=command.page_size,
        )
        sessions = [SessionSummary(**row) for row in rows]
        return self.Result(sessions=sessions, total=total)


class GetSessionFeature(BaseFeature):
    @dataclass
    class Command:
        session_id: str

    @dataclass
    class Result:
        session: SessionDetail

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def handle(self, command: Command) -> Result:
        row = await queries.get_session(self._pool, command.session_id)
        if row is None:
            raise SessionNotFoundError(command.session_id)
        context_rows = await queries.get_context_history(self._pool, command.session_id)
        step_rows = await queries.get_session_steps(self._pool, command.session_id)
        history_rows = await queries.get_task_history(self._pool, command.session_id)
        context = [ContextEvent(**r) for r in context_rows]
        steps = [SessionStep(**r) for r in step_rows]
        task_history = [TaskHistoryEntry(**r) for r in history_rows]
        session = SessionDetail(
            **{**row, "context": context, "steps": steps, "task_history": task_history}
        )
        return self.Result(session=session)
