from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.db.connection import get_pool


def make_pool(
    *,
    fetchrow_return: object = None,
    fetch_return: list[object] | None = None,
) -> MagicMock:
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=fetchrow_return)
    pool.fetch = AsyncMock(return_value=fetch_return or [])
    return pool


@pytest.fixture
def mock_pool() -> MagicMock:
    return make_pool()


@pytest.fixture
def test_client(mock_pool: MagicMock, mocker: object) -> TestClient:
    import pytest_mock

    assert isinstance(mocker, pytest_mock.MockerFixture)
    mocker.patch("app.app.init_pool", new=AsyncMock())
    mocker.patch("app.app.close_pool", new=AsyncMock())

    from app.app import create_app

    app = create_app()
    app.dependency_overrides[get_pool] = lambda: mock_pool
    with TestClient(app) as client:
        return client
