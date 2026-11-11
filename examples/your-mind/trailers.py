"""Redoes in English the 3 segments with a fiction trailer (opening 5, contract 1, reality 1).

  python3 trailers.py            # only writes the minimal HyperFrames project in trailers-en/
  python3 trailers.py --render   # writes, renders (global lock + memory cap) and cuts into film/assets/clips_en/<scene>_<i>.mp4

Uses the functions in film/build.py (visual, corner label, CSS, grain and vignette), so the look is the same as v2-mixed,
only with English text and without the 0.45 s crossfade with the previous segment. Each scene lasts exactly as long as
the segment (film/assets/voice/slots.json). Once the .mp4 files are in clips_en, film/assemble_final.py uses them.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.join(HERE, "film")
PROJ = os.path.join(HERE, "trailers-en")
DEST = os.path.join(FILM, "assets/clips_en")
SEGS = [("opening", 5), ("contract", 1), ("reality", 1)]
GAP = 0.5

sys.path.insert(0, FILM)
import build as B
from script import SCENES

SEGMENTS = {c: ss for c, _, ss in SCENES}
TP = json.load(open(os.path.join(FILM, "assets/voice/slots.json")))


def composition(cid, scene, i):
    d = TP[scene][i][1]
    p = f"{scene}-s{i}"
    vis = dict(SEGMENTS[scene][i][2], _t0=0.0, _d=d, _loose=[])
    html, tw = B.VISUALS[vis["visual"]](p, vis)
    label = B.label_html(vis.get("label"))
    parts = vis["_loose"] + [f'<div id="{p}" class="clip" data-start="0" data-duration="{d:.2f}">{html}{label}</div>']
    js = "\n    ".join(x.replace("{t0}", "0").replace("{d}", f"{d:.2f}") for x in tw)
    return d, f"""<template>
  <style>{B.CSS}</style>
  <div id="root" data-composition-id="{cid}" data-width="{B.W}" data-height="{B.H}">
    {chr(10).join(parts)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


def generate():
    os.makedirs(os.path.join(PROJ, "compositions"), exist_ok=True)
    os.makedirs(os.path.join(PROJ, "assets"), exist_ok=True)
    link = os.path.join(PROJ, "assets/trailers")
    if not os.path.exists(link):
        os.symlink(os.path.join(FILM, "assets/trailers"), link)
    for f in ("hyperframes.json", "package.json"):
        open(os.path.join(PROJ, f), "w").write(open(os.path.join(FILM, f)).read())
    json.dump({"id": "trailers-en", "name": "trailers-en"}, open(os.path.join(PROJ, "meta.json"), "w"))
    hosts, start, dur, t = [], {}, {}, 0.0
    for scene, i in SEGS:
        cid = f"{scene}_{i}"
        d, html = composition(cid, scene, i)
        open(os.path.join(PROJ, f"compositions/{cid}.html"), "w").write(html)
        hosts.append(f'<div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{t:.2f}" '
                     f'data-duration="{d:.2f}" data-track-index="1" data-width="{B.W}" data-height="{B.H}"></div>')
        start[cid], dur[cid] = round(t, 2), d
        t += d + GAP
    total = t - GAP
    open(os.path.join(PROJ, "index.html"), "w").write(f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width={B.W}, height={B.H}" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,500;0,700;1,400;1,500&family=IBM+Plex+Mono:wght@400;500;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:{B.W}px;height:{B.H}px;overflow:hidden;background:{B.DARK}}}#root{{width:100%;height:100%;position:relative}}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}" data-width="{B.W}" data-height="{B.H}">
{chr(10).join(hosts)}
{B.grain_vignette(total)}
</div><script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script></body></html>
""")
    json.dump({"start": start, "dur": dur, "total": round(total, 2)}, open(os.path.join(PROJ, "timing.json"), "w"), indent=1)
    print("project in", PROJ, start, f"total {total:.2f} s")
    return start, dur


def render(start, dur):
    out = os.path.join(PROJ, "trailers.mp4")
    cmd = (f'mkdir -p "${{TMPDIR:-/tmp}}/studio" && flock "${{TMPDIR:-/tmp}}/studio/snap.lock" systemd-run --user --scope -q -p MemoryMax=4G -p MemorySwapMax=0 '
           f'bash -c \'cd "{PROJ}" && npx hyperframes@0.8.185 render --fps 30 --quality draft --workers 1 -o trailers.mp4\'')
    subprocess.run(cmd, shell=True, check=True)
    os.makedirs(DEST, exist_ok=True)
    for cid, t0 in start.items():
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t0), "-t", f"{dur[cid]:.3f}", "-i", out, "-an", "-vf", "fps=30",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-g", "15", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                        os.path.join(DEST, f"{cid}.mp4")], check=True)
        print("ok", cid)


if __name__ == "__main__":
    start, dur = generate()
    if "--render" in sys.argv:
        render(start, dur)
