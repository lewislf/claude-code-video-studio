"""What is left of the v2 build: which segments come from which clip (SUBST, read by assemble_final.py)
and the pieces ../trailers.py uses for the 3 fiction trailer segments (visuals, corner label, CSS, grain and vignette).
"""
import json, os

W, H = 1920, 1080
HERE = os.path.dirname(os.path.abspath(__file__))
XF = 0.45  # crossfade between segments (s); trailer cuts run this much past the segment

DARK, INK, MUTED = "#0b0d12", "#eef1f7", "#8a93a8"
PAPER, BLACK, RED = "#efe8da", "#1b1b1b", "#8e1b1b"
CYAN, AMBER, LILAC = "#5ad1c6", "#f2b84b", "#a78bfa"
LABELS = {"fiction": ("FICTION", AMBER)}
TRAILER = {
    "severance": ("assets/trailers/severance_h264.mp4", [(24, 3.2), (39.5, 2.6), (33.5, 3), (147, 3.4), (9, 3), (63, 2.5)],
                  "Severance · Apple TV+ · official trailer"),
    "matrix": ("assets/trailers/matrix_h264.mp4", [(84, 3.4), (72, 3), (18.5, 2.6), (114, 3), (135, 3), (42, 3)],
               "The Matrix · Warner Bros. · trailer"),
}

SUBST = {  # (scene, segment index) -> new clip; ms = start inside the clip
    ("mapping", 1): dict(clip="A", ms=0), ("mapping", 2): dict(clip="A", ms=11.66), ("mapping", 5): dict(clip="B", ms=0),
    ("reading", 2): dict(clip="D", ms=0), ("reading", 7): dict(clip="E", ms=0), ("reading", 12): dict(clip="F", ms=0),
    ("opening", 0): dict(clip="M1", ms=0), ("opening", 1): dict(clip="M1", ms=10.99),
    ("opening", 2): dict(clip="M2", ms=0), ("opening", 3): dict(clip="M3", ms=0),
    ("writing", 1): dict(clip="M4", ms=0), ("writing", 3): dict(clip="M5", ms=0),
    ("writing", 4): dict(clip="M6", ms=0), ("writing", 6): dict(clip="M7", ms=0),
    ("closing", 7): dict(clip="M8", ms=0),
    ("reality", 0): dict(clip="C", ms=0), ("reality", 5): dict(clip="C", ms=7.45), ("reality", 6): dict(clip="C", ms=19.75),
}

_MAP5 = os.path.join(HERE, "assets/clips/clip_map.json")
if os.path.exists(_MAP5):  # v5 scenes (one per segment), cut by scenes/assemble.py
    for _c, _d in json.load(open(_MAP5)).items():
        for _i, _id in _d.items():
            if os.path.exists(os.path.join(HERE, f"assets/clips/{_id}.mp4")):
                SUBST[(_c, int(_i))] = dict(clip=_id, ms=0)

for _c, _i in (("opening", 5), ("contract", 1), ("reality", 1)):  # trailers with English text (../trailers.py)
    if os.path.exists(os.path.join(HERE, f"assets/clips_en/{_c}_{_i}.mp4")):
        SUBST[(_c, _i)] = dict(clip=f"../clips_en/{_c}_{_i}", ms=0)


# Each visual returns (html, tweens). {t0} and {d} become the segment start and duration; ids carry the segment prefix p.
# <video> tags go loose at the scene root (s["_loose"]), behind the segment, because video inside a timed clip does not render.

def trailer_cuts(p, s, key):
    """Trailer cuts in sequence."""
    file, cuts, source = TRAILER[key]
    t, d, i = s["_t0"], s["_d"] + XF, 0
    end = t + d
    while t < end - 0.05:
        ms, dur = cuts[i % len(cuts)]
        dur = min(dur, end - t)
        s["_loose"].append(f'<video id="{p}-v{i}" class="clip vid" src="{file}" muted data-start="{t:.2f}" data-duration="{dur:.2f}" data-media-start="{ms}"></video>')
        t += dur; i += 1
    return f'<div class="seg"><div class="fiction-band">{source}</div></div>', []


TRIO = [("2022", "Severance", "splits your memory in two"), ("1999", "The Matrix", "builds the world you see"),
        ("2010", "Roko's Basilisk", "punishes anyone who doesn't obey")]
BASILISK_EYE = (f'<svg class="icon" viewBox="0 0 400 400"><path d="M60 200 Q200 90 340 200 Q200 310 60 200 Z" fill="#120a0a" stroke="{RED}" stroke-width="3"/>'
                f'<circle cx="200" cy="200" r="70" fill="{RED}"/><ellipse cx="200" cy="200" rx="9" ry="56" fill="#000"/></svg>')


def fiction_trio(p, s):
    """Three panels: Severance and The Matrix over their trailers, the basilisk over its eye."""
    t0, d = s["_t0"], s["_d"] + XF
    for k, (key, ms) in enumerate((("severance", 39), ("matrix", 84))):
        s["_loose"].append(f'<video id="{p}-pv{k}" class="clip pv" src="{TRAILER[key][0]}" muted data-start="{t0:.2f}" data-duration="{d:.2f}" '
                           f'data-media-start="{ms}" style="left:{k * 640}px;width:640px"></video>')
    panels = "".join(f'<div id="{p}-p{i}" class="panel{" hollow" if i < 2 else ""}">{BASILISK_EYE if i == 2 else ""}<div class="panel-c">'
                     f'<div class="mono">{year}</div><div class="panel-n">{name}</div><div class="panel-l">{line}</div></div></div>'
                     for i, (year, name, line) in enumerate(TRIO))
    tw = [f'tl.fromTo("#{p}-p{i}",{{opacity:0,y:60}},{{opacity:1,y:0,duration:0.7,ease:"expo.out"}},{{t0}}+{{d}}*{0.12 + i * 0.27:.2f});' for i in range(3)]
    return f'<div class="seg"><div class="trio">{panels}</div></div>', tw


VISUALS = {"fiction_trio": fiction_trio, "severance": lambda p, s: trailer_cuts(p, s, "severance"),
           "matrix": lambda p, s: trailer_cuts(p, s, "matrix")}


def label_html(key):
    if key not in LABELS:
        return ""
    text, color = LABELS[key]
    return f'<div class="label" style="color:{color};border-color:{color}">{text}</div>'


CSS = f"""
#root{{position:absolute;inset:0;overflow:hidden;background:{DARK};font-family:"Inter",sans-serif}}
.seg{{position:absolute;inset:0;overflow:hidden}}
.dark{{background:{DARK};color:{INK}}} .paper{{background:{PAPER};color:{BLACK}}} .black{{background:#000;color:{INK}}}
.full{{position:absolute;inset:0;width:100%;height:100%}} .cam{{position:absolute;inset:0;transform-origin:50% 55%}}
.kb{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:50% 50%}}
.vid{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}} .pv{{position:absolute;top:0;height:100%;object-fit:cover}}
.shade-b{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.35) 0%,rgba(0,0,0,0) 30%,rgba(0,0,0,0) 55%,rgba(0,0,0,.75) 100%)}}
.credit{{position:absolute;left:72px;bottom:40px;font:400 20px "IBM Plex Mono",monospace;color:rgba(238,241,247,.6)}}
.fiction-band{{position:absolute;right:72px;bottom:44px;font:400 24px "IBM Plex Mono",monospace;color:{AMBER};background:rgba(0,0,0,.6);padding:8px 14px}}
.center{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:36px;text-align:center;padding:0 200px}}
.middle{{position:absolute;left:180px;right:180px;top:50%;transform:translateY(-50%);text-align:center}}
.bottom{{position:absolute;left:180px;right:180px;bottom:120px;text-align:center}}
.shadow{{text-shadow:0 4px 30px rgba(0,0,0,.9)}}
.phrase{{font-family:"EB Garamond",serif;font-size:84px;line-height:1.12;font-weight:500}} .phrase-p{{font-size:68px}}
.phrase-g{{font-family:"EB Garamond",serif;font-size:150px;line-height:1.05;font-weight:700;letter-spacing:-0.01em}}
.word{{display:inline-block}}
.mono{{font-family:"IBM Plex Mono",monospace;letter-spacing:.2em;font-size:30px}}
.over{{position:absolute;left:0;right:0;top:70px;text-align:center;color:#5d5446}} .over.light{{color:{INK};text-shadow:0 2px 12px #000}}
.film-title{{font-family:"EB Garamond",serif;font-size:112px;font-weight:700;letter-spacing:.1em;color:{INK}}}
.title-line{{width:900px;height:3px;background:{AMBER};transform-origin:left}}
.label{{position:absolute;left:72px;top:60px;font:500 28px "IBM Plex Mono",monospace;letter-spacing:.18em;border:2px solid;padding:10px 18px;z-index:5;background:rgba(11,13,18,.82)}}
.source{{position:absolute;right:72px;bottom:56px;font:400 26px "IBM Plex Mono",monospace;color:{MUTED}}} .source.dim{{color:#5d5446}}
.doc{{position:absolute;left:560px;top:110px;width:800px;height:860px;background:#fbf8f1;box-shadow:0 30px 60px rgba(0,0,0,.25);padding:64px;color:{BLACK}}}
.doc-top{{display:flex;justify-content:space-between;font:600 28px "IBM Plex Mono",monospace;border-bottom:4px solid {BLACK};padding-bottom:16px;margin-bottom:40px}}
.doc-lines i{{display:block;height:14px;background:#dcd5c6;margin:0 0 22px;border-radius:4px}} .doc-lines i:nth-child(3n){{width:70%}}
.doc-lines.dim i{{background:#2c3342}}
.page{{position:absolute;left:150px;top:90px;width:760px;height:900px;overflow:hidden;background:#fff;box-shadow:0 40px 80px rgba(0,0,0,.35)}}
.page img{{width:100%;display:block;transform-origin:50% 0}} .page.fake{{padding:60px}}
.card{{position:absolute;left:1010px;top:200px;width:780px;color:{BLACK}}}
.card-r{{color:{RED};margin-bottom:30px;font-size:28px}}
.card-t{{position:relative;font:700 60px/1.12 "EB Garamond",serif;margin-bottom:30px}}
.mark{{position:absolute;left:-12px;right:-12px;top:6px;bottom:0;background:{AMBER};opacity:.45;transform-origin:left;z-index:0}} .tt{{position:relative;z-index:1}}
.card-a{{font:italic 36px "EB Garamond",serif;color:#4a443a}}
.portrait{{display:flex;align-items:center;gap:26px;margin-top:50px}} .portrait img{{width:170px;height:170px;object-fit:cover;border-radius:50%;filter:grayscale(.3)}}
.portrait span{{font:600 34px "EB Garamond",serif}} .portrait i{{font:400 18px "IBM Plex Mono",monospace;color:#7a705e;font-style:normal}}
.stamp{{position:absolute;right:40px;top:380px;font:700 50px "IBM Plex Mono",monospace;color:{RED};border:6px solid {RED};padding:12px 22px;transform:rotate(-12deg);background:rgba(251,248,241,.7)}}
.svg-leg{{font:500 40px "IBM Plex Mono",monospace;fill:{BLACK}}} .dark .svg-leg{{fill:{INK}}}
.svg-big{{font:700 64px "EB Garamond",serif;fill:{BLACK}}}
.contract .sig{{display:flex;justify-content:space-between;font:400 40px "EB Garamond",serif;border-top:2px solid #cfc6b4;padding:26px 0}}
.ok{{color:#177a3c}} .no{{color:{RED}}}
.caveat{{position:absolute;left:300px;right:300px;top:50%;transform:translateY(-50%)}}
.caveat-t{{color:{RED};margin-bottom:40px}} .caveat-l{{font:500 56px/1.25 "EB Garamond",serif;margin-bottom:28px}} .caveat-l span{{color:{RED};margin-right:24px}}
.folder{{position:absolute;left:460px;top:180px;width:1000px;height:720px}}
.tab{{width:360px;height:70px;background:#b99b62;border-radius:14px 14px 0 0;font:700 32px "IBM Plex Mono",monospace;color:#2b2112;padding:16px 30px;letter-spacing:.15em}}
.folder-c{{height:650px;background:#caa96c;border-radius:0 14px 14px 14px;padding:80px;color:#2b2112;box-shadow:0 30px 80px rgba(0,0,0,.5)}}
.folder-name{{font:700 170px "EB Garamond",serif;margin-top:60px}}
.quote{{font:italic 500 76px/1.2 "EB Garamond",serif;max-width:1400px}} .source-c{{font:400 30px "IBM Plex Mono",monospace;color:{MUTED}}}
.local{{position:absolute;left:72px;bottom:60px;color:{MUTED}}}
.screen-mock{{position:absolute;left:360px;top:160px;width:1200px;height:740px;background:#fbf8f1;border:14px solid #2a2e38;border-radius:24px}}
.target{{position:absolute;right:300px;top:200px;width:140px;height:140px;border-radius:50%;border:10px solid {CYAN}}}
.cursor{{position:absolute;left:600px;top:370px;width:0;height:0;border-left:30px solid transparent;border-right:30px solid transparent;border-bottom:70px solid {BLACK};rotate:-30deg}}
.phones{{position:absolute;left:260px;top:170px;display:flex;gap:100px}}
.phone{{width:420px;height:800px;background:#151922;border:10px solid #2a3040;border-radius:50px;padding:50px 34px;display:flex;flex-direction:column;gap:22px}} .phone .mono{{font-size:24px;letter-spacing:.05em;color:{MUTED}}}
.post{{height:110px;border-radius:14px}}
.date-top{{position:absolute;left:0;right:0;top:80px;text-align:center;color:{MUTED}}}
.num-side{{position:absolute;right:140px;top:430px;font:700 110px "EB Garamond",serif;text-align:right}} .num-side span{{display:block;font:400 30px "IBM Plex Mono",monospace;color:{MUTED}}}
.terms{{position:absolute;left:560px;top:0;width:800px;height:1080px;overflow:hidden;background:#141821}}
.scroll i{{display:block;height:12px;background:#2c3342;margin:24px 50px;border-radius:4px}} .scroll i:nth-child(4n){{width:55%}}
.accepted{{position:absolute;left:0;right:0;bottom:120px;text-align:center;font:500 46px "Inter",sans-serif}}
.rights{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:30px;font:700 104px "EB Garamond",serif}}
.list-t{{position:absolute;left:300px;top:150px;color:{CYAN}}}
.list{{position:absolute;left:300px;right:300px;top:54%;transform:translateY(-50%);display:flex;flex-direction:column;gap:44px}}
.item{{font:500 68px "EB Garamond",serif}} .item span{{color:{CYAN};margin-right:30px}}
.question{{position:absolute;left:300px;right:200px;top:200px}} .question-t{{color:{AMBER};margin-bottom:60px}}
.question-l{{font:600 96px/1.15 "EB Garamond",serif;margin-bottom:18px}} .question-l span{{font:400 30px "IBM Plex Mono",monospace;color:{MUTED};margin-right:36px;vertical-align:middle}}
.trio{{position:absolute;inset:0;display:flex}} .panel{{flex:1;position:relative;overflow:hidden;border-right:2px solid #1a1d24;background:#0b0d12}}
.panel-c{{position:absolute;left:50px;right:40px;bottom:110px;text-shadow:0 2px 20px #000}} .panel-c .mono{{color:{AMBER}}}
.panel-n{{font:700 76px "EB Garamond",serif;margin:14px 0;color:{INK}}} .panel-l{{font:italic 40px "EB Garamond",serif;color:#cfd5e2}}
.icon{{position:absolute;left:120px;top:180px;width:400px;height:400px;opacity:.85}}
.panel.hollow{{background:linear-gradient(180deg,rgba(0,0,0,0) 40%,rgba(0,0,0,.85) 100%)}}
.desk{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 60%,#2a2116 0%,#0b0d12 70%)}}
.mini-folder{{position:absolute;width:250px;box-shadow:0 20px 40px rgba(0,0,0,.6)}} .mini-tab{{width:100px;height:28px;background:#b99b62;border-radius:8px 8px 0 0}}
.mini-c{{height:300px;background:#caa96c;border-radius:0 8px 8px 8px;padding:30px 22px;font:700 26px "IBM Plex Mono",monospace;color:#2b2112;letter-spacing:.06em}}
.trauma-w{{position:absolute;top:300px;width:440px;text-align:center;font:italic 600 80px "EB Garamond",serif}}
.drug{{position:absolute;left:1080px;top:340px;width:700px}} .drug-n{{font:700 120px "EB Garamond",serif}} .drug-l{{font:400 44px/1.3 "EB Garamond",serif;color:#4a443a}}
.score{{position:absolute;left:260px;right:260px;top:230px}} .score-l{{display:flex;gap:50px;align-items:baseline;border-top:3px solid #cfc6b4;padding:40px 0}}
.score-l b{{font:700 80px "EB Garamond",serif;width:200px}} .score-l span{{font:400 46px "EB Garamond",serif;flex:1}} .score-l i{{font:600 46px "EB Garamond",serif;font-style:normal}}
.score-x{{margin-top:50px;font:italic 60px "EB Garamond",serif;color:{RED};text-align:center}}
.decide{{position:absolute;width:600px;text-align:center;font:600 76px "EB Garamond",serif}} .decide-t{{position:absolute;left:0;right:0;top:80px;text-align:center;color:{AMBER}}}
.caption-g{{position:absolute;left:0;right:0;bottom:120px;text-align:center;font:700 120px "EB Garamond",serif;color:{CYAN};text-shadow:0 4px 30px #000}}
.caption-b{{position:absolute;left:0;right:0;bottom:80px;text-align:center;font:400 36px "IBM Plex Mono",monospace;color:{INK};text-shadow:0 2px 12px #000}}
.nums{{position:absolute;right:110px;top:250px;text-align:right;text-shadow:0 4px 30px #000}} .nums b{{display:block;font:700 130px/1 "EB Garamond",serif}}
.nums span{{display:block;font:400 32px "IBM Plex Mono",monospace;color:{CYAN};margin:8px 0 50px}}
.slices{{position:absolute;left:260px;top:330px;width:700px;height:520px}} .slice{{position:absolute;inset:0;background:rgba(90,209,198,.08);border:2px solid rgba(90,209,198,.5);transform-origin:50% 50%}}
.scan{{position:absolute;left:-30px;right:-30px;top:0;height:4px;background:{AMBER};box-shadow:0 0 30px {AMBER}}}
.steps{{position:absolute;left:1130px;top:330px;display:flex;flex-direction:column;gap:70px;font:600 58px "EB Garamond",serif}}
.comp{{position:absolute;left:200px;right:200px;top:290px}} .comp-l{{margin-bottom:80px}} .comp-l span{{font:400 34px "IBM Plex Mono",monospace;color:{MUTED}}}
.bar{{height:60px;background:#151922;margin:16px 0}} .bar i{{display:block;height:100%}} .comp-l b{{font:700 90px "EB Garamond",serif}}
.comp-note{{color:{MUTED};font-size:24px}}
.four-n{{position:absolute;left:0;right:0;top:120px;text-align:center;font:700 130px "EB Garamond",serif;color:{RED}}}
.you{{position:absolute;left:0;right:0;bottom:100px;text-align:center;color:{AMBER};font-size:40px;text-shadow:0 2px 12px #000}}
.col{{position:absolute;top:0;width:40px;font:400 40px/1.1 "IBM Plex Mono",monospace;color:#3fd16a;text-shadow:0 0 12px #2fa04f;word-break:break-all;opacity:.85}}
.counter{{position:absolute;left:50%;top:40px;transform:translateX(-50%);padding:4px 34px;background:rgba(11,13,18,.88);white-space:nowrap;font:700 96px "EB Garamond",serif;color:{INK};text-shadow:0 4px 30px #000}}
.tri-t{{position:absolute;left:0;right:0;top:150px;text-align:center;color:{LILAC}}} .tris{{position:absolute;left:150px;right:150px;top:300px;display:flex;gap:50px}}
.tri{{flex:1;border:3px solid rgba(167,139,250,.25);padding:50px 40px;font:500 52px/1.2 "EB Garamond",serif;min-height:460px}} .tri b{{display:block;font:700 90px "EB Garamond",serif;color:{LILAC}}}
.post-f{{position:absolute;left:460px;top:200px;width:1000px;background:#151922;border:2px solid #2a3040;border-radius:16px;padding:50px;transform-origin:50% 50%}}
.post-f.small{{left:560px;top:260px;width:800px}}
.post-h{{display:flex;justify-content:space-between;font:400 28px "IBM Plex Mono",monospace;color:{MUTED};margin-bottom:30px}} .post-h b{{color:{INK}}}
.post-u{{font:400 32px "Inter",sans-serif;color:{MUTED};margin-bottom:20px}} .post-u b{{color:{AMBER}}}
.post-t{{font:700 64px/1.15 "EB Garamond",serif;margin-bottom:40px}}
.copy{{position:absolute;font:400 22px "IBM Plex Mono",monospace;color:{MUTED};border:1px solid #2a3040;padding:10px 14px;background:#11141b}}
.ban{{position:absolute;left:0;right:0;bottom:130px;text-align:center;color:{RED}}}
.book{{position:absolute;left:300px;top:160px;width:540px;height:760px;background:#1b2433;color:{INK};padding:60px 50px;box-shadow:30px 40px 80px rgba(0,0,0,.35);transform-origin:0 50%}}
.book-a{{font:400 30px "IBM Plex Mono",monospace;letter-spacing:.1em;color:{AMBER}}} .book-t{{font:700 76px/1.08 "EB Garamond",serif;margin:50px 0}}
.book-r{{position:absolute;bottom:50px;right:50px}}
.book-note{{position:absolute;left:1000px;top:330px;width:760px;font:500 58px/1.25 "EB Garamond",serif}} .book-note .mono{{margin-bottom:30px}} .book-note .pq{{margin-top:40px;color:#5d5446;font-size:26px}}
.robot-x{{position:absolute;left:0;right:0;top:250px;display:flex;justify-content:center}}
.groups{{position:absolute;left:150px;right:150px;top:330px;display:flex;justify-content:space-around;font:600 64px "EB Garamond",serif;text-align:center}}
.silhouettes{{display:flex;gap:16px;justify-content:center;margin-bottom:30px}} .silhouettes i{{width:80px;height:220px;background:#2a3040;border-radius:40px 40px 10px 10px}}
"""


def grain_vignette(total):
    n = max(1, int(total / 0.5))
    return f"""<div id="grain-overlay" style="position:absolute;inset:0;pointer-events:none;z-index:100;overflow:hidden"><div class="grain-texture"></div></div>
      <div id="hf-vignette" style="position:absolute;inset:0;pointer-events:none;z-index:90"></div>
      <style>
        @keyframes hf-grain-noise {{0%,100%{{transform:translate(0,0)}}10%{{transform:translate(-5%,-5%)}}20%{{transform:translate(-10%,5%)}}30%{{transform:translate(5%,-10%)}}40%{{transform:translate(-5%,15%)}}50%{{transform:translate(-10%,5%)}}60%{{transform:translate(15%,0)}}70%{{transform:translate(0,10%)}}80%{{transform:translate(-15%,0)}}90%{{transform:translate(10%,5%)}}}}
        #grain-overlay .grain-texture{{position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");opacity:.11;animation:hf-grain-noise .5s steps(1) {n} both}}
        #hf-vignette{{background:radial-gradient(ellipse at center,transparent 50%,rgba(0,0,0,.6) 100%)}}
      </style>"""
