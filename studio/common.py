"""Shared by every studio script. Every command runs with the project folder as the current directory.

Project = script.py + assets/ + scenes/<group>/build_<group>.py (see template/).
"""
import json, os, shutil, subprocess, sys, tempfile

PROJ = os.getcwd()
sys.path.insert(0, PROJ)
FF = os.environ.get("FF", "ffmpeg")
FPS = 30
TMP = os.path.join(tempfile.gettempdir(), "studio")
os.makedirs(TMP, exist_ok=True)
DUR_FILE = "assets/voice/durations.json"
MAP_FILE = "assets/clips/map.json"  # {scene: {seg: clip_id}}, written by scenes.py render


def script():
    if not os.path.exists("script.py"):
        sys.exit(f"no script.py in {PROJ}: run the commands from inside the project folder")
    import script as S
    return S


def durations():
    if not os.path.exists(DUR_FILE):
        sys.exit(f"missing {DUR_FILE}: run tts.py generate and tts.py pick first")
    return json.load(open(DUR_FILE))


def timeline():
    """(rows, scene_start, total). rows = [(scene, seg, absolute start, absolute end)]."""
    S, TP = script(), durations()
    rows, scene_start, t = [], {}, 0.0
    for scene, _, ss in S.SCENES:
        scene_start[scene] = t
        dur_s = TP[scene][-1][0] + TP[scene][-1][1]
        for i in range(len(ss)):
            b = TP[scene][i + 1][0] if i + 1 < len(ss) else dur_s
            rows.append((scene, i, t + TP[scene][i][0], t + b))
        t += dur_s
    return rows, scene_start, t


def taskline(*args):
    if shutil.which("taskline"):
        subprocess.run(["taskline", *map(str, args)], capture_output=True)
