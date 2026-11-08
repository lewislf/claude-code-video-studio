"""Clipe do final "a simulação está falhando": o último quadro da porta segura na tela e vai quebrando até o preto.

  python3 glitch.py <duração> <rajadas> <início do colapso> <preto> saida.mp4 [entrada.mp4]
  ex.: python3 glitch.py 10 "1.2:0.25:0.4,3.0:0.4:0.7" 6.0 8.4 assets/cenas3/fechamento_10.mp4

rajadas: t0:duração:força (0..1). Do início do colapso até o preto a força sobe até 1; depois do preto sobram dois
lampejos de chiado. Tudo determinístico (o "aleatório" é hash de seno sobre faixa e quadro), então re-renderizar dá igual.
"""
import subprocess, sys

FF = "/home/linuxbrew/.linuxbrew/bin/ffmpeg"
BASE = ("assets/cenas3/fechamento_9.mp4", 3.6)  # quadro aceso da porta, antes do fade do fim


def forca(rajadas, t_col, t_preto):
    g = "+".join(f"{a}*between(T,{t0},{t0 + d})" for t0, d, a in rajadas) or "0"
    col = f"clip((T-{t_col})/{t_preto - t_col},0,1)"
    # liga/desliga a cada 1/20 s, para a falha "engasgar" em vez de ficar contínua
    pisca = "gt(abs(sin(floor(T*20)*91.7)),0.3)"
    return f"min(1,({g})*{pisca}+{col}*(0.55+0.45*{pisca}))"


def filtro(dur, rajadas, t_col, t_preto, video=False):
    G = forca(rajadas, t_col, t_preto)
    h = lambda a, b: f"abs(sin(({a})*12.9898+({b})*78.233))"  # hash 0..1
    faixa = "floor(Y/(14+40*" + h("floor(T*15)", "3") + "))"
    salto = f"({G})*gt({h(faixa, 'floor(T*15)')},0.62)*({h(faixa + '+7', 'floor(T*15)')}-0.5)*420"
    rgb = f"({G})*26"
    xs = f"(X+{salto})"
    ex = lambda c, d: f"{c}(clip({xs}{d},0,W-1),Y)"
    zoom = f"zoompan=z='1+0.05*on/{dur * 30}':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.45':d=1:s=1920x1080:fps=30"  # aproximação lenta
    if video:  # a cena já tem câmera própria
        zoom = "scale=1920:1080"
    return (f"[0:v]{zoom},format=gbrp,"
            f"geq=r='{ex('r', '+' + rgb)}':g='{ex('g', '')}':b='{ex('b', '-' + rgb)}',"
            # chiado e linhas de varredura, proporcionais à força
            f"noise=alls=28:allf=t,format=yuv420p,"
            f"eq=brightness='0.25*gt({G.replace('T', 't')},0.85)*gt(abs(sin(floor(t*24)*33.1)),0.6)':eval=frame,"
            f"drawbox=0:0:iw:ih:black:t=fill:enable='gte(t,{t_preto})*not(between(t,{t_preto + 0.35},{t_preto + 0.42}))*not(between(t,{t_preto + 0.9},{t_preto + 0.94}))'[v]")


if __name__ == "__main__":
    dur, raj, t_col, t_preto, out = float(sys.argv[1]), sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
    rajadas = [tuple(map(float, r.split(":"))) for r in raj.split(",") if r]
    if len(sys.argv) > 6:  # sobre um vídeo (a cena do basilisco)
        entrada = ["-i", sys.argv[6], "-t", str(dur)]
    else:                  # sobre o quadro parado da porta
        subprocess.run([FF, "-loglevel", "error", "-y", "-ss", str(BASE[1]), "-i", BASE[0], "-frames:v", "1", "-update", "1", "/tmp/claude-1002/glitch_base.png"], check=True)
        entrada = ["-loop", "1", "-framerate", "30", "-i", "/tmp/claude-1002/glitch_base.png", "-t", str(dur)]
    subprocess.run(["systemd-run", "--user", "--scope", "-q", "-p", "MemoryMax=3G", "-p", "MemorySwapMax=0",
                    FF, "-loglevel", "error", "-y", *entrada,
                    "-filter_complex", filtro(dur, rajadas, t_col, t_preto, len(sys.argv) > 6), "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
                    "-g", "30", "-r", "30", "-pix_fmt", "yuv420p", out], check=True)
    print("pronto:", out)
