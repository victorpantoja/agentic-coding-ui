from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ws.manager import ConnectionManager


@pytest.fixture
def manager() -> ConnectionManager:
    return ConnectionManager()


def _ws() -> MagicMock:
    ws = MagicMock()
    ws.send_text = AsyncMock()
    return ws


async def test_connect_and_count(manager: ConnectionManager) -> None:
    ws = _ws()
    manager.connect("s1", ws)
    assert manager.active_count("s1") == 1


async def test_disconnect(manager: ConnectionManager) -> None:
    ws = _ws()
    manager.connect("s1", ws)
    manager.disconnect("s1", ws)
    assert manager.active_count("s1") == 0


async def test_disconnect_nonexistent(manager: ConnectionManager) -> None:
    manager.disconnect("s1", _ws())
    assert manager.active_count("s1") == 0


async def test_broadcast_reaches_all(manager: ConnectionManager) -> None:
    ws1, ws2 = _ws(), _ws()
    manager.connect("s1", ws1)
    manager.connect("s1", ws2)
    await manager.broadcast("s1", {"type": "test"})
    ws1.send_text.assert_called_once()
    ws2.send_text.assert_called_once()


async def test_broadcast_no_connections(manager: ConnectionManager) -> None:
    await manager.broadcast("s1", {"type": "test"})


async def test_broadcast_removes_dead_connection(manager: ConnectionManager) -> None:
    ws = _ws()
    ws.send_text.side_effect = Exception("closed")
    manager.connect("s1", ws)
    await manager.broadcast("s1", {"type": "test"})
    assert manager.active_count("s1") == 0


async def test_active_count_unknown_session(manager: ConnectionManager) -> None:
    assert manager.active_count("nope") == 0
