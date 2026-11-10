#!/usr/bin/env bash
# After tts.py generate/pick: fits the voice, redoes g8 (depends on per-word times) and reassembles the video.
#   PY=<python with faster-whisper, soundfile> ./rebuild.sh
set -euo pipefail
cd "$(dirname "$0")"
FF=ffmpeg
PY=${PY:-python3}
CAP="systemd-run --user --scope -q -p MemoryMax=4G -p MemorySwapMax=0"
R=film/renders
taskline set rebuild-en 0 7 --label "rebuild EN" --pid $$

$CAP $PY dub.py; taskline add rebuild-en
$CAP $PY word_times.py 2>&1 | grep -v Warn | tail -1
python3 - <<'EOF'  # "But" at the exact moment line 2 of the ending was placed (Whisper misses it on the processed audio)
import json
p = "scenes/g8_closing2/words/closing.json"; d = json.load(open(p))
i10 = json.load(open("film/assets/voice/slots.json"))["closing"][10][0]
t2 = json.load(open("film/end_times.json"))["line2"]
for w in d:
    if w["start"] >= i10 and w["text"].lower().startswith("but"):
        w["start"] = round(i10 + t2, 2); break
json.dump(d, open(p, "w"), indent=1)
w = {x["text"].lower().strip(".,?!"): round(x["start"] - i10, 2) for x in d if x["start"] >= i10}
print("final:", {k: w.get(k) for k in ("glitches", "but", "problem", "model", "or", "failing")})
json.dump(w, open("out/tmp/final_words.json", "w"))
EOF
taskline add rebuild-en

touch .start  # render_all skips clips newer than this mark; g8 has to be redone
./render_all.sh g8 | tail -3; taskline add rebuild-en

# visual glitch of the ending on the English words (bursts as t0:duration:strength, see film/glitch.py)
RAW=$(mktemp --suffix=.mp4)
cp film/assets/clips/closing_10.mp4 "$RAW"
ARGS=$(python3 -c "
import json; w=json.load(open('out/tmp/final_words.json')); t=json.load(open('film/end_times.json'))
g=lambda k,d: w.get(k, d)
bursts=[(0.25,0.3,0.5),(g('glitches',2.2),0.35,0.35),(t['reveal']-0.15,0.4,0.95),(g('model',6.0),0.45,0.5),(g('failing',8.4),0.39,0.9)]
print(t['dur'], ','.join(f'{a}:{b}:{c}' for a,b,c in bursts), g('failing',8.4), t['black'])")
(cd film && python3 glitch.py $ARGS assets/clips/closing_10.mp4 "$RAW"); taskline add rebuild-en

(cd film && OUT=en-1x $CAP python3 assemble_final.py | tail -1); taskline add rebuild-en
$CAP $FF -loglevel error -y -i $R/en-1x.mp4 -an -vf "setpts=PTS/1.35,fps=30" -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p $R/en-135-mute.mp4
$FF -loglevel error -y -i $R/en-135-mute.mp4 -i out/tmp/audio.m4a -map 0:v -map 1:a -c copy -shortest $R/en-135.mp4
(cd film && ./progress_bar.sh en-135 en-135-bar >/dev/null 2>&1); taskline add rebuild-en
$FF -loglevel error -y -i $R/en-135-bar.mp4 -i out/your-mind-en.srt -map 0:v -map 0:a -map 1:s -c:v copy -c:a copy -c:s mov_text \
  -metadata:s:a:0 language=eng -metadata:s:s:0 language=eng -movflags +faststart out/your-mind-en-1080p.mp4
$FF -loglevel error -y -i out/your-mind-en-1080p.mp4 -map 0:v -map 0:a -map 0:s -vf scale=-2:720 -c:v libx264 -preset medium -crf 32 \
  -maxrate 220k -bufsize 440k -c:a aac -b:a 64k -c:s mov_text -movflags +faststart out/your-mind-en-phone.mp4
taskline done rebuild-en
ls -la out/your-mind-en-*.mp4
