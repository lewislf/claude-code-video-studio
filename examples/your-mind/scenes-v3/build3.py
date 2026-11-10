"""v3 scenes D, E and C, third round: same language as scene A (large shapes, light, depth).

  python3 build3.py     # generates everything (A, B, F from build2; D, E, C from here)
"""
import json, random
import build2 as b2
from build import INFO, START, GAP, CYAN, MAGENTA, AMBER, MINT, LILAC, RED, head_L
from build2 import composition2
from art2 import prismo_head, prismo_human, brain_card, brain_pink, brain_side, head_line


def scene_D3():
    d = INFO["D"]
    rr = random.Random(2)
    rain = "".join(f'<line x1="{x}" y1="{y}" x2="{x - 22}" y2="{y + 90}"/>' for x in range(-100, 2100, 110) for y in range(-200, 1100, 190) for _ in [0] if rr.random() < 0.5)
    rain2 = "".join(f'<line x1="{rr.randint(-100, 2000)}" y1="{y}" x2="{0}" y2="{y + 40}" transform="translate(0 0)"/>' for y in range(-120, 1100, 64) for _ in range(5)).replace('x2="0"','x2="0"')
    rain2 = "".join(f'<line x1="{x}" y1="{y}" x2="{x - 10}" y2="{y + 40}"/>' for x, y in [(rr.randint(-100, 2000), rr.randint(-200, 1100)) for _ in range(260)])
    ecg = "M0 0 " + " ".join("h60 l16 -70 l18 150 l14 -96 l10 16 h46" for _ in range(8))
    extra = """
<linearGradient id="D-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05061c"/><stop offset="1" stop-color="#241a5a"/></linearGradient>
<linearGradient id="D-lane" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c1a52"/><stop offset="1" stop-color="#07061a"/></linearGradient>
<radialGradient id="D-light" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff6c8" stop-opacity="1"/><stop offset=".35" stop-color="#ffe9a0" stop-opacity=".55"/><stop offset="1" stop-color="#ffe9a0" stop-opacity="0"/></radialGradient>
<linearGradient id="D-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#232a6e"/><stop offset="1" stop-color="#121644"/></linearGradient>
<linearGradient id="D-ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b1e54"/><stop offset="1" stop-color="#090b26"/></linearGradient>
<linearGradient id="D-night" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0f3c"/><stop offset="1" stop-color="#2a3a8c"/></linearGradient>
<linearGradient id="D-day" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a7cff"/><stop offset="1" stop-color="#ffc98a"/></linearGradient>
<linearGradient id="D-blanket" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a82e0"/><stop offset="1" stop-color="#2c4a9a"/></linearGradient>
<linearGradient id="D-beam" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#cfe0ff" stop-opacity=".28"/><stop offset="1" stop-color="#cfe0ff" stop-opacity="0"/></linearGradient>"""
    svg = f"""<g id="D-road">
<rect width="1920" height="1080" fill="url(#D-sky)"/>
<polygon points="900,470 1020,470 2300,1080 -380,1080" fill="url(#D-lane)"/>
<g id="D-stripe" stroke="#9aa6ff" stroke-width="14" stroke-dasharray="70 110" opacity=".75"><line x1="960" y1="470" x2="960" y2="1080"/></g>
<g stroke="#9aa6ff" stroke-width="10" opacity=".5"><line x1="910" y1="470" x2="-120" y2="1080"/><line x1="1010" y1="470" x2="2040" y2="1080"/></g>
<g id="D-rain2" stroke="#a9c4ff" stroke-width="2" opacity=".28">{rain2}</g><g id="D-rain" stroke="#cfe0ff" stroke-width="5" opacity=".5">{rain}</g>
<g id="D-headlights" transform="translate(960 560)"><g id="D-headlightsG" transform="scale(1.5)">

<path d="M-170 70 L-170 -10 Q-170 -70 -110 -76 L110 -76 Q170 -70 170 -10 L170 70 Z" fill="#06051a"/><path d="M-120 -66 L120 -66 L100 -20 L-100 -20 Z" fill="#1d2468"/>
<circle cx="-118" cy="24" r="86" fill="url(#D-light)"/><circle cx="118" cy="24" r="86" fill="url(#D-light)"/>
<circle cx="-118" cy="24" r="26" fill="#fffbe2"/><circle cx="118" cy="24" r="26" fill="#fffbe2"/></g></g>
<rect id="D-sirenR" width="1920" height="1080" fill="#ff1f5a" opacity="0"/><rect id="D-sirenB" width="1920" height="1080" fill="#2a7bff" opacity="0"/>
<rect id="D-flash" width="1920" height="1080" fill="#ffffff" opacity="0"/></g>
<g id="D-room" opacity="0">
<rect width="1920" height="1080" fill="url(#D-wall)"/><rect y="760" width="1920" height="320" fill="url(#D-ground)"/>
<polygon points="260,640 760,640 1180,1080 -200,1080" fill="url(#D-beam)" opacity=".8"/>
<g filter="url(#D-shadow)"><rect x="160" y="110" width="660" height="560" rx="18" fill="#6a7bd0"/></g>
<clipPath id="D-clipW"><rect x="190" y="140" width="600" height="500" rx="8"/></clipPath>
<rect x="190" y="140" width="600" height="500" rx="8" fill="url(#D-night)"/><rect id="D-dayR" x="190" y="140" width="600" height="500" fill="url(#D-day)" opacity="0"/>
<g clip-path="url(#D-clipW)"><g id="D-orbit" transform="translate(490 780)"><circle cx="0" cy="-560" r="64" fill="#ffd23e" filter="url(#D-glow)"/><circle cx="0" cy="560" r="52" fill="#eef4ff"/></g></g>
<g stroke="#6a7bd0" stroke-width="14"><line x1="490" y1="140" x2="490" y2="640"/><line x1="190" y1="390" x2="790" y2="390"/></g>
<path d="M40 -20 L 250 -20 C 230 200 270 480 200 1090 L 40 1090 Z" fill="#33449c"/><path d="M110 -20 C 140 200 150 480 110 1090" stroke="#1f2a70" stroke-width="12" fill="none"/><path d="M880 -20 L 710 -20 C 740 200 700 480 760 1090 L 880 1090 Z" fill="#33449c"/><path d="M820 -20 C 790 200 780 480 820 1090" stroke="#1f2a70" stroke-width="12" fill="none"/>
<g transform="translate(1000 240)"><circle r="104" fill="#eef1ff" stroke="#8d7bff" stroke-width="10"/><circle r="92" fill="#14122e"/>
<g fill="#8d7bff"><rect x="-4" y="-86" width="8" height="18"/><rect x="-4" y="68" width="8" height="18"/><rect x="68" y="-4" width="18" height="8"/><rect x="-86" y="-4" width="18" height="8"/></g>
<g id="D-hand"><line x1="0" y1="0" x2="0" y2="-72" stroke="#eef1f7" stroke-width="9" stroke-linecap="round"/></g><g id="D-hand2"><line x1="0" y1="0" x2="44" y2="0" stroke="#ffb23e" stroke-width="12" stroke-linecap="round"/></g><circle r="10" fill="#ffb23e"/></g>
<g filter="url(#D-shadow)"><rect x="1360" y="330" width="420" height="470" rx="30" fill="#14122e" stroke="#8d7bff" stroke-width="8"/><rect x="1390" y="364" width="360" height="330" rx="14" fill="#06051a"/><rect x="1530" y="800" width="80" height="150" fill="#2a2a6a"/><rect x="1450" y="940" width="240" height="36" rx="16" fill="#2a2a6a"/></g>
<clipPath id="D-cm"><rect x="1390" y="364" width="360" height="330" rx="14"/></clipPath>
<g clip-path="url(#D-cm)"><g id="D-ecg" transform="translate(1390 530)"><path d="{ecg}" fill="none" stroke="{MINT}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" filter="url(#D-glow)"/></g></g>
<g transform="translate(-300 0)"><g filter="url(#D-shadow)"><rect x="700" y="780" width="900" height="110" rx="20" fill="#2a2a6a"/><rect x="680" y="690" width="940" height="110" rx="26" fill="#dfe4ff"/><rect x="680" y="640" width="220" height="100" rx="44" fill="#f4f6ff"/>
<g id="D-blanket"><path d="M880 700 C 960 560 1200 560 1340 640 C 1460 700 1560 690 1620 720 L1620 800 L880 800 Z" fill="url(#D-blanket)"/><path d="M960 690 C 1060 610 1220 620 1320 670" fill="none" stroke="#fff" stroke-opacity=".28" stroke-width="10" stroke-linecap="round"/></g>
<rect x="700" y="880" width="56" height="150" fill="#2a2a6a"/><rect x="1560" y="880" width="56" height="150" fill="#2a2a6a"/></g></g></g>"""
    html = """<div id="D-l1" class="pill2" style="left:0;right:0;text-align:center;top:70px;font-size:56px">UNITED KINGDOM · 2006</div>
<div id="D-l2" class="pill2" style="left:200px;top:790px;font-size:110px"><span id="D-month">MONTH 1</span></div>
<div id="D-l3" class="pill2" style="left:0;right:0;text-align:center;top:22px;font-size:60px;color:#ff4f7d">VEGETATIVE STATE</div>"""
    js = """
  tl.fromTo("#D-l1",{opacity:0,y:-20},{opacity:1,y:0,duration:0.6},0.4);
  tl.fromTo("#D-rain",{y:0},{y:190,duration:0.45,repeat:16,ease:"none"},0);
  tl.fromTo("#D-rain2",{y:0},{y:64,duration:0.2,repeat:36,ease:"none"},0);
  tl.fromTo("#D-stripe",{attr:{"stroke-dashoffset":0}},{attr:{"stroke-dashoffset":-180},duration:0.5,repeat:12,ease:"none"},0);
  tl.fromTo("#D-headlights",{scale:0.4,opacity:1,transformOrigin:"50% 50%"},{scale:2.6,opacity:1,transformOrigin:"50% 50%",duration:4.4,ease:"power2.in"},1.6);
  tl.fromTo("#D-flash",{opacity:0},{opacity:1,duration:0.08},6.0);
  tl.fromTo("#D-flash",{opacity:1},{opacity:0,duration:0.5,immediateRender:false},6.1);
  tl.fromTo("#D-headlights",{opacity:1},{opacity:0,duration:0.1,immediateRender:false},6.0);
  tl.fromTo("#D-sirenR",{opacity:0},{opacity:0.35,duration:0.22,repeat:7,yoyo:true,ease:"none"},6.4);
  tl.fromTo("#D-sirenB",{opacity:0},{opacity:0.35,duration:0.22,repeat:7,yoyo:true,ease:"none"},6.51);
  tl.fromTo("#D-l1",{opacity:1},{opacity:0,duration:0.4,immediateRender:false},6.0);
  tl.fromTo("#D-road",{opacity:1},{opacity:0,duration:0.8,immediateRender:false},7.8);
  tl.fromTo("#D-room",{opacity:0},{opacity:1,duration:0.8},7.8);
  tl.fromTo("#D-ecg",{x:1390},{x:1390-196,duration:0.9,repeat:14,ease:"none"},7.8);
  tl.fromTo("#D-blanket",{scaleY:1,transformOrigin:"50% 100%"},{scaleY:1.04,transformOrigin:"50% 100%",duration:1.1,repeat:7,yoyo:true,ease:"sine.inOut"},7.8);
  tl.fromTo("#D-orbit",{rotation:0},{rotation:1800,duration:5.2,ease:"none"},8.2);
  tl.fromTo("#D-dayR",{opacity:0},{opacity:0.9,duration:0.4,repeat:12,yoyo:true,ease:"sine.inOut"},8.4);
  tl.fromTo("#D-hand",{rotation:0},{rotation:7200,duration:5.2,ease:"none"},8.2);
  tl.fromTo("#D-hand2",{rotation:0},{rotation:600,duration:5.2,ease:"none"},8.2);
  tl.fromTo("#D-l2",{opacity:0,y:20},{opacity:1,y:0,duration:0.4},8.2);
  var om={v:1};tl.fromTo(om,{v:1},{v:5.4,duration:5.0,ease:"none",onUpdate:function(){document.getElementById("D-month").textContent="MONTH "+Math.min(5,Math.floor(om.v));}},8.3);
  tl.fromTo("#D-l2",{opacity:1},{opacity:0,duration:0.3,immediateRender:false},12.3);
  tl.fromTo("#D-l3",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},12.6);
"""
    return composition2("D", d, svg, html, js, extra, background=("#1a1450", "#0a0a30", "#04041a"), seed=5)


def scene_E3():
    d = INFO["E"]
    targets = [(1330, 480), (1650, 440), (1560, 650), (1310, 650)]
    target_svg = "".join(f'<circle id="E-tgt{k}" cx="{x}" cy="{y}" r="54" fill="none" stroke="{CYAN}" stroke-width="8" opacity=".55"/><circle id="E-tgc{k}" cx="{x}" cy="{y}" r="16" fill="{CYAN}" opacity=".6"/>' for k, (x, y) in enumerate(targets))
    extra = """<linearGradient id="E-screen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16143a"/><stop offset="1" stop-color="#0b1c40"/></linearGradient>
<linearGradient id="E-fall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#150d40" stop-opacity="0"/><stop offset="1" stop-color="#150d40" stop-opacity="1"/></linearGradient>
<radialGradient id="E-brain2" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#1c6fa0" stop-opacity=".9"/><stop offset="1" stop-color="#0c2e66" stop-opacity=".95"/></radialGradient>
<radialGradient id="E-bloom" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#3be0ff" stop-opacity=".4"/><stop offset="1" stop-color="#3be0ff" stop-opacity="0"/></radialGradient>"""
    svg = f"""<g id="E-cam">
<ellipse id="E-bloom" cx="1480" cy="520" rx="640" ry="470" fill="url(#E-bloom)" opacity="0"/>
<g id="E-headW"><g id="E-bob"><g transform="translate(-231 110) scale(3.1)">{head_line("E-pm")}<g id="E-brain" opacity=".7"><g transform="translate(196 118) scale(.82) translate(-196 -118)">{brain_side("E-br")}</g></g><g id="E-pm-eye"><ellipse cx="257" cy="129" rx="9" ry="5.6" fill="#0a0820" stroke="#3be0ff" stroke-width="1.2"/><circle cx="259" cy="129" r="3.6" fill="#29b6ff"/><circle cx="260.2" cy="127.8" r="1.1" fill="#fff"/></g><path d="M 245 118 Q 257 111 269 119" fill="none" stroke="#3be0ff" stroke-width="2" stroke-linecap="round"/></g>
<g id="E-chip"><rect x="327" y="224" width="62" height="38" rx="11" fill="{AMBER}" filter="url(#E-glow)" transform="rotate(-6 358 243)"/></g></g></g>
<g id="E-waves" fill="none" stroke="{AMBER}" stroke-width="8" opacity="0"><circle id="E-o0" cx="358" cy="215" r="24"/></g>
<path id="E-wire" d="M358 213 C 600 120 1000 150 1100 470" fill="none" stroke="#7a8cff" stroke-width="8" stroke-linecap="round" opacity="0"/>
<path id="E-signal" d="M358 213 C 600 120 1000 150 1100 470" fill="none" stroke="#ffd23e" stroke-width="14" stroke-linecap="round" stroke-dasharray="46 240" opacity="0" filter="url(#E-glow)"/>
<g id="E-mon" opacity="0"><g filter="url(#E-shadow)"><rect x="1100" y="250" width="740" height="520" rx="34" fill="#1a1850" stroke="{LILAC}" stroke-width="8"/><rect x="1130" y="280" width="680" height="460" rx="16" fill="url(#E-screen)"/>
<rect x="1420" y="770" width="100" height="90" fill="#1a1850" stroke="{LILAC}" stroke-width="5"/><rect x="1300" y="856" width="340" height="30" rx="15" fill="#1a1850" stroke="{LILAC}" stroke-width="5"/></g>{target_svg}
<g id="E-pointer" transform="translate(1200 330)"><g id="E-pointerM" transform="scale(1.7)"><path d="M0 0 L0 54 L16 40 L28 66 L40 60 L28 36 L50 36 Z" fill="#ffffff" stroke="#1a0f3a" stroke-width="3"/></g></g></g></g>"""
    html = """<div id="E-l1" class="pill2" style="left:72px;top:60px;font-size:38px;color:#ffb23e">2024 · COMPANY DEMO</div>
<div id="E-l2" class="pill2" style="left:1100px;width:740px;text-align:center;top:945px;font-size:48px"><i style="background:#3be0ff"></i>BRAIN SIGNALS</div>"""
    ks = ",".join(f"[{x - 8},{y - 14}]" for x, y in targets)
    js = """
  tl.fromTo("#E-cam",{scale:1,svgOrigin:"960 540"},{scale:1.05,svgOrigin:"960 540",duration:15,ease:"none"},0);
  tl.fromTo("#E-headW",{x:-500,opacity:0},{x:0,opacity:1,duration:1.4,ease:"power3.out"},0.2);
  tl.fromTo("#E-bob",{y:0},{y:-14,duration:1.6,repeat:9,yoyo:true,ease:"sine.inOut"},1.6);
  [3.2,6.4,9.8,12.6].forEach(function(t){tl.fromTo("#E-pm-eye",{scaleY:1,transformOrigin:"50% 50%"},{scaleY:0.08,transformOrigin:"50% 50%",duration:0.09,repeat:1,yoyo:true,immediateRender:false},t);});
  tl.fromTo("#E-brain",{opacity:0.4},{opacity:1,duration:0.8,repeat:15,yoyo:true,ease:"sine.inOut"},1.2);
  tl.fromTo("#E-chip",{scale:1,transformOrigin:"50% 50%"},{scale:1.35,transformOrigin:"50% 50%",duration:0.5,repeat:9,yoyo:true,ease:"sine.inOut"},1.8);
  tl.fromTo("#E-l1",{opacity:0,y:-20},{opacity:1,y:0,duration:0.6},3.6);
  tl.fromTo("#E-mon",{x:700,opacity:0},{x:0,opacity:1,duration:1.4,ease:"power3.out"},1.0);
  tl.fromTo("#E-bloom",{opacity:0},{opacity:1,duration:1.0},4.2);
  tl.fromTo("#E-wire",{opacity:0},{opacity:0.9,duration:0.6},4.4);
  tl.fromTo("#E-waves",{opacity:0},{opacity:1,duration:0.3},4.8);
  tl.fromTo("#E-o0",{scale:0.6,opacity:0.9,svgOrigin:"358 215"},{scale:2.4,opacity:0,svgOrigin:"358 201",duration:1.4,repeat:5,ease:"power1.out",immediateRender:false},4.8);
  tl.fromTo("#E-signal",{opacity:0,attr:{"stroke-dashoffset":0}},{opacity:1,attr:{"stroke-dashoffset":-286},duration:0.8,repeat:11,ease:"none"},5.0);
  tl.fromTo("#E-l2",{opacity:0,y:20},{opacity:1,y:0,duration:0.5},5.6);
  var P=[@TARGETS@], t0=9.0, seg=0.675;
  var cx=[1200],cy=[330];
  P.forEach(function(p){cx.push(p[0],p[0]);cy.push(p[1],p[1]);});
  tl.set("#E-pointer",{x:1200,y:330},0);
  tl.to("#E-pointer",{keyframes:{x:cx,y:cy,easeEach:"power2.inOut"},duration:seg*cx.length-seg,ease:"none"},t0);
  for(var k=0;k<P.length;k++){
    var ta=t0+(2*k+1)*seg;
    tl.fromTo("#E-tgt"+k,{scale:1,opacity:0.55,transformOrigin:"50% 50%"},{scale:1.6,opacity:1,transformOrigin:"50% 50%",duration:0.3,ease:"back.out(3)"},ta);
    tl.fromTo("#E-tgc"+k,{opacity:0.6,scale:1,transformOrigin:"50% 50%"},{opacity:1,scale:2.4,transformOrigin:"50% 50%",duration:0.3},ta);
  }
""".replace("@TARGETS@", ks)
    return composition2("E", d, svg, html, js, extra, background=("#33186e", "#170f4a", "#0a0a26"), seed=9)


def cube(cx, cy, s, top_color, left_color, right_color, stroke, w=5, extra=""):
    top = f"M{cx} {cy - s} L{cx + s * 1.1} {cy - s * 0.45} L{cx} {cy + s * 0.1} L{cx - s * 1.1} {cy - s * 0.45} Z"
    left = f"M{cx - s * 1.1} {cy - s * 0.45} L{cx} {cy + s * 0.1} L{cx} {cy + s} L{cx - s * 1.1} {cy + s * 0.55} Z"
    right = f"M{cx + s * 1.1} {cy - s * 0.45} L{cx} {cy + s * 0.1} L{cx} {cy + s} L{cx + s * 1.1} {cy + s * 0.55} Z"
    return (f'<g {extra}><path d="{top}" fill="{top_color}"/><path d="{left}" fill="{left_color}"/><path d="{right}" fill="{right_color}"/>'
            f'<path d="{top} {left} {right}" fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"/></g>')


def scene_C3():
    d = INFO["C1"] + GAP + INFO["C2"]
    act2 = INFO["C1"] + GAP
    rng = random.Random(5)
    post_colors = ["#2b2a80", "#7b2a6c", "#25427a", "#6b5b2a", "#2a6a6a"]
    cards = "".join(
        f'<g transform="translate(0 {k * 190})"><rect x="-150" y="-330" width="300" height="170" rx="20" fill="{post_colors[k % 5]}"/>'
        f'<circle cx="-100" cy="-290" r="22" fill="#eef1ff" opacity=".85"/><rect x="-66" y="-304" width="150" height="12" rx="6" fill="#eef1ff" opacity=".7"/><rect x="-66" y="-282" width="100" height="10" rx="5" fill="#eef1ff" opacity=".4"/>'
        f'<rect x="-130" y="-244" width="260" height="56" rx="12" fill="#000" opacity=".22"/><circle cx="-84" cy="-218" r="14" fill="#ffd23e"/><path d="M-60 -196 L-20 -236 L20 -204 L50 -226 L112 -196 Z" fill="#fff" opacity=".35"/><path d="M110 -176 c-8 -10 -22 -2 -14 8 l14 12 l14 -12 c8 -10 -6 -18 -14 -8 Z" fill="#ff4f7d" transform="translate(-10 -16)"/></g>'
        for k in range(8))
    buildings = "".join(
        f'<rect x="{x}" y="{720 - h}" width="{w}" height="{h}" fill="{c}"/><rect x="{x}" y="{720 - h}" width="{w}" height="10" fill="#6a7bd0" opacity=".5"/>'
        for x, w, h, c in [(560 + k * 58, 48 + (k * 7) % 14, 120 + (k * 53) % 380, ["#2b2a80", "#3a2a8c", "#25427a"][k % 3]) for k in range(20)])
    windows = "".join(f'<rect x="{572 + k * 58 + (j % 2) * 22}" y="{720 - 54 - j * 42}" width="10" height="14" fill="#ffd23e" opacity=".6"/>' for k in range(20) for j in range(1 + (120 + (k * 53) % 380) // 50))
    cols, rows, step = 40, 18, 46
    dot_colors = [CYAN, CYAN, "#5fb7ff", LILAC]
    dots = "".join(f'<use class="m" href="#C-pm{i % 3}" x="{960 + (i % cols - 19.5) * step:.0f}" y="{610 + (i // cols - 8.5) * step:.0f}"/>' for i in range(cols * rows))
    real = f'<g transform="translate({960 + 6.5 * step:.0f} {610 - 2.5 * step:.0f})"><g id="C-real" opacity="0"><circle r="44" fill="#1a1050"/><circle r="40" fill="{AMBER}" opacity=".5" filter="url(#C-glow)"/><g transform="scale(2.1)"><use href="#C-pmA"/></g></g></g>'
    tiles = "".join(cube(235 + c * 242, 250 + l * 250, 96, "#4fd8ff55", "#2a2a8c", "#17175e", CYAN, 5, 'class="tile"') for l in range(3) for c in range(7))
    you_cube = cube(235 + 3 * 242, 250 + 1 * 250, 104, "#ffd27a", "#d98a1e", "#9a5a10", AMBER, 8)
    extra = '<g id="C-pm0"><g transform="scale(.15) translate(-205 -140)"><path d="M150 250 C160 200 110 180 110 120 C110 50 190 28 244 62 C284 88 270 120 282 138 L300 160 L282 164 L284 182 C290 200 262 214 238 212 C232 226 236 240 240 252" fill="#4a4ab0" fill-opacity=".35" stroke="#3be0ff" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/><path d="M 262 84 C 262 56 226 36 188 38 C 150 38 122 62 122 98 C 122 118 134 126 150 124 C 164 122 176 128 192 130 C 210 130 222 116 238 108 C 252 102 262 96 262 84 Z" fill="#ff9fa8" stroke="#d8657a" stroke-width="8"/></g></g><g id="C-pmA"><g transform="scale(.15) translate(-205 -140)"><path d="M150 250 C160 200 110 180 110 120 C110 50 190 28 244 62 C284 88 270 120 282 138 L300 160 L282 164 L284 182 C290 200 262 214 238 212 C232 226 236 240 240 252" fill="#7a4a10" fill-opacity=".5" stroke="#ffb23e" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/><path d="M 262 84 C 262 56 226 36 188 38 C 150 38 122 62 122 98 C 122 118 134 126 150 124 C 164 122 176 128 192 130 C 210 130 222 116 238 108 C 252 102 262 96 262 84 Z" fill="#ffd27a" stroke="#d98a1e" stroke-width="8"/></g></g><g id="C-pm1" transform="scale(.9)"><use href="#C-pm0"/></g><g id="C-pm2" transform="scale(1.1)"><use href="#C-pm0"/></g><radialGradient id="C-neb" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ff8ad0" stop-opacity=".4"/><stop offset=".55" stop-color="#ff8ad0" stop-opacity=".16"/><stop offset="1" stop-color="#ff8ad0" stop-opacity="0"/></radialGradient><radialGradient id="C-focusG" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffb23e" stop-opacity=".55"/><stop offset="1" stop-color="#ffb23e" stop-opacity="0"/></radialGradient>'
    svg = f"""<g id="C-a1">
<g id="C-phoneW" transform="translate(960 540)"><g id="C-phone" filter="url(#C-shadow)"><rect x="-200" y="-400" width="400" height="800" rx="54" fill="#15133a" stroke="{LILAC}" stroke-width="8"/>
<rect x="-172" y="-364" width="344" height="728" rx="26" fill="#0e0c26"/>
<clipPath id="C-cp"><rect x="-172" y="-364" width="344" height="728" rx="26"/></clipPath><g clip-path="url(#C-cp)"><g id="C-posts">{cards}</g></g></g></g>
<g id="C-city" opacity="0"><ellipse cx="1110" cy="730" rx="580" ry="36" fill="#05031a" opacity=".5" filter="url(#C-blur6)"/><ellipse cx="1150" cy="600" rx="640" ry="300" fill="url(#C-neb)"/>{buildings}{windows}</g>
<g id="C-boxG" opacity="0" filter="url(#C-glow)"><path id="C-box" d="M960 150 L1370 360 L1370 760 L960 950 L550 760 L550 360 Z M550 360 L960 560 L1370 360 M960 560 L960 950" fill="none" stroke="{CYAN}" stroke-width="10" stroke-linejoin="round"/></g></g>
<g id="C-a2" opacity="0"><g id="C-grid">{dots}{real}</g></g>
<g id="C-a3" opacity="0"><g id="C-cam3"><ellipse id="C-focus" cx="{235 + 3 * 242}" cy="{250 + 250}" rx="360" ry="300" fill="url(#C-focusG)"/><g filter="url(#C-glow)">{tiles}</g><g id="C-you" filter="url(#C-glow)">{you_cube}</g></g></g>
"""
    html = f"""<div id="C-t1" class="pill2" style="left:0;right:0;text-align:center;top:70px;font-size:56px"><i style="background:#3be0ff"></i>FEED</div>
<div id="C-n" class="pill2" style="left:0;right:0;text-align:center;top:44px;font-size:84px">1</div>
<div id="C-t3" class="pill2" style="left:0;right:0;text-align:center;top:930px;font-size:64px;color:#ffb23e">ARE YOU HERE?</div>"""
    js = f"""
  var A2={act2:.2f};
  tl.fromTo("#C-posts",{{y:0}},{{y:-760,duration:2.4,ease:"none"}},0.2);
  tl.fromTo("#C-t1",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.5}},0.4);
  tl.fromTo("#C-phone",{{scale:1.0,x:0,y:0,transformOrigin:"50% 50%"}},{{scale:0.4,x:-640,y:90,transformOrigin:"50% 50%",duration:2.2,ease:"power2.inOut"}},2.4);
  tl.fromTo("#C-city",{{opacity:0,scale:1.5,svgOrigin:"960 540"}},{{opacity:1,scale:1,svgOrigin:"960 540",duration:2.2,ease:"power2.out"}},2.6);
  tl.fromTo("#C-t1",{{opacity:1}},{{opacity:0,duration:0.3,immediateRender:false}},4.4);
  tl.fromTo("#C-boxG",{{opacity:0,scale:1.15,svgOrigin:"960 540"}},{{opacity:1,scale:1,svgOrigin:"960 540",duration:1.2,ease:"power3.out"}},5.0);
  tl.fromTo("#C-a1",{{opacity:1}},{{opacity:0,duration:0.5,immediateRender:false}},A2-0.1);
  tl.fromTo("#C-a2",{{opacity:0}},{{opacity:1,duration:0.4}},A2);
  tl.fromTo("#C-grid .m",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,transformOrigin:"50% 50%",duration:0.3,ease:"back.out(2)",stagger:{{amount:6.0,from:"center",grid:[18,40]}}}},A2+0.4);
  tl.fromTo("#C-n",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.5}},A2+0.4);
  var on={{v:1}};tl.fromTo(on,{{v:1}},{{v:720,duration:6.0,ease:"none",onUpdate:function(){{var n=Math.round(on.v);document.getElementById("C-n").textContent=n.toLocaleString("en-US")+(n===1?" mind":" minds");}}}},A2+0.5);
  tl.fromTo("#C-real",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.5,ease:"back.out(3)"}},A2+7.2);
  tl.fromTo("#C-real",{{scale:1}},{{scale:1.5,transformOrigin:"50% 50%",duration:0.45,repeat:5,yoyo:true,ease:"sine.inOut",immediateRender:false}},A2+7.8);
  tl.fromTo("#C-grid",{{scale:1,svgOrigin:"1259 495"}},{{scale:3.2,x:-299,y:45,svgOrigin:"1259 495",duration:3.0,ease:"power2.in",immediateRender:false}},A2+9.2);
  tl.fromTo("#C-a2",{{opacity:1}},{{opacity:0,duration:0.6,immediateRender:false}},A2+11.6);
  tl.fromTo("#C-n",{{opacity:1}},{{opacity:0,duration:0.4,immediateRender:false}},A2+8.9);
  tl.fromTo("#C-a3",{{opacity:0,scale:1.25,svgOrigin:"960 540"}},{{opacity:1,scale:1,svgOrigin:"960 540",duration:1.2,ease:"power2.out"}},A2+11.9);
  tl.fromTo("#C-cam3",{{scale:1,svgOrigin:"960 540"}},{{scale:1.05,svgOrigin:"960 540",duration:7.5,ease:"none"}},A2+13.0);
  tl.fromTo("#C-you",{{opacity:1}},{{opacity:0.55,duration:0.35,repeat:7,yoyo:true,ease:"sine.inOut",immediateRender:false}},A2+13.4);
  tl.fromTo("#C-t3",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.5}},A2+14.2);
"""
    return composition2("C", d, svg, html, js, extra, background=("#3a1d7a", "#1a1050", "#0b0a24"), seed=14)


b2.SCENES = [("A", b2.scene_A2, START["A"], INFO["A"]), ("B", b2.scene_B2, START["B"], INFO["B"]), ("D", scene_D3, START["D"], INFO["D"]),
            ("E", scene_E3, START["E"], INFO["E"]), ("F", b2.scene_F2, START["F"], INFO["F"]), ("C", scene_C3, START["C1"], INFO["C1"] + GAP + INFO["C2"])]

if __name__ == "__main__":
    b2.main()
