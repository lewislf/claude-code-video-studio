"""Acha som com energia de fala que não cai dentro de nenhuma palavra transcrita: gaguejo, sílaba solta, respiração, artefato.

  python3 achar_sobras.py [cena ...]

Usa os tempos por palavra de ../cenas-v5/palavras/<cena>.json. Também marca palavra longa demais para o tamanho dela,
que é onde o transcritor costuma esconder uma repetição ("ca-camundongo" vira "camundongo" com o dobro da duração).
"""
import json, sys, wave
import numpy as np

CENAS = sys.argv[1:]  # antes do import: montar_final troca sys.argv
import montar_final as M  # noqa: E402

PASSO, LIMIAR, FOLGA, MIN = 0.01, -38, 0.06, 0.09


def energia(cena):
    w = wave.open(f"assets/voz/{cena}.wav")
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    j = int(sr * PASSO); n = len(x) // j
    return 20 * np.log10(np.sqrt((x[: n * j].reshape(n, j) ** 2).mean(1)) + 1e-9)


def sobras(cena, stt="/tmp/claude-1002/stt"):
    db = energia(cena)
    ws = json.load(open(f"../cenas-v5/palavras/{cena}.json"))
    try:  # palavras da transcrição literal (whisper small) também cobrem: sobra só o que nenhuma das duas reconheceu
        ws2 = [{"start": w["start"], "end": w["end"]} for g in json.load(open(f"{stt}/{cena}.json"))["segments"] for w in g.get("words", [])]
    except FileNotFoundError:
        ws2 = []
    coberto = np.zeros(len(db), bool)
    for w in ws + ws2:
        coberto[max(int((w["start"] - FOLGA) / PASSO), 0): int((w["end"] + FOLGA) / PASSO) + 1] = True
    fala = (db > LIMIAR) & ~coberto
    out, k = [], 0
    while k < len(fala):
        if fala[k]:
            a = k
            while k < len(fala) and fala[k]:
                k += 1
            if (k - a) * PASSO >= MIN:
                out.append((a * PASSO, k * PASSO, "SOBRA", f"{db[a:k].max():.0f} dB"))
        k += 1
    for w in ws:
        if not w["text"][-1].isalnum():  # fim de frase sempre sai longo (a voz arrasta a última sílaba)
            continue
        letras = sum(c.isalpha() for c in w["text"]) or 1
        d = (db[int(w["start"] / PASSO): int(w["end"] / PASSO) + 1] > LIMIAR).sum() * PASSO  # só o trecho com som
        if d > 0.3 + 0.1 * letras:
            out.append((w["start"], w["end"], "LONGA", f"'{w['text']}' {d:.2f}s com som"))
    return sorted(out)


if __name__ == "__main__":
    for cena in CENAS or [c for c, _, _ in M.CENAS]:
        for a, b, tipo, info in sobras(cena):
            t = M.ini_cena[cena] + a
            print(f"{int(t // 60):02d}:{t % 60:05.2f}  {cena:<11} {a:7.2f}-{b:7.2f}  {tipo:<6} {info}")
