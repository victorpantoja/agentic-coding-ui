#################### Base image ####################
FROM python:3.13.9-slim-bookworm AS base

ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN adduser --disabled-password --home /app --shell /bin/bash app

WORKDIR /app


#################### Build stage - Production ####################
FROM base AS builder-prod

RUN --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    --mount=type=cache,target=/app/.cache/uv \
    uv sync --no-dev --no-install-project --frozen


#################### Build stage - Development ####################
FROM base AS builder-dev

RUN --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    --mount=type=cache,target=/app/.cache/uv \
    uv sync --group dev --no-install-project --frozen


#################### Production image ####################
FROM base AS prod

USER app

COPY --from=builder-prod --chown=app:app /app/.venv/ /app/.venv/

COPY backend/app app

COPY --chown=app:app docker/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]


#################### Development image ####################
FROM base AS dev

USER app

COPY --from=builder-dev --chown=app:app /app/.venv/ /app/.venv/

COPY backend/app app
COPY backend/tests tests
COPY backend/pyproject.toml pyproject.toml

COPY backend/.ruff.toml .ruff.toml
COPY backend/.mypy.ini .mypy.ini

COPY --chown=app:app docker/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["pytest"]
