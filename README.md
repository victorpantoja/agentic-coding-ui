# Agentic Dashboard

A production-ready UI and backend to monitor and interact with coding sessions driven by the [sovereign-brain](../agentic-coding) MCP server.

## Architecture

```
┌─────────────┐   WebSocket / REST   ┌──────────────────┐   SSE/MCP   ┌─────────────────┐
│  React 19   │ ◄──────────────────► │  FastAPI Backend  │ ──────────► │ sovereign-brain │
│  (Vite)     │                      │  (Python 3.12)    │             │  MCP Server     │
└─────────────┘                      └──────────────────┘             └─────────────────┘
      nginx                           routes→features→adapters          port 8000 (SSE)
```

### Backend module structure

```
backend/app/
├── app.py                   # FastAPI factory (create_app)
├── main.py                  # Uvicorn entry point
├── config.py                # Pydantic Settings
├── common/
│   ├── features.py          # BaseFeature (Command/Result pattern)
│   └── models.py            # DataResponse, ListResponse, StatusResponse, ErrorResponse
├── health/                  # GET /health
├── mcp/                     # sovereign-brain MCP client
│   ├── client.py
│   ├── exceptions.py
│   └── models.py            # AgentInstruction
├── sessions/                # Session lifecycle
│   ├── routes.py            # /api/sessions/*
│   ├── features.py          # ListSessions, StartSession, GetTestSpec, …
│   ├── models.py
│   ├── exceptions.py
│   └── adapters/
│       └── session_store.py # In-memory session store
└── ws/                      # WebSocket live stream
    ├── routes.py            # WS /ws/{session_id}
    └── manager.py           # ConnectionManager
```

### Frontend

- **SessionDashboard** — sidebar list + new session form
- **LiveMonologue** — streams `AgentInstruction` steps per agent (architect / tester / dev / reviewer)
- **DiffViewer** — renders unified diffs from instruction context

## Prerequisites

- Docker & Docker Compose
- [just](https://github.com/casey/just) task runner
- sovereign-brain stack running (creates the `sovereign-net` Docker network)

## Quick start

```bash
# 1. Create the shared network (one-time)
just network

# 2. Build and start
just up-build

# Dashboard → http://localhost:80
```

### Local development (no Docker)

```bash
just install          # uv sync --extra dev

# Terminal 1
just dev-backend      # uvicorn on :8080  (MCP_URL=http://localhost:8000/sse)

# Terminal 2
just dev-frontend     # vite on :5173
```

Set `MCP_URL=http://localhost:8000/sse` in `backend/.env` when running locally.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_URL` | `http://mcp-server:8000/sse` | sovereign-brain SSE endpoint |
| `DEBUG` | `false` | FastAPI debug mode |
| `PORT` | `8080` | Backend listen port |
| `CORS_ORIGINS` | `["http://localhost:5173","http://frontend:80"]` | Allowed origins |

Copy `.env.example` → `.env` to override.

## Docker networking

The backend joins **two** Docker networks:

| Network | Purpose |
|---------|---------|
| `dashboard-net` | Frontend ↔ Backend communication |
| `sovereign-net` | Backend ↔ sovereign-brain MCP server |

`sovereign-net` is an **external** network created by `just network`. The sovereign-brain `mcp-server` container must also be attached to it.

## API reference

All responses are wrapped in a shared envelope:

```json
{ "success": true, "data": { … } }          // DataResponse
{ "success": true, "data": [ … ], "total": N } // ListResponse
{ "success": true, "status": "abandoned" }   // StatusResponse
```

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/sessions` | List all sessions |
| `POST` | `/api/sessions` | Start a new session |
| `GET` | `/api/sessions/{id}` | Get session detail |
| `POST` | `/api/sessions/{id}/test-spec` | Get test specification |
| `POST` | `/api/sessions/{id}/implement` | Implement logic |
| `POST` | `/api/sessions/{id}/review` | Run review |
| `POST` | `/api/sessions/{id}/context` | Fetch context |
| `DELETE` | `/api/sessions/{id}` | Abandon session |
| `WS` | `/ws/{session_id}` | Live instruction stream |
| `GET` | `/health` | Health check |

## Quality

```bash
just test        # pytest inside Docker (100% coverage enforced)
just lint        # ruff check
just typecheck   # mypy strict
just check       # lint + typecheck
```

## CI/CD

| Workflow | Trigger | Checks |
|----------|---------|--------|
| `lint.yaml` | Every push | ruff check + format + mypy |
| `run_tests.yaml` | Every push | pytest in Docker (100% cov) |
| `run-security-checks.yaml` | PRs + main | Trivy (CRITICAL/HIGH) + Semgrep |
| `vulture.yaml` | PRs + main | Dead code (≥80% confidence) |
