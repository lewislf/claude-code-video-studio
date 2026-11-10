"""v4 scenes: the mouse block (the mouse and box art comes from mouse-art, approved).

  python3 build4.py     # generates compositions/*.html and index.html (scenes in sequence, no audio)

Scenes (duration = narration clip in film/assets/voice/slots.json):
  M2 opening 2 "But that shock never happened in that box."   M3 opening 3 "With light."
  M4 writing 1 engram                             M5 writing 3 two boxes and the shock
  M6 writing 4 fear in the calm box              M7 writing 6 mouse with an optical fiber
  M8 closing 7 "It only felt fear."
"""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.join(HERE, "../scenes-v3")
sys.path.insert(0, V3)
import build2 as b2
from build2 import composition2
from build import CYAN, MAGENTA, AMBER, MINT, LILAC
from art2 import brain_side, BRAIN_SIDE

MOUSE_SVG = open(os.path.join(HERE, "../mouse-art/art/mouse.svg.part")).read()
D = json.load(open(os.path.join(HERE, "../film/assets/voice/slots.json")))
DUR = {"M2": D["opening"][2][1], "M3": D["opening"][3][1], "M4": D["writing"][1][1], "M5": D["writing"][3][1],
       "M6": D["writing"][4][1], "M7": D["writing"][6][1], "M8": D["closing"][7][1]}
PINK, PINK_E = "#ff9fa8", "#d8657a"


def mouse(p):
    s = MOUSE_SVG
    for k in ("gBody", "gHead", "cpEye"):
        s = s.replace(k, f"{p}-{k}")
    return s.replace('id="r', f'id="{p}-r').replace('href="#r', f'href="#{p}-r')


def box_grad(p, t):
    c = {"c": ("#4a3aa6", "#6a4fd0", "#3a2a8c", "#2a1d70", "#2a6fa8", "#1a3b86"),
         "v": ("#a01a48", "#d1224f", "#7a1236", "#5a0e28", "#8a1c40", "#5a1030")}[t]
    return (f'<linearGradient id="{p}-wallL{t}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c[0]}"/><stop offset="1" stop-color="{c[1]}"/></linearGradient>'
            f'<linearGradient id="{p}-wallR{t}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c[2]}"/><stop offset="1" stop-color="{c[3]}"/></linearGradient>'
            f'<linearGradient id="{p}-floor{t}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c[4]}"/><stop offset="1" stop-color="{c[5]}"/></linearGradient>')


def box(p, t="c", k=""):
    """Isometric box from the approved illustration (floor center at 960,620). t: c calm, v red. k: id suffix."""
    edge = "#3be0ff" if t == "c" else "#ff4f7d"
    return (f'<g id="{p}-cx{k}"><polygon points="540,620 960,410 960,150 540,360" fill="url(#{p}-wallL{t})"/>'
            f'<polygon points="960,410 1380,620 1380,360 960,150" fill="url(#{p}-wallR{t})"/>'
            f'<polygon points="960,410 1380,620 960,830 540,620" fill="url(#{p}-floor{t})"/>'
            f'<g fill="none" stroke-linecap="round" stroke-linejoin="round" filter="url(#{p}-glow)"><polyline points="540,360 540,620 960,830 1380,620 1380,360" stroke="{edge}" stroke-width="7" opacity=".9"/>'
            f'<path d="M540 360 L960 150 L1380 360 M960 150 L960 410" stroke="{"#8d7bff" if t == "c" else "#ff9bb0"}" stroke-width="5" opacity=".7"/></g></g>')


def bolt(x, y, s=1, color=AMBER):
    return f'<g transform="translate({x} {y}) scale({s})"><path d="M10 -70 L-26 6 L-4 6 L-14 64 L30 -14 L6 -14 Z" fill="{color}" stroke="#fff6c8" stroke-width="3" stroke-linejoin="round"/></g>'


def prep(p, js):
    return js.replace("@P@", p)


# ---------------------------------------------------------------- M2: the shock never happened there
def scene_M2():
    p = "M2"
    extra = box_grad(p, "c")
    svg = f"""{box(p)}
<g transform="translate(870 716) scale(.9)"><g id="{p}-mouseW"><g id="{p}-bob">{mouse(p)}</g></g></g>
<g id="{p}-bubble" opacity="0"><circle cx="1280" cy="470" r="22" fill="#eef1f7" opacity=".85"/><circle cx="1330" cy="420" r="32" fill="#eef1f7" opacity=".9"/><ellipse cx="1460" cy="300" rx="150" ry="112" fill="#eef1f7" opacity=".95"/>
<g transform="translate(1460 300)">{bolt(0, 0, 1.2)}</g></g>
<g id="{p}-x" opacity="0" stroke="#ff4f7d" stroke-width="22" stroke-linecap="round" filter="url(#{p}-glow)"><path d="M1370 210 L1550 390 M1550 210 L1370 390"/></g>"""
    html = f'<div id="{p}-t" class="title" style="left:0;right:0;text-align:center;top:870px;font-size:92px">That shock never happened in that box</div>'
    js = """
  tl.fromTo("#@P@-cx",{opacity:0},{opacity:1,duration:0.8},0);
  tl.fromTo("#@P@-mouseW",{x:-300,opacity:0},{x:0,opacity:1,duration:1.4,ease:"power2.out"},0.3);
  tl.fromTo("#@P@-bob",{y:0},{y:-6,duration:0.9,repeat:8,yoyo:true,ease:"sine.inOut"},1.7);
  tl.fromTo("#@P@-rEyelid",{y:-52},{y:0,duration:0.09,repeat:1,yoyo:true,immediateRender:false},3.3);
  tl.fromTo("#@P@-bubble",{opacity:0,scale:0.3,svgOrigin:"1260 500"},{opacity:1,scale:1,svgOrigin:"1260 500",duration:0.6,ease:"back.out(2)"},2.6);
  tl.fromTo("#@P@-x",{opacity:0,scale:2,svgOrigin:"1460 300"},{opacity:1,scale:1,svgOrigin:"1460 300",duration:0.3,ease:"back.out(3)"},5.2);
  tl.fromTo("#@P@-t",{opacity:0,y:30},{opacity:1,y:0,duration:0.7,ease:"power3.out"},4.6);
  tl.fromTo("#@P@-cam",{scale:1,svgOrigin:"960 560"},{scale:1.12,svgOrigin:"960 560",duration:8.3,ease:"none"},0);
"""
    return svg_wrap(p, svg, html, js, extra)


def svg_wrap(p, svg, html, js, extra, background=("#3a1d7a", "#1a1050", "#0b0a24"), seed=3):
    body = f'<g id="{p}-cam">{svg}</g>'
    return composition2(p, DUR[p], body, html, prep(p, js), extra, background=background, seed=seed)


# ---------------------------------------------------------------- M3: with light
def scene_M3():
    p = "M3"
    extra = box_grad(p, "c") + f'<radialGradient id="{p}-hg"><stop offset="0" stop-color="#bff4ff" stop-opacity=".95"/><stop offset="1" stop-color="#7fe6ff" stop-opacity="0"/></radialGradient><linearGradient id="{p}-beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7fe6ff" stop-opacity=".9"/><stop offset="1" stop-color="#7fe6ff" stop-opacity=".1"/></linearGradient>'
    svg = f"""{box(p)}
<circle id="{p}-halo" cx="1060" cy="470" r="110" fill="url(#{p}-hg)" opacity="0"/>
<g transform="translate(900 700) scale(1.15)"><g id="{p}-mouseW"><g id="{p}-bob">{mouse(p)}</g></g></g>
<path id="{p}-cable" d="M1010 -40 C 1010 160 1040 300 1052 430" fill="none" stroke="#9aa6d0" stroke-width="12" stroke-linecap="round" stroke-dasharray="700" stroke-dashoffset="700"/>
<path id="{p}-light" d="M1010 -40 C 1010 160 1040 300 1052 430" fill="none" stroke="#7fe6ff" stroke-width="12" stroke-linecap="round" stroke-dasharray="60 700" stroke-dashoffset="60" filter="url(#{p}-glow)" opacity="0"/>
<g id="{p}-rings" fill="none" stroke="#7fe6ff" stroke-width="6" opacity="0"><circle id="{p}-a1" cx="1052" cy="456" r="40"/><circle id="{p}-a2" cx="1052" cy="456" r="40"/></g>"""
    html = f'<div id="{p}-t" class="title" style="left:0;right:0;text-align:center;top:880px;font-size:120px;color:#bff4ff">With light</div>'
    js = """
  tl.fromTo("#@P@-cx",{opacity:0},{opacity:1,duration:0.6},0);
  tl.fromTo("#@P@-mouseW",{opacity:0},{opacity:1,duration:0.6},0.1);
  tl.fromTo("#@P@-bob",{y:0},{y:-5,duration:0.8,repeat:5,yoyo:true,ease:"sine.inOut"},0.6);
  tl.fromTo("#@P@-cable",{attr:{"stroke-dashoffset":700}},{attr:{"stroke-dashoffset":0},duration:1.2,ease:"power2.out"},0.4);
  tl.fromTo("#@P@-light",{opacity:0,attr:{"stroke-dashoffset":60}},{opacity:1,attr:{"stroke-dashoffset":-640},duration:1.0,ease:"power1.in"},1.7);
  tl.fromTo("#@P@-halo",{opacity:0,scale:0.3,svgOrigin:"1060 470"},{opacity:0.9,scale:1.3,svgOrigin:"1060 470",duration:0.5,ease:"power2.out"},2.6);
  tl.fromTo("#@P@-rings",{opacity:0},{opacity:1,duration:0.1},2.6);
  ["a1","a2"].forEach(function(k,i){tl.fromTo("#@P@-"+k,{scale:0.5,opacity:0.9,svgOrigin:"1052 456"},{scale:6,opacity:0,svgOrigin:"1052 456",duration:1.3,ease:"power2.out",immediateRender:false},2.6+i*0.5);});
  tl.fromTo("#@P@-t",{opacity:0,y:30},{opacity:1,y:0,duration:0.6,ease:"power3.out"},2.9);
  tl.fromTo("#@P@-cam",{scale:1,svgOrigin:"1052 500"},{scale:1.22,svgOrigin:"1052 500",duration:5.6,ease:"power1.inOut"},0);
"""
    return svg_wrap(p, svg, html, js, extra)


# ---------------------------------------------------------------- M4: engram
def scene_M4():
    p = "M4"
    rng = random.Random(7)
    pts = []
    while len(pts) < 70:
        x, y = rng.uniform(122, 262), rng.uniform(38, 130)
        if all((x - a) ** 2 + (y - b) ** 2 > 60 for a, b in pts):
            pts.append((round(x, 1), round(y, 1)))
    group = [i for i, (x, y) in enumerate(pts) if (x - 205) ** 2 + (y - 78) ** 2 < 24 ** 2][:11]
    ed = "".join(f'<line x1="{pts[a][0]}" y1="{pts[a][1]}" x2="{pts[b][0]}" y2="{pts[b][1]}"/>' for i, a in enumerate(group) for b in group[i + 1:i + 3])
    nodes = "".join(f'<circle class="n" cx="{x}" cy="{y}" r="2.3" fill="#ffd0e6"/>' for x, y in pts)
    group_nodes = "".join(f'<circle class="g" cx="{pts[i][0]}" cy="{pts[i][1]}" r="3.4" fill="{AMBER}"/>' for i in group)
    extra = box_grad(p, "c") + f'<clipPath id="{p}-cp"><path d="{BRAIN_SIDE}"/></clipPath>'
    cx, cy = group and (sum(pts[i][0] for i in group) / len(group), sum(pts[i][1] for i in group) / len(group))
    svg = f"""<g id="{p}-mini" opacity="0"><g transform="translate(20 520) scale(.62)">{box(p)}<g transform="translate(870 716) scale(.9)">{mouse(p)}</g></g></g>
<g transform="translate(1260 470)"><g id="{p}-brainW"><g id="{p}-brain"><g transform="scale(2.5) translate(-192 -84)">{brain_side(p + "b")}
<g clip-path="url(#{p}-cp)">{nodes}<g stroke="{AMBER}" stroke-width="1.1" opacity="0" id="{p}-ed">{ed}</g><g id="{p}-gr" opacity="0">{group_nodes}</g></g></g></g></g></g>
<circle id="{p}-halo" cx="{1260 + (cx - 192) * 2.5:.0f}" cy="{470 + (cy - 84) * 2.5:.0f}" r="70" fill="{AMBER}" opacity="0" filter="url(#{p}-glow)"/>"""
    html = (f'<div id="{p}-t1" class="pill2" style="left:980px;width:560px;text-align:center;top:130px;font-size:56px;color:#ffd27a"><i style="background:#ffb23e"></i>ENGRAM</div>')
    js = """
  tl.fromTo("#@P@-mini",{opacity:0},{opacity:1,duration:1.0},0.2);
  tl.fromTo("#@P@-brainW",{opacity:0,scale:0.4,transformOrigin:"50% 50%"},{opacity:1,scale:1,transformOrigin:"50% 50%",duration:1.4,ease:"power3.out"},3.0);
  tl.fromTo("#@P@-brain",{y:0},{y:-10,duration:1.8,repeat:5,yoyo:true,ease:"sine.inOut"},4.4);
  tl.fromTo("#@P@-brainW .n",{opacity:0.15},{opacity:1,duration:0.2,repeat:9,yoyo:true,ease:"none",stagger:{each:0.07,from:"random"}},5.0);
  tl.fromTo("#@P@-gr",{opacity:0},{opacity:1,duration:0.7},8.4);
  tl.fromTo("#@P@-ed",{opacity:0},{opacity:1,duration:0.7},8.9);
  tl.fromTo("#@P@-halo",{opacity:0},{opacity:0.55,duration:0.8,repeat:5,yoyo:true,ease:"sine.inOut"},8.6);
  tl.fromTo("#@P@-t1",{opacity:0,y:20},{opacity:1,y:0,duration:0.6},11.2);
"""
    return svg_wrap(p, svg, html, js, extra)


# ---------------------------------------------------------------- M5: two boxes and the shock
def scene_M5():
    p = "M5"
    extra = box_grad(p, "c") + box_grad(p, "v")
    svg = f"""<g transform="translate(-268 70) scale(.8)"><g id="{p}-A"><g id="{p}-Aw">{box(p, "c", "a")}</g></g></g>
<g transform="translate(652 70) scale(.8)"><g id="{p}-B"><g id="{p}-Bw" opacity="0">{box(p, "v", "b")}</g></g></g>
<g transform="translate(428 643) scale(.72)"><g id="{p}-mouseW"><g id="{p}-bob">{mouse(p)}</g></g></g>
<g id="{p}-shock" opacity="0">{bolt(1420, 540, 1.5)}{bolt(1310, 585, 1.0)}{bolt(1530, 590, 1.0)}</g>
<path id="{p}-bridge" d="M560 470 C 800 200 1200 200 1380 470" fill="none" stroke="#7fe6ff" stroke-width="10" stroke-linecap="round" stroke-dasharray="14 14" opacity="0" filter="url(#{p}-glow)"/>
<circle id="{p}-pulse" r="18" fill="#7fe6ff" opacity="0" filter="url(#{p}-glow)"/>
<rect id="{p}-fl" width="1920" height="1080" fill="#ff2a63" opacity="0"/>"""
    html = f'<div id="{p}-t" class="pill2" style="left:20px;width:960px;text-align:center;top:60px;font-size:44px;opacity:0"><i style="background:#3be0ff"></i>CALM BOX</div><div id="{p}-t2" class="pill2" style="left:940px;width:960px;text-align:center;top:60px;font-size:44px;opacity:0;color:#ff9bb0"><i style="background:#ff4f7d"></i>SHOCK BOX</div>'
    js = """
  tl.fromTo("#@P@-A",{opacity:0},{opacity:1,duration:0.8},0);
  tl.fromTo("#@P@-mouseW",{opacity:0},{opacity:1,duration:0.6},0.2);
  tl.fromTo("#@P@-bob",{y:0},{y:-5,duration:0.9,repeat:12,yoyo:true,ease:"sine.inOut"},0.8);
  tl.fromTo("#@P@-t",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},0.9);
  tl.fromTo("#@P@-Bw",{opacity:0},{opacity:1,duration:0.8},2.6);
  tl.fromTo("#@P@-t2",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},3.0);
  tl.fromTo("#@P@-mouseW",{x:0,y:0},{keyframes:{x:[0,640,1278],y:[0,-305,0],easeEach:"power2.inOut"},duration:2.2,ease:"none",immediateRender:false},4.0);
  tl.fromTo("#@P@-fl",{opacity:0},{opacity:0.55,duration:0.07,ease:"power4.out"},6.5);
  tl.fromTo("#@P@-fl",{opacity:0.55},{opacity:0,duration:0.6,immediateRender:false},6.57);
  tl.fromTo("#@P@-shock",{opacity:0,scale:0.3,svgOrigin:"1420 560"},{opacity:1,scale:1,svgOrigin:"1420 560",duration:0.2,ease:"back.out(3)"},6.5);
  tl.fromTo("#@P@-shock",{opacity:1},{opacity:0,duration:0.5,immediateRender:false},7.6);
    tl.fromTo("#@P@-bridge",{opacity:0},{opacity:1,duration:0.2},6.3);
  tl.fromTo("#@P@-bridge",{attr:{"stroke-dashoffset":0}},{attr:{"stroke-dashoffset":-280},duration:1.6,ease:"none"},6.3);
  tl.fromTo("#@P@-bridge",{opacity:1},{opacity:0,duration:0.5,immediateRender:false},8.2);
  tl.set("#@P@-pulse",{x:560,y:470},0);
  tl.fromTo("#@P@-pulse",{opacity:0},{opacity:1,duration:0.1},6.3);
  tl.to("#@P@-pulse",{keyframes:{x:[560,820,1160,1380],y:[470,290,290,470],easeEach:"none"},duration:1.1,ease:"power1.in",immediateRender:false},6.3);
  tl.fromTo("#@P@-pulse",{opacity:1},{opacity:0,duration:0.2,immediateRender:false},7.4);
  tl.fromTo("#@P@-cam",{x:0,scale:1,svgOrigin:"960 540"},{x:-70,scale:1.06,svgOrigin:"960 540",duration:12.0,ease:"none"},0);
"""
    return svg_wrap(p, svg, html, js, extra)


# ---------------------------------------------------------------- M6: fear in the calm box
def scene_M6():
    p = "M6"
    extra = box_grad(p, "c") + f'<radialGradient id="{p}-vg" cx="50%" cy="50%" r="70%"><stop offset=".3" stop-color="#ff1f5a" stop-opacity="0"/><stop offset="1" stop-color="#ff1f5a" stop-opacity="1"/></radialGradient>'
    svg = f"""{box(p)}
<g transform="translate(870 716) scale(.9)"><g id="{p}-mouseW"><g id="{p}-shake"><g id="{p}-bob">{mouse(p)}</g></g></g></g>
<g id="{p}-ex" opacity="0"><circle cx="1010" cy="505" r="32" fill="#ffd23e"/><rect x="1005" y="483" width="10" height="26" rx="4" fill="#1a0f3a"/><circle cx="1010" cy="522" r="5" fill="#1a0f3a"/></g>
<rect id="{p}-redwash" width="1920" height="1080" fill="url(#{p}-vg)" opacity="0"/><rect id="{p}-redwash2" width="1920" height="1080" fill="#ff1f5a" opacity="0"/>"""
    html = ""
    js = """
  tl.fromTo("#@P@-cx",{opacity:0},{opacity:1,duration:0.8},0);
  tl.fromTo("#@P@-mouseW",{x:-420,opacity:0},{x:0,opacity:1,duration:1.8,ease:"power2.out"},0.2);
  tl.fromTo("#@P@-bob",{y:0},{y:-5,duration:0.7,repeat:12,yoyo:true,ease:"sine.inOut"},0.4);
  tl.fromTo("#@P@-rEyelid",{y:-52},{y:0,duration:0.09,repeat:1,yoyo:true,immediateRender:false},3.2);
  tl.fromTo("#@P@-ex",{opacity:0,scale:0.2,svgOrigin:"1010 540"},{opacity:1,scale:1,svgOrigin:"1010 540",duration:0.25,ease:"back.out(3)"},5.2);
  tl.fromTo("#@P@-redwash",{opacity:0},{opacity:1,duration:0.6,ease:"power2.out"},5.2);
  tl.fromTo("#@P@-redwash2",{opacity:0},{opacity:0.16,duration:0.6,ease:"power2.out"},5.2);
  tl.fromTo("#@P@-shake",{x:-3},{x:3,duration:0.05,repeat:80,yoyo:true,ease:"none"},5.3);
  tl.fromTo("#@P@-bob",{y:-5},{y:0,duration:0.2},5.2);
  tl.fromTo("#@P@-cam",{scale:1,svgOrigin:"1030 640"},{scale:1.5,svgOrigin:"1030 640",duration:5.0,ease:"sine.inOut"},0);
  tl.fromTo("#@P@-cam",{scale:1.5},{scale:1.9,duration:0.25,ease:"power4.out",immediateRender:false},5.2);
  tl.fromTo("#@P@-cam",{scale:1.9},{scale:2.05,duration:5.4,ease:"none",immediateRender:false},5.45);
"""
    return svg_wrap(p, svg, html, js, extra, background=("#3a1d7a", "#1a1050", "#0b0a24"), seed=11)


# ---------------------------------------------------------------- M7: mouse with an optical fiber
def scene_M7():
    p = "M7"
    extra = box_grad(p, "c")
    svg = f"""{box(p)}
<g transform="translate(900 700) scale(1.15)"><g id="{p}-mouseW"><g id="{p}-bob">{mouse(p)}</g></g></g>
<path id="{p}-cable" d="M1010 -60 C 1010 160 1040 300 1052 440" fill="none" stroke="#9aa6d0" stroke-width="12" stroke-linecap="round"/>
<rect x="1036" y="426" width="34" height="24" rx="7" fill="#c9d0f0" stroke="#7a86c8" stroke-width="3"/>
<path id="{p}-light" d="M1010 -60 C 1010 160 1040 300 1052 440" fill="none" stroke="#7fe6ff" stroke-width="12" stroke-linecap="round" stroke-dasharray="70 700" stroke-dashoffset="70" filter="url(#{p}-glow)" opacity="0"/>
<circle id="{p}-halo" cx="1052" cy="458" r="36" fill="#7fe6ff" opacity="0" filter="url(#{p}-glow)"/>"""
    html = f'<div id="{p}-t" class="pill2" style="left:0;right:0;text-align:center;top:870px;font-size:40px;color:#bff4ff"><i style="background:#7fe6ff"></i>GENETICALLY MODIFIED MOUSE · LIGHT FIBER IN THE BRAIN</div>'
    js = """
  tl.fromTo("#@P@-cx",{opacity:0},{opacity:1,duration:0.6},0);
  tl.fromTo("#@P@-mouseW",{opacity:0},{opacity:1,duration:0.6},0.1);
  tl.fromTo("#@P@-bob",{y:0},{y:-5,duration:0.9,repeat:12,yoyo:true,ease:"sine.inOut"},0.5);
  tl.fromTo("#@P@-rEyelid",{y:-52},{y:0,duration:0.09,repeat:1,yoyo:true,immediateRender:false},2.8);
  tl.fromTo("#@P@-rEyelid",{y:-52},{y:0,duration:0.09,repeat:1,yoyo:true,immediateRender:false},7.4);
  tl.fromTo("#@P@-t",{opacity:0,y:20},{opacity:1,y:0,duration:0.6},1.0);
  [0,1,2].forEach(function(k){
    tl.fromTo("#@P@-light",{opacity:0,attr:{"stroke-dashoffset":70}},{opacity:1,attr:{"stroke-dashoffset":-640},duration:1.0,ease:"power1.in",immediateRender:false},2.4+k*3.0);
    tl.fromTo("#@P@-halo",{opacity:0,scale:0.4,svgOrigin:"1052 458"},{opacity:0.9,scale:1.8,svgOrigin:"1052 458",duration:0.45,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false},3.3+k*3.0);
  });
  tl.fromTo("#@P@-cam",{scale:1,svgOrigin:"1050 520"},{scale:1.2,svgOrigin:"1050 520",duration:12,ease:"sine.inOut"},0);
"""
    return svg_wrap(p, svg, html, js, extra)


# ---------------------------------------------------------------- M8: it only felt fear
def scene_M8():
    p = "M8"
    extra = box_grad(p, "c") + box_grad(p, "v") + f'<linearGradient id="{p}-fx" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffcf6a" stop-opacity=".5"/><stop offset="1" stop-color="#ffe3a0" stop-opacity="0"/></linearGradient>'
    svg = f"""<polygon id="{p}-beam" points="760,-40 1160,-40 1230,700 690,700" fill="url(#{p}-fx)" opacity="0"/>
<g transform="translate(0 120)"><g id="{p}-cx1">{box(p, "c")}</g>
<g id="{p}-cx2" opacity="0">{box(p, "v", "b")}</g>
<g transform="translate(870 716) scale(.9)"><g id="{p}-mouseW"><g id="{p}-shake"><g id="{p}-bob">{mouse(p)}</g></g></g></g></g>
<g transform="translate(960 110) scale(1.0)"><g id="{p}-key" opacity="0"><circle cx="0" cy="0" r="34" fill="none" stroke="{AMBER}" stroke-width="12"/><path d="M0 34 L0 130 M0 100 L30 100 M0 124 L22 124" stroke="{AMBER}" stroke-width="12" fill="none" stroke-linecap="round"/></g></g>"""
    html = ""
    js = """
  tl.fromTo("#@P@-cx1",{opacity:0},{opacity:1,duration:0.8},0);
  tl.fromTo("#@P@-mouseW",{opacity:0},{opacity:1,duration:0.8},0.2);
  tl.fromTo("#@P@-bob",{y:0},{y:-4,duration:0.5,repeat:18,yoyo:true,ease:"sine.inOut"},0.6);
  tl.fromTo("#@P@-shake",{x:-2.5},{x:2.5,duration:0.06,repeat:120,yoyo:true,ease:"none"},1.0);
  tl.fromTo("#@P@-beam",{opacity:0},{opacity:1,duration:1.6},2.6);
  tl.fromTo("#@P@-key",{opacity:0,y:-80},{opacity:1,y:0,duration:1.0,ease:"power3.out"},4.4);
  tl.fromTo("#@P@-cx2",{opacity:0},{opacity:0.6,duration:1.6},5.0);
  tl.fromTo("#@P@-cam",{scale:1.2,svgOrigin:"1030 640"},{scale:1.0,svgOrigin:"960 480",duration:9.7,ease:"sine.inOut"},0);
"""
    return svg_wrap(p, svg, html, js, extra, background=("#2a1560", "#150d40", "#07061a"), seed=17)


SCENES = [("M2", scene_M2), ("M3", scene_M3), ("M4", scene_M4), ("M5", scene_M5), ("M6", scene_M6), ("M7", scene_M7), ("M8", scene_M8)]


def main():
    os.makedirs(os.path.join(HERE, "compositions"), exist_ok=True)
    hosts, t = [], 0.0
    start = {}
    for k, fn in SCENES:
        open(os.path.join(HERE, f"compositions/{k}.html"), "w").write(fn())
        hosts.append(f'<div id="{k}" data-composition-id="{k}" data-composition-src="compositions/{k}.html" data-start="{t:.2f}" data-duration="{DUR[k]:.2f}" data-track-index="1" data-width="1920" data-height="1080"></div>')
        start[k] = round(t, 2)
        t += DUR[k] + 0.5
    total = t - 0.5
    open(os.path.join(HERE, "index.html"), "w").write(f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@700&family=IBM+Plex+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#0b0a24}}#root{{width:100%;height:100%;position:relative}}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}" data-width="1920" data-height="1080">
{chr(10).join(hosts)}
</div><script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script></body></html>
""")
    json.dump({"start": start, "dur": DUR, "total": round(total, 2)}, open(os.path.join(HERE, "timing.json"), "w"), indent=1)
    print("ok, total", round(total, 2), "s", start)


if __name__ == "__main__":
    main()
