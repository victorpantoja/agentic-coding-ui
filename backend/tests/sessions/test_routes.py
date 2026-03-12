from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.db.connection import get_pool

NOW = datetime.now(timezone.utc)

_SESSION_SUMMARY = {
    "id": "s1",
    "request": "build something",
    "status": "active",
    "created_at": NOW,
    "updated_at": NOW,
}

_SESSION_DETAIL = {
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


def test_default_get_pool() -> None:
    from app.sessions.routes import get_pool as _fn
    assert callable(_fn)


def test_list_sessions_empty(mock_pool: MagicMock, test_client: TestClient) -> None:
    mock_pool.fetchrow = AsyncMock(return_value={"count": 0})
    mock_pool.fetch = AsyncMock(return_value=[])
    resp = test_client.get("/api/sessions")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []
    assert body["total"] == 0


def test_list_sessions_with_data(mock_pool: MagicMock, test_client: TestClient) -> None:
    mock_pool.fetchrow = AsyncMock(return_value={"count": 1})
    mock_pool.fetch = AsyncMock(return_value=[_SESSION_SUMMARY])
    resp = test_client.get("/api/sessions")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_list_sessions_query_params(mock_pool: MagicMock, test_client: TestClient) -> None:
    mock_pool.fetchrow = AsyncMock(return_value={"count": 0})
    mock_pool.fetch = AsyncMock(return_value=[])
    resp = test_client.get("/api/sessions?search=foo&date_from=2026-01-01&page=2&page_size=5")
    assert resp.status_code == 200


def test_get_session_found(mock_pool: MagicMock, test_client: TestClient) -> None:
    mock_pool.fetchrow = AsyncMock(return_value=_SESSION_DETAIL)
    mock_pool.fetch = AsyncMock(side_effect=[[], []])  # context, steps
    resp = test_client.get("/api/sessions/s1")
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == "s1"


def test_get_session_not_found(mock_pool: MagicMock, test_client: TestClient) -> None:
    mock_pool.fetchrow = AsyncMock(return_value=None)
    resp = test_client.get("/api/sessions/missing")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()
