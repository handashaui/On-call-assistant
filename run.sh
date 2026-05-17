#!/usr/bin/env bash
set -euo pipefail

args=(app.main:app --host "${HOST:-127.0.0.1}" --port "${PORT:-8000}")
if [[ "${RELOAD:-0}" == "1" ]]; then
  args+=(--reload)
fi

uvicorn "${args[@]}"
