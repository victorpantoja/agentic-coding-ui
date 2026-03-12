from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.db import queries

NOW = datetime.now(timezone.utc)


def _pool(fetchrow_return: object = None, fetch_return: list[object] | None = None) -> MagicMock:
    p = MagicMock()
    p.fetchrow = AsyncMock(return_value=fetchrow_return)
    p.fetch = AsyncMock(return_value=fetch_return or [])
    return p


# ── list_sessions ─────────────────────────────────────────────────────────────

async def test_list_sessions_empty() -> None:
    pool = _pool(fetchrow_return={"count": 0}, fetch_return=[])
    rows, total = await queries.list_sessions(pool)
    assert rows == []
    assert total == 0


async def test_list_sessions_returns_rows() -> None:
    row = {"id": "abc", "request": "r", "status": "active", "created_at": NOW, "updated_at": NOW}
    pool = _pool(fetchrow_return={"count": 1}, fetch_return=[row])
    rows, total = await queries.list_sessions(pool)
    assert total == 1
    assert rows[0]["id"] == "abc"


async def test_list_sessions_with_search() -> None:
    pool = _pool(fetchrow_return={"count": 0}, fetch_return=[])
    await queries.list_sessions(pool, search="foo")
    call_args = pool.fetchrow.call_args[0]
    assert "ILIKE" in call_args[0]


async def test_list_sessions_with_date_from() -> None:
    pool = _pool(fetchrow_return={"count": 0}, fetch_return=[])
    await queries.list_sessions(pool, date_from="2026-01-01")
    call_args = pool.fetchrow.call_args[0]
    assert "updated_at >=" in call_args[0]


async def test_list_sessions_with_date_to() -> None:
    pool = _pool(fetchrow_return={"count": 0}, fetch_return=[])
    await queries.list_sessions(pool, date_to="2026-12-31")
    call_args = pool.fetchrow.call_args[0]
    assert "updated_at <" in call_args[0]


async def test_list_sessions_all_filters() -> None:
    pool = _pool(fetchrow_return={"count": 0}, fetch_return=[])
    await queries.list_sessions(pool, search="x", date_from="2026-01-01", date_to="2026-12-31")
    call_args = pool.fetchrow.call_args[0]
    assert "ILIKE" in call_args[0]
    assert "updated_at >=" in call_args[0]
    assert "updated_at <" in call_args[0]


async def test_list_sessions_pagination() -> None:
    pool = _pool(fetchrow_return={"count": 25}, fetch_return=[])
    await queries.list_sessions(pool, page=2, page_size=10)
    fetch_args = pool.fetch.call_args[0]
    assert "LIMIT" in fetch_args[0]
    assert "OFFSET" in fetch_args[0]
    assert 10 in fetch_args[1:]
    assert 10 in fetch_args[1:]  # offset = (2-1)*10 = 10


# ── get_session ───────────────────────────────────────────────────────────────

async def test_get_session_found() -> None:
    row = {
        "id": "sid", "request": "r", "status": "active",
        "plan": None, "test_spec": None, "implementation": None, "review": None,
        "created_at": NOW, "updated_at": NOW,
    }
    pool = _pool(fetchrow_return=row)
    result = await queries.get_session(pool, "sid")
    assert result is not None
    assert result["id"] == "sid"


async def test_get_session_jsonb_as_string() -> None:
    row = {
        "id": "sid", "request": "r", "status": "active",
        "plan": '{"step": 1}', "test_spec": None, "implementation": None, "review": None,
        "created_at": NOW, "updated_at": NOW,
    }
    pool = _pool(fetchrow_return=row)
    result = await queries.get_session(pool, "sid")
    assert result is not None
    assert result["plan"] == {"step": 1}


async def test_get_session_not_found() -> None:
    pool = _pool(fetchrow_return=None)
    result = await queries.get_session(pool, "missing")
    assert result is None


# ── get_context_history ───────────────────────────────────────────────────────

async def test_get_context_history_empty() -> None:
    pool = _pool(fetch_return=[])
    result = await queries.get_context_history(pool, "sid")
    assert result == []


async def test_get_context_history_with_events() -> None:
    event = {"id": "eid", "event_type": "plan", "data": {}, "summary": "s", "created_at": NOW}
    pool = _pool(fetch_return=[event])
    result = await queries.get_context_history(pool, "sid")
    assert len(result) == 1
    assert result[0]["event_type"] == "plan"


async def test_get_context_history_jsonb_as_string() -> None:
    event = {"id": "eid", "event_type": "plan", "data": '{"agent": "architect"}', "summary": "s", "created_at": NOW}
    pool = _pool(fetch_return=[event])
    result = await queries.get_context_history(pool, "sid")
    assert result[0]["data"] == {"agent": "architect"}


# ── get_session_steps ─────────────────────────────────────────────────────────

async def test_get_session_steps_empty() -> None:
    pool = _pool(fetch_return=[])
    result = await queries.get_session_steps(pool, "sid")
    assert result == []


async def test_get_session_steps_returns_rows() -> None:
    step = {
        "id": "st1", "step_name": "plan", "status": "pending",
        "scheduled_at": NOW, "started_at": None, "ended_at": None, "error_details": None,
    }
    pool = _pool(fetch_return=[step])
    result = await queries.get_session_steps(pool, "sid")
    assert len(result) == 1
    assert result[0]["step_name"] == "plan"
    assert result[0]["status"] == "pending"
