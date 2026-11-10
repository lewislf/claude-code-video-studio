"""Engine for the v5 scenes: fixed times, log camera, spring, text that rises through a mask, counter, person (mascot).

Typical use (see example_scene.py):
    from engine import *
    def scene_X():
        p = "X"; start, dur = seg("contract", 0)
        t_vc = 2.4                                          # local time (s) inside the segment
        svg = ...; html = ...; js = f'camZ("#X-cam", 0, 2, 1, 1.4, 960, 540); pop("#X-a", {t_vc});'
        return composition(p, dur, svg, html, js)
"""
import json, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.join(HERE, "../scenes-v3")
sys.path.insert(0, V3)
import build2 as b2
from build2 import composition2
from build import CYAN, MAGENTA, AMBER, MINT, LILAC, RED
from art2 import head_line, brain_side, BRAIN_SIDE, H_LINE

SEGMENTS = json.load(open(os.path.join(HERE, "segments.json")))


def seg(scene, i):
    """(scene start in s, segment duration in s)."""
    s = SEGMENTS[scene][i]
    return s["start"], s["dur"]


def _norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


# ---------------------------------------------------------------- helper JS (goes at the start of the scene script)
JS_LIB = r"""
  function camZ(sel,t0,dur,z0,z1,ox,oy,ease){
    var o={l:Math.log(z0)};
    tl.set(sel,{scale:z0,svgOrigin:ox+" "+oy},t0>0?0:t0);
    tl.to(o,{l:Math.log(z1),duration:dur,ease:ease||"power3.inOut",onUpdate:function(){gsap.set(sel,{scale:Math.exp(o.l),svgOrigin:ox+" "+oy});},immediateRender:false},t0);
  }
  function pop(sel,t,from,dur){
    tl.fromTo(sel,{scale:from||0.3,opacity:0,transformOrigin:"50% 50%"},{scale:1,opacity:1,duration:dur||0.7,ease:"elastic.out(1,0.45)",immediateRender:false},t);
    tl.set(sel,{opacity:0},0);
  }
  function rise(sel,t,dur){
    tl.fromTo(sel,{yPercent:125},{yPercent:0,duration:dur||0.75,ease:"expo.out",immediateRender:true},t);
  }
  function count_up(id,t0,dur,v0,v1,fmt){
    var o={v:v0};
    tl.fromTo(o,{v:v0},{v:v1,duration:dur,ease:"power2.out",onUpdate:function(){var e=document.getElementById(id);if(e)e.textContent=fmt?fmt(o.v):Math.round(o.v);}},t0);
  }
  function vanish(sel,t,dur){tl.fromTo(sel,{opacity:1},{opacity:0,duration:dur||0.4,immediateRender:false},t);}
  function enter(sel,t,dur){tl.fromTo(sel,{opacity:0},{opacity:1,duration:dur||0.5},t);}
"""


def composition(i, dur, svg, html, js, extra="", background=("#3a1d7a", "#1a1050", "#0b0a24"), seed=3):
    """Full scene. `svg` goes inside the camera group `#{i}-cam`; `html` sits on top (text)."""
    body = f'<g id="{i}-cam">{svg}</g>'
    return composition2(i, dur, body, html, JS_LIB + js.replace("@P@", i), extra, background=background, seed=seed)


def text(id_, txt, style="", cls="title", height="1.3em"):
    """Big text that rises from inside a mask. Animate with `rise('#id span', t)`. `style` positions the block."""
    return (f'<div id="{id_}" class="{cls}" style="{style};opacity:1;overflow:hidden;height:{height};line-height:{height}">'
            f'<span style="display:block">{txt}</span></div>')


def label(id_, txt, style="", color="#3be0ff", size=44):
    return f'<div id="{id_}" class="pill2" style="{style};font-size:{size}px;color:{color}"><i style="background:{color}"></i>{txt}</div>'


def person(p, tx=0, ty=0, s=1.0, glow=None):
    """The person (profile head in neon line + pink side brain + blue eye). Local box ~ x 110..300, y 28..252.
    Ids: {p}-person (group), {p}-eye (eye, can move from -3 to 3 to look), {p}-brain (brain), {p}-bob (for the sway)."""
    glow = glow or f"{p}-glow"
    return (f'<g transform="translate({tx} {ty}) scale({s})"><g id="{p}-person"><g id="{p}-bob">{head_line(p + "h", glow)}'
            f'<g id="{p}-brain" opacity=".95"><g transform="translate(196 118) scale(.82) translate(-196 -118)">{brain_side(p + "c")}</g></g>'
            f'<g id="{p}-eye"><ellipse cx="257" cy="129" rx="9" ry="5.6" fill="#0a0820" stroke="#3be0ff" stroke-width="1.2"/><circle cx="259" cy="129" r="3.6" fill="#29b6ff"/><circle cx="260.2" cy="127.8" r="1.1" fill="#fff"/></g>'
            f'<path d="M 245 118 Q 257 111 269 119" fill="none" stroke="#3be0ff" stroke-width="2" stroke-linecap="round"/></g></g></g>')


def person_idle(p, dur, blinks=(2.2, 5.1, 8.6, 12.3, 16.0, 20.5, 25.0)):
    """JS: gentle sway and blinks (deterministic). Call with the same `p` as `person`."""
    js = f'tl.fromTo("#{p}-bob",{{y:0}},{{y:-5,duration:1.6,repeat:{max(1, int(dur / 1.6))},yoyo:true,ease:"sine.inOut"}},0);'
    for t in blinks:
        if t < dur - 0.3:
            js += f'tl.fromTo("#{p}-eye",{{scaleY:1,transformOrigin:"50% 50%"}},{{scaleY:0.08,transformOrigin:"50% 50%",duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t});'
    return js


def write_scenes(scenes, folder, extra_index=""):
    """scenes: [(id, function, dur)]. Writes compositions/<id>.html and index.html (scenes in sequence, 0.5 s apart)."""
    os.makedirs(os.path.join(folder, "compositions"), exist_ok=True)
    hosts, t, start = [], 0.0, {}
    for k, fn, dur in scenes:
        open(os.path.join(folder, f"compositions/{k}.html"), "w").write(fn())
        hosts.append(f'<div id="{k}" data-composition-id="{k}" data-composition-src="compositions/{k}.html" data-start="{t:.2f}" data-duration="{dur:.2f}" data-track-index="1" data-width="1920" data-height="1080"></div>')
        start[k] = round(t, 2)
        t += dur + 0.5
    total = t - 0.5
    open(os.path.join(folder, "index.html"), "w").write(f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@700&family=IBM+Plex+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#0b0a24}}#root{{width:100%;height:100%;position:relative}}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}" data-width="1920" data-height="1080">
{chr(10).join(hosts)}{extra_index}
</div><script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script></body></html>
""")
    json.dump({"start": start, "dur": {k: d for k, _, d in scenes}, "total": round(total, 2)}, open(os.path.join(folder, "timing.json"), "w"), indent=1)
    return start, total
