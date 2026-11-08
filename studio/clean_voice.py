"""Writes assets/voice_clean/<scene>.wav from assets/voice/ without changing any duration.

  python3 clean_voice.py cuts.json

cuts.json: {"scene": {"mute": [[t0, t1], ...], "clicks": [t, ...]}} in seconds local to the scene.
Mute zeroes the stretch with a 12 ms fade at the edges (the rest of the speech stays in place, sync does not change).
Click: linear interpolation over 3 ms around the jump.
"""
import json, os, shutil, sys, wave
import numpy as np

FADE = 0.012


def clean(scene, mute=(), clicks=()):
    w = wave.open(f"assets/voice/{scene}.wav")
    p, sr = w.getparams(), w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)
    nf = int(FADE * sr)
    for t0, t1 in mute:
        a, b = int(t0 * sr), int(t1 * sr)
        x[a:b] = 0
        x[max(a - nf, 0):a] *= np.linspace(1, 0, a - max(a - nf, 0))
        x[b:b + nf] *= np.linspace(0, 1, len(x[b:b + nf]))
    for t in clicks:
        c, r = int(t * sr), int(0.0015 * sr)
        a, b = max(c - r, 0), min(c + r, len(x) - 1)
        x[a:b] = np.linspace(x[a], x[b], b - a)
    o = wave.open(f"assets/voice_clean/{scene}.wav", "wb")
    o.setparams(p)
    o.writeframes(np.clip(x, -32768, 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    os.makedirs("assets/voice_clean", exist_ok=True)
    cuts = json.load(open(sys.argv[1]))
    for f in os.listdir("assets/voice"):  # scenes without cuts are copied as is, so VOICE=assets/voice_clean has every scene
        if f.endswith(".wav") and f[:-4] not in cuts:
            shutil.copy(f"assets/voice/{f}", "assets/voice_clean/")
    for scene, c in cuts.items():
        clean(scene, c.get("mute", []), c.get("clicks", []))
        print(scene, len(c.get("mute", [])), "stretches,", len(c.get("clicks", [])), "clicks")
    assert all(wave.open(f"assets/voice_clean/{c}.wav").getnframes() == wave.open(f"assets/voice/{c}.wav").getnframes() for c in cuts)
