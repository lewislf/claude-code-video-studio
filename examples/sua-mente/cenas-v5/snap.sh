#!/usr/bin/env bash
# Snapshot com trava global e teto de memória. Uso: ./snap.sh <projeto> <saida> <t1,t2,...>
# Só um snapshot por vez na máquina (flock), 3 GB no máximo, recusa se sobrar pouca memória.
set -euo pipefail
PROJ=$(realpath "$1"); OUT=$2; TIMES=$3
mkdir -p /tmp/claude-1002
exec 9>/tmp/claude-1002/snap.lock
flock 9
DISP=$(free -m | awk '/^Mem:/{print $7}')
if [ "$DISP" -lt 3300 ]; then echo "memória disponível ${DISP} MB (< 3300): não rodei" >&2; exit 3; fi
rm -rf "$OUT"
systemd-run --user --scope -q -p MemoryMax=3000M -p MemorySwapMax=0 bash -c 'cd "$1" && npx hyperframes snapshot --at "$3" -o "$2"' _ "$PROJ" "$OUT" "$TIMES" 2>&1 | tail -2
ls "$OUT" | head -40
