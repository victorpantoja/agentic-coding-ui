from __future__ import annotations

from unittest.mock import AsyncMock

from fastapi import FastAPI


def test_create_app_returns_fastapi(mocker: object) -> None:
    mocker.patch("app.app.init_pool", new=AsyncMock())  # type: ignore[attr-defined]
    mocker.patch("app.app.close_pool", new=AsyncMock())  # type: ignore[attr-defined]
    from app.app import create_app
    app = create_app()
    assert isinstance(app, FastAPI)


def test_create_app_debug_mode(mocker: object) -> None:
    mocker.patch("app.app.init_pool", new=AsyncMock())  # type: ignore[attr-defined]
    mocker.patch("app.app.close_pool", new=AsyncMock())  # type: ignore[attr-defined]
    from app.app import create_app
    app = create_app(debug=True)
    assert app.debug is True


def test_routes_registered(mocker: object) -> None:
    mocker.patch("app.app.init_pool", new=AsyncMock())  # type: ignore[attr-defined]
    mocker.patch("app.app.close_pool", new=AsyncMock())  # type: ignore[attr-defined]
    from app.app import create_app
    app = create_app()
    paths = {r.path for r in app.routes}  # type: ignore[attr-defined]
    assert "/health" in paths
    assert "/api/sessions" in paths


def test_exception_handler_session_not_found(mocker: object) -> None:
    from unittest.mock import MagicMock
    from fastapi.testclient import TestClient

    mocker.patch("app.app.init_pool", new=AsyncMock())  # type: ignore[attr-defined]
    mocker.patch("app.app.close_pool", new=AsyncMock())  # type: ignore[attr-defined]

    from app.app import create_app
    from app.db.connection import get_pool

    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=None)
    pool.fetch = AsyncMock(return_value=[])

    app = create_app()
    app.dependency_overrides[get_pool] = lambda: pool
    with TestClient(app) as client:
        resp = client.get("/api/sessions/nonexistent-uuid")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()
