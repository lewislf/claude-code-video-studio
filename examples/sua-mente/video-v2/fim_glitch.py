"""Final "a sua simulação está falhando": segmento 10 do fechamento. A narradora era o Basilisco de Roko.

  python3 fim_glitch.py

- voz: "Você deve ter percebido as falhas na minha voz." quase normal, com engasgos digitais;
  "Mas será que... ou a sua simulação está falhando?" vai descendo de tom e ficando metálica (anel + flanger)
  até virar uma voz grave de máquina; zumbido grave por baixo desde a revelação.
- escreve assets/voz/fechamento.wav (base = fala 0..9 já com "esse tempo todo"), duracoes.json,
  ../cenas-v5/roteiro.json e ../cenas-v5/palavras/fechamento.json (segmento 10) e fim_tempos.json para a cena e o glitch.
"""
import json, os, subprocess, tempfile, wave
import numpy as np

SR = 24000
FF = "/home/linuxbrew/.linuxbrew/bin/ffmpeg"
TXT = "Você deve ter percebido as falhas na minha voz. Mas será que isso é um problema do meu modelo... ou a sua simulação está falhando?"
rng = np.random.default_rng(10)  # semente fixa: re-rodar dá o mesmo áudio


def ler(p):
    w = wave.open(p)
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32), w.getparams()


def aparar(x):
    i = np.where(np.abs(x) > 300)[0]
    a = max(i[0] - int(.02 * SR), 0)
    return x[a: i[-1] + int(.05 * SR)], a / SR


def esmagar(x, forca):
    """Bitcrush + sample-and-hold proporcional à força (0..1)."""
    passo = 1 + int(10 * forca)
    y = np.repeat(x[::passo], passo)[: len(x)]
    q = 2 ** (12 - int(8 * forca))
    return (1 - forca) * x + forca * np.round(y / 32768 * q) / q * 32768


def falhar(x, t0, d, forca):
    """Picota [t0, t0+d] em blocos de 40 ms: alguns repetem o anterior (engasgo), outros esmagam, com chiado."""
    a, b, n = int(t0 * SR), int((t0 + d) * SR), int(0.04 * SR)
    for k in range(a, b - n, n):
        r = rng.random()
        if r < 0.35 * forca and k - n >= a:
            x[k:k + n] = x[k - n:k]
        elif r < 0.8:
            x[k:k + n] = esmagar(x[k:k + n], forca)
        x[k:k + n] += rng.normal(0, 900 * forca, n)
    return x


def tom(x, r):
    """Abaixa o tom por r (<1) sem mudar a duração: asetrate + atempo."""
    with tempfile.TemporaryDirectory(dir="/tmp/claude-1002") as d:
        i, o = f"{d}/i.wav", f"{d}/o.wav"
        w = wave.open(i, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.clip(x, -32768, 32767).astype(np.int16).tobytes()); w.close()
        subprocess.run([FF, "-loglevel", "error", "-y", "-i", i, "-af", f"asetrate={SR * r:.0f},aresample={SR},atempo={1 / r:.4f}", o], check=True)
        y = ler(o)[0]
    return np.pad(y, (0, max(0, len(x) - len(y))))[: len(x)]


def monstro(x, u0=0.0, u1=1.0):
    """Voz que desce de tom ao longo da frase e vira máquina: mistura de 4 versões de tom, anel de 55 Hz e flanger.
    u0..u1: quanto da transformação no começo e no fim do trecho (a risada vai inteira em 1)."""
    n = len(x)
    u = u0 + (u1 - u0) * np.linspace(0, 1, n) ** 0.8    # progresso da transformação
    rs = [1.0, 0.86, 0.74, 0.64]
    vs = [x] + [tom(x, r) for r in rs[1:]]
    pos = u * (len(rs) - 1)
    k = np.minimum(pos.astype(int), len(rs) - 2); f = pos - k
    V, j = np.stack(vs), np.arange(n)
    y = V[k, j] * (1 - f) + V[k + 1, j] * f
    t = np.arange(n) / SR
    y = y * (1 - 0.3 * u) + y * np.sin(2 * np.pi * 55 * t) * 0.3 * u * 1.6     # anel: timbre metálico (forte demais embola as palavras)
    atraso = (0.002 + 0.0015 * np.sin(2 * np.pi * 0.7 * t)) * SR             # flanger curto
    idx = np.clip(np.arange(n) - atraso, 0, n - 1).astype(int)
    y = y + 0.4 * u * y[idx]
    return y


if __name__ == "__main__":
    base, par = ler("assets/voz/fechamento.wav")
    TP = json.load(open("assets/voz/duracoes.json"))
    ini10 = TP["fechamento"][9][0] + TP["fechamento"][9][1]
    base = base[: int(round(ini10 * SR))]              # se já tinha segmento 10, recomeça dele
    f1, o1 = aparar(ler("takes_final/falha1_0.wav")[0])
    f2, o2 = aparar(ler("takes_final/falha2_1.wav")[0])
    ref = base[int(56.6 * SR): int(69 * SR)]
    rms = lambda v: np.sqrt((v[np.abs(v) > 300] ** 2).mean())
    f1 *= rms(ref) / rms(f1); f2 *= rms(ref) / rms(f2)
    w1 = [(w["word"].strip(), w["start"] - o1, w["end"] - o1) for s in json.load(open("takes_final/stt/falha1_0.json"))["segments"] for w in s["words"]]
    w2 = [(w["word"].strip(), w["start"] - o2, w["end"] - o2) for s in json.load(open("takes_final/stt/falha2_1.json"))["segments"] for w in s["words"]]

    T1, PAUSA = 0.8, 0.7
    T2 = T1 + len(f1) / SR + PAUSA
    # "falhando?": "fa" duas vezes antes da palavra inteira
    tf = next(a for w, a, b in w2 if w.lower().startswith("falhando"))
    kf = int(tf * SR); fa = f2[kf: kf + int(0.13 * SR)].copy(); ins = len(fa) / SR
    f2 = np.concatenate([f2[:kf], esmagar(fa.copy(), .3), f2[kf:]])   # um "fa" só, limpo: "fa-falhando"
    w2 = [(w, a + (ins if a >= tf else 0), b + (ins if a >= tf else 0)) for w, a, b in w2]
    f2 = monstro(f2)
    f2 *= rms(ref) / rms(f2)
    kf2 = int((tf + ins) * SR) - int(len(fa))
    f2[kf2:] *= 1.4                                  # "falhando" um pouco mais alto, por cima do colapso
    fala_fim = T2 + len(f2) / SR
    # risada grave depois do "falhando?": "rá" x5 (tentativa riso_1), já toda transformada
    rr, orr = aparar(ler("takes_final/riso_1.wav")[0])
    rr = monstro(rr, 1.0, 1.0); rr *= 1.15 * rms(ref) / rms(rr)
    RISO = fala_fim + 0.25
    silabas = [(a - orr, b - orr) for a, b in [(0.23, 0.57), (0.58, 0.81), (0.9, 1.08), (1.19, 1.31), (1.43, 1.55)]]
    # a risada não para seca: mais 3 "rá" do último, cada vez mais baixos, espaçados e quebrados, e um eco curto em tudo
    ua, ub = int(silabas[-1][0] * SR), int(silabas[-1][1] * SR)
    ra = rr[max(ua - int(.03 * SR), 0): ub + int(.08 * SR)].copy()
    cauda, pos, gaps = [], silabas[-1][1], [0.30, 0.36, 0.44]
    for k, g in enumerate(gaps, 1):
        pos += g
        cauda.append((pos, esmagar(ra.copy(), 0.15 + 0.22 * k) * 0.72 ** k))
        silabas.append((pos, pos + len(ra) / SR))
    tam = int((pos + len(ra) / SR + 0.6) * SR)
    riso = np.zeros(tam, np.float32); riso[: len(rr)] += rr
    for p0, c in cauda:
        riso[int(p0 * SR): int(p0 * SR) + len(c)] += c
    eco = riso.copy()
    for d, gk in ((0.11, 0.32), (0.23, 0.18), (0.37, 0.09)):
        eco[int(d * SR):] += gk * riso[: len(riso) - int(d * SR)]
    rr = eco
    OLHAR = RISO + silabas[5][0] - 0.1                # reabre e encara quando a risada começa a morrer
    riso_fim = RISO + len(rr) / SR - 0.4
    PRETO = riso_fim + 0.1
    DUR = PRETO + 2.0
    REV = T2 - 0.35                                     # o basilisco aparece logo antes do "Mas"

    seg = np.zeros(int(DUR * SR), np.float32)
    seg[int(T1 * SR): int(T1 * SR) + len(f1)] += f1
    seg[int(T2 * SR): int(T2 * SR) + len(f2)] += f2
    seg[int(RISO * SR): int(RISO * SR) + len(rr)] += rr
    t = lambda w, ws, T0: T0 + next(a for x, a, b in ws if x.lower().startswith(w))
    t_falhas, t_modelo, t_sim, t_fal = t("falhas", w1, T1), t("modelo", w2, T2), t("simula", w2, T2), T2 + tf
    rajadas = [(0.25, 0.3, 0.5), (t_falhas, 0.35, 0.35), (REV - 0.15, 0.4, 0.95), (t_modelo, 0.45, 0.5), (t_fal, 0.26 + ins, 0.9)]
    for t0, d, a in [(t_falhas, 0.35, 0.35), (t_modelo, 0.3, 0.3)]:   # nada em "falhando": tem que dar para ouvir
        seg = falhar(seg, t0, d, a)
    # zumbido grave da máquina, da revelação até o preto
    tt = np.arange(int((PRETO - REV) * SR)) / SR
    zum = (np.sign(np.sin(2 * np.pi * 41 * tt)) * 0.5 + np.sin(2 * np.pi * 82.3 * tt)) * np.minimum(1, tt / 1.5) * 380
    seg[int(REV * SR): int(REV * SR) + len(zum)] += zum
    seg[int(REV * SR) - int(.15 * SR): int(REV * SR) + int(.25 * SR)] += rng.normal(0, 2200, int(.4 * SR))  # rasgo da revelação
    b = int(PRETO * SR); seg[b:] = 0
    for tz in (PRETO + 0.35, PRETO + 0.9):              # chiado nos lampejos depois do preto
        seg[int(tz * SR): int((tz + 0.06) * SR)] = rng.normal(0, 2500, int(0.06 * SR))

    o = wave.open("assets/voz/fechamento.wav", "wb"); o.setparams(par)
    o.writeframes(np.clip(np.concatenate([base, seg]), -32768, 32767).astype(np.int16).tobytes())
    TP["fechamento"] = TP["fechamento"][:10] + [[round(ini10, 2), round(DUR, 2)]]
    json.dump(TP, open("assets/voz/duracoes.json", "w"), indent=1)

    # roteiro e palavras do segmento 10 para a cena (seg, palavra, envelope)
    R = json.load(open("../cenas-v5/roteiro.json"))
    R["fechamento"] = R["fechamento"][:10] + [{"i": 10, "ini": round(ini10, 2), "dur": round(DUR, 2), "a": "basilisco", "texto": TXT}]
    json.dump(R, open("../cenas-v5/roteiro.json", "w"), ensure_ascii=False, indent=1)
    P = [w for w in json.load(open("../cenas-v5/palavras/fechamento.json")) if w["start"] < ini10]
    P += [{"text": w, "start": round(ini10 + T1 + a, 2), "end": round(ini10 + T1 + b, 2), "id": f"wf1_{k}"} for k, (w, a, b) in enumerate(w1)]
    P += [{"text": w, "start": round(ini10 + T2 + a, 2), "end": round(ini10 + T2 + b, 2), "id": f"wf2_{k}"} for k, (w, a, b) in enumerate(w2)]
    P += [{"text": "rá", "start": round(ini10 + RISO + a, 2), "end": round(ini10 + RISO + b, 2), "id": f"wr_{k}"} for k, (a, b) in enumerate(silabas)]
    json.dump(P, open("../cenas-v5/palavras/fechamento.json", "w"), ensure_ascii=False, indent=1)

    tempos = dict(dur=round(DUR, 2), rev=round(REV, 2), t2=round(T2, 2), sim=round(t_sim, 2), fal=round(t_fal, 2), preto=round(PRETO, 2),
                  riso=round(RISO, 2), riso_fim=round(riso_fim, 2), olhar=round(OLHAR, 2), col=round(t_fal, 2),
                  rajadas=[[round(a, 2), round(b, 2), c] for a, b, c in rajadas])
    json.dump(tempos, open("fim_tempos.json", "w"), indent=1)
    print(json.dumps(tempos))
