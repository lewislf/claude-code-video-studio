"""Redoes only the audio of a finished render (video copied), with the voices from VOICE and the current music.

  VOICE=assets/voice_clean python3 swap_audio.py v1 v2
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as M

src, out = sys.argv[1], sys.argv[2]
subprocess.run([M.FF, "-loglevel", "error", "-y", "-i", f"renders/{src}.mp4", "-i", M.mix_audio(), "-map", "0:v", "-map", "1:a", "-c", "copy",
                "-t", f"{M.TOTAL:.2f}", "-movflags", "+faststart", f"renders/{out}.mp4"], check=True)
print(f"done: renders/{out}.mp4 (voices from {M.VOICE})")
