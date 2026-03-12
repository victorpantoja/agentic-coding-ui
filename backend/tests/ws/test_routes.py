from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from app.sessions.adapters.session_store import SessionStore
from app.sessions.routes import get_store, get_ws_manager
from app.ws.manager import ConnectionManager
from app.ws.routes import session_ws


def _make_client(
    store: SessionStore, manager: ConnectionManager
) -> "TestClient":
    from fastapi.testclient import TestClient
    from app.app import create_app

    app = create_app()
    app.dependency_overrides[get_store] = lambda: store
    app.dependency_overrides[get_ws_manager] = lambda: manager
    return TestClient(app)


def test_ws_connect_existing_session() -> None:
    store = SessionStore()
    store.create("s1", "req")
    manager = ConnectionManager()
    client = _make_client(store, manager)
    with client.websocket_connect("/ws/s1") as ws:
        data = ws.receive_json()
        assert data["session_id"] == "s1"


def test_ws_connect_no_session() -> None:
    store = SessionStore()
    manager = ConnectionManager()
    client = _make_client(store, manager)
    with client.websocket_connect("/ws/nonexistent") as ws:
        ws.send_text("ping")


async def test_ws_websocket_disconnect_exception() -> None:
    store = SessionStore()
    manager = ConnectionManager()
    ws = MagicMock(spec=WebSocket)
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()
    ws.receive = AsyncMock(side_effect=WebSocketDisconnect(code=1000))
    await session_ws("s1", ws, store, manager)
    assert manager.active_count("s1") == 0
