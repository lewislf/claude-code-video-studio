"""Prévia só do final (segmentos 9 e 10 do fechamento), com voz e música, em 1,35x e HD.

  python3 previa_final.py        # renders/previa-final.mp4
"""
import subprocess, sys

sys.argv = sys.argv[:1]  # montar_final troca sys.argv
import montar_final as M

V = 1.35
a9 = M.TP["fechamento"][9][0]
mus0 = M.ini_cena["fechamento"] + a9
dur = sum(M.TP["fechamento"][k][1] for k in (9, 10))
lista = f"{M.TMP}/previa.txt"
open(lista, "w").write("file '%s/assets/cenas3/fechamento_9.mp4'\nfile '%s/assets/cenas3/fechamento_10.mp4'\n" % (M.AQUI, M.AQUI))
subprocess.run([M.FF, "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista,
                "-ss", f"{a9:.2f}", "-i", "assets/voz/fechamento.wav", "-ss", f"{mus0:.2f}", "-i", "assets/musica.mp3",
                "-filter_complex",
                f"[1:a]aresample=48000[v];[2:a]aresample=48000,volume=0.14,atrim=0:{dur:.2f},afade=t=out:st={dur - 3:.2f}:d=3[m];"
                f"[v][m]amix=inputs=2:normalize=0:duration=first,volume=2.2,atempo={V}[a];[0:v]setpts=PTS/{V},fps=30[vv]",
                "-map", "[vv]", "-map", "[a]", "-t", f"{dur / V:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "renders/previa-final.mp4"], check=True)
print("pronto: renders/previa-final.mp4", f"({dur / V:.1f} s)")
