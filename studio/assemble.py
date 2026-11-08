"""Assembles the whole video with ffmpeg: each narration segment becomes a clip of exact duration (in frames), in script order.

  python3 assemble.py                         # renders/v1.mp4
  OUT=v2 VOICE=assets/voice_clean python3 assemble.py

Clip for each segment: assets/clips/<id>.mp4 via assets/clips/map.json (scenes.py render). A segment with no clip becomes a
dark screen and is listed at the end, so the video comes out even when incomplete. Audio: per-scene voices at their times +
assets/music.mp3 (if present) at MUSIC_VOL with fades, loudnorm -14 LUFS in two passes. No Chrome, runs light.
"""
import json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import FF, FPS, MAP_FILE, TMP, script, taskline, timeline

SCENES = script().SCENES
rows, scene_start, TOTAL = timeline()
OUT = os.environ.get("OUT", "v1")
VOICE = os.environ.get("VOICE", "assets/voice")  # assets/voice_clean: voices without stutters/clicks (clean_voice.py)
MUSIC_VOL = float(os.environ.get("MUSIC_VOL", "0.14"))
MAP = json.load(open(MAP_FILE)) if os.path.exists(MAP_FILE) else {}
T = tempfile.mkdtemp(prefix="assemble-", dir=TMP)


def clip_for(scene, i):
    cid = MAP.get(scene, {}).get(str(i))
    return cid if cid and os.path.exists(f"assets/clips/{cid}.mp4") else None


def segment_clip(scene, i, a, b, k):
    n = round(b * FPS) - round(a * FPS)
    out = f"{T}/{k:03d}.mp4"
    cid = clip_for(scene, i)
    src = ["-i", f"assets/clips/{cid}.mp4"] if cid else ["-f", "lavfi", "-i", f"color=c=0x0b0a24:s=1920x1080:r={FPS}"]
    vf = f"fps={FPS},scale=1920:1080:flags=lanczos,tpad=stop_mode=clone:stop_duration=3,format=yuv420p"
    subprocess.run([FF, "-loglevel", "error", "-y", *src, "-vf", vf, "-frames:v", str(n), "-an", "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "17", "-g", "30", "-r", str(FPS), "-pix_fmt", "yuv420p", out], check=True)
    return out, bool(cid)


def mix_audio():
    """Per-scene voices at their times + music with fades, loudnorm -14 LUFS in two passes. Returns the .m4a."""
    ins, filt, labels = [], [], []
    for n, (scene, _, _) in enumerate(SCENES):
        ins += ["-i", f"{VOICE}/{scene}.wav"]
        ms = int(round(scene_start[scene] * 1000))
        filt.append(f"[{n}:a]aresample=48000,adelay={ms}|{ms}[v{n}]")
        labels.append(f"[v{n}]")
    nm = len(SCENES)
    filt.append(f"{''.join(labels)}amix=inputs={nm}:normalize=0:duration=longest[voice]")
    if os.path.exists("assets/music.mp3"):
        ins += ["-i", "assets/music.mp3"]
        filt.append(f"[{nm}:a]aresample=48000,volume={MUSIC_VOL},atrim=0:{TOTAL:.2f},afade=t=in:d=2,afade=t=out:st={max(0, TOTAL - 3):.2f}:d=3[mus]")
        filt.append("[voice][mus]amix=inputs=2:normalize=0:duration=longest[a]")
    else:
        filt[-1] = filt[-1].replace("[voice]", "[a]")
    raw = f"{T}/audio.wav"
    subprocess.run([FF, "-loglevel", "error", "-y", *ins, "-filter_complex", ";".join(filt), "-map", "[a]", raw], check=True)
    r = subprocess.run([FF, "-hide_banner", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    audio = f"{T}/audio.m4a"
    subprocess.run([FF, "-loglevel", "error", "-y", "-i", raw, "-af", ln, "-ar", "48000", "-c:a", "aac", "-b:a", "192k", audio], check=True)
    return audio


def main():
    os.makedirs("renders", exist_ok=True)
    taskline("set", "assemble", 0, len(rows), "--label", "assembling video", "--pid", os.getpid())
    outs = [None] * len(rows)

    def job(k):
        outs[k] = segment_clip(*rows[k], k)
        taskline("add", "assemble")

    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(job, range(len(rows))))
    lst = f"{T}/list.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p, _ in outs))
    video = f"{T}/video.mp4"
    subprocess.run([FF, "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video], check=True)
    final = f"renders/{OUT}.mp4"
    subprocess.run([FF, "-loglevel", "error", "-y", "-i", video, "-i", mix_audio(), "-map", "0:v", "-map", "1:a", "-c", "copy",
                    "-t", f"{TOTAL:.2f}", "-movflags", "+faststart", final], check=True)
    taskline("done", "assemble")
    missing = [f"{c}:{i}" for (c, i, _, _), (_, ok) in zip(rows, outs) if not ok]
    print("done:", final, f"({TOTAL:.1f} s)")
    if missing:
        print(f"{len(missing)} of {len(rows)} segments without a clip (dark screen):", " ".join(missing))


if __name__ == "__main__":
    main()
