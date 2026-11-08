"""Narração v2, frase por frase, com a melhor de N tentativas.

  python tts.py gerar      gera N tentativas por frase (GPU, OmniVoice) em TAKES/
  python tts.py escolher   transcreve cada tentativa (faster-whisper), fica com a que
                           mais bate com o texto e tem ritmo normal; monta assets/voz/<cena>.wav
                           e assets/voz/duracoes.json

Rodar as duas etapas em processos separados (cabem no teto de 4 GB).
"""
import difflib, json, os, re, sys
import numpy as np, soundfile as sf
from roteiro import CENAS, texto_falado

REF = "../teste-voz/vozes/terror_grave_lento.wav"
REF_TXT = ("Era uma noite comum, até que o telefone tocou. Do outro lado, ninguém falava. "
           "Só havia uma respiração... lenta, pesada. A polícia nunca explicou o que aconteceu naquela casa. "
           "Mas os arquivos revelam algo que ninguém queria que você soubesse.")
SPEED, N, GAP = 0.85, 3, 0.28   # velocidade, tentativas por frase, silêncio entre frases (s)
TAKES = "/tmp/claude-1002/takes-v2"
OUT = "assets/voz"


def frases(texto):
    return [f for f in re.split(r"(?<=[.?!:])\s+", texto.strip()) if f]


def itens():
    for cena, _, segs in CENAS:
        for i, (texto, pausa, _) in enumerate(segs):
            for j, f in enumerate(frases(texto)):
                yield cena, i, j, f


def gerar():
    import torch
    from omnivoice.models.omnivoice import OmniVoice
    from omnivoice.utils.dtype import tts_dtype_name
    from taskline import Progress
    os.makedirs(TAKES, exist_ok=True)
    lista = list(itens())
    m = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cuda", dtype=getattr(torch, tts_dtype_name("cuda")))
    with Progress("tts-v2", total=len(lista) * N, label="voz v2 (tentativas)") as prog:
        for cena, i, j, f in lista:
            for k in range(N):
                p = f"{TAKES}/{cena}_{i:02d}_{j:02d}_{k}.wav"
                if not os.path.exists(p):
                    torch.manual_seed(7000 + 31 * k + 101 * j + 977 * i)
                    a = m.generate(text=texto_falado(f), language="Portuguese", ref_audio=REF,
                                   ref_text=REF_TXT, speed=SPEED)[0].squeeze().float().cpu().numpy()
                    sf.write(p, a, m.sampling_rate)
                prog.advance()


def norm(t):
    t = t.lower()
    t = re.sub(r"[^a-záàâãéêíóôõúç ]", " ", t)
    return " ".join(t.split())


def nota(esperado, ouvido, dur):
    """Maior é melhor: semelhança do texto, menos palavras repetidas, ritmo plausível."""
    e, o = norm(esperado), norm(ouvido)
    sim = difflib.SequenceMatcher(None, e, o).ratio()
    pal = o.split()
    rep = sum(1 for a, b in zip(pal, pal[1:]) if a == b)
    wps = len(esperado.split()) / max(dur, 0.1)
    ritmo = 0 if 1.4 <= wps <= 3.4 or len(esperado.split()) <= 3 else 0.3
    return sim - 0.15 * rep - ritmo


def escolher():
    from faster_whisper import WhisperModel
    from taskline import Progress
    wm = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=6)  # a GPU não tem libcublas 12
    lista = list(itens())
    escolha, log = {}, []
    with Progress("asr-v2", total=len(lista) * N, label="conferindo a voz") as prog:
        for cena, i, j, f in lista:
            melhor = None
            for k in range(N):
                p = f"{TAKES}/{cena}_{i:02d}_{j:02d}_{k}.wav"
                a, sr = sf.read(p)
                segs, _ = wm.transcribe(p, language="pt", beam_size=1)
                ouvido = " ".join(s.text for s in segs)
                n = nota(f, ouvido, len(a) / sr)
                if melhor is None or n > melhor[0]:
                    melhor = (n, k, ouvido)
                prog.advance()
            escolha[(cena, i, j)] = melhor[1]
            log.append(f"{melhor[0]:.2f}\t{cena} {i}.{j}\t{f}\t|\t{melhor[2].strip()}")
    open("asr-escolha.tsv", "w").write("\n".join(log))
    os.makedirs(OUT, exist_ok=True)
    dur = {}
    for cena, _, segs in CENAS:
        pedacos, tempos, t = [], [], 0.0
        for i, (texto, pausa, _) in enumerate(segs):
            ini = t
            fs = frases(texto)
            for j, _f in enumerate(fs):
                a, sr = sf.read(f"{TAKES}/{cena}_{i:02d}_{j:02d}_{escolha[(cena, i, j)]}.wav", dtype="float32")
                pedacos.append(a)
                t += len(a) / sr
                if j < len(fs) - 1:
                    pedacos.append(np.zeros(int(GAP * sr), dtype=np.float32)); t += GAP
            pedacos.append(np.zeros(int(pausa * sr), dtype=np.float32)); t += pausa
            tempos.append([round(ini, 3), round(t - ini, 3)])
        sf.write(f"{OUT}/{cena}.wav", np.concatenate(pedacos), sr)
        dur[cena] = tempos
    json.dump(dur, open(f"{OUT}/duracoes.json", "w"), indent=1)
    tot = sum(v[-1][0] + v[-1][1] for v in dur.values())
    piores = sorted(log)[:8]
    print(f"total: {tot:.1f} s ({tot/60:.1f} min)\npiores frases (nota, cena, texto | ouvido):\n" + "\n".join(piores))


if __name__ == "__main__":
    {"gerar": gerar, "escolher": escolher}[sys.argv[1]]()
