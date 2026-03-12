from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.mcp.client import SovereignBrainClient
    from app.sessions.adapters.session_store import SessionStore
    from app.ws.manager import ConnectionManager


class BaseFeature:
    def __init__(
        self,
        store: "SessionStore",
        client: "SovereignBrainClient | None" = None,
        manager: "ConnectionManager | None" = None,
    ) -> None:
        self._store = store
        self._client = client
        self._manager = manager
