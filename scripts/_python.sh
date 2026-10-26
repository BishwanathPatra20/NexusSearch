#!/usr/bin/env bash
# Prefer project venv so scripts work without `source .venv/bin/activate`.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -x "${ROOT}/.venv/bin/python" ]]; then
  echo "${ROOT}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  echo python3
elif command -v python >/dev/null 2>&1; then
  echo python
else
  echo "No python3 found. Run: python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt" >&2
  exit 1
fi
