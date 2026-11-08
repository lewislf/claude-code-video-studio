"""Acha emendas bruscas na voz (silêncio digital -> som alto, ou som alto -> silêncio, em poucos ms) e saltos de amostra.

  python3 achar_estalos.py [cena ...]

A voz sintética é montada por frase com silêncio exato entre elas; onde a frase começa ou termina sem fade sai um estalo.
"""
import os, sys, wave
import numpy as np

CENAS = sys.argv[1:]  # antes do import: montar_final troca sys.argv
sys.path.insert(0, ".")
import montar_final as M  # noqa: E402


def ler(cena):
    w = wave.open(f"{os.environ.get('VOZ', 'assets/voz')}/{cena}.wav")
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return x, w.getframerate()


def suspeitas(x, sr):
    out = []
    j = int(sr * 0.004)  # janela de 4 ms
    n = len(x) // j
    rms = np.sqrt((x[: n * j].reshape(n, j) ** 2).mean(1) + 1e-12)
    db = 20 * np.log10(rms)
    for k in range(1, n):
        # silêncio absoluto colado em som acima de -30 dB: corte seco
        if db[k - 1] < -80 and db[k] > -30:
            out.append((k * j / sr, "ENTRA SECO", db[k]))
        if db[k - 1] > -30 and db[k] < -80:
            out.append((k * j / sr, "SAI SECO", db[k - 1]))
    d = np.abs(np.diff(x))
    for i in np.where(d > 0.5)[0]:  # salto de meia escala entre duas amostras: clique
        out.append((i / sr, "CLIQUE", 20 * np.log10(d[i])))
    return out


if __name__ == "__main__":
    for cena in CENAS or [c for c, _, _ in M.CENAS]:
        x, sr = ler(cena)
        for t, tipo, v in suspeitas(x, sr):
            tv = M.ini_cena[cena] + t
            print(f"{int(tv // 60):02d}:{tv % 60:05.2f}  {cena:<11} {t:7.2f}  {tipo:<10} {v:6.1f} dB")
