"""English dub over the released pt-BR video timeline: voice track, mixed audio and .srt (rebuild.sh muxes them).

  python3 dub.py            # needs assets/voice/<scene>.wav + durations.json from studio/tts.py generate/pick
  out/: tmp/audio.m4a, your-mind-en.srt, fit.tsv (segments that had to be sped up)

Each English segment starts where the pt-BR segment i started (film/assets/voice/slots.json, 1x timeline).
If it is longer than the window it is sped up with atempo; above MAX it is reported in fit.tsv to shorten the text.
The last segment (glitch ending) is rebuilt with film/end_glitch.py's effects at the same times as the pt-BR one.
Then: music at 0.14 as in assemble_final.py, 2-pass loudnorm -14 LUFS, atempo 1.35, muxed over the video (copied).
"""
import json, os, re, subprocess, sys
import numpy as np, soundfile as sf

FILM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "film")
sys.path.insert(0, FILM)
import end_glitch as FG  # only defs at import time
import script as S

FF, SPEED, MAX, BREATH, SR = "ffmpeg", 1.35, 1.15, 0.25, 24000
TP = json.load(open(f"{FILM}/assets/voice/slots.json"))
EN = json.load(open("assets/voice/durations.json"))
TMP = "out/tmp"; os.makedirs(TMP, exist_ok=True)


def trim(x, thr=0.01):
    i = np.where(np.abs(x) > thr)[0]
    return x[max(i[0] - int(.02 * SR), 0): i[-1] + int(.06 * SR)] if len(i) else x[:0]


def stretch(x, f):
    if f <= 1.0:
        return x
    i, o = f"{TMP}/s_i.wav", f"{TMP}/s_o.wav"
    sf.write(i, x, SR)
    subprocess.run([FF, "-loglevel", "error", "-y", "-i", i, "-af", f"atempo={f:.4f}", o], check=True)
    return sf.read(o, dtype="float32")[0]


def fit(x, room):
    f = len(x) / SR / room
    return stretch(x, f), f


def glitch(seg_en, base_level):
    """Segment 10 of the pt-BR glitch ending with the English lines in the same slots (T1..REV, T2..LAUGH)."""
    t = json.load(open(f"{FILM}/end_times.json"))
    T1, T2, LAUGH, REV, BLACK, DUR = 0.8, t["line2"], t["laugh"], t["reveal"], t["black"], t["dur"]
    s1, s2 = re.split(r"(?<=[.?!])\s+", S.SCENES[-1][2][-1][0])[:2]
    # split the generated segment at its longest internal silence: line 1 | line 2
    env = np.convolve(np.abs(seg_en) > 0.01, np.ones(int(.05 * SR)), "same") > 0
    d = np.diff(np.r_[1, env.astype(int), 1])
    s, e = np.where(d == -1)[0], np.where(d == 1)[0]  # silent runs [s, e)
    inner = (s > 0) & (e < len(env))
    k = np.argmax((e - s) * inner); a, b = s[k], e[k]
    f1, f2 = trim(seg_en[:a]), trim(seg_en[b:])
    f1, r1 = fit(f1, REV - 0.15 - T1)
    f2, r2 = fit(f2, LAUGH - 0.25 - T2)
    f1, f2 = f1 * 32768, f2 * 32768  # end_glitch works in int16 units
    rms = lambda v: np.sqrt((v[np.abs(v) > 300] ** 2).mean())
    f1 *= base_level / rms(f1)
    f2 = FG.monster(f2); f2 *= base_level / rms(f2)
    rr, orr = FG.trim(FG.read_wav(f"{FILM}/final_takes/laugh_1.wav")[0])  # the laugh is language-free: same as pt-BR
    rr = FG.monster(rr, 1.0, 1.0); rr *= 1.15 * base_level / rms(rr)
    sil = [(a - orr, b - orr) for a, b in [(0.23, 0.57), (0.58, 0.81), (0.9, 1.08), (1.19, 1.31), (1.43, 1.55)]]
    ua, ub = int(sil[-1][0] * SR), int(sil[-1][1] * SR)
    ra = rr[max(ua - int(.03 * SR), 0): ub + int(.08 * SR)].copy()
    pos, tail = sil[-1][1], []
    for k, g in enumerate([0.30, 0.36, 0.44], 1):
        pos += g; tail.append((pos, FG.crush(ra.copy(), 0.15 + 0.22 * k) * 0.72 ** k))
    laugh = np.zeros(int((pos + len(ra) / SR + 0.6) * SR), np.float32); laugh[: len(rr)] += rr
    for p0, c in tail:
        laugh[int(p0 * SR): int(p0 * SR) + len(c)] += c
    echo = laugh.copy()
    for d, gk in ((0.11, 0.32), (0.23, 0.18), (0.37, 0.09)):
        echo[int(d * SR):] += gk * laugh[: len(laugh) - int(d * SR)]
    seg = np.zeros(int(DUR * SR), np.float32)
    for t0, x in ((T1, f1), (T2, f2), (LAUGH, echo)):
        n = min(len(x), len(seg) - int(t0 * SR)); seg[int(t0 * SR): int(t0 * SR) + n] += x[:n]
    for t0, d, a in [(T1 + 0.45 * len(f1) / SR, 0.35, 0.35), (T2 + 0.35 * len(f2) / SR, 0.3, 0.3)]:
        seg = FG.stutter(seg, t0, d, a)
    tt = np.arange(int((BLACK - REV) * SR)) / SR
    seg[int(REV * SR): int(REV * SR) + len(tt)] += (np.sign(np.sin(2 * np.pi * 41 * tt)) * 0.5 + np.sin(2 * np.pi * 82.3 * tt)) * np.minimum(1, tt / 1.5) * 380
    seg[int(REV * SR) - int(.15 * SR): int(REV * SR) + int(.25 * SR)] += FG.rng.normal(0, 2200, int(.4 * SR))
    seg[int(BLACK * SR):] = 0
    for tz in (BLACK + 0.35, BLACK + 0.9):
        seg[int(tz * SR): int((tz + 0.06) * SR)] = FG.rng.normal(0, 2500, int(0.06 * SR))
    cues = [(T1, T1 + len(f1) / SR, s1), (T2, T2 + len(f2) / SR, s2)]
    return seg / 32768, cues, (r1, r2)


# subtitles: numbers as digits (the script spells them out for the voice), max 2 lines of LINE chars
NUM = [("two thousand thirteen", "2013"), ("two thousand twenty-four", "2024"), ("two thousand fifteen", "2015"),
       ("two thousand eighteen", "2018"), ("two thousand six", "2006"), ("two thousand twelve", "2012"),
       ("two thousand fourteen", "2014"), ("two thousand three", "2003"), ("nineteen ninety-nine", "1999"), ("twenty ten", "2010"),
       ("one hundred thirty-nine thousand", "139,000"), ("fifty million", "50 million"), ("thirty-three years", "33 years"),
       ("almost fifty thousand", "almost 50,000"), ("twenty-three-year-old", "23-year-old"), ("two hundred forty-one", "241"),
       ("six hundred eighty-nine thousand", "689,000"), ("sixteen hours", "16 hours")]
LINE = 42


def shown(s):
    for a, b in NUM:
        s = s.replace(a, b).replace(a.capitalize(), b)
    return s


def wrap(s):
    if len(s) <= LINE:
        return s
    w = s.split()
    k = min(range(1, len(w)), key=lambda i: abs(len(" ".join(w[:i])) - len(" ".join(w[i:]))))
    return " ".join(w[:k]) + "\n" + " ".join(w[k:])


def pack(pieces):
    """Greedy: joins pieces while they fit in two lines."""
    out = [""]
    for x in pieces:
        if out[-1] and len(out[-1]) + len(x) + 1 > 2 * LINE:
            out.append("")
        out[-1] = f"{out[-1]} {x}".strip()
    return out


def chunks(s):
    """Splits a long sentence at commas/colons, then at words if a piece still does not fit."""
    return [p for o in pack(re.split(r"(?<=[,:])\s+", s)) for p in (pack(o.split()) if len(o) > 2 * LINE else [o])]


def main():
    total = sum(v[-1][0] + v[-1][1] for v in TP.values())
    track = np.zeros(int((total + 1) * SR), np.float32)
    cues, report, t0 = [], [], 0.0
    for scene, _, segs in S.SCENES:
        wav, sr = sf.read(f"assets/voice/{scene}.wav", dtype="float32")
        assert sr == SR
        for i, (text, _, _) in enumerate(segs):
            a, d = EN[scene][i]
            x = wav[int(a * SR): int((a + d) * SR)]
            start = t0 + TP[scene][i][0]
            if scene == "closing" and i == len(segs) - 1:
                ref = track[int((t0 + TP[scene][5][0]) * SR): int((t0 + TP[scene][7][0]) * SR)] * 32768
                seg, gc, rs = glitch(x, np.sqrt((ref[np.abs(ref) > 300] ** 2).mean()))
                track[int(start * SR): int(start * SR) + len(seg)] += seg
                cues += [(start + p, start + q, s) for p, q, s in gc]
                report += [(f"{rs[0]:.2f}", scene, i, "glitch line 1"), (f"{rs[1]:.2f}", scene, i, "glitch line 2")]
                continue
            x = trim(x)
            room = TP[scene][i][1] - BREATH
            x, f = fit(x, room)
            if f > 1.0:
                report.append((f"{f:.2f}", scene, i, "TOO LONG, shorten" if f > MAX else "sped up"))
            track[int(start * SR): int(start * SR) + len(x)] += x
            # one cue per sentence, split by length (sentences are separated by short silences)
            ss = re.split(r"(?<=[.?!:])\s+", text.strip())
            L, c = len(x) / SR, start
            w = sum(len(s) for s in ss)
            for s in ss:
                d = L * len(s) / w
                cues.append((c, c + d, s)); c += d
        t0 += TP[scene][-1][0] + TP[scene][-1][1]
    open("out/fit.tsv", "w").write("\n".join("\t".join(map(str, r)) for r in sorted(report, reverse=True)))
    print(f"{sum(1 for r in report if float(r[0]) > MAX)} segments above {MAX}x (out/fit.tsv)")
    sf.write(f"{TMP}/voice.wav", track[: int(total * SR)], SR)

    # mix as assemble_final.mix_audio, then 1.35x
    raw = f"{TMP}/mix.wav"
    subprocess.run([FF, "-loglevel", "error", "-y", "-i", f"{TMP}/voice.wav", "-i", f"{FILM}/assets/music.mp3", "-filter_complex",
                    f"[0:a]aresample=48000[v];[1:a]aresample=48000,volume=0.14,atrim=0:{total:.2f},afade=t=in:d=2,afade=t=out:st={total - 3:.2f}:d=3[m];"
                    "[v][m]amix=inputs=2:normalize=0:duration=longest[a]", "-map", "[a]", raw], check=True)
    r = subprocess.run([FF, "-hide_banner", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rindex("{"): r.stderr.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    audio = f"{TMP}/audio.m4a"
    subprocess.run([FF, "-loglevel", "error", "-y", "-i", raw, "-af", f"{ln},atempo={SPEED}", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", audio], check=True)

    def ts(t):
        t = max(t, 0) / SPEED
        return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(t % 1 * 1000):03d}"
    srt = "out/your-mind-en.srt"
    out = []
    for a, b, s in cues:
        s = shown(s)
        parts = chunks(s) if len(s) > 2 * LINE else [s]
        w, c = sum(len(p) for p in parts), a
        for p in parts:
            d = (b - a) * len(p) / w
            out.append((c, c + d, wrap(p))); c += d
    open(srt, "w").write("\n".join(f"{n}\n{ts(a)} --> {ts(b)}\n{s}\n" for n, (a, b, s) in enumerate(out, 1)))
    print("ready: out/tmp/audio.m4a, out/your-mind-en.srt")


if __name__ == "__main__":
    main()
