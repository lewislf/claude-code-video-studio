"""Finds abrupt joins in the voice (digital silence glued to loud sound within a few ms) and sample jumps.

  python3 find_clicks.py [scene ...]        # VOICE=assets/voice by default

The voice is assembled per sentence with exact silence between them; where a sentence starts or ends without a fade there is a click.
Output: time in the video, scene, local time, kind. The local times go into clean_voice.py's cuts.json.
"""
import os, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import script, timeline


def read(scene):
    w = wave.open(f"{os.environ.get('VOICE', 'assets/voice')}/{scene}.wav")
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return x, w.getframerate()


def suspects(x, sr):
    out = []
    j = int(sr * 0.004)  # 4 ms window
    n = len(x) // j
    db = 20 * np.log10(np.sqrt((x[: n * j].reshape(n, j) ** 2).mean(1) + 1e-12))
    for k in range(1, n):
        if db[k - 1] < -80 and db[k] > -30:
            out.append((k * j / sr, "HARD IN", db[k]))
        if db[k - 1] > -30 and db[k] < -80:
            out.append((k * j / sr, "HARD OUT", db[k - 1]))
    d = np.abs(np.diff(x))
    for i in np.where(d > 0.5)[0]:  # half-scale jump between two samples: click
        out.append((i / sr, "CLICK", 20 * np.log10(d[i])))
    return out


if __name__ == "__main__":
    _, start, _ = timeline()
    for scene in sys.argv[1:] or [c for c, _, _ in script().SCENES]:
        for t, kind, v in suspects(*read(scene)):
            tv = start[scene] + t
            print(f"{int(tv // 60):02d}:{tv % 60:05.2f}  {scene:<11} {t:7.2f}  {kind:<10} {v:6.1f} dB")
