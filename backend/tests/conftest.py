from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.mcp.client import SovereignBrainClient
from app.mcp.models import AgentInstruction
from app.sessions.adapters.session_store import SessionStore
from app.ws.manager import ConnectionManager

MOCK_INSTRUCTION = AgentInstruction(
    agent="architect",
    system_prompt="You are an architect.",
    user_message="Build a user service.",
    action_required="Produce a plan.",
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
    client.start_session = AsyncMock(return_value=MOCK_INSTRUCTION)  # type: ignore[method-assign]
    client.get_test_spec = AsyncMock(return_value=MOCK_INSTRUCTION)  # type: ignore[method-assign]
    client.implement_logic = AsyncMock(return_value=MOCK_INSTRUCTION)  # type: ignore[method-assign]
    client.run_review = AsyncMock(return_value=MOCK_INSTRUCTION)  # type: ignore[method-assign]
    client.fetch_context = AsyncMock(return_value=MOCK_INSTRUCTION)  # type: ignore[method-assign]
    return client


@pytest.fixture
def test_client(
    store: SessionStore,
    manager: ConnectionManager,
    mock_mcp: SovereignBrainClient,
) -> TestClient:
    from app.app import create_app
    from app.sessions.routes import get_mcp_client, get_store, get_ws_manager

    app = create_app()
    app.dependency_overrides[get_store] = lambda: store
    app.dependency_overrides[get_ws_manager] = lambda: manager
    app.dependency_overrides[get_mcp_client] = lambda: mock_mcp
    return TestClient(app)
