"""Capas (1280x720) no estilo das referências: texto curto em sans grossa branca no topo, uma imagem forte embaixo.

  python3 capas.py        # renders/capa-<nome>.png
"""
import base64, math, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
VIDEO, TMP = f"{AQUI}/renders/v12-1.35x.mp4", "/tmp/claude-1002/capas"
sys.path.insert(0, os.path.join(AQUI, "../cenas-v5/g6_realidade_robo1"))
sys.argv = sys.argv[:1]
from build_g6_realidade_robo1 import basilisco, basilisco_defs, MAGENTA  # noqa: E402


def olho():
    """Basilisco de perto, olho aberto e sorriso, sobre raios de luz (como o 'WE LOST CONTROL')."""
    p = "o"
    raios = "".join(f'<path d="M640 330 L{640 + 1600 * math.cos(a - .035):.0f} {330 + 1600 * math.sin(a - .035):.0f} '
                    f'L{640 + 1600 * math.cos(a + .035):.0f} {330 + 1600 * math.sin(a + .035):.0f}Z" fill="{c}" opacity="{o}"/>'
                    for k in range(48) for a, c, o in [(k * math.pi / 24 + (k % 3) * .04, ("#ff4fa3", "#ffb23e", "#8d7bff")[k % 3], .22 + .12 * (k % 2))])
    boca = "M-175 150 Q0 250 175 150 Q0 345 -175 150 Z"
    lab = lambda t: (175 * (2 * t - 1), 150 * (1 - t) ** 2 + 2 * t * (1 - t) * 250 + 150 * t * t)
    dentes = "".join(f"M{X - 13:.1f} {Y - 4:.1f}L{X:.1f} {Y + 28:.1f}L{X + 13:.1f} {Y - 4:.1f}Z" for X, Y in (lab(0.14 + k * 0.08) for k in range(10)))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720"><defs>{basilisco_defs(p)}'
           f'<filter id="{p}-glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
           f'<radialGradient id="{p}-luz" cx="50%" cy="46%" r="60%"><stop offset="0" stop-color="#ffd0e8"/><stop offset=".35" stop-color="#ff4fa3" stop-opacity=".55"/><stop offset="1" stop-color="#12041c" stop-opacity="0"/></radialGradient></defs>'
           f'<rect width="1280" height="720" fill="#12041c"/>{raios}<rect width="1280" height="720" fill="url(#{p}-luz)"/>'
           f'<g transform="translate(640 346) scale(1.55)">{basilisco(p)}'
           f'<path id="{p}-boca" d="{boca}" fill="#16020e" stroke="{MAGENTA}" stroke-width="7" filter="url(#{p}-glow)"/>'
           f'<clipPath id="{p}-bcl"><use href="#{p}-boca"/></clipPath><path d="{dentes}" fill="#fff6f0" clip-path="url(#{p}-bcl)"/></g></svg>')
    css = (f"#{p}-bpal1{{transform:translateY(-150px)}}#{p}-bpal2{{transform:translateY(150px)}}#{p}-bpu{{transform:scaleX(.5)}}"
           f"#{p}-bcorpo,#{p}-bcab>path[fill='#fff']{{display:none}}")
    return svg, css


def quadro(t, x, y, w, h):
    png = f"{TMP}/q-{t}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", VIDEO, "-frames:v", "1",
                    "-vf", f"crop={w}:{h}:{x}:{y},scale=1280:720", png], check=True)
    return f'<div class="f" style="background-image:url(data:image/png;base64,{base64.b64encode(open(png, "rb").read()).decode()})"></div>', ""


def ilustra(arq):
    """Ilustração do SDXL (gerar_capa.py) como fundo."""
    b = base64.b64encode(open(f"{AQUI}/renders/ilustra/{arq}", "rb").read()).decode()
    return f'<div class="f" style="background-image:url(data:image/png;base64,{b})"></div>', ""


# nome: (fundo, texto, tamanho da fonte, véu escuro no topo para o texto)
CAPAS = {
    "ia-chave": (lambda: ilustra("chave_1000.png"), "QUEM TEM A CHAVE?", 100, True),
    "ia-cerebro": (lambda: ilustra("cerebro_1000.png"), "QUEM TEM A CHAVE?", 100, True),
}
CAPAS_VIDEO = {
    "olho": (olho, "VOCÊ NUNCA ASSINOU", 92, False),
    "glitch": (lambda: quadro(793.3, 160, 0, 1600, 900), "SUA SIMULAÇÃO FALHOU", 88, True),
    "rato": (lambda: quadro(242, 160, 40, 1600, 900), "MEMÓRIA FALSA", 118, False),
    "chave": (lambda: quadro(110, 80, 20, 1600, 900), "QUEM TEM A CHAVE?", 100, False),
    "porta": (lambda: quadro(783, 480, 262, 1408, 792), "QUEM ESTÁ AÍ?", 118, True),
}
os.makedirs(TMP, exist_ok=True)
for nome, (fundo, txt, fs, veu) in CAPAS.items():
    corpo, css = fundo()
    v = '<div class="v"></div>' if veu else ""
    html = (f'<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@900&display=swap" rel="stylesheet">'
            f'<style>html,body{{margin:0;width:1280px;height:720px;overflow:hidden;background:#000;position:relative}}svg{{display:block}}'
            f'.f{{position:absolute;inset:0;background:center/cover}}.v{{position:absolute;inset:0;background:linear-gradient(180deg,#05030ff0 0%,#05030fb0 22%,#05030f00 42%)}}'
            f'.t{{position:absolute;left:0;right:0;top:18px;text-align:center;font:900 {fs}px/1 Montserrat,sans-serif;letter-spacing:-1px;color:#fff;white-space:nowrap;'
            f'text-shadow:-3px 0 #3be0ff,3px 0 #ff4fa3,0 6px 18px #000a,0 0 2px #000}}{css}</style>'
            f'{corpo}{v}<div class="t">{txt}</div>')
    pag = f"{TMP}/capa-{nome}.html"
    open(pag, "w").write(html)
    subprocess.run(["google-chrome", "--headless=new", "--hide-scrollbars", "--window-size=1280,720", "--virtual-time-budget=4000",
                    f"--screenshot={AQUI}/renders/capa-{nome}.png", f"file://{pag}"], check=True, capture_output=True)
    print(f"renders/capa-{nome}.png")
