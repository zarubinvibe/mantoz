#!/bin/sh
# Mantoz installer.
#
# It never guesses. Every step says what it found, what it did, and what is left
# for you. A missing optional tool is reported and the install continues; a broken
# tree stops it.
set -e
cd "$(dirname "$0")"

say() { printf '%s\n' "$*"; }
warn() { printf '!! %s\n' "$*" >&2; }

# Run a command with a hard time budget, and kill the command itself rather than
# its shell. Without this an installer on a slow or black-holed network keeps a
# download running after everything above it has given up, and the leftover
# process writes into a directory somebody else is already deleting.
# ponytail: portable POSIX watchdog; drop it for `timeout` once GNU coreutils is a given.
with_budget() {
  budget=$1; shift
  "$@" & job=$!
  (
    waited=0
    while [ "$waited" -lt "$budget" ]; do
      sleep 1
      kill -0 "$job" 2>/dev/null || exit 0
      waited=$((waited + 1))
    done
    kill -TERM "$job" 2>/dev/null
  ) & watchdog=$!
  wait "$job" 2>/dev/null; status=$?
  kill -TERM "$watchdog" 2>/dev/null
  return $status
}

say "Mantoz — population-scale evaluation with simulated personas"
say ""

# 1. Python. Mantoz runs on 3.12; uv can fetch that version itself, so an older
#    system python is reported and does not stop the install.
if ! command -v python3 >/dev/null 2>&1; then
  warn "python3 not found. Install Python 3.12 or newer, then run this script again."
  exit 1
fi
PYVER=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
say "python3 $PYVER found"
if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)'; then
  warn "this python3 is $PYVER and Mantoz runs on 3.12 or newer."
  warn "uv fetches its own 3.12 below, so the system python does not have to change."
fi

# 2. uv creates the environment and installs Harbor. Without it the checks below
#    still run, and the exact command to finish the install is printed.
if command -v uv >/dev/null 2>&1; then
  say "uv found, creating the environment"
  export UV_HTTP_TIMEOUT=20
  if with_budget 60 uv venv --python 3.12 >/dev/null 2>&1 \
     && with_budget 90 uv pip install -e . >/dev/null 2>&1; then
    say "dependencies installed, Harbor included"
  else
    warn "uv did not finish inside its time budget: no network, or Harbor is unreachable."
    warn "Finish it later with: uv venv --python 3.12 && uv pip install -e ."
  fi
else
  warn "uv not found, so dependencies are not installed yet."
  warn "Get uv from https://docs.astral.sh/uv/ then run: uv venv --python 3.12 && uv pip install -e ."
fi

# 3. Docker runs the four task environments. It is optional for the checks.
if command -v docker >/dev/null 2>&1; then
  say "docker found, the sandboxed environments can run"
else
  warn "docker not found. Persona generation and reports still work; the four task"
  warn "environments need Docker, which is free, or the paid Modal backend."
fi

# 4. The tree itself has to be sound. This one is not optional.
say ""
say "running the offline self-check"
sh scripts/mantoz-selfcheck.sh --selftest

say ""
say "Done. First run:"
say "  uv run python -m mantoz.population run --n-runs 3 --seed 7 --task survey --out runs/first.json"
say "  uv run python -m mantoz.viewer render --report runs/first.json --out runs/first.html"
