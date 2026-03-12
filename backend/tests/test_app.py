from fastapi import FastAPI

from app.app import create_app


def test_create_app_returns_fastapi() -> None:
    app = create_app()
    assert isinstance(app, FastAPI)


def test_create_app_debug_mode() -> None:
    app = create_app(debug=True)
    assert app.debug is True


def test_routes_registered() -> None:
    app = create_app()
    paths = {r.path for r in app.routes}  # type: ignore[attr-defined]
    assert "/health" in paths
    assert "/api/sessions" in paths


def test_exception_handler_session_not_found() -> None:
    from fastapi.testclient import TestClient
    from app.sessions.adapters.session_store import SessionStore
    from app.sessions.routes import get_store

    app = create_app()
    store = SessionStore()
    app.dependency_overrides[get_store] = lambda: store
    client = TestClient(app)
    resp = client.get("/api/sessions/nonexistent")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_exception_handler_mcp_error() -> None:
    from unittest.mock import AsyncMock
    from fastapi.testclient import TestClient
    from app.mcp.client import SovereignBrainClient
    from app.mcp.exceptions import MCPClientError
    from app.sessions.adapters.session_store import SessionStore
    from app.sessions.routes import get_mcp_client, get_store, get_ws_manager
    from app.ws.manager import ConnectionManager

    app = create_app()
    store = SessionStore()
    manager = ConnectionManager()
    bad_mcp = SovereignBrainClient("http://test/sse")
    bad_mcp.start_session = AsyncMock(side_effect=MCPClientError("down"))  # type: ignore[method-assign]
    app.dependency_overrides[get_store] = lambda: store
    app.dependency_overrides[get_ws_manager] = lambda: manager
    app.dependency_overrides[get_mcp_client] = lambda: bad_mcp
    client = TestClient(app)
    resp = client.post("/api/sessions", json={"request": "build"})
    assert resp.status_code == 502
    assert "MCP error" in resp.json()["detail"]
