from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.connection import close_pool, init_pool
from app.health import routes as health_routes
from app.sessions import routes as sessions_routes
from app.sessions.exceptions import SessionNotFoundError
from app.ws import routes as ws_routes


def create_app(debug: bool = False) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        await init_pool(settings.database_url)
        yield
        await close_pool()

    app = FastAPI(
        title="Agentic Dashboard API",
        description="Read-only view of sovereign-brain coding sessions",
        version="0.1.0",
        debug=debug,
        lifespan=lifespan,
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

    app.include_router(sessions_routes.router)
    app.include_router(health_routes.router)
    app.include_router(ws_routes.router)

    return app
