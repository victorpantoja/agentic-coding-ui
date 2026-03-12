set dotenv-load := true

default:
    @just --list

# ── Docker network ────────────────────────────────────────────────────────────

network:
    docker network create sovereign-net 2>/dev/null || true

# ── Build ─────────────────────────────────────────────────────────────────────

build: network
    docker compose build

build-backend:
    docker build --target prod -t agentic-dashboard-backend:latest -f docker/Dockerfile .

build-frontend:
    docker compose build frontend

# ── Stack lifecycle ───────────────────────────────────────────────────────────

up: network
    docker compose up -d --remove-orphans

up-build: network
    docker compose up -d --build --remove-orphans

down:
    docker compose down --remove-orphans

clean:
    docker compose down --rmi local --volumes --remove-orphans

# ── Testing ───────────────────────────────────────────────────────────────────

test:
    docker build --target dev -t agentic-dashboard:test -f docker/Dockerfile .
    docker run --rm -e MCP_URL=http://test-mcp/sse agentic-dashboard:test

test-local:
    cd backend && uv run pytest

# ── Linting & type checking ───────────────────────────────────────────────────

lint:
    docker build --target dev -t agentic-dashboard:test -f docker/Dockerfile .
    docker run --rm --entrypoint ruff agentic-dashboard:test check app/ tests/

lint-fix:
    cd backend && uv run ruff check --fix app/ tests/

typecheck:
    cd backend && uv run mypy app/

check: lint typecheck

# ── Logs ──────────────────────────────────────────────────────────────────────

logs:
    docker compose logs -f

logs-backend:
    docker compose logs -f backend

logs-frontend:
    docker compose logs -f frontend

# ── Local development ─────────────────────────────────────────────────────────

install:
    cd backend && uv sync --extra dev

dev-backend:
    cd backend && uv run uvicorn app.main:app --reload --port 8080

dev-frontend:
    cd frontend && npm install && npm run dev
