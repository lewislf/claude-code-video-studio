"""Assembles the full video straight with ffmpeg: each segment becomes a clip of exact length (in frames), in narration order.

  OUT=en-1x python3 assemble_final.py     # output: renders/<OUT>.mp4 (+ 720p)

Replaced segments (build.py::SUBST + assets/clips/clip_map.json) come from the clips in assets/clips/. The rest
(fiction trailers) are cut from the old render renders/v2-mixed.mp4. Audio: per-scene voices at their times,
music at 0.14 with fades, loudnorm -14 LUFS. No Chrome, so it runs light (no 5 GB cap like the HyperFrames render).
"""
import json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import build as B
from script import SCENES

FF = "ffmpeg"
FPS = 30
TP = json.load(open("assets/voice/slots.json"))
OLD = "renders/v2-mixed.mp4"
OUT = os.environ.get("OUT", "v6-misto")
TMP = tempfile.mkdtemp(prefix="assemble-")
VOICE = os.environ.get("VOICE", "assets/voice")  # assets/voice_limpa: voices without stutter/clicks

# timeline: (scene, i, absolute start, absolute end)
rows, scene_start, t = [], {}, 0.0
for scene, _, ss in SCENES:
    scene_start[scene] = t
    dur_c = TP[scene][-1][0] + TP[scene][-1][1]
    for i in range(len(ss)):
        a = t + TP[scene][i][0]
        b = t + (TP[scene][i + 1][0] if i + 1 < len(ss) else dur_c)
        rows.append((scene, i, a, b))
    t += dur_c
TOTAL = t


def scene_clip(scene, i, a, b, k):
    n = round(b * FPS) - round(a * FPS)
    out = f"{TMP}/{k:03d}.mp4"
    sub = B.SUBST.get((scene, i))
    if sub:
        src, ss = f"assets/clips/{sub['clip']}.mp4", sub["ms"]
    else:
        src, ss = OLD, a
    vf = f"fps={FPS},scale=1920:1080:flags=lanczos,tpad=stop_mode=clone:stop_duration=3,format=yuv420p"
    subprocess.run([FF, "-loglevel", "error", "-y", "-ss", f"{ss:.3f}", "-i", src, "-vf", vf, "-frames:v", str(n), "-an", "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "17", "-g", "30", "-r", str(FPS), "-pix_fmt", "yuv420p", out], check=True)
    return out, bool(sub)


def mix_audio():
    """Per-scene voices at their times + music at 0.14 with fades, 2-pass loudnorm -14 LUFS. Returns the .m4a."""
    ins, filt, labels = [], [], []
    for n, (scene, _, _) in enumerate(SCENES):
        ins += ["-i", f"{VOICE}/{scene}.wav"]
        ms = int(round(scene_start[scene] * 1000))
        filt.append(f"[{n}:a]aresample=48000,adelay={ms}|{ms}[v{n}]")
        labels.append(f"[v{n}]")
    nm = len(SCENES)
    ins += ["-i", "assets/music.mp3"]
    filt.append(f"{''.join(labels)}amix=inputs={nm}:normalize=0:duration=longest[voice]")
    filt.append(f"[{nm}:a]aresample=48000,volume=0.14,atrim=0:{TOTAL:.2f},afade=t=in:d=2,afade=t=out:st={TOTAL - 3:.2f}:d=3[mus]")
    filt.append("[voice][mus]amix=inputs=2:normalize=0:duration=longest[a]")
    raw = f"{TMP}/audio.wav"
    subprocess.run([FF, "-loglevel", "error", "-y", *ins, "-filter_complex", ";".join(filt), "-map", "[a]", raw], check=True)
    # 2-pass loudnorm (1-pass ended at -15.5 LUFS)
    r = subprocess.run([FF, "-hide_banner", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    audio = f"{TMP}/audio.m4a"
    subprocess.run([FF, "-loglevel", "error", "-y", "-i", raw, "-af", ln, "-ar", "48000", "-c:a", "aac", "-b:a", "192k", audio], check=True)
    return audio


def main():
    try:
        subprocess.run(["taskline", "set", "assemble-final", "0", str(len(rows)), "--label", "assemble video", "--pid", str(os.getpid())])
    except Exception:
        pass
    outs = [None] * len(rows)

    def work(k):
        c, i, a, b = rows[k]
        outs[k] = scene_clip(c, i, a, b, k)
        subprocess.run(["taskline", "add", "assemble-final"])

    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(work, range(len(rows))))
    new = sum(1 for _, n in outs if n)
    print(f"{new} of {len(rows)} segments are new scenes; the rest comes from the old render")
    concat = f"{TMP}/list.txt"
    open(concat, "w").write("".join(f"file '{p}'\n" for p, _ in outs))
    video = f"{TMP}/video.mp4"
    subprocess.run([FF, "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", video], check=True)
    audio = mix_audio()
    final = f"renders/{OUT}.mp4"
    subprocess.run([FF, "-loglevel", "error", "-y", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a", "-c", "copy", "-t", f"{TOTAL:.2f}", "-movflags", "+faststart", final], check=True)
    subprocess.run([FF, "-loglevel", "error", "-y", "-i", final, "-vf", "scale=-2:720", "-c:v", "libx264", "-preset", "medium", "-crf", "30", "-maxrate", "1500k",
                    "-bufsize", "3000k", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", f"renders/{OUT}-720p.mp4"], check=True)
    subprocess.run(["taskline", "done", "assemble-final"])
    print("ready:", final, f"({TOTAL:.1f} s)")


if __name__ == "__main__":
    main()
