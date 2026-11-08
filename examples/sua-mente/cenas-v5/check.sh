#!/usr/bin/env bash
# `hyperframes check` também abre um Chrome (~1 GB). Use este script (mesma trava dos snapshots). Uso: ./check.sh <projeto>
set -euo pipefail
PROJ=$(realpath "$1")
exec 9>/tmp/claude-1002/snap.lock
flock 9
systemd-run --user --scope -q -p MemoryMax=2500M -p MemorySwapMax=0 bash -c 'cd "$1" && npx hyperframes check --json 2>&1 | grep -E "\"(errorCount|warningCount|message)\"" | head -12' _ "$PROJ"
