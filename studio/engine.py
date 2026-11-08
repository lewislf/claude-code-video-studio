"""Scene engine: per-word timing, log-scale camera, spring, text that rises through a mask, counter, bokeh and particle background.

Typical use (see template/scenes/g1/build_g1.py):
    from engine import *
    def contract_0():
        p = "contract_0"; start, dur = seg("contract", 0)
        t = word("contract", 0, "offer")                # local time (s) within the segment
        svg = ...; html = text(f"{p}-t", "OFFER", "left:200px;top:120px")
        js = f'camZ("#{p}-cam", 0, 2, 1, 1.3, 960, 540); rise("#{p}-t span", {t});'
        return composition(p, dur, svg, html, js)
    SCENES = [("contract_0", contract_0, seg("contract", 0)[1])]
    MAP = {("contract", 0): "contract_0"}

Times come from the project's assets/voice/durations.json (tts.py) and words/<scene>.json (transcribe.py).
"""
import json, os, random, re, sys, unicodedata


PROJ = os.getcwd()  # scenes.py runs from the project root
sys.path.insert(0, PROJ)
import script as _S  # noqa: E402

_DUR = os.path.join(PROJ, "assets/voice/durations.json")
if not os.path.exists(_DUR):
    sys.exit(f"missing {_DUR}: run tts.py generate and tts.py pick first")
_TP = json.load(open(_DUR))
_TXT = {c: [t for t, _, _ in ss] for c, _, ss in _S.SCENES}
_WORDS = {}
CYAN, MAGENTA, AMBER, MINT, LILAC, RED = "#3be0ff", "#ff4fa3", "#ffb23e", "#38e8a8", "#8d7bff", "#ff4f7d"


def seg(scene, i):
    """(segment start within the scene in s, segment duration in s)."""
    return tuple(_TP[scene][i])


def text_seg(scene, i):
    return _TXT[scene][i]


def _norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def words_seg(scene, i):
    """[(text, local start, local end)] of the segment's words (times relative to the segment start)."""
    if scene not in _WORDS:
        f = os.path.join(PROJ, "words", f"{scene}.json")
        _WORDS[scene] = json.load(open(f)) if os.path.exists(f) else []
    start, dur = seg(scene, i)
    return [(w["text"], round(w["start"] - start, 2), round(w["end"] - start, 2)) for w in _WORDS[scene] if start - 0.05 <= w["start"] < start + dur]


def word(scene, i, target, n=0, default=None):
    """Local start (s) of the n-th occurrence of `target` (prefix, accent-insensitive) in the segment. If not found, `default` or proportional."""
    k = _norm(target)
    hits = [t0 for (w, t0, _) in words_seg(scene, i) if _norm(w).startswith(k)]
    if len(hits) > n:
        return max(0.0, hits[n])
    if default is not None:
        return default
    txt = [_norm(x) for x in text_seg(scene, i).split()]
    idx = next((j for j, x in enumerate(txt) if x.startswith(k)), 0)
    return round(seg(scene, i)[1] * idx / max(1, len(txt)), 2)


# ---------------------------------------------------------------- visual base (background, particles, vignette, fade in/out)
CSS = """
.scene{position:absolute;inset:0;width:1920px;height:1080px;overflow:hidden;background:#0b0a24;font-family:"IBM Plex Mono",monospace}
.scene .full{position:absolute;inset:0;width:1920px;height:1080px}
.black{position:absolute;inset:0;background:#000;pointer-events:none;z-index:50}
.tit{position:absolute;font:700 132px "EB Garamond",serif;color:#eef1f7;opacity:0;text-shadow:0 6px 40px rgba(0,0,0,.7);white-space:nowrap;letter-spacing:.02em}
.tit small{display:block;font:500 30px "IBM Plex Mono",monospace;letter-spacing:.2em;color:#ffb23e;margin-top:-4px}
.pill2{position:absolute;font:500 36px "IBM Plex Mono",monospace;letter-spacing:.14em;color:#eef1f7;opacity:0;white-space:nowrap;text-shadow:0 4px 24px #000}
.pill2 i{display:inline-block;width:18px;height:18px;border-radius:50%;margin-right:14px;vertical-align:-2px}
"""

DUST = """
(function(){var s=7;var r=function(){s=(s+0x6d2b79f5)|0;var t=Math.imul(s^(s>>>15),1|s);t=(t+Math.imul(t^(t>>>7),61|t))^t;return((t^(t>>>14))>>>0)/4294967296;};
var g=document.getElementById("@ID@-part"),colors=["#3be0ff","#8d7bff","#ff9bd0","#ffd23e"];
for(var i=0;i<30;i++){var c=document.createElementNS("http://www.w3.org/2000/svg","circle");
c.setAttribute("id","@ID@p"+i);c.setAttribute("cx",Math.round(r()*1920));c.setAttribute("cy",Math.round(200+r()*880));
c.setAttribute("r",(2+r()*4).toFixed(1));c.setAttribute("fill",colors[i%4]);c.setAttribute("opacity",(0.2+r()*0.45).toFixed(2));g.appendChild(c);
tl.fromTo("#@ID@p"+i,{y:0},{y:-(100+r()*240),duration:@DUR@,ease:"none"},0);}})();
"""

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
  function countUp(id,t0,dur,v0,v1,fmt){
    var o={v:v0};
    tl.fromTo(o,{v:v0},{v:v1,duration:dur,ease:"power2.out",onUpdate:function(){var e=document.getElementById(id);if(e)e.textContent=fmt?fmt(o.v):Math.round(o.v);}},t0);
  }
  function fadeOut(sel,t,dur){tl.fromTo(sel,{opacity:1},{opacity:0,duration:dur||0.4,immediateRender:false},t);}
  function fadeIn(sel,t,dur){tl.fromTo(sel,{opacity:0},{opacity:1,duration:dur||0.5},t);}
"""


def bokeh(i, seed, n=10, colors=("#3be0ff", "#8d7bff", "#ff4fa3", "#ffb23e")):
    rng = random.Random(seed)
    c = "".join(f'<circle cx="{rng.uniform(0, 1920):.0f}" cy="{rng.uniform(0, 1080):.0f}" r="{rng.uniform(90, 280):.0f}" fill="{rng.choice(colors)}" opacity="{rng.uniform(.06, .15):.2f}"/>' for _ in range(n))
    return f'<g id="{i}-bokeh" filter="url(#{i}-blur40)">{c}</g>'


def defs(i, extra="", bg=("#3a1d7a", "#1a1050", "#0b0a24"), seed=3):
    """Ready-made filters per scene: {i}-glow, {i}-blur6, {i}-blur40, {i}-shadow, {i}-vig, {i}-bg."""
    return f"""<defs>
<radialGradient id="{i}-bg" cx="50%" cy="46%" r="78%"><stop offset="0" stop-color="{bg[0]}"/><stop offset=".55" stop-color="{bg[1]}"/><stop offset="1" stop-color="{bg[2]}"/></radialGradient>
<radialGradient id="{i}-vig" cx="50%" cy="50%" r="72%"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".62"/></radialGradient>
<filter id="{i}-glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="{i}-blur40" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="42"/></filter>
<filter id="{i}-blur6" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="{i}-shadow" x="-30%" y="-30%" width="170%" height="180%"><feDropShadow dx="0" dy="16" stdDeviation="16" flood-color="#05031a" flood-opacity=".6"/></filter>
{extra}</defs>
<rect width="1920" height="1080" fill="url(#{i}-bg)"/>{bokeh(i, seed)}<g id="{i}-part"></g>"""


def composition(i, dur, svg, html, js, extra="", bg=("#3a1d7a", "#1a1050", "#0b0a24"), seed=3):
    """Full scene. `svg` goes inside the camera group `#{i}-cam`; `html` sits on top (text). `extra` goes into <defs>."""
    js = (JS_LIB + js.replace("@P@", i)).replace("@ID@", i).replace("@DUR@", f"{dur:.2f}")
    return f"""<template>
  <style>{CSS}</style>
  <div id="{i}-root" data-composition-id="{i}" data-width="1920" data-height="1080">
    <div class="scene">
    <svg id="{i}-svg" class="full" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">{defs(i, extra, bg, seed)}<g id="{i}-cam">{svg}</g><rect width="1920" height="1080" fill="url(#{i}-vig)" pointer-events="none"/></svg>
    {html}
    <div id="{i}-black" class="black"></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {DUST.replace("@ID@", i).replace("@DUR@", f"{dur:.2f}")}
    tl.fromTo("#{i}-bokeh",{{x:0,y:0}},{{x:-70,y:-34,duration:{dur:.2f},ease:"none"}},0);
    {js}
    tl.fromTo("#{i}-black", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.4, ease: "none" }}, 0);
    tl.fromTo("#{i}-black", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "none", immediateRender: false }}, {dur - 0.4:.2f});
    window.__timelines["{i}"] = tl;
  </script>
</template>
"""


def text(id_, txt, style="", cls="tit", height="1.3em"):
    """Big text that rises inside a mask. Animate with `rise('#id span', t)`. `style` positions the block."""
    return (f'<div id="{id_}" class="{cls}" style="{style};opacity:1;overflow:hidden;height:{height};line-height:{height}">'
            f'<span style="display:block">{txt}</span></div>')


def label(id_, txt, style="", color="#3be0ff", size=44):
    return f'<div id="{id_}" class="pill2" style="{style};font-size:{size}px;color:{color}"><i style="background:{color}"></i>{txt}</div>'


def write_scenes(scenes, folder):
    """scenes: [(id, function, dur)]. Writes compositions/<id>.html, index.html (scenes in sequence, 0.5 s apart) and timings.json."""
    os.makedirs(os.path.join(folder, "compositions"), exist_ok=True)
    hosts, t, start = [], 0.0, {}
    for k, fn, dur in scenes:
        open(os.path.join(folder, f"compositions/{k}.html"), "w").write(fn())
        hosts.append(f'<div id="{k}" data-composition-id="{k}" data-composition-src="compositions/{k}.html" data-start="{t:.2f}" data-duration="{dur:.2f}" data-track-index="1" data-width="1920" data-height="1080"></div>')
        start[k] = round(t, 2)
        t += dur + 0.5
    total = t - 0.5
    open(os.path.join(folder, "index.html"), "w").write(f"""<!doctype html>
<html lang="{getattr(_S, 'LANG', 'en')}"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@700&family=IBM+Plex+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#0b0a24}}#root{{width:100%;height:100%;position:relative}}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}" data-width="1920" data-height="1080">
{chr(10).join(hosts)}
</div><script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script></body></html>
""")
    json.dump({"start": start, "dur": {k: d for k, _, d in scenes}, "total": round(total, 2)}, open(os.path.join(folder, "timings.json"), "w"), indent=1)
    return start, total
