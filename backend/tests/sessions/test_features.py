from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.sessions.exceptions import SessionNotFoundError
from app.sessions.features import GetSessionFeature, ListSessionsFeature

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

_CONTEXT_ROW = {
    "id": "c1",
    "event_type": "plan",
    "data": {"agent": "architect"},
    "summary": "session started",
    "created_at": NOW,
}


def _pool(fetchrow_return: object = None, fetch_return: list[object] | None = None) -> MagicMock:
    p = MagicMock()
    p.fetchrow = AsyncMock(return_value=fetchrow_return)
    p.fetch = AsyncMock(return_value=fetch_return or [])
    return p


# ── ListSessionsFeature ───────────────────────────────────────────────────────

async def test_list_sessions_empty() -> None:
    pool = _pool(fetchrow_return={"count": 0})
    result = await ListSessionsFeature(pool=pool).handle(ListSessionsFeature.Command())
    assert result.sessions == []
    assert result.total == 0


async def test_list_sessions_with_data() -> None:
    pool = _pool(
        fetchrow_return={"count": 1},
        fetch_return=[
            {"id": "s1", "request": "r", "status": "active", "created_at": NOW, "updated_at": NOW}
        ],
    )
    result = await ListSessionsFeature(pool=pool).handle(ListSessionsFeature.Command())
    assert len(result.sessions) == 1
    assert result.sessions[0].id == "s1"
    assert result.total == 1


async def test_list_sessions_passes_filters() -> None:
    pool = _pool(fetchrow_return={"count": 0})
    cmd = ListSessionsFeature.Command(
        search="foo", date_from="2026-01-01", date_to="2026-12-31", page=2, page_size=5
    )
    with patch("app.sessions.features.queries.list_sessions", new=AsyncMock(return_value=([], 0))) as m:
        await ListSessionsFeature(pool=pool).handle(cmd)
        m.assert_awaited_once_with(
            pool, search="foo", date_from="2026-01-01", date_to="2026-12-31", page=2, page_size=5
        )


# ── GetSessionFeature ─────────────────────────────────────────────────────────

async def test_get_session_found() -> None:
    pool = _pool(fetchrow_return=_SESSION_ROW, fetch_return=[_CONTEXT_ROW])
    result = await GetSessionFeature(pool=pool).handle(GetSessionFeature.Command(session_id="s1"))
    assert result.session.id == "s1"
    assert len(result.session.context) == 1
    assert result.session.context[0].event_type == "plan"


async def test_get_session_not_found() -> None:
    pool = _pool(fetchrow_return=None)
    with pytest.raises(SessionNotFoundError):
        await GetSessionFeature(pool=pool).handle(GetSessionFeature.Command(session_id="missing"))


async def test_get_session_no_context() -> None:
    pool = _pool(fetchrow_return=_SESSION_ROW, fetch_return=[])
    result = await GetSessionFeature(pool=pool).handle(GetSessionFeature.Command(session_id="s1"))
    assert result.session.context == []
