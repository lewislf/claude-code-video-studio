"""Compares the actual speech (words/<scene>.json, from transcribe.py) with the script and lists what is extra in the audio:
repetitions and added stretches.

  python3 find_stutters.py [scene ...]

Output: one line per suspect, with the time in the final video (scene start + local time).
"""
import difflib, json, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import script, timeline

norm = lambda w: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", w.lower()).encode("ascii", "ignore").decode())
TXT = {c: " ".join(t for t, _, _ in ss) for c, _, ss in script().SCENES}


def suspects(scene):
    ref = [norm(w) for w in TXT[scene].split() if norm(w)]
    ws = json.load(open(f"words/{scene}.json"))
    hyp = [norm(w["text"]) for w in ws]
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_opcodes():
        if op in ("insert", "replace") and j2 > j1:
            rep = any(hyp[j] and (hyp[j] == hyp[j - 1] or hyp[j - 1].startswith(hyp[j]) or hyp[j].startswith(hyp[j - 1]))
                      for j in range(max(j1, 1), j2 + 1) if j < len(hyp))
            if op == "insert" or rep:
                out.append((ws[j1]["start"], ws[j2 - 1]["end"], "REPEAT" if rep else "EXTRA",
                            " ".join(w["text"] for w in ws[j1:j2]), " ".join(ref[i1:i2])))
    return sorted(out)


if __name__ == "__main__":
    _, start, _ = timeline()
    for scene in sys.argv[1:] or list(TXT):
        if not os.path.exists(f"words/{scene}.json"):
            continue
        for a, b, kind, extra, exp in suspects(scene):
            t = start[scene] + a
            print(f"{int(t // 60):02d}:{t % 60:05.2f}  {scene:<11} {a:6.2f}-{b:6.2f}  {kind:<7} '{extra}'  (script: {exp})")
