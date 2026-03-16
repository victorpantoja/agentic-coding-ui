from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient

NOW = datetime.now(timezone.utc)

_SESSION_ROW = {
    "id": "s1",
    "request": "build something",
    "status": "active",
    "plan": None,
    "test_spec": None,
    "implementation": None,
    "review": None,
    "created_at": NOW,
    "updated_at": NOW,
}

_EVENT = {
    "id": "e1", "event_type": "plan", "data": {"key": "val"}, "summary": "started",
    "agent": None, "duration_ms": None, "created_at": NOW,
}
_EVENT2 = {
    "id": "e2", "event_type": "test", "data": {}, "summary": "tests written",
    "agent": "orchestrator", "duration_ms": 100, "created_at": NOW,
}

_STEP = {
    "id": "st1", "step_name": "plan", "status": "pending",
    "scheduled_at": NOW, "started_at": None, "ended_at": None, "error_details": None,
}
_STEP_RUNNING = {**_STEP, "status": "running"}

_HISTORY = {
    "iteration": 1,
    "reviewer_critique": "fix it",
    "diff": "",
    "lint_output": {"passed": False},
    "arch_output": {"passed": True},
    "is_approved": False,
    "lessons_learned": "fix lint",
    "created_at": NOW,
}


def _make_sleep_wsd_on(n: int):
    """Return an async sleep mock that raises WebSocketDisconnect on the nth call."""
    call_count = 0

    async def mock_sleep(_: float) -> None:
        nonlocal call_count
        call_count += 1
        if call_count >= n:
            raise WebSocketDisconnect()

    return mock_sleep


def test_ws_not_found(mock_pool: MagicMock, test_client: TestClient) -> None:
    mock_pool.fetchrow = AsyncMock(return_value=None)
    with test_client.websocket_connect("/ws/missing") as ws:
        msg = ws.receive_json()
    assert msg["type"] == "error"
    assert "not found" in msg["data"]["detail"].lower()


def test_ws_initial_state(
    mock_pool: MagicMock, test_client: TestClient, mocker: object
) -> None:
    # fetch order: context, steps, task_history
    mock_pool.fetchrow = AsyncMock(return_value=_SESSION_ROW)
    mock_pool.fetch = AsyncMock(side_effect=[[_EVENT], [_STEP], []])
    mocker.patch("asyncio.sleep", side_effect=_make_sleep_wsd_on(1))  # type: ignore[attr-defined]

    with test_client.websocket_connect("/ws/s1") as ws:
        msg = ws.receive_json()

    assert msg["type"] == "session"
    assert msg["data"]["id"] == "s1"
    assert len(msg["data"]["context"]) == 1
    assert len(msg["data"]["steps"]) == 1
    assert msg["data"]["task_history"] == []
    assert isinstance(msg["data"]["created_at"], str)


def test_ws_poll_no_changes(
    mock_pool: MagicMock, test_client: TestClient, mocker: object
) -> None:
    # fetch order: init_ctx, init_steps, init_history, poll_ctx, poll_steps, poll_hist
    mock_pool.fetchrow = AsyncMock(side_effect=[_SESSION_ROW, _SESSION_ROW])
    init = [[_EVENT], [_STEP], []]
    poll = [[_EVENT], [_STEP], []]
    mock_pool.fetch = AsyncMock(side_effect=init + poll)
    mocker.patch("asyncio.sleep", side_effect=_make_sleep_wsd_on(2))  # type: ignore[attr-defined]

    messages = []
    with test_client.websocket_connect("/ws/s1") as ws:
        messages.append(ws.receive_json())  # "session"

    assert messages[0]["type"] == "session"
    assert len(messages) == 1


def test_ws_new_context_event(
    mock_pool: MagicMock, test_client: TestClient, mocker: object
) -> None:
    mock_pool.fetchrow = AsyncMock(side_effect=[_SESSION_ROW, _SESSION_ROW])
    init = [[_EVENT], [_STEP], []]
    poll = [[_EVENT, _EVENT2], [_STEP], []]
    mock_pool.fetch = AsyncMock(side_effect=init + poll)
    mocker.patch("asyncio.sleep", side_effect=_make_sleep_wsd_on(2))  # type: ignore[attr-defined]

    messages = []
    with test_client.websocket_connect("/ws/s1") as ws:
        messages.append(ws.receive_json())  # "session"
        messages.append(ws.receive_json())  # "context_event"

    assert messages[0]["type"] == "session"
    assert messages[1]["type"] == "context_event"
    assert messages[1]["data"]["id"] == "e2"


def test_ws_step_status_change(
    mock_pool: MagicMock, test_client: TestClient, mocker: object
) -> None:
    mock_pool.fetchrow = AsyncMock(side_effect=[_SESSION_ROW, _SESSION_ROW])
    init = [[_EVENT], [_STEP], []]
    poll = [[_EVENT], [_STEP_RUNNING], []]
    mock_pool.fetch = AsyncMock(side_effect=init + poll)
    mocker.patch("asyncio.sleep", side_effect=_make_sleep_wsd_on(2))  # type: ignore[attr-defined]

    messages = []
    with test_client.websocket_connect("/ws/s1") as ws:
        messages.append(ws.receive_json())  # "session"
        messages.append(ws.receive_json())  # "steps"

    assert messages[0]["type"] == "session"
    assert messages[1]["type"] == "steps"
    assert messages[1]["data"][0]["status"] == "running"


def test_ws_status_change(
    mock_pool: MagicMock, test_client: TestClient, mocker: object
) -> None:
    approved = {**_SESSION_ROW, "status": "approved"}
    mock_pool.fetchrow = AsyncMock(side_effect=[_SESSION_ROW, approved])
    init = [[_EVENT], [_STEP], []]
    poll = [[_EVENT], [_STEP], []]
    mock_pool.fetch = AsyncMock(side_effect=init + poll)
    mocker.patch("asyncio.sleep", side_effect=_make_sleep_wsd_on(2))  # type: ignore[attr-defined]

    messages = []
    with test_client.websocket_connect("/ws/s1") as ws:
        messages.append(ws.receive_json())  # "session"
        messages.append(ws.receive_json())  # "status"

    assert messages[0]["type"] == "session"
    assert messages[1]["type"] == "status"
    assert messages[1]["data"]["status"] == "approved"


def test_ws_task_history_update(
    mock_pool: MagicMock, test_client: TestClient, mocker: object
) -> None:
    mock_pool.fetchrow = AsyncMock(side_effect=[_SESSION_ROW, _SESSION_ROW])
    init = [[_EVENT], [_STEP], []]
    poll = [[_EVENT], [_STEP], [_HISTORY]]
    mock_pool.fetch = AsyncMock(side_effect=init + poll)
    mocker.patch("asyncio.sleep", side_effect=_make_sleep_wsd_on(2))  # type: ignore[attr-defined]

    messages = []
    with test_client.websocket_connect("/ws/s1") as ws:
        messages.append(ws.receive_json())  # "session"
        messages.append(ws.receive_json())  # "task_history"

    assert messages[0]["type"] == "session"
    assert messages[1]["type"] == "task_history"
    assert messages[1]["data"][0]["iteration"] == 1
    assert messages[1]["data"][0]["is_approved"] is False
