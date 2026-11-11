"""Renders the clips of a group and cuts one scene per file into ../film/assets/clips/<id>.mp4.

  python3 assemble.py g2_locked [g4_reading ...]

Global lock (flock) shared with the agents' snapshots, plus a memory cap. Updates ../film/assets/clips/clip_map.json
({scene: {seg: id}}), which the video's build.py reads with --v3.
"""
import importlib.util, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, "../film/assets/clips")
os.makedirs(DEST, exist_ok=True)
FF = os.environ.get("FF", "ffmpeg")
MAP_JSON = os.path.join(DEST, "clip_map.json")


def load(group):
    folder = os.path.join(HERE, group)
    script = [f for f in os.listdir(folder) if f.startswith("build_") and f.endswith(".py")][0]
    sys.path.insert(0, folder); sys.path.insert(0, HERE)
    spec = importlib.util.spec_from_file_location(script[:-3], os.path.join(folder, script))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return folder, m


for group in sys.argv[1:]:
    folder, m = load(group)
    only = [x for x in os.environ.get('ONLY', '').split(',') if x]
    scenes = [c for c in m.SCENES if not only or c[0] in only]
    start, total = m.write_scenes(scenes, folder)
    output = os.path.join(folder, "clips.mp4")
    cmd = (f'mkdir -p "${{TMPDIR:-/tmp}}/studio" && flock "${{TMPDIR:-/tmp}}/studio/snap.lock" systemd-run --user --scope -q -p MemoryMax={os.environ.get("MEMCAP", "3500M")} -p MemorySwapMax=0 '
           f'bash -c \'cd "{folder}" && npx hyperframes@0.8.185 render --fps 30 --quality draft --workers {os.environ.get("WORKERS", "2")} {os.environ.get("RFLAGS", "")} -o clips.mp4\'')
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if not os.path.exists(output):
        print("render FAILED", group, r.stdout[-400:], r.stderr[-400:]); continue
    t = json.load(open(os.path.join(folder, "timing.json")))
    for k, i0 in t["start"].items():
        d = t["dur"][k]
        subprocess.run([FF, "-loglevel", "error", "-y", "-ss", str(i0), "-t", str(d), "-i", output, "-an", "-vf", "fps=30", "-c:v", "libx264",
                        "-preset", "slow", "-crf", "16", "-g", "15", "-pix_fmt", "yuv420p", "-movflags", "+faststart", os.path.join(DEST, f"{k}.mp4")], check=True)
    seg_map = json.load(open(MAP_JSON)) if os.path.exists(MAP_JSON) else {}
    for (scene, seg), clip_id in m.SEG_MAP.items():
        if only and clip_id not in only: continue
        seg_map.setdefault(scene, {})[str(seg)] = clip_id
    json.dump(seg_map, open(MAP_JSON, "w"), indent=1)
    os.remove(output)
    print("ok", group, len(t["start"]), "scenes")
