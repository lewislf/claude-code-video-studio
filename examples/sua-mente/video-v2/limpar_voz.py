"""Gera assets/voz_limpa/<cena>.wav a partir de assets/voz/ sem mudar a duração de nada.

  python3 limpar_voz.py cortes.json

cortes.json: {"cena": {"silenciar": [[t0, t1], ...], "cliques": [t, ...]}} em segundos locais da cena.
Silenciar zera o trecho com fade de 12 ms nas bordas (o resto da fala fica no mesmo lugar, a sincronia não muda).
Clique: interpola linearmente 3 ms em volta do salto.
"""
import json, os, shutil, sys, wave
import numpy as np

FADE = 0.012


def limpar(cena, silenciar=(), cliques=()):
    w = wave.open(f"assets/voz/{cena}.wav")
    p, sr = w.getparams(), w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)
    nf = int(FADE * sr)
    for t0, t1 in silenciar:
        a, b = int(t0 * sr), int(t1 * sr)
        x[a:b] = 0
        x[max(a - nf, 0):a] *= np.linspace(1, 0, a - max(a - nf, 0))
        x[b:b + nf] *= np.linspace(0, 1, len(x[b:b + nf]))
    for t in cliques:
        c, r = int(t * sr), int(0.0015 * sr)
        a, b = max(c - r, 0), min(c + r, len(x) - 1)
        x[a:b] = np.linspace(x[a], x[b], b - a)
    o = wave.open(f"assets/voz_limpa/{cena}.wav", "wb")
    o.setparams(p)
    o.writeframes(np.clip(x, -32768, 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    os.makedirs("assets/voz_limpa", exist_ok=True)
    cortes = json.load(open(sys.argv[1]))
    for f in os.listdir("assets/voz"):  # o que não tem corte vai igual, para VOZ=assets/voz_limpa ter todas as cenas
        if f.endswith(".wav") and f[:-4] not in cortes:
            shutil.copy(f"assets/voz/{f}", "assets/voz_limpa/")
    for cena, c in cortes.items():
        limpar(cena, c.get("silenciar", []), c.get("cliques", []))
        print(cena, len(c.get("silenciar", [])), "trechos,", len(c.get("cliques", [])), "cliques")
    assert all(wave.open(f"assets/voz_limpa/{c}.wav").getnframes() == wave.open(f"assets/voz/{c}.wav").getnframes() for c in cortes)
