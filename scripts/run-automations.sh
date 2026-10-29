#!/usr/bin/env bash
# Run Idea B automation agents (cron-friendly). API must be running OR use inline Python.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.
PY="$(bash "${ROOT}/scripts/_python.sh")"

"$PY" <<'PY'
from backend.app.db.connection import get_connection
from backend.app.services.automation.runner import run_automation_batch

with get_connection() as conn:
    runs = run_automation_batch(conn, [], trigger="schedule")
for r in runs:
    print(f"{r['status']:9} {r['agent']}: {r.get('message', '')}")
PY
