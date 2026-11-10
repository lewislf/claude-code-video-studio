"""Pilot scene in the v5 pattern: contract, segment 3 ("The one who signed was the outside person...").

  python3 example_scene.py     # writes compositions/ and index.html in this folder
"""
from engine import *

CE, SG = "contract", 3


def contract_3():
    p = "K3"
    start, dur = seg(CE, SG)
    t_signed, t_outside, t_works, t_suffers, t_obeys, t_inside, t_never, t_nothing, t_born, t_employed = (
        1.16, 2.7, 4.24, 4.63, 5.4, 6.55, 8.87, 10.02, 11.18, 11.56)
    extra = f"""<linearGradient id="{p}-paper" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#e9dcc2"/></linearGradient>
<linearGradient id="{p}-wall" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1c1a58"/><stop offset="1" stop-color="#2a2878"/></linearGradient>
<linearGradient id="{p}-doorlight" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffe9a8" stop-opacity=".65"/><stop offset="1" stop-color="#ffe9a8" stop-opacity="0"/></linearGradient>"""
    lines = "".join(f'<rect x="-210" y="{-250 + k * 34}" width="{360 if k % 3 else 270}" height="10" rx="5" fill="#8a7f68" opacity=".45"/>' for k in range(7))
    svg = f"""
<g id="{p}-world">
 <rect x="-600" y="-200" width="3300" height="1400" fill="url(#{p}-wall)"/>
 <g id="{p}-door" opacity="0"><rect x="80" y="190" width="340" height="680" rx="14" fill="#14123a" stroke="#8d7bff" stroke-width="8" filter="url(#{p}-glow)"/>
  <polygon points="80,190 420,190 420,870 80,870" fill="url(#{p}-doorlight)"/><text x="250" y="150" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="40" fill="#38e8a8" filter="url(#{p}-glow)">EXIT</text></g>
 <ellipse cx="740" cy="905" rx="300" ry="26" fill="#05031a" opacity=".5"/>
 <g transform="translate(428 360)"><g id="{p}-outside" opacity="0"><g transform="scale(1.75)">{person(p + "f", glow=p + "-glow")}</g></g></g>
 <g id="{p}-desk" opacity="0">
  <rect x="2200" y="640" width="860" height="40" rx="12" fill="#3a2a8c"/><rect x="2260" y="680" width="40" height="230" fill="#2a1d70"/><rect x="2960" y="680" width="40" height="230" fill="#2a1d70"/>
  <rect x="2330" y="500" width="260" height="140" rx="14" fill="#0e0c26" stroke="#8d7bff" stroke-width="6"/>
  <g id="{p}-stack"></g>
  <ellipse cx="2630" cy="905" rx="420" ry="26" fill="#05031a" opacity=".5"/>
 </g>
 <g transform="translate(2271 250)"><g id="{p}-inside" opacity="0"><g transform="scale(1.75)" opacity=".8">{person(p + "d", glow=p + "-glow")}</g></g></g>
 <g id="{p}-drops" opacity="0" fill="#7fe6ff"><path d="M2840 330 q-12 26 0 36 q12 -10 0 -36z"/><path d="M2800 400 q-10 22 0 30 q10 -8 0 -30z"/></g>
 <g transform="translate(1330 470)"><g id="{p}-sheet" opacity="0">
  <g filter="url(#{p}-shadow)"><rect x="-260" y="-330" width="520" height="660" rx="16" fill="url(#{p}-paper)"/></g>{lines}
  <text x="-210" y="150" font-family="EB Garamond" font-weight="700" font-size="34" fill="#5a4a30">CONTRACT</text>
  <line x1="-210" y1="260" x2="-20" y2="260" stroke="#3a3a3a" stroke-width="4"/><line x1="40" y1="260" x2="230" y2="260" stroke="#3a3a3a" stroke-width="4"/>
  <path id="{p}-signature" d="M-205 252 C -180 200 -160 270 -140 230 S -100 210 -80 250 S -50 230 -28 246" fill="none" stroke="#1d2f9a" stroke-width="7" stroke-linecap="round" stroke-dasharray="320" stroke-dashoffset="320"/>
  <g id="{p}-blank" opacity="0"><circle cx="135" cy="238" r="30" fill="#ff4f7d"/><text x="135" y="251" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="40" fill="#fff">?</text></g>
 </g></g>
 <g id="{p}-badge" opacity="0" transform="translate(0 0)"><g transform="translate(2630 520)"><rect x="-120" y="0" width="240" height="120" rx="14" fill="#fffaf0" stroke="#ffb23e" stroke-width="6"/><rect x="-100" y="22" width="60" height="60" rx="8" fill="#8d7bff"/><rect x="-24" y="30" width="110" height="12" rx="6" fill="#8a7f68"/><rect x="-24" y="56" width="80" height="10" rx="5" fill="#bfb49a"/><path d="M0 -300 L-60 0 M0 -300 L60 0" stroke="#ffb23e" stroke-width="6"/></g></g>
</g>"""
    stack = "".join(f'<rect x="{2720 + (k % 3) * 8}" y="{628 - k * 14}" width="150" height="12" rx="3" fill="#fffaf0" transform="rotate({(k % 3 - 1) * 2} 2795 {628 - k * 14})"/>' for k in range(9))
    svg = svg.replace(f'<g id="{p}-stack"></g>', f'<g id="{p}-stack" opacity="0">{stack}</g>')
    html = (text(f"{p}-t1", "OUTSIDE", "left:540px;top:900px;font-size:76px;color:#bff4ff;letter-spacing:.12em") +
            text(f"{p}-t2", "INSIDE", "left:2400px;top:900px;font-size:76px;color:#c9b8ff;letter-spacing:.12em") +
            text(f"{p}-t3", "BORN EMPLOYED", "left:0;right:0;text-align:center;top:70px;font-size:96px;color:#ffd98a"))
    js = f"""
  camZ("#{p}-cam", 0, 3.0, 1.0, 1.0, 960, 540);
  enter("#{p}-door", 0.1, 0.6); pop("#{p}-outside", 0.2, 0.5, 0.8);
  enter("#{p}-sheet", {t_signed - 0.15:.2f}, 0.35); tl.fromTo("#{p}-sheet",{{scale:0.5,transformOrigin:"50% 50%"}},{{scale:1,duration:0.7,ease:"elastic.out(1,0.5)",immediateRender:false}},{t_signed - 0.15:.2f});
  tl.fromTo("#{p}-signature",{{attr:{{"stroke-dashoffset":320}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.9,ease:"power2.inOut"}},{t_signed + 0.25:.2f});
  rise("#{p}-t1 span", {t_outside:.2f});
  ["#{p}-world","#{p}-t1","#{p}-t2"].forEach(function(s){{tl.fromTo(s,{{x:0}},{{x:-1380,duration:1.3,ease:"power3.inOut",immediateRender:false}},{t_works - 0.25:.2f});}});
  enter("#{p}-desk", {t_works - 0.4:.2f}, 0.3);
  pop("#{p}-inside", {t_works - 0.1:.2f}, 0.5, 0.8);
  enter("#{p}-stack", {t_works:.2f}, 0.1);
  tl.fromTo("#{p}-stack rect",{{y:-160,opacity:0}},{{y:0,opacity:1,duration:0.35,ease:"bounce.out",stagger:0.34}},{t_works:.2f});
  enter("#{p}-drops", {t_suffers:.2f}, 0.2); tl.fromTo("#{p}-drops",{{y:0}},{{y:34,duration:0.9,repeat:3,ease:"power1.in"}},{t_suffers:.2f}); vanish("#{p}-drops", {t_obeys:.2f}, 0.3);
  tl.fromTo("#{p}-inside",{{y:0}},{{y:10,duration:0.28,repeat:5,yoyo:true,ease:"sine.inOut"}},{t_obeys:.2f});
  rise("#{p}-t2 span", {t_inside:.2f});
  enter("#{p}-blank", {t_never:.2f}, 0.2);
  tl.fromTo("#{p}-inside",{{rotation:0,transformOrigin:"50% 50%"}},{{rotation:3,duration:0.12,repeat:7,yoyo:true,ease:"none"}},{t_never + 0.3:.2f});
  rise("#{p}-t3 span", {t_born:.2f}, 0.9);
  enter("#{p}-badge", {t_born:.2f}, 0.1);
  tl.fromTo("#{p}-badge",{{y:-380}},{{y:0,duration:0.9,ease:"bounce.out",immediateRender:false}},{t_born:.2f});
  camZ("#{p}-cam", {t_never - 0.2:.2f}, {max(0.5, dur - t_never + 0.2):.2f}, 1.0, 1.12, 960, 620, "power1.inOut");
""" + person_idle(p + "f", dur) + person_idle(p + "d", dur, (3.0, 7.3, 10.2))
    return composition(p, dur, svg, html, js, extra)


SCENES = [("K3", contract_3, seg(CE, SG)[1])]

if __name__ == "__main__":
    print(write_scenes(SCENES, HERE))
