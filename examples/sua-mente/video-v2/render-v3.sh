#!/usr/bin/env bash
# Vídeo inteiro (estilo misto) com as cenas novas de cenas-v3. Saída: renders/v3-misto.mp4 (+ 720p).
set -euo pipefail
cd "$(dirname "$0")"
FF=/home/linuxbrew/.linuxbrew/bin/ffmpeg
taskline set render-v3 0 3 --label "v3: gerar" --pid $$
python3 build.py misto --v3
taskline set render-v3 1 3 --label "v3: esperando memória"
until [ "$(free -m | awk '/^Mem:/{print $7}')" -ge 5200 ]; do sleep 20; done
taskline set render-v3 1 3 --label "v3: render (2 workers)"
systemd-run --user --scope -q -p MemoryMax=5G -p MemorySwapMax=0 \
  npx hyperframes render --fps 24 --quality draft --workers 2 -o renders/bruto-v3.mp4 > /tmp/claude-1002/render-v3.log 2>&1
grep -q "Render complete\|rendered in" /tmp/claude-1002/render-v3.log || { taskline fail render-v3 "render falhou"; exit 1; }
taskline set render-v3 2 3 --label "v3: áudio e 720p"
$FF -loglevel error -y -i renders/bruto-v3.mp4 -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 -c:a aac -b:a 192k renders/v3-misto.mp4
$FF -loglevel error -y -i renders/v3-misto.mp4 -vf scale=-2:720 -c:v libx264 -preset medium -crf 30 -maxrate 1500k -bufsize 3000k -c:a aac -b:a 96k -movflags +faststart renders/v3-misto-720p.mp4
rm -f renders/bruto-v3.mp4
taskline done render-v3
