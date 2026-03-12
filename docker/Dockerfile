FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

RUN adduser --disabled-password --home /app --shell /bin/bash app
WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

# ── Production ────────────────────────────────────────────────────────────────
FROM base AS prod

COPY backend/pyproject.toml ./
RUN uv venv && uv pip install -e .

COPY backend/app/ app/

USER app
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

# ── Development / Testing ─────────────────────────────────────────────────────
FROM base AS dev

COPY backend/pyproject.toml backend/.ruff.toml backend/.mypy.ini ./
RUN uv venv && uv pip install -e ".[dev]"

COPY backend/app/ app/
COPY backend/tests/ tests/

CMD ["uv", "run", "pytest"]
