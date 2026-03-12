#!/usr/bin/env bash
set -euo pipefail

# Ensure the shared sovereign-net network exists
docker network create sovereign-net 2>/dev/null || true

docker compose up --detach --remove-orphans

echo "Agentic Dashboard is up — http://localhost:80"
