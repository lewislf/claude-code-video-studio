"""v3 scenes, second round: richer drawing (layers, light, volume, character, camera with depth).

  python3 build2.py

Scenes not yet redone come from build.py. Each redone scene goes through the critic before reaching the user.
"""
import json, math, os, random
import build as b0
from build import HERE, INFO, START, GAP, CYAN, MAGENTA, AMBER, MINT, LILAC, RED, network, path_d

CSS2 = b0.CSS + """
.title{position:absolute;font:700 132px "EB Garamond",serif;color:#eef1f7;opacity:0;text-shadow:0 6px 40px rgba(0,0,0,.7);white-space:nowrap;letter-spacing:.02em}
.title small{display:block;font:500 30px "IBM Plex Mono",monospace;letter-spacing:.2em;color:#ffb23e;margin-top:-4px}
.pill2{position:absolute;font:500 36px "IBM Plex Mono",monospace;letter-spacing:.14em;color:#eef1f7;opacity:0;white-space:nowrap;text-shadow:0 4px 24px #000}
.pill2 i{display:inline-block;width:18px;height:18px;border-radius:50%;margin-right:14px;vertical-align:-2px}
"""


def bokeh(i, seed, n=10, colors=("#3be0ff", "#8d7bff", "#ff4fa3", "#ffb23e")):
    rng = random.Random(seed)
    c = "".join(f'<circle cx="{rng.uniform(0, 1920):.0f}" cy="{rng.uniform(0, 1080):.0f}" r="{rng.uniform(90, 280):.0f}" fill="{rng.choice(colors)}" opacity="{rng.uniform(.06, .15):.2f}"/>' for _ in range(n))
    return f'<g id="{i}-bokeh" filter="url(#{i}-blur40)">{c}</g>'


def defs2(i, extra="", background=("#3a1d7a", "#1a1050", "#0b0a24"), seed=3):
    return f"""<defs>
<radialGradient id="{i}-background" cx="50%" cy="46%" r="78%"><stop offset="0" stop-color="{background[0]}"/><stop offset=".55" stop-color="{background[1]}"/><stop offset="1" stop-color="{background[2]}"/></radialGradient>
<radialGradient id="{i}-vig" cx="50%" cy="50%" r="72%"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".62"/></radialGradient>
<filter id="{i}-glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="{i}-blur40" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="42"/></filter>
<filter id="{i}-blur6" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="{i}-shadow" x="-30%" y="-30%" width="170%" height="180%"><feDropShadow dx="0" dy="16" stdDeviation="16" flood-color="#05031a" flood-opacity=".6"/></filter>
{extra}</defs>
<rect width="1920" height="1080" fill="url(#{i}-background)"/>{bokeh(i, seed)}<g id="{i}-part"></g>"""


def composition2(i, dur, body_svg, html, js, extra_defs="", background=("#3a1d7a", "#1a1050", "#0b0a24"), seed=3):
    js = js.replace("@ID@", i).replace("@DUR@", f"{dur:.2f}")
    return f"""<template>
  <style>{CSS2}</style>
  <div id="{i}-root" data-composition-id="{i}" data-width="1920" data-height="1080">
    <div class="scene">
    <svg id="{i}-svg" class="full" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">{defs2(i, extra_defs, background, seed)}{body_svg}<rect width="1920" height="1080" fill="url(#{i}-vig)" pointer-events="none"/></svg>
    {html}
    <div id="{i}-black" class="black"></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {b0.DUST.replace("@ID@", i).replace("@DUR@", f"{dur:.2f}")}
    tl.fromTo("#{i}-bokeh",{{x:0,y:0}},{{x:-70,y:-34,duration:{dur:.2f},ease:"none"}},0);
    {js}
    tl.fromTo("#{i}-black", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.4, ease: "none" }}, 0);
    tl.fromTo("#{i}-black", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "none", immediateRender: false }}, {dur - 0.4:.2f});
    window.__timelines["{i}"] = tl;
  </script>
</template>
"""


# ---------------------------------------------------------------- rich pieces
def fly_rich(p, prefix="A"):
    facets = "".join(f'<circle cx="{74 + dx}" cy="{-8 + dy}" r="3.2" fill="#8c1230" opacity=".55"/>' for dx in (-10, 0, 10, 20) for dy in (-18, -6, 6, 18) if (dx - 5) ** 2 + (dy) ** 2 < 360)
    bristles = "".join(f'<path d="M{-6 + k * 9} {-26 - (k % 2) * 2} l{2 + k % 3} -9" />' for k in range(8))
    return f"""<g id="{p}">
<g id="{p}-wings" filter="url(#{prefix}-shadow)">
<ellipse cx="-14" cy="-74" rx="126" ry="40" fill="url(#{prefix}-wing)" transform="rotate(-26 -14 -74)" stroke="#fff" stroke-opacity=".6" stroke-width="2.5"/>
<path d="M-120 -40 L 82 -108 M -96 -56 L 52 -104 M -80 -34 L 36 -82" stroke="#fff" stroke-opacity=".5" stroke-width="2.4" fill="none"/>
<ellipse cx="-4" cy="-62" rx="104" ry="32" fill="url(#{prefix}-wing)" opacity=".75" transform="rotate(-10 -4 -62)"/></g>
<g stroke="#2a1a3a" stroke-width="8" stroke-linecap="round" fill="none"><path d="M-6 26 Q-14 52 -30 74"/><path d="M14 30 Q18 54 14 80"/><path d="M36 24 Q50 48 70 66"/><path d="M-32 30 Q-48 54 -66 70"/></g>
<ellipse cx="-47" cy="11" rx="60" ry="38" fill="#ff3b6b" opacity=".85"/><ellipse cx="-61" cy="2" rx="60" ry="38" fill="#35e6a6" opacity=".85"/>
<path d="M-112 4 C-112 -30 -80 -40 -48 -40 C-6 -40 10 -14 10 8 C10 34 -24 48 -58 48 C-92 48 -112 32 -112 4 Z" fill="url(#{prefix}-abd)"/>
<path d="M-98 -18 Q-84 8 -98 32 M-74 -34 Q-58 8 -74 44 M-48 -38 Q-32 8 -48 46" stroke="#3a2412" stroke-width="8" fill="none" stroke-linecap="round" opacity=".9"/>
<ellipse cx="-30" cy="-20" rx="56" ry="9" fill="#fff" opacity=".22"/>
<ellipse cx="12" cy="-4" rx="44" ry="36" fill="url(#{prefix}-trunk)"/><g stroke="#3a2412" stroke-width="2.4" fill="none" stroke-linecap="round" opacity=".7">{bristles}</g>
<g id="{p}-head"><circle id="{p}-headC" cx="64" cy="-2" r="34" fill="url(#{prefix}-trunk)"/>
<path d="M82 -30 Q104 -56 126 -52" stroke="#3a2412" stroke-width="5" fill="none" stroke-linecap="round"/><circle cx="128" cy="-52" r="6" fill="#3a2412"/>
<ellipse id="{p}-eye" cx="74" cy="-8" rx="26" ry="28" fill="url(#{prefix}-eye)"/>{facets}
<ellipse cx="84" cy="-20" rx="9" ry="7" fill="#fff" opacity=".75"/>
<ellipse id="{p}-brainDot" cx="56" cy="-2" rx="9" ry="8" fill="#3be0ff" opacity="0" filter="url(#{prefix}-glow)"/>
<path id="{p}-proboscis" d="M98 8 q 14 6 20 20" stroke="#2a1a3a" stroke-width="7" fill="none" stroke-linecap="round"/></g></g>"""


def fly_defs(prefix):
    return f"""<linearGradient id="{prefix}-abd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6d79c"/><stop offset="1" stop-color="#c98d48"/></linearGradient>
<radialGradient id="{prefix}-trunk" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#f2b872"/><stop offset="1" stop-color="#b66f2c"/></radialGradient>
<radialGradient id="{prefix}-eye" cx="40%" cy="30%" r="80%"><stop offset="0" stop-color="#ff6a82"/><stop offset=".6" stop-color="#e23352"/><stop offset="1" stop-color="#8c1230"/></radialGradient>
<linearGradient id="{prefix}-wing" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e8f4ff" stop-opacity=".85"/><stop offset="1" stop-color="#a8c8ff" stop-opacity=".35"/></linearGradient>
<filter id="{prefix}-shadowF" x="-30%" y="-30%" width="170%" height="180%"><feDropShadow dx="0" dy="16" stdDeviation="16" flood-color="#05031a" flood-opacity=".6"/></filter>"""


def network_rich(p, seed, n=170, prefix="A"):
    pts, edges = network(seed, n, 40)
    layer = [k % 3 for k in range(len(pts))]
    edge_svg = []
    for a, bb in edges:
        c = max(layer[a], layer[bb])
        edge_svg.append(f'<line class="ed{c}" x1="{pts[a][0]}" y1="{pts[a][1]}" x2="{pts[bb][0]}" y2="{pts[bb][1]}"/>')
    nodes = []
    colors = [CYAN, "#5fb7ff", LILAC, MAGENTA, CYAN, "#7be8ff"]
    for k, (x, y) in enumerate(pts):
        c = layer[k]
        r = (4, 7, 11)[c]
        nodes.append(f'<circle class="node n{c}" cx="{x}" cy="{y}" r="{r}" fill="{colors[k % 6]}"/>')
    lobe_svg = '<path vector-effect="non-scaling-stroke" transform="scale(2.05 2.8)" d="M-210 10 C-220 -50 -170 -100 -110 -96 C-80 -116 -30 -112 0 -104 C30 -112 80 -116 110 -96 C170 -100 220 -50 210 10 C210 60 160 96 100 90 C60 104 20 100 0 92 C-20 100 -60 104 -100 90 C-160 96 -210 60 -210 10 Z"/>'
    return (f'<g id="{p}"><rect x="-440" y="-290" width="880" height="580" fill="none"/>'
            f'<g class="lobe" fill="url(#{prefix}-lobe)" stroke="#7fdcff" stroke-opacity=".85" stroke-width="4" opacity="0">{lobe_svg}</g>'
            f'<g class="eds" opacity="0"><g class="e0" stroke="#4a5aff" stroke-width="1.6" opacity=".4">{"".join(e for e in edge_svg if "ed0" in e)}</g>'
            f'<g class="e1" stroke="#6a7cff" stroke-width="2.4" opacity=".65">{"".join(e for e in edge_svg if "ed1" in e)}</g>'
            f'<g class="e2" stroke="#8fa6ff" stroke-width="3.4" opacity=".9">{"".join(e for e in edge_svg if "ed2" in e)}</g></g>'
            f'<g class="g0" opacity=".5">{"".join(x for x in nodes if "n0" in x)}</g><g class="g1">{"".join(x for x in nodes if "n1" in x)}</g>'
            f'<g class="g2" filter="url(#{prefix}-glow)">{"".join(x for x in nodes if "n2" in x)}</g></g>'), pts, edges


from art2 import fly_rich, fly_defs, brain_card
PTS_R, EDGES_R = None, None


def scene_A2():
    global PTS_R, EDGES_R
    d = INFO["A"]
    extra = fly_defs("A") + """
<radialGradient id="A-brain" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#1c6fa0" stop-opacity=".9"/><stop offset="1" stop-color="#0c2e66" stop-opacity=".95"/></radialGradient>
<radialGradient id="A-poppyFill" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#5a4a8c"/><stop offset="1" stop-color="#1a1238"/></radialGradient>
<radialGradient id="A-lobe" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="#3b5bff" stop-opacity=".28"/><stop offset="1" stop-color="#3b5bff" stop-opacity=".04"/></radialGradient>
<linearGradient id="A-land1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2c2a92"/><stop offset="1" stop-color="#1a3a86"/></linearGradient>
<linearGradient id="A-land2" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#3a2a9c"/><stop offset="1" stop-color="#24307f"/></linearGradient>
<radialGradient id="A-pin" cx="40%" cy="30%" r="80%"><stop offset="0" stop-color="#ffe08a"/><stop offset="1" stop-color="#ff8a2a"/></radialGradient>
<radialGradient id="A-fruit" cx="38%" cy="30%" r="80%"><stop offset="0" stop-color="#ffc35a"/><stop offset=".6" stop-color="#ff8a2a"/><stop offset="1" stop-color="#d9501c"/></radialGradient>"""
    grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="1080"/>' for x in range(0, 1921, 120)) + "".join(f'<line x1="0" y1="{y}" x2="1920" y2="{y}"/>' for y in range(0, 1081, 120))
    pins_pos = [(520, 740), (860, 800), (1240, 590), (1580, 660)]
    pins = "".join(
        f'<g id="A-pin{k}"><g transform="translate({x} {y}) scale(2.0)" filter="url(#A-shadow)"><path d="M0 0 C-34 -44 -42 -78 0 -96 C42 -78 34 -44 0 0 Z" fill="url(#A-pin)"/>'
        f'<circle cy="-58" r="25" fill="#1a1050"/><text y="-47" text-anchor="middle" font-size="34" font-weight="700" fill="#ffd27a">?</text><ellipse cx="-12" cy="-80" rx="8" ry="14" fill="#fff" opacity=".4" transform="rotate(20 -12 -80)"/></g></g>'
        for k, (x, y) in enumerate(pins_pos))
    route = '<polyline id="A-route" points="140,860 520,740 860,800 1240,590 1580,660 1820,400" fill="none" stroke="#6a8cff" stroke-width="14" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="2400" stroke-dashoffset="2400" filter="url(#A-glow)"/>'
    terrain = ('<g filter="url(#A-blur6)"><path d="M-40 780 C 240 640 480 860 760 740 C 1040 620 1320 820 1620 640 C 1780 560 1900 600 1980 560 L1980 1120 L-40 1120 Z" fill="url(#A-land1)" opacity=".85"/>'
               '<path d="M-40 380 C 300 260 540 440 860 330 C 1180 220 1440 400 1980 260 L1980 -40 L-40 -40 Z" fill="url(#A-land2)" opacity=".7"/></g>')
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#8a78d0" opacity=".55"/>' for x, y, r in [(-60,-30,7),(10,-50,6),(70,10,8),(-20,30,6),(40,50,7),(-90,20,5),(20,0,5)])
    seed_svg = (f'<ellipse cx="0" cy="124" rx="150" ry="18" fill="#05031a" opacity=".45"/><g filter="url(#A-shadow)"><path d="M-140 0 C-140 -92 -60 -122 20 -114 C100 -106 150 -60 140 6 C130 74 60 112 -20 108 C-100 104 -140 70 -140 0 Z" fill="url(#A-poppyFill)" stroke="#b9a8ff" stroke-width="5" filter="url(#A-glow)"/>'
               f'<path d="M-96 -52 C-60 -92 10 -100 60 -86" stroke="#fff" stroke-opacity=".35" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M-30 -30 C-10 0 -10 40 -30 70" stroke="#0e0828" stroke-width="7" fill="none" stroke-linecap="round" opacity=".7"/>{dots}</g>')
    fruit = ('<g id="A-fruit" opacity="0"><g transform="translate(330 800)"><ellipse cx="0" cy="205" rx="220" ry="22" fill="#05031a" opacity=".35"/>'
             '<circle r="200" fill="url(#A-fruit)" filter="url(#A-shadow)"/><ellipse cx="-64" cy="-72" rx="50" ry="86" fill="#fff" opacity=".28" transform="rotate(28 -64 -72)"/>'
             '<path d="M0 -192 C-6 -232 16 -256 42 -266" stroke="#4b7a2a" stroke-width="16" fill="none" stroke-linecap="round"/><path d="M24 -236 C88 -272 152 -240 136 -200 C96 -200 56 -210 24 -236 Z" fill="#58b84a"/></g></g>')
    network_svg, PTS_R, EDGES_R = network_rich("A-r", 11)
    left = min(range(len(PTS_R)), key=lambda k: PTS_R[k][0] + 0.3 * PTS_R[k][1])
    paths = []
    rng = random.Random(4)
    for _ in range(5):
        a_, b_ = rng.sample(range(len(PTS_R)), 2)
        c = path_d(PTS_R, EDGES_R, a_, b_)
        if len(c) > 4:
            paths.append(c)
    svg = f"""<g id="A-streetmap" opacity="0">{terrain}<g stroke="#4a4ad0" stroke-width="2" opacity=".28">{grid}</g>{route}{pins}</g>
<g id="A-cam">{fruit}<g transform="translate(960 540)"><g id="A-fly"><g transform="scale(2.3)"><g id="A-flyBob">{fly_rich("A-mo")}</g></g></g></g>
</g>
<g id="A-stage" opacity="0"><g transform="translate(600 480)"><g id="A-bcA"><g transform="scale(.62)">{brain_card("A-bc")}</g></g></g><g transform="translate(1400 490) scale(1.9)"><g id="A-poppy">{seed_svg}</g></g></g>
<g id="A-link" opacity="0"><path d="M1004 350 C 1004 430 1064 470 1086 516" fill="none" stroke="#3be0ff" stroke-width="4" stroke-dasharray="10 8" stroke-linecap="round"/></g>
<g transform="translate(960 540)"><g id="A-netX"><g id="A-network">{network_svg}</g><circle id="A-pulse" r="12" fill="#ffd23e" filter="url(#A-glow)" opacity="0"/></g></g>"""
    html = """<div id="A-t1" class="title" style="left:420px;right:0;text-align:center;top:800px">fruit fly</div>
<div id="A-l2" class="pill2" style="left:320px;width:560px;text-align:center;top:800px;font-size:46px"><i style="background:#3be0ff"></i>BRAIN</div>
<div id="A-l3" class="pill2" style="left:1060px;width:680px;text-align:center;top:800px;font-size:46px"><i style="background:#9a8cff"></i>POPPY SEED</div>
<div id="A-n1" class="num" style="left:90px;top:780px;font-size:150px"><span id="A-n1v">0</span><small>NEURONS</small></div>
<div id="A-n2" class="num" style="right:90px;top:780px;text-align:right;font-size:150px"><span id="A-n2v">0</span><small>CONNECTIONS</small></div>"""
    js = """
  tl.fromTo("#A-streetmap",{opacity:0},{opacity:1,duration:1.0},0.2);
  tl.fromTo("#A-route",{attr:{"stroke-dashoffset":2400}},{attr:{"stroke-dashoffset":0},duration:4.2,ease:"power1.inOut"},0.8);
  [0,1,2,3].forEach(function(k){
    tl.fromTo("#A-pin"+k,{y:-420,opacity:0,scaleY:1,transformOrigin:"50% 100%"},{y:0,opacity:1,duration:0.7,ease:"bounce.out"},1.2+k*0.95);
    tl.fromTo("#A-pin"+k,{scaleY:1,scaleX:1},{scaleY:0.82,scaleX:1.12,duration:0.1,repeat:1,yoyo:true,ease:"power2.out",immediateRender:false},1.2+k*0.95+0.55);
  });
  tl.fromTo("#A-streetmap",{scale:1,svgOrigin:"960 540"},{scale:0.55,svgOrigin:"960 540",duration:1.2,ease:"power2.in",immediateRender:false},5.2);
  tl.fromTo("#A-streetmap",{opacity:1},{opacity:0,duration:1.0,immediateRender:false},5.5);
  tl.fromTo("#A-fruit",{opacity:0,scale:0.4,svgOrigin:"330 800"},{opacity:1,scale:1,svgOrigin:"330 800",duration:1.2,ease:"back.out(1.6)"},5.8);
  var fx=[1500,980,380,-380,-120,0], fy=[-420,-280,-130,-170,-90,0];
  tl.set("#A-fly",{x:fx[0],y:fy[0]},0);
  tl.to("#A-fly",{keyframes:{x:fx,y:fy,easeEach:"sine.inOut"},duration:3.0,ease:"none"},6.0);
  tl.fromTo("#A-flyBob",{y:0,rotation:-3,transformOrigin:"50% 50%"},{y:-8,rotation:2.5,transformOrigin:"50% 50%",duration:0.5,repeat:9,yoyo:true,ease:"sine.inOut"},9.0);
  tl.fromTo("#A-mo-wings",{scaleY:1,transformOrigin:"50% 100%"},{scaleY:0.28,transformOrigin:"50% 100%",duration:0.05,repeat:230,yoyo:true,ease:"none"},6.0);
  tl.fromTo("#A-t1",{opacity:0,y:30},{opacity:1,y:0,duration:0.7,ease:"power3.out"},8.8);
  tl.fromTo("#A-t1",{opacity:1},{opacity:0,duration:0.4,immediateRender:false},11.3);
  tl.fromTo("#A-fruit",{opacity:1},{opacity:0,duration:0.5,immediateRender:false},11.0);
  tl.fromTo("#A-cam",{scale:1,svgOrigin:"1103 535"},{scale:1.7,svgOrigin:"1103 535",duration:2.6,ease:"power2.inOut"},11.8);
  tl.fromTo("#A-cam",{opacity:1},{opacity:0,duration:0.6,immediateRender:false},14.2);
  tl.fromTo("#A-stage",{opacity:0},{opacity:1,duration:0.6,immediateRender:false},14.6);
  tl.fromTo("#A-bcA",{x:503,y:55,scale:0.15,transformOrigin:"50% 50%"},{x:0,y:0,scale:1,transformOrigin:"50% 50%",duration:1.0,ease:"back.out(1.4)",immediateRender:false},14.6);
  tl.fromTo("#A-poppy",{scale:0.2,transformOrigin:"50% 50%"},{scale:1,transformOrigin:"50% 50%",duration:0.9,ease:"back.out(1.4)",immediateRender:false},15.2);
  tl.fromTo("#A-bc",{scale:1,transformOrigin:"50% 50%"},{scale:1.04,transformOrigin:"50% 50%",duration:0.8,repeat:5,yoyo:true,ease:"sine.inOut",immediateRender:false},16.0);
  tl.fromTo("#A-l2",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},15.8);
  tl.fromTo("#A-l3",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},16.2);
  tl.fromTo("#A-l2",{opacity:1},{opacity:0,duration:0.4,immediateRender:false},18.0);
  tl.fromTo("#A-l3",{opacity:1},{opacity:0,duration:0.4,immediateRender:false},18.0);
  tl.fromTo("#A-stage",{opacity:1},{opacity:0,duration:0.8,immediateRender:false},18.2);
  tl.fromTo("#A-network",{x:-320,y:-20,scale:0.3,rotation:-6,transformOrigin:"50% 50%"},{x:0,scale:0.9,y:-30,rotation:0,transformOrigin:"50% 50%",duration:4.5,ease:"power2.out"},18.4);
  tl.fromTo("#A-r .lobe",{opacity:0},{opacity:1,duration:1.6},18.6);
  tl.fromTo("#A-r .eds",{opacity:0},{opacity:1,duration:1.8},18.9);
  tl.fromTo("#A-r .node",{scale:0,transformOrigin:"50% 50%"},{scale:1,transformOrigin:"50% 50%",duration:0.45,ease:"back.out(2.4)",stagger:{each:0.011}},18.6);
  var P=@PATHS@;
  P.forEach(function(c,k){
    var xs=c.map(function(p){return p[0];}), ys=c.map(function(p){return p[1];});
    var id="A-pl"+k; var el=document.createElementNS("http://www.w3.org/2000/svg","circle");
    el.setAttribute("id",id);el.setAttribute("r","12");el.setAttribute("fill","#ffd23e");el.setAttribute("filter","url(#A-glow)");el.setAttribute("opacity","0");
    document.getElementById("A-netX").appendChild(el);
    tl.set("#"+id,{x:xs[0],y:ys[0]},0);
    [0,1].forEach(function(r){
      var t0=22.0+k*0.55+r*3.4;
      tl.fromTo("#"+id,{opacity:0},{opacity:1,duration:0.15},t0);
      tl.to("#"+id,{keyframes:{x:xs,y:ys,easeEach:"none"},duration:2.4,ease:"none",immediateRender:false},t0);
      tl.fromTo("#"+id,{opacity:1},{opacity:0,duration:0.2,immediateRender:false},t0+2.3);
    });
  });
  tl.fromTo("#A-n1",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},24.2);
  var o1={v:0};tl.fromTo(o1,{v:0},{v:139255,duration:2.6,ease:"power2.out",onUpdate:function(){document.getElementById("A-n1v").textContent=Math.round(o1.v).toLocaleString("en-US");}},24.4);
  tl.fromTo("#A-n2",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},26.8);
  var o2={v:0};tl.fromTo(o2,{v:0},{v:50,duration:1.8,ease:"power2.out",onUpdate:function(){document.getElementById("A-n2v").textContent="≈ "+Math.round(o2.v)+" million";}},27.0);
""".replace("@PATHS@", json.dumps(paths))
    return composition2("A", d, svg, html, js, extra, background=("#3a1d7a", "#1a1050", "#0b0a24"), seed=3)



# ---------------------------------------------------------------- Scene B: the simulated brain and the fly that reacts
def scene_B2():
    d = INFO["B"]
    extra = fly_defs("B") + """
<radialGradient id="B-lobe" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="#3b5bff" stop-opacity=".3"/><stop offset="1" stop-color="#3b5bff" stop-opacity=".05"/></radialGradient>
<linearGradient id="B-bezel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a4a9a"/><stop offset="1" stop-color="#1b1b4a"/></linearGradient>
<linearGradient id="B-screen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16143a"/><stop offset="1" stop-color="#0a1a3a"/></linearGradient>
<radialGradient id="B-bloom" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#3be0ff" stop-opacity=".55"/><stop offset="1" stop-color="#3be0ff" stop-opacity="0"/></radialGradient>
<linearGradient id="B-stand" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a3a8a"/><stop offset="1" stop-color="#1a1a48"/></linearGradient>"""
    network_svg, pts, edges = network_rich("B-r", 11, prefix="B")
    left = min(range(len(pts)), key=lambda k: pts[k][0] + 0.3 * pts[k][1])
    right = max(range(len(pts)), key=lambda k: pts[k][0] - 0.3 * pts[k][1])
    path = path_d(pts, edges, left, right)
    fx, fy, fe = 800, 440, 0.44          # where the network ends (screen center) and its scale
    gx, gy = fx + pts[right][0] * fe, fy + pts[right][1] * fe
    svg = f"""<g id="B-mon" opacity="0"><g transform="translate(-530 0)"><g filter="url(#B-shadow)">
<rect x="960" y="190" width="740" height="540" rx="38" fill="url(#B-bezel)" stroke="#8d7bff" stroke-width="4"/>
<rect x="986" y="216" width="688" height="488" rx="20" fill="url(#B-screen)"/>
<path d="M986 216 L 1260 216 L 1040 704 L 986 704 Z" fill="#fff" opacity=".05"/>
<circle cx="1330" cy="712" r="5" fill="#38e8a8" id="B-led" opacity=".3"/>
<rect x="1290" y="730" width="80" height="80" fill="url(#B-stand)"/><rect x="1180" y="806" width="300" height="26" rx="13" fill="url(#B-stand)" stroke="#8d7bff" stroke-width="3"/></g>
<ellipse id="B-bloom" cx="1330" cy="460" rx="520" ry="400" fill="url(#B-bloom)" opacity="0"/>
<g stroke="#3a3a8a" stroke-width="3" opacity=".55" fill="none"><line x1="1010" y1="240" x2="1010" y2="680"/><line x1="1010" y1="256" x2="1100" y2="256"/><line x1="1010" y1="296" x2="1080" y2="296"/><line x1="1010" y1="336" x2="1110" y2="336"/></g></g></g>
<g transform="translate(960 540)"><g id="B-netX"><g id="B-network">{network_svg}<circle id="B-pulse" r="30" fill="#ffd23e" filter="url(#B-glow)" opacity="0"/>
<circle id="B-start" cx="{pts[left][0]}" cy="{pts[left][1]}" r="58" fill="none" stroke="{AMBER}" stroke-width="14" opacity="0"/>
<circle id="B-end" cx="{pts[right][0]}" cy="{pts[right][1]}" r="58" fill="none" stroke="{MINT}" stroke-width="14" opacity="0"/></g></g></g>
<path id="B-bridge" d="M{gx:.0f} {gy:.0f} C {gx + 300:.0f} {gy - 40:.0f} 1260 600 1462 592" fill="none" stroke="{MINT}" stroke-width="7" stroke-dasharray="700" stroke-dashoffset="700" stroke-linecap="round" filter="url(#B-glow)"/>
<g transform="translate(1600 600)"><g id="B-fly"><g transform="scale(-1.5 1.5)"><g id="B-flyBob">{fly_rich("B-mo", "B")}</g></g></g></g>
<g id="B-sparks" opacity="0" fill="#ffd23e" filter="url(#B-glow)"><circle cx="1400" cy="560" r="9"/><circle cx="1372" cy="590" r="6"/><circle cx="1386" cy="626" r="8"/><circle cx="1350" cy="548" r="5"/><circle cx="1344" cy="640" r="6"/><circle cx="1410" cy="520" r="5"/><circle cx="1330" cy="600" r="4"/><circle cx="1405" cy="668" r="6"/></g>"""
    html = '<div id="B-l1" class="pill2" style="left:440px;width:720px;text-align:center;top:100px;font-size:44px"><i style="background:#3be0ff"></i>SIMULATED BRAIN</div>'
    js = """
  tl.fromTo("#B-network",{scale:0.2,opacity:0,transformOrigin:"50% 50%"},{scale:1.0,opacity:1,transformOrigin:"50% 50%",duration:1.6,ease:"power2.out"},0.2);
  tl.fromTo("#B-r .lobe",{opacity:0},{opacity:1,duration:1.0},0.3);
  tl.fromTo("#B-r .eds",{opacity:0},{opacity:1,duration:1.2},0.5);
  tl.fromTo("#B-r .node",{scale:0,transformOrigin:"50% 50%"},{scale:1,transformOrigin:"50% 50%",duration:0.4,ease:"back.out(2.4)",stagger:{each:0.006}},0.2);
  tl.fromTo("#B-netX",{x:0},{x:-440,duration:1.6,ease:"power2.inOut"},2.2);
  tl.fromTo("#B-network",{scale:1.0,transformOrigin:"50% 50%"},{scale:0.6,transformOrigin:"50% 50%",duration:1.6,ease:"power2.inOut",immediateRender:false},2.2);
  tl.fromTo("#B-mon",{x:900,opacity:0},{x:0,opacity:1,duration:1.4,ease:"power3.out"},2.4);
  tl.fromTo("#B-netX",{x:-440,y:0},{x:@DX@,y:@DY@,duration:1.5,ease:"power2.inOut",immediateRender:false},4.7);
  tl.fromTo("#B-network",{scale:0.6,transformOrigin:"50% 50%"},{scale:@FE@,transformOrigin:"50% 50%",duration:1.5,ease:"power2.inOut",immediateRender:false},4.7);
  tl.fromTo("#B-bloom",{opacity:0},{opacity:1,duration:0.7},6.0);
  tl.fromTo("#B-led",{opacity:0.3},{opacity:1,duration:0.3},6.0);
  tl.fromTo("#B-l1",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},6.4);
  tl.fromTo("#B-fly",{x:500,opacity:0},{x:0,opacity:1,duration:1.0,ease:"power3.out"},6.0);
  tl.fromTo("#B-flyBob",{y:0,rotation:-2,transformOrigin:"50% 50%"},{y:-8,rotation:2,transformOrigin:"50% 50%",duration:0.45,repeat:9,yoyo:true,ease:"sine.inOut"},7.0);
  tl.fromTo("#B-mo-wings",{scaleY:1,transformOrigin:"50% 100%"},{scaleY:0.3,transformOrigin:"50% 100%",duration:0.05,repeat:80,yoyo:true,ease:"none"},6.4);
  var cam=@CAM@, xs=cam.map(function(p){return p[0];}), ys=cam.map(function(p){return p[1];});
  tl.set("#B-pulse",{x:xs[0],y:ys[0]},0);
  tl.fromTo("#B-start",{opacity:0,scale:0.4,transformOrigin:"50% 50%"},{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.4,ease:"back.out(3)"},6.5);
  [0,1].forEach(function(k){
    tl.fromTo("#B-pulse",{opacity:0},{opacity:1,duration:0.1},6.7+k*1.1);
    tl.to("#B-pulse",{keyframes:{x:xs,y:ys,easeEach:"none"},duration:1.0,ease:"none",immediateRender:false},6.7+k*1.1);
    tl.fromTo("#B-pulse",{opacity:1},{opacity:0,duration:0.1,immediateRender:false},6.7+k*1.1+0.95);
  });
  tl.fromTo("#B-end",{opacity:0,scale:0.4,transformOrigin:"50% 50%"},{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.4,ease:"back.out(3)"},7.8);
  tl.fromTo("#B-bridge",{attr:{"stroke-dashoffset":700}},{attr:{"stroke-dashoffset":0},duration:0.9,ease:"power2.inOut"},8.0);
  tl.fromTo("#B-mo-proboscis",{attr:{d:"M98 8 q 14 6 20 20"}},{attr:{d:"M98 8 q 34 10 50 46"},duration:0.35,ease:"back.out(2)"},8.8);
  tl.fromTo("#B-flyBob",{scale:1,transformOrigin:"90% 50%"},{scale:1.12,transformOrigin:"90% 50%",duration:0.18,ease:"power2.out",repeat:3,yoyo:true,immediateRender:false},8.8);
  tl.fromTo("#B-sparks",{opacity:0,scale:0.5,transformOrigin:"50% 50%"},{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.3,ease:"back.out(3)"},8.9);
  tl.fromTo("#B-sparks",{opacity:1},{opacity:0,duration:0.4,immediateRender:false},9.9);
""".replace("@CAM@", json.dumps(path)).replace("@DX@", str(fx - 960)).replace("@DY@", str(fy - 540)).replace("@FE@", str(fe))
    return composition2("B", d, svg, html, js, extra, background=("#2c1a6a", "#171049", "#0a0a24"), seed=8)


# ---------------------------------------------------------------- Scene F: server corridor and the three questions
def scene_F2():
    d = INFO["F"]
    extra = """
<radialGradient id="F-end" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#9af0ff" stop-opacity=".9"/><stop offset=".4" stop-color="#6a8cff" stop-opacity=".4"/><stop offset="1" stop-color="#6a8cff" stop-opacity="0"/></radialGradient>
<linearGradient id="F-ceiling" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0828"/><stop offset="1" stop-color="#1c1a58"/></linearGradient>
<linearGradient id="F-ground" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#06051a"/><stop offset="1" stop-color="#26246a"/></linearGradient>
<linearGradient id="F-rack" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1a1856"/><stop offset="1" stop-color="#2c2a88"/></linearGradient>"""
    vp = (960, 500)
    def wall_points(side):
        def p(u, v):
            xb = 960 + side * 960; xf = 960 + side * 118
            yt0, yb0 = -40, 1120; yt1, yb1 = 410, 600
            x = xb + (xf - xb) * u
            yt = yt0 + (yt1 - yt0) * u; yb = yb0 + (yb1 - yb0) * u
            return x, yt + (yb - yt) * v
        return p
    panels, leds, cables = [], [], []
    for side in (-1, 1):
        p = wall_points(side)
        us = [1 - 1 / (1 + 0.5 * i) for i in range(0, 26)]
        for i in range(len(us) - 1):
            a, bb = us[i], us[i + 1]
            q = [p(a, 0.03), p(bb, 0.03), p(bb, 0.97), p(a, 0.97)]
            shade = 0.18 + 0.7 * (a ** 0.8)
            panels.append(f'<polygon points="{" ".join(f"{x:.0f},{y:.0f}" for x, y in q)}" fill="url(#F-rack)" stroke="#5a5ad0" stroke-width="3"/>'
                          f'<polygon points="{" ".join(f"{x:.0f},{y:.0f}" for x, y in q)}" fill="#05031a" opacity="{shade:.2f}"/>')
            x1, y1 = p(a, 0.025); x2, y2 = p(bb, 0.025)
            cables.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#ff4fa3" stroke-width="{max(2, 8 * (1 - a)):.1f}" opacity=".7"/>')
            for r in range(11):
                for c in range(3):
                    uu = a + (bb - a) * (0.18 + 0.3 * c); vv = 0.10 + 0.08 * r
                    x, y = p(uu, vv)
                    size = max(2.2, 20 * (1 - uu) ** 1.3)
                    color = CYAN if (i + r + c) % 4 else (AMBER if (r + c) % 2 else MAGENTA)
                    leds.append(f'<rect class="led" x="{x - size:.1f}" y="{y - size * 0.5:.1f}" width="{size * 2:.1f}" height="{size:.1f}" rx="{size * 0.2:.1f}" fill="{color}"/>')
    strips = "".join(f'<polygon points="{960 + dx * 0.06:.0f},430 {960 - dx * 0.06:.0f},430 {960 - dx:.0f},-40 {960 + dx:.0f},-40" fill="#cfe8ff" opacity=".16"/>' for dx in (170, 520, 880))
    marks = "".join(
        f'<g id="F-q{k}" opacity="0"><text x="{x}" y="{y + int(s_ * 0.34)}" text-anchor="middle" font-size="{s_}" font-weight="700" fill="{c}" stroke="#05031a" stroke-width="14" paint-order="stroke" stroke-linejoin="round" filter="url(#F-glow)">?</text></g>'
        for k, (x, y, s_, c) in enumerate([(960, 470, 420, AMBER), (590, 620, 300, CYAN), (1330, 640, 340, MAGENTA)]))
    guides = "".join(f'<line x1="{x}" y1="1120" x2="{960 + (x - 960) * 0.12:.0f}" y2="590" stroke="#6ad8ff" stroke-width="3" opacity=".22"/>' for x in (260, 560, 960, 1360, 1660))
    door = '<rect x="905" y="470" width="110" height="120" rx="8" fill="#cfeaff" opacity=".85" filter="url(#F-glow)"/>'
    svg = f"""<g id="F-cam"><polygon points="0,-40 1920,-40 1080,430 840,430" fill="url(#F-ceiling)"/><polygon points="0,1120 1920,1120 1080,590 840,590" fill="url(#F-ground)"/>
<ellipse id="F-haze" cx="960" cy="510" rx="520" ry="330" fill="url(#F-end)"/>{strips}
<g>{"".join(panels)}</g><g>{guides}</g>{door}<g>{"".join(cables)}</g><g>{"".join(leds)}</g></g>{marks}"""
    js = """
  tl.fromTo("#F-cam",{scale:1,svgOrigin:"960 500"},{scale:1.8,svgOrigin:"960 500",duration:8.2,ease:"sine.inOut"},0);
  tl.fromTo("#F-haze",{opacity:0.7},{opacity:1,duration:0.8,repeat:9,yoyo:true,ease:"sine.inOut"},0);
  tl.fromTo("#F-cam .led",{opacity:1},{opacity:0.15,duration:0.18,repeat:30,yoyo:true,ease:"steps(1)",stagger:{each:0.0105,from:"random"}},0.2);
  [[0,0.4],[1,2.8],[2,4.9]].forEach(function(a){
    tl.fromTo("#F-q"+a[0],{opacity:0,scale:0.3,transformOrigin:"50% 50%"},{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.6,ease:"back.out(3)"},a[1]);
    tl.fromTo("#F-q"+a[0],{y:0},{y:-14,duration:1.2,repeat:5,yoyo:true,ease:"sine.inOut",immediateRender:false},a[1]+0.7);
  });
"""
    return composition2("F", d, svg, "", js, extra, background=("#1c1450", "#0d0a30", "#05041a"), seed=21)


SCENES = [("A", scene_A2, START["A"], INFO["A"]), ("B", scene_B2, START["B"], INFO["B"]), ("D", b0.scene_D, START["D"], INFO["D"]),
         ("E", b0.scene_E, START["E"], INFO["E"]), ("F", scene_F2, START["F"], INFO["F"]), ("C", b0.scene_C, START["C1"], INFO["C1"] + GAP + INFO["C2"])]


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
