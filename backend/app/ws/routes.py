from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

import asyncpg
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.db import queries
from app.db.connection import get_pool

router = APIRouter()


def _to_jsonable(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_jsonable(v) for v in obj]
    return obj


@router.websocket("/ws/{session_id}")
async def session_websocket(
    session_id: str,
    websocket: WebSocket,
    pool: asyncpg.Pool = Depends(get_pool),
) -> None:
    await websocket.accept()
    try:
        row = await queries.get_session(pool, session_id)
        if row is None:
            await websocket.send_json(
                {"type": "error", "data": {"detail": f"Session not found: {session_id}"}}
            )
            await websocket.close()
            return

        context = await queries.get_context_history(pool, session_id)
        await websocket.send_json(
            {"type": "session", "data": _to_jsonable({**row, "context": context})}
        )

        last_count = len(context)
        last_status = row["status"]

        while True:
            await asyncio.sleep(2)

            new_context = await queries.get_context_history(pool, session_id)
            for event in new_context[last_count:]:
                await websocket.send_json(
                    {"type": "context_event", "data": _to_jsonable(event)}
                )
            last_count = len(new_context)

            updated = await queries.get_session(pool, session_id)
            if updated and updated["status"] != last_status:
                last_status = updated["status"]
                await websocket.send_json(
                    {"type": "status", "data": _to_jsonable(updated)}
                )
    except WebSocketDisconnect:
        pass
