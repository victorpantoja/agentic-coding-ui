from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import app.db.connection as conn_module


async def test_init_pool_sets_global(mocker: object) -> None:
    fake_pool = MagicMock()
    mocker.patch("asyncpg.create_pool", new=AsyncMock(return_value=fake_pool))
    conn_module._pool = None
    result = await conn_module.init_pool("postgresql://test/test")
    assert result is fake_pool
    assert conn_module._pool is fake_pool


async def test_close_pool_clears_global(mocker: object) -> None:
    fake_pool = MagicMock()
    fake_pool.close = AsyncMock()
    conn_module._pool = fake_pool
    await conn_module.close_pool()
    fake_pool.close.assert_awaited_once()
    assert conn_module._pool is None


async def test_close_pool_noop_when_none() -> None:
    conn_module._pool = None
    await conn_module.close_pool()  # no error


def test_get_pool_returns_pool(mocker: object) -> None:
    fake_pool = MagicMock()
    conn_module._pool = fake_pool
    assert conn_module.get_pool() is fake_pool


def test_get_pool_raises_when_none() -> None:
    conn_module._pool = None
    with pytest.raises(AssertionError):
        conn_module.get_pool()
