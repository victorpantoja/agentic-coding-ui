from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession
from mcp.client.sse import sse_client

from app.mcp.exceptions import MCPClientError
from app.mcp.models import AgentInstruction


class SovereignBrainClient:
    def __init__(self, url: str) -> None:
        self.url = url

    @asynccontextmanager
    async def _session(self) -> AsyncIterator[ClientSession]:
        async with sse_client(self.url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session

    async def _call_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> AgentInstruction:
        async with self._session() as session:
            result = await session.call_tool(tool_name, arguments)
            if not result.content:
                raise MCPClientError(f"Empty response from tool {tool_name}")
            raw = result.content[0].text  # type: ignore[union-attr]
            return AgentInstruction.model_validate(json.loads(raw))

    async def start_session(
        self,
        request: str,
        project_context: str | None = None,
        review_feedback: str | None = None,
    ) -> AgentInstruction:
        args: dict[str, Any] = {"request": request}
        if project_context is not None:
            args["project_context"] = project_context
        if review_feedback is not None:
            args["review_feedback"] = review_feedback
        return await self._call_tool("start_session", args)

    async def get_test_spec(
        self,
        plan: str,
        session_id: str,
        scenario: str | None = None,
        existing_code: str | None = None,
        project_context: str | None = None,
    ) -> AgentInstruction:
        args: dict[str, Any] = {"plan": plan, "session_id": session_id}
        if scenario is not None:
            args["scenario"] = scenario
        if existing_code is not None:
            args["existing_code"] = existing_code
        if project_context is not None:
            args["project_context"] = project_context
        return await self._call_tool("get_test_spec", args)

    async def implement_logic(
        self,
        test_code: str,
        test_file_path: str,
        session_id: str,
        error_output: str | None = None,
        existing_code: str | None = None,
    ) -> AgentInstruction:
        args: dict[str, Any] = {
            "test_code": test_code,
            "test_file_path": test_file_path,
            "session_id": session_id,
        }
        if error_output is not None:
            args["error_output"] = error_output
        if existing_code is not None:
            args["existing_code"] = existing_code
        return await self._call_tool("implement_logic", args)

    async def run_review(
        self,
        diff: str,
        session_id: str,
        changed_files: list[str] | None = None,
        plan: str | None = None,
        project_context: str | None = None,
    ) -> AgentInstruction:
        args: dict[str, Any] = {"diff": diff, "session_id": session_id}
        if changed_files is not None:
            args["changed_files"] = changed_files
        if plan is not None:
            args["plan"] = plan
        if project_context is not None:
            args["project_context"] = project_context
        return await self._call_tool("run_review", args)

    async def fetch_context(
        self,
        query: str,
        session_id: str | None = None,
        limit: int = 10,
    ) -> AgentInstruction:
        args: dict[str, Any] = {"query": query, "limit": limit}
        if session_id is not None:
            args["session_id"] = session_id
        return await self._call_tool("fetch_context", args)
