from __future__ import annotations

from fastapi.testclient import TestClient

from app.mcp.client import SovereignBrainClient
from app.sessions.adapters.session_store import SessionStore
from app.sessions.routes import get_mcp_client, get_store, get_ws_manager
from app.ws.manager import ConnectionManager


def test_default_get_store() -> None:
    from app.sessions.routes import get_store as _fn
    assert isinstance(_fn(), SessionStore)


def test_default_get_ws_manager() -> None:
    from app.sessions.routes import get_ws_manager as _fn
    assert isinstance(_fn(), ConnectionManager)


def test_default_get_mcp_client() -> None:
    from app.sessions.routes import get_mcp_client as _fn
    assert isinstance(_fn(), SovereignBrainClient)


def test_list_sessions_empty(test_client: TestClient) -> None:
    resp = test_client.get("/api/sessions")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []
    assert body["total"] == 0


def test_create_session(test_client: TestClient) -> None:
    resp = test_client.post("/api/sessions", json={"request": "build a service"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["session_id"] == "test-session-1"


def test_list_sessions_after_create(test_client: TestClient) -> None:
    test_client.post("/api/sessions", json={"request": "req"})
    resp = test_client.get("/api/sessions")
    assert resp.json()["total"] == 1


def test_get_session(test_client: TestClient) -> None:
    test_client.post("/api/sessions", json={"request": "req"})
    resp = test_client.get("/api/sessions/test-session-1")
    assert resp.status_code == 200
    assert resp.json()["data"]["session_id"] == "test-session-1"


def test_get_session_not_found(test_client: TestClient) -> None:
    assert test_client.get("/api/sessions/nope").status_code == 404


def test_get_test_spec(test_client: TestClient) -> None:
    test_client.post("/api/sessions", json={"request": "req"})
    resp = test_client.post(
        "/api/sessions/test-session-1/test-spec", json={"plan": "the plan"}
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["agent"] == "architect"


def test_get_test_spec_not_found(test_client: TestClient) -> None:
    resp = test_client.post("/api/sessions/missing/test-spec", json={"plan": "p"})
    assert resp.status_code == 404


def test_implement_logic(test_client: TestClient) -> None:
    test_client.post("/api/sessions", json={"request": "req"})
    resp = test_client.post(
        "/api/sessions/test-session-1/implement",
        json={"test_code": "pass", "test_file_path": "tests/t.py"},
    )
    assert resp.status_code == 200


def test_implement_logic_not_found(test_client: TestClient) -> None:
    resp = test_client.post(
        "/api/sessions/missing/implement",
        json={"test_code": "c", "test_file_path": "p.py"},
    )
    assert resp.status_code == 404


def test_run_review(test_client: TestClient) -> None:
    test_client.post("/api/sessions", json={"request": "req"})
    resp = test_client.post(
        "/api/sessions/test-session-1/review", json={"diff": "--- a\n+++ b"}
    )
    assert resp.status_code == 200


def test_run_review_not_found(test_client: TestClient) -> None:
    resp = test_client.post("/api/sessions/missing/review", json={"diff": "d"})
    assert resp.status_code == 404


def test_fetch_context(test_client: TestClient) -> None:
    test_client.post("/api/sessions", json={"request": "req"})
    resp = test_client.post(
        "/api/sessions/test-session-1/context", json={"query": "patterns"}
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["agent"] == "architect"


def test_fetch_context_not_found(test_client: TestClient) -> None:
    resp = test_client.post("/api/sessions/missing/context", json={"query": "q"})
    assert resp.status_code == 404


def test_abandon_session(test_client: TestClient) -> None:
    test_client.post("/api/sessions", json={"request": "req"})
    resp = test_client.delete("/api/sessions/test-session-1")
    assert resp.status_code == 200
    assert resp.json()["status"] == "abandoned"


def test_abandon_session_not_found(test_client: TestClient) -> None:
    resp = test_client.delete("/api/sessions/missing")
    assert resp.status_code == 404
