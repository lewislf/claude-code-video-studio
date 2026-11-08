#!/usr/bin/env bash
# Snapshot with a global lock and a memory cap. Usage: ./snap.sh <project> <out> <t1,t2,...>
# Only one snapshot at a time on the machine (flock), 3 GB max, refuses if little memory is left.
set -euo pipefail
PROJ=$(realpath "$1"); OUT=$2; TIMES=$3
L=${TMPDIR:-/tmp}/studio; mkdir -p "$L"
exec 9>"$L/snap.lock"
flock 9
AVAIL=$(free -m | awk '/^Mem:/{print $7}')
if [ "$AVAIL" -lt 3300 ]; then echo "available memory ${AVAIL} MB (< 3300): not running" >&2; exit 3; fi
rm -rf "$OUT"
systemd-run --user --scope -q -p MemoryMax=3000M -p MemorySwapMax=0 bash -c 'cd "$1" && npx --yes hyperframes@0.8.185 snapshot --at "$3" -o "$2"' _ "$PROJ" "$OUT" "$TIMES" 2>&1 | tail -2
ls "$OUT" | head -40
