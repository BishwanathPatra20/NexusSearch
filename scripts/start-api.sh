#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.
export KNOWLEDGEPILOT_OFFLINE_MODE=true
PYTHON="$(bash "${BASH_SOURCE[0]%/*}/_python.sh")"
exec "$PYTHON" -m uvicorn backend.app.main:app --host 127.0.0.1 --port "${KNOWLEDGEPILOT_PORT:-8000}"
