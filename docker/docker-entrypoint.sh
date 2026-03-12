#!/bin/bash
set -e
set -u
set -o pipefail
(( ${ENTRYPOINT_DEBUG:-0} > 0 )) && set -x

declare -a COMMAND

if [[ "${1:-}" == "pytest" ]]; then
    COMMAND+=("uv" "run" "pytest")
    shift
    COMMAND+=("$@")
else
    COMMAND+=("uv" "run" "uvicorn" "app.main:app" "--host" "0.0.0.0" "--port" "8080")
fi

echo "Starting: ${COMMAND[*]}"
exec "${COMMAND[@]}"
