"""YouTube thumbnail (1280x720): the grinning Basilisk looks at a contract with a blank signature and an ACCEPTED stamp.

  python3 thumbnail.py        # renders/thumbnail.png
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../scenes/g6_reality_robot1"))
sys.argv = sys.argv[:1]
from build_g6_reality_robot1 import basilisk, basilisk_defs, MAGENTA, CYAN  # noqa: E402

p = "t"
mouth = lambda x, yu, yl, y0: f"M{-x} {y0} Q0 {yu} {x} {y0} Q0 {yl} {-x} {y0} Z"
x, y0, yu, yl = 175, 150, 250, 345
lip = lambda t: (x * (2 * t - 1), y0 * (1 - t) ** 2 + 2 * t * (1 - t) * yu + y0 * t * t)
teeth = "".join(f"M{X - 13:.1f} {Y - 4:.1f}L{X:.1f} {Y + 28:.1f}L{X + 13:.1f} {Y - 4:.1f}Z" for X, Y in (lip(0.14 + k * 0.08) for k in range(10)))
grin = (f'<path id="{p}-mouth" d="{mouth(x, yu, yl, y0)}" fill="#16020e" stroke="{MAGENTA}" stroke-width="7" stroke-linejoin="round" filter="url(#{p}-glow)"/>'
           f'<clipPath id="{p}-mclip"><use href="#{p}-mouth"/></clipPath><path d="{teeth}" fill="#fff6f0" clip-path="url(#{p}-mclip)"/>')

lines = "".join(f'<rect x="60" y="{y}" width="{w}" height="12" rx="6" fill="#8a7f68" opacity=".45"/>'
                 for y, w in [(250, 440), (280, 470), (310, 400), (360, 450), (390, 420), (420, 300)])
contract = (f'<g transform="translate(400 720) rotate(-6) scale(.82)"><g transform="translate(-300 -360)">'
            f'<rect x="8" y="14" width="600" height="740" rx="14" fill="#000" opacity=".45"/>'
            f'<rect width="600" height="740" rx="14" fill="#f4ecd8" stroke="#c9bb98" stroke-width="4"/>'
            f'<text x="300" y="100" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="40" fill="#2a1e10">TERMS OF USE</text>'
            f'<text x="300" y="150" text-anchor="middle" font-family="IBM Plex Mono" font-weight="500" font-size="26" fill="#6a5a40">OF YOUR MIND</text>'
            f'<rect x="60" y="185" width="480" height="4" fill="#2a1e10" opacity=".6"/>{lines}'
            f'<text x="60" y="510" font-family="IBM Plex Mono" font-weight="500" font-size="22" fill="#4a3e28">Memories, thoughts and perception</text>'
            f'<text x="60" y="540" font-family="IBM Plex Mono" font-weight="500" font-size="22" fill="#4a3e28">become accessible to third parties.</text>'
            f'<text x="60" y="665" font-family="EB Garamond" font-weight="700" font-size="56" fill="#2a1e10">X</text>'
            f'<rect x="100" y="660" width="420" height="4" fill="#2a1e10"/>'
            f'<text x="310" y="700" text-anchor="middle" font-family="IBM Plex Mono" font-size="20" fill="#6a5a40">signature of the holder</text>'
            f'<g transform="translate(400 640) rotate(-14)" opacity=".88"><rect x="-150" y="-58" width="300" height="116" rx="12" fill="none" stroke="#d81e4a" stroke-width="10"/>'
            f'<text x="0" y="26" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="72" fill="#d81e4a">ACCEPTED</text></g>'
            f'</g></g>')

title = lambda dx, color, op: (f'<g transform="translate({dx} 0)" opacity="{op}"><text x="70" y="170" font-family="EB Garamond" font-weight="700" font-size="150" fill="{color}">YOU NEVER</text>'
                              f'<text x="70" y="300" font-family="EB Garamond" font-weight="700" font-size="150" fill="{color}">SIGNED.</text></g>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1280" height="720"><defs>{basilisk_defs(p)}'
       f'<filter id="{p}-glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
       f'<radialGradient id="{p}-bg" cx="70%" cy="50%" r="75%"><stop offset="0" stop-color="#3a0c3a"/><stop offset=".55" stop-color="#140620"/><stop offset="1" stop-color="#030108"/></radialGradient>'
       f'<filter id="{p}-shadow"><feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#000" flood-opacity=".9"/></filter></defs>'
       f'<rect width="1920" height="1080" fill="url(#{p}-bg)"/>'
       f'<g transform="translate(1420 600) scale(1.12)"><circle r="620" fill="url(#{p}-aura)" opacity=".55"/>{basilisk(p)}{grin}</g>'
       f'{contract}'
       f'<g filter="url(#{p}-shadow)">{title(-6, CYAN, .7)}{title(6, MAGENTA, .7)}{title(0, "#f4f1ea", 1)}</g>'
       f'</svg>')
# half-closed eyelids, iris turned to the contract, thin pupil, without the original fangs
css = (f"#{p}-blid1{{transform:translateY(-84px)}}#{p}-blid2{{transform:translateY(78px)}}#{p}-bgaze{{transform:translateX(-62px)}}"
       f"#{p}-bpupil{{transform:scaleX(.45)}}#{p}-bhead>path[fill='#fff']{{display:none}}#{p}-bbody{{display:none}}")
html = (f'<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@700&family=IBM+Plex+Mono:wght@400;500;700&display=swap" rel="stylesheet">'
        f'<style>html,body{{margin:0;background:#000}}svg{{display:block}}{css}</style>{svg}')
os.makedirs(f"{HERE}/renders", exist_ok=True)
page = f"{HERE}/renders/thumbnail.html"
open(page, "w").write(html)
subprocess.run(["google-chrome", "--headless=new", "--hide-scrollbars", "--window-size=1280,720", "--virtual-time-budget=4000",
                f"--screenshot={HERE}/renders/thumbnail.png", f"file://{page}"], check=True, capture_output=True)
os.remove(page)
print("ready: renders/thumbnail.png")
