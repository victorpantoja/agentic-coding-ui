set dotenv-load := true

default:
    @just --list

# ── Build ─────────────────────────────────────────────────────────────────────

# Build both dev images and create the Docker network
build:
    docker network create sovereign-net 2>/dev/null || true
    docker build --target dev -t agentic-dashboard:dev -f docker/Dockerfile .
    docker build --target dev -t agentic-dashboard:frontend-dev -f docker/Dockerfile.frontend frontend/

# ── Stack lifecycle ───────────────────────────────────────────────────────────

# Start dev stack (local files mounted, reloads on code change)
up:
    docker network create sovereign-net 2>/dev/null || true
    docker compose up -d

down:
    docker compose down --remove-orphans

clean:
    docker compose down --rmi local --volumes --remove-orphans

# ── Testing ───────────────────────────────────────────────────────────────────

# Run tests inside the dev container
test:
    docker run --rm agentic-dashboard:dev

# ── Logs ──────────────────────────────────────────────────────────────────────

logs:
    docker compose logs -f

logs-backend:
    docker compose logs -f backend

logs-frontend:
    docker compose logs -f frontend
