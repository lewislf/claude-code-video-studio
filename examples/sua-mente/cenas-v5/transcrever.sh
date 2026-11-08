#!/usr/bin/env bash
# Tempos por palavra de cada cena (whisper small, pt). Saída: palavras/<cena>.json, tempos em segundos da cena.
set -euo pipefail
cd "$(dirname "$0")"
V=../video-v2/assets/voz
CENAS=(abertura contrato trancada escrever mapear ler influenciar realidade robo fechamento)
taskline set asr-palavras 0 ${#CENAS[@]} --label "palavras por cena" --pid $$
for c in "${CENAS[@]}"; do
  d=/tmp/claude-1002/asr2/$c; mkdir -p $d; cp $V/$c.wav $d/
  systemd-run --user --scope -q -p MemoryMax=4G -p MemorySwapMax=0 npx hyperframes transcribe $d/$c.wav -l pt -m small -d $d > $d/log.txt 2>&1
  cp $d/transcript.json palavras/$c.json
  taskline add asr-palavras
done
taskline done asr-palavras
