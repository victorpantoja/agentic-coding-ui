from __future__ import annotations

from fastapi import APIRouter, Depends

from app.common.models import DataResponse, ListResponse, StatusResponse
from app.mcp.client import SovereignBrainClient
from app.mcp.exceptions import MCPClientError  # noqa: F401 (re-exported for app exception handler)
from app.sessions.adapters.session_store import SessionStore, session_store
from app.sessions.features import (
    AbandonSessionFeature,
    FetchContextFeature,
    GetSessionFeature,
    GetTestSpecFeature,
    ImplementLogicFeature,
    ListSessionsFeature,
    RunReviewFeature,
    StartSessionFeature,
)
from app.sessions.models import (
    AgentInstruction,
    FetchContextRequest,
    GetTestSpecRequest,
    ImplementRequest,
    ReviewRequest,
    SessionRecord,
    StartSessionRequest,
)
from app.ws.manager import ConnectionManager, ws_manager

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])

# ── Dependency providers ──────────────────────────────────────────────────────

store_dep = Depends(lambda: session_store)
manager_dep = Depends(lambda: ws_manager)


def get_store() -> SessionStore:
    return session_store


def get_ws_manager() -> ConnectionManager:
    return ws_manager


def get_mcp_client() -> SovereignBrainClient:
    from app.config import settings

    return SovereignBrainClient(settings.mcp_url)


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("", response_model=ListResponse[SessionRecord])
async def list_sessions(
    store: SessionStore = Depends(get_store),
) -> ListResponse[SessionRecord]:
    result = await ListSessionsFeature(store=store).handle(
        ListSessionsFeature.Command()
    )
    return ListResponse(data=result.sessions, total=len(result.sessions))


@router.post("", response_model=DataResponse[SessionRecord], status_code=201)
async def create_session(
    body: StartSessionRequest,
    store: SessionStore = Depends(get_store),
    manager: ConnectionManager = Depends(get_ws_manager),
    client: SovereignBrainClient = Depends(get_mcp_client),
) -> DataResponse[SessionRecord]:
    result = await StartSessionFeature(store=store, client=client, manager=manager).handle(
        StartSessionFeature.Command(
            request=body.request,
            project_context=body.project_context,
            review_feedback=body.review_feedback,
        )
    )
    return DataResponse(data=result.session)


@router.get("/{session_id}", response_model=DataResponse[SessionRecord])
async def get_session(
    session_id: str,
    store: SessionStore = Depends(get_store),
) -> DataResponse[SessionRecord]:
    result = await GetSessionFeature(store=store).handle(
        GetSessionFeature.Command(session_id=session_id)
    )
    return DataResponse(data=result.session)


@router.post("/{session_id}/test-spec", response_model=DataResponse[AgentInstruction])
async def get_test_spec(
    session_id: str,
    body: GetTestSpecRequest,
    store: SessionStore = Depends(get_store),
    manager: ConnectionManager = Depends(get_ws_manager),
    client: SovereignBrainClient = Depends(get_mcp_client),
) -> DataResponse[AgentInstruction]:
    result = await GetTestSpecFeature(store=store, client=client, manager=manager).handle(
        GetTestSpecFeature.Command(
            session_id=session_id,
            plan=body.plan,
            scenario=body.scenario,
            existing_code=body.existing_code,
            project_context=body.project_context,
        )
    )
    return DataResponse(data=result.instruction)


@router.post("/{session_id}/implement", response_model=DataResponse[AgentInstruction])
async def implement_logic(
    session_id: str,
    body: ImplementRequest,
    store: SessionStore = Depends(get_store),
    manager: ConnectionManager = Depends(get_ws_manager),
    client: SovereignBrainClient = Depends(get_mcp_client),
) -> DataResponse[AgentInstruction]:
    result = await ImplementLogicFeature(store=store, client=client, manager=manager).handle(
        ImplementLogicFeature.Command(
            session_id=session_id,
            test_code=body.test_code,
            test_file_path=body.test_file_path,
            error_output=body.error_output,
            existing_code=body.existing_code,
        )
    )
    return DataResponse(data=result.instruction)


@router.post("/{session_id}/review", response_model=DataResponse[AgentInstruction])
async def run_review(
    session_id: str,
    body: ReviewRequest,
    store: SessionStore = Depends(get_store),
    manager: ConnectionManager = Depends(get_ws_manager),
    client: SovereignBrainClient = Depends(get_mcp_client),
) -> DataResponse[AgentInstruction]:
    result = await RunReviewFeature(store=store, client=client, manager=manager).handle(
        RunReviewFeature.Command(
            session_id=session_id,
            diff=body.diff,
            changed_files=body.changed_files,
            plan=body.plan,
            project_context=body.project_context,
        )
    )
    return DataResponse(data=result.instruction)


@router.post("/{session_id}/context", response_model=DataResponse[AgentInstruction])
async def fetch_context(
    session_id: str,
    body: FetchContextRequest,
    store: SessionStore = Depends(get_store),
    client: SovereignBrainClient = Depends(get_mcp_client),
) -> DataResponse[AgentInstruction]:
    result = await FetchContextFeature(store=store, client=client).handle(
        FetchContextFeature.Command(
            session_id=session_id,
            query=body.query,
            limit=body.limit,
        )
    )
    return DataResponse(data=result.instruction)


@router.delete("/{session_id}", response_model=StatusResponse)
async def abandon_session(
    session_id: str,
    store: SessionStore = Depends(get_store),
    manager: ConnectionManager = Depends(get_ws_manager),
) -> StatusResponse:
    result = await AbandonSessionFeature(store=store, manager=manager).handle(
        AbandonSessionFeature.Command(session_id=session_id)
    )
    return StatusResponse(status=result.status)
