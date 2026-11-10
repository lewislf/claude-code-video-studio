"""Group g7: robot 5 to 9 and closing 0 to 2 (v5 scenes).

  python3 build_g7_robot2_closing1.py     # writes compositions/ and index.html in this folder

Reused pieces: key and beam from M8 (scenes-v4/build4.py), corridor with the door from F2 (scenes-v3/build2.py),
lightning (`bolt`, build4), the profile person with a brain (engine.person, only in closing 1, where the narration talks about the brain),
the real person, pictures and orbs (scenes/figure.py; other people with the same pieces via figure_var).
The evil robot and the lock are this group's own art, in the same neon line.
"""
import os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from engine import *  # noqa: E402,F403
HERE = os.path.dirname(os.path.abspath(__file__))  # engine also defines HERE (scenes); here it is the group folder
sys.path.insert(0, os.path.join(HERE, "../../scenes-v4"))
from build4 import bolt  # noqa: E402
from figure import figure, figure_idle, picture, orb, SKIN, HAIR, HOME, WORK, ANCHORS  # noqa: E402

SKINS = [SKIN, "#c98e62", "#8d5a3b"]


def anchors(variant="home", pose="standing", turn=25):
    """Anchors from figure.py (hand_r, hand_l, head_center, shoulder_arm...) for the person drawn with these parameters."""
    return ANCHORS[("home" if variant == "home" else "work", "standing" if pose == "standing" else "sitting", 30 if turn >= 15 else 0)]


def pivot(variant="home", pose="standing", turn=25):
    """Shoulder svgOrigin to rotate {p}-arm (the arm group has no transform, so it is in the person's local coordinates)."""
    x, y = anchors(variant, pose, turn)["shoulder_arm"]
    return f"{x} {y}"


def figure_var(p, variant="home", pose="standing", glow=None, skin=0, hair=None, outfit=None, pants=None, **kw):
    """The figure.py person with another skin, hair or outfit (swaps the base hex of each piece). outfit=(torso, ...): only the 1st counts."""
    # The masks in the new drawing are "M-9999 -9999h19998v19998..." cut by clip-path. getBBox ignores the clip, so
    # every transformOrigin in % (trunk breathing, pop, squash) rotated around a point thousands of px away and the
    # trunk rose and swallowed the head. A rectangle the size of the person gives the same drawing and an honest box.
    s = figure(p, variant, pose, glow=glow, **kw).replace("M-9999 -9999h19998v19998h-19998Z", "M-300 -640h600v700h-600Z")
    v = HOME if variant == "home" else WORK
    if skin:
        s = s.replace(SKIN, SKINS[skin])
    if hair:
        s = s.replace(HAIR, hair)
    if outfit:
        s = s.replace(v["torso"], outfit[0])
    if pants:
        s = s.replace(v["pants"], pants)
    return s


def idle(p, dur, blinks, pose="standing"):
    """figure_idle with the breathing pivot at the hip via svgOrigin ({p}-trunk has no transform)."""
    return figure_idle(p, dur, blinks).replace('transformOrigin:"50% 100%"', f'svgOrigin:"0 {-230 if pose == "standing" else -175}"')


def portrait(p, x, y, k, variant="home", **kw):
    """Head and shoulders of a standing person, facing front (photo/avatar): the point PORTRAIT_DY below the head center goes to (x, y)."""
    cx, cy = anchors(variant, "standing", 0)["head_center"]
    return (f'<g transform="translate({x - cx * k:.1f} {y - (cy + PORTRAIT_DY) * k:.1f}) scale({k})">'
            f'{figure_var(p, variant, "standing", chair=False, shadow=False, turn=0, **kw)}</g>')


PORTRAIT_DY = 40   # ponytail: tune by eye in the snapshot (it used to be the (0,-575) of the old character)


PLEX = "font-family:'IBM Plex Mono',monospace;font-weight:500;letter-spacing:.14em"

# extra JS: SVG text that rises through a mask (follows the camera) and a stroke that draws itself
JS_G7 = r"""
  function sr(sel,t,h){tl.set(sel,{opacity:0},0);tl.fromTo(sel,{y:h,opacity:1},{y:0,opacity:1,duration:0.75,ease:"expo.out",immediateRender:false},t);}
  function draw(sel,t,d,L){tl.fromTo(sel,{attr:{"stroke-dashoffset":L}},{attr:{"stroke-dashoffset":0},duration:d,ease:"power2.inOut"},t);}
  function exit_up(sel,t){tl.fromTo(sel,{yPercent:0},{yPercent:-125,duration:0.45,ease:"power3.in",immediateRender:false},t);}
"""


def srise(id_, x, y, txt, size, color, family="EB Garamond", weight=700, align="middle", spacing=0, outline=True):
    """SVG text attached to the art (follows the camera), rising through a mask. Animate with sr('#id', t, size*1.3)."""
    return (f'<clipPath id="{id_}-m"><rect x="-4000" y="{y - size * 1.0:.0f}" width="12000" height="{size * 1.32:.0f}"/></clipPath>'
            f'<g clip-path="url(#{id_}-m)"><text id="{id_}" x="{x}" y="{y}" text-anchor="{align}" font-family="{family}" font-weight="{weight}" '
            f'font-size="{size}" letter-spacing="{spacing}" fill="{color}" stroke="#05031a" stroke-width="{size * 0.12 if outline else 0:.1f}" paint-order="stroke" '
            f'stroke-linejoin="round" opacity="0">{txt}</text></g>')


def mono(id_, txt, style, color, size=56, dot=True):
    """Large uppercase IBM Plex Mono label (rises through a mask, `rise('#id span', t)`)."""
    d = (f'<i style="display:inline-block;width:{size * .36:.0f}px;height:{size * .36:.0f}px;border-radius:50%;background:{color};'
         f'margin-right:{size * .4:.0f}px;vertical-align:{size * .08:.0f}px;box-shadow:0 0 18px {color}"></i>') if dot else ""
    return text(id_, d + txt, f"{style};{PLEX};font-size:{size}px;color:{color}")


# ---------------------------------------------------------------- this group's art
def robot(p, glow, eye=RED, color=MAGENTA):
    """Evil robot in neon line. Local: x -320..320, y -330..300 (base at y=300). Ids: {p}-eyes (lit eyes)."""
    shape = ('<rect x="-170" y="-250" width="340" height="230" rx="44"/>'
             '<rect x="-204" y="-176" width="34" height="86" rx="12"/><rect x="170" y="-176" width="34" height="86" rx="12"/>'
             '<rect x="-56" y="-22" width="112" height="40" rx="8"/>'
             '<path d="M-205 14 L205 14 L165 296 L-165 296 Z"/>')
    arms = "M-205 44 C-275 80 -305 150 -292 238 M205 44 C275 80 305 150 292 238"
    claws = "M-312 232 Q-326 262 -306 288 M-272 232 Q-258 262 -278 288 M312 232 Q326 262 306 288 M272 232 Q258 262 278 288"
    eyes = ('<path d="M-118 -178 L-30 -148 L-38 -116 L-112 -124 Z"/><path d="M118 -178 L30 -148 L38 -116 L112 -124 Z"/>'
             '<circle cx="0" cy="130" r="24"/><circle cx="0" cy="-312" r="17"/>')
    teeth = "".join(f'<line x1="{x}" y1="-82" x2="{x}" y2="-46" stroke="{color}" stroke-width="3" opacity=".7"/>' for x in range(-64, 80, 32))
    return (f'<defs><linearGradient id="{p}-rbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#30268a"/><stop offset="1" stop-color="#120d3a"/></linearGradient>'
            f'<radialGradient id="{p}-reyeglow"><stop offset="0" stop-color="{eye}" stop-opacity=".85"/><stop offset="1" stop-color="{eye}" stop-opacity="0"/></radialGradient></defs>'
            f'<g id="{p}-robot"><path d="{arms}" fill="none" stroke="#120d3a" stroke-width="30" stroke-linecap="round"/>'
            f'<g fill="url(#{p}-rbg)">{shape}</g>'
            f'<g fill="none" stroke="{color}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round" filter="url(#{glow})">{shape}<path d="{arms}"/><path d="{claws}"/>'
            f'<line x1="0" y1="-250" x2="0" y2="-294"/></g>'
            f'<rect x="-96" y="-84" width="192" height="40" rx="10" fill="#05031a" stroke="{color}" stroke-width="4"/>{teeth}'
            f'<circle cx="0" cy="130" r="50" fill="#05031a" stroke="{color}" stroke-width="5"/>'
            f'<g fill="#3a3466">{eyes}</g>'
            f'<g id="{p}-eyes"><circle cx="-74" cy="-146" r="86" fill="url(#{p}-reyeglow)" opacity=".6"/><circle cx="74" cy="-146" r="86" fill="url(#{p}-reyeglow)" opacity=".6"/>'
            f'<g fill="{eye}">{eyes}</g></g></g>')


def plate(p, glow, r=230):
    """Lock: round amber plate with the keyhole. Center (0,0), radius r. Ids: {p}-light (lit keyhole)."""
    k = r / 230
    hole = (f"M{-34 * k:.1f} {4.5 * k:.1f} A{56 * k:.1f} {56 * k:.1f} 0 1 1 {34 * k:.1f} {4.5 * k:.1f} "
            f"L{58 * k:.1f} {120 * k:.1f} L{-58 * k:.1f} {120 * k:.1f} Z")
    # keyhole: circle centered at (0,-40k); the whole path moves up 40k
    hole = f'<path d="{hole}" transform="translate(0 {-40 * k:.1f})"'
    screws = "".join(f'<circle cx="{x * k:.0f}" cy="{y * k:.0f}" r="{11 * k:.1f}" fill="#ffcf6a" opacity=".75"/>' for x, y in ((-140, -140), (140, -140), (-140, 140), (140, 140)))
    return (f'<defs><radialGradient id="{p}-platefill" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#5a3f1a"/><stop offset="1" stop-color="#1d1208"/></radialGradient>'
            f'<radialGradient id="{p}-plateglow" cx="50%" cy="40%" r="60%"><stop offset="0" stop-color="#fffbe8"/><stop offset="1" stop-color="#ffb23e"/></radialGradient></defs>'
            f'<circle r="{r}" fill="url(#{p}-platefill)"/>'
            f'<circle r="{r}" fill="none" stroke="{AMBER}" stroke-width="{12 * k:.1f}" filter="url(#{glow})"/>'
            f'<circle r="{r * .84:.1f}" fill="none" stroke="#ffcf6a" stroke-width="{3 * k:.1f}" opacity=".45"/>{screws}'
            f'{hole} fill="#05031a" stroke="#ffcf6a" stroke-width="{4 * k:.1f}"/>'
            f'{hole} id="{p}-light" fill="url(#{p}-plateglow)" opacity="0" filter="url(#{glow})"/>')


def key(glow, color=AMBER):
    """Key from M8 (scenes-v4): ring at (0,0), shaft down to (0,130)."""
    return (f'<g filter="url(#{glow})"><circle cx="0" cy="0" r="34" fill="none" stroke="{color}" stroke-width="12"/>'
            f'<path d="M0 34 L0 130 M0 100 L30 100 M0 124 L22 124" stroke="{color}" stroke-width="12" fill="none" stroke-linecap="round"/></g>')


def beam_def(p):
    return (f'<linearGradient id="{p}-fx" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffcf6a" stop-opacity=".5"/>'
            f'<stop offset="1" stop-color="#ffe3a0" stop-opacity="0"/></linearGradient>')


def ground(p, y=880, color="#26246a"):
    return (f'<linearGradient id="{p}-floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{color}" stop-opacity=".75"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient>')


def corridor(p, glow):
    """Server corridor from F2 (scenes-v3/build2.py::scene_F2), with prefixed ids and the door in the background."""
    defs = f"""<defs><radialGradient id="{p}-end" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#9af0ff" stop-opacity=".9"/><stop offset=".4" stop-color="#6a8cff" stop-opacity=".4"/><stop offset="1" stop-color="#6a8cff" stop-opacity="0"/></radialGradient>
<linearGradient id="{p}-ceiling" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0828"/><stop offset="1" stop-color="#1c1a58"/></linearGradient>
<linearGradient id="{p}-ground2" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#06051a"/><stop offset="1" stop-color="#26246a"/></linearGradient>
<linearGradient id="{p}-rack" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1a1856"/><stop offset="1" stop-color="#2c2a88"/></linearGradient></defs>"""

    def points(side):
        def f(u, v):
            xb = 960 + side * 960; xf = 960 + side * 118
            yt0, yb0 = -40, 1120; yt1, yb1 = 410, 600
            x = xb + (xf - xb) * u
            yt = yt0 + (yt1 - yt0) * u; yb = yb0 + (yb1 - yb0) * u
            return x, yt + (yb - yt) * v
        return f
    parts, leds, cables = [], [], []
    for side in (-1, 1):
        f = points(side)
        us = [1 - 1 / (1 + 0.5 * i) for i in range(0, 26)]
        for i in range(len(us) - 1):
            a, bb = us[i], us[i + 1]
            q = " ".join(f"{x:.0f},{y:.0f}" for x, y in [f(a, 0.03), f(bb, 0.03), f(bb, 0.97), f(a, 0.97)])
            parts.append(f'<polygon points="{q}" fill="url(#{p}-rack)" stroke="#5a5ad0" stroke-width="3"/>'
                          f'<polygon points="{q}" fill="#05031a" opacity="{0.18 + 0.7 * (a ** 0.8):.2f}"/>')
            x1, y1 = f(a, 0.025); x2, y2 = f(bb, 0.025)
            cables.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#ff4fa3" stroke-width="{max(2, 8 * (1 - a)):.1f}" opacity=".7"/>')
            for r in range(11):
                for c in range(3):
                    uu = a + (bb - a) * (0.18 + 0.3 * c); vv = 0.10 + 0.08 * r
                    x, y = f(uu, vv)
                    size = max(2.2, 20 * (1 - uu) ** 1.3)
                    color = CYAN if (i + r + c) % 4 else (AMBER if (r + c) % 2 else MAGENTA)
                    leds.append(f'<rect class="{p}-led" x="{x - size:.1f}" y="{y - size * 0.5:.1f}" width="{size * 2:.1f}" height="{size:.1f}" rx="{size * 0.2:.1f}" fill="{color}"/>')
    strips = "".join(f'<polygon points="{960 + dx * 0.06:.0f},430 {960 - dx * 0.06:.0f},430 {960 - dx:.0f},-40 {960 + dx:.0f},-40" fill="#cfe8ff" opacity=".16"/>' for dx in (170, 520, 880))
    guides = "".join(f'<line x1="{x}" y1="1120" x2="{960 + (x - 960) * 0.12:.0f}" y2="590" stroke="#6ad8ff" stroke-width="3" opacity=".22"/>' for x in (260, 560, 960, 1360, 1660))
    door = (f'<rect x="905" y="470" width="110" height="120" rx="8" fill="#0b0920"/>'
             f'<g transform="translate(960 530)"><g id="{p}-doorglow"><rect x="-55" y="-60" width="110" height="120" rx="8" fill="#cfeaff" opacity=".9" filter="url(#{glow})"/></g></g>'
             f'<rect x="905" y="470" width="110" height="120" rx="8" fill="none" stroke="#8d7bff" stroke-width="3"/>')
    return (defs + f'<polygon points="0,-40 1920,-40 1080,430 840,430" fill="url(#{p}-ceiling)"/><polygon points="0,1120 1920,1120 1080,590 840,590" fill="url(#{p}-ground2)"/>'
            f'<ellipse id="{p}-haze" cx="960" cy="510" rx="520" ry="330" fill="url(#{p}-end)"/>{strips}'
            f'<g>{"".join(parts)}</g><g>{guides}</g>{door}<g>{"".join(cables)}</g><g>{"".join(leds)}</g>')


def scene(p, dur, svg, html, js, extra="", **kw):
    return composition(p, dur, svg, html, JS_G7 + js, extra, **kw)


# ================================================================ robot 5: the idea does not hold up
def robot_5():
    p, C, S = "robot_5", "robot", 5
    start, dur = seg(C, S)
    t_hold, t_shaky, t_assumptions, t_machine, t_want = 1.19, 3.23, 4.02, 5.88, 7.39
    t_rejected, t_forum, t_there_is, t_no, t_evidence, t_threat = 8.13, 11.13, 12.19, 12.79, 13.51, 14.89
    blocks = [(960, 120, 800), (978, 300, 720), (940, 420, 640), (988, 340, 560), (955, 470, 480)]
    extra = (ground(p) + f'<linearGradient id="{p}-blk" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5a46c8"/><stop offset="1" stop-color="#241a6e"/></linearGradient>'
             f'<radialGradient id="{p}-iris"><stop offset="0" stop-color="#ffd27a"/><stop offset=".45" stop-color="{RED}"/><stop offset="1" stop-color="#5a0a20"/></radialGradient>')
    rng = random.Random(5)
    blocks_svg = ""
    for k, (cx, w, y) in enumerate(blocks):
        x0 = cx - w / 2
        pts = [(x0 + 8, y + 10)] + [(x0 + w * (j + 1) / 5 + rng.uniform(-14, 14), y + 14 + (j % 2) * 44 + rng.uniform(-8, 8)) for j in range(4)] + [(x0 + w - 8, y + 70)]
        crack = "M" + " L".join(f"{a:.0f} {b:.0f}" for a, b in pts)
        blocks_svg += (f'<g id="{p}-b{k}"><rect x="{x0:.0f}" y="{y}" width="{w}" height="80" rx="10" fill="url(#{p}-blk)" stroke="#8d7bff" stroke-width="5"/>'
               f'<line x1="{x0 + 14:.0f}" y1="{y + 10}" x2="{x0 + w - 14:.0f}" y2="{y + 10}" stroke="#cfc6ff" stroke-width="3" opacity=".5"/>'
               f'<path id="{p}-cr{k}" d="{crack}" fill="none" stroke="#f3eeff" stroke-width="4" stroke-linejoin="round" stroke-dasharray="900" stroke-dashoffset="900"/></g>')
    # iris clipped by the almond (it used to leak above and below); the ending squashes the whole eye, outline included
    extra += f'<clipPath id="{p}-almond"><path d="M-205 0 Q0 -165 205 0 Q0 165 -205 0 Z"/></clipPath>'
    eye = (f'<g id="{p}-eye"><g id="{p}-lid"><path d="M-205 0 Q0 -165 205 0 Q0 165 -205 0 Z" fill="#2a0a1a"/>'
            f'<g clip-path="url(#{p}-almond)"><circle r="98" fill="url(#{p}-iris)"/><g id="{p}-pup"><circle r="34" fill="#05031a"/><circle r="34" fill="none" stroke="#ff9fb5" stroke-width="3" opacity=".6"/></g>'
            f'<circle cx="-34" cy="-40" r="14" fill="#fff" opacity=".7"/></g></g>'
            f'<path d="M-205 0 Q0 -165 205 0 Q0 165 -205 0 Z" fill="none" stroke="{RED}" stroke-width="7" filter="url(#{p}-glow)"/></g>')
    bubbles = ""
    # people from the forum itself: each post has the avatar of a different person
    authors = [dict(variant="work", skin=1, outfit=("#3a4a8a", "#2a3870")), dict(variant="home", skin=0, hair="#c99a3a", outfit=("#2fa88a", "#1f8068")),
               dict(variant="home", skin=2, hair="#140c08", outfit=("#d0408a", "#a02a68"))]
    for k, (x, y) in enumerate([(1330, 230), (1400, 440), (1310, 650)]):
        lines = "".join(f'<rect x="{x + 110}" y="{y + 40 + j * 32}" width="{250 - j * 60}" height="14" rx="7" fill="#8d7bff" opacity=".55"/>' for j in range(3))
        extra += f'<clipPath id="{p}-av{k}"><circle cx="{x + 40}" cy="{y + 79}" r="52"/></clipPath>'
        av = (f'<circle cx="{x + 40}" cy="{y + 79}" r="52" fill="#3a2f8a"/><g clip-path="url(#{p}-av{k})">{portrait(f"{p}-a{k}", x + 40, y + 100, 0.66, glow=p + "-glow", **authors[k])}</g>'
              f'<circle cx="{x + 40}" cy="{y + 79}" r="52" fill="none" stroke="#cfc6ff" stroke-width="4"/>')
        bubbles += (f'<g id="{p}-bubble{k}"><path d="M{x} {y} h380 a24 24 0 0 1 24 24 v110 a24 24 0 0 1 -24 24 h-300 l-40 40 v-40 h-40 a24 24 0 0 1 -24 -24 v-110 a24 24 0 0 1 24 -24 z" '
                f'fill="#1c1a58" stroke="#8d7bff" stroke-width="5" filter="url(#{p}-shadow)"/>{av}{lines}'
                f'<g id="{p}-x{k}"><circle cx="{x + 370}" cy="{y + 10}" r="38" fill="{RED}" filter="url(#{p}-glow)"/>'
                f'<path d="M{x + 354} {y - 6} l32 32 M{x + 386} {y - 6} l-32 32" stroke="#fff" stroke-width="8" stroke-linecap="round"/></g></g>')
    svg = f"""<g id="{p}-world">
<rect x="-300" y="880" width="2520" height="400" fill="url(#{p}-floor)"/>
<g transform="translate(960 560) scale(1.4)"><g id="{p}-ghost" opacity="0" filter="url(#{p}-blur6)">{robot(p + "g", p + "-glow")}</g></g>
<ellipse id="{p}-floorshadow" cx="960" cy="886" rx="300" ry="24" fill="#05031a" opacity=".55"/>
<g id="{p}-tower">{blocks_svg}<g transform="translate(955 380)"><g id="{p}-eyeW">{eye}</g></g></g>
{bubbles}
</g>"""
    html = (text(f"{p}-t1", "SHAKY", "left:70px;top:340px;font-size:76px;color:#e2dcff") +
            text(f"{p}-t2", "ASSUMPTIONS", "left:70px;top:440px;font-size:76px;color:#c9b8ff") +
            text(f"{p}-t3", "NO EVIDENCE", "left:0;right:0;text-align:center;top:250px;font-size:128px;color:#ffd98a"))
    fall = ""
    rng_fall = random.Random(9)
    for k, (cx, w, y) in enumerate(blocks):
        dy = 880 - (y + 80) - (0 if k == 0 else rng_fall.uniform(0, 30))
        dx = [0, -330, 300, -560, 520][k]
        rot = [0, -14, 10, -24, 18][k]
        fall += f'tl.to("#{p}-b{k}",{{x:{dx},y:{dy:.0f},rotation:{rot},transformOrigin:"50% 50%",duration:0.75,ease:"bounce.out"}},{t_there_is + 0.12 * (4 - k):.2f});'
    js = f"""
  camZ("#{p}-cam", 0, 3.0, 1.12, 1.0, 960, 560);
  camZ("#{p}-cam", 3.1, {t_there_is - 3.3:.2f}, 1.0, 1.07, 960, 470, "sine.inOut");
  camZ("#{p}-cam", {t_there_is:.2f}, 1.4, 1.07, 0.98, 960, 640);
  tl.fromTo("#{p}-pup",{{x:-34}},{{x:34,duration:1.1,repeat:5,yoyo:true,ease:"sine.inOut"}},0.3);
  tl.fromTo("#{p}-tower",{{rotation:-1.4,transformOrigin:"50% 100%"}},{{rotation:1.4,duration:0.55,repeat:{int((t_there_is - 0.3 - t_hold) / 0.55) - 1},yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_hold:.2f});
  rise("#{p}-t1 span", {t_shaky:.2f}); rise("#{p}-t2 span", {t_assumptions:.2f});
  {"".join(f'draw("#{p}-cr{k}", {t_assumptions + 0.12 * k:.2f}, 0.5, 900);' for k in range(5))}
  tl.fromTo("#{p}-ghost",{{opacity:0}},{{opacity:0.32,duration:0.8}},{t_machine:.2f});
  tl.fromTo("#{p}-ghost",{{opacity:0.32}},{{opacity:0,duration:0.8,immediateRender:false}},{t_want + 0.5:.2f});
  {"".join(f'pop("#{p}-bubble{k}", {t_rejected + 0.45 * k:.2f}, 0.4, 0.7); pop("#{p}-x{k}", {t_rejected + 0.45 * k + 0.5:.2f}, 2.2, 0.45);' for k in range(3))}
  tl.fromTo("#{p}-pup",{{scale:1,transformOrigin:"50% 50%"}},{{scale:0.62,transformOrigin:"50% 50%",duration:0.3,immediateRender:false}},{t_rejected:.2f});
  vanish("#{p}-t1", {t_there_is - 0.3:.2f}, 0.4); vanish("#{p}-t2", {t_there_is - 0.3:.2f}, 0.4);
  {"".join(f'vanish("#{p}-bubble{k}", {t_there_is - 0.3:.2f}, 0.4);' for k in range(3))}
  tl.to("#{p}-tower",{{rotation:9,duration:0.35,ease:"power2.in"}},{t_there_is - 0.15:.2f});
  {fall}
  tl.to("#{p}-eyeW",{{y:420,x:-60,rotation:-8,duration:0.8,ease:"bounce.out"}},{t_there_is + 0.1:.2f});
  tl.to("#{p}-eye",{{scaleY:0.04,transformOrigin:"50% 50%",duration:0.35,ease:"power2.in"}},{t_there_is + 0.6:.2f});
  tl.to("#{p}-eye",{{opacity:0,duration:0.3}},{t_there_is + 0.95:.2f});
  tl.fromTo("#{p}-floorshadow",{{attr:{{rx:300}}}},{{attr:{{rx:760}},duration:0.6}},{t_there_is + 0.2:.2f});
  tl.fromTo("#{p}-world",{{y:0}},{{y:10,duration:0.06,repeat:7,yoyo:true,ease:"none"}},{t_there_is + 0.75:.2f});
  rise("#{p}-t3 span", {t_no:.2f}, 0.9);
"""
    return scene(p, dur, svg, html, js, extra, seed=5)


# ================================================================ robot 6: the fear of an evil robot
def robot_6():
    p, C, S = "robot_6", "robot", 6
    start, dur = seg(C, S)
    t_notice, t_fear, t_robot, t_pressure, t_people, t_real, t_acting, t_today = 0.55, 3.3, 4.05, 5.24, 6.42, 7.25, 7.95, 8.46
    extra = (ground(p, color="#2a1d70") + f'<radialGradient id="{p}-redglow" cx="72%" cy="40%" r="70%"><stop offset="0" stop-color="{RED}" stop-opacity=".55"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>'
             f'<clipPath id="{p}-bigscreen"><rect x="1080" y="180" width="660" height="560" rx="14"/></clipPath>'
             f'<linearGradient id="{p}-light" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe3a0" stop-opacity=".45"/><stop offset="1" stop-color="#ffe3a0" stop-opacity="0"/></linearGradient>')
    # street at night: buildings in the background, lamp post, sidewalk; the robot shows on a big screen on the right facade
    rng = random.Random(61)
    background = ""
    for x0, w, top in ((-40, 230, 300), (200, 180, 200), (390, 260, 340), (660, 200, 240), (870, 170, 390)):
        windows_svg = "".join(f'<rect x="{x0 + 22 + c * 46}" y="{top + 30 + r * 58}" width="24" height="32" rx="3" fill="{"#ffe39a" if rng.random() < 0.35 else "#16124a"}" opacity=".7"/>'
                      for r in range(int((840 - top - 60) / 58)) for c in range(int((w - 30) / 46)))
        background += f'<rect x="{x0}" y="{top}" width="{w}" height="{840 - top}" fill="#1a1450" stroke="#3a2f8a" stroke-width="3"/>{windows_svg}'
    facade = (f'<rect x="1010" y="110" width="800" height="730" fill="#201a5e" stroke="#5a4ad0" stroke-width="4"/>'
               f'<rect x="1066" y="166" width="688" height="588" rx="20" fill="#05031a" stroke="#8d7bff" stroke-width="8" filter="url(#{p}-shadow)"/>'
               f'<rect x="1100" y="754" width="40" height="86" fill="#14103e"/><rect x="1680" y="754" width="40" height="86" fill="#14103e"/>')
    lamp = (f'<polygon points="930,300 990,300 1060,840 860,840" fill="url(#{p}-light)"/>'
             f'<path d="M 960 840 L 960 270 Q 960 240 990 240 L 1010 240" fill="none" stroke="#3a2f8a" stroke-width="14" stroke-linecap="round"/>'
             f'<ellipse cx="1004" cy="262" rx="30" ry="12" fill="#ffe3a0" filter="url(#{p}-glow)"/>')
    people = ""
    types = [dict(variant="home", skin=0), dict(variant="work", skin=2, outfit=("#3a4a8a", "#2a3870")),
             dict(variant="home", skin=1, hair="#140c08", outfit=("#2fa88a", "#1f8068"))]
    for k, x in enumerate((190, 470, 750)):
        people += (f'<g transform="translate({x} 840) scale(.74)"><g id="{p}-sq{k}"><g id="{p}-jitter{k}">'
                f'{figure_var(f"{p}-g{k}", glow=p + "-glow", **types[k])}</g></g></g>')
    waves = "".join(f'<circle id="{p}-wave{k}" cx="1410" cy="460" r="80" fill="none" stroke="{RED}" stroke-width="10" opacity="0"/>' for k in range(3))
    svg = f"""<rect x="-200" y="840" width="2320" height="400" fill="url(#{p}-floor)"/>
<g opacity=".8">{background}</g>{facade}
<rect id="{p}-redtint" x="-200" y="-200" width="2320" height="1480" fill="url(#{p}-redglow)" opacity="0"/>
<rect id="{p}-screen" x="1080" y="180" width="660" height="560" rx="14" fill="#3a0a24" opacity="0"/>
<g clip-path="url(#{p}-bigscreen)"><g transform="translate(1410 470) scale(.86)"><g id="{p}-robW" opacity="0"><g id="{p}-rob">{robot(p, p + "-glow")}</g></g></g></g>
{waves}{lamp}
<rect x="-200" y="836" width="2320" height="8" fill="#3a2f8a"/>
{people}"""
    html = (text(f"{p}-t1", "FEAR", "left:110px;top:40px;font-size:180px;color:#ff8aa6") +
            text(f"{p}-t3", "TODAY", "left:110px;top:60px;font-size:160px;color:#ffd98a") +
            mono(f"{p}-t2", "REAL PEOPLE", "left:130px;top:910px", MINT, 60))
    js = f"""
  camZ("#{p}-cam", 0, {t_fear - 0.2:.2f}, 1.0, 1.12, 700, 600, "sine.inOut");
  camZ("#{p}-cam", {t_fear - 0.1:.2f}, 0.8, 1.12, 0.96, 960, 600);
  camZ("#{p}-cam", {t_fear + 0.8:.2f}, {dur - t_fear - 0.8:.2f}, 0.96, 1.04, 700, 640, "sine.inOut");
  {"".join(f'tl.fromTo("#{p}-g{k}-eye",{{x:0}},{{x:3,duration:0.3}},{t_notice + 0.2 * k:.2f});' for k in range(3))}
  tl.fromTo("#{p}-screen",{{opacity:0}},{{opacity:1,duration:0.12,repeat:3,yoyo:true,ease:"steps(1)"}},{t_fear - 0.3:.2f});
  tl.set("#{p}-screen",{{opacity:1}},{t_fear + 0.2:.2f});
  tl.fromTo("#{p}-robW",{{opacity:0,y:420}},{{opacity:1,y:0,duration:1.1,ease:"power3.out"}},{t_fear - 0.15:.2f});
  tl.fromTo("#{p}-redtint",{{opacity:0}},{{opacity:1,duration:0.8}},{t_fear:.2f});
  tl.fromTo("#{p}-eyes",{{opacity:0.2}},{{opacity:1,duration:0.12,repeat:4,yoyo:true,ease:"steps(1)"}},{t_robot:.2f});
  rise("#{p}-t1 span", {t_fear:.2f}, 0.8);
  {"".join(f'tl.fromTo("#{p}-jitter{k}",{{x:-3}},{{x:3,duration:0.07,repeat:{int((t_pressure - t_fear) / 0.07)},yoyo:true,ease:"none"}},{t_fear + 0.4:.2f});' for k in range(3))}
  tl.to("#{p}-rob",{{rotation:-6,transformOrigin:"50% 100%",duration:0.5,ease:"power2.out"}},{t_pressure - 0.1:.2f});
  {"".join(f'tl.fromTo("#{p}-wave{k}",{{attr:{{r:80}},opacity:0.9}},{{attr:{{r:1300}},opacity:0,duration:1.1,ease:"power1.out",immediateRender:false}},{t_pressure + 0.25 * k:.2f});' for k in range(3))}
  {"".join(f'tl.fromTo("#{p}-sq{k}",{{scaleY:1,scaleX:1,svgOrigin:"0 0"}},{{scaleY:0.84,scaleX:1.06,svgOrigin:"0 0",duration:0.35,ease:"power2.out"}},{t_pressure + 0.2 + 0.1 * k:.2f});' for k in range(3))}
  {"".join(f'tl.to("#{p}-sq{k}",{{scaleY:1,scaleX:1,duration:0.8,ease:"elastic.out(1,0.4)"}},{t_people + 0.1 * k:.2f});' for k in range(3))}
  rise("#{p}-t2 span", {t_people:.2f});
  vanish("#{p}-t1", {t_today - 0.45:.2f}, 0.3);
  {"".join(f'tl.fromTo("#{p}-sq{k}",{{x:0,y:0}},{{x:120,y:-50,duration:0.3,ease:"power2.out",immediateRender:false}},{t_acting + 0.12 * k:.2f}); tl.to("#{p}-sq{k}",{{y:0,duration:0.3,ease:"bounce.out"}},{t_acting + 0.3 + 0.12 * k:.2f});' for k in range(3))}
  rise("#{p}-t3 span", {t_today - 0.1:.2f}, 0.6);
  tl.fromTo("#{p}-rob",{{y:0}},{{y:-8,duration:1.2,repeat:2,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_pressure + 0.6:.2f});
""" + "".join(idle(f"{p}-g{k}", dur, (1.4 + k, 4.6 + k * 0.5, 7.3 + k * 0.3)) for k in range(3))
    return scene(p, dur, svg, html, js, extra, seed=6)


# ================================================================ robot 7: Giancarlo Guizzardi and the book
def robot_7():
    p, C, S = "robot_7", "robot", 7
    start, dur = seg(C, S)
    t_scientist, t_giancarlo, t_guizzardi, t_ufes, t_book, t_title = 0.26, 1.97, 2.92, 5.08, 5.82, 6.61
    t_who, t_fear, t_robot, t_proposal, t_separate, t_ai, t_actually, t_does, t_imagine = 8.58, 9.08, 9.68, 10.9, 11.91, 12.93, 14.98, 15.75, 16.69
    extra = (ground(p) + f'<linearGradient id="{p}-cover" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2c2380"/><stop offset="1" stop-color="#0f0b33"/></linearGradient>'
             f'<linearGradient id="{p}-pages" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e9dcc2"/><stop offset="1" stop-color="#fffaf0"/></linearGradient>')
    book = f"""<rect x="-246" y="-334" width="520" height="700" rx="12" fill="url(#{p}-pages)"/>
<g stroke="#bfb49a" stroke-width="2">{"".join(f'<line x1="262" y1="{-320 + j * 14}" x2="270" y2="{-318 + j * 14}"/>' for j in range(48))}</g>
<polygon points="-260,-350 -300,-330 -300,370 -260,350" fill="#1a1450" stroke="#8d7bff" stroke-width="4"/>
<rect x="-260" y="-350" width="520" height="700" rx="14" fill="url(#{p}-cover)" stroke="#ff4fa3" stroke-width="6" filter="url(#{p}-shadow)"/>
<rect x="-230" y="-320" width="460" height="640" rx="8" fill="none" stroke="#ff4fa3" stroke-width="2" opacity=".5"/>
{srise(p + "-c1", 0, -232, "Who's afraid", 70, "#ffe9c4")}{srise(p + "-c2", 0, -158, "of the evil", 70, "#ffe9c4")}{srise(p + "-c3", 0, -84, "robot?", 70, "#ff9fb5")}
<g transform="translate(0 176) scale(.42)"><g id="{p}-coverbot">{robot(p + "c", p + "-glow")}</g></g>"""
    # right side of the world (shows up after "separate"): what it does vs what the person imagines
    X = 1920
    bars = "".join(f'<rect id="{p}-bar{k}" x="{X + 200}" y="{430 + k * 62}" width="{w}" height="40" rx="10" fill="{CYAN}" opacity="{1 - k * 0.2:.1f}"/>'
                     for k, w in enumerate((440, 290, 170, 90)))
    monitor = (f'<rect x="{X + 150}" y="260" width="660" height="440" rx="26" fill="#0e0c26" stroke="#8d7bff" stroke-width="7" filter="url(#{p}-shadow)"/>'
               f'<rect x="{X + 200}" y="306" width="380" height="20" rx="10" fill="#8d7bff" opacity=".6"/><rect x="{X + 200}" y="346" width="260" height="20" rx="10" fill="#8d7bff" opacity=".6"/>'
               f'<rect id="{p}-pointer" x="{X + 476}" y="340" width="14" height="32" fill="{CYAN}"/>{bars}'
               f'<rect x="{X + 440}" y="700" width="80" height="60" fill="#2a1d70"/><rect x="{X + 340}" y="756" width="280" height="22" rx="11" fill="#2a1d70"/>')
    rng = random.Random(71)
    shelf = '<rect x="1170" y="220" width="710" height="660" rx="10" fill="#1a1450" stroke="#3a2f8a" stroke-width="5"/>'
    for yb in (400, 580, 760):
        x = 1190
        while x < 1850:
            w, h = rng.randint(22, 40), rng.randint(110, 160)
            shelf += f'<rect x="{x}" y="{yb - h}" width="{w}" height="{h}" rx="4" fill="{rng.choice([CYAN, LILAC, MAGENTA, AMBER, MINT, "#6a8cff"])}" opacity=".5"/>'
            x += w + rng.randint(4, 10)
        shelf += f'<rect x="1170" y="{yb}" width="710" height="14" fill="#3a2f8a"/>'
    guizzardi = figure_var(p + "-gz", "work", "standing", glow=p + "-glow", hair="#b9b6c8", outfit=("#3a4a8a", "#2a3870"))
    cloud = (f'<g id="{p}-cloud"><circle cx="{X + 1196}" cy="330" r="14" fill="#1c1a58" stroke="#8d7bff" stroke-width="4"/>'
             f'<circle cx="{X + 1240}" cy="292" r="22" fill="#1c1a58" stroke="#8d7bff" stroke-width="4"/>'
             f'<ellipse cx="{X + 1580}" cy="290" rx="320" ry="222" fill="#1c1a58" stroke="#8d7bff" stroke-width="6" filter="url(#{p}-shadow)"/>'
             f'<g transform="translate({X + 1580} 296) scale(.58)">{robot(p + "n", p + "-glow")}</g></g>')
    svg = f"""<rect x="-300" y="880" width="4600" height="400" fill="url(#{p}-floor)"/>
<g id="{p}-world">
<g opacity=".75">{shelf}</g>
<g transform="translate(1070 905) scale(.8)"><g id="{p}-gzW" opacity="0">{guizzardi}</g></g>
<ellipse cx="1500" cy="930" rx="330" ry="22" fill="#05031a" opacity=".5"/>
<g transform="translate(1500 540)"><g id="{p}-book" opacity="0">{book}</g></g>
<rect id="{p}-div" x="{X + 957}" y="90" width="6" height="900" rx="3" fill="#eef1f7" filter="url(#{p}-glow)"/>
<g id="{p}-mon">{monitor}</g>
<g transform="translate({X + 1120} 900) scale(.82)"><g id="{p}-personW">{figure_var(p + "p", "home", "standing", glow=p + "-glow", skin=1, hair="#140c08", outfit=("#d0408a", "#a02a68"))}</g></g>
<g id="{p}-cloudW" opacity="0">{cloud}</g>
{srise(p + "-s1", X + 530, 880, "ACTUALLY DOES", 80, "#bff4ff")}{srise(p + "-s2", X + 1600, 830, "WE IMAGINE", 92, "#ffb3c6")}
</g>"""
    html = (mono(f"{p}-t0", "COMPUTER SCIENTIST", "left:110px;top:250px", AMBER, 44, dot=False) +
            text(f"{p}-t1", "Giancarlo", "left:104px;top:330px;font-size:140px;color:#eef1f7") +
            text(f"{p}-t2", "Guizzardi", "left:104px;top:480px;font-size:140px;color:#c9b8ff") +
            mono(f"{p}-t3", "UFES", "left:116px;top:700px", MINT, 72))
    exit_js = "".join(f'vanish("#{p}-t{k}", {t_separate - 0.6:.2f}, 0.5);' for k in range(4))
    js = f"""
  camZ("#{p}-cam", 0, {t_title:.2f}, 1.06, 1.0, 600, 540, "sine.inOut");
  camZ("#{p}-cam", {t_title:.2f}, 1.5, 1.0, 1.32, 1460, 470);
  camZ("#{p}-cam", {t_proposal - 0.2:.2f}, 1.0, 1.32, 1.0, 1460, 470);
  pop("#{p}-gzW", {t_scientist:.2f}, 0.5, 0.8);
  tl.fromTo("#{p}-gz-eye",{{x:0,y:0}},{{x:3,y:1,duration:0.3}},{t_book:.2f});
  tl.fromTo("#{p}-gz-arm",{{rotation:0,svgOrigin:"{pivot("work")}"}},{{rotation:-62,svgOrigin:"{pivot("work")}",duration:0.6,ease:"back.out(2)"}},{t_book + 0.2:.2f});
  camZ("#{p}-cam", {t_separate + 1.2:.2f}, {dur - t_separate - 1.2:.2f}, 1.0, 1.05, 960, 560, "sine.inOut");
  rise("#{p}-t0 span", {t_scientist:.2f}); rise("#{p}-t1 span", {t_giancarlo:.2f}, 0.8); rise("#{p}-t2 span", {t_guizzardi:.2f}, 0.8); rise("#{p}-t3 span", {t_ufes:.2f});
  tl.fromTo("#{p}-book",{{opacity:0,y:-700,rotation:-18}},{{opacity:1,y:0,rotation:-4,duration:0.9,ease:"back.out(1.4)"}},{t_book - 0.6:.2f});
  tl.fromTo("#{p}-book",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.07,transformOrigin:"50% 50%",duration:0.25,repeat:1,yoyo:true,ease:"power2.out",immediateRender:false}},{t_book + 0.3:.2f});
  tl.to("#{p}-book",{{rotation:0,duration:1.0,ease:"sine.inOut"}},{t_title:.2f});
  tl.fromTo("#{p}c-eyes",{{opacity:0.2}},{{opacity:1,duration:0.1,repeat:4,yoyo:true,ease:"steps(1)"}},{t_book:.2f});
  sr("#{p}-c1", {t_who:.2f}, 92); sr("#{p}-c2", {t_fear:.2f}, 92); sr("#{p}-c3", {t_robot:.2f}, 92);
  {exit_js}
  tl.fromTo("#{p}-world",{{x:0}},{{x:-1920,duration:1.25,ease:"power3.inOut"}},{t_separate - 0.35:.2f});
  tl.fromTo("#{p}-div",{{scaleY:0,transformOrigin:"50% 0%"}},{{scaleY:1,transformOrigin:"50% 0%",duration:0.8,ease:"power2.inOut"}},{t_separate + 0.5:.2f});
  {"".join(f'tl.fromTo("#{p}-bar{k}",{{scaleX:0.05,transformOrigin:"0% 50%"}},{{scaleX:1,transformOrigin:"0% 50%",duration:0.6,ease:"power2.out"}},{t_ai + 0.18 * k:.2f});' for k in range(4))}
  tl.fromTo("#{p}-pointer",{{opacity:1}},{{opacity:0,duration:0.25,repeat:13,yoyo:true,ease:"steps(1)"}},{t_ai + 0.4:.2f});
  sr("#{p}-s1", {t_actually:.2f}, 104);
  tl.fromTo("#{p}-bar0",{{scaleX:1}},{{scaleX:1.12,duration:0.3,repeat:1,yoyo:true,immediateRender:false}},{t_does:.2f});
  tl.fromTo("#{p}-cloudW",{{opacity:0,scale:0.4,transformOrigin:"20% 90%"}},{{opacity:1,scale:1,transformOrigin:"20% 90%",duration:0.8,ease:"elastic.out(1,0.5)"}},{t_imagine - 0.25:.2f});
  tl.fromTo("#{p}n-eyes",{{opacity:0.2}},{{opacity:1,duration:0.1,repeat:4,yoyo:true,ease:"steps(1)"}},{t_imagine + 0.5:.2f});
  sr("#{p}-s2", {t_imagine:.2f}, 120);
  tl.fromTo("#{p}p-eye",{{x:0,y:0}},{{x:2,y:-3,duration:0.4}},{t_imagine - 0.3:.2f});
""" + idle(p + "p", dur, (13.5, 15.4, 17.6)) + idle(p + "-gz", dur, (2.2, 4.4, 7.0)) + f'tl.fromTo("#{p}-coverbot",{{y:0}},{{y:-10,duration:0.9,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_title + 1.4:.2f});'
    return scene(p, dur, svg, html, js, extra, seed=7)


# ================================================================ robot 8: people are the ones who decide
def robot_8():
    p, C, S = "robot_8", "robot", 8
    start, dur = seg(C, S)
    t_separation, t_picture, t_no, t_machine, t_evil = 2.05, 3.57, 4.58, 7.89, 8.08
    t_labs, t_companies, t_platforms, t_people, t_decided, t_test, t_show, t_keep = 9.42, 10.63, 11.42, 12.82, 13.6, 14.63, 16.25, 17.0
    extra = (ground(p, color="#2a2878") + f'<linearGradient id="{p}-bldg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c2a88"/><stop offset="1" stop-color="#16124a"/></linearGradient>'
             f'<clipPath id="{p}-cl"><rect x="-400" y="-400" width="400" height="800"/></clipPath><clipPath id="{p}-cr"><rect x="0" y="-400" width="400" height="800"/></clipPath>')

    def windows(x0, y0, nc, nr, dx, dy, w, h, cls):
        out = ""
        for r in range(nr):
            for c in range(nc):
                x, y = x0 + c * dx, y0 + r * dy
                out += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#0e0c26"/><rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#ffe39a" opacity="0"/>'
        return out
    lab_svg = (f'<g id="{p}-lab"><rect x="150" y="470" width="440" height="330" fill="url(#{p}-bldg)" stroke="#8d7bff" stroke-width="5"/>'
           f'<polygon points="126,472 614,472 530,404 210,404" fill="#2a1d70" stroke="#8d7bff" stroke-width="5" stroke-linejoin="round"/>'
           f'{windows(196, 516, 3, 2, 134, 104, 90, 70, p + "-labwin")}<rect x="330" y="720" width="80" height="80" fill="#0e0c26" stroke="#8d7bff" stroke-width="4"/>'
           f'<g transform="translate(370 336)"><path d="M-46 30 L46 30 L60 50 Q66 64 50 64 L-50 64 Q-66 64 -60 50 Z" fill="{MINT}" opacity=".35" id="{p}-liq"/>'
           f'<path d="M-30 -66 L30 -66 M-18 -66 L-18 -18 L-60 50 Q-66 64 -50 64 L50 64 Q66 64 60 50 L18 -18 L18 -66" fill="none" stroke="{MINT}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round" filter="url(#{p}-glow)"/>'
           f'<g id="{p}-bubbles" opacity="0" fill="{MINT}"><circle cx="-14" cy="20" r="8"/><circle cx="12" cy="0" r="6"/><circle cx="0" cy="-30" r="5"/></g></g></g>')
    company = (f'<g id="{p}-company"><rect x="740" y="300" width="440" height="500" fill="url(#{p}-bldg)" stroke="{CYAN}" stroke-width="5"/>'
           f'<rect x="790" y="276" width="340" height="26" fill="#2a1d70" stroke="{CYAN}" stroke-width="4"/><line x1="960" y1="276" x2="960" y2="226" stroke="{CYAN}" stroke-width="5"/>'
           f'<circle id="{p}-antenna" cx="960" cy="220" r="10" fill="{RED}"/>'
           f'<rect x="784" y="334" width="352" height="190" rx="12" fill="#0e0c26" stroke="{CYAN}" stroke-width="5"/>'
           f'<g id="{p}-screen" opacity="0"><rect x="806" y="354" width="96" height="150" rx="8" fill="{MAGENTA}"/><rect x="914" y="354" width="96" height="150" rx="8" fill="{CYAN}"/><rect x="1022" y="354" width="96" height="150" rx="8" fill="{AMBER}"/></g>'
           f'{windows(790, 560, 4, 3, 90, 78, 60, 50, p + "-cowin")}</g>')
    leds = "".join(f'<rect class="{p}-led" x="{1372 + c * 140 + j * 30}" y="{482 + r * 36}" width="20" height="10" rx="3" fill="{CYAN if (r + j + c) % 3 else AMBER}" opacity=".25"/>'
                   for c in range(3) for r in range(8) for j in range(3))
    racks = "".join(f'<rect x="{1360 + c * 140}" y="466" width="120" height="310" rx="8" fill="#0e0c26" stroke="#5a5ad0" stroke-width="3"/>' for c in range(3))
    platform = (f'<g id="{p}-platform"><rect x="1330" y="430" width="440" height="370" fill="url(#{p}-bldg)" stroke="{MAGENTA}" stroke-width="5"/>'
           f'<rect x="1310" y="414" width="480" height="22" fill="#2a1d70" stroke="{MAGENTA}" stroke-width="4"/>'
           f'{racks}{leds}'
           f'<g transform="translate(1550 640)"><g id="{p}-lock" opacity="0"><path d="M-44 -30 L-44 -70 A44 44 0 0 1 44 -70 L44 -30" fill="none" stroke="{AMBER}" stroke-width="16" filter="url(#{p}-glow)"/>'
           f'<rect x="-70" y="-34" width="140" height="110" rx="16" fill="{AMBER}" stroke="#fff3c4" stroke-width="4"/><circle cy="10" r="14" fill="#5a3f1a"/><rect x="-5" y="12" width="10" height="34" fill="#5a3f1a"/></g></g></g>')
    people = ""
    # who decides: the researcher in a lab coat, the executive in a suit, the dev in a hoodie, each one left of their building
    types = [dict(variant="work", skin=1, hair="#140c08"), dict(variant="work", skin=0, outfit=("#2a2f5a", "#1c2048")),
             dict(variant="home", skin=2, hair="#140c08", outfit=("#d0408a", "#a02a68"))]
    for k, cx in enumerate((168, 662, 1250)):
        people += (f'<g transform="translate({cx} 862) scale(.7)"><g id="{p}-pw{k}" opacity="0">{figure_var(f"{p}{k}", glow=p + "-glow", **types[k])}</g></g>')
    rob = robot(p + "L", p + "-glow"), robot(p + "R", p + "-glow")
    svg = f"""<rect x="-300" y="800" width="2520" height="400" fill="url(#{p}-floor)"/>
<g id="{p}-buildings" opacity="0">{lab_svg}{company}{platform}</g>
<g transform="translate(960 520) scale(1.2)"><g id="{p}-hL"><g clip-path="url(#{p}-cl)">{rob[0]}</g><path d="M0 -340 L-10 -200 L8 -60 L-8 80 L6 300" fill="none" stroke="#fff" stroke-width="7" stroke-linejoin="round" filter="url(#{p}-glow)"/></g>
<g id="{p}-hR"><g clip-path="url(#{p}-cr)">{rob[1]}</g><path d="M0 -340 L-10 -200 L8 -60 L-8 80 L6 300" fill="none" stroke="#fff" stroke-width="7" stroke-linejoin="round" filter="url(#{p}-glow)"/></g></g>
<line id="{p}-split" x1="960" y1="90" x2="960" y2="900" stroke="#ffffff" stroke-width="8" stroke-linecap="round" filter="url(#{p}-glow)" opacity="0"/>
{people}"""

    def swap(i, cx, a, b, color):
        sty = f"position:absolute;left:{cx - 300}px;width:600px;top:884px;height:1.3em;line-height:1.3em;overflow:hidden;text-align:center;{PLEX};font-size:64px;color:{color};text-shadow:0 0 18px {color}"
        return (f'<div style="{sty}"><span id="{p}-n{i}" style="display:block;position:absolute;left:0;right:0">{a}</span>'
                f'<span id="{p}-v{i}" style="display:block;position:absolute;left:0;right:0">{b}</span></div>')
    html = (swap(0, 370, "LABS", "TEST", MINT) + swap(1, 960, "COMPANIES", "SHOW", CYAN) + swap(2, 1550, "PLATFORMS", "KEEP", "#ff8ac4") +
            text(f"{p}-t1", "PEOPLE", "left:0;right:0;text-align:center;top:40px;font-size:130px;color:#ffd98a"))
    light_up = []
    for i, (t, sel) in enumerate(((t_labs, "lab"), (t_companies, "company"), (t_platforms, "platform"))):
        light_up.append(f'tl.fromTo("#{p}-{sel}",{{opacity:0.3}},{{opacity:1,duration:0.35,immediateRender:false}},{t_labs + 0.12 * i:.2f});'
                      f'tl.fromTo("#{p}-{sel}",{{y:30}},{{y:0,duration:0.7,ease:"elastic.out(1,0.5)",immediateRender:false}},{t:.2f});'
                      f'rise("#{p}-n{i}", {t:.2f});')
    js = f"""
  camZ("#{p}-cam", 0, 3.0, 1.1, 1.0, 960, 520);
  camZ("#{p}-cam", 3.0, {dur - 3.0:.2f}, 1.0, 1.04, 960, 560, "sine.inOut");
  tl.fromTo("#{p}-hL",{{y:0}},{{y:-8,duration:1.0,repeat:1,yoyo:true,ease:"sine.inOut"}},0);
  tl.fromTo("#{p}-hR",{{y:0}},{{y:-8,duration:1.0,repeat:1,yoyo:true,ease:"sine.inOut"}},0);
  tl.fromTo("#{p}-split",{{opacity:1,scaleY:0,transformOrigin:"50% 0%"}},{{scaleY:1,transformOrigin:"50% 0%",duration:0.7,ease:"power2.inOut"}},{t_separation:.2f});
  vanish("#{p}-split", {t_picture + 0.2:.2f}, 0.4);
  tl.fromTo("#{p}-hL",{{x:0}},{{x:-360,duration:1.6,ease:"power3.out",immediateRender:false}},{t_picture:.2f});
  tl.fromTo("#{p}-hR",{{x:0}},{{x:360,duration:1.6,ease:"power3.out",immediateRender:false}},{t_picture:.2f});
  tl.fromTo("#{p}-buildings",{{opacity:0}},{{opacity:0.3,duration:1.0}},{t_picture:.2f});
  tl.to(["#{p}L-eyes","#{p}R-eyes"],{{opacity:0,duration:0.12,repeat:4,yoyo:true,ease:"steps(1)"}},{t_machine:.2f});
  tl.to(["#{p}L-eyes","#{p}R-eyes"],{{opacity:0,duration:0.2}},{t_evil + 0.5:.2f});
  tl.to("#{p}-hL",{{x:-700,opacity:0,duration:0.7,ease:"power2.in"}},{t_evil + 0.4:.2f}); tl.to("#{p}-hR",{{x:700,opacity:0,duration:0.7,ease:"power2.in"}},{t_evil + 0.4:.2f});
  tl.set("#{p}-buildings",{{opacity:1}},{t_labs - 0.01:.2f});
  tl.set(["#{p}-lab","#{p}-company","#{p}-platform"],{{opacity:0.3}},{t_labs - 0.01:.2f});
  {"".join(light_up)}
  tl.fromTo(".{p}-labwin",{{opacity:0}},{{opacity:0.85,duration:0.2,stagger:0.04}},{t_labs + 0.05:.2f});
  tl.fromTo(".{p}-cowin",{{opacity:0}},{{opacity:1,duration:0.15,stagger:0.02}},{t_labs + 0.15:.2f});
  tl.fromTo(".{p}-led",{{opacity:0.25}},{{opacity:1,duration:0.1,stagger:{{each:0.003,from:"random"}}}},{t_labs + 0.25:.2f});
  tl.fromTo("#{p}-screen",{{opacity:0}},{{opacity:0.9,duration:0.3}},{t_labs + 0.15:.2f});
  tl.fromTo(".{p}-cowin",{{opacity:1}},{{opacity:0.4,duration:0.12,repeat:3,yoyo:true,ease:"steps(1)",immediateRender:false}},{t_companies:.2f});
  tl.fromTo(".{p}-led",{{opacity:1}},{{opacity:0.3,duration:0.1,repeat:3,yoyo:true,ease:"steps(1)",immediateRender:false}},{t_platforms:.2f});
  rise("#{p}-t1 span", {t_people:.2f}, 0.9);
  {"".join(f'pop("#{p}-pw{k}", {t_people + 0.15 * k:.2f}, 0.4, 0.8);' for k in range(3))}
  {"".join(f'exit_up("#{p}-n{i}", {t:.2f}); rise("#{p}-v{i}", {t + 0.2:.2f});' for i, t in enumerate((t_test, t_show, t_keep)))}
  tl.fromTo("#{p}-liq",{{opacity:0.35}},{{opacity:1,duration:0.25,repeat:3,yoyo:true}},{t_test:.2f});
  enter("#{p}-bubbles", {t_test:.2f}, 0.2); tl.fromTo("#{p}-bubbles",{{y:0}},{{y:-40,duration:0.6,repeat:3,ease:"power1.out"}},{t_test:.2f});
  tl.fromTo("#{p}-screen",{{opacity:0.9,scale:0.8,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.6,ease:"elastic.out(1,0.45)",immediateRender:false}},{t_show:.2f});
  pop("#{p}-lock", {t_keep:.2f}, 1.8, 0.5);
  tl.to(".{p}-led",{{fill:"{AMBER}",duration:0.3}},{t_keep + 0.2:.2f});
  tl.fromTo("#{p}-antenna",{{opacity:1}},{{opacity:0.2,duration:0.3,repeat:{int(dur / 0.6) - 1},yoyo:true,ease:"steps(1)"}},0);
  {"".join(f'tl.fromTo("#{p}{k}-eye",{{x:0,y:0}},{{x:2,y:-3,duration:0.3,immediateRender:false}},{t_decided:.2f});' for k in range(3))}
""" + "".join(idle(f"{p}{k}", dur, (13.6 + k * 0.4, 15.8 + k * 0.3, 17.2)) for k in range(3))
    return scene(p, dur, svg, html, js, extra, seed=8)


# ================================================================ robot 9: whoever holds the key has a name
def robot_9():
    p, C, S = "robot_9", "robot", 9
    start, dur = seg(C, S)
    t_robot, t_distraction, t_who, t_holds, t_key, t_name, t_address, t_model = 0.25, 1.31, 2.85, 2.98, 3.54, 4.18, 4.66, 5.57
    extra = (ground(p) + beam_def(p) + f'<linearGradient id="{p}-fxr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{RED}" stop-opacity=".45"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></linearGradient>'
             f'<linearGradient id="{p}-paper" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#e9dcc2"/></linearGradient>')
    owner = dict(variant="work", skin=0, outfit=("#2a2f5a", "#1c2048"))   # who holds the key: the same person as in the badge photo
    HAND = anchors("work")["hand_l"]   # hand on the right side of the screen; the key goes behind the person and the fingers cover the top of the ring
    field = lambda y, w: f'<rect x="1384" y="{y}" width="{w}" height="8" rx="4" fill="#bfb49a"/>'
    badge = (f'<rect x="1100" y="430" width="720" height="470" rx="30" fill="url(#{p}-paper)" stroke="{AMBER}" stroke-width="7" filter="url(#{p}-shadow)"/>'
              f'<rect x="1100" y="430" width="720" height="56" rx="28" fill="{AMBER}"/><rect x="1100" y="458" width="720" height="28" fill="{AMBER}"/>'
              f'<rect x="1420" y="404" width="80" height="44" rx="12" fill="#bfb49a" stroke="#8a7f68" stroke-width="4"/>'
              f'<rect x="1140" y="516" width="210" height="236" rx="16" fill="#14123a" stroke="#8d7bff" stroke-width="5"/>'
              f'<g clip-path="url(#{p}-photo)"><rect x="1140" y="516" width="210" height="236" fill="#3a2f8a"/>{portrait(p + "f", 1245, 646, 1.15, glow=p + "-glow", **owner)}</g>'
              f'{field(612, 390)}{field(712, 390)}<rect x="1140" y="862" width="640" height="8" rx="4" fill="#bfb49a"/>'
              f'{srise(p + "-r1", 1384, 584, "NAME", 50, "#2a1d70", family="IBM Plex Mono", weight=600, align="start", spacing=6, outline=False)}'
              f'{srise(p + "-r2", 1384, 684, "ADDRESS", 50, "#2a1d70", family="IBM Plex Mono", weight=600, align="start", spacing=6, outline=False)}'
              f'{srise(p + "-r3", 1140, 834, "BUSINESS MODEL", 50, "#a01a48", family="IBM Plex Mono", weight=600, align="start", spacing=6, outline=False)}')
    extra += f'<clipPath id="{p}-photo"><rect x="1140" y="516" width="210" height="236" rx="16"/></clipPath>'
    svg = f"""<rect x="-300" y="930" width="2520" height="400" fill="url(#{p}-floor)"/>
<polygon id="{p}-fr" points="300,-40 640,-40 800,930 140,930" fill="url(#{p}-fxr)"/>
<polygon id="{p}-sparks" points="1090,-40 1410,-40 1650,930 850,930" fill="url(#{p}-fx)" opacity="0"/>
<ellipse cx="470" cy="932" rx="300" ry="20" fill="#05031a" opacity=".55"/>
<g transform="translate(470 600) scale(1.1)"><g id="{p}-rob"><g id="{p}-robS">{robot(p, p + "-glow")}</g></g></g>
<g transform="translate(-280 0)"><g id="{p}-badgeW" opacity="0">{badge}</g></g>
<ellipse cx="1716" cy="932" rx="130" ry="14" fill="#05031a" opacity=".55"/>
<g transform="translate(1700 930) scale(.82)"><g id="{p}-exW" opacity="0">
<g transform="translate({HAND[0] + 12:.1f} {HAND[1] + 32:.1f}) scale(1.1)"><g id="{p}-key">{key(p + "-glow")}</g></g>
{figure_var(p + "g", glow=p + "-glow", shadow=False, **owner)}</g></g>"""
    html = text(f"{p}-t1", "DISTRACTION", "left:100px;top:60px;font-size:130px;color:#ff8aa6")
    js = f"""
  camZ("#{p}-cam", 0, {t_who:.2f}, 1.08, 1.0, 470, 600, "sine.inOut");
  camZ("#{p}-cam", {t_who:.2f}, {dur - t_who:.2f}, 1.0, 1.05, 1200, 660, "power2.inOut");
  tl.fromTo("#{p}-eyes",{{opacity:0.3}},{{opacity:1,duration:0.1,repeat:4,yoyo:true,ease:"steps(1)"}},{t_robot:.2f});
  tl.to("#{p}-robS",{{scale:0.62,transformOrigin:"50% 100%",duration:1.0,ease:"power3.inOut"}},{t_distraction:.2f});
  tl.to("#{p}-rob",{{opacity:0.4,duration:0.8}},{t_distraction + 0.3:.2f});
  tl.to("#{p}-eyes",{{opacity:0,duration:0.4}},{t_distraction + 0.5:.2f});
  rise("#{p}-t1 span", {t_distraction:.2f}, 0.8);
  tl.to("#{p}-fr",{{opacity:0,duration:0.6}},{t_who - 0.3:.2f});
  tl.fromTo("#{p}-sparks",{{opacity:0}},{{opacity:1,duration:0.7}},{t_who - 0.2:.2f});
  tl.fromTo("#{p}-badgeW",{{opacity:0,y:-900}},{{opacity:1,y:0,duration:0.9,ease:"bounce.out"}},{t_holds:.2f});
  tl.fromTo("#{p}-exW",{{opacity:0,x:260}},{{opacity:1,x:0,duration:0.7,ease:"power3.out"}},{t_who - 0.2:.2f});
  tl.fromTo("#{p}-key",{{rotation:-3,svgOrigin:"0 -30"}},{{rotation:-15,svgOrigin:"0 -30",duration:0.5,repeat:5,yoyo:true,ease:"sine.inOut"}},{t_key:.2f});
  sr("#{p}-r1", {t_name:.2f}, 66); sr("#{p}-r2", {t_address:.2f}, 66); sr("#{p}-r3", {t_model:.2f}, 66);
""" + idle(p + "f", dur, (4.8, 7.2)) + idle(p + "g", dur, (3.2, 6.0))
    return scene(p, dur, svg, html, js, extra, background=("#2a1560", "#150d40", "#07061a"), seed=9)


# ================================================================ closing 0: so, who has the key?
PLATE0 = (960, 400)   # lock center in closing 0


def closing_0():
    p, C, S = "closing_0", "closing", 0
    start, dur = seg(C, S)
    t_who, t_key = 0.6, 1.28
    svg = f"""<polygon id="{p}-beam" points="700,-40 1220,-40 1360,820 560,820" fill="url(#{p}-fx)" opacity="0"/>
<ellipse cx="960" cy="690" rx="250" ry="24" fill="#05031a" opacity=".45"/>
<g transform="translate(420 400) rotate(-90) scale(2.2)"><g id="{p}-key" opacity="0">{key(p + "-glow")}</g></g>
<g transform="translate({PLATE0[0]} {PLATE0[1]})"><g id="{p}-plate" opacity="0">{plate(p, p + "-glow", 230)}</g></g>"""
    html = text(f"{p}-t1", "WHO HAS THE KEY?", "left:0;right:0;text-align:center;top:760px;font-size:124px;color:#ffe9c4")
    js = f"""
  camZ("#{p}-cam", 0, {dur:.2f}, 1.0, 1.16, {PLATE0[0]}, {PLATE0[1]}, "sine.inOut");
  tl.fromTo("#{p}-beam",{{opacity:0}},{{opacity:1,duration:0.6}},0.05);
  pop("#{p}-plate", 0.1, 0.6, 0.8);
  tl.fromTo("#{p}-key",{{opacity:0,y:-220}},{{opacity:1,y:0,duration:0.9,ease:"power3.out"}},0.3);
  rise("#{p}-t1 span", {t_who:.2f}, 0.8);
  tl.fromTo("#{p}-light",{{opacity:0}},{{opacity:0.75,duration:0.25,repeat:1,yoyo:true}},{t_key:.2f});
  tl.fromTo("#{p}-key",{{x:0}},{{x:-10,duration:0.3,repeat:1,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_key + 0.1:.2f});
"""
    return scene(p, dur, svg, html, js, beam_def(p), background=("#2a1560", "#150d40", "#07061a"), seed=17)


# ================================================================ closing 1: the technology arrived before the question
def head_with_lock(p, tx, ty, s, r_plate=22):
    """The big person; the lock goes on the back of the head, over the brain. Returns (svg, plate center, plate radius in px)."""
    cx, cy = tx + 160 * s, ty + 82 * s
    return person(p + "h", tx, ty, s, glow=p + "-glow"), (cx, cy), r_plate * s


def closing_1():
    p, C, S = "closing_1", "closing", 1
    start, dur = seg(C, S)
    t_memory, t_mapping, t_brain, t_reading, t_thinks, t_choosing, t_sees = 0.61, 1.6, 2.45, 3.53, 4.7, 5.6, 7.14
    t_every, t_technology, t_arrived, t_before, t_question, t_first, t_manages, t_then, t_asks, t_should = (7.65, 9.77, 10.2, 10.4, 10.78,
                                                                            11.6, 12.6, 13.6, 14.7, 16.08)
    s, hx, hy = 3.1, 464, 146
    head_svg, (pcx, pcy), r = head_with_lock(p, hx, hy, s)
    L = lambda u, v: (hx + u * s, hy + v * s)   # person local point -> screen
    bcx, bcy = L(192, 90)                       # brain center
    z0 = 230 / r
    sk = 2.2 / z0                     # key scale equal to closing 0 in the first frame
    kx = pcx + (420 - PLATE0[0]) / z0    # key ring in the same relative place
    # mesh (mapping) over the brain
    rng = random.Random(11)
    pts = []
    while len(pts) < 34:
        x, y = rng.uniform(-1, 1), rng.uniform(-1, 1)
        if x * x + y * y < 0.85:
            pts.append((bcx + x * 51.5 * s, bcy + y * 32 * s))
    links = "".join(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}"/>'
                  for i, a in enumerate(pts) for b in pts[i + 1:] if (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 < 70 ** 2)
    mesh = (f'<g id="{p}-mesh" opacity="0"><g stroke="{CYAN}" stroke-width="2.5" opacity=".7">{links}</g>'
             + "".join(f'<circle class="{p}-node" cx="{x:.0f}" cy="{y:.0f}" r="7" fill="{CYAN}" filter="url(#{p}-glow)"/>' for x, y in pts) + '</g>')
    ex, ey = L(257 + 9, 129)   # front tip of the eye (engine.person: eye at 257,129, rx 9)
    screen_svg = (f'<g id="{p}-screen" opacity="0"><path d="M{ex:.0f} {ey:.0f} L1450 410 M{ex:.0f} {ey:.0f} L1450 740" stroke="{MAGENTA}" stroke-width="4" stroke-dasharray="14 12" opacity=".8"/>'
            f'<rect x="1450" y="400" width="330" height="350" rx="22" fill="#0e0c26" stroke="{MAGENTA}" stroke-width="7" filter="url(#{p}-shadow)"/>'
            f'<rect x="1478" y="428" width="274" height="90" rx="10" fill="{MAGENTA}"/><rect x="1478" y="532" width="274" height="90" rx="10" fill="{CYAN}" opacity=".85"/>'
            f'<rect x="1478" y="636" width="274" height="90" rx="10" fill="{AMBER}" opacity=".85"/></g>')
    waves = "".join(f'<path id="{p}-wave{k}" d="M{L(177, 50)[0] + k * 60:.0f} {L(177, 50)[1] - k * 6:.0f} q 30 -40 60 0 t 60 0 t 60 0 t 60 0" fill="none" stroke="{LILAC}" stroke-width="6" stroke-linecap="round" '
                    f'stroke-dasharray="300" stroke-dashoffset="300" filter="url(#{p}-glow)" transform="translate(0 {-k * 40})"/>' for k in range(3))
    steps = [("WRITING", AMBER), ("MAPPING", CYAN), ("READING", LILAC), ("CHOOSING", MAGENTA)]
    ICONS = {"WRITING": '<path d="M -22 22 L -18 6 L 12 -24 L 26 -10 L -4 20 Z" fill="#fff"/><path d="M -22 22 L -4 20 L -18 6 Z" fill="#05031a" opacity=".35"/>',
            "MAPPING": '<g stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round"><circle r="24"/><path d="M -24 0 H 24 M 0 -24 V 24 M -14 -17 Q 0 0 -14 17 M 14 -17 Q 0 0 14 17"/></g>',
            "READING": '<path d="M -28 0 Q 0 -26 28 0 Q 0 26 -28 0 Z" fill="none" stroke="#fff" stroke-width="5"/><circle r="9" fill="#fff"/>',
            "CHOOSING": '<path d="M -24 -2 L -8 16 L 26 -20" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>'}
    orbs_v = "".join(f'<g id="{p}-ob{k}" opacity="0"><g transform="translate(170 {300 + 150 * k})"><g id="{p}-obi{k}"><circle r="72" fill="{c}" fill-opacity=".38" stroke="{c}" stroke-width="6" filter="url(#{p}-glow)"/>'
                     f'<circle r="60" fill="{c}" fill-opacity=".25"/><circle cx="-22" cy="-26" r="11" fill="#fff" opacity=".5"/><g transform="scale(1.5)">{ICONS[w]}</g></g></g></g>' for k, (w, c) in enumerate(steps))
    # labels inside the art, next to the orbs: in HTML they stayed outside the camera and drifted when it zoomed
    labels_svg = "".join(f'<g id="{p}-l{k}"><circle id="{p}-ld{k}" cx="290" cy="{300 + 150 * k}" r="10" fill="{c}" opacity="0" filter="url(#{p}-glow)"/>'
                      + srise(f"{p}-lt{k}", 320, 300 + 150 * k + 20, w, 56, c, family="IBM Plex Mono", weight=500, align="start", spacing=7.8, outline=False) + '</g>'
                      for k, (w, c) in enumerate(steps))
    svg = f"""<ellipse cx="{L(200, 0)[0]:.0f}" cy="{L(0, 256)[1]:.0f}" rx="300" ry="20" fill="#05031a" opacity=".45"/>
<g id="{p}-person">{head_svg}</g>
<circle id="{p}-flash" cx="{L(209, 92)[0]:.0f}" cy="{L(209, 92)[1]:.0f}" r="150" fill="{AMBER}" opacity="0" filter="url(#{p}-blur40)"/>
<g transform="translate({L(220, 36)[0]:.0f} {L(220, 36)[1]:.0f})"><g id="{p}-lightning" opacity="0">{bolt(0, 0, 1.5)}</g></g>
{mesh}
<clipPath id="{p}-brainclip"><ellipse cx="{bcx:.0f}" cy="{bcy:.0f}" rx="{59 * s:.0f}" ry="{40 * s:.0f}"/></clipPath>
<g clip-path="url(#{p}-brainclip)"><rect id="{p}-scan" x="{L(127, 48)[0]:.0f}" y="{L(127, 48)[1]:.0f}" width="22" height="{88 * s:.0f}" fill="{LILAC}" opacity="0" filter="url(#{p}-glow)"/></g>
<g id="{p}-waves">{waves}</g>
{screen_svg}{orbs_v}{labels_svg}
<g id="{p}-lockW"><g transform="translate({kx:.1f} {pcy:.1f}) rotate(-90) scale({sk:.4f})"><g id="{p}-keyW"><g id="{p}-key">{key(p + "-glow")}</g></g></g>
<g transform="translate({pcx:.1f} {pcy:.1f}) scale({r / 230:.4f})">{plate(p + "b", p + "-glow", 230)}</g></g>
<g transform="translate(1540 880) scale(.64)"><g id="{p}-r1W" opacity="0">{figure_var(p + "-r1", "work", glow=p + "-glow", skin=2, hair="#140c08")}</g></g>
<g transform="translate(1750 880) scale(.64)"><g id="{p}-r2W" opacity="0">{figure_var(p + "-r2", "home", glow=p + "-glow", skin=1, hair="#c99a3a", outfit=("#2fa88a", "#1f8068"))}</g></g>
<g transform="translate(1730 330)"><g id="{p}-q" opacity="0"><text x="0" y="60" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="210" fill="{MAGENTA}" stroke="#05031a" stroke-width="12" paint-order="stroke" filter="url(#{p}-glow)">?</text></g></g>"""

    html = (text(f"{p}-a1", "BEFORE THE", "left:100px;top:230px;font-size:112px;color:#eef1f7") +
             text(f"{p}-a2", "QUESTION", "left:100px;top:360px;font-size:112px;color:#ffb3c6") +
             mono(f"{p}-a3", "FIRST", "left:100px;top:560px", AMBER, 60) +
             mono(f"{p}-a4", "THEN", "left:100px;top:660px", MAGENTA, 60))
    label_times = [0.0, t_mapping, t_reading, t_choosing]
    js = f"""
  camZ("#{p}-cam", 0, 2.3, {z0:.3f}, 1.0, {pcx:.1f}, {pcy:.1f}, "power3.inOut");
  camZ("#{p}-cam", 2.4, {t_arrived - 2.6:.2f}, 1.0, 1.04, 1060, 520, "sine.inOut");
  camZ("#{p}-cam", {t_arrived + 0.2:.2f}, 1.6, 1.04, 1.16, {pcx:.1f}, {pcy:.1f});
  camZ("#{p}-cam", {t_then - 0.2:.2f}, 1.4, 1.16, 1.0, 960, 500);
  {"".join(f'sr("#{p}-lt{k}", {t:.2f}, 73); tl.fromTo("#{p}-ld{k}",{{opacity:0}},{{opacity:1,duration:0.3}},{t:.2f}); pop("#{p}-ob{k}", {t:.2f}, 0.5, 0.8);' for k, t in enumerate(label_times))}
  tl.to("#{p}-lockW",{{opacity:0,duration:0.5}},2.0);
  tl.to("#{p}-person",{{opacity:0.35,duration:0.5}},{t_technology - 0.4:.2f});
  tl.to("#{p}-mesh",{{opacity:0,duration:0.4}},{t_technology - 0.4:.2f});
  tl.fromTo("#{p}-lockW",{{opacity:0}},{{opacity:1,duration:0.5,immediateRender:false}},{t_technology - 0.1:.2f});
  tl.fromTo("#{p}-lightning",{{opacity:0,y:-160}},{{opacity:1,y:0,duration:0.35,ease:"power4.in"}},{t_memory - 0.3:.2f});
  tl.fromTo("#{p}-flash",{{opacity:0}},{{opacity:0.7,duration:0.2,repeat:1,yoyo:true}},{t_memory + 0.05:.2f});
  tl.to("#{p}-lightning",{{opacity:0,duration:0.4}},{t_mapping:.2f});
  enter("#{p}-mesh", {t_mapping:.2f}, 0.2);
  tl.fromTo(".{p}-node",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,transformOrigin:"50% 50%",duration:0.4,ease:"back.out(3)",stagger:0.03}},{t_mapping:.2f});
  tl.to("#{p}-mesh",{{opacity:0.35,duration:0.5}},{t_reading:.2f});
  tl.fromTo("#{p}-scan",{{opacity:1,x:0}},{{x:{123 * s:.0f},duration:0.8,repeat:1,yoyo:true,ease:"sine.inOut"}},{t_reading:.2f});
  tl.to("#{p}-scan",{{opacity:0,duration:0.3}},{t_choosing:.2f});
  {"".join(f'draw("#{p}-wave{k}", {t_reading + 0.3 + 0.25 * k:.2f}, 0.8, 300);' for k in range(3))}
  pop("#{p}-screen", {t_choosing:.2f}, 0.5, 0.8);
  tl.fromTo("#{p}h-eye",{{x:0}},{{x:3,duration:0.3}},{t_choosing:.2f});
  {"".join(f'tl.fromTo("#{p}-l{k}",{{opacity:1}},{{opacity:0.35,duration:0.12,repeat:3,yoyo:true,ease:"steps(1)",immediateRender:false}},{t_every + 0.12 * k:.2f});' for k in range(4))}
  tl.fromTo("#{p}-flash",{{opacity:0}},{{opacity:0.45,duration:0.3,repeat:1,yoyo:true,immediateRender:false}},{t_every:.2f});
  {"".join(f'vanish("#{p}-l{k}", {t_technology - 0.2:.2f}, 0.4); vanish("#{p}-ob{k}", {t_technology - 0.2:.2f}, 0.4);' for k in range(4))}
  tl.to("#{p}-screen",{{opacity:0,duration:0.5}},{t_technology - 0.2:.2f}); tl.to("#{p}-waves",{{opacity:0.25,duration:0.5}},{t_technology - 0.2:.2f});
  tl.to("#{p}-keyW",{{y:{(pcx - kx - 130 * sk + 12) / sk:.1f},duration:0.7,ease:"power2.in"}},{t_arrived:.2f});
  rise("#{p}-a1 span", {t_before:.2f}, 0.8); rise("#{p}-a2 span", {t_question:.2f}, 0.8);
  rise("#{p}-a3 span", {t_first:.2f});
  tl.fromTo("#{p}-key",{{scaleX:1,transformOrigin:"50% 50%"}},{{scaleX:0.12,duration:0.45,ease:"power2.inOut"}},{t_manages - 0.2:.2f});
  tl.fromTo("#{p}b-light",{{opacity:0}},{{opacity:1,duration:0.4}},{t_manages:.2f});
  tl.fromTo("#{p}-flash",{{opacity:0}},{{opacity:0.55,duration:0.5,immediateRender:false}},{t_manages:.2f});
  vanish("#{p}-a1", {t_then - 0.3:.2f}, 0.4); vanish("#{p}-a2", {t_then - 0.3:.2f}, 0.4);
  rise("#{p}-a4 span", {t_then:.2f});
  pop("#{p}-r1W", {t_first:.2f}, 0.5, 0.8);
  tl.fromTo("#{p}-r1-arm",{{rotation:0,svgOrigin:"{pivot("work")}"}},{{rotation:-150,svgOrigin:"{pivot("work")}",duration:0.5,ease:"back.out(2)"}},{t_manages:.2f});
  tl.fromTo("#{p}-r1W",{{y:0}},{{y:-40,duration:0.22,repeat:1,yoyo:true,ease:"power2.out",immediateRender:false}},{t_manages + 0.1:.2f});
  pop("#{p}-r2W", {t_then + 0.2:.2f}, 0.5, 0.8);
  tl.fromTo("#{p}-r2-eye",{{x:0,y:0}},{{x:1,y:-3,duration:0.3}},{t_asks:.2f});
  tl.fromTo("#{p}-q",{{opacity:0,y:-160,rotation:-30,transformOrigin:"50% 50%"}},{{opacity:1,y:0,rotation:0,transformOrigin:"50% 50%",duration:0.9,ease:"back.out(1.6)"}},{t_asks - 0.2:.2f});
  tl.fromTo("#{p}-q",{{rotation:0}},{{rotation:-12,duration:0.25,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_should:.2f});
""" + person_idle(p + "h", dur, (1.2, 4.4, 8.3, 12.0, 15.2)) + idle(p + "-r1", dur, (12.9, 15.6)) + idle(p + "-r2", dur, (15.0,))
    return scene(p, dur, svg, html, js, background=("#2a1560", "#150d40", "#07061a"), seed=18)


# ================================================================ closing 2: new rights for the mind
def closing_2():
    p, C, S = "closing_2", "closing", 2
    start, dur = seg(C, S)
    t_researchers, t_argue, t_new, t_rights = 0.71, 2.14, 3.12, 4.14
    t_privacy, t_liberty, t_integrity = 5.34, 6.7, 8.33
    t_right, t_no_one, t_inside, t_head, t_without, t_knowing = 10.34, 11.15, 11.86, 12.97, 13.58, 14.79
    # the person in home clothes, in the armchair, with the pictures of their life on the wall and the memories around the head
    gx, gy, gs = 1250, 880, 1.1
    hc = anchors("home", "sitting")["head_center"]
    hx, hy = gx + hc[0] * gs, gy + hc[1] * gs      # head center of the seated person (for the dive)
    CX, CY = 1370, 540                              # dome center
    colors = (CYAN, LILAC, MINT)
    rings = "".join(f'<circle id="{p}-ring{k}" cx="{CX}" cy="{CY}" r="{380 + 45 * k}" fill="none" stroke="{c}" stroke-width="{9 - k * 2}" '
                    f'stroke-dasharray="{6.2832 * (380 + 45 * k):.0f}" stroke-dashoffset="{6.2832 * (380 + 45 * k):.0f}" filter="url(#{p}-glow)" transform="rotate(-90 {CX} {CY})"/>'
                    for k, c in enumerate(colors))
    dome_defs = (f'<radialGradient id="{p}-domegrad" cx="50%" cy="50%" r="50%"><stop offset=".7" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".22"/></radialGradient>'
            f'<linearGradient id="{p}-wallgrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c2380"/><stop offset="1" stop-color="#1a1450"/></linearGradient>')
    room = (f'<rect x="900" y="130" width="940" height="700" rx="18" fill="url(#{p}-wallgrad)" stroke="#5a4ad0" stroke-width="4"/>'
            f'<polygon points="900,830 1840,830 1900,985 840,985" fill="#2a2060" stroke="#5a4ad0" stroke-width="4" stroke-linejoin="round"/>'
            f'<ellipse cx="1310" cy="905" rx="330" ry="48" fill="{MAGENTA}" opacity=".18"/>'
            f'<g transform="translate(990 830)"><rect x="-34" y="-70" width="68" height="70" rx="10" fill="#8a5a3a"/>'
            f'<path d="M 0 -70 Q -60 -150 -40 -230 M 0 -70 Q 10 -170 0 -260 M 0 -70 Q 60 -140 50 -220" stroke="{MINT}" stroke-width="14" fill="none" stroke-linecap="round" opacity=".85"/></g>'
            + picture(p + "-q0", "family", 1080, 250, .62) + picture(p + "-q1", "birthday", 1290, 235, .5)
            + picture(p + "-q2", "graduation", 1480, 260, .6, rot=2) + picture(p + "-q3", "beach", 1690, 245, .58, rot=-2))
    orbs = [("heart", 1480, 470, MAGENTA), ("cake", 1620, 410, AMBER), ("note", 1740, 540, LILAC), ("sun", 1590, 600, MINT)]
    orbs_svg = "".join(f'<g transform="translate(0 0)"><g id="{p}-ob{k}" opacity="0">{orb(f"{p}-o{k}", sm, x, y, c, 44)}</g></g>' for k, (sm, x, y, c) in enumerate(orbs))
    svg = f"""<circle id="{p}-dome" cx="{CX}" cy="{CY}" r="470" fill="url(#{p}-domegrad)" opacity="0"/>
{room}
<g transform="translate({gx} {gy}) scale({gs})"><g id="{p}-gW">{figure_var(p + "-g", "home", "sitting", glow=p + "-glow")}</g></g>
{orbs_svg}
{rings}"""
    corridor_svg = corridor(p + "c", p + "-glow")
    lock_svg = (f'<g transform="translate(960 530)"><g id="{p}-lock" opacity="0"><g transform="scale(.2)">{plate(p + "k", p + "-glow", 230)}</g></g></g>')
    html = (f'<svg id="{p}-corridor" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;opacity:0">'
            f'<rect width="1920" height="1080" fill="#05041a"/><g id="{p}-corridorZ">{corridor_svg}{lock_svg}</g><rect width="1920" height="1080" fill="url(#{p}-vig)"/>'
            f'<linearGradient id="{p}-stripe" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05041a" stop-opacity=".97"/><stop offset=".7" stop-color="#05041a" stop-opacity=".82"/><stop offset="1" stop-color="#05041a" stop-opacity="0"/></linearGradient>'
            f'<rect id="{p}-stripeR" width="1920" height="380" fill="url(#{p}-stripe)" opacity="0"/></svg>')
    html += (mono(f"{p}-t0", "RESEARCHERS", "left:90px;top:130px", AMBER, 72) +
             text(f"{p}-t1", "NEW", "left:90px;top:100px;font-size:120px;color:#eef1f7") +
             text(f"{p}-t2", "RIGHTS", "left:90px;top:236px;font-size:120px;color:#ffd98a") +
             mono(f"{p}-l0", "MENTAL PRIVACY", "left:90px;top:440px", CYAN, 44) +
             mono(f"{p}-l1", "COGNITIVE LIBERTY", "left:90px;top:540px", LILAC, 44) +
             mono(f"{p}-l2", "INTEGRITY OF THE MIND", "left:90px;top:640px", MINT, 44) +
             text(f"{p}-t3", "WITHOUT YOU KNOWING", "left:0;right:0;text-align:center;top:90px;font-size:124px;color:#ffe9c4"))
    js = f"""
  camZ("#{p}-cam", 0, {t_right:.2f}, 1.08, 1.0, {CX}, {CY}, "sine.inOut");
  camZ("#{p}-cam", {t_right:.2f}, 1.15, 1.0, 80.0, {hx:.1f}, {hy:.1f}, "power3.in");
  {"".join(f'pop("#{p}-ob{k}", {t_argue + 0.25 * k:.2f}, 0.3, 0.8); tl.fromTo("#{p}-o{k}",{{y:0}},{{y:-12,duration:{1.3 + 0.2 * k:.1f},repeat:{int((t_right - t_argue) / (1.3 + 0.2 * k))},yoyo:true,ease:"sine.inOut"}},{t_argue + 0.8 + 0.25 * k:.2f});' for k in range(len(orbs)))}
  tl.fromTo("#{p}-g-eye",{{x:0,y:0}},{{x:2,y:-3,duration:0.4}},{t_argue + 0.3:.2f});
  rise("#{p}-t0 span", {t_researchers:.2f}); exit_up("#{p}-t0 span", {t_new - 0.35:.2f});
  rise("#{p}-t1 span", {t_new:.2f}, 0.8); rise("#{p}-t2 span", {t_rights:.2f}, 0.8);
  enter("#{p}-dome", {t_privacy:.2f}, 0.8);
  {"".join(f'draw("#{p}-ring{k}", {t:.2f}, 1.0, {6.2832 * (380 + 45 * k):.0f}); rise("#{p}-l{k} span", {t:.2f});' for k, t in enumerate((t_privacy, t_liberty, t_integrity)))}
  {"".join(f'vanish("#{p}-{n}", {t_right - 0.25:.2f}, 0.35);' for n in ("t1", "t2", "l0", "l1", "l2", "dome", "ring0", "ring1", "ring2"))}
  tl.fromTo("#{p}-corridor",{{opacity:0}},{{opacity:1,duration:0.35}},{t_right + 1.1:.2f});
  tl.fromTo("#{p}-corridorZ",{{scale:1,svgOrigin:"960 530"}},{{scale:3.3,svgOrigin:"960 530",duration:{dur - t_right - 0.8:.2f},ease:"sine.inOut"}},{t_right + 0.8:.2f});
  tl.fromTo("#{p}c-haze",{{opacity:0.7}},{{opacity:1,duration:0.8,repeat:5,yoyo:true,ease:"sine.inOut"}},{t_right:.2f});
  tl.fromTo(".{p}c-led",{{opacity:1}},{{opacity:0.15,duration:0.18,repeat:12,yoyo:true,ease:"steps(1)",stagger:{{each:0.0105,from:"random"}}}},{t_right + 0.8:.2f});
  tl.fromTo("#{p}c-doorglow",{{scaleX:1,transformOrigin:"50% 50%"}},{{scaleX:0.04,transformOrigin:"50% 50%",duration:0.9,ease:"power3.inOut"}},{t_without:.2f});
  pop("#{p}-lock", {t_knowing - 0.3:.2f}, 0.4, 0.8);
  enter("#{p}-stripeR", {t_without - 0.3:.2f}, 0.4); rise("#{p}-t3 span", {t_without:.2f}, 0.8);
""" + idle(p + "-g", dur, (1.4, 4.6, 7.4, 9.9), "sitting")
    return scene(p, dur, svg, html, js, dome_defs, background=("#2a1560", "#150d40", "#07061a"), seed=19)


SCENES = [(k, f, seg(c, i)[1]) for k, f, c, i in [
    ("robot_5", robot_5, "robot", 5), ("robot_6", robot_6, "robot", 6), ("robot_7", robot_7, "robot", 7),
    ("robot_8", robot_8, "robot", 8), ("robot_9", robot_9, "robot", 9),
    ("closing_0", closing_0, "closing", 0), ("closing_1", closing_1, "closing", 1),
    ("closing_2", closing_2, "closing", 2)]]
SEG_MAP = {("robot", 5): "robot_5", ("robot", 6): "robot_6", ("robot", 7): "robot_7", ("robot", 8): "robot_8", ("robot", 9): "robot_9",
        ("closing", 0): "closing_0", ("closing", 1): "closing_1", ("closing", 2): "closing_2"}

if __name__ == "__main__":
    print(write_scenes(SCENES, HERE))
