"""Group g4_reading: scene "reading", segments 0, 1, 3, 4, 5, 6, 8, 9, 10 and 11 (2, 7 and 12 already exist: D, E and F from v3).

  python3 build_g4_reading.py     # writes compositions/ and index.html in this folder

Round 2: the profile head with the pink brain stayed only in reading_0 (the "reading the brain" theme). Where the narration talks about a person
(the woman in the hospital, the patients, the volunteers, "you") a real person from figure.py comes in, in everyday settings:
hospital room, wheelchair, MRI scanner, living room. The real article pages (reading_3, reading_8) stay.
"""
import math, os, random, re, sys

HERE_G = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE_G, ".."))
from engine import *  # noqa: E402,F401
from art2 import fly_rich, fly_defs, H_LINE, BRAIN_SIDE, brain_side  # noqa: E402
from figure import figure, picture, orb, head, HOME, SKIN, HAIR, TIE, ANCHORS  # noqa: E402

SCENE_KEY = "reading"

# variations of the same person (color swap over figure(..., "home"/"work"))
# (base hex from figure.py; shadow and light are neutral layers on top, so swapping the base recolors the whole piece)
GOWN = {HOME["torso"]: "#8fcde6", HOME["pants"]: "#6fa8c8", HOME["shoe"]: "#dfe8f2", HAIR: "#2a1812"}   # the woman: hospital gown
VOLUNTEER = {HOME["torso"]: "#2fb88a"}                               # volunteer: green hoodie
SCIENTIST2 = {TIE: "#2bb8d8", HAIR: "#c4c0d4"}                  # second scientist: cyan tie, gray hair


def tinge(svg, colors):
    for a, b in colors.items():
        svg = svg.replace(a, b)
    return svg


def idle_g(p, dur, blinks=(2.0, 5.3, 8.8, 12.1), hip=-230):
    """Like figure.figure_idle, with breathing through svgOrigin (the box of {p}-trunk contains the 19998 px clip rectangles
    of the generated SVG, so transformOrigin in % rotates/stretches from a point 10 thousand px away from the body)."""
    n = max(1, int(dur / 1.7))
    js = (f'tl.fromTo("#{p}-trunk",{{scaleY:1,svgOrigin:"0 {hip}"}},{{scaleY:1.012,svgOrigin:"0 {hip}",duration:1.7,repeat:{n},yoyo:true,ease:"sine.inOut"}},0);'
          f'tl.fromTo("#{p}-head",{{y:0}},{{y:-5,duration:1.7,repeat:{n},yoyo:true,ease:"sine.inOut"}},0.2);')
    for t in blinks:
        if t < dur - 0.3:
            js += f'tl.fromTo("#{p}-eye",{{scaleY:1,transformOrigin:"50% 50%"}},{{scaleY:0.08,transformOrigin:"50% 50%",duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t:.2f});'
    return js


def on_head(svg, p, inner):
    """Draws `inner` (person local coordinates) at the end of {p}-head, over the hair and face: follows the
    head bob."""
    i = svg.index(f'<g id="{p}-head">')
    depth = 0
    for m in re.finditer(r"<g\b|</g>", svg[i:]):
        depth += 1 if m.group(0) != "</g>" else -1
        if depth == 0:
            j = i + m.start()
            return svg[:j] + inner + svg[j:]
    raise ValueError(p)


def standing_head(variant="home"):
    a = ANCHORS[("home" if variant == "home" else "work", "standing", 30)]
    return a["head_center"], a["head_top"]


def xray(p, xid):
    """Pink brain seen through the skull (from the forehead up) of the standing person. Id {xid} starts invisible."""
    (cx, cy), _ = standing_head()
    ex, ey = cx - 4, cy - 30                    # skull, from the eyebrow (y ~ cy - 8) up: the eyes stay visible
    return (f'<clipPath id="{xid}-cp"><ellipse cx="{ex}" cy="{ey}" rx="40" ry="22"/></clipPath>'
            f'<g id="{xid}" opacity="0" clip-path="url(#{xid}-cp)"><ellipse cx="{ex}" cy="{ey}" rx="40" ry="22" fill="#ff9fb4" opacity=".35"/>'
            f'<g transform="translate({ex} {ey + 6}) scale(.56) translate(-191 -90)">{brain_side(xid + "c")}</g></g>')


def headphones(variant="home"):
    """Headphones on the standing head (turn 30): arc over the hair and ear cup on the visible ear (left side)."""
    (cx, cy), (tx_, ty_) = standing_head(variant)
    ex, ey = cx - 40, cy + 8
    return (f'<path d="M {ex + 2} {ey - 6} C {ex - 8} {ty_ - 18} {cx + 34} {ty_ - 14} {cx + 30} {ty_ + 18}" fill="none" stroke="#2a2a6a" stroke-width="9" stroke-linecap="round"/>'
            f'<path d="M {ex + 2} {ey - 6} C {ex - 8} {ty_ - 18} {cx + 34} {ty_ - 14} {cx + 30} {ty_ + 18}" fill="none" stroke="#8d7bff" stroke-width="2.5" stroke-linecap="round"/>'
            f'<ellipse cx="{ex}" cy="{ey}" rx="12" ry="17" fill="#2a2a6a" stroke="#8d7bff" stroke-width="3.5"/>'
            f'<ellipse cx="{ex - 2}" cy="{ey}" rx="5" ry="9" fill="#3be0ff" opacity=".8"/>')


def arm_js(g, t0, ang, dur, rep=0, variant="work", pose="standing"):
    """Rotates {g}-arm at the shoulder (local svgOrigin; % is thrown off by the clip rectangles)."""
    ox, oy = ANCHORS[("home" if variant == "home" else "work", pose, 30)]["shoulder_arm"]
    yo = ",yoyo:true" if rep else ""
    return (f'tl.fromTo("#{g}-arm",{{rotation:0,svgOrigin:"{ox} {oy}"}},{{rotation:{ang},svgOrigin:"{ox} {oy}",duration:{dur},repeat:{rep}{yo},'
            f'ease:"sine.inOut",immediateRender:false}},{t0:.2f});')


def lying_down(svg, tx, ty, s):
    """Standing person (figure standing) lying face up, head to the right, feet at (tx, ty)."""
    return f'<g transform="translate({tx} {ty}) rotate(90) scale({-s} {s})">{svg}</g>'


def her(p, pose="standing", glow=None, **kw):
    return tinge(figure(p, "home", pose, glow=glow, **kw), GOWN)


# ---------------------------------------------------------------- group helper JS
LIB = r"""
  function _fz(sel,s,px,py,cx,cy){var e=document.querySelector(sel);if(e)e.setAttribute("transform","translate("+(cx-s*px).toFixed(2)+" "+(cy-s*py).toFixed(2)+") scale("+s.toFixed(5)+")");}
  function focusInit(sel,a,cx,cy){_fz(sel,a[2],a[0],a[1],cx,cy);}
  function focusTo(sel,t,dur,a,b,cx,cy,ease){var o={u:0};tl.fromTo(o,{u:0},{u:1,duration:dur,ease:ease||"power3.inOut",immediateRender:false,onUpdate:function(){
    var la=Math.log(a[2]),s=Math.exp(la+(Math.log(b[2])-la)*o.u),px=a[0]+(b[0]-a[0])*o.u,py=a[1]+(b[1]-a[1])*o.u;
    _fz(sel,s,px,py,cx,cy);}},t);}
  function mark(sel,t,dur){tl.fromTo(sel,{scaleX:0,transformOrigin:"0% 50%"},{scaleX:1,transformOrigin:"0% 50%",duration:dur||0.6,ease:"power2.inOut"},t);}
  function draw(sel,t,dur,len){tl.fromTo(sel,{attr:{"stroke-dashoffset":len}},{attr:{"stroke-dashoffset":0},duration:dur,ease:"power2.inOut"},t);}
  function pulse(sel,t,dur,s,rep){tl.fromTo(sel,{scale:1,transformOrigin:"50% 50%"},{scale:s,transformOrigin:"50% 50%",duration:dur,repeat:rep,yoyo:true,ease:"sine.inOut",immediateRender:false},t);}
  function fade(sel,t,dur,a,b){tl.fromTo(sel,{opacity:a},{opacity:b,duration:dur,ease:"sine.inOut",immediateRender:false},t);}
  function glance(sel,t,x0,x1){tl.fromTo(sel,{x:x0},{x:x1,duration:0.35,ease:"power2.inOut",immediateRender:false},t);}
  function swing(sel,t,dur,a,b,ease){tl.fromTo(sel,{scaleX:a,transformOrigin:"100% 50%"},{scaleX:b,transformOrigin:"100% 50%",duration:dur,ease:ease||"power2.inOut",immediateRender:false},t);}
"""


def bob_js(sel, dur):
    """Same bob as engine.person_idle, for overlays that need to follow the head."""
    return f'tl.fromTo("{sel}",{{y:0}},{{y:-5,duration:1.6,repeat:{max(1, int(dur / 1.6))},yoyo:true,ease:"sine.inOut"}},0);'


def make_scene(p, dur, svg, html, js, extra=""):
    return composition(p, dur, svg, html, LIB + js, extra)


def tx(id_, txt, left, top, size, color="#eef1f7", cls="title", extra=""):
    style = f"left:{left}px;top:{top}px;font-size:{size}px;color:{color}"
    if cls == "pill2":
        style += ";letter-spacing:.14em"
    return text(id_, txt, style + extra, cls)


def centered(id_, txt, top, size, color="#eef1f7", cls="title", left=0, width=1920):
    return text(id_, txt, f"left:{left}px;width:{width}px;text-align:center;top:{top}px;font-size:{size}px;color:{color}" +
                 (";letter-spacing:.14em" if cls == "pill2" else ""), cls)


def local_g(tx_, ty, s, inner, brain=False):
    """Places `inner` in the person local system (same translate/scale as `person`). brain=True: in the brain system."""
    if brain:
        inner = f'<g transform="translate(196 118) scale(.82) translate(-196 -118)">{inner}</g>'
    return f'<g transform="translate({tx_} {ty}) scale({s})">{inner}</g>'


# ---------------------------------------------------------------- fixed set: person, door, machine
PX, PY, PS = -165, 190, 2.5          # person in the door scenes: box x 110..585, y 260..820
BRAIN_W = (PX + 193 * PS, PY + 91 * PS)  # brain center in world coordinates


def trio_defs(p):
    return f"""<linearGradient id="{p}-ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b1e54"/><stop offset="1" stop-color="#090b26"/></linearGradient>
<linearGradient id="{p}-machineG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e4e8ff"/><stop offset="1" stop-color="#8e96d0"/></linearGradient>
<linearGradient id="{p}-leafG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2c2a88"/><stop offset="1" stop-color="#1a1856"/></linearGradient>
<linearGradient id="{p}-lightG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff6c8"/><stop offset="1" stop-color="#9af0ff"/></linearGradient>
<linearGradient id="{p}-wedgeG" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff2b8" stop-opacity=".75"/><stop offset="1" stop-color="#fff2b8" stop-opacity="0"/></linearGradient>
<radialGradient id="{p}-tunnelG" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#bff6ff" stop-opacity="1"/><stop offset=".5" stop-color="#3be0ff" stop-opacity=".55"/><stop offset="1" stop-color="#3be0ff" stop-opacity="0"/></radialGradient>
<radialGradient id="{p}-tunnelRG" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffc2cf" stop-opacity="1"/><stop offset=".5" stop-color="#ff4f7d" stop-opacity=".6"/><stop offset="1" stop-color="#ff4f7d" stop-opacity="0"/></radialGradient>"""


def ground(p, y=838):
    return (f'<rect x="-400" y="{y}" width="2720" height="600" fill="url(#{p}-ground)"/>'
            f'<line x1="-400" y1="{y + 2}" x2="2320" y2="{y + 2}" stroke="#8d7bff" stroke-width="3" opacity=".35"/>')


def room_defs(p):
    return f"""<linearGradient id="{p}-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#232a6e"/><stop offset="1" stop-color="#121644"/></linearGradient>
<linearGradient id="{p}-blanket" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a82e0"/><stop offset="1" stop-color="#2c4a9a"/></linearGradient>
<linearGradient id="{p}-screen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16143a"/><stop offset="1" stop-color="#0b1c40"/></linearGradient>"""


def door_svg(p, light=0.0):
    """Standing door in the middle (x 860..1080, y 380..840). Leaf hinged on the right: {p}-leaf (scaleX opens it)."""
    return f"""<g id="{p}-door"><rect x="840" y="830" width="260" height="14" rx="6" fill="#05031a" opacity=".6"/>
<rect x="866" y="386" width="208" height="454" fill="#06051a"/>
<rect id="{p}-light" x="866" y="386" width="208" height="454" fill="url(#{p}-lightG)" opacity="{light}"/>
<polygon id="{p}-wedge" points="866,840 920,840 780,940 520,940" fill="url(#{p}-wedgeG)" opacity="{light}"/>
<g id="{p}-leaf"><rect x="870" y="390" width="200" height="450" fill="url(#{p}-leafG)" stroke="#8d7bff" stroke-width="4"/>
<rect x="892" y="420" width="156" height="170" rx="8" fill="none" stroke="#5a5ad0" stroke-width="4"/><rect x="892" y="620" width="156" height="190" rx="8" fill="none" stroke="#5a5ad0" stroke-width="4"/>
<circle cx="896" cy="612" r="11" fill="#ffb23e"/></g>
<rect x="856" y="376" width="228" height="468" fill="none" stroke="#8d7bff" stroke-width="12" filter="url(#{p}-glow)"/></g>"""


def machine(p):
    """MRI machine (x 1160..1820, y 330..840): housing, tunnel with cyan ring, table."""
    return f"""<g id="{p}-machine"><ellipse cx="1500" cy="846" rx="380" ry="22" fill="#05031a" opacity=".6"/>
<rect x="1250" y="674" width="40" height="166" rx="6" fill="#3a3a8a" stroke="#8d7bff" stroke-width="3"/><rect x="1176" y="674" width="24" height="166" rx="6" fill="#3a3a8a" stroke="#8d7bff" stroke-width="3"/><rect x="1160" y="832" width="150" height="10" rx="5" fill="#8d7bff" opacity=".7"/>
<g filter="url(#{p}-shadow)"><rect x="1300" y="330" width="520" height="510" rx="96" fill="url(#{p}-machineG)"/></g>
<rect x="1300" y="782" width="520" height="18" fill="#8d7bff" opacity=".55"/>
<circle cx="1560" cy="560" r="184" fill="#b4bbe8"/><circle cx="1560" cy="560" r="168" fill="#0b0a24"/>
<circle cx="1560" cy="560" r="120" fill="#14123a"/>
<circle id="{p}-tunnel" cx="1560" cy="560" r="150" fill="url(#{p}-tunnelG)" opacity=".25"/>
<circle id="{p}-tunnelR" cx="1560" cy="560" r="150" fill="url(#{p}-tunnelRG)" opacity="0"/>
<circle id="{p}-ring" cx="1560" cy="560" r="168" fill="none" stroke="#3be0ff" stroke-width="10" opacity=".35" filter="url(#{p}-glow)"/>
<circle id="{p}-ringR" cx="1560" cy="560" r="168" fill="none" stroke="#ff4f7d" stroke-width="12" opacity="0" filter="url(#{p}-glow)"/>
<rect x="1160" y="640" width="430" height="34" rx="12" fill="#dfe4ff" stroke="#8d7bff" stroke-width="3"/>
<path d="M1336 372 Q1560 330 1784 372" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="10" stroke-linecap="round"/></g>"""


def person_door(p):
    return f'<ellipse cx="360" cy="846" rx="230" ry="18" fill="#05031a" opacity=".55"/>' + person(p, PX, PY, PS)


# ---------------------------------------------------------------- reading 0: "File three. Read."
def reading_0():
    p, sg = "reading_0", 0
    start, dur = seg(SCENE_KEY, sg)
    t_file, t_3, t_read = 0.2, 1.0, 2.08
    extra = f"""<linearGradient id="{p}-front" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a3aa6"/><stop offset="1" stop-color="#2c2380"/></linearGradient>
<linearGradient id="{p}-paper" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#e9dcc2"/></linearGradient>
<radialGradient id="{p}-haloG" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ff9fb4" stop-opacity=".8"/><stop offset="1" stop-color="#ff9fb4" stop-opacity="0"/></radialGradient>"""
    tx_, ty_, s_ = 238, 288, 2.2
    svg = f"""<g id="{p}-folder">
<ellipse cx="960" cy="940" rx="620" ry="30" fill="#05031a" opacity=".55" filter="url(#{p}-blur6)"/>
<rect x="410" y="96" width="400" height="150" rx="24" fill="#2a1d70" stroke="#8d7bff" stroke-width="5"/>
<text x="446" y="178" font-family="IBM Plex Mono" font-weight="700" font-size="48" letter-spacing="5" fill="#3be0ff">FILE</text>
<g id="{p}-n3"><circle cx="740" cy="160" r="40" fill="#ffb23e"/><text x="740" y="178" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="54" fill="#1a1050">3</text></g>
<rect x="410" y="232" width="1100" height="672" rx="26" fill="#211862"/>
<g filter="url(#{p}-shadow)"><rect x="470" y="196" width="980" height="560" rx="10" fill="url(#{p}-paper)" transform="rotate(-2 960 480)"/>
<rect x="500" y="214" width="940" height="560" rx="10" fill="#f4ecd8" transform="rotate(1.6 960 480)"/></g>
<g fill="#8a7f68" opacity=".45"><rect x="980" y="238" width="380" height="12" rx="6"/><rect x="980" y="266" width="300" height="12" rx="6"/></g>
<g filter="url(#{p}-shadow)"><rect x="400" y="292" width="1120" height="620" rx="26" fill="url(#{p}-front)"/></g>
<rect x="400" y="292" width="1120" height="620" rx="26" fill="none" stroke="#8d7bff" stroke-width="6" filter="url(#{p}-glow)"/>
<ellipse id="{p}-halo" cx="{tx_ + 193 * s_:.0f}" cy="{ty_ + 91 * s_:.0f}" rx="230" ry="160" fill="url(#{p}-haloG)" opacity="0"/>
{person(p, tx_, ty_, s_)}
<g id="{p}-scan" opacity="0"><rect x="470" y="340" width="470" height="8" rx="4" fill="#3be0ff" filter="url(#{p}-glow)"/><rect x="470" y="300" width="470" height="44" fill="#3be0ff" opacity=".12"/></g>
</g>"""
    html = tx(f"{p}-reading", "Read", 1000, 420, 270)
    js = f"""
  camZ("#{p}-cam", 0, {dur:.2f}, 1.0, 1.05, 960, 540, "none");
  tl.fromTo("#{p}-folder",{{y:780,rotation:5,transformOrigin:"50% 50%"}},{{y:0,rotation:0,transformOrigin:"50% 50%",duration:0.9,ease:"expo.out"}},{max(0.05, t_file - 0.15):.2f});
  pop("#{p}-n3", {t_3:.2f}, 0.2, 0.7);
  rise("#{p}-reading > span", {t_read:.2f}, 0.8);
  tl.fromTo("#{p}-scan",{{y:0,opacity:0}},{{y:470,opacity:1,duration:0.7,ease:"power1.inOut"}},{t_read - 0.1:.2f});
  vanish("#{p}-scan", {t_read + 0.6:.2f}, 0.15);
  fade("#{p}-halo", {t_read:.2f}, 0.4, 0, 1);
  pulse("#{p}-brain", {t_read + 0.1:.2f}, 0.22, 1.07, 1);
""" + person_idle(p, dur, (1.3,))
    return make_scene(p, dur, svg, html, js, extra)


# ---------------------------------------------------------------- reading 1: the fly on the fruit, and a living person looking at it
def reading_1():
    p, sg = "reading_1", 1
    start, dur = seg(SCENE_KEY, sg)
    t_brain, t_fly, t_read, t_brain2, t_alive = 0.81, 2.07, 3.4, 3.82, 5.2
    FX, FY, FR = 600, 780, 150          # fruit; the ground sits at y = FY + FR
    GROUND_Y = FY + FR
    MX, MY, MS = 540, 566, 0.9          # fly standing on top of the fruit
    GX, GS = 1390, 1.12                 # mirrored person (looks left, at the fly)
    gp = f"{p}-g"
    extra = fly_defs(p + "m") + trio_defs(p) + f"""<radialGradient id="{p}-fruit" cx="38%" cy="30%" r="80%"><stop offset="0" stop-color="#ffc35a"/><stop offset=".6" stop-color="#ff8a2a"/><stop offset="1" stop-color="#d9501c"/></radialGradient>
<radialGradient id="{p}-haloG" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ff9fb4" stop-opacity=".7"/><stop offset="1" stop-color="#ff9fb4" stop-opacity="0"/></radialGradient>
<linearGradient id="{p}-scanG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3be0ff" stop-opacity="0"/><stop offset=".8" stop-color="#3be0ff" stop-opacity=".35"/><stop offset="1" stop-color="#bff6ff" stop-opacity="1"/></linearGradient>"""
    fruit = (f'<g transform="translate({FX} {FY})"><ellipse cx="0" cy="{FR + 2}" rx="{FR * 1.2:.0f}" ry="20" fill="#05031a" opacity=".55"/>'
             f'<circle r="{FR}" fill="url(#{p}-fruit)" filter="url(#{p}-shadow)"/><ellipse cx="-50" cy="-56" rx="38" ry="64" fill="#fff" opacity=".28" transform="rotate(28 -50 -56)"/>'
             f'<g transform="rotate(32)"><path d="M0 -144 C-4 -174 12 -192 32 -200" stroke="#4b7a2a" stroke-width="12" fill="none" stroke-linecap="round"/>'
             f'<path d="M18 -177 C66 -204 114 -180 102 -150 C72 -150 42 -158 18 -177 Z" fill="#58b84a" transform="translate(-14 26)"/></g></g>')
    fly_shadow = f'<ellipse cx="{MX + 6}" cy="{MY + 80}" rx="92" ry="12" fill="#5a1a08" opacity=".45" filter="url(#{p}-blur6)"/>'
    fly = (f'<g transform="translate({MX} {MY}) scale({MS})"><g id="{p}-flyHover"><g filter="url(#{p}-shadow)">{fly_rich(p + "-fly", p + "m")}</g></g></g>')
    body = on_head(figure(gp, "home", "standing", glow=f"{p}-glow"), gp, xray(gp, f"{p}-cx"))
    # person head in world coordinates (for halo and scan)
    (acx, acy), (_, aty) = standing_head()
    hx0, hx1 = GX - GS * (acx + 52), GX - GS * (acx - 52)
    hy0, hy1 = GROUND_Y + GS * aty, GROUND_Y + GS * (acy + 56)
    hcx, hcy = (hx0 + hx1) / 2, (hy0 + hy1) / 2
    svg = f"""{ground(p, GROUND_Y)}
<ellipse id="{p}-halo" cx="{hcx:.0f}" cy="{hcy:.0f}" rx="240" ry="200" fill="url(#{p}-haloG)" opacity="0"/>
<g transform="translate({GX} {GROUND_Y}) scale({-GS} {GS})"><g id="{p}-gW">{body}</g></g>
<clipPath id="{p}-scc"><ellipse cx="{hcx:.0f}" cy="{hcy:.0f}" rx="{GS * 56:.0f}" ry="{GS * 62:.0f}"/></clipPath><g clip-path="url(#{p}-scc)"><g id="{p}-scan" opacity="0"><rect x="{hx0 - 150:.0f}" y="{hy0 - 20:.0f}" width="150" height="{hy1 - hy0 + 40:.0f}" fill="url(#{p}-scanG)"/></g></g>
{fruit}{fly_shadow}{fly}"""
    html = (tx(f"{p}-m1", "Mapping", 1040, 330, 100) + tx(f"{p}-m2", "a fly's brain", 1040, 470, 100, "#9af0ff") +
            tx(f"{p}-t1", 'Reading a <span style="color:#ff9fb4">living</span>', 110, 110, 124) +
            tx(f"{p}-t2", "human brain", 110, 270, 124))
    A0, A1, B0, B1 = "[740,700,2.0]", "[740,700,2.1]", "[960,540,1.0]", "[960,540,1.04]"
    C = "960,540"
    js = f"""
  focusInit("#{p}-cam",{A0},{C});
  focusTo("#{p}-cam",0,{t_read - 0.25:.2f},{A0},{A1},{C},"none");
  focusTo("#{p}-cam",{t_read - 0.25:.2f},1.4,{A1},{B0},{C},"power3.inOut");
  focusTo("#{p}-cam",{t_read + 1.15:.2f},{dur - t_read - 1.15:.2f},{B0},{B1},{C},"none");
  tl.fromTo("#{p}-fly-wings",{{scaleY:1,transformOrigin:"50% 100%"}},{{scaleY:0.35,transformOrigin:"50% 100%",duration:0.05,repeat:15,yoyo:true,ease:"none"}},{t_fly:.2f});
  tl.fromTo("#{p}-flyHover",{{y:0}},{{y:-6,duration:0.8,repeat:6,yoyo:true,ease:"sine.inOut"}},0);
  tl.fromTo("#{p}-fly-brainDot",{{opacity:0}},{{opacity:1,duration:0.3}},{t_brain:.2f});
  pulse("#{p}-fly-brainDot",{t_fly:.2f},0.2,1.8,3);
  rise("#{p}-m1 > span",{max(0.1, t_brain - 0.4):.2f}); rise("#{p}-m2 > span",{t_fly - 0.1:.2f});
  vanish("#{p}-m1",{t_read - 0.4:.2f},0.3); vanish("#{p}-m2",{t_read - 0.4:.2f},0.3);
  rise("#{p}-t1 > span",{t_read + 0.3:.2f});
  rise("#{p}-t2 > span",{t_alive - 0.25:.2f},0.8);
  enter("#{p}-scan",{t_brain2 - 0.1:.2f},0.15);
  tl.fromTo("#{p}-scan",{{x:0}},{{x:{hx1 - hx0 + 150:.0f},duration:0.8,ease:"power1.inOut",immediateRender:false}},{t_brain2 - 0.1:.2f});
  vanish("#{p}-scan",{t_brain2 + 0.65:.2f},0.15);
  tl.fromTo("#{p}-cx",{{opacity:0}},{{opacity:0.8,duration:0.6,immediateRender:false}},{t_brain2 + 0.1:.2f});
  fade("#{p}-halo",{t_alive - 0.2:.2f},0.4,0,1);
  pulse("#{p}-halo",{t_alive + 0.2:.2f},0.35,1.12,1);
  pulse("#{p}-cx",{t_alive:.2f},0.3,1.05,1);
""" + idle_g(gp, dur, (1.6, t_alive + 0.3))
    return make_scene(p, dur, svg, html, js, extra)


# ---------------------------------------------------------------- article page with camera
def page(p, img, w, h, panel, marks, decor=""):
    """Panel with the real page (`assets/docs/img.png`) clipped. marks: [(id, x, y, w, h)] in page px."""
    x0, y0, pw, ph = panel
    rects = "".join(f'<rect id="{p}-{k}" x="{x}" y="{y}" width="{ww}" height="{hh}" rx="6" fill="#ffd23e" opacity=".55" style="mix-blend-mode:multiply"/>'
                    for k, x, y, ww, hh in marks)
    fd = "".join(f'<linearGradient id="{p}-fd{k}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="#fff" stop-opacity=".97"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                 for k, x1, y1, x2, y2 in [("L", 0, 0, 1, 0), ("R", 1, 0, 0, 0), ("T", 0, 0, 0, 1), ("B", 0, 1, 0, 0)])
    return f"""{fd}<clipPath id="{p}-clip"><rect x="{x0}" y="{y0}" width="{pw}" height="{ph}" rx="26"/></clipPath>
<g filter="url(#{p}-shadow)"><rect x="{x0}" y="{y0}" width="{pw}" height="{ph}" rx="26" fill="#0e0c26"/></g>
<g clip-path="url(#{p}-clip)"><g id="{p}-pgW"><g id="{p}-pg">
<rect x="0" y="0" width="{w}" height="{h}" fill="#fff"/>
<image href="assets/docs/{img}.png" x="0" y="0" width="{w}" height="{h}"/>{rects}{decor}</g></g>
<rect x="{x0}" y="{y0}" width="90" height="{ph}" fill="url(#{p}-fdL)"/><rect x="{x0 + pw - 90}" y="{y0}" width="90" height="{ph}" fill="url(#{p}-fdR)"/>
<rect x="{x0}" y="{y0}" width="{pw}" height="70" fill="url(#{p}-fdT)"/><rect x="{x0}" y="{y0 + ph - 70}" width="{pw}" height="70" fill="url(#{p}-fdB)"/></g>
<rect x="{x0}" y="{y0}" width="{pw}" height="{ph}" rx="26" fill="none" stroke="#8d7bff" stroke-width="6" filter="url(#{p}-glow)"/>"""


# ---------------------------------------------------------------- reading 3: Owen 2006, real page
def reading_3():
    p, sg = "reading_3", 3
    start, dur = seg(SCENE_KEY, sg)
    t_adr, t_owen, t_machine, t_scanner, t_imagine, t_you, t_playing, t_tennis = 2.03, 2.05, 4.21, 5.02, 6.76, 7.46, 8.43, 8.9
    W, H = 1600, 2037
    marks = [("m0", 92, 196, 690, 58), ("m1", 92, 262, 408, 58), ("m2", 92, 338, 196, 32),
              ("m4", 1052, 131, 456, 29), ("m5", 1052, 159, 456, 29)]
    decor = (f'<rect id="{p}-fig" x="346" y="1197" width="678" height="506" fill="none" stroke="#3be0ff" stroke-width="7" stroke-dasharray="2400" stroke-dashoffset="2400"/>'
            f'<g id="{p}-scan" opacity="0"><rect x="346" y="1197" width="678" height="10" fill="#3be0ff"/><rect x="346" y="1157" width="678" height="40" fill="#3be0ff" opacity=".18"/></g>'
            f'<circle id="{p}-bb0" cx="525" cy="1293" r="46" fill="none" stroke="#ffb23e" stroke-width="7" opacity="0"/>'
            f'<circle id="{p}-bb1" cx="519" cy="1518" r="46" fill="none" stroke="#ffb23e" stroke-width="7" opacity="0"/>')
    svg = page(p, "owen2006", W, H, (60, 60, 1120, 960), marks, decor)
    C = "620,540"
    K0, K1, K2, K3, K4 = "[800,690,0.71]", "[525,470,1.08]", "[685,1490,1.3]", "[1308,345,2.0]", "[1308,350,2.12]"
    L = 1240
    html = (tx(f"{p}-a1", "Adrian", L, 210, 150) + tx(f"{p}-a2", "Owen", L, 390, 150, "#ffd98a") +
            tx(f"{p}-b1", "BRAIN", L, 300, 52, "#3be0ff", "pill2") + tx(f"{p}-b2", "scanner", L, 380, 108) +
            tx(f"{p}-c1", "Imagine", L, 170, 104) + tx(f"{p}-c2", "you are", L, 310, 104) +
            tx(f"{p}-c3", 'playing <b style="color:#ffd98a">tennis</b>', L, 450, 96) +
            tx(f"{p}-src", "SCIENCE · 2006", L, 920, 46, "#ffb23e", "pill2"))
    js = f"""
  tl.fromTo("#{p}-pgW",{{y:1000,rotation:-6,transformOrigin:"50% 50%"}},{{y:0,rotation:0,transformOrigin:"50% 50%",duration:1.0,ease:"expo.out"}},0.05);
  focusInit("#{p}-pg",{K0},{C});
  mark("#{p}-m0",0.8,0.5); mark("#{p}-m1",1.15,0.4);
  rise("#{p}-src > span",0.9);
  focusTo("#{p}-pg",{t_adr - 0.35:.2f},1.2,{K0},{K1},{C});
  mark("#{p}-m2",{t_adr + 0.4:.2f},0.4);
  rise("#{p}-a1 > span",{t_adr:.2f}); rise("#{p}-a2 > span",{t_owen + 0.15:.2f});
  vanish("#{p}-a1",{t_machine - 0.3:.2f},0.3); vanish("#{p}-a2",{t_machine - 0.3:.2f},0.3);
  focusTo("#{p}-pg",{t_machine - 0.3:.2f},1.3,{K1},{K2},{C});
  rise("#{p}-b1 > span",{t_machine:.2f}); rise("#{p}-b2 > span",{t_scanner:.2f});
  draw("#{p}-fig",{t_machine + 0.4:.2f},0.9,2400);
  enter("#{p}-scan",{t_scanner - 0.1:.2f},0.2);
  tl.fromTo("#{p}-scan",{{y:0}},{{y:496,duration:0.7,repeat:1,yoyo:true,ease:"sine.inOut"}},{t_scanner - 0.1:.2f});
  vanish("#{p}-scan",{t_scanner + 1.3:.2f},0.2);
  pop("#{p}-bb0",{t_scanner + 0.5:.2f},0.3); pop("#{p}-bb1",{t_scanner + 0.75:.2f},0.3);
  vanish("#{p}-b1",{t_imagine - 0.4:.2f},0.3); vanish("#{p}-b2",{t_imagine - 0.4:.2f},0.3);
  focusTo("#{p}-pg",{t_imagine - 0.35:.2f},1.2,{K2},{K3},{C});
  focusTo("#{p}-pg",{t_imagine + 0.85:.2f},{dur - t_imagine - 0.85:.2f},{K3},{K4},{C},"none");
  mark("#{p}-m4",{t_imagine + 0.3:.2f},0.6); mark("#{p}-m5",{t_you + 0.3:.2f},0.6);
  rise("#{p}-c1 > span",{t_imagine:.2f}); rise("#{p}-c2 > span",{t_you:.2f}); rise("#{p}-c3 > span",{t_playing - 0.1:.2f},0.6);
"""
    return make_scene(p, dur, svg, html, js)


# ---------------------------------------------------------------- reading 4: in the hospital room, her scan matches healthy people
def reading_4():
    p, sg = "reading_4", 4
    start, dur = seg(SCENE_KEY, sg)
    t_responds, t_same, t_person, t_she, t_listening, t_trapped, t_own, t_noway, t_tell = (2.04, 2.73, 4.4, 5.85, 6.52,
                                                                           7.69, 9.36, 10.1, 11.56)
    gp = f"{p}-g"
    TX, TY, S = 831, 640, 1.0                       # her feet; lying down: local (x, y) becomes (TX - y, TY - x); head at x ~ 1275..1375
    ear = (TX + 482, TY - 6)                        # head (world), where the waves converge
    extra = room_defs(p) + f"""<radialGradient id="{p}-blobG" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff2b0"/><stop offset=".45" stop-color="#ffb23e" stop-opacity=".9"/><stop offset="1" stop-color="#ff7a2a" stop-opacity="0"/></radialGradient>
<clipPath id="{p}-tl"><rect x="176" y="126" width="798" height="300"/></clipPath>"""
    SC = 1.25
    panel = lambda k, cx: (f'<g transform="translate({cx - 192 * SC:.1f} {300 - 84 * SC:.1f}) scale({SC})">{brain_side(f"{p}-c{k}")}'
                            f'<g id="{p}-bl{k}" opacity="0"><circle cx="205" cy="58" r="30" fill="url(#{p}-blobG)"/></g></g>')
    bl = lambda cx: (cx + (205 - 192) * SC, 300 + (58 - 84) * SC)
    (ax_, ay_), (bx_, by_) = bl(375), bl(775)

    def label_svg(k, lines, cx, color):
        tsp = "".join(f'<text x="{cx}" y="{y}" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="44" letter-spacing="6" fill="{color}">{s}</text>'
                      for s, y in lines)
        return f'<clipPath id="{p}-lc{k}"><rect x="{cx - 200}" y="428" width="400" height="104"/></clipPath><g clip-path="url(#{p}-lc{k})"><g id="{p}-lb{k}">{tsp}</g></g>'

    monitor = f"""<g filter="url(#{p}-shadow)"><rect x="555" y="560" width="40" height="236" fill="#3a3a8a" stroke="#8d7bff" stroke-width="3"/><rect x="480" y="788" width="190" height="16" rx="8" fill="#3a3a8a" stroke="#8d7bff" stroke-width="3"/><rect x="150" y="100" width="850" height="460" rx="28" fill="#14122e" stroke="#8d7bff" stroke-width="8"/></g>
<rect x="176" y="126" width="798" height="408" rx="14" fill="url(#{p}-screen)"/>
<line x1="575" y1="150" x2="575" y2="510" stroke="#3a3a8a" stroke-width="4"/>
<g clip-path="url(#{p}-tl)">{panel("a", 375)}{panel("b", 775)}</g>
{label_svg("a", [("HERS", 492)], 375, "#ffd98a")}{label_svg("b", [("HEALTHY", 466), ("PEOPLE", 516)], 775, "#3be0ff")}
<path id="{p}-arc" d="M{ax_:.0f} {ay_ - 30:.0f} Q 575 120 {bx_:.0f} {by_ - 30:.0f}" fill="none" stroke="#ffb23e" stroke-width="7" stroke-linecap="round" stroke-dasharray="700" stroke-dashoffset="700" filter="url(#{p}-glow)"/>"""
    bed = f"""<ellipse cx="1060" cy="936" rx="480" ry="22" fill="#05031a" opacity=".55"/>
<g fill="#4a4ab0"><rect x="690" y="780" width="20" height="140"/><rect x="1410" y="780" width="20" height="140"/></g>
<circle cx="700" cy="922" r="15" fill="#2a2a6a" stroke="#8d7bff" stroke-width="3"/><circle cx="1420" cy="922" r="15" fill="#2a2a6a" stroke="#8d7bff" stroke-width="3"/>
<rect x="660" y="742" width="800" height="46" rx="14" fill="#2a2a6a" stroke="#8d7bff" stroke-width="3"/>
<rect x="1452" y="586" width="34" height="236" rx="14" fill="#3a3a8a" stroke="#8d7bff" stroke-width="4"/>
<rect x="640" y="696" width="820" height="56" rx="22" fill="#dfe4ff"/>
<ellipse cx="1335" cy="694" rx="118" ry="26" fill="#f4f6ff"/>"""
    woman = lying_down(her(gp, "standing", glow=f"{p}-glow", shadow=False), TX, TY, S)
    blanket = (f'<path d="M 650 752 L 650 640 C 680 604 740 600 792 598 C 800 540 884 534 894 596 C 980 590 1060 584 1214 602 C 1228 640 1230 700 1226 752 Z" fill="url(#{p}-blanket)"/>'
             f'<path d="M 820 610 C 920 600 1060 600 1180 614" stroke="#fff" stroke-opacity=".28" stroke-width="10" fill="none" stroke-linecap="round"/>')
    rim = f'<rect id="{p}-rim" x="{TX - 40}" y="530" width="{600}" height="190" rx="95" fill="none" stroke="#ff4f7d" stroke-width="7" opacity="0" filter="url(#{p}-glow)"/>'
    # sound waves: arcs (no clipping) that shrink toward the ear; an invisible circle centers the box on the ear
    a0, a1 = math.radians(200), math.radians(252)
    arc = (f'M{ear[0] + 300 * math.cos(a0):.0f} {ear[1] + 300 * math.sin(a0):.0f} A300 300 0 0 1 '
            f'{ear[0] + 300 * math.cos(a1):.0f} {ear[1] + 300 * math.sin(a1):.0f}')
    waves = "".join(f'<g id="{p}-o{k}" opacity="0"><circle cx="{ear[0]}" cy="{ear[1]}" r="300" fill="none"/>'
                    f'<path d="{arc}" fill="none" stroke="#3be0ff" stroke-width="9" stroke-linecap="round" vector-effect="non-scaling-stroke"/></g>' for k in range(3))
    svg = f"""<rect x="-400" y="-300" width="2720" height="1100" fill="url(#{p}-wall)"/>{ground(p, 800)}
{monitor}{bed}{woman}{blanket}{rim}<g filter="url(#{p}-glow)">{waves}</g>"""
    html = (tx(f"{p}-t0", "She was listening", 1000, 130, 96, "#9af0ff") + tx(f"{p}-t1", "Trapped inside", 1000, 150, 112) +
            tx(f"{p}-t2", "her own body", 1000, 300, 112) + tx(f"{p}-t3", "NO WAY TO TELL ANYONE", 1006, 500, 48, "#ff4f7d", "pill2"))
    C = "960,540"
    K0, K1, KW, KD, KE = "[575,330,1.42]", "[575,330,1.5]", "[960,540,1.0]", "[1540,540,1.8]", "[1540,540,1.9]"
    waves_js = "".join(
        f'tl.fromTo("#{p}-o{k}",{{scale:1.1,opacity:0,transformOrigin:"50% 50%"}},{{scale:0.14,opacity:1,transformOrigin:"50% 50%",duration:0.6,ease:"power1.in",repeat:2,immediateRender:false}},{t_she + 0.2 + k * 0.2:.2f});'
        f'tl.set("#{p}-o{k}",{{opacity:0}},{t_trapped - 0.1:.2f});' for k in range(3))
    rim_js = "".join(f'tl.fromTo("#{p}-rim",{{opacity:0}},{{opacity:1,duration:0.15,repeat:1,yoyo:true,immediateRender:false}},{t_trapped + 0.2 + k * 0.9:.2f});' for k in range(3))
    js = f"""
  focusInit("#{p}-cam",{K0},{C});
  focusTo("#{p}-cam",0,{t_same - 0.4:.2f},{K0},{K1},{C},"none");
  focusTo("#{p}-cam",{t_same - 0.4:.2f},1.2,{K1},{KW},{C});
  focusTo("#{p}-cam",{t_she - 0.35:.2f},1.4,{KW},{KD},{C});
  focusTo("#{p}-cam",{t_she + 1.05:.2f},{dur - t_she - 1.05:.2f},{KD},{KE},{C},"none");
  fade("#{p}-bla",{t_responds:.2f},0.25,0,1); pulse("#{p}-bla",{t_responds:.2f},0.35,1.3,7);
  tl.fromTo("#{p}-lba",{{y:110}},{{y:0,duration:0.75,ease:"expo.out"}},{t_responds + 0.2:.2f});
  fade("#{p}-blb",{t_same + 0.3:.2f},0.25,0,1); pulse("#{p}-blb",{t_same + 0.3:.2f},0.35,1.3,5);
  draw("#{p}-arc",{t_same + 0.4:.2f},0.9,700);
  tl.fromTo("#{p}-lbb",{{y:110}},{{y:0,duration:0.75,ease:"expo.out"}},{t_person:.2f});
  rise("#{p}-t0 > span",{t_she + 0.45:.2f}); vanish("#{p}-t0",{t_trapped - 0.3:.2f},0.3);
  rise("#{p}-t1 > span",{t_trapped:.2f}); rise("#{p}-t2 > span",{t_own:.2f}); rise("#{p}-t3 > span",{t_noway + 0.2:.2f});
  tl.fromTo("#{p}-rim",{{opacity:0}},{{opacity:0.55,duration:0.4,immediateRender:false}},{t_trapped + 2.9:.2f});
""" + waves_js + rim_js + idle_g(gp, dur, (1.5, 4.2, t_listening + 0.1, t_tell - 0.5, t_tell - 0.2))
    return make_scene(p, dur, svg, html, js, extra)


# ---------------------------------------------------------------- reading 5: years of debate, then 241 beds and one in four lights up
def reading_5():
    p, sg = "reading_5", 5
    start, dur = seg(SCENE_KEY, sg)
    t_challenged, t_debate, t_years, t_2024, t_study, t_241, t_signs, t_one = (0.63, 2.04, 2.68, 4.09, 6.41, 7.16,
                                                                 11.88, 13.89)
    cols, rows, x0, y0, px_, py_, ms = 22, 11, 124, 200, 76, 68, 0.235
    rng = random.Random(24)
    slots = [(r, c) for r in range(rows) for c in range(cols)][:241]
    lit_cells = set(rng.sample(slots, 60))
    bed = f"""<g id="{p}-bed"><rect x="-128" y="62" width="14" height="44" fill="#4a4ab0"/><rect x="110" y="62" width="14" height="44" fill="#4a4ab0"/>
<rect x="-136" y="54" width="268" height="16" rx="6" fill="#4a4ab0"/><rect x="124" y="-40" width="20" height="130" rx="9" fill="#6a7bd0"/>
<rect x="-140" y="26" width="270" height="32" rx="12" fill="#dfe4ff"/><ellipse cx="80" cy="24" rx="44" ry="13" fill="#f4f6ff"/>
<circle cx="80" cy="2" r="24" fill="{SKIN}"/><path d="M 84 -22 C 110 -20 112 16 96 22 C 104 8 102 -10 84 -22 Z" fill="#3a2216"/>
<path d="M -132 30 L -132 0 C -122 -26 -98 -26 -90 -6 C -40 -14 20 -16 56 -4 L 60 30 Z" fill="#5a82e0"/></g>
<g id="{p}-lit"><circle cx="80" cy="2" r="58" fill="#ffb23e" opacity=".35"/><circle cx="80" cy="2" r="27" fill="none" stroke="#ffd27a" stroke-width="7"/>
<circle cx="80" cy="-62" r="17" fill="#fff2b0"/></g>"""
    cell = lambda r, c: (x0 + px_ / 2 + c * px_, y0 + py_ / 2 + r * py_)
    center = (5, 10)
    cells, lit = {}, []
    for (r, c) in slots:
        x, y = cell(r, c)
        d = max(abs(r - center[0]), abs(c - center[1]))
        u = f'transform="translate({x:.1f} {y + 6:.1f}) scale({ms})"'
        cells.setdefault(d, []).append(f'<use href="#{p}-bed" {u}/>')
        if (r, c) in lit_cells:
            lit.append(f'<use class="lit" href="#{p}-lit" {u} opacity="0"/>')
    grid = "".join(f'<g id="{p}-d{d}" opacity="0">{"".join(us)}</g>' for d, us in sorted(cells.items()))
    rng.shuffle(lit)
    # debate: two scientists facing each other
    ga, gb = f"{p}-ga", f"{p}-gb"
    debate = f"""<g id="{p}-debate">{ground(p, 930)}
<g transform="translate(640 930)"><g id="{ga}W">{figure(ga, "work", "standing", glow=f"{p}-glow")}</g></g>
<g transform="translate(1290 930) scale(-1 1)"><g id="{gb}W">{tinge(figure(gb, "work", "standing", glow=f"{p}-glow"), SCIENTIST2)}</g></g>"""
    for k, (x, y, s, c) in enumerate([(860, 390, 230, "#ffb23e"), (1070, 340, 200, "#3be0ff"), (960, 560, 170, "#ff4fa3")]):
        debate += (f'<g transform="translate({x} {y})"><g id="{p}-q{k}" opacity="0"><rect x="-10" y="-10" width="20" height="20" fill="none"/>'
                f'<text x="0" y="{s * 0.34:.0f}" text-anchor="middle" font-size="{s}" font-weight="700" font-family="EB Garamond" fill="{c}" stroke="#05031a" stroke-width="6" paint-order="stroke">?</text></g></g>')
    debate += "</g>"
    svg = f"""{debate}<g id="{p}-grid">{grid}</g><g filter="url(#{p}-glow)">{"".join(lit)}</g>"""
    html = (centered(f"{p}-year", f'<span id="{p}-yearN">2006</span>', 40, 150, "#ffd98a") +
            centered(f"{p}-n", f'<span id="{p}-nN">1</span> patients', 4, 104) +
            centered(f"{p}-u", "one out of four", 4, 108, "#ffd98a") +
            centered(f"{p}-src", "BODIEN ET AL. · NEJM · 2024", 990, 40, "#ffb23e", "pill2"))
    C = "960,540"
    KA, KB, KC, KD, KE = "[960,560,1.0]", "[960,560,1.07]", "[960,574,1.7]", "[960,574,1.0]", "[960,574,1.03]"
    rings = "".join(f'enter("#{p}-d{d}",{t_study - 0.1 + d * 0.11:.2f},0.25);' for d in sorted(cells))
    arm = lambda g, t0: arm_js(g, t0, -38, 0.3, 3)
    js = f"""
  focusInit("#{p}-cam",{KA},{C});
  focusTo("#{p}-cam",0,{t_study - 0.6:.2f},{KA},{KB},{C},"none");
  focusTo("#{p}-cam",{t_study - 0.28:.2f},0.02,{KB},{KC},{C},"none");
  focusTo("#{p}-cam",{t_study - 0.25:.2f},2.0,{KC},{KD},{C},"power3.out");
  focusTo("#{p}-cam",{t_study + 1.8:.2f},{dur - t_study - 1.8:.2f},{KD},{KE},{C},"none");
  pop("#{p}-q0",{t_challenged:.2f},0.3); pop("#{p}-q1",{t_debate - 0.4:.2f},0.3); pop("#{p}-q2",{t_debate + 0.3:.2f},0.3);
  {arm(ga, t_challenged)}{arm(gb, t_debate - 0.4)}
  rise("#{p}-year > span",{t_years - 0.3:.2f});
  count_up("{p}-yearN",{t_years:.2f},{max(0.8, t_2024 + 0.4 - t_years):.2f},2006,2024);
  vanish("#{p}-debate",{t_study - 0.6:.2f},0.3);
  vanish("#{p}-year",{t_study - 0.5:.2f},0.3);
  {rings}
  rise("#{p}-n > span",{t_241 - 0.3:.2f});
  count_up("{p}-nN",{t_241 - 0.2:.2f},1.4,1,241);
  vanish("#{p}-n",{t_one - 0.25:.2f},0.25);
  tl.fromTo("#{p}-cam .lit",{{opacity:0}},{{opacity:1,duration:0.25,stagger:{{amount:1.4}}}},{t_signs:.2f});
  rise("#{p}-u > span",{t_one:.2f},0.8);
  rise("#{p}-src > span",{t_signs + 0.6:.2f});
""" + idle_g(ga, t_study, (1.9, 4.4)) + idle_g(gb, t_study, (3.1,))
    return make_scene(p, dur, svg, html, js, extra=bed)


# ---------------------------------------------------------------- reading 6: in the wheelchair, the only door was a machine
def wheelchair():
    """Wheelchair seen from the front, in the local system of figure(..., "sitting") (feet at y=0, seat at y ~ -160, facing front):
    background (backrest, seat, supports, behind the body) and wheels (large, beside the hips, in front)."""
    style = 'fill="#2a1d70" stroke="#8d7bff" stroke-width="4"'
    background = (''.join(f'<rect x="{x - 7}" y="-372" width="14" height="230" rx="7" {style}/><rect x="{x - 13 if x < 0 else x - 1}" y="-380" width="14" height="22" rx="7" fill="#14122e" stroke="#8d7bff" stroke-width="3"/>' for x in (-104, 104))
             + f'<rect x="-98" y="-350" width="196" height="196" rx="18" {style}/>'
             + '<rect x="-82" y="-336" width="164" height="168" rx="12" fill="#3a2a8a" opacity=".6"/>'
             + f'<rect x="-112" y="-174" width="224" height="24" rx="10" {style}/>'
             + ''.join(f'<path d="M {x} -152 L {x * 0.86:.0f} -8" stroke="#8d7bff" stroke-width="7" stroke-linecap="round"/>' for x in (-70, 70))
             + ''.join(f'<rect x="{x}" y="-9" width="84" height="10" rx="5" fill="#8d7bff"/>' for x in (-104, 20))
             + ''.join(f'<circle cx="{x}" cy="-12" r="11" fill="#14122e" stroke="#b4bbe8" stroke-width="4"/>' for x in (-98, 98))
             + ''.join(f'<rect x="{min(x, x * 1.3):.0f}" y="-222" width="{abs(x) * 0.3:.0f}" height="12" rx="6" {style}/>' for x in (-104, 104)))

    def wheel(x):
        spokes = "".join(f'<line x1="{x}" y1="-104" x2="{x + 26 * math.cos(math.radians(a)):.1f}" y2="{-104 + 92 * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 45))
        return (f'<ellipse cx="{x}" cy="-104" rx="32" ry="104" fill="none" stroke="#b4bbe8" stroke-width="10"/>'
                f'<ellipse cx="{x}" cy="-104" rx="24" ry="88" fill="none" stroke="#8d7bff" stroke-width="3.5"/>'
                f'<g stroke="#b4bbe8" stroke-width="2.5" opacity=".8">{spokes}</g><circle cx="{x}" cy="-104" r="8" fill="#b4bbe8"/>')
    return background, wheel(-132) + wheel(132)


def reading_6():
    p, sg = "reading_6", 6
    start, dur = seg(SCENE_KEY, sg)
    t_people, t_only, t_door, t_out, t_head, t_machine = 1.11, 2.14, 2.32, 3.59, 4.92, 5.71
    gp = f"{p}-g"
    GX, GY, GS = 330, 840, 1.05
    background, wheels = wheelchair()
    woman = f'<g transform="translate({GX} {GY}) scale({GS})"><g id="{gp}W">{background}{her(gp, "sitting", glow=f"{p}-glow", chair=False)}{wheels}</g></g>'
    anc = ANCHORS[("home", "sitting", 30)]
    hand = (GX + anc["hand_r"][0] * GS, GY + anc["hand_r"][1] * GS)
    iv_drip = (f'<g><rect x="96" y="836" width="80" height="10" rx="5" fill="#8d7bff"/><line x1="136" y1="330" x2="136" y2="840" stroke="#b4bbe8" stroke-width="7"/>'
            f'<path d="M 112 330 L 160 330" stroke="#b4bbe8" stroke-width="6" stroke-linecap="round"/>'
            f'<rect x="108" y="338" width="56" height="92" rx="14" fill="#cfefff" fill-opacity=".75" stroke="#fff" stroke-width="3"/><rect x="114" y="380" width="44" height="44" rx="10" fill="#9fdcff" opacity=".8"/>'
            f'</g>')
    tube = (f'<path d="M 136 430 C 136 560 {hand[0] - 80:.0f} {hand[1] - 40:.0f} {hand[0] + 4:.0f} {hand[1] + 2:.0f}" fill="none" stroke="#e8f4ff" stroke-width="4" opacity=".85"/>'
             f'<rect x="{hand[0] - 6:.0f}" y="{hand[1] - 4:.0f}" width="18" height="10" rx="3" fill="#f4f6ff" opacity=".9"/>')
    # memories that leave her head through the door
    hc = (GX + anc["head_center"][0] * GS, GY + anc["head_center"][1] * GS)
    orbs = "".join(orb(f"{p}-o{k}", s, hc[0] + dx, hc[1] + dy, c, 40) for k, (s, c, dx, dy) in
                    enumerate([("heart", "#ff4fa3", 120, -95), ("note", "#3be0ff", 195, -35), ("sun", "#ffb23e", 200, 50)]))
    svg = ground(p) + machine(p) + door_svg(p, 0) + iv_drip + woman + tube + f'<g id="{p}-orbs">{orbs}</g>'
    html = (tx(f"{p}-t1", "The only door", 1060, 70, 120) + tx(f"{p}-t2", "a machine", 1180, 880, 120, "#9af0ff"))
    C = "960,540"
    K0, K1, K2 = "[560,560,1.35]", "[560,560,1.42]", "[960,580,1.0]"
    target = (1560, 560)
    orb_js = ""
    for k, (dx, dy) in enumerate([(120, -95), (195, -35), (200, 50)]):
        sx, sy = hc[0] + dx, hc[1] + dy
        orb_js += (f'pop("#{p}-o{k}",{t_people + 0.2 + k * 0.25:.2f},0.3,0.6);'
                   f'tl.fromTo("#{p}-o{k}",{{x:0,y:0}},{{x:{966 - sx:.0f},y:{600 - sy:.0f},duration:1.3,ease:"power2.inOut",immediateRender:false}},{t_out + 0.1 + k * 0.22:.2f});'
                   f'tl.fromTo("#{p}-o{k}",{{x:{966 - sx:.0f},y:{600 - sy:.0f},scale:1}},{{x:{target[0] - sx:.0f},y:{target[1] - sy:.0f},scale:0.4,duration:0.9,ease:"power2.in",immediateRender:false}},{t_machine - 0.5 + k * 0.12:.2f});'
                   f'tl.fromTo("#{p}-o{k}",{{opacity:1}},{{opacity:0,duration:0.2,immediateRender:false}},{t_machine + 0.3 + k * 0.12:.2f});')
    js = f"""
  focusInit("#{p}-cam",{K0},{C});
  focusTo("#{p}-cam",0,{t_head - 0.3:.2f},{K0},{K1},{C},"none");
  focusTo("#{p}-cam",{t_head - 0.3:.2f},1.6,{K1},{K2},{C});
  tl.set("#{p}-machine",{{opacity:0}},0);
  pop("#{p}-door",{t_door - 0.2:.2f},0.3,0.8);
  rise("#{p}-t1 > span",{t_only:.2f});
  glance("#{gp}-eye",{t_door + 0.1:.2f},0,3);
  swing("#{p}-leaf",{t_out:.2f},1.1,1,0.7);
  enter("#{p}-light",{t_out:.2f},0.6); enter("#{p}-wedge",{t_out + 0.2:.2f},0.8);
  fade("#{p}-machine",{t_head - 0.2:.2f},0.8,0,0.45); fade("#{p}-machine",{t_machine:.2f},0.4,0.45,1);
  tl.fromTo("#{p}-ring",{{opacity:0.35}},{{opacity:1,duration:0.3,immediateRender:false}},{t_machine:.2f});
  tl.fromTo("#{p}-tunnel",{{opacity:0.25}},{{opacity:1,duration:0.4,immediateRender:false}},{t_machine:.2f});
  pulse("#{p}-ring",{t_machine + 0.3:.2f},0.25,1.04,1);
  rise("#{p}-t2 > span",{t_machine:.2f});
""" + orb_js + idle_g(gp, dur, (1.2, 5.3), hip=-170)
    return make_scene(p, dur, svg, html, js, trio_defs(p))


# ---------------------------------------------------------------- reading 8: Tang 2023, real page
def reading_8():
    p, sg = "reading_8", 8
    start, dur = seg(SCENE_KEY, sg)
    (t_without, t_university, t_texas, t_scans, t_model, t_language, t_reconstruct, t_gist, t_hearing, t_imagining) = (
        0.97, 2.64, 3.43, 4.07, 5.04, 5.61, 7.1, 8.17, 11.12, 11.82)
    W, H = 1600, 2071
    marks = [("h0", 182, 189, 1140, 38), ("h1", 638, 408, 412, 34), ("h1b", 588, 461, 402, 34),
              ("h2", 184, 1054, 506, 40), ("h3", 826, 1162, 326, 40), ("h4", 1176, 946, 154, 40), ("h4b", 184, 1000, 431, 40),
              ("h5", 1010, 1108, 360, 40), ("h5b", 184, 1162, 84, 40)]
    svg = page(p, "tang2023", W, H, (740, 60, 1120, 960), marks)
    C = "1300,540"
    K0, K1, K2, K3 = "[800,690,0.71]", "[760,526,0.92]", "[790,1040,0.88]", "[790,1110,0.88]"
    L = 80
    html = (tx(f"{p}-a1", "Without", L, 190, 150) + tx(f"{p}-a2", "surgery", L, 370, 150, "#9af0ff") +
            tx(f"{p}-b1", "University", L, 250, 104) + tx(f"{p}-b2", "of Texas", L, 390, 104, "#ffd98a") +
            tx(f"{p}-c1", "Brain scans", L, 200, 104) + tx(f"{p}-c2", "and a language", L, 350, 80) + tx(f"{p}-c3", "model", L, 460, 104, "#9af0ff") +
            tx(f"{p}-d1", "Reconstruct", L, 170, 104) + tx(f"{p}-d2", "the gist", L, 310, 104, "#ffd98a") +
            tx(f"{p}-d3", "hearing or", L, 480, 92) + tx(f"{p}-d4", "imagining", L, 600, 104, "#9af0ff") +
            tx(f"{p}-src1", "BIORXIV · PREPRINT", L, 860, 42, "#ffb23e", "pill2") + tx(f"{p}-src2", "2022", L, 924, 42, "#ffb23e", "pill2"))
    js = f"""
  tl.fromTo("#{p}-pgW",{{y:1000,rotation:6,transformOrigin:"50% 50%"}},{{y:0,rotation:0,transformOrigin:"50% 50%",duration:1.0,ease:"expo.out"}},0.05);
  focusInit("#{p}-pg",{K0},{C});
  rise("#{p}-a1 > span",{t_without:.2f}); rise("#{p}-a2 > span",{t_without + 0.3:.2f});
  rise("#{p}-src1 > span",0.9); rise("#{p}-src2 > span",1.05);
  focusTo("#{p}-pg",{t_without + 0.6:.2f},1.2,{K0},{K1},{C});
  mark("#{p}-h0",{t_without + 1.0:.2f},0.7);
  vanish("#{p}-a1",{t_university - 0.3:.2f},0.3); vanish("#{p}-a2",{t_university - 0.3:.2f},0.3);
  rise("#{p}-b1 > span",{t_university:.2f}); rise("#{p}-b2 > span",{t_texas - 0.2:.2f});
  mark("#{p}-h1",{t_university + 0.1:.2f},0.5); mark("#{p}-h1b",{t_university + 0.45:.2f},0.5);
  vanish("#{p}-b1",{t_scans - 0.3:.2f},0.3); vanish("#{p}-b2",{t_scans - 0.3:.2f},0.3);
  focusTo("#{p}-pg",{t_scans - 0.3:.2f},1.2,{K1},{K2},{C});
  focusTo("#{p}-pg",{t_scans + 0.9:.2f},{dur - t_scans - 0.9:.2f},{K2},{K3},{C},"none");
  rise("#{p}-c1 > span",{t_scans:.2f}); mark("#{p}-h2",{t_scans + 0.5:.2f},0.6);
  rise("#{p}-c2 > span",{t_model - 0.2:.2f}); rise("#{p}-c3 > span",{t_language:.2f}); mark("#{p}-h3",{t_model + 0.2:.2f},0.5);
  vanish("#{p}-c1",{t_reconstruct - 0.3:.2f},0.3); vanish("#{p}-c2",{t_reconstruct - 0.3:.2f},0.3); vanish("#{p}-c3",{t_reconstruct - 0.3:.2f},0.3);
  rise("#{p}-d1 > span",{t_reconstruct:.2f}); mark("#{p}-h4",{t_reconstruct + 0.1:.2f},0.4); mark("#{p}-h4b",{t_reconstruct + 0.45:.2f},0.6);
  rise("#{p}-d2 > span",{t_gist:.2f});
  rise("#{p}-d3 > span",{t_hearing:.2f}); rise("#{p}-d4 > span",{t_imagining:.2f});
  mark("#{p}-h5",{t_hearing:.2f},0.5); mark("#{p}-h5b",{t_imagining:.2f},0.3);
"""
    return make_scene(p, dur, svg, html, js)


# ---------------------------------------------------------------- reading 9: the volunteer lying in the scanner, 16 hours of training, and the system fails
def _bez(a, b, c, d, n):
    out = []
    for k in range(n + 1):
        u = k / n
        out.append(tuple(round((1 - u) ** 3 * a[i] + 3 * (1 - u) ** 2 * u * b[i] + 3 * (1 - u) * u ** 2 * c[i] + u ** 3 * d[i]) for i in (0, 1)))
    return out


def reading_9():
    p, sg = "reading_9", 9
    start, dur = seg(SCENE_KEY, sg)
    t_wasnt, t_word, t_word2, t_each, t_trained, t_16, t_hours, t_resisted, t_else, t_system2, t_failed = (
        0.38, 0.72, 2.05, 2.78, 4.11, 6.09, 6.63, 8.12, 9.99, 10.97, 11.63)
    gp = f"{p}-g"
    extra = trio_defs(p) + room_defs(p)
    vol = on_head(tinge(figure(gp, "home", "standing", glow=f"{p}-glow", shadow=False), VOLUNTEER), gp, headphones())
    TX, TY, S = 1170, 650, 0.7
    table_extra = ('<rect x="1050" y="640" width="130" height="34" rx="12" fill="#dfe4ff" stroke="#8d7bff" stroke-width="3"/>'
                  '<rect x="1070" y="674" width="22" height="166" fill="#2a2a6a"/>')
    # control monitor on the table, on the left
    chips1 = "".join(f'<rect id="{p}-w{k}" x="{x}" y="392" width="{w}" height="26" rx="8" fill="#9af0ff" opacity="0"/>'
                     for k, (x, w) in enumerate([(236, 44), (290, 30), (330, 58), (398, 36), (444, 50), (504, 28), (542, 46), (598, 26)]))
    chips2 = "".join(f'<rect id="{p}-i{k}" x="{x}" y="456" width="{w}" height="40" rx="12" fill="#ffd27a" opacity="0"/>' for k, (x, w) in enumerate([(236, 150), (398, 110), (520, 104)]))
    monitor = f"""<ellipse cx="430" cy="846" rx="320" ry="18" fill="#05031a" opacity=".55"/>
<rect x="160" y="690" width="560" height="22" rx="8" fill="#3a3a8a" stroke="#8d7bff" stroke-width="3"/><rect x="186" y="712" width="20" height="128" fill="#2a2a6a"/><rect x="674" y="712" width="20" height="128" fill="#2a2a6a"/>
<rect x="410" y="640" width="40" height="52" fill="#2a2a6a"/><rect x="360" y="682" width="140" height="12" rx="6" fill="#2a2a6a"/>
<g filter="url(#{p}-shadow)"><rect x="200" y="330" width="460" height="316" rx="22" fill="#14122e" stroke="#8d7bff" stroke-width="7"/></g>
<rect x="222" y="352" width="416" height="272" rx="10" fill="url(#{p}-screen)"/>
{chips1}{chips2}<rect x="236" y="548" width="388" height="22" rx="11" fill="#2a2a6a"/><rect id="{p}-bar" x="236" y="548" width="388" height="22" rx="11" fill="#38e8a8"/>
<rect id="{p}-screenR" x="222" y="352" width="416" height="272" rx="10" fill="#ff4f7d" opacity="0"/>"""
    cable_pts = _bez((1300, 800), (1100, 838), (820, 838), (700, 760), 12)
    cable = f'<path d="M1300 800 C 1100 838 820 838 700 760" fill="none" stroke="#5a5ad0" stroke-width="9" stroke-linecap="round"/>'
    packets = "".join(f'<circle id="{p}-pk{k}" cx="0" cy="0" r="10" fill="#3be0ff" opacity="0" filter="url(#{p}-glow)"/>' for k in range(3))
    clock = f"""<g transform="translate(930 200) scale(.85)"><g id="{p}-clock"><circle r="96" fill="#eef1ff" stroke="#8d7bff" stroke-width="10"/><circle r="84" fill="#14122e"/>
<g fill="#8d7bff"><rect x="-4" y="-78" width="8" height="16"/><rect x="-4" y="62" width="8" height="16"/><rect x="62" y="-4" width="16" height="8"/><rect x="-78" y="-4" width="16" height="8"/></g>
<g id="{p}-hand"><line x1="0" y1="0" x2="0" y2="-64" stroke="#eef1f7" stroke-width="8" stroke-linecap="round"/></g><g id="{p}-hand2"><line x1="0" y1="0" x2="40" y2="0" stroke="#ffb23e" stroke-width="11" stroke-linecap="round"/></g><circle r="9" fill="#ffb23e"/></g></g>"""
    thought = (f'<g id="{p}-thought" opacity="0"><circle cx="1500" cy="575" r="10" fill="#2a1d70" stroke="#ff4fa3" stroke-width="4"/><circle cx="1462" cy="510" r="15" fill="#2a1d70" stroke="#ff4fa3" stroke-width="4"/><circle cx="1405" cy="430" r="22" fill="#2a1d70" stroke="#ff4fa3" stroke-width="4"/>'
           f'<ellipse cx="1200" cy="250" rx="180" ry="130" fill="#2a1d70" stroke="#ff4fa3" stroke-width="6" filter="url(#{p}-glow)"/>'
           + picture(f"{p}-beach", "beach", 1200, 250, 0.82) + '</g>')
    svg = (ground(p) + monitor + cable + machine(p) + table_extra + lying_down(vol, TX, TY, S) + packets + clock + thought)
    html = (centered(f"{p}-t1", "It wasn't word for word", 50, 104) +
            tx(f"{p}-h", f'<span id="{p}-hN">0</span> hours', 1070, 130, 100, "#ffd98a") +
            centered(f"{p}-t2", "the system failed", 880, 120, "#ff4f7d"))
    C = "960,540"
    K0, K1, K2, K3 = "[430,500,1.6]", "[430,500,1.66]", "[960,560,1.0]", "[1000,560,1.05]"
    w_js = "".join(f'tl.fromTo("#{p}-w{k}",{{opacity:0}},{{opacity:1,duration:0.12}},{t_word + k * 0.14:.2f});' for k in range(8))
    i_js = "".join(f'pop("#{p}-i{k}",{t_word2 + k * 0.18:.2f},0.4,0.5);' for k in range(3))
    pk_js = ""
    xs, ys = [x for x, _ in cable_pts], [y for _, y in cable_pts]
    for j, t0 in enumerate([t_trained + 0.2 + k * 0.45 for k in range(int((t_resisted - 0.6 - t_trained) / 0.45))]):
        k = j % 3
        pk_js += (f'tl.set("#{p}-pk{k}",{{x:{xs[0]},y:{ys[0]},opacity:1}},{t0:.2f});'
                  f'tl.to("#{p}-pk{k}",{{keyframes:{{x:{xs},y:{ys}}},duration:1.2,ease:"none",immediateRender:false}},{t0:.2f});'
                  f'tl.set("#{p}-pk{k}",{{opacity:0}},{t0 + 1.2:.2f});')
    js = f"""
  focusInit("#{p}-cam",{K0},{C});
  focusTo("#{p}-cam",0,{t_each - 0.3:.2f},{K0},{K1},{C},"none");
  focusTo("#{p}-cam",{t_each - 0.3:.2f},1.4,{K1},{K2},{C});
  focusTo("#{p}-cam",{t_failed - 0.4:.2f},{dur - t_failed + 0.4:.2f},{K2},{K3},{C},"power2.inOut");
  tl.set("#{p}-tunnel",{{opacity:1}},0); tl.set("#{p}-ring",{{opacity:1}},0);
  rise("#{p}-t1 > span",{t_wasnt:.2f});
  vanish("#{p}-t1",{t_each - 0.2:.2f},0.3);
  {w_js}{i_js}
  pop("#{p}-clock",{t_trained - 0.2:.2f},0.3,0.7);
  tl.fromTo("#{p}-hand",{{rotation:0,transformOrigin:"50% 100%"}},{{rotation:5760,transformOrigin:"50% 100%",duration:{t_hours + 0.4 - t_trained:.2f},ease:"power1.inOut"}},{t_trained:.2f});
  tl.fromTo("#{p}-hand2",{{rotation:0,transformOrigin:"0% 50%"}},{{rotation:480,transformOrigin:"0% 50%",duration:{t_hours + 0.4 - t_trained:.2f},ease:"power1.inOut"}},{t_trained:.2f});
  tl.fromTo("#{p}-bar",{{scaleX:0.02,transformOrigin:"0% 50%"}},{{scaleX:1,transformOrigin:"0% 50%",duration:{t_hours + 0.4 - t_trained:.2f},ease:"power1.inOut"}},{t_trained:.2f});
  rise("#{p}-h > span",{t_trained:.2f});
  count_up("{p}-hN",{t_trained + 0.1:.2f},{t_hours + 0.3 - t_trained:.2f},0,16);
  pulse("#{p}-ring",{t_16:.2f},0.2,1.05,3);
  vanish("#{p}-clock",{t_resisted - 0.6:.2f},0.3); vanish("#{p}-h",{t_resisted - 0.6:.2f},0.3);
  pop("#{p}-thought",{t_else - 0.6:.2f},0.3,0.7);
  vanish("#{p}-tunnel",{t_system2:.2f},0.2); vanish("#{p}-ring",{t_system2:.2f},0.2);
  tl.fromTo("#{p}-tunnelR",{{opacity:0}},{{opacity:1,duration:0.08,repeat:9,yoyo:true,ease:"steps(1)",immediateRender:false}},{t_system2:.2f});
  tl.fromTo("#{p}-ringR",{{opacity:0}},{{opacity:1,duration:0.15,immediateRender:false}},{t_system2:.2f});
  tl.fromTo("#{p}-screenR",{{opacity:0}},{{opacity:0.55,duration:0.08,repeat:5,yoyo:true,ease:"steps(1)",immediateRender:false}},{t_failed - 0.2:.2f});
  tl.fromTo("#{p}-screenR",{{opacity:0}},{{opacity:0.5,duration:0.2,immediateRender:false}},{t_failed + 0.3:.2f});
  tl.fromTo("#{p}-bar",{{fill:"#38e8a8"}},{{fill:"#ff4f7d",duration:0.2,immediateRender:false}},{t_failed - 0.2:.2f});
  tl.fromTo("#{p}-machine",{{x:0}},{{x:6,duration:0.05,repeat:9,yoyo:true,ease:"none",immediateRender:false}},{t_failed:.2f});
  rise("#{p}-t2 > span",{t_failed:.2f});
""" + "".join(f'tl.fromTo("#{p}-i{k}",{{x:0}},{{x:{(-1) ** k * 14},duration:0.06,repeat:7,yoyo:true,ease:"none",immediateRender:false}},{t_failed:.2f});' for k in range(3)) + pk_js + idle_g(gp, dur, (2.9, 6.8, t_else))
    return make_scene(p, dur, svg, html, js, extra)


# ---------------------------------------------------------------- reading 10: at home, the machine knocks on the door and needs your cooperation
def reading_10():
    p, sg = "reading_10", 10
    start, dur = seg(SCENE_KEY, sg)
    t_today, t_read, t_mind, t_machine, t_needs, t_your, t_coop = 0.36, 0.93, 1.85, 2.07, 2.29, 3.32, 3.55
    gp = f"{p}-g"
    GX, GS, STEP = 690, 0.72, 100                 # person walks to the door (rotated arm brings the hand to the knob at x ~ 896)
    extra = trio_defs(p) + f"""<linearGradient id="{p}-wallG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a2d7a"/><stop offset="1" stop-color="#241a5a"/></linearGradient>"""
    wall = (f'<rect x="-400" y="-300" width="1500" height="1140" fill="url(#{p}-wallG)"/>'
              f'<rect x="-400" y="800" width="1500" height="40" fill="#1c1450"/>'
              f'<rect x="1084" y="-300" width="16" height="1140" fill="#4a3a9a"/><line x1="1100" y1="-300" x2="1100" y2="840" stroke="#8d7bff" stroke-width="4" opacity=".6"/>'
              + picture(f"{p}-qa", "family", 220, 380, 0.85) + picture(f"{p}-qb", "birthday", 500, 340, 0.72) + picture(f"{p}-qc", "dog", 470, 560, 0.62))
    knocks = "".join(f'<circle id="{p}-k{k}" cx="1100" cy="600" r="20" fill="none" stroke="#ffb23e" stroke-width="7" opacity="0"/>' for k in range(3))
    # smaller machine, further back, outside the house (in reading_9 it fills the whole right side, at full size)
    MS_, MTX, MTY = 0.7, 520, 838 - 846 * 0.7
    tunnel_c = (MTX + 1560 * MS_, MTY + 560 * MS_)
    small_machine = f'<g transform="translate({MTX} {MTY:.1f}) scale({MS_})">{machine(p)}</g>'
    beam = f'<path id="{p}-beam" d="M{tunnel_c[0] - 135:.0f} {tunnel_c[1] - 30:.0f} L1090 {tunnel_c[1] - 30:.0f}" fill="none" stroke="#3be0ff" stroke-width="10" stroke-linecap="round" stroke-dasharray="40 26" opacity="0" filter="url(#{p}-glow)"/>'
    person_ = f'<g transform="translate({GX} 840) scale({GS})"><g id="{gp}W">{figure(gp, "home", "standing", glow=f"{p}-glow")}</g></g>'
    pos = [("heart", "#ff4fa3", 610, 292), ("cake", "#ffb23e", 740, 268), ("car", "#3be0ff", 870, 300)]
    orbs = "".join(orb(f"{p}-o{k}", s, x, y, c, 40) for k, (s, c, x, y) in enumerate(pos))
    svg = ground(p) + wall + small_machine + door_svg(p, 0) + knocks + beam + person_ + orbs
    html = (tx(f"{p}-t1", "Today,", 250, 34, 110) + tx(f"{p}-t2", "the machine needs", 600, 34, 110) +
            centered(f"{p}-t3", "your cooperation", 905, 112, "#ffd98a"))
    C = "960,540"
    knock_js = "".join(f'tl.fromTo("#{p}-k{k}",{{attr:{{r:20}},opacity:1}},{{attr:{{r:80}},opacity:0,duration:0.45,ease:"power2.out",immediateRender:false}},{t_needs + k * 0.3:.2f});' for k in range(3))
    orb_js = ""
    for k, (_, _, x, y) in enumerate(pos):
        orb_js += (f'pop("#{p}-o{k}",{t_mind - 0.3 + k * 0.2:.2f},0.3,0.6);'
                   f'tl.fromTo("#{p}-o{k}",{{y:0}},{{y:-10,duration:0.7,repeat:1,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_mind + 0.4 + k * 0.2:.2f});'
                   f'tl.fromTo("#{p}-o{k}",{{x:0,y:0,scale:1}},{{x:{tunnel_c[0] - x:.0f},y:{tunnel_c[1] - y:.0f},scale:0.45,duration:1.1,ease:"power2.inOut",immediateRender:false}},{t_coop + 0.7 + k * 0.18:.2f});'
                   f'tl.fromTo("#{p}-o{k}",{{opacity:1}},{{opacity:0,duration:0.2,immediateRender:false}},{t_coop + 1.65 + k * 0.18:.2f});')
    js = f"""
  focusInit("#{p}-cam",[960,560,1.0],{C});
  focusTo("#{p}-cam",0,{t_coop:.2f},[960,560,1.0],[930,560,1.06],{C},"none");
  focusTo("#{p}-cam",{t_coop:.2f},1.4,[930,560,1.06],[1000,560,1.0],{C});
  tl.set("#{p}-tunnel",{{opacity:1}},0); tl.set("#{p}-ring",{{opacity:1}},0);
  rise("#{p}-t1 > span",{t_today:.2f});
  enter("#{p}-beam",{t_read:.2f},0.3);
  tl.fromTo("#{p}-beam",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-132}},duration:0.6,repeat:4,ease:"none"}},{t_read:.2f});
  pulse("#{p}-ring",{t_read:.2f},0.25,1.04,3);
  rise("#{p}-t2 > span",{t_machine:.2f});
  {knock_js}
  tl.fromTo("#{p}-door",{{x:0}},{{x:5,duration:0.05,repeat:5,yoyo:true,ease:"none",immediateRender:false}},{t_needs:.2f});
  glance("#{gp}-eye",{t_needs + 0.2:.2f},0,3);
  rise("#{p}-t3 > span",{t_your:.2f},0.8);
  vanish("#{p}-beam",{t_coop:.2f},0.3);
  tl.fromTo("#{gp}W",{{x:0}},{{x:{STEP / GS:.0f},duration:0.7,ease:"power2.inOut",immediateRender:false}},{t_coop - 0.55:.2f});
  tl.fromTo("#{gp}W",{{y:0}},{{y:-10,duration:0.175,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_coop - 0.55:.2f});
  {arm_js(gp, t_coop + 0.1, -35, 0.4, variant="home")}
  swing("#{p}-leaf",{t_coop + 0.4:.2f},1.0,1,0.16,"power3.out");
  enter("#{p}-light",{t_coop + 0.4:.2f},0.5); enter("#{p}-wedge",{t_coop + 0.55:.2f},0.6);
""" + orb_js + idle_g(gp, dur, (1.4, 4.9))
    return make_scene(p, dur, svg, html, js, extra)


# ---------------------------------------------------------------- reading 11: "Today." (the person's face up close, in the door light)
def reading_11():
    p, sg = "reading_11", 11
    start, dur = seg(SCENE_KEY, sg)
    S = 3.3
    hp = f"{p}-h"
    extra = f"""<linearGradient id="{p}-lightR" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff2b8" stop-opacity="0"/><stop offset="1" stop-color="#fff2b8" stop-opacity=".85"/></linearGradient>"""
    shoulder = (f'<path d="M 860 1100 C 870 960 960 900 1120 890 C 1300 880 1420 930 1470 1100 Z" fill="{HOME["torso"]}"/>'
             f'<path d="M 860 1100 C 870 960 960 900 1060 892 C 1010 960 1000 1030 1000 1100 Z" fill="{HOME["torso2"]}" opacity=".55"/>')
    neck = (f'<rect x="1078" y="720" width="132" height="230" rx="40" fill="{SKIN}"/>'
               f'<path d="M 1078 800 Q 1144 850 1210 800 L 1210 860 L 1078 860 Z" fill="#140a2e" opacity=".28"/>')
    svg = (f'<rect id="{p}-light" x="1500" y="-100" width="900" height="1300" fill="url(#{p}-lightR)" opacity=".8"/>' + neck + shoulder +
           f'<g transform="translate({1240 - 205 * S:.0f} {140 - 28 * S:.0f}) scale({S})"><g id="{p}-headB">{head(hp, HOME)}</g></g>')
    html = tx(f"{p}-t1", "Today", 80, 380, 210, "#ffd98a")
    C = "960,540"
    js = f"""
  focusInit("#{p}-cam",[1100,560,1.0],{C});
  focusTo("#{p}-cam",0,{dur:.2f},[1100,560,1.0],[1120,560,1.06],{C},"none");
  rise("#{p}-t1 > span",0.08,0.7);
  tl.fromTo("#{hp}-eye",{{x:0}},{{x:3,duration:0.3,ease:"power2.inOut"}},0.3);
  tl.fromTo("#{hp}-eye",{{scaleY:1,transformOrigin:"50% 50%"}},{{scaleY:0.08,transformOrigin:"50% 50%",duration:0.08,repeat:1,yoyo:true,immediateRender:false}},0.8);
  tl.fromTo("#{p}-light",{{opacity:0.8}},{{opacity:0.45,duration:0.07,repeat:5,yoyo:true,ease:"steps(1)",immediateRender:false}},0.5);
"""
    out = make_scene(p, dur, svg, html, js, extra)
    # 1.27 s scene: the default fade-in (0.4 s) would eat a third of it; here it is short
    return out.replace(f'tl.fromTo("#{p}-black", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.4', f'tl.fromTo("#{p}-black", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.12')


SEGS = [(0, reading_0), (1, reading_1), (3, reading_3), (4, reading_4), (5, reading_5), (6, reading_6), (8, reading_8), (9, reading_9), (10, reading_10), (11, reading_11)]
SCENES = [(f"reading_{i}", fn, seg(SCENE_KEY, i)[1]) for i, fn in SEGS]
SEG_MAP = {(SCENE_KEY, i): f"reading_{i}" for i, _ in SEGS}

if __name__ == "__main__":
    print(write_scenes(SCENES, HERE_G))
