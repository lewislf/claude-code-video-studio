#!/usr/bin/env bash
# Final sped-up version (default 1.35x, 1080p) and a light copy for phones (540p, ~28 MB for 13 min).
#   deliver.sh v1-bar [1.35]     (from inside the project folder)  ->  renders/<name>-<speed>x.mp4 and -mobile.mp4
# Uses NVENC if FF_GPU points to an ffmpeg with h264_nvenc; otherwise libx264.
set -euo pipefail
IN=renders/$1.mp4; V=${2:-1.35}; OUT=renders/$1-${V}x.mp4
FILTER="[0:v]setpts=PTS/$V,fps=30[v];[0:a]atempo=$V[a]"
if [ -n "${FF_GPU:-}" ]; then
  "$FF_GPU" -loglevel error -stats -y -i "$IN" -filter_complex "$FILTER" -map "[v]" -map "[a]" -c:v h264_nvenc -preset p5 -cq 19 \
    -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart "$OUT"
else
  systemd-run --user --scope -q -p MemoryMax=4G -p MemorySwapMax=0 "${FF:-ffmpeg}" -loglevel error -stats -y -i "$IN" \
    -filter_complex "$FILTER" -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -c:a aac -b:a 192k \
    -movflags +faststart "$OUT"
fi
"${FF:-ffmpeg}" -loglevel error -y -i "$OUT" -vf scale=-2:540 -c:v libx264 -preset medium -b:v 230k -c:a aac -b:a 96k \
  -movflags +faststart "${OUT%.mp4}-mobile.mp4"
ls -la "$OUT" "${OUT%.mp4}-mobile.mp4"
