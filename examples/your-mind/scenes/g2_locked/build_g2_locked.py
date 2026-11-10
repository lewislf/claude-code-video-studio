"""Scenes v5, group g2_locked: the 9 segments of the "locked" scene (a memory that exists but cannot be reached).

  python3 build_g2_locked.py     # writes compositions/ and index.html in this folder

Metaphor: the door and the padlock. Round 2: a real person (figure.py) lives each scene in a different setting
(hallway and kitchen, living room, bedroom at night, doctor's office, street before dawn); the head with the pink brain is only in
segment 2, where the narration talks about the brain. The mouse from the isometric box comes back in the MIT segment.
"""
import base64, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "../../scenes-v4"))
from engine import *  # noqa: E402,F401
from build4 import mouse, box, box_grad, bolt  # noqa: E402
import figure as G  # noqa: E402
HERE = os.path.dirname(os.path.abspath(__file__))  # engine and build4 also define HERE; this folder's value wins

SCENE = "locked"
DOCS = os.path.join(HERE, "assets/docs")

# ---------------------------------------------------------------- own JS: camera and attribute transforms
# Everything that moves by translate/scale here is written straight into the `transform` attribute (no GSAP x/y/scale),
# so attribute and GSAP never fight (GOTCHAS 1 to 4). Chained states: the end of one step is the start of the next.
JS2 = r"""
  function _el(s){return document.querySelector(s);}
  function camT(st){var z=st[0];return "translate("+(st[3]-z*st[1]).toFixed(2)+" "+(st[4]-z*st[2]).toFixed(2)+") scale("+z.toFixed(4)+")";}
  function camK(sel,t0,dur,a,b,ease){var e=_el(sel),o={k:0};
    tl.fromTo(o,{k:0},{k:1,duration:dur,ease:ease||"power3.inOut",immediateRender:false,onUpdate:function(){var k=o.k;
      var z=Math.exp(Math.log(a[0])+(Math.log(b[0])-Math.log(a[0]))*k);
      e.setAttribute("transform",camT([z,a[1]+(b[1]-a[1])*k,a[2]+(b[2]-a[2])*k,a[3]+(b[3]-a[3])*k,a[4]+(b[4]-a[4])*k]));}},t0);}
  function trT(st){return "translate("+st[0].toFixed(2)+" "+st[1].toFixed(2)+") rotate("+(st[3]||0).toFixed(2)+") scale("+st[2].toFixed(4)+")";}
  function trK(sel,t0,dur,a,b,ease){var e=_el(sel),o={k:0};
    tl.fromTo(o,{k:0},{k:1,duration:dur,ease:ease||"power3.inOut",immediateRender:false,onUpdate:function(){var k=o.k,r=[];
      for(var i=0;i<4;i++){r.push((a[i]||0)+((b[i]||0)-(a[i]||0))*k);} e.setAttribute("transform",trT(r));}},t0);}
"""


def cam(p, start, steps):
    """Camera on #{p}-cam. State (z, Px, Py[, Sx, Sy]): world point P shows up at S on screen with zoom z.
    steps: [(t0, dur, state, ease)]. Returns the JS (the initial state is applied right away)."""
    def full(st):
        return list(st) + [960, 540] if len(st) == 3 else list(st)
    a = full(start)
    js = f'_el("#{p}-cam").setAttribute("transform",camT({a}));'
    for t0, d, st, *ease in steps:
        b = full(st)
        js += f'camK("#{p}-cam",{t0:.2f},{d:.2f},{a},{b},"{ease[0] if ease else "power3.inOut"}");'
        a = b
    return js


def move(sel, start, steps):
    """Attribute-driven motion of a group: state (x, y, s[, rot]). Returns (initial attribute, JS)."""
    a = list(start) + [0] * (4 - len(start))
    js = ""
    for t0, d, st, *ease in steps:
        b = list(st) + [0] * (4 - len(st))
        js += f'trK("{sel}",{t0:.2f},{d:.2f},{a},{b},"{ease[0] if ease else "power3.inOut"}");'
        a = b
    x, y, s, r = list(start) + [0] * (4 - len(start))
    return f'translate({x} {y}) rotate({r}) scale({s})', js


def comp(p, dur, svg, html, js, extra="", **kw):
    return composition(p, dur, svg, html, JS2 + js, extra, **kw)


# ---------------------------------------------------------------- scene art pieces
def padlock(p, k, color=AMBER):
    """Padlock centered at (0,0), ~120 x 150. Ids: {p}-lock{k} (whole), {p}-shackle{k} (shackle, rises to open)."""
    return (f'<g id="{p}-lock{k}"><rect x="-70" y="-95" width="140" height="190" fill="none" opacity="0"/>'
            f'<g id="{p}-shackle{k}"><path d="M-38 -6 L-38 -46 A38 38 0 0 1 38 -46 L38 -6" fill="none" stroke="#d9dcf0" stroke-width="15" stroke-linecap="round"/></g>'
            f'<rect x="-60" y="-12" width="120" height="96" rx="18" fill="{color}" stroke="#fff3c8" stroke-width="4"/>'
            f'<rect x="-60" y="-12" width="120" height="30" rx="14" fill="#fff" opacity=".22"/>'
            f'<circle cx="0" cy="26" r="13" fill="#2a1446"/><path d="M-6 30 L-9 58 L9 58 L6 30 Z" fill="#2a1446"/></g>')


def orb(p, k, color=AMBER, r=34):
    """Memory: sphere of light centered at (0,0). Ids {p}-orb{k} and {p}-orbh{k} (halo)."""
    return (f'<g id="{p}-orb{k}"><circle id="{p}-orbh{k}" r="{r * 2.1:.0f}" fill="{color}" opacity=".22" filter="url(#{p}-blur6)"/>'
            f'<circle r="{r}" fill="{color}"/><circle cx="{-r * .3:.0f}" cy="{-r * .32:.0f}" r="{r * .38:.0f}" fill="#fff" opacity=".55"/></g>')


def key_shape(color=AMBER):
    """Key pointing right, bow at (0,0), ~250 long."""
    return (f'<circle cx="0" cy="0" r="38" fill="none" stroke="{color}" stroke-width="16"/>'
            f'<path d="M38 0 L230 0 M190 0 L190 36 M222 0 L222 28" stroke="{color}" stroke-width="16" fill="none" stroke-linecap="round"/>')


def front_door(p, k, x, y, w, h, leaf="#2a2068", edge=LILAC):
    """Front door: frame (with glow), opening and leaf. The leaf {p}-leaf{k} opens with scaleX from the hinge (left)."""
    return (f'<g filter="url(#{p}-shadow)"><rect x="{x - 26}" y="{y - 26}" width="{w + 52}" height="{h + 26}" rx="10" fill="#1d1752"/></g>'
            f'<rect x="{x - 26}" y="{y - 26}" width="{w + 52}" height="{h + 26}" rx="10" fill="none" stroke="{edge}" stroke-width="6" filter="url(#{p}-glow)"/>'
            f'@GAP{k}@'
            f'<g id="{p}-leaf{k}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{leaf}" stroke="#5a4cc0" stroke-width="4"/>'
            f'<rect x="{x + w * .14:.0f}" y="{y + h * .07:.0f}" width="{w * .72:.0f}" height="{h * .36:.0f}" rx="8" fill="none" stroke="#5a4cc0" stroke-width="4"/>'
            f'<rect x="{x + w * .14:.0f}" y="{y + h * .52:.0f}" width="{w * .72:.0f}" height="{h * .4:.0f}" rx="8" fill="none" stroke="#5a4cc0" stroke-width="4"/>'
            f'<circle cx="{x + w * .86:.0f}" cy="{y + h * .5:.0f}" r="{max(6, w * .045):.0f}" fill="{AMBER}"/></g>')


def wall(p, floor=900, color=("#24206a", "#1a1650")):
    return (f'<rect x="-1500" y="-1500" width="4920" height="{floor + 1500}" fill="url(#{p}-wallG)"/>'
            f'<rect x="-1500" y="{floor}" width="4920" height="1600" fill="#100c34"/>'
            f'<rect x="-1500" y="{floor - 6}" width="4920" height="12" fill="#3a3290"/>')


def wall_defs(p, a="#2a2474", b="#18144a"):
    return f'<linearGradient id="{p}-wallG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{b}"/><stop offset="1" stop-color="{a}"/></linearGradient>'


def bubble(p, k, content, x=330, y=-40):
    """Thought bubble in the person's local coordinates (comes out of the top of the head). Id {p}-bub{k}."""
    return (f'<g id="{p}-bub{k}"><circle cx="262" cy="34" r="9" fill="#eef1f7" opacity=".85"/><circle cx="286" cy="8" r="14" fill="#eef1f7" opacity=".9"/>'
            f'<ellipse cx="{x}" cy="{y}" rx="78" ry="58" fill="#eef1f7"/><g transform="translate({x} {y})">{content}</g></g>')


def title(id_, txt, style, size=96, color="#eef1f7", mono=False):
    family = "font-family:'IBM Plex Mono',monospace;font-weight:700;letter-spacing:.08em;" if mono else ""
    return text(id_, txt, f"{style};font-size:{size}px;color:{color};{family}")



# ---------------------------------------------------------------- round 2: the real person (figure.py) and settings with a story
# New character (figure.py, turn 25 -> ANCHORS for turn 30). Its groups have a huge box (M-9999 masks), so every
# rotation/scale on a group that holds the person uses svgOrigin in px in its local system, never transformOrigin in %.
def anchors(pose):
    return G.ANCHORS[("home", pose, 30)]


def neck(pose):
    cx, cy = anchors(pose)["head_center"]
    return f"{cx} {cy + 45}"


def shoulder(pose):
    return "%s %s" % anchors(pose)["shoulder_arm"]


def human(p, variant="home", pose="standing", chair=True, mug=True, hand=""):
    """Person from figure.py inside {p}-flip (scaleX -1 with svgOrigin "0 0" turns it around). figure ids get the prefix {p}-g.
    mug=False removes the mug the sitting pose holds. hand goes at the end of {p}-g-arm (turns with the arm)."""
    g = p + "-g"
    s = G.figure(g, variant, pose, chair=chair)
    if not mug and pose != "standing":
        i = s.index('<path d="M 14,-254 C 0,-254 0,-232 14,-232"')
        j = s.index('/>', s.rindex('stroke="#a98bff"')) + 2
        assert 0 < j - i < 6000
        s = s[:i] + s[j:]
    if hand:
        i = s.rindex("<g", 0, s.index(f'id="{g}-arm"'))
        depth = 0
        for m in re.finditer(r"<g\b|</g>", s[i:]):
            depth += -1 if m.group(0) == "</g>" else 1
            if depth == 0:
                break
        k = i + m.start()
        s = s[:k] + hand + s[k:]
    return f'<g id="{p}-flip">{s}</g>'


def idle_h(p, dur, blinks=(2.0, 5.3, 8.8, 12.1, 16.4)):
    """JS: breathing, head sway and blinks (figure_idle already uses svgOrigin)."""
    return G.figure_idle(p + "-g", dur, blinks)


def bubble_xy(pose="standing"):
    """Center of the thought bubble in the person's local system (above and to the right of head_top)."""
    tx, ty = anchors(pose)["head_top"]
    return tx + 175, ty - 175


def bubble_h(p, k, content, sitting=False, rx=100, ry=75):
    """Thought bubble in the person's local system, coming out of the top of the head (ANCHORS head_top). Id {p}-bub{k}."""
    pose = "sitting" if sitting else "standing"
    tx, ty = anchors(pose)["head_top"]
    x, y = bubble_xy(pose)
    return (f'<g id="{p}-bub{k}"><circle cx="{tx + 50:.0f}" cy="{ty - 22:.0f}" r="11" fill="#eef1f7" opacity=".85"/><circle cx="{tx + 88:.0f}" cy="{ty - 62:.0f}" r="17" fill="#eef1f7" opacity=".92"/>'
            f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rx}" ry="{ry}" fill="#eef1f7"/><g transform="translate({x:.0f} {y:.0f})">{content}</g></g>')


def room(p, k, x0, x1, c1, c2, top=-700, floor=900, floor_color="#241638", baseboard="#6a4a8a", floor_h=700):
    """Wall with gradient, floor and baseboard. Returns (svg, defs)."""
    defs = f'<linearGradient id="{p}-roomG{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c2}"/><stop offset="1" stop-color="{c1}"/></linearGradient>'
    svg = (f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{floor - top}" fill="url(#{p}-roomG{k})"/>'
           f'<rect x="{x0}" y="{floor}" width="{x1 - x0}" height="{floor_h}" fill="{floor_color}"/>'
           f'<rect x="{x0}" y="{floor - 10}" width="{x1 - x0}" height="14" fill="{baseboard}"/>')
    return svg, defs


def doorway(p, k, x0, x1, ytop, floor=900, side=1, top=-700, is_open=True, color="#4a3a9a"):
    """Door in a wall seen in cross-section. Closed leaf {p}-dc{k}; open leaf {p}-do{k} (hinge on side `side`)."""
    w = x1 - x0
    xa = x1 if side > 0 else x0
    xb = xa + side * 110
    cy = (ytop + floor) / 2
    return (f'<rect x="{x0}" y="{top}" width="{w}" height="{floor - top}" fill="#1a1448"/>'
            f'<rect x="{x0}" y="{ytop}" width="{w}" height="{floor - ytop}" fill="#0c0a26"/>'
            f'<rect x="{x0 - 8}" y="{ytop - 8}" width="{w + 16}" height="{floor - ytop + 8}" fill="none" stroke="{LILAC}" stroke-width="6" filter="url(#{p}-glow)"/>'
            f'<g id="{p}-dc{k}" opacity="{0 if is_open else 1}"><rect x="{x0}" y="{ytop}" width="{w}" height="{floor - ytop}" fill="{color}" stroke="#8d7bff" stroke-width="3"/>'
            f'<circle cx="{xa - side * 14}" cy="{cy + 10:.0f}" r="7" fill="{AMBER}"/></g>'
            f'<g id="{p}-do{k}" opacity="{1 if is_open else 0}"><polygon points="{xa},{ytop} {xb},{ytop + 34} {xb},{floor - 16} {xa},{floor}" fill="{color}" stroke="#8d7bff" stroke-width="4"/>'
            f'<circle cx="{xa + side * 92}" cy="{cy + 10:.0f}" r="7" fill="{AMBER}"/></g>')


def window(x, y, w, h, sky=("#101a4a", "#3a2a7a"), moon=True, frame="#d9cfe8", curtain="#ff8fb8"):
    light = (f'<circle cx="{x + w * .72:.0f}" cy="{y + h * .3:.0f}" r="{min(w, h) * .12:.0f}" fill="#fff3c8"/>' if moon else
          f'<ellipse cx="{x + w * .3:.0f}" cy="{y + h * .3:.0f}" rx="{w * .16:.0f}" ry="{h * .06:.0f}" fill="#fff" opacity=".8"/>')
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{sky[0]}"/><rect x="{x}" y="{y + h * .5:.0f}" width="{w}" height="{h * .5:.0f}" fill="{sky[1]}" opacity=".7"/>{light}'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{frame}" stroke-width="14"/>'
            f'<path d="M{x + w / 2} {y} V{y + h} M{x} {y + h / 2} H{x + w}" stroke="{frame}" stroke-width="8"/>'
            f'<rect x="{x - 34}" y="{y - 20}" width="40" height="{h + 50}" rx="10" fill="{curtain}" opacity=".85"/><rect x="{x + w - 6}" y="{y - 20}" width="40" height="{h + 50}" rx="10" fill="{curtain}" opacity=".85"/>'
            f'<rect x="{x - 50}" y="{y - 30}" width="{w + 100}" height="12" rx="6" fill="{frame}"/>')


def lamp(p, k, x, y, top=-700, color="#ffb23e"):
    """Pendant lamp with a cone of light. Glow id {p}-light{k}."""
    return (f'<g id="{p}-light{k}" opacity=".9"><polygon points="{x - 50},{y + 46} {x + 50},{y + 46} {x + 260},{y + 640} {x - 260},{y + 640}" fill="{color}" opacity=".10"/>'
            f'<ellipse cx="{x}" cy="{y + 50}" rx="120" ry="40" fill="{color}" opacity=".25" filter="url(#{p}-blur6)"/></g>'
            f'<path d="M{x} {top} V{y}" stroke="#6a4a5a" stroke-width="6"/><path d="M{x - 44} {y} L{x + 44} {y} L{x + 70} {y + 50} L{x - 70} {y + 50} Z" fill="{color}"/>'
            f'<ellipse cx="{x}" cy="{y + 50}" rx="66" ry="10" fill="#fff3c8"/>')


def table(x0, x1, ytop, floor=900, color="#6a3e2a", leg="#4a2a1e"):
    return (f'<rect x="{x0}" y="{ytop}" width="{x1 - x0}" height="24" rx="8" fill="{color}"/>'
            f'<rect x="{x0 + 20}" y="{ytop + 24}" width="22" height="{floor - ytop - 24}" fill="{leg}"/><rect x="{x1 - 42}" y="{ytop + 24}" width="22" height="{floor - ytop - 24}" fill="{leg}"/>')


def table_lamp(x, ytop, color="#ffd27a"):
    return (f'<ellipse cx="{x}" cy="{ytop - 110}" rx="110" ry="80" fill="{color}" opacity=".18"/><rect x="{x - 8}" y="{ytop - 90}" width="16" height="90" fill="#c9b8a0"/>'
            f'<path d="M{x - 50} {ytop - 90} L{x + 50} {ytop - 90} L{x + 34} {ytop - 160} L{x - 34} {ytop - 160} Z" fill="{color}"/><ellipse cx="{x}" cy="{ytop - 4}" rx="34" ry="8" fill="#c9b8a0"/>')


def plant(x, floor=900, s=1.0):
    leaves = "".join(f'<ellipse cx="0" cy="-60" rx="22" ry="62" fill="{c}" transform="translate(0 -110) rotate({a})"/>'
                     for a, c in [(-50, "#2f9a70"), (-20, "#38b87e"), (10, "#2f9a70"), (40, "#38b87e"), (70, "#2a8a66")])
    return (f'<g transform="translate({x} {floor}) scale({s})">{leaves}<path d="M-44 -110 L44 -110 L34 0 L-34 0 Z" fill="#c96a4a"/>'
            f'<rect x="-50" y="-118" width="100" height="16" rx="6" fill="#e07a58"/></g>')


def armchair(x, floor, s, color="#c9506a", color2="#a03a56"):
    return (f'<g transform="translate({x} {floor}) scale({s})"><rect x="-150" y="-410" width="74" height="300" rx="30" fill="{color2}"/>'
            f'<rect x="-130" y="-176" width="270" height="70" rx="24" fill="{color}"/><rect x="-118" y="-106" width="18" height="106" fill="#3a2030"/><rect x="112" y="-106" width="18" height="106" fill="#3a2030"/></g>')


def picture_dark():
    """Frame with the faded memory: dark background cracked in red (box 120 x 92, centered)."""
    return ('<rect x="-62" y="-48" width="124" height="96" rx="6" fill="#8a6a3a"/><rect x="-54" y="-40" width="108" height="80" fill="#2a0c1c"/>'
            f'<path d="M-40 -30 L-10 2 L-24 30 M-10 2 L22 -10 L44 26 M22 -10 L30 -34" stroke="{RED}" stroke-width="4" fill="none" stroke-linecap="round"/>')


def drop(x, y, s=1.0):
    return f'<path transform="translate({x} {y}) scale({s})" d="M0 -16 C 8 -4 12 2 12 8 A12 12 0 0 1 -12 8 C -12 2 -8 -4 0 -16 Z" fill="#9fe6ff"/>'



# ================================================================ 0 home: leaves the hallway, walks into the kitchen and forgets what they came to do
def locked_0():
    p = "locked_0"
    start, dur = seg(SCENE, 0)
    t_you, t_walked, t_forgot, t_what = 2.49, 2.73, 4.18, 4.75
    g = p + "-g"
    S = 0.85
    w0, d0 = room(p, 0, -700, 1000, "#3c2d80", "#271c5c", floor_color="#22163a")
    w1, d1 = room(p, 1, 1060, 2700, "#8a4a62", "#55294a", floor_color="#3a2028", baseboard="#c08a6a")
    hallway = (G.picture(f"{p}-pic0", "family", 330, 400, .85) + G.picture(f"{p}-pic1", "beach", 660, 370, .7, rot=2)
                + table(90, 300, 700) + table_lamp(195, 700) + plant(880, s=.9))
    tiles = "".join(f'<path d="M1160 {y} H1670" stroke="#f0d8c8" stroke-width="2" opacity=".25"/>' for y in range(590, 690, 32))
    kitchen = (window(1230, 320, 260, 230) + lamp(p, 0, 1360, 250)
               + f'<rect x="1160" y="560" width="510" height="130" fill="#f0d8c8" opacity=".14"/>{tiles}'
               + '<rect x="1530" y="330" width="170" height="170" rx="8" fill="#b8665a"/><path d="M1615 340 V490" stroke="#8a4a42" stroke-width="4"/>'
               + '<rect x="1170" y="704" width="490" height="196" fill="#b8665a"/>'
               + "".join(f'<rect x="{x}" y="720" width="104" height="166" rx="6" fill="none" stroke="#8a4a42" stroke-width="4"/><circle cx="{x + 88}" cy="800" r="5" fill="#f0d8c8"/>' for x in (1186, 1306, 1426, 1546))
               + '<rect x="1150" y="686" width="530" height="22" rx="6" fill="#efe2cf"/>'
               + '<rect x="1284" y="632" width="36" height="54" rx="4" fill="#bff4ff" opacity=".35" stroke="#bff4ff" stroke-width="3"/>'
               + '<path d="M1540 686 Q1540 640 1580 640 Q1620 640 1620 686 Z" fill="#ff8a6a"/><path d="M1620 660 l26 -14" stroke="#ff8a6a" stroke-width="8" stroke-linecap="round"/>'
               + '<rect x="1726" y="420" width="180" height="480" rx="18" fill="#dfe6f2"/><path d="M1726 570 H1906" stroke="#9aa6c0" stroke-width="5"/>'
               + '<rect x="1746" y="470" width="10" height="70" rx="5" fill="#9aa6c0"/><rect x="1746" y="600" width="10" height="110" rx="5" fill="#9aa6c0"/>')
    door = doorway(p, 0, 1000, 1060, 380, side=1)
    tr0, js_mov = move(f"#{p}-personW", (460, 900, S), [(t_walked - 0.05, 1.3, (1330, 900, S), "power1.inOut")])
    qmark = f'<g id="{p}-qmark" opacity="0"><text x="0" y="34" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="120" fill="{MAGENTA}">?</text></g>'
    item = f'<g id="{p}-item">{G.orb(p + "-cup", "cup", 0, 0, CYAN, 50)}</g>'
    svg = f"""{w0}{w1}{hallway}{kitchen}{door}
<g id="{p}-personW" transform="{tr0}">{human(p, "home", "standing")}{bubble_h(p, 0, item + qmark)}</g>"""
    html = (title(f"{p}-t1", "HAVE YOU EVER WALKED INTO A ROOM", "left:0;right:0;text-align:center;top:950px", 64, "#bff4ff", True) +
            title(f"{p}-t2", "WHAT DID YOU COME TO DO?", "left:110px;top:920px", 100, "#ffd98a"))
    js = cam(p, (1.0, 760, 540), [
        (0, t_walked, (1.06, 720, 560), "sine.inOut"),
        (t_walked - 0.1, 1.5, (1.12, 1420, 560), "power2.inOut"),
        (t_walked + 1.4, dur - t_walked - 1.4, (1.16, 1400, 570), "sine.inOut")])
    js += js_mov + f"""
  pop("#{p}-bub0", 0.5, 0.3, 0.8);
  tl.fromTo("#{p}-item",{{rotation:-8,transformOrigin:"50% 50%"}},{{rotation:8,duration:0.5,repeat:5,yoyo:true,ease:"sine.inOut"}},0.9);
  tl.fromTo("#{g}-body",{{y:0}},{{y:-12,duration:0.16,repeat:7,yoyo:true,ease:"sine.inOut"}},{t_walked - 0.05:.2f});
  rise("#{p}-t1 span", {t_you:.2f});
  vanish("#{p}-t1", {t_forgot - 0.1:.2f}, 0.3);
  tl.fromTo("#{g}-eye",{{x:0}},{{x:2,duration:0.3}},{t_you:.2f});
  tl.fromTo("#{p}-item",{{opacity:1,scale:1,transformOrigin:"50% 50%"}},{{opacity:0,scale:0.2,transformOrigin:"50% 50%",duration:0.35,ease:"back.in(2)",immediateRender:false}},{t_forgot:.2f});
  pop("#{p}-qmark", {t_forgot + 0.3:.2f}, 0.2, 0.7);
  tl.fromTo("#{p}-qmark",{{rotation:-10,transformOrigin:"50% 50%"}},{{rotation:10,duration:0.35,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_forgot + 1.0:.2f});
  tl.fromTo("#{g}-eye",{{x:2}},{{x:-2,duration:0.2,repeat:2,yoyo:true,immediateRender:false}},{t_forgot + 0.1:.2f});
  tl.fromTo("#{p}-flip",{{scaleX:1,svgOrigin:"0 0"}},{{scaleX:-1,svgOrigin:"0 0",duration:0.3,ease:"power2.inOut"}},{t_forgot + 0.55:.2f});
  tl.fromTo("#{g}-arm",{{rotation:0,svgOrigin:"{shoulder("standing")}"}},{{rotation:-155,svgOrigin:"{shoulder("standing")}",duration:0.45,ease:"back.out(1.6)"}},{t_what + 0.1:.2f});
  rise("#{p}-t2 span", {t_what - 0.05:.2f}, 0.8);
""" + idle_h(p, dur, (1.6, 4.0))
    return comp(p, dur, svg, html, js, d0 + d1)


# ================================================================ 4 doc: MIT 2015, mice with amnesia
def locked_4():
    p = "locked_4"
    start, dur = seg(SCENE, 4)
    t_mit, t_mice, t_amnesia, t_remember, t_lost, t_science, t_switch_on, t_light, t_neurons, t_memory = (
        3.2, 5.06, 5.99, 6.87, 8.92, 10.83, 11.75, 12.89, 13.37, 14.59)
    img = os.path.join(DOCS, "ryan2015.png")  # not in the repository (see CREDITS.md in film): blank page without it
    b64 = base64.b64encode(open(img, "rb").read()).decode() if os.path.exists(img) else ""
    PW = 700
    PH = PW * 2071 / 1600
    k = PW / 1600
    hl_y, hl_h = 1408 * k, 104 * k  # "One Sentence Summary: Memory can be retrieved by optogenetic activation..."
    page = (f'<g transform="translate(150 96) rotate(-2.5 {PW / 2} {PH / 2:.0f})"><g id="{p}-page">'
              f'<g filter="url(#{p}-shadow)"><rect x="-10" y="-10" width="{PW + 20}" height="{PH + 20:.0f}" rx="6" fill="#fffdf6"/></g>'
              f'<image href="data:image/png;base64,{b64}" x="0" y="0" width="{PW}" height="{PH:.0f}"/>'
              f'<g id="{p}-hl"><rect x="{180 * k:.1f}" y="{hl_y:.1f}" width="{1240 * k:.1f}" height="{hl_h:.1f}" rx="6" fill="{AMBER}" opacity=".38"/></g>'
              f'<rect x="{180 * k - 8:.1f}" y="{hl_y - 8:.1f}" width="{1240 * k + 16:.1f}" height="{hl_h + 16:.1f}" rx="10" fill="none" stroke="{AMBER}" stroke-width="5" id="{p}-hlb" opacity="0"/>'
              f'</g></g>')
    # mouse in the box (approved art from build4), on the right
    CS = 0.72
    CX, CY = 1400 - CS * 960, 650 - CS * 490
    head = (CX + CS * 1052, CY + CS * 440)
    neurons = "".join(f'<circle class="n" cx="{x * 1.7:.0f}" cy="{y * 1.7:.0f}" r="9" fill="#9aa0c8"/>' for x, y in
                   [(-40, -14), (-18, 16), (6, -22), (28, 10), (46, -12), (-30, 34), (14, 36), (-52, 8)])
    svg = f"""{page}
<g id="{p}-box" opacity="0"><g transform="translate({CX:.1f} {CY:.1f}) scale({CS})">{box(p)}
 <g transform="translate(900 700) scale(1.15)"><g id="{p}-mouseW"><g id="{p}-bob">{mouse(p)}</g></g></g>
 <path id="{p}-cable" d="M1052 -200 C 1052 100 1052 300 1052 440" fill="none" stroke="#9aa6d0" stroke-width="12" stroke-linecap="round" stroke-dasharray="700" stroke-dashoffset="700"/>
 <path id="{p}-lightBeam" d="M1052 -200 C 1052 100 1052 300 1052 440" fill="none" stroke="#7fe6ff" stroke-width="14" stroke-linecap="round" stroke-dasharray="90 800" stroke-dashoffset="90" filter="url(#{p}-glow)" opacity="0"/>
</g></g>
<circle id="{p}-halo" cx="{head[0]:.0f}" cy="{head[1] + 14:.0f}" r="40" fill="#7fe6ff" opacity="0" filter="url(#{p}-glow)"/>
<g transform="translate(1690 260)"><g id="{p}-bubW" opacity="0">
 <circle cx="-150" cy="215" r="12" fill="#eef1f7" opacity=".8"/><circle cx="-118" cy="168" r="18" fill="#eef1f7" opacity=".85"/>
 <circle r="140" fill="#141040" stroke="#eef1f7" stroke-width="6"/>
 <g id="{p}-nodes">{neurons}</g>
 <g id="{p}-orbW" opacity=".25">{orb(p, 0, AMBER, 30)}</g>
 <g transform="translate(0 4) scale(.55)"><g id="{p}-lockW">{padlock(p, 0, "#8d8fb0")}</g></g>
 <g id="{p}-rings" opacity="0" fill="none" stroke="{AMBER}" stroke-width="6"><circle id="{p}-a1" r="60"/><circle id="{p}-a2" r="60"/></g>
</g></g>"""
    html = (title(f"{p}-t1", "2015", "left:1240px;top:170px", 230, "#ffd98a") +
            title(f"{p}-t2", "MIT", "left:1280px;top:480px", 160, "#bff4ff", True) +
            title(f"{p}-t3", "AMNESIA", "right:90px;top:900px;text-align:right", 80, "#c9b8ff", True) +
            title(f"{p}-t4", "THE MEMORY CAME BACK", "right:60px;top:895px;text-align:right", 88, "#ffd98a"))
    hx, hy = 150 + 180 * k + 620 * k, 96 + hl_y + 20
    js = cam(p, (1.0, 960, 540), [
        (0.2, 1.4, (1.05, 860, 540), "sine.inOut"),
        (1.6, 2.4, (1.7, hx, hy, 560, 640), "power3.inOut"),
        (t_mice - 0.6, 1.2, (1.0, 960, 540, 960, 540), "power3.inOut"),
        (t_science - 0.5, dur - t_science + 0.5, (1.03, 1000, 540), "sine.inOut")])
    js += f"""
  tl.fromTo("#{p}-page",{{y:420,opacity:0}},{{y:0,opacity:1,duration:1.0,ease:"expo.out"}},0.05);
  rise("#{p}-t1 span", 0.35, 0.9);
  tl.fromTo("#{p}-hl",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,transformOrigin:"0% 50%",duration:1.6,ease:"power2.inOut"}},1.9);
  enter("#{p}-hlb", 3.4, 0.3);
  rise("#{p}-t2 span", {t_mit:.2f});
  vanish("#{p}-t1", {t_mice - 0.7:.2f}, 0.3); vanish("#{p}-t2", {t_mice - 0.7:.2f}, 0.3);
  enter("#{p}-box", {t_mice - 0.3:.2f}, 0.5);
  tl.fromTo("#{p}-mouseW",{{x:-260}},{{x:0,duration:1.2,ease:"power2.out"}},{t_mice - 0.3:.2f});
  tl.fromTo("#{p}-bob",{{y:0}},{{y:-5,duration:0.8,repeat:{int((dur - t_mice) / 0.8)},yoyo:true,ease:"sine.inOut"}},{t_mice:.2f});
  rise("#{p}-t3 span", {t_amnesia:.2f});
  vanish("#{p}-t3", {t_memory - 0.4:.2f}, 0.3);
  pop("#{p}-bubW", {t_remember:.2f}, 0.4, 0.8);
  tl.fromTo("#{p}-orbW",{{opacity:0.7}},{{opacity:0.18,duration:0.9}},{t_lost:.2f});
  tl.fromTo("#{p}-lockW",{{rotation:-8,transformOrigin:"50% 50%"}},{{rotation:8,duration:0.12,repeat:5,yoyo:true,ease:"none"}},{t_lost:.2f});
  tl.fromTo("#{p}-cable",{{attr:{{"stroke-dashoffset":700}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.9,ease:"power2.out"}},{t_science - 0.3:.2f});
  [0,1].forEach(function(j){{
    tl.fromTo("#{p}-lightBeam",{{opacity:0,attr:{{"stroke-dashoffset":90}}}},{{opacity:1,attr:{{"stroke-dashoffset":-650}},duration:0.8,ease:"power1.in",immediateRender:false}},{t_switch_on:.2f}+j*1.0);
  }});
  tl.fromTo("#{p}-halo",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:0.75,scale:1.6,transformOrigin:"50% 50%",duration:0.45,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_light:.2f});
  tl.fromTo("#{p}-nodes .n",{{attr:{{fill:"#9aa0c8"}}}},{{attr:{{fill:"#7fe6ff"}},duration:0.2,stagger:0.07}},{t_neurons:.2f});
  tl.fromTo("#{p}-shackle0",{{y:0}},{{y:-30,duration:0.35,ease:"back.out(3)"}},{t_memory - 0.15:.2f});
  tl.fromTo("#{p}-lockW",{{opacity:1,y:0}},{{opacity:0,y:80,duration:0.6,ease:"power2.in",immediateRender:false}},{t_memory + 0.3:.2f});
  tl.fromTo("#{p}-orbW",{{opacity:0.18,scale:1,transformOrigin:"50% 50%"}},{{opacity:1,scale:1.5,transformOrigin:"50% 50%",duration:0.7,ease:"elastic.out(1,0.5)",immediateRender:false}},{t_memory:.2f});
  enter("#{p}-rings", {t_memory:.2f}, 0.1);
  ["a1","a2"].forEach(function(q,i){{tl.fromTo("#{p}-"+q,{{scale:0.6,opacity:0.9,transformOrigin:"50% 50%"}},{{scale:2.0,opacity:0,transformOrigin:"50% 50%",duration:1.0,ease:"power2.out"}},{t_memory:.2f}+i*0.4);}});
  rise("#{p}-t4 span", {t_memory:.2f}, 0.8);
  tl.fromTo("#{p}-rEyelid",{{y:-52}},{{y:0,duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t_amnesia + 1.2:.2f});
  tl.fromTo("#{p}-rEyelid",{{y:-52}},{{y:0,duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t_light + 0.6:.2f});
"""
    return comp(p, dur, svg, html, js, box_grad(p, "c"))


def person_at(cx, cy, s):
    """State (x, y, s) that puts the center of the person's head at (cx, cy) with scale s."""
    return (round(cx - s * 205, 2), round(cy - s * 140, 2), s)


def brain_at(cx, cy, s):
    """Center of the brain in world space for the person with the head centered at (cx, cy), scale s."""
    return cx - 13 * s, cy - 56 * s


def shards(p, k, color=AMBER, r=30):
    """A memory that breaks: 5 shards {p}-sh{k}-i around (0,0)."""
    pts = [(-1, -1), (1, -1), (1.2, .6), (-.2, 1.2), (-1.2, .4)]
    out = ""
    for i, (dx, dy) in enumerate(pts):
        out += (f'<g id="{p}-sh{k}-{i}"><path d="M0 0 L{dx * r:.0f} {dy * r:.0f} L{pts[(i + 1) % 5][0] * r:.0f} {pts[(i + 1) % 5][1] * r:.0f} Z" '
                f'fill="{color}" stroke="#fff3c8" stroke-width="2"/></g>')
    return out


# ================================================================ 1 doc: doorway effect (Radvansky and Copeland, 2006)
# Living room. The person carries the memory in the bubble, walks through the door on the right into the other room and the memory breaks.
def locked_1():
    p = "locked_1"
    start, dur = seg(SCENE, 1)
    t_effect, t_2006, t_study, t_through, t_hinder, t_remember, t_you = 1.94, 3.6, 5.31, 6.62, 8.1, 8.93, 10.0
    g = p + "-g"
    X, Y, W, H = 1370, 300, 320, 600
    next_room = (f'<rect x="{X}" y="{Y}" width="{W}" height="{H}" fill="url(#{p}-nextRoomG)"/>'
             f'<polygon points="{X},{Y + H} {X + W},{Y + H} {X + W * .78},{Y + H - 150} {X + W * .22},{Y + H - 150}" fill="#3a2a30"/>'
             f'<rect x="{X + W * .3:.0f}" y="{Y + 110}" width="{W * .4:.0f}" height="{H * .3:.0f}" fill="#bfe6ff" opacity=".25"/>'
             f'<rect x="{X + W * .3:.0f}" y="{Y + 110}" width="{W * .4:.0f}" height="{H * .3:.0f}" fill="none" stroke="#d9cfe8" stroke-width="5" opacity=".5"/>')
    door = front_door(p, 0, X, Y, W, H).replace("@GAP0@", next_room)
    w0, d0 = room(p, 0, -700, 2700, "#3c2d80", "#241a58", floor_color="#22163a")
    rug = '<ellipse cx="760" cy="960" rx="560" ry="46" fill="#ff8fb8" opacity=".22"/><ellipse cx="760" cy="960" rx="500" ry="36" fill="none" stroke="#ff8fb8" stroke-width="4" opacity=".4"/>'
    decor = (rug + G.picture(f"{p}-pic0", "family", 1205, 430, .55)
            + armchair(660, 900, .8) + plant(1820, s=.95))
    c0 = (900, 900, .85)
    inside = (1500, 845, .42)
    tr0, js_mov = move(f"#{p}-personW", c0, [(t_through - 0.1, 1.5, inside, "power1.inOut")])
    memory = f'<g id="{p}-orbW">{G.orb(p + "-ob", "clock", 0, 0, AMBER, 52)}</g><g id="{p}-shards" opacity="0">{shards(p, 0, AMBER, 40)}</g>'
    svg = f"""{w0}{decor}
<ellipse cx="{X + W / 2}" cy="905" rx="230" ry="18" fill="#05031a" opacity=".5"/>
{door}
<g id="{p}-personW" transform="{tr0}">{human(p, "home", "standing")}{bubble_h(p, 0, memory)}</g>"""
    img = os.path.join(DOCS, "radvansky2006.png")
    if os.path.exists(img):  # real page, if someone drops the PNG into assets/docs
        b64 = base64.b64encode(open(img, "rb").read()).decode()
        inner = f'<img src="data:image/png;base64,{b64}" style="width:100%;display:block;border-radius:6px">'
    else:  # card with the real citation (the page is not in the repository: see CREDITS.md in film)
        inner = ("<div style=\"font:700 44px 'IBM Plex Mono',monospace;letter-spacing:.06em;color:#ffb23e\">MEMORY &amp; COGNITION</div>"
                 "<div style=\"font:700 64px 'EB Garamond',serif;line-height:1.05;color:#fffaf0;margin:26px 0 22px;white-space:normal\">"
                 f"Walking through doorways <span id=\"{p}-mk\" style=\"background:linear-gradient(#ffb23e66,#ffb23e66) no-repeat 0 85%/0% 40%\">causes forgetting</span></div>"
                 "<div style=\"font:500 44px 'IBM Plex Mono',monospace;color:#c9b8ff\">Radvansky and Copeland</div>")
    card = (f'<div id="{p}-card" style="position:absolute;left:60px;top:430px;width:600px;padding:40px 44px;border-radius:22px;'
            f'background:rgba(16,12,52,.94);border:4px solid #8d7bff;box-shadow:0 30px 80px rgba(0,0,0,.6);opacity:0">{inner}</div>')
    html = (title(f"{p}-t1", "DOORWAY EFFECT", "left:70px;top:116px", 86, "#ffd98a") +
            title(f"{p}-t2", "2006", "left:76px;top:262px", 120, "#bff4ff", True) + card)
    js = cam(p, (1.0, 960, 540), [
        (0, t_through, (1.05, 940, 560), "sine.inOut"),
        (t_through - 0.2, 1.8, (1.18, 1300, 590), "power2.inOut"),
        (t_you - 0.3, dur - t_you + 0.3, (1.85, 1530, 640), "power3.inOut")])
    js += js_mov + f"""
  pop("#{p}-bub0", 0.3, 0.3, 0.8);
  tl.fromTo("#{p}-orbW",{{rotation:-6,transformOrigin:"50% 50%"}},{{rotation:6,duration:0.6,repeat:7,yoyo:true,ease:"sine.inOut"}},0.9);
  tl.fromTo("#{g}-eye",{{x:0}},{{x:2,duration:0.3}},0.6);
  rise("#{p}-t1 span", {t_effect:.2f}, 0.8);
  tl.fromTo("#{p}-leaf0",{{scaleX:1,transformOrigin:"0% 50%"}},{{scaleX:0.06,transformOrigin:"0% 50%",duration:0.6,ease:"power2.inOut"}},{t_effect + 0.6:.2f});
  rise("#{p}-t2 span", {t_2006:.2f}, 0.8);
  tl.fromTo("#{p}-card",{{opacity:0,y:60}},{{opacity:1,y:0,duration:0.8,ease:"expo.out"}},{t_study:.2f});
  tl.fromTo("#{p}-mk",{{backgroundSize:"0% 40%"}},{{backgroundSize:"100% 40%",duration:0.9,ease:"power2.inOut"}},{t_through:.2f});
  tl.fromTo("#{g}-body",{{y:0}},{{y:-12,duration:0.17,repeat:7,yoyo:true,ease:"sine.inOut"}},{t_through - 0.1:.2f});
  tl.fromTo("#{p}-orbW",{{opacity:1}},{{opacity:0,duration:0.15,immediateRender:false}},{t_remember - 0.3:.2f});
  enter("#{p}-shards", {t_remember - 0.3:.2f}, 0.05);
  [[-30,-24],[32,-26],[38,18],[-6,32],[-40,14]].forEach(function(d,i){{
    tl.fromTo("#{p}-sh0-"+i,{{x:0,y:0,rotation:0,transformOrigin:"50% 50%"}},{{x:d[0],y:d[1],rotation:(i%2?90:-90),duration:1.1,ease:"power2.out"}},{t_remember - 0.3:.2f});
  }});
  tl.fromTo("#{p}-shards",{{opacity:1}},{{opacity:0.35,duration:0.8,immediateRender:false}},{t_remember + 0.8:.2f});
  vanish("#{p}-card", {t_you - 0.4:.2f}, 0.4); vanish("#{p}-t2", {t_you - 0.4:.2f}, 0.4); vanish("#{p}-t1", {t_you - 0.4:.2f}, 0.4);
  tl.fromTo("#{g}-eye",{{x:2}},{{x:-2,duration:0.25,repeat:3,yoyo:true,immediateRender:false}},{t_remember:.2f});
""" + idle_h(p, dur, (1.4, 4.4, 9.4))
    return comp(p, dur, svg, html, js, d0 + f'<linearGradient id="{p}-nextRoomG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a2a3a"/><stop offset=".7" stop-color="#7a4a5a"/><stop offset="1" stop-color="#8a5a62"/></linearGradient>')


# ================================================================ 2 episodes: the door marks the end of one; remembering means opening a path
def locked_2():
    p = "locked_2"
    start, dur = seg(SCENE, 2)
    (t_brain, t_episodes, t_door, t_end, t_effect, t_small, t_not_even, t_erase, t_remember, t_open, t_path, t_can, t_fail) = (
        1.66, 3.68, 4.91, 5.96, 7.21, 7.78, 8.54, 9.53,
        12.39, 14.05, 14.55, 15.68, 16.06)
    cx, cy, s = 300, 530, 1.9
    bx, by = brain_at(cx, cy, s)
    EW, EG, E0, EY, EH = 250, 64, 600, 380, 300
    colors = [(LILAC, "#2c2470"), (MINT, "#123f3c"), (AMBER, "#4a3216"), (MAGENTA, "#4a1636")]
    eps, doors = "", ""
    for i, (c, f) in enumerate(colors):
        x = E0 + i * (EW + EG)
        kind = ["family", "birthday", "car", "graduation"][i]
        sc = (EH - 28) / 150
        obj = (f'<clipPath id="{p}-ec{i}"><rect x="{x + 14}" y="{EY + 14}" width="{EW - 28}" height="{EH - 28}" rx="12"/></clipPath>'
               f'<rect x="{x + 14}" y="{EY + 14}" width="{EW - 28}" height="{EH - 28}" rx="12" fill="#fffaf0"/>'
               f'<g clip-path="url(#{p}-ec{i})"><g transform="translate({x + 14 - (200 * sc - EW + 28) / 2:.1f} {EY + 14}) scale({sc:.3f})">{G.picture_scene(kind)}</g></g>')
        eps += (f'<g id="{p}-ep{i}"><g filter="url(#{p}-shadow)"><rect x="{x}" y="{EY}" width="{EW}" height="{EH}" rx="18" fill="{f}"/></g>'
                f'{obj}'
                f'<rect x="{x}" y="{EY}" width="{EW}" height="{EH}" rx="18" fill="none" stroke="{c}" stroke-width="5"/></g>')
        if i < 3:
            dx = x + EW + EG / 2
            doors += (f'<g id="{p}-door{i}"><rect x="{dx - 26}" y="{EY - 30}" width="52" height="{EH + 60}" rx="6" fill="#1d1752" stroke="{LILAC}" stroke-width="5"/>'
                       f'<g id="{p}-doorLeaf{i}"><rect x="{dx - 18}" y="{EY - 20}" width="36" height="{EH + 40}" fill="#3a2f9a"/><circle cx="{dx + 10}" cy="{EY + EH / 2}" r="6" fill="{AMBER}"/></g></g>')
    xs = [E0 + i * (EW + EG) + EW / 2 for i in range(4)]
    ym = EY + EH / 2
    path_d = f"M{bx:.0f} {by:.0f} C {bx + 120:.0f} {by - 160:.0f} {E0 - 80} {ym} {xs[0]:.0f} {ym}" + "".join(f" L{x:.0f} {ym}" for x in xs[1:])
    fail_x = E0 + 2 * (EW + EG) + EW + EG / 2
    svg = f"""<g id="{p}-personW" transform="translate({person_at(cx, cy, s)[0]} {person_at(cx, cy, s)[1]}) scale({s})">{person(p)}</g>
<g id="{p}-eps">{eps}</g>{doors}
<path id="{p}-path1" d="{path_d}" fill="none" stroke="#bff4ff" stroke-width="12" stroke-linecap="round" stroke-dasharray="2400" stroke-dashoffset="2400" filter="url(#{p}-glow)"/>
<g id="{p}-x" opacity="0" stroke="{RED}" stroke-width="18" stroke-linecap="round" filter="url(#{p}-glow)"><path d="M{fail_x - 50} {ym - 50} L{fail_x + 50} {ym + 50} M{fail_x + 50} {ym - 50} L{fail_x - 50} {ym + 50}"/></g>"""
    html = (title(f"{p}-t1", "EPISODES", "left:0;right:0;text-align:center;top:120px", 120, "#eef1f7") +
            title(f"{p}-t2", "THE EFFECT IS SMALL", "left:0;right:0;text-align:center;top:140px", 64, "#c9b8ff", True) +
            title(f"{p}-t3", "REMEMBERING MEANS OPENING A PATH", "left:0;right:0;text-align:center;top:120px", 88, "#bff4ff") +
            title(f"{p}-t4", "AND THE PATH CAN FAIL", "left:0;right:0;text-align:center;top:800px", 80, "#ff9bb0", True))
    js = cam(p, (1.5, 360, 520), [
        (t_brain + 0.3, 1.7, (1.0, 960, 540), "power3.inOut"),
        (t_episodes + 0.3, t_small - t_episodes - 0.5, (1.04, 940, 540), "sine.inOut"),
        (t_small - 0.2, 1.4, (0.95, 960, 540), "power3.inOut"),
        (t_remember - 0.4, 1.4, (1.0, 960, 560), "power3.inOut"),
        (t_open, dur - t_open, (1.03, 960, 550), "sine.inOut")])
    js += f"""
  tl.fromTo("#{p}-brain",{{opacity:0.95}},{{opacity:0.5,duration:0.4,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_brain:.2f});
  tl.fromTo("#{p}-ep0,#{p}-ep1,#{p}-ep2,#{p}-ep3",{{opacity:0,scale:0.5,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.7,ease:"elastic.out(1,0.55)",stagger:0.22}},{t_brain + 0.7:.2f});
  rise("#{p}-t1 span", {t_episodes:.2f}, 0.8);
  vanish("#{p}-t1", {t_effect - 0.2:.2f}, 0.3);
  tl.fromTo("#{p}-door0,#{p}-door1,#{p}-door2",{{opacity:0,y:-320}},{{opacity:1,y:0,duration:0.55,ease:"bounce.out",stagger:0.18}},{t_door - 0.1:.2f});
  tl.fromTo("#{p}-ep0",{{opacity:1}},{{opacity:0.45,duration:0.6,immediateRender:false}},{t_end:.2f});
  rise("#{p}-t2 span", {t_effect:.2f});
  tl.fromTo("#{p}-door1",{{opacity:1}},{{opacity:0.25,duration:0.12,repeat:5,yoyo:true,ease:"none",immediateRender:false}},{t_not_even:.2f});
  vanish("#{p}-t2", {t_remember - 0.4:.2f}, 0.3);
  tl.fromTo("#{p}-ep0",{{opacity:0.45}},{{opacity:1,duration:0.6,immediateRender:false}},{t_remember:.2f});
  rise("#{p}-t3 span", {t_remember:.2f}, 0.8);
  tl.fromTo("#{p}-path1",{{attr:{{"stroke-dashoffset":2400}}}},{{attr:{{"stroke-dashoffset":1180}},duration:{t_path - t_remember:.2f},ease:"power1.inOut"}},{t_remember:.2f});
  tl.fromTo("#{p}-doorLeaf0,#{p}-doorLeaf1",{{scaleX:1,transformOrigin:"0% 50%"}},{{scaleX:0.1,transformOrigin:"0% 50%",duration:0.35,stagger:0.45}},{t_open:.2f});
  tl.fromTo("#{p}-path1",{{attr:{{"stroke-dashoffset":1180}}}},{{attr:{{"stroke-dashoffset":620}},duration:1.0,ease:"power1.in",immediateRender:false}},{t_path:.2f});
  tl.fromTo("#{p}-path1",{{stroke:"#bff4ff"}},{{stroke:"#ff4f7d",duration:0.2,immediateRender:false}},{t_fail:.2f});
  pop("#{p}-x", {t_fail:.2f}, 0.3, 0.6);
  tl.fromTo("#{p}-door2",{{x:-6}},{{x:6,duration:0.05,repeat:9,yoyo:true,ease:"none",immediateRender:false}},{t_fail:.2f});
  vanish("#{p}-t3", {t_can - 0.5:.2f}, 0.3);
  rise("#{p}-t4 span", {t_can - 0.6:.2f}, 0.7);
  tl.fromTo("#{p}-eye",{{x:0}},{{x:3,duration:0.4}},{t_episodes:.2f});
""" + person_idle(p, dur, (2.0, 6.2, 9.9, 13.2, 16.6))
    return comp(p, dur, svg, html, js)


# ================================================================ 3 trauma: bedroom at night, the person does not remember, but the body reacts
# The bed, the lamp, the cup, the radio and the window are in the scene from the start; each one becomes the trigger at its word_time.
def locked_3():
    p = "locked_3"
    start, dur = seg(SCENE, 3)
    (t_be, t_violent, t_can, t_remember, t_body, t_smell, t_sound, t_place, t_back, t_without) = (
        1.59, 4.17, 4.81, 6.11, 9.51, 10.79, 12.02, 12.57, 13.75, 15.03)
    g = p + "-g"
    PX, S = 470, .95
    hx, hy = PX + S * anchors("sitting")["head_center"][0], 900 + S * anchors("sitting")["head_center"][1]  # head center
    w0, d0 = room(p, 0, -700, 2700, "#2c2266", "#120e34", floor_color="#1a1230", baseboard="#4a3a7a")
    bed = ('<rect x="230" y="560" width="34" height="340" rx="12" fill="#4a2e6a" stroke="#8d7bff" stroke-width="4"/>'
            '<rect x="240" y="800" width="420" height="52" rx="10" fill="#4a2e6a"/><rect x="250" y="852" width="20" height="48" fill="#2a1a40"/><rect x="630" y="852" width="20" height="48" fill="#2a1a40"/>'
            '<rect x="252" y="742" width="400" height="62" rx="18" fill="#d9d0ff"/><ellipse cx="318" cy="730" rx="54" ry="24" fill="#f4f0ff"/>'
            '<path d="M340 736 Q 480 724 652 744 L 652 812 Q 480 822 340 810 Z" fill="#5a4ab0"/><path d="M360 760 Q 500 750 640 768" stroke="#8d7bff" stroke-width="4" fill="none" opacity=".6"/>')
    nightstand = (table(980, 1160, 720, color="#5a3a5a", leg="#3a2440") + table_lamp(1030, 720)
               + '<rect x="1092" y="684" width="38" height="36" rx="6" fill="#fffaf0"/><path d="M1130 692 q12 0 10 12 q-2 8 -10 6" stroke="#fffaf0" stroke-width="5" fill="none"/>'
               + f'<g id="{p}-steam" opacity=".45" fill="none" stroke="#e8e0ff" stroke-width="5" stroke-linecap="round"><path d="M1102 676 q-10 -18 0 -34 q10 -16 0 -32"/><path d="M1120 676 q-10 -18 0 -34 q10 -16 0 -32"/></g>')
    dresser = ('<rect x="1230" y="640" width="290" height="260" rx="10" fill="#3a2a5a" stroke="#6a5ab0" stroke-width="4"/>'
              + "".join(f'<rect x="1250" y="{y}" width="250" height="68" rx="6" fill="none" stroke="#6a5ab0" stroke-width="4"/><circle cx="1375" cy="{y + 34}" r="7" fill="#c9b8ff"/>' for y in (662, 742, 822))
              + '<rect x="1300" y="548" width="150" height="92" rx="14" fill="#c96a4a"/><circle cx="1340" cy="594" r="26" fill="#3a1a1a"/><circle cx="1340" cy="594" r="12" fill="#6a3a2a"/>'
              + '<rect x="1384" y="570" width="50" height="14" rx="4" fill="#ffd27a"/><rect x="1384" y="600" width="50" height="10" rx="4" fill="#3a1a1a"/><path d="M1420 548 L1460 488" stroke="#c9cce8" stroke-width="5" stroke-linecap="round"/>'
              + f'<g id="{p}-waves" opacity="0" fill="none" stroke="{MAGENTA}" stroke-width="7" stroke-linecap="round"><path d="M1470 566 q16 28 0 56"/><path d="M1492 548 q26 46 0 92"/><path d="M1514 530 q36 64 0 128"/></g>')
    win = (window(1590, 220, 260, 300, sky=("#0a0f30", "#1a1a50"), curtain="#6a5ab0")
           + f'<g id="{p}-winFlash" opacity="0"><rect x="1590" y="220" width="260" height="300" fill="{MAGENTA}" opacity=".5"/>'
           + '<path d="M1640 520 V330 M1620 330 H1670" stroke="#1a0820" stroke-width="10"/><rect x="1700" y="390" width="120" height="130" fill="#1a0820"/></g>')
    pictures = (G.picture(f"{p}-pic0", "beach", 250, 390, .8) + f'<g transform="translate(250 390) scale(1.6)"><g id="{p}-picDark" opacity="0">{picture_dark()}</g></g>')
    objs = [(1110, 650), (1375, 594), (1720, 370)]       # cup, radio, window
    labs = [("A SMELL", t_smell, 1070), ("A SOUND", t_sound, 1375), ("A PLACE", t_place, 1720)]
    halos = "".join(f'<circle id="{p}-h{i}" cx="{x}" cy="{y}" r="110" fill="{MAGENTA}" opacity="0" filter="url(#{p}-blur6)"/>' for i, (x, y) in enumerate(objs))
    lines = "".join(f'<path id="{p}-l{i}" d="M{x} {y} C {x - 200} {y - 160} {hx + 260:.0f} {hy - 160:.0f} {hx + 40:.0f} {hy:.0f}" fill="none" stroke="{MAGENTA}" stroke-width="7" stroke-dasharray="40 1400" stroke-dashoffset="40" opacity="0" filter="url(#{p}-glow)"/>' for i, (x, y) in enumerate(objs))
    ecg = "M-200 1035 " + " ".join("h140 l14 -50 l18 100 l14 -70 l10 20" for _ in range(16))
    bolts = "".join(f'<g transform="translate({hx + dx:.0f} {hy + dy:.0f}) rotate({r})">{bolt(0, 0, 1.0, RED)}</g>' for dx, dy, r in [(-150, -60, -20), (150, -90, 25), (10, -190, 0)])
    drops = "".join(drop(hx + dx, hy + dy, 1.2) for dx, dy in [(-50, -40), (62, -10), (-20, 30)])
    inner = f'<g id="{p}-orbW" opacity="0">{orb(p, 0, RED, 40)}</g><g transform="scale(.55)"><g id="{p}-lockW" opacity="0">{padlock(p, 0)}</g></g>'
    extra = (f'<radialGradient id="{p}-redG" cx="50%" cy="50%" r="70%"><stop offset=".35" stop-color="#ff1f5a" stop-opacity="0"/><stop offset="1" stop-color="#ff1f5a" stop-opacity="1"/></radialGradient>'
             f'<radialGradient id="{p}-fearG"><stop offset="0" stop-color="#ff4f7d" stop-opacity=".8"/><stop offset="1" stop-color="#ff4f7d" stop-opacity="0"/></radialGradient>')
    svg = f"""{w0}{pictures}{win}{dresser}{nightstand}{bed}{halos}
<circle id="{p}-fear" cx="{hx:.0f}" cy="{hy + 60:.0f}" r="300" fill="url(#{p}-fearG)" opacity="0"/>
<g id="{p}-bolts" opacity="0">{bolts}</g>
<g transform="translate({PX} 900) scale({S})"><g id="{p}-shake">{human(p, "home", "sitting", chair=False, mug=False)}{bubble_h(p, 0, inner, sitting=True)}</g></g>
<g id="{p}-drops" opacity="0">{drops}</g>
{lines}
<path id="{p}-ecg" d="{ecg}" fill="none" stroke="{RED}" stroke-width="6" stroke-linejoin="round" stroke-dasharray="12000" stroke-dashoffset="12000" filter="url(#{p}-glow)"/>
<rect id="{p}-flash" x="-400" y="-400" width="2720" height="1880" fill="#ff2a63" opacity="0"/>
<rect id="{p}-redwash" x="-400" y="-400" width="2720" height="1880" fill="url(#{p}-redG)" opacity="0"/>"""
    html = (title(f"{p}-t0", "MAY NOT BE ABLE TO REMEMBER", "left:0;right:0;text-align:center;top:60px", 64, "#eef1f7", True) +
            title(f"{p}-t1", "THE BODY REACTS", "left:0;right:0;text-align:center;top:36px", 110, "#ff9bb0") +
            "".join(title(f"{p}-n{i}", name, f"left:{x - 160}px;width:320px;text-align:center;top:908px", 52, "#ffd2e6", True) for i, (name, _, x) in enumerate(labs)) +
            title(f"{p}-t2", "WITHOUT WARNING", "left:780px;top:236px", 72, "#ff4f7d", True))
    js = cam(p, (1.0, 960, 540), [
        (1.0, 1.8, (1.25, 700, 505), "power3.inOut"),
        (t_violent + 0.2, 2.2, (1.28, 710, 505), "power3.inOut"),
        (t_body - 0.6, 1.4, (1.0, 960, 540), "power3.inOut"),
        (t_back - 0.1, 0.2, (1.03, 960, 540), "power4.out"),
        (t_back + 0.1, 0.8, (1.0, 960, 540), "power2.out")])
    js += f"""
  pop("#{p}-bub0", 0.4, 0.3, 0.8);
  enter("#{p}-orbW", 0.6, 0.5);
  tl.fromTo("#{p}-orbW",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.2,duration:0.5,repeat:3,yoyo:true,ease:"sine.inOut"}},0.6);
  tl.fromTo("#{p}-steam",{{y:0}},{{y:-10,duration:1.2,repeat:{int(dur / 1.2)},yoyo:true,ease:"sine.inOut"}},0);
  tl.fromTo("#{p}-flash",{{opacity:0}},{{opacity:0.5,duration:0.06}},{t_violent:.2f});
  tl.fromTo("#{p}-flash",{{opacity:0.5}},{{opacity:0,duration:0.5,immediateRender:false}},{t_violent + 0.06:.2f});
  enter("#{p}-bolts", {t_violent:.2f}, 0.05); vanish("#{p}-bolts", {t_violent + 0.6:.2f}, 0.3);
  tl.fromTo("#{p}-shake",{{x:-4}},{{x:4,duration:0.05,repeat:9,yoyo:true,ease:"none"}},{t_violent:.2f});
  tl.fromTo("#{g}-head",{{rotation:0,svgOrigin:"{neck("sitting")}"}},{{rotation:-6,svgOrigin:"{neck("sitting")}",duration:0.3,ease:"back.out(2)"}},{t_violent:.2f});
  rise("#{p}-t0 span", {t_can:.2f});
  pop("#{p}-lockW", {t_remember - 0.2:.2f}, 2.2, 0.6);
  tl.fromTo("#{p}-orbW",{{opacity:1}},{{opacity:0,duration:0.4,immediateRender:false}},{t_remember:.2f});
  enter("#{p}-picDark", {t_remember:.2f}, 0.6);
  tl.fromTo("#{g}-eye",{{x:0}},{{x:-3,duration:0.3,repeat:3,yoyo:true}},{t_remember + 0.6:.2f});
  vanish("#{p}-t0", {t_body - 0.6:.2f}, 0.3);
  rise("#{p}-t1 span", {t_body - 0.1:.2f}, 0.8);
  enter("#{p}-drops", {t_body:.2f}, 0.4);
  tl.fromTo("#{p}-drops",{{y:0}},{{y:16,duration:1.4,repeat:{int((dur - t_body) / 1.4)},ease:"power1.in"}},{t_body:.2f});
  tl.fromTo("#{p}-ecg",{{attr:{{"stroke-dashoffset":12000}}}},{{attr:{{"stroke-dashoffset":2200}},duration:{dur - t_body:.2f},ease:"none"}},{t_body - 0.2:.2f});
  tl.fromTo("#{p}-shake",{{x:-2}},{{x:2,duration:0.06,repeat:{int((dur - t_body) / 0.06) - 2},yoyo:true,ease:"none",immediateRender:false}},{t_body + 0.1:.2f});
  tl.fromTo("#{p}-waves path",{{opacity:0.2}},{{opacity:1,duration:0.15,stagger:0.08,repeat:5,yoyo:true,immediateRender:false}},{t_sound:.2f});
  enter("#{p}-waves", {t_sound:.2f}, 0.05);
  tl.fromTo("#{p}-steam",{{opacity:0.45,attr:{{stroke:"#e8e0ff"}}}},{{opacity:1,attr:{{stroke:"#ff4fa3"}},duration:0.3,immediateRender:false}},{t_smell:.2f});
  tl.fromTo("#{p}-winFlash",{{opacity:0}},{{opacity:1,duration:0.12,repeat:3,yoyo:true,ease:"none"}},{t_place:.2f});
  tl.fromTo("#{p}-winFlash",{{opacity:0}},{{opacity:0.8,duration:0.3,immediateRender:false}},{t_place + 0.6:.2f});
""" + "".join(f"""
  tl.fromTo("#{p}-h{i}",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:0.55,scale:1,transformOrigin:"50% 50%",duration:0.5,ease:"power3.out"}},{tt - 0.05:.2f});
  rise("#{p}-n{i} span", {tt:.2f}, 0.6);
  tl.fromTo("#{p}-l{i}",{{opacity:1,attr:{{"stroke-dashoffset":40}}}},{{opacity:1,attr:{{"stroke-dashoffset":-1300}},duration:0.7,ease:"power1.in"}},{tt + 0.15:.2f});
  tl.fromTo("#{p}-l{i}",{{opacity:1}},{{opacity:0,duration:0.1,immediateRender:false}},{tt + 0.85:.2f});
  tl.fromTo("#{p}-lockW",{{rotation:-9,transformOrigin:"50% 50%"}},{{rotation:9,duration:0.07,repeat:5,yoyo:true,ease:"none",immediateRender:false}},{tt + 0.8:.2f});""" for i, (_, tt, _x) in enumerate(labs)) + f"""
  tl.fromTo("#{p}-fear",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:1,scale:1.15,transformOrigin:"50% 50%",duration:0.5,ease:"power4.out"}},{t_back:.2f});
  tl.fromTo("#{p}-redwash",{{opacity:0}},{{opacity:0.85,duration:0.5,ease:"power2.out"}},{t_back:.2f});
  tl.fromTo("#{p}-fear",{{scale:1.15}},{{scale:0.95,duration:0.4,repeat:{int((dur - t_back - 0.5) / 0.4)},yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_back + 0.5:.2f});
  rise("#{p}-t2 span", {t_without:.2f}, 0.6);
""" + idle_h(p, dur, (1.2, 3.4, 8.6, 12.9))
    return comp(p, dur, svg, html, js, d0 + extra, background=("#3a1238", "#1c0a30", "#0a0614"), seed=21)


# ================================================================ 5 line: it had not been erased, it was just out of reach
def locked_5():
    p = "locked_5"
    start, dur = seg(SCENE, 5)
    t_had, t_erased, t_just, t_without = 0.51, 1.32, 2.35, 3.26
    X, Y, W, H = 770, 210, 380, 620
    light = (f'<rect x="{X}" y="{Y}" width="{W}" height="{H}" fill="#ffd27a"/>')
    door = front_door(p, 0, X, Y, W, H).replace("@GAP0@", light)
    gaps = (f'<g id="{p}-gap" opacity=".35" filter="url(#{p}-glow)"><rect x="{X - 4}" y="{Y}" width="8" height="{H}" fill="#ffd27a"/>'
               f'<rect x="{X + W - 4}" y="{Y}" width="8" height="{H}" fill="#ffd27a"/><rect x="{X}" y="{Y + H - 6}" width="{W}" height="10" fill="#ffd27a"/></g>'
               f'<polygon id="{p}-beam" points="{X},{Y + H} {X + W},{Y + H} {X + W + 260},1080 {X - 260},1080" fill="url(#{p}-beamG)" opacity=".3"/>')
    step = (W + 52) / 9
    chain = (f'<g id="{p}-chain"><rect x="{X - 44}" y="{Y + H * .5 - 40:.0f}" width="26" height="80" rx="6" fill="#9aa0c8" stroke="#eef1f7" stroke-width="3"/>'
                f'<rect x="{X + W + 18}" y="{Y + H * .5 - 40:.0f}" width="26" height="80" rx="6" fill="#9aa0c8" stroke="#eef1f7" stroke-width="3"/>'
                f'<g fill="none" stroke="#c9cce8" stroke-width="14">' +
                "".join(f'<ellipse cx="{X - 26 + i * step:.0f}" cy="{Y + H * .5:.0f}" rx="{step * .62:.0f}" ry="15"/>' for i in range(10)) + '</g></g>')
    svg = f"""{wall(p, 860)}
{gaps}
{door}
<g transform="translate({X + W / 2 + 1} {Y + H * .5 + 60})"><g id="{p}-lockW" opacity="0"><g transform="scale(1.4)">{padlock(p, 0)}</g></g></g>
{chain}"""
    extra = wall_defs(p) + f'<linearGradient id="{p}-beamG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd27a" stop-opacity=".8"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></linearGradient>'
    html = (title(f"{p}-t1", "IT HADN'T BEEN ERASED", "left:0;right:0;text-align:center;top:40px", 92, "#ffd98a") +
            title(f"{p}-t2", "IT WAS JUST OUT OF REACH", "left:0;right:0;text-align:center;top:920px", 92, "#bff4ff"))
    js = cam(p, (1.0, 960, 540), [(0, dur, (1.12, 960, 520), "sine.inOut")])
    js += f"""
  rise("#{p}-t1 span", {t_had:.2f}, 0.8);
  tl.fromTo("#{p}-leaf0",{{scaleX:1,transformOrigin:"0% 50%"}},{{scaleX:0.82,transformOrigin:"0% 50%",duration:0.5,ease:"power2.out"}},{t_erased - 0.2:.2f});
  tl.fromTo("#{p}-gap",{{opacity:0.35}},{{opacity:1,duration:0.5}},{t_erased - 0.2:.2f});
  tl.fromTo("#{p}-beam",{{opacity:0.3}},{{opacity:1,duration:0.6}},{t_erased - 0.2:.2f});
  tl.fromTo("#{p}-leaf0",{{scaleX:0.82}},{{scaleX:1,transformOrigin:"0% 50%",duration:0.2,ease:"power4.in",immediateRender:false}},{t_just - 0.1:.2f});
  tl.fromTo("#{p}-gap",{{opacity:1}},{{opacity:0.6,duration:0.3,immediateRender:false}},{t_just:.2f});
  tl.fromTo("#{p}-beam",{{opacity:1}},{{opacity:0.45,duration:0.3,immediateRender:false}},{t_just:.2f});
  tl.fromTo("#{p}-chain ellipse, #{p}-chain rect",{{opacity:0,y:-60}},{{opacity:1,y:0,duration:0.25,stagger:0.04,ease:"power2.out"}},{t_just + 0.1:.2f});
  tl.fromTo("#{p}-lockW",{{opacity:0,y:-500}},{{opacity:1,y:0,duration:0.55,ease:"bounce.out"}},{t_without - 0.45:.2f});
  rise("#{p}-t2 span", {t_without:.2f}, 0.8);
  tl.fromTo("#{p}-gap",{{opacity:0.6}},{{opacity:0.95,duration:0.9,repeat:2,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_without + 0.3:.2f});
"""
    return comp(p, dur, svg, html, js, extra)


# ================================================================ 6 drug: doctor's office, the patient takes propranolol before recalling
def locked_6():
    p = "locked_6"
    start, dur = seg(SCENE, 6)
    (t_touch, t_people, t_patients, t_stress, t_drug, t_propranolol, t_recall, t_trauma, t_dim, t_load, t_emotion) = (
        1.42, 3.45, 6.72, 7.9, 10.13, 11.86, 14.06, 14.66, 16.33, 16.72, 17.13)
    g = p + "-g"
    PX, S = 600, 1.0
    bx, by = PX + S * bubble_xy("sitting")[0], 900 + S * bubble_xy("sitting")[1]          # bubble center
    cc = anchors("sitting")["head_center"]
    mx, my = PX + S * (cc[0] + 22), 900 + S * (cc[1] + 30)          # mouth
    w0, d0 = room(p, 0, -700, 2700, "#1f4a6a", "#12284a", floor_color="#14223a", baseboard="#3a7a9a")
    decor = (G.picture(f"{p}-pic0", "graduation", 220, 330, .7, frame="#c9a24a") + G.picture(f"{p}-pic1", "beach", 220, 560, .55)
            + G.picture(f"{p}-pic2", "award", 1300, 215, .5, frame="#c9a24a") + G.picture(f"{p}-pic3", "coffee", 1520, 215, .5)
            + '<circle cx="1760" cy="200" r="54" fill="#eef1f7" stroke="#9aa6c0" stroke-width="8"/><path d="M1760 168 V200 L1784 214" stroke="#14223a" stroke-width="7" fill="none" stroke-linecap="round"/>'
            + plant(1070, s=.8) + armchair(PX, 900, 1.0, "#3a8a9a", "#2a6a7a")
            + table(1180, 1640, 720, color="#8a6a4a", leg="#5a4232")
            + '<rect x="1230" y="700" width="120" height="20" rx="3" fill="#fffaf0" transform="rotate(-4 1290 710)"/><path d="M1240 706 H1330" stroke="#9aa6c0" stroke-width="3" transform="rotate(-4 1290 710)"/>'
            + '<rect x="1430" y="640" width="52" height="80" rx="6" fill="#bff4ff" opacity=".45" stroke="#eef1f7" stroke-width="3"/><rect x="1434" y="676" width="44" height="40" rx="4" fill="#3be0ff" opacity=".35"/>'
            + '<rect x="1540" y="670" width="44" height="50" rx="6" fill="#ff8a6a"/><path d="M1550 670 L1546 630 M1562 670 L1566 626 M1574 670 L1584 634" stroke="#eef1f7" stroke-width="4" stroke-linecap="round"/>')
    pill0 = (1430, 380, 1.0)
    tr_p, js_p = move(f"#{p}-pillW", pill0, [(t_recall - 0.4, 0.9, (mx, my, 0.12), "power2.in")])
    key0 = (bx - 330, by - 200, 0.5, -30)
    tr_k, js_k = move(f"#{p}-keyW", key0, [(t_touch - 0.3, 0.9, (bx - 120, by + 13, 0.5, 0), "power3.out")])
    meter = (f'<g id="{p}-meter" opacity="0"><rect x="1700" y="300" width="90" height="500" rx="45" fill="#140f3a" stroke="{LILAC}" stroke-width="5"/>'
               f'<g transform="translate(1745 790)"><g id="{p}-level"><rect x="-33" y="-470" width="66" height="470" rx="33" fill="url(#{p}-loadG)"/></g></g></g>')
    inner = (f'<g id="{p}-orbW" opacity="0"><g id="{p}-orbR">{orb(p, 0, RED, 40)}</g><g id="{p}-orbC" opacity="0">{orb(p, 1, LILAC, 40)}</g></g>'
           f'<g transform="translate(0 4) scale(.5)"><g id="{p}-lockW">{padlock(p, 0)}</g></g>')
    svg = f"""{w0}{decor}
<g transform="translate({PX} 900) scale({S})"><g id="{p}-shake">{human(p, "home", "sitting", chair=False)}{bubble_h(p, 0, inner, sitting=True)}</g></g>
<g id="{p}-keyW" transform="{tr_k}"><g id="{p}-key" opacity="0">{key_shape("#d9dcf0")}</g></g>
<path id="{p}-traj" d="M{pill0[0] - 150} {pill0[1] + 20} C {pill0[0] - 420} {pill0[1] - 180} {mx + 300:.0f} {my - 260:.0f} {mx + 40:.0f} {my - 10:.0f}" fill="none" stroke="{AMBER}" stroke-width="7" stroke-linecap="round" stroke-dasharray="4 26" opacity="0" filter="url(#{p}-glow)"/>
<g id="{p}-pillW" transform="{tr_p}"><g id="{p}-pill" opacity="0"><rect x="-190" y="-80" width="380" height="160" fill="none" opacity="0"/>
 <g filter="url(#{p}-shadow)"><path d="M0 -70 L-110 -70 A70 70 0 0 0 -110 70 L0 70 Z" fill="#fffaf0"/><path d="M0 -70 L110 -70 A70 70 0 0 1 110 70 L0 70 Z" fill="{AMBER}"/></g>
 <rect x="-150" y="-52" width="250" height="22" rx="11" fill="#fff" opacity=".5"/></g></g>
{meter}"""
    extra = d0 + f'<linearGradient id="{p}-loadG" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{AMBER}"/><stop offset="1" stop-color="{RED}"/></linearGradient>'
    html = (title(f"{p}-t1", "POST-TRAUMATIC STRESS", "left:0;right:0;text-align:center;top:60px", 72, "#ff9bb0", True) +
            title(f"{p}-t2", "PROPRANOLOL", "left:1000px;right:60px;text-align:center;top:470px", 110, "#ffd98a") +
            title(f"{p}-t4", "RECALLING THE TRAUMA", "left:1000px;right:60px;text-align:center;top:480px", 60, "#ff9bb0", True) +
            title(f"{p}-t3", "EMOTIONAL WEIGHT", "right:250px;top:920px;text-align:right", 72, "#c9b8ff", True))
    js = cam(p, (1.0, 960, 540), [
        (0.8, 1.6, (1.45, bx - 60, by + 80), "power3.inOut"),
        (t_patients - 0.5, 1.4, (1.0, 960, 540), "power3.inOut"),
        (t_drug - 0.3, 1.3, (1.06, 1100, 520), "power3.inOut"),
        (t_recall - 0.5, 1.5, (1.25, 860, 495), "power3.inOut"),
        (t_dim - 0.4, dur - t_dim + 0.4, (1.0, 1000, 540), "sine.inOut")])
    js += js_p + js_k + f"""
  pop("#{p}-bub0", 0.3, 0.3, 0.8);
  enter("#{p}-orbW", {t_recall + 0.3:.2f}, 0.4);
  enter("#{p}-key", {t_touch - 0.3:.2f}, 0.4);
  tl.fromTo("#{p}-key",{{rotation:0,transformOrigin:"0% 50%"}},{{rotation:14,transformOrigin:"0% 50%",duration:0.18,repeat:5,yoyo:true,ease:"sine.inOut"}},{t_touch + 0.7:.2f});
  tl.fromTo("#{p}-lockW",{{rotation:-6,transformOrigin:"50% 50%"}},{{rotation:6,duration:0.09,repeat:7,yoyo:true,ease:"none"}},{t_touch + 0.7:.2f});
  vanish("#{p}-key", {t_people + 0.6:.2f}, 0.4);
  tl.fromTo("#{g}-eye",{{x:0}},{{x:-2,duration:0.3}},{t_touch:.2f});
  rise("#{p}-t1 span", {t_stress - 0.2:.2f}, 0.8);
  tl.fromTo("#{p}-shake",{{x:-3}},{{x:3,duration:0.05,repeat:15,yoyo:true,ease:"none"}},{t_stress + 0.3:.2f});
  vanish("#{p}-t1", {t_drug - 0.5:.2f}, 0.3);
  pop("#{p}-pill", {t_drug:.2f}, 0.2, 0.9);
  tl.fromTo("#{p}-pill",{{rotation:-12,transformOrigin:"50% 50%"}},{{rotation:12,duration:0.8,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_drug + 0.8:.2f});
  tl.fromTo("#{g}-eye",{{x:-2}},{{x:3,duration:0.4,immediateRender:false}},{t_drug:.2f});
  rise("#{p}-t2 span", {t_propranolol:.2f}, 0.8);
  vanish("#{p}-t2", {t_recall - 0.4:.2f}, 0.3);
  tl.fromTo("#{g}-head",{{rotation:0,svgOrigin:"{neck("sitting")}"}},{{rotation:-7,svgOrigin:"{neck("sitting")}",duration:0.3,repeat:1,yoyo:true,repeatDelay:0.2,ease:"power2.out"}},{t_recall + 0.4:.2f});
  tl.fromTo("#{p}-pill",{{opacity:1}},{{opacity:0,duration:0.15,immediateRender:false}},{t_recall + 0.45:.2f});
  tl.fromTo("#{p}-shackle0",{{y:0}},{{y:-30,duration:0.35,ease:"back.out(3)"}},{t_recall:.2f});
  tl.fromTo("#{p}-lockW",{{opacity:1}},{{opacity:0,duration:0.3,immediateRender:false}},{t_recall + 0.4:.2f});
  tl.fromTo("#{p}-orbR",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.5,duration:0.35,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_trauma + 0.1:.2f});
  tl.fromTo("#{p}-orbR",{{opacity:1}},{{opacity:0,duration:1.2,immediateRender:false}},{t_dim:.2f});
  tl.fromTo("#{p}-orbC",{{opacity:0,scale:1.4,transformOrigin:"50% 50%"}},{{opacity:1,scale:0.8,transformOrigin:"50% 50%",duration:1.4,ease:"power2.inOut"}},{t_dim:.2f});
  tl.fromTo("#{p}-meter",{{opacity:0,x:120}},{{opacity:1,x:0,duration:0.7,ease:"expo.out"}},{t_dim - 0.2:.2f});
  enter("#{p}-traj", {t_drug + 0.2:.2f}, 0.5); vanish("#{p}-traj", {t_recall - 0.1:.2f}, 0.3);
  tl.fromTo("#{p}-traj",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-120}},duration:{t_recall - t_drug:.2f},ease:"none"}},{t_drug + 0.2:.2f});
  rise("#{p}-t4 span", {t_recall + 0.3:.2f}, 0.7); vanish("#{p}-t4", {t_dim - 0.3:.2f}, 0.3);
  tl.fromTo("#{p}-level",{{scaleY:1,transformOrigin:"50% 100%"}},{{scaleY:0.32,transformOrigin:"50% 100%",duration:2.0,ease:"power2.inOut"}},{t_dim:.2f});
  rise("#{p}-t3 span", {t_load:.2f}, 0.8);
""" + idle_h(p, dur, (3.0, 5.2, 9.6, 13.4, 17.8))
    return comp(p, dur, svg, html, js, extra, seed=5)


# ================================================================ 7 scoreboard: 2018 positive, 2015 did not replicate, science still debating
def locked_7():
    p = "locked_7"
    start, dur = seg(SCENE, 7)
    t_2018, t_pos, t_other, t_2015, t_not, t_replicate, t_before, t_science = 1.4, 3.91, 4.77, 5.54, 6.57, 7.52, 9.57, 10.72
    PX, PY, L = 960, 300, 500

    def pan(k, year, positive):
        mark = (f'<g id="{p}-mk{k}" opacity="0"><circle cx="240" cy="-180" r="44" fill="{MINT if positive else RED}"/>'
                 + (f'<path d="M218 -180 L234 -164 L264 -196" fill="none" stroke="#08261c" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>' if positive else
                    f'<path d="M222 -198 L258 -162 M258 -198 L222 -162" stroke="#3a0818" stroke-width="12" stroke-linecap="round"/>') + '</g>')
        caption = ("POSITIVE RESULT" if positive else "FAILED TO REPLICATE")
        return (f'<g id="{p}-pan{k}" transform="translate({PX + (-L if k == 0 else L)} {PY})">'
                f'<path d="M0 0 L-300 300 M0 0 L300 300" stroke="#c9cce8" stroke-width="5"/>'
                f'<path d="M-330 300 L330 300 Q 300 350 0 352 Q -300 350 -330 300 Z" fill="#8d7bff" stroke="#c9b8ff" stroke-width="5"/>'
                f'<g id="{p}-cd{k}" opacity="0"><g filter="url(#{p}-shadow)"><rect x="-310" y="80" width="620" height="218" rx="20" fill="#16123e" stroke="{MINT if positive else RED}" stroke-width="6"/></g>'
                f'<text id="{p}-year{k}" x="0" y="200" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="120" fill="#fffaf0">{year}</text>'
                f'<text x="0" y="268" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="44" fill="{MINT if positive else "#ff9bb0"}" id="{p}-res{k}" opacity="0">{caption}</text>'
                f'<g transform="translate(0 290)">{mark}</g></g></g>')
    svg = f"""<ellipse cx="{PX}" cy="905" rx="300" ry="24" fill="#05031a" opacity=".5"/>
<path d="M{PX - 150} 900 L{PX + 150} 900 L{PX + 90} 860 L{PX - 90} 860 Z" fill="#3a2f9a" stroke="{LILAC}" stroke-width="5"/>
<rect x="{PX - 18}" y="{PY}" width="36" height="566" fill="#2a2068" stroke="{LILAC}" stroke-width="5"/>
<g id="{p}-bar" transform="rotate(0 {PX} {PY})"><rect x="{PX - L - 20}" y="{PY - 14}" width="{2 * L + 40}" height="28" rx="14" fill="#c9b8ff" stroke="#fff" stroke-width="3"/>
 <circle cx="{PX - L}" cy="{PY}" r="14" fill="{AMBER}"/><circle cx="{PX + L}" cy="{PY}" r="14" fill="{AMBER}"/></g>
<circle cx="{PX}" cy="{PY}" r="34" fill="{AMBER}" filter="url(#{p}-glow)"/>
{pan(0, "2018", True)}{pan(1, "2015", False)}"""
    html = title(f"{p}-t1", "SCIENCE IS STILL DEBATING IT", "left:0;right:0;text-align:center;top:70px", 92, "#eef1f7")
    # scale: bar angle in degrees; the pans hang from the ends (position only, always upright)
    tilt = f"""
  function tilt(a){{var r=a*Math.PI/180,c=Math.cos(r),s=Math.sin(r);
    _el("#{p}-bar").setAttribute("transform","rotate("+a.toFixed(3)+" {PX} {PY})");
    _el("#{p}-pan0").setAttribute("transform","translate("+({PX}-{L}*c).toFixed(2)+" "+({PY}-{L}*s).toFixed(2)+")");
    _el("#{p}-pan1").setAttribute("transform","translate("+({PX}+{L}*c).toFixed(2)+" "+({PY}+{L}*s).toFixed(2)+")");}}
  function tiltK(t0,d,a0,a1,ease){{var o={{a:a0}};tl.fromTo(o,{{a:a0}},{{a:a1,duration:d,ease:ease||"power2.inOut",immediateRender:false,onUpdate:function(){{tilt(o.a);}}}},t0);}}
  tilt(0);"""
    osc = "".join(f'tiltK({t_science + 0.2 + i * 0.55:.2f},0.55,{a:.1f},{b:.1f},"sine.inOut");' for i, (a, b) in enumerate([(7, -6), (-6, 5), (5, -4), (-4, 3), (3, -2), (-2, 1)]))
    js = cam(p, (1.0, 960, 520), [
        (0, 1.2, (1.03, 940, 560), "power3.inOut"),
        (t_other - 0.2, 1.2, (1.03, 980, 560), "power3.inOut"),
        (t_before - 0.2, 1.3, (0.95, 960, 560), "power3.inOut"),
        (t_before + 1.1, dur - t_before - 1.1, (1.0, 960, 540), "sine.inOut")])
    js += tilt + f"""
  tl.fromTo("#{p}-cd0",{{opacity:0,y:-500}},{{opacity:1,y:0,duration:0.7,ease:"bounce.out"}},{t_2018 - 0.4:.2f});
  tiltK({t_2018 + 0.2:.2f},0.8,0,-8,"back.out(2)");
  pop("#{p}-mk0", {t_pos - 0.1:.2f}, 0.2, 0.7);
  enter("#{p}-res0", {t_pos - 0.6:.2f}, 0.4);
  tl.fromTo("#{p}-cd1",{{opacity:0,y:-500}},{{opacity:1,y:0,duration:0.7,ease:"bounce.out"}},{t_2015 - 0.4:.2f});
  tiltK({t_2015 + 0.2:.2f},0.8,-8,7,"back.out(2)");
  pop("#{p}-mk1", {t_replicate - 0.2:.2f}, 0.2, 0.7);
  enter("#{p}-res1", {t_not:.2f}, 0.4);
  {osc}
  rise("#{p}-t1 span", {t_science:.2f}, 0.9);
"""
    return comp(p, dur, svg, html, js, seed=13)


# ================================================================ 8 who decides: on the street before dawn; the memory leaves the padlock and becomes the sun
def locked_8():
    p = "locked_8"
    start, dur = seg(SCENE, 8)
    t_suffer, t_release, t_ask, t_who, t_which, t_too_much = 0.78, 2.46, 4.96, 5.66, 6.47, 8.11
    ops = [("THE PATIENT?", 9.14), ("THE DOCTOR?", 10.38), ("THE EMPLOYER?", 11.72), ("THE STATE?", 13.03)]
    g = p + "-g"
    PX, S = 520, .8
    bx, by = PX + S * bubble_xy()[0], 900 + S * bubble_xy()[1]
    SUN = (1730, 150)
    ys = [330, 450, 570, 690]
    ox, oy = anchors("standing")["shoulder_arm"]
    mxl, myl = anchors("standing")["hand_l"]
    arm_angle = math.degrees(math.atan2(myl - oy, mxl - ox))          # hanging arm (~85 degrees)
    OX, OY = PX + S * ox, 900 + S * oy
    angles = [round(math.degrees(math.atan2(y + 40 - OY, 1300 - OX)) - arm_angle, 1) for y in ys]   # arm rotation per option
    hand_key = (f'<g transform="translate({mxl} {myl}) rotate({arm_angle:.1f})"><g id="{p}-kW" opacity="0">'
                 f'<g transform="scale(1.06) translate(36 0)">{key_shape()}</g><rect x="-11" y="-14" width="22" height="28" rx="10" fill="{G.SKIN}"/></g></g>')
    sky = (f'<rect x="-700" y="-700" width="3400" height="1600" fill="url(#{p}-sky)"/>'
           f'<rect id="{p}-aur" x="-700" y="-700" width="3400" height="1600" fill="url(#{p}-aurg)" opacity="0"/>')
    import random
    rnd = random.Random(8)
    skyline = ""
    x = 880
    while x < 2600:
        w, h = rnd.randint(90, 170), rnd.randint(50, 110)
        skyline += f'<rect x="{x}" y="{900 - h}" width="{w}" height="{h}" fill="#221a4c"/>'
        skyline += "".join(f'<rect x="{x + 14 + k * 28}" y="{900 - h + 18}" width="12" height="14" fill="#ffd27a" opacity=".55"/>' for k in range((w - 20) // 28) if rnd.random() < .5)
        x += w + rnd.randint(6, 30)
    home = ('<path d="M-420 380 L-60 200 L320 380 Z" fill="#6a3a5a"/><rect x="-400" y="380" width="700" height="520" fill="#5a3a6a"/>'
            '<rect x="20" y="470" width="130" height="130" fill="#ffd27a" opacity=".9"/><path d="M85 470 V600 M20 535 H150" stroke="#5a3a6a" stroke-width="8"/>'
            '<rect x="170" y="690" width="96" height="210" fill="#3a2244" stroke="#c9a2c8" stroke-width="5"/><circle cx="252" cy="800" r="7" fill="#ffb23e"/>'
            '<rect x="-300" y="470" width="130" height="130" fill="#ffd27a" opacity=".6"/>')
    streetlight = ('<rect x="352" y="360" width="10" height="540" fill="#2a2244"/><path d="M357 360 Q357 330 390 330" stroke="#2a2244" stroke-width="10" fill="none"/>'
             f'<ellipse cx="398" cy="340" rx="26" ry="12" fill="#fff3c8"/><polygon points="380,346 416,346 520,900 280,900" fill="#ffd27a" opacity=".07"/>')
    street = ('<rect x="-700" y="900" width="3400" height="60" fill="#3a2e5a"/><rect x="-700" y="958" width="3400" height="10" fill="#5a4a8a"/>'
           '<rect x="-700" y="968" width="3400" height="600" fill="#14102a"/>' + "".join(f'<rect x="{x}" y="1030" width="90" height="12" rx="6" fill="#eef1f7" opacity=".4"/>' for x in range(-200, 2600, 200)))
    rays = "".join(f'<path d="M{math.cos(math.radians(a)) * 110:.0f} {math.sin(math.radians(a)) * 110:.0f} L{math.cos(math.radians(a)) * 165:.0f} {math.sin(math.radians(a)) * 165:.0f}"/>' for a in range(0, 360, 30))
    sun0 = (bx, by, S)
    tr_s, js_s = move(f"#{p}-sunW", sun0, [(t_release + 0.1, 1.4, (SUN[0], SUN[1], 2.4), "power2.inOut")])
    inner = f'<g id="{p}-orbW">{orb(p, 0, RED, 38)}</g><g transform="translate(0 4) scale(.5)"><g id="{p}-lockW">{padlock(p, 0)}</g></g>'
    svg = f"""{sky}
<g transform="translate({SUN[0]} {SUN[1]})"><g id="{p}-rays" opacity="0" stroke="{AMBER}" stroke-width="10" stroke-linecap="round" filter="url(#{p}-glow)">{rays}</g></g>
<g id="{p}-sunW" transform="{tr_s}"><g id="{p}-sun" opacity="0">{orb(p, 1, AMBER, 34)}</g></g>
{skyline}{home}{streetlight}{street}
<g transform="translate({PX} 900) scale({S})">{human(p, "home", "standing", hand=hand_key)}{bubble_h(p, 0, inner)}</g>"""
    extra = (f'<linearGradient id="{p}-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0e0a30"/><stop offset=".55" stop-color="#2a1d6a"/><stop offset="1" stop-color="#4a2a7a"/></linearGradient>'
             f'<linearGradient id="{p}-aurg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a2a8a" stop-opacity="0"/><stop offset=".45" stop-color="#ff7ab8" stop-opacity=".35"/><stop offset=".62" stop-color="#ffb23e" stop-opacity=".8"/></linearGradient>')
    html = (title(f"{p}-t0", "LIBERATION", "right:70px;top:440px;text-align:right", 110, "#ffd98a") +
            title(f"{p}-t1", "WHO DECIDES", "left:0;right:0;text-align:center;top:40px", 120, "#eef1f7") +
            title(f"{p}-t2", "WHICH MEMORY HURTS TOO MUCH?", "left:0;right:0;text-align:center;top:190px", 60, "#ff9bb0", True) +
            "".join(title(f"{p}-o{i}", name, f"left:1280px;top:{y}px", 64, "#3a1d6a", True) for i, ((name, _), y) in enumerate(zip(ops, ys))))
    js = cam(p, (1.35, bx - 60, by + 160), [
        (0.2, t_release - 0.2, (1.42, bx - 60, by + 150), "sine.inOut"),
        (t_release + 0.1, 1.6, (1.0, 960, 540), "power3.inOut"),
        (ops[3][1], dur - ops[3][1], (1.04, 980, 540), "sine.inOut")])
    swing = ""
    a0 = angles[0]
    sh = shoulder("standing")
    for i, (name, tt) in enumerate(ops):
        swing += ((f'tl.fromTo("#{g}-arm",{{rotation:{a0},svgOrigin:"{sh}"}},{{rotation:{angles[i]},svgOrigin:"{sh}",duration:0.45,ease:"back.out(2)",immediateRender:false}},{tt - 0.15:.2f});' if i else "")
                 + f'rise("#{p}-o{i} span", {tt - 0.1:.2f}, 0.6);'
                 f'tl.fromTo("#{p}-o{i}",{{color:"#3a1d6a"}},{{color:"#fffaf0",duration:0.2}},{tt:.2f});'
                 + (f'tl.fromTo("#{p}-o{i - 1}",{{color:"#fffaf0"}},{{color:"#5a3a8a",duration:0.2,immediateRender:false}},{tt:.2f});' if i else ""))
        a0 = angles[i]
    js += js_s + f"""
  pop("#{p}-bub0", 0.2, 0.4, 0.7);
  tl.fromTo("#{p}-orbW",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.3,duration:0.3,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_suffer - 0.4:.2f});
  tl.fromTo("#{g}-eye",{{x:0}},{{x:-2,duration:0.3}},{t_suffer:.2f});
  tl.fromTo("#{p}-shackle0",{{y:0}},{{y:-34,duration:0.35,ease:"back.out(3)"}},{t_release - 0.3:.2f});
  tl.fromTo("#{p}-lockW",{{opacity:1,y:0,rotation:0,transformOrigin:"50% 50%"}},{{opacity:0,y:260,rotation:40,transformOrigin:"50% 50%",duration:0.9,ease:"power2.in",immediateRender:false}},{t_release + 0.1:.2f});
  tl.fromTo("#{p}-orbW",{{opacity:1}},{{opacity:0,duration:0.2,immediateRender:false}},{t_release + 0.1:.2f});
  enter("#{p}-sun", {t_release + 0.05:.2f}, 0.2);
  tl.fromTo("#{p}-bub0",{{opacity:1}},{{opacity:0,duration:0.4,immediateRender:false}},{t_release + 0.8:.2f});
  tl.fromTo("#{p}-aur",{{opacity:0}},{{opacity:1,duration:1.6,ease:"power2.out"}},{t_release + 0.3:.2f});
  tl.fromTo("#{p}-rays",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:0.9,scale:1,transformOrigin:"50% 50%",duration:0.8,ease:"expo.out"}},{t_release + 1.3:.2f});
  tl.fromTo("#{p}-rays",{{rotation:0,transformOrigin:"50% 50%"}},{{rotation:40,duration:{dur - t_release - 1.3:.2f},ease:"none",immediateRender:false}},{t_release + 1.3:.2f});
  tl.fromTo("#{g}-arm",{{rotation:0,svgOrigin:"{shoulder("standing")}"}},{{rotation:-130,svgOrigin:"{shoulder("standing")}",duration:0.5,ease:"back.out(1.6)"}},{t_release:.2f});
  tl.fromTo("#{g}-arm",{{rotation:-130,svgOrigin:"{shoulder("standing")}"}},{{rotation:{angles[0]},svgOrigin:"{shoulder("standing")}",duration:0.6,ease:"power2.inOut",immediateRender:false}},{t_ask - 0.6:.2f});
  rise("#{p}-t0 span", {t_release:.2f}, 0.8);
  vanish("#{p}-t0", {t_ask - 0.7:.2f}, 0.3);
  pop("#{p}-kW", {t_ask - 0.2:.2f}, 0.3, 0.9);
  rise("#{p}-t1 span", {t_who:.2f}, 0.8);
  rise("#{p}-t2 span", {t_which:.2f}, 0.8);
  tl.fromTo("#{g}-eye",{{x:-2}},{{x:3,duration:0.4,immediateRender:false}},{t_ask:.2f});
  {swing}
  tl.fromTo("#{g}-arm",{{rotation:{angles[3]},svgOrigin:"{shoulder("standing")}"}},{{rotation:{angles[3] - 5},svgOrigin:"{shoulder("standing")}",duration:0.8,repeat:1,yoyo:true,ease:"sine.inOut",immediateRender:false}},{ops[3][1] + 0.6:.2f});
""" + idle_h(p, dur, (1.8, 4.2, 7.0, 10.9, 13.9))
    return comp(p, dur, svg, html, js, extra, seed=8)


SCENES = [(f"{SCENE}_{i}", fn, seg(SCENE, i)[1]) for i, fn in enumerate([locked_0, locked_1, locked_2, locked_3, locked_4, locked_5, locked_6, locked_7, locked_8])]
SEG_MAP = {(SCENE, int(k.split("_")[1])): k for k, _, _ in SCENES}

if __name__ == "__main__":
    print(write_scenes(SCENES, HERE))
