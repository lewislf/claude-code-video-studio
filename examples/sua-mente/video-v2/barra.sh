#!/usr/bin/env bash
# Barra de progresso fina no rodapé, sem número: trilho translúcido + preenchimento em gradiente violeta-ciano com brilho.
#   ./barra.sh v7-misto v8-misto
# Recodifica só o vídeo (o áudio é copiado). A ponta anda em subpixel via overlay com x fracionário (eval=frame).
set -euo pipefail
cd "$(dirname "$0")"
FF=/home/linuxbrew/.linuxbrew/bin/ffmpeg
IN=renders/$1.mp4; OUT=renders/$2.mp4
T=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
H=4; Y=1066; M=0   # 4 px de altura, 10 px acima da borda
FC="color=c=white@0.10:s=1920x${H}:r=30,format=rgba[trilho];"
FC+="gradients=s=1920x${H}:c0=0x8d7bff:c1=0x5ee6ff:x0=0:y0=0:x1=1920:y1=0:r=30,format=rgba[g1];"
FC+="gradients=s=1920x16:c0=0x8d7bff:c1=0x5ee6ff:x0=0:y0=0:x1=1920:y1=0:r=30,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='140*exp(-pow((Y-7.5)/3.2,2))'[brilho];"
FC+="[0:v][trilho]overlay=0:${Y}:shortest=1[a];"
FC+="[a][brilho]overlay=x='-W+W*t/${T}':y=$((Y-6)):eval=frame:shortest=1[b];"
FC+="[b][g1]overlay=x='-W+W*t/${T}':y=${Y}:eval=frame:shortest=1[v]"
systemd-run --user --scope -q -p MemoryMax=4G -p MemorySwapMax=0 \
  "$FF" -loglevel error -stats -y -i "$IN" -filter_complex "$FC" -map "[v]" -map 0:a -c:v libx264 -preset veryfast -crf 17 \
  -pix_fmt yuv420p -g 30 -c:a copy -movflags +faststart "$OUT"
"$FF" -loglevel error -y -i "$OUT" -vf scale=-2:720 -c:v libx264 -preset medium -crf 30 -maxrate 1500k -bufsize 3000k \
  -c:a aac -b:a 96k -movflags +faststart "renders/$2-720p.mp4"
echo "pronto: $OUT"
