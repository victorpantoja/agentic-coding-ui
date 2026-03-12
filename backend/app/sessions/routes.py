from __future__ import annotations

import asyncpg
from fastapi import APIRouter, Depends, Query

from app.common.models import DataResponse, ListResponse
from app.db.connection import get_pool
from app.sessions.features import GetSessionFeature, ListSessionsFeature
from app.sessions.models import SessionDetail, SessionSummary

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.get("", response_model=ListResponse[SessionSummary])
async def list_sessions(
    search: str = Query(""),
    date_from: str = Query(""),
    date_to: str = Query(""),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    pool: asyncpg.Pool = Depends(get_pool),
) -> ListResponse[SessionSummary]:
    result = await ListSessionsFeature(pool=pool).handle(
        ListSessionsFeature.Command(
            search=search,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size,
        )
    )
    return ListResponse(data=result.sessions, total=result.total)


@router.get("/{session_id}", response_model=DataResponse[SessionDetail])
async def get_session(
    session_id: str,
    pool: asyncpg.Pool = Depends(get_pool),
) -> DataResponse[SessionDetail]:
    result = await GetSessionFeature(pool=pool).handle(
        GetSessionFeature.Command(session_id=session_id)
    )
    return DataResponse(data=result.session)
