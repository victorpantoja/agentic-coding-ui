from __future__ import annotations

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.sessions.adapters.session_store import SessionStore
from app.sessions.routes import get_store, get_ws_manager
from app.ws.manager import ConnectionManager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/{session_id}")
async def session_ws(
    session_id: str,
    websocket: WebSocket,
    store: SessionStore = Depends(get_store),
    manager: ConnectionManager = Depends(get_ws_manager),
) -> None:
    await websocket.accept()
    manager.connect(session_id, websocket)

    record = store.get(session_id)
    if record is not None:
        await websocket.send_text(record.model_dump_json())

    try:
        while True:
            msg = await websocket.receive()
            if msg.get("type") == "websocket.disconnect":
                break
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(session_id, websocket)
