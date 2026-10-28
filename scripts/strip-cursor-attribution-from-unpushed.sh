#!/usr/bin/env bash
# Rewrite unpushed commits to remove Cursor co-author / Made-with trailers (safety net before push).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

UPSTREAM=""
if git rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
  UPSTREAM=$(git rev-parse '@{u}')
fi
if [ -z "$UPSTREAM" ]; then
  echo "No upstream branch; nothing to scan."
  exit 0
fi

if ! git log "${UPSTREAM}..HEAD" --format=%B | grep -qiE 'co-authored-by:[[:space:]]*cursor|made-with:[[:space:]]*cursor|cursoragent@cursor.com'; then
  echo "Unpushed commits: no Cursor attribution trailers."
  exit 0
fi

export FILTER_BRANCH_SQUELCH_WARNING=1
git filter-branch -f --msg-filter '
  sed "/^Co-authored-by: Cursor/d;/^Made-with: Cursor/d;/cursoragent@cursor.com/I d"
' "${UPSTREAM}..HEAD"
echo "Stripped Cursor trailers from unpushed commits."
