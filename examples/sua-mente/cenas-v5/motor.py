"""Motor das cenas v5: tempo por palavra, câmera em log, mola, texto que sobe por máscara, contador, pessoa (mascote).

Uso típico (veja exemplo.py):
    from motor import *
    def cena_X():
        p = "X"; ini, dur = seg("contrato", 0)
        t_vc = palavra("contrato", 0, "proposta")        # tempo local (s) dentro do segmento
        svg = ...; html = ...; js = f'camZ("#X-cam", 0, 2, 1, 1.4, 960, 540); pop("#X-a", {t_vc});'
        return composicao(p, dur, svg, html, js)
"""
import json, os, re, sys, unicodedata
AQUI = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.join(AQUI, "../cenas-v3")
sys.path.insert(0, V3)
import build2 as b2
from build2 import composicao2
from build import CIANO, MAGENTA, AMBAR, MENTA, LILAS, VERM
from arte2 import cabeca_linha, cerebro_lateral, CEREBRO_LAT, H_LINHA

ROT = json.load(open(os.path.join(AQUI, "roteiro.json")))
_PAL = {}


def seg(cena, i):
    """(início da cena em s, duração do segmento em s)."""
    s = ROT[cena][i]
    return s["ini"], s["dur"]


def texto_seg(cena, i):
    return ROT[cena][i]["texto"]


def _norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def palavras_seg(cena, i):
    """[(texto, início local, fim local)] das palavras do segmento (tempos relativos ao início do segmento)."""
    if cena not in _PAL:
        f = os.path.join(AQUI, "palavras", f"{cena}.json")
        _PAL[cena] = json.load(open(f)) if os.path.exists(f) else []
    s = ROT[cena][i]
    ini, dur = s["ini"], s["dur"]
    out = [(w["text"], round(w["start"] - ini, 2), round(w["end"] - ini, 2)) for w in _PAL[cena] if ini - 0.05 <= w["start"] < ini + dur]
    return out


def palavra(cena, i, alvo, n=0, padrao=None):
    """Início local (s) da n-ésima ocorrência de `alvo` (prefixo, sem acento) no segmento. Se não achar, `padrao` ou proporcional."""
    ws = palavras_seg(cena, i)
    k = _norm(alvo)
    hits = [t0 for (w, t0, _) in ws if _norm(w).startswith(k)]
    if len(hits) > n:
        return max(0.0, hits[n])
    if padrao is not None:
        return padrao
    txt = [_norm(x) for x in ROT[cena][i]["texto"].split()]
    idx = next((j for j, x in enumerate(txt) if x.startswith(k)), 0)
    return round(ROT[cena][i]["dur"] * idx / max(1, len(txt)), 2)


# ---------------------------------------------------------------- JS de apoio (entra no começo do script da cena)
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
  function contar(id,t0,dur,v0,v1,fmt){
    var o={v:v0};
    tl.fromTo(o,{v:v0},{v:v1,duration:dur,ease:"power2.out",onUpdate:function(){var e=document.getElementById(id);if(e)e.textContent=fmt?fmt(o.v):Math.round(o.v);}},t0);
  }
  function some(sel,t,dur){tl.fromTo(sel,{opacity:1},{opacity:0,duration:dur||0.4,immediateRender:false},t);}
  function entra(sel,t,dur){tl.fromTo(sel,{opacity:0},{opacity:1,duration:dur||0.5},t);}
"""


def composicao(i, dur, svg, html, js, extra="", fundo=("#3a1d7a", "#1a1050", "#0b0a24"), seed=3):
    """Cena completa. `svg` vai dentro do grupo de câmera `#{i}-cam`; `html` fica por cima (texto)."""
    corpo = f'<g id="{i}-cam">{svg}</g>'
    return composicao2(i, dur, corpo, html, JS_LIB + js.replace("@P@", i), extra, fundo=fundo, seed=seed)


def texto(id_, txt, estilo="", cls="tit", alt="1.3em"):
    """Texto grande que sobe por dentro de uma máscara. Use `rise('#id span', t)` para animar. `estilo` posiciona o bloco."""
    return (f'<div id="{id_}" class="{cls}" style="{estilo};opacity:1;overflow:hidden;height:{alt};line-height:{alt}">'
            f'<span style="display:block">{txt}</span></div>')


def rotulo(id_, txt, estilo="", cor="#3be0ff", tam=44):
    return f'<div id="{id_}" class="pill2" style="{estilo};font-size:{tam}px;color:{cor}"><i style="background:{cor}"></i>{txt}</div>'


def pessoa(p, tx=0, ty=0, s=1.0, glow=None):
    """A pessoa (cabeça de perfil em linha neon + cérebro rosa lateral + olho azul). Caixa local ~ x 110..300, y 28..252.
    Ids: {p}-pessoa (grupo), {p}-olho (olho, pode andar de -3 a 3 para olhar), {p}-cer (cérebro), {p}-bob (para o balanço)."""
    glow = glow or f"{p}-glow"
    return (f'<g transform="translate({tx} {ty}) scale({s})"><g id="{p}-pessoa"><g id="{p}-bob">{cabeca_linha(p + "h", glow)}'
            f'<g id="{p}-cer" opacity=".95"><g transform="translate(196 118) scale(.82) translate(-196 -118)">{cerebro_lateral(p + "c")}</g></g>'
            f'<g id="{p}-olho"><ellipse cx="257" cy="129" rx="9" ry="5.6" fill="#0a0820" stroke="#3be0ff" stroke-width="1.2"/><circle cx="259" cy="129" r="3.6" fill="#29b6ff"/><circle cx="260.2" cy="127.8" r="1.1" fill="#fff"/></g>'
            f'<path d="M 245 118 Q 257 111 269 119" fill="none" stroke="#3be0ff" stroke-width="2" stroke-linecap="round"/></g></g></g>')


def vida_pessoa(p, dur, piscadas=(2.2, 5.1, 8.6, 12.3, 16.0, 20.5, 25.0)):
    """JS: balanço suave e piscadas (determinístico). Chame com o mesmo `p` de `pessoa`."""
    js = f'tl.fromTo("#{p}-bob",{{y:0}},{{y:-5,duration:1.6,repeat:{max(1, int(dur / 1.6))},yoyo:true,ease:"sine.inOut"}},0);'
    for t in piscadas:
        if t < dur - 0.3:
            js += f'tl.fromTo("#{p}-olho",{{scaleY:1,transformOrigin:"50% 50%"}},{{scaleY:0.08,transformOrigin:"50% 50%",duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t});'
    return js


def escreve_cenas(cenas, pasta, indice_extra=""):
    """cenas: [(id, funcao, dur)]. Escreve compositions/<id>.html e index.html (cenas em sequência, 0,5 s de folga)."""
    os.makedirs(os.path.join(pasta, "compositions"), exist_ok=True)
    hosts, t, ini = [], 0.0, {}
    for k, fn, dur in cenas:
        open(os.path.join(pasta, f"compositions/{k}.html"), "w").write(fn())
        hosts.append(f'<div id="{k}" data-composition-id="{k}" data-composition-src="compositions/{k}.html" data-start="{t:.2f}" data-duration="{dur:.2f}" data-track-index="1" data-width="1920" data-height="1080"></div>')
        ini[k] = round(t, 2)
        t += dur + 0.5
    total = t - 0.5
    open(os.path.join(pasta, "index.html"), "w").write(f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@700&family=IBM+Plex+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#0b0a24}}#root{{width:100%;height:100%;position:relative}}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}" data-width="1920" data-height="1080">
{chr(10).join(hosts)}{indice_extra}
</div><script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script></body></html>
""")
    json.dump({"inicio": ini, "dur": {k: d for k, _, d in cenas}, "total": round(total, 2)}, open(os.path.join(pasta, "tempos.json"), "w"), indent=1)
    return ini, total
