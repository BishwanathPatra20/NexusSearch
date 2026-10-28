#!/usr/bin/env bash
# Point this repo at .githooks so Cursor attribution trailers are stripped on every commit.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
chmod +x .githooks/commit-msg
git config --local core.hooksPath .githooks
echo "Installed: core.hooksPath=.githooks (repo-local only)"
