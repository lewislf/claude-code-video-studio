"""Generates compositions/*.html and index.html for the v3 scenes (own vector drawing, approved narration).

  python3 build.py

Each scene has the exact duration of its narration clip (timing.json). Local times in seconds.
"""
import json, math, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
TM = json.load(open(os.path.join(HERE, "timing.json")))
INFO, START, GAP = TM["info"], TM["start"], TM["gap"]
CYAN, MAGENTA, AMBER, MINT, LILAC, RED = "#3be0ff", "#ff4fa3", "#ffb23e", "#38e8a8", "#8d7bff", "#ff4f7d"

CSS = """
.scene{position:absolute;inset:0;width:1920px;height:1080px;overflow:hidden;background:#0b0a24;font-family:"IBM Plex Mono",monospace}
.scene .full{position:absolute;inset:0;width:1920px;height:1080px}
.black{position:absolute;inset:0;background:#000;pointer-events:none;z-index:50}
.pill{position:absolute;font:500 28px "IBM Plex Mono",monospace;letter-spacing:.16em;color:#3be0ff;border:2px solid #3be0ff;padding:10px 18px;background:rgba(11,10,36,.78);opacity:0;white-space:nowrap}
.pill.amber{color:#ffb23e;border-color:#ffb23e}.pill.red{color:#ff4f7d;border-color:#ff4f7d}.pill.lilac{color:#8d7bff;border-color:#8d7bff}
.num{position:absolute;font:700 120px "EB Garamond",serif;color:#eef1f7;opacity:0;text-shadow:0 4px 30px #000;white-space:nowrap}
.num small{display:block;font:400 30px "IBM Plex Mono",monospace;letter-spacing:.14em;color:#3be0ff;margin-top:-6px}
"""

DUST = """
(function(){var s=7;var r=function(){s=(s+0x6d2b79f5)|0;var t=Math.imul(s^(s>>>15),1|s);t=(t+Math.imul(t^(t>>>7),61|t))^t;return((t^(t>>>14))>>>0)/4294967296;};
var g=document.getElementById("@ID@-part"),colors=["#3be0ff","#8d7bff","#ff9bd0","#ffd23e"];
for(var i=0;i<30;i++){var c=document.createElementNS("http://www.w3.org/2000/svg","circle");
c.setAttribute("id","@ID@p"+i);c.setAttribute("cx",Math.round(r()*1920));c.setAttribute("cy",Math.round(200+r()*880));
c.setAttribute("r",(2+r()*4).toFixed(1));c.setAttribute("fill",colors[i%4]);c.setAttribute("opacity",(0.2+r()*0.45).toFixed(2));g.appendChild(c);
tl.fromTo("#@ID@p"+i,{y:0},{y:-(100+r()*240),duration:@DUR@,ease:"none"},0);}})();
"""


def defs(i):
    return f"""<defs>
<radialGradient id="{i}-background" cx="50%" cy="46%" r="75%"><stop offset="0" stop-color="#34196f"/><stop offset=".55" stop-color="#1a1050"/><stop offset="1" stop-color="#0b0a24"/></radialGradient>
<filter id="{i}-glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="1920" height="1080" fill="url(#{i}-background)"/><g id="{i}-part"></g>"""


def composition(i, dur, body_svg, html, js):
    js = js.replace("@ID@", i).replace("@DUR@", f"{dur:.2f}")
    return f"""<template>
  <style>{CSS}</style>
  <div id="{i}-root" data-composition-id="{i}" data-width="1920" data-height="1080">
    <div class="scene">
    <svg id="{i}-svg" class="full" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">{defs(i)}{body_svg}</svg>
    {html}
    <div id="{i}-black" class="black"></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {DUST.replace("@ID@", i).replace("@DUR@", f"{dur:.2f}")}
    {js}
    tl.fromTo("#{i}-black", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.4, ease: "none" }}, 0);
    tl.fromTo("#{i}-black", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "none", immediateRender: false }}, {dur - 0.4:.2f});
    window.__timelines["{i}"] = tl;
  </script>
</template>
"""


# ---------------------------------------------------------------- drawing pieces
def fly(p):
    return f"""<g id="{p}">
<g id="{p}-wings"><ellipse cx="-10" cy="-52" rx="74" ry="24" fill="#d9eeff" opacity=".45" transform="rotate(-28 -10 -52)"/>
<ellipse cx="-30" cy="-46" rx="80" ry="26" fill="#cfe6ff" opacity=".6" transform="rotate(-18 -30 -46)"/></g>
<g stroke="#2a1a3a" stroke-width="7" stroke-linecap="round" fill="none"><path d="M-6 26 L-22 70"/><path d="M14 28 L24 74"/><path d="M34 22 L58 64"/><path d="M-30 30 L-52 68"/></g>
<ellipse cx="-47" cy="10" rx="58" ry="36" fill="#ff3b6b" opacity=".8"/><ellipse cx="-61" cy="2" rx="58" ry="36" fill="#35e6a6" opacity=".8"/>
<ellipse cx="-54" cy="6" rx="58" ry="36" fill="#e9bd78"/>
<path d="M-96 -14 Q-84 6 -96 28 M-72 -28 Q-58 6 -72 40 M-48 -32 Q-34 6 -48 42" stroke="#3a2412" stroke-width="7" fill="none" stroke-linecap="round" opacity=".85"/>
<ellipse cx="10" cy="-4" rx="40" ry="33" fill="#d99a4e"/><ellipse cx="-30" cy="-26" rx="60" ry="9" fill="#fff" opacity=".16"/>
<g id="{p}-head"><circle id="{p}-headC" cx="62" cy="-2" r="32" fill="#d99a4e"/>
<ellipse id="{p}-eye" cx="72" cy="-8" rx="24" ry="26" fill="#e23352"/><circle cx="80" cy="-16" r="8" fill="#ff9aab"/>
<ellipse id="{p}-brainDot" cx="54" cy="-2" rx="9" ry="8" fill="#3be0ff" opacity="0" filter="url(#A-glow)"/>
<path d="M92 8 q 12 6 18 18" stroke="#2a1a3a" stroke-width="6" fill="none" stroke-linecap="round"/></g></g>"""


def network(seed, n=140, dmin=44, colors=True):
    rng = random.Random(seed)
    pts = []
    def inside(x, y):
        return ((x + 150) / 260) ** 2 + (y / 250) ** 2 <= 1 or ((x - 150) / 260) ** 2 + (y / 250) ** 2 <= 1
    t = 0
    while len(pts) < n and t < 30000:
        t += 1
        x, y = rng.uniform(-410, 410), rng.uniform(-250, 250)
        if inside(x, y) and all((x - a) ** 2 + (y - b) ** 2 >= dmin ** 2 for a, b in pts):
            pts.append((round(x, 1), round(y, 1)))
    edges = set()
    for k, (x, y) in enumerate(pts):
        for j in sorted(range(len(pts)), key=lambda j: (pts[j][0] - x) ** 2 + (pts[j][1] - y) ** 2)[1:4]:
            edges.add(tuple(sorted((k, j))))
    return pts, sorted(edges)


def network_svg(p, pts, edges):
    edge_svg = "".join(f'<line class="ed" x1="{pts[a][0]}" y1="{pts[a][1]}" x2="{pts[b][0]}" y2="{pts[b][1]}"/>' for a, b in edges)
    colors = [CYAN, CYAN, CYAN, LILAC, "#5fb7ff", MAGENTA]
    nodes = "".join(f'<circle class="node" cx="{x}" cy="{y}" r="{5 + (k * 7) % 5}" fill="{colors[k % 6]}"/>' for k, (x, y) in enumerate(pts))
    return f'<g id="{p}"><rect x="-420" y="-260" width="840" height="520" fill="none" stroke="none"/><g stroke="#5f6cff" stroke-width="2.2" opacity="0" class="eds">{edge_svg}</g><g filter="url(#{p[0]}-glow)">{nodes}</g></g>'


def path_d(pts, edges, a, b):
    neighbors = {}
    for x, y in edges:
        neighbors.setdefault(x, []).append(y); neighbors.setdefault(y, []).append(x)
    prev, queue = {a: None}, [a]
    while queue:
        u = queue.pop(0)
        if u == b:
            break
        for v in neighbors.get(u, []):
            if v not in prev:
                prev[v] = u; queue.append(v)
    c, u = [], b
    while u is not None:
        c.append(pts[u]); u = prev.get(u)
    return c[::-1]


PTS_A, EDGES_A = network(11)
LEFT = min(range(len(PTS_A)), key=lambda k: PTS_A[k][0] + 0.3 * PTS_A[k][1])
RIGHT = max(range(len(PTS_A)), key=lambda k: PTS_A[k][0] - 0.3 * PTS_A[k][1])
PATH_A = path_d(PTS_A, EDGES_A, LEFT, RIGHT)


# ---------------------------------------------------------------- Scene A: the fly connectome
def scene_A():
    d = INFO["A"]
    grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="1080"/>' for x in range(0, 1921, 120)) + "".join(f'<line x1="0" y1="{y}" x2="1920" y2="{y}"/>' for y in range(0, 1081, 120))
    streets = '<polyline points="120,840 480,720 840,780 1200,540 1560,600 1800,360" fill="none" stroke="#5f6cff" stroke-width="10" opacity=".5"/><polyline points="240,240 600,360 960,300 1320,420 1680,240" fill="none" stroke="#5f6cff" stroke-width="8" opacity=".4"/>'
    pins_pos = [(420, 760), (860, 700), (1180, 560), (1500, 640)]
    pins = "".join(f'<g id="A-pin{k}"><g transform="translate({x} {y})"><path d="M0 0 C-30 -40 -36 -70 0 -84 C36 -70 30 -40 0 0 Z" fill="{AMBER}"/><circle cy="-52" r="22" fill="#1a1050"/><text y="-42" text-anchor="middle" font-size="30" font-weight="700" fill="{AMBER}">?</text></g></g>' for k, (x, y) in enumerate(pins_pos))
    seed_svg = '<circle r="46" fill="#1d1840" stroke="#8d7bff" stroke-width="4"/><circle cx="-14" cy="-12" r="5" fill="#6a5fc0"/><circle cx="16" cy="10" r="5" fill="#6a5fc0"/><circle cx="-4" cy="24" r="4" fill="#6a5fc0"/><circle cx="20" cy="-20" r="4" fill="#6a5fc0"/>'
    svg = f"""<g id="A-streetmap" opacity="0"><g stroke="#3b3a9c" stroke-width="2" opacity=".35">{grid}</g>{streets}{pins}</g>
<g id="A-cam"><g transform="translate(860 560)"><g id="A-fly"><g id="A-flyBob" transform="scale(1.6)">{fly("A-mo")}</g></g></g>
<g transform="translate(1160 640)"><g id="A-poppy">{seed_svg}</g></g></g>
<g transform="translate(960 540)"><g id="A-network">{network_svg("A-r", PTS_A, EDGES_A)}</g><circle id="A-pulse" r="9" fill="#ffd23e" filter="url(#A-glow)" opacity="0"/></g>"""
    html = """<div id="A-l1" class="pill" style="left:800px;top:820px">FRUIT FLY</div>
<div id="A-l2" class="pill" style="left:830px;top:610px">BRAIN</div>
<div id="A-l3" class="pill amber" style="left:1330px;top:960px">POPPY SEED</div>
<div id="A-n1" class="num" style="left:90px;top:760px"><span id="A-n1v">0</span><small>NEURONS</small></div>
<div id="A-n2" class="num" style="right:90px;top:760px;text-align:right"><span id="A-n2v">0</span><small>CONNECTIONS</small></div>
<div id="A-cred" class="pill lilac" style="right:72px;top:60px;font-size:22px">FlyWire · Nature · 2024</div>"""
    js = """
  tl.fromTo("#A-streetmap",{opacity:0},{opacity:1,duration:1.0},0.2);
  [0,1,2,3].forEach(function(k){tl.fromTo("#A-pin"+k,{y:-300,opacity:0},{y:0,opacity:1,duration:0.6,ease:"bounce.out"},1.3+k*0.9);});
  tl.fromTo("#A-streetmap",{scale:1,svgOrigin:"960 540"},{scale:0.5,svgOrigin:"960 540",duration:1.2,ease:"power2.in",immediateRender:false},5.4);
  tl.fromTo("#A-streetmap",{opacity:1},{opacity:0,duration:1.0,immediateRender:false},5.6);
  tl.fromTo("#A-fly",{x:1100,y:-320,opacity:0},{x:0,y:0,opacity:1,duration:1.6,ease:"power3.out"},6.0);
  tl.fromTo("#A-flyBob",{y:0},{y:-12,duration:0.45,repeat:11,yoyo:true,ease:"sine.inOut"},7.6);
  tl.fromTo("#A-mo-wings",{scaleY:1,transformOrigin:"50% 100%"},{scaleY:0.3,transformOrigin:"50% 100%",duration:0.06,repeat:200,yoyo:true,ease:"none"},6.0);
  tl.fromTo("#A-l1",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},9.6);
  tl.fromTo("#A-l1",{opacity:1},{opacity:0,duration:0.3,immediateRender:false},11.5);
  tl.fromTo("#A-cam",{scale:1,svgOrigin:"953 556"},{scale:3.0,svgOrigin:"953 556",duration:2.6,ease:"power2.inOut"},11.8);
  tl.fromTo("#A-mo-headC",{opacity:1},{opacity:0.22,duration:1.0},12.8);
  tl.fromTo("#A-mo-brainDot",{opacity:0},{opacity:1,duration:0.8},13.0);
  tl.fromTo("#A-poppy",{x:900,rotation:0},{x:0,rotation:360,duration:2.2,ease:"power2.out"},12.4);
  tl.fromTo("#A-l2",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},14.8);
  tl.fromTo("#A-l3",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},15.4);
  tl.fromTo("#A-l2",{opacity:1},{opacity:0,duration:0.4,immediateRender:false},18.0);
  tl.fromTo("#A-l3",{opacity:1},{opacity:0,duration:0.4,immediateRender:false},18.0);
  tl.fromTo("#A-cam",{opacity:1},{opacity:0,duration:0.8,immediateRender:false},18.2);
  tl.fromTo("#A-network",{scale:0.5,transformOrigin:"50% 50%"},{scale:1,transformOrigin:"50% 50%",duration:6,ease:"sine.out"},18.4);
  tl.fromTo("#A-r .eds",{opacity:0},{opacity:0.7,duration:1.6},18.9);
  tl.fromTo("#A-r .node",{scale:0,transformOrigin:"50% 50%"},{scale:1,transformOrigin:"50% 50%",duration:0.4,ease:"back.out(2)",stagger:{each:0.012}},18.6);
  var cam=@CAM@, xs=cam.map(function(p){return p[0];}), ys=cam.map(function(p){return p[1];});
  tl.set("#A-pulse",{x:xs[0],y:ys[0]},0);
  [0,1,2].forEach(function(k){
    tl.fromTo("#A-pulse",{opacity:0},{opacity:1,duration:0.15},22.2+k*2.4);
    tl.to("#A-pulse",{keyframes:{x:xs,y:ys,easeEach:"none"},duration:2.0,ease:"none",immediateRender:false},22.2+k*2.4);
  });
  tl.fromTo("#A-n1",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},24.2);
  var o1={v:0};tl.fromTo(o1,{v:0},{v:139255,duration:2.6,ease:"power2.out",onUpdate:function(){document.getElementById("A-n1v").textContent=Math.round(o1.v).toLocaleString("en-US");}},24.4);
  tl.fromTo("#A-n2",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},27.4);
  var o2={v:0};tl.fromTo(o2,{v:0},{v:50,duration:2.2,ease:"power2.out",onUpdate:function(){document.getElementById("A-n2v").textContent="≈ "+Math.round(o2.v)+" million";}},27.6);
  tl.fromTo("#A-cred",{opacity:0},{opacity:1,duration:0.6},25.0);
""".replace("@CAM@", json.dumps(PATH_A))
    return composition("A", d, svg, html, js)


# ---------------------------------------------------------------- Scene B: the simulated brain
def scene_B():
    d = INFO["B"]
    svg = f"""<g id="B-mon" opacity="0"><rect x="1030" y="250" width="720" height="500" rx="32" fill="#14122e" stroke="{LILAC}" stroke-width="6"/>
<rect id="B-screen" x="1056" y="276" width="668" height="448" rx="14" fill="#0e0c26"/><rect id="B-light" x="1056" y="276" width="668" height="448" rx="14" fill="{CYAN}" opacity="0"/>
<rect x="1360" y="750" width="60" height="70" fill="#14122e" stroke="{LILAC}" stroke-width="4"/><rect x="1260" y="820" width="260" height="22" rx="11" fill="#14122e" stroke="{LILAC}" stroke-width="4"/></g>
<g transform="translate(960 540)"><g id="B-netX"><g id="B-network">{network_svg("B-r", PTS_A, EDGES_A)}
<circle id="B-start" cx="{PTS_A[LEFT][0]}" cy="{PTS_A[LEFT][1]}" r="22" fill="none" stroke="{AMBER}" stroke-width="6" opacity="0"/>
<circle id="B-end" cx="{PTS_A[RIGHT][0]}" cy="{PTS_A[RIGHT][1]}" r="22" fill="none" stroke="{MINT}" stroke-width="6" opacity="0"/>
<circle id="B-pulse" r="10" fill="#ffd23e" filter="url(#B-glow)" opacity="0"/></g></g></g>"""
    html = '<div id="B-l1" class="pill" style="left:1090px;top:130px">SIMULATED</div>'
    js = """
  tl.fromTo("#B-network",{scale:0.2,opacity:0,transformOrigin:"50% 50%"},{scale:1.0,opacity:1,transformOrigin:"50% 50%",duration:1.6,ease:"power2.out"},0.2);
  tl.fromTo("#B-r .eds",{opacity:0},{opacity:0.7,duration:1.0},0.6);
  tl.fromTo("#B-netX",{x:0},{x:-400,duration:1.6,ease:"power2.inOut"},2.2);
  tl.fromTo("#B-network",{scale:1.0,transformOrigin:"50% 50%"},{scale:0.62,transformOrigin:"50% 50%",duration:1.6,ease:"power2.inOut",immediateRender:false},2.2);
  tl.fromTo("#B-mon",{x:900,opacity:0},{x:0,opacity:1,duration:1.4,ease:"power3.out"},2.4);
  tl.fromTo("#B-netX",{x:-400},{x:440,duration:1.5,ease:"power2.inOut",immediateRender:false},4.7);
  tl.fromTo("#B-network",{scale:0.62,transformOrigin:"50% 50%"},{scale:0.40,transformOrigin:"50% 50%",duration:1.5,ease:"power2.inOut",immediateRender:false},4.7);
  tl.fromTo("#B-light",{opacity:0},{opacity:0.22,duration:0.5},6.2);
  var cam=@CAM@, xs=cam.map(function(p){return p[0];}), ys=cam.map(function(p){return p[1];});
  tl.set("#B-pulse",{x:xs[0],y:ys[0]},0);
  tl.fromTo("#B-start",{opacity:0},{opacity:1,duration:0.3},6.4);
  [0,1].forEach(function(k){
    tl.fromTo("#B-pulse",{opacity:0},{opacity:1,duration:0.1},6.6+k*1.9);
    tl.to("#B-pulse",{keyframes:{x:xs,y:ys,easeEach:"none"},duration:1.7,ease:"none",immediateRender:false},6.6+k*1.9);
  });
  tl.fromTo("#B-end",{opacity:0,scale:0.4,transformOrigin:"50% 50%"},{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.4,ease:"back.out(3)"},8.2);
  tl.fromTo("#B-l1",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},7.4);
""".replace("@CAM@", json.dumps(PATH_A))
    return composition("B", d, svg, html, js)


# ---------------------------------------------------------------- Scene C: simulation (feed, world, minds, you)
def scene_C():
    d = INFO["C1"] + GAP + INFO["C2"]
    act2 = INFO["C1"] + GAP
    rng = random.Random(5)
    buildings = "".join(
        f'<rect x="{x}" y="{700 - h}" width="{w}" height="{h}" fill="{c}"/>'
        for x, w, h, c in [(430 + k * 52, 40, 60 + (k * 37) % 220, ["#2b2a80", "#3a2a8c", "#25427a"][k % 3]) for k in range(20)]
    )
    windows = "".join(f'<rect x="{438 + k * 52 + (j % 2) * 18}" y="{700 - 40 - j * 34}" width="8" height="10" fill="#ffd23e" opacity=".55"/>' for k in range(20) for j in range(2 + (k * 37) % 5))
    cube = lambda cx, cy, s: f"M{cx} {cy - s} L{cx + s * 1.1} {cy - s * 0.45} L{cx + s * 1.1} {cy + s * 0.55} L{cx} {cy + s} L{cx - s * 1.1} {cy + s * 0.55} L{cx - s * 1.1} {cy - s * 0.45} Z M{cx - s * 1.1} {cy - s * 0.45} L{cx} {cy + 0.1 * s} L{cx + s * 1.1} {cy - s * 0.45} M{cx} {cy + 0.1 * s} L{cx} {cy + s}"
    cols, rows, step = 29, 13, 62
    dots = "".join(f'<circle class="m" cx="{960 + (i % cols - 14) * step}" cy="{560 + (i // cols - 6) * step}" r="20" fill="{CYAN}" opacity=".9"/>' for i in range(cols * rows))
    real = f'<circle id="C-real" cx="{960 + 5 * step}" cy="{560 + 1 * step}" r="24" fill="{AMBER}" filter="url(#C-glow)" opacity="0"/>'
    tiles = "".join(
        f'<g class="tile" opacity=".85"><path d="{cube(240 + c * 240, 330 + l * 240, 78)}" fill="none" stroke="{CYAN}" stroke-width="5" filter="url(#C-glow)"/>'
        f'<g fill="#3a2a8c"><rect x="{240 + c * 240 - 30}" y="{330 + l * 240 + 6}" width="16" height="34"/><rect x="{240 + c * 240 - 6}" y="{330 + l * 240 - 8}" width="16" height="48"/><rect x="{240 + c * 240 + 18}" y="{330 + l * 240 + 14}" width="16" height="26"/></g></g>'
        for l in range(3) for c in range(7)
    )
    svg = f"""<g id="C-a1">
<g id="C-phoneW" transform="translate(960 540)"><g id="C-phone"><rect x="-190" y="-380" width="380" height="760" rx="46" fill="#14122e" stroke="{LILAC}" stroke-width="6"/>
<rect x="-164" y="-346" width="328" height="692" rx="22" fill="#0e0c26"/>
<clipPath id="C-cp"><rect x="-164" y="-346" width="328" height="692" rx="22"/></clipPath><g clip-path="url(#C-cp)"><g id="C-posts"><rect x="-140" y="-320" width="280" height="140" rx="16" fill="#2b2a80"/><rect x="-140" y="-160" width="280" height="140" rx="16" fill="#7b2a6c"/><rect x="-140" y="0" width="280" height="140" rx="16" fill="#25427a"/><rect x="-140" y="160" width="280" height="140" rx="16" fill="#6b5b2a"/><rect x="-140" y="320" width="280" height="140" rx="16" fill="#2b2a80"/></g></g></g></g>
<g id="C-city" opacity="0">{buildings}{windows}</g>
<path id="C-box" d="{cube(960, 480, 330)}" fill="none" stroke="{CYAN}" stroke-width="8" filter="url(#C-glow)" opacity="0"/></g>
<g id="C-a2" opacity="0"><g id="C-grid">{dots}{real}</g></g>
<g id="C-a3" opacity="0">{tiles}<path id="C-you" d="{cube(240 + 3 * 240, 330 + 1 * 240, 86)}" fill="{AMBER}" fill-opacity=".25" stroke="{AMBER}" stroke-width="8" filter="url(#C-glow)"/></g>
<rect id="C-scan" x="0" y="0" width="1920" height="6" fill="#ffffff" opacity="0"/>"""
    html = f"""<div id="C-t1" class="pill" style="left:810px;top:70px">FEED</div>
<div id="C-t2" class="pill" style="left:860px;top:70px">MINDS</div>
<div id="C-n" class="num" style="left:0;right:0;text-align:center;top:70px;font-size:96px">1</div>
<div id="C-t3" class="pill amber" style="left:690px;top:880px;font-size:40px">ARE YOU HERE?</div>"""
    js = f"""
  var A2={act2:.2f};
  tl.fromTo("#C-posts",{{y:0}},{{y:-300,duration:2.4,ease:"none"}},0.2);
  tl.fromTo("#C-t1",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.5}},0.4);
  tl.fromTo("#C-phone",{{scale:1,x:0,y:0}},{{scale:0.26,x:-260,y:120,duration:2.2,ease:"power2.inOut"}},2.4);
  tl.fromTo("#C-city",{{opacity:0,scale:1.5,svgOrigin:"960 540"}},{{opacity:1,scale:1,svgOrigin:"960 540",duration:2.2,ease:"power2.out"}},2.6);
  tl.fromTo("#C-t1",{{opacity:1}},{{opacity:0,duration:0.3,immediateRender:false}},4.4);
  tl.fromTo("#C-box",{{opacity:0,scale:1.15,svgOrigin:"960 480"}},{{opacity:1,scale:1,svgOrigin:"960 480",duration:1.2,ease:"power3.out"}},5.0);
  tl.fromTo("#C-a1",{{opacity:1}},{{opacity:0,duration:0.5,immediateRender:false}},A2-0.1);
  tl.fromTo("#C-a2",{{opacity:0}},{{opacity:1,duration:0.4}},A2);
  tl.fromTo("#C-grid .m",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,transformOrigin:"50% 50%",duration:0.3,ease:"back.out(2)",stagger:{{amount:6.0,from:"center",grid:[13,29]}}}},A2+0.4);
  tl.fromTo("#C-n",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.5}},A2+0.4);
  var on={{v:0}};tl.fromTo(on,{{v:0}},{{v:2.86,duration:6.0,ease:"power1.in",onUpdate:function(){{var n=Math.round(Math.pow(10,on.v));document.getElementById("C-n").textContent=n.toLocaleString("en-US")+(n===1?" mind":" minds");}}}},A2+0.4);
  tl.fromTo("#C-real",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.5,ease:"back.out(3)"}},A2+7.2);
  tl.fromTo("#C-real",{{scale:1}},{{scale:1.5,transformOrigin:"50% 50%",duration:0.45,repeat:5,yoyo:true,ease:"sine.inOut",immediateRender:false}},A2+7.8);
  tl.fromTo("#C-grid",{{scale:1,svgOrigin:"1270 622"}},{{scale:3.2,svgOrigin:"1270 622",duration:3.0,ease:"power2.in",immediateRender:false}},A2+9.2);
  tl.fromTo("#C-a2",{{opacity:1}},{{opacity:0,duration:0.6,immediateRender:false}},A2+11.6);
  tl.fromTo("#C-n",{{opacity:1}},{{opacity:0,duration:0.4,immediateRender:false}},A2+11.4);
  tl.fromTo("#C-a3",{{opacity:0,scale:1.25,svgOrigin:"960 540"}},{{opacity:1,scale:1,svgOrigin:"960 540",duration:1.2,ease:"power2.out"}},A2+11.9);
  tl.fromTo("#C-you",{{opacity:1}},{{opacity:0.4,duration:0.35,repeat:7,yoyo:true,ease:"sine.inOut",immediateRender:false}},A2+13.4);
  tl.fromTo("#C-t3",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.5}},A2+14.2);
  tl.fromTo("#C-scan",{{y:0,opacity:0.18}},{{y:1080,opacity:0.18,duration:1.6,repeat:3,ease:"none"}},A2+14.0);
"""
    return composition("C", d, svg, html, js)


# ---------------------------------------------------------------- Scene D: hospital (without showing the patient)
def scene_D():
    d = INFO["D"]
    rain = "".join(f'<line x1="{x}" y1="{y}" x2="{x - 14}" y2="{y + 44}"/>' for x in range(0, 2000, 70) for y in range(-120, 1100, 120))
    ecg = "M0 640 " + " ".join("h70 l14 -60 l16 120 l12 -78 l8 18 h60" for _ in range(14))
    svg = f"""<g id="D-road">
<rect x="0" y="560" width="1920" height="520" fill="#0e0c28"/><polygon points="740,560 1180,560 1900,1080 20,1080" fill="#15133a"/>
<g id="D-stripe" stroke="#8d7bff" stroke-width="10" stroke-dasharray="60 90" opacity=".7"><line x1="960" y1="560" x2="960" y2="1080"/></g>
<g id="D-rain" stroke="#8fb4ff" stroke-width="3" opacity=".35">{rain}</g>
<g id="D-headlights" transform="translate(960 600)"><g id="D-lampsG"><circle cx="-90" cy="0" r="26" fill="#fff6c8" filter="url(#D-glow)"/><circle cx="90" cy="0" r="26" fill="#fff6c8" filter="url(#D-glow)"/></g></g>
<rect id="D-sirenR" width="1920" height="1080" fill="#ff1f5a" opacity="0"/><rect id="D-sirenB" width="1920" height="1080" fill="#2a7bff" opacity="0"/>
<rect id="D-flash" width="1920" height="1080" fill="#ffffff" opacity="0"/></g>
<g id="D-room" opacity="0">
<rect width="1920" height="1080" fill="#101a3a"/><rect y="760" width="1920" height="320" fill="#0c1230"/>
<clipPath id="D-clipW"><rect x="200" y="170" width="440" height="400" rx="10"/></clipPath>
<rect x="200" y="170" width="440" height="400" rx="10" fill="#1c3f8a"/>
<g clip-path="url(#D-clipW)"><g id="D-orbit" transform="translate(420 700)"><circle cx="0" cy="-470" r="46" fill="#ffd23e" filter="url(#D-glow)"/><circle cx="0" cy="470" r="38" fill="#e8f0ff"/></g></g>
<rect x="200" y="170" width="440" height="400" rx="10" fill="none" stroke="#6a7bd0" stroke-width="10"/><line x1="420" y1="170" x2="420" y2="570" stroke="#6a7bd0" stroke-width="8"/><line x1="200" y1="370" x2="640" y2="370" stroke="#6a7bd0" stroke-width="8"/>
<circle cx="820" cy="230" r="70" fill="#14122e" stroke="#8d7bff" stroke-width="6"/><g id="D-hand" transform="translate(820 230)"><line x1="0" y1="0" x2="0" y2="-52" stroke="#eef1f7" stroke-width="7" stroke-linecap="round"/></g><g id="D-hand2" transform="translate(820 230)"><line x1="0" y1="0" x2="34" y2="0" stroke="#ffb23e" stroke-width="9" stroke-linecap="round"/></g>
<rect x="880" y="610" width="720" height="40" rx="10" fill="#2a2a6a"/><rect x="900" y="560" width="680" height="60" rx="14" fill="#cfd5f5"/>
<rect x="900" y="520" width="160" height="60" rx="26" fill="#eef1ff"/>
<g id="D-blanket"><path d="M1080 560 C 1140 480 1300 480 1400 530 C 1470 560 1540 560 1580 580 L1580 620 L1080 620 Z" fill="#3a5fb0"/></g>
<rect x="880" y="650" width="40" height="130" fill="#2a2a6a"/><rect x="1580" y="650" width="40" height="130" fill="#2a2a6a"/>
<rect x="1640" y="320" width="230" height="320" rx="18" fill="#14122e" stroke="#8d7bff" stroke-width="6"/>
<clipPath id="D-cm"><rect x="1656" y="360" width="198" height="240" rx="8"/></clipPath><rect x="1656" y="360" width="198" height="240" rx="8" fill="#08071a"/>
<g clip-path="url(#D-cm)"><g id="D-ecg" transform="translate(1656 -250)"><path d="{ecg}" fill="none" stroke="{MINT}" stroke-width="5" stroke-linecap="round"/></g></g>
<rect id="D-night" x="200" y="170" width="440" height="400" rx="10" fill="#0a0a30" opacity="0"/></g>"""
    html = """<div id="D-l1" class="pill" style="left:72px;top:60px">UNITED KINGDOM · 2006</div>
<div id="D-l2" class="pill lilac" style="left:210px;top:610px;opacity:0"><span id="D-month">MONTH 1</span></div>
<div id="D-l3" class="pill red" style="left:880px;top:880px">VEGETATIVE STATE</div>"""
    js = """
  tl.fromTo("#D-l1",{opacity:0,y:-20},{opacity:1,y:0,duration:0.6},0.4);
  tl.fromTo("#D-rain",{y:0},{y:120,duration:0.5,repeat:16,ease:"none"},0);
  tl.fromTo("#D-stripe",{attr:{"stroke-dashoffset":0}},{attr:{"stroke-dashoffset":-150},duration:0.6,repeat:10,ease:"none"},0);
  tl.fromTo("#D-headlights",{scale:0.15,opacity:0.2,transformOrigin:"50% 50%"},{scale:3.4,opacity:1,transformOrigin:"50% 50%",duration:2.6,ease:"power3.in"},3.4);
  tl.fromTo("#D-flash",{opacity:0},{opacity:1,duration:0.08},6.0);
  tl.fromTo("#D-flash",{opacity:1},{opacity:0,duration:0.5,immediateRender:false},6.1);
  tl.fromTo("#D-headlights",{opacity:1},{opacity:0,duration:0.1,immediateRender:false},6.0);
  tl.fromTo("#D-sirenR",{opacity:0},{opacity:0.35,duration:0.22,repeat:7,yoyo:true,ease:"none"},6.4);
  tl.fromTo("#D-sirenB",{opacity:0},{opacity:0.35,duration:0.22,repeat:7,yoyo:true,ease:"none"},6.51);
  tl.fromTo("#D-road",{opacity:1},{opacity:0,duration:0.8,immediateRender:false},7.8);
  tl.fromTo("#D-l1",{opacity:1},{opacity:0,duration:0.4,immediateRender:false},6.0);
  tl.fromTo("#D-room",{opacity:0},{opacity:1,duration:0.8},7.8);
  tl.fromTo("#D-ecg",{x:1656},{x:1656-240,duration:0.9,repeat:14,ease:"none"},7.8);
  tl.fromTo("#D-blanket",{scaleY:1,transformOrigin:"50% 100%"},{scaleY:1.04,transformOrigin:"50% 100%",duration:1.1,repeat:7,yoyo:true,ease:"sine.inOut"},7.8);
  tl.fromTo("#D-orbit",{rotation:0},{rotation:1800,duration:5.2,ease:"none"},8.2);
  tl.fromTo("#D-hand",{rotation:0},{rotation:7200,duration:5.2,ease:"none"},8.2);
  tl.fromTo("#D-hand2",{rotation:0},{rotation:600,duration:5.2,ease:"none"},8.2);
  tl.fromTo("#D-l2",{opacity:0,y:20},{opacity:1,y:0,duration:0.4},8.2);
  var om={v:1};tl.fromTo(om,{v:1},{v:5.4,duration:5.0,ease:"none",onUpdate:function(){document.getElementById("D-month").textContent="MONTH "+Math.min(5,Math.floor(om.v));}},8.3);
  tl.fromTo("#D-l3",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},12.6);
"""
    return composition("D", d, svg, html, js)


def head_L():
    """Head profile (facing right) with brain, eye, ear and implant. Local box ~ 600x700."""
    outline = ("M 214 720 C 206 650 186 600 150 548 C 84 462 76 330 126 226 C 178 118 286 62 386 84 "
                "C 478 104 530 168 536 246 L 546 276 C 552 294 548 306 540 316 L 600 380 C 608 390 604 400 592 402 "
                "L 556 404 L 560 426 L 544 440 L 560 456 C 566 490 556 520 528 540 C 506 554 478 558 458 560 "
                "L 452 584 C 450 640 456 680 462 720 Z")
    return f"""<defs>
<linearGradient id="E-skin" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="720"><stop offset="0" stop-color="#4a4aa8"/><stop offset=".72" stop-color="#2c2c78"/><stop offset="1" stop-color="#2c2c78" stop-opacity="0"/></linearGradient>
<linearGradient id="E-stroke" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="720"><stop offset="0" stop-color="{LILAC}"/><stop offset=".74" stop-color="{LILAC}"/><stop offset="1" stop-color="{LILAC}" stop-opacity="0"/></linearGradient>
</defs>
<g id="E-head"><g transform="translate(300 190) scale(.98)">
<path d="{outline}" fill="url(#E-skin)" stroke="url(#E-stroke)" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>
<path d="M 470 262 Q 500 246 528 262" fill="none" stroke="#b9a8ff" stroke-width="7" stroke-linecap="round"/>
<ellipse cx="496" cy="296" rx="17" ry="12" fill="#f4f0ff"/><circle cx="502" cy="296" r="8" fill="#1a0f3a"/><circle cx="505" cy="292" r="2.6" fill="#fff"/>
<path d="M 392 318 C 358 300 346 372 380 396 C 406 410 424 362 404 340" fill="none" stroke="#9a8aff" stroke-width="7" stroke-linecap="round"/><path d="M 388 338 C 372 338 372 366 390 372" fill="none" stroke="#9a8aff" stroke-width="4" stroke-linecap="round" opacity=".8"/>
<path d="M 520 464 Q 540 470 552 462" fill="none" stroke="#8d7bff" stroke-width="5" stroke-linecap="round"/>
<g id="E-brain" opacity=".4" filter="url(#E-glow)">
<path d="M 176 262 C 156 168 250 118 346 128 C 440 122 506 172 490 250 C 496 306 450 336 404 332 C 360 350 252 346 212 322 C 180 306 172 282 176 262 Z" fill="{CYAN}" fill-opacity=".2" stroke="{CYAN}" stroke-width="6"/>
<g fill="none" stroke="{CYAN}" stroke-width="4.5" stroke-linecap="round" opacity=".95">
<path d="M 202 236 C 238 196 272 252 312 208 S 392 232 430 196 S 480 232 478 256"/>
<path d="M 196 284 C 238 256 274 306 320 270 S 394 296 440 266"/>
<path d="M 232 318 C 266 296 306 326 350 304 S 420 322 456 300"/>
<path d="M 292 138 C 280 176 306 190 296 226 M 380 134 C 368 170 396 184 384 222"/></g>
</g>
<g id="E-chip"><rect x="318" y="62" width="58" height="36" rx="10" fill="{AMBER}" filter="url(#E-glow)" transform="rotate(-8 347 80)"/></g>
</g></g>"""


# ---------------------------------------------------------------- Scene E: the cursor that obeys the brain
def scene_E():
    d = INFO["E"]
    targets = [(1240, 440), (1590, 400), (1500, 620), (1260, 610)]
    target_svg = "".join(f'<circle id="E-tgt{k}" cx="{x}" cy="{y}" r="38" fill="none" stroke="{CYAN}" stroke-width="6" opacity=".5"/><circle id="E-tgc{k}" cx="{x}" cy="{y}" r="12" fill="{CYAN}" opacity=".5"/>' for k, (x, y) in enumerate(targets))
    svg = head_L() + f"""<path id="E-wire" d="M646 268 C 800 150 1010 220 1100 480" fill="none" stroke="#5f6cff" stroke-width="6" opacity="0"/>
<path id="E-signal" d="M646 268 C 800 150 1010 220 1100 480" fill="none" stroke="#ffd23e" stroke-width="10" stroke-linecap="round" stroke-dasharray="36 200" opacity="0" filter="url(#E-glow)"/>
<g id="E-mon" opacity="0"><rect x="1100" y="270" width="660" height="460" rx="28" fill="#14122e" stroke="{LILAC}" stroke-width="6"/><rect x="1124" y="294" width="612" height="412" rx="12" fill="#0e0c26"/>
<rect x="1400" y="730" width="56" height="64" fill="#14122e" stroke="{LILAC}" stroke-width="4"/><rect x="1300" y="794" width="256" height="22" rx="11" fill="#14122e" stroke="{LILAC}" stroke-width="4"/>{target_svg}
<g id="E-pointer" transform="translate(1180 360)"><g id="E-pointerM"><path d="M0 0 L0 54 L16 40 L28 66 L40 60 L28 36 L50 36 Z" fill="#ffffff" stroke="#1a0f3a" stroke-width="3"/></g></g></g>"""
    html = """<div id="E-l1" class="pill amber" style="left:72px;top:60px">2024 · COMPANY DEMO</div>
<div id="E-l2" class="pill" style="left:400px;top:940px">BRAIN SIGNALS</div>"""
    ks = ",".join(f"[{x - 4},{y - 10}]" for x, y in targets)
    js = """
  tl.fromTo("#E-head",{x:-500,opacity:0},{x:0,opacity:1,duration:1.4,ease:"power3.out"},0.2);
  tl.fromTo("#E-brain",{opacity:0.4},{opacity:1,duration:0.8,repeat:15,yoyo:true,ease:"sine.inOut"},1.2);
  tl.fromTo("#E-chip",{scale:1,transformOrigin:"50% 50%"},{scale:1.35,transformOrigin:"50% 50%",duration:0.5,repeat:9,yoyo:true,ease:"sine.inOut"},1.8);
  tl.fromTo("#E-l1",{opacity:0,y:-20},{opacity:1,y:0,duration:0.6},3.6);
  tl.fromTo("#E-mon",{x:700,opacity:0},{x:0,opacity:1,duration:1.4,ease:"power3.out"},3.0);
  tl.fromTo("#E-wire",{opacity:0},{opacity:0.9,duration:0.6},4.4);
  tl.fromTo("#E-signal",{opacity:0,attr:{"stroke-dashoffset":0}},{opacity:1,attr:{"stroke-dashoffset":-236},duration:0.8,repeat:11,ease:"none"},5.0);
  tl.fromTo("#E-l2",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},5.6);
  var P=[@TARGETS@], t0=9.0, seg=0.675;
  var cx=[1180],cy=[360];
  P.forEach(function(p){cx.push(p[0],p[0]);cy.push(p[1],p[1]);});
  tl.set("#E-pointer",{x:1180,y:360},0);
  tl.to("#E-pointer",{keyframes:{x:cx,y:cy,easeEach:"power2.inOut"},duration:seg*cx.length-seg,ease:"none"},t0);
  for(var k=0;k<P.length;k++){
    var ta=t0+(2*k+1)*seg;
    tl.fromTo("#E-tgt"+k,{scale:1,opacity:0.5,transformOrigin:"50% 50%"},{scale:1.6,opacity:1,transformOrigin:"50% 50%",duration:0.3,ease:"back.out(3)"},ta);
    tl.fromTo("#E-tgc"+k,{opacity:0.5,scale:1,transformOrigin:"50% 50%"},{opacity:1,scale:2.2,transformOrigin:"50% 50%",duration:0.3},ta);
  }
""".replace("@TARGETS@", ks)
    return composition("E", d, svg, html, js)


# ---------------------------------------------------------------- Scene F: server corridor and the questions
def scene_F():
    d = INFO["F"]
    vx, vy = 960, 500
    def wall_points(side, u0, u1):
        # left wall (side=-1) or right wall (+1): interpolates from the screen edge to the background
        def p(u, v):
            xb = 960 + side * 960; xf = 960 + side * 120
            yt0, yb0 = 0, 1080; yt1, yb1 = 420, 580
            x = xb + (xf - xb) * u
            yt = yt0 + (yt1 - yt0) * u; yb = yb0 + (yb1 - yb0) * u
            return x, yt + (yb - yt) * v
        return p
    panels = []; leds = []
    for side in (-1, 1):
        p = wall_points(side, 0, 1)
        us = [1 - 1 / (1 + 0.55 * i) for i in range(0, 13)]
        for i in range(len(us) - 1):
            a, b = us[i], us[i + 1]
            q = [p(a, 0.04), p(b, 0.04), p(b, 0.96), p(a, 0.96)]
            panels.append(f'<polygon points="{" ".join(f"{x:.0f},{y:.0f}" for x, y in q)}" fill="#171548" stroke="#3a3aa0" stroke-width="3"/>')
            for r in range(9):
                for c in range(3):
                    uu = a + (b - a) * (0.2 + 0.3 * c); vv = 0.12 + 0.1 * r
                    x, y = p(uu, vv)
                    size = max(2.0, 18 * (1 - uu) ** 1.3)
                    color = CYAN if (i + r + c) % 4 else (AMBER if (r + c) % 2 else MAGENTA)
                    leds.append(f'<rect class="led" x="{x - size:.1f}" y="{y - size * 0.5:.1f}" width="{size * 2:.1f}" height="{size:.1f}" fill="{color}"/>')
    marks = "".join(f'<text id="F-q{k}" x="{x}" y="{y}" text-anchor="middle" font-size="{s}" font-weight="700" fill="{c}" opacity="0" filter="url(#F-glow)">?</text>' for k, (x, y, s, c) in enumerate([(960, 560, 360, AMBER), (560, 520, 260, CYAN), (1380, 560, 300, MAGENTA)]))
    svg = f"""<rect y="580" width="1920" height="500" fill="#0d0b30"/><polygon points="0,1080 960,580 1920,1080" fill="#14123c"/>
<g id="F-cam"><g>{"".join(panels)}</g><g>{"".join(leds)}</g></g>{marks}"""
    js = """
  tl.fromTo("#F-cam",{scale:1,svgOrigin:"960 500"},{scale:2.4,svgOrigin:"960 500",duration:8.0,ease:"sine.inOut"},0);
  tl.fromTo("#F-cam .led",{opacity:1},{opacity:0.15,duration:0.18,repeat:30,yoyo:true,ease:"steps(1)",stagger:{each:0.021,from:"random"}},0.2);
  tl.fromTo("#F-q0",{opacity:0,scale:0.3,transformOrigin:"50% 50%"},{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.5,ease:"back.out(3)"},0.4);
  tl.fromTo("#F-q0",{opacity:1},{opacity:0,duration:0.4,immediateRender:false},2.6);
  tl.fromTo("#F-q1",{opacity:0,scale:0.3,transformOrigin:"50% 50%"},{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.5,ease:"back.out(3)"},2.8);
  tl.fromTo("#F-q1",{opacity:1},{opacity:0,duration:0.4,immediateRender:false},4.7);
  tl.fromTo("#F-q2",{opacity:0,scale:0.3,transformOrigin:"50% 50%"},{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.5,ease:"back.out(3)"},4.9);
"""
    return composition("F", d, svg, "", js)


SCENES = [("A", scene_A, START["A"], INFO["A"]), ("B", scene_B, START["B"], INFO["B"]), ("D", scene_D, START["D"], INFO["D"]),
         ("E", scene_E, START["E"], INFO["E"]), ("F", scene_F, START["F"], INFO["F"]), ("C", scene_C, START["C1"], INFO["C1"] + GAP + INFO["C2"])]


def main():
    os.makedirs(os.path.join(HERE, "compositions"), exist_ok=True)
    hosts = []
    total = max(i + d for _, _, i, d in SCENES)
    for k, fn, start, dur in SCENES:
        open(os.path.join(HERE, f"compositions/{k}.html"), "w").write(fn())
        hosts.append(f'<div id="{k}" data-composition-id="{k}" data-composition-src="compositions/{k}.html" data-start="{start:.2f}" data-duration="{dur:.2f}" data-track-index="1" data-width="1920" data-height="1080"></div>')
    open(os.path.join(HERE, "index.html"), "w").write(f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@700&family=IBM+Plex+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#0b0a24}}#root{{width:100%;height:100%;position:relative}}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}" data-width="1920" data-height="1080">
{chr(10).join(hosts)}
<audio id="voice" src="assets/voice.wav" data-start="0" data-duration="{total:.2f}" data-track-index="2" data-volume="1"></audio>
<audio id="music" src="assets/music.mp3" data-start="0" data-duration="{total:.2f}" data-track-index="3" data-volume="0.14" data-fade-in="2" data-fade-out="3"></audio>
</div><script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script></body></html>
""")
    print("ok, total", round(total, 2), "s")


if __name__ == "__main__":
    main()
