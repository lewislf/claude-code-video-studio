"""Refaz só o áudio de um render pronto (vídeo copiado), com as vozes de VOZ.

  VOZ=assets/voz_limpa python3 trocar_audio.py v10-base v10-limpo
"""
import subprocess, sys

orig, saida = sys.argv[1], sys.argv[2]  # antes do import: montar_final troca sys.argv
import montar_final as M

audio = M.mixar_audio()
subprocess.run([M.FF, "-loglevel", "error", "-y", "-i", f"renders/{orig}.mp4", "-i", audio, "-map", "0:v", "-map", "1:a", "-c", "copy",
                "-t", f"{M.TOTAL:.2f}", "-movflags", "+faststart", f"renders/{saida}.mp4"], check=True)
print(f"pronto: renders/{saida}.mp4 (vozes de {M.VOZ})")
