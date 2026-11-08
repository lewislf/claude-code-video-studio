#!/usr/bin/env bash
# Renderiza os estilos pedidos (padrão: os três), normaliza o áudio em -14 LUFS
# e gera uma cópia 720p leve. Uso: ./render.sh [doc] [3d] [misto]
set -euo pipefail
cd "$(dirname "$0")"
FF=/home/linuxbrew/.linuxbrew/bin/ffmpeg
ESTILOS=("$@"); [ $# -eq 0 ] && ESTILOS=(doc 3d misto)
taskline set render-v2 0 ${#ESTILOS[@]} --label "render v2" --pid $$
for e in "${ESTILOS[@]}"; do
  python3 build.py "$e"
  # 2 workers: com 4 o Chromium passa de 4 GB e o teto mata o render
  systemd-run --user --scope -q -p MemoryMax=4G -p MemorySwapMax=0 \
    npx hyperframes render --fps 24 --quality draft --workers 2 -o "renders/bruto-$e.mp4" > "/tmp/claude-1002/render-$e.log" 2>&1
  grep -q "Render complete\|rendered in" "/tmp/claude-1002/render-$e.log" || { taskline fail render-v2 "$e falhou"; exit 1; }
  $FF -loglevel error -y -i "renders/bruto-$e.mp4" -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 -c:a aac -b:a 192k "renders/v2-$e.mp4"
  $FF -loglevel error -y -i "renders/v2-$e.mp4" -vf scale=-2:720 -c:v libx264 -preset medium -crf 32 -maxrate 400k -bufsize 800k \
    -c:a aac -b:a 64k -movflags +faststart "renders/v2-$e-720p.mp4"
  rm -f "renders/bruto-$e.mp4"
  taskline add render-v2
done
taskline done render-v2
