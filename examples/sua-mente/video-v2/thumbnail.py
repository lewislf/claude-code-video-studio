"""Thumbnail do YouTube (1280x720): o Basilisco sorrindo olha para um contrato com a assinatura em branco e carimbo de ACEITO.

  python3 thumbnail.py        # renders/thumbnail.png
"""
import os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "../cenas-v5/g6_realidade_robo1"))
sys.argv = sys.argv[:1]
from build_g6_realidade_robo1 import basilisco, basilisco_defs, MAGENTA, AMBAR, CIANO  # noqa: E402

p = "t"
boca = lambda x, yu, yl, y0: f"M{-x} {y0} Q0 {yu} {x} {y0} Q0 {yl} {-x} {y0} Z"
x, y0, yu, yl = 175, 150, 250, 345
lab = lambda t: (x * (2 * t - 1), y0 * (1 - t) ** 2 + 2 * t * (1 - t) * yu + y0 * t * t)
dentes = "".join(f"M{X - 13:.1f} {Y - 4:.1f}L{X:.1f} {Y + 28:.1f}L{X + 13:.1f} {Y - 4:.1f}Z" for X, Y in (lab(0.14 + k * 0.08) for k in range(10)))
sorriso = (f'<path id="{p}-boca" d="{boca(x, yu, yl, y0)}" fill="#16020e" stroke="{MAGENTA}" stroke-width="7" stroke-linejoin="round" filter="url(#{p}-glow)"/>'
           f'<clipPath id="{p}-bcl"><use href="#{p}-boca"/></clipPath><path d="{dentes}" fill="#fff6f0" clip-path="url(#{p}-bcl)"/>')

linhas = "".join(f'<rect x="60" y="{y}" width="{w}" height="12" rx="6" fill="#8a7f68" opacity=".45"/>'
                 for y, w in [(250, 440), (280, 470), (310, 400), (360, 450), (390, 420), (420, 300)])
contrato = (f'<g transform="translate(400 720) rotate(-6) scale(.82)"><g transform="translate(-300 -360)">'
            f'<rect x="8" y="14" width="600" height="740" rx="14" fill="#000" opacity=".45"/>'
            f'<rect width="600" height="740" rx="14" fill="#f4ecd8" stroke="#c9bb98" stroke-width="4"/>'
            f'<text x="300" y="100" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="40" fill="#2a1e10">TERMOS DE USO</text>'
            f'<text x="300" y="150" text-anchor="middle" font-family="IBM Plex Mono" font-weight="500" font-size="26" fill="#6a5a40">DA SUA MENTE</text>'
            f'<rect x="60" y="185" width="480" height="4" fill="#2a1e10" opacity=".6"/>{linhas}'
            f'<text x="60" y="510" font-family="IBM Plex Mono" font-weight="500" font-size="22" fill="#4a3e28">Memórias, pensamentos e percepção</text>'
            f'<text x="60" y="540" font-family="IBM Plex Mono" font-weight="500" font-size="22" fill="#4a3e28">passam a ser acessíveis por terceiros.</text>'
            f'<text x="60" y="665" font-family="EB Garamond" font-weight="700" font-size="56" fill="#2a1e10">X</text>'
            f'<rect x="100" y="660" width="420" height="4" fill="#2a1e10"/>'
            f'<text x="310" y="700" text-anchor="middle" font-family="IBM Plex Mono" font-size="20" fill="#6a5a40">assinatura do titular</text>'
            f'<g transform="translate(400 640) rotate(-14)" opacity=".88"><rect x="-150" y="-58" width="300" height="116" rx="12" fill="none" stroke="#d81e4a" stroke-width="10"/>'
            f'<text x="0" y="26" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="72" fill="#d81e4a">ACEITO</text></g>'
            f'</g></g>')

titulo = lambda dx, cor, op: (f'<g transform="translate({dx} 0)" opacity="{op}"><text x="70" y="170" font-family="EB Garamond" font-weight="700" font-size="150" fill="{cor}">VOCÊ NUNCA</text>'
                              f'<text x="70" y="300" font-family="EB Garamond" font-weight="700" font-size="150" fill="{cor}">ASSINOU.</text></g>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1280" height="720"><defs>{basilisco_defs(p)}'
       f'<filter id="{p}-glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
       f'<radialGradient id="{p}-fundo" cx="70%" cy="50%" r="75%"><stop offset="0" stop-color="#3a0c3a"/><stop offset=".55" stop-color="#140620"/><stop offset="1" stop-color="#030108"/></radialGradient>'
       f'<filter id="{p}-sombra"><feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#000" flood-opacity=".9"/></filter></defs>'
       f'<rect width="1920" height="1080" fill="url(#{p}-fundo)"/>'
       f'<g transform="translate(1420 600) scale(1.12)"><circle r="620" fill="url(#{p}-aura)" opacity=".55"/>{basilisco(p)}{sorriso}</g>'
       f'{contrato}'
       f'<g filter="url(#{p}-sombra)">{titulo(-6, CIANO, .7)}{titulo(6, MAGENTA, .7)}{titulo(0, "#f4f1ea", 1)}</g>'
       f'</svg>')
# pálpebras semicerradas, íris virada para o contrato, pupila fina, sem as presas originais
css = (f"#{p}-bpal1{{transform:translateY(-84px)}}#{p}-bpal2{{transform:translateY(78px)}}#{p}-bolhar{{transform:translateX(-62px)}}"
       f"#{p}-bpu{{transform:scaleX(.45)}}#{p}-bcab>path[fill='#fff']{{display:none}}#{p}-bcorpo{{display:none}}")
html = (f'<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@700&family=IBM+Plex+Mono:wght@400;500;700&display=swap" rel="stylesheet">'
        f'<style>html,body{{margin:0;background:#000}}svg{{display:block}}{css}</style>{svg}')
os.makedirs(f"{AQUI}/renders", exist_ok=True)
pag = f"{AQUI}/renders/thumbnail.html"
open(pag, "w").write(html)
subprocess.run(["google-chrome", "--headless=new", "--hide-scrollbars", "--window-size=1280,720", "--virtual-time-budget=4000",
                f"--screenshot={AQUI}/renders/thumbnail.png", f"file://{pag}"], check=True, capture_output=True)
os.remove(pag)
print("pronto: renders/thumbnail.png")
