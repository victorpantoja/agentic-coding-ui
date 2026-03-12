from fastapi.testclient import TestClient

from app.app import create_app

client = TestClient(create_app())


def test_health_ok() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
