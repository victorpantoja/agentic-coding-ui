from __future__ import annotations

import asyncpg

_pool: asyncpg.Pool | None = None


async def init_pool(database_url: str) -> asyncpg.Pool:
    global _pool
    _pool = await asyncpg.create_pool(database_url, min_size=1, max_size=10)
    return _pool  # type: ignore[return-value]


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    assert _pool is not None, "Database pool not initialized"
    return _pool  # type: ignore[return-value]
