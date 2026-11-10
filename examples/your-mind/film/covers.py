"""Covers (1280x720) in the style of the references: short text in heavy white sans at the top, one strong image below.

  python3 covers.py        # renders/cover-<name>.png
"""
import base64, math, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO, TMP = f"{HERE}/renders/v12-1.35x.mp4", tempfile.mkdtemp(prefix="covers-")
sys.path.insert(0, os.path.join(HERE, "../scenes/g6_reality_robot1"))
sys.argv = sys.argv[:1]
from build_g6_reality_robot1 import basilisk, basilisk_defs, MAGENTA  # noqa: E402


def eye():
    """Basilisk up close, eye open and grinning, over light rays (like 'WE LOST CONTROL')."""
    p = "o"
    rays = "".join(f'<path d="M640 330 L{640 + 1600 * math.cos(a - .035):.0f} {330 + 1600 * math.sin(a - .035):.0f} '
                    f'L{640 + 1600 * math.cos(a + .035):.0f} {330 + 1600 * math.sin(a + .035):.0f}Z" fill="{c}" opacity="{o}"/>'
                    for k in range(48) for a, c, o in [(k * math.pi / 24 + (k % 3) * .04, ("#ff4fa3", "#ffb23e", "#8d7bff")[k % 3], .22 + .12 * (k % 2))])
    mouth = "M-175 150 Q0 250 175 150 Q0 345 -175 150 Z"
    lip = lambda t: (175 * (2 * t - 1), 150 * (1 - t) ** 2 + 2 * t * (1 - t) * 250 + 150 * t * t)
    teeth = "".join(f"M{X - 13:.1f} {Y - 4:.1f}L{X:.1f} {Y + 28:.1f}L{X + 13:.1f} {Y - 4:.1f}Z" for X, Y in (lip(0.14 + k * 0.08) for k in range(10)))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720"><defs>{basilisk_defs(p)}'
           f'<filter id="{p}-glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
           f'<radialGradient id="{p}-light" cx="50%" cy="46%" r="60%"><stop offset="0" stop-color="#ffd0e8"/><stop offset=".35" stop-color="#ff4fa3" stop-opacity=".55"/><stop offset="1" stop-color="#12041c" stop-opacity="0"/></radialGradient></defs>'
           f'<rect width="1280" height="720" fill="#12041c"/>{rays}<rect width="1280" height="720" fill="url(#{p}-light)"/>'
           f'<g transform="translate(640 346) scale(1.55)">{basilisk(p)}'
           f'<path id="{p}-mouth" d="{mouth}" fill="#16020e" stroke="{MAGENTA}" stroke-width="7" filter="url(#{p}-glow)"/>'
           f'<clipPath id="{p}-mclip"><use href="#{p}-mouth"/></clipPath><path d="{teeth}" fill="#fff6f0" clip-path="url(#{p}-mclip)"/></g></svg>')
    css = (f"#{p}-blid1{{transform:translateY(-150px)}}#{p}-blid2{{transform:translateY(150px)}}#{p}-bpupil{{transform:scaleX(.5)}}"
           f"#{p}-bbody,#{p}-bhead>path[fill='#fff']{{display:none}}")
    return svg, css


def frame(t, x, y, w, h):
    png = f"{TMP}/frame-{t}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", VIDEO, "-frames:v", "1",
                    "-vf", f"crop={w}:{h}:{x}:{y},scale=1280:720", png], check=True)
    return f'<div class="f" style="background-image:url(data:image/png;base64,{base64.b64encode(open(png, "rb").read()).decode()})"></div>', ""


def illustration(file):
    """SDXL illustration as background."""
    b = base64.b64encode(open(f"{HERE}/renders/ilustra/{file}", "rb").read()).decode()
    return f'<div class="f" style="background-image:url(data:image/png;base64,{b})"></div>', ""


# name: (background, text, font size, dark veil at the top for the text)
COVERS = {
    "ai-key": (lambda: illustration("chave_1000.png"), "WHO HAS THE KEY?", 100, True),
    "ai-brain": (lambda: illustration("cerebro_1000.png"), "WHO HAS THE KEY?", 100, True),
}
COVERS_VIDEO = {
    "eye": (eye, "YOU NEVER SIGNED", 92, False),
    "glitch": (lambda: frame(793.3, 160, 0, 1600, 900), "YOUR SIMULATION FAILED", 88, True),
    "mouse": (lambda: frame(242, 160, 40, 1600, 900), "FALSE MEMORY", 118, False),
    "key": (lambda: frame(110, 80, 20, 1600, 900), "WHO HAS THE KEY?", 100, False),
    "door": (lambda: frame(783, 480, 262, 1408, 792), "WHO'S THERE?", 118, True),
}
os.makedirs(TMP, exist_ok=True)
for name, (background, txt, fs, veil) in COVERS.items():
    body, css = background()
    v = '<div class="v"></div>' if veil else ""
    html = (f'<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@900&display=swap" rel="stylesheet">'
            f'<style>html,body{{margin:0;width:1280px;height:720px;overflow:hidden;background:#000;position:relative}}svg{{display:block}}'
            f'.f{{position:absolute;inset:0;background:center/cover}}.v{{position:absolute;inset:0;background:linear-gradient(180deg,#05030ff0 0%,#05030fb0 22%,#05030f00 42%)}}'
            f'.t{{position:absolute;left:0;right:0;top:18px;text-align:center;font:900 {fs}px/1 Montserrat,sans-serif;letter-spacing:-1px;color:#fff;white-space:nowrap;'
            f'text-shadow:-3px 0 #3be0ff,3px 0 #ff4fa3,0 6px 18px #000a,0 0 2px #000}}{css}</style>'
            f'{body}{v}<div class="t">{txt}</div>')
    page = f"{TMP}/cover-{name}.html"
    open(page, "w").write(html)
    subprocess.run(["google-chrome", "--headless=new", "--hide-scrollbars", "--window-size=1280,720", "--virtual-time-budget=4000",
                    f"--screenshot={HERE}/renders/cover-{name}.png", f"file://{page}"], check=True, capture_output=True)
    print(f"renders/cover-{name}.png")
