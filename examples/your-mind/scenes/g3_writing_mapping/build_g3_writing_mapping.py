"""Scenes v5, group g3: writing 0, 2, 5, 7 and mapping 0, 3, 4, 6, 7, 8.

  python3 build_g3_writing_mapping.py      # writes compositions/, index.html, timing.json for this folder

Reuses: mouse and isometric box (scenes-v4/build4.py), fly, neuron network and fly brain
(scenes-v3/build2.py, art2.py), the person (engine.py). Real paper pages in assets/ (copied from film/assets/docs).
"""
import json, math, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "../../scenes-v4"))
from engine import *
from build4 import mouse, box, box_grad, bolt
from build2 import network_rich
from art2 import fly_rich, fly_defs, brain_card
from build import path_d
import figure as G   # module, not *: this file has its own orb() (sphere with a small box)
OUT_DIR = os.path.dirname(os.path.abspath(__file__))  # engine also exports HERE (scenes); do not use HERE here


def human(p, var="home", pose="sitting", x=0, y=0, s=1.0, mirror=False, colors=None, scene=None, chair=True):
    """The real person (figure.py), positioned. The figure's {p}-headW group carries its transform as an attribute; here it becomes
    an outer + inner group so figure_idle can animate it without throwing the head to (0,0) (GOTCHAS 1).
    colors: {original_color: new_color} to draw another person with the same parts."""
    g = G.figure(p, var, pose, glow=f"{scene or p}-glow", chair=chair)
    g, n = re.subn(rf'<g id="{p}-headW" transform="([^"]+)">', rf'<g transform="\1"><g id="{p}-headW">', g, count=1)
    assert n == 1 and g.endswith("</g></g></g>")
    g = g + "</g>"
    for a, b in (colors or {}).items():
        g = g.replace(a, b)
    return f'<g transform="translate({x} {y}) scale({-s if mirror else s} {s})">{g}</g>'


def anchor(var, pose, name):
    return G.ANCHORS[("home" if var == "home" else "work", pose, 30)][name]


def shoulder(var, pose):
    """Arm svgOrigin: local shoulder coordinate (a % of the box is off, the new arm's box includes clipped shadows)."""
    x, y = anchor(var, pose, "shoulder_arm")
    return f'svgOrigin:"{x} {y}"'


def neck(var, pose):
    x, y = anchor(var, pose, "head_center")
    return f'svgOrigin:"{x} {y + 50:.0f}"'


# ---------------------------------------------------------------- extra JS: camera with several keyframes (a single origin)
JS_G3 = r"""
  function camK(sel,ox,oy,ks){
    var o={l:Math.log(ks[0][1])};
    tl.set(sel,{scale:ks[0][1],svgOrigin:ox+" "+oy},0);
    for(var i=1;i<ks.length;i++){
      tl.fromTo(o,{l:Math.log(ks[i-1][1])},{l:Math.log(ks[i][1]),duration:Math.max(0.05,ks[i][0]-ks[i-1][0]),ease:ks[i][2]||"power3.inOut",
        onUpdate:function(){gsap.set(sel,{scale:Math.exp(o.l),svgOrigin:ox+" "+oy});},immediateRender:false},ks[i-1][0]);
    }
  }
  function slideOut(sel,t,dur){tl.fromTo(sel,{yPercent:0},{yPercent:-125,duration:dur||0.5,ease:"expo.in",immediateRender:false},t);}
  function highlight(sel,t,dur){tl.fromTo(sel,{scaleX:0,transformOrigin:"0% 50%"},{scaleX:1,transformOrigin:"0% 50%",duration:dur||0.6,ease:"power2.inOut"},t);}
  function drawStroke(sel,t,dur,len){tl.fromTo(sel,{attr:{"stroke-dashoffset":len||2000}},{attr:{"stroke-dashoffset":0},duration:dur||1,ease:"power2.inOut"},t);}
"""


def comp(p, dur, svg, html, js, extra="", **kw):
    return composition(p, dur, svg, html, JS_G3 + js, extra, **kw)


def headline(id_, txt, style, cls="title"):
    """Big text that rises through a mask (EB Garamond)."""
    return text(id_, txt, style, cls)


def mono(id_, txt, style, color="#bff4ff", size=56):
    return text(id_, txt, f"{style};font:500 {size}px 'IBM Plex Mono',monospace;letter-spacing:.14em;color:{color}", "title", "1.35em")


# ---------------------------------------------------------------- parts
def folder_defs(p):
    return (f'<linearGradient id="{p}-fBack" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a44c4"/><stop offset="1" stop-color="#2c1f80"/></linearGradient>'
            f'<linearGradient id="{p}-fFront" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7d62e8"/><stop offset="1" stop-color="#4330a8"/></linearGradient>'
            f'<linearGradient id="{p}-paper" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#e9dcc2"/></linearGradient>')


def folder(p, sheet="", flap=""):
    """File folder centered at (0,0), ~640 x 470. Ids: {p}-folder, {p}-sheet (rises on opening), {p}-flap (opens)."""
    return f"""<g id="{p}-folder">
<ellipse cx="0" cy="252" rx="360" ry="26" fill="#05031a" opacity=".55"/>
<path d="M-320 -200 L-300 -244 L-110 -244 L-88 -200 L320 -200 L320 230 L-320 230 Z" fill="url(#{p}-fBack)" stroke="#8d7bff" stroke-width="4" stroke-linejoin="round"/>
<g transform="translate(0 0)"><g id="{p}-sheet"><g filter="url(#{p}-shadow)"><rect x="-270" y="-250" width="540" height="420" rx="10" fill="url(#{p}-paper)"/></g>{sheet}</g></g>
<g transform="translate(0 230)"><g id="{p}-flap"><g transform="translate(0 -230)">
<path d="M-320 -130 L320 -150 L320 230 L-320 230 Z" fill="url(#{p}-fFront)" stroke="#3be0ff" stroke-width="5" stroke-linejoin="round" filter="url(#{p}-glow)"/>
<path d="M-300 -112 L300 -130" stroke="#fff" stroke-opacity=".35" stroke-width="6" stroke-linecap="round"/>
{flap}</g></g></g></g>"""


def monitor(p, x, y, w, h, screen=""):
    """Monitor (bezel from B) with the screen area at (x,y,w,h). `screen` is clipped inside."""
    return f"""<g filter="url(#{p}-shadow)">
<rect x="{x - 26}" y="{y - 26}" width="{w + 52}" height="{h + 52}" rx="36" fill="url(#{p}-bezel)" stroke="#8d7bff" stroke-width="4"/>
<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="url(#{p}-screen)"/>
<rect x="{x + w / 2 - 40}" y="{y + h + 26}" width="80" height="70" fill="url(#{p}-bezel)"/><rect x="{x + w / 2 - 160}" y="{y + h + 92}" width="320" height="24" rx="12" fill="url(#{p}-bezel)" stroke="#8d7bff" stroke-width="3"/></g>
<clipPath id="{p}-scp"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18"/></clipPath><g clip-path="url(#{p}-scp)">{screen}<path d="M{x} {y} L {x + w * .4} {y} L {x + w * .1} {y + h} L {x} {y + h} Z" fill="#fff" opacity=".04"/></g>"""


def monitor_defs(p):
    return (f'<linearGradient id="{p}-bezel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a4a9a"/><stop offset="1" stop-color="#1b1b4a"/></linearGradient>'
            f'<linearGradient id="{p}-screen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16143a"/><stop offset="1" stop-color="#0a1a3a"/></linearGradient>')


def network_defs(p):
    return f'<radialGradient id="{p}-lobe" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="#3b5bff" stop-opacity=".3"/><stop offset="1" stop-color="#3b5bff" stop-opacity=".05"/></radialGradient>'


def brain_defs(p):
    return f'<radialGradient id="{p}-brain" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#1c6fa0" stop-opacity=".9"/><stop offset="1" stop-color="#0c2e66" stop-opacity=".95"/></radialGradient>'


def page(p, img, w, ih, marks):
    """Real page from the paper (image `assets/{img}.png`, width w in screen px, ih = height/width). Origin at the top left corner.
    marks: [(id, x, y, width, height, color)] in pixels of the original image (1600 wide)."""
    k = w / 1600
    ms = "".join(f'<g transform="translate({x * k:.1f} {y * k:.1f})"><rect id="{p}-{i}" width="{lw * k:.1f}" height="{lh * k:.1f}" rx="3" fill="{c}" opacity=".42" style="mix-blend-mode:multiply"/></g>'
                 for i, x, y, lw, lh, c in marks)
    return (f'<g filter="url(#{p}-shadow)"><rect x="-8" y="-8" width="{w + 16}" height="{w * ih + 16}" rx="6" fill="#fffdf6"/></g>'
            f'<image href="assets/{img}.png" x="0" y="0" width="{w}" height="{w * ih:.1f}" preserveAspectRatio="none"/>{ms}'
            f'<rect x="-8" y="-8" width="{w + 16}" height="{w * ih + 16}" rx="6" fill="none" stroke="#8d7bff" stroke-width="3" opacity=".6"/>')


# ---------------------------------------------------------------- chapter cards (writing 0, mapping 0)
def chapter_card(scene, n, name, theme):
    p = f"{scene}_0"
    start, dur = seg(scene, 0)
    t_file, t_n, t_name = {"writing": (0.19, 1.95, 2.27), "mapping": (0.2, 1.91, 2.33)}[scene]
    lines = "".join(f'<rect x="-220" y="{-200 + k * 38}" width="{400 if k % 3 else 300}" height="11" rx="5" fill="#8a7f68" opacity=".4"/>' for k in range(9))
    if theme == "writing":
        sheet = (lines + f'<path id="{p}-scribble" d="M-210 130 C -180 80 -160 150 -130 110 S -90 90 -60 130 S -20 100 10 126 S 60 96 90 128 S 140 104 170 124" '
                 f'fill="none" stroke="#1d2f9a" stroke-width="9" stroke-linecap="round" stroke-dasharray="700" stroke-dashoffset="700"/>'
                 f'<g transform="translate(170 124)"><g id="{p}-pen" opacity="0"><g transform="rotate(35)"><rect x="-10" y="-150" width="22" height="130" rx="8" fill="#ffb23e" stroke="#7a4a10" stroke-width="3"/>'
                 f'<path d="M-10 -20 L12 -20 L1 4 Z" fill="#2a1d70"/></g></g></g>')
    else:
        rg = random.Random(5)
        pts = [(-200, 100), (-120, -60), (-30, 60), (40, -150), (110, 20), (200, -90), (190, 120), (-210, -170)]
        links = [(0, 1), (1, 2), (2, 4), (1, 3), (3, 5), (4, 5), (4, 6), (0, 2), (7, 1), (7, 3)]
        grid = "".join(f'<line x1="{x}" y1="-250" x2="{x}" y2="170"/>' for x in range(-240, 271, 60)) + "".join(f'<line x1="-270" y1="{y}" x2="270" y2="{y}"/>' for y in range(-220, 171, 60))
        sheet = (f'<g stroke="#8a7f68" stroke-width="2" opacity=".35">{grid}</g>'
                 f'<g id="{p}-link" stroke="#3b5bff" stroke-width="7" stroke-linecap="round" fill="none">' +
                 "".join(f'<path d="M{pts[a][0]} {pts[a][1]} L{pts[b][0]} {pts[b][1]}" stroke-dasharray="400" stroke-dashoffset="400"/>' for a, b in links) + '</g>' +
                 "".join(f'<circle class="node" cx="{x}" cy="{y}" r="15" fill="{["#3be0ff", "#ff4fa3", "#8d7bff", "#ffb23e"][k % 4]}" stroke="#1a1050" stroke-width="4"/>' for k, (x, y) in enumerate(pts)) +
                 f'<g transform="translate(110 20)"><g id="{p}-pin" opacity="0"><path d="M0 0 C-30 -40 -36 -70 0 -86 C36 -70 30 -40 0 0 Z" fill="#ff4f7d" stroke="#fff" stroke-width="4"/><circle cy="-56" r="13" fill="#fff"/></g></g>')
    flap = (f'<rect x="-240" y="-60" width="300" height="120" rx="10" fill="#fffaf0" opacity=".92"/>'
              f'<text x="-90" y="34" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="104" fill="#2c1f80">{n}</text>'
              f'<rect x="100" y="-40" width="160" height="14" rx="7" fill="#bff4ff" opacity=".5"/><rect x="100" y="-6" width="120" height="14" rx="7" fill="#bff4ff" opacity=".35"/>')
    extra = folder_defs(p) + f'<linearGradient id="{p}-num" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8d7bff" stop-opacity=".55"/><stop offset="1" stop-color="#3be0ff" stop-opacity=".08"/></linearGradient>'
    # the person in front of the folder, standing, reaching out a hand
    FLOOR, FX, FS = 790, 1260, 0.8
    # same pose on both cards (chapter echo); the outfit changes: home on 1, work on 2
    desk_y = 690
    var = "home" if theme == "writing" else "work"
    figure_svg = human(p + "g", var, "standing", 830, FLOOR, 0.85, scene=p)
    arm = -80
    FY = desk_y - 230 * FS
    desk = (f'<g filter="url(#{p}-shadow)"><rect x="950" y="{desk_y}" width="640" height="26" rx="10" fill="#2a1d70" stroke="#8d7bff" stroke-width="4"/></g>'
            f'<path d="M990 {desk_y + 26} L984 {FLOOR} M1550 {desk_y + 26} L1556 {FLOOR}" stroke="#8d7bff" stroke-width="10" stroke-linecap="round"/>')
    floor = (f'<rect x="0" y="{FLOOR}" width="1920" height="{1080 - FLOOR}" fill="#0b0828" opacity=".55"/>'
            f'<line x1="60" y1="{FLOOR}" x2="1860" y2="{FLOOR}" stroke="#8d7bff" stroke-width="3" opacity=".6"/>')
    svg = f"""<g id="{p}-world">
{floor}
<g transform="translate(330 0)"><g id="{p}-numG"><rect x="-260" y="180" width="520" height="620" fill="none"/>
<text id="{p}-num" x="0" y="{FLOOR}" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="820" fill="url(#{p}-num)" fill-opacity="0" stroke="#bfb3ff" stroke-width="7" stroke-dasharray="3200" stroke-dashoffset="3200" filter="url(#{p}-glow)">{n}</text></g></g>
{desk}
<g transform="translate({FX} {FY:.0f}) scale({FS})"><g id="{p}-folderW">{folder(p, sheet, flap)}</g></g>
{figure_svg}
<g id="{p}-shine" opacity="0" fill="#ffd98a">{"".join(f'<circle cx="{FX + 330 * FS * math.cos(a):.0f}" cy="{FY - 170 * FS + 150 * FS * math.sin(a):.0f}" r="{6 + (k % 3) * 3}"/>' for k, a in enumerate([i * 0.785 for i in range(8)]))}</g>
</g>"""
    html = (mono(f"{p}-t1", "FILE", "left:150px;top:120px", "#ffd27a", 64) +
            headline(f"{p}-t2", name, "left:690px;width:1000px;text-align:center;top:800px;font-size:170px;color:#eef1f7;letter-spacing:.06em"))
    js = f"""
  camK("#{p}-world",960,540,[[0,1.14],[{dur:.2f},1.0,"power2.out"]]);
  tl.fromTo("#{p}-folderW",{{y:-900,rotation:-9,transformOrigin:"50% 50%"}},{{y:0,rotation:0,transformOrigin:"50% 50%",duration:0.8,ease:"back.out(1.2)"}},0.05);
  tl.fromTo("#{p}g-eye",{{x:0,y:0}},{{x:3,y:{-2 if theme == "mapping" else 1},duration:0.3}},{t_file:.2f});
  tl.fromTo("#{p}g-arm",{{rotation:0,{shoulder(var, "standing")}}},{{rotation:{arm},{shoulder(var, "standing")},duration:0.45,ease:"back.out(1.6)"}},{t_name - 0.35:.2f});
  rise("#{p}-t1 span",{t_file:.2f});
  drawStroke("#{p}-num",0.25,1.6,3200);
  tl.fromTo("#{p}-num",{{attr:{{"fill-opacity":0}}}},{{attr:{{"fill-opacity":1}},duration:0.4,immediateRender:false}},{t_n:.2f});
  tl.fromTo("#{p}-numG",{{scale:1.18,transformOrigin:"50% 50%"}},{{scale:1,transformOrigin:"50% 50%",duration:0.7,ease:"elastic.out(1,0.45)",immediateRender:false}},{t_n:.2f});
  rise("#{p}-t2 span",{t_name:.2f},0.7);
  tl.fromTo("#{p}-flap",{{scaleY:1,skewX:0,transformOrigin:"50% 100%"}},{{scaleY:0.7,skewX:-8,transformOrigin:"50% 100%",duration:0.4,ease:"back.out(2)"}},{t_name - 0.1:.2f});
  tl.fromTo("#{p}-sheet",{{y:0}},{{y:-150,duration:0.5,ease:"back.out(1.6)"}},{t_name - 0.05:.2f});
  tl.fromTo("#{p}-shine",{{opacity:0,scale:0.6,svgOrigin:"{FX} {FY - 170 * FS:.0f}"}},{{opacity:1,scale:1.15,svgOrigin:"{FX} {FY - 170 * FS:.0f}",duration:0.5,ease:"power2.out"}},{t_name + 0.1:.2f});
  tl.fromTo("#{p}-shine",{{opacity:1}},{{opacity:0.35,duration:0.4,immediateRender:false}},{t_name + 0.6:.2f});
""" + G.figure_idle(p + "g", dur, (1.1,))
    if theme == "writing":
        js += f"""
  enter("#{p}-pen",{t_name:.2f},0.15);
  drawStroke("#{p}-scribble",{t_name + 0.1:.2f},0.6,700);
  tl.fromTo("#{p}-pen",{{x:-380,y:6}},{{x:0,y:0,duration:0.6,ease:"power2.inOut",immediateRender:false}},{t_name + 0.1:.2f});
"""
    else:
        js += f"""
  tl.fromTo("#{p}-link path",{{attr:{{"stroke-dashoffset":400}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.3,stagger:0.05,ease:"power2.out"}},{t_name + 0.05:.2f});
  tl.fromTo("#{p}-pin",{{opacity:0,y:-120}},{{opacity:1,y:0,duration:0.45,ease:"bounce.out"}},{t_name + 0.25:.2f});
"""
    return comp(p, dur, svg, html, js, extra, seed=5 if theme == "writing" else 9)


def writing_0():
    return chapter_card("writing", "1", "WRITE", "writing")


def mapping_0():
    return chapter_card("mapping", "2", "MAP", "mapping")


# ---------------------------------------------------------------- writing 2: Ramirez 2013 page, mouse and engram
def writing_2():
    SC, SG = "writing", 2
    p = "writing_2"
    start, dur = seg(SC, SG)
    t_susumu, t_nobel, t_laureate, t_mark, t_lit, t_explore, t_box, t_mod, t_respond, t_light = (
        0.94, 3.51, 2.48, 4.2, 5.79,
        7.26, 8.29, 11.69, 13.27, 14.04)
    W, IH = 660, 2071 / 1600
    pg = page(p, "ramirez2013", W, IH, [("m1", 318, 184, 966, 70, "#ffb23e"), ("m2", 948, 346, 304, 48, "#ff4fa3")])
    rg = random.Random(3)
    BX, BY = 1640, 250
    nodes = []
    while len(nodes) < 22:
        a, r = rg.uniform(0, 6.283), 118 * math.sqrt(rg.uniform(0.02, 1))
        x, y = BX + r * math.cos(a), BY + r * math.sin(a)
        if all((x - u) ** 2 + (y - v) ** 2 > 38 ** 2 for u, v in nodes):
            nodes.append((round(x), round(y)))
    eng = sorted(range(len(nodes)), key=lambda k: (nodes[k][0] - BX + 10) ** 2 + (nodes[k][1] - BY + 10) ** 2)[:7]
    edges = "".join(f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}"/>' for a in range(len(nodes)) for b in range(a + 1, len(nodes)) if (nodes[a][0] - nodes[b][0]) ** 2 + (nodes[a][1] - nodes[b][1]) ** 2 < 70 ** 2)
    eng_edges = "".join(f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}"/>' for i, a in enumerate(eng) for b in eng[i + 1:] if (nodes[a][0] - nodes[b][0]) ** 2 + (nodes[a][1] - nodes[b][1]) ** 2 < 80 ** 2)
    extra = box_grad(p, "c") + f'<radialGradient id="{p}-bubbleG" cx="45%" cy="40%" r="70%"><stop offset="0" stop-color="#2a1d70"/><stop offset="1" stop-color="#120c3a"/></radialGradient>'
    svg = f"""
<g transform="translate(140 118) rotate(-2)"><g id="{p}-pg">{pg}</g></g>
<g id="{p}-lab" opacity="0">
 <g transform="translate(707 262) scale(.68)">{box(p)}
  <g transform="translate(900 700) scale(1.15)"><g id="{p}-mouseW"><g id="{p}-bob">{mouse(p)}</g></g></g>
  <path id="{p}-cable" d="M1010 -440 L1010 -60 C 1010 160 1040 300 1052 440" fill="none" stroke="#9aa6d0" stroke-width="12" stroke-linecap="round" stroke-dasharray="1100" stroke-dashoffset="1100"/>
  <path id="{p}-light" d="M1010 -440 L1010 -60 C 1010 160 1040 300 1052 440" fill="none" stroke="#7fe6ff" stroke-width="14" stroke-linecap="round" stroke-dasharray="80 1100" stroke-dashoffset="80" filter="url(#{p}-glow)" opacity="0"/>
  <circle id="{p}-halo" cx="1052" cy="458" r="40" fill="#7fe6ff" opacity="0" filter="url(#{p}-glow)"/>
 </g>
 <g id="{p}-bubble" opacity="0">
  <circle cx="1470" cy="470" r="10" fill="#c9b8ff" opacity=".7"/><circle cx="1510" cy="418" r="16" fill="#c9b8ff" opacity=".8"/>
  <circle cx="{BX}" cy="{BY}" r="150" fill="url(#{p}-bubbleG)" stroke="#8d7bff" stroke-width="5" filter="url(#{p}-glow)"/>
  <g stroke="#6a7cff" stroke-width="2.5" opacity=".7">{edges}</g>
  <g id="{p}-engEdges" stroke="#ffb23e" stroke-width="5" opacity="0">{eng_edges}</g>
  <g>{"".join(f'<circle cx="{x}" cy="{y}" r="10" fill="#5fb7ff" opacity=".8"/>' for x, y in nodes)}</g>
  <g id="{p}-eng" opacity="0" filter="url(#{p}-glow)">{"".join(f'<circle cx="{nodes[k][0]}" cy="{nodes[k][1]}" r="14" fill="#ffb23e"/>' for k in eng)}</g>
  <g id="{p}-ring" opacity="0" fill="none" stroke="#7fe6ff" stroke-width="5">{"".join(f'<circle cx="{nodes[k][0]}" cy="{nodes[k][1]}" r="22"/>' for k in eng)}</g>
 </g>
</g>"""
    html = (headline(f"{p}-n1", "Susumu", "left:1230px;top:250px;font-size:130px;color:#ffd0ea") +
            headline(f"{p}-n2", "Tonegawa", "left:1230px;top:400px;font-size:130px;color:#ffd0ea") +
            text(f"{p}-n3", "NOBEL LAUREATE", "left:1236px;top:596px;font:500 58px 'IBM Plex Mono',monospace;letter-spacing:.05em;color:#ffd27a", "title", "1.35em") +
            mono(f"{p}-c1", "CALM BOX", "left:960px;width:900px;text-align:center;top:900px", "#bff4ff", 56) +
            mono(f"{p}-c2", "RESPOND TO LIGHT", "left:960px;width:900px;text-align:center;top:900px", "#7fe6ff", 56))
    z0 = 2.0
    js = f"""
  camK("#{p}-cam",470,250,[[0,2.25],[{t_mark:.2f},{z0},"sine.inOut"],[{t_mark + 1.6:.2f},1.0],[{dur:.2f},1.035,"sine.inOut"]]);
  tl.fromTo("#{p}-pg",{{y:420,rotation:-5,opacity:0}},{{y:0,rotation:0,opacity:1,duration:0.9,ease:"expo.out"}},0.05);
  highlight("#{p}-m1",0.6,0.8);
  highlight("#{p}-m2",{t_susumu:.2f},0.7);
  rise("#{p}-n1 span",{t_susumu:.2f}); rise("#{p}-n2 span",{1.48:.2f});
  rise("#{p}-n3 span",{t_laureate + 0.3:.2f});
  slideOut("#{p}-n1 span",{t_mark:.2f}); slideOut("#{p}-n2 span",{t_mark + 0.08:.2f}); slideOut("#{p}-n3 span",{t_mark + 0.16:.2f});
  enter("#{p}-lab",{t_mark + 0.2:.2f},0.8);
  tl.fromTo("#{p}-bob",{{y:0}},{{y:-6,duration:0.8,repeat:10,yoyo:true,ease:"sine.inOut"}},{t_mark:.2f});
  tl.fromTo("#{p}-rEyelid",{{y:-52}},{{y:0,duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t_mark + 2.4:.2f});
  tl.fromTo("#{p}-rEyelid",{{y:-52}},{{y:0,duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t_mod + 0.5:.2f});
  tl.fromTo("#{p}-bubble",{{opacity:0,scale:0.3,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.8,ease:"back.out(1.6)"}},{t_lit - 0.6:.2f});
  tl.fromTo("#{p}-eng",{{opacity:0}},{{opacity:1,duration:0.15,repeat:3,yoyo:true}},{t_lit:.2f});
  tl.fromTo("#{p}-eng",{{opacity:0}},{{opacity:1,duration:0.3,immediateRender:false}},{t_lit + 0.6:.2f});
  enter("#{p}-engEdges",{t_lit + 0.4:.2f},0.5);
  tl.fromTo("#{p}-mouseW",{{x:-90}},{{x:60,duration:{t_mod - t_explore:.2f},ease:"sine.inOut"}},{t_explore:.2f});
  tl.fromTo("#{p}-cx polyline",{{attr:{{"stroke-width":7}}}},{{attr:{{"stroke-width":14}},duration:0.4,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_box:.2f});
  rise("#{p}-c1 span",{t_box:.2f});
  slideOut("#{p}-c1 span",{t_respond - 0.35:.2f},0.4);
  tl.fromTo("#{p}-ring",{{opacity:0,scale:1.8,svgOrigin:"{BX} {BY}"}},{{opacity:1,scale:1,svgOrigin:"{BX} {BY}",duration:0.6,ease:"back.out(2)"}},{t_mod:.2f});
  drawStroke("#{p}-cable",{t_mod:.2f},1.0,1100);
  rise("#{p}-c2 span",{t_respond:.2f});
  tl.fromTo("#{p}-light",{{opacity:0,attr:{{"stroke-dashoffset":80}}}},{{opacity:1,attr:{{"stroke-dashoffset":-1020}},duration:0.9,ease:"power1.in"}},{t_light - 0.8:.2f});
  tl.fromTo("#{p}-halo",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:0.9,scale:1.8,transformOrigin:"50% 50%",duration:0.4,ease:"power2.out"}},{t_light:.2f});
  tl.fromTo("#{p}-eng circle",{{attr:{{fill:"#ffb23e"}}}},{{attr:{{fill:"#bff4ff"}},duration:0.25,immediateRender:false}},{t_light:.2f});
"""
    return comp(p, dur, svg, html, js, extra, seed=4)


def gear(cx, cy, r, teeth, color, id_):
    pts = []
    for k in range(teeth * 2):
        for d in (0, 1):
            a = (k + d * 0.5) * math.pi / teeth
            rr = r if k % 2 == 0 else r * 0.78
            pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return (f'<g transform="translate(0 0)"><g id="{id_}"><polygon points="{" ".join(pts)}" fill="{color}" stroke="#7a4a10" stroke-width="2"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .3:.1f}" fill="#2a1d70"/></g></g>')


def orb(p, k, color):
    """Memory: glass sphere with a life moment (the coffee) inside. Centered at (0,0), radius 110."""
    return (f'<circle r="118" fill="{color}" opacity=".18" filter="url(#{p}-glow)"/>'
            f'<circle r="110" fill="url(#{p}-orb)" stroke="{color}" stroke-width="6"/>'
            f'<clipPath id="{p}-oc{k}"><circle r="104"/></clipPath><g clip-path="url(#{p}-oc{k})"><g transform="scale(1.4) translate(-100 -75)">{G.picture_scene("coffee")}</g></g>'
            f'<ellipse cx="-38" cy="-56" rx="36" ry="20" fill="#fff" opacity=".35" transform="rotate(-30 -38 -56)"/>')


# ---------------------------------------------------------------- writing 5: same mechanism for false and true memories
def writing_5():
    SC, SG = "writing", 5
    p = "writing_5"
    start, dur = seg(SC, SG)
    t_brain, t_same, t_memory, t_false, t_true, t_inside, t_not, t_diff = (
        2.31, 3.58, 4.94, 6.27, 6.99,
        8.49, 9.45, 11.78)
    pp = p + "a"
    S, TX, TY = 2.6, 427, 196
    BXc, BYc = TX + 192 * S, TY + 84 * S          # brain center on screen
    extra = box_grad(p, "c") + f'<radialGradient id="{p}-orb" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#3a2a8c"/><stop offset="1" stop-color="#120c3a"/></radialGradient>'
    path_l = f"M330 430 C 520 200 760 220 {BXc:.0f} {BYc:.0f}"
    path_r = f"M1590 430 C 1400 200 1160 220 {BXc:.0f} {BYc:.0f}"
    svg = f"""<g id="{p}-world">
 <ellipse cx="960" cy="900" rx="300" ry="26" fill="#05031a" opacity=".45"/>
 {person(pp, TX, TY, S)}
 <g id="{p}-gears" opacity="0">{gear(BXc - 26, BYc - 8, 46, 9, "#ffb23e", p + "-g1")}{gear(BXc + 44, BYc + 30, 32, 7, "#ffd27a", p + "-g2")}</g>
 <path id="{p}-pathL" d="{path_l}" fill="none" stroke="#ff4fa3" stroke-width="6" stroke-dasharray="14 12" opacity="0"/>
 <path id="{p}-pathR" d="{path_r}" fill="none" stroke="#38e8a8" stroke-width="6" stroke-dasharray="14 12" opacity="0"/>
 <g transform="translate(330 430)"><g id="{p}-orbL"><g id="{p}-orbLI">{orb(p, "L", "#ff4fa3")}</g></g></g>
 <g transform="translate(1590 430)"><g id="{p}-orbR"><g id="{p}-orbRI">{orb(p, "R", "#38e8a8")}</g></g></g>
 <circle id="{p}-flash" cx="{BXc:.0f}" cy="{BYc:.0f}" r="120" fill="#ffd0ea" opacity="0" filter="url(#{p}-glow)"/>
</g>
<g id="{p}-inside" opacity="0">
 <rect width="1920" height="1080" fill="#14093a" opacity=".86"/>
 <g transform="translate(660 520) scale(1.7)"><g id="{p}-i1"><g id="{p}-i1b">{orb(p, "i1", "#c9b8ff")}</g></g></g>
 <g transform="translate(1260 520) scale(1.7)"><g id="{p}-i2"><g id="{p}-i2b">{orb(p, "i2", "#c9b8ff")}</g></g></g>
 <text id="{p}-q" x="960" y="575" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="170" fill="#ffd27a" opacity="0" filter="url(#{p}-glow)">?</text>
</g>"""
    html = (mono(f"{p}-l1", "FALSE", "left:130px;width:400px;text-align:center;top:580px", "#ff9bd0", 54) +
            mono(f"{p}-l2", "TRUE", "left:1340px;width:500px;text-align:center;top:580px", "#7ff5c8", 54) +
            headline(f"{p}-t1", "The same mechanism", "left:0;right:0;text-align:center;top:40px;font-size:110px;color:#ffd98a") +
            headline(f"{p}-t2", "From the inside", "left:0;right:0;text-align:center;top:60px;font-size:120px;color:#eef1f7") +
            mono(f"{p}-t3", "YOU CAN'T TELL THE DIFFERENCE", "left:0;right:0;text-align:center;top:880px", "#ffd27a", 54))
    dx_l, dy_l = BXc - 330, BYc - 430
    dx_r, dy_r = BXc - 1590, BYc - 430
    js = f"""
  camK("#{p}-world",{BXc:.0f},{BYc:.0f},[[0,1.08],[{t_inside - 0.4:.2f},1.0,"sine.inOut"],[{t_inside + 0.7:.2f},4.2,"power3.in"],[{dur:.2f},4.4,"none"]]);
  pop("#{p}-orbL",0.3,0.4,0.8); pop("#{p}-orbR",0.5,0.4,0.8);
  rise("#{p}-l1 span",0.5); rise("#{p}-l2 span",0.7);
  tl.fromTo("#{p}-orbLI",{{y:0}},{{y:-14,duration:1.1,repeat:3,yoyo:true,ease:"sine.inOut"}},0.4);
  tl.fromTo("#{p}-orbRI",{{y:-14}},{{y:0,duration:1.1,repeat:3,yoyo:true,ease:"sine.inOut"}},0.4);
  tl.fromTo("#{pp}-brain",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.08,transformOrigin:"50% 50%",duration:0.25,repeat:1,yoyo:true}},{t_brain:.2f});
  enter("#{p}-gears",{t_same:.2f},0.3);
  tl.fromTo("#{p}-g1",{{rotation:0,transformOrigin:"50% 50%"}},{{rotation:360,transformOrigin:"50% 50%",duration:{dur - t_same:.2f},ease:"none"}},{t_same:.2f});
  tl.fromTo("#{p}-g2",{{rotation:0,transformOrigin:"50% 50%"}},{{rotation:-500,transformOrigin:"50% 50%",duration:{dur - t_same:.2f},ease:"none"}},{t_same:.2f});
  rise("#{p}-t1 span",{t_same:.2f});
  enter("#{p}-pathL",{t_memory:.2f},0.4); enter("#{p}-pathR",{t_memory + 0.2:.2f},0.4);
  tl.fromTo("#{p}-pathL",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-260}},duration:3,ease:"none"}},{t_memory:.2f});
  tl.fromTo("#{p}-pathR",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-260}},duration:3,ease:"none"}},{t_memory:.2f});
  tl.fromTo("#{pp}-eye",{{x:0}},{{x:-4,duration:0.3}},{t_false - 0.4:.2f});
  tl.fromTo("#{p}-orbL",{{x:0,y:0,scale:1,transformOrigin:"50% 50%"}},{{keyframes:{{x:[0,{dx_l * .45:.0f},{dx_l:.0f}],y:[0,-110,{dy_l:.0f}]}},scale:0.25,transformOrigin:"50% 50%",duration:0.8,ease:"power2.in",immediateRender:false}},{t_false - 0.3:.2f});
  vanish("#{p}-orbL",{t_false + 0.45:.2f},0.15); vanish("#{p}-pathL",{t_false - 0.35:.2f},0.25);
  tl.fromTo("#{p}-flash",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:0.9,scale:1.4,transformOrigin:"50% 50%",duration:0.25,yoyo:true,repeat:1}},{t_false + 0.45:.2f});
  tl.fromTo("#{pp}-eye",{{x:-4}},{{x:4,duration:0.3,immediateRender:false}},{t_true - 0.4:.2f});
  tl.fromTo("#{p}-orbR",{{x:0,y:0,scale:1,transformOrigin:"50% 50%"}},{{keyframes:{{x:[0,{dx_r * .45:.0f},{dx_r:.0f}],y:[0,-110,{dy_r:.0f}]}},scale:0.25,transformOrigin:"50% 50%",duration:0.8,ease:"power2.in",immediateRender:false}},{t_true - 0.3:.2f});
  vanish("#{p}-orbR",{t_true + 0.45:.2f},0.15); vanish("#{p}-pathR",{t_true - 0.35:.2f},0.25);
  tl.fromTo("#{p}-flash",{{opacity:0,scale:0.4}},{{opacity:0.9,scale:1.4,duration:0.25,yoyo:true,repeat:1,immediateRender:false}},{t_true + 0.45:.2f});
  tl.fromTo("#{pp}-eye",{{x:4}},{{x:0,duration:0.3,immediateRender:false}},{t_true + 0.6:.2f});
  slideOut("#{p}-l1 span",{t_false + 0.3:.2f}); slideOut("#{p}-l2 span",{t_true + 0.3:.2f});
  slideOut("#{p}-t1 span",{t_inside - 0.5:.2f});
  enter("#{p}-inside",{t_inside + 0.35:.2f},0.5);
  rise("#{p}-t2 span",{t_inside + 0.2:.2f});
  pop("#{p}-i1",{t_inside + 0.5:.2f},0.3,0.8); pop("#{p}-i2",{t_inside + 0.7:.2f},0.3,0.8);
  tl.fromTo("#{p}-i1b",{{y:0}},{{y:-10,duration:0.9,repeat:5,yoyo:true,ease:"sine.inOut"}},{t_inside + 1.2:.2f});
  tl.fromTo("#{p}-i2b",{{y:-10}},{{y:0,duration:0.9,repeat:5,yoyo:true,ease:"sine.inOut"}},{t_inside + 1.2:.2f});
  rise("#{p}-t3 span",{t_not:.2f});
  tl.fromTo("#{p}-i1",{{x:0,y:0}},{{keyframes:{{x:[0,176,353,176,0],y:[0,-50,0,50,0]}},duration:1.6,ease:"power1.inOut",immediateRender:false}},{t_not + 0.6:.2f});
  tl.fromTo("#{p}-i2",{{x:0,y:0}},{{keyframes:{{x:[0,-176,-353,-176,0],y:[0,50,0,-50,0]}},duration:1.6,ease:"power1.inOut",immediateRender:false}},{t_not + 0.6:.2f});
  tl.fromTo("#{p}-q",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.6,ease:"elastic.out(1,0.45)"}},{t_diff - 0.3:.2f});
""" + person_idle(pp, dur, (1.6, 4.3, 7.7))
    return comp(p, dur, svg, html, js, extra, seed=6)


# ---------------------------------------------------------------- writing 7: memory is not a sealed file
def writing_7():
    SC, SG = "writing", 7
    p = "writing_7"
    start, dur = seg(SC, SG)
    t_alarm, t_memory, t_file, t_sealed, t_edit, t_outside, t_write, t_other, t_how, t_trust, t_own = (
        3.04, 3.74, 4.87, 5.48, 7.43,
        8.36, 11.01, 11.69, 12.78, 13.44, 13.93)
    lines = "".join(f'<rect x="-220" y="{-215 + k * 40}" width="{410 if k % 3 else 300}" height="12" rx="6" fill="#8a7f68" opacity=".45"/>' for k in range(9))
    strikes = "".join(f'<path class="strike" d="M-226 {-209 + k * 40} L{-226 + (410 if k % 3 else 300) + 12} {-209 + k * 40}" stroke="#ff4f7d" stroke-width="7" stroke-linecap="round" stroke-dasharray="440" stroke-dashoffset="440"/>' for k in (1, 3, 4, 6))
    rewrites = "".join(f'<path class="rewrite" d="M-210 {-196 + k * 40} c 30 -20 50 14 80 -4 s 50 10 80 -6 s 50 12 84 -4" fill="none" stroke="#ff4fa3" stroke-width="6" stroke-linecap="round" stroke-dasharray="300" stroke-dashoffset="300"/>' for k in (1, 3, 4, 6))
    sheet = lines + strikes + rewrites
    flap = (f'<text x="-40" y="10" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="76" fill="#eef1f7">memory</text>'
              f'<g transform="translate(220 40)"><g id="{p}-seal"><g id="{p}-sL"><path d="M0 -62 A62 62 0 0 0 0 62 L8 30 L-6 0 L10 -30 Z" fill="#d1224f" stroke="#7a1236" stroke-width="4"/></g>'
              f'<g id="{p}-sR"><path d="M0 -62 A62 62 0 0 1 0 62 L8 30 L-6 0 L10 -30 Z" fill="#e8365f" stroke="#7a1236" stroke-width="4"/></g>'
              f'<circle r="34" fill="none" stroke="#ff9bb0" stroke-width="4" opacity=".7"/></g></g>')
    extra = folder_defs(p) + (f'<radialGradient id="{p}-lamp" cx="50%" cy="40%" r="50%"><stop offset="0" stop-color="#ffd98a" stop-opacity=".55"/>'
                             f'<stop offset="1" stop-color="#ffb23e" stop-opacity="0"/></radialGradient>')
    # another person: the same figure.py parts with a dark coat, different skin and hair, magenta tie (the pen color)
    OTHER = {G.WORK["torso"]: "#3a2f5a", G.HAIR: "#cfcfdc", G.SKIN: "#c98e66", G.TIE: "#38e8a8"}
    OX, OY, OS = 1640, 950, 1.05                       # other person standing, mirrored
    (sx, sy), (hx, hy) = anchor("work", "standing", "shoulder_arm"), anchor("work", "standing", "hand_l")
    a = math.radians(-75)                               # raised arm (same rotation as the tween), in local space
    rx, ry = sx + (hx - sx) * math.cos(a) - (hy - sy) * math.sin(a), sy + (hx - sx) * math.sin(a) + (hy - sy) * math.cos(a)
    HAND = (OX - hx * OS, OY + hy * OS)                 # resting hand on screen
    PEN = (HAND[0] + 12, HAND[1] + 10)                   # pen tip at rest: the hand holds it near the tip, pen body pointing away from the body
    CX0, CY0 = 1250, 400                               # pen group origin (the tip)
    HX7, HY7 = round(OX - rx * OS), round(OY + ry * OS)  # hand with the arm raised
    # part B: the person's room, with pictures of moments from their life on the wall
    FRAMES = [("family", 230, 205, .82, -3), ("birthday", 520, 190, .82, 2), ("graduation", 810, 210, .82, -2),
          ("car", 1110, 195, .8, 3), ("beach", 1410, 210, .8, -2), ("dog", 1700, 195, .8, 2)]
    frames = "".join(G.picture(f"{p}-q{k}", t, x, y, s, r) +
                      f'<g transform="translate({x} {y}) rotate({r}) scale({s})"><g class="mx" opacity="0">'
                      f'<path d="M-96 -40 c 30 -34 60 26 96 -8 s 60 30 92 -22 M-90 30 c 40 -20 70 30 110 0 s 40 -10 70 10" fill="none" stroke="#ff4fa3" stroke-width="11" stroke-linecap="round"/></g></g>'
                      for k, (t, x, y, s, r) in enumerate(FRAMES))
    room = (f'<rect x="0" y="940" width="1920" height="140" fill="#0b0828" opacity=".7"/><line x1="0" y1="940" x2="1920" y2="940" stroke="#8d7bff" stroke-width="4" opacity=".55"/>'
            f'<ellipse cx="470" cy="975" rx="330" ry="34" fill="#2a1d70" opacity=".6"/>'
            f'<ellipse cx="780" cy="560" rx="230" ry="260" fill="url(#{p}-lamp)"/>'
            f'<path d="M780 940 L780 560" stroke="#8d7bff" stroke-width="9" stroke-linecap="round"/><ellipse cx="780" cy="944" rx="60" ry="12" fill="#2a1d70" stroke="#8d7bff" stroke-width="4"/>'
            f'<path d="M716 560 L844 560 L816 470 L744 470 Z" fill="#ffd27a" stroke="#d98a1e" stroke-width="4" stroke-linejoin="round"/>')
    svg = f"""<g id="{p}-A">
 <g transform="translate(900 560)"><g id="{p}-folderW">{folder(p, sheet, flap)}</g></g>
 <g id="{p}-otherW" opacity="0">
  {human(p + "o", "work", "standing", OX, OY, OS, mirror=True, colors=OTHER, scene=p)}
  <g transform="translate({CX0} {CY0})"><g id="{p}-pen"><g transform="rotate(-50) scale(.8)"><rect x="-14" y="-200" width="30" height="180" rx="10" fill="#ff4fa3" stroke="#7a1236" stroke-width="4"/><path d="M-14 -20 L16 -20 L1 12 Z" fill="#2a1d70"/></g></g></g>
 </g>
 <path id="{p}-wire2" d="M{HX7} {HY7} L{HX7} {HY7}" fill="none" stroke="#ff4fa3" stroke-width="5" stroke-dasharray="12 10" stroke-linecap="round" opacity="0" filter="url(#{p}-glow)"/>
 <path id="{p}-wire" d="M{HAND[0]:.0f} {HAND[1] - 20:.0f} C 1480 560 1300 400 1110 330" fill="none" stroke="#ff4fa3" stroke-width="6" stroke-dasharray="14 11" opacity="0"/>
 <rect id="{p}-alarm" width="1920" height="1080" fill="#ff1f5a" opacity="0"/>
</g>
<g id="{p}-B" opacity="0">
 {room}
 {frames}
 {human(p + "v", "home", "sitting", 430, 940, 1.15, scene=p)}
</g>"""
    html = (mono(f"{p}-a1", "SEALED FILE", "left:0;right:0;text-align:center;top:36px", "#ffd27a", 64) +
            f'<div id="{p}-strikeLine" style="position:absolute;left:692px;top:77px;width:536px;height:8px;background:#ff4f7d;border-radius:4px;transform:scaleX(0);transform-origin:0 50%;box-shadow:0 0 18px #ff4f7d"></div>' +
            mono(f"{p}-a2", "EDITED FROM THE OUTSIDE", "left:0;right:0;text-align:center;top:36px", "#ff9bd0", 64) +
            mono(f"{p}-a3", "SOMEONE ELSE", "left:0;right:0;text-align:center;top:920px", "#ff9bd0", 64) +
            headline(f"{p}-q1", "How do you trust", "left:930px;top:340px;font-size:108px;color:#eef1f7") +
            headline(f"{p}-q2", "your own?", "left:930px;top:500px;font-size:150px;color:#ffd98a"))
    js = f"""
  camK("#{p}-A",900,520,[[0,1.15],[{t_sealed:.2f},1.0,"sine.inOut"],[{t_write:.2f},0.98],[{t_how:.2f},0.9,"sine.inOut"]]);
  tl.fromTo("#{p}-folderW",{{y:640,rotation:6,transformOrigin:"50% 50%"}},{{y:0,rotation:0,transformOrigin:"50% 50%",duration:1.0,ease:"back.out(1.3)"}},0.1);
  tl.fromTo("#{p}-alarm",{{opacity:0}},{{opacity:0.22,duration:0.08,repeat:3,yoyo:true}},{t_alarm:.2f});
  tl.fromTo("#{p}-folderW",{{x:0}},{{x:8,duration:0.05,repeat:7,yoyo:true,ease:"none",immediateRender:false}},{t_alarm:.2f});
  tl.fromTo("#{p}-seal",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.2,transformOrigin:"50% 50%",duration:0.2,repeat:1,yoyo:true}},{t_memory:.2f});
  rise("#{p}-a1 span",{t_file:.2f});
  tl.fromTo("#{p}-strikeLine",{{scaleX:0}},{{scaleX:1,duration:0.4,ease:"power2.out"}},{t_sealed + 0.3:.2f});
  tl.fromTo("#{p}-sL",{{x:0,y:0,rotation:0,transformOrigin:"50% 50%"}},{{x:-60,y:260,rotation:-50,transformOrigin:"50% 50%",duration:0.9,ease:"power2.in"}},{t_sealed + 0.3:.2f});
  tl.fromTo("#{p}-sR",{{x:0,y:0,rotation:0,transformOrigin:"50% 50%"}},{{x:70,y:280,rotation:60,transformOrigin:"50% 50%",duration:0.9,ease:"power2.in"}},{t_sealed + 0.3:.2f});
  vanish("#{p}-seal",{t_sealed + 0.9:.2f},0.3);
  tl.fromTo("#{p}-flap",{{scaleY:1,skewX:0,transformOrigin:"50% 100%"}},{{scaleY:0.66,skewX:-8,transformOrigin:"50% 100%",duration:0.5,ease:"back.out(2)"}},{t_sealed + 0.9:.2f});
  tl.fromTo("#{p}-sheet",{{y:0}},{{y:-170,duration:0.6,ease:"back.out(1.5)"}},{t_sealed + 1.0:.2f});
  slideOut("#{p}-a1 span",{t_edit - 0.5:.2f}); tl.fromTo("#{p}-strikeLine",{{opacity:1}},{{opacity:0,duration:0.3}},{t_edit - 0.5:.2f});
  rise("#{p}-a2 span",{t_edit:.2f});
  enter("#{p}-otherW",{t_edit - 0.7:.2f},0.4);
  tl.fromTo("#{p}-otherW",{{x:320}},{{x:0,duration:0.7,ease:"power3.out"}},{t_edit - 0.7:.2f});
  tl.fromTo("#{p}o-arm",{{rotation:0,{shoulder("work", "standing")}}},{{rotation:-75,{shoulder("work", "standing")},duration:0.4,ease:"back.out(1.6)"}},{t_edit - 0.2:.2f});
  tl.fromTo("#{p}o-arm",{{rotation:-75,{shoulder("work", "standing")}}},{{rotation:0,{shoulder("work", "standing")},duration:0.5,ease:"power2.inOut",immediateRender:false}},{t_write - 0.1:.2f});
  tl.fromTo("#{p}-pen",{{x:{PEN[0] - CX0:.0f},y:{PEN[1] - CY0:.0f}}},{{keyframes:{{x:[{PEN[0] - CX0:.0f},-560,-170,-560,-170,-560,-170,-560,-170,{PEN[0] - CX0:.0f}],y:[{PEN[1] - CY0:.0f},-179,-179,-99,-99,-59,-59,21,21,{PEN[1] - CY0:.0f}]}},duration:{t_write + 0.3 - t_edit:.2f},ease:"power1.inOut"}},{t_edit:.2f});
  enter("#{p}-wire2",{t_edit + 0.25:.2f},0.25); vanish("#{p}-wire2",{t_write - 0.2:.2f},0.2);
  var F2=document.getElementById("{p}-wire2");
  tl.fromTo({{k:0}},{{k:0}},{{k:1,duration:{t_write - t_edit:.2f},ease:"none",onUpdate:function(){{
    var x={CX0 + 8}+gsap.getProperty("#{p}-pen","x"), y={CY0 + 9}+gsap.getProperty("#{p}-pen","y");
    F2.setAttribute("d","M{HX7} {HY7} Q "+(({HX7}+x)/2)+" "+(Math.min({HY7},y)-120)+" "+x+" "+y);}}}},{t_edit:.2f});
  tl.fromTo("#{p}-sheet .strike",{{attr:{{"stroke-dashoffset":440}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.35,stagger:0.3}},{t_edit + 0.3:.2f});
  tl.fromTo("#{p}-sheet .rewrite",{{attr:{{"stroke-dashoffset":300}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.45,stagger:0.45}},{t_outside + 0.3:.2f});
  slideOut("#{p}-a2 span",{t_write:.2f});
  tl.fromTo("#{p}o-eye",{{x:0}},{{x:3,duration:0.3}},{t_edit:.2f});
  enter("#{p}-wire",{t_other - 0.2:.2f},0.3);
  tl.fromTo("#{p}-wire",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-150}},duration:1.2,ease:"none",immediateRender:false}},{t_other - 0.2:.2f});
  tl.fromTo("#{p}o-headW",{{rotation:0,{neck("work", "standing")}}},{{rotation:-6,{neck("work", "standing")},duration:0.3,yoyo:true,repeat:1}},{t_other:.2f});
  rise("#{p}-a3 span",{t_other - 0.1:.2f});
  tl.fromTo("#{p}-A",{{opacity:1}},{{opacity:0,duration:0.45}},{t_how - 0.35:.2f});
  slideOut("#{p}-a3 span",{t_how - 0.35:.2f},0.4);
  enter("#{p}-B",{t_how - 0.1:.2f},0.45);
  tl.fromTo("#{p}-B",{{scale:1.12,svgOrigin:"460 560"}},{{scale:1,svgOrigin:"460 560",duration:{dur - t_how:.2f},ease:"power2.out"}},{t_how - 0.1:.2f});
  rise("#{p}-q1 span",{t_how:.2f},0.8); rise("#{p}-q2 span",{t_own:.2f},0.8);
  var QS="{",".join(f"#{p}-q{k}" for k in range(len(FRAMES)))}";
  tl.fromTo(QS,{{y:0}},{{y:-8,duration:1.0,repeat:2,yoyo:true,ease:"sine.inOut",stagger:0.15}},{t_how:.2f});
  tl.fromTo("#{p}-B .mx",{{opacity:0}},{{opacity:1,duration:0.08,repeat:5,yoyo:true,stagger:0.17}},{t_trust:.2f});
  tl.fromTo("#{p}-B .mx",{{opacity:0}},{{opacity:0.9,duration:0.2,immediateRender:false}},{t_trust + 1.4:.2f});
  tl.fromTo(QS,{{x:-5}},{{x:5,duration:0.05,repeat:9,yoyo:true,ease:"none",stagger:0.12,immediateRender:false}},{t_trust:.2f});
  tl.fromTo("#{p}v-eye",{{x:0,y:0}},{{x:2,y:-3,duration:0.3}},{t_how:.2f});
  tl.fromTo("#{p}v-headW",{{rotation:0,{neck("home", "sitting")}}},{{rotation:-8,{neck("home", "sitting")},duration:0.6,ease:"power2.inOut"}},{t_how + 0.1:.2f});
""" + G.figure_idle(p + "o", dur, (9.6, 11.3)) + G.figure_idle(p + "v", dur, (14.6, 15.8))
    return comp(p, dur, svg, html, js, extra, seed=12)


from art2 import BRAIN_SIL


def cursor(color):
    return f'<path d="M0 0 L0 46 L12 35 L21 55 L30 51 L21 31 L38 31 Z" fill="{color}" stroke="#fff" stroke-width="3.5" stroke-linejoin="round"/>'


def star(r, color):
    pts = " ".join(f"{(r if k % 2 == 0 else r * .45) * math.cos(-math.pi / 2 + k * math.pi / 5):.1f},{(r if k % 2 == 0 else r * .45) * math.sin(-math.pi / 2 + k * math.pi / 5):.1f}" for k in range(10))
    return f'<polygon points="{pts}" fill="{color}" stroke="#fff6c8" stroke-width="3" stroke-linejoin="round"/>'


# ---------------------------------------------------------------- mapping 3: slices, microscope, AI and volunteers
def mapping_3():
    SC, SG = "mapping", 3
    p = "mapping_3"
    start, dur = seg(SC, SG)
    t_slices, t_layers, t_photo, t_mic, t_ai, t_trace, t_neurons, t_cursors, t_researchers, t_volunteers, t_fix, t_errors, t_game = (
        1.25, 1.94, 3.65, 4.22, 6.46,
        8.34, 9.43, 10.4, 11.3, 12.56,
        13.55, 14.63, 15.26)
    N, X0 = 9, 560
    slices = []
    for k in reversed(range(N)):
        f = 0.55 + 0.45 * math.sin(math.pi * (k + .5) / N)
        sx, sy = 1.3 * f, 0.30 * f
        yc = 430 + k * 22
        rg = random.Random(k)
        dots = "".join(f'<circle cx="{rg.uniform(-150, 150) * f:.0f}" cy="{rg.uniform(-26, 26) * f:.0f}" r="{rg.uniform(3, 6):.1f}" fill="{rg.choice(["#3be0ff", "#ff4fa3", "#8d7bff", "#ffd27a"])}"/>' for _ in range(14))
        slices.append(f'<g transform="translate({X0} {yc})"><g id="{p}-s{k}"><path transform="translate(0 14) scale({sx:.3f} {sy:.3f})" d="{BRAIN_SIL}" fill="#13235e"/>'
                   f'<path transform="scale({sx:.3f} {sy:.3f})" d="{BRAIN_SIL}" fill="url(#{p}-slice)" stroke="#7fdcff" stroke-width="3" vector-effect="non-scaling-stroke"/>{dots}</g></g>')
    # microscope photo panel
    PX, PY, PW = 1100, 180, 680
    rg = random.Random(21)
    cells = []
    tries = 0
    while len(cells) < 140 and tries < 20000:
        tries += 1
        r = rg.uniform(20, 58)
        x, y = rg.uniform(PX, PX + PW), rg.uniform(PY, PY + PW)
        if all(math.hypot(x - a, y - b) > r + c + 4 for a, b, c in cells):
            cells.append((round(x), round(y), round(r)))
    colors = ["#3be0ff", "#ff4fa3", "#8d7bff", "#ffb23e", "#38e8a8", "#5fb7ff", "#ff9bd0"]
    inside = [i for i, (x, y, r) in enumerate(cells) if PX + 70 < x < PX + PW - 70 and PY + 70 < y < PY + PW - 70 and r > 34]
    errors = random.Random(4).sample(inside, 7)
    base = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{"#9c9cae" if i % 3 else "#868698"}" stroke="#15151f" stroke-width="6"/>'
                   f'<ellipse cx="{x - r * .3:.0f}" cy="{y - r * .2:.0f}" rx="{r * .22:.0f}" ry="{r * .12:.0f}" fill="#55556a" opacity=".7"/>' for i, (x, y, r) in enumerate(cells))
    order = sorted(range(len(cells)), key=lambda i: cells[i][1])
    cl = "".join(f'<circle class="cl" cx="{cells[i][0]}" cy="{cells[i][1]}" r="{cells[i][2] - 3}" fill="{colors[i % 7]}" opacity="0"/>' if i not in errors else
                 f'<circle class="cl" cx="{cells[i][0]}" cy="{cells[i][1]}" r="{cells[i][2] - 3}" fill="#ff2a55" opacity="0"/>' for i in order)
    ok = "".join(f'<circle id="{p}-ok{j}" cx="{cells[i][0]}" cy="{cells[i][1]}" r="{cells[i][2] - 3}" fill="{colors[i % 7]}" opacity="0"/>'
                 f'<g id="{p}-x{j}" opacity="0" stroke="#fff" stroke-width="7" stroke-linecap="round"><path d="M{cells[i][0] - 14} {cells[i][1] - 14} l28 28 M{cells[i][0] + 14} {cells[i][1] - 14} l-28 28"/></g>'
                 f'<circle id="{p}-bu{j}" cx="{cells[i][0]}" cy="{cells[i][1]}" r="{cells[i][2]}" fill="none" stroke="#fff6c8" stroke-width="6" opacity="0"/>' for j, i in enumerate(errors))
    origins = [(1000, 1150), (1960, 1000), (1990, 300), (1300, -80), (900, -60), (1990, 650), (1700, 1160)]
    cursors = "".join(f'<g id="{p}-c{j}" opacity="0"><g transform="scale(1.3)">{cursor(colors[(j * 2) % 7])}</g></g>' for j in range(7))
    stars = "".join(f'<g transform="translate({x} {y})"><g class="star" opacity="0">{star(r, c)}</g></g>' for x, y, r, c in
                       [(1080, 160, 34, "#ffd23e"), (1785, 195, 28, "#ff9bd0"), (1780, 852, 36, "#38e8a8"), (1070, 860, 26, "#3be0ff"), (1440, 130, 30, "#ffd23e"), (1792, 560, 24, "#ffd23e")])
    extra = (f'<linearGradient id="{p}-slice" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a6fa8"/><stop offset="1" stop-color="#3a2a8c"/></linearGradient>'
             f'<linearGradient id="{p}-mic" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3a3a8a"/><stop offset=".5" stop-color="#7a7ad0"/><stop offset="1" stop-color="#2a2a6a"/></linearGradient>'
             f'<linearGradient id="{p}-beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bff4ff" stop-opacity=".9"/><stop offset="1" stop-color="#7fe6ff" stop-opacity=".15"/></linearGradient>'
             f'<clipPath id="{p}-panelClip"><rect x="{PX}" y="{PY}" width="{PW}" height="{PW}" rx="10"/></clipPath>')
    f0 = 0.55 + 0.45 * math.sin(math.pi * .5 / N)
    hw = 210 * 1.3 * f0
    svg = f"""
<ellipse cx="{X0}" cy="860" rx="320" ry="28" fill="#05031a" opacity=".45"/>
<g id="{p}-stack">{"".join(slices)}</g>
<rect id="{p}-blade" x="200" y="300" width="720" height="8" rx="4" fill="#bff4ff" opacity="0" filter="url(#{p}-glow)"/>
<polygon id="{p}-beam" points="{X0 - 12},236 {X0 + 12},236 {X0 + hw:.0f},300 {X0 - hw:.0f},300" fill="url(#{p}-beam)" opacity="0"/>
<g transform="translate({X0} 0)"><g id="{p}-micro"><g filter="url(#{p}-shadow)">
 <rect x="-72" y="-260" width="144" height="340" rx="22" fill="url(#{p}-mic)" stroke="#8d7bff" stroke-width="4"/>
 <rect x="-96" y="58" width="192" height="30" rx="12" fill="url(#{p}-mic)" stroke="#bff4ff" stroke-width="3"/>
 <rect x="-82" y="102" width="164" height="26" rx="10" fill="url(#{p}-mic)" stroke="#8d7bff" stroke-width="3"/>
 <path d="M-60 132 L60 132 L22 230 L-22 230 Z" fill="url(#{p}-mic)" stroke="#8d7bff" stroke-width="3"/></g>
 <rect x="-40" y="-120" width="80" height="12" rx="6" fill="#3be0ff" opacity=".7"/><rect x="-40" y="-90" width="50" height="12" rx="6" fill="#ffb23e" opacity=".7"/>
 <circle id="{p}-tip" cx="0" cy="234" r="11" fill="#bff4ff" filter="url(#{p}-glow)"/></g></g>
<g id="{p}-ghost" opacity="0"><path transform="translate({X0} 430) scale({1.3 * f0:.3f} {0.3 * f0:.3f})" d="{BRAIN_SIL}" fill="none" stroke="#bff4ff" stroke-width="4" vector-effect="non-scaling-stroke"/></g>
<g id="{p}-panel" opacity="0"><rect x="{PX - 16}" y="{PY - 16}" width="{PW + 32}" height="{PW + 32}" rx="18" fill="#0e0c26" stroke="#8d7bff" stroke-width="4" filter="url(#{p}-shadow)"/>
 <g clip-path="url(#{p}-panelClip)"><rect x="{PX}" y="{PY}" width="{PW}" height="{PW}" fill="#3a3a48"/>{base}<g>{cl}</g>{ok}
 <rect id="{p}-scan" x="{PX}" y="{PY}" width="{PW}" height="10" fill="#3be0ff" opacity="0" filter="url(#{p}-glow)"/></g>
 <rect id="{p}-border" x="{PX - 16}" y="{PY - 16}" width="{PW + 32}" height="{PW + 32}" rx="18" fill="none" stroke="#38e8a8" stroke-width="10" opacity="0" filter="url(#{p}-glow)"/></g>
{cursors}{stars}
<rect id="{p}-flash" width="1920" height="1080" fill="#eef8ff" opacity="0"/>"""
    html = "".join(mono(f"{p}-l{k}", txt, "left:0;right:0;text-align:center;top:910px", color, 76) for k, (txt, color) in enumerate(
        [("ULTRA-THIN LAYERS", "#bff4ff"), ("ELECTRON MICROSCOPE", "#c9b8ff"), ("ARTIFICIAL INTELLIGENCE", "#7fe6ff"),
         ("RESEARCHERS AND VOLUNTEERS", "#ffd27a"), ("LIKE IN A GAME", "#7ff5c8")]))
    js = f"""
  camK("#{p}-cam",620,520,[[0,1.5],[{t_layers + 0.6:.2f},1.25,"sine.inOut"],[{t_mic + 1.3:.2f},1.0],[{dur:.2f},1.0]]);
  tl.fromTo("#{p}-stack",{{opacity:0,y:40}},{{opacity:1,y:0,duration:0.7,ease:"power3.out"}},0.05);
  tl.fromTo("#{p}-blade",{{opacity:0,y:0}},{{opacity:1,y:240,duration:0.55,ease:"power1.inOut"}},{t_slices - 0.1:.2f});
  vanish("#{p}-blade",{t_slices + 0.45:.2f},0.15);
  {";".join(f'tl.fromTo("#{p}-s{k}",{{y:0}},{{y:{(300 + k * 62) - (430 + k * 22)},duration:0.9,ease:"back.out(1.4)"}},{t_layers - 0.2 + (8 - k) * 0.04:.2f})' for k in range(N))};
  tl.fromTo("#{p}-stack",{{x:0}},{{x:0}},0);
  rise("#{p}-l0 span",{t_layers:.2f});
  tl.fromTo("#{p}-micro",{{y:-520}},{{y:0,duration:0.8,ease:"back.out(1.2)"}},{t_photo - 0.5:.2f});
  slideOut("#{p}-l0 span",{t_mic - 0.4:.2f},0.4); rise("#{p}-l1 span",{t_mic:.2f});
  tl.fromTo("#{p}-beam",{{opacity:0}},{{opacity:0.9,duration:0.12,repeat:5,yoyo:true}},{t_photo:.2f});
  tl.fromTo("#{p}-flash",{{opacity:0}},{{opacity:0.6,duration:0.06,yoyo:true,repeat:1}},{t_photo + 0.1:.2f});
  tl.fromTo("#{p}-flash",{{opacity:0}},{{opacity:0.6,duration:0.06,yoyo:true,repeat:1,immediateRender:false}},{t_mic + 0.6:.2f});
  tl.fromTo("#{p}-panel",{{opacity:0,scale:0.25,svgOrigin:"{PX + PW / 2} {PY + PW / 2}"}},{{opacity:1,scale:1,svgOrigin:"{PX + PW / 2} {PY + PW / 2}",duration:0.8,ease:"back.out(1.4)"}},{t_mic + 1.3:.2f});
  tl.fromTo("#{p}-beam",{{opacity:0.9}},{{opacity:0.35,duration:0.3,immediateRender:false}},{t_mic + 1.3:.2f});
  slideOut("#{p}-l1 span",{t_ai - 0.4:.2f},0.4); rise("#{p}-l2 span",{t_ai:.2f});
  tl.fromTo("#{p}-scan",{{opacity:0,y:0}},{{opacity:1,y:{PW - 10},duration:{t_neurons + 0.6 - t_ai:.2f},ease:"none"}},{t_ai:.2f});
  vanish("#{p}-scan",{t_neurons + 0.6:.2f},0.3);
  tl.fromTo("#{p}-panel .cl",{{opacity:0}},{{opacity:0.78,duration:0.25,stagger:{(t_neurons + 0.5 - t_ai) / len(cells):.4f}}},{t_ai:.2f});
  {";".join(f'enter("#{p}-x{j}",{t_neurons + 0.2:.2f},0.2)' for j in range(7))};
  slideOut("#{p}-l2 span",{t_cursors - 0.2:.2f},0.4); rise("#{p}-l3 span",{t_researchers - 0.3:.2f});
  var CFROM={json.dumps(origins)}, CTO={json.dumps([[cells[i][0] - 6, cells[i][1] - 4] for i in errors])};
  for(var j=0;j<7;j++){{
    tl.set("#{p}-c"+j,{{x:CFROM[j][0],y:CFROM[j][1]}},0);
    tl.fromTo("#{p}-c"+j,{{opacity:0}},{{opacity:1,duration:0.2}},{t_cursors:.2f}+j*0.28);
    tl.to("#{p}-c"+j,{{x:CTO[j][0],y:CTO[j][1],duration:1.3,ease:"power2.inOut"}},{t_cursors:.2f}+j*0.28);
    var tc={t_fix:.2f}+j*0.22;
    tl.fromTo("#{p}-c"+j,{{scale:1,transformOrigin:"0% 0%"}},{{scale:0.8,transformOrigin:"0% 0%",duration:0.08,yoyo:true,repeat:1}},tc);
    tl.fromTo("#{p}-ok"+j,{{opacity:0}},{{opacity:0.9,duration:0.15}},tc+0.05);
    tl.fromTo("#{p}-x"+j,{{opacity:1}},{{opacity:0,duration:0.1,immediateRender:false}},tc+0.05);
    tl.fromTo("#{p}-bu"+j,{{opacity:1,scale:1,transformOrigin:"50% 50%"}},{{opacity:0,scale:2.2,transformOrigin:"50% 50%",duration:0.6,ease:"power2.out",immediateRender:false}},tc+0.05);
  }}
  slideOut("#{p}-l3 span",{t_game - 0.4:.2f},0.4); rise("#{p}-l4 span",{t_game:.2f});
  tl.fromTo("#{p}-border",{{opacity:0}},{{opacity:1,duration:0.2,repeat:3,yoyo:true}},{t_game:.2f});
  tl.fromTo("#{p}-border",{{opacity:0}},{{opacity:0.8,duration:0.3,immediateRender:false}},{t_game + 0.9:.2f});
  tl.fromTo("#{p} .star",{{opacity:0,scale:0,rotation:-90,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,rotation:0,transformOrigin:"50% 50%",duration:0.6,ease:"elastic.out(1,0.45)",stagger:0.08}},{t_game:.2f});
"""
    js = js.replace(f'"#{p} .star"', f'"#{p}-cam .star"').replace(f'tl.fromTo("#{p}-stack",{{x:0}},{{x:0}},0);', "")
    return comp(p, dur, svg, html, js, extra, seed=13)


# ---------------------------------------------------------------- mapping 4: 33 years against 50 thousand, camera pulls back on a log scale
def mapping_4():
    SC, SG = "mapping", 4
    p = "mapping_4"
    start, dur = seg(SC, SG)
    t_years, t_work, t_without, t_ai, t_almost, t_50, t_thousand = (0.43, 1.16, 3.58, 3.95,
                                                        9.92, 10.09, 11.04)
    PIT, CELL = 70, 60
    S0 = 6 * PIT - 10                      # side of the 33 block
    S = S0 * math.sqrt(50000 / 33)         # side of the 50 thousand block (same area scale)
    FLOOR, CX = 760, 955
    zf = 800 / S
    ox = (820 - CX * zf) / (1 - zf)
    oy = (900 - FLOOR * zf) / (1 - zf)
    L = ox + (1040 - ox) / zf
    cells = []
    for i in range(33):
        r, c = divmod(i, 6)
        cells.append(f'<g transform="translate({750 + c * PIT + 30} {FLOOR - CELL - r * PIT + 30})"><rect class="cc" x="-30" y="-30" width="{CELL}" height="{CELL}" rx="9" fill="#3be0ff" opacity="0"/></g>')
    extra = (f'<pattern id="{p}-pat" patternUnits="userSpaceOnUse" x="{L:.1f}" y="{FLOOR}" width="{PIT}" height="{PIT}"><rect x="5" y="5" width="{CELL}" height="{CELL}" rx="9" fill="#ff4f7d"/></pattern>'
             f'<pattern id="{p}-pat2" patternUnits="userSpaceOnUse" x="{L:.1f}" y="{FLOOR}" width="{S0 * 1.12:.1f}" height="{S0 * 1.12:.1f}"><rect x="{S0 * .06:.1f}" y="{S0 * .06:.1f}" width="{S0}" height="{S0}" rx="30" fill="#ffd0dc" fill-opacity=".22" stroke="#ffe3ea" stroke-width="16"/></pattern>')
    svg = f"""
<line x1="-60000" y1="{FLOOR + 6}" x2="80000" y2="{FLOOR + 6}" stroke="#8d7bff" stroke-width="3" vector-effect="non-scaling-stroke" opacity=".7"/>
<g id="{p}-block">{"".join(cells)}</g>
<g transform="translate(-40 0)"><g id="{p}-scaleRef">
 {human(p + "g", "work", "sitting", 1290, FLOOR, 0.5, scene=p)}
 <rect x="1330" y="{FLOOR - 104}" width="170" height="14" rx="6" fill="#2a1d70" stroke="#8d7bff" stroke-width="3"/>
 <path d="M1350 {FLOOR - 90} L1350 {FLOOR} M1480 {FLOOR - 90} L1480 {FLOOR}" stroke="#8d7bff" stroke-width="6" stroke-linecap="round"/>
 <g transform="translate(1418 {FLOOR - 104})"><g id="{p}-screen"><path d="M-8 0 L-30 -66 L36 -66 L52 0 Z" fill="#3a3a8a" stroke="#bff4ff" stroke-width="3" stroke-linejoin="round"/><path d="M-20 -54 L28 -54 L38 -12 L-6 -12 Z" fill="#3be0ff" opacity=".55"/></g></g>
</g>
</g><g transform="translate(750 {FLOOR + 34})"><g id="{p}-leg" opacity="0"><rect x="0" y="0" width="{CELL}" height="{CELL}" rx="9" fill="#3be0ff"/>
 <text x="{CELL + 26}" y="{CELL - 10}" font-family="IBM Plex Mono" font-weight="500" font-size="54" letter-spacing="6" fill="#bff4ff">= 1 YEAR</text></g></g>
<circle id="{p}-ring" cx="{CX}" cy="{FLOOR - S0 / 2}" r="{0.9 * 45 / zf:.0f}" fill="none" stroke="#3be0ff" stroke-width="5" vector-effect="non-scaling-stroke" opacity="0"/>
<rect id="{p}-big" x="{L:.1f}" y="{FLOOR - S0}" width="{S0}" height="{S0}" fill="url(#{p}-pat)" stroke="#ff9bb0" stroke-width="4" vector-effect="non-scaling-stroke" opacity="0"/>
<rect id="{p}-big2" x="{L:.1f}" y="{FLOOR - S0}" width="{S0}" height="{S0}" fill="url(#{p}-pat2)" opacity="0"/>"""
    html = (text(f"{p}-n1", f'<span id="{p}-n1v">0</span>', "left:110px;top:70px;font-size:170px;color:#bff4ff") +
            mono(f"{p}-a1", "YEARS", "left:120px;top:300px", "#bff4ff", 50) +
            mono(f"{p}-a2", "OF HUMAN WORK", "left:120px;top:375px", "#7fe6ff", 44) +
            mono(f"{p}-a3", "WITHOUT ARTIFICIAL", "left:120px;top:450px", "#ff9bb0", 42) +
            mono(f"{p}-a4", "INTELLIGENCE", "left:120px;top:505px", "#ff9bb0", 42) +
            mono(f"{p}-a5", "ALMOST", "left:124px;top:562px", "#ffd27a", 44) +
            text(f"{p}-n2", f'<span id="{p}-n2v">33</span>', "left:110px;top:588px;font-size:160px;color:#ffd0dc") +
            f'<div id="{p}-arrow" style="position:absolute;left:640px;top:690px;width:380px;height:6px;background:#ff9bb0;border-radius:3px;transform:scaleX(0);transform-origin:0 50%;box-shadow:0 0 14px #ff4f7d"><i style="position:absolute;right:-6px;top:-9px;border-left:22px solid #ff9bb0;border-top:12px solid transparent;border-bottom:12px solid transparent"></i></div>' +
            mono(f"{p}-a6", "YEARS", "left:124px;top:790px", "#ff9bb0", 46) +
            mono(f"{p}-a7", "33 YEARS", "left:778px;width:340px;text-align:center;top:966px", "#7fe6ff", 50) +
            f'<div id="{p}-magnifier" style="position:absolute;left:868px;top:800px;width:160px;height:160px;opacity:0"><svg width="160" height="160" viewBox="0 0 240 240">'
            f'<circle cx="120" cy="120" r="114" fill="#120c3a" stroke="#3be0ff" stroke-width="6"/><line x1="30" y1="182" x2="210" y2="182" stroke="#8d7bff" stroke-width="3"/>'
            + "".join(f'<rect x="{54 + (i % 6) * 22}" y="{158 - (i // 6) * 22}" width="18" height="18" rx="3" fill="#3be0ff"/>' for i in range(33)) + '</svg></div>')
    js = f"""
  camK("#{p}-cam",{ox:.1f},{oy:.1f},[[0,1.1],[{t_without:.2f},1.0,"sine.inOut"],[{t_thousand + 0.1:.2f},{zf:.5f},"power2.inOut"],[{dur:.2f},{zf * 0.97:.5f},"sine.inOut"]]);
  rise("#{p}-n1 > span",0.0,0.6);
  tl.fromTo("#{p}-block .cc",{{opacity:0,scale:0.2,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.45,ease:"back.out(2.5)",stagger:0.05}},0.1);
  count_up("{p}-n1v",0.1,1.75,0,33);
  rise("#{p}-a1 span",{t_years:.2f}); rise("#{p}-a2 span",{t_work:.2f});
  pop("#{p}-leg",{t_years:.2f},0.4,0.6); vanish("#{p}-leg",{t_without + 0.4:.2f},0.4);
  tl.fromTo("#{p}g-eye",{{x:0}},{{x:3,duration:0.2}},0.1);
  tl.set("#{p}g-arm",{{rotation:-60,{shoulder("work", "sitting")}}},0);
  tl.fromTo("#{p}g-arm",{{rotation:-60,{shoulder("work", "sitting")}}},{{rotation:-66,{shoulder("work", "sitting")},duration:0.16,repeat:13,yoyo:true,ease:"sine.inOut"}},0.1);
  enter("#{p}-big",{t_without:.2f},0.3); enter("#{p}-big2",{t_without + 2.5:.2f},1.5);
  rise("#{p}-a3 span",{t_without:.2f}); rise("#{p}-a4 span",{t_ai:.2f});
  rise("#{p}-n2 > span",{t_without + 0.3:.2f}); rise("#{p}-a6 span",{t_without + 0.5:.2f});
  enter("#{p}-ring",{t_thousand - 1.0:.2f},0.6); rise("#{p}-a7 span",{t_thousand - 0.9:.2f}); pop("#{p}-magnifier",{t_thousand - 0.9:.2f},0.4,0.6);
  var G={{l:Math.log({S0})}};
  tl.fromTo(G,{{l:Math.log({S0})}},{{l:Math.log({S:.1f}),duration:{t_thousand + 0.1 - t_without:.2f},ease:"power2.inOut",onUpdate:function(){{
    var s=Math.exp(G.l), e=document.getElementById("{p}-big"); e.setAttribute("width",s); e.setAttribute("height",s); e.setAttribute("y",{FLOOR}-s);
    var u=(G.l-Math.log({S0}))/(Math.log({S:.1f})-Math.log({S0})), z=gsap.getProperty("#{p}-cam","scale"), xw={ox:.1f}+(1470+(1040-1470)*u-{ox:.1f})/z;
    ["{p}-big","{p}-big2","{p}-pat","{p}-pat2"].forEach(function(i){{document.getElementById(i).setAttribute("x",xw);}}); var e2=document.getElementById("{p}-big2"); e2.setAttribute("width",s); e2.setAttribute("height",s); e2.setAttribute("y",{FLOOR}-s);
    var v=33*Math.pow(s/{S0},2); document.getElementById("{p}-n2v").textContent=(v>49990?50000:Math.round(v)).toLocaleString("en-US");}}}},{t_without:.2f});
  rise("#{p}-a5 span",{t_almost:.2f});
  tl.fromTo("#{p}-arrow",{{scaleX:0}},{{scaleX:1,duration:0.5,ease:"power2.out"}},{t_thousand - 0.2:.2f});
  tl.fromTo("#{p}-n2",{{scale:1,transformOrigin:"0% 50%"}},{{scale:1.12,transformOrigin:"0% 50%",duration:0.25,yoyo:true,repeat:1}},{t_thousand:.2f});
""" + G.figure_idle(p + "g", dur, (2.6, 5.0))
    return comp(p, dur, svg, html, js, extra, seed=15)
    # ponytail: the 50,000 counter only works because growth ends exactly at S; if S0 changes, check the rounding


# ---------------------------------------------------------------- mapping 6: Nature 2024 page, the simulation predicts the fly eating
def mapping_6():
    SC, SG = "mapping", 6
    p = "mapping_6"
    start, dur = seg(SC, SG)
    t_activity, t_sim, t_sugar, t_model, t_predict, t_fly, t_eat, t_test, t_real, t_held, t_confirm = (
        0.28, 1.39, 3.79, 4.37, 4.9,
        7.23, 8.4, 9.38, 11.0, 12.6, 13.54)
    W, IH = 600, 2126 / 1600
    mk = [("h1", 1140, 786, 270, 40, "#ffb23e"), ("h2", 576, 822, 870, 40, "#ffb23e"), ("h3", 576, 856, 880, 40, "#ffb23e"), ("h4", 576, 891, 160, 40, "#ffb23e"),
          ("v1", 1326, 925, 128, 40, "#38e8a8"), ("v2", 576, 960, 860, 40, "#38e8a8")]
    pg = page(p, "shiu2024", W, IH, mk)
    network_svg, pts, edge_list = network_rich(f"{p}-r", 11, prefix=p)
    left = min(range(len(pts)), key=lambda k: pts[k][0] + 0.3 * pts[k][1])
    right = max(range(len(pts)), key=lambda k: pts[k][0] - 0.3 * pts[k][1])
    route = path_d(pts, edge_list, left, right)
    NX, NY, NE = 1170, 450, 0.62
    gx, gy = NX + pts[right][0] * NE, NY + pts[right][1] * NE
    sx, sy = NX + pts[left][0] * NE, NY + pts[left][1] * NE
    check_pts = [route[int(len(route) * f)] for f in (0.25, 0.5, 0.75)] + [route[-1]]
    checks = "".join(f'<g transform="translate({NX + x * NE:.0f} {NY + y * NE:.0f})"><g class="ck" opacity="0"><circle r="30" fill="#38e8a8" stroke="#eafff6" stroke-width="4"/><path d="M-13 1 L-4 11 L14 -10" fill="none" stroke="#0b2a20" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g></g>' for x, y in check_pts)
    extra = fly_defs(p) + network_defs(p) + f'<linearGradient id="{p}-sugarG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#d9dcef"/></linearGradient>'
    sugar = (f'<path id="{p}-sugarL" d="M{sx - 10:.0f} {sy + 128:.0f} L{sx:.0f} {sy + 40:.0f}" stroke="#ffd27a" stroke-width="5" stroke-dasharray="10 8" opacity="0"/>'
              f'<g transform="translate({sx - 10:.0f} {sy + 170:.0f})"><g id="{p}-sugarCube" opacity="0">'
              f'<polygon points="0,-40 46,-18 0,4 -46,-18" fill="url(#{p}-sugarG)" stroke="#fff6c8" stroke-width="3"/><polygon points="-46,-18 0,4 0,54 -46,32" fill="#cfd3ea" stroke="#fff6c8" stroke-width="3"/>'
              f'<polygon points="0,4 46,-18 46,32 0,54" fill="#b7bcdc" stroke="#fff6c8" stroke-width="3"/></g></g>')
    svg = f"""
<g transform="translate(110 150) rotate(-2)"><g id="{p}-pg">{pg}</g></g>
<g id="{p}-sim" opacity="0">
 <g transform="translate({NX} {NY}) scale({NE})"><g id="{p}-netW">{network_svg}</g></g>
 <circle id="{p}-pulse" r="16" fill="#ffd23e" filter="url(#{p}-glow)" opacity="0"/>
 <circle id="{p}-start" cx="{sx:.0f}" cy="{sy:.0f}" r="34" fill="none" stroke="#ffb23e" stroke-width="9" opacity="0"/>
 {sugar}
 <path id="{p}-bridge" d="M{gx:.0f} {gy:.0f} C {gx + 120:.0f} {gy - 40:.0f} 1460 600 1532 560" fill="none" stroke="#38e8a8" stroke-width="7" stroke-dasharray="500" stroke-dashoffset="500" stroke-linecap="round" filter="url(#{p}-glow)"/>
 <g transform="translate(1660 560)"><g id="{p}-fly"><g transform="scale(-1.3 1.3)"><g id="{p}-flyBob">{fly_rich(p + "-fl", p)}</g></g></g></g>
 <g id="{p}-sparks" opacity="0" fill="#ffd23e" filter="url(#{p}-glow)"><circle cx="1490" cy="600" r="9"/><circle cx="1468" cy="628" r="6"/><circle cx="1480" cy="660" r="8"/><circle cx="1450" cy="590" r="5"/></g>
 {checks}
</g>
<g transform="translate(1640 270) rotate(4)"><g id="{p}-photo" opacity="0"><g filter="url(#{p}-shadow)"><rect x="-170" y="-130" width="340" height="300" rx="8" fill="#fffaf0"/></g>
 <image href="assets/fly.jpg" x="-152" y="-112" width="304" height="228" preserveAspectRatio="xMidYMid slice"/></g></g>"""
    html = (headline(f"{p}-a1", "simulation", "left:1010px;top:250px;font-size:130px;color:#bff4ff") +
            headline(f"{p}-a2", "sugar", "left:1010px;top:440px;font-size:150px;color:#ffd27a") +
            mono(f"{p}-b0", "SUGAR", f"left:{sx - 160:.0f}px;width:300px;text-align:center;top:{sy + 236:.0f}px", "#ffd27a", 40) +
            mono(f"{p}-b1", "EATING", "left:760px;width:1100px;text-align:center;top:920px", "#ffd27a", 56) +
            mono(f"{p}-b2", "REAL FLIES", "left:760px;width:1100px;text-align:center;top:920px", "#7ff5c8", 56) +
            mono(f"{p}-b3", "PREDICTIONS HELD UP", "left:760px;width:1100px;text-align:center;top:920px", "#7ff5c8", 56))
    js = f"""
  camK("#{p}-cam",380,390,[[0,1.62],[{t_model:.2f},1.5,"sine.inOut"],[{t_model + 1.5:.2f},1.0],[{dur:.2f},1.0]]);
  tl.fromTo("#{p}-pg",{{y:420,rotation:-5,opacity:0}},{{y:0,rotation:0,opacity:1,duration:0.9,ease:"expo.out"}},0.0);
  rise("#{p}-a1 span",{t_sim:.2f}); rise("#{p}-a2 span",{t_sugar:.2f});
  highlight("#{p}-h1",{t_sugar - 0.6:.2f},0.35); highlight("#{p}-h2",{t_sugar - 0.25:.2f},0.6); highlight("#{p}-h3",{t_sugar + 0.35:.2f},0.6); highlight("#{p}-h4",{t_sugar + 0.95:.2f},0.2);
  slideOut("#{p}-a1 span",{t_model - 0.1:.2f}); slideOut("#{p}-a2 span",{t_model:.2f});
  enter("#{p}-sim",{t_model + 0.2:.2f},0.8);
  tl.fromTo("#{p}-netW",{{scale:0.4,opacity:0,transformOrigin:"50% 50%"}},{{scale:1,opacity:1,transformOrigin:"50% 50%",duration:1.2,ease:"power3.out"}},{t_model + 0.2:.2f});
  tl.fromTo("#{p}-r .lobe",{{opacity:0}},{{opacity:1,duration:0.8}},{t_model + 0.3:.2f});
  tl.fromTo("#{p}-r .eds",{{opacity:0}},{{opacity:1,duration:0.8}},{t_model + 0.5:.2f});
  tl.fromTo("#{p}-fly",{{x:400}},{{x:0,duration:1.0,ease:"power3.out"}},{t_model + 0.6:.2f});
  tl.fromTo("#{p}-flyBob",{{y:0,rotation:-2,transformOrigin:"50% 50%"}},{{y:-8,rotation:2,transformOrigin:"50% 50%",duration:0.5,repeat:18,yoyo:true,ease:"sine.inOut"}},{t_model + 1.6:.2f});
  tl.fromTo("#{p}-fl-wings",{{scaleY:1,transformOrigin:"50% 100%"}},{{scaleY:0.3,transformOrigin:"50% 100%",duration:0.05,repeat:{2 * int((dur - t_model - 0.6) / 0.1) - 1},yoyo:true,ease:"none"}},{t_model + 0.6:.2f});
  pop("#{p}-sugarCube",{t_predict - 0.2:.2f},0.3,0.7); enter("#{p}-sugarL",{t_predict:.2f},0.3); rise("#{p}-b0 span",{t_predict:.2f});
  tl.fromTo("#{p}-start",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.4,ease:"back.out(3)"}},{t_predict:.2f});
  var route={json.dumps([[round(NX + x * NE, 1), round(NY + y * NE, 1)] for x, y in route])}, xs=route.map(function(q){{return q[0];}}), ys=route.map(function(q){{return q[1];}});
  tl.set("#{p}-pulse",{{x:xs[0],y:ys[0]}},0);
  [0,1].forEach(function(k){{
    var t0={t_predict + 0.3:.2f}+k*1.3;
    tl.fromTo("#{p}-pulse",{{opacity:0}},{{opacity:1,duration:0.1}},t0);
    tl.to("#{p}-pulse",{{keyframes:{{x:xs,y:ys,easeEach:"none"}},duration:1.1,ease:"none",immediateRender:false}},t0);
    tl.fromTo("#{p}-pulse",{{opacity:1}},{{opacity:0,duration:0.1,immediateRender:false}},t0+1.05);
  }});
  drawStroke("#{p}-bridge",{t_eat - 0.6:.2f},0.6,500);
  tl.fromTo("#{p}-fl-proboscis",{{attr:{{d:"M104 10 q 14 6 20 20"}}}},{{attr:{{d:"M104 10 q 34 10 50 46"}},duration:0.35,ease:"back.out(2)"}},{t_eat - 0.1:.2f});
  tl.fromTo("#{p}-sparks",{{opacity:0,scale:0.5,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.3,ease:"back.out(3)"}},{t_eat:.2f});
  rise("#{p}-b1 span",{t_eat - 0.2:.2f});
  slideOut("#{p}-b1 span",{t_test - 0.3:.2f},0.4);
  highlight("#{p}-v1",{t_test:.2f},0.3); highlight("#{p}-v2",{t_test + 0.3:.2f},0.8);
  pop("#{p}-photo",{t_test + 0.6:.2f},0.4,0.8);
  rise("#{p}-b2 span",{t_real - 0.5:.2f});
  slideOut("#{p}-b2 span",{t_held - 0.4:.2f},0.4); rise("#{p}-b3 span",{t_held:.2f});
  tl.fromTo("#{p}-sim .ck",{{opacity:0,scale:0,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.6,ease:"elastic.out(1,0.45)",stagger:0.3}},{t_confirm - 0.4:.2f});
"""
    return comp(p, dur, svg, html, js, extra, seed=8)


# ---------------------------------------------------------------- mapping 7: the brain became a map and the map behaves like a brain
def mapping_7():
    SC, SG = "mapping", 7
    p = "mapping_7"
    start, dur = seg(SC, SG)
    t_start, t_one, t_became, t_map, t_map2, t_computer, t_started, t_behave, t_brain2 = (
        0.0, 2.14, 3.27, 3.65, 4.87, 6.0,
        7.18, 8.09, 9.49)
    network_svg, pts, edge_list = network_rich(f"{p}-r", 11, prefix=p)
    NX, NY, NE = 960, 400, 0.78
    rg = random.Random(9)
    routes = []
    for _ in range(12):
        a_, b_ = rg.sample(range(len(pts)), 2)
        c = path_d(pts, edge_list, a_, b_)
        if len(c) > 4:
            routes.append([[round(NX + x * NE, 1), round(NY + y * NE, 1)] for x, y in c])
    routes = routes[:6]
    grid = "".join(f'<line x1="{x}" y1="110" x2="{x}" y2="690"/>' for x in range(480, 1441, 80)) + "".join(f'<line x1="470" y1="{y}" x2="1450" y2="{y}"/>' for y in range(120, 691, 80))
    pulses = "".join(f'<circle id="{p}-pl{k}" r="11" fill="#ffd23e" filter="url(#{p}-glow)" opacity="0"/>' for k in range(len(routes)))
    extra = network_defs(p) + monitor_defs(p) + brain_defs(p) + f'<radialGradient id="{p}-bloom" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#3be0ff" stop-opacity=".45"/><stop offset="1" stop-color="#3be0ff" stop-opacity="0"/></radialGradient>'
    svg = f"""
<ellipse id="{p}-bloom" cx="960" cy="400" rx="640" ry="420" fill="url(#{p}-bloom)" opacity="0"/>
<g id="{p}-mon" opacity="0">{monitor(p, 450, 100, 1020, 600)}</g>
<g id="{p}-grid" stroke="#4a5aff" stroke-width="2" opacity="0">{grid}</g>
<g transform="translate({NX} {NY}) scale({NE})"><g id="{p}-netW" opacity="0">{network_svg}</g></g>
{pulses}
<g transform="translate(960 400) scale(1.25)"><g id="{p}-brainW">{brain_card(p + "-bc", glow=p + "-glow", fill=p + "-brain")}</g></g>
<g transform="translate(960 400) scale(1.25)"><g id="{p}-outline" opacity="0"><path transform="scale(1 1.38)" d="{BRAIN_SIL}" fill="none" stroke="#ff9fd0" stroke-width="5" vector-effect="non-scaling-stroke" stroke-dasharray="16 10" filter="url(#{p}-glow)"/></g></g>"""
    html = (mono(f"{p}-a1", "A BRAIN", "left:0;right:0;text-align:center;top:850px", "#bff4ff", 60) +
            mono(f"{p}-a2", "BECAME A MAP", "left:0;right:0;text-align:center;top:850px", "#c9b8ff", 60) +
            headline(f"{p}-f1", "The map started behaving", "left:0;right:0;text-align:center;top:822px;font-size:92px;color:#eef1f7") +
            headline(f"{p}-f2", "like a brain", "left:0;right:0;text-align:center;top:935px;font-size:92px;color:#ffd98a"))
    js = f"""
  camK("#{p}-cam",960,420,[[0,1.18],[{t_became:.2f},1.06,"sine.inOut"],[{t_computer:.2f},1.0],[{dur:.2f},0.96,"sine.inOut"]]);
  tl.fromTo("#{p}-brainW",{{opacity:0,scale:0.6,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:1.0,ease:"back.out(1.5)"}},0.1);
  tl.fromTo("#{p}-brainW",{{y:0}},{{y:-10,duration:0.9,repeat:1,yoyo:true,ease:"sine.inOut",immediateRender:false}},1.1);
  rise("#{p}-a1 span",{t_one:.2f});
  tl.fromTo("#{p}-brainW",{{scale:1}},{{scale:1.08,duration:0.2,repeat:1,yoyo:true,immediateRender:false}},{2.33:.2f});
  tl.fromTo("#{p}-brainW",{{opacity:1,scaleY:1}},{{opacity:0,scaleY:0.15,duration:0.6,ease:"power2.in",immediateRender:false}},{t_became:.2f});
  slideOut("#{p}-a1 span",{t_became - 0.2:.2f},0.35); rise("#{p}-a2 span",{t_became:.2f});
  enter("#{p}-netW",{t_became + 0.3:.2f},0.3);
  tl.fromTo("#{p}-r .node",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,transformOrigin:"50% 50%",duration:0.4,ease:"back.out(2.4)",stagger:{{each:0.006}}}},{t_became + 0.3:.2f});
  tl.fromTo("#{p}-r .eds",{{opacity:0}},{{opacity:1,duration:0.8}},{t_map:.2f});
  tl.fromTo("#{p}-r .lobe",{{opacity:0}},{{opacity:0.6,duration:0.8}},{t_map:.2f});
  tl.fromTo("#{p}-grid",{{opacity:0}},{{opacity:0.35,duration:0.8}},{t_map2:.2f});
  enter("#{p}-mon",{t_computer - 0.5:.2f},0.4);
  tl.fromTo("#{p}-mon",{{scale:1.35,svgOrigin:"960 400"}},{{scale:1,svgOrigin:"960 400",duration:0.9,ease:"power3.out"}},{t_computer - 0.5:.2f});
  enter("#{p}-bloom",{t_computer:.2f},0.8);
  slideOut("#{p}-a2 span",{t_started - 0.45:.2f},0.4);
  rise("#{p}-f1 span",{t_started:.2f},0.8); rise("#{p}-f2 span",{9.06:.2f},0.8);
  var P={json.dumps(routes)};
  P.forEach(function(c,k){{
    var xs=c.map(function(q){{return q[0];}}), ys=c.map(function(q){{return q[1];}});
    tl.set("#{p}-pl"+k,{{x:xs[0],y:ys[0]}},0);
    [0,1].forEach(function(r){{
      var t0={t_behave:.2f}+k*0.22+r*1.6;
      tl.fromTo("#{p}-pl"+k,{{opacity:0}},{{opacity:1,duration:0.12}},t0);
      tl.to("#{p}-pl"+k,{{keyframes:{{x:xs,y:ys,easeEach:"none"}},duration:1.3,ease:"none",immediateRender:false}},t0);
      tl.fromTo("#{p}-pl"+k,{{opacity:1}},{{opacity:0,duration:0.15,immediateRender:false}},t0+1.2);
    }});
  }});
  tl.fromTo("#{p}-r .g2",{{opacity:1}},{{opacity:0.35,duration:0.15,repeat:9,yoyo:true,ease:"none"}},{t_behave:.2f});
  tl.fromTo("#{p}-outline",{{opacity:0,scale:1.15,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.9,ease:"power2.out"}},{t_brain2 - 0.3:.2f});
"""
    return comp(p, dur, svg, html, js, extra, seed=19, background=("#2c1a6a", "#171049", "#0a0a24"))


# ---------------------------------------------------------------- mapping 8: one fly, simplified model, it is not copying a consciousness
def mapping_8():
    SC, SG = "mapping", 8
    p = "mapping_8"
    start, dur = seg(SC, SG)
    t_simp, t_mapping, t_connections, t_not, t_copy, t_conscious, t_keep, t_img, t_brain, t_running, t_computer, t_back = (
        0.77, 2.47, 3.13, 4.09, 4.45, 5.47,
        7.25, 8.85, 9.32, 9.97, 11.57, 12.79)
    network_svg, pts, edge_list = network_rich(f"{p}-r", 11, n=90, prefix=p)
    NX, NY, NE = 960, 470, 0.6
    pp = p + "h"
    # consciousness = the person and their memories (figure.py orbs) circling the head
    HX, HY = 1660, 300
    TX, TY = anchor("home", "standing", "head_top")
    TX, TY = 1665 - TX * 0.97, 880 + TY * 0.97          # top of the head on screen (mirrored person)
    ORB = [("heart", "#ff4fa3"), ("note", "#8d7bff"), ("cake", "#ffb23e"), ("sun", "#ffd23e"), ("car", "#3be0ff"), ("clock", "#38e8a8")]
    ANG = [math.radians(a) for a in (-150, -120, -90, -60, -30, 0)]
    wires8 = "".join(f'<line x1="{TX:.0f}" y1="{TY + 12:.0f}" x2="{HX + 175 * math.cos(a):.0f}" y2="{HY + 175 * math.sin(a):.0f}" stroke="{c}" stroke-width="4" stroke-dasharray="6 6" stroke-linecap="round"/>' for a, (_, c) in zip(ANG, ORB))
    aura = "".join(G.orb(f"{p}-ob{k}", icon, HX + 175 * math.cos(a), HY + 175 * math.sin(a), color, 40) for k, (a, (icon, color)) in enumerate(zip(ANG, ORB)))
    extra = (fly_defs(p) + network_defs(p) + monitor_defs(p) + brain_defs(p) +
             f'<radialGradient id="{p}-aur" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffd0ea" stop-opacity=".55"/><stop offset="1" stop-color="#ff9bd0" stop-opacity="0"/></radialGradient>')
    points = "".join(f'<circle class="pt" cx="{960 + x}" cy="{400 + y}" r="7" fill="#ffd23e" filter="url(#{p}-glow)" opacity="0"/>' for x, y in
                     [(-150, -40), (-90, 30), (-40, -70), (40, 40), (100, -30), (160, 50), (-170, 60), (0, 0), (120, 90), (-110, -100)])
    screen = (f'<g transform="translate(960 400) scale(.78)">{brain_card(p + "-bc", glow=p + "-glow", fill=p + "-brain")}</g>{points}')
    svg = f"""<g id="{p}-A">
 <g transform="translate(360 500)"><g id="{p}-fly"><g transform="scale(1.75)"><g id="{p}-flyBob">{fly_rich(p + "-fl", p)}</g></g></g></g>
 <path d="M600 470 L 660 470" stroke="#8d7bff" stroke-width="6" stroke-linecap="round"/><path d="M646 452 L670 470 L646 488" fill="none" stroke="#8d7bff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
 <g transform="translate({NX} {NY}) scale({NE})"><g id="{p}-netW">{network_svg}</g></g>
 <g transform="translate({NX} {NY}) scale({NE})"><g id="{p}-copy" opacity="0"><g opacity=".7">{network_svg.replace(f'id="{p}-r"', f'id="{p}-r2"')}</g></g></g>
 <ellipse id="{p}-aura" cx="{HX}" cy="{HY}" rx="260" ry="210" fill="url(#{p}-aur)" opacity="0"/>
 <g id="{p}-wires" opacity="0">{wires8}</g>
 {human(pp, "home", "standing", 1665, 880, 0.97, mirror=True, scene=p)}
 <g id="{p}-orb" opacity="0">{aura}</g>
 <g id="{p}-bar" opacity="0"><line x1="1320" y1="200" x2="1320" y2="800" stroke="#ff4f7d" stroke-width="8" stroke-dasharray="20 14" filter="url(#{p}-glow)"/></g>
 <g transform="translate(1320 470)"><g id="{p}-xx" opacity="0" stroke="#ff4f7d" stroke-width="26" stroke-linecap="round" filter="url(#{p}-glow)"><path d="M-66 -66 L66 66 M66 -66 L-66 66"/></g></g>
</g>
<g id="{p}-B" opacity="0">
 <g transform="translate(960 470)"><g id="{p}-polar"><g transform="translate(-960 -470)">
  <g filter="url(#{p}-shadow)"><rect x="470" y="96" width="980" height="784" rx="10" fill="#fffaf0"/></g>
  <rect x="500" y="126" width="920" height="630" rx="4" fill="#1a1050"/>
  <g transform="translate(960 420) scale(.82) translate(-960 -420)">{monitor(p, 610, 190, 700, 420, screen)}</g>
 </g></g></g>
</g>
<rect id="{p}-flash" width="1920" height="1080" fill="#fff" opacity="0"/>"""
    html = "".join(mono(f"{p}-l{k}", txt, f"left:0;right:0;text-align:center;top:{top}px", color, size) for k, (txt, color, top, size) in enumerate(
        [("VERY SIMPLIFIED", "#bff4ff", 900, 56), ("MAPPING CONNECTIONS", "#c9b8ff", 900, 56), ("IS NOT COPYING A CONSCIOUSNESS", "#ff9bb0", 900, 56),
         ("KEEP THAT IMAGE IN MIND", "#ffd27a", 920, 56), ("A BRAIN RUNNING INSIDE A COMPUTER", "#bff4ff", 930, 44), ("IT WILL COME BACK", "#ffd27a", 920, 64)]))
    js = f"""
  camK("#{p}-A",60,500,[[0,1.6],[0.9,1.55,"none"],[{t_mapping - 0.2:.2f},1.0,"power2.inOut"],[{t_keep:.2f},1.0]]);
  tl.fromTo("#{p}-flyBob",{{y:0,rotation:-2,transformOrigin:"50% 50%"}},{{y:-10,rotation:2,transformOrigin:"50% 50%",duration:0.55,repeat:12,yoyo:true,ease:"sine.inOut"}},0);
  tl.fromTo("#{p}-fl-wings",{{scaleY:1,transformOrigin:"50% 100%"}},{{scaleY:0.3,transformOrigin:"50% 100%",duration:0.05,repeat:{2 * int(t_keep / 0.1) - 1},yoyo:true,ease:"none"}},0);
  enter("#{p}-r .lobe",0,0.4); enter("#{p}-r .eds",0,0.4);
  rise("#{p}-l0 span",{t_simp:.2f});
  tl.fromTo("#{p}-r .g0",{{opacity:0.5}},{{opacity:0,duration:0.6}},{t_simp + 0.2:.2f});
  tl.fromTo("#{p}-r .e0",{{opacity:0.4}},{{opacity:0,duration:0.6}},{t_simp + 0.2:.2f});
  slideOut("#{p}-l0 span",{t_mapping - 0.4:.2f},0.4); rise("#{p}-l1 span",{t_mapping:.2f});
  tl.fromTo("#{p}-r .e2",{{opacity:0.9}},{{opacity:0.3,duration:0.2,repeat:5,yoyo:true}},{t_connections:.2f});
  tl.fromTo("#{p}-r .g2",{{opacity:1}},{{opacity:0.4,duration:0.2,repeat:5,yoyo:true}},{t_connections:.2f});
  enter("#{p}-aura",{t_not - 0.4:.2f},0.6); enter("#{p}-orb",{t_not - 0.3:.2f},0.6); enter("#{p}-wires",{t_not - 0.3:.2f},0.6);
  tl.fromTo("{",".join(f"#{p}-ob{k}" for k in range(len(ORB)))}",{{y:0}},{{y:-10,duration:0.7,repeat:3,yoyo:true,ease:"sine.inOut",stagger:0.12}},{t_not - 0.3:.2f});
  slideOut("#{p}-l1 span",{t_not - 0.45:.2f},0.4); rise("#{p}-l2 span",{t_not:.2f});
  enter("#{p}-copy",{t_copy - 0.1:.2f},0.2);
  tl.fromTo("#{p}-copy",{{x:0}},{{x:190,duration:{t_conscious - t_copy + 0.1:.2f},ease:"power2.in",immediateRender:false}},{t_copy - 0.1:.2f});
  enter("#{p}-bar",{t_conscious - 0.05:.2f},0.1);
  tl.fromTo("#{p}-xx",{{opacity:0,scale:2.2,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.3,ease:"back.out(3)"}},{t_conscious:.2f});
  tl.fromTo("#{p}-copy",{{x:190}},{{x:30,duration:0.8,ease:"power3.out",immediateRender:false}},{t_conscious + 0.05:.2f});
  vanish("#{p}-copy",{t_conscious + 0.5:.2f},0.5);
  tl.fromTo("#{pp}-eye",{{x:0}},{{x:3,duration:0.3}},{t_copy:.2f});
  tl.fromTo("#{p}-A",{{opacity:1}},{{opacity:0,duration:0.5}},{t_keep - 0.2:.2f});
  slideOut("#{p}-l2 span",{t_keep - 0.4:.2f},0.4); rise("#{p}-l3 span",{t_keep:.2f});
  enter("#{p}-B",{t_keep + 0.1:.2f},0.5);
  tl.fromTo("#{p}-polar",{{scale:1.25,rotation:0,transformOrigin:"50% 50%"}},{{scale:1,rotation:0,transformOrigin:"50% 50%",duration:1.2,ease:"power3.out"}},{t_keep + 0.1:.2f});
  tl.fromTo("#{p}-B .pt",{{opacity:0}},{{opacity:1,duration:0.18,repeat:21,yoyo:true,stagger:{{each:0.13,from:"random"}}}},{t_keep + 0.5:.2f});
  tl.fromTo("#{p}-flash",{{opacity:0}},{{opacity:0.85,duration:0.06,yoyo:true,repeat:1}},{t_img - 0.1:.2f});
  tl.fromTo("#{p}-polar",{{rotation:0}},{{rotation:-4,duration:0.5,ease:"back.out(2)",immediateRender:false}},{t_img:.2f});
  slideOut("#{p}-l3 span",{t_brain - 0.35:.2f},0.35); rise("#{p}-l4 span",{t_brain:.2f});
  slideOut("#{p}-l4 span",{t_back - 0.3:.2f},0.35); rise("#{p}-l5 span",{t_back:.2f},0.8);
  tl.fromTo("#{p}-polar",{{scale:1,y:0}},{{scale:0.9,y:-20,duration:1.4,ease:"power2.inOut",immediateRender:false}},{t_back:.2f});
""" + G.figure_idle(pp, dur, (1.2, 3.4, 6.2))
    return comp(p, dur, svg, html, js, extra, seed=22)


# ---------------------------------------------------------------- scene list
_FN = {("writing", 0): writing_0, ("writing", 2): writing_2, ("writing", 5): writing_5, ("writing", 7): writing_7,
       ("mapping", 0): mapping_0, ("mapping", 3): mapping_3, ("mapping", 4): mapping_4, ("mapping", 6): mapping_6, ("mapping", 7): mapping_7,
       ("mapping", 8): mapping_8}
SEG_MAP = {k: f"{k[0]}_{k[1]}" for k in _FN}
SCENES = [(SEG_MAP[k], fn, seg(*k)[1]) for k, fn in _FN.items()]

if __name__ == "__main__":
    print(write_scenes(SCENES, OUT_DIR))
