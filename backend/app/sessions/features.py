from __future__ import annotations

from pydantic import BaseModel

from app.common.features import BaseFeature
from app.mcp.models import AgentInstruction
from app.sessions.exceptions import SessionNotFoundError
from app.sessions.models import SessionRecord, SessionStatus


class ListSessionsFeature(BaseFeature):
    class Command(BaseModel):
        pass

    class Result(BaseModel):
        sessions: list[SessionRecord]

    async def handle(self, command: Command) -> Result:
        return self.Result(sessions=self._store.list_all())


class GetSessionFeature(BaseFeature):
    class Command(BaseModel):
        session_id: str

    class Result(BaseModel):
        session: SessionRecord

    async def handle(self, command: Command) -> Result:
        session = self._store.get(command.session_id)
        if session is None:
            raise SessionNotFoundError(command.session_id)
        return self.Result(session=session)


class StartSessionFeature(BaseFeature):
    class Command(BaseModel):
        request: str
        project_context: str | None = None
        review_feedback: str | None = None

    class Result(BaseModel):
        session: SessionRecord
        instruction: AgentInstruction

    async def handle(self, command: Command) -> Result:
        assert self._client is not None
        assert self._manager is not None
        instruction = await self._client.start_session(
            request=command.request,
            project_context=command.project_context,
            review_feedback=command.review_feedback,
        )
        session = self._store.create(instruction.session_id, command.request)
        self._store.append_instruction(instruction.session_id, instruction)
        await self._manager.broadcast(
            instruction.session_id,
            {"type": "instruction", "payload": instruction.model_dump()},
        )
        return self.Result(session=session, instruction=instruction)


class GetTestSpecFeature(BaseFeature):
    class Command(BaseModel):
        session_id: str
        plan: str
        scenario: str | None = None
        existing_code: str | None = None
        project_context: str | None = None

    class Result(BaseModel):
        instruction: AgentInstruction

    async def handle(self, command: Command) -> Result:
        assert self._client is not None
        assert self._manager is not None
        if self._store.get(command.session_id) is None:
            raise SessionNotFoundError(command.session_id)
        instruction = await self._client.get_test_spec(
            plan=command.plan,
            session_id=command.session_id,
            scenario=command.scenario,
            existing_code=command.existing_code,
            project_context=command.project_context,
        )
        self._store.append_instruction(command.session_id, instruction)
        await self._manager.broadcast(
            command.session_id,
            {"type": "instruction", "payload": instruction.model_dump()},
        )
        return self.Result(instruction=instruction)


class ImplementLogicFeature(BaseFeature):
    class Command(BaseModel):
        session_id: str
        test_code: str
        test_file_path: str
        error_output: str | None = None
        existing_code: str | None = None

    class Result(BaseModel):
        instruction: AgentInstruction

    async def handle(self, command: Command) -> Result:
        assert self._client is not None
        assert self._manager is not None
        if self._store.get(command.session_id) is None:
            raise SessionNotFoundError(command.session_id)
        instruction = await self._client.implement_logic(
            test_code=command.test_code,
            test_file_path=command.test_file_path,
            session_id=command.session_id,
            error_output=command.error_output,
            existing_code=command.existing_code,
        )
        self._store.append_instruction(command.session_id, instruction)
        await self._manager.broadcast(
            command.session_id,
            {"type": "instruction", "payload": instruction.model_dump()},
        )
        return self.Result(instruction=instruction)


class RunReviewFeature(BaseFeature):
    class Command(BaseModel):
        session_id: str
        diff: str
        changed_files: list[str] | None = None
        plan: str | None = None
        project_context: str | None = None

    class Result(BaseModel):
        instruction: AgentInstruction

    async def handle(self, command: Command) -> Result:
        assert self._client is not None
        assert self._manager is not None
        if self._store.get(command.session_id) is None:
            raise SessionNotFoundError(command.session_id)
        instruction = await self._client.run_review(
            diff=command.diff,
            session_id=command.session_id,
            changed_files=command.changed_files,
            plan=command.plan,
            project_context=command.project_context,
        )
        self._store.append_instruction(command.session_id, instruction)
        await self._manager.broadcast(
            command.session_id,
            {"type": "instruction", "payload": instruction.model_dump()},
        )
        return self.Result(instruction=instruction)


class FetchContextFeature(BaseFeature):
    class Command(BaseModel):
        session_id: str
        query: str
        limit: int = 10

    class Result(BaseModel):
        instruction: AgentInstruction

    async def handle(self, command: Command) -> Result:
        assert self._client is not None
        if self._store.get(command.session_id) is None:
            raise SessionNotFoundError(command.session_id)
        instruction = await self._client.fetch_context(
            query=command.query,
            session_id=command.session_id,
            limit=command.limit,
        )
        return self.Result(instruction=instruction)


class AbandonSessionFeature(BaseFeature):
    class Command(BaseModel):
        session_id: str

    class Result(BaseModel):
        status: str = "abandoned"

    async def handle(self, command: Command) -> Result:
        assert self._manager is not None
        if self._store.get(command.session_id) is None:
            raise SessionNotFoundError(command.session_id)
        self._store.set_status(command.session_id, SessionStatus.abandoned)
        await self._manager.broadcast(
            command.session_id,
            {"type": "status", "payload": {"status": "abandoned"}},
        )
        return self.Result()
