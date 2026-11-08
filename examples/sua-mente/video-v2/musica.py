"""Trilha de fundo local com MusicGen: 8 trechos de ~28 s (dois prompts alternados),
emendados com crossfade e repetidos até cobrir a narração. Saída: assets/musica.mp3
normalizada em -16 LUFS."""
import json, subprocess
import numpy as np, soundfile as sf, torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

PROMPT = ("dark cinematic ambient underscore for an investigative documentary, low sustained strings, "
          "deep drone, slow tense heartbeat pulse, sparse piano notes, mysterious, minimal, no drums, 70 bpm")
PROMPT2 = ("dark ambient drone for a psychological thriller documentary, eerie synth pads, distant metallic textures, "
           "low cello, unsettling, slow, minimal, no drums, 70 bpm")
N, XF = 8, 3.0  # trechos e crossfade em segundos

alvo = 1110  # s; cobre a narração (~17,5 min) com folga. O index.html corta no fim do vídeo.

proc = AutoProcessor.from_pretrained("facebook/musicgen-small")
m = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small").to("cuda")
sr = m.config.audio_encoder.sampling_rate
trechos = []
for i in range(N):
    torch.manual_seed(42 + i)
    x = proc(text=[PROMPT if i % 2 == 0 else PROMPT2], padding=True, return_tensors="pt").to("cuda")
    a = m.generate(**x, do_sample=True, guidance_scale=3.0, max_new_tokens=1400)  # ~28 s
    trechos.append(a[0, 0].float().cpu().numpy())
    print(f"trecho {i}: {len(trechos[-1])/sr:.1f} s", flush=True)


def emenda(a, b):
    k = int(XF * sr)
    r = np.linspace(0, 1, k, dtype=np.float32)
    return np.concatenate([a[:-k], a[-k:] * (1 - r) + b[:k] * r, b[k:]])


base = trechos[0]
for t in trechos[1:]:
    base = emenda(base, t)
out = base
while len(out) < alvo * sr:
    out = emenda(out, base)
out = out[: int(alvo * sr)]
out = out / max(1e-6, np.abs(out).max()) * 0.89  # pico ~ -1 dBFS
sf.write("/tmp/claude-1002/musica.wav", out, sr)
subprocess.run(["/home/linuxbrew/.linuxbrew/bin/ffmpeg", "-loglevel", "error", "-y", "-i", "/tmp/claude-1002/musica.wav",
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-b:a", "192k", "assets/musica.mp3"], check=True)
print(f"musica.mp3: {len(out)/sr:.1f} s")
