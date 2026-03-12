from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.health import routes as health_routes
from app.mcp.exceptions import MCPClientError
from app.sessions import routes as sessions_routes
from app.sessions.exceptions import SessionNotFoundError
from app.ws import routes as ws_routes


def create_app(debug: bool = False) -> FastAPI:
    app = FastAPI(
        title="Agentic Dashboard API",
        description="Monitor and interact with sovereign-brain coding sessions",
        version="0.1.0",
        debug=debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(SessionNotFoundError)
    async def session_not_found_handler(
        request: Request, exc: SessionNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404, content={"detail": f"Session not found: {exc}"}
        )

    @app.exception_handler(MCPClientError)
    async def mcp_error_handler(
        request: Request, exc: MCPClientError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=502, content={"detail": f"MCP error: {exc}"}
        )

    app.include_router(sessions_routes.router)
    app.include_router(ws_routes.router)
    app.include_router(health_routes.router)

    return app
