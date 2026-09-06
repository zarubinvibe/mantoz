#!/bin/sh
# Offline self-check of a fresh clone: no network, no Docker, no Harbor, no git.
# Accepts --selftest so the release gate can discover and run it.
set -e
cd "$(dirname "$0")/.."
PY=python3
command -v "$PY" >/dev/null 2>&1 || { echo "mantoz-selfcheck: python3 not found" >&2; exit 1; }
exec "$PY" scripts/mantoz-selfcheck.py "$@"
