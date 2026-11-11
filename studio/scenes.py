"""Builds and renders the project's scene groups (scenes/<group>/build_<group>.py).

  python3 scenes.py build g1 [g2 ...]     # writes the group's compositions/ and index.html (fast, no Chrome)
  python3 scenes.py render g1 [g2 ...]    # renders the group and cuts one clip per scene into assets/clips/<id>.mp4

Variables: ONLY=id1,id2 (just those scenes), WORKERS=2, MEMCAP=3500M, RFLAGS="--browser-gpu".
The group build defines SCENES = [(id, function, dur)] and MAP = {(scene, seg): id}; render merges MAP into assets/clips/map.json,
which assemble.py reads. One render at a time on the machine (same lock as snap.sh).
"""
import importlib.util, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import FF, MAP_FILE, TMP

HF = {"paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}, "media": {"autoProxy": True}}
PKG = {"name": "scenes", "private": True, "type": "module", "scripts": {"check": "npx --yes hyperframes@0.8.185 check"}}


def load(group):
    folder = os.path.abspath(os.path.join("scenes", group))
    f = next(f for f in os.listdir(folder) if f.startswith("build_") and f.endswith(".py"))
    for name, data in (("hyperframes.json", HF), ("package.json", PKG)):
        if not os.path.exists(os.path.join(folder, name)):
            json.dump(data, open(os.path.join(folder, name), "w"), indent=2)
    sys.path.insert(0, folder)
    spec = importlib.util.spec_from_file_location(f[:-3], os.path.join(folder, f))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return folder, m


def build(group):
    folder, m = load(group)
    only = [x for x in os.environ.get("ONLY", "").split(",") if x]
    scenes = [c for c in m.SCENES if not only or c[0] in only]
    from engine import write_scenes
    write_scenes(scenes, folder)
    print("ok", group, len(scenes), "scenes in", folder)
    return folder, m, only


def render(group):
    folder, m, only = build(group)
    dest = os.path.dirname(MAP_FILE)
    os.makedirs(dest, exist_ok=True)
    out = os.path.join(folder, "clips.mp4")
    cmd = (f'flock {TMP}/snap.lock systemd-run --user --scope -q -p MemoryMax={os.environ.get("MEMCAP", "3500M")} -p MemorySwapMax=0 '
           f'bash -c \'cd "{folder}" && npx --yes hyperframes@0.8.185 render --fps 30 --quality draft '
           f'--workers {os.environ.get("WORKERS", "2")} {os.environ.get("RFLAGS", "")} -o clips.mp4\'')
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if not os.path.exists(out):
        sys.exit(f"render FAILED {group}\n{r.stdout[-600:]}\n{r.stderr[-600:]}")
    t = json.load(open(os.path.join(folder, "timings.json")))
    for k, i0 in t["start"].items():
        subprocess.run([FF, "-loglevel", "error", "-y", "-ss", str(i0), "-t", str(t["dur"][k]), "-i", out, "-an", "-vf", "fps=30",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-g", "15", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                        os.path.join(dest, f"{k}.mp4")], check=True)
    clip_map = json.load(open(MAP_FILE)) if os.path.exists(MAP_FILE) else {}
    for (scene, sg), cid in m.MAP.items():
        if not only or cid in only:
            clip_map.setdefault(scene, {})[str(sg)] = cid
    json.dump(clip_map, open(MAP_FILE, "w"), indent=1)
    os.remove(out)
    print("ok", group, len(t["start"]), "clips in", dest)


if __name__ == "__main__":
    action, groups = sys.argv[1], sys.argv[2:]
    for g in groups:
        {"build": build, "render": render}[action](g)
