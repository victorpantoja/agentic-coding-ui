import pytest

from app.config import Settings


def test_defaults() -> None:
    s = Settings()
    assert s.mcp_url == "http://mcp-server:8000/sse"
    assert s.port == 8080
    assert s.debug is False


def test_env_override() -> None:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("MCP_URL", "http://custom:9000/sse")
        mp.setenv("PORT", "9090")
        mp.setenv("DEBUG", "true")
        s = Settings()
        assert s.mcp_url == "http://custom:9000/sse"
        assert s.port == 9090
        assert s.debug is True
