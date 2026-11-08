"""Troca só os segmentos que mudaram num render pronto, sem remontar o vídeo inteiro.

  python3 remendar.py v6-misto v7-misto abertura_7 fechamento_1

Recodifica apenas os segmentos cujo clipe (build.py::SUBST) está na lista; o resto do vídeo e o áudio são copiados do render
de origem. Funciona porque montar_final.py fecha cada segmento num keyframe (cada clipe começa com IDR).
"""
import subprocess, sys

orig, saida, clips = sys.argv[1], sys.argv[2], set(sys.argv[3:])  # antes do import: montar_final troca sys.argv
import montar_final as M
FF, FPS = M.FF, M.FPS
fr = lambda t: round(t * FPS)
alvo = [k for k, (c, i, _, _) in enumerate(M.linhas) if (M.B.SUBST.get((c, i)) or {}).get("clip") in clips]
if not alvo:
    sys.exit("nenhum segmento usa esses clipes")

lista, cursor = [], 0
for k in alvo:
    c, i, a, b = M.linhas[k]
    novo, _ = M.cena_clip(c, i, a, b, k)
    if fr(a) > cursor:
        lista += [f"file '{M.AQUI}/renders/{orig}.mp4'", f"inpoint {cursor / FPS:.4f}", f"outpoint {fr(a) / FPS:.4f}"]
    lista.append(f"file '{novo}'")
    cursor = fr(b)
if cursor < fr(M.TOTAL):  # sem isso o inpoint no fim volta ao último keyframe e cola ~2 s do render antigo no final
    lista += [f"file '{M.AQUI}/renders/{orig}.mp4'", f"inpoint {cursor / FPS:.4f}"]
open(f"{M.TMP}/lista.txt", "w").write("\n".join(lista) + "\n")

video = f"{M.TMP}/video.mp4"
subprocess.run([FF, "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{M.TMP}/lista.txt", "-map", "0:v", "-c", "copy", video], check=True)
final = f"renders/{saida}.mp4"
subprocess.run([FF, "-loglevel", "error", "-y", "-i", video, "-i", f"renders/{orig}.mp4", "-map", "0:v", "-map", "1:a", "-c", "copy",
                "-t", f"{M.TOTAL:.2f}", "-movflags", "+faststart", final], check=True)
subprocess.run([FF, "-loglevel", "error", "-y", "-i", final, "-vf", "scale=-2:720", "-c:v", "libx264", "-preset", "medium", "-crf", "30", "-maxrate", "1500k",
                "-bufsize", "3000k", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", f"renders/{saida}-720p.mp4"], check=True)
print(f"pronto: {final}, segmentos trocados: {alvo}")
