"""Group g6: reality 2, 3, 4, 7, 8 and robot 0 to 4 in the v5 pattern.

  python3 build_g6_reality_robot1.py      # writes compositions/, index.html and timing.json in this folder
"""
import os, sys, random, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from engine import *
from art2 import fly_defs, fly_rich
from figure import figure, figure_idle, picture, orb, SKIN, HAIR, HOME, WORK, ANCHORS
from engine import composition as _engine_composition

HERE = os.path.dirname(os.path.abspath(__file__))  # after the import: engine also exports HERE (the scenes root)

MONO = "font-family:'IBM Plex Mono',monospace;font-weight:500;letter-spacing:.14em"


# ------------------------------------------------------------------ real figure (round 2)
SKINS = [SKIN, "#c68a5e", "#8d5a3a", "#e8b48a"]


def person_v(p, var="home", pose="standing", torso=None, pants=None, skin=0, hair=None, **kw):
    """figure() with clothes, skin and hair swapped by the base hex of each piece (shadow and light are neutral layers on top)."""
    v = HOME if var == "home" else WORK
    s = figure(p, var, pose, **kw)
    for old, new in ((v["torso"], torso), (v["pants"], pants), (SKIN, SKINS[skin] if skin else None), (HAIR, hair)):
        if new:
            s = s.replace(old, new)
    return s


def place(x, y, s, content, flip=False, id_=None, op=None):
    """Places art with its feet at the origin: static outer group, inner group with the id for GSAP."""
    o = f' opacity="{op}"' if op is not None else ""
    g = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">{content}</g>'
    return f'<g id="{id_}"{o}>{g}</g>' if id_ else g


# Fixed origins (figure local coordinates, turn 30) to rotate/scale body parts. A transformOrigin in % measures the group box
# in GSAP and, with the new drawing, gets the wrong box: the head vanishes when rotating and the trunk detaches when breathing.
ORIG = {"sitting": dict(nuca="-5 -345", eye="2 -388", trunk="0 -161"), "standing": dict(nuca="0 -447", eye="7 -490", trunk="3 -265")}


def life(p, dur, blinks=(2.0, 5.3, 8.8, 12.1, 16.4, 20.2), pose="standing"):
    """figure_idle with svgOrigin instead of transformOrigin (breathes, sways the head on -headW, blinks)."""
    o = ORIG[pose]
    js = figure_idle(p, dur, ())
    js = js.replace('transformOrigin:"50% 100%"', f'svgOrigin:"{o["trunk"]}"')
    for t in blinks:
        if t < dur - 0.3:
            js += f'tl.fromTo("#{p}-eye",{{scaleY:1,svgOrigin:"{o["eye"]}"}},{{scaleY:0.08,svgOrigin:"{o["eye"]}",duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t});'
    return js


# outfit variations for crowds (0 is the main person, lilac hoodie)
OUTFITS = [("home", None, None, 0, None), ("work", None, None, 1, None),
          ("home", "#38e8a8", "#3a2a5a", 2, "#241711"), ("work", "#ffb23e", "#2f3f9a", 3, "#c9a050"),
          ("home", "#ff4fa3", "#232344", 1, "#8a3a2a"), ("work", "#3be0ff", "#3a2a20", 2, "#3a2a20"),
          ("home", "#ffd23e", "#4a2a6a", 3, "#241711")]


def crowd_defs(p, s=0.15):
    """Defs #{p}-pg0..6: small standing people, feet at (0,0), each with different clothes and skin."""
    return "".join(f'<g id="{p}-pg{k}"><g transform="scale({s})">{person_v(f"{p}-pg{k}x", r[0], "standing", r[1], r[2], r[3], r[4], shadow=False)}</g></g>'
                   for k, r in enumerate(OUTFITS))


def crowd(p, cols, rows, ex, ey, cx, cy, cls="m", skip=(), seed=1, offset=True):
    """Grid of small people (feet on the line). Back row first so the front row covers it."""
    rr = random.Random(seed)
    out = []
    for j in range(rows):
        for i in range(cols):
            if (j, i) in skip:
                continue
            x = cx + (i - (cols - 1) / 2) * ex + (ex / 2 if offset and j % 2 else 0)
            out.append(f'<g transform="translate({x:.0f} {cy + (j - (rows - 1) / 2) * ey:.0f})"><use class="{cls}" href="#{p}-pg{rr.randint(1, 6)}"/></g>')
    return "".join(out)


# ------------------------------------------------------------------ shared pieces
# fingers of the sitting figure hand_l (48.9,-190.7) over the object that covers the mug built into the drawing
HAND = "".join(f'<rect x="{38 + k}" y="{-214 + k * 10}" width="26" height="11" rx="5.5" fill="{SKIN}" stroke="#6a3b26" stroke-width="1.6"/>' for k in range(3))
def cube(cx, cy, s, col_top, col_left, col_right, stroke, w=5, extra=""):
    top = f"M{cx} {cy - s} L{cx + s * 1.1} {cy - s * 0.45} L{cx} {cy + s * 0.1} L{cx - s * 1.1} {cy - s * 0.45} Z"
    left = f"M{cx - s * 1.1} {cy - s * 0.45} L{cx} {cy + s * 0.1} L{cx} {cy + s} L{cx - s * 1.1} {cy + s * 0.55} Z"
    right = f"M{cx + s * 1.1} {cy - s * 0.45} L{cx} {cy + s * 0.1} L{cx} {cy + s} L{cx + s * 1.1} {cy + s * 0.55} Z"
    return (f'<g {extra}><path d="{top}" fill="{col_top}"/><path d="{left}" fill="{col_left}"/><path d="{right}" fill="{col_right}"/>'
            f'<path d="{top} {left} {right}" fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"/></g>')


def person_dir(p, x0, y0, s, scene):
    """The person looking right. Final box x0..x0+190s, y0..y0+224s."""
    return person(p, x0 - 110 * s, y0 - 28 * s, s, glow=scene + "-glow")


def forum_window(p, w=1100, h=700, lines=9, skeleton=False):
    """Rebuilt forum window, centered at (0,0). Ids: {p}-fl (post lines), {p}-fu (user), {p}-ft (title)."""
    x0, y0 = -w / 2, -h / 2
    ls = "".join(f'<rect class="fl" x="{x0 + 70}" y="{y0 + 330 + k * 38}" width="{(w - 140) * (0.62 if k % 4 == 3 else 0.95 - (k % 3) * 0.08):.0f}" height="16" rx="8" fill="#8d7bff" opacity=".55"/>' for k in range(lines))
    sk = ls.replace('class="fl"', "") if skeleton else ""
    return (f'<g filter="url(#{p}-shadow)"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="26" fill="#14123a" stroke="{LILAC}" stroke-width="6"/></g>'
            f'<rect x="{x0}" y="{y0}" width="{w}" height="96" rx="26" fill="#221e5c"/><rect x="{x0}" y="{y0 + 60}" width="{w}" height="36" fill="#221e5c"/>'
            f'<circle cx="{x0 + 50}" cy="{y0 + 48}" r="13" fill="{RED}"/><circle cx="{x0 + 90}" cy="{y0 + 48}" r="13" fill="{AMBER}"/><circle cx="{x0 + 130}" cy="{y0 + 48}" r="13" fill="{MINT}"/>'
            f'<text x="{x0 + 190}" y="{y0 + 64}" font-family="IBM Plex Mono" font-weight="700" font-size="46" fill="#eef1f7" letter-spacing="4">LessWrong</text>'
            f'<text x="{-x0 - 50}" y="{y0 + 64}" text-anchor="end" font-family="IBM Plex Mono" font-weight="500" font-size="44" fill="{AMBER}">2010</text>'
            f'<g id="{p}-fu"><circle cx="{x0 + 110}" cy="{y0 + 170}" r="44" fill="#2a2a8c" stroke="{CYAN}" stroke-width="5"/>'
            f'<circle cx="{x0 + 110}" cy="{y0 + 158}" r="15" fill="{CYAN}"/><path d="M{x0 + 84} {y0 + 196} q26 -26 52 0" fill="{CYAN}"/>'
            f'<text x="{x0 + 180}" y="{y0 + 186}" font-family="IBM Plex Mono" font-weight="700" font-size="50" fill="{CYAN}">Roko</text></g>'
            f'<g id="{p}-ft"><text x="{x0 + 70}" y="{y0 + 290}" font-family="EB Garamond" font-weight="700" font-size="62" fill="#eef1f7">thought experiment</text></g>'
            f'<g opacity=".18">{sk}</g><g id="{p}-fl">{ls}</g>')


def basilisk(p):
    """Original creature: neon king serpent (crown of spikes, a single eye with a slit pupil, body rings behind).
    Centered at (0,0); head ~ -330..330 x -360..300, body up to ~ +-760 x 520.
    Ids: {p}-bbody (rings), {p}-bhead (head), {p}-blid1/2 (eyelids), {p}-bpupil (pupil), {p}-biris, {p}-bolho (eye group)."""
    bz = lambda t, a, b, c, d: (1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c + t ** 3 * d
    scales = "".join(f'<path d="M{bz(t, -600, -300, 300, 600) - 30:.0f} {bz(t, 760, 520, 520, 760) - 50:.0f} q30 -24 60 0" fill="none" stroke="{MAGENTA}" stroke-width="5" opacity=".6"/>'
                      for t in [0.12 + k * 0.04 for k in range(20)])
    body = (f'<g id="{p}-bbody">'
             f'<path d="M-560 820 C-600 560 -380 520 -230 360 M560 820 C600 560 380 520 230 360" fill="none" stroke="#3a0f3a" stroke-width="120" stroke-linecap="round"/>'
             f'<path d="M-560 820 C-600 560 -380 520 -230 360 M560 820 C600 560 380 520 230 360" fill="none" stroke="{MAGENTA}" stroke-width="8" stroke-dasharray="46 22" filter="url(#{p}-glow)"/>'
             f'<path d="M-600 760 C-300 520 300 520 600 760" fill="none" stroke="#2a0a2e" stroke-width="150" stroke-linecap="round"/>'
             f'<path d="M-600 760 C-300 520 300 520 600 760" fill="none" stroke="{LILAC}" stroke-width="7" stroke-dasharray="50 24" filter="url(#{p}-glow)"/>{scales}</g>')
    spikes = "".join(f'<path d="M{x - 34} {-250 + abs(x) * 0.18:.0f} L{x + dx} {-250 - h + abs(x) * 0.18:.0f} L{x + 34} {-250 + abs(x) * 0.18:.0f} Z" fill="#2a0a2e" stroke="{AMBER}" stroke-width="6" stroke-linejoin="round"/>'
                       for x, h, dx in [(-240, 90, -30), (-150, 140, -16), (-60, 190, -6), (0, 230, 0), (60, 190, 6), (150, 140, 16), (240, 90, 30)])
    head_d = "M0 -280 C150 -280 300 -200 330 -60 C350 40 260 160 150 230 C90 270 40 300 0 300 C-40 300 -90 270 -150 230 C-260 160 -350 40 -330 -60 C-300 -200 -150 -280 0 -280 Z"
    head = (f'<g id="{p}-bhead"><g filter="url(#{p}-glow)">{spikes}</g>'
           f'<path d="{head_d}" fill="url(#{p}-bpele)" stroke="{MAGENTA}" stroke-width="9" filter="url(#{p}-glow)"/>'
           f'<path d="M-250 -120 C-180 -60 -120 -70 -90 -40 M250 -120 C180 -60 120 -70 90 -40" fill="none" stroke="{MAGENTA}" stroke-width="6" opacity=".7"/>'
           f'<path d="M-200 110 Q-120 150 -60 120 M200 110 Q120 150 60 120 M-110 190 Q0 240 110 190" fill="none" stroke="{LILAC}" stroke-width="6" opacity=".7"/>'
           f'<path d="M-40 250 L-26 300 L-12 250 M40 250 L26 300 L12 250" fill="#fff" stroke="#ffd8e8" stroke-width="3"/>'
           f'<g id="{p}-bolho"><ellipse cx="0" cy="-10" rx="190" ry="120" fill="#0a0414" stroke="{AMBER}" stroke-width="7" filter="url(#{p}-glow)"/>'
           f'<clipPath id="{p}-bcp"><ellipse cx="0" cy="-10" rx="186" ry="116"/></clipPath>'
           f'<g clip-path="url(#{p}-bcp)"><g id="{p}-bgaze"><circle id="{p}-biris" cx="0" cy="-10" r="106" fill="url(#{p}-biridg)"/>'
           f'<g transform="translate(0 -10)"><ellipse id="{p}-bpupil" cx="0" cy="0" rx="20" ry="96" fill="#05020a"/></g>'
           f'<circle cx="34" cy="-52" r="16" fill="#fff" opacity=".85"/></g>'
           f'<rect id="{p}-blid1" x="-200" y="-140" width="400" height="130" fill="#2a0a2e"/><rect id="{p}-blid2" x="-200" y="-10" width="400" height="130" fill="#2a0a2e"/></g></g></g>')
    return body + head


def basilisk_defs(p):
    return (f'<radialGradient id="{p}-bpele" cx="50%" cy="35%" r="75%"><stop offset="0" stop-color="#4a1050"/><stop offset="1" stop-color="#16061e"/></radialGradient>'
            f'<radialGradient id="{p}-biridg" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffe9a0"/><stop offset=".45" stop-color="{AMBER}"/><stop offset=".8" stop-color="#ff4f7d"/><stop offset="1" stop-color="#5a0a20"/></radialGradient>'
            f'<radialGradient id="{p}-aura" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ff4fa3" stop-opacity=".45"/><stop offset="1" stop-color="#ff4fa3" stop-opacity="0"/></radialGradient>')


DARK = ("#2a0f3a", "#120828", "#05030f")

# The engine camZ does tl.set(scale z0) at time 0 on every call and GSAP compensates the svgOrigin change (smoothOrigin),
# so the second and third calls shift the camera. This version only sets the initial state on the first call
# and turns smoothOrigin off. Declared after JS_LIB in the same scope, it replaces the engine one.
CAM = r"""
  function popO(sel,t,from,dur,o){
    tl.fromTo(sel,{scale:from||0.3,opacity:0,svgOrigin:o},{scale:1,opacity:1,svgOrigin:o,duration:dur||0.7,ease:"elastic.out(1,0.45)",immediateRender:false},t);
    tl.set(sel,{opacity:0},0);
  }
  function camZ(sel,t0,dur,z0,z1,ox,oy,ease){
    camZ.f=camZ.f||{};
    if(!camZ.f[sel]){camZ.f[sel]=1;tl.set(sel,{scale:z0,svgOrigin:ox+" "+oy,smoothOrigin:false},0);}
    var o={l:Math.log(z0)};
    tl.to(o,{l:Math.log(z1),duration:dur,ease:ease||"power3.inOut",onUpdate:function(){gsap.set(sel,{scale:Math.exp(o.l),svgOrigin:ox+" "+oy,smoothOrigin:false});},immediateRender:false},t0);
  }
"""


def composition(i, dur, svg, html, js, extra="", **kw):
    return _engine_composition(i, dur, svg, html, CAM + js, extra, **kw)


# ------------------------------------------------------------------ reality 2: Bostrom's page
def reality_2():
    p, SC, SG = "reality_2", "reality", 2
    start, dur = seg(SC, SG)
    t_cinema, t_but, t_year, t_nick, t_arg, t_bed, t_sleep = 0.92, 2.15, 2.58, 4.78, 6.52, 7.5, 8.04
    rr = random.Random(4)
    rain = "".join(f'<rect x="{-520 + c * 44}" y="{-600 + r * 52 + rr.randint(0, 40)}" width="18" height="{rr.choice((22, 30, 38))}" rx="4" fill="{MINT}" opacity="{rr.uniform(.2, .9):.2f}"/>'
                    for c in range(24) for r in range(24) if rr.random() < 0.55)
    row = lambda y, xs: "".join(f'<rect x="{x - 64}" y="{y}" width="128" height="150" rx="34" fill="#0c0a26" stroke="#2a2878" stroke-width="4"/>' for x in xs)
    # the person in the cinema seat, popcorn in hand (figure local coordinates, feet at 0)
    seat = ('<rect x="-128" y="-372" width="74" height="250" rx="30" fill="#3a1048" stroke="#7a2a6a" stroke-width="5"/>'
                '<rect x="-118" y="-168" width="236" height="52" rx="22" fill="#3a1048" stroke="#7a2a6a" stroke-width="5"/>')
    popcorn = ('<path d="M -14 -262 L 70 -262 L 60 -170 L -4 -170 Z" fill="#fff4e8" stroke="#e8d8c8" stroke-width="2"/>'
              '<path d="M 2 -262 L 10 -170 M 28 -262 L 28 -170 M 54 -262 L 46 -170" stroke="#ff4f7d" stroke-width="10"/>'
              + "".join(f'<circle cx="{cx}" cy="{cy}" r="13" fill="#fff3c4" stroke="#e8c070" stroke-width="2"/>' for cx, cy in ((-6, -266), (14, -276), (36, -272), (60, -264), (26, -288), (4, -284), (48, -282)))
              + HAND)
    viewer = place(290, 1040, 0.95, seat + figure(p + "s", "home", "sitting", chair=False, shadow=False) + popcorn)
    seats = f'{row(880, range(40, 1960, 150))}{viewer}{row(960, range(-30, 1990, 160))}'
    # abstract lines on the page (page 700 px wide; image 1600 x 2264 -> factor .4375)
    f = 700 / 1600
    marks = "".join(f'<rect class="mark" x="{326 * f:.1f}" y="{(648 + k * 41.2) * f:.1f}" width="{(1366 - 326) * f:.1f}" height="{38 * f:.1f}" rx="3" fill="{AMBER}" opacity=".42"/>' for k in range(8))
    extra = (f'<radialGradient id="{p}-cone" cx="50%" cy="100%" r="100%"><stop offset="0" stop-color="#bff4ff" stop-opacity=".35"/><stop offset="1" stop-color="#bff4ff" stop-opacity="0"/></radialGradient>'
             f'<clipPath id="{p}-screen"><rect x="-540" y="-290" width="1080" height="580" rx="18"/></clipPath>'
             f'<radialGradient id="{p}-moon" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff3c4"/><stop offset="1" stop-color="#ffd27a"/></radialGradient>')
    svg = f"""
<g id="{p}-cinema">
 <polygon points="960,1080 420,300 1500,300" fill="url(#{p}-cone)" opacity=".5"/>
 <g transform="translate(960 380)"><g filter="url(#{p}-shadow)"><rect x="-560" y="-310" width="1120" height="620" rx="26" fill="#0a0820" stroke="{LILAC}" stroke-width="8"/></g>
  <g id="{p}-screenGlow" opacity=".45"><g clip-path="url(#{p}-screen)"><rect x="-540" y="-290" width="1080" height="580" fill="#04140e"/><g id="{p}-rain">{rain}</g></g></g></g>
 <g id="{p}-seats">{seats}</g>
</g>
<g transform="translate(270 75) rotate(-2.5) scale(.9)"><g id="{p}-page" opacity="0">
 <g filter="url(#{p}-shadow)"><rect x="-6" y="-6" width="712" height="1003" rx="8" fill="#fffaf0"/></g>
 <image href="assets/docs/bostrom2003.png" x="0" y="0" width="700" height="990.5"/>
 <g id="{p}-marks" style="mix-blend-mode:multiply">{marks}</g>
</g></g>
<g id="{p}-pw" opacity="0">
 <ellipse cx="1640" cy="1012" rx="320" ry="24" fill="#05031a" opacity=".55"/>
 <rect x="1650" y="500" width="230" height="240" rx="12" fill="#0a0e36" stroke="{LILAC}" stroke-width="7"/>
 <g id="{p}-moon" opacity="0"><circle cx="1790" cy="590" r="44" fill="url(#{p}-moon)" filter="url(#{p}-glow)"/><circle cx="1812" cy="578" r="39" fill="#0a0e36"/>
  <circle cx="1700" cy="560" r="4" fill="#fff"/><circle cx="1840" cy="690" r="3" fill="#fff"/><circle cx="1720" cy="680" r="3" fill="#fff"/></g>
 <path d="M1765 500 V740 M1650 620 H1880" stroke="{LILAC}" stroke-width="6"/>
 <rect x="1836" y="752" width="56" height="258" rx="16" fill="#2a1d70" stroke="{LILAC}" stroke-width="5"/>
 <rect x="1462" y="928" width="420" height="34" rx="10" fill="#1c1450" stroke="{LILAC}" stroke-width="4"/>
 <path d="M1490 960 V1006 M1860 960 V1006" stroke="{LILAC}" stroke-width="8" stroke-linecap="round"/>
 <rect x="1478" y="866" width="400" height="66" rx="20" fill="#5a5ab0"/>
 <ellipse cx="1800" cy="852" rx="56" ry="24" fill="#cfd0ff"/>
 <path d="M1600 862 H1876 V934 H1600 Q1578 900 1600 862 Z" fill="#3a3a9a"/><path d="M1620 876 H1860" stroke="#5a5ab0" stroke-width="5"/>
 {place(1560, 1008, 0.95, figure(p + "q", "home", "sitting", chair=False, shadow=False), flip=True)}
</g>
"""
    html = (text(f"{p}-t1", "2003", "left:1140px;top:90px;font-size:210px;color:#ffd98a", height="1.15em") +
            text(f"{p}-t2", "NICK BOSTROM", f"left:1150px;top:360px;font-size:66px;color:#bff4ff;{MONO}"))
    js = f"""
  camZ("#{p}-cam", 0, {t_but:.2f}, 1.0, 1.08, 960, 380, "power1.inOut");
  tl.fromTo("#{p}-screenGlow",{{opacity:.45}},{{opacity:1,duration:0.5}},{t_cinema - 0.3:.2f});
  tl.fromTo("#{p}-rain",{{y:-260}},{{y:200,duration:{t_but + 0.6:.2f},ease:"none"}},0);
  tl.fromTo("#{p}-cinema",{{opacity:1,scale:1,svgOrigin:"960 540"}},{{opacity:0,scale:.7,svgOrigin:"960 540",duration:0.9,ease:"power3.in",immediateRender:false}},{t_but - 0.1:.2f});
  tl.fromTo("#{p}-page",{{opacity:0,y:700,rotation:-8}},{{opacity:1,y:0,rotation:0,duration:1.1,ease:"expo.out"}},{t_but:.2f});
  rise("#{p}-t1 span", {t_year:.2f}, 0.9);
  rise("#{p}-t2 span", {t_nick:.2f});
  tl.fromTo("#{p}-marks .mark",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,transformOrigin:"0% 50%",duration:0.22,ease:"power2.inOut",stagger:0.12}},{t_arg:.2f});
  camZ("#{p}-cam", {t_arg - 0.2:.2f}, 1.0, 1.08, 1.75, 600, 380, "power3.inOut");
  vanish("#{p}-t1", {t_arg - 0.2:.2f}, 0.3); vanish("#{p}-t2", {t_arg - 0.2:.2f}, 0.3);
  camZ("#{p}-cam", {t_bed - 0.1:.2f}, 1.1, 1.75, 1.0, 600, 380, "power3.inOut");
  tl.to(["#{p}-t1","#{p}-t2"],{{opacity:1,duration:0.4}},{t_bed + 0.3:.2f});
  tl.set("#{p}s-head",{{rotation:-7,svgOrigin:"-5 -345"}},0);
  tl.to("#{p}s-head",{{svgOrigin:"-5 -345",rotation:-12,duration:0.5,ease:"back.out(2)"}},{t_cinema:.2f});
  tl.fromTo("#{p}s-eye",{{scale:1,svgOrigin:"2 -388"}},{{scale:1.35,svgOrigin:"2 -388",duration:0.3,repeat:1,yoyo:true,immediateRender:false}},{t_cinema + 0.1:.2f});
  tl.fromTo("#{p}-pw",{{opacity:0,y:60}},{{opacity:1,y:0,duration:0.8,ease:"expo.out"}},{t_bed:.2f});
  enter("#{p}-moon", {t_sleep - 0.2:.2f}, 0.5);
  tl.fromTo("#{p}q-eye",{{scale:1,svgOrigin:"2 -388"}},{{scale:1.7,svgOrigin:"2 -388",duration:0.35,ease:"back.out(3)"}},{t_sleep:.2f});
  tl.fromTo("#{p}q",{{x:0}},{{x:4,duration:0.06,repeat:11,yoyo:true,ease:"none",immediateRender:false}},{t_sleep + 0.3:.2f});
""" + life(p + "s", t_but, (1.2, 3.4), "sitting") + life(p + "q", dur, (), "sitting")
    return composition(p, dur, svg, html, js, extra, seed=6)


# ------------------------------------------------------------------ reality 3: the minds multiply
def sim_def(p, s=80, k=2.6):
    """Simulations: glass cubes with a person (ancestor) inside. Defs #{p}-sim1..6 centered at (0,0); needs crowd_defs."""
    return "".join(f'<g id="{p}-sim{j}">{cube(0, 0, s, "#4fd8ff1c", "#2a2a8c55", "#17175e55", CYAN, 4)}'
                   f'<g transform="translate(0 {s * 0.5:.0f}) scale({k / 2.6:.3f})"><use href="#{p}-pg{j}"/></g></g>' for j in range(1, 7))


def planet(p, cx=960, cy=1500, r=900, n_towers=17, seed=2):
    rr = random.Random(seed)
    arc = lambda x: cy - math.sqrt(max(0, r * r - (x - cx) ** 2))
    towers = ""
    for k in range(n_towers):
        x = cx - 560 + k * 70 + rr.randint(-10, 10)
        h = rr.randint(50, 190) if abs(x - cx) > 60 else 0
        if h:
            yb = arc(x) + 12
            windows = "".join(f'<rect x="{x - 8 + (j % 2) * 12}" y="{yb - h + 14 + (j // 2) * 26:.0f}" width="7" height="11" fill="{AMBER}" opacity=".8"/>' for j in range(2 * max(1, h // 30)))
            towers += f'<g class="tower"><rect x="{x - 22}" y="{yb - h:.0f}" width="44" height="{h}" rx="4" fill="#2a2878" stroke="{LILAC}" stroke-width="3"/>{windows}</g>'
    lights = "".join(f'<circle class="lamp" cx="{x:.0f}" cy="{y:.0f}" r="{rr.uniform(3, 7):.1f}" fill="{rr.choice((AMBER, "#ffe9a0", CYAN))}"/>'
                    for x, y in [(cx + rr.uniform(-800, 800), cy - rr.uniform(500, 880)) for _ in range(260)] + [(cx + rr.uniform(-880, 880), cy + rr.uniform(-500, 880)) for _ in range(520)] if (x - cx) ** 2 + (y - cy) ** 2 < (r - 20) ** 2)
    return (f'<circle cx="{cx}" cy="{cy}" r="{r + 40}" fill="{CYAN}" opacity=".08" filter="url(#{p}-blur40)"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{p}-planet)" stroke="{CYAN}" stroke-width="6"/>'
            f'<g id="{p}-lights">{lights}</g><g id="{p}-towers">{towers}</g>'
            f'<g transform="translate({cx} {arc(cx)})"><g id="{p}-towerC"><path d="M-30 12 L-14 -110 L14 -110 L30 12 Z" fill="#2a2878" stroke="{CYAN}" stroke-width="4"/><circle cx="0" cy="-118" r="12" fill="{CYAN}" filter="url(#{p}-glow)"/></g></g>')


def reality_3():
    p, SC, SG = "reality_3", "reality", 3
    start, dur = seg(SC, SG)
    t_civ, t_sim, t_minds, t_fly, t_scale, t_power, t_millions, t_simulation, t_ancestors = (2.18, 5.54, 6.11, 8.93, 10.53,
                                                                     12.35, 13.61, 14.34, 16.33)
    extra = (crowd_defs(p) + fly_defs(p + "M") + sim_def(p) +
             f'<radialGradient id="{p}-planet" cx="45%" cy="20%" r="70%"><stop offset="0" stop-color="#3a3aa8"/><stop offset=".6" stop-color="#1c1a60"/><stop offset="1" stop-color="#0a0a2a"/></radialGradient>')
    # field of simulations (shows up on the zoom out)
    field, rc = [], random.Random(31)
    for gy in range(-760, 2300, 250):
        for gx in range(-1700, 3700, 260):
            x, y = gx + (gy // 250 % 2) * 130, gy
            if (x - 960) ** 2 + (y - 1500) ** 2 < 1050 ** 2 or (abs(x - 960) < 620 and -60 < y < 640):
                continue
            field.append(f'<g transform="translate({x} {y})"><use class="cell" href="#{p}-sim{rc.randint(1, 6)}"/></g>')
    svg = f"""
<g id="{p}-field">{''.join(field)}</g>
<g id="{p}-planet">{planet(p)}</g>
<g transform="translate(960 600)"><g id="{p}-beam" opacity="0"><rect x="-9" y="-130" width="18" height="130" fill="{CYAN}" opacity=".85" filter="url(#{p}-glow)"/></g></g>
<g transform="translate(960 330)"><g id="{p}-cube" opacity="0"><rect x="-200" y="-200" width="400" height="400" fill="none"/>
 {cube(0, 0, 150, "#1e3a8add", "#2a2a8cee", "#17175eee", CYAN, 6, f'filter="url(#{p}-glow)"')}</g></g>
<g id="{p}-pw" opacity="0">{person_dir(p + "s", 885, 235, 0.88, p)}</g>
<g transform="translate(470 380)"><g id="{p}-cubeFly" opacity="0"><rect x="-150" y="-150" width="300" height="300" fill="none"/>
 {cube(0, 0, 112, "#ffb23e1c", "#5a3a1a55", "#3a2a1055", AMBER, 5, f'filter="url(#{p}-glow)"')}
 <g transform="translate(6 -6) scale(.6)">{fly_rich(p + "-fly", p + "M")}</g></g></g>
<g transform="translate(1450 380)"><g id="{p}-cubeCrowd" opacity="0"><rect x="-150" y="-150" width="300" height="300" fill="none"/>
 {cube(0, 0, 112, "#4fd8ff1c", "#2a2a8c55", "#17175e55", CYAN, 5, f'filter="url(#{p}-glow)"')}
 <g id="{p}-crowdGrid"><g transform="scale(.55)">{crowd(p, 5, 2, 80, 91, 0, 27, seed=3)}</g></g></g></g>
"""
    html = (text(f"{p}-t1", "MILLIONS OF SIMULATIONS", "left:0;right:0;text-align:center;top:50px;font-size:104px;color:#eef1f7") +
            f'<div id="{p}-n" class="pill2" style="left:0;right:0;text-align:center;top:690px;font-size:92px;color:#ffd98a;opacity:0;font-weight:700">1</div>')
    js = f"""
  camZ("#{p}-cam", 0, {t_civ:.2f}, 1.25, 1.0, 960, 560, "power2.out");
  tl.fromTo("#{p}-towers .tower",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,transformOrigin:"50% 100%",duration:0.5,ease:"back.out(2)",stagger:0.11}},{max(0.4, t_civ - 1.6):.2f});
  tl.fromTo("#{p}-lights .lamp",{{opacity:0}},{{opacity:1,duration:0.2,stagger:{{amount:{t_civ + 1.2:.2f},from:"random"}}}},0.2);
  tl.fromTo("#{p}-towerC",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,transformOrigin:"50% 100%",duration:0.7,ease:"back.out(2)"}},{t_civ + 0.6:.2f});
  enter("#{p}-beam", {t_sim:.2f}, 0.2);
  tl.fromTo("#{p}-beam",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,transformOrigin:"50% 100%",duration:0.4,ease:"power2.out",immediateRender:false}},{t_sim:.2f});
  pop("#{p}-cube", {t_sim + 0.2:.2f}, 0.4, 0.8);
  pop("#{p}-pw", {t_minds:.2f}, 0.4, 0.8);
  pop("#{p}-cubeFly", {t_fly - 0.2:.2f}, 0.4, 0.8);
  tl.fromTo("#{p}-fly-wings",{{scaleY:1,transformOrigin:"50% 100%"}},{{scaleY:0.6,transformOrigin:"50% 100%",duration:0.05,repeat:11,yoyo:true,ease:"none",immediateRender:false}},{t_fly + 0.4:.2f});
  popO("#{p}-cubeCrowd", {t_scale - 0.4:.2f}, 0.4, 0.8, "0 0");
  camZ("#{p}-cam", {t_scale:.2f}, 2.6, 1.0, 0.36, 960, 420, "power3.inOut");
  tl.fromTo("#{p}-field .cell",{{scale:0,opacity:0,svgOrigin:"0 0"}},{{scale:1,opacity:1,svgOrigin:"0 0",duration:0.4,ease:"back.out(2)",stagger:{{amount:2.4,from:"center"}}}},{t_scale + 0.3:.2f});
  rise("#{p}-t1 span", {t_millions:.2f}, 0.9);
  enter("#{p}-n", {t_millions:.2f}, 0.3);
  count_up("{p}-n", {t_millions:.2f}, {t_ancestors - t_millions + 0.6:.2f}, 1, 1000000, function(v){{return Math.round(v).toLocaleString("en-US");}});
  tl.fromTo("#{p}-field",{{opacity:1}},{{opacity:0.55,duration:0.25,repeat:5,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_simulation:.2f});
  camZ("#{p}-cam", {t_scale + 2.6:.2f}, {dur - t_scale - 2.6:.2f}, 0.36, 0.33, 960, 420, "none");
""" + person_idle(p + "s", dur, (7.0, 10.0, 14.8))
    return composition(p, dur, svg, html, js, extra, seed=11)


# ------------------------------------------------------------------ reality 4: the trilemma
def reality_4():
    p, SC, SG = "reality_4", "reality", 4
    start, dur = seg(SC, SG)
    t_at_least, t_three, t_one, t_q1, t_point, t_two, t_not, t_three2, t_q3, t_minds, t_yours, t_simulation = (
        0.7, 2.02, 4.23, 4.42, 7.65, 8.68, 10.57, 14.56, 15.02, 16.35, 17.59, 19.72)
    # captions taken from the speech (the script visual items paraphrase and the user rejects text that differs from the narration)
    items = ["Almost no civilization ever gets that far", "Those that do have no interest in running these simulations", "Almost all minds like yours are inside a simulation"]
    rr = random.Random(7)
    CX, CY, R = (400, 960, 1520), 540, 236
    extra = (crowd_defs(p) + sim_def(p, 46, 1.5) +
             "".join(f'<clipPath id="{p}-cp{k}"><circle cx="{CX[k]}" cy="{CY}" r="{R - 6}"/></clipPath>' for k in range(3)) +
             f'<radialGradient id="{p}-planet" cx="45%" cy="25%" r="70%"><stop offset="0" stop-color="#3a3aa8"/><stop offset="1" stop-color="#0e0c3a"/></radialGradient>'
             f'<radialGradient id="{p}-inside" cx="50%" cy="40%" r="60%"><stop offset="0" stop-color="#2a1e70"/><stop offset="1" stop-color="#0c0a26"/></radialGradient>')
    stars = lambda k: "".join(f'<circle cx="{CX[k] + rr.uniform(-220, 220):.0f}" cy="{CY + rr.uniform(-220, 120):.0f}" r="{rr.uniform(1.5, 3.5):.1f}" fill="#fff" opacity=".7"/>' for _ in range(24))
    # 1: planet with a city that goes dark
    c1 = CX[0]
    towers1 = "".join(f'<rect class="t1" x="{c1 - 120 + j * 34}" y="{CY - 40 - h}" width="26" height="{h}" rx="3" fill="#2a2878" stroke="{LILAC}" stroke-width="3"/>'
                      for j, h in enumerate((50, 90, 64, 120, 80, 100, 56, 74)))
    lights1 = "".join(f'<circle class="l1" cx="{c1 + rr.uniform(-150, 150):.0f}" cy="{CY + rr.uniform(-20, 140):.0f}" r="5" fill="{AMBER}"/>' for _ in range(40))
    p1 = (f'<circle cx="{c1}" cy="{CY + 150}" r="190" fill="url(#{p}-planet)" stroke="{CYAN}" stroke-width="5"/>'
          f'<g id="{p}-towers1">{towers1}</g><g id="{p}-lights1">{lights1}</g>')
    # 2: server that doesn't run simulations
    c2 = CX[1]
    drawers = "".join(f'<rect x="{c2 - 100}" y="{CY - 70 + j * 58}" width="200" height="46" rx="8" fill="#1c1a52" stroke="{LILAC}" stroke-width="3"/>'
                  f'<circle class="led" cx="{c2 + 74}" cy="{CY - 47 + j * 58}" r="8" fill="{MINT}"/>' for j in range(5))
    sims2 = "".join(f'<use class="s2" href="#{p}-sim{j}" x="{c2 + dx}" y="{CY - 140 + dy}"/>' for j, (dx, dy) in zip((2, 4, 5), ((-110, 10), (0, -10), (110, 10))))
    p2 = (f'<rect x="{c2 - 120}" y="{CY - 90}" width="240" height="320" rx="14" fill="#0e0c2a" stroke="{CYAN}" stroke-width="5"/>{drawers}'
          f'<g id="{p}-sims2">{sims2}</g>')
    # 3: crowd of people (minds like yours) and you in front, the main person
    c3 = CX[2]
    g3 = crowd(p, 9, 4, 58, 96, c3, CY + 40, cls="m3", skip=((3, 3), (3, 4), (2, 4), (2, 3)), seed=5)
    you = (f'<g transform="translate({c3} {CY + 20})"><g id="{p}-you"><ellipse cx="0" cy="40" rx="78" ry="120" fill="{AMBER}" opacity=".32" filter="url(#{p}-blur6)"/>'
            f'{place(0, 120, 0.22, figure(p + "v", "home", "standing", shadow=False))}</g></g>')
    p3 = f'<g id="{p}-g3">{g3}</g>{you}'
    panels = ""
    for k, content in enumerate((p1, p2, p3)):
        panels += (f'<g id="{p}-panel{k}" opacity="0"><circle cx="{CX[k]}" cy="{CY}" r="{R + 30}" fill="{CYAN}" opacity=".06" filter="url(#{p}-blur6)"/>'
                    f'<circle cx="{CX[k]}" cy="{CY}" r="{R}" fill="url(#{p}-inside)"/>'
                    f'<g clip-path="url(#{p}-cp{k})">{stars(k)}{content}</g>'
                    f'<circle id="{p}-ring{k}" cx="{CX[k]}" cy="{CY}" r="{R}" fill="none" stroke="{CYAN}" stroke-width="8" filter="url(#{p}-glow)"/>'
                    f'<g transform="translate({CX[k]} {CY - R - 16})"><g id="{p}-digit{k}"><circle r="56" fill="#14123a" stroke="{AMBER}" stroke-width="6"/>'
                    f'<text y="26" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="80" fill="#ffd98a">{k + 1}</text></g></g></g>')
    svg = f'<g id="{p}-pan">{panels}</g>'
    cap = "left:0;right:0;text-align:center;top:900px;font-size:76px;color:#eef1f7"
    html = (text(f"{p}-t0", "AT LEAST ONE OF THREE THINGS IS TRUE", f"left:0;right:0;text-align:center;top:60px;font-size:52px;color:#ffd98a;{MONO}") +
            text(f"{p}-c0", items[0], cap) + text(f"{p}-c1", items[1], cap.replace("font-size:76px", "font-size:62px")) + text(f"{p}-c2", items[2], cap.replace("#eef1f7", "#ffd98a").replace("font-size:76px", "font-size:62px")))
    focus = lambda t, k, d=1.1: (f'tl.to("#{p}-pan",{{x:{(1 - k) * 560},duration:{d},ease:"power3.inOut"}},{t:.2f});' +
                                "".join(f'tl.to("#{p}-panel{j}",{{opacity:{1 if j == k else 0.28},duration:{d * 0.7:.2f}}},{t:.2f});' for j in range(3)))
    leave = lambda sel, t: f'tl.to("{sel} span",{{yPercent:-125,opacity:0,duration:0.45,ease:"power2.in"}},{t:.2f});'
    js = f"""
  camZ("#{p}-cam", 0, {t_one:.2f}, 1.06, 1.0, 960, 540, "power1.out");
  rise("#{p}-t0 span", {t_at_least:.2f}, 0.8);
  [0,1,2].forEach(function(k){{popO("#{p}-panel"+k, {t_at_least + 0.2:.2f}+k*0.25, 0.4, 0.8, {list(CX)}[k]+" {CY}");}});
  [0,1,2].forEach(function(k){{tl.fromTo("#{p}-digit"+k,{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,transformOrigin:"50% 50%",duration:0.6,ease:"elastic.out(1,0.45)",immediateRender:false}},{t_three - 0.3:.2f}+k*0.25);}});
  {leave(f"#{p}-t0", t_one - 0.3)}
  camZ("#{p}-cam", {t_one:.2f}, 1.1, 1.0, 1.32, 960, 540);
  {focus(t_one, 0)}
  rise("#{p}-c0 span", {t_q1:.2f});
  tl.to("#{p}-lights1 .l1",{{opacity:0,duration:0.15,stagger:{{amount:1.0,from:"random"}}}},{t_point - 0.6:.2f});
  tl.to("#{p}-towers1 .t1",{{scaleY:0,transformOrigin:"50% 100%",duration:0.4,ease:"power2.in",stagger:0.08}},{t_point - 0.2:.2f});
  {leave(f"#{p}-c0", t_two - 0.3)}
  {focus(t_two, 1)}
  rise("#{p}-c1 span", {t_two + 0.6:.2f});
  tl.fromTo("#{p}-sims2 .s2",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,transformOrigin:"50% 50%",duration:0.5,ease:"back.out(2)",stagger:0.15,immediateRender:false}},{t_two + 0.4:.2f});
  tl.to("#{p}-sims2 .s2",{{scale:0,opacity:0,transformOrigin:"50% 50%",duration:0.35,ease:"back.in(2)",stagger:0.12}},{t_not:.2f});
  tl.to("#{p}-panel1 .led",{{attr:{{fill:"#3a2a4a"}},duration:0.15,stagger:0.1}},{t_not + 0.2:.2f});
  {leave(f"#{p}-c1", t_three2 - 0.3)}
  {focus(t_three2, 2)}
  rise("#{p}-c2 span", {t_q3:.2f});
  tl.fromTo("#{p}-g3 .m3",{{scale:0,svgOrigin:"0 0"}},{{scale:1,svgOrigin:"0 0",duration:0.3,ease:"back.out(2)",stagger:{{amount:1.0,from:"center"}},immediateRender:false}},{t_minds - 0.3:.2f});
  tl.fromTo("#{p}-you",{{scale:0,svgOrigin:"0 40"}},{{scale:1.6,svgOrigin:"0 40",duration:0.6,ease:"elastic.out(1,0.45)"}},{t_yours - 0.1:.2f});
  tl.fromTo("#{p}-you",{{scale:1.6}},{{scale:1.25,duration:0.4,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_yours + 0.6:.2f});
  camZ("#{p}-cam", {t_simulation - 0.3:.2f}, 1.2, 1.32, 1.0, 960, 540);
  tl.to("#{p}-pan",{{x:0,duration:1.2,ease:"power3.inOut"}},{t_simulation - 0.3:.2f});
  tl.to(["#{p}-panel0","#{p}-panel1"],{{opacity:0.5,duration:0.8}},{t_simulation - 0.3:.2f});
  tl.to("#{p}-ring2",{{attr:{{stroke:"#ffb23e"}},duration:0.5}},{t_simulation:.2f});
""" + life(p + "v", dur, (17.0, 19.4))
    return composition(p, dur, svg, html, js, extra, seed=12)


# ------------------------------------------------------------------ reality 7: the argument doesn't prove
def monitor(p, cx, cy):
    """Computer with a brain (the consciousness it would produce) on the screen. Box ~ cx-230..cx+230, cy-170..cy+238."""
    traces = "".join(f'<path d="M{cx + a} {cy + b} h{c} v{d}" fill="none" stroke="{CYAN}" stroke-width="3" opacity=".6"/><circle cx="{cx + a + c}" cy="{cy + b + d}" r="5" fill="{CYAN}"/>'
                      for a, b, c, d in ((-196, -110, 60, 30), (-196, 40, 50, -24), (196, -96, -58, 26), (196, 50, -46, -30), (-120, 96, 0, -20), (110, 96, 0, -24)))
    return (f'<g filter="url(#{p}-shadow)"><rect x="{cx - 230}" y="{cy - 170}" width="460" height="300" rx="22" fill="#14123a" stroke="{LILAC}" stroke-width="7"/></g>'
            f'<rect x="{cx - 206}" y="{cy - 146}" width="412" height="252" rx="10" fill="#08142a"/>'
            f'<clipPath id="{p}-screenClip"><rect x="{cx - 206}" y="{cy - 146}" width="412" height="252" rx="10"/></clipPath>'
            f'<g id="{p}-screen" opacity=".25" clip-path="url(#{p}-screenClip)">{traces}'
            f'<g transform="translate({cx} {cy - 34}) scale(1.3) translate(-192 -95)">{brain_side(p + "c")}</g></g>'
            f'<path d="M{cx - 40} {cy + 130} L{cx - 60} {cy + 220} L{cx + 60} {cy + 220} L{cx + 40} {cy + 130} Z" fill="#221e5c" stroke="{LILAC}" stroke-width="5"/>'
            f'<rect x="{cx - 140}" y="{cy + 216}" width="280" height="22" rx="11" fill="#221e5c" stroke="{LILAC}" stroke-width="5"/>')


def living_room(p):
    """Living room with life pictures on the wall, couch and lamp (the life that may be simulated)."""
    return (f'<rect x="-100" y="-100" width="2120" height="960" fill="#1a1046" opacity=".55"/>'
            f'<rect x="-100" y="860" width="2120" height="320" fill="#150d3a"/><path d="M-100 860 H2020" stroke="{LILAC}" stroke-width="6" opacity=".7"/>'
            f'<ellipse cx="1000" cy="950" rx="560" ry="62" fill="#3a1d7a" stroke="{LILAC}" stroke-width="4" opacity=".9"/>'
            f'<rect x="150" y="640" width="500" height="160" rx="44" fill="#4a2378"/><rect x="170" y="760" width="460" height="130" rx="28" fill="#5a2a8a"/>'
            f'<rect x="200" y="740" width="200" height="46" rx="20" fill="#6a3aa0"/><rect x="410" y="740" width="200" height="46" rx="20" fill="#6a3aa0"/>'
            f'<rect x="120" y="700" width="86" height="200" rx="34" fill="#4a2378"/><rect x="594" y="700" width="86" height="200" rx="34" fill="#4a2378"/>'
            f'<path d="M190 900 V930 M610 900 V930" stroke="#2a1450" stroke-width="12" stroke-linecap="round"/>'
            + picture(f"{p}-picA", "family", 330, 360, .9, -2) + picture(f"{p}-picB", "beach", 640, 330, .8, 3) + picture(f"{p}-picC", "dog", 1390, 340, .9, 2) +
            f'<polygon points="1660,540 1560,900 1840,900 1760,540" fill="{AMBER}" opacity=".08"/>'
            f'<path d="M1710 540 V912" stroke="#c9b8ff" stroke-width="8"/><rect x="1650" y="904" width="120" height="16" rx="8" fill="#c9b8ff"/>'
            f'<path d="M1650 540 L1676 460 L1744 460 L1770 540 Z" fill="#ffd27a" stroke="{AMBER}" stroke-width="4"/>')


def sim_grid(p):
    """Simulation grid over the room: floor in perspective and gridded walls."""
    vx, vy = 960, 560
    k = (860 - vy) / (1180 - vy)  # floor lines start at the baseboard (y 860), not at the vanishing point behind the person
    ls = [f'<line class="gridline" x1="{vx + (x - vx) * k:.0f}" y1="860" x2="{x}" y2="1180" stroke="{CYAN}" stroke-width="3"/>' for x in range(-1400, 3400, 240)]
    ls += [f'<line class="gridline" x1="-100" y1="{y}" x2="2020" y2="{y}" stroke="{CYAN}" stroke-width="3"/>' for y in (880, 920, 980, 1060)]
    ls += [f'<line class="gridline" x1="{x}" y1="-100" x2="{x}" y2="860" stroke="{CYAN}" stroke-width="2.5"/>' for x in range(0, 1960, 160)]
    ls += [f'<line class="gridline" x1="-100" y1="{y}" x2="2020" y2="{y}" stroke="{CYAN}" stroke-width="2.5"/>' for y in range(60, 860, 160)]
    return f'<g opacity=".6" filter="url(#{p}-glow)">{"".join(ls)}</g>'


def reality_7():
    p, SC, SG = "reality_7", "reality", 7
    start, dur = seg(SC, SG)
    t_at, t_not, t_prove, t_simulation, t_depends, t_bet, t_computer, t_conscious, t_nobody, t_knows, t_possible = (
        0.35, 2.86, 4.12, 5.55, 6.84, 7.95, 9.93, 12.22, 13.66, 14.41, 15.45)
    extra = f'<radialGradient id="{p}-coin" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#ffe9a0"/><stop offset="1" stop-color="#d98a1e"/></radialGradient>'
    # mug held by the handle in the standing figure hand_l (57.9,-227.4): handle before the body (the hand covers it), mug body after
    mug = ('<path d="M 92 -246 q 22 0 20 18 q -2 14 -20 12" stroke="#fff4e8" stroke-width="8" fill="none"/>'
              '<rect x="48" y="-258" width="46" height="56" rx="9" fill="#fff4e8" stroke="#d8c8b0" stroke-width="3"/>'
              '<rect x="48" y="-236" width="46" height="10" fill="#ff4fa3" opacity=".8"/>'
              '<path d="M 62 -270 q -8 -12 0 -24 M 80 -270 q -8 -12 0 -24" stroke="#d9d0ff" stroke-width="4" fill="none" stroke-linecap="round" opacity=".7"/>')
    a1 = (f'<g id="{p}-room">{living_room(p)}{place(1000, 930, 0.82, mug + figure(p + "s", "home", "standing"))}</g>'
          f'<g id="{p}-grid" opacity="0">{sim_grid(p)}</g>'
          f'<g id="{p}-box" opacity="0" filter="url(#{p}-glow)"><path d="M960 120 L1440 360 L1440 800 L960 1010 L480 800 L480 360 Z M480 360 L960 580 L1440 360 M960 580 L960 1010" fill="none" stroke="{CYAN}" stroke-width="10" stroke-linejoin="round" stroke-dasharray="40 26"/></g>'
          f'<rect id="{p}-stripe" x="-200" y="-200" width="2320" height="420" fill="#0b0a24" opacity="0"/>')
    a2 = (f'<ellipse cx="640" cy="905" rx="380" ry="28" fill="#05031a" opacity=".5"/>'
          f'<g transform="translate(640 560) scale(1.35)"><g id="{p}-monitor">{monitor(p, 0, 0)}</g></g>'
          f'<g id="{p}-brainGlow" opacity="0"><circle cx="640" cy="514" r="150" fill="{MAGENTA}" opacity=".35" filter="url(#{p}-blur40)"/></g>'
          f'<path id="{p}-cable" d="M955 600 C1080 700 1220 660 1330 540" fill="none" stroke="{CYAN}" stroke-width="8" stroke-dasharray="26 18" filter="url(#{p}-glow)" opacity="0"/>'
          f'<g transform="translate(1440 470) scale(1.3)"><g id="{p}-coin" opacity="0"><circle r="88" fill="url(#{p}-coin)" stroke="#fff3c4" stroke-width="6"/><circle r="64" fill="none" stroke="#b56a10" stroke-width="5"/>'
          f'<text y="26" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="80" fill="#8a4a08">?</text></g></g>'
          f'<ellipse cx="1730" cy="1004" rx="150" ry="16" fill="#05031a" opacity=".55"/>'
          f'<g id="{p}-rw">{place(1730, 1000, 0.8, figure(p + "r", "home", "standing", shadow=False), flip=True)}</g>')
    svg = f'<g id="{p}-a1">{a1}</g><g id="{p}-a2" opacity="0">{a2}</g>'
    html = (text(f"{p}-t1", "DOESN'T PROVE", "left:0;right:0;text-align:center;top:20px;font-size:170px;color:#ff4f7d") +
            text(f"{p}-t2", "CONSCIOUSNESS", f"left:240px;width:800px;text-align:center;top:190px;font-size:64px;color:#ff9bd0;{MONO}"))
    js = f"""
  camZ("#{p}-cam", 0, {t_not + 0.4:.2f}, 1.7, 1.0, 1000, 470, "power2.inOut");
  tl.fromTo("#{p}s-head",{{rotation:0,svgOrigin:"0 -447"}},{{rotation:-9,svgOrigin:"0 -447",duration:0.5,ease:"back.out(2)"}},{t_at:.2f});
  tl.fromTo("#{p}s-eye",{{scale:1,svgOrigin:"7 -490"}},{{scale:1.4,svgOrigin:"7 -490",duration:0.3,repeat:1,yoyo:true,immediateRender:false}},{t_at + 0.1:.2f});
  tl.to("#{p}-room",{{opacity:0.55,duration:0.5}},{t_not:.2f});
  enter("#{p}-grid", {t_not:.2f}, 0.3);
  tl.fromTo("#{p}-grid .gridline",{{opacity:0}},{{opacity:1,duration:0.2,stagger:{{amount:0.6,from:"center"}}}},{t_not:.2f});
  enter("#{p}-box", {t_not + 0.2:.2f}, 0.4);
  tl.fromTo("#{p}-stripe",{{opacity:0}},{{opacity:0.94,duration:0.3,immediateRender:false}},{t_prove - 0.2:.2f});
  rise("#{p}-t1 span", {t_prove - 0.1:.2f}, 0.8);
  tl.fromTo(["#{p}-box","#{p}-grid"],{{opacity:1}},{{opacity:0.2,duration:0.1,repeat:7,yoyo:true,ease:"none",immediateRender:false}},{t_simulation:.2f});
  tl.to("#{p}-t1 span",{{yPercent:-125,opacity:0,duration:0.5,ease:"power2.in"}},{t_depends - 0.4:.2f});
  tl.to("#{p}-a1",{{y:-1100,opacity:0,duration:1.0,ease:"power3.inOut"}},{t_depends - 0.2:.2f});
  tl.fromTo("#{p}-a2",{{y:1100,opacity:1}},{{y:0,opacity:1,duration:1.0,ease:"power3.inOut",immediateRender:false}},{t_depends - 0.2:.2f});
  tl.set("#{p}-a2",{{opacity:0}},0);
  enter("#{p}-cable", {t_bet - 0.2:.2f}, 0.3);
  tl.fromTo("#{p}-cable",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-220}},duration:{t_nobody - t_bet:.2f},ease:"none",immediateRender:false}},{t_bet:.2f});
  pop("#{p}-coin", {t_bet:.2f}, 0.3, 0.6);
  tl.fromTo("#{p}-coin",{{scaleX:1,transformOrigin:"50% 50%"}},{{scaleX:-1,transformOrigin:"50% 50%",duration:0.3,repeat:{int((t_nobody - t_bet - 0.9) / 0.3)},yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_bet + 0.6:.2f});
  tl.fromTo("#{p}-screen",{{opacity:.25}},{{opacity:1,duration:0.4}},{t_computer:.2f});
  tl.fromTo("#{p}-monitor",{{scale:1,transformOrigin:"50% 100%"}},{{scale:1.06,transformOrigin:"50% 100%",duration:0.2,repeat:1,yoyo:true,immediateRender:false}},{t_computer:.2f});
  enter("#{p}-brainGlow", {t_conscious - 0.3:.2f}, 0.5);
  rise("#{p}-t2 span", {t_conscious:.2f});
  tl.fromTo("#{p}-brainGlow",{{opacity:1}},{{opacity:0.4,duration:0.35,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_conscious + 0.5:.2f});
  tl.to("#{p}-coin",{{scaleX:1.3,scaleY:1.3,transformOrigin:"50% 50%",duration:0.7,ease:"elastic.out(1,0.45)"}},{t_nobody + 0.05:.2f});
  tl.to("#{p}-coin",{{rotation:-8,transformOrigin:"50% 50%",duration:0.3,repeat:5,yoyo:true,ease:"sine.inOut"}},{t_knows:.2f});
  tl.to("#{p}-cable",{{opacity:0.25,duration:0.12,repeat:5,yoyo:true,ease:"none"}},{t_knows:.2f});
  tl.to("#{p}-screen",{{opacity:0.5,duration:0.3,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_possible - 0.4:.2f});
  camZ("#{p}-cam", {t_depends + 0.8:.2f}, {dur - t_depends - 0.8:.2f}, 1.0, 1.08, 1000, 600, "none");
  tl.fromTo("#{p}r-eye",{{x:0}},{{x:3,duration:0.3}},{t_computer:.2f});
  tl.fromTo("#{p}r-head",{{rotation:0,svgOrigin:"0 -447"}},{{rotation:-12,svgOrigin:"0 -447",duration:0.45,ease:"back.out(2)",immediateRender:false}},{t_nobody:.2f});
  tl.fromTo("#{p}r-body",{{scaleY:1,scaleX:1,svgOrigin:"0 0"}},{{scaleY:0.96,scaleX:1.03,svgOrigin:"0 0",duration:0.15,repeat:1,yoyo:true,immediateRender:false}},{t_knows:.2f});
  tl.fromTo("#{p}r-arm",{{rotation:0,svgOrigin:"43 -412"}},{{rotation:-22,svgOrigin:"43 -412",duration:0.3,repeat:1,yoyo:true,repeatDelay:0.6,ease:"power2.out",immediateRender:false}},{t_knows:.2f});
""" + life(p + "s", t_depends, (1.5, 4.2)) + life(p + "r", dur, (8.0, 11.2, 15.0))
    return composition(p, dur, svg, html, js, extra, seed=13)


# ------------------------------------------------------------------ reality 8: the size of the universe
def phone(p, cards=6):
    colors = ["#2b2a80", "#7b2a6c", "#25427a", "#6b5b2a", "#2a6a6a"]
    cs = "".join(f'<g transform="translate(0 {k * 190})"><rect x="-150" y="-330" width="300" height="170" rx="20" fill="{colors[k % 5]}"/>'
                 f'<circle cx="-100" cy="-290" r="22" fill="#eef1ff" opacity=".85"/><rect x="-66" y="-304" width="150" height="12" rx="6" fill="#eef1ff" opacity=".7"/>'
                 f'<rect x="-130" y="-244" width="260" height="56" rx="12" fill="#000" opacity=".22"/><circle cx="-84" cy="-218" r="14" fill="#ffd23e"/></g>' for k in range(cards))
    return (f'<rect x="-200" y="-400" width="400" height="800" rx="54" fill="#15133a" stroke="{LILAC}" stroke-width="8"/><rect x="-172" y="-364" width="344" height="728" rx="26" fill="#0e0c26"/>'
            f'<clipPath id="{p}-phoneClip"><rect x="-172" y="-364" width="344" height="728" rx="26"/></clipPath><g clip-path="url(#{p}-phoneClip)"><g id="{p}-posts">{cs}</g></g>')


ARMCHAIR = ('<rect x="-150" y="-410" width="88" height="290" rx="36" fill="#6a2a6a" stroke="#ff4fa3" stroke-width="4"/>'
            '<rect x="-140" y="-178" width="270" height="64" rx="26" fill="#6a2a6a" stroke="#ff4fa3" stroke-width="4"/>'
            '<path d="M -110 -114 L -116 0 M 100 -114 L 106 0" stroke="#ff4fa3" stroke-width="8" stroke-linecap="round"/>')
# phone in the sitting figure hand_l, covering the mug built into the drawing, and the screen light on the face (head_center -5,-386)
PHONE_HAND = ('<linearGradient id="@P@-lg" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#bff4ff" stop-opacity=".9"/><stop offset="1" stop-color="#bff4ff" stop-opacity="0"/></linearGradient>'
           '<polygon id="@P@-light" points="12,-262 42,-266 64,-378 -24,-372" fill="url(#@P@-lg)" opacity=".3" filter="url(#@C@-blur6)"/>'
           '<g transform="rotate(-10 27 -218)"><rect x="2" y="-268" width="50" height="96" rx="10" fill="#15133a" stroke="#8d7bff" stroke-width="4"/>'
           '<rect x="8" y="-260" width="38" height="78" rx="5" fill="#3be0ff"/><rect x="12" y="-252" width="30" height="16" rx="3" fill="#eef1ff" opacity=".7"/>'
           '<rect x="12" y="-230" width="30" height="16" rx="3" fill="#2b2a80" opacity=".6"/></g>' + HAND)


def reality_8():
    p, SC, SG = "reality_8", "reality", 8
    start, dur = seg(SC, SG)
    t_does, t_shows, t_ctrl, t_all, t_perceive, t_know, t_same, t_face, t_size, t_universe = (
        0.93, 2.93, 4.54, 5.5, 6.31, 8.44, 9.4, 10.73, 12.09, 12.73)
    rr = random.Random(8)
    HX, HY = 1000, 560  # scene center (the person inside the cube)
    # spiral galaxy of minds and stars around
    gal = []
    for i in range(900):
        arm = i % 3
        r = 1500 + (i / 900) ** 0.8 * 4600
        a = arm * 2.094 + r / 1500 + rr.uniform(-0.35, 0.35)
        x, y = HX + r * math.cos(a), HY + 0.45 * r * math.sin(a)
        if (i // 3) % 3 == 0:  # heads on the three arms
            gal.append(f'<use href="#{p}-pg{rr.randint(1, 6)}" transform="translate({x:.0f} {y:.0f}) scale({0.4 + r / 9000 + rr.uniform(0, .35):.2f})"/>')
        else:
            gal.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr.uniform(6, 26):.0f}" fill="{rr.choice((CYAN, LILAC, "#fff", MAGENTA))}" opacity="{rr.uniform(.35, .9):.2f}"/>')
    extra = crowd_defs(p) + f'<radialGradient id="{p}-core" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffd8f0" stop-opacity=".9"/><stop offset=".3" stop-color="#ff8ad0" stop-opacity=".35"/><stop offset="1" stop-color="#ff8ad0" stop-opacity="0"/></radialGradient>'
    svg = f"""
<g id="{p}-galaxy" opacity="0"><ellipse cx="{HX}" cy="{HY}" rx="3200" ry="1500" fill="url(#{p}-core)"/>{''.join(gal)}</g>
<g transform="translate({HX} {HY})"><g id="{p}-cube" opacity="0"><rect x="-460" y="-460" width="920" height="920" fill="none"/>
 {cube(0, 60, 400, "#4fd8ff14", "#2a2a8c40", "#17175e40", "none", 0)}
 <g id="{p}-walls" opacity="0">{cube(0, 60, 400, "#ff4fa330", "#8d7bff3a", "#3be0ff2c", "none", 0)}</g></g></g>
<g id="{p}-proj" opacity="0"><g transform="translate(770 655) skewY(26.57)">{picture(p + "-picFamily", "family", 0, 0, .78)}</g>
 <g transform="translate(1235 655) skewY(-26.57)">{picture(p + "-picCar", "car", 0, 0, .78)}</g></g>
<g id="{p}-pw">{place(1000, 955, 0.95, ARMCHAIR + figure(p + "s", "home", "sitting", chair=False) + PHONE_HAND.replace("@P@", p + "s").replace("@C@", p))}</g>
<g transform="translate({HX} {HY})"><g id="{p}-cubeFront" opacity="0"><rect x="-460" y="-460" width="920" height="920" fill="none"/>
 <g filter="url(#{p}-glow)" fill="none" stroke="{CYAN}" stroke-linejoin="round"><path d="M0 -340 L440 -120 L440 280 L0 460 L-440 280 L-440 -120 Z" stroke-width="8"/>
 <path d="M-440 -120 L0 100 L440 -120 M0 100 V460" stroke-width="5" opacity=".28"/></g></g></g>
<path id="{p}-link" d="M462 560 C 500 520 520 470 560 446" fill="none" stroke="{CYAN}" stroke-width="7" stroke-dasharray="20 14" filter="url(#{p}-glow)" opacity="0"/>
<g transform="translate(1340 300)"><g id="{p}-q" opacity="0"><text y="40" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="200" fill="{AMBER}" filter="url(#{p}-glow)">?</text></g></g>
<g transform="translate(330 560) scale(.62)"><g id="{p}-phone" opacity="0">{phone(p)}</g></g>
<g transform="translate({HX} {HY})"><g id="{p}-here" opacity="0"><circle r="620" fill="none" stroke="{AMBER}" stroke-width="44" filter="url(#{p}-glow)"/></g></g>
"""
    bands = f'<div id="{p}-bands" style="position:absolute;left:0;top:0;width:1920px;height:1080px;opacity:0;background:linear-gradient(#0b0a24f0 0,#0b0a24c0 15%,transparent 26%,transparent 74%,#0b0a24c0 84%,#0b0a24f0 100%)"></div>'
    html = (bands + text(f"{p}-t1", "The same question", "left:0;right:0;text-align:center;top:40px;font-size:110px;color:#eef1f7") +
            text(f"{p}-t3", "FACEBOOK", f"left:130px;width:400px;text-align:center;top:830px;font-size:48px;color:#bff4ff;{MONO}") +
            text(f"{p}-t2", "the size of the universe", "left:0;right:0;text-align:center;top:900px;font-size:110px;color:#ffd98a"))
    js = f"""
  camZ("#{p}-cam", 0, {t_ctrl:.2f}, 1.25, 1.0, 1000, 470, "power2.inOut");
  tl.set("#{p}s-head",{{rotation:12,svgOrigin:"-5 -345"}},0);
  tl.fromTo("#{p}s-light",{{opacity:.15}},{{opacity:.5,duration:0.25,repeat:{int(dur / 0.5)},yoyo:true,ease:"sine.inOut"}},0);
  tl.to("#{p}s-head",{{svgOrigin:"-5 -345",rotation:0,duration:0.5,ease:"back.out(2)"}},{t_shows:.2f});
  enter("#{p}-proj", {t_ctrl + 0.2:.2f}, 0.4);
  tl.fromTo("#{p}-proj",{{opacity:1}},{{opacity:0.4,duration:0.22,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_all:.2f});
  pop("#{p}-cube, #{p}-cubeFront", {t_does:.2f}, 1.4, 0.9);
  enter("#{p}-walls", {t_ctrl:.2f}, 0.4);
  tl.fromTo("#{p}-walls",{{opacity:1}},{{opacity:0.35,duration:0.22,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_all:.2f});
  tl.to("#{p}s-eye",{{x:-3,duration:0.25,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_perceive:.2f});
  pop("#{p}-q", {t_know:.2f}, 0.3, 0.8);
  rise("#{p}-t1 span", {t_same:.2f}, 0.8);
  pop("#{p}-phone", {t_face - 0.2:.2f}, 0.4, 0.8);
  enter("#{p}-link", {t_face + 0.2:.2f}, 0.3); rise("#{p}-t3 span", {t_face:.2f});
  vanish("#{p}-link", {t_size:.2f}, 0.5); vanish("#{p}-t3", {t_size:.2f}, 0.5);
  tl.fromTo("#{p}-posts",{{y:0}},{{y:-570,duration:{dur - t_face:.2f},ease:"none"}},{t_face:.2f});
  vanish("#{p}-q", {t_size - 0.3:.2f}, 0.3);
  enter("#{p}-galaxy", {t_size + 0.3:.2f}, 0.9); enter("#{p}-bands", {t_size + 0.3:.2f}, 0.9);
  enter("#{p}-here", {t_size + 0.8:.2f}, 0.6);
  camZ("#{p}-cam", {t_size - 0.4:.2f}, {dur - t_size:.2f}, 1.0, 0.22, {HX}, {HY}, "power3.inOut");
  vanish("#{p}-phone", {t_size:.2f}, 0.35);
  rise("#{p}-t2 span", {t_universe - 0.3:.2f}, 0.9);
""" + life(p + "s", dur, (1.4, 3.6, 7.8, 11.0), "sitting")
    return composition(p, dur, svg, html, js, extra, seed=15)


# ------------------------------------------------------------------ robot 0: the strangest story
def robot_0():
    p, SC, SG = "robot_0", "robot", 0
    start, dur = seg(SC, SG)
    t_story, t_strangest = 0.49, 1.48
    extra = basilisk_defs(p)
    rp = random.Random(12)
    buildings = ""
    for k, (x0, w, top) in enumerate(((800, 150, 800), (960, 120, 860), (1090, 170, 770), (1270, 130, 840), (1410, 190, 790), (1610, 140, 850), (1760, 200, 780))):
        windows = "".join(f'<rect x="{x0 + 18 + c * 34}" y="{top + 24 + r * 44}" width="16" height="22" rx="2" fill="{AMBER}" opacity="{rp.choice((0, 0, .25, .8))}"/>'
                      for c in range(int((w - 30) // 34)) for r in range(int((990 - top - 40) // 44)))
        buildings += f'<rect x="{x0}" y="{top}" width="{w}" height="{1000 - top}" fill="#140c34" stroke="#2a2470" stroke-width="4"/>{windows}'
    svg = f"""
<g transform="translate(1460 640) scale(.9)"><g id="{p}-bas" opacity="0">{basilisk(p)}</g></g>
<rect x="0" y="0" width="1920" height="1080" fill="url(#{p}-vig)" opacity=".45"/>
{buildings}
<rect x="-100" y="990" width="2120" height="200" fill="#100a2c"/><path d="M-100 990 H2020" stroke="{LILAC}" stroke-width="5" opacity=".6"/>
<path d="M120 1040 H260 M420 1040 H560 M720 1040 H860 M1020 1040 H1160 M1320 1040 H1460 M1620 1040 H1760" stroke="#3a2a6a" stroke-width="8"/>
<polygon points="420,384 250,994 760,994 470,384" fill="{AMBER}" opacity=".13"/>
<path d="M300 994 V350 Q300 330 320 330 H440" fill="none" stroke="#3a3a7a" stroke-width="14" stroke-linecap="round"/>
<path d="M404 344 H476 L466 384 H414 Z" fill="#2a2a5a" stroke="{LILAC}" stroke-width="4"/><ellipse cx="440" cy="386" rx="30" ry="8" fill="#ffe9a0" filter="url(#{p}-glow)"/>
<ellipse cx="580" cy="994" rx="170" ry="16" fill="#05031a" opacity=".6"/>
<g id="{p}-pw">{place(560, 990, 0.78, figure(p + "s", "home", "standing", shadow=False))}</g>
"""
    html = text(f"{p}-t1", "The strangest story", "left:0;right:0;text-align:center;top:60px;font-size:124px;color:#eef1f7")
    js = f"""
  camZ("#{p}-cam", 0, {dur:.2f}, 1.0, 1.12, 700, 620, "power1.inOut");
  rise("#{p}-t1 span", {t_story - 0.1:.2f}, 0.8);
  tl.fromTo("#{p}-bas",{{opacity:0.14}},{{opacity:0.3,duration:0.6}},0);
  tl.to("#{p}-bas",{{opacity:0.9,duration:0.6}},{t_strangest - 0.3:.2f});
  tl.fromTo("#{p}-blid1",{{y:0}},{{y:-130,duration:0.5,ease:"power2.out"}},{t_strangest:.2f});
  tl.fromTo("#{p}-blid2",{{y:0}},{{y:130,duration:0.5,ease:"power2.out"}},{t_strangest:.2f});
  tl.fromTo("#{p}-bgaze",{{x:0,y:0}},{{x:-60,y:10,duration:0.5,ease:"power2.out"}},{t_strangest + 0.5:.2f});
  tl.fromTo("#{p}s-head",{{rotation:0,svgOrigin:"0 -447"}},{{rotation:-14,svgOrigin:"0 -447",duration:0.45,ease:"back.out(2)"}},{t_strangest + 0.15:.2f});
  tl.fromTo("#{p}s-eye",{{scale:1,svgOrigin:"7 -490"}},{{scale:1.5,svgOrigin:"7 -490",duration:0.3,ease:"back.out(3)"}},{t_strangest + 0.2:.2f});
  tl.fromTo("#{p}s-body",{{scaleY:1,scaleX:1,svgOrigin:"0 0"}},{{scaleY:0.95,scaleX:1.03,svgOrigin:"0 0",duration:0.12,repeat:1,yoyo:true,immediateRender:false}},{t_strangest + 0.3:.2f});
""" + life(p + "s", dur, (0.9,))
    return composition(p, dur, svg, html, js, extra, background=("#2c1460", "#140b3a", "#06051a"), seed=21)


# ------------------------------------------------------------------ robot 1: the forum post
def robot_1():
    p, SC, SG = "robot_1", "robot", 1
    start, dur = seg(SC, SG)
    (t_year, t_forum, t_lesswrong, t_roko, t_post, t_experiment, t_imagine, t_ai, t_power, t_exist, t_it, t_punish, t_everyone, t_knew, t_help) = (
        0.22, 1.89, 3.71, 5.69, 6.45, 7.11, 8.89, 9.43,
        12.2, 13.71, 14.69, 15.4, 16.12, 17.65, 19.51)
    rr = random.Random(9)
    nodes = [(rr.uniform(80, 1840), rr.uniform(80, 1000)) for _ in range(40)]
    network = "".join(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="{LILAC}" stroke-width="2" opacity=".35"/>'
                   for i, a in enumerate(nodes) for b in nodes[i + 1:] if math.dist(a, b) < 260)
    network += "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="6" fill="{CYAN}" opacity=".6"/>' for x, y in nodes)
    PX, PY, PS = (240, 600, 960, 1320, 1680), 1050, 0.4
    WHO = (1, 2, 0, 3, 4)  # outfits: the main person in the middle, different figures around
    HY = PY - 600 * PS  # head height (checked in the snapshot)
    def one(k, x):
        r = OUTFITS[WHO[k]]
        body = person_v(f"{p}p{k}", r[0], "standing", r[1], r[2], r[3], r[4])
        return (f'<g id="{p}-g{k}" opacity="0">{place(x, PY, PS, body, flip=k > 2)}'
                f'<g id="{p}-r{k}" opacity="0"><circle cx="{x}" cy="{HY:.0f}" r="50" fill="{RED}" opacity=".6" filter="url(#{p}-blur6)"/></g>'
                f'<g id="{p}-k{k}" opacity="0"><circle cx="{x}" cy="{HY:.0f}" r="46" fill="{CYAN}" opacity=".3" filter="url(#{p}-blur6)"/></g></g>')
    people = "".join(one(k, x) for k, x in enumerate(PX))
    rays = "".join(f'<line id="{p}-ray{k}" x1="960" y1="470" x2="{x}" y2="{HY - 20:.0f}" stroke="{RED}" stroke-width="10" stroke-linecap="round" filter="url(#{p}-glow)" opacity="0"/>' for k, x in enumerate(PX))
    rings = (f'<circle r="300" fill="url(#{p}-aura)"/>'
             f'<g id="{p}-ring1"><circle r="250" fill="none" stroke="{LILAC}" stroke-width="6" stroke-dasharray="120 40" filter="url(#{p}-glow)"/></g>'
             f'<g id="{p}-ring2"><circle r="200" fill="none" stroke="{CYAN}" stroke-width="10" stroke-dasharray="30 26" filter="url(#{p}-glow)"/></g>'
             f'<circle id="{p}-ringC" r="160" fill="none" stroke="{AMBER}" stroke-width="12" stroke-dasharray="1006" stroke-dashoffset="1006" transform="rotate(-90)" filter="url(#{p}-glow)"/>'
             f'<circle r="120" fill="#140a2a" stroke="{MAGENTA}" stroke-width="8"/>'
             f'<ellipse cx="0" cy="0" rx="90" ry="58" fill="#0a0414" stroke="{AMBER}" stroke-width="5"/>'
             f'<circle id="{p}-iris" r="44" fill="url(#{p}-biridg)"/><g id="{p}-pupG"><ellipse cx="0" cy="0" rx="10" ry="40" fill="#05020a"/></g>')
    extra = basilisk_defs(p) + f'<clipPath id="{p}-ftc"><rect x="-480" y="-130" width="960" height="90"/></clipPath>'
    window = forum_window(p, skeleton=True).replace(f'<g id="{p}-ft">', f'<g clip-path="url(#{p}-ftc)"><g id="{p}-ft">').replace("thought experiment</text></g>", "thought experiment</text></g></g>")
    svg = f"""
<g id="{p}-network" opacity="0">{network}</g>
<g transform="translate(960 560)"><g id="{p}-window" opacity="0">{window}</g></g>
<g id="{p}-a2" opacity="0">
 {rays}
 <g transform="translate(960 470)"><g id="{p}-ai">{rings}</g></g>
 {people}
</g>
"""
    html = (text(f"{p}-t1", "ARTIFICIAL INTELLIGENCE FROM THE FUTURE", f"left:0;right:0;text-align:center;top:40px;font-size:54px;color:#bff4ff;{MONO}") +
            text(f"{p}-t2", "punish", "left:0;right:0;text-align:center;top:30px;font-size:130px;color:#ff4f7d"))
    js = f"""
  camZ("#{p}-cam", 0, {t_lesswrong:.2f}, 1.12, 1.0, 960, 560, "power1.out");
  enter("#{p}-network", 0.1, 0.8);
  pop("#{p}-window", 0.3, 0.3, 0.9);
  camZ("#{p}-cam", {t_lesswrong - 0.1:.2f}, 0.9, 1.0, 1.35, 700, 240);
  tl.fromTo("#{p}-fu",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,transformOrigin:"50% 50%",duration:0.6,ease:"elastic.out(1,0.45)"}},{t_roko - 0.2:.2f});
  camZ("#{p}-cam", {t_post - 0.2:.2f}, 1.0, 1.35, 1.12, 960, 560);
  tl.fromTo("#{p}-fl .fl",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,transformOrigin:"0% 50%",duration:0.25,stagger:0.12}},{t_post:.2f});
  tl.fromTo("#{p}-ft",{{y:90}},{{y:0,duration:0.75,ease:"expo.out"}},{t_experiment - 0.1:.2f});
  camZ("#{p}-cam", {t_imagine - 0.2:.2f}, 1.0, 1.12, 4.0, 960, 700, "power3.in");
  vanish("#{p}-window", {t_imagine + 0.5:.2f}, 0.3); vanish("#{p}-network", {t_imagine + 0.4:.2f}, 0.3);
  tl.set("#{p}-cam",{{scale:1,svgOrigin:"960 540",smoothOrigin:false}},{t_imagine + 0.81:.2f});
  enter("#{p}-a2", {t_imagine + 0.7:.2f}, 0.3);
  tl.fromTo("#{p}-ai",{{scale:0.2,transformOrigin:"50% 50%"}},{{scale:0.85,transformOrigin:"50% 50%",duration:0.9,ease:"elastic.out(1,0.5)",immediateRender:false}},{t_ai - 0.2:.2f});
  rise("#{p}-t1 span", {t_ai:.2f});
  tl.fromTo("#{p}-ring1",{{rotation:0,transformOrigin:"50% 50%"}},{{rotation:200,transformOrigin:"50% 50%",duration:{dur - t_ai:.2f},ease:"none"}},{t_ai:.2f});
  tl.fromTo("#{p}-ring2",{{rotation:0,transformOrigin:"50% 50%"}},{{rotation:-320,transformOrigin:"50% 50%",duration:{dur - t_ai:.2f},ease:"none"}},{t_ai:.2f});
  tl.to("#{p}-ai",{{scale:1.15,duration:0.6,ease:"back.out(3)"}},{t_power:.2f});
  tl.fromTo("#{p}-ringC",{{attr:{{"stroke-dashoffset":1006}}}},{{attr:{{"stroke-dashoffset":0}},duration:{t_exist - t_power:.2f},ease:"power1.inOut"}},{t_power + 0.4:.2f});
  tl.to("#{p}-ai",{{scale:0.95,duration:0.7,ease:"power2.inOut"}},{t_it - 0.3:.2f});
  [0,1,2,3,4].forEach(function(k){{popO("#{p}-g"+k, {t_it - 0.3:.2f}+k*0.1, 0.4, 0.7, {list(PX)}[k]+" {PY}");}});
  tl.to("#{p}-t1 span",{{yPercent:-125,opacity:0,duration:0.4,ease:"power2.in"}},{t_punish - 0.5:.2f});
  rise("#{p}-t2 span", {t_punish:.2f}, 0.7);
  tl.to("#{p}-ringC",{{attr:{{stroke:"#ff4f7d"}},duration:0.3}},{t_punish:.2f});
  tl.fromTo("#{p}-pupG",{{scaleX:1,transformOrigin:"50% 50%"}},{{scaleX:0.4,transformOrigin:"50% 50%",duration:0.3}},{t_punish:.2f});
  [0,1,2,3,4].forEach(function(k){{tl.fromTo("#{p}-ray"+k,{{opacity:0}},{{opacity:0.9,duration:0.15,immediateRender:false}},{t_everyone:.2f}+k*0.08);}});
  [0,1,2,3,4].forEach(function(k){{tl.to("#{p}-ray"+k,{{opacity:0,duration:0.3}},{t_knew - 0.3:.2f});}});
  [0,1,2,3,4].forEach(function(k){{enter("#{p}-k"+k, {t_knew:.2f}+k*0.1, 0.3);}});
  [0,1,2,3,4].forEach(function(k){{enter("#{p}-r"+k, {t_help:.2f}+k*0.08, 0.3); tl.to("#{p}-ray"+k,{{opacity:0.9,duration:0.2}},{t_help + 0.3:.2f}+k*0.08);}});
  [0,1,2,3,4].forEach(function(k){{tl.fromTo("#{p}p"+k,{{x:0}},{{x:3,duration:0.05,repeat:9,yoyo:true,ease:"none",immediateRender:false}},{t_help + 0.4:.2f});}});
  camZ("#{p}-cam", {t_punish:.2f}, {dur - t_punish:.2f}, 1.0, 1.06, 960, 600, "none");
"""
    return composition(p, dur, svg, html, js, extra, background=("#2c1460", "#140b3a", "#06051a"), seed=22)


# ------------------------------------------------------------------ robot 2: and you, now, already know
def robot_2():
    p, SC, SG = "robot_2", "robot", 2
    start, dur = seg(SC, SG)
    t_you, t_now, t_already, t_knows = 0.17, 0.88, 1.77, 2.12
    extra = basilisk_defs(p)
    svg = f"""
<g transform="translate(1360 420) scale(.72)"><g id="{p}-bas"><circle r="520" fill="url(#{p}-aura)" opacity="0" id="{p}-aur"/>{basilisk(p)}</g></g>
<rect x="-100" y="1000" width="2120" height="200" fill="#0c0820"/><path d="M-100 1000 H2020" stroke="#3a2a6a" stroke-width="5"/>
<ellipse cx="900" cy="1004" rx="520" ry="22" fill="#05031a" opacity=".6"/>
<polygon id="{p}-light" points="960,600 960,770 690,640 680,540" fill="#bff4ff" opacity=".16"/>
<g id="{p}-pw">{place(640, 1000, 1.0, figure(p + "s", "home", "sitting", shadow=False))}</g>
<rect x="720" y="800" width="700" height="28" rx="10" fill="#2a1d5a" stroke="{LILAC}" stroke-width="4"/>
<path d="M760 828 V1000 M1380 828 V1000" stroke="{LILAC}" stroke-width="10" stroke-linecap="round"/>
<rect x="730" y="786" width="170" height="14" rx="5" fill="#3a3a7a" stroke="{LILAC}" stroke-width="3"/>
<path d="M1080 792 L1068 800 H1132 L1120 792 Z M1092 760 H1108 V792 H1092 Z" fill="#221e5c" stroke="{LILAC}" stroke-width="4"/>
<g filter="url(#{p}-shadow)"><rect x="930" y="560" width="340" height="210" rx="16" fill="#14123a" stroke="{LILAC}" stroke-width="6"/></g>
<rect id="{p}-screen" x="948" y="578" width="304" height="174" rx="8" fill="#0e1a3a"/>
<rect x="948" y="578" width="304" height="30" rx="8" fill="#221e5c"/><circle cx="966" cy="593" r="6" fill="{RED}"/><circle cx="986" cy="593" r="6" fill="{AMBER}"/><circle cx="1006" cy="593" r="6" fill="{MINT}"/>
<rect x="970" y="626" width="160" height="14" rx="7" fill="#eef1f7" opacity=".8"/>
{''.join(f'<rect x="970" y="{652 + k * 20}" width="{[250, 220, 236, 150][k]}" height="10" rx="5" fill="{LILAC}" opacity=".6"/>' for k in range(4))}
"""
    html = text(f"{p}-t1", "Already know", "left:110px;top:150px;font-size:140px;color:#ffd98a", height="1.2em")
    js = f"""
  camZ("#{p}-cam", 0, {t_now:.2f}, 1.2, 1.12, 960, 1080, "power2.out");
  camZ("#{p}-cam", {t_now:.2f}, {dur - t_now:.2f}, 1.12, 1.0, 960, 1080, "power2.inOut");
  tl.fromTo("#{p}-blid1",{{y:0}},{{y:-130,duration:0.45,ease:"power3.out"}},{t_now:.2f});
  tl.fromTo("#{p}-blid2",{{y:0}},{{y:130,duration:0.45,ease:"power3.out"}},{t_now:.2f});
  tl.fromTo("#{p}-aur",{{opacity:0}},{{opacity:1,duration:0.6}},{t_now:.2f});
  tl.fromTo("#{p}-bgaze",{{x:0,y:0}},{{x:-70,y:40,duration:0.5,ease:"power2.inOut"}},{t_already - 0.3:.2f});
  tl.fromTo("#{p}-bpupil",{{scaleX:1,transformOrigin:"50% 50%"}},{{scaleX:0.35,transformOrigin:"50% 50%",duration:0.3,ease:"power2.out"}},{t_knows:.2f});
  rise("#{p}-t1 span", {t_already - 0.05:.2f}, 0.7);
  tl.fromTo("#{p}s-eye",{{x:0}},{{x:3,duration:0.2}},{t_now + 0.2:.2f});
  tl.fromTo("#{p}s-head",{{rotation:0,svgOrigin:"-5 -345"}},{{rotation:-10,svgOrigin:"-5 -345",duration:0.4,ease:"back.out(2)"}},{t_now + 0.2:.2f});
  tl.fromTo("#{p}s-eye",{{scale:1,svgOrigin:"2 -388"}},{{scale:1.6,svgOrigin:"2 -388",duration:0.3,ease:"back.out(3)",immediateRender:false}},{t_knows:.2f});
  tl.fromTo("#{p}s-body",{{scaleY:1,scaleX:1,svgOrigin:"0 0"}},{{scaleY:0.94,scaleX:1.04,svgOrigin:"0 0",duration:0.12,repeat:1,yoyo:true,immediateRender:false}},{t_knows:.2f});
  tl.fromTo("#{p}-light",{{opacity:.16}},{{opacity:.3,duration:0.2,repeat:{int(dur / 0.4)},yoyo:true,ease:"sine.inOut"}},0);
""" + life(p + "s", dur, (0.7,), "sitting")
    return composition(p, dur, svg, html, js, extra, background=DARK, seed=23)


# ------------------------------------------------------------------ robot 3: Roko's Basilisk
# whoever looks at the monster of the legend: the same figure art, with a tunic from another era
LEGEND = lambda q: person_v(q, "home", "standing", "#9a6a3a", "#4a3a2a", 1, "#241711", shadow=False)


def robot_3():
    p, SC, SG = "robot_3", "robot", 3
    start, dur = seg(SC, SG)
    t_bas, t_monster, t_legend, t_kills, t_looks, t_idea, t_harm, t_known = (0.67, 3.08, 3.82, 4.48, 5.13,
                                                                    6.39, 8.07, 9.19)
    extra = basilisk_defs(p) + f'<radialGradient id="{p}-harmGrad"><stop offset="0" stop-color="{RED}" stop-opacity=".85"/><stop offset=".5" stop-color="{RED}" stop-opacity=".4"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>' + f'<filter id="{p}-stone"><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncR type="linear" slope=".7"/><feFuncG type="linear" slope=".7"/><feFuncB type="linear" slope=".75"/></feComponentTransfer></filter>'
    BX, BY, BS = 960, 560, 0.72
    ex, ey = BX, BY - 10 * BS  # eye
    svg = f"""
<g transform="translate({BX} {BY}) scale({BS})"><g id="{p}-bas"><circle r="560" fill="url(#{p}-aura)"/>{basilisk(p)}</g></g>
<polygon id="{p}-beam" points="{ex - 60},{ey} {ex + 30},{ey + 40} 300,750 292,705" fill="{AMBER}" opacity="0" filter="url(#{p}-blur6)"/>
<ellipse cx="280" cy="1030" rx="170" ry="18" fill="#05031a" opacity=".6"/><ellipse cx="1650" cy="1030" rx="170" ry="18" fill="#05031a" opacity=".6"/>
<g id="{p}-pa" opacity="0">{place(260, 1030, 0.62, LEGEND(p + "a"))}</g>
<g id="{p}-stone" opacity="0" filter="url(#{p}-stone)">{place(260, 1030, 0.62, LEGEND(p + "z"))}</g>
<g id="{p}-pb" opacity="0">{place(1660, 1030, 0.62, figure(p + "b", "home", "standing", shadow=False), flip=True)}</g>
<g id="{p}-harm" opacity="0"><circle cx="1660" cy="712" r="170" fill="url(#{p}-harmGrad)"/></g>
<g id="{p}-spark" opacity="0"><circle cx="{ex}" cy="{ey}" r="30" fill="#fff" filter="url(#{p}-glow)"/><circle cx="{ex}" cy="{ey}" r="60" fill="{MAGENTA}" opacity=".4" filter="url(#{p}-blur6)"/></g>
"""
    html = text(f"{p}-t1", "Roko's Basilisk", "left:0;right:0;text-align:center;top:30px;font-size:120px;color:#eef1f7")
    js = f"""
  tl.set("#{p}-blid1",{{y:-130}},0); tl.set("#{p}-blid2",{{y:130}},0);
  camZ("#{p}-cam", 0, 0.01, 2.6, 2.6, {ex}, {ey});
  camZ("#{p}-cam", {t_bas - 0.3:.2f}, 1.8, 2.6, 1.0, {ex}, {ey}, "power3.inOut");
  rise("#{p}-t1 span", {t_bas + 1.3:.2f}, 0.8);
  tl.fromTo("#{p}-bas",{{scaleY:1,scaleX:1,transformOrigin:"50% 100%"}},{{scaleY:1.07,scaleX:0.96,transformOrigin:"50% 100%",duration:0.25,repeat:1,yoyo:true,ease:"power2.out",immediateRender:false}},{t_monster:.2f});
  popO("#{p}-pa", {t_legend - 0.3:.2f}, 0.4, 0.7, "260 1030");
  tl.fromTo("#{p}-bgaze",{{x:0,y:0}},{{x:-70,y:30,duration:0.4,ease:"power2.inOut"}},{t_legend:.2f});
  tl.fromTo("#{p}a-eye",{{x:0}},{{x:3,duration:0.2}},{t_legend + 0.2:.2f});
  tl.fromTo("#{p}-beam",{{opacity:0}},{{opacity:0.75,duration:0.2,immediateRender:false}},{t_kills:.2f});
  tl.fromTo("#{p}-bpupil",{{scaleX:1,transformOrigin:"50% 50%"}},{{scaleX:0.3,transformOrigin:"50% 50%",duration:0.25}},{t_kills:.2f});
  tl.to("#{p}-stone",{{opacity:1,duration:0.6}},{t_looks:.2f});
  tl.to("#{p}-pa",{{opacity:0,duration:0.6}},{t_looks + 0.1:.2f});
  vanish("#{p}-beam", {t_looks + 0.7:.2f}, 0.4);
  tl.to("#{p}-t1 span",{{yPercent:-125,opacity:0,duration:0.45,ease:"power2.in"}},{t_idea - 0.3:.2f});
  popO("#{p}-pb", {t_idea - 0.4:.2f}, 0.4, 0.7, "1660 1030");
  tl.to("#{p}-bgaze",{{x:70,y:30,duration:0.4,ease:"power2.inOut"}},{t_idea - 0.2:.2f});
  enter("#{p}-spark", {t_idea:.2f}, 0.15);
  tl.fromTo("#{p}-spark",{{x:0,y:0}},{{x:{1660 - ex:.0f},y:{712 - ey:.0f},duration:{t_harm - t_idea - 0.1:.2f},ease:"sine.inOut",immediateRender:false}},{t_idea:.2f});
  vanish("#{p}-spark", {t_harm - 0.1:.2f}, 0.15);
  enter("#{p}-harm", {t_harm - 0.1:.2f}, 0.3);
  tl.fromTo("#{p}b",{{x:0}},{{x:4,duration:0.05,repeat:11,yoyo:true,ease:"none",immediateRender:false}},{t_harm:.2f});
  tl.fromTo("#{p}-harm",{{opacity:1}},{{opacity:0.5,duration:0.35,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_known:.2f});
  camZ("#{p}-cam", {t_idea - 0.4:.2f}, {dur - t_idea + 0.4:.2f}, 1.0, 1.08, 1300, 700, "power1.inOut");
  tl.fromTo("#{p}b-head",{{rotation:0,svgOrigin:"0 -447"}},{{rotation:10,svgOrigin:"0 -447",duration:0.4,ease:"power2.out"}},{t_harm:.2f});
""" + life(p + "b", dur, (9.4,)) + life(p + "a", dur, (5.0,))
    return composition(p, dur, svg, html, js, extra, background=DARK, seed=24)


# ------------------------------------------------------------------ robot 4: erased, banned, spread
def robot_4():
    p, SC, SG = "robot_4", "robot", 4
    start, dur = seg(SC, SG)
    t_founder, t_erased, t_banned, t_five, t_years, t_effect, t_backfire, t_banned2, t_spread, t_internet = (
        0.23, 1.53, 2.65, 4.36, 5.05, 5.77, 6.64, 8.07, 8.77, 11.38)
    rr = random.Random(10)
    WX, WY = 760, 540
    # network globe around (shows up on the zoom out)
    GR = 1250
    nodes = []
    for i in range(70):
        a, b = rr.uniform(0, 2 * math.pi), rr.uniform(-1, 1)
        x, y = WX + GR * math.cos(a) * math.sqrt(1 - b * b), WY + GR * b * 0.9
        if math.dist((x, y), (WX, WY)) > 700:
            nodes.append((x, y))
    globe = (f'<circle cx="{WX}" cy="{WY}" r="{GR}" fill="none" stroke="{LILAC}" stroke-width="6" opacity=".5"/>' +
             "".join(f'<ellipse cx="{WX}" cy="{WY}" rx="{GR * abs(math.cos(k * 0.5)):.0f}" ry="{GR}" fill="none" stroke="{LILAC}" stroke-width="4" opacity=".3"/>' for k in range(1, 4)) +
             "".join(f'<ellipse cx="{WX}" cy="{WY + GR * 0.9 * f:.0f}" rx="{GR * math.sqrt(1 - f * f):.0f}" ry="{GR * 0.12 * math.sqrt(1 - f * f):.0f}" fill="none" stroke="{LILAC}" stroke-width="4" opacity=".3"/>' for f in (-0.6, -0.3, 0, 0.3, 0.6)) +
             "".join(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="{CYAN}" stroke-width="4" opacity=".35"/>' for i, a in enumerate(nodes) for b in nodes[i + 1:] if math.dist(a, b) < 420))
    copy_def = (f'<g id="{p}-copyDef"><rect x="-90" y="-60" width="180" height="120" rx="14" fill="#14123a" stroke="{LILAC}" stroke-width="5"/>'
             f'<rect x="-90" y="-60" width="180" height="30" rx="14" fill="#221e5c"/><circle cx="-66" cy="-45" r="6" fill="{RED}"/>'
             + "".join(f'<rect x="-70" y="{-14 + k * 20}" width="{140 - (k % 2) * 40}" height="9" rx="4" fill="{LILAC}" opacity=".7"/>' for k in range(3)) + '</g>')
    copies = "".join(f'<g transform="translate({x:.0f} {y:.0f}) scale(1.6)"><g class="copy"><use href="#{p}-copyDef"/></g></g>' for x, y in nodes)
    copies += "".join(f'<g transform="translate({x:.0f} {y:.0f}) scale(1.6)"><g class="copy"><use href="#{p}-copyDef"/></g></g>' for x, y in
                      [(WX + r * math.cos(a), WY + r * math.sin(a) * 0.8) for a, r in [(rr.uniform(0, 6.28), rr.uniform(760, 1150)) for _ in range(24)]])
    extra = copy_def
    svg = f"""
<g id="{p}-globe" opacity="0">{globe}</g>
<g id="{p}-copies">{copies}</g>
<g transform="translate({WX} {WY}) scale(.92)"><g id="{p}-window">{forum_window(p)}
 <g id="{p}-banned" opacity="0"><g transform="translate(0 40)"><circle r="230" fill="none" stroke="{RED}" stroke-width="40" filter="url(#{p}-glow)"/><line x1="-163" y1="163" x2="163" y2="-163" stroke="{RED}" stroke-width="40" stroke-linecap="round"/></g></g>
</g></g>
<g id="{p}-fw"><ellipse cx="1580" cy="1004" rx="150" ry="16" fill="#05031a" opacity=".55"/>
 {place(1580, 1000, 0.74, person_v(p + "f", "work", "standing", "#38e8a8", "#232344", 0, "#c9a050", shadow=False), flip=True)}</g>
"""
    html = (f'<div id="{p}-n" class="title" style="left:1380px;top:330px;font-size:300px;color:#ff4f7d;opacity:0">0</div>' +
            text(f"{p}-t1", "YEARS", f"left:1400px;top:660px;font-size:90px;color:#ff9bb0;{MONO}"))
    js = f"""
  camZ("#{p}-cam", 0, {t_erased:.2f}, 1.1, 1.0, {WX}, {WY}, "power2.out");
  tl.fromTo("#{p}-fu",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.2,transformOrigin:"50% 50%",duration:0.3,repeat:1,yoyo:true,immediateRender:false}},{t_founder:.2f});
  tl.to("#{p}-fl .fl",{{scaleX:0,transformOrigin:"100% 50%",duration:0.18,stagger:{{each:0.06,from:"end"}}}},{t_erased:.2f});
  tl.to(["#{p}-ft","#{p}-fu"],{{opacity:0.15,duration:0.3}},{t_erased + 0.3:.2f});
  tl.fromTo("#{p}-banned",{{opacity:0,scale:2.2,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.3,ease:"power4.in"}},{t_banned:.2f});
  tl.fromTo("#{p}-window",{{x:0}},{{x:12,duration:0.05,repeat:5,yoyo:true,ease:"none",immediateRender:false}},{t_banned + 0.3:.2f});
  enter("#{p}-n", {t_five - 0.2:.2f}, 0.2);
  count_up("{p}-n", {t_five - 0.2:.2f}, {t_years - t_five + 0.4:.2f}, 0, 5);
  rise("#{p}-t1 span", {t_years:.2f});
  tl.to(["#{p}-n","#{p}-t1"],{{opacity:0,duration:0.4}},{t_backfire - 0.2:.2f});
  tl.fromTo("#{p}f-head",{{rotation:0,svgOrigin:"0 -447"}},{{rotation:8,svgOrigin:"0 -447",duration:0.3,repeat:1,yoyo:true,ease:"power2.inOut"}},{t_erased:.2f});
  tl.fromTo("#{p}f-body",{{scaleY:1,svgOrigin:"0 0"}},{{scaleY:1.03,svgOrigin:"0 0",duration:0.15,repeat:1,yoyo:true,immediateRender:false}},{t_banned:.2f});
  tl.to("#{p}-fw",{{x:420,opacity:0,duration:0.6,ease:"power2.in"}},{t_five - 0.7:.2f});
  camZ("#{p}-cam", {t_effect:.2f}, 1.8, 1.0, 0.42, {WX}, {WY}, "power3.inOut");
  enter("#{p}-globe", {t_effect + 0.2:.2f}, 1.0);
  tl.fromTo("#{p}-banned",{{opacity:1}},{{opacity:0.15,duration:0.6,immediateRender:false}},{t_banned2:.2f});
  tl.fromTo("#{p}-copies .copy",{{scale:0,opacity:0,x:0,transformOrigin:"50% 50%"}},{{scale:1,opacity:1,transformOrigin:"50% 50%",duration:0.45,ease:"back.out(2.5)",stagger:{{amount:2.4,from:"random"}}}},{t_spread:.2f});
  camZ("#{p}-cam", {t_effect + 1.8:.2f}, {dur - t_effect - 1.8:.2f}, 0.42, 0.37, {WX}, {WY}, "none");
  tl.fromTo("#{p}-globe",{{opacity:1}},{{opacity:0.6,duration:0.3,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_internet - 0.6:.2f});
""" + life(p + "f", dur, (1.6, 3.9))
    return composition(p, dur, svg, html, js, extra, background=("#2c1460", "#140b3a", "#06051a"), seed=25)


SEG_MAP = {("reality", 2): "reality_2", ("reality", 3): "reality_3", ("reality", 4): "reality_4", ("reality", 7): "reality_7",
        ("reality", 8): "reality_8", ("robot", 0): "robot_0", ("robot", 1): "robot_1", ("robot", 2): "robot_2", ("robot", 3): "robot_3", ("robot", 4): "robot_4"}
_FN = {"reality_2": reality_2, "reality_3": reality_3, "reality_4": reality_4, "reality_7": reality_7, "reality_8": reality_8,
       "robot_0": robot_0, "robot_1": robot_1, "robot_2": robot_2, "robot_3": robot_3, "robot_4": robot_4}
SCENES = [(k, _FN[k], seg(c, i)[1]) for (c, i), k in SEG_MAP.items()]

if __name__ == "__main__":
    print(write_scenes(SCENES, HERE))
