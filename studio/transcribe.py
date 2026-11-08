"""Timing of every narrated word (whisper small via `npx hyperframes transcribe`).

  python3 transcribe.py [scene ...]     # output: words/<scene>.json, times in seconds within the scene

engine.py uses this to fire animation on a word (`word(scene, seg, "key")`). Language: script.LANG (default "en").
"""
import os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import TMP, script, taskline

S = script()
lang = getattr(S, "LANG", "en")
scenes = sys.argv[1:] or [c for c, _, _ in S.SCENES]
os.makedirs("words", exist_ok=True)
taskline("set", "words", 0, len(scenes), "--label", "words per scene", "--pid", os.getpid())
for c in scenes:
    d = os.path.join(TMP, "asr", c)
    os.makedirs(d, exist_ok=True)
    shutil.copy(f"assets/voice/{c}.wav", d)
    subprocess.run(["systemd-run", "--user", "--scope", "-q", "-p", "MemoryMax=4G", "-p", "MemorySwapMax=0",
                    "npx", "--yes", "hyperframes@0.8.185", "transcribe", f"{d}/{c}.wav", "-l", lang, "-m", "small", "-d", d],
                   check=True, stdout=open(f"{d}/log.txt", "w"), stderr=subprocess.STDOUT)
    shutil.copy(f"{d}/transcript.json", f"words/{c}.json")
    taskline("add", "words")
taskline("done", "words")
