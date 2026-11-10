"""Per-word times of the English closing narration (for g8), written to scenes/g8_closing2/words/closing.json."""
import json
from faster_whisper import WhisperModel
import soundfile as sf
FILM = "film"
TP = json.load(open(f"{FILM}/assets/voice/slots.json"))
t0 = 0.0
for c, v in TP.items():
    if c == "closing": break
    t0 += v[-1][0] + v[-1][1]
dur = TP["closing"][-1][0] + TP["closing"][-1][1]
x, sr = sf.read("out/tmp/voice.wav", dtype="float32")
sf.write("out/tmp/closing.wav", x[int(t0 * sr): int((t0 + dur) * sr)], sr)
m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=6)
segs, _ = m.transcribe("out/tmp/closing.wav", language="en", word_timestamps=True, beam_size=5)
out = [{"text": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2), "id": f"w{k}"}
       for k, w in enumerate(w for s in segs for w in s.words)]
json.dump(out, open("scenes/g8_closing2/words/closing.json", "w"), indent=1)
i10 = TP["closing"][10][0]
print(len(out), "words;", " ".join(f'{w["text"]}@{w["start"]-i10:.2f}' for w in out if w["start"] >= i10))
