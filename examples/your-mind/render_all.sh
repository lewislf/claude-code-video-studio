#!/usr/bin/env bash
# Renders the English scenes and cuts them into film/assets/clips/. g8 is left out: it depends on the word times.
#   ./render_all.sh            # everything but g8
#   ./render_all.sh g8         # only g8
# One render at a time (flock), memory cap, batches of 3 scenes. Resumable: a batch whose clips are newer than .start is skipped.
set -uo pipefail
cd "$(dirname "$0")"
FF=ffmpeg
DEST=$PWD/film/assets/clips
[ -f .start ] || touch .start
CAP="systemd-run --user --scope -q -p MemoryMax=4000M -p MemorySwapMax=0"

group_ids() { python3 - "$1" <<'EOF'
import importlib.util, os, sys
g = sys.argv[1]; sys.path[:0] = [g, "scenes"]
f = [x for x in os.listdir(g) if x.startswith("build_") and x.endswith(".py")][0]
s = importlib.util.spec_from_file_location("m", f"{g}/{f}"); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
print(" ".join(c[0] for c in m.SCENES))
EOF
}

batches=()
if [ "${1:-}" = g8 ]; then groups=(scenes/g8_closing2); else groups=(scenes/g[1-7]_*); fi
for g in "${groups[@]}"; do
  ids=($(group_ids "$g")); n=${#ids[@]}
  for ((k=0; k<n; k+=3)); do batches+=("$g|$(IFS=,; echo "${ids[*]:k:3}")"); done
done
extra=0; [ "${1:-}" = g8 ] || extra=4
taskline set render-en 0 $(( ${#batches[@]} + extra )) --label "render EN scenes" --pid $$

for l in "${batches[@]}"; do
  g=${l%%|*}; so=${l#*|}
  fresh=1; for id in ${so//,/ }; do [ "$DEST/$id.mp4" -nt .start ] || fresh=0; done
  if [ $fresh = 0 ]; then
    echo "== $g $so"
    (cd scenes && ONLY=$so WORKERS=2 MEMCAP=4000M python3 assemble.py "$(basename "$g")") || echo "FAILED $g $so"
  fi
  taskline add render-en
done
[ "${1:-}" = g8 ] && { taskline done render-en; exit 0; }

render() {  # dir output
  [ -f "$1/$2" ] && [ "$1/$2" -nt .start ] && return 0
  mkdir -p "${TMPDIR:-/tmp}/studio"; flock "${TMPDIR:-/tmp}/studio/snap.lock" $CAP bash -c "cd '$1' && npx hyperframes render --fps 30 --quality draft --workers 2 -o '$2'" >/dev/null 2>&1
  [ -f "$1/$2" ] || { echo "FAILED render $1"; return 1; }
}
cut() {  # input start dur id
  $FF -loglevel error -y -ss "$2" -t "$3" -i "$1" -an -vf fps=30 -c:v libx264 -preset slow -crf 16 -g 15 -pix_fmt yuv420p -movflags +faststart "$DEST/$4.mp4"
}

echo "== scenes-v3"; (cd scenes-v3 && python3 build3.py >/dev/null)
if render scenes-v3 clips-en.mp4; then
  for c in "A 0 30.14" "B 30.64 10.67" "D 41.81 15.42" "E 57.73 15.15" "F 73.38 8.22" "C 82.10 27.53"; do set -- $c; cut scenes-v3/clips-en.mp4 $2 $3 $1; done
fi; taskline add render-en
echo "== scenes-v4"; (cd scenes-v4 && python3 build4.py >/dev/null)
if render scenes-v4 clips-en.mp4; then
  for c in "M2 0 8.3" "M3 8.8 5.61" "M4 14.91 15.22" "M5 30.63 12.05" "M6 43.18 10.86" "M7 54.54 11.96" "M8 67.0 9.72"; do set -- $c; cut scenes-v4/clips-en.mp4 $2 $3 $1; done
fi; taskline add render-en
echo "== m1"; render scene-m1 clips-en.mp4 && cut scene-m1/clips-en.mp4 0 13.6 M1; taskline add render-en
echo "== trailers"; python3 trailers.py --render || echo "FAILED trailers"; taskline add render-en
taskline done render-en
echo done
