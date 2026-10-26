#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
PYTHON="$(bash "${BASH_SOURCE[0]%/*}/_python.sh")"
exec "$PYTHON" -m streamlit run frontend/streamlit_app.py --server.address 127.0.0.1 --server.port "${STREAMLIT_SERVER_PORT:-8501}"
