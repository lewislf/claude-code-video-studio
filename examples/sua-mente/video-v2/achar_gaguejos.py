"""Compara a fala real (whisper, palavra a palavra) com o roteiro e lista o que sobra no áudio: repetições, sílabas soltas, ruído.

  python3 achar_gaguejos.py /tmp/claude-1002/stt [cena ...]

Saída: uma linha por suspeita, com o tempo no vídeo final (início da cena + tempo local).
"""
import difflib, json, re, sys, unicodedata

sys.path.insert(0, "../cenas-v5")
STT, PEDIDAS = sys.argv[1], sys.argv[2:]  # antes do import: montar_final troca sys.argv
ROT = json.load(open("../cenas-v5/roteiro.json"))
norm = lambda w: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", w.lower()).encode("ascii", "ignore").decode())


def inicio_cenas():
    import montar_final as M  # noqa: E402  (ini_cena: início de cada cena no vídeo)
    return M.ini_cena


def suspeitas(cena):
    texto = " ".join(s["texto"] for s in ROT[cena])
    ref = [norm(w) for w in texto.split() if norm(w)]
    ws = [w for seg in json.load(open(f"{STT}/{cena}.json"))["segments"] for w in seg.get("words", [])]
    hyp = [norm(w["word"]) for w in ws]
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_opcodes():
        if op in ("insert", "replace") and j2 > j1:
            extra = " ".join(w["word"].strip() for w in ws[j1:j2])
            esperado = " ".join(ref[i1:i2])
            # palavra repetida logo depois de si mesma, ou trecho a mais sem correspondência no roteiro
            rep = any(hyp[j] and (hyp[j] == hyp[j - 1] or hyp[j - 1].startswith(hyp[j]) or hyp[j].startswith(hyp[j - 1])) for j in range(max(j1, 1), j2 + 1) if j < len(hyp))
            if op == "insert" or rep:
                out.append((ws[j1]["start"], ws[j2 - 1]["end"], "REPETE" if rep else "A MAIS", extra, esperado))
        # palavra reconhecida com baixa confiança costuma ser artefato de síntese
    for w in ws:
        if w.get("probability", 1) < 0.25:
            out.append((w["start"], w["end"], "INCERTO", w["word"].strip(), f"p={w['probability']:.2f}"))
    return sorted(out)


if __name__ == "__main__":
    ini = inicio_cenas()
    for cena in (PEDIDAS or ROT.keys()):
        try:
            ss = suspeitas(cena)
        except FileNotFoundError:
            continue
        for a, b, tipo, extra, esp in ss:
            t = ini[cena] + a
            print(f"{int(t // 60):02d}:{t % 60:05.2f}  {cena:<11} {a:6.2f}-{b:6.2f}  {tipo:<7} '{extra}'  (roteiro: {esp})")
