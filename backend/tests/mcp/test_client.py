from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.mcp.client import SovereignBrainClient
from app.mcp.exceptions import MCPClientError
from app.mcp.models import AgentInstruction

MOCK_INSTRUCTION = AgentInstruction(
    agent="architect",
    system_prompt="sys",
    user_message="msg",
    action_required="act",
    session_id="s1",
    step="plan",
    context={},
)


def _make_session(text: str) -> MagicMock:
    content = MagicMock()
    content.text = text
    result = MagicMock()
    result.content = [content]
    session = MagicMock()
    session.initialize = AsyncMock()
    session.call_tool = AsyncMock(return_value=result)
    return session


@asynccontextmanager  # type: ignore[arg-type]
async def _mock_sse(*args: Any, **kwargs: Any):  # type: ignore[misc]
    yield AsyncMock(), AsyncMock()


def _session_cm(session: MagicMock) -> Any:
    @asynccontextmanager
    async def _cm(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        yield session

    return _cm


from unittest.mock import patch  # noqa: E402


@pytest.fixture
def client() -> SovereignBrainClient:
    return SovereignBrainClient("http://test/sse")


async def test_start_session(client: SovereignBrainClient) -> None:
    session = _make_session(MOCK_INSTRUCTION.model_dump_json())
    with (
        patch("app.mcp.client.sse_client", _mock_sse),
        patch("app.mcp.client.ClientSession", _session_cm(session)),
    ):
        result = await client.start_session("build")
    assert result.agent == "architect"
    session.call_tool.assert_called_once_with("start_session", {"request": "build"})


async def test_start_session_with_optionals(client: SovereignBrainClient) -> None:
    session = _make_session(MOCK_INSTRUCTION.model_dump_json())
    with (
        patch("app.mcp.client.sse_client", _mock_sse),
        patch("app.mcp.client.ClientSession", _session_cm(session)),
    ):
        await client.start_session("build", project_context="ctx", review_feedback="fb")
    args = session.call_tool.call_args[0][1]
    assert args["project_context"] == "ctx"
    assert args["review_feedback"] == "fb"


async def test_get_test_spec(client: SovereignBrainClient) -> None:
    session = _make_session(MOCK_INSTRUCTION.model_dump_json())
    with (
        patch("app.mcp.client.sse_client", _mock_sse),
        patch("app.mcp.client.ClientSession", _session_cm(session)),
    ):
        result = await client.get_test_spec("plan", "s1")
    assert result.session_id == "s1"


async def test_get_test_spec_with_optionals(client: SovereignBrainClient) -> None:
    session = _make_session(MOCK_INSTRUCTION.model_dump_json())
    with (
        patch("app.mcp.client.sse_client", _mock_sse),
        patch("app.mcp.client.ClientSession", _session_cm(session)),
    ):
        await client.get_test_spec(
            "plan", "s1", scenario="s", existing_code="c", project_context="p"
        )
    args = session.call_tool.call_args[0][1]
    assert "scenario" in args and "existing_code" in args and "project_context" in args


async def test_implement_logic(client: SovereignBrainClient) -> None:
    session = _make_session(MOCK_INSTRUCTION.model_dump_json())
    with (
        patch("app.mcp.client.sse_client", _mock_sse),
        patch("app.mcp.client.ClientSession", _session_cm(session)),
    ):
        result = await client.implement_logic("code", "tests/t.py", "s1")
    assert result.agent == "architect"


async def test_implement_logic_with_optionals(client: SovereignBrainClient) -> None:
    session = _make_session(MOCK_INSTRUCTION.model_dump_json())
    with (
        patch("app.mcp.client.sse_client", _mock_sse),
        patch("app.mcp.client.ClientSession", _session_cm(session)),
    ):
        await client.implement_logic("c", "p.py", "s1", error_output="err", existing_code="old")
    args = session.call_tool.call_args[0][1]
    assert "error_output" in args and "existing_code" in args


async def test_run_review(client: SovereignBrainClient) -> None:
    session = _make_session(MOCK_INSTRUCTION.model_dump_json())
    with (
        patch("app.mcp.client.sse_client", _mock_sse),
        patch("app.mcp.client.ClientSession", _session_cm(session)),
    ):
        result = await client.run_review("diff", "s1")
    assert result.step == "plan"


async def test_run_review_with_optionals(client: SovereignBrainClient) -> None:
    session = _make_session(MOCK_INSTRUCTION.model_dump_json())
    with (
        patch("app.mcp.client.sse_client", _mock_sse),
        patch("app.mcp.client.ClientSession", _session_cm(session)),
    ):
        await client.run_review("diff", "s1", changed_files=["a.py"], plan="p", project_context="ctx")
    args = session.call_tool.call_args[0][1]
    assert "changed_files" in args and "plan" in args and "project_context" in args


async def test_fetch_context(client: SovereignBrainClient) -> None:
    session = _make_session(MOCK_INSTRUCTION.model_dump_json())
    with (
        patch("app.mcp.client.sse_client", _mock_sse),
        patch("app.mcp.client.ClientSession", _session_cm(session)),
    ):
        result = await client.fetch_context("query", session_id="s1")
    assert result.agent == "architect"


async def test_fetch_context_no_session_id(client: SovereignBrainClient) -> None:
    session = _make_session(MOCK_INSTRUCTION.model_dump_json())
    with (
        patch("app.mcp.client.sse_client", _mock_sse),
        patch("app.mcp.client.ClientSession", _session_cm(session)),
    ):
        await client.fetch_context("query")
    args = session.call_tool.call_args[0][1]
    assert "session_id" not in args


async def test_empty_response_raises(client: SovereignBrainClient) -> None:
    result = MagicMock()
    result.content = []
    session = MagicMock()
    session.initialize = AsyncMock()
    session.call_tool = AsyncMock(return_value=result)
    with (
        patch("app.mcp.client.sse_client", _mock_sse),
        patch("app.mcp.client.ClientSession", _session_cm(session)),
        pytest.raises(MCPClientError),
    ):
        await client.start_session("req")
