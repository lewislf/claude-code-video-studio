"""Monta o vídeo completo direto com ffmpeg: cada segmento vira um clipe de duração exata (em quadros), na ordem da narração.

  python3 montar_final.py           # saída: renders/v5-misto.mp4 (+ 720p)

Segmentos trocados (build.py::SUBST + assets/cenas3/mapa_v5.json) vêm dos clipes em assets/cenas3/. Os que não foram trocados
(trailers de ficção) são cortados do render antigo renders/v2-misto.mp4. Áudio: vozes por cena nos tempos de index.html,
música a 0,14 com fade, loudnorm -14 LUFS. Não usa o Chrome, então roda leve (sem o teto de 5 GB do render do HyperFrames).
"""
import json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
os.chdir(AQUI)
sys.argv = ["build.py", "misto", "--v3"]
import build as B
from roteiro import CENAS

FF = "/home/linuxbrew/.linuxbrew/bin/ffmpeg"
FPS = 30
TP = json.load(open("assets/voz/duracoes.json"))
ANTIGO = "renders/v2-misto.mp4"
SAIDA = os.environ.get("SAIDA", "v6-misto")
TMP = tempfile.mkdtemp(prefix="montar-", dir="/tmp/claude-1002")
VOZ = os.environ.get("VOZ", "assets/voz")  # assets/voz_limpa: vozes sem gaguejo/estalo (limpar_voz.py)

# linha do tempo: (cena, i, início absoluto, fim absoluto)
linhas, ini_cena, t = [], {}, 0.0
for cena, _, ss in CENAS:
    ini_cena[cena] = t
    dur_c = TP[cena][-1][0] + TP[cena][-1][1]
    for i in range(len(ss)):
        a = t + TP[cena][i][0]
        b = t + (TP[cena][i + 1][0] if i + 1 < len(ss) else dur_c)
        linhas.append((cena, i, a, b))
    t += dur_c
TOTAL = t


def cena_clip(cena, i, a, b, k):
    n = round(b * FPS) - round(a * FPS)
    out = f"{TMP}/{k:03d}.mp4"
    sub = B.SUBST.get((cena, i))
    if sub:
        src, ss = f"assets/cenas3/{sub['clip']}.mp4", sub["ms"]
    else:
        src, ss = ANTIGO, a
    vf = f"fps={FPS},scale=1920:1080:flags=lanczos,tpad=stop_mode=clone:stop_duration=3,format=yuv420p"
    subprocess.run([FF, "-loglevel", "error", "-y", "-ss", f"{ss:.3f}", "-i", src, "-vf", vf, "-frames:v", str(n), "-an", "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "17", "-g", "30", "-r", str(FPS), "-pix_fmt", "yuv420p", out], check=True)
    return out, bool(sub)


def mixar_audio():
    """Vozes por cena nos seus tempos + música a 0,14 com fade, loudnorm -14 LUFS em duas passagens. Devolve o .m4a."""
    ins, filt, rot = [], [], []
    for n, (cena, _, _) in enumerate(CENAS):
        ins += ["-i", f"{VOZ}/{cena}.wav"]
        ms = int(round(ini_cena[cena] * 1000))
        filt.append(f"[{n}:a]aresample=48000,adelay={ms}|{ms}[v{n}]")
        rot.append(f"[v{n}]")
    nm = len(CENAS)
    ins += ["-i", "assets/musica.mp3"]
    filt.append(f"{''.join(rot)}amix=inputs={nm}:normalize=0:duration=longest[voz]")
    filt.append(f"[{nm}:a]aresample=48000,volume=0.14,atrim=0:{TOTAL:.2f},afade=t=in:d=2,afade=t=out:st={TOTAL - 3:.2f}:d=3[mus]")
    filt.append("[voz][mus]amix=inputs=2:normalize=0:duration=longest[a]")
    bruto = f"{TMP}/audio.wav"
    subprocess.run([FF, "-loglevel", "error", "-y", *ins, "-filter_complex", ";".join(filt), "-map", "[a]", bruto], check=True)
    # loudnorm em duas passagens (a de uma passagem ficava em -15,5 LUFS)
    r = subprocess.run([FF, "-hide_banner", "-i", bruto, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    audio = f"{TMP}/audio.m4a"
    subprocess.run([FF, "-loglevel", "error", "-y", "-i", bruto, "-af", ln, "-ar", "48000", "-c:a", "aac", "-b:a", "192k", audio], check=True)
    return audio


def main():
    try:
        subprocess.run(["taskline", "set", "montar-final", "0", str(len(linhas)), "--label", "montar vídeo", "--pid", str(os.getpid())])
    except Exception:
        pass
    saidas = [None] * len(linhas)

    def trabalho(k):
        c, i, a, b = linhas[k]
        saidas[k] = cena_clip(c, i, a, b, k)
        subprocess.run(["taskline", "add", "montar-final"])

    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(trabalho, range(len(linhas))))
    novos = sum(1 for _, n in saidas if n)
    print(f"{novos} de {len(linhas)} segmentos são cenas novas; o resto vem do render antigo")
    lista = f"{TMP}/lista.txt"
    open(lista, "w").write("".join(f"file '{p}'\n" for p, _ in saidas))
    video = f"{TMP}/video.mp4"
    subprocess.run([FF, "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", video], check=True)
    audio = mixar_audio()
    final = f"renders/{SAIDA}.mp4"
    subprocess.run([FF, "-loglevel", "error", "-y", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a", "-c", "copy", "-t", f"{TOTAL:.2f}", "-movflags", "+faststart", final], check=True)
    subprocess.run([FF, "-loglevel", "error", "-y", "-i", final, "-vf", "scale=-2:720", "-c:v", "libx264", "-preset", "medium", "-crf", "30", "-maxrate", "1500k",
                    "-bufsize", "3000k", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", f"renders/{SAIDA}-720p.mp4"], check=True)
    subprocess.run(["taskline", "done", "montar-final"])
    print("pronto:", final, f"({TOTAL:.1f} s)")


if __name__ == "__main__":
    main()
