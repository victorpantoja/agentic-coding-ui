set dotenv-load := true

DEV_IMAGE := "agentic-dashboard:dev"

default:
    @just --list

# ── Docker network ────────────────────────────────────────────────────────────

network:
    docker network create sovereign-net 2>/dev/null || true

# ── Build ─────────────────────────────────────────────────────────────────────

# Build all images
build: network
    docker compose build

# Build the dev/test image
build-dev:
    docker build --target dev -t {{DEV_IMAGE}} -f docker/Dockerfile .

# Build production backend image
build-backend:
    docker build --target prod -t agentic-dashboard-backend:latest -f docker/Dockerfile .

# Build frontend image
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

# ── Testing (runs inside Docker) ──────────────────────────────────────────────

# Run full pytest suite with coverage inside the dev container
test: build-dev
    docker run --rm \
        -e MCP_URL=http://test-mcp/sse \
        {{DEV_IMAGE}}

# ── Linting & type checking (runs inside Docker via uv run) ───────────────────

# ruff lint check
lint: build-dev
    docker run --rm {{DEV_IMAGE}} uv run ruff check app/ tests/

# ruff format check
fmt-check: build-dev
    docker run --rm {{DEV_IMAGE}} uv run ruff format --check app/ tests/

# ruff auto-fix (runs locally via uv — modifies files)
lint-fix:
    cd backend && uv run ruff check --fix app/ tests/
    cd backend && uv run ruff format app/ tests/

# mypy strict type checking
typecheck: build-dev
    docker run --rm {{DEV_IMAGE}} uv run mypy app/

# All quality checks
check: lint fmt-check typecheck

# ── Logs ──────────────────────────────────────────────────────────────────────

logs:
    docker compose logs -f

logs-backend:
    docker compose logs -f backend

logs-frontend:
    docker compose logs -f frontend

# ── Local dev frontend (no Docker needed for UI) ─────────────────────────────

dev-frontend:
    cd frontend && npm install && npm run dev
