#!/usr/bin/env bash
# `hyperframes check` also opens a Chrome (~1 GB). Use this script (same lock as the snapshots). Usage: ./check.sh <project>
set -euo pipefail
PROJ=$(realpath "$1")
L=${TMPDIR:-/tmp}/studio; mkdir -p "$L"
exec 9>"$L/snap.lock"
flock 9
systemd-run --user --scope -q -p MemoryMax=2500M -p MemorySwapMax=0 bash -c 'cd "$1" && npx --yes hyperframes@0.8.185 check --json 2>&1 | grep -E "\"(errorCount|warningCount|message)\"" | head -12' _ "$PROJ"
