"""Scenes v5, group g1: end of the opening and the contract block (Severance).

  python3 build_g1_opening_contract.py     # writes compositions/, index.html and timing.json for this folder

Recurring motif: the amber key (M8) and the keyhole (the door at the end of corridor F).
"""
import math, os, random, re, sys
SCENE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCENE_DIR, ".."))
from engine import *  # noqa: F401,F403  (brings HERE from engine, which points to scenes)
HERE = SCENE_DIR
sys.path.insert(0, os.path.join(SCENE_DIR, "../../scenes-v4"))
import build4 as b4  # noqa: E402  (box, mouse, box_grad of the approved mouse)
from art2 import fly_rich, fly_defs  # noqa: E402
from figure import figure, picture, orb, ANCHORS  # noqa: E402


def figure_idle(p, dur, blinks=(2.0, 5.3, 8.8, 12.1, 16.4, 20.2)):
    """Like figure.figure_idle, without the breathing on {p}-trunk: the new trunk has 19998 px mask paths (M-9999...),
    so getBBox is huge and scaleY with a % transformOrigin shifts the trunk ~150 px up (head inside the shirt).
    Keeps the head bob (on {p}-head, y only) and the blinks."""
    n = max(1, int(dur / 1.7))
    js = f'tl.fromTo("#{p}-head",{{y:0}},{{y:-4,duration:1.7,repeat:{n},yoyo:true,ease:"sine.inOut"}},0.2);'
    for t in blinks:
        if t < dur - 0.3:
            js += f'tl.fromTo("#{p}-eye",{{scaleY:1,transformOrigin:"50% 50%"}},{{scaleY:0.08,transformOrigin:"50% 50%",duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t});'
    return js

# ---------------------------------------------------------------- keyframe camera
# Each keyframe: [t, zoom, cx, cy(, ease)]. The point (cx, cy) sits at the center of the screen. Zoom interpolated in log, easeInOutCubic.
CAM_JS = r"""
  function cam(sel, ks){
    var el=document.querySelector(sel);
    function place(z,cx,cy){el.setAttribute("transform","translate(960 540) scale("+z+") translate("+(-cx)+" "+(-cy)+")");}
    place(ks[0][1],ks[0][2],ks[0][3]);
    function seg(a,b){
      var o={u:0}, la=Math.log(a[1]), lb=Math.log(b[1]), ez=gsap.parseEase(b[4]||"power3.inOut");
      tl.fromTo(o,{u:0},{u:1,duration:Math.max(0.01,b[0]-a[0]),ease:"none",immediateRender:false,onUpdate:function(){
        var e=ez(o.u); place(Math.exp(la+(lb-la)*e), a[2]+(b[2]-a[2])*e, a[3]+(b[3]-a[3])*e);}},a[0]);
    }
    for(var i=0;i+1<ks.length;i++){seg(ks[i],ks[i+1]);}
  }
  function look(sel,t,x,dur){tl.to(sel,{x:x,duration:dur||0.35,ease:"power2.inOut"},t);}
"""
# only in the scenes with the new figure (kept out of CAM_JS so the HTML of the other scenes does not change)
FIGURE_JS = r"""
  // transform origin at a local point (x, y) of the group: the new figure has huge mask paths and "50% 50%" lands far away
  function originAt(sel,x,y){try{var b=document.querySelector(sel).getBBox();return (x-b.x)+"px "+(y-b.y)+"px";}catch(e){return "50% 100%";}}
  function popFig(sel,t,x,y,from,dur){
    tl.fromTo(sel,{scale:from||0.3,opacity:0,transformOrigin:originAt(sel,x,y)},{scale:1,opacity:1,duration:dur||0.7,ease:"elastic.out(1,0.45)",immediateRender:false},t);
    tl.set(sel,{opacity:0},0);
  }
"""


def comp(p, dur, svg_cam, html, js, extra="", fixed="", background=("#3a1d7a", "#1a1050", "#0b0a24"), seed=3):
    """Like engine.composition, but with `fixed` (svg outside the camera, on top) and the keyframe camera."""
    body = f'<g id="{p}-cam">{svg_cam}</g>{fixed}'
    return composition2(p, dur, body, html, JS_LIB + CAM_JS + js, extra, background=background, seed=seed)


# ---------------------------------------------------------------- motif and office pieces
def key_svg(p, k="key", s=1.0, x=0, y=0, op=0):
    """Amber key (drawing from scenes-v4/build4.py::scene_M8, with glow). Local center ~ (0, 60). Animatable id {p}-{k}."""
    return (f'<g transform="translate({x} {y}) scale({s})"><g id="{p}-{k}" opacity="{op}"><rect x="-60" y="-50" width="120" height="220" fill="none"/>'
            f'<g filter="url(#{p}-glow)"><circle cx="0" cy="0" r="34" fill="none" stroke="{AMBER}" stroke-width="12"/>'
            f'<path d="M0 34 L0 130 M0 100 L30 100 M0 124 L22 124" stroke="{AMBER}" stroke-width="12" fill="none" stroke-linecap="round"/></g>'
            f'<circle cx="-12" cy="-14" r="6" fill="#fff3c8" opacity=".8"/></g></g>')


def keyhole(p, k="keyhole", s=1.0, x=0, y=0, op=1, lit=True):
    """Keyhole plate in amber line, with a lit hole. Local center (0, 0), box ~ 140 x 240."""
    core = AMBER if lit else "#05031a"
    return (f'<g transform="translate({x} {y}) scale({s})"><g id="{p}-{k}" opacity="{op}"><rect x="-70" y="-120" width="140" height="240" fill="none"/>'
            f'<rect x="-62" y="-112" width="124" height="224" rx="40" fill="#14123a" stroke="{AMBER}" stroke-width="7" filter="url(#{p}-glow)"/>'
            f'<g id="{p}-{k}-hole"><circle cx="0" cy="-26" r="26" fill="{core}"/><polygon points="-14,-10 14,-10 26,62 -26,62" fill="{core}"/></g>'
            f'<circle cx="-40" cy="-90" r="5" fill="{AMBER}" opacity=".7"/><circle cx="40" cy="90" r="5" fill="{AMBER}" opacity=".7"/></g></g>')


def sheet_svg(p, k="sheet", lines=7, title=True, fine_print=0):
    """Contract sheet (local center 0,0; 520 x 660). Signature in {p}-signature (dasharray 320), empty line on the right.
    `fine_print`: fine print lines between the body and the signatures."""
    rows = "".join(f'<rect x="-210" y="{-250 + j * 34}" width="{360 if j % 3 else 270}" height="10" rx="5" fill="#8a7f68" opacity=".45"/>' for j in range(lines))
    rows += "".join(f'<rect x="-210" y="{10 + j * 16}" width="{420 - (j % 4) * 30}" height="5" rx="2.5" fill="#8a7f68" opacity=".55"/>' for j in range(fine_print))
    title_svg = '<rect x="-210" y="-300" width="200" height="20" rx="6" fill="#5a4a30" opacity=".75"/>' if title else ""
    return (f'<g id="{p}-{k}"><rect x="-260" y="-330" width="520" height="660" fill="none"/>'
            f'<g filter="url(#{p}-shadow)"><rect x="-260" y="-330" width="520" height="660" rx="16" fill="url(#{p}-paper)"/></g>{title_svg}{rows}'
            f'<line x1="-210" y1="260" x2="-20" y2="260" stroke="#3a3a3a" stroke-width="4"/><line x1="40" y1="260" x2="230" y2="260" stroke="#3a3a3a" stroke-width="4"/>'
            f'<path id="{p}-signature" d="M-205 252 C -180 200 -160 270 -140 230 S -100 210 -80 250 S -50 230 -28 246" fill="none" stroke="#1d2f9a" stroke-width="7" stroke-linecap="round" stroke-dasharray="320" stroke-dashoffset="320"/>'
            f'<g id="{p}-empty" opacity="0"><circle cx="135" cy="228" r="40" fill="#ff4f7d"/><text x="135" y="246" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="52" fill="#fff">?</text></g></g>')


def office_grads(p):
    return (f'<linearGradient id="{p}-paper" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#e9dcc2"/></linearGradient>'
            f'<linearGradient id="{p}-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a1850"/><stop offset=".72" stop-color="#2a2878"/><stop offset=".72" stop-color="#15134a"/><stop offset="1" stop-color="#0c0a2e"/></linearGradient>'
            f'<linearGradient id="{p}-doorLight" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffe9a8" stop-opacity=".7"/><stop offset="1" stop-color="#ffe9a8" stop-opacity=".05"/></linearGradient>'
            f'<radialGradient id="{p}-screen" cx="50%" cy="40%" r="70%"><stop offset="0" stop-color="#3be0ff" stop-opacity=".55"/><stop offset="1" stop-color="#1a3b86" stop-opacity=".2"/></radialGradient>')


def door(p, x, y=190, k="door", opened=0.0, with_lock=True):
    """Door (340 x 680) with warm light behind it and an amber keyhole. {p}-{k}-leaf is the door leaf (scaleX to open it)."""
    kh = keyhole(p, k + "-keyhole", 0.5, x + 290, y + 360, 1, False) if with_lock else ""
    return (f'<g id="{p}-{k}"><rect x="{x - 20}" y="{y - 20}" width="380" height="720" rx="18" fill="#0c0a2e" stroke="#8d7bff" stroke-width="8" filter="url(#{p}-glow)"/>'
            f'<rect x="{x}" y="{y}" width="340" height="680" fill="url(#{p}-doorLight)"/>'
            f'<g id="{p}-{k}-leaf"><rect x="{x}" y="{y}" width="340" height="680" fill="#24206a" stroke="#4a46b0" stroke-width="4"/>'
            f'<rect x="{x + 40}" y="{y + 50}" width="260" height="250" rx="8" fill="none" stroke="#3a3690" stroke-width="5"/>'
            f'<rect x="{x + 40}" y="{y + 360}" width="200" height="260" rx="8" fill="none" stroke="#3a3690" stroke-width="5"/>{kh}</g></g>')


def desk(p, x0, width=1000, y=640, k="desk"):
    """Desk seen from the front (top at y) with a monitor on the right and a shadow."""
    mx = x0 + width - 330
    return (f'<g id="{p}-{k}"><ellipse cx="{x0 + width / 2:.0f}" cy="{y + 268}" rx="{width * 0.52:.0f}" ry="26" fill="#05031a" opacity=".55"/>'
            f'<rect x="{x0 + 60}" y="{y + 40}" width="40" height="230" fill="#22186a"/><rect x="{x0 + width - 100}" y="{y + 40}" width="40" height="230" fill="#22186a"/>'
            f'<rect x="{x0}" y="{y}" width="{width}" height="44" rx="12" fill="#3a2a8c" stroke="#5a4ad0" stroke-width="3"/>'
            f'<rect x="{mx + 110}" y="{y - 40}" width="40" height="40" fill="#2a1d70"/><rect x="{mx + 50}" y="{y - 10}" width="160" height="12" rx="6" fill="#2a1d70"/>'
            f'<rect x="{mx}" y="{y - 230}" width="260" height="180" rx="14" fill="#0e0c26" stroke="#8d7bff" stroke-width="6"/>'
            f'<rect id="{p}-{k}-screen" x="{mx + 14}" y="{y - 216}" width="232" height="152" rx="6" fill="url(#{p}-screen)"/></g>')


# ---------------------------------------------------------------- contract 3: the one who signed was the outside person
def contract_3():
    SC, SG = "contract", 3
    p = "contract_3"
    start, dur = seg(SC, SG)
    t_signed, t_outside, t_work, t_suffers, t_obeys, t_inside, t_never, t_anything, t_born, t_employed = (
        0.46, 1.54, 3.43, 4.24, 4.72, 5.8 - 0.15, 7.3, 9.08, 10.2, 10.88)
    SH = 1380  # shift of the world from outside to inside
    stack = "".join(f'<rect x="{2600 + (k % 3) * 8}" y="{628 - k * 15}" width="150" height="12" rx="3" fill="#fffaf0" stroke="#c9bb98" stroke-width="1.5" transform="rotate({(k % 3 - 1) * 2} 2675 {628 - k * 15})"/>' for k in range(9))
    IX, IY, IS = 2350, 900, 1.1                 # inside person (shirt and tie), sitting at the desk
    hc = ANCHORS[("work", "sitting", 30)]["head_center"]
    nx, ny = IX + (hc[0] + 4) * IS, IY + (hc[1] + 52) * IS   # base of the neck (collar) of the new figure
    badge = (f'<g id="{p}-badge" opacity="0"><path d="M{nx - 22:.0f} {ny:.0f} L{nx:.0f} {ny + 52:.0f} L{nx + 22:.0f} {ny:.0f}" fill="none" stroke="{AMBER}" stroke-width="5" stroke-linejoin="round"/>'
              f'<g transform="translate({nx:.0f} {ny + 52:.0f}) scale(.36)"><g id="{p}-badgeB"><rect x="-150" y="-10" width="300" height="190" fill="none"/>'
              f'<rect x="-150" y="0" width="300" height="180" rx="18" fill="#fffaf0" stroke="{AMBER}" stroke-width="7"/><rect x="-36" y="-14" width="72" height="26" rx="8" fill="{AMBER}"/>'
              f'<rect x="-122" y="34" width="104" height="116" rx="10" fill="#2a2878"/>'
              f'<g transform="translate(-130 40) scale(.42)"><path d="{H_LINE}" fill="none" stroke="#3be0ff" stroke-width="7" stroke-linecap="round"/></g>'
              f'<rect x="4" y="50" width="120" height="16" rx="8" fill="#8a7f68"/><rect x="4" y="84" width="90" height="14" rx="7" fill="#bfb49a"/><rect x="4" y="114" width="110" height="14" rx="7" fill="#bfb49a"/></g></g></g>')
    extra = office_grads(p)
    svg = f"""
<g id="{p}-world">
 <rect x="-600" y="-300" width="4400" height="1600" fill="url(#{p}-wall)"/>
 {door(p, 60, 180)}
 <ellipse cx="810" cy="870" rx="270" ry="24" fill="#05031a" opacity=".5"/>
 <g transform="translate(780 870) scale(1.05)"><g id="{p}-outside" opacity="0">{figure(p + "-figOut", "home", "standing", glow=p + "-glow")}</g></g>
 {desk(p, 2150, 1000)}
 <g id="{p}-stack" opacity="0">{stack}</g>
 <g transform="translate({IX} {IY}) scale({IS})"><g id="{p}-inside" opacity="0">{figure(p + "-figIn", "work", "sitting", glow=p + "-glow")}</g></g>
 <g id="{p}-drops" opacity="0" fill="#7fe6ff"><path d="M2420 370 q-12 26 0 36 q12 -10 0 -36z"/><path d="M2450 420 q-10 22 0 30 q10 -8 0 -30z"/></g>
 {badge}
</g>
<g transform="translate(1330 470)"><g id="{p}-sheetM"><g id="{p}-sheetW" opacity="0">{sheet_svg(p)}<circle cx="0" cy="-306" r="20" fill="{RED}" stroke="#fff3c8" stroke-width="4"/><circle cx="-6" cy="-312" r="6" fill="#fff" opacity=".7"/></g></g></g>"""
    html = (text(f"{p}-t1", "OUTSIDE", "left:560px;width:520px;text-align:center;top:905px;font-size:80px;color:#bff4ff;letter-spacing:.12em") +
            text(f"{p}-t2", "INSIDE", "left:920px;width:640px;text-align:center;top:930px;font-size:80px;color:#c9b8ff;letter-spacing:.12em") +
            text(f"{p}-t3", "BORN EMPLOYED", "left:0;right:0;text-align:center;top:60px;font-size:104px;color:#ffd98a"))
    js = f"""
  cam("#{p}-cam", [[0,1.0,960,540],[{t_work - 0.3:.2f},1.0,960,540],[{t_never - 0.2:.2f},1.0,960,540],[{dur:.2f},1.0,1030,540,"sine.inOut"]]);
  popFig("#{p}-outside", 0.2, 0, 0, 0.5, 0.8);
  enter("#{p}-sheetW", {t_signed - 0.2:.2f}, 0.3); tl.fromTo("#{p}-sheetW",{{scale:0.5,transformOrigin:"50% 50%"}},{{scale:1,duration:0.7,ease:"elastic.out(1,0.5)",immediateRender:false}},{t_signed - 0.2:.2f});
  look("#{p}-figOut-eye", {t_signed:.2f}, 3);
  tl.fromTo("#{p}-signature",{{attr:{{"stroke-dashoffset":320}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.9,ease:"power2.inOut"}},{t_signed + 0.25:.2f});
  rise("#{p}-t1 span", {t_outside:.2f});
  tl.fromTo(["#{p}-world","#{p}-t1"],{{x:0}},{{x:-{SH},duration:1.3,ease:"power3.inOut",immediateRender:false}},{t_work - 0.25:.2f});
  tl.fromTo("#{p}-sheetM",{{x:0,scale:1,transformOrigin:"50% 50%"}},{{x:-930,scale:0.8,transformOrigin:"50% 50%",duration:1.3,ease:"power3.inOut",immediateRender:false}},{t_work - 0.25:.2f});
  popFig("#{p}-inside", {t_work - 0.1:.2f}, 0, 0, 0.5, 0.8);
  enter("#{p}-stack", {t_work:.2f}, 0.1);
  tl.fromTo("#{p}-stack rect",{{y:-160,opacity:0}},{{y:0,opacity:1,duration:0.35,ease:"bounce.out",stagger:0.3}},{t_work:.2f});
  enter("#{p}-drops", {t_suffers:.2f}, 0.2); tl.fromTo("#{p}-drops",{{y:0}},{{y:40,duration:0.8,repeat:2,ease:"power1.in"}},{t_suffers:.2f}); vanish("#{p}-drops", {t_obeys + 0.4:.2f}, 0.3);
  tl.fromTo("#{p}-inside",{{y:0}},{{y:8,duration:0.25,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_obeys:.2f});
  rise("#{p}-t2 span", {t_inside:.2f});
  look("#{p}-figIn-eye", {t_never - 0.3:.2f}, -3);
  enter("#{p}-empty", {t_never:.2f}, 0.15); tl.fromTo("#{p}-empty",{{scale:2.2,transformOrigin:"50% 50%"}},{{scale:1,duration:0.6,ease:"back.out(3)",immediateRender:false}},{t_never:.2f});
  tl.fromTo("#{p}-sheetW",{{rotation:0}},{{rotation:2.5,duration:0.1,repeat:5,yoyo:true,ease:"none",immediateRender:false}},{t_anything:.2f});
  tl.fromTo("#{p}-inside",{{rotation:0,transformOrigin:originAt("#{p}-inside",0,-200)}},{{rotation:3,duration:0.12,repeat:7,yoyo:true,ease:"none",immediateRender:false}},{t_anything:.2f});
  look("#{p}-figIn-eye", {t_born - 0.2:.2f}, 0);
  tl.to("#{p}-t2 span",{{yPercent:125,duration:0.5,ease:"power2.in"}},{t_born - 0.3:.2f});
  rise("#{p}-t3 span", {t_born:.2f}, 0.9);
  enter("#{p}-badge", {t_born:.2f}, 0.1);
  tl.fromTo("#{p}-badge",{{y:-260}},{{y:0,duration:0.9,ease:"bounce.out",immediateRender:false}},{t_born:.2f});
  tl.fromTo("#{p}-badgeB",{{rotation:-8,transformOrigin:"50% 0%"}},{{rotation:0,duration:1.4,ease:"elastic.out(1,0.3)",immediateRender:false}},{t_born + 0.7:.2f});
""" + figure_idle(p + "-figOut", dur) + figure_idle(p + "-figIn", dur, (3.6, 7.0, 10.4))
    return comp(p, dur, svg, html, FIGURE_JS + js, extra)


# ---------------------------------------------------------------- contract 2: read the contract carefully
def contract_2():
    SC, SG = "contract", 2
    p = "contract_2"
    start, dur = seg(SC, SG)
    t_sounds, t_relief, t_but, t_read, t_contract, t_carefully = 0.29, 1.03, 1.98, 2.21, 2.83, 3.77
    FX, FY, FS = 520, 1475, 1.8                 # close shot: the person in a hoodie standing, cut at the hip (hoodie hem), reading the offer
    hc = ANCHORS[("home", "standing", 30)]["head_center"]
    hx, hy = FX + hc[0] * FS, FY + hc[1] * FS     # head
    big = "".join(f'<rect x="-150" y="{-104 + j * 34}" width="{300 - (j % 3) * 40}" height="12" rx="6" fill="#8a7f68" opacity=".75"/>' for j in range(7))
    extra = office_grads(p) + f'<clipPath id="{p}-lensClip"><circle cx="0" cy="0" r="122"/></clipPath>'
    svg = f"""
<circle id="{p}-halo" cx="{hx:.0f}" cy="{hy:.0f}" r="300" fill="#38e8a8" opacity="0" filter="url(#{p}-blur40)"/>
<g transform="translate({FX} {FY}) scale({FS})"><g id="{p}-fig">{figure(p + "-figA", "home", "standing", glow=p + "-glow", shadow=False)}</g></g>
<g transform="translate(1380 520)"><g id="{p}-sheetW">{sheet_svg(p, fine_print=8)}</g></g>
<g transform="translate(1390 586)"><g id="{p}-lens" opacity="0"><rect x="-150" y="-150" width="420" height="420" fill="none"/>
 <path d="M92 92 L210 210" stroke="#8d7bff" stroke-width="30" stroke-linecap="round"/><path d="M92 92 L210 210" stroke="#b9adff" stroke-width="10" stroke-linecap="round" opacity=".6"/>
 <g clip-path="url(#{p}-lensClip)"><circle r="122" fill="#fffaf0"/><rect id="{p}-highlight" x="-160" y="-2" width="320" height="24" fill="#ff4f7d" opacity="0"/>{big}</g>
 <circle r="126" fill="none" stroke="#3be0ff" stroke-width="12" filter="url(#{p}-glow)"/><path d="M-80 -70 A 100 100 0 0 1 -20 -104" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round" opacity=".7"/></g></g>"""
    html = (text(f"{p}-t1", "SOUNDS LIKE A RELIEF", "left:0;right:0;text-align:center;top:28px;font-size:96px;color:#bff8e4") +
            text(f"{p}-t2", "READ THE CONTRACT", "left:480px;width:820px;top:960px;font-size:66px;color:#eef1f7") +
            text(f"{p}-t3", "CAREFULLY", "left:1290px;width:520px;top:960px;font-size:66px;color:#ffd98a"))
    js = f"""
  cam("#{p}-cam", [[0,1.0,960,540],[{t_but:.2f},1.04,900,540,"sine.inOut"],[{t_contract + 0.1:.2f},1.12,1100,540],[{dur:.2f},1.16,1110,540,"sine.inOut"]]);
  tl.set("#{p}-signature",{{attr:{{"stroke-dashoffset":0}}}},0);
  popFig("#{p}-fig", 0.1, 0, -300, 0.6, 0.8); pop("#{p}-sheetW", 0.25, 0.6, 0.8);
  rise("#{p}-t1 span", {t_sounds:.2f});
  tl.fromTo("#{p}-halo",{{opacity:0}},{{opacity:0.45,duration:0.5,yoyo:true,repeat:1,ease:"sine.inOut"}},{t_relief:.2f});
  tl.fromTo("#{p}-figA-eye",{{scaleY:1,transformOrigin:"50% 50%"}},{{scaleY:0.1,transformOrigin:"50% 50%",duration:0.2,yoyo:true,repeat:1,repeatDelay:0.4,immediateRender:false}},{t_relief:.2f});
  tl.fromTo("#{p}-fig",{{y:0}},{{y:6,duration:0.45,yoyo:true,repeat:1,ease:"sine.inOut",immediateRender:false}},{t_relief:.2f});
  tl.to("#{p}-t1 span",{{yPercent:-125,duration:0.45,ease:"power2.in"}},{t_but - 0.1:.2f});
  look("#{p}-figA-eye", {t_but:.2f}, 3);
  rise("#{p}-t2 span", {t_read:.2f});
  enter("#{p}-lens", {t_read:.2f}, 0.2);
  tl.fromTo("#{p}-lens",{{x:520,y:260,rotation:12,transformOrigin:"50% 50%"}},{{x:0,y:0,rotation:0,duration:0.9,ease:"power3.out",immediateRender:false}},{t_read:.2f});
  tl.fromTo("#{p}-lens",{{x:0}},{{x:-40,duration:1.6,ease:"sine.inOut",yoyo:true,repeat:1,immediateRender:false}},{t_read + 0.9:.2f});
  rise("#{p}-t3 span", {t_carefully - 0.2:.2f});
  tl.fromTo("#{p}-highlight",{{opacity:0,scaleX:0,transformOrigin:"0% 50%"}},{{opacity:0.55,scaleX:1,duration:0.6,ease:"power2.out"}},{t_carefully:.2f});
""" + figure_idle(p + "-figA", dur, (3.9,))
    return comp(p, dur, svg, html, FIGURE_JS + js, extra)


# ---------------------------------------------------------------- contract 4: would that choice be free?
def contract_4():
    SC, SG = "contract", 4
    p = "contract_4"
    start, dur = seg(SC, SG)
    t_consent, t_extreme, t_how, t_accept, t_never, t_remember, t_saying_no, t_cost, t_job, t_that, t_choice, t_free = (
        1.25, 3.04, 4.19, 4.81, 6.73, 8.11, 9.04, 9.81, 10.68,
        11.53, 11.95, 13.65)
    PX, PY, S = 420, 970, 1.2                   # person standing (work), feet at PY
    mx, my = PX + 260, PY - 600 * S             # the memory of signing, in an orb next to the face
    hc = ANCHORS[("work", "standing", 30)]["head_center"]
    nx, ny = PX + (hc[0] + 4) * S, PY + (hc[1] + 48) * S     # base of the neck (collar) of the new figure
    SX, SY = 1420, 545                          # sheet
    cbx, cby = SX - 150, SY + 130               # center of the accept checkbox
    badge = (f'<g id="{p}-badge" opacity="0"><path id="{p}-lanyard" d="M{nx - 22:.0f} {ny:.0f} L{nx:.0f} {ny + 58:.0f} L{nx + 22:.0f} {ny:.0f}" fill="none" stroke="{AMBER}" stroke-width="5" stroke-linejoin="round"/>'
              f'<g transform="translate({nx:.0f} {ny + 58:.0f}) scale(.42)"><g id="{p}-badgeB"><rect x="-140" y="-12" width="280" height="190" fill="none"/>'
              f'<rect id="{p}-badgeF" x="-130" y="0" width="260" height="160" rx="16" fill="#fffaf0" stroke="{AMBER}" stroke-width="7"/><rect x="-30" y="-12" width="60" height="22" rx="7" fill="{AMBER}"/>'
              f'<rect x="-106" y="28" width="90" height="104" rx="9" fill="#2a2878"/><g transform="translate(-112 34) scale(.37)"><path d="{H_LINE}" fill="none" stroke="#3be0ff" stroke-width="7"/></g>'
              f'<rect x="4" y="44" width="104" height="14" rx="7" fill="#8a7f68"/><rect x="4" y="76" width="78" height="12" rx="6" fill="#bfb49a"/><rect x="4" y="102" width="96" height="12" rx="6" fill="#bfb49a"/></g></g></g>')
    button = lambda k, y, color, icon: (f'<g transform="translate(1480 {y})"><g id="{p}-{k}" opacity="0"><rect x="-150" y="-150" width="300" height="300" fill="none"/>'
                                     f'<circle r="132" fill="#0e0c2e" stroke="{color}" stroke-width="12" filter="url(#{p}-glow)"/><circle r="104" fill="{color}" opacity=".16"/>'
                                     f'<path d="{icon}" fill="none" stroke="{color}" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/></g></g>')
    extra = office_grads(p)
    svg = f"""
<ellipse id="{p}-shadowFig" cx="{PX + 20}" cy="{PY + 6}" rx="230" ry="22" fill="#05031a" opacity="0"/>
<ellipse id="{p}-shadowBadge" cx="{PX - 155}" cy="{PY + 4}" rx="62" ry="8" fill="#05031a" opacity="0"/>
<g transform="translate({PX} {PY}) scale({S})"><g id="{p}-fig">{figure(p + "-figA", "work", "standing", glow=p + "-glow")}</g></g>
<g id="{p}-memW">{orb(p + "-mem", "clock", round(mx), round(my), AMBER, 58)}</g>
{badge}
<g transform="translate({SX} {SY})"><g id="{p}-sheetM"><g id="{p}-sheetW" opacity="0">{sheet_svg(p, lines=6, fine_print=0)}
 <rect x="-200" y="80" width="100" height="100" rx="12" fill="#fffaf0" stroke="#3a3a3a" stroke-width="6"/>
 <path id="{p}-check" d="M-186 128 L-158 160 L-104 84" fill="none" stroke="#1faa7a" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="160" stroke-dashoffset="160"/>
 <rect x="-60" y="112" width="250" height="12" rx="6" fill="#8a7f68" opacity=".55"/><rect x="-60" y="140" width="190" height="12" rx="6" fill="#8a7f68" opacity=".55"/></g></g></g>
<path id="{p}-wire" d="M{mx:.0f} {my:.0f} C {mx + 260:.0f} {my - 160:.0f} {cbx - 220:.0f} {cby - 260:.0f} {cbx:.0f} {cby:.0f}" fill="none" stroke="{AMBER}" stroke-width="7" stroke-dasharray="1400" stroke-dashoffset="1400" stroke-linecap="round" filter="url(#{p}-glow)"/>
{button("yes", 360, MINT, "M-52 4 L-14 44 L58 -44")}
{button("no", 760, RED, "M-44 -44 L44 44 M44 -44 L-44 44")}"""
    html = (text(f"{p}-t1", "CONSENT", "left:0;right:0;text-align:center;top:34px;font-size:110px;color:#eef1f7") +
            text(f"{p}-t2", "WILL NEVER BE ABLE TO REMEMBER", "left:720px;right:30px;text-align:center;top:944px;font-size:56px;color:#ffd98a") +
            text(f"{p}-t3", "WOULD THAT CHOICE BE FREE?", "left:0;right:0;text-align:center;top:34px;font-size:100px;color:#eef1f7"))
    js = f"""
  cam("#{p}-cam", [[0,0.95,{SX},{SY - 20}],[{t_extreme - 0.05:.2f},0.99,{SX},{SY - 20},"sine.inOut"],[{t_extreme + 0.35:.2f},1.3,{cbx + 60},{cby - 70},"power4.out"],[{t_how - 0.1:.2f},1.32,{cbx + 60},{cby - 70},"none"],
       [{t_accept + 0.3:.2f},1.0,960,540],[{t_that:.2f},1.0,960,540],[{dur:.2f},1.04,960,540,"sine.inOut"]]);
  enter("#{p}-sheetW", 0.05, 0.4);
  rise("#{p}-t1 span", {t_consent:.2f});
  tl.fromTo("#{p}-check",{{attr:{{"stroke-dashoffset":160}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.5,ease:"power2.out"}},{t_consent + 0.6:.2f});
  tl.to("#{p}-t1 span",{{yPercent:-125,duration:0.35,ease:"power2.in"}},{t_extreme - 0.3:.2f});
  popFig("#{p}-fig", {t_how:.2f}, 0, 0, 0.6, 0.8); tl.fromTo("#{p}-shadowFig",{{opacity:0}},{{opacity:0.5,duration:0.5}},{t_how:.2f});
  enter("#{p}-mem", {t_accept:.2f}, 0.3);
  tl.fromTo("#{p}-wire",{{attr:{{"stroke-dashoffset":1400}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.8,ease:"power2.inOut"}},{t_accept:.2f});
  tl.fromTo("#{p}-signature",{{attr:{{"stroke-dashoffset":320}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.7,ease:"power2.inOut"}},{t_accept + 0.5:.2f});
  rise("#{p}-t2 span", {t_never:.2f});
  tl.to("#{p}-mem",{{opacity:0.15,scale:0.4,transformOrigin:"50% 50%",duration:0.8,ease:"power2.in"}},{t_never + 0.2:.2f});
  tl.to("#{p}-wire",{{attr:{{"stroke-dashoffset":-1400}},duration:0.7,ease:"power2.in"}},{t_remember:.2f});
  tl.to("#{p}-check",{{opacity:0.2,duration:0.5}},{t_remember:.2f});
  look("#{p}-figA-eye", {t_remember:.2f}, -3);
  tl.to("#{p}-t2 span",{{yPercent:125,duration:0.4,ease:"power2.in"}},{t_saying_no - 0.3:.2f});
  tl.to("#{p}-sheetM",{{x:700,opacity:0,duration:0.6,ease:"power2.in"}},{t_saying_no - 0.3:.2f});
  pop("#{p}-yes", {t_saying_no - 0.1:.2f}, 0.4, 0.7); pop("#{p}-no", {t_saying_no + 0.1:.2f}, 0.4, 0.7);
  look("#{p}-figA-eye", {t_saying_no:.2f}, 3);
  tl.fromTo("#{p}-no",{{scale:1}},{{scale:0.86,duration:0.15,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{t_saying_no + 0.8:.2f});
  enter("#{p}-badge", {t_cost:.2f}, 0.1);
  tl.fromTo("#{p}-badge",{{y:-200}},{{y:0,duration:0.7,ease:"bounce.out",immediateRender:false}},{t_cost:.2f});
  tl.to("#{p}-lanyard",{{opacity:0,duration:0.15}},{t_job:.2f});
  tl.to("#{p}-badgeF",{{attr:{{fill:"#8a8aa0"}},duration:0.3}},{t_job:.2f});
  tl.to("#{p}-badgeB",{{x:-430,y:960,rotation:-74,transformOrigin:"50% 0%",duration:0.6,ease:"power2.in"}},{t_job + 0.05:.2f});  // falls to the floor next to the foot
  tl.fromTo("#{p}-shadowBadge",{{opacity:0}},{{opacity:0.55,duration:0.2,immediateRender:false}},{t_job + 0.55:.2f});
  rise("#{p}-t3 span", {t_that:.2f}, 0.9);
  tl.fromTo("#{p}-yes",{{scale:1}},{{scale:1.1,duration:0.45,yoyo:true,repeat:1,ease:"sine.inOut",immediateRender:false}},{t_choice:.2f});
  tl.fromTo("#{p}-no",{{scale:1}},{{scale:1.1,duration:0.45,yoyo:true,repeat:1,ease:"sine.inOut",immediateRender:false}},{t_choice + 0.9:.2f});
  look("#{p}-figA-eye", {t_choice:.2f}, -2); look("#{p}-figA-eye", {t_choice + 0.9:.2f}, 3); look("#{p}-figA-eye", {t_free:.2f}, 0);
""" + figure_idle(p + "-figA", dur, (5.2, 9.6, 12.6))
    return comp(p, dur, svg, html, FIGURE_JS + js, extra)


# ---------------------------------------------------------------- contract 5: someone can hold the key
def contract_5():
    SC, SG = "contract", 5
    p = "contract_5"
    start, dur = seg(SC, SG)
    t_severance, t_fiction, t_nobody, t_split, t_memory, t_but, t_memory2, t_lock, t_someone, t_hold, t_key, t_not = (
        0.33, 1.07, 2.25, 3.13, 4.06, 5.57, 6.84, 8.62,
        9.97, 10.77, 11.41, 11.77)
    PX, PY, S = 150, 170, 2.9
    ox, oy = PX + 215 * S, PY + 72 * S          # the memory
    SX, SY, SS = 2000, 200, 2.6                 # someone (mirrored)
    kx, ky = SX - 200 * SS, SY + 92 * SS        # where the key is kept (inside someone's head)
    KS = 0.55
    brain = lambda k: f'<g transform="translate(196 118) scale(.82) translate(-196 -118)">{brain_side(p + k)}</g>'
    eye = (f'<g id="{p}-eye"><ellipse cx="257" cy="129" rx="9" ry="5.6" fill="#0a0820" stroke="#3be0ff" stroke-width="1.2"/><circle cx="259" cy="129" r="3.6" fill="#29b6ff"/><circle cx="260.2" cy="127.8" r="1.1" fill="#fff"/></g>'
            f'<path d="M 245 118 Q 257 111 269 119" fill="none" stroke="#3be0ff" stroke-width="2" stroke-linecap="round"/>')
    extra = (f'<clipPath id="{p}-cA"><rect x="60" y="0" width="134" height="300"/></clipPath><clipPath id="{p}-cB"><rect x="194" y="0" width="140" height="300"/></clipPath>'
             f'<radialGradient id="{p}-orbg"><stop offset="0" stop-color="#fffbe8"/><stop offset=".5" stop-color="#ffd98a"/><stop offset="1" stop-color="#ffb23e" stop-opacity="0"/></radialGradient>'
             f'<linearGradient id="{p}-sil" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c1450"/><stop offset="1" stop-color="#0a0828"/></linearGradient>')
    svg = f"""
<ellipse cx="{PX + 205 * S:.0f}" cy="{PY + 262 * S:.0f}" rx="270" ry="22" fill="#05031a" opacity=".5"/>
<g transform="translate({PX} {PY}) scale({S})"><g id="{p}-fig"><g id="{p}-bob">{head_line(p + "h", p + "-glow")}
 <g id="{p}-brainA" clip-path="url(#{p}-cA)">{brain("brainL")}</g><g id="{p}-brainB" clip-path="url(#{p}-cB)">{brain("brainR")}</g>
 <path id="{p}-cut" d="M194 22 L194 168" stroke="{AMBER}" stroke-width="2.6" stroke-dasharray="7 6" fill="none" opacity="0" filter="url(#{p}-glow)"/>{eye}</g></g></g>
<g transform="translate({SX} {SY}) scale({-SS} {SS})"><g id="{p}-someone" opacity="0"><path d="{H_LINE} Z" fill="url(#{p}-sil)" stroke="#8d7bff" stroke-width="3" stroke-linejoin="round" filter="url(#{p}-glow)"/></g></g>
<circle id="{p}-orb" cx="{ox:.0f}" cy="{oy:.0f}" r="34" fill="url(#{p}-orbg)" opacity="0"/>
{keyhole(p, "keyhole", 0.42, round(ox), round(oy), 0)}
{key_svg(p, "key", KS, round(ox), round(oy - 60 * KS), 0)}"""
    dx, dy = (kx - ox) / KS, (ky - oy) / KS
    html = (text(f"{p}-t1", "SEVERANCE IS FICTION", "left:0;right:0;text-align:center;top:40px;font-size:100px;color:#eef1f7") +
            text(f"{p}-t2", "LOCKED AWAY", "left:0;right:0;text-align:center;top:40px;font-size:110px;color:#ffd98a;letter-spacing:.06em") +
            text(f"{p}-t3", "THE KEY", "left:0;right:0;text-align:center;top:40px;font-size:100px;color:#ffd98a") +
            text(f"{p}-t4", "IS NOT AS FICTIONAL", "left:0;right:0;text-align:center;top:920px;font-size:88px;color:#eef1f7"))
    js = f"""
  cam("#{p}-cam", [[0,1.0,960,540],[{t_but:.2f},1.06,820,540,"sine.inOut"],[{t_lock - 0.1:.2f},2.2,{ox + 60:.0f},{oy + 50:.0f}],[{t_someone - 0.3:.2f},2.3,{ox + 60:.0f},{oy + 50:.0f},"none"],
       [{t_key + 0.1:.2f},1.0,1080,540],[{dur:.2f},1.05,1080,560,"sine.inOut"]]);
  pop("#{p}-fig", 0.1, 0.6, 0.8);
  tl.fromTo("#{p}-cut",{{opacity:0}},{{opacity:1,duration:0.3}},{t_severance:.2f});
  tl.fromTo("#{p}-cut",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-130}},duration:{t_memory - t_severance:.2f},ease:"none"}},{t_severance:.2f});
  tl.fromTo("#{p}-brainA",{{x:0}},{{x:-9,duration:0.7,ease:"power3.out",immediateRender:false}},{t_severance + 0.2:.2f});
  tl.fromTo("#{p}-brainB",{{x:0}},{{x:9,duration:0.7,ease:"power3.out",immediateRender:false}},{t_severance + 0.2:.2f});
  rise("#{p}-t1 span", {t_severance:.2f});
  tl.to("#{p}-t1 span",{{yPercent:-125,duration:0.45,ease:"power2.in"}},{t_nobody:.2f});
  tl.to("#{p}-brainA",{{x:-15,duration:0.18,yoyo:true,repeat:5,ease:"sine.inOut"}},{t_split:.2f});
  tl.to("#{p}-brainB",{{x:15,duration:0.18,yoyo:true,repeat:5,ease:"sine.inOut"}},{t_split:.2f});
  tl.to(["#{p}-brainA","#{p}-brainB"],{{x:0,duration:0.8,ease:"elastic.out(1,0.4)"}},{t_memory:.2f});
  tl.to("#{p}-cut",{{opacity:0,duration:0.4}},{t_memory + 0.2:.2f});
  tl.fromTo("#{p}-orb",{{opacity:0,scale:0.2,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.7,ease:"elastic.out(1,0.5)"}},{t_memory2:.2f});
  tl.fromTo("#{p}-orb",{{scale:1}},{{scale:1.25,duration:0.4,yoyo:true,repeat:1,ease:"sine.inOut",immediateRender:false}},{t_memory2 + 0.8:.2f});
  pop("#{p}-keyhole", {t_lock:.2f}, 1.8, 0.6);
  tl.to("#{p}-orb",{{scale:0.6,duration:0.4}},{t_lock:.2f});
  rise("#{p}-t2 span", {t_lock:.2f});
  tl.to("#{p}-t2 span",{{yPercent:-125,duration:0.4,ease:"power2.in"}},{t_someone - 0.4:.2f});
  enter("#{p}-key", {t_someone - 0.4:.2f}, 0.3);
  tl.fromTo("#{p}-key",{{y:0}},{{y:-150,duration:0.5,ease:"power2.out",immediateRender:false}},{t_someone - 0.4:.2f});
  enter("#{p}-someone", {t_someone:.2f}, 0.6);
  tl.to("#{p}-key",{{keyframes:{{x:[0,{dx * 0.45:.0f},{dx:.0f}],y:[-150,{dy - 520:.0f},{dy:.0f}],easeEach:"sine.inOut"}},rotation:360,transformOrigin:"50% 30%",duration:{max(0.8, t_key - t_someone + 0.2):.2f},ease:"power1.inOut"}},{t_someone + 0.1:.2f});
  tl.fromTo("#{p}-key",{{scale:1}},{{scale:2.6,duration:0.6,ease:"elastic.out(1,0.5)",immediateRender:false}},{t_key + 0.3:.2f});
  rise("#{p}-t3 span", {t_key:.2f});
  rise("#{p}-t4 span", {t_not:.2f}, 0.9);
  look("#{p}-eye", {t_key:.2f}, 3);
  tl.fromTo("#{p}-bob",{{y:0}},{{y:-4,duration:1.6,repeat:8,yoyo:true,ease:"sine.inOut"}},0);
"""
    return comp(p, dur, svg, html, js, extra, seed=9)


# ---------------------------------------------------------------- contract 0: home and work side by side, the door that erases memory
def contract_0():
    SC, SG = "contract", 0
    p = "contract_0"
    start, dur = seg(SC, SG)
    t_offer, t_perk, t_strange, t_when, t_leave, t_office, t_forget, t_everything, t_inside, t_pressure, t_work, t_conflicts, t_dont, t_home = (
        0.94, 3.03, 3.9, 4.72, 4.92, 5.36, 6.71, 7.46, 9.46,
        9.92, 11.24, 12.41, 13.38, 14.39)
    FLOOR, PX0, DOOR_X, OX = 880, 1300, 2000, 2520     # floor, chair, door plane (home | work), spot in the office
    S = 1.1
    # walk timing: goes in 3.75 -> 5.35 and comes back 5.6 -> 8.4; w_door and w_exit are the moments
    # when the middle of the body crosses the door plane (on the way back it matches "forget")
    w_rise, w_desk, w_back, w_chair = 3.75, 5.35, 5.6, 8.4
    inv = lambda f: math.sqrt(f / 2) if f < 0.5 else 1 - math.sqrt((1 - f) / 2)     # inverse of power1.inOut (the ease used by walk)
    w_door = w_rise + (w_desk - w_rise) * inv((DOOR_X - PX0) / (OX - PX0))
    w_exit = w_back + (w_chair - w_back) * inv((OX - DOOR_X) / (OX - PX0))

    def person_g(k, var, pose, x, flip=False, op=0):
        return (f'<g transform="translate({x} {FLOOR}) scale({-S if flip else S} {S})"><g id="{p}-w{k}" opacity="{op}">'
                f'{figure(f"{p}-fig{k}", var, pose, glow=p + "-glow", chair=False)}</g></g>')

    def fixed_chair(x):
        """Only the chair from the sitting drawing (with its clipPaths and rim), so it stays in place when the person stands up."""
        g = figure(f"{p}-chair", "home", "sitting")
        defs = g[g.index("<defs>"):g.index("</defs>") + 7]
        chair_svg = re.search(r"<!--chair-->.*?<!--/chair-->", g, re.S).group(0)
        return f'<g transform="translate({x} {FLOOR}) scale({S})">{defs}<g filter="url(#{p}-chair-rim)">{chair_svg}</g></g>'
    home_pics = [("family", 260, 250, -2), ("birthday", 550, 230, 2), ("car", 840, 260, -1), ("graduation", 390, 520, 1), ("beach", 710, 540, -2)]
    work_pics = [("award", 2900, 240, 1), ("meeting", 3180, 220, -1), ("spreadsheet", 3460, 240, 2), ("coffee", 3740, 225, -2)]
    frames_home = "".join(picture(f"{p}-picH{k}", t, x, y, 1.0, r) for k, (t, x, y, r) in enumerate(home_pics))
    frames_work = "".join(picture(f"{p}-picW{k}", t, x, y, 0.95, r, frame="#5a6a9a") for k, (t, x, y, r) in enumerate(work_pics))
    orb_home = [("heart", 1095, 320, "#ff4fa3"), ("sun", 1250, 245, "#ffd23e"), ("cake", 1430, 255, "#ffb23e"), ("car", 1050, 480, "#ff7a5a"), ("note", 1590, 360, "#ff9bd0")]
    orb_work = [("clock", 2290, 200, "#3be0ff"), ("lightning", 2470, 115, "#8d7bff"), ("cup", 2710, 390, "#38e8a8"), ("clock", 2670, 185, "#6a8cff")]   # outside the head path_d
    orbs_home = "".join(f'<g id="{p}-orbH{k}w">{orb(f"{p}-orbH{k}", s_, x, y, c, 64)}</g>' for k, (s_, x, y, c) in enumerate(orb_home))
    orbs_work = "".join(f'<g id="{p}-orbW{k}w">{orb(f"{p}-orbW{k}", s_, x, y, c, 64)}</g>' for k, (s_, x, y, c) in enumerate(orb_work))
    # bills: sheets with a dollar sign that fall and lean on the door, on the office side
    bill = lambda k, x, rot: (f'<g transform="translate({x} {FLOOR - 100}) rotate({rot})"><g id="{p}-bill{k}" opacity="0"><rect x="-80" y="-100" width="160" height="200" rx="10" fill="#fffaf0" stroke="#c9bb98" stroke-width="3"/>'
                                f'<circle cx="0" cy="-30" r="44" fill="#ff4f7d"/><text x="0" y="-4" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="74" fill="#fff">$</text>'
                                f'<rect x="-56" y="34" width="112" height="10" rx="5" fill="#8a7f68" opacity=".6"/><rect x="-56" y="56" width="80" height="10" rx="5" fill="#8a7f68" opacity=".6"/></g></g>')
    bills = bill(0, 2250, -8) + bill(1, 2390, 6) + bill(2, 2320, -2) + bill(3, 2470, 10) + bill(4, 2560, -14)
    # conflicts: red sparks
    spark = lambda k, x, y, s: (f'<g transform="translate({x} {y}) scale({s})"><g id="{p}-spark{k}" opacity="0"><rect x="-70" y="-70" width="140" height="140" fill="none"/>'
                                 f'<g stroke="#ff4f7d" stroke-width="9" stroke-linecap="round" filter="url(#{p}-glow)">'
                                 + "".join(f'<path d="M{24 * math.cos(a):.0f} {24 * math.sin(a):.0f} L{62 * math.cos(a + 0.12):.0f} {62 * math.sin(a + 0.12):.0f}"/>' for a in [j * math.pi / 4 + 0.2 for j in range(8)])
                                 + f'</g><path d="M-14 -22 L6 -4 L-8 2 L12 22" fill="none" stroke="#fff3f6" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g></g>')
    sparks = spark(0, 2300, 520, 1.2) + spark(1, 2560, 420, 1.0) + spark(2, 2440, 650, 0.9) + spark(3, 2700, 600, 1.1) + spark(4, 2230, 360, 0.8)
    extra = office_grads(p) + (
        f'<linearGradient id="{p}-wallHome" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a1f5e"/><stop offset="1" stop-color="#5a2f6e"/></linearGradient>'
        f'<linearGradient id="{p}-wallWork" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16285a"/><stop offset="1" stop-color="#22407a"/></linearGradient>'
        f'<linearGradient id="{p}-ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a1240"/><stop offset="1" stop-color="#07061a"/></linearGradient>'
        f'<radialGradient id="{p}-lamp"><stop offset="0" stop-color="#ffe2a0" stop-opacity=".5"/><stop offset="1" stop-color="#ffe2a0" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="{p}-clipHome"><rect x="-900" y="-900" width="{DOOR_X + 900}" height="2700"/></clipPath>'
        f'<clipPath id="{p}-clipWork"><rect x="{DOOR_X}" y="-900" width="2900" height="2700"/></clipPath>')
    svg = f"""
<rect x="-900" y="-900" width="2900" height="1780" fill="url(#{p}-wallHome)"/>
<rect x="2000" y="-900" width="2900" height="1780" fill="url(#{p}-wallWork)"/>
<rect x="-900" y="{FLOOR}" width="5800" height="900" fill="url(#{p}-ground)"/><rect x="-900" y="{FLOOR - 6}" width="5800" height="10" fill="#8d7bff" opacity=".35"/>
<ellipse cx="900" cy="300" rx="900" ry="420" fill="url(#{p}-lamp)"/>
<ellipse cx="{PX0 + 20}" cy="{FLOOR + 30}" rx="330" ry="40" fill="#7a3a6a" opacity=".55"/>
<g id="{p}-picsHome">{frames_home}</g>
<g id="{p}-picsWork">{frames_work}</g>
{desk(p, 2700, 1000)}
<path d="M2000 -900 L2000 180" stroke="#8d7bff" stroke-width="6" opacity=".45"/>
{bills}
{sparks}
{door(p, 1830, 200)}
<rect id="{p}-flare" x="1830" y="200" width="340" height="680" fill="#fff4d0" opacity="0" filter="url(#{p}-blur6)"/>
{fixed_chair(PX0)}
{person_g("A", "home", "sitting", PX0, op=1)}
<!-- the crossing: the same person in two drawings walking together, home clipped left of the door plane and work
     on the right; in the middle of the door the body is half hoodie, half shirt -->
<g clip-path="url(#{p}-clipHome)">{person_g("B", "home", "standing", PX0)}{person_g("E", "home", "standing", OX, flip=True)}</g>
<g clip-path="url(#{p}-clipWork)">{person_g("C", "work", "standing", PX0)}{person_g("D", "work", "standing", OX, flip=True)}</g>
<g id="{p}-veil" opacity="0"><rect x="{DOOR_X - 14}" y="200" width="28" height="680" fill="#fff4d0" opacity=".55" filter="url(#{p}-blur6)"/><rect x="{DOOR_X - 5}" y="200" width="10" height="680" fill="#fffbea"/></g>
<g id="{p}-orbsHome">{orbs_home}</g>
<g id="{p}-orbsWork">{orbs_work}</g>
<g transform="translate(1650 600) scale(.42)"><g id="{p}-sheetM"><g id="{p}-sheetW" opacity="0">{sheet_svg(p, fine_print=6)}
 <g transform="translate(140 175)"><g id="{p}-seal" opacity="0"><rect x="-80" y="-80" width="160" height="160" fill="none"/>
  <path d="{' '.join(('M' if j == 0 else 'L') + f'{(70 if j % 2 == 0 else 52) * math.cos(j * 3.14159 / 12):.1f} {(70 if j % 2 == 0 else 52) * math.sin(j * 3.14159 / 12):.1f}' for j in range(24))} Z" fill="{AMBER}" stroke="#fff3c8" stroke-width="4"/>
  <circle r="36" fill="none" stroke="#fff3c8" stroke-width="5"/></g></g></g></g></g>"""
    html = (text(f"{p}-t1", "JOB OFFER", "left:0;right:0;text-align:center;top:40px;font-size:96px;color:#eef1f7") +
            text(f"{p}-t2", "STRANGE PERK", "left:0;right:0;text-align:center;top:40px;font-size:96px;color:#ffd98a") +
            text(f"{p}-t3", "YOU FORGET EVERYTHING", "left:0;right:0;text-align:center;top:40px;font-size:100px;color:#bff4ff") +
            text(f"{p}-t4", '<i style="background:#ff4f7d;width:26px;height:26px"></i>PRESSURE', "left:520px;top:940px;font-size:66px;color:#ff9bb0", cls="pill2") +
            text(f"{p}-t5", '<i style="background:#ff4f7d;width:26px;height:26px"></i>CONFLICTS', "left:1140px;top:940px;font-size:66px;color:#ff9bb0", cls="pill2") +
            text(f"{p}-t6", "DON'T FOLLOW YOU HOME", "left:0;right:0;text-align:center;top:40px;font-size:100px;color:#ffd98a"))
    hide = lambda k, t: f'tl.fromTo("#{p}-w{k}",{{opacity:1}},{{opacity:0,duration:0.02,immediateRender:false}},{t:.2f});'
    show = lambda k, t: f'tl.fromTo("#{p}-w{k}",{{opacity:0}},{{opacity:1,duration:0.02,immediateRender:false}},{t:.2f});'
    walk = lambda k, t0, t1, dx: (f'tl.fromTo("#{p}-w{k}",{{x:0}},{{x:{dx / S:.0f},duration:{t1 - t0:.2f},ease:"power1.inOut",immediateRender:false}},{t0:.2f});'
                                  f'tl.fromTo("#{p}-fig{k}",{{y:0}},{{y:-10,duration:0.18,yoyo:true,repeat:{max(1, int((t1 - t0) / 0.18) - 1)},ease:"sine.inOut",immediateRender:false}},{t0:.2f});')
    js = f"""
  cam("#{p}-cam", [[0,0.86,1100,540],[{w_rise - 0.2:.2f},0.9,1120,540,"sine.inOut"],[{w_door - 0.3:.2f},0.7,1960,560],[{w_door + 0.25:.2f},0.7,2060,560,"none"],
       [{w_desk + 0.15:.2f},1.0,2900,540],[{w_back + 0.3:.2f},1.0,2880,540,"none"],[{w_exit - 0.25:.2f},0.75,2060,540],[{w_exit + 0.2:.2f},0.75,1980,540,"none"],
       [{t_forget + 0.6:.2f},0.8,2000,540],[{t_inside + 0.3:.2f},0.8,2000,540,"none"],[{t_pressure + 0.4:.2f},1.0,2560,540],
       [{t_dont - 0.2:.2f},1.06,2560,540,"sine.inOut"],[{t_home - 0.2:.2f},0.92,1170,540],[{dur:.2f},0.93,1170,540,"sine.inOut"]]);
  tl.fromTo("#{p}-picsHome > g",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.6,ease:"back.out(2)",stagger:0.12}},0.15);
  tl.fromTo("#{p}-orbsHome > g",{{opacity:0}},{{opacity:1,duration:0.4,stagger:0.1}},0.4);
"""
    for k in range(len(orb_home)):
        js += f'  tl.fromTo("#{p}-orbH{k}",{{y:0}},{{y:-14,duration:{1.1 + 0.17 * k:.2f},yoyo:true,repeat:{int(dur / (1.1 + 0.17 * k))},ease:"sine.inOut"}},0);\n'
    for k in range(len(orb_work)):
        js += f'  tl.fromTo("#{p}-orbW{k}",{{y:0}},{{y:-12,duration:{0.9 + 0.15 * k:.2f},yoyo:true,repeat:{int(dur / (0.9 + 0.15 * k))},ease:"sine.inOut"}},0);\n'
    js += f"""
  enter("#{p}-sheetW", {t_offer - 0.1:.2f}, 0.3); tl.fromTo("#{p}-sheetW",{{scale:0.4,rotation:-8,transformOrigin:"50% 50%"}},{{scale:1,rotation:0,duration:0.8,ease:"elastic.out(1,0.5)",immediateRender:false}},{t_offer - 0.1:.2f});
  look("#{p}-figA-eye", {t_offer:.2f}, 3);
  rise("#{p}-t1 span", {t_offer:.2f});
  tl.to("#{p}-t1 span",{{yPercent:-125,duration:0.35,ease:"power2.in"}},{t_perk - 0.35:.2f});
  rise("#{p}-t2 span", {t_perk:.2f});
  tl.fromTo("#{p}-seal",{{opacity:0,scale:2.6,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.35,ease:"power4.in",immediateRender:false}},{t_perk:.2f});
  tl.fromTo("#{p}-sheetW",{{y:0}},{{y:10,duration:0.08,yoyo:true,repeat:1,immediateRender:false}},{t_perk + 0.35:.2f});
  tl.fromTo("#{p}-seal",{{rotation:0}},{{rotation:14,duration:0.12,yoyo:true,repeat:3,ease:"sine.inOut",immediateRender:false}},{t_strange - 0.4:.2f});
  tl.to("#{p}-sheetM",{{y:-500,x:200,rotation:20,opacity:0,duration:0.5,ease:"power2.in"}},{w_rise - 0.3:.2f});
  tl.to("#{p}-t2 span",{{yPercent:-125,duration:0.35,ease:"power2.in"}},{w_door + 0.1:.2f});
  {hide("A", w_rise)} {show("B", w_rise)} {show("C", w_rise)} {walk("B", w_rise, w_desk, OX - PX0)} {walk("C", w_rise, w_desk, OX - PX0)} {hide("B", w_desk)}
  tl.fromTo("#{p}-veil",{{opacity:0}},{{opacity:0.85,duration:0.25,yoyo:true,repeat:1,ease:"sine.inOut"}},{w_door - 0.25:.2f});
  tl.to("#{p}-door-leaf",{{scaleX:0.12,transformOrigin:"0% 50%",duration:0.5,ease:"power2.inOut"}},{w_rise + 0.2:.2f});
  tl.to("#{p}-orbsHome",{{x:120,y:-75,duration:{w_door - w_rise:.2f},ease:"power1.inOut"}},{w_rise:.2f});
  tl.to("#{p}-orbsHome",{{opacity:0.22,duration:0.4}},{w_rise + 0.2:.2f});
  tl.fromTo("#{p}-flare",{{opacity:0}},{{opacity:0.45,duration:0.15,yoyo:true,repeat:1}},{w_door - 0.12:.2f});
  {hide("C", w_back)}
  tl.fromTo("#{p}-orbsWork > g",{{opacity:0,scale:0.3,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.5,ease:"back.out(2.4)",stagger:0.13}},{w_door + 0.25:.2f});
  tl.fromTo("#{p}-picsWork > g",{{scale:1}},{{scale:1.08,transformOrigin:"50% 50%",duration:0.2,yoyo:true,repeat:1,stagger:0.1,immediateRender:false}},{w_desk - 0.2:.2f});
  look("#{p}-figC-eye", {w_desk:.2f}, 3);
  {show("D", w_back)} {show("E", w_back)} {walk("D", w_back, w_chair, OX - PX0)} {walk("E", w_back, w_chair, OX - PX0)} {hide("D", w_chair)}
  tl.fromTo("#{p}-veil",{{opacity:0}},{{opacity:0.85,duration:0.3,yoyo:true,repeat:1,ease:"sine.inOut",immediateRender:false}},{w_exit - 0.3:.2f});
  tl.to("#{p}-orbsWork",{{y:-30,duration:{w_exit - w_back:.2f},ease:"power1.inOut"}},{w_back:.2f});
  tl.fromTo("#{p}-flare",{{opacity:0}},{{opacity:0.6,duration:0.15,yoyo:true,repeat:1,immediateRender:false}},{w_exit - 0.12:.2f});
  tl.to("#{p}-orbsWork > g",{{scale:1.7,opacity:0,transformOrigin:"50% 50%",duration:0.45,ease:"power2.out",stagger:0.07}},{t_forget:.2f});
  rise("#{p}-t3 span", {t_forget:.2f});
  {hide("E", w_chair + 0.05)} {show("A", w_chair + 0.05)}
  tl.fromTo("#{p}-figA",{{y:0}},{{y:10,duration:0.12,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{w_chair + 0.05:.2f});
  tl.to("#{p}-orbsHome",{{opacity:1,duration:0.45}},{w_chair - 0.1:.2f});
  tl.to("#{p}-orbsHome",{{x:0,y:0,duration:{w_chair - w_exit:.2f},ease:"power1.inOut"}},{w_exit + 0.1:.2f});
  tl.fromTo("#{p}-picsWork > g",{{opacity:1}},{{opacity:0.55,duration:0.2,yoyo:true,repeat:1,stagger:0.08,immediateRender:false}},{t_inside - 0.2:.2f});
  tl.to("#{p}-t3 span",{{yPercent:-125,duration:0.35,ease:"power2.in"}},{t_pressure - 0.4:.2f});
  rise("#{p}-t4 span", {t_pressure:.2f});
"""
    for k in range(5):
        js += (f'  enter("#{p}-bill{k}", {t_pressure + 0.1 + k * 0.22:.2f}, 0.1); tl.fromTo("#{p}-bill{k}",{{y:-900,rotation:{(-1) ** k * 30}}},{{y:0,rotation:0,duration:0.6,ease:"bounce.out",immediateRender:false}},{t_pressure + 0.1 + k * 0.22:.2f});\n')
    js += f"""
  tl.fromTo("#{p}-bill0, #{p}-bill1, #{p}-bill2, #{p}-bill3, #{p}-bill4",{{x:0}},{{x:-4,duration:0.07,yoyo:true,repeat:5,ease:"none",immediateRender:false}},{t_work:.2f});
  rise("#{p}-t5 span", {t_conflicts:.2f});
"""
    for k in range(5):
        js += (f'  tl.fromTo("#{p}-spark{k}",{{opacity:0,scale:0.2,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.35,ease:"back.out(3)",immediateRender:false}},{t_conflicts + k * 0.12:.2f});\n'
               f'  tl.fromTo("#{p}-spark{k}",{{rotation:0}},{{rotation:{(-1) ** k * 25},duration:0.1,yoyo:true,repeat:5,ease:"none",immediateRender:false}},{t_conflicts + 0.35 + k * 0.12:.2f});\n')
    js += f"""
  tl.to(["#{p}-t4 span","#{p}-t5 span"],{{yPercent:-125,duration:0.35,ease:"power2.in"}},{t_dont - 0.35:.2f});
  tl.to("#{p}-door-leaf",{{scaleX:1,transformOrigin:"0% 50%",duration:0.3,ease:"power3.in"}},{t_dont - 0.2:.2f});
  tl.to("#{p}-spark0, #{p}-spark4",{{x:-70,duration:0.15,yoyo:true,repeat:1,ease:"power2.in"}},{t_dont + 0.1:.2f});
  tl.to("#{p}-bill0, #{p}-bill1, #{p}-bill2, #{p}-bill3, #{p}-bill4, #{p}-spark0, #{p}-spark1, #{p}-spark2, #{p}-spark3, #{p}-spark4",{{opacity:0,duration:0.4}},{t_home - 0.5:.2f});  // they stay on the other side: nothing peeks over the edge at the end
  rise("#{p}-t6 span", {t_dont:.2f}, 0.9);
  look("#{p}-figA-eye", {t_home:.2f}, 0);
""" + "".join(figure_idle(f"{p}-fig{k}", dur) for k in "ABCDE")
    return comp(p, dur, svg, html, FIGURE_JS + js, extra, seed=5)


# ---------------------------------------------------------------- opening 4: who has the power to get inside your mind?
def opening_4():
    SC, SG = "opening", 4
    p = "opening_4"
    start, dur = seg(SC, SG)
    t_question, t_who, t_get_inside, t_mind, t_lock, t_write, t_read, t_decide, t_reality, t_see = (
        2.1, 3.01, 4.48, 5.32, 6.35, 7.99, 9.2, 10.86, 11.73, 13.14)
    PX, PY, S = 380, 150, 3.0
    W = lambda lx, ly: (PX + lx * S, PY + ly * S)
    khx, khy = W(193, 90)                         # the single keyhole, at the center of the brain (BRAIN_SIDE already scaled by .82)
    KS = 0.6                                    # key scale; the tip (local 0,130) goes into the hole (keyhole local 0,-26 * .4)
    kx, ky = khx, khy - 10 - 130 * KS
    wx, wy = W(226, 54)                         # point written by the light
    eye_x, eye_y = W(257, 129)                        # eye
    RX0, RX1, RY0, RY1 = 1380, 1640, 330, 560   # reality picture
    rg = random.Random(4)
    hills = (f'<path d="M{RX0} {RY1} L{RX0 + 60} {RY0 + 140} L{RX0 + 120} {RY0 + 180} L{RX0 + 180} {RY0 + 110} L{RX1} {RY0 + 170} L{RX1} {RY1} Z" fill="#ff4fa3" opacity=".55"/>'
              f'<circle cx="{RX1 - 70}" cy="{RY0 + 70}" r="32" fill="#ffd98a"/>')
    extra = (f'<linearGradient id="{p}-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a1060"/><stop offset="1" stop-color="#ff4fa3" stop-opacity=".5"/></linearGradient>'
             f'<linearGradient id="{p}-scan" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#38e8a8" stop-opacity="0"/><stop offset=".7" stop-color="#38e8a8" stop-opacity=".3"/><stop offset=".9" stop-color="#bfffe8" stop-opacity=".8"/><stop offset="1" stop-color="#38e8a8" stop-opacity="0"/></linearGradient>'
             f'<clipPath id="{p}-clipBrain"><path transform="translate({PX} {PY}) scale({S}) translate(196 118) scale(.82) translate(-196 -118)" d="{BRAIN_SIDE}"/></clipPath>'
             f'<clipPath id="{p}-clipPic"><rect x="{RX0}" y="{RY0}" width="{RX1 - RX0}" height="{RY1 - RY0}" rx="10"/></clipPath>')
    svg = f"""
<ellipse cx="{PX + 205 * S:.0f}" cy="{PY + 262 * S:.0f}" rx="300" ry="24" fill="#05031a" opacity=".5"/>
<g transform="translate({PX} {PY}) scale({S})"><g id="{p}-fig">{person(p + "a", glow=p + "-glow")}</g></g>
<circle id="{p}-mem" cx="{khx:.0f}" cy="{khy:.0f}" r="70" fill="#ffd98a" opacity="0" filter="url(#{p}-blur6)"/>
{keyhole(p, "keyhole", 0.4, round(khx), round(khy), 0, lit=False)}
<g id="{p}-write" opacity="0"><path d="M{wx + 60:.0f} -60 C {wx + 60:.0f} 120 {wx + 10:.0f} 200 {wx:.0f} {wy:.0f}" fill="none" stroke="#9aa6d0" stroke-width="10" stroke-linecap="round"/>
 <path id="{p}-lightning" d="M{wx + 60:.0f} -60 C {wx + 60:.0f} 120 {wx + 10:.0f} 200 {wx:.0f} {wy:.0f}" fill="none" stroke="#7fe6ff" stroke-width="12" stroke-linecap="round" stroke-dasharray="70 600" stroke-dashoffset="70" filter="url(#{p}-glow)"/>
 <circle id="{p}-ring" cx="{wx:.0f}" cy="{wy:.0f}" r="30" fill="none" stroke="#7fe6ff" stroke-width="6"/></g>
<g clip-path="url(#{p}-clipBrain)"><rect id="{p}-sweep" x="{PX + 100 * S:.0f}" y="{PY:.0f}" width="120" height="{180 * S:.0f}" fill="url(#{p}-scan)" opacity="0"/></g>
<g id="{p}-real" opacity="0"><polygon points="{eye_x + 10:.0f},{eye_y - 6:.0f} {RX0},{RY0 + 20} {RX0},{RY1 - 20} {eye_x + 10:.0f},{eye_y + 6:.0f}" fill="#ff4fa3" opacity=".22"/>
 <rect x="{RX0}" y="{RY0}" width="{RX1 - RX0}" height="{RY1 - RY0}" rx="10" fill="url(#{p}-sky)"/>
 <g clip-path="url(#{p}-clipPic)"><g id="{p}-landscape">{hills}</g></g>
 <rect x="{RX0}" y="{RY0}" width="{RX1 - RX0}" height="{RY1 - RY0}" rx="10" fill="none" stroke="#ff4fa3" stroke-width="9" filter="url(#{p}-glow)"/></g>
{key_svg(p, "key", KS, round(kx), round(ky), 0)}"""
    lab = lambda k, txt, color, top: text(f"{p}-l{k}", f'<i style="background:{color};width:26px;height:26px"></i>{txt}', f"left:90px;top:{top}px;font-size:62px;color:{color}", cls="pill2")
    html = (text(f"{p}-t0", "ONE QUESTION", "left:0;right:0;text-align:center;top:60px;font-size:60px;color:#ffd98a;letter-spacing:.2em", cls="pill2") +
            text(f"{p}-t1", "WHO HAS THE POWER", "left:0;right:0;text-align:center;top:22px;font-size:84px;color:#eef1f7") +
            text(f"{p}-t2", "TO GET INSIDE YOUR MIND?", "left:0;right:0;text-align:center;top:122px;font-size:84px;color:#eef1f7") +
            lab(0, "LOCK AWAY", "#ffd27a", 330) + lab(1, "WRITE", "#7fe6ff", 440) + lab(2, "READ", "#7ff0c8", 550) + lab(3, "DECIDE", "#ff9bd0", 660))
    kdx, kdy = -520 / KS, -260 / KS
    js = f"""
  cam("#{p}-cam", [[0,1.0,960,560],[{t_get_inside - 0.2:.2f},1.0,960,560,"none"],[{t_mind + 0.5:.2f},1.25,{khx + 60:.0f},480],
       [{t_write:.2f},1.3,980,470,"sine.inOut"],[{t_reality - 0.3:.2f},1.22,1010,480],[{dur:.2f},1.12,1000,500,"sine.inOut"]]);
  pop("#{p}-fig", 0.2, 0.6, 0.8);
  rise("#{p}-t0 span", {t_question - 0.4:.2f});
  tl.to("#{p}-t0 span",{{yPercent:-125,duration:0.3,ease:"power2.in"}},{t_who - 0.3:.2f});
  rise("#{p}-t1 span", {t_who:.2f}); rise("#{p}-t2 span", {t_get_inside - 0.3:.2f});
  tl.to(["#{p}-t1 span","#{p}-t2 span"],{{yPercent:-125,duration:0.4,ease:"power2.in"}},{t_lock - 0.5:.2f});
  pop("#{p}-keyhole", {t_get_inside - 0.3:.2f}, 0.4, 0.6);
  enter("#{p}-key", {t_get_inside - 0.1:.2f}, 0.3);
  tl.fromTo("#{p}-key",{{x:{kdx:.0f},y:{kdy:.0f},rotation:-40,transformOrigin:"50% 82%"}},{{x:0,y:0,rotation:0,duration:0.9,ease:"power3.out",immediateRender:false}},{t_get_inside - 0.1:.2f});
  tl.to("#{p}-key",{{rotation:90,transformOrigin:"50% 82%",duration:0.35,ease:"back.out(2)"}},{t_mind:.2f});
  tl.to("#{p}-keyhole-hole > *",{{attr:{{fill:"#ffb23e"}},duration:0.15}},{t_mind + 0.2:.2f});
  tl.to("#{p}-key",{{rotation:0,transformOrigin:"50% 82%",duration:0.3,ease:"back.out(2)"}},{t_lock + 0.25:.2f});
  tl.to("#{p}-keyhole-hole > *",{{attr:{{fill:"#05031a"}},duration:0.15}},{t_lock + 0.45:.2f});
  tl.to("#{p}-key",{{opacity:0,y:-60,duration:0.5}},{t_lock + 0.8:.2f});
  tl.fromTo("#{p}a-brain",{{opacity:0.95}},{{opacity:1,duration:0.2}},{t_mind:.2f});
  look("#{p}a-eye", {t_get_inside:.2f}, -3); look("#{p}a-eye", {t_lock:.2f}, 0);
  tl.fromTo("#{p}-mem",{{opacity:0}},{{opacity:0.75,duration:0.4}},{t_lock - 0.2:.2f});
  tl.to("#{p}-mem",{{opacity:0.3,duration:0.5}},{t_lock + 0.5:.2f});
  tl.fromTo("#{p}-keyhole",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.18,duration:0.18,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{t_lock + 0.45:.2f});
  rise("#{p}-l0 span", {t_lock:.2f});
  enter("#{p}-write", {t_write - 0.3:.2f}, 0.3);
  tl.fromTo("#{p}-lightning",{{attr:{{"stroke-dashoffset":70}}}},{{attr:{{"stroke-dashoffset":-560}},duration:0.7,ease:"power1.in",repeat:2,repeatDelay:0.25}},{t_write - 0.1:.2f});
  tl.fromTo("#{p}-ring",{{scale:0.4,opacity:1,transformOrigin:"50% 50%"}},{{scale:3,opacity:0,duration:0.8,repeat:2,repeatDelay:0.15,ease:"power2.out",immediateRender:false}},{t_write + 0.55:.2f});
  rise("#{p}-l1 span", {t_write:.2f});
  tl.fromTo("#{p}-sweep",{{opacity:0,x:0}},{{opacity:1,x:{130 * S:.0f},duration:0.9,ease:"sine.inOut",yoyo:true,repeat:3}},{t_read - 0.1:.2f});
  rise("#{p}-l2 span", {t_read:.2f});
  enter("#{p}-real", {t_decide:.2f}, 0.4);
  tl.fromTo("#{p}-real",{{scale:0.6,transformOrigin:"0% 50%"}},{{scale:1,duration:0.7,ease:"elastic.out(1,0.6)",immediateRender:false}},{t_decide:.2f});
  rise("#{p}-l3 span", {t_decide:.2f});
  look("#{p}a-eye", {t_decide:.2f}, 3);
  tl.fromTo("#{p}-landscape",{{x:0}},{{x:-120,duration:0.5,ease:"power3.inOut",yoyo:true,repeat:1,immediateRender:false}},{t_reality:.2f});
  tl.to("#{p}-landscape path",{{attr:{{fill:"#38e8a8"}},duration:0.3}},{t_see:.2f});
  tl.to("#{p}-real rect",{{attr:{{stroke:"#38e8a8"}},duration:0.3}},{t_see:.2f});
""" + person_idle(p + "a", dur)
    return comp(p, dur, svg, html, js, extra, seed=4)


# ---------------------------------------------------------------- opening 6: real pieces
def _inside(pt, poly):
    x, y = pt
    c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def opening_6():
    SC, SG = "opening", 6
    p = "opening_6"
    start, dur = seg(SC, SG)
    t_science, t_done, t_pieces, t_but, t_pieces2, t_real = 0.37, 2.14, 2.57, 3.69, 4.17, 5.16
    S, TX, TY = 5.2, 960 - 192 * 5.2, 430 - 98 * 5.2
    shards = [[(116, 30), (190, 30), (178, 88), (116, 100)], [(190, 30), (268, 30), (268, 82), (226, 92), (178, 88)],
             [(116, 100), (178, 88), (168, 162), (116, 162)], [(178, 88), (226, 92), (216, 162), (168, 162)], [(226, 92), (268, 82), (268, 162), (216, 162)]]
    real_ids = (1, 2, 4)
    rg = random.Random(6)
    pts = []
    while len(pts) < 90:
        x, y = rg.uniform(124, 260), rg.uniform(40, 128)
        if ((x - 192) / 66) ** 2 + ((y - 84) / 44) ** 2 < 1 and all((x - a) ** 2 + (y - b) ** 2 > 40 for a, b in pts):
            pts.append((round(x, 1), round(y, 1)))
    extra = "".join(f'<clipPath id="{p}-cp{k}"><polygon points="{" ".join(f"{x},{y}" for x, y in c)}"/></clipPath>' for k, c in enumerate(shards))
    parts = ""
    for k, c in enumerate(shards):
        cx = sum(x for x, _ in c) / len(c); cy = sum(y for _, y in c) / len(c)
        dots = "".join(f'<circle class="n" cx="{x}" cy="{y}" r="1.5" fill="#ffb23e"/>' for x, y in pts if _inside((x, y), c)) if k in real_ids else ""
        parts += (f'<g id="{p}-shard{k}"><rect x="{cx - 50:.0f}" y="{cy - 50:.0f}" width="100" height="100" fill="none"/><g class="body" clip-path="url(#{p}-cp{k})">'
                   f'{brain_side(p + f"b{k}")}{dots}</g></g>')
    svg = f"""
<ellipse cx="960" cy="840" rx="380" ry="28" fill="#05031a" opacity=".45"/>
<g transform="translate({TX:.0f} {TY:.0f}) scale({S})"><g id="{p}-ghost" opacity="0" fill="none" stroke="#b9adff" stroke-width=".9" stroke-dasharray="2.5 2.5"><path d="{BRAIN_SIDE}"/><ellipse cx="150" cy="138" rx="27" ry="17"/></g>
<g id="{p}-brain">{parts}</g></g>"""
    html = (text(f"{p}-t1", "PIECES", "left:1040px;top:870px;font-size:124px;color:#eef1f7") +
            text(f"{p}-t2", "REAL", "left:0;width:1000px;text-align:right;top:870px;font-size:124px;color:#ffd98a"))
    js = f"""
  cam("#{p}-cam", [[0,0.95,960,520],[{t_pieces:.2f},1.0,960,520,"sine.inOut"],[{t_but + 0.3:.2f},1.03,960,520],[{dur:.2f},1.06,960,530,"sine.inOut"]]);
  pop("#{p}-brain", 0.1, 0.6, 0.9);
  tl.fromTo("#{p}-brain .n",{{opacity:0.15}},{{opacity:1,duration:0.18,repeat:9,yoyo:true,ease:"none",stagger:{{each:0.02,from:"random"}}}},{t_science:.2f});
  enter("#{p}-ghost", {t_done:.2f}, 0.4);
"""
    for k, c in enumerate(shards):
        cx = sum(x for x, _ in c) / len(c) - 192; cy = sum(y for _, y in c) / len(c) - 96
        n = math.hypot(cx, cy) or 1
        dx, dy = cx / n * 10, cy / n * 10
        js += f'  tl.to("#{p}-shard{k}",{{x:{dx:.1f},y:{dy:.1f},duration:0.7,ease:"power3.out"}},{t_done + 0.1:.2f});\n'
        if k not in real_ids:
            js += f'  tl.to("#{p}-shard{k} .body",{{opacity:0.12,duration:0.5}},{t_pieces:.2f});\n'
        else:
            js += (f'  tl.fromTo("#{p}-shard{k}",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.08,duration:0.25,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{t_pieces2 + 0.1 * k:.2f});\n'
                   f'  tl.to("#{p}-shard{k}",{{x:{dx * 0.5:.1f},y:{dy * 0.5:.1f},duration:0.9,ease:"elastic.out(1,0.5)"}},{t_real:.2f});\n')
    js += f"""  rise("#{p}-t1 span", {t_pieces:.2f}); rise("#{p}-t2 span", {t_real - 0.15:.2f});
  tl.fromTo("#{p}-brain .n",{{attr:{{r:1.5}}}},{{attr:{{r:2.4}},duration:0.3,yoyo:true,repeat:3,immediateRender:false}},{t_real:.2f});
"""
    return comp(p, dur, svg, html, js, extra, seed=6)


# ---------------------------------------------------------------- opening 7: the files opened one by one, each with a preview of its topic
def _prev_write(p):
    """Mouse in the isometric box with the light fiber (scenes-v4 M3). Local card box: 400 x 300 centered at 0,0."""
    return (f'<g transform="translate(0 22) scale(.33) translate(-960 -490)">{b4.box(p)}'
            f'<circle id="{p}-write-halo" cx="1060" cy="470" r="120" fill="url(#{p}-hg)" opacity="0"/>'
            f'<g transform="translate(900 700) scale(1.15)"><g id="{p}-write-mouse">{b4.mouse(p)}</g></g>'
            f'<path d="M1010 -120 C 1010 160 1040 300 1052 430" fill="none" stroke="#9aa6d0" stroke-width="14" stroke-linecap="round"/>'
            f'<path id="{p}-write-light" d="M1010 -120 C 1010 160 1040 300 1052 430" fill="none" stroke="#7fe6ff" stroke-width="16" stroke-linecap="round" stroke-dasharray="90 800" stroke-dashoffset="90" filter="url(#{p}-glow)"/>'
            f'<circle id="{p}-write-ring" cx="1052" cy="456" r="40" fill="none" stroke="#7fe6ff" stroke-width="8" opacity="0"/></g>')


def _prev_map(p):
    """Neuron network (scenes-v3 A) behind and the fruit fly (art2) in front."""
    network_s, _, _ = b2.network_rich(f"{p}-net", 11, n=80, prefix=p)
    network_s = network_s.replace(' opacity="0">', '>', 2)  # lobe and edges visible from the start
    return (f'<g transform="translate(-30 -10) scale(.46)"><g id="{p}-map-network">{network_s}</g></g>'
            f'<g transform="translate(70 62) scale(.62)"><g id="{p}-map-fly">{fly_rich(p + "-fruitfly", prefix=p)}</g></g>')


def _prev_read(p):
    """The head with the brain, the electrode and the monitor that reads the signals (scenes-v3 E)."""
    targets = [(84, -40), (140, -54), (128, 6), (76, 2)]
    targets_svg = "".join(f'<circle id="{p}-read-tgt{k}" cx="{x}" cy="{y}" r="13" fill="none" stroke="{CYAN}" stroke-width="4" opacity=".7"/>' for k, (x, y) in enumerate(targets))
    return (f'<g transform="translate(-338 -164) scale(1.22)">{person(p + "L", glow=p + "-glow")}'
            f'<rect x="150" y="34" width="34" height="20" rx="6" fill="{AMBER}" transform="rotate(-18 167 44)" filter="url(#{p}-glow)"/></g>'
            f'<path d="M-140 -112 C -40 -190 30 -150 44 -76" fill="none" stroke="#7a8cff" stroke-width="6" stroke-linecap="round"/>'
            f'<path id="{p}-read-signal" d="M-140 -112 C -40 -190 30 -150 44 -76" fill="none" stroke="#ffd23e" stroke-width="9" stroke-linecap="round" stroke-dasharray="26 200" stroke-dashoffset="0" filter="url(#{p}-glow)"/>'
            f'<rect x="40" y="-86" width="140" height="112" rx="12" fill="#1a1850" stroke="{LILAC}" stroke-width="5"/><rect x="50" y="-76" width="120" height="92" rx="6" fill="#0b1c40"/>{targets_svg}'
            f'<rect x="100" y="26" width="20" height="26" fill="#1a1850" stroke="{LILAC}" stroke-width="3"/><rect x="74" y="50" width="72" height="10" rx="5" fill="#1a1850" stroke="{LILAC}" stroke-width="3"/>'
            f'<g transform="translate(60 -64)"><g id="{p}-read-pointer"><path d="M0 0 L0 24 L7 18 L12 29 L18 26 L12 16 L22 16 Z" fill="#fff" stroke="#1a0f3a" stroke-width="2"/></g></g>')


def _prev_influence(p):
    """Phone with the feed scrolling (scenes-v3 C) and likes floating up."""
    post_colors = ["#2b2a80", "#7b2a6c", "#25427a", "#6b5b2a", "#2a6a6a"]
    cards = "".join(
        f'<g transform="translate(0 {k * 190})"><rect x="-150" y="-330" width="300" height="170" rx="20" fill="{post_colors[k % 5]}"/>'
        f'<circle cx="-100" cy="-290" r="22" fill="#eef1ff" opacity=".85"/><rect x="-66" y="-304" width="150" height="12" rx="6" fill="#eef1ff" opacity=".7"/><rect x="-66" y="-282" width="100" height="10" rx="5" fill="#eef1ff" opacity=".4"/>'
        f'<rect x="-130" y="-244" width="260" height="56" rx="12" fill="#000" opacity=".22"/><circle cx="-84" cy="-218" r="14" fill="#ffd23e"/><path d="M-60 -196 L-20 -236 L20 -204 L50 -226 L112 -196 Z" fill="#fff" opacity=".35"/>'
        f'<path d="M110 -176 c-8 -10 -22 -2 -14 8 l14 12 l14 -12 c8 -10 -6 -18 -14 -8 Z" fill="#ff4f7d" transform="translate(-10 -16)"/></g>' for k in range(9))
    heart = lambda x, y, s: f'<g transform="translate({x} {y}) scale({s})"><path d="M0 14 C -26 -4 -20 -26 0 -14 C 20 -26 26 -4 0 14 Z" fill="#ff4fa3" filter="url(#{p}-glow)"/></g>'
    return (f'<g transform="translate(-10 6) rotate(-7) scale(.34)"><rect x="-200" y="-400" width="400" height="800" rx="54" fill="#15133a" stroke="{LILAC}" stroke-width="10"/>'
            f'<rect x="-172" y="-364" width="344" height="728" rx="26" fill="#0e0c26"/><clipPath id="{p}-influence-cp"><rect x="-172" y="-364" width="344" height="728" rx="26"/></clipPath>'
            f'<g clip-path="url(#{p}-influence-cp)"><g id="{p}-influence-posts">{cards}</g></g></g>'
            f'<g id="{p}-influence-hearts">{heart(-120, 40, 1.6)}{heart(120, -20, 2.1)}{heart(130, 90, 1.3)}{heart(-130, -80, 1.2)}</g>')


def _prev_robot(p):
    """The evil robot: big robot head, red eyes."""
    return (f'<g transform="scale(2.5)"><g id="{p}-robot-head"><rect x="-46" y="-36" width="92" height="76" rx="14" fill="#2a0a1a" stroke="#ff4f7d" stroke-width="5"/>'
            f'<circle id="{p}-robot-eye1" cx="-18" cy="0" r="10" fill="#ff4f7d" filter="url(#{p}-glow)"/><circle id="{p}-robot-eye2" cx="18" cy="0" r="10" fill="#ff4f7d" filter="url(#{p}-glow)"/>'
            f'<path d="M-20 24 L-10 20 L0 24 L10 20 L20 24" fill="none" stroke="#ff4f7d" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M0 -36 L0 -50" stroke="#ff4f7d" stroke-width="5"/><circle cx="0" cy="-54" r="6" fill="#ff4f7d"/>'
            f'<rect x="-58" y="-10" width="12" height="26" rx="4" fill="#5a1030"/><rect x="46" y="-10" width="12" height="26" rx="4" fill="#5a1030"/></g></g>')


def opening_7():
    SC, SG = "opening", 7
    p = "opening_7"
    start, dur = seg(SC, SG)
    t_open, t_one, t_separate, t_already, t_fear, t_conclusion, t_uncomfortable, t_danger, t_not, t_robot = (
        2.41, 3.56, 4.84, 5.66, 7.92, 9.65, 10.39, 12.12, 13.23, 14.03)
    FX, RX, BY = [320, 760, 1200, 1640], 2200, 800
    opens = [t_open, t_open + 1.04, t_open + 2.08, t_open + 3.12]
    # (number, name, topic color, folder color, preview)
    files = [("1", "WRITE", "#7fe6ff", "#c9a46a", _prev_write(p)), ("2", "MAP", "#38e8a8", "#b99ae0", _prev_map(p)),
           ("3", "READ", "#ffd27a", "#c9a46a", _prev_read(p)), ("4", "INFLUENCE", "#ff7ac0", "#b99ae0", _prev_influence(p)),
           ("", "EVIL ROBOT", "#ff4f7d", "#8a3a4a", _prev_robot(p))]

    def folder(k, x):
        num, name, color, folder_color, prev = files[k]
        front = (f'<text x="0" y="-132" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="44" letter-spacing="8" fill="#2a1a0a" opacity=".85">FILE</text>'
                  f'<circle cx="0" cy="-62" r="54" fill="{color}" stroke="#2a1a0a" stroke-width="6"/>'
                  f'<text x="0" y="-36" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="84" fill="#1a0f2e">{num}</text>') if num else (
                  f'<g transform="translate(0 -92) scale(1.1)"><circle r="44" fill="none" stroke="#2a0a14" stroke-width="10"/><path d="M-31 -31 L31 31" stroke="#2a0a14" stroke-width="10"/></g>')
        return (f'<ellipse cx="{x}" cy="{BY + 8}" rx="190" ry="20" fill="#05031a" opacity=".55"/>'
                f'<ellipse id="{p}-g{k}" cx="{x}" cy="{BY + 4}" rx="230" ry="44" fill="{color}" opacity="0" filter="url(#{p}-blur6)"/>'
                f'<g transform="translate({x} {BY})"><g id="{p}-folder{k}" opacity="0"><rect x="-210" y="-480" width="420" height="560" fill="none"/>'
                f'<path d="M-150 -210 L-150 0 L150 0 L150 -210 L-24 -210 L-40 -240 L-140 -240 L-150 -226 Z" fill="{folder_color}" stroke="#05031a" stroke-width="3"/>'
                f'<g transform="translate(0 -320)"><g id="{p}-c{k}" opacity="0"><rect x="-200" y="-150" width="400" height="300" fill="none"/>'
                f'<circle r="230" fill="{color}" opacity=".18" filter="url(#{p}-blur40)"/>'
                f'<rect x="-200" y="-150" width="400" height="300" rx="20" fill="#0d0b2c"/>'
                f'<g clip-path="url(#{p}-cc)">{prev}</g>'
                f'<rect x="-200" y="-150" width="400" height="300" rx="20" fill="none" stroke="{color}" stroke-width="7" filter="url(#{p}-glow)"/></g></g>'
                f'<g id="{p}-front{k}"><path d="M-158 -190 L158 -190 L150 0 L-150 0 Z" fill="{folder_color}" stroke="#05031a" stroke-width="3"/>'
                f'<path d="M-158 -190 L158 -190 L157 -180 L-157 -180 Z" fill="#fff" opacity=".3"/>{front}</g>'
                f'<text x="0" y="78" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="50" letter-spacing="3" fill="{color}" stroke="#05031a" stroke-width="8" paint-order="stroke">{name}</text></g></g>')
    folders = "".join(folder(k, x) for k, x in enumerate(FX)) + folder(4, RX)
    cabinets = "".join(f'<g opacity=".5"><rect x="{x}" y="120" width="250" height="500" rx="8" fill="#1c1660" stroke="#4a46b0" stroke-width="4"/>'
                       + "".join(f'<rect x="{x + 20}" y="{140 + d * 158}" width="210" height="138" rx="6" fill="#241e78" stroke="#3a3690" stroke-width="3"/>'
                                 f'<rect x="{x + 95}" y="{196 + d * 158}" width="60" height="14" rx="7" fill="#8d7bff" opacity=".7"/>' for d in range(3)) + '</g>'
                       for x in range(-260, 2800, 300))
    extra = (b4.box_grad(p, "c") + fly_defs(p) +
             f'<radialGradient id="{p}-hg"><stop offset="0" stop-color="#bff4ff" stop-opacity=".95"/><stop offset="1" stop-color="#7fe6ff" stop-opacity="0"/></radialGradient>'
             f'<radialGradient id="{p}-lobe" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="#3b5bff" stop-opacity=".28"/><stop offset="1" stop-color="#3b5bff" stop-opacity=".04"/></radialGradient>'
             f'<clipPath id="{p}-cc"><rect x="-200" y="-150" width="400" height="300" rx="20"/></clipPath>'
             f'<linearGradient id="{p}-desk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a1d70"/><stop offset="1" stop-color="#0e0a30"/></linearGradient>'
             f'<radialGradient id="{p}-deskLight"><stop offset="0" stop-color="#ffe9a8" stop-opacity=".3"/><stop offset="1" stop-color="#ffe9a8" stop-opacity="0"/></radialGradient>')
    svg = f"""
<ellipse cx="1260" cy="560" rx="1400" ry="560" fill="url(#{p}-deskLight)"/>{cabinets}
<polygon points="-700,1400 3200,1400 2700,640 -200,640" fill="url(#{p}-desk)" stroke="#5a4ad0" stroke-width="4"/>
<path d="M-200 640 L2700 640" stroke="#8d7bff" stroke-width="6" filter="url(#{p}-glow)"/>
{folders}"""
    html = (text(f"{p}-t1", '<i style="background:#38e8a8;width:26px;height:26px"></i>ALREADY HAPPENED', "left:310px;width:800px;text-align:center;top:190px;font-size:62px;color:#7ff0c8", cls="pill2") +
            text(f"{p}-t2", '<i style="background:#ff4f7d;width:26px;height:26px"></i>JUST FEAR', "left:1380px;width:520px;text-align:center;top:190px;font-size:58px;color:#ff9bb0", cls="pill2") +
            text(f"{p}-t3", "THE DANGER", "left:0;right:0;text-align:center;top:40px;font-size:124px;color:#eef1f7"))
    ks = [[0, 1.0, 980, 560], [opens[0] - 0.45, 1.0, 980, 560, "none"]]
    for k in range(4):
        ks.append([opens[k] + 0.15, 1.3, FX[k], 570])
        if k < 3:
            ks.append([opens[k + 1] - 0.45, 1.3, FX[k], 570, "none"])
    ks += [[opens[3] + 0.55, 1.3, FX[3], 570, "none"], [opens[3] + 1.2, 0.8, 1290, 540], [t_conclusion - 0.2, 0.8, 1290, 540, "none"],
           [t_uncomfortable + 0.1, 1.3, 2120, 570], [dur, 1.36, 2100, 560, "sine.inOut"]]
    ks_js = "[" + ",".join("[" + ",".join(f'"{v}"' if isinstance(v, str) else f"{v:.2f}" for v in kf) + "]" for kf in ks) + "]"
    js = f"""
  cam("#{p}-cam", {ks_js});
"""
    for k in range(4):
        t0 = 0.25 + k * 0.28
        js += (f'  enter("#{p}-folder{k}", {t0:.2f}, 0.1); tl.fromTo("#{p}-folder{k}",{{y:-760,rotation:{(-1) ** k * 7}}},{{y:0,rotation:0,duration:0.75,ease:"bounce.out",immediateRender:false}},{t0:.2f});\n')
    for k in range(5):
        t_k = opens[k] if k < 4 else t_fear - 0.05
        js += (f'  tl.fromTo("#{p}-front{k}",{{y:0}},{{y:14,duration:0.16,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{t_k:.2f});\n'
               f'  tl.fromTo("#{p}-c{k}",{{opacity:0,y:200,scale:0.45,transformOrigin:"50% 100%"}},{{opacity:1,y:0,scale:1,duration:0.75,ease:"back.out(1.6)",immediateRender:false}},{t_k:.2f});\n'
               f'  tl.fromTo("#{p}-g{k}",{{opacity:0}},{{opacity:0.6,duration:0.4}},{t_k + 0.1:.2f});\n')
    js += f"""
  tl.fromTo("#{p}-write-light",{{attr:{{"stroke-dashoffset":90}}}},{{attr:{{"stroke-dashoffset":-700}},duration:0.6,ease:"power1.in",repeat:3,repeatDelay:0.15}},{opens[0] + 0.25:.2f});
  tl.fromTo("#{p}-write-halo",{{opacity:0}},{{opacity:0.9,duration:0.3,yoyo:true,repeat:5,ease:"sine.inOut"}},{opens[0] + 0.75:.2f});
  tl.fromTo("#{p}-write-ring",{{opacity:0.9,scale:0.5,svgOrigin:"1052 456"}},{{opacity:0,scale:5,svgOrigin:"1052 456",duration:0.9,repeat:2,ease:"power2.out"}},{opens[0] + 0.75:.2f});
  tl.fromTo("#{p}-write-mouse",{{y:0}},{{y:-6,duration:0.3,yoyo:true,repeat:5,ease:"sine.inOut"}},{opens[0] + 0.8:.2f});
  tl.fromTo("#{p}-map-network .g2 circle",{{opacity:0.3}},{{opacity:1,duration:0.16,repeat:13,yoyo:true,ease:"none",stagger:{{each:0.03,from:"random"}}}},{opens[1] + 0.2:.2f});
  tl.fromTo("#{p}-fruitfly-wings",{{scaleY:1,transformOrigin:"50% 100%"}},{{scaleY:0.55,transformOrigin:"50% 100%",duration:0.05,repeat:39,yoyo:true,ease:"none"}},{opens[1] + 0.2:.2f});
  tl.fromTo("#{p}-map-fly",{{y:0}},{{y:-10,duration:0.5,repeat:5,yoyo:true,ease:"sine.inOut"}},{opens[1] + 0.2:.2f});
  tl.fromTo("#{p}-read-signal",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-226}},duration:0.55,repeat:7,ease:"none"}},{opens[2] + 0.2:.2f});
  tl.to("#{p}-read-pointer",{{keyframes:{{x:[0,24,24,80,80,68,68,16],y:[0,24,24,10,10,70,70,66],easeEach:"power2.inOut"}},duration:2.6,ease:"none"}},{opens[2] + 0.3:.2f});
  tl.fromTo("#{p}-read-tgt0, #{p}-read-tgt1, #{p}-read-tgt2, #{p}-read-tgt3",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.5,transformOrigin:"50% 50%",duration:0.25,yoyo:true,repeat:1,stagger:0.62,ease:"back.out(3)",immediateRender:false}},{opens[2] + 0.6:.2f});
  tl.fromTo("#{p}-influence-posts",{{y:0}},{{y:-950,duration:3.4,ease:"power1.inOut"}},{opens[3] + 0.2:.2f});
  tl.fromTo("#{p}-influence-hearts > g",{{y:40,opacity:0}},{{y:-60,opacity:1,duration:0.9,stagger:0.25,ease:"power2.out",repeat:1,repeatDelay:0.2}},{opens[3] + 0.4:.2f});
  rise("#{p}-t1 span", {opens[3] + 0.9:.2f});
  enter("#{p}-folder4", {t_fear - 0.45:.2f}, 0.1); tl.fromTo("#{p}-folder4",{{y:-760,rotation:-8}},{{y:0,rotation:0,duration:0.6,ease:"bounce.out",immediateRender:false}},{t_fear - 0.45:.2f});
  rise("#{p}-t2 span", {t_fear:.2f});
  tl.fromTo("#{p}-folder4",{{rotation:0,transformOrigin:"50% 100%"}},{{rotation:2.5,duration:0.08,yoyo:true,repeat:11,ease:"none",immediateRender:false}},{t_fear + 0.8:.2f});
  tl.fromTo("#{p}-robot-eye1, #{p}-robot-eye2",{{opacity:1}},{{opacity:0.25,duration:0.12,yoyo:true,repeat:9,ease:"steps(1)"}},{t_fear + 0.6:.2f});
  tl.to(["#{p}-t1 span","#{p}-t2 span"],{{yPercent:-125,duration:0.4,ease:"power2.in"}},{t_conclusion - 0.3:.2f});
  tl.fromTo("#{p}-robot-head",{{x:-3}},{{x:3,duration:0.05,yoyo:true,repeat:13,ease:"none",immediateRender:false}},{t_uncomfortable:.2f});
  rise("#{p}-t3 span", {t_danger - 0.1:.2f});
  tl.to("#{p}-folder4",{{y:620,rotation:16,opacity:0,duration:0.8,ease:"power3.in"}},{t_not:.2f});
  tl.to("#{p}-g4",{{opacity:0,duration:0.5}},{t_not:.2f});
"""
    return comp(p, dur, svg, html, js, extra, seed=7)


# ---------------------------------------------------------------- opening 8: who has the key? (corridor F)
def corridor(p):
    """Server corridor from scene F (scenes-v3/build2.py::scene_F2), with prefixed ids. Vanishing point at (960, 500)."""
    extra = (f'<radialGradient id="{p}-end" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#9af0ff" stop-opacity=".9"/><stop offset=".4" stop-color="#6a8cff" stop-opacity=".4"/><stop offset="1" stop-color="#6a8cff" stop-opacity="0"/></radialGradient>'
             f'<linearGradient id="{p}-ceiling" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0828"/><stop offset="1" stop-color="#1c1a58"/></linearGradient>'
             f'<linearGradient id="{p}-ground" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#06051a"/><stop offset="1" stop-color="#26246a"/></linearGradient>'
             f'<linearGradient id="{p}-rack" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1a1856"/><stop offset="1" stop-color="#2c2a88"/></linearGradient>')

    def projector(side):
        def f(u, v):
            xb = 960 + side * 960; xf = 960 + side * 118
            yt0, yb0 = -40, 1120; yt1, yb1 = 410, 600
            x = xb + (xf - xb) * u
            yt = yt0 + (yt1 - yt0) * u; yb = yb0 + (yb1 - yb0) * u
            return x, yt + (yb - yt) * v
        return f
    parts, leds, cables = [], [], []
    for side in (-1, 1):
        q_ = projector(side)
        us = [1 - 1 / (1 + 0.5 * i) for i in range(0, 26)]
        for i in range(len(us) - 1):
            a, bb = us[i], us[i + 1]
            q = [q_(a, 0.03), q_(bb, 0.03), q_(bb, 0.97), q_(a, 0.97)]
            pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in q)
            parts.append(f'<polygon points="{pts}" fill="url(#{p}-rack)" stroke="#5a5ad0" stroke-width="3"/><polygon points="{pts}" fill="#05031a" opacity="{0.18 + 0.7 * (a ** 0.8):.2f}"/>')
            x1, y1 = q_(a, 0.025); x2, y2 = q_(bb, 0.025)
            cables.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#ff4fa3" stroke-width="{max(2, 8 * (1 - a)):.1f}" opacity=".7"/>')
            for r in range(11):
                for c in range(3):
                    uu = a + (bb - a) * (0.18 + 0.3 * c); vv = 0.10 + 0.08 * r
                    x, y = q_(uu, vv)
                    size = max(2.2, 20 * (1 - uu) ** 1.3)
                    color = CYAN if (i + r + c) % 4 else (AMBER if (r + c) % 2 else MAGENTA)
                    leds.append(f'<rect class="led" x="{x - size:.1f}" y="{y - size * 0.5:.1f}" width="{size * 2:.1f}" height="{size:.1f}" rx="{size * 0.2:.1f}" fill="{color}"/>')
    strips = "".join(f'<polygon points="{960 + dx * 0.06:.0f},430 {960 - dx * 0.06:.0f},430 {960 - dx:.0f},-40 {960 + dx:.0f},-40" fill="#cfe8ff" opacity=".16"/>' for dx in (170, 520, 880))
    guides = "".join(f'<line x1="{x}" y1="1120" x2="{960 + (x - 960) * 0.12:.0f}" y2="590" stroke="#6ad8ff" stroke-width="3" opacity=".22"/>' for x in (260, 560, 960, 1360, 1660))
    svg = (f'<polygon points="0,-40 1920,-40 1080,430 840,430" fill="url(#{p}-ceiling)"/><polygon points="0,1120 1920,1120 1080,590 840,590" fill="url(#{p}-ground)"/>'
           f'<ellipse id="{p}-haze" cx="960" cy="510" rx="520" ry="330" fill="url(#{p}-end)"/>{strips}<g>{"".join(parts)}</g><g>{guides}</g>'
           f'<rect x="905" y="470" width="110" height="120" rx="8" fill="#cfeaff" opacity=".85" filter="url(#{p}-glow)"/><g>{"".join(cables)}</g><g id="{p}-leds">{"".join(leds)}</g>')
    return svg, extra


def opening_8():
    SC, SG = "opening", 8
    p = "opening_8"
    start, dur = seg(SC, SG)
    t_hold, t_question, t_who, t_key = 0.33, 1.02, 2.33, 2.66
    hall, extra = corridor(p)
    svg = hall + f'<g id="{p}-door">{keyhole(p, "keyhole", 0.5, 960, 530, 1, lit=False)}</g>'
    fixed = (f'<linearGradient id="{p}-stripe" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05041a" stop-opacity="0"/><stop offset="1" stop-color="#05041a" stop-opacity=".85"/></linearGradient>'
            f'<radialGradient id="{p}-halo"><stop offset="0" stop-color="#ffb23e" stop-opacity=".55"/><stop offset="1" stop-color="#ffb23e" stop-opacity="0"/></radialGradient>'
            f'<circle id="{p}-hk" cx="1440" cy="400" r="330" fill="url(#{p}-halo)" opacity="0"/>'
            f'<rect x="0" y="760" width="1920" height="320" fill="url(#{p}-stripe)"/>{key_svg(p, "key", 2.4, 1440, 260, 0)}')
    html = (text(f"{p}-t1", "HOLD ON TO ONE QUESTION", "left:0;right:0;text-align:center;top:60px;font-size:60px;color:#ffd98a;letter-spacing:.2em", cls="pill2") +
            text(f"{p}-t2", "WHO HAS THE KEY?", "left:0;right:0;text-align:center;top:850px;font-size:140px;color:#eef1f7"))
    js = f"""
  cam("#{p}-cam", [[0,1.5,960,525],[{dur:.2f},2.9,960,530,"sine.inOut"]]);
  tl.fromTo("#{p}-haze",{{opacity:0.7}},{{opacity:1,duration:0.8,repeat:5,yoyo:true,ease:"sine.inOut"}},0);
  tl.fromTo("#{p}-leds .led",{{opacity:1}},{{opacity:0.15,duration:0.18,repeat:14,yoyo:true,ease:"steps(1)",stagger:{{each:0.0035,from:"random"}}}},0.1);
  rise("#{p}-t1 span", {t_hold:.2f});
  tl.to("#{p}-t1 span",{{yPercent:-125,duration:0.35,ease:"power2.in"}},{t_who - 0.45:.2f});
  rise("#{p}-t2 span", {t_who:.2f}, 0.9);
  tl.to("#{p}-keyhole-hole > *",{{attr:{{fill:"#ffb23e"}},duration:0.2}},{t_key:.2f});
  enter("#{p}-hk", {t_key - 0.1:.2f}, 0.5);
  enter("#{p}-key", {t_key - 0.15:.2f}, 0.2);
  tl.fromTo("#{p}-key",{{scale:0.3,rotation:-120,transformOrigin:"50% 30%"}},{{scale:1,rotation:0,duration:1.1,ease:"elastic.out(1,0.45)",immediateRender:false}},{t_key - 0.15:.2f});
  tl.fromTo("#{p}-key",{{rotation:0}},{{rotation:8,duration:0.9,yoyo:true,repeat:1,ease:"sine.inOut",immediateRender:false}},{t_key + 1.0:.2f});
"""
    return comp(p, dur, svg, html, js, extra, fixed=fixed, background=("#1c1450", "#0d0a30", "#05041a"), seed=21)


SCENE_FNS = [("opening", 4, opening_4), ("opening", 6, opening_6), ("opening", 7, opening_7), ("opening", 8, opening_8),
            ("contract", 0, contract_0), ("contract", 2, contract_2), ("contract", 3, contract_3), ("contract", 4, contract_4), ("contract", 5, contract_5)]
SCENES = [(f.__name__, f, seg(c, s)[1]) for c, s, f in SCENE_FNS]
SEG_MAP = {(c, s): f.__name__ for c, s, f in SCENE_FNS}

if __name__ == "__main__":
    print(write_scenes(SCENES, HERE))
