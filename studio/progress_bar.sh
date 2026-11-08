#!/usr/bin/env bash
# Thin progress bar at the bottom, no numbers: translucent track + violet-cyan gradient fill with a glow.
#   progress_bar.sh v1 v1-bar   (from inside the project folder)
# Re-encodes only the video (audio is copied). The tip moves at subpixel precision via overlay with fractional x (eval=frame).
set -euo pipefail
mkdir -p renders
FF=${FF:-ffmpeg}
IN=renders/$1.mp4; OUT=renders/$2.mp4
T=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
H=4; Y=1066; M=0   # 4 px tall, 10 px above the edge
FC="color=c=white@0.10:s=1920x${H}:r=30,format=rgba[track];"
FC+="gradients=s=1920x${H}:c0=0x8d7bff:c1=0x5ee6ff:x0=0:y0=0:x1=1920:y1=0:r=30,format=rgba[g1];"
FC+="gradients=s=1920x16:c0=0x8d7bff:c1=0x5ee6ff:x0=0:y0=0:x1=1920:y1=0:r=30,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='140*exp(-pow((Y-7.5)/3.2,2))'[glow];"
FC+="[0:v][track]overlay=0:${Y}:shortest=1[a];"
FC+="[a][glow]overlay=x='-W+W*t/${T}':y=$((Y-6)):eval=frame:shortest=1[b];"
FC+="[b][g1]overlay=x='-W+W*t/${T}':y=${Y}:eval=frame:shortest=1[v]"
systemd-run --user --scope -q -p MemoryMax=4G -p MemorySwapMax=0 \
  "$FF" -loglevel error -stats -y -i "$IN" -filter_complex "$FC" -map "[v]" -map 0:a -c:v libx264 -preset veryfast -crf 17 \
  -pix_fmt yuv420p -g 30 -c:a copy -movflags +faststart "$OUT"
echo "done: $OUT"
