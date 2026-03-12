from __future__ import annotations

import json
from typing import Any

import asyncpg


async def list_sessions(
    pool: asyncpg.Pool,
    *,
    search: str = "",
    date_from: str = "",
    date_to: str = "",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    conditions: list[str] = []
    args: list[Any] = []

    if search:
        args.append(f"%{search}%")
        conditions.append(f"request ILIKE ${len(args)}")
    if date_from:
        args.append(date_from)
        conditions.append(f"updated_at >= ${len(args)}::date")
    if date_to:
        args.append(date_to)
        conditions.append(f"updated_at < (${len(args)}::date + interval '1 day')")

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    count_row = await pool.fetchrow(f"SELECT COUNT(*) FROM sessions {where}", *args)
    total = int(count_row["count"])  # type: ignore[index]

    args += [page_size, (page - 1) * page_size]
    n = len(args)
    rows = await pool.fetch(
        f"""
        SELECT id::text, request, status, created_at, updated_at
        FROM sessions {where}
        ORDER BY updated_at DESC
        LIMIT ${n - 1} OFFSET ${n}
        """,
        *args,
    )
    return [dict(r) for r in rows], total


async def get_session(
    pool: asyncpg.Pool,
    session_id: str,
) -> dict[str, Any] | None:
    row = await pool.fetchrow(
        """
        SELECT id::text, request, status,
               plan, test_spec, implementation, review,
               created_at, updated_at
        FROM sessions WHERE id = $1::uuid
        """,
        session_id,
    )
    if row is None:
        return None
    d = dict(row)
    for field in ("plan", "test_spec", "implementation", "review"):
        if isinstance(d[field], str):
            d[field] = json.loads(d[field])
    return d


async def get_session_steps(
    pool: asyncpg.Pool,
    session_id: str,
) -> list[dict[str, Any]]:
    rows = await pool.fetch(
        """
        SELECT id::text, step_name, status, scheduled_at, started_at, ended_at, error_details
        FROM session_steps
        WHERE session_id = $1::uuid
        ORDER BY
            CASE step_name
                WHEN 'plan'      THEN 1
                WHEN 'test'      THEN 2
                WHEN 'implement' THEN 3
                WHEN 'review'    THEN 4
            END
        """,
        session_id,
    )
    return [dict(r) for r in rows]


async def get_context_history(
    pool: asyncpg.Pool,
    session_id: str,
) -> list[dict[str, Any]]:
    rows = await pool.fetch(
        """
        SELECT id::text, event_type, data, summary, created_at
        FROM context_history
        WHERE session_id = $1::uuid
        ORDER BY created_at ASC
        """,
        session_id,
    )
    result = []
    for r in rows:
        d = dict(r)
        if isinstance(d.get("data"), str):
            d["data"] = json.loads(d["data"])
        result.append(d)
    return result
