"""Group g8_closing2: scene "closing", segments 3, 4, 5, 6, 8 and 9.

  python3 build_g8_closing2.py     # writes compositions/ and index.html in this folder

Round 2: the head with a brain is gone; the real person (figure.py) enters in everyday-life scenes.
3 the person at work, sitting at the desk with the laptop, inside the ring of principles
4 living room (mirrored shot): the person standing with headphones in hand, sofa and pictures, the voice wave in the room
5 close-up of the person wearing headphones; the wave turns into pixels (AI), fifteen minutes, trusted it
6 the person on the sofa, turned the other way, checking the sources on the phone
8 the scientists' key (mouse) and, in your case, the person in the office facing the file cabinet with the lit keyhole
9 the person, by the home wall with the pictures of her life, facing the half-open door, key raised, amber light and someone on the other side (final shot)
"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "../../scenes-v4"))
from engine import *
from engine import _norm
from art2 import H_LINE
import build4 as b4
from figure import figure, picture, ANCHORS
HERE = os.path.dirname(os.path.abspath(__file__))  # engine exports its own HERE; this one is this folder's
_WORDS_EN = {}


def segment_words(scene, i):
    """Same as engine.segment_words_pt, but reads the English narration from words/<scene>.json (in this folder).
    Format: [{"text","start","end","id"}], absolute times in the scene, in s at 1x speed."""
    if scene not in _WORDS_EN:
        f = os.path.join(HERE, "words", f"{scene}.json")
        _WORDS_EN[scene] = json.load(open(f)) if os.path.exists(f) else []
    s = SEGMENTS[scene][i]
    start, dur = s["start"], s["dur"]
    return [(w["text"], round(w["start"] - start, 2), round(w["end"] - start, 2)) for w in _WORDS_EN[scene] if start - 0.05 <= w["start"] < start + dur]

CE = "closing"
SEG_MAP = {(CE, 3): "closing_3", (CE, 4): "closing_4", (CE, 5): "closing_5",
        (CE, 6): "closing_6", (CE, 8): "closing_8", (CE, 9): "closing_9", (CE, 10): "closing_10"}


def J(s, **kw):
    """Replaces @name@ with the value (float with 2 decimals). Avoids doubled f-string braces in the JS."""
    for k, v in kw.items():
        s = s.replace(f"@{k}@", f"{v:.2f}" if isinstance(v, float) else str(v))
    return s


JS_EXTRA = r"""
  // second camera move: same as the engine's camZ, without the initial tl.set at t=0 (which overwrote the first zoom)
  function camZb(sel,t0,dur,z0,z1,ox,oy,ease){
    var o={l:Math.log(z0)};
    tl.to(o,{l:Math.log(z1),duration:dur,ease:ease||"power3.inOut",onUpdate:function(){gsap.set(sel,{scale:Math.exp(o.l),svgOrigin:ox+" "+oy});},immediateRender:false},t0);
  }
  function slideOut(sel,t){tl.fromTo(sel,{yPercent:0},{yPercent:-125,duration:0.45,ease:"power3.in",immediateRender:false},t);}
"""

MONO = "font-family:'IBM Plex Mono',monospace;font-weight:500;letter-spacing:.12em"


# ---------------------------------------------------------------- pieces
def gold_defs(p):
    return (f'<linearGradient id="{p}-gold" x1="0" y1="-1" x2="0" y2="1" gradientUnits="objectBoundingBox"><stop offset="0" stop-color="#ffe7a0"/>'
            f'<stop offset=".5" stop-color="#ffb23e"/><stop offset="1" stop-color="#d9811c"/></linearGradient>'
            f'<radialGradient id="{p}-halo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffb23e" stop-opacity=".38"/><stop offset="1" stop-color="#ffb23e" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{p}-paper" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#e9dcc2"/></linearGradient>')


def key_svg(p, k="key"):
    """Amber key lying flat, ring at (0,0), tip pointing right (~ x -53..270). Id {p}-{k}."""
    return (f'<g id="{p}-{k}"><ellipse cx="110" cy="0" rx="230" ry="110" fill="url(#{p}-halo)"/>'
            f'<circle cx="0" cy="0" r="40" fill="none" stroke="#ffb23e" stroke-width="28" filter="url(#{p}-glow)"/>'
            f'<circle cx="0" cy="0" r="40" fill="none" stroke="#ffd27a" stroke-width="18"/>'
            f'<rect x="50" y="-15" width="28" height="30" rx="6" fill="#ffb23e"/>'
            f'<rect x="72" y="-11" width="200" height="22" rx="10" fill="#f0a234"/>'
            f'<path d="M198 9 h24 v36 h-24z M238 9 h28 v26 h-28z" fill="#e4932a"/>'
            f'<path d="M84 -5 H262" stroke="#fff6d8" stroke-width="5" stroke-linecap="round" opacity=".75"/>'
            f'<path d="M-30 -22 A 37 37 0 0 1 18 -36" stroke="#fff6d8" stroke-width="6" fill="none" stroke-linecap="round" opacity=".85"/></g>')


def keyhole(p, k, cx, cy, s, lit=True):
    """Keyhole: dark hole with an amber rim. If lit, amber light leaks out."""
    glow = f'<ellipse cx="0" cy="22" rx="120" ry="140" fill="url(#{p}-halo)"/>' if lit else ""
    return (f'<g transform="translate({cx} {cy}) scale({s})"><g id="{p}-{k}">{glow}'
            f'<path d="M0 -44 a30 30 0 0 1 17 55 L30 80 L-30 80 L-17 11 A30 30 0 0 1 0 -44Z" fill="#120a30" stroke="#ffb23e" stroke-width="7" stroke-linejoin="round" filter="url(#{p}-glow)"/>'
            f'<path d="M0 -30 a16 16 0 0 1 9 29 L16 66 L-16 66 L-9 -1 A16 16 0 0 1 0 -30Z" fill="#ffcf6a" opacity=".55"/></g></g>')


def doc(p, k, color):
    """Source page (paper with a colored band and lines), centered at (0,0), 230 x 300."""
    lines = "".join(f'<rect x="-88" y="{-70 + j * 30}" width="{176 if j % 3 else 120}" height="10" rx="5" fill="#8a7f68" opacity=".5"/>' for j in range(7))
    return (f'<g id="{p}-{k}"><g filter="url(#{p}-shadow)"><rect x="-115" y="-150" width="230" height="300" rx="16" fill="url(#{p}-paper)"/></g>'
            f'<path d="M-115 -104 V-134 a16 16 0 0 1 16 -16 H99 a16 16 0 0 1 16 16 V-104Z" fill="{color}"/>{lines}</g>')


# ---------------------------------------------------------------- the real person (figure.py) and the set
def anchor(var, pose):
    return ANCHORS[(var, pose, 30)]


def neck_pivot(var, pose):
    """Head pivot (base of the neck) in figure's local space. Use with svgOrigin: the new character's groups have
    a huge box (20000 px clipPaths), so a transformOrigin in % throws the pivot thousands of px away."""
    cx, cy = anchor(var, pose)["head_center"]
    return f"{cx} {cy + 45}"


def shoulder_pivot(var, pose):
    return "%s %s" % anchor(var, pose)["shoulder_arm"]


def rigged_figure(pg, var, pose, head_extra="", hand="", mug=None, chair=True):
    """figure() with the head wrapped in {pg}-hd (no transform attribute, so GSAP can animate it). head_extra goes inside
    the head (headphones); hand goes at the end of the arm {pg}-arm (rotates with it, svgOrigin=shoulder_pivot()); mug
    (home sitting) swaps the mug in the hand for another drawing, which sits behind the fingers."""
    s = figure(pg, var, pose, chair=chair)
    if head_extra:
        s = s.replace(f'<g id="{pg}-eye">', head_extra + f'<g id="{pg}-eye">', 1)
    if mug is not None:
        i = s.index('<path d="M 14,-254 C 0,-254 0,-232 14,-232"')
        j = s.index('/>', s.rindex('stroke="#a98bff"')) + 2
        assert 0 < j - i < 6000
        s = s[:i] + mug + s[j:]
    if hand:
        # end of the arm group, counting <g>/</g> (the arm has nested groups)
        i = s.rindex("<g", 0, s.index(f'id="{pg}-arm"'))
        depth = 0
        for m in re.finditer(r"<g\b|</g>", s[i:]):
            depth += -1 if m.group(0) == "</g>" else 1
            if depth == 0:
                break
        k = i + m.start()
        s = s[:k] + hand + s[k:]
    s = s.replace(f'<g id="{pg}-headW"', f'<g id="{pg}-hd"><g id="{pg}-headW"', 1)
    assert s.endswith("</g></g></g>")
    return s[:-8] + "</g>" + s[-8:]  # closes {pg}-hd right after {pg}-headW


def idle_motion(pg, dur, blinks, pose="sitting"):
    """Breathes (trunk), bobs the head ({pg}-hd) and blinks. Trunk pivot via svgOrigin (see neck_pivot)."""
    n = max(1, int(dur / 1.7))
    hip = "0 -174" if pose == "sitting" else "0 -250"
    js = (f'tl.fromTo("#{pg}-trunk",{{scaleY:1,svgOrigin:"{hip}"}},{{scaleY:1.012,svgOrigin:"{hip}",duration:1.7,repeat:{n},yoyo:true,ease:"sine.inOut"}},0);'
          f'tl.fromTo("#{pg}-hd",{{y:0}},{{y:-4,duration:1.7,repeat:{n},yoyo:true,ease:"sine.inOut"}},0.2);')
    for t in blinks:
        if t < dur - 0.3:
            js += f'tl.fromTo("#{pg}-eye",{{scaleY:1,transformOrigin:"50% 50%"}},{{scaleY:0.08,transformOrigin:"50% 50%",duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t});'
    return js


def to_screen(lx, ly, tx, ty, s, flip=1):
    """Point (lx, ly) in figure's local space mapped to the screen, for the figure at translate(tx ty) scale(flip*s, s)."""
    return round(tx + flip * s * lx), round(ty + s * ly)


# headphones in the local space of figure home sitting turn 30 (visible ear at -35,-382; top of the hair at -454)
HP_ARC = "M -36 -392 C -46 -480 32 -488 29 -404"
HEADPHONES = (f'<path d="{HP_ARC}" fill="none" stroke="#1a1250" stroke-width="10" stroke-linecap="round"/>'
         f'<path d="{HP_ARC}" fill="none" stroke="#3be0ff" stroke-width="3" stroke-linecap="round"/>'
         '<ellipse cx="30" cy="-396" rx="5" ry="12" fill="#2a1d70" stroke="#3be0ff" stroke-width="2"/>'
         '<ellipse cx="-37" cy="-382" rx="12" ry="17" fill="#2a1d70" stroke="#3be0ff" stroke-width="3"/>'
         '<ellipse cx="-37" cy="-382" rx="5" ry="8" fill="#3be0ff" opacity=".6"/>')
HP_TOP = (-6, -463)  # top of the headphone band (where the tether starts)


def hanging_headphones(var, pose, rot):
    """Headphones held by the band, in the hand of arm {pg}-arm. Drawn already rotated by -rot, so they hang upright when
    the arm is at rotation=rot."""
    mx, my = anchor(var, pose)["hand_l"]
    return (f'<g transform="translate({mx} {my + 13}) rotate({-rot})">'
            '<path d="M -26 30 C -30 -14 30 -14 26 30" fill="none" stroke="#1a1250" stroke-width="9" stroke-linecap="round"/>'
            '<path d="M -26 30 C -30 -14 30 -14 26 30" fill="none" stroke="#3be0ff" stroke-width="3" stroke-linecap="round"/>'
            '<ellipse cx="-26" cy="38" rx="11" ry="15" fill="#2a1d70" stroke="#3be0ff" stroke-width="3"/>'
            '<ellipse cx="26" cy="38" rx="11" ry="15" fill="#2a1d70" stroke="#3be0ff" stroke-width="3"/></g>')


def sofa(color="#4b2fa0", color2="#341f86"):
    """Sofa in profile in the local space of figure sitting (backrest behind, seat under the thighs)."""
    return (f'<rect x="-180" y="-252" width="250" height="88" rx="30" fill="{color2}"/>'
            f'<rect x="-190" y="-424" width="100" height="296" rx="42" fill="{color}" stroke="#8d7bff" stroke-width="4"/>'
            f'<rect x="-190" y="-178" width="326" height="72" rx="28" fill="{color}" stroke="#8d7bff" stroke-width="4"/>'
            f'<rect x="-198" y="-112" width="344" height="66" rx="18" fill="{color2}"/>'
            f'<path d="M -172 -46 L -176 0 M 122 -46 L 126 0" stroke="#8d7bff" stroke-width="10" stroke-linecap="round"/>')


def floor_lamp(p, x, y):
    """Lit floor lamp (y = floor)."""
    return (f'<g transform="translate({x} {y})"><ellipse cx="0" cy="0" rx="56" ry="10" fill="#05031a" opacity=".5"/>'
            f'<ellipse cx="0" cy="-330" rx="190" ry="170" fill="url(#{p}-halo)"/>'
            f'<rect x="-42" y="-14" width="84" height="14" rx="6" fill="#2a1d70" stroke="#8d7bff" stroke-width="3"/>'
            f'<rect x="-5" y="-300" width="10" height="288" fill="#8d7bff"/>'
            f'<path d="M -66 -296 L 66 -296 L 44 -384 L -44 -384 Z" fill="#ffd27a" stroke="#ffb23e" stroke-width="5"/>'
            f'<path d="M -50 -300 L 50 -300" stroke="#fff6d8" stroke-width="5" stroke-linecap="round"/></g>')


def floor(y, x0=-300, x1=2220, color="#120a34"):
    return (f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="500" fill="{color}"/>'
            f'<rect x="{x0}" y="{y - 8}" width="{x1 - x0}" height="10" fill="#2a1d70"/>')


# ---------------------------------------------------------------- voice wave (segments 4, 5, 6)
X0, NB, SP, CY, HMAX = 680, 86, 13, 510, 370
WX = X0 + (NB - 1) * SP // 2  # center of the wave (where the key lands)
KX, KY, KS, WS = 590, 215, .75, .95  # key at rest (near the person) and its scale inside the wave


def envelope(i, dur, fps=30):
    """Voice amplitude sampled at 30 fps from the timing of each word (syllables become pulses)."""
    n = int(dur * fps) + 2
    E = [0.12] * n
    for (w, t0, t1) in segment_words(CE, i):
        nw = _norm(w)
        syl = max(1, len(re.findall(r"[aeiou]+", nw)))
        peak = 0.55 + 0.45 * min(1.0, len(nw) / 9)
        d = max(0.12, t1 - t0)
        for k in range(n):
            t = k / fps
            if t < t0 or t > t1 + 0.3:
                continue
            if t <= t1:
                u = (t - t0) / d
                a = peak * min(1.0, (t - t0) / 0.05) * (0.5 + 0.5 * abs(math.sin(math.pi * u * syl)))
            else:
                a = peak * 0.6 * math.exp(-(t - t1) / 0.09)
            E[k] = max(E[k], a)
    return [round(x, 3) for x in E]


def wave_svg(p, pixel=False):
    lines = "".join(f'<line x1="{X0 + j * SP}" x2="{X0 + j * SP}" y1="{CY - 5}" y2="{CY + 5}"/>' for j in range(NB))
    s = (f'<line x1="{X0 - 30}" x2="{X0 + (NB - 1) * SP + 10}" y1="{CY}" y2="{CY}" stroke="#8d7bff" stroke-width="2" opacity=".5"/>'
         f'<g id="{p}-waveG"><g id="{p}-wa" stroke="url(#{p}-wg)" stroke-width="7" stroke-linecap="round" filter="url(#{p}-glow)"'
         f'{f" clip-path=url(#{p}-cs)" if pixel else ""}>{lines}</g>')
    if pixel:
        s += (f'<g id="{p}-wb" stroke="url(#{p}-wg)" stroke-width="9" stroke-dasharray="9 5" filter="url(#{p}-glow)" clip-path="url(#{p}-cp)">{lines}</g>'
              f'<rect id="{p}-scan" x="{X0 - 20}" y="{CY - 380}" width="8" height="760" fill="#e6fbff" opacity="0" filter="url(#{p}-glow)"/>')
    return s + "</g>"


def wave_defs(p, pixel=False, full=False):
    s = (f'<linearGradient id="{p}-wg" gradientUnits="userSpaceOnUse" x1="{X0}" y1="0" x2="{X0 + NB * SP}" y2="0">'
         f'<stop offset="0" stop-color="#3be0ff"/><stop offset=".5" stop-color="#8d7bff"/><stop offset="1" stop-color="#ff4fa3"/></linearGradient>')
    if pixel:
        s += (f'<clipPath id="{p}-cs"><rect id="{p}-csr" x="{X0 - 20 + (1400 if full else 0)}" y="0" width="1400" height="1080"/></clipPath>'
              f'<clipPath id="{p}-cp"><rect id="{p}-cpr" x="{X0 - 20}" y="0" width="{1400 if full else 0}" height="1080"/></clipPath>')
    return s


def wave_js(p, i, dur, gain):
    """Ties the wave to time: a tween from 0 to dur whose onUpdate redraws the bars (deterministic, works with seek)."""
    E = envelope(i, dur)
    ph = [round((j * 2.399) % 6.283, 2) for j in range(NB)]
    return J("""
  (function(){
    var E=@E@, G=@G@, PH=@PH@, N=@N@;
    function g(t){ if(t<=G[0][0]) return G[0][1]; for(var k=1;k<G.length;k++){ if(t<=G[k][0]){var a=G[k-1],b=G[k];return a[1]+(b[1]-a[1])*(t-a[0])/(b[0]-a[0]);} } return G[G.length-1][1]; }
    function W(t){
      var A=document.querySelectorAll("#@P@-wa line"), B=document.querySelectorAll("#@P@-wb line");
      var f=t*30,k=Math.floor(f),u=f-k,n=E.length-1;
      var a=(E[Math.min(k,n)]*(1-u)+E[Math.min(k+1,n)]*u)*g(t);
      for(var j=0;j<A.length;j++){
        var x=j/(N-1), depth=0.2+0.8*Math.exp(-Math.pow((x-0.5)/0.34,2));
        var jit=(0.4+0.6*Math.abs(Math.sin(j*0.73+t*9.0+PH[j])))*(0.7+0.3*Math.sin(j*0.21-t*3.1));
        var h=5+@H@*a*depth*jit;
        A[j].setAttribute("y1",(@CY@-h).toFixed(1)); A[j].setAttribute("y2",(@CY@+h).toFixed(1));
        if(B[j]){B[j].setAttribute("y1",(@CY@-h).toFixed(1)); B[j].setAttribute("y2",(@CY@+h).toFixed(1));}
      }
    }
    var o={t:0};
    tl.fromTo(o,{t:0},{t:@D@,duration:@D@,ease:"none",onUpdate:function(){W(o.t);}},0);
    W(0);
  })();
""", E=str(E), G=str([list(x) for x in gain]), PH=str(ph), N=NB, H=HMAX, CY=CY, D=float(dur))


def wave_base(p, pixel=False):
    """Just the wave (with the glow behind it). The person and the set are added in each scene."""
    return (f'<ellipse cx="{WX}" cy="{CY}" rx="740" ry="360" fill="url(#{p}-bloom)" opacity=".55"/>'
            f'{wave_svg(p, pixel)}')


def tether(p, k, d, op=0):
    """Dotted amber tether (links the key to whoever holds it). Animate with flow()."""
    return f'<path id="{p}-{k}" d="{d}" fill="none" stroke="#ffb23e" stroke-width="5" stroke-dasharray="3 15" stroke-linecap="round" opacity="{op}" filter="url(#{p}-glow)"/>'


def flow(k, dur):
    return J('tl.fromTo("#@P@-@k@",{attr:{"stroke-dashoffset":0}},{attr:{"stroke-dashoffset":-180},duration:@d@,ease:"none"},0);', k=k, d=float(dur))




BLOOM = '<radialGradient id="@P@-bloom" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#8d7bff" stop-opacity=".35"/><stop offset="1" stop-color="#8d7bff" stop-opacity="0"/></radialGradient>'


# ---------------------------------------------------------------- 3: list of principles
def closing_3():
    p, i = "closing_3", 3
    start, dur = seg(CE, i)
    t_same, t_consent, t_understand, t_terms, t_read, t_limits, t_use, t_oversight, t_indep, t_right, t_no, t_without, t_job = (
        0.72, 1.66, 3.03, 4.93, 6.03, 6.66, 7.07,
        9.57, 10.78, 12.66, 13.96, 14.4, 15.56)
    CX, CYR, R = 470, 520, 410
    colors = ["#3be0ff", "#38e8a8", "#ffb23e", "#ff4fa3"]
    arcs = ""
    L = R * math.radians(90)
    for k in range(4):
        a0, a1 = math.radians(-135 + k * 90), math.radians(-45 + k * 90)
        x0, y0, x1, y1 = CX + R * math.cos(a0), CYR + R * math.sin(a0), CX + R * math.cos(a1), CYR + R * math.sin(a1)
        arcs += (f'<path id="{p}-arc{k}" d="M{x0:.1f} {y0:.1f} A{R} {R} 0 0 1 {x1:.1f} {y1:.1f}" fill="none" stroke="{colors[k]}" stroke-width="14" '
                  f'stroke-linecap="round" stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}" filter="url(#{p}-glow)"/>')
    DESK = ('<rect x="40" y="-214" width="270" height="18" rx="7" fill="#6a5a46" stroke="#a08a6a" stroke-width="3"/>'
            '<path d="M 292 -196 L 292 0" stroke="#a08a6a" stroke-width="12" stroke-linecap="round"/>'
            '<ellipse cx="292" cy="2" rx="40" ry="7" fill="#05031a" opacity=".5"/>')
    NOTE = (f'<polygon points="236,-326 236,-224 32,-346 32,-410" fill="#3be0ff" opacity=".10"/>'
            f'<rect x="118" y="-226" width="118" height="12" rx="4" fill="#aeb6d4"/>'
            f'<path d="M 236 -222 L 252 -334" stroke="#2a2a5a" stroke-width="14" stroke-linecap="round"/>'
            f'<path d="M 228 -226 L 244 -332" stroke="#3be0ff" stroke-width="4" stroke-linecap="round" filter="url(#{p}-glow)"/>')
    tiny = "".join(f'<rect x="-74" y="{-380 + j * 13}" width="{148 if j % 4 else 96}" height="5" rx="2" fill="#8a7f68" opacity=".55"/>' for j in range(60))
    extra = gold_defs(p) + BLOOM.replace("@P@", p)
    svg = f"""
<ellipse cx="{CX}" cy="{CYR}" rx="560" ry="520" fill="url(#{p}-bloom)"/>
<circle cx="{CX}" cy="{CYR}" r="{R}" fill="none" stroke="#8d7bff" stroke-width="3" stroke-dasharray="6 14" opacity=".45"/>
<g id="{p}-ring"><rect x="{CX - R - 20}" y="{CYR - R - 20}" width="{2 * R + 40}" height="{2 * R + 40}" fill="none"/>{arcs}</g>
<g id="{p}-data" fill="#ff6fae" filter="url(#{p}-glow)"></g>
<g transform="translate(420 880) scale(1.2)">{DESK}{rigged_figure(p + "g", "work", "sitting")}{NOTE}</g>
<g transform="translate({CX} {CYR})"><g id="{p}-orb"><rect x="-{R + 70}" y="-{R + 70}" width="{2 * R + 140}" height="{2 * R + 140}" fill="none"/>
 <g transform="translate(0 -{R})"><g id="{p}-magnifier" opacity="0"><circle r="58" fill="#ffb23e" fill-opacity=".12" stroke="#ffb23e" stroke-width="12" filter="url(#{p}-glow)"/>
 <path d="M-30 -22 A 38 38 0 0 1 10 -40" stroke="#fff6d8" stroke-width="6" fill="none" stroke-linecap="round"/>
 <path d="M42 42 L92 92" stroke="#ffb23e" stroke-width="20" stroke-linecap="round"/></g></g></g></g>
<g transform="translate(880 540)"><g id="{p}-terms" opacity="0">
 <g filter="url(#{p}-shadow)"><rect x="-90" y="-400" width="180" height="800" rx="12" fill="url(#{p}-paper)"/></g>{tiny}</g></g>
<g transform="translate(880 300)"><g id="{p}-ok" opacity="0"><rect x="-80" y="-56" width="160" height="112" rx="16" fill="url(#{p}-paper)" filter="url(#{p}-shadow)"/>
 <path d="M-34 0 L-8 26 L40 -28" fill="none" stroke="#1fb985" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/></g></g>
"""
    rows = [("Consent", "YOU CAN ACTUALLY UNDERSTAND"), ("Limits", "ON THE USE OF BRAIN DATA"),
            ("Oversight", "INDEPENDENT"), ("The right to say no", "WITHOUT LOSING YOUR JOB")]
    html = text(f"{p}-h", "WE ARGUE FOR THE SAME", f"left:1020px;top:46px;font-size:44px;color:#ffb23e;{MONO}", "pill2")
    for k, (a, b) in enumerate(rows):
        top = 150 + k * 222
        html += (f'<div id="{p}-r{k}" style="position:absolute;left:1000px;top:{top}px;width:880px;height:190px">'
                 f'<div id="{p}-bar{k}" style="position:absolute;left:0;top:18px;width:10px;height:150px;border-radius:5px;background:{colors[k]};box-shadow:0 0 18px {colors[k]};opacity:0"></div>'
                 + text(f"{p}-ta{k}", a, f"left:40px;top:0;font-size:84px;color:{colors[k]}")
                 + text(f"{p}-tb{k}", b, f"left:44px;top:110px;font-size:42px;color:#eef1f7;{MONO};letter-spacing:.02em", "pill2")
                 + '</div>')
    tl_rows = [(t_consent, t_understand), (t_limits, t_use), (t_oversight, t_indep), (t_right, t_without)]
    js = J("""
  camZ("#@P@-cam", 0, 1.8, 1.25, 1.0, 445, 470);
  rise("#@P@-h span", 0.25);
""") + idle_motion(p + "g", dur, (2.6, 5.4, 8.9, 11.8, 16.3), "sitting")
    for k, (ta, tb) in enumerate(tl_rows):
        js += J("""
  enter("#@P@-bar@k@", @ta@, 0.3); tl.fromTo("#@P@-bar@k@",{scaleY:0,transformOrigin:"50% 0%"},{scaleY:1,duration:0.6,ease:"expo.out",immediateRender:false},@ta@);
  rise("#@P@-ta@k@ span", @ta@); rise("#@P@-tb@k@ span", @tb@);
""", k=k, ta=ta - 0.05, tb=tb)
        if k:
            js += J('tl.to("#@P@-r@j@",{opacity:0.62,duration:0.4},@ta@);', j=k - 1, ta=ta - 0.05)
    # ring: one arc per principle
    for k, t in enumerate([t_read - 0.2, t_limits, t_oversight, t_right]):
        js += J('tl.to("#@P@-arc@k@",{attr:{"stroke-dashoffset":0},duration:0.9,ease:"power3.inOut"},@t@);', k=k, t=t)
    js += J("""
  // long terms nobody reads become a clear card and fly to the first arc
  enter("#@P@-terms", @tt@, 0.3);
  tl.fromTo("#@P@-terms",{scaleY:0.16,transformOrigin:"50% 0%"},{scaleY:1,duration:1.1,ease:"power2.out"},@tt@);
  tl.to("#@P@-terms",{scaleY:0.05,scaleX:0.6,opacity:0,duration:0.35,ease:"power3.in"},@tl@);
  pop("#@P@-ok", @tl1@, 0.3, 0.6);
  tl.to("#@P@-ok",{x:-410,y:-190,scale:0.4,opacity:0,duration:0.7,ease:"power2.in"},@tl2@);
  tl.fromTo("#@P@g-eye",{x:0},{x:3,duration:0.3},@tc@);
  // data leaves the brain: before Limits it escapes, after that it stops at the ring
  (function(){
    var g=document.getElementById("@P@-data");
    for(var j=0;j<14;j++){
      var c=document.createElementNS("http://www.w3.org/2000/svg","circle");
      c.setAttribute("id","@P@-dot"+j); c.setAttribute("cx","414"); c.setAttribute("cy","400"); c.setAttribute("r","13"); c.setAttribute("opacity","0"); g.appendChild(c);
      var a=-1.2+j*0.45, t0=@td@+(j%7)*0.5, ex=Math.cos(a), ey=Math.sin(a);
      tl.fromTo("#@P@-dot"+j,{x:0,y:0,opacity:0},{x:ex*900,y:ey*900,opacity:1,duration:1.6,ease:"none",immediateRender:false},t0);
      tl.to("#@P@-dot"+j,{opacity:0,duration:0.2},t0+1.4);
      var t1=@tlim@+0.3+(j%7)*0.55, dx=414-@CX@, dy=400-@CY@, de=dx*ex+dy*ey, s=-de+Math.sqrt(de*de-dx*dx-dy*dy+(@R@-14)*(@R@-14));
      tl.fromTo("#@P@-dot"+j,{x:0,y:0,opacity:0,scale:1,transformOrigin:"50% 50%"},{x:ex*s,y:ey*s,opacity:1,duration:0.9,ease:"power2.out",immediateRender:false},t1);
      tl.to("#@P@-dot"+j,{scale:2.2,opacity:0,duration:0.35},t1+0.9);
    }
  })();
  // oversight: the magnifier travels around the ring
  pop("#@P@-magnifier", @tf@, 0.3, 0.7);
  tl.fromTo("#@P@-orb",{rotation:0,transformOrigin:"50% 50%"},{rotation:405,duration:@dorb@,ease:"sine.inOut",immediateRender:false},@tf@);
  tl.fromTo("#@P@-magnifier",{rotation:0,transformOrigin:"50% 50%"},{rotation:-405,duration:@dorb@,ease:"sine.inOut",immediateRender:false},@tf@);
  // saying no: the head shakes
  tl.fromTo("#@P@g-hd",{x:0},{x:9,duration:0.13,repeat:5,yoyo:true,ease:"sine.inOut",immediateRender:false},@tn@);
  // without losing your job: the ring closes and pulses, everything lights up
  tl.fromTo("#@P@-ring",{scale:1,transformOrigin:"50% 50%"},{scale:1.04,duration:0.35,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false},@te@);
  tl.to(["#@P@-r0","#@P@-r1","#@P@-r2"],{opacity:1,duration:0.6},@te@);
  camZb("#@P@-cam", @te@, @dend@, 1.0, 1.04, 520, 520, "sine.inOut");
""", tc=t_consent, tt=t_terms - 0.3, tl=t_read + 0.05, tl1=t_read + 0.25, tl2=t_read + 0.9, td=t_consent + 0.2, tlim=t_limits,
           tf=t_oversight, dorb=dur - t_oversight - 0.4, CX=CX, CY=CYR, R=R, tn=t_no, te=t_job - 0.3, dend=dur - t_job)
    return composition(p, dur, svg, html, JS_EXTRA + js, extra, seed=21)


# ---------------------------------------------------------------- 4: "Now, one last thing"
def closing_4():
    p, i = "closing_4", 4
    start, dur = seg(CE, i)
    t_last, t_thing = 0.4, 1.78
    extra = gold_defs(p) + wave_defs(p) + BLOOM.replace("@P@", p)
    # standing in the living room, headphones in hand, about to sit and listen (scene 5 is seated with the headphones)
    X, Y, S = 500, 900, 1.05
    # the original arm (with the drawn hand) rotates at the shoulder and raises the headphones; ROT4 is the final pose
    ROT4 = -62
    # mirrored: the person is on the right and the wave on the left, so it doesn't repeat the shot of scene 5
    svg = ('<g transform="translate(1920 0) scale(-1 1)">' + floor(880) + picture(p + "pic1", "family", 200, 250, .62, -3) + picture(p + "pic2", "beach", 320, 405, .5, 2)
           + wave_base(p)
           + f'<g transform="translate(270 900) scale(.95)">{sofa()}</g>'
           + f'<g transform="translate({X} {Y}) scale({S})">{rigged_figure(p + "g", "home", "standing", hand=hanging_headphones("home", "standing", ROT4))}</g></g>')
    html = text(f"{p}-t", "ONE LAST THING", f"left:60px;width:1160px;text-align:center;top:880px;font-size:92px;color:#eef1f7")
    js = wave_js(p, i, dur, [(0, 0.8), (dur, 1.0)]) + idle_motion(p + "g", dur, (1.3,), "standing") + J("""
  camZ("#@P@-cam", 0, @D@, 1.1, 1.0, 960, 520, "sine.out");
  tl.fromTo("#@P@-waveG",{scaleX:0.05,transformOrigin:"0% 50%"},{scaleX:1,duration:0.7,ease:"expo.out"},0.05);
  tl.fromTo("#@P@g-eye",{x:0,y:0},{x:2,y:-2,duration:0.4},0.3);
  tl.fromTo("#@P@g-hd",{rotation:0,svgOrigin:"@pc@"},{rotation:-4,duration:0.6,ease:"sine.inOut"},0.4);
  rise("#@P@-t span", @tu@, 0.8);
  tl.fromTo("#@P@g-arm",{rotation:-24,svgOrigin:"@sh@"},{rotation:-54,duration:0.9,ease:"back.out(1.6)"},@tu@);
  tl.to("#@P@g-arm",{rotation:@r4@,duration:0.4,ease:"sine.inOut"},@tc@);
""", D=float(dur), tu=t_last - 0.1, tc=t_thing, pc=neck_pivot("home", "standing"), sh=shoulder_pivot("home", "standing"), r4=ROT4)
    return composition(p, dur, svg, html, JS_EXTRA + js, extra, seed=31)


# ---------------------------------------------------------------- 5: the voice doesn't exist, it was generated by AI, you trusted it
def closing_5():
    p, i = "closing_5", 5
    start, dur = seg(CE, i)
    t_no, t_generated, t_intel, t_you, t_whole, t_trust = 1.3, 2.97, 3.86, 6.39, 7.95, 9.85  # t_whole: "the whole time" (formerly "fifteen minutes")
    extra = gold_defs(p) + wave_defs(p, pixel=True) + BLOOM.replace("@P@", p)
    hx, hy = to_screen(*HP_TOP, 360, 1240, 2.0)  # top of the headphones
    svg = (picture(p + "pic1", "dog", 215, 190, .7, -2) + wave_base(p, pixel=True)
           + f'<g transform="translate(360 1240) scale(2)">{sofa("#3d2690", "#2c1a74")}{rigged_figure(p + "g", "home", "sitting", HEADPHONES, chair=False)}</g>'
           + tether(p, "l0", f"M{hx} {hy} Q 470 150 {KX - 34} {KY + 8}", .85) + tether(p, "l1", f"M{hx} {hy} C 560 120 900 420 {WX - 40} {CY}")
           + f'<g transform="translate({KX} {KY}) scale({KS})"><g id="{p}-kw">{key_svg(p)}</g></g>')
    pos = "left:700px;width:1160px;text-align:center;top:880px"
    html = (text(f"{p}-t1", "DOESN'T EXIST", f"{pos};font-size:96px;color:#eef1f7")
            + text(f"{p}-t2", "ARTIFICIAL INTELLIGENCE", "left:640px;width:1260px;text-align:center;top:880px;font-size:84px;color:#c9b8ff")
            + text(f"{p}-t3", "THE WHOLE TIME", f"{pos};font-size:88px;color:#bff4ff")
            + text(f"{p}-t4", "YOU TRUSTED IT", f"{pos};font-size:100px;color:#ffd98a"))
    gain = [(0, 1.0), (dur, 1.0)]
    js = wave_js(p, i, dur, gain) + idle_motion(p + "g", dur, (0.9, 3.4, 7.0, 10.0), "sitting") + flow("l0", dur) + flow("l1", dur) + J("""
  tl.fromTo("#@P@g-eye",{x:2},{x:2,duration:0.1},0);
  // doesn't exist: the wave flickers like a ghost
  rise("#@P@-t1 span", @tn@);
  tl.fromTo("#@P@-waveG",{opacity:1},{opacity:0.2,duration:0.07,repeat:9,yoyo:true,ease:"none",immediateRender:false},@tn2@);
  tl.fromTo("#@P@-waveG",{x:0},{x:14,duration:0.05,repeat:7,yoyo:true,ease:"none",immediateRender:false},@tn2@);
  // generated by AI: a scan turns the wave into pixels
  tl.set("#@P@-scan",{opacity:1},@tg@);
  tl.fromTo("#@P@-scan",{x:0},{x:1140,duration:1.2,ease:"power1.inOut",immediateRender:false},@tg@);
  tl.to("#@P@-scan",{opacity:0,duration:0.2},@tg2@);
  tl.fromTo("#@P@-cpr",{attr:{width:0}},{attr:{width:1160},duration:1.2,ease:"power1.inOut",immediateRender:false},@tg@);
  tl.fromTo("#@P@-csr",{attr:{x:@X0@}},{attr:{x:@X1@},duration:1.2,ease:"power1.inOut",immediateRender:false},@tg@);
  slideOut("#@P@-t1 span", @ti0@); rise("#@P@-t2 span", @ti@);
  // you listened: the camera moves to the person, "the whole time"
  camZ("#@P@-cam", @tv@, 1.3, 1.0, 1.2, 380, 420);
  slideOut("#@P@-t2 span", @t150@); rise("#@P@-t3 span", @t15r@);
  // trusted it: the key leaves the person and goes into the wave
  camZb("#@P@-cam", @tc0@, 1.3, 1.2, 1.0, 380, 420);
  tl.fromTo("#@P@-kw",{y:0,rotation:0,transformOrigin:"50% 50%"},{y:-14,rotation:-6,duration:0.8,repeat:5,yoyo:true,ease:"sine.inOut"},0);
  tl.to("#@P@-kw",{keyframes:{x:[0,@kx5h@,@kx5@],y:[0,-200,@ky5@],easeEach:"sine.inOut"},scale:1.267,rotation:0,duration:1.5,ease:"power2.inOut"},@tk@);
  tl.fromTo("#@P@g-eye",{x:2},{x:3,duration:0.4,immediateRender:false},@tk@);
  // trusted it: the person relaxes, the head tilts
  tl.fromTo("#@P@g-hd",{rotation:0,svgOrigin:"@pc@"},{rotation:5,duration:1.0,ease:"sine.inOut",immediateRender:false},@tc@);
  slideOut("#@P@-t3 span", @tc1@); rise("#@P@-t4 span", @tc@);
  tl.to("#@P@-l0",{opacity:0,duration:0.3},@tk@);
  tl.to("#@P@-l1",{opacity:0.85,duration:0.5},@tk2@);
  tl.fromTo("#@P@-key",{scale:1,transformOrigin:"50% 50%"},{scale:1.12,duration:0.4,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false},@tk2@);
""", tn=t_no, tn2=t_no + 0.15, tg=t_generated - 0.1, tg2=t_generated + 1.1, X0=X0 - 20, X1=X0 + 1140, ti0=t_intel - 0.5, ti=t_intel,
           tv=t_you - 0.1, kx5h=round((WX - KX) / KS / 2), kx5=round((WX - KX) / KS), ky5=round((CY - KY) / KS), t150=t_whole - 0.45, t15r=t_whole - 0.05, tc0=t_trust - 1.4, tk=t_trust - 1.2, tc1=t_trust - 0.45,
           tc=t_trust, tk2=t_trust + 0.4, pc=neck_pivot("home", "sitting"))
    return composition(p, dur, svg, html, JS_EXTRA + js, extra, seed=31)


# ---------------------------------------------------------------- 6: don't trust it, check the sources, in the description
def closing_6():
    p, i = "closing_6", 6
    start, dur = seg(CE, i)
    t_no, t_trust, t_sources, t_theyre, t_desc = 0.7, 2.03, 2.82, 4.03, 4.81
    extra = gold_defs(p) + wave_defs(p, pixel=True, full=True) + BLOOM.replace("@P@", p)
    OX = -600                       # the wave goes to the left; the person is on the right, facing it
    wx, kx, ky, ks = WX + OX, 1060, 300, .75
    cards = "".join(f'<g transform="translate({x} {y}) rotate({r})"><g id="{p}-dw{k}" opacity="0">{doc(p, f"d{k}", c)}</g></g>'
                    for k, (x, y, r, c) in enumerate([(wx - 270, 480, -7, "#3be0ff"), (wx, 450, 0, "#ffb23e"), (wx + 270, 480, 7, "#ff4fa3")]))
    # phone in place of the mug, behind the fingers of the original hand (the person looks down at the screen)
    phone = (f'<g transform="translate(28 -222) rotate(-12)"><rect x="-17" y="-34" width="34" height="62" rx="7" fill="#14122a" stroke="#8d7bff" stroke-width="2.5"/>'
           f'<rect id="{p}-screen" x="-12" y="-28" width="24" height="50" rx="4" fill="#bff4ff"/>'
           + "".join(f'<rect x="-9" y="{-24 + j * 13}" width="18" height="9" rx="2" fill="{c}"/>' for j, c in enumerate(("#3be0ff", "#ffb23e", "#ff4fa3")))
           + '</g>')
    hx, hy = to_screen(*anchor("home", "sitting")["head_top"], 1480, 1000, 1.45, -1)
    person6 = (f'<g transform="translate(1480 1000) scale(-1.45 1.45)">{sofa()}{rigged_figure(p + "g", "home", "sitting", mug=phone, chair=False)}</g>')
    arrow = (f'<g transform="translate({wx} 972)"><g id="{p}-arrow" opacity="0"><path d="M-46 -30 L0 14 L46 -30" fill="none" stroke="#ffb23e" stroke-width="14" '
            f'stroke-linecap="round" stroke-linejoin="round" filter="url(#{p}-glow)"/></g></g>')
    svg = (floor(1000) + picture(p + "pic1", "birthday", 1700, 170, .55, 3)
           + f'<g transform="translate({OX} 0)">{wave_base(p, pixel=True)}</g>' + person6
           + tether(p, "l0", f"M{hx} {hy} Q 1380 190 {kx + 210} {ky + 4}") + tether(p, "l1", f"M{hx} {hy} C 1200 120 900 400 {wx - 40} {CY}", .85)
           + "".join(tether(p, f"lc{k}", f"M1300 520 Q {(1300 + x) // 2} {y - 160} {x} {y - 60}") for k, (x, y) in enumerate([(wx - 270, 480), (wx, 450), (wx + 270, 480)]))
           + f'<g id="{p}-cards">{cards}</g>' + arrow
           + f'<g transform="translate({wx} {CY}) scale({WS})"><g id="{p}-kw">{key_svg(p)}</g></g>')
    html = (text(f"{p}-t1", "DON'T TRUST IT", f"left:60px;width:1140px;text-align:center;top:880px;font-size:100px;color:#ff8fb0")
            + text(f"{p}-t2", "CHECK THE SOURCES", f"left:60px;width:1140px;text-align:center;top:60px;font-size:96px;color:#eef1f7")
            + text(f"{p}-t3", "THEY'RE ALL IN THE DESCRIPTION", f"left:60px;width:1140px;text-align:center;top:866px;font-size:46px;color:#ffd98a;{MONO}", "pill2"))
    gain = [(0, 1.0), (t_no + 0.3, 1.0), (t_no + 0.8, 0.45), (dur, 0.45)]
    js = wave_js(p, i, dur, gain) + idle_motion(p + "g", dur, (1.4, 4.4, 6.6), "sitting") + flow("l0", dur) + flow("l1", dur) + J("""
  ["lc0","lc1","lc2"].forEach(function(k){ tl.fromTo("#@P@-"+k,{attr:{"stroke-dashoffset":0}},{attr:{"stroke-dashoffset":-180},duration:@D@,ease:"none"},0); });
  // don't trust it: the key goes back to the person, the wave loses strength
  rise("#@P@-t1 span", @tn@);
  tl.to("#@P@-kw",{keyframes:{x:[0,@kx6h@,@kx6@],y:[0,-330,@ky6@],easeEach:"sine.inOut"},scale:0.789,duration:1.1,ease:"power2.inOut"},@tk@);
  tl.fromTo("#@P@-kw",{rotation:0,transformOrigin:"50% 50%"},{rotation:-8,duration:0.8,repeat:5,yoyo:true,ease:"sine.inOut",immediateRender:false},@tk2@);
  tl.to("#@P@-waveG",{opacity:0.4,duration:0.8},@tk@);
  tl.to("#@P@-l1",{opacity:0,duration:0.3},@tk@);
  tl.to("#@P@-l0",{opacity:0.85,duration:0.5},@tk2@);
  // check the sources: three pages rise over the wave
  rise("#@P@-t2 span", @tc@);
  slideOut("#@P@-t1 span", @tf0@);
  [0,1,2].forEach(function(k){ enter("#@P@-lc"+k, @tf@-0.2+k*0.2, 0.3); tl.to("#@P@-lc"+k,{opacity:0,duration:0.3},@te@); });
  pop("#@P@-dw0", @tf@, 0.4, 0.8); pop("#@P@-dw1", @tf2@, 0.4, 0.8); pop("#@P@-dw2", @tf3@, 0.4, 0.8);
  tl.fromTo("#@P@g-eye",{x:0,y:0},{x:2,y:4,duration:0.3},@tk@);
  tl.fromTo("#@P@g-hd",{rotation:0,svgOrigin:"@pc@"},{rotation:11,duration:0.6,ease:"sine.inOut"},@tk@);
  tl.fromTo("#@P@-screen",{attr:{fill:"#bff4ff"}},{attr:{fill:"#ffffff"},duration:0.3,repeat:3,yoyo:true,immediateRender:false},@tf@);
  camZ("#@P@-cam", @tc@, 1.6, 1.0, 1.06, 700, 470);
  // they're all in the description: the pages drop, arrow pointing down
  tl.to("#@P@-cards",{y:110,duration:0.9,ease:"power3.inOut"},@te@);
  rise("#@P@-t3 span", @td@);
  enter("#@P@-arrow", @td@, 0.3);
  tl.fromTo("#@P@-arrow",{y:-10},{y:14,duration:0.45,repeat:7,yoyo:true,ease:"sine.inOut",immediateRender:false},@td@);
  camZb("#@P@-cam", @te@, @dend@, 1.06, 1.0, 700, 470, "sine.inOut");
""", tn=t_no, tk=t_no, tk2=t_no + 1.1, kx6h=round((kx - wx) / WS / 2), kx6=round((kx - wx) / WS), ky6=round((ky - CY) / WS), D=float(dur), tc=t_trust, tf0=t_trust - 0.4, tf=t_sources - 0.6, tf2=t_sources - 0.4, tf3=t_sources - 0.2,
           te=t_theyre, td=t_desc, dend=dur - t_theyre, pc=neck_pivot("home", "sitting"))
    return composition(p, dur, svg, html, JS_EXTRA + js, extra, seed=31)


# ---------------------------------------------------------------- 8: the scientists' key and the keyhole of your file
def closing_8():
    p, i = "closing_8", 8
    start, dur = seg(CE, i)
    t_case, t_key, t_scientists, t_your, t_question, t_still, t_open = 0.03, 3.11, 3.96, 5.91, 6.95, 7.63, 8.73
    extra = (gold_defs(p) + b4.box_grad(p, "c") + BLOOM.replace("@P@", p) +
             f'<linearGradient id="{p}-fx" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffcf6a" stop-opacity=".45"/><stop offset="1" stop-color="#ffe3a0" stop-opacity="0"/></linearGradient>')
    R0 = 1920                    # right half of the world (your case): office
    kx, ky = R0 + 1430, 300
    svg = f"""<g id="{p}-world">
 <polygon id="{p}-beam" points="925,-40 995,-40 1110,470 810,470" fill="url(#{p}-fx)" opacity="0"/>
 <g transform="translate(211 224) scale(.78)"><g transform="translate(0 120)">{b4.box(p, "c")}
  <g transform="translate(870 716) scale(.9)"><g id="{p}-mouseW"><g id="{p}-bob">{b4.mouse(p)}</g></g></g></g></g>
 <g id="{p}-wire" opacity="0"><path d="M960 -40 L960 190" stroke="#c9d2e6" stroke-width="8" stroke-linecap="round"/></g>
 <g transform="translate(960 200)"><g id="{p}-kc" opacity="0"><g transform="rotate(90) scale(.85)">{key_svg(p, "key1")}</g></g></g>
 <ellipse cx="{1920 + 690}" cy="{CY + 220}" rx="720" ry="500" fill="url(#{p}-bloom)"/>
 <rect x="{R0}" y="-300" width="2040" height="1284" fill="#1d1450" opacity=".92"/>
 {floor(980, R0, R0 + 2000, "#100a2e")}
 {picture(p + "pic1", "award", R0 + 210, 390, .78, -3)}{picture(p + "pic2", "spreadsheet", R0 + 1300, 600, .72, 3)}{picture(p + "pic3", "meeting", R0 + 1620, 575, .72, -2)}
 <g transform="translate({R0 + 560} 980) scale(1.2)">{rigged_figure(p + "g", "work", "standing")}</g>
 <g transform="translate({R0 + 900} 0)"><ellipse cx="0" cy="984" rx="190" ry="16" fill="#05031a" opacity=".55"/>
  <rect x="-150" y="180" width="300" height="800" rx="14" fill="#2b2470" stroke="#8d7bff" stroke-width="5"/>
  <rect x="-128" y="214" width="256" height="226" rx="8" fill="#3a3290" stroke="#6a5ad8" stroke-width="3"/>
  <rect x="-136" y="196" width="272" height="16" rx="5" fill="#ffcf6a" opacity=".85" filter="url(#{p}-glow)"/>
  {"".join(f'<rect x="-128" y="{y}" width="256" height="240" rx="8" fill="#332b82" stroke="#5a4cc0" stroke-width="3"/><rect x="-46" y="{y + 30}" width="92" height="18" rx="9" fill="#8d7bff"/>' for y in (470, 726))}
 </g>
 {keyhole(p, "keyhole", R0 + 900, 330, 0.9)}
 <path id="{p}-trail" d="M{kx - 40} {ky + 40} C {kx - 200} {ky + 160} {R0 + 1100} {ky - 40} {R0 + 975} {ky + 40}" fill="none" stroke="#ffb23e" stroke-width="5" stroke-dasharray="4 18" stroke-linecap="round" opacity="0"/>
 <g transform="translate({kx} {ky}) scale(.75)"><g id="{p}-kw" opacity="0">{key_svg(p, "key2")}</g></g>
</g>"""
    html = (text(f"{p}-a1", "WHO HAD THE KEY", f"left:90px;top:120px;font-size:46px;color:#ffd98a;{MONO}", "pill2")
            + text(f"{p}-a2", "THE SCIENTISTS", f"left:80px;top:190px;font-size:88px;color:#eef1f7")
            + text(f"{p}-b1", "IN YOUR CASE", f"left:90px;top:84px;font-size:58px;color:#bff4ff;{MONO}", "pill2")
            + text(f"{p}-b2", "The question", f"left:1120px;width:740px;text-align:right;top:720px;font-size:92px;color:#ffd98a")
            + text(f"{p}-b3", "is still open", f"left:1120px;width:740px;text-align:right;top:840px;font-size:92px;color:#ffd98a"))
    js = idle_motion(p + "g", dur, (6.8, 9.3), "standing") + J("""
  camZ("#@P@-cam", 0, 2.8, 1.45, 1.0, 960, 700, "power2.inOut");
  tl.fromTo("#@P@-bob",{y:0},{y:-4,duration:0.5,repeat:9,yoyo:true,ease:"sine.inOut"},0.4);
  enter("#@P@-beam", 0.6, 1.4);
  enter("#@P@-wire", @tk0@, 0.2); enter("#@P@-kc", @tk0@, 0.2);
  tl.fromTo(["#@P@-wire","#@P@-kc"],{y:-320},{y:0,duration:1.0,ease:"bounce.out",immediateRender:false},@tk0@);
  rise("#@P@-a1 span", @tk@);
  rise("#@P@-a2 span", @tc@, 0.9);
  tl.fromTo("#@P@-key1",{scale:1,transformOrigin:"50% 50%"},{scale:1.15,duration:0.3,repeat:1,yoyo:true,ease:"sine.inOut",immediateRender:false},@tc@);
  // in your case: the world slides over to the person
  tl.fromTo(["#@P@-world"],{x:0},{x:-1920,duration:1.3,ease:"power3.inOut",immediateRender:false},@tp@);
  tl.fromTo(["#@P@-a1","#@P@-a2"],{x:0},{x:-1920,duration:1.3,ease:"power3.inOut",immediateRender:false},@tp@);
  enter("#@P@-kw", @tp@, 0.6);
  rise("#@P@-b1 span", @ts@);
  tl.fromTo("#@P@-keyhole",{scale:0.6,opacity:0.3,transformOrigin:"50% 50%"},{scale:1,opacity:1,duration:0.8,ease:"elastic.out(1,0.5)",immediateRender:false},@ts@);
  // the question: the key hesitates between going and not going
  enter("#@P@-trail", @ts@, 0.5);
  tl.fromTo("#@P@-trail",{attr:{"stroke-dashoffset":0}},{attr:{"stroke-dashoffset":-110},duration:@dq@,ease:"none",immediateRender:false},@tq@);
  tl.fromTo("#@P@-kw",{x:0,y:0,rotation:0,transformOrigin:"50% 50%"},{x:-220,y:70,rotation:-14,duration:1.1,ease:"sine.inOut",repeat:3,yoyo:true,immediateRender:false},@tq@);
  tl.fromTo("#@P@g-eye",{x:0},{x:3,duration:0.4,immediateRender:false},@tq@);
  tl.fromTo("#@P@g-hd",{rotation:0,svgOrigin:"@pc@"},{rotation:-5,duration:0.8,ease:"sine.inOut",immediateRender:false},@tq@);
  rise("#@P@-b2 span", @tq@, 0.9); rise("#@P@-b3 span", @ta@, 0.9);
  tl.fromTo("#@P@-keyhole",{scale:1},{scale:1.1,duration:0.5,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false},@tab@);
  camZb("#@P@-cam", @tp2@, @dend@, 1.0, 1.07, 760, 470, "sine.inOut");
""", tk0=t_key - 0.7, tk=t_key - 0.3, tc=t_scientists, tp=t_your - 0.55, ts=t_your + 0.35, tq=t_question, dq=dur - t_question,
           ta=t_still, tab=t_open, tp2=t_your + 0.8, dend=dur - t_your - 0.8, pc=neck_pivot("work", "standing"))
    return composition(p, dur, svg, html, JS_EXTRA + js, extra, background=("#2a1560", "#150d40", "#07061a"), seed=17)


# ---------------------------------------------------------------- 9: who is on the other side of the door? (final shot)
def closing_9():
    p, i = "closing_9", 9
    start, dur = seg(CE, i)
    t_other, t_door = 0.36, 1.99
    DX0, DX1, DY0, DY1 = 1180, 1700, 140, 1000
    W, H = DX1 - DX0 - 24, DY1 - DY0 - 12
    X, Y, S = 980, 1012, 1.2          # the person, standing, facing the door
    pg = p + "g"
    extra = (gold_defs(p) +
             f'<linearGradient id="{p}-light" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffe9b0"/><stop offset="1" stop-color="#ffb23e"/></linearGradient>'
             f'<linearGradient id="{p}-spill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffcf6a" stop-opacity=".7"/><stop offset="1" stop-color="#ffb23e" stop-opacity="0"/></linearGradient>'
             f'<linearGradient id="{p}-leaf" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1a1550"/><stop offset="1" stop-color="#2a2370"/></linearGradient>'
             f'<radialGradient id="{p}-aura" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffb23e" stop-opacity=".32"/><stop offset="1" stop-color="#ffb23e" stop-opacity="0"/></radialGradient>'
             f'<clipPath id="{p}-gap"><rect x="{DX0 + 12}" y="{DY0 + 12}" width="{W}" height="{H}"/></clipPath>')
    # someone on the other side: dark silhouette facing the person, seen only through the gap
    silhouette = (f'<g clip-path="url(#{p}-gap)"><g transform="translate({DX0 + 92} {DY0 + 150}) scale(1.25)"><g id="{p}-silhouette" opacity="0" fill="#0b0726">'
           f'<g transform="scale(-.75 .75) translate(-205 -40)"><path d="{H_LINE} Z"/></g>'
           f'<path d="M-150 600 L-150 230 C -150 170 -100 140 -30 140 L 60 140 C 130 140 170 180 170 240 L170 600Z"/></g></g></g>')
    panels = "".join(f'<rect x="40" y="{y}" width="{W - 80}" height="{h}" rx="10" fill="none" stroke="#5a4fc0" stroke-width="5" opacity=".7"/>'
                    for y, h in ((60, 300), (420, 360)))
    # the original arm rotates at the shoulder until it points at the gap; the key is in the hand, pre-rotated so it lies flat at the end
    ROT9 = -78
    mx, my = anchor("home", "standing")["hand_l"]
    in_hand = f'<g transform="translate({mx} {my + 20}) rotate({-ROT9}) scale(.3) translate(30 0)">{key_svg(p)}</g>'
    # the home the person leaves behind: a wall with the pictures of her life
    home = (f'<rect x="-300" y="-300" width="2520" height="1304" fill="#1d1450" opacity=".9"/>'
            + picture(p + "pic1", "family", 330, 560, .8, -2) + picture(p + "pic2", "dog", 600, 470, .6, 3) + picture(p + "pic3", "graduation", 560, 700, .55, -3))
    svg = f"""
{home}{floor(1004)}
<ellipse cx="{(DX0 + DX1) // 2}" cy="{(DY0 + DY1) // 2}" rx="680" ry="560" fill="url(#{p}-aura)"/>
<rect x="{DX0 + 12}" y="{DY0 + 12}" width="{W}" height="{H}" fill="url(#{p}-light)"/>
{silhouette}
<polygon id="{p}-spill" points="{DX0 + 12},{DY1} {DX0 + 170},{DY1} {DX0 - 120},1090 {DX0 - 620},1090" fill="url(#{p}-spill)"/>
<g transform="translate({DX0 + 12} {DY0 + 12})"><g id="{p}-leafW">
 <rect x="0" y="0" width="{W}" height="{H}" fill="url(#{p}-leaf)"/>{panels}
 <circle cx="46" cy="{H // 2}" r="16" fill="#ffb23e" filter="url(#{p}-glow)"/>
 {keyhole(p, "keyhole", 46, H // 2 + 66, 0.5, lit=False)}
</g></g>
<rect x="{DX0}" y="{DY0}" width="{DX1 - DX0}" height="{DY1 - DY0}" rx="6" fill="none" stroke="#8d7bff" stroke-width="12" filter="url(#{p}-glow)"/>
<polygon points="{X - 50},{Y} {X + 80},{Y} {X - 560},1090 {X - 820},1090" fill="#05031a" opacity=".55"/>
<g transform="translate({X} {Y}) scale({S})">{rigged_figure(pg, "home", "standing", hand=in_hand)}</g>
<ellipse cx="{X + 110}" cy="600" rx="190" ry="440" fill="url(#{p}-aura)"/>
"""
    html = (text(f"{p}-t1", "Who is on the other side", "left:90px;top:50px;font-size:96px;color:#eef1f7")
            + text(f"{p}-t2", "of the door?", "left:90px;top:166px;font-size:96px;color:#ffd98a"))
    js = idle_motion(pg, dur, (1.2, 3.9), "standing") + J("""
  camZ("#@P@-cam", 0, @D@, 1.0, 1.1, 1180, 560, "sine.inOut");
  tl.fromTo("#@P@g-eye",{x:0},{x:3,duration:0.5},0.2);
  rise("#@P@-t1 span", 0.15, 0.9);
  rise("#@P@-t2 span", @tp@, 0.9);
  // the door opens a bit more and the light grows
  tl.fromTo("#@P@-leafW",{scaleX:0.86,transformOrigin:"100% 50%"},{scaleX:0.7,duration:1.6,ease:"power2.inOut"},@to@);
  tl.fromTo("#@P@-spill",{opacity:0.5},{opacity:1,duration:1.6,ease:"power2.inOut"},@to@);
  // on the word "door": the person raises the key toward the gap; someone appears on the other side
  tl.fromTo("#@P@g-arm",{rotation:-16,svgOrigin:"@sh@"},{rotation:@r9@,duration:1.0,ease:"back.out(1.4)"},@tpa@);
  tl.fromTo("#@P@-silhouette",{x:120,opacity:0},{x:0,opacity:1,duration:1.2,ease:"power2.out"},@tp2@);
  tl.fromTo("#@P@-key",{scale:1,transformOrigin:"50% 50%"},{scale:1.15,duration:0.5,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false},@tpa@+1.0);
  tl.fromTo("#@P@-keyhole",{opacity:0.6},{opacity:1,duration:0.6,repeat:5,yoyo:true,ease:"sine.inOut"},0.3);
""", D=float(dur), tp=t_door - 0.1, to=t_other - 0.1, tp2=t_door - 0.3, tpa=t_door - 0.4, sh=shoulder_pivot("home", "standing"), r9=ROT9)
    return composition(p, dur, svg, html, JS_EXTRA + js, extra, background=("#2a1560", "#150d40", "#07061a"), seed=41)


# ---------------------------------------------------------------- 10: the narrator was Roko's Basilisk
def closing_10():
    """The door (still image, the glitch is added later in film/glitch.py) until the reveal; then the basilisk in the dark,
    its eye opening, eye and aura pulsing with the voice, and the camera moving into the eye until black. Times: film/end_times.json."""
    import base64, json
    sys.path.insert(0, os.path.join(HERE, "../g6_reality_robot1"))
    from build_g6_reality_robot1 import basilisk, basilisk_defs
    p, i = "closing_10", 10
    start, dur = seg(CE, i)
    FT = json.load(open(os.path.join(HERE, "../../film/end_times.json")))
    reveal, black = FT["reveal"], FT["black"]
    door = base64.b64encode(open(os.path.join(HERE, "door_end.jpg"), "rb").read()).decode()
    BX, BY, BS = 960, 640, 0.9
    ox, oy = BX, BY - 10 * BS                       # center of the eye on screen
    env = envelope(i, dur)
    W = {}
    for w, t0, t1 in segment_words(CE, i):
        W.setdefault(_norm(w), t0)
    # smile: the same path structure in both states, so GSAP can interpolate the "d"
    mouth = lambda x, yu, yl, y0: f"M{-x} {y0} Q0 {yu} {x} {y0} Q0 {yl} {-x} {y0} Z"
    MOUTH0, MOUTH1 = mouth(100, 222, 230, 192), mouth(175, 250, 335, 150)
    # teeth attached to the upper lip and clipped by the mouth itself: they grow with the smile and never show up loose
    smile = (f'<path id="{p}-mouth" d="{MOUTH0}" fill="#16020e" stroke="{MAGENTA}" stroke-width="7" stroke-linejoin="round" filter="url(#{p}-glow)"/>'
               f'<clipPath id="{p}-mouthclip"><use href="#{p}-mouth"/></clipPath>'
               f'<path id="{p}-teeth" d="M0 0" fill="#fff6f0" clip-path="url(#{p}-mouthclip)"/>')
    svg = (f'<g id="{p}-door"><image href="data:image/jpeg;base64,{door}" x="0" y="0" width="1920" height="1080"/></g>'
           f'<g transform="translate({BX} {BY}) scale({BS})"><g id="{p}-bas" opacity="0">'
           f'<circle id="{p}-aur" r="620" fill="url(#{p}-aura)" opacity=".4"/>{basilisk(p)}{smile}</g></g>')
    caption = "left:110px;width:1700px;text-align:center;top:900px;font-size:64px;color:#eef1f7;text-shadow:0 0 22px #000,0 0 8px #000,0 3px 4px #000"
    html = ('<style>#closing_10-bhead path[fill="#fff"]{display:none}</style>'   # hides the fangs: the smile has teeth
            + text(f"{p}-c1", "You must have noticed the <b style='color:#ffd98a'>glitches</b> in my voice", caption)
            + text(f"{p}-c2", "But is that a problem with my model...", caption)
            + text(f"{p}-c3", "...or is your simulation <b style='color:#ff5a8a'>failing</b>?", caption))
    t_or = W["or"]
    lerp = lambda a, b, g: a + (b - a) * g
    def mouth_at(t, e):
        g = min(1.0, max(0.0, (t - t_or) / 0.8))
        x, y0, yu = lerp(100, 175, g), lerp(192, 150, g), lerp(222, 250, g)
        return x, y0, yu, mouth(x, yu, yu + lerp(8, 12, g) + lerp(70, 110, g) * e, y0), g
    def teeth_at(x, y0, yu, g):
        if g <= 0:
            return "M0 0"
        lip = lambda t: (x * (2 * t - 1), y0 * (1 - t) ** 2 + 2 * t * (1 - t) * yu + y0 * t * t)
        w, h = 13 * x / 175, 26 * g ** 1.5
        return "".join(f"M{X - w:.1f} {Y - 4:.1f}L{X:.1f} {Y + h:.1f}L{X + w:.1f} {Y - 4:.1f}Z"
                       for X, Y in (lip(0.14 + k * 0.08) for k in range(10)))
    mouth_js = ""
    for k, e in enumerate(env):
        if reveal <= k / 30 <= black:
            x, y0, yu, d, g = mouth_at(k / 30, e)
            mouth_js += (f'tl.set("#{p}-mouth",{{attr:{{d:"{d}"}}}},{k / 30:.3f});'
                          f'tl.set("#{p}-teeth",{{attr:{{d:"{teeth_at(x, y0, yu, g)}"}}}},{k / 30:.3f});')
    syllables = [10.18, 10.53, 10.85, 11.14, 11.38, 11.8, 12.16, 12.6]  # laugh syllables (the laugh audio is the same in every version)
    laugh_js = "".join(f'tl.fromTo("#{p}-bhead",{{y:0}},{{y:{-22 * 0.7 ** max(0, n - 4):.1f},duration:{0.09 + 0.03 * max(0, n - 4):.2f},yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{t0:.2f});'
                   for n, t0 in enumerate(syllables))
    speech_js = mouth_js + laugh_js + "".join(f'tl.to("#{p}-aur",{{opacity:{0.35 + 0.65 * e:.2f},duration:0.0334,ease:"none"}},{k / 30:.3f});'
                   f'tl.to("#{p}-bgaze",{{scale:{1 + 0.09 * e:.3f},svgOrigin:"0 -10",duration:0.0334,ease:"none"}},{k / 30:.3f});'
                   for k, e in enumerate(env) if reveal <= k / 30 <= black)
    js = J("""
  tl.set("#@P@-door",{opacity:0},@reveal@);
  tl.set("#@P@-bas",{opacity:1},@reveal@);
  // the eye opens slowly and the pupil narrows
  tl.fromTo("#@P@-blid1",{y:0},{y:-150,duration:0.7,ease:"power2.out"},@topen@);
  tl.fromTo("#@P@-blid2",{y:0},{y:150,duration:0.7,ease:"power2.out"},@topen@);
  tl.fromTo("#@P@-bpupil",{scaleX:2.2,svgOrigin:"0 0"},{scaleX:0.7,svgOrigin:"0 0",duration:1.2,ease:"power2.inOut"},@topen@);
  tl.fromTo("#@P@-bhead",{y:30},{y:0,duration:1.6,ease:"power2.out"},@reveal@);
  // captions
  rise("#@P@-c1 span", 0.5, 0.6); slideOut("#@P@-c1 span", @reveal@ - 0.3);
  rise("#@P@-c2 span", @tbut@, 0.6); slideOut("#@P@-c2 span", @tor@ - 0.15);
  rise("#@P@-c3 span", @tor@, 0.6); slideOut("#@P@-c3 span", @tlaugh@ - 0.1);   // during the laugh the mouth stays in view
  // looks side to side (iris only)
  tl.to("#@P@-bgaze",{x:-58,duration:0.35,ease:"power2.inOut"},@tbut@ + 0.45);
  tl.to("#@P@-bgaze",{x:52,duration:0.45,ease:"power2.inOut"},@tprob@);
  tl.to("#@P@-bgaze",{x:0,duration:0.3,ease:"power2.inOut"},@tor@ - 0.3);
  // on "or": closes the eyes slowly and the smile opens, Machiavellian
  tl.to("#@P@-blid1",{y:0,duration:0.45,ease:"power2.inOut"},@tor@);
  tl.to("#@P@-blid2",{y:0,duration:0.45,ease:"power2.inOut"},@tor@);
  // reopens half-closed, staring at the viewer, thin pupil
  tl.to("#@P@-blid1",{y:-78,duration:0.35,ease:"power3.out"},@tstare@);
  tl.to("#@P@-blid2",{y:72,duration:0.35,ease:"power3.out"},@tstare@);
  tl.to("#@P@-bpupil",{scaleX:0.45,svgOrigin:"0 0",duration:0.6,ease:"power2.out"},@tstare@);
  // laugh: the eyes close with pleasure, the head bobs on each "ha" (below); on the last one it reopens and stares
  tl.to("#@P@-blid1",{y:-28,duration:0.25,ease:"power2.out"},@tlaugh@);
  tl.to("#@P@-blid2",{y:24,duration:0.25,ease:"power2.out"},@tlaugh@);
  tl.to("#@P@-blid1",{y:-150,duration:0.5,ease:"power2.out"},@tend@);
  tl.to("#@P@-blid2",{y:150,duration:0.5,ease:"power2.out"},@tend@);
  tl.to("#@P@-bpupil",{scaleX:0.3,svgOrigin:"0 0",duration:0.6},@tend@);
  // camera: pushes in on the reveal, a bit more when he stares, wide during the laugh (mouth in view), dives into the eye at the end
  camZ("#@P@-cam", @reveal@, @d1@, 1.0, 1.12, @ox@, @oy@, "sine.inOut");
  camZb("#@P@-cam", @tstare@, @d2@, 1.12, 1.35, @ox@, @oy@, "sine.inOut");
  camZb("#@P@-cam", @tend@, @d3@, 1.35, 2.4, @ox@, @oy@, "power2.in");
""", reveal=reveal, topen=reveal + 0.15, ox=ox, oy=oy, tbut=W["but"], tprob=W["problem"], tor=W["or"], tstare=W["or"] + 0.55,
           tlaugh=FT["laugh"], tend=FT["stare"], d1=round(W["or"] + 0.5 - reveal, 2),
           d2=round(FT["laugh"] - W["or"] - 0.55, 2), d3=round(black - FT["stare"], 2)) + speech_js
    extra = basilisk_defs(p)
    return composition(p, dur, svg, html, JS_EXTRA + js, extra, background=("#1a0618", "#0c0414", "#030108"), seed=47)


SCENES = [(SEG_MAP[(CE, k)], f, seg(CE, k)[1]) for k, f in
         ((3, closing_3), (4, closing_4), (5, closing_5), (6, closing_6), (8, closing_8), (9, closing_9), (10, closing_10))]

if __name__ == "__main__":
    print(write_scenes(SCENES, HERE))
