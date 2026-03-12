import pytest

from app.config import Settings


def test_defaults() -> None:
    with pytest.MonkeyPatch.context() as mp:
        mp.delenv("DATABASE_URL", raising=False)
        s = Settings()
        assert "sovereign_brain" in s.database_url
        assert s.port == 8080
        assert s.debug is False


def test_env_override() -> None:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DATABASE_URL", "postgresql://u:p@host/db")
        mp.setenv("PORT", "9090")
        mp.setenv("DEBUG", "true")
        s = Settings()
        assert s.database_url == "postgresql://u:p@host/db"
        assert s.port == 9090
        assert s.debug is True
