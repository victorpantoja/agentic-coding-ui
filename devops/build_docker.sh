#!/usr/bin/env bash
set -euo pipefail

docker build \
  --target dev \
  -t agentic-dashboard:local \
  -f docker/Dockerfile \
  .

echo "Built agentic-dashboard:local (dev target)"
