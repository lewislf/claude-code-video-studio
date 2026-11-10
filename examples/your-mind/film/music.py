"""Local background track with MusicGen: 8 chunks of ~28 s (two alternating prompts),
joined with crossfades and repeated until it covers the narration. Output: assets/music.mp3
normalized to -16 LUFS."""
import os, subprocess, tempfile
import numpy as np, soundfile as sf, torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

PROMPT = ("dark cinematic ambient underscore for an investigative documentary, low sustained strings, "
          "deep drone, slow tense heartbeat pulse, sparse piano notes, mysterious, minimal, no drums, 70 bpm")
PROMPT2 = ("dark ambient drone for a psychological thriller documentary, eerie synth pads, distant metallic textures, "
           "low cello, unsettling, slow, minimal, no drums, 70 bpm")
N, XF = 8, 3.0  # chunks and crossfade in seconds

target = 1110  # s; covers the narration (~17.5 min) with room to spare. The video cuts it at the end.

proc = AutoProcessor.from_pretrained("facebook/musicgen-small")
m = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small").to("cuda")
sr = m.config.audio_encoder.sampling_rate
chunks = []
for i in range(N):
    torch.manual_seed(42 + i)
    x = proc(text=[PROMPT if i % 2 == 0 else PROMPT2], padding=True, return_tensors="pt").to("cuda")
    a = m.generate(**x, do_sample=True, guidance_scale=3.0, max_new_tokens=1400)  # ~28 s
    chunks.append(a[0, 0].float().cpu().numpy())
    print(f"chunk {i}: {len(chunks[-1])/sr:.1f} s", flush=True)


def splice(a, b):
    k = int(XF * sr)
    r = np.linspace(0, 1, k, dtype=np.float32)
    return np.concatenate([a[:-k], a[-k:] * (1 - r) + b[:k] * r, b[k:]])


base = chunks[0]
for t in chunks[1:]:
    base = splice(base, t)
out = base
while len(out) < target * sr:
    out = splice(out, base)
out = out[: int(target * sr)]
out = out / max(1e-6, np.abs(out).max()) * 0.89  # peak ~ -1 dBFS
wav = os.path.join(tempfile.mkdtemp(), "music.wav")
sf.write(wav, out, sr)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav,
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-b:a", "192k", "assets/music.mp3"], check=True)
print(f"music.mp3: {len(out)/sr:.1f} s")
