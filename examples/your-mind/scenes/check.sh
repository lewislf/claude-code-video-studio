#!/usr/bin/env bash
# `hyperframes check` also opens a Chrome (~1 GB). Use this script (same lock as the snapshots). Usage: ./check.sh <project>
set -euo pipefail
PROJ=$(realpath "$1")
mkdir -p "${TMPDIR:-/tmp}/studio"
exec 9>"${TMPDIR:-/tmp}/studio/snap.lock"
flock 9
systemd-run --user --scope -q -p MemoryMax=2500M -p MemorySwapMax=0 bash -c 'cd "$1" && npx hyperframes check --json 2>&1 | grep -E "\"(errorCount|warningCount|message)\"" | head -12' _ "$PROJ"
