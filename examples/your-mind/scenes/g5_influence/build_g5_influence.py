"""Group g5: the whole "influence" scene (segments 0 to 8), in the v5 pattern.

  python3 build_g5_influence.py     # writes compositions/ and index.html in this folder

Theme: influence without touching the brain, only by controlling the screen and the feed (Facebook experiment, 2012).
"""
import math, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from engine import *  # noqa: E402,F401
from figure import figure, figure_idle as _figure_idle_base, picture, orb, ANCHORS, SKIN, HAIR, HOME, WORK, TIE  # noqa: E402
HERE = os.path.dirname(os.path.abspath(__file__))  # engine brings the HERE of scenes; here it is the group folder

SCENE_KEY = "influence"

# The engine's camZ writes a set at t=0 on every call and the tween's first render is lazy: on a direct seek (snapshot,
# chunked render) the last set wins and the camera shows up at the wrong zoom. This version keeps one state per selector.
CAM_JS = r"""
  var __cam={};
  function camZ(sel,t0,dur,z0,z1,ox,oy,ease){
    if(!__cam[sel]){__cam[sel]={l:Math.log(z0)};tl.set(sel,{scale:z0,svgOrigin:ox+" "+oy},0);}
    var o=__cam[sel];
    tl.to(o,{l:Math.log(z1),duration:dur,ease:ease||"power3.inOut",lazy:false,immediateRender:false,onUpdate:function(){gsap.set(sel,{scale:Math.exp(o.l),svgOrigin:ox+" "+oy});}},t0);
  }
"""
_composition_base = composition


def composition(i, dur, svg, html, js, extra="", **kw):
    return _composition_base(i, dur, svg, html, CAM_JS + js, extra, **kw)


def ID(i):
    return f"{SCENE_KEY}_{i}"


def D(i):
    return seg(SCENE_KEY, i)[1]


def ft(sel, a, b, t):
    return f'tl.fromTo("{sel}",{a},{b},{t:.2f});\n'


# ---------------------------------------------------------------- feed pieces (same look as the phone in scene C)
CARD_COLORS = {"happy": ("#7b2a6c", "#6b5b2a"), "sad": ("#25427a", "#2b2a80"), "neutral": ("#2a6a6a", "#3a2a8c")}


def card(kind, k=0):
    """Post card 300x170 (x -150..150, y 0..170): avatar, name, illustration. happy = smiling sun, sad = rain cloud."""
    color = CARD_COLORS[kind][k % 2]
    s = (f'<rect x="-150" y="0" width="300" height="170" rx="20" fill="{color}"/>'
         '<circle cx="-110" cy="34" r="20" fill="#eef1ff" opacity=".85"/><rect x="-80" y="22" width="150" height="12" rx="6" fill="#eef1ff" opacity=".7"/>'
         '<rect x="-80" y="42" width="96" height="10" rx="5" fill="#eef1ff" opacity=".4"/><rect x="-132" y="66" width="264" height="90" rx="12" fill="#000" opacity=".22"/>')
    if kind == "happy":
        rays = "".join(f'<line x1="0" y1="-40" x2="0" y2="-50" transform="rotate({a})"/>' for a in range(0, 360, 45))
        s += (f'<g transform="translate(0 111)"><g stroke="#ffd23e" stroke-width="5" stroke-linecap="round">{rays}</g>'
              '<circle r="31" fill="#ffd23e"/><circle cx="-10" cy="-7" r="4" fill="#5a3a00"/><circle cx="10" cy="-7" r="4" fill="#5a3a00"/>'
              '<path d="M-14 6 Q0 20 14 6" fill="none" stroke="#5a3a00" stroke-width="4.5" stroke-linecap="round"/></g>'
              '<path d="M110 -176 c-8 -10 -22 -2 -14 8 l14 12 l14 -12 c8 -10 -6 -18 -14 -8 Z" fill="#ff4f7d" transform="translate(0 312)"/>')
    elif kind == "sad":
        s += ('<g transform="translate(0 104)"><g stroke="#7fb4ff" stroke-width="4" stroke-linecap="round"><line x1="-18" y1="22" x2="-24" y2="40"/><line x1="0" y1="24" x2="-6" y2="44"/><line x1="18" y1="22" x2="12" y2="40"/></g>'
              '<circle cx="-22" cy="0" r="20" fill="#a9b8d8"/><circle cx="4" cy="-10" r="25" fill="#a9b8d8"/><circle cx="28" cy="2" r="18" fill="#a9b8d8"/><rect x="-40" y="0" width="84" height="20" rx="10" fill="#a9b8d8"/>'
              '<circle cx="-6" cy="0" r="3.5" fill="#2a3050"/><circle cx="14" cy="0" r="3.5" fill="#2a3050"/><path d="M-8 14 Q4 6 16 14" fill="none" stroke="#2a3050" stroke-width="3.5" stroke-linecap="round"/></g>')
    else:
        s += ('<circle cx="-84" cy="96" r="14" fill="#ffd23e"/><path d="M-60 146 L-20 106 L20 138 L50 116 L112 146 Z" fill="#fff" opacity=".35"/>')
    return s


def phone_mock(p, name, kinds, tint="#2a3a8c", extra=""):
    """Phone from scene C (400x800, centered at 0,0) with cards. Ids: {p}-{name}posts, {p}-{name}c{k}, {p}-{name}tint."""
    cards = "".join(f'<g transform="translate(0 {-344 + k * 190})"><g id="{p}-{name}c{k}">{card(t, k)}</g></g>' for k, t in enumerate(kinds))
    return (f'<g filter="url(#{p}-shadow)"><rect x="-200" y="-400" width="400" height="800" rx="54" fill="#15133a" stroke="{LILAC}" stroke-width="8"/>'
            f'<rect x="-172" y="-364" width="344" height="728" rx="26" fill="#0e0c26"/></g>'
            f'<clipPath id="{p}-{name}cp"><rect x="-172" y="-364" width="344" height="728" rx="26"/></clipPath>'
            f'<g clip-path="url(#{p}-{name}cp)"><g id="{p}-{name}posts">{cards}{extra}</g>'
            f'<rect id="{p}-{name}tint" x="-172" y="-364" width="344" height="728" fill="{tint}" opacity="0"/></g>'
            f'<rect x="-50" y="-386" width="100" height="10" rx="5" fill="#2a2870"/>')


SWAP = '<g transform="translate(0 -344)"><g id="{p}-swap">' + card("sad").replace("{", "{{").replace("}", "}}") + '</g></g>'


def figure_crowd(p, cols=26, rows=7, cls="member"):
    """Grid of small people (mixed clothes), feet at y = 540 + r*80."""
    rng = random.Random(21)
    return "".join(f'<use class="{cls}" href="#{p}-tiny{(c * 5 + r * 3 + rng.randint(0, 7)) % 8}" x="{960 + (c - (cols - 1) / 2) * 68 + rng.randint(-8, 8):.0f}" y="{540 + r * 80 + rng.randint(-5, 5)}"/>'
                   for r in range(rows) for c in range(cols))


def page(p, img, name, highlights):
    """Real page (1600x2142) in image coordinates, with sheet, shadow and highlight rectangles (animated width)."""
    rs = "".join(f'<rect id="{p}-{name}h{k}" x="{x}" y="{y}" width="0" height="{h}" fill="#ffd23e" opacity=".55" style="mix-blend-mode:multiply"/>'
                 for k, (x, y, w, h) in enumerate(highlights))
    return (f'<rect x="-14" y="-14" width="1628" height="2170" rx="10" fill="#fffdf6" filter="url(#{p}-shadow)"/>'
            f'<image href="assets/docs/{img}.png" x="0" y="0" width="1600" height="2142"/>{rs}')


def highlight(p, name, highlights, t0, step=0.45, off=0):
    return "".join(f'tl.fromTo("#{p}-{name}h{k + off}",{{attr:{{width:0}}}},{{attr:{{width:{w}}},duration:{step:.2f},ease:"power1.inOut"}},{t0 + k * step:.2f});\n'
                   for k, (x, y, w, h) in enumerate(highlights))


# ---------------------------------------------------------------- the real person (figure.py) with expression and phone
# Other people (not "you") = same figure.py art with another palette. Keys = figure.py base hex.
OTHER_A = {HOME["torso"]: "#2bb3a0", HOME["pants"]: "#3a3a4a", HOME["shoe"]: "#ffd23e", HAIR: "#1a1010", SKIN: "#c68a5e"}
OTHER_B = {HOME["torso"]: "#ff7a5a", HOME["pants"]: "#4a3a7a", HAIR: "#d9a441", SKIN: "#f6d2b8"}
OPERATOR = {WORK["torso"]: "#4a4f6e", HAIR: "#cfcdd8", SKIN: "#c99372", TIE: "#ffb23e"}   # the man at the desk
_MOUTH_LAUGH = ('<path d="M -11,34 Q 0,44 11,33 Q 0,40 -11,34 Z" fill="#6e2836"/>'
             '<path d="M -11.5,34.2 Q 0,43 11,33.2" fill="none" stroke="#6e2836" stroke-width="2.4" stroke-linecap="round"/>')
_LIP = '<path d="M -4.5,45 Q 0,46.6 4.5,45" fill="none" stroke="#140a2e" stroke-opacity=".27" stroke-width="1.6" stroke-linecap="round"/>'
_MOUTH_N = '<path d="M -9.5,37.6 Q 0,39.4 9.5,37.2" fill="none" stroke="#6e2836" stroke-width="2.4" stroke-linecap="round"/>' + _LIP
_MOUTH_T = ('<path d="M -10,42 Q 0,33.6 10,41.4" fill="none" stroke="#6e2836" stroke-width="2.4" stroke-linecap="round"/>'
           '<path d="M -4,46 Q 0,47 4,46" fill="none" stroke="#140a2e" stroke-opacity=".22" stroke-width="1.4" stroke-linecap="round"/>')
_BIG = "M-9999 -9999h19998v19998h-19998Z "


def _group_end(s, i):
    """Index right after the </g> that closes the <g ...> starting at s[i]."""
    depth = 0
    for m in re.finditer(r"<g\b|</g>", s[i:]):
        depth += 1 if m.group(0) != "</g>" else -1
        if depth == 0:
            return i + m.end()
    raise ValueError("unclosed group")


def _limb(A, B, C, wa, wb, wc):
    """Port of limb() from the approved sketch: limb with a soft elbow, rounded end at A."""
    def nrm(p, q):
        dx, dy = q[0] - p[0], q[1] - p[1]
        l = math.hypot(dx, dy)
        return (-dy / l, dx / l)
    n1, n2 = nrm(A, B), nrm(B, C)
    nb = (n1[0] + n2[0], n1[1] + n2[1])
    L = math.hypot(*nb)
    nb = (nb[0] / L, nb[1] / L)

    def side(s):
        return [(A[0] + n1[0] * wa * s, A[1] + n1[1] * wa * s), (B[0] + nb[0] * wb * s, B[1] + nb[1] * wb * s), (C[0] + n2[0] * wc * s, C[1] + n2[1] * wc * s)]

    def seg(a, b, c):
        t = ((c[0] - a[0]) / 6, (c[1] - a[1]) / 6)
        return (f"C{a[0] + (b[0] - a[0]) / 3:.1f} {a[1] + (b[1] - a[1]) / 3:.1f} {b[0] - t[0]:.1f} {b[1] - t[1]:.1f} {b[0]:.1f} {b[1]:.1f}"
                f"C{b[0] + t[0]:.1f} {b[1] + t[1]:.1f} {c[0] - (c[0] - b[0]) / 3:.1f} {c[1] - (c[1] - b[1]) / 3:.1f} {c[0]:.1f} {c[1]:.1f}")
    o, i = side(1), side(-1)[::-1]
    d = (B[0] - A[0], B[1] - A[1])
    dl = math.hypot(*d)
    return (f"M{o[0][0]:.1f} {o[0][1]:.1f}" + seg(*o) + f"L{i[0][0]:.1f} {i[0][1]:.1f}" + seg(*i)
            + f"Q{A[0] - d[0] / dl * wa * 1.5:.1f} {A[1] - d[1] / dl * wa * 1.5:.1f} {o[0][0]:.1f} {o[0][1]:.1f}Z")


def _piece(cid, d, color, li=3.3, sh=8, rim=None):
    """piece() from the sketch: base hex plus clipped light and shadow as neutral layers (swapping the hex recolors it)."""
    s = f'<clipPath id="{cid}"><path d="{d}"/></clipPath><path d="{d}" fill="{color}"/><g clip-path="url(#{cid})">'
    if li:
        s += f'<path d="{_BIG}{d}" transform="translate({li} {li})" fill="#ffffff" fill-opacity=".26" fill-rule="evenodd"/>'
    if sh:
        s += f'<path d="{_BIG}{d}" transform="translate({-sh} {-sh * .35:.1f})" fill="#140a2e" fill-opacity=".33" fill-rule="evenodd"/>'
    if rim:
        s += f'<path d="{_BIG}{d}" transform="translate(-2 0)" fill="{rim}" fill-rule="evenodd"/>'
    return s + "</g>"


def _phone(p, cx, cy, ang, L=38, W=14, front=False):
    """Tilted phone (long vertical axis rotated `ang` degrees). The screen ({p}-screen) is on the local -x side, which points
    at the face; a soft glow comes off it."""
    if front:   # screen facing the viewer: reads as a phone right away
        return (f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({ang})">'
                f'<ellipse cx="0" cy="-6" rx="{W * 1.6:.0f}" ry="{L * .8:.0f}" fill="url(#{p}-glowGrad)"/>'
                f'<rect x="{-W / 2}" y="{-L / 2}" width="{W}" height="{L}" rx="5" fill="#1b1846" stroke="#8d7bff" stroke-width="1.8"/>'
                f'<rect id="{p}-screen" x="{-W / 2 + 2.2}" y="{-L / 2 + 4}" width="{W - 4.4}" height="{L - 8}" rx="2.5" fill="#3be0ff"/>'
                + "".join(f'<rect x="{-W / 2 + 4}" y="{-L / 2 + 7 + k * 9}" width="{W - 8}" height="6" rx="1.5" fill="#0e0c26" opacity=".35"/>' for k in range(int((L - 12) // 9)))
                + "</g>")
    return (f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({ang})">'
            f'<ellipse cx="-14" cy="0" rx="26" ry="{L * .75:.0f}" fill="url(#{p}-glowGrad)"/>'
            f'<rect x="{-W / 2}" y="{-L / 2}" width="{W}" height="{L}" rx="4" fill="#1b1846" stroke="#8d7bff" stroke-width="1.6"/>'
            f'<rect x="{W / 2 - 4.5}" y="{-L / 2 + 5}" width="2" height="7" rx="1" fill="#8d7bff" opacity=".7"/>'
            f'<rect id="{p}-screen" x="{-W / 2 - 1.2}" y="{-L / 2 + 2}" width="4.2" height="{L - 4}" rx="2" fill="#3be0ff"/></g>')


def _phone_arm(p, color, skin, shoulder):
    """Bent arm on the right side of the frame, phone at chest height (standing person, turn 30). Starting point: shoulder."""
    S = shoulder
    E = (S[0] + 4, S[1] + 84)
    W = (E[0] + 54, E[1] - 36)
    u = ((W[0] - E[0]), (W[1] - E[1]))
    ul = math.hypot(*u)
    u = (u[0] / ul, u[1] / ul)
    W2 = (W[0] - u[0] * 9, W[1] - u[1] * 9)
    sleeve = _limb(S, E, W2, 19.5, 17.5, 15.0)
    wrist = _limb(W2, ((W2[0] + W[0]) / 2, (W2[1] + W[1]) / 2), W, 15.0, 14.2, 13.4)
    H = (W[0] + u[0] * 9, W[1] + u[1] * 9)              # center of the hand
    # hand drawn in the phone's frame (long axis = local y, screen on the -x side, pointing at the face):
    # palm behind, four fingers across the back of the phone, thumb folding over the screen edge
    C = (H[0] + 4, H[1] - 14)
    crease = "#140a2e"
    palm = (f'<path d="M 2,4 C 14,0 22,10 19,22 C 16,30 4,31 -2,25 C -5,18 -4,8 2,4 Z" fill="{skin}"/>'
             f'<path d="M 2,4 C 14,0 22,10 19,22 C 16,30 4,31 -2,25 C -5,18 -4,8 2,4 Z" fill="{crease}" fill-opacity=".16"/>')
    fingers = "".join(f'<path d="M {14 - k:.0f},{y} L {-1 - k * .6:.1f},{y + 1.2:.1f}" stroke="{skin}" stroke-width="5.4" stroke-linecap="round"/>'
                    f'<path d="M {13 - k:.0f},{y + 2.6:.1f} L {1 - k * .6:.1f},{y + 3.4:.1f}" stroke="{crease}" stroke-opacity=".22" stroke-width="1.1" stroke-linecap="round"/>'
                    for k, y in enumerate((-6, 0, 6, 12)))
    thumb = (f'<path d="M 6,24 Q -4,22 -9.5,13" fill="none" stroke="{skin}" stroke-width="6" stroke-linecap="round"/>'
               f'<path d="M 4,26 Q -5,23 -10,15" fill="none" stroke="{crease}" stroke-opacity=".2" stroke-width="1.2" stroke-linecap="round"/>')
    handset = (f'<g transform="translate({C[0]:.1f} {C[1]:.1f}) rotate(53)">'
            f'<ellipse cx="-16" cy="-2" rx="28" ry="32" fill="url(#{p}-glowGrad)"/>{palm}'
            f'<rect x="-7.5" y="-21" width="15" height="42" rx="4" fill="#1b1846" stroke="#8d7bff" stroke-width="1.6"/>'
            f'<rect id="{p}-screen" x="-8.7" y="-19" width="4.2" height="38" rx="2" fill="#3be0ff"/>{fingers}{thumb}</g>')
    hand = fingers = ""
    return (f'<g id="{p}-arm">' + _piece(f"{p}-sleeve", sleeve, color, rim="#ff4fa3")
            + f'<g clip-path="url(#{p}-sleeve)"><path d="M {E[0] - 14:.0f},{E[1] - 4:.0f} Q {E[0]:.0f},{E[1] + 4:.0f} {E[0] + 12:.0f},{E[1] - 8:.0f}" fill="none" stroke="#140a2e" stroke-opacity=".3" stroke-width="3" stroke-linecap="round"/></g>'
            + _piece(f"{p}-cuff", wrist, color, li=0, sh=3) + f'<path d="{wrist}" fill="#140a2e" fill-opacity=".3"/>'
            + hand + handset + fingers + "</g>")


def _gaze_down(s, p, dx=0.0, dy=3.4, lid=4.0):
    """Eyes on the phone in the hand: the pupil drops and the upper eyelid droops (static, built into the SVG).
    dx/dy shift the pupil in the eye's frame (dx > 0 = the way the person is facing); lid lowers the eyelid."""
    i = s.index(f'<g id="{p}-eye"')
    j = _group_end(s, i)
    o = s[i:j]
    o = re.sub(r'(<path d="M-?[\d.]+ -?[\d.]+A[^"]*" transform="matrix\(([^)]*)\))',
               lambda m: f"{m.group(1)} translate({dx if float(m.group(2).split()[0]) > 0 else -dx} {dy})", o)
    for pat in (r"(Q 0,)(-?[\d.]+)( -9,0\.5)", r"(Q -1,)(-?[\d.]+)( 10,-0\.5)", r"(Q 0,)(-?[\d.]+)( 9,0\.5)"):
        o = re.sub(pat, lambda m: f"{m.group(1)}{float(m.group(2)) + lid:.2f}{m.group(3)}", o)
    return s[:i] + o + s[j:]


def human(p, variant="home", pose="sitting", phone=False, colors=None, chair=False, mood="happy", shadow=True, glasses=False, glow=None, gaze=None):
    """figure() with a swappable mouth ({p}-mouthF/N/T), animatable eyebrows ({p}-browR, {p}-browL) and, if phone, a phone in hand
    ({p}-screen = the phone's screen; sitting: in place of the mug; standing: arm bent at chest height), with gaze and head
    lowered to the phone. glow (default = phone): screen glow on the face ({p}-faceGlow). Same local box as figure()."""
    k = ("home" if variant == "home" else "work", "standing" if pose == "standing" else "sitting", 30)
    anchor = ANCHORS[k]
    glow = phone if glow is None else glow
    s = figure(p, variant, pose, glow=None, chair=chair, shadow=shadow)
    skin = (colors or {}).get(SKIN, SKIN)
    # mouth: the paths after the nose that share the nose's matrix
    nose_tf = re.search(r'<path d="M 2,5 C 6,12[^>]*transform="([^"]*)"', s).group(1)
    start = s.index(f'<g id="{p}-head">')
    end = _group_end(s, start)
    head = s[start:end]
    pos = head.index('<path d="M-4 22A3')
    pos = head.index("/>", head.index("/>", pos) + 2) + 2               # after the 2 nose highlight paths
    mouth_re = re.compile(r'<path d="([^"]*)" transform="' + re.escape(nose_tf) + r'"([^>]*)/>')
    rest, orig = head[pos:], ""
    while True:
        m = mouth_re.match(rest)
        if not m:
            break
        orig += f'<path d="{m.group(1)}"{m.group(2)}/>'
        rest = rest[m.end():]
    home = k[0] == "home"
    bF = orig if home else _MOUTH_LAUGH + _LIP
    bN = _MOUTH_N if home else orig
    op = {"happy": (1, 0, 0), "neutral": (0, 1, 0), "sad": (0, 0, 1)}[mood]
    mouth = (f'<g transform="{nose_tf}"><g id="{p}-mouthF" opacity="{op[0]}">{bF}</g><g id="{p}-mouthN" opacity="{op[1]}">{bN}</g>'
            f'<g id="{p}-mouthT" opacity="{op[2]}">{_MOUTH_T}</g></g>')
    head = head[:pos] + mouth + rest
    # eyebrows: a pair (color + shadow) with the same matrix becomes an animatable group with no transform attribute
    sides = iter(("R", "L"))

    def _brow(m):
        return f'<g transform="{m.group(2)}"><g id="{p}-brow{next(sides)}"><path d="{m.group(1)}"{m.group(3)}/><path d="{m.group(1)}"{m.group(4)}/></g></g>'
    head = re.sub(r'<path d="(M [56],-2[03][^"]*)" transform="([^"]*)"([^>]*)/><path d="\1" transform="\2"([^>]*)/>', _brow, head, count=2)
    cx, cy = anchor["head_center"]
    extra_head = ""
    if glasses:
        eyes = list(dict.fromkeys(re.findall(r'<path d="M -9.5,0.8 Q -1,-11.5[^>]*transform="matrix\(([^)]*)\)"', head)))
        lenses = []
        for mt in eyes:
            a, b_, c_, d_, e, f = map(float, mt.split())
            lenses.append((e, f + 1, abs(a) * 13.5, d_ * 11.5))
        lenses.sort()
        (x1, y1, rx1, ry1), (x2, y2, rx2, ry2) = lenses
        extra_head = (f'<g fill="#bff4ff" fill-opacity=".16" stroke="#241c34" stroke-width="2.2">'
                     f'<ellipse cx="{x1:.1f}" cy="{y1:.1f}" rx="{rx1:.1f}" ry="{ry1:.1f}"/><ellipse cx="{x2:.1f}" cy="{y2:.1f}" rx="{rx2:.1f}" ry="{ry2:.1f}"/></g>'
                     f'<path d="M {x1 + rx1:.1f},{y1 - 1:.1f} Q {(x1 + rx1 + x2 - rx2) / 2:.1f},{y1 - 4:.1f} {x2 - rx2:.1f},{y2 - 1:.1f} M {x1 - rx1:.1f},{y1 - 2:.1f} L {x1 - rx1 - 14:.1f},{y1 - 5:.1f}" '
                     f'fill="none" stroke="#241c34" stroke-width="2.2" stroke-linecap="round"/>'
                     f'<path d="M {x2 - rx2 * .5:.1f},{y2 - ry2 * .5:.1f} l 5,-2" stroke="#ffffff" stroke-opacity=".7" stroke-width="1.6" stroke-linecap="round"/>')
    if phone:   # head tilts toward the phone: static group inside {p}-head (GSAP only animates {p}-headW outside it)
        head = head.replace(f'<g id="{p}-head">', f'<g id="{p}-head"><g transform="rotate(7 {cx} {cy + 46})">', 1)[:-4] + extra_head + "</g></g>"
    elif extra_head:
        head = head[:-4] + extra_head + "</g>"
    s = s[:start] + head + s[end:]
    if phone:
        s = _gaze_down(s, p)
    elif gaze:
        s = _gaze_down(s, p, *gaze)
    if phone:
        if k[1] == "sitting":   # swap the mug for the phone, under the fingers that were already holding it
            i = s.index(f'id="{p}-arm"')
            j = _group_end(s, s.rindex("<g", 0, i))
            arm_svg = s[i:j]
            mug = re.compile(r'<g clip-path="url\(#[^"]+\)">(?:<path [^>]*#ffb347[^>]*/>)+</g>|<path [^>]*(?:#ffb347|#7a3d1c|#4a2412|#a98bff)[^>]*/>')
            m0 = mug.search(arm_svg)
            arm_svg = arm_svg[:m0.start()] + "@PHONE@" + mug.sub("", arm_svg[m0.start():])
            arm_svg = re.sub(r'<g opacity="[^"]*"></g>', "", arm_svg)
            mx, my = anchor["hand_l"]
            arm_svg = arm_svg.replace("@PHONE@", _phone(p, mx - 24, my - 22, -16, 46, 26, front=True))
            s = s[:i] + arm_svg + s[j:]
        else:
            i = s.rindex("<g", 0, s.index(f'id="{p}-arm"'))
            j = _group_end(s, i)
            s = s[:i] + _phone_arm(p, HOME["torso"] if home else WORK["torso"], SKIN, anchor["shoulder_arm"]) + s[j:]
    defs = (f'<filter id="{p}-glowBlur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="9"/></filter>'
            f'<radialGradient id="{p}-glowGrad"><stop offset="0" stop-color="#3be0ff" stop-opacity=".45"/><stop offset="1" stop-color="#3be0ff" stop-opacity="0"/></radialGradient>')
    s = s.replace("</defs>", defs + "</defs>", 1)
    if glow:   # outside the body (the rim filter does not catch the glow); static, follows the tilted face
        dx = 16 if phone else 14
        s = s[:-4] + (f'<ellipse id="{p}-faceGlow" cx="{cx + dx:.0f}" cy="{cy + (20 if phone else 6):.0f}" rx="40" ry="46" fill="#3be0ff" opacity=".22" '
                      f'filter="url(#{p}-glowBlur)" style="mix-blend-mode:screen"/>') + "</g>"
    for a, b in (colors or {}).items():
        s = s.replace(a, b)
    return s


def figure_idle(p, dur, blinks=(2.0, 5.3, 8.8, 12.1, 16.4, 20.2)):
    """figure.figure_idle without the breathing on {p}-trunk: the trunk's box includes the 19998 px clips (M-9999...), so
    transformOrigin "50% 100%" lands at y ~ +9999 and the scaleY throws the trunk ~120 px up (hood over the head)."""
    return re.sub(r'tl\.fromTo\("#[^"]*-trunk".*?\);', "", _figure_idle_base(p, dur, blinks), count=1)


def mood_js(p, old_mood, new_mood, t, dur=0.3):
    """Switches the mouth from `old_mood` to `new_mood` at time t (happy/neutral/sad); sad also raises the inner ends of the eyebrows."""
    k = {"happy": "F", "neutral": "N", "sad": "T"}
    brows = f"#{p}-browR, #{p}-browL"
    js = ft(f"#{p}-mouth{k[old_mood]}", "{opacity:1}", "{opacity:0,duration:%.2f,immediateRender:false}" % dur, t)
    js += ft(f"#{p}-mouth{k[new_mood]}", "{opacity:0}", "{opacity:1,duration:%.2f,immediateRender:false}" % dur, t)
    if new_mood == "sad":
        js += ft(brows, "{rotation:0,y:0,transformOrigin:'0% 50%'}", "{rotation:14,y:-2.5,transformOrigin:'0% 50%',duration:0.4,immediateRender:false}", t)
    if old_mood == "sad":
        js += ft(brows, "{rotation:14,y:-2.5,transformOrigin:'0% 50%'}", "{rotation:0,y:0,transformOrigin:'0% 50%',duration:0.4,immediateRender:false}", t)
    return js


def phone_gaze(p):
    """The gaze at the phone is already drawn in the SVG (human(phone=True)); kept so the scenes stay untouched."""
    return ""


def screen_js(p, colors, t0, step=0.5):
    """The phone's small screen changes color on every post (feed scrolling)."""
    return "".join(f'tl.to("#{p}-screen",{{attr:{{fill:"{c}"}},duration:0.15}},{t0 + k * step:.2f});\n' for k, c in enumerate(colors))


def floor(y, op=.55):
    return (f'<rect x="-400" y="{y}" width="2720" height="700" fill="#0b0824" opacity="{op}"/>'
            f'<rect x="-400" y="{y}" width="2720" height="4" fill="#4a3aa0" opacity=".6"/>')


def sofa(color="#b0466e", dark="#7a2a50"):
    """Sofa in profile (seated person with feet at y=0, facing right). Draw it before the person."""
    return (f'<rect x="-196" y="-250" width="360" height="110" rx="26" fill="{dark}"/>'
            f'<rect x="-196" y="-400" width="96" height="290" rx="40" fill="{color}"/>'
            f'<rect x="-170" y="-330" width="80" height="120" rx="30" fill="#ffd23e" opacity=".85" transform="rotate(-10 -130 -270)"/>'
            f'<rect x="-196" y="-168" width="370" height="92" rx="24" fill="{color}"/><rect x="-186" y="-176" width="350" height="34" rx="16" fill="#d0628e"/>'
            f'<rect x="-176" y="-80" width="20" height="80" rx="6" fill="#3a1a30"/><rect x="140" y="-80" width="20" height="80" rx="6" fill="#3a1a30"/>')


def lamp(p, x, y, height=420, color="#ffd27a"):
    return (f'<g transform="translate({x} {y})"><ellipse cx="0" cy="-{height - 30}" rx="150" ry="150" fill="{color}" opacity=".16" filter="url(#{p}-blur40)"/>'
            f'<path d="M -6 0 L -6 -{height - 60} L 6 -{height - 60} L 6 0 Z" fill="#2a1d70"/><ellipse cx="0" cy="0" rx="50" ry="10" fill="#2a1d70"/>'
            f'<path d="M -54 -{height - 60} L -34 -{height} L 34 -{height} L 54 -{height - 60} Z" fill="{color}"/></g>')


def tiny_person(shirt, pants, skin, hair, phone=False):
    """Small front-facing figure (feet at y=0, height ~88). For crowds via <use>."""
    s = (f'<rect x="-10" y="-36" width="8" height="36" rx="3" fill="{pants}"/><rect x="2" y="-36" width="8" height="36" rx="3" fill="{pants}"/>'
         f'<path d="M -14 -34 L -14 -58 Q -14 -66 -6 -66 L 6 -66 Q 14 -66 14 -58 L 14 -34 Z" fill="{shirt}"/>')
    if phone:
        s += (f'<path d="M -13 -60 L -6 -44 L 0 -46 M 13 -60 L 6 -44 L 0 -46" stroke="{shirt}" stroke-width="6" stroke-linecap="round" fill="none"/>'
              f'<rect x="-5" y="-54" width="10" height="13" rx="2" fill="#bff4ff"/><circle cx="0" cy="-62" r="16" fill="#3be0ff" opacity=".22"/>'
              f'<circle cx="0" cy="-74" r="10" fill="{skin}"/><path d="M -10 -76 Q -10 -86 0 -86 Q 10 -86 10 -76 Q 4 -81 -10 -76 Z" fill="{hair}"/>')
    else:
        s += (f'<path d="M -14 -60 L -18 -36 M 14 -60 L 18 -36" stroke="{shirt}" stroke-width="6" stroke-linecap="round"/>'
              f'<circle cx="-18" cy="-34" r="3.5" fill="{skin}"/><circle cx="18" cy="-34" r="3.5" fill="{skin}"/>'
              f'<circle cx="0" cy="-77" r="10" fill="{skin}"/><path d="M -10 -78 Q -11 -89 0 -89 Q 11 -89 10 -78 Q 3 -84 -10 -78 Z" fill="{hair}"/>'
              f'<path d="M -4 -74 Q 0 -71 4 -74" stroke="#7a3a2a" stroke-width="1.6" fill="none" stroke-linecap="round"/>')
    return s


PEOPLE_PALETTE = [("#ff7a8a", "#2f3f9a", SKIN, HAIR), ("#38e8a8", "#3a3a4a", "#c68a5e", "#1a1010"), ("#ffd23e", "#4a3a7a", "#f6d2b8", "#d9a441"),
             ("#6a8cff", "#232344", "#8a5a3a", "#14100c"), ("#ff9f43", "#2a5a6a", "#e8b48c", "#5a2a1a"), ("#c77dff", "#3a2a2a", "#a86b45", "#2a1a10"),
             ("#f3f6ff", "#2a3a8a", SKIN, "#241711"), ("#ff4fa3", "#1e2a4a", "#d9a07a", "#8a4a20")]


def figure_defs(p, phone=False):
    return "".join(f'<g id="{p}-tiny{k}">{tiny_person(*c, phone=phone)}</g>' for k, c in enumerate(PEOPLE_PALETTE))


def laptop_desk(p):
    """Desk with a laptop in front of the seated person (draw it first; the hand rests on the keyboard)."""
    return ('<rect x="440" y="-200" width="18" height="200" fill="#3a2a6a"/><rect x="166" y="-200" width="16" height="200" fill="#3a2a6a"/>'
            '<rect x="100" y="-216" width="390" height="22" rx="6" fill="#6a4a9a"/>'
            '<rect x="96" y="-228" width="210" height="12" rx="4" fill="#c9d0ea"/>'
            f'<polygon id="{p}-laptopGlow" points="316,-236 340,-392 60,-450 50,-400" fill="#3be0ff" opacity=".14"/>'
            '<path d="M 304 -224 L 342 -392" stroke="#c9d0ea" stroke-width="16" stroke-linecap="round"/>'
            f'<path id="{p}-laptopScreen" d="M 296 -232 L 332 -386" stroke="#3be0ff" stroke-width="6" stroke-linecap="round"/>'
            '<g transform="translate(410 -216)"><rect x="-18" y="-40" width="36" height="40" rx="6" fill="#ff7a8a"/><path d="M 18 -32 q 14 2 10 16 q -2 8 -10 6" stroke="#ff7a8a" stroke-width="6" fill="none"/>'
            '<path d="M -4 -50 q -6 -10 0 -18 M 8 -50 q -6 -10 0 -18" stroke="#eef1ff" stroke-width="3" fill="none" opacity=".6"/></g>')


def armchair(color="#2a8a9a", dark="#1a5a6a"):
    """Armchair in profile (seated person, feet at y=0). Draw it before the person."""
    return (f'<rect x="-190" y="-270" width="300" height="120" rx="30" fill="{dark}"/>'
            f'<path d="M -200 -150 L -200 -390 Q -200 -440 -150 -440 Q -100 -440 -100 -390 L -100 -150 Z" fill="{color}"/>'
            f'<rect x="-200" y="-176" width="350" height="96" rx="26" fill="{color}"/><rect x="-190" y="-184" width="330" height="30" rx="14" fill="#3bb0c0"/>'
            '<rect x="-180" y="-84" width="18" height="84" rx="5" fill="#123a44"/><rect x="120" y="-84" width="18" height="84" rx="5" fill="#123a44"/>')


def bed_back():
    return ('<rect x="-236" y="-440" width="64" height="420" rx="22" fill="#4a2f9a" stroke="#8d7bff" stroke-width="4"/>'
            '<rect x="-236" y="-182" width="600" height="44" rx="16" fill="#e8e4ff"/>'
            '<rect x="-206" y="-282" width="120" height="96" rx="34" fill="#fffaf0" transform="rotate(-14 -146 -234)"/>')


def bed_front():
    return ('<path d="M -60 -150 C -40 -214 130 -216 170 -184 C 220 -176 300 -180 364 -176 L 364 -128 L -60 -128 Z" fill="#ff7a8a"/>'
            '<path d="M -40 -164 C 0 -196 100 -200 150 -182" stroke="#ffb0bc" stroke-width="6" fill="none" stroke-linecap="round"/>'
            '<rect x="-236" y="-140" width="600" height="140" rx="14" fill="#3a2a8c"/><rect x="-236" y="-140" width="600" height="14" rx="6" fill="#ff5a70"/>'
            '<rect x="-236" y="-8" width="600" height="8" rx="3" fill="#2a1d70"/>')


def night_window(x, y, w, h):
    return (f'<g transform="translate({x} {y})"><rect width="{w}" height="{h}" rx="10" fill="#0e1240" stroke="#8d7bff" stroke-width="8"/>'
            f'<circle cx="{w * .7:.0f}" cy="{h * .32:.0f}" r="{h * .14:.0f}" fill="#fff3b0"/><circle cx="{w * .7 + h * .07:.0f}" cy="{h * .28:.0f}" r="{h * .12:.0f}" fill="#0e1240"/>'
            + "".join(f'<circle cx="{w * a:.0f}" cy="{h * b:.0f}" r="2.5" fill="#fff"/>' for a, b in ((.2, .2), (.35, .55), (.15, .7), (.55, .8), (.85, .65)))
            + f'<path d="M {w / 2} 0 V {h} M 0 {h / 2} H {w}" stroke="#8d7bff" stroke-width="6"/></g>')


def bus_seat():
    return ('<rect x="-160" y="-420" width="74" height="300" rx="22" fill="#2a6ad0"/><rect x="-150" y="-406" width="54" height="40" rx="10" fill="#7fb4ff"/>'
            '<rect x="-160" y="-176" width="320" height="56" rx="18" fill="#2a6ad0"/><rect x="-40" y="-120" width="18" height="120" fill="#5a6a8a"/>')


def bus_windows(p, x0, x1, y0, y1):
    """Strip of bus windows with the city going by ({p}-city moves left)."""
    w = x1 - x0
    rng = random.Random(5)
    buildings = ""
    xx = 0
    while xx < 2 * w + 400:
        bw, bh = rng.randint(60, 130), rng.randint(90, int((y1 - y0) * .85))
        buildings += f'<rect x="{xx}" y="{y1 - y0 - bh}" width="{bw}" height="{bh}" fill="{rng.choice(["#2a2f7a", "#35308a", "#24286a"])}"/>'
        buildings += "".join(f'<rect x="{xx + 12 + c * 22}" y="{y1 - y0 - bh + 14 + r * 26}" width="10" height="12" fill="#ffd27a" opacity="{rng.choice([.2, .7, .9])}"/>'
                           for r in range(max(1, bh // 26 - 1)) for c in range(max(1, (bw - 16) // 22)))
        xx += bw + rng.randint(6, 24)
    return (f'<clipPath id="{p}-windowClip"><rect x="{x0}" y="{y0}" width="{w}" height="{y1 - y0}" rx="18"/></clipPath>'
            f'<rect x="{x0}" y="{y0}" width="{w}" height="{y1 - y0}" rx="18" fill="#3a5ab8"/>'
            f'<g clip-path="url(#{p}-windowClip)"><g transform="translate({x0} {y0})"><g id="{p}-city">{buildings}</g></g></g>'
            + "".join(f'<rect x="{x0 + k * w / 3 - 8:.0f}" y="{y0 - 6}" width="16" height="{y1 - y0 + 12}" fill="#c9d0ea"/>' for k in range(1, 3))
            + f'<rect x="{x0 - 8}" y="{y0 - 8}" width="{w + 16}" height="{y1 - y0 + 16}" rx="22" fill="none" stroke="#c9d0ea" stroke-width="12"/>')


def kitchen(x0, x1, ytop, yfloor):
    """Counter (behind the person), upper cabinets, sunny window. Global coordinates."""
    w = x1 - x0
    return (f'<rect x="{x0}" y="{ytop - 480}" width="{w}" height="150" rx="10" fill="#e8d8c0"/>'
            + "".join(f'<rect x="{x0 + 10 + k * (w - 20) / 3:.0f}" y="{ytop - 470}" width="{(w - 20) / 3 - 10:.0f}" height="130" rx="8" fill="#f6ead8"/><circle cx="{x0 + (k + .5) * (w - 20) / 3 + 10:.0f}" cy="{ytop - 350}" r="5" fill="#a08a6a"/>' for k in range(3))
            + f'<g transform="translate({x0 + w * .38:.0f} {ytop - 300})"><rect width="{w * .4:.0f}" height="220" rx="8" fill="#ffe9b0" stroke="#f6ead8" stroke-width="10"/>'
            f'<circle cx="{w * .28:.0f}" cy="90" r="42" fill="#ffb23e"/><path d="M 0 180 Q {w * .1:.0f} 150 {w * .2:.0f} 170 T {w * .4:.0f} 160 V 220 H 0 Z" fill="#8bd18b"/></g>'
            f'<rect x="{x0}" y="{ytop}" width="{w}" height="22" rx="6" fill="#d0c0a8"/><rect x="{x0 + 10}" y="{ytop + 22}" width="{w - 20}" height="{yfloor - ytop - 22}" fill="#b98a5e"/>'
            + "".join(f'<rect x="{x0 + 22 + k * (w - 44) / 3:.0f}" y="{ytop + 36}" width="{(w - 44) / 3 - 12:.0f}" height="{yfloor - ytop - 60}" rx="8" fill="#c99a6e"/>' for k in range(3))
            + f'<g transform="translate({x1 - 90} {ytop})"><path d="M -34 0 L -30 -60 Q 0 -74 30 -60 L 34 0 Z" fill="#ff4f7d"/><path d="M 30 -50 q 22 4 18 26" stroke="#ff4f7d" stroke-width="7" fill="none"/>'
            f'<path d="M -6 -80 q -8 -14 0 -26 M 10 -80 q -8 -14 0 -26" stroke="#eef1ff" stroke-width="4" fill="none" opacity=".7"/></g>')


# ---------------------------------------------------------------- 0: "File four. Influence."
def scene0():
    i = 0; p = ID(i); dur = D(i)
    t_file, t_4, t_title = 0.2, 0.69, 2.05
    extra = (f'<linearGradient id="{p}-backGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9a35a"/><stop offset="1" stop-color="#a5672b"/></linearGradient>'
             f'<linearGradient id="{p}-frontGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3c983"/><stop offset="1" stop-color="#d39a50"/></linearGradient>'
             f'<radialGradient id="{p}-light" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#3be0ff" stop-opacity=".55"/><stop offset="1" stop-color="#3be0ff" stop-opacity="0"/></radialGradient>')
    svg = f"""<g id="{p}-folderY">
 <ellipse cx="960" cy="935" rx="620" ry="30" fill="#05031a" opacity=".55" filter="url(#{p}-blur6)"/>
 <path d="M410 300 L410 244 Q410 222 432 222 L842 222 Q864 222 872 244 L892 300 L1510 300 L1510 900 L410 900 Z" fill="url(#{p}-backGrad)" stroke="#ffe0a0" stroke-width="5"/>
 <clipPath id="{p}-tabcp"><rect x="420" y="226" width="460" height="74"/></clipPath>
 <g clip-path="url(#{p}-tabcp)"><g id="{p}-tabT"><text x="446" y="268" font-family="IBM Plex Mono" font-weight="700" font-size="46" letter-spacing="5" fill="#3a2412">FILE 4</text></g></g>
 <rect x="460" y="282" width="1000" height="600" rx="8" fill="#fffaf0" transform="rotate(-2 960 580)"/>
 <rect x="470" y="292" width="980" height="590" rx="8" fill="#efe6d2" transform="rotate(1.6 960 580)"/>
 <ellipse id="{p}-shine" cx="960" cy="330" rx="420" ry="260" fill="url(#{p}-light)" opacity="0"/>
 <g transform="translate(960 650) scale(.56)"><g id="{p}-phoneY">{phone_mock(p, "a", ["happy", "neutral", "sad", "happy", "neutral", "sad", "happy", "neutral"])}</g></g>
 <path d="M380 452 L1540 452 L1504 912 L416 912 Z" fill="url(#{p}-frontGrad)" stroke="#ffe0a0" stroke-width="5" stroke-linejoin="round"/>
 <path d="M396 470 L1524 470" stroke="#fff6dc" stroke-width="4" opacity=".6"/>
 <clipPath id="{p}-ticp"><rect x="420" y="560" width="1080" height="260"/></clipPath>
 <g clip-path="url(#{p}-ticp)"><g id="{p}-title"><text x="960" y="760" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="190" fill="#2a1650">Influence</text></g></g>
</g>"""
    js = (f'camZ("#{p}-cam", 0, {dur:.2f}, 1.0, 1.1, 960, 560, "power1.inOut");\n'
          + ft(f"#{p}-folderY", "{y:760,rotation:3,transformOrigin:'50% 50%'}", "{y:0,rotation:0,transformOrigin:'50% 50%',duration:0.8,ease:'expo.out'}", 0.0)
          + ft(f"#{p}-tabT", "{y:80}", "{y:0,duration:0.7,ease:'expo.out'}", max(0.3, t_file + 0.1))
          + ft(f"#{p}-phoneY", "{y:0}", "{y:-400,duration:0.9,ease:'back.out(1.5)'}", t_title - 0.35)
          + ft(f"#{p}-shine", "{opacity:0}", "{opacity:1,duration:0.6}", t_title - 0.2)
          + ft(f"#{p}-aposts", "{y:0}", "{y:-420,duration:%.2f,ease:'none'}" % (dur - t_title + 0.3), t_title - 0.3)
          + ft(f"#{p}-title", "{y:260}", "{y:0,duration:0.8,ease:'expo.out'}", t_title))
    return composition(p, dur, svg, "", js, extra, seed=4)


# ---------------------------------------------------------------- 1: lab, implant, brain scanner... only a feed
def scene1():
    i = 1; p = ID(i); dur = D(i)
    t_lab, t_imp, t_scan, t_next, t_only, t_feed = 2.14, 3.09, 5.13, 6.74, 8.02, 8.56
    extra = (f'<radialGradient id="{p}-ring" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#8d7bff"/><stop offset="1" stop-color="#3a2a8c"/></radialGradient>'
             f'<linearGradient id="{p}-glass" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#bff4ff" stop-opacity=".18"/><stop offset="1" stop-color="#bff4ff" stop-opacity=".05"/></linearGradient>')
    flask = (f'<ellipse cx="0" cy="178" rx="170" ry="16" fill="#05031a" opacity=".5"/>'
              f'<path d="M-112 60 L112 60 L150 130 Q160 160 130 160 L-130 160 Q-160 160 -150 130 Z" fill="{MINT}" opacity=".75"/>'
              f'<g id="{p}-bubbles" fill="#d8fff0">' + "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in [(-40, 120, 9), (20, 100, 7), (60, 135, 10), (-80, 140, 6), (0, 80, 5)]) + '</g>'
              f'<path d="M-50 -170 L-50 -60 L-150 130 Q-160 160 -130 160 L130 160 Q160 160 150 130 L50 -60 L50 -170 Z" fill="url(#{p}-glass)" stroke="{CYAN}" stroke-width="8" stroke-linejoin="round" filter="url(#{p}-glow)"/>'
              f'<rect x="-66" y="-190" width="132" height="22" rx="10" fill="#15133a" stroke="{CYAN}" stroke-width="6"/>'
              f'<path d="M-24 -40 L-60 40" stroke="#fff" stroke-opacity=".4" stroke-width="10" stroke-linecap="round"/>')
    mri = (f'<ellipse cx="0" cy="200" rx="250" ry="18" fill="#05031a" opacity=".5"/>'
          f'<circle r="180" fill="url(#{p}-ring)" stroke="#c9b8ff" stroke-width="6" filter="url(#{p}-shadow)"/>'
          f'<circle r="96" fill="#0b0a24" stroke="{CYAN}" stroke-width="6" filter="url(#{p}-glow)"/>'
          f'<rect x="-250" y="40" width="500" height="30" rx="12" fill="#eef1ff"/><rect x="-40" y="70" width="80" height="120" fill="#2a2870"/>'
          f'<path d="M-130 -120 A180 180 0 0 1 60 -170" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="12" stroke-linecap="round"/>')
    chip = (f'<g id="{p}-chip"><path d="M196 34 C 196 0 230 -10 250 -30" fill="none" stroke="{AMBER}" stroke-width="3" stroke-linecap="round"/>'
            f'<rect x="180" y="26" width="34" height="20" rx="5" fill="{AMBER}" filter="url(#{p}-glow)" transform="rotate(-12 197 36)"/></g>')
    svg = f"""<g id="{p}-trio">
 <g transform="translate(400 470)"><g id="{p}-lab">{flask}</g></g>
 <g transform="translate(632 246) scale(1.6)"><g id="{p}-implantW">{person(p + "i", glow=p + "-glow")}{chip}</g></g>
 <g transform="translate(1520 470)"><g id="{p}-mri">{mri}</g></g>
</g>
<g id="{p}-home" opacity="0">
 {floor(905)}
 <ellipse id="{p}-halo" cx="1440" cy="540" rx="380" ry="440" fill="#3be0ff" opacity="0" filter="url(#{p}-blur40)"/>
 {picture(p + "-q1", "family", 330, 300, .9, -2)}{picture(p + "-q2", "beach", 610, 270, .75, 3)}
 {lamp(p, 190, 905, 470)}
 <g transform="translate(560 905)"><g id="{p}-g">{sofa()}{human(p + "g", "home", "sitting", phone=True)}</g></g>
 <polygon id="{p}-beam" points="668,560 1270,250 1270,830" fill="#3be0ff" opacity="0"/>
 <g transform="translate(1440 540) scale(.72)"><g id="{p}-phone">{phone_mock(p, "f", ["happy", "neutral", "sad", "happy", "neutral", "happy", "sad", "neutral"])}</g></g>
</g>"""
    html = (text(f"{p}-l1", "LAB", "left:140px;width:520px;text-align:center;top:720px;font-size:46px;color:#bff4ff", "pill2")
            + text(f"{p}-l2", "IMPLANT", "left:700px;width:520px;text-align:center;top:720px;font-size:46px;color:#ffd98a", "pill2")
            + text(f"{p}-l3", "BRAIN SCANNER", "left:1260px;width:520px;text-align:center;top:720px;font-size:46px;color:#c9b8ff", "pill2")
            + text(f"{p}-t", "Only a feed", "left:1000px;width:980px;text-align:center;top:40px;font-size:120px;color:#ffffff"))
    js = (f'camZ("#{p}-cam", 0, {t_scan + 0.6:.2f}, 1.45, 1.0, 400, 470);\n'
          f'camZ("#{p}-cam", {t_scan + 0.6:.2f}, {dur - t_scan - 0.6:.2f}, 1.0, 1.05, 400, 470, "power1.inOut");\n'
          f'pop("#{p}-lab", 0.25, 0.4, 0.8); rise("#{p}-l1 span", {t_lab:.2f});\n'
          + ft(f"#{p}-bubbles", "{y:0}", "{y:-60,duration:0.9,repeat:7,ease:'power1.in'}", t_lab)
          + f'pop("#{p}-implantW", {t_imp - 0.1:.2f}, 0.4, 0.8); rise("#{p}-l2 span", {t_imp:.2f});\n'
          + ft(f"#{p}-chip", "{opacity:1}", "{opacity:0.35,duration:0.3,repeat:9,yoyo:true,ease:'sine.inOut'}", t_imp + 0.6)
          + f'pop("#{p}-mri", {t_scan - 0.1:.2f}, 0.4, 0.8); rise("#{p}-l3 span", {t_scan:.2f});\n'
          + ft(f"#{p}-trio", "{opacity:1,y:0,scale:1,svgOrigin:'960 470'}", "{opacity:0,y:90,scale:0.82,svgOrigin:'960 470',duration:0.9,ease:'power2.inOut',immediateRender:false}", t_next)
          + "".join(vanish(f"#{p}-l{k} span", t_next) for k in (1, 2, 3))
          + f'enter("#{p}-home", {t_next + 0.3:.2f}, 0.4);\n'
          + ft(f"#{p}-g", "{x:-500}", "{x:0,duration:1.0,ease:'expo.out',immediateRender:false}", t_next + 0.3)
          + ft(f"#{p}-phone", "{y:900}", "{y:0,duration:1.0,ease:'back.out(1.2)',immediateRender:false}", t_next + 0.5)
          + ft(f"#{p}-halo", "{opacity:0}", "{opacity:0.22,duration:0.8}", t_next + 0.9)
          + ft(f"#{p}-beam", "{opacity:0}", "{opacity:0.12,duration:0.6}", t_feed - 0.2)
          + ft(f"#{p}-fposts", "{y:0}", "{y:-500,duration:%.2f,ease:'none'}" % (dur - t_next), t_next + 0.4)
          + phone_gaze(p + "g") + screen_js(p + "g", ["#ffd23e", "#8d7bff", "#7fb4ff", "#ffd23e", "#38e8a8"], t_next + 0.6, 0.55)
          + f'rise("#{p}-t span", {t_only:.2f}, 0.9);\n'
          + person_idle(p + "i", dur) + figure_idle(p + "g", dur, (t_next + 1.4, t_next + 3.0)))
    return composition(p, dur, svg, html, js, extra, seed=6)


def vanish(sel, t):
    return f'tl.to("{sel}",{{yPercent:-125,duration:0.45,ease:"power2.in"}},{t:.2f});\n'


# ---------------------------------------------------------------- 2: January 2012, 689 thousand people, fewer happy / fewer sad
def scene2():
    i = 2; p = ID(i); dur = D(i)
    t_jan, t_week, t_fb, t_swap, t_num, t_people = 0.13, 3.31, 4.05, 4.65, 5.66, 7.48
    t_some, t_fewer1, t_happy, t_others, t_fewer2, t_posts2 = 8.55, 9.55, 11.34, 12.89, 13.58, 14.5
    extra = figure_defs(p)
    days = "".join(f'<rect id="{p}-d{k}" x="{565 + k * 116}" y="480" width="96" height="96" rx="16" fill="#2a2870" stroke="#4a4ab0" stroke-width="4"/>' for k in range(7))
    days += "".join(f'<rect x="{565 + k * 116}" y="604" width="96" height="96" rx="16" fill="#1e1c5a" opacity=".6"/>' for k in range(7))
    rings = "".join(f'<rect x="{620 + k * 140}" y="306" width="18" height="70" rx="9" fill="#eef1ff" stroke="#15133a" stroke-width="4"/>' for k in range(5))
    tL = ["happy", "neutral", "happy", "sad", "happy", "neutral", "happy", "sad"]
    tR = ["sad", "neutral", "sad", "happy", "sad", "neutral", "sad", "happy"]
    svg = f"""
<g id="{p}-cal"><g filter="url(#{p}-shadow)"><rect x="520" y="330" width="880" height="420" rx="34" fill="#15133a" stroke="{LILAC}" stroke-width="8"/></g>
 <rect x="524" y="334" width="872" height="100" rx="30" fill="#7b2a6c"/><rect x="524" y="404" width="872" height="30" fill="#7b2a6c"/>{rings}{days}
 <rect id="{p}-week" x="550" y="466" width="822" height="124" rx="24" fill="none" stroke="{AMBER}" stroke-width="8" opacity="0" filter="url(#{p}-glow)"/></g>
<g id="{p}-g1" opacity="0">
 {floor(880)}
 {night_window(170, 150, 300, 230)}
 <g transform="translate(990 880)"><rect x="-70" y="-190" width="140" height="190" rx="10" fill="#4a2f9a"/><rect x="-60" y="-120" width="120" height="8" fill="#2a1d70"/></g>
 {lamp(p, 990, 690, 220, "#ffd27a")}
 <g transform="translate(520 880) scale(1.05)">{bed_back()}{human(p + "b", "home", "sitting", phone=True)}{bed_front()}</g>
 <polygon id="{p}-beam" points="640,540 1200,180 1200,900" fill="#3be0ff" opacity=".1"/>
 <g transform="translate(1380 540) scale(.9)">{phone_mock(p, "m", ["happy", "neutral", "happy", "sad", "neutral", "happy"], extra=SWAP.format(p=p))}</g>
</g>
<g id="{p}-crowd" opacity="0">{figure_crowd(p)}</g>
<g id="{p}-pair" opacity="0">
 <g><clipPath id="{p}-pLcp"><rect x="30" y="96" width="900" height="790" rx="30"/></clipPath>
  <rect x="30" y="96" width="900" height="790" rx="30" fill="#120c40" opacity=".85"/>
  <g clip-path="url(#{p}-pLcp)">{bus_windows(p, 60, 900, 130, 400)}<rect x="30" y="840" width="900" height="60" fill="#2a2440"/>
   <rect x="452" y="96" width="16" height="760" fill="#ffd23e"/>
   <g transform="translate(200 850) scale(.85)">{bus_seat()}{human(p + "L", "home", "sitting", phone=True, colors=OTHER_A)}</g></g>
  <rect x="30" y="96" width="900" height="790" rx="30" fill="none" stroke="{LILAC}" stroke-width="6"/>
  <g transform="translate(690 500) scale(.66)">{phone_mock(p, "L", tL, "#1a2a6c")}</g></g>
 <g id="{p}-sideR"><clipPath id="{p}-pRcp"><rect x="990" y="96" width="900" height="790" rx="30"/></clipPath>
  <rect x="990" y="96" width="900" height="790" rx="30" fill="#2a1a40" opacity=".85"/>
  <g clip-path="url(#{p}-pRcp)">{kitchen(1000, 1520, 640, 860)}<rect x="990" y="850" width="900" height="50" fill="#3a2a3a"/>
   <g transform="translate(1180 860) scale(.78)">{human(p + "R", "home", "standing", phone=True, colors=OTHER_B, mood="neutral")}</g></g>
  <rect x="990" y="96" width="900" height="790" rx="30" fill="none" stroke="{LILAC}" stroke-width="6"/>
  <g transform="translate(1680 500) scale(.66)">{phone_mock(p, "R", tR, "#ffb23e")}</g></g>
</g>"""
    html = (text(f"{p}-t1", "January 2012", "left:0;right:0;text-align:center;top:110px;font-size:120px;color:#ffd98a")
            + text(f"{p}-n", f'<b id="{p}-nv" style="font-weight:700">0</b>', "left:0;right:0;text-align:center;top:40px;font-size:170px;color:#ffffff")
            + text(f"{p}-np", "PEOPLE", "left:0;right:0;text-align:center;top:262px;font-size:60px;color:#3be0ff", "pill2")
            + text(f"{p}-lL", "FEWER HAPPY POSTS", "left:20px;width:900px;text-align:center;top:905px;font-size:48px;color:#9fb8ff;letter-spacing:.01em", "pill2")
            + text(f"{p}-lR", "FEWER SAD POSTS", "left:980px;width:900px;text-align:center;top:905px;font-size:48px;color:#ffd98a;letter-spacing:.01em", "pill2"))
    js = (f'camZ("#{p}-cam", 0, {t_fb:.2f}, 1.12, 1.0, 960, 540, "power2.out");\n'
          f'camZ("#{p}-cam", {t_fb:.2f}, {t_some - t_fb:.2f}, 1.0, 1.04, 960, 540, "none");\n'
          f'camZ("#{p}-cam", {t_some:.2f}, {dur - t_some:.2f}, 1.04, 1.0, 960, 540, "power1.inOut");\n'
          f'rise("#{p}-t1 span", {t_jan:.2f}); pop("#{p}-cal", 0.05, 0.6, 0.9);\n'
          + "".join(ft(f"#{p}-d{k}", "{fill:'#2a2870'}", "{fill:'#ffb23e',duration:0.15,immediateRender:false}", t_week - 0.6 + k * 0.17) for k in range(7))
          + ft(f"#{p}-week", "{opacity:0}", "{opacity:1,duration:0.3}", t_week + 0.6)
          + vanish(f"#{p}-t1 span", t_fb - 0.2)
          + ft(f"#{p}-cal", "{opacity:1}", "{opacity:0,y:-200,duration:0.5,ease:'power2.in',immediateRender:false}", t_fb - 0.2)
          + f'enter("#{p}-g1", {t_fb:.2f}, 0.3);\n'
          + ft(f"#{p}-g1", "{scale:1.2,svgOrigin:'960 650'}", "{scale:1,svgOrigin:'960 650',duration:0.9,ease:'expo.out',immediateRender:false}", t_fb)
          + ft(f"#{p}-mposts", "{y:0}", "{y:-300,duration:3,ease:'none'}", t_fb)
          + f'tl.set("#{p}-swap",{{x:380}},0);\n'
          + ft(f"#{p}-mc0", "{x:0}", "{x:-380,duration:0.4,ease:'power2.in'}", t_swap)
          + ft(f"#{p}-swap", "{x:380}", "{x:0,duration:0.5,ease:'back.out(1.4)',immediateRender:false}", t_swap + 0.25)
          + phone_gaze(p + "b") + screen_js(p + "b", ["#ffd23e", "#8d7bff", "#ffd23e"], t_fb + 0.2, 0.6)
          + f'tl.to("#{p}b-screen",{{attr:{{fill:"#7fb4ff"}},duration:0.2}},{t_swap + 0.3:.2f});\n'
          + mood_js(p + "b", "happy", "neutral", t_swap + 0.5)
          + ft(f"#{p}-g1", "{scale:1,opacity:1,svgOrigin:'960 650'}", "{scale:0.06,opacity:0,svgOrigin:'960 650',duration:0.9,ease:'power2.in',immediateRender:false}", t_num - 0.2)
          + f'enter("#{p}-crowd", {t_num:.2f}, 0.3);\n'
          + ft(f"#{p}-crowd .member", "{scale:0,transformOrigin:'50% 50%'}", "{scale:1,transformOrigin:'50% 50%',duration:0.3,ease:'back.out(2)',stagger:{amount:1.6,from:'center',grid:[7,26]}}", t_num)
          + ft(f"#{p}-crowd", "{scale:1.4,svgOrigin:'960 650'}", "{scale:1,svgOrigin:'960 650',duration:2.6,ease:'power2.out',immediateRender:false}", t_num)
          + f'rise("#{p}-n span", {t_num:.2f});\n'
          + f'count_up("{p}-nv", {t_num:.2f}, 1.5, 0, 689, function(v){{return (Math.round(v)*1000).toLocaleString("en-US");}});\n'
          + f'rise("#{p}-np span", {t_people:.2f});\n'
          + vanish(f"#{p}-n span", t_some - 0.3) + vanish(f"#{p}-np span", t_some - 0.3)
          + ft(f"#{p}-crowd", "{opacity:1}", "{opacity:0,duration:0.5,immediateRender:false}", t_some - 0.3)
          + f'enter("#{p}-pair", {t_some:.2f}, 0.4);\n'
          + ft(f"#{p}-pair", "{x:-300}", "{x:0,duration:0.9,ease:'expo.out',immediateRender:false}", t_some)
          + ft(f"#{p}-sideR", "{opacity:0.25}", "{opacity:1,duration:0.5,immediateRender:false}", t_others - 0.3)
          + ft(f"#{p}-sideR", "{opacity:1}", "{opacity:0.25,duration:0.01}", 0)
          + ft(f"#{p}-Lposts", "{y:0}", "{y:-380,duration:%.2f,ease:'none'}" % (dur - t_some), t_some)
          + ft(f"#{p}-Rposts", "{y:0}", "{y:-380,duration:%.2f,ease:'none'}" % (dur - t_some), t_some)
          + f'rise("#{p}-lL span", {t_fewer1:.2f});\n'
          + "".join(ft(f"#{p}-Lc{k}", "{x:0,opacity:1}", "{x:-360,opacity:0,duration:0.45,ease:'power2.in'}", t_fewer1 + 0.3 + n * 0.3) for n, k in enumerate(k for k, t in enumerate(tL) if t == "happy"))
          + ft(f"#{p}-Ltint", "{opacity:0}", "{opacity:0.35,duration:0.8}", t_happy - 0.3)
          + mood_js(p + "L", "happy", "sad", t_happy - 0.2, 0.4)
          + ft(f"#{p}L-faceGlow", "{attr:{fill:'#3be0ff'}}", "{attr:{fill:'#3b5bff'},duration:0.8}", t_happy - 0.3)
          + ft(f"#{p}-city", "{x:0}", "{x:-900,duration:%.2f,ease:'none'}" % (dur - t_some), t_some)
          + phone_gaze(p + "L") + phone_gaze(p + "R")
          + f'rise("#{p}-lR span", {t_fewer2:.2f});\n'
          + "".join(ft(f"#{p}-Rc{k}", "{x:0,opacity:1}", "{x:360,opacity:0,duration:0.45,ease:'power2.in'}", t_fewer2 + 0.3 + n * 0.25) for n, k in enumerate(k for k, t in enumerate(tR) if t == "sad"))
          + ft(f"#{p}-Rtint", "{opacity:0}", "{opacity:0.18,duration:0.8}", t_posts2)
          + mood_js(p + "R", "neutral", "happy", t_posts2, 0.35)
          + ft(f"#{p}R-faceGlow", "{attr:{fill:'#3be0ff'}}", "{attr:{fill:'#ffd23e'},duration:0.8}", t_posts2)
          + figure_idle(p + "b", dur, (t_fb + 1.0, t_fb + 2.6)) + figure_idle(p + "L", dur, (9.4, 12.2, 14.8)) + figure_idle(p + "R", dur, (10.1, 13.3, 15.5)))
    return composition(p, dur, svg, html, js, extra, seed=11)


# ---------------------------------------------------------------- 3: "Nobody was told."
def scene3():
    i = 3; p = ID(i); dur = D(i)
    t_nobody, t_was, t_told = 0.46, 1.34, 1.57
    extra = figure_defs(p, phone=True) + f'<linearGradient id="{p}-bell" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe08a"/><stop offset="1" stop-color="#e08a1e"/></linearGradient>'
    rng = random.Random(3)
    rows = ""
    for r in range(6):
        e = 1.0 + r * 0.42
        y = 420 + r * 124
        n = int(2200 / (54 * e)) + 2
        rows += f'<g opacity="{0.45 + r * 0.11:.2f}">' + "".join(
            f'<use href="#{p}-tiny{rng.randint(0, 7)}" transform="translate({-140 + (c + (r % 2) * .5) * 54 * e + rng.randint(-6, 6):.0f} {y + rng.randint(-6, 6)}) scale({e:.2f})"/>'
            for c in range(n)) + '</g>'
    svg = f"""<g id="{p}-crowd">{rows}</g>
<ellipse cx="960" cy="420" rx="320" ry="320" fill="#0b0a24" opacity=".75" filter="url(#{p}-blur40)"/>
<rect x="-100" y="760" width="2120" height="420" fill="#0b0a24" opacity=".8" filter="url(#{p}-blur40)"/>
<g transform="translate(960 400) scale(.9)"><g id="{p}-bell">
 <g id="{p}-bellB"><circle cx="0" cy="-172" r="22" fill="url(#{p}-bell)"/>
 <path d="M-130 90 C-130 -40 -110 -150 0 -158 C110 -150 130 -40 130 90 L166 136 L-166 136 Z" fill="url(#{p}-bell)" stroke="#fff3c8" stroke-width="6" stroke-linejoin="round" filter="url(#{p}-shadow)"/>
 <circle cx="0" cy="166" r="34" fill="#e08a1e"/><path d="M-80 -60 C-74 -110 -40 -134 -6 -136" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="14" stroke-linecap="round"/></g>
 <circle cx="0" cy="0" r="250" fill="none" stroke="{RED}" stroke-width="30" stroke-dasharray="1571" stroke-dashoffset="1571" id="{p}-ring" transform="rotate(-135)" filter="url(#{p}-glow)"/>
 <line id="{p}-slash" x1="-177" y1="-177" x2="177" y2="177" stroke="{RED}" stroke-width="30" stroke-linecap="round" stroke-dasharray="500" stroke-dashoffset="500"/>
</g></g>"""
    html = f'<div style="position:absolute;left:0;right:0;bottom:0;height:330px;background:linear-gradient(rgba(8,6,28,0),rgba(8,6,28,.96) 40%)"></div>' + text(f"{p}-t", "Nobody was told", "left:0;right:0;text-align:center;top:830px;font-size:130px;color:#ffffff")
    js = (f'camZ("#{p}-cam", 0, {dur:.2f}, 1.0, 1.1, 960, 400, "power1.inOut");\n'
          f'pop("#{p}-bell", 0.1, 0.4, 0.8);\n'
          + ft(f"#{p}-bellB", "{rotation:-12,transformOrigin:'50% 0%'}", "{rotation:12,transformOrigin:'50% 0%',duration:0.16,repeat:5,yoyo:true,ease:'sine.inOut'}", 0.3)
          + ft(f"#{p}-crowd", "{scale:1.15,svgOrigin:'960 540'}", "{scale:1,svgOrigin:'960 540',duration:%.2f,ease:'power2.out'}" % dur, 0)
          + f'rise("#{p}-t span", {t_nobody:.2f}, 0.8);\n'
          + ft(f"#{p}-ring", "{attr:{'stroke-dashoffset':1571}}", "{attr:{'stroke-dashoffset':0},duration:0.5,ease:'power2.inOut'}", t_was - 0.3)
          + ft(f"#{p}-slash", "{attr:{'stroke-dashoffset':500}}", "{attr:{'stroke-dashoffset':0},duration:0.3,ease:'power2.in'}", t_told)
          + ft(f"#{p}-bellB", "{opacity:1}", "{opacity:0.7,duration:0.3,immediateRender:false}", t_told + 0.2))
    return composition(p, dur, svg, html, js, extra, background=("#2c1460", "#160c40", "#08061c"), seed=13)


# ---------------------------------------------------------------- 4: the study page (Kramer, Guillory and Hancock, PNAS 2014)
R_AUTHORS = [(105, 287, 760, 30)]
R_QUOTE = [(594, 744, 180, 29), (105, 771, 669, 29), (105, 798, 250, 29)]


def scene4():
    i = 4; p = ID(i); dur = D(i)
    t_authors, t_measure, t_chose, t_who, t_less, t_wrote, t_fewer, t_pos, t_more, t_neg = (
        1.0, 1.84, 3.61, 4.67, 5.24, 7.28,
        8.12, 9.48, 11.09, 11.72)
    S, X0, Y0 = 0.42, 624, 150
    ox, oy = 470, Y0 + 785 * S    # screen point where the quoted sentence sits after the slide
    svg = f"""<g id="{p}-pageX"><g id="{p}-pageY"><g transform="translate({X0} {Y0}) scale({S})">{page(p, "kramer2014", "k", R_AUTHORS + R_QUOTE)}
 <g id="{p}-scan" opacity="0"><rect x="0" y="-8" width="1600" height="16" fill="{CYAN}" opacity=".75" filter="url(#{p}-glow)"/><rect x="0" y="-160" width="1600" height="152" fill="{CYAN}" opacity=".1"/></g>
</g></g></g>"""
    panel_html = f"""<div id="{p}-panel" style="position:absolute;left:1090px;top:150px;width:740px;height:780px;background:#0e0c26;border:4px solid #8d7bff;border-radius:34px;box-shadow:0 24px 70px rgba(0,0,0,.7);opacity:0;overflow:hidden">
 {text(p + "-pt", "WORDS", "left:0;right:0;text-align:center;top:44px;font-size:56px;color:#eef1f7", "pill2")}
 <div style="position:absolute;left:60px;right:60px;top:590px;height:6px;background:#4a4ab0;border-radius:3px"></div>
 <div id="{p}-gp" style="position:absolute;left:110px;top:210px;width:190px;height:380px;border:4px dashed #38e8a8;border-bottom:none;border-radius:16px 16px 0 0;opacity:0"></div>
 <div id="{p}-gn" style="position:absolute;left:450px;top:290px;width:190px;height:300px;border:4px dashed #ff4f7d;border-bottom:none;border-radius:16px 16px 0 0;opacity:0"></div>
 <div id="{p}-bp" style="position:absolute;left:110px;bottom:190px;width:190px;height:380px;background:linear-gradient(#38e8a8,#14705a);border-radius:16px 16px 0 0"></div>
 <div id="{p}-bn" style="position:absolute;left:450px;bottom:190px;width:190px;height:300px;background:linear-gradient(#ff4f7d,#8a1838);border-radius:16px 16px 0 0"></div>
 <div id="{p}-arrowP" style="position:absolute;left:175px;top:140px;width:0;height:0;border-left:30px solid transparent;border-right:30px solid transparent;border-top:46px solid #38e8a8;opacity:0"></div>
 <div id="{p}-arrowN" style="position:absolute;left:515px;top:150px;width:0;height:0;border-left:30px solid transparent;border-right:30px solid transparent;border-bottom:46px solid #ff4f7d;opacity:0"></div>
 {text(p + "-lp", "POSITIVE", "left:25px;width:360px;text-align:center;top:625px;font-size:46px;color:#38e8a8;letter-spacing:.03em", "pill2")}
 {text(p + "-ln", "NEGATIVE", "left:365px;width:360px;text-align:center;top:625px;font-size:46px;color:#ff7d9a;letter-spacing:.03em", "pill2")}
</div>"""
    html = text(f"{p}-t", "WHAT THOSE PEOPLE WROTE", "left:0;right:0;text-align:center;top:14px;font-size:56px;color:#ffd98a", "pill2") + panel_html
    js = (f'camZ("#{p}-cam", 0, {t_who:.2f}, 1.0, 1.15, {ox}, {oy:.0f}, "power1.inOut");\n'
          f'camZ("#{p}-cam", {t_who:.2f}, 1.7, 1.15, 2.2, {ox}, {oy:.0f});\n'
          f'camZ("#{p}-cam", {t_who + 1.7:.2f}, {dur - t_who - 1.7:.2f}, 2.2, 2.35, {ox}, {oy:.0f}, "none");\n'
          + ft(f"#{p}-pageY", "{y:700,rotation:-6,transformOrigin:'50% 50%'}", "{y:0,rotation:0,transformOrigin:'50% 50%',duration:1.1,ease:'expo.out'}", 0.0)
          + ft(f"#{p}-pageX", "{x:0}", "{x:-28,duration:%.2f,ease:'none'}" % t_who, 0)
          + highlight(p, "k", R_AUTHORS, t_authors, 0.7)
          + f'rise("#{p}-t span", {t_measure:.2f});\n'
          + ft(f"#{p}-scan", "{opacity:0}", "{opacity:1,duration:0.2}", t_measure)
          + ft(f"#{p}-scan", "{y:420}", "{y:2000,duration:%.2f,ease:'power1.inOut'}" % (t_who - t_measure), t_measure)
          + ft(f"#{p}-scan", "{opacity:1}", "{opacity:0,duration:0.3,immediateRender:false}", t_who - 0.3)
          + vanish(f"#{p}-t span", t_who - 0.2)
          + ft(f"#{p}-pageX", "{x:-28}", "{x:%d,duration:1.7,ease:'power3.inOut',immediateRender:false}" % (ox - (X0 + 440 * S)), t_who)
          + highlight(p, "k", R_QUOTE, t_less + 0.1, 0.55, len(R_AUTHORS))
          + ft(f"#{p}-panel", "{opacity:0,x:500}", "{opacity:1,x:0,duration:0.8,ease:'expo.out'}", t_wrote - 0.3)
          + f'rise("#{p}-pt span", {t_wrote:.2f});\n'
          + ft(f"#{p}-gp", "{opacity:0}", "{opacity:0.7,duration:0.2}", t_fewer)
          + ft(f"#{p}-bp", "{height:380}", "{height:310,duration:0.8,ease:'power2.inOut'}", t_fewer)
          + ft(f"#{p}-arrowP", "{opacity:0,y:-30}", "{opacity:1,y:0,duration:0.5,ease:'back.out(2)'}", t_fewer + 0.3)
          + f'rise("#{p}-lp span", {t_pos:.2f});\n'
          + ft(f"#{p}-gn", "{opacity:0}", "{opacity:0.7,duration:0.2}", t_more)
          + ft(f"#{p}-bn", "{height:300}", "{height:370,duration:0.8,ease:'power2.inOut'}", t_more)
          + ft(f"#{p}-arrowN", "{opacity:0,y:30}", "{opacity:1,y:0,duration:0.5,ease:'back.out(2)'}", t_more + 0.3)
          + f'rise("#{p}-ln span", {t_neg:.2f});\n')
    return composition(p, dur, svg, html, js, seed=15)


# ---------------------------------------------------------------- 5: the effect was small; nobody asked; the data use policy nobody reads
def scene5():
    i = 5; p = ID(i); dur = D(i)
    t_small, t_size, t_never, t_problem, t_nobody, t_asked = 0.57, 2.06, 2.84, 4.46, 6.07, 6.48
    t_justify, t_policy, t_accept, t_create, t_that = 7.92, 9.8, 12.68, 13.29, 14.71
    rng = random.Random(8)
    lines, y = [], 300
    while y < 4400:
        for _ in range(rng.randint(5, 9)):
            lines.append(f'<rect x="880" y="{y}" width="{rng.randint(560, 740)}" height="12" rx="6" fill="#8a7f68" opacity=".45"/>')
            y += 28
        y += 34
    extra = f'<linearGradient id="{p}-paper" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#ece2cc"/></linearGradient>'
    svg = f"""
{floor(960)}
{picture(p + "-q1", "graduation", 300, 250, .8, -3)}
<g transform="translate(230 960) scale(1.2)">{laptop_desk(p)}{human(p + "a", "home", "sitting", chair=True, mood="neutral")}</g>
<g id="{p}-effect"><g transform="translate(1300 440) scale(1.9)"><g id="{p}-fx">
 <rect x="-120" y="120" width="240" height="8" rx="4" fill="#4a4ab0"/>
 <rect x="-80" y="40" width="60" height="80" rx="8" fill="{MINT}"/><rect x="20" y="42" width="60" height="78" rx="8" fill="{RED}"/>
 <g id="{p}-lens" opacity="0"><circle cx="0" cy="70" r="150" fill="#bff4ff" fill-opacity=".08" stroke="#eef1ff" stroke-width="16" filter="url(#{p}-glow)"/><path d="M106 176 L210 280" stroke="#eef1ff" stroke-width="34" stroke-linecap="round"/></g>
</g></g></g>
<g transform="translate(1260 470)"><g id="{p}-balloon" opacity="0">
 <path d="M-300 -170 Q-300 -200 -270 -200 L270 -200 Q300 -200 300 -170 L300 130 Q300 160 270 160 L-150 160 L-260 240 L-210 160 L-270 160 Q-300 160 -300 130 Z" fill="#ffffff" fill-opacity=".05" stroke="#eef1ff" stroke-width="10" stroke-dasharray="34 22" stroke-linejoin="round"/>
 <text x="0" y="80" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="300" fill="#eef1ff" opacity=".55">?</text>
 <line id="{p}-x1" x1="-210" y1="-150" x2="210" y2="120" stroke="{RED}" stroke-width="28" stroke-linecap="round" stroke-dasharray="500" stroke-dashoffset="500"/>
 <line id="{p}-x2" x1="210" y1="-150" x2="-210" y2="120" stroke="{RED}" stroke-width="28" stroke-linecap="round" stroke-dasharray="500" stroke-dashoffset="500"/>
</g></g>
<g id="{p}-docX" opacity="0"><g id="{p}-docS">
 <rect x="820" y="120" width="860" height="4400" rx="14" fill="url(#{p}-paper)" filter="url(#{p}-shadow)"/>
 <clipPath id="{p}-hcp"><rect x="840" y="150" width="820" height="90"/></clipPath>
 <g clip-path="url(#{p}-hcp)"><g id="{p}-head"><text x="1250" y="220" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="50" letter-spacing="2" fill="#1a1050">DATA USE POLICY</text></g></g>
 <rect id="{p}-hl" x="860" y="166" width="0" height="74" rx="8" fill="#ffd23e" opacity=".5" style="mix-blend-mode:multiply"/>
 {"".join(lines)}
</g></g>
<g id="{p}-footer"><g transform="translate(0 0)">
 <rect x="790" y="860" width="920" height="170" rx="26" fill="#15133a" stroke="{LILAC}" stroke-width="6" filter="url(#{p}-shadow)"/>
 <rect x="830" y="910" width="74" height="74" rx="12" fill="#0b0a24" stroke="#eef1ff" stroke-width="6"/>
 <path id="{p}-ck" d="M846 948 L864 968 L892 924" fill="none" stroke="{MINT}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80"/>
 <g transform="translate(1300 947)"><g id="{p}-bt"><rect id="{p}-btr" x="-340" y="-50" width="680" height="100" rx="22" fill="#3b5bff"/>
 <text x="0" y="17" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="46" letter-spacing="4" fill="#ffffff">CREATE ACCOUNT</text></g></g>
</g></g>"""
    html = (text(f"{p}-t1", "SMALL", "left:900px;width:800px;text-align:center;top:170px;font-size:64px;color:#ffd98a", "pill2")
            + text(f"{p}-t2", "No one asked", "left:620px;width:1300px;text-align:center;top:60px;font-size:120px;color:#ffffff")
            + text(f"{p}-t3", "That text", "left:70px;top:90px;font-size:110px;color:#ffffff")
            + text(f"{p}-t4", "nobody reads", "left:70px;top:220px;font-size:110px;color:#ffd98a"))
    js = (f'camZ("#{p}-cam", 0, {t_that - 0.2:.2f}, 1.0, 1.05, 960, 540, "none");\n'
          f'camZ("#{p}-cam", {t_that - 0.2:.2f}, 1.0, 1.05, 0.72, 960, 540);\n'
          + ft(f"#{p}a-eye", "{x:0}", "{x:3,duration:0.5}", 0.2)
          + f'pop("#{p}-fx", 0.05, 0.5, 0.7);\n'
          + ft(f"#{p}-lens", "{opacity:0,scale:0.4,transformOrigin:'50% 50%'}", "{opacity:1,scale:1,transformOrigin:'50% 50%',duration:0.6,ease:'back.out(2)'}", t_small - 0.1)
          + f'rise("#{p}-t1 span", {t_small:.2f});\n'
          + ft(f"#{p}-fx", "{scale:1}", "{scale:0.5,transformOrigin:'50% 50%',duration:0.9,ease:'power2.inOut',immediateRender:false}", t_size)
          + ft(f"#{p}-effect", "{opacity:1}", "{opacity:0,duration:0.5,immediateRender:false}", t_never + 0.4)
          + vanish(f"#{p}-t1 span", t_never + 0.4)
          + ft(f"#{p}-balloon", "{opacity:0,scale:0.6,transformOrigin:'50% 50%'}", "{opacity:1,scale:1,transformOrigin:'50% 50%',duration:0.8,ease:'back.out(1.6)'}", t_problem)
          + ft(f"#{p}-balloon", "{y:0}", "{y:-14,duration:0.9,repeat:2,yoyo:true,ease:'sine.inOut',immediateRender:false}", t_problem + 0.8)
          + f'rise("#{p}-t2 span", {t_nobody:.2f});\n'
          + ft(f"#{p}-x1", "{attr:{'stroke-dashoffset':500}}", "{attr:{'stroke-dashoffset':0},duration:0.25,ease:'power2.in'}", t_asked)
          + ft(f"#{p}-x2", "{attr:{'stroke-dashoffset':500}}", "{attr:{'stroke-dashoffset':0},duration:0.25,ease:'power2.in'}", t_asked + 0.2)
          + ft(f"#{p}-balloon", "{opacity:1}", "{opacity:0,duration:0.4,immediateRender:false}", t_justify - 0.2)
          + vanish(f"#{p}-t2 span", t_justify - 0.2)
          + f'enter("#{p}-docX", {t_justify - 0.1:.2f}, 0.2);\n'
          + ft(f"#{p}-docX", "{x:1100}", "{x:0,duration:1.0,ease:'expo.out',immediateRender:false}", t_justify - 0.1)
          + ft(f"#{p}-head", "{y:90}", "{y:0,duration:0.7,ease:'expo.out'}", t_justify + 0.3)
          + ft(f"#{p}-hl", "{attr:{width:0}}", "{attr:{width:780},duration:0.8,ease:'power1.inOut'}", t_policy)
          + ft(f"#{p}-docS", "{y:0}", "{y:-2600,duration:%.2f,ease:'power1.in'}" % (t_that - t_policy - 0.2), t_policy + 0.9)
          + ft(f"#{p}a-eye", "{x:3}", "{x:-2,duration:0.18,repeat:7,yoyo:true,ease:'sine.inOut',immediateRender:false}", t_policy + 1.4)
          + ft(f"#{p}-footer", "{y:300}", "{y:0,duration:0.7,ease:'expo.out'}", t_accept - 0.8)
          + ft(f"#{p}-ck", "{attr:{'stroke-dashoffset':80}}", "{attr:{'stroke-dashoffset':0},duration:0.3,ease:'power2.out'}", t_accept)
          + ft(f"#{p}-bt", "{scale:1,transformOrigin:'50% 50%'}", "{scale:0.9,transformOrigin:'50% 50%',duration:0.12,repeat:1,yoyo:true}", t_create)
          + ft(f"#{p}-btr", "{fill:'#3b5bff'}", "{fill:'#1fae80',duration:0.2,immediateRender:false}", t_create + 0.1)
          + ft(f"#{p}-q1", "{opacity:1}", "{opacity:0,duration:0.4,immediateRender:false}", t_that - 0.2)
          + f'rise("#{p}-t3 span", {t_that + 0.55:.2f}); rise("#{p}-t4 span", {t_that + 0.95:.2f});\n'
          + ft(f"#{p}a-eye", "{scaleY:1,transformOrigin:'50% 50%'}", "{scaleY:0.3,transformOrigin:'50% 50%',duration:0.3,immediateRender:false}", t_that + 0.6)
          + ft(f"#{p}a-arm", "{y:0}", "{y:7,duration:0.1,repeat:1,yoyo:true,immediateRender:false}", t_create)
          + mood_js(p + "a", "neutral", "happy", t_accept - 0.2) + mood_js(p + "a", "happy", "neutral", t_that + 0.4)
          + ft(f"#{p}-laptopScreen", "{attr:{stroke:'#3be0ff'}}", "{attr:{stroke:'#fffaf0'},duration:0.3}", t_justify)
          + figure_idle(p + "a", dur, (2.6, 5.2, 9.0, 12.0)))
    return composition(p, dur, svg, html, js, extra, seed=17)


# ---------------------------------------------------------------- 6: the study came out in 2014; two weeks later, the expression of concern
R_CONS = [(128, 667, 646, 28), (105, 694, 669, 28), (105, 721, 255, 28)]


def scene6():
    i = 6; p = ID(i); dur = D(i)
    t_study, t_year, t_two, t_journal, t_published, t_note, t_concern, t_consent = (
        0.86, 2.07, 3.61, 5.4, 6.84, 7.25, 7.68, 9.01)
    S2, X2, Y2 = 0.44, 860, 100
    # final zoom 2.9 to 3.0 with the visible window fully inside page B (no edge between A and B in frame):
    # visible left = ox*(1-1/z) = 840..855 > 814 (edge of sheet B after the drift); right < 1524
    ox, oy = 1282, 342   # already minus the page's -40 px drift
    days = "".join(f'<circle id="{p}-d{k}" cx="{1030 + k * 54}" cy="720" r="18" fill="#2a2870" stroke="#4a4ab0" stroke-width="4"/>' for k in range(14))
    svg = f"""<g id="{p}-drift">
<g transform="translate(250 150) rotate(-3)"><g id="{p}-pA"><g transform="scale(.4)">{page(p, "kramer2014", "a", [])}<rect id="{p}-veil" x="-14" y="-14" width="1628" height="2170" rx="10" fill="#000" opacity="0"/></g></g></g>
<g id="{p}-cal">{days}</g>
<g id="{p}-pB" opacity="0"><g transform="translate({X2} {Y2}) scale({S2})">{page(p, "pnas_concern", "b", R_CONS)}<rect x="-14" y="-14" width="84" height="2170" fill="#ffffff"/></g>
 <g transform="translate(1330 690) rotate(-9)"><g id="{p}-stamp" opacity="0">
  <rect x="-440" y="-62" width="880" height="124" rx="14" fill="#fff3f5" fill-opacity=".92" stroke="{RED}" stroke-width="10"/>
  <text x="0" y="20" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="54" letter-spacing="3" fill="{RED}">EXPRESSION OF CONCERN</text></g></g>
</g></g>"""
    html = (text(f"{p}-year", "2014", "left:1010px;top:250px;font-size:260px;color:#ffd98a")
            + text(f"{p}-later", "TWO WEEKS LATER", "left:1000px;top:580px;font-size:52px;color:#bff4ff", "pill2")
            + f'<div id="{p}-stripe" style="position:absolute;left:250px;width:1420px;top:906px;height:118px;background:#0e0c26;border:3px solid #8d7bff;border-radius:28px;box-shadow:0 18px 50px rgba(0,0,0,.55);opacity:0"></div>'
            + text(f"{p}-consent", "PARTICIPANTS' CONSENT", "left:0;right:0;text-align:center;top:930px;font-size:60px;color:#ffd98a", "pill2"))
    js = (f'camZ("#{p}-cam", 0, {t_consent:.2f}, 1.0, 1.03, {ox:.0f}, {oy:.0f}, "none");\n'
          f'camZ("#{p}-cam", {t_consent:.2f}, 1.5, 1.03, 2.9, {ox:.0f}, {oy:.0f});\n'
          f'camZ("#{p}-cam", {t_consent + 1.5:.2f}, {dur - t_consent - 1.5:.2f}, 2.9, 3.0, {ox:.0f}, {oy:.0f}, "none");\n'
          + ft(f"#{p}-drift", "{x:0}", "{x:-40,duration:%.2f,ease:'none'}" % t_consent, 0)
          + ft(f"#{p}-pA", "{y:900,rotation:-8,transformOrigin:'50% 50%'}", "{y:0,rotation:0,transformOrigin:'50% 50%',duration:1.0,ease:'expo.out'}", max(0.05, t_study - 0.6))
          + f'rise("#{p}-year span", {t_year:.2f}, 0.9);\n'
          + f'rise("#{p}-later span", {t_two:.2f});\n'
          + f'tl.set("#{p}-cal",{{opacity:0}},0); enter("#{p}-cal", {t_two - 0.2:.2f}, 0.3);\n'
          + ft(f"#{p}-cal circle", "{fill:'#2a2870',scale:1,transformOrigin:'50% 50%'}", "{fill:'#ffb23e',scale:1.25,transformOrigin:'50% 50%',duration:0.12,stagger:0.09}", t_two + 0.1)
          + vanish(f"#{p}-year span", t_journal) + vanish(f"#{p}-later span", t_journal)
          + ft(f"#{p}-cal", "{opacity:1}", "{opacity:0,duration:0.4,immediateRender:false}", t_journal)
          + ft(f"#{p}-veil", "{opacity:0}", "{opacity:0.4,duration:0.6}", t_published)
          # the study page leaves before the zoom: with it gone from behind the notice, no purple seam is left on the left edge
          + ft(f"#{p}-pA", "{opacity:1}", "{opacity:0,duration:0.5,immediateRender:false}", t_consent - 0.6)
          + f'enter("#{p}-pB", {t_journal + 0.1:.2f}, 0.2);\n'
          + ft(f"#{p}-pB", "{x:1100,rotation:6,svgOrigin:'1200 600'}", "{x:0,rotation:0,svgOrigin:'1200 600',duration:1.1,ease:'expo.out',immediateRender:false}", t_journal + 0.1)
          + ft(f"#{p}-stamp", "{opacity:0,scale:2.6,transformOrigin:'50% 50%'}", "{opacity:1,scale:1,transformOrigin:'50% 50%',duration:0.28,ease:'power4.in'}", t_note)
          + ft(f"#{p}-pB", "{y:0}", "{y:10,duration:0.08,repeat:1,yoyo:true,immediateRender:false}", t_note + 0.28)
          + ft(f"#{p}-stamp", "{opacity:1}", "{opacity:0,duration:0.4,immediateRender:false}", t_consent)
          + highlight(p, "b", R_CONS, t_consent + 0.4, 0.5)
          + ft(f"#{p}-stripe", "{opacity:0}", "{opacity:1,duration:0.6}", t_consent)
          + f'rise("#{p}-consent span", {t_consent + 0.1:.2f});\n')
    return composition(p, dur, svg, html, js, seed=19)


# ---------------------------------------------------------------- 7: no chip, no light in the brain; just someone who controlled the screen
def scene7():
    i = 7; p = ID(i); dur = D(i)
    # whisper times run ~1.4 s early at the start of this segment ("Notice" and "no" fell into the previous one): start set by hand
    t_chip, t_light, t_brain = 1.0, 2.1, 2.94
    t_only, t_control, t_you, t_through, t_measure, t_react = 4.0, 5.48, 7.35, 8.23, 9.23, 10.1
    PX, PY, PS = -166, 176, 2.6
    monitor = (f'<g filter="url(#{p}-shadow)"><rect x="1110" y="290" width="420" height="310" rx="24" fill="#15133a" stroke="{LILAC}" stroke-width="8"/>'
           f'<rect x="1290" y="600" width="60" height="70" fill="#2a2870"/><rect x="1220" y="664" width="200" height="22" rx="11" fill="#2a2870"/></g>'
           f'<rect x="1130" y="310" width="380" height="270" rx="12" fill="#0b1c40"/>'
           + "".join(f'<rect id="{p}-mc{k}" x="1146" y="{326 + k * 52}" width="128" height="40" rx="8" fill="{c}"/>' for k, c in enumerate(["#7b2a6c", "#25427a", "#6b5b2a"]))
           + "".join(f'<rect x="1296" y="{340 + k * 46}" width="196" height="8" rx="4" fill="#4a4ab0"/><circle id="{p}-k{k}" cx="{1330 + k * 50}" cy="{344 + k * 46}" r="13" fill="{c}"/>' for k, c in enumerate([AMBER, CYAN, MAGENTA]))
           + f'<path id="{p}-chart" d="M1150 560 L1190 548 L1220 556 L1250 520 L1280 534 L1310 500 L1340 516 L1370 478 L1400 492 L1430 462 L1490 470" fill="none" stroke="{MINT}" stroke-width="6" stroke-linejoin="round" stroke-dasharray="420" stroke-dashoffset="420" filter="url(#{p}-glow)"/>')
    rng = random.Random(9)
    buildings, xx = "", -60
    while xx < 700:
        bw, bh = rng.randint(90, 160), rng.randint(260, 560)
        buildings += f'<rect x="{xx}" y="{950 - bh}" width="{bw}" height="{bh}" fill="{rng.choice(["#24205e", "#2c2470", "#1e1a52"])}"/>'
        buildings += "".join(f'<rect x="{xx + 16 + c * 30}" y="{950 - bh + 24 + r * 40}" width="14" height="18" fill="#ffd27a" opacity="{rng.choice([.15, .5, .85])}"/>'
                           for r in range(bh // 40 - 1) for c in range((bw - 24) // 30))
        xx += bw + rng.randint(10, 30)
    # standing person with the phone (hand at chest) and the big phone beside them as a magnifier of what they see
    GX, GS = 330, 1.22
    phone_x, phone_y = GX + 112.7 * GS, 950 - 382.6 * GS
    # the man at the desk, facing left (toward the monitor), behind the desktop
    OX, OS = 1730, 1.3
    SKIN_O, SHIRT_O = OPERATOR[SKIN], OPERATOR[WORK["torso"]]
    blinds = "".join(f'<rect x="1560" y="{292 + k * 22}" width="250" height="12" rx="3" fill="#8d7bff" opacity=".22"/>' for k in range(7))
    typing_hand = lambda x, y, n: (f'<g transform="translate({x} {y})"><g id="{p}-typing{n}"><rect x="2" y="-9" width="26" height="15" rx="6" fill="{SHIRT_O}"/>'
                              f'<path d="M -14,0 C -14,-8 -2,-11 8,-8 L 8,5 C -2,7 -14,6 -14,0 Z" fill="{SKIN_O}"/>'
                              f'<path d="M -12,2 L -4,3 M -11,-3 L -4,-3" stroke="#140a2e" stroke-opacity=".3" stroke-width="1.4" stroke-linecap="round"/></g></g>')
    svg = f"""
<g id="{p}-street" opacity="0">
 {floor(950)}
 <g opacity=".85">{buildings}</g>
 <g transform="translate(150 950)"><rect x="-8" y="-720" width="16" height="720" fill="#3a3a6a"/><path d="M 0 -716 Q 50 -756 104 -724" stroke="#3a3a6a" stroke-width="14" fill="none"/>
  <ellipse cx="108" cy="-712" rx="28" ry="12" fill="#ffd27a"/><polygon points="88,-706 128,-706 320,-30 -100,-30" fill="#ffd27a" opacity=".07"/>
  <ellipse cx="108" cy="-520" rx="160" ry="260" fill="#ffd27a" opacity=".1" filter="url(#{p}-blur40)"/></g>
 <ellipse cx="{GX + 20}" cy="952" rx="190" ry="16" fill="#ffd27a" opacity=".08"/>
 <g transform="translate({GX} 950) scale({GS})">{human(p + "g", "home", "standing", phone=True)}</g>
 <polygon points="{phone_x + 8:.0f},{phone_y - 10:.0f} 700,262 700,738 {phone_x + 8:.0f},{phone_y + 12:.0f}" fill="#3be0ff" opacity=".07"/>
 <path d="M {phone_x + 8:.0f} {phone_y - 10:.0f} L 700 262 M {phone_x + 8:.0f} {phone_y + 12:.0f} L 700 738" stroke="#3be0ff" stroke-width="2" stroke-dasharray="6 8" opacity=".45"/>
</g>
<g id="{p}-office" opacity="0">
 <rect x="1040" y="230" width="1000" height="720" rx="34" fill="#1b1450" opacity=".9"/>
 <rect x="1040" y="230" width="1000" height="720" rx="34" fill="none" stroke="#4a3aa0" stroke-width="4" opacity=".7"/>
 <rect x="1546" y="278" width="278" height="170" rx="10" fill="#0e1240" stroke="#4a3aa0" stroke-width="6"/>{blinds}
 <ellipse cx="1330" cy="500" rx="330" ry="250" fill="#3be0ff" opacity=".08" filter="url(#{p}-blur40)"/>
 <g transform="translate({OX} 950) scale({-OS} {OS})">{human(p + "o", "work", "sitting", colors=OPERATOR, chair=True, mood="neutral", glasses=True, glow=True, gaze=(2.6, 1.2, 1.5))}</g>
 <path d="M 1052 712 L 1960 712 L 1960 744 L 1040 744 Z" fill="#5a46b0"/>
 <rect x="1040" y="744" width="920" height="18" fill="#3a2a8c"/>
 <rect x="1430" y="762" width="520" height="188" fill="#2a1d70"/>
 <rect x="1462" y="786" width="190" height="64" rx="8" fill="none" stroke="#4a3aa0" stroke-width="4"/><rect x="1462" y="866" width="190" height="64" rx="8" fill="none" stroke="#4a3aa0" stroke-width="4"/>
 <rect x="1532" y="812" width="50" height="10" rx="5" fill="#8d7bff" opacity=".6"/><rect x="1532" y="892" width="50" height="10" rx="5" fill="#8d7bff" opacity=".6"/>
 <rect x="1070" y="762" width="24" height="188" fill="#2a1d70"/>
 <ellipse cx="1470" cy="955" rx="460" ry="20" fill="#05031a" opacity=".5"/>
 <g transform="translate(-20 34)">{monitor}</g>
 <ellipse cx="1660" cy="722" rx="140" ry="14" fill="#3be0ff" opacity=".12"/>
 <path d="M 1590 732 L 1766 732 L 1754 710 L 1602 710 Z" fill="#232060" stroke="#8d7bff" stroke-width="2.5" stroke-linejoin="round"/>
 <path d="M 1606 716 L 1750 716 M 1600 722 L 1756 722 M 1596 727 L 1760 727" stroke="#8d7bff" stroke-width="2.4" stroke-dasharray="7 4" opacity=".8"/>
 <g transform="translate(1520 714)"><path d="M -60 0 L -6 0 L -2 -8 L -56 -8 Z" fill="#eef1ff" opacity=".9"/><path d="M -58 -8 L -4 -8 L 0 -14 L -54 -14 Z" fill="#c9d0ea"/></g>
 <g transform="translate(1562 714)"><path d="M -16 0 L -14 -34 Q 0 -40 14 -34 L 16 0 Z" fill="#ff7a8a"/><path d="M 14 -28 q 14 2 10 16 q -2 6 -11 5" stroke="#ff7a8a" stroke-width="5" fill="none"/>
  <path d="M -4 -44 q -6 -10 0 -18 M 6 -44 q -6 -10 0 -18" stroke="#eef1ff" stroke-width="3" fill="none" opacity=".5"/></g>
 {typing_hand(1640, 716, 0)}{typing_hand(1708, 718, 1)}
 <path id="{p}-cable" d="M1090 500 C 1030 500 1010 520 950 520" fill="none" stroke="{AMBER}" stroke-width="8" stroke-linecap="round" stroke-dasharray="18 14" filter="url(#{p}-glow)"/>
 <path d="M{phone_x:.0f} {phone_y - 40:.0f} C 600 90 1100 80 1300 352" fill="none" stroke="{MAGENTA}" stroke-width="4" stroke-dasharray="10 12" opacity=".35"/>
 <path id="{p}-loop" d="M{phone_x:.0f} {phone_y - 40:.0f} C 600 90 1100 80 1300 352" fill="none" stroke="{MAGENTA}" stroke-width="8" stroke-linecap="round" stroke-dasharray="560 1200" stroke-dashoffset="560" opacity="0" filter="url(#{p}-glow)"/>
</g>
<g id="{p}-closeup">
{person(p + "a", PX, PY, PS, glow=p + "-glow")}
<g transform="translate({PX} {PY}) scale({PS})">
 <g id="{p}-chip" opacity="0"><rect x="186" y="18" width="30" height="18" rx="4" fill="{AMBER}" filter="url(#{p}-glow)" transform="rotate(-10 201 27)"/>
  <path d="M196 18 C 196 -10 220 -20 236 -40" fill="none" stroke="{AMBER}" stroke-width="2.5"/>
  <path id="{p}-cx" d="M178 4 L226 48 M226 4 L178 48" stroke="{RED}" stroke-width="6" stroke-linecap="round" stroke-dasharray="140" stroke-dashoffset="140"/></g>
 <g id="{p}-light" opacity="0"><path d="M150 -90 C 150 -20 170 30 178 74" fill="none" stroke="#7fb4ff" stroke-width="4" stroke-linecap="round"/>
  <circle id="{p}-lightDot" cx="178" cy="78" r="16" fill="#3b8bff" opacity=".8" filter="url(#{p}-glow)"/>
  <path id="{p}-lx" d="M154 54 L202 102 M202 54 L154 102" stroke="{RED}" stroke-width="6" stroke-linecap="round" stroke-dasharray="140" stroke-dashoffset="140"/></g>
</g></g>
<g transform="translate(820 500) scale(.62)"><g id="{p}-phone" opacity="0">{phone_mock(p, "f", ["happy", "neutral", "sad", "happy", "neutral", "sad", "happy", "neutral"], extra=SWAP.format(p=p))}</g></g>"""
    html = (text(f"{p}-t1", "No chip", "left:860px;top:250px;font-size:120px;color:#ffd98a")
            + text(f"{p}-t2", "No light in the brain", "left:840px;top:420px;font-size:92px;color:#bfd8ff")
            + text(f"{p}-t3", "JUST SOMEONE", "left:1060px;width:860px;text-align:center;top:110px;font-size:64px;color:#ffd98a", "pill2"))
    js = (f'camZ("#{p}-cam", 0, {t_only:.2f}, 1.3, 1.34, 280, 540, "none");\n'
          f'camZ("#{p}-cam", {t_only:.2f}, 1.4, 1.34, 1.0, 280, 540);\n'
          f'camZ("#{p}-cam", {t_only + 1.4:.2f}, {dur - t_only - 1.4:.2f}, 1.0, 1.02, 280, 540, "none");\n'
          + ft(f"#{p}a-eye", "{x:0}", "{x:3,duration:0.4}", 0.1)
          + f'enter("#{p}-chip", {t_chip - 0.3:.2f}, 0.25); rise("#{p}-t1 span", {t_chip - 0.3:.2f});\n'
          + ft(f"#{p}-cx", "{attr:{'stroke-dashoffset':140}}", "{attr:{'stroke-dashoffset':0},duration:0.3}", t_chip + 0.3)
          + ft(f"#{p}-chip", "{opacity:1}", "{opacity:0,duration:0.4,immediateRender:false}", t_light - 0.3)
          + f'enter("#{p}-light", {t_light - 0.2:.2f}, 0.25); rise("#{p}-t2 span", {t_light - 0.2:.2f});\n'
          + ft(f"#{p}-lightDot", "{scale:1,transformOrigin:'50% 50%'}", "{scale:1.6,transformOrigin:'50% 50%',duration:0.2,repeat:3,yoyo:true}", t_light)
          + ft(f"#{p}-lx", "{attr:{'stroke-dashoffset':140}}", "{attr:{'stroke-dashoffset':0},duration:0.3}", t_brain)
          + ft(f"#{p}-light", "{opacity:1}", "{opacity:0,duration:0.4,immediateRender:false}", t_only - 0.3)
          + vanish(f"#{p}-t1 span", t_only - 0.3) + vanish(f"#{p}-t2 span", t_only - 0.3)
          + ft(f"#{p}-closeup", "{x:0,opacity:1}", "{x:-500,opacity:0,duration:0.7,ease:'power2.in',immediateRender:false}", t_only - 0.1)
          + f'enter("#{p}-street", {t_only + 0.2:.2f}, 0.5);\n'
          + ft(f"#{p}-street", "{x:-300}", "{x:0,duration:1.1,ease:'expo.out',immediateRender:false}", t_only + 0.2)
          + f'enter("#{p}-office", {t_only:.2f}, 0.2);\n'
          + ft(f"#{p}-office", "{x:600}", "{x:0,duration:0.8,ease:'expo.out',immediateRender:false}", t_only)
          + f'enter("#{p}-phone", {t_only + 0.2:.2f}, 0.2);\n'
          + ft(f"#{p}-phone", "{y:700}", "{y:0,duration:1.0,ease:'back.out(1.3)',immediateRender:false}", t_only + 0.2)
          + f'rise("#{p}-t3 span", {4.27:.2f});\n'
          + "".join(ft(f"#{p}-k{k}", "{x:0}", "{x:%d,duration:0.6,repeat:3,yoyo:true,ease:'sine.inOut'}" % (90 - k * 70), t_control + k * 0.15) for k in range(3))
          + "".join(ft(f"#{p}-typing{n}", "{y:0}", "{y:-4,duration:0.14,repeat:%d,yoyo:true,ease:'sine.inOut'}" % (13 - n * 2), t_control - 0.2 + n * 0.07) for n in range(2))
          + mood_js(p + "o", "neutral", "happy", t_measure + 0.5, 0.35)
          + ft(f"#{p}-cable", "{attr:{'stroke-dashoffset':0}}", "{attr:{'stroke-dashoffset':128},duration:0.5,repeat:%d,ease:'none'}" % int((dur - t_control) / 0.5 - 1), t_control)
          + f'tl.set("#{p}-swap",{{x:380}},0);\n'
          + ft(f"#{p}-fc0", "{x:0}", "{x:-380,duration:0.4,ease:'power2.in'}", t_you)
          + ft(f"#{p}-swap", "{x:380}", "{x:0,duration:0.5,ease:'back.out(1.4)',immediateRender:false}", t_you + 0.25)
          + ft(f"#{p}-mc0", "{fill:'#7b2a6c'}", "{fill:'#25427a',duration:0.2,immediateRender:false}", t_you + 0.25)
          + ft(f"#{p}-fposts", "{y:0}", "{y:-380,duration:%.2f,ease:'power1.inOut'}" % (dur - t_through), t_through)
          + ft(f"#{p}-chart", "{attr:{'stroke-dashoffset':420}}", "{attr:{'stroke-dashoffset':0},duration:1.4,ease:'power1.inOut'}", t_measure)
          + f'enter("#{p}-loop", {t_measure - 0.2:.2f}, 0.1);\n'
          + ft(f"#{p}-loop", "{attr:{'stroke-dashoffset':560}}", "{attr:{'stroke-dashoffset':-1200},duration:1.1,repeat:1,ease:'none'}", t_measure - 0.2)
          + phone_gaze(p + "g") + f'tl.to("#{p}g-screen",{{attr:{{fill:"#7fb4ff"}},duration:0.2}},{t_you + 0.3:.2f});\n'
          + mood_js(p + "g", "happy", "sad", t_you + 0.5, 0.35)
          + ft(f"#{p}g-faceGlow", "{opacity:0.22}", "{opacity:0.45,duration:0.25,repeat:3,yoyo:true,immediateRender:false}", t_react - 0.3)
          + person_idle(p + "a", dur, (0.6, 3.6)) + figure_idle(p + "g", dur, (6.0, 8.8)) + figure_idle(p + "o", dur, (6.6, 9.4)))
    return composition(p, dur, svg, html, js, seed=23)


# ---------------------------------------------------------------- 8: whoever controls the screen chooses the world that reaches it
def scene8():
    i = 8; p = ID(i); dur = D(i)
    t_control, t_not, t_head, t_they, t_choose, t_world, t_reach = 0.28, 1.38, 3.14, 3.98, 4.47, 5.86, 6.35
    GX, GY, GS = 250, 860, 1.15            # person seated in the armchair (feet at GY)
    EX, EY = GX + 14 * GS, GY - 385 * GS    # eye (the front one, figure home sitting turn 30)
    HX, HY = GX + ANCHORS[("home", "sitting", 30)]["head_center"][0] * GS, GY + ANCHORS[("home", "sitting", 30)]["head_center"][1] * GS
    kinds = ["happy", "sad", "neutral", "sad", "happy", "neutral", "neutral", "happy", "sad"]
    new_kinds = ["neutral", "happy", "sad", "happy", "sad", "happy", "sad", "neutral", "happy"]
    picked = (1, 4, 8)
    grid_svg = "".join(f'<g transform="translate({1000 + (k % 3) * 300} {196 + (k // 3) * 186}) scale(.9)"><g id="{p}-g{k}">{card(t, k)}</g>'
                    f'<g id="{p}-n{k}" opacity="0">{card(new_kinds[k], k + 1)}</g></g>' for k, t in enumerate(kinds))
    flying = "".join(f'<g transform="translate({1000 + (k % 3) * 300} {273 + (k // 3) * 186})"><g id="{p}-v{n}" opacity="0"><g transform="scale(.5) translate(0 -85)">{card(new_kinds[k], k + 1)}</g></g></g>'
                  for n, k in enumerate(picked))
    extra = (f'<linearGradient id="{p}-screen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16143a"/><stop offset="1" stop-color="#0b1c40"/></linearGradient>'
             f'<linearGradient id="{p}-beam" gradientUnits="userSpaceOnUse" x1="{EX:.0f}" y1="0" x2="790" y2="0"><stop offset="0" stop-color="#3be0ff" stop-opacity=".5"/><stop offset="1" stop-color="#3be0ff" stop-opacity=".08"/></linearGradient>')
    svg = f"""
<ellipse id="{p}-bloom" cx="1300" cy="470" rx="640" ry="420" fill="#3be0ff" opacity="0" filter="url(#{p}-blur40)"/>
<polygon id="{p}-lightning" points="{EX + 14:.0f},{EY:.0f} 790,190 790,760" fill="url(#{p}-beam)" opacity="0"/>
<g filter="url(#{p}-shadow)"><rect x="760" y="150" width="1080" height="640" rx="30" fill="#15133a" stroke="{LILAC}" stroke-width="10"/></g>
<rect x="786" y="176" width="1028" height="588" rx="16" fill="url(#{p}-screen)"/>
<clipPath id="{p}-tcp"><rect x="786" y="176" width="1028" height="588" rx="16"/></clipPath>
<g clip-path="url(#{p}-tcp)"><g id="{p}-grid" opacity="0">{grid_svg}</g><rect id="{p}-flash" x="786" y="176" width="1028" height="588" fill="#eef1ff" opacity="0"/>
 <g transform="translate(1300 320)"><g id="{p}-pointer" opacity="0"><g transform="scale(1.6)"><path d="M0 0 L0 54 L16 40 L28 66 L40 60 L28 36 L50 36 Z" fill="#ffffff" stroke="#1a0f3a" stroke-width="3"/></g></g></g></g>
<rect x="1240" y="790" width="120" height="60" fill="#2a2870"/>
{floor(860, .45)}
<ellipse cx="330" cy="866" rx="300" ry="26" fill="#3a2a8c" opacity=".7"/>
<circle id="{p}-ring" cx="{HX:.0f}" cy="{HY - 8:.0f}" r="96" fill="none" stroke="{CYAN}" stroke-width="6" stroke-dasharray="16 14" opacity="0" filter="url(#{p}-glow)"/>
<g transform="translate({GX} {GY}) scale({GS})">{armchair()}{human(p + "a", "home", "sitting", mood="neutral")}</g>
{flying}"""
    html = (text(f"{p}-t1", "Whoever controls the screen", "left:0;right:0;text-align:center;top:850px;font-size:96px;color:#ffffff")
            + text(f"{p}-t2", "doesn't need to get inside your head", "left:0;right:0;text-align:center;top:960px;font-size:72px;color:#bff4ff")
            + text(f"{p}-t3", "They choose the world", "left:0;right:0;text-align:center;top:850px;font-size:96px;color:#ffd98a")
            + text(f"{p}-t4", "that reaches it", "left:0;right:0;text-align:center;top:960px;font-size:84px;color:#ffffff"))
    pointer_js = (f'tl.set("#{p}-pointer",{{x:0,y:0}},0);\n'
              + f'enter("#{p}-pointer", {t_choose - 0.3:.2f}, 0.2);\n'
              + "".join(f'tl.to("#{p}-pointer",{{x:{(k % 3) * 300 - 300 + 40},y:{(k // 3) * 186 - 124 + 60},duration:0.32,ease:"power2.inOut"}},{t_choose - 0.2 + n * 0.42:.2f});\n'
                        + ft(f"#{p}-n{k}", "{opacity:0,scale:1.15,transformOrigin:'50% 50%'}", "{opacity:1,scale:1,transformOrigin:'50% 50%',duration:0.3,ease:'back.out(2)'}", t_choose + 0.12 + n * 0.42)
                        for n, k in enumerate(picked)))
    others = ",".join(f'"#{p}-g{k}"' for k in range(9) if k not in picked)
    js = (f'camZ("#{p}-cam", 0, {t_head - 0.4:.2f}, 1.0, 1.02, {EX:.0f}, {EY:.0f}, "none");\n'
          f'camZ("#{p}-cam", {t_head - 0.4:.2f}, 0.9, 1.02, 1.035, {EX:.0f}, {EY:.0f});\n'
          f'camZ("#{p}-cam", {t_they:.2f}, 1.3, 1.035, 1.0, {EX:.0f}, {EY:.0f});\n'
          f'camZ("#{p}-cam", {t_they + 1.3:.2f}, {dur - t_they - 1.3:.2f}, 1.0, 1.05, {EX:.0f}, {EY:.0f}, "none");\n'
          + ft(f"#{p}a-eye", "{x:0}", "{x:3,duration:0.4}", 0.1)
          + f'rise("#{p}-t1 span", {t_control - 0.2:.2f});\n'
          + ft(f"#{p}-flash", "{opacity:0}", "{opacity:0.7,duration:0.08}", t_control + 0.5)
          + ft(f"#{p}-flash", "{opacity:0.7}", "{opacity:0,duration:0.5,immediateRender:false}", t_control + 0.6)
          + ft(f"#{p}-grid", "{opacity:0}", "{opacity:1,duration:0.2}", t_control + 0.55)
          + ft(f"#{p}-bloom", "{opacity:0}", "{opacity:0.2,duration:0.8}", t_control + 0.55)
          + ft(f"#{p}-grid", "{y:0}", "{y:-20,duration:%.2f,ease:'none'}" % (dur - t_control), t_control)
          + f'rise("#{p}-t2 span", {t_not:.2f});\n'
          + ft(f"#{p}-ring", "{opacity:0,scale:1.3,transformOrigin:'50% 50%'}", "{opacity:0.9,scale:1,transformOrigin:'50% 50%',duration:0.5,ease:'back.out(2)'}", t_head - 0.4)
          + ft(f"#{p}-ring", "{rotation:0,transformOrigin:'50% 50%'}", "{rotation:40,transformOrigin:'50% 50%',duration:1.4,ease:'none',immediateRender:false}", t_head - 0.4)
          + ft(f"#{p}-ring", "{opacity:0.9}", "{opacity:0,duration:0.4,immediateRender:false}", t_they - 0.2)
          + vanish(f"#{p}-t1 span", t_they - 0.25) + vanish(f"#{p}-t2 span", t_they - 0.25)
          + f'rise("#{p}-t3 span", {t_they:.2f});\n'
          + pointer_js
          + f'tl.to([{others}],{{opacity:0.25,duration:0.5}},{t_world - 0.2:.2f});\n'
          + f'rise("#{p}-t4 span", {6.09:.2f});\n'
          + ft(f"#{p}-lightning", "{opacity:0}", "{opacity:1,duration:0.6}", t_reach - 0.3)
          + "".join(ft(f"#{p}-v{n}", "{x:0,y:0,scale:1,opacity:1}",
                       "{x:%.0f,y:%.0f,scale:0.15,opacity:0,duration:0.95,repeat:1,repeatDelay:0.2,ease:'power2.in',immediateRender:false}" % (EX - (1000 + (k % 3) * 300), EY - (273 + (k // 3) * 186)),
                       t_reach - 0.2 + n * 0.25)
                    for n, k in enumerate(picked))
          + mood_js(p + "a", "neutral", "happy", t_reach + 0.7)
          + figure_idle(p + "a", dur, (2.0, 4.6, 7.4)))
    return composition(p, dur, svg, html, js, extra, seed=29)


FUNCS = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8]
SCENES = [(ID(k), f, D(k)) for k, f in enumerate(FUNCS)]
SEG_MAP = {(SCENE_KEY, k): ID(k) for k in range(len(FUNCS))}

if __name__ == "__main__":
    print(write_scenes(SCENES, HERE))
