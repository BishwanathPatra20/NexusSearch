#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.
PY="$(bash "${ROOT}/scripts/_python.sh")"
if ! "$PY" -c "import pytest" 2>/dev/null; then
  echo "Installing dev dependencies…"
  "$PY" -m pip install -r requirements-dev.txt
fi
"$PY" -m pytest tests/ -q
