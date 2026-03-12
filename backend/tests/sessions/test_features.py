from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.mcp.client import SovereignBrainClient
from app.mcp.exceptions import MCPClientError
from app.mcp.models import AgentInstruction
from app.sessions.adapters.session_store import SessionStore
from app.sessions.exceptions import SessionNotFoundError
from app.sessions.features import (
    AbandonSessionFeature,
    FetchContextFeature,
    GetSessionFeature,
    GetTestSpecFeature,
    ImplementLogicFeature,
    ListSessionsFeature,
    RunReviewFeature,
    StartSessionFeature,
)
from app.ws.manager import ConnectionManager

INST = AgentInstruction(
    agent="architect",
    system_prompt="s",
    user_message="m",
    action_required="a",
    session_id="test-session-1",
    step="plan",
    context={},
)


@pytest.fixture
def store() -> SessionStore:
    return SessionStore()


@pytest.fixture
def manager() -> ConnectionManager:
    return ConnectionManager()


@pytest.fixture
def mock_mcp() -> SovereignBrainClient:
    client = SovereignBrainClient("http://test/sse")
    client.start_session = AsyncMock(return_value=INST)  # type: ignore[method-assign]
    client.get_test_spec = AsyncMock(return_value=INST)  # type: ignore[method-assign]
    client.implement_logic = AsyncMock(return_value=INST)  # type: ignore[method-assign]
    client.run_review = AsyncMock(return_value=INST)  # type: ignore[method-assign]
    client.fetch_context = AsyncMock(return_value=INST)  # type: ignore[method-assign]
    return client


# ── ListSessions ──────────────────────────────────────────────────────────────

async def test_list_sessions_empty(store: SessionStore) -> None:
    result = await ListSessionsFeature(store=store).handle(ListSessionsFeature.Command())
    assert result.sessions == []


async def test_list_sessions_with_data(store: SessionStore) -> None:
    store.create("s1", "req")
    result = await ListSessionsFeature(store=store).handle(ListSessionsFeature.Command())
    assert len(result.sessions) == 1


# ── GetSession ────────────────────────────────────────────────────────────────

async def test_get_session_found(store: SessionStore) -> None:
    store.create("s1", "req")
    result = await GetSessionFeature(store=store).handle(GetSessionFeature.Command(session_id="s1"))
    assert result.session.session_id == "s1"


async def test_get_session_not_found(store: SessionStore) -> None:
    with pytest.raises(SessionNotFoundError):
        await GetSessionFeature(store=store).handle(GetSessionFeature.Command(session_id="nope"))


# ── StartSession ──────────────────────────────────────────────────────────────

async def test_start_session(
    store: SessionStore, manager: ConnectionManager, mock_mcp: SovereignBrainClient
) -> None:
    result = await StartSessionFeature(store=store, client=mock_mcp, manager=manager).handle(
        StartSessionFeature.Command(request="build a service")
    )
    assert result.session.session_id == "test-session-1"
    assert result.instruction.agent == "architect"
    assert len(result.session.instructions) == 1


# ── GetTestSpec ───────────────────────────────────────────────────────────────

async def test_get_test_spec(
    store: SessionStore, manager: ConnectionManager, mock_mcp: SovereignBrainClient
) -> None:
    store.create("test-session-1", "req")
    result = await GetTestSpecFeature(store=store, client=mock_mcp, manager=manager).handle(
        GetTestSpecFeature.Command(session_id="test-session-1", plan="architecture plan")
    )
    assert result.instruction.agent == "architect"


async def test_get_test_spec_session_not_found(
    store: SessionStore, manager: ConnectionManager, mock_mcp: SovereignBrainClient
) -> None:
    with pytest.raises(SessionNotFoundError):
        await GetTestSpecFeature(store=store, client=mock_mcp, manager=manager).handle(
            GetTestSpecFeature.Command(session_id="missing", plan="plan")
        )


# ── ImplementLogic ────────────────────────────────────────────────────────────

async def test_implement_logic(
    store: SessionStore, manager: ConnectionManager, mock_mcp: SovereignBrainClient
) -> None:
    store.create("test-session-1", "req")
    result = await ImplementLogicFeature(store=store, client=mock_mcp, manager=manager).handle(
        ImplementLogicFeature.Command(
            session_id="test-session-1",
            test_code="def test_x(): pass",
            test_file_path="tests/test_x.py",
        )
    )
    assert result.instruction is not None


async def test_implement_logic_session_not_found(
    store: SessionStore, manager: ConnectionManager, mock_mcp: SovereignBrainClient
) -> None:
    with pytest.raises(SessionNotFoundError):
        await ImplementLogicFeature(store=store, client=mock_mcp, manager=manager).handle(
            ImplementLogicFeature.Command(
                session_id="missing", test_code="c", test_file_path="p.py"
            )
        )


# ── RunReview ─────────────────────────────────────────────────────────────────

async def test_run_review(
    store: SessionStore, manager: ConnectionManager, mock_mcp: SovereignBrainClient
) -> None:
    store.create("test-session-1", "req")
    result = await RunReviewFeature(store=store, client=mock_mcp, manager=manager).handle(
        RunReviewFeature.Command(session_id="test-session-1", diff="--- a\n+++ b")
    )
    assert result.instruction is not None


async def test_run_review_session_not_found(
    store: SessionStore, manager: ConnectionManager, mock_mcp: SovereignBrainClient
) -> None:
    with pytest.raises(SessionNotFoundError):
        await RunReviewFeature(store=store, client=mock_mcp, manager=manager).handle(
            RunReviewFeature.Command(session_id="missing", diff="d")
        )


# ── FetchContext ──────────────────────────────────────────────────────────────

async def test_fetch_context(
    store: SessionStore, mock_mcp: SovereignBrainClient
) -> None:
    store.create("test-session-1", "req")
    result = await FetchContextFeature(store=store, client=mock_mcp).handle(
        FetchContextFeature.Command(session_id="test-session-1", query="find patterns")
    )
    assert result.instruction.agent == "architect"


async def test_fetch_context_session_not_found(
    store: SessionStore, mock_mcp: SovereignBrainClient
) -> None:
    with pytest.raises(SessionNotFoundError):
        await FetchContextFeature(store=store, client=mock_mcp).handle(
            FetchContextFeature.Command(session_id="missing", query="q")
        )


# ── AbandonSession ────────────────────────────────────────────────────────────

async def test_abandon_session(
    store: SessionStore, manager: ConnectionManager
) -> None:
    store.create("s1", "req")
    result = await AbandonSessionFeature(store=store, manager=manager).handle(
        AbandonSessionFeature.Command(session_id="s1")
    )
    assert result.status == "abandoned"


async def test_abandon_session_not_found(
    store: SessionStore, manager: ConnectionManager
) -> None:
    with pytest.raises(SessionNotFoundError):
        await AbandonSessionFeature(store=store, manager=manager).handle(
            AbandonSessionFeature.Command(session_id="missing")
        )
