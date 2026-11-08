"""Sentence-by-sentence narration with OmniVoice, keeping the best of N takes.

  python tts.py generate   N takes per sentence (GPU) in .tmp/takes/
  python tts.py pick       transcribes each take (faster-whisper), keeps the one closest to the text with a normal
                           pace; writes assets/voice/<scene>.wav, assets/voice/durations.json and asr-choice.tsv

Run the two steps in separate processes (each fits in 4 GB). Needs the OmniVoice venv.
Language: script.LANG (ISO code, default "en"), used by OmniVoice and by the whisper check.
Voice: script.VOICE = {"ref": wav, "ref_txt": exact transcript of the wav, "speed": 0.85}.
Without VOICE, uses the deep narrator in studio/voices/ (a Portuguese sample; its ref_txt stays Portuguese).
"""
import difflib, json, os, re, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import script, taskline

S = script()
HERE = os.path.dirname(os.path.abspath(__file__))
LANG = getattr(S, "LANG", "en")
VOICE = {"ref": os.path.join(HERE, "voices/deep_narrator.wav"),
         "ref_txt": ("Era uma noite comum, até que o telefone tocou. Do outro lado, ninguém falava. "
                     "Só havia uma respiração... lenta, pesada. A polícia nunca explicou o que aconteceu naquela casa. "
                     "Mas os arquivos revelam algo que ninguém queria que você soubesse."),
         "speed": 0.85} | getattr(S, "VOICE", {})
PRONUNCIATION = getattr(S, "PRONUNCIATION", {})
N, GAP = int(os.environ.get("N", 3)), 0.28  # takes per sentence, silence between sentences (s)
TAKES, OUT = ".tmp/takes", "assets/voice"


def spoken(t):
    for k in sorted(PRONUNCIATION, key=len, reverse=True):
        t = t.replace(k, PRONUNCIATION[k])
    return t


def sentences(text):
    return [f for f in re.split(r"(?<=[.?!:])\s+", text.strip()) if f]


def items():
    for scene, _, segs in S.SCENES:
        for i, (text, _, _) in enumerate(segs):
            for j, f in enumerate(sentences(text)):
                yield scene, i, j, f


def generate():
    import torch
    from omnivoice.models.omnivoice import OmniVoice
    from omnivoice.utils.dtype import tts_dtype_name
    os.makedirs(TAKES, exist_ok=True)
    todo = list(items())
    m = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cuda", dtype=getattr(torch, tts_dtype_name("cuda")))
    taskline("set", "tts", 0, len(todo) * N, "--label", "voice (takes)", "--pid", os.getpid())
    for scene, i, j, f in todo:
        for k in range(N):
            p = f"{TAKES}/{scene}_{i:02d}_{j:02d}_{k}.wav"
            if not os.path.exists(p):  # resumable: takes that already exist are not redone
                torch.manual_seed(7000 + 31 * k + 101 * j + 977 * i)
                a = m.generate(text=spoken(f), language=LANG, ref_audio=VOICE["ref"],
                               ref_text=VOICE["ref_txt"], speed=VOICE["speed"])[0].squeeze().float().cpu().numpy()
                sf.write(p, a, m.sampling_rate)
            taskline("add", "tts")
    taskline("done", "tts")


def norm(t):
    t = re.sub(r"[\W\d_]+", " ", t.lower())
    return " ".join(t.split())


def score(expected, heard, dur):
    """Higher is better: text similarity, fewer repeated words, plausible pace."""
    e, o = norm(expected), norm(heard)
    sim = difflib.SequenceMatcher(None, e, o).ratio()
    words = o.split()
    rep = sum(1 for a, b in zip(words, words[1:]) if a == b)
    wps = len(expected.split()) / max(dur, 0.1)
    pace = 0 if 1.4 <= wps <= 3.4 or len(expected.split()) <= 3 else 0.3
    return sim - 0.15 * rep - pace


def pick():
    from faster_whisper import WhisperModel
    wm = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=6)
    todo = list(items())
    choice, log = {}, []
    taskline("set", "asr", 0, len(todo) * N, "--label", "checking the voice", "--pid", os.getpid())
    for scene, i, j, f in todo:
        best = None
        for k in range(N):
            p = f"{TAKES}/{scene}_{i:02d}_{j:02d}_{k}.wav"
            a, sr = sf.read(p)
            segs, _ = wm.transcribe(p, language=LANG, beam_size=1)
            heard = " ".join(s.text for s in segs)
            n = score(f, heard, len(a) / sr)
            if best is None or n > best[0]:
                best = (n, k, heard)
            taskline("add", "asr")
        choice[(scene, i, j)] = best[1]
        log.append(f"{best[0]:.2f}\t{scene} {i}.{j}\t{f}\t|\t{best[2].strip()}")
    taskline("done", "asr")
    open("asr-choice.tsv", "w").write("\n".join(log))
    os.makedirs(OUT, exist_ok=True)
    dur = {}
    for scene, _, segs in S.SCENES:
        pieces, times, t = [], [], 0.0
        for i, (text, pause, _) in enumerate(segs):
            start, fs = t, sentences(text)
            for j in range(len(fs)):
                a, sr = sf.read(f"{TAKES}/{scene}_{i:02d}_{j:02d}_{choice[(scene, i, j)]}.wav", dtype="float32")
                pieces.append(a)
                t += len(a) / sr
                if j < len(fs) - 1:
                    pieces.append(np.zeros(int(GAP * sr), dtype=np.float32)); t += GAP
            pieces.append(np.zeros(int(pause * sr), dtype=np.float32)); t += pause
            times.append([round(start, 3), round(t - start, 3)])
        sf.write(f"{OUT}/{scene}.wav", np.concatenate(pieces), sr)
        dur[scene] = times
    json.dump(dur, open(f"{OUT}/durations.json", "w"), indent=1)
    tot = sum(v[-1][0] + v[-1][1] for v in dur.values())
    print(f"total: {tot:.1f} s ({tot / 60:.1f} min)\nworst sentences (score, scene, text | heard):\n" + "\n".join(sorted(log)[:8]))


if __name__ == "__main__":
    {"generate": generate, "pick": pick}[sys.argv[1]]()
