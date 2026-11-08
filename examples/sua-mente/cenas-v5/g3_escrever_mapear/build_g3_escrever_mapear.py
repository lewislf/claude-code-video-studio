"""Cenas v5, grupo g3: escrever 0, 2, 5, 7 e mapear 0, 3, 4, 6, 7, 8.

  python3 build_g3_escrever_mapear.py      # escreve compositions/, index.html, tempos.json desta pasta

Reaproveita: rato e caixa isométrica (cenas-v4/build4.py), mosca, rede de neurônios e cérebro de mosca
(cenas-v3/build2.py, arte2.py), a pessoa (motor.py). Páginas reais dos artigos em assets/ (cópia de video-v2/assets/docs).
"""
import json, math, os, random, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
sys.path.insert(0, os.path.join(AQUI, "../../cenas-v4"))
from motor import *
from build4 import rato, caixa, grad_caixa, bolt
from build2 import rede_rica
from arte2 import mosca_rica, mosca_defs, cerebro_card
from build import caminho
import gente as G   # módulo, não *: este arquivo já tem um orbe() próprio (esfera com caixinha)
PASTA = os.path.dirname(os.path.abspath(__file__))  # motor também exporta AQUI (cenas-v5); não usar AQUI aqui


def humano(p, var="casa", pose="sentado", x=0, y=0, s=1.0, espelho=False, cores=None, cena=None, cadeira=True):
    """A pessoa de verdade (gente.py) posicionada. O grupo {p}-cabW do gente traz transform no atributo; aqui ele vira
    grupo externo + interno para o vida_gente poder animar sem jogar a cabeça em (0,0) (GOTCHAS 1).
    cores: {cor_original: cor_nova} para desenhar outra pessoa com as mesmas peças."""
    g = G.gente(p, var, pose, glow=f"{cena or p}-glow", cadeira=cadeira)
    g, n = re.subn(rf'<g id="{p}-cabW" transform="([^"]+)">', rf'<g transform="\1"><g id="{p}-cabW">', g, count=1)
    assert n == 1 and g.endswith("</g></g></g>")
    g = g + "</g>"
    for a, b in (cores or {}).items():
        g = g.replace(a, b)
    return f'<g transform="translate({x} {y}) scale({-s if espelho else s} {s})">{g}</g>'


def anc(var, pose, nome):
    return G.ANCORAS[("casa" if var == "casa" else "trabalho", pose, 30)][nome]


def ombro(var, pose):
    """svgOrigin do braço: coordenada local do ombro (o % da caixa erra, a caixa do braço novo inclui sombras recortadas)."""
    x, y = anc(var, pose, "ombro_braco")
    return f'svgOrigin:"{x} {y}"'


def pescoco(var, pose):
    x, y = anc(var, pose, "cabeca_centro")
    return f'svgOrigin:"{x} {y + 50:.0f}"'


TEMPOS = {}


def T(cena, sg, w, n=0, d=None):
    t = palavra(cena, sg, w, n, d)
    TEMPOS.setdefault(f"{cena}_{sg}", []).append((w, n, t))
    return t


# ---------------------------------------------------------------- JS extra: câmera com vários pontos (uma origem só)
JS_G3 = r"""
  function camK(sel,ox,oy,ks){
    var o={l:Math.log(ks[0][1])};
    tl.set(sel,{scale:ks[0][1],svgOrigin:ox+" "+oy},0);
    for(var i=1;i<ks.length;i++){
      tl.fromTo(o,{l:Math.log(ks[i-1][1])},{l:Math.log(ks[i][1]),duration:Math.max(0.05,ks[i][0]-ks[i-1][0]),ease:ks[i][2]||"power3.inOut",
        onUpdate:function(){gsap.set(sel,{scale:Math.exp(o.l),svgOrigin:ox+" "+oy});},immediateRender:false},ks[i-1][0]);
    }
  }
  function sai(sel,t,dur){tl.fromTo(sel,{yPercent:0},{yPercent:-125,duration:dur||0.5,ease:"expo.in",immediateRender:false},t);}
  function marca(sel,t,dur){tl.fromTo(sel,{scaleX:0,transformOrigin:"0% 50%"},{scaleX:1,transformOrigin:"0% 50%",duration:dur||0.6,ease:"power2.inOut"},t);}
  function traco(sel,t,dur,len){tl.fromTo(sel,{attr:{"stroke-dashoffset":len||2000}},{attr:{"stroke-dashoffset":0},duration:dur||1,ease:"power2.inOut"},t);}
"""


def comp(p, dur, svg, html, js, extra="", **kw):
    return composicao(p, dur, svg, html, JS_G3 + js, extra, **kw)


def tit(id_, txt, estilo, cls="tit"):
    """Texto grande que sobe por máscara (EB Garamond)."""
    return texto(id_, txt, estilo, cls)


def mono(id_, txt, estilo, cor="#bff4ff", tam=56):
    return texto(id_, txt, f"{estilo};font:500 {tam}px 'IBM Plex Mono',monospace;letter-spacing:.14em;color:{cor}", "tit", "1.35em")


# ---------------------------------------------------------------- peças
def pasta_defs(p):
    return (f'<linearGradient id="{p}-pT" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a44c4"/><stop offset="1" stop-color="#2c1f80"/></linearGradient>'
            f'<linearGradient id="{p}-pF" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7d62e8"/><stop offset="1" stop-color="#4330a8"/></linearGradient>'
            f'<linearGradient id="{p}-papel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#e9dcc2"/></linearGradient>')


def pasta(p, folha="", frente=""):
    """Pasta de arquivo centrada em (0,0), ~640 x 470. Ids: {p}-pasta, {p}-folha (sobe ao abrir), {p}-frente (abre)."""
    return f"""<g id="{p}-pasta">
<ellipse cx="0" cy="252" rx="360" ry="26" fill="#05031a" opacity=".55"/>
<path d="M-320 -200 L-300 -244 L-110 -244 L-88 -200 L320 -200 L320 230 L-320 230 Z" fill="url(#{p}-pT)" stroke="#8d7bff" stroke-width="4" stroke-linejoin="round"/>
<g transform="translate(0 0)"><g id="{p}-folha"><g filter="url(#{p}-sombra)"><rect x="-270" y="-250" width="540" height="420" rx="10" fill="url(#{p}-papel)"/></g>{folha}</g></g>
<g transform="translate(0 230)"><g id="{p}-frente"><g transform="translate(0 -230)">
<path d="M-320 -130 L320 -150 L320 230 L-320 230 Z" fill="url(#{p}-pF)" stroke="#3be0ff" stroke-width="5" stroke-linejoin="round" filter="url(#{p}-glow)"/>
<path d="M-300 -112 L300 -130" stroke="#fff" stroke-opacity=".35" stroke-width="6" stroke-linecap="round"/>
{frente}</g></g></g></g>"""


def monitor(p, x, y, w, h, tela=""):
    """Monitor (bezel do B) com a área de tela em (x,y,w,h). `tela` vai recortado dentro."""
    return f"""<g filter="url(#{p}-sombra)">
<rect x="{x - 26}" y="{y - 26}" width="{w + 52}" height="{h + 52}" rx="36" fill="url(#{p}-bezel)" stroke="#8d7bff" stroke-width="4"/>
<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="url(#{p}-tela)"/>
<rect x="{x + w / 2 - 40}" y="{y + h + 26}" width="80" height="70" fill="url(#{p}-bezel)"/><rect x="{x + w / 2 - 160}" y="{y + h + 92}" width="320" height="24" rx="12" fill="url(#{p}-bezel)" stroke="#8d7bff" stroke-width="3"/></g>
<clipPath id="{p}-tcp"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18"/></clipPath><g clip-path="url(#{p}-tcp)">{tela}<path d="M{x} {y} L {x + w * .4} {y} L {x + w * .1} {y + h} L {x} {y + h} Z" fill="#fff" opacity=".04"/></g>"""


def monitor_defs(p):
    return (f'<linearGradient id="{p}-bezel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a4a9a"/><stop offset="1" stop-color="#1b1b4a"/></linearGradient>'
            f'<linearGradient id="{p}-tela" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16143a"/><stop offset="1" stop-color="#0a1a3a"/></linearGradient>')


def rede_defs(p):
    return f'<radialGradient id="{p}-lobo" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="#3b5bff" stop-opacity=".3"/><stop offset="1" stop-color="#3b5bff" stop-opacity=".05"/></radialGradient>'


def cer_defs(p):
    return f'<radialGradient id="{p}-cer" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#1c6fa0" stop-opacity=".9"/><stop offset="1" stop-color="#0c2e66" stop-opacity=".95"/></radialGradient>'


def pagina(p, img, w, ih, marcas):
    """Página real do artigo (imagem `assets/{img}.png`, largura w em px de tela, ih = altura/largura). Origem no canto sup. esq.
    marcas: [(id, x, y, largura, altura, cor)] em pixels da imagem original (1600 de largura)."""
    k = w / 1600
    ms = "".join(f'<g transform="translate({x * k:.1f} {y * k:.1f})"><rect id="{p}-{i}" width="{lw * k:.1f}" height="{lh * k:.1f}" rx="3" fill="{c}" opacity=".42" style="mix-blend-mode:multiply"/></g>'
                 for i, x, y, lw, lh, c in marcas)
    return (f'<g filter="url(#{p}-sombra)"><rect x="-8" y="-8" width="{w + 16}" height="{w * ih + 16}" rx="6" fill="#fffdf6"/></g>'
            f'<image href="assets/{img}.png" x="0" y="0" width="{w}" height="{w * ih:.1f}" preserveAspectRatio="none"/>{ms}'
            f'<rect x="-8" y="-8" width="{w + 16}" height="{w * ih + 16}" rx="6" fill="none" stroke="#8d7bff" stroke-width="3" opacity=".6"/>')


# ---------------------------------------------------------------- cartões de capítulo (escrever 0, mapear 0)
def cartao(cena, n, nome, tema):
    p = f"{cena}_0"
    ini, dur = seg(cena, 0)
    t_arq = T(cena, 0, "arquivo")
    t_n = T(cena, 0, n)
    t_nome = T(cena, 0, "escrever" if cena == "escrever" else "mapi")
    linhas = "".join(f'<rect x="-220" y="{-200 + k * 38}" width="{400 if k % 3 else 300}" height="11" rx="5" fill="#8a7f68" opacity=".4"/>' for k in range(9))
    if tema == "escrever":
        folha = (linhas + f'<path id="{p}-risco" d="M-210 130 C -180 80 -160 150 -130 110 S -90 90 -60 130 S -20 100 10 126 S 60 96 90 128 S 140 104 170 124" '
                 f'fill="none" stroke="#1d2f9a" stroke-width="9" stroke-linecap="round" stroke-dasharray="700" stroke-dashoffset="700"/>'
                 f'<g transform="translate(170 124)"><g id="{p}-caneta" opacity="0"><g transform="rotate(35)"><rect x="-10" y="-150" width="22" height="130" rx="8" fill="#ffb23e" stroke="#7a4a10" stroke-width="3"/>'
                 f'<path d="M-10 -20 L12 -20 L1 4 Z" fill="#2a1d70"/></g></g></g>')
    else:
        rg = random.Random(5)
        pts = [(-200, 100), (-120, -60), (-30, 60), (40, -150), (110, 20), (200, -90), (190, 120), (-210, -170)]
        lig = [(0, 1), (1, 2), (2, 4), (1, 3), (3, 5), (4, 5), (4, 6), (0, 2), (7, 1), (7, 3)]
        grade = "".join(f'<line x1="{x}" y1="-250" x2="{x}" y2="170"/>' for x in range(-240, 271, 60)) + "".join(f'<line x1="-270" y1="{y}" x2="270" y2="{y}"/>' for y in range(-220, 171, 60))
        folha = (f'<g stroke="#8a7f68" stroke-width="2" opacity=".35">{grade}</g>'
                 f'<g id="{p}-lig" stroke="#3b5bff" stroke-width="7" stroke-linecap="round" fill="none">' +
                 "".join(f'<path d="M{pts[a][0]} {pts[a][1]} L{pts[b][0]} {pts[b][1]}" stroke-dasharray="400" stroke-dashoffset="400"/>' for a, b in lig) + '</g>' +
                 "".join(f'<circle class="no" cx="{x}" cy="{y}" r="15" fill="{["#3be0ff", "#ff4fa3", "#8d7bff", "#ffb23e"][k % 4]}" stroke="#1a1050" stroke-width="4"/>' for k, (x, y) in enumerate(pts)) +
                 f'<g transform="translate(110 20)"><g id="{p}-pino" opacity="0"><path d="M0 0 C-30 -40 -36 -70 0 -86 C36 -70 30 -40 0 0 Z" fill="#ff4f7d" stroke="#fff" stroke-width="4"/><circle cy="-56" r="13" fill="#fff"/></g></g>')
    frente = (f'<rect x="-240" y="-60" width="300" height="120" rx="10" fill="#fffaf0" opacity=".92"/>'
              f'<text x="-90" y="34" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="104" fill="#2c1f80">{n}</text>'
              f'<rect x="100" y="-40" width="160" height="14" rx="7" fill="#bff4ff" opacity=".5"/><rect x="100" y="-6" width="120" height="14" rx="7" fill="#bff4ff" opacity=".35"/>')
    extra = pasta_defs(p) + f'<linearGradient id="{p}-num" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8d7bff" stop-opacity=".55"/><stop offset="1" stop-color="#3be0ff" stop-opacity=".08"/></linearGradient>'
    # a pessoa diante da pasta, em pé, estendendo a mão
    CHAO, FX, FS = 790, 1260, 0.8
    # mesma pose nos dois cartões (eco de capítulo); a roupa muda: casa no 1, trabalho no 2
    mesa_y = 690
    var = "casa" if tema == "escrever" else "trabalho"
    gente_svg = humano(p + "g", var, "em_pe", 830, CHAO, 0.85, cena=p)
    braco = -80
    FY = mesa_y - 230 * FS
    mesa = (f'<g filter="url(#{p}-sombra)"><rect x="950" y="{mesa_y}" width="640" height="26" rx="10" fill="#2a1d70" stroke="#8d7bff" stroke-width="4"/></g>'
            f'<path d="M990 {mesa_y + 26} L984 {CHAO} M1550 {mesa_y + 26} L1556 {CHAO}" stroke="#8d7bff" stroke-width="10" stroke-linecap="round"/>')
    chao = (f'<rect x="0" y="{CHAO}" width="1920" height="{1080 - CHAO}" fill="#0b0828" opacity=".55"/>'
            f'<line x1="60" y1="{CHAO}" x2="1860" y2="{CHAO}" stroke="#8d7bff" stroke-width="3" opacity=".6"/>')
    svg = f"""<g id="{p}-mundo">
{chao}
<g transform="translate(330 0)"><g id="{p}-numG"><rect x="-260" y="180" width="520" height="620" fill="none"/>
<text id="{p}-num" x="0" y="{CHAO}" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="820" fill="url(#{p}-num)" fill-opacity="0" stroke="#bfb3ff" stroke-width="7" stroke-dasharray="3200" stroke-dashoffset="3200" filter="url(#{p}-glow)">{n}</text></g></g>
{mesa}
<g transform="translate({FX} {FY:.0f}) scale({FS})"><g id="{p}-pastaW">{pasta(p, folha, frente)}</g></g>
{gente_svg}
<g id="{p}-brilho" opacity="0" fill="#ffd98a">{"".join(f'<circle cx="{FX + 330 * FS * math.cos(a):.0f}" cy="{FY - 170 * FS + 150 * FS * math.sin(a):.0f}" r="{6 + (k % 3) * 3}"/>' for k, a in enumerate([i * 0.785 for i in range(8)]))}</g>
</g>"""
    html = (mono(f"{p}-t1", "ARQUIVO", "left:150px;top:120px", "#ffd27a", 64) +
            tit(f"{p}-t2", nome, "left:690px;width:1000px;text-align:center;top:800px;font-size:170px;color:#eef1f7;letter-spacing:.06em"))
    js = f"""
  camK("#{p}-mundo",960,540,[[0,1.14],[{dur:.2f},1.0,"power2.out"]]);
  tl.fromTo("#{p}-pastaW",{{y:-900,rotation:-9,transformOrigin:"50% 50%"}},{{y:0,rotation:0,transformOrigin:"50% 50%",duration:0.8,ease:"back.out(1.2)"}},0.05);
  tl.fromTo("#{p}g-olho",{{x:0,y:0}},{{x:3,y:{-2 if tema == "mapear" else 1},duration:0.3}},{t_arq:.2f});
  tl.fromTo("#{p}g-braco",{{rotation:0,{ombro(var, "em_pe")}}},{{rotation:{braco},{ombro(var, "em_pe")},duration:0.45,ease:"back.out(1.6)"}},{t_nome - 0.35:.2f});
  rise("#{p}-t1 span",{t_arq:.2f});
  traco("#{p}-num",0.25,1.6,3200);
  tl.fromTo("#{p}-num",{{attr:{{"fill-opacity":0}}}},{{attr:{{"fill-opacity":1}},duration:0.4,immediateRender:false}},{t_n:.2f});
  tl.fromTo("#{p}-numG",{{scale:1.18,transformOrigin:"50% 50%"}},{{scale:1,transformOrigin:"50% 50%",duration:0.7,ease:"elastic.out(1,0.45)",immediateRender:false}},{t_n:.2f});
  rise("#{p}-t2 span",{t_nome:.2f},0.7);
  tl.fromTo("#{p}-frente",{{scaleY:1,skewX:0,transformOrigin:"50% 100%"}},{{scaleY:0.7,skewX:-8,transformOrigin:"50% 100%",duration:0.4,ease:"back.out(2)"}},{t_nome - 0.1:.2f});
  tl.fromTo("#{p}-folha",{{y:0}},{{y:-150,duration:0.5,ease:"back.out(1.6)"}},{t_nome - 0.05:.2f});
  tl.fromTo("#{p}-brilho",{{opacity:0,scale:0.6,svgOrigin:"{FX} {FY - 170 * FS:.0f}"}},{{opacity:1,scale:1.15,svgOrigin:"{FX} {FY - 170 * FS:.0f}",duration:0.5,ease:"power2.out"}},{t_nome + 0.1:.2f});
  tl.fromTo("#{p}-brilho",{{opacity:1}},{{opacity:0.35,duration:0.4,immediateRender:false}},{t_nome + 0.6:.2f});
""" + G.vida_gente(p + "g", dur, (1.1,))
    if tema == "escrever":
        js += f"""
  entra("#{p}-caneta",{t_nome:.2f},0.15);
  traco("#{p}-risco",{t_nome + 0.1:.2f},0.6,700);
  tl.fromTo("#{p}-caneta",{{x:-380,y:6}},{{x:0,y:0,duration:0.6,ease:"power2.inOut",immediateRender:false}},{t_nome + 0.1:.2f});
"""
    else:
        js += f"""
  tl.fromTo("#{p}-lig path",{{attr:{{"stroke-dashoffset":400}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.3,stagger:0.05,ease:"power2.out"}},{t_nome + 0.05:.2f});
  tl.fromTo("#{p}-pino",{{opacity:0,y:-120}},{{opacity:1,y:0,duration:0.45,ease:"bounce.out"}},{t_nome + 0.25:.2f});
"""
    return comp(p, dur, svg, html, js, extra, seed=5 if tema == "escrever" else 9)


def escrever_0():
    return cartao("escrever", "1", "ESCREVER", "escrever")


def mapear_0():
    return cartao("mapear", "2", "MAPEAR", "mapear")


# ---------------------------------------------------------------- escrever 2: página do Ramirez 2013, camundongo e engrama
def escrever_2():
    CE, SG = "escrever", 2
    p = "escrever_2"
    ini, dur = seg(CE, SG)
    t_sus, t_nob, t_ganh, t_marc, t_acen, t_expl, t_caixa, t_mod, t_resp, t_luz = (
        T(CE, SG, "susumu"), T(CE, SG, "nobel"), T(CE, SG, "ganhador"), T(CE, SG, "marcou"), T(CE, SG, "acendiam"),
        T(CE, SG, "explorava"), T(CE, SG, "caixa"), T(CE, SG, "modificados"), T(CE, SG, "responder"), T(CE, SG, "luz"))
    W, IH = 660, 2071 / 1600
    pg = pagina(p, "ramirez2013", W, IH, [("m1", 318, 184, 966, 70, "#ffb23e"), ("m2", 948, 346, 304, 48, "#ff4fa3")])
    rg = random.Random(3)
    BX, BY = 1640, 250
    nos = []
    while len(nos) < 22:
        a, r = rg.uniform(0, 6.283), 118 * math.sqrt(rg.uniform(0.02, 1))
        x, y = BX + r * math.cos(a), BY + r * math.sin(a)
        if all((x - u) ** 2 + (y - v) ** 2 > 38 ** 2 for u, v in nos):
            nos.append((round(x), round(y)))
    eng = sorted(range(len(nos)), key=lambda k: (nos[k][0] - BX + 10) ** 2 + (nos[k][1] - BY + 10) ** 2)[:7]
    ed = "".join(f'<line x1="{nos[a][0]}" y1="{nos[a][1]}" x2="{nos[b][0]}" y2="{nos[b][1]}"/>' for a in range(len(nos)) for b in range(a + 1, len(nos)) if (nos[a][0] - nos[b][0]) ** 2 + (nos[a][1] - nos[b][1]) ** 2 < 70 ** 2)
    ede = "".join(f'<line x1="{nos[a][0]}" y1="{nos[a][1]}" x2="{nos[b][0]}" y2="{nos[b][1]}"/>' for i, a in enumerate(eng) for b in eng[i + 1:] if (nos[a][0] - nos[b][0]) ** 2 + (nos[a][1] - nos[b][1]) ** 2 < 80 ** 2)
    extra = grad_caixa(p, "c") + f'<radialGradient id="{p}-bol" cx="45%" cy="40%" r="70%"><stop offset="0" stop-color="#2a1d70"/><stop offset="1" stop-color="#120c3a"/></radialGradient>'
    svg = f"""
<g transform="translate(140 118) rotate(-2)"><g id="{p}-pg">{pg}</g></g>
<g id="{p}-lab" opacity="0">
 <g transform="translate(707 262) scale(.68)">{caixa(p)}
  <g transform="translate(900 700) scale(1.15)"><g id="{p}-ratoW"><g id="{p}-bob">{rato(p)}</g></g></g>
  <path id="{p}-cabo" d="M1010 -440 L1010 -60 C 1010 160 1040 300 1052 440" fill="none" stroke="#9aa6d0" stroke-width="12" stroke-linecap="round" stroke-dasharray="1100" stroke-dashoffset="1100"/>
  <path id="{p}-luz" d="M1010 -440 L1010 -60 C 1010 160 1040 300 1052 440" fill="none" stroke="#7fe6ff" stroke-width="14" stroke-linecap="round" stroke-dasharray="80 1100" stroke-dashoffset="80" filter="url(#{p}-glow)" opacity="0"/>
  <circle id="{p}-halo" cx="1052" cy="458" r="40" fill="#7fe6ff" opacity="0" filter="url(#{p}-glow)"/>
 </g>
 <g id="{p}-bolha" opacity="0">
  <circle cx="1470" cy="470" r="10" fill="#c9b8ff" opacity=".7"/><circle cx="1510" cy="418" r="16" fill="#c9b8ff" opacity=".8"/>
  <circle cx="{BX}" cy="{BY}" r="150" fill="url(#{p}-bol)" stroke="#8d7bff" stroke-width="5" filter="url(#{p}-glow)"/>
  <g stroke="#6a7cff" stroke-width="2.5" opacity=".7">{ed}</g>
  <g id="{p}-ede" stroke="#ffb23e" stroke-width="5" opacity="0">{ede}</g>
  <g>{"".join(f'<circle cx="{x}" cy="{y}" r="10" fill="#5fb7ff" opacity=".8"/>' for x, y in nos)}</g>
  <g id="{p}-eng" opacity="0" filter="url(#{p}-glow)">{"".join(f'<circle cx="{nos[k][0]}" cy="{nos[k][1]}" r="14" fill="#ffb23e"/>' for k in eng)}</g>
  <g id="{p}-anel" opacity="0" fill="none" stroke="#7fe6ff" stroke-width="5">{"".join(f'<circle cx="{nos[k][0]}" cy="{nos[k][1]}" r="22"/>' for k in eng)}</g>
 </g>
</g>"""
    html = (tit(f"{p}-n1", "Susumu", "left:1230px;top:250px;font-size:130px;color:#ffd0ea") +
            tit(f"{p}-n2", "Tonegawa", "left:1230px;top:400px;font-size:130px;color:#ffd0ea") +
            texto(f"{p}-n3", "GANHADOR DO NOBEL", "left:1236px;top:596px;font:500 58px 'IBM Plex Mono',monospace;letter-spacing:.05em;color:#ffd27a", "tit", "1.35em") +
            mono(f"{p}-c1", "CAIXA TRANQUILA", "left:960px;width:900px;text-align:center;top:900px", "#bff4ff", 56) +
            mono(f"{p}-c2", "RESPONDER À LUZ", "left:960px;width:900px;text-align:center;top:900px", "#7fe6ff", 56))
    z0 = 2.0
    js = f"""
  camK("#{p}-cam",470,250,[[0,2.25],[{t_marc:.2f},{z0},"sine.inOut"],[{t_marc + 1.6:.2f},1.0],[{dur:.2f},1.035,"sine.inOut"]]);
  tl.fromTo("#{p}-pg",{{y:420,rotation:-5,opacity:0}},{{y:0,rotation:0,opacity:1,duration:0.9,ease:"expo.out"}},0.05);
  marca("#{p}-m1",0.6,0.8);
  marca("#{p}-m2",{t_sus:.2f},0.7);
  rise("#{p}-n1 span",{t_sus:.2f}); rise("#{p}-n2 span",{T(CE, SG, "tonegawa"):.2f});
  rise("#{p}-n3 span",{t_ganh + 0.3:.2f});
  sai("#{p}-n1 span",{t_marc:.2f}); sai("#{p}-n2 span",{t_marc + 0.08:.2f}); sai("#{p}-n3 span",{t_marc + 0.16:.2f});
  entra("#{p}-lab",{t_marc + 0.2:.2f},0.8);
  tl.fromTo("#{p}-bob",{{y:0}},{{y:-6,duration:0.8,repeat:10,yoyo:true,ease:"sine.inOut"}},{t_marc:.2f});
  tl.fromTo("#{p}-rPalpebra",{{y:-52}},{{y:0,duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t_marc + 2.4:.2f});
  tl.fromTo("#{p}-rPalpebra",{{y:-52}},{{y:0,duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t_mod + 0.5:.2f});
  tl.fromTo("#{p}-bolha",{{opacity:0,scale:0.3,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.8,ease:"back.out(1.6)"}},{t_acen - 0.6:.2f});
  tl.fromTo("#{p}-eng",{{opacity:0}},{{opacity:1,duration:0.15,repeat:3,yoyo:true}},{t_acen:.2f});
  tl.fromTo("#{p}-eng",{{opacity:0}},{{opacity:1,duration:0.3,immediateRender:false}},{t_acen + 0.6:.2f});
  entra("#{p}-ede",{t_acen + 0.4:.2f},0.5);
  tl.fromTo("#{p}-ratoW",{{x:-90}},{{x:60,duration:{t_mod - t_expl:.2f},ease:"sine.inOut"}},{t_expl:.2f});
  tl.fromTo("#{p}-cx polyline",{{attr:{{"stroke-width":7}}}},{{attr:{{"stroke-width":14}},duration:0.4,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_caixa:.2f});
  rise("#{p}-c1 span",{t_caixa:.2f});
  sai("#{p}-c1 span",{t_resp - 0.35:.2f},0.4);
  tl.fromTo("#{p}-anel",{{opacity:0,scale:1.8,svgOrigin:"{BX} {BY}"}},{{opacity:1,scale:1,svgOrigin:"{BX} {BY}",duration:0.6,ease:"back.out(2)"}},{t_mod:.2f});
  traco("#{p}-cabo",{t_mod:.2f},1.0,1100);
  rise("#{p}-c2 span",{t_resp:.2f});
  tl.fromTo("#{p}-luz",{{opacity:0,attr:{{"stroke-dashoffset":80}}}},{{opacity:1,attr:{{"stroke-dashoffset":-1020}},duration:0.9,ease:"power1.in"}},{t_luz - 0.8:.2f});
  tl.fromTo("#{p}-halo",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:0.9,scale:1.8,transformOrigin:"50% 50%",duration:0.4,ease:"power2.out"}},{t_luz:.2f});
  tl.fromTo("#{p}-eng circle",{{attr:{{fill:"#ffb23e"}}}},{{attr:{{fill:"#bff4ff"}},duration:0.25,immediateRender:false}},{t_luz:.2f});
"""
    return comp(p, dur, svg, html, js, extra, seed=4)


def engrenagem(cx, cy, r, dentes, cor, id_):
    pts = []
    for k in range(dentes * 2):
        for d in (0, 1):
            a = (k + d * 0.5) * math.pi / dentes
            rr = r if k % 2 == 0 else r * 0.78
            pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return (f'<g transform="translate(0 0)"><g id="{id_}"><polygon points="{" ".join(pts)}" fill="{cor}" stroke="#7a4a10" stroke-width="2"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .3:.1f}" fill="#2a1d70"/></g></g>')


def orbe(p, k, cor):
    """Lembrança: esfera de vidro com um momento da vida (o café) dentro. Centrada em (0,0), raio 110."""
    return (f'<circle r="118" fill="{cor}" opacity=".18" filter="url(#{p}-glow)"/>'
            f'<circle r="110" fill="url(#{p}-orb)" stroke="{cor}" stroke-width="6"/>'
            f'<clipPath id="{p}-oc{k}"><circle r="104"/></clipPath><g clip-path="url(#{p}-oc{k})"><g transform="scale(1.4) translate(-100 -75)">{G.cena_quadro("cafe")}</g></g>'
            f'<ellipse cx="-38" cy="-56" rx="36" ry="20" fill="#fff" opacity=".35" transform="rotate(-30 -38 -56)"/>')


# ---------------------------------------------------------------- escrever 5: mesmo mecanismo para memória falsa e verdadeira
def escrever_5():
    CE, SG = "escrever", 5
    p = "escrever_5"
    ini, dur = seg(CE, SG)
    t_cer, t_mesmo, t_lemb, t_fal, t_ver, t_den, t_nao, t_dif = (
        T(CE, SG, "cerebro"), T(CE, SG, "mesmo"), T(CE, SG, "lembrar"), T(CE, SG, "falsa"), T(CE, SG, "verdadeira"),
        T(CE, SG, "dentro"), T(CE, SG, "nao"), T(CE, SG, "diferenca"))
    pp = p + "a"
    S, TX, TY = 2.6, 427, 196
    BXc, BYc = TX + 192 * S, TY + 84 * S          # centro do cérebro na tela
    extra = grad_caixa(p, "c") + f'<radialGradient id="{p}-orb" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#3a2a8c"/><stop offset="1" stop-color="#120c3a"/></radialGradient>'
    caminho_e = f"M330 430 C 520 200 760 220 {BXc:.0f} {BYc:.0f}"
    caminho_d = f"M1590 430 C 1400 200 1160 220 {BXc:.0f} {BYc:.0f}"
    svg = f"""<g id="{p}-mundo">
 <ellipse cx="960" cy="900" rx="300" ry="26" fill="#05031a" opacity=".45"/>
 {pessoa(pp, TX, TY, S)}
 <g id="{p}-eng" opacity="0">{engrenagem(BXc - 26, BYc - 8, 46, 9, "#ffb23e", p + "-g1")}{engrenagem(BXc + 44, BYc + 30, 32, 7, "#ffd27a", p + "-g2")}</g>
 <path id="{p}-ce" d="{caminho_e}" fill="none" stroke="#ff4fa3" stroke-width="6" stroke-dasharray="14 12" opacity="0"/>
 <path id="{p}-cd" d="{caminho_d}" fill="none" stroke="#38e8a8" stroke-width="6" stroke-dasharray="14 12" opacity="0"/>
 <g transform="translate(330 430)"><g id="{p}-oe"><g id="{p}-oeI">{orbe(p, "e", "#ff4fa3")}</g></g></g>
 <g transform="translate(1590 430)"><g id="{p}-od"><g id="{p}-odI">{orbe(p, "d", "#38e8a8")}</g></g></g>
 <circle id="{p}-flash" cx="{BXc:.0f}" cy="{BYc:.0f}" r="120" fill="#ffd0ea" opacity="0" filter="url(#{p}-glow)"/>
</g>
<g id="{p}-dentro" opacity="0">
 <rect width="1920" height="1080" fill="#14093a" opacity=".86"/>
 <g transform="translate(660 520) scale(1.7)"><g id="{p}-i1"><g id="{p}-i1b">{orbe(p, "i1", "#c9b8ff")}</g></g></g>
 <g transform="translate(1260 520) scale(1.7)"><g id="{p}-i2"><g id="{p}-i2b">{orbe(p, "i2", "#c9b8ff")}</g></g></g>
 <text id="{p}-q" x="960" y="575" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="170" fill="#ffd27a" opacity="0" filter="url(#{p}-glow)">?</text>
</g>"""
    html = (mono(f"{p}-l1", "FALSA", "left:130px;width:400px;text-align:center;top:580px", "#ff9bd0", 54) +
            mono(f"{p}-l2", "VERDADEIRA", "left:1340px;width:500px;text-align:center;top:580px", "#7ff5c8", 54) +
            tit(f"{p}-t1", "O mesmo mecanismo", "left:0;right:0;text-align:center;top:40px;font-size:110px;color:#ffd98a") +
            tit(f"{p}-t2", "De dentro", "left:0;right:0;text-align:center;top:60px;font-size:120px;color:#eef1f7") +
            mono(f"{p}-t3", "NÃO DÁ PARA SABER A DIFERENÇA", "left:0;right:0;text-align:center;top:880px", "#ffd27a", 54))
    dx_e, dy_e = BXc - 330, BYc - 430
    dx_d, dy_d = BXc - 1590, BYc - 430
    js = f"""
  camK("#{p}-mundo",{BXc:.0f},{BYc:.0f},[[0,1.08],[{t_den - 0.4:.2f},1.0,"sine.inOut"],[{t_den + 0.7:.2f},4.2,"power3.in"],[{dur:.2f},4.4,"none"]]);
  pop("#{p}-oe",0.3,0.4,0.8); pop("#{p}-od",0.5,0.4,0.8);
  rise("#{p}-l1 span",0.5); rise("#{p}-l2 span",0.7);
  tl.fromTo("#{p}-oeI",{{y:0}},{{y:-14,duration:1.1,repeat:3,yoyo:true,ease:"sine.inOut"}},0.4);
  tl.fromTo("#{p}-odI",{{y:-14}},{{y:0,duration:1.1,repeat:3,yoyo:true,ease:"sine.inOut"}},0.4);
  tl.fromTo("#{pp}-cer",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.08,transformOrigin:"50% 50%",duration:0.25,repeat:1,yoyo:true}},{t_cer:.2f});
  entra("#{p}-eng",{t_mesmo:.2f},0.3);
  tl.fromTo("#{p}-g1",{{rotation:0,transformOrigin:"50% 50%"}},{{rotation:360,transformOrigin:"50% 50%",duration:{dur - t_mesmo:.2f},ease:"none"}},{t_mesmo:.2f});
  tl.fromTo("#{p}-g2",{{rotation:0,transformOrigin:"50% 50%"}},{{rotation:-500,transformOrigin:"50% 50%",duration:{dur - t_mesmo:.2f},ease:"none"}},{t_mesmo:.2f});
  rise("#{p}-t1 span",{t_mesmo:.2f});
  entra("#{p}-ce",{t_lemb:.2f},0.4); entra("#{p}-cd",{t_lemb + 0.2:.2f},0.4);
  tl.fromTo("#{p}-ce",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-260}},duration:3,ease:"none"}},{t_lemb:.2f});
  tl.fromTo("#{p}-cd",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-260}},duration:3,ease:"none"}},{t_lemb:.2f});
  tl.fromTo("#{pp}-olho",{{x:0}},{{x:-4,duration:0.3}},{t_fal - 0.4:.2f});
  tl.fromTo("#{p}-oe",{{x:0,y:0,scale:1,transformOrigin:"50% 50%"}},{{keyframes:{{x:[0,{dx_e * .45:.0f},{dx_e:.0f}],y:[0,-110,{dy_e:.0f}]}},scale:0.25,transformOrigin:"50% 50%",duration:0.8,ease:"power2.in",immediateRender:false}},{t_fal - 0.3:.2f});
  some("#{p}-oe",{t_fal + 0.45:.2f},0.15); some("#{p}-ce",{t_fal - 0.35:.2f},0.25);
  tl.fromTo("#{p}-flash",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:0.9,scale:1.4,transformOrigin:"50% 50%",duration:0.25,yoyo:true,repeat:1}},{t_fal + 0.45:.2f});
  tl.fromTo("#{pp}-olho",{{x:-4}},{{x:4,duration:0.3,immediateRender:false}},{t_ver - 0.4:.2f});
  tl.fromTo("#{p}-od",{{x:0,y:0,scale:1,transformOrigin:"50% 50%"}},{{keyframes:{{x:[0,{dx_d * .45:.0f},{dx_d:.0f}],y:[0,-110,{dy_d:.0f}]}},scale:0.25,transformOrigin:"50% 50%",duration:0.8,ease:"power2.in",immediateRender:false}},{t_ver - 0.3:.2f});
  some("#{p}-od",{t_ver + 0.45:.2f},0.15); some("#{p}-cd",{t_ver - 0.35:.2f},0.25);
  tl.fromTo("#{p}-flash",{{opacity:0,scale:0.4}},{{opacity:0.9,scale:1.4,duration:0.25,yoyo:true,repeat:1,immediateRender:false}},{t_ver + 0.45:.2f});
  tl.fromTo("#{pp}-olho",{{x:4}},{{x:0,duration:0.3,immediateRender:false}},{t_ver + 0.6:.2f});
  sai("#{p}-l1 span",{t_fal + 0.3:.2f}); sai("#{p}-l2 span",{t_ver + 0.3:.2f});
  sai("#{p}-t1 span",{t_den - 0.5:.2f});
  entra("#{p}-dentro",{t_den + 0.35:.2f},0.5);
  rise("#{p}-t2 span",{t_den + 0.2:.2f});
  pop("#{p}-i1",{t_den + 0.5:.2f},0.3,0.8); pop("#{p}-i2",{t_den + 0.7:.2f},0.3,0.8);
  tl.fromTo("#{p}-i1b",{{y:0}},{{y:-10,duration:0.9,repeat:5,yoyo:true,ease:"sine.inOut"}},{t_den + 1.2:.2f});
  tl.fromTo("#{p}-i2b",{{y:-10}},{{y:0,duration:0.9,repeat:5,yoyo:true,ease:"sine.inOut"}},{t_den + 1.2:.2f});
  rise("#{p}-t3 span",{t_nao:.2f});
  tl.fromTo("#{p}-i1",{{x:0,y:0}},{{keyframes:{{x:[0,176,353,176,0],y:[0,-50,0,50,0]}},duration:1.6,ease:"power1.inOut",immediateRender:false}},{t_nao + 0.6:.2f});
  tl.fromTo("#{p}-i2",{{x:0,y:0}},{{keyframes:{{x:[0,-176,-353,-176,0],y:[0,50,0,-50,0]}},duration:1.6,ease:"power1.inOut",immediateRender:false}},{t_nao + 0.6:.2f});
  tl.fromTo("#{p}-q",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.6,ease:"elastic.out(1,0.45)"}},{t_dif - 0.3:.2f});
""" + vida_pessoa(pp, dur, (1.6, 4.3, 7.7))
    return comp(p, dur, svg, html, js, extra, seed=6)


# ---------------------------------------------------------------- escrever 7: a memória não é um arquivo lacrado
def escrever_7():
    CE, SG = "escrever", 7
    p = "escrever_7"
    ini, dur = seg(CE, SG)
    t_ass, t_mem, t_arq, t_lac, t_edit, t_fora, t_escr, t_outra, t_como, t_conf, t_nas = (
        T(CE, SG, "assusta"), T(CE, SG, "memoria"), T(CE, SG, "arquivo"), T(CE, SG, "lacrado"), T(CE, SG, "editada"),
        T(CE, SG, "fora"), T(CE, SG, "escrita"), T(CE, SG, "outra"), T(CE, SG, "como"), T(CE, SG, "confia"), T(CE, SG, "nas"))
    linhas = "".join(f'<rect x="-220" y="{-215 + k * 40}" width="{410 if k % 3 else 300}" height="12" rx="6" fill="#8a7f68" opacity=".45"/>' for k in range(9))
    riscos = "".join(f'<path class="rs" d="M-226 {-209 + k * 40} L{-226 + (410 if k % 3 else 300) + 12} {-209 + k * 40}" stroke="#ff4f7d" stroke-width="7" stroke-linecap="round" stroke-dasharray="440" stroke-dashoffset="440"/>' for k in (1, 3, 4, 6))
    novos = "".join(f'<path class="nv" d="M-210 {-196 + k * 40} c 30 -20 50 14 80 -4 s 50 10 80 -6 s 50 12 84 -4" fill="none" stroke="#ff4fa3" stroke-width="6" stroke-linecap="round" stroke-dasharray="300" stroke-dashoffset="300"/>' for k in (1, 3, 4, 6))
    folha = linhas + riscos + novos
    frente = (f'<text x="-40" y="10" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="76" fill="#eef1f7">memória</text>'
              f'<g transform="translate(220 40)"><g id="{p}-selo"><g id="{p}-sE"><path d="M0 -62 A62 62 0 0 0 0 62 L8 30 L-6 0 L10 -30 Z" fill="#d1224f" stroke="#7a1236" stroke-width="4"/></g>'
              f'<g id="{p}-sD"><path d="M0 -62 A62 62 0 0 1 0 62 L8 30 L-6 0 L10 -30 Z" fill="#e8365f" stroke="#7a1236" stroke-width="4"/></g>'
              f'<circle r="34" fill="none" stroke="#ff9bb0" stroke-width="4" opacity=".7"/></g></g>')
    extra = pasta_defs(p) + (f'<radialGradient id="{p}-abaj" cx="50%" cy="40%" r="50%"><stop offset="0" stop-color="#ffd98a" stop-opacity=".55"/>'
                             f'<stop offset="1" stop-color="#ffb23e" stop-opacity="0"/></radialGradient>')
    # outra pessoa: as mesmas peças do gente.py com casaco escuro, pele e cabelo diferentes, gravata magenta (a cor da caneta)
    OUTRA = {G.TRAB["torso"]: "#3a2f5a", G.CABELO: "#cfcfdc", G.PELE: "#c98e66", G.GRAVATA: "#38e8a8"}
    OX, OY, OS = 1640, 950, 1.05                       # outra pessoa em pé, espelhada
    (sx, sy), (hx, hy) = anc("trabalho", "em_pe", "ombro_braco"), anc("trabalho", "em_pe", "mao_e")
    a = math.radians(-75)                               # braço erguido (mesma rotação do tween), no espaço local
    rx, ry = sx + (hx - sx) * math.cos(a) - (hy - sy) * math.sin(a), sy + (hx - sx) * math.sin(a) + (hy - sy) * math.cos(a)
    MAO = (OX - hx * OS, OY + hy * OS)                 # mão parada na tela
    PEN = (MAO[0] + 12, MAO[1] + 10)                   # ponta da caneta em repouso: a mão segura perto da ponta, corpo da caneta para fora do corpo
    CX0, CY0 = 1250, 400                               # origem do grupo da caneta (a ponta)
    HX7, HY7 = round(OX - rx * OS), round(OY + ry * OS)  # mão com o braço erguido
    # parte B: a sala da pessoa, com quadros dos momentos da vida dela na parede
    QD = [("familia", 230, 205, .82, -3), ("aniversario", 520, 190, .82, 2), ("formatura", 810, 210, .82, -2),
          ("carro", 1110, 195, .8, 3), ("praia", 1410, 210, .8, -2), ("cachorro", 1700, 195, .8, 2)]
    quadros = "".join(G.quadro(f"{p}-q{k}", t, x, y, s, r) +
                      f'<g transform="translate({x} {y}) rotate({r}) scale({s})"><g class="mx" opacity="0">'
                      f'<path d="M-96 -40 c 30 -34 60 26 96 -8 s 60 30 92 -22 M-90 30 c 40 -20 70 30 110 0 s 40 -10 70 10" fill="none" stroke="#ff4fa3" stroke-width="11" stroke-linecap="round"/></g></g>'
                      for k, (t, x, y, s, r) in enumerate(QD))
    sala = (f'<rect x="0" y="940" width="1920" height="140" fill="#0b0828" opacity=".7"/><line x1="0" y1="940" x2="1920" y2="940" stroke="#8d7bff" stroke-width="4" opacity=".55"/>'
            f'<ellipse cx="470" cy="975" rx="330" ry="34" fill="#2a1d70" opacity=".6"/>'
            f'<ellipse cx="780" cy="560" rx="230" ry="260" fill="url(#{p}-abaj)"/>'
            f'<path d="M780 940 L780 560" stroke="#8d7bff" stroke-width="9" stroke-linecap="round"/><ellipse cx="780" cy="944" rx="60" ry="12" fill="#2a1d70" stroke="#8d7bff" stroke-width="4"/>'
            f'<path d="M716 560 L844 560 L816 470 L744 470 Z" fill="#ffd27a" stroke="#d98a1e" stroke-width="4" stroke-linejoin="round"/>')
    svg = f"""<g id="{p}-A">
 <g transform="translate(900 560)"><g id="{p}-pastaW">{pasta(p, folha, frente)}</g></g>
 <g id="{p}-outraW" opacity="0">
  {humano(p + "o", "trabalho", "em_pe", OX, OY, OS, espelho=True, cores=OUTRA, cena=p)}
  <g transform="translate({CX0} {CY0})"><g id="{p}-caneta"><g transform="rotate(-50) scale(.8)"><rect x="-14" y="-200" width="30" height="180" rx="10" fill="#ff4fa3" stroke="#7a1236" stroke-width="4"/><path d="M-14 -20 L16 -20 L1 12 Z" fill="#2a1d70"/></g></g></g>
 </g>
 <path id="{p}-fio2" d="M{HX7} {HY7} L{HX7} {HY7}" fill="none" stroke="#ff4fa3" stroke-width="5" stroke-dasharray="12 10" stroke-linecap="round" opacity="0" filter="url(#{p}-glow)"/>
 <path id="{p}-fio" d="M{MAO[0]:.0f} {MAO[1] - 20:.0f} C 1480 560 1300 400 1110 330" fill="none" stroke="#ff4fa3" stroke-width="6" stroke-dasharray="14 11" opacity="0"/>
 <rect id="{p}-alarme" width="1920" height="1080" fill="#ff1f5a" opacity="0"/>
</g>
<g id="{p}-B" opacity="0">
 {sala}
 {quadros}
 {humano(p + "v", "casa", "sentado", 430, 940, 1.15, cena=p)}
</g>"""
    html = (mono(f"{p}-a1", "ARQUIVO LACRADO", "left:0;right:0;text-align:center;top:36px", "#ffd27a", 64) +
            f'<div id="{p}-risca" style="position:absolute;left:598px;top:77px;width:724px;height:8px;background:#ff4f7d;border-radius:4px;transform:scaleX(0);transform-origin:0 50%;box-shadow:0 0 18px #ff4f7d"></div>' +
            mono(f"{p}-a2", "EDITADA POR FORA", "left:0;right:0;text-align:center;top:36px", "#ff9bd0", 64) +
            mono(f"{p}-a3", "OUTRA PESSOA", "left:0;right:0;text-align:center;top:920px", "#ff9bd0", 64) +
            tit(f"{p}-q1", "Como você confia", "left:930px;top:340px;font-size:108px;color:#eef1f7") +
            tit(f"{p}-q2", "nas suas?", "left:930px;top:500px;font-size:150px;color:#ffd98a"))
    js = f"""
  camK("#{p}-A",900,520,[[0,1.15],[{t_lac:.2f},1.0,"sine.inOut"],[{t_escr:.2f},0.98],[{t_como:.2f},0.9,"sine.inOut"]]);
  tl.fromTo("#{p}-pastaW",{{y:640,rotation:6,transformOrigin:"50% 50%"}},{{y:0,rotation:0,transformOrigin:"50% 50%",duration:1.0,ease:"back.out(1.3)"}},0.1);
  tl.fromTo("#{p}-alarme",{{opacity:0}},{{opacity:0.22,duration:0.08,repeat:3,yoyo:true}},{t_ass:.2f});
  tl.fromTo("#{p}-pastaW",{{x:0}},{{x:8,duration:0.05,repeat:7,yoyo:true,ease:"none",immediateRender:false}},{t_ass:.2f});
  tl.fromTo("#{p}-selo",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.2,transformOrigin:"50% 50%",duration:0.2,repeat:1,yoyo:true}},{t_mem:.2f});
  rise("#{p}-a1 span",{t_arq:.2f});
  tl.fromTo("#{p}-risca",{{scaleX:0}},{{scaleX:1,duration:0.4,ease:"power2.out"}},{t_lac + 0.3:.2f});
  tl.fromTo("#{p}-sE",{{x:0,y:0,rotation:0,transformOrigin:"50% 50%"}},{{x:-60,y:260,rotation:-50,transformOrigin:"50% 50%",duration:0.9,ease:"power2.in"}},{t_lac + 0.3:.2f});
  tl.fromTo("#{p}-sD",{{x:0,y:0,rotation:0,transformOrigin:"50% 50%"}},{{x:70,y:280,rotation:60,transformOrigin:"50% 50%",duration:0.9,ease:"power2.in"}},{t_lac + 0.3:.2f});
  some("#{p}-selo",{t_lac + 0.9:.2f},0.3);
  tl.fromTo("#{p}-frente",{{scaleY:1,skewX:0,transformOrigin:"50% 100%"}},{{scaleY:0.66,skewX:-8,transformOrigin:"50% 100%",duration:0.5,ease:"back.out(2)"}},{t_lac + 0.9:.2f});
  tl.fromTo("#{p}-folha",{{y:0}},{{y:-170,duration:0.6,ease:"back.out(1.5)"}},{t_lac + 1.0:.2f});
  sai("#{p}-a1 span",{t_edit - 0.5:.2f}); tl.fromTo("#{p}-risca",{{opacity:1}},{{opacity:0,duration:0.3}},{t_edit - 0.5:.2f});
  rise("#{p}-a2 span",{t_edit:.2f});
  entra("#{p}-outraW",{t_edit - 0.7:.2f},0.4);
  tl.fromTo("#{p}-outraW",{{x:320}},{{x:0,duration:0.7,ease:"power3.out"}},{t_edit - 0.7:.2f});
  tl.fromTo("#{p}o-braco",{{rotation:0,{ombro("trabalho", "em_pe")}}},{{rotation:-75,{ombro("trabalho", "em_pe")},duration:0.4,ease:"back.out(1.6)"}},{t_edit - 0.2:.2f});
  tl.fromTo("#{p}o-braco",{{rotation:-75,{ombro("trabalho", "em_pe")}}},{{rotation:0,{ombro("trabalho", "em_pe")},duration:0.5,ease:"power2.inOut",immediateRender:false}},{t_escr - 0.1:.2f});
  tl.fromTo("#{p}-caneta",{{x:{PEN[0] - CX0:.0f},y:{PEN[1] - CY0:.0f}}},{{keyframes:{{x:[{PEN[0] - CX0:.0f},-560,-170,-560,-170,-560,-170,-560,-170,{PEN[0] - CX0:.0f}],y:[{PEN[1] - CY0:.0f},-179,-179,-99,-99,-59,-59,21,21,{PEN[1] - CY0:.0f}]}},duration:{t_escr + 0.3 - t_edit:.2f},ease:"power1.inOut"}},{t_edit:.2f});
  entra("#{p}-fio2",{t_edit + 0.25:.2f},0.25); some("#{p}-fio2",{t_escr - 0.2:.2f},0.2);
  var F2=document.getElementById("{p}-fio2");
  tl.fromTo({{k:0}},{{k:0}},{{k:1,duration:{t_escr - t_edit:.2f},ease:"none",onUpdate:function(){{
    var x={CX0 + 8}+gsap.getProperty("#{p}-caneta","x"), y={CY0 + 9}+gsap.getProperty("#{p}-caneta","y");
    F2.setAttribute("d","M{HX7} {HY7} Q "+(({HX7}+x)/2)+" "+(Math.min({HY7},y)-120)+" "+x+" "+y);}}}},{t_edit:.2f});
  tl.fromTo("#{p}-folha .rs",{{attr:{{"stroke-dashoffset":440}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.35,stagger:0.3}},{t_edit + 0.3:.2f});
  tl.fromTo("#{p}-folha .nv",{{attr:{{"stroke-dashoffset":300}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.45,stagger:0.45}},{t_fora + 0.3:.2f});
  sai("#{p}-a2 span",{t_escr:.2f});
  tl.fromTo("#{p}o-olho",{{x:0}},{{x:3,duration:0.3}},{t_edit:.2f});
  entra("#{p}-fio",{t_outra - 0.2:.2f},0.3);
  tl.fromTo("#{p}-fio",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-150}},duration:1.2,ease:"none",immediateRender:false}},{t_outra - 0.2:.2f});
  tl.fromTo("#{p}o-cabW",{{rotation:0,{pescoco("trabalho", "em_pe")}}},{{rotation:-6,{pescoco("trabalho", "em_pe")},duration:0.3,yoyo:true,repeat:1}},{t_outra:.2f});
  rise("#{p}-a3 span",{t_outra - 0.1:.2f});
  tl.fromTo("#{p}-A",{{opacity:1}},{{opacity:0,duration:0.45}},{t_como - 0.35:.2f});
  sai("#{p}-a3 span",{t_como - 0.35:.2f},0.4);
  entra("#{p}-B",{t_como - 0.1:.2f},0.45);
  tl.fromTo("#{p}-B",{{scale:1.12,svgOrigin:"460 560"}},{{scale:1,svgOrigin:"460 560",duration:{dur - t_como:.2f},ease:"power2.out"}},{t_como - 0.1:.2f});
  rise("#{p}-q1 span",{t_como:.2f},0.8); rise("#{p}-q2 span",{t_nas:.2f},0.8);
  var QS="{",".join(f"#{p}-q{k}" for k in range(len(QD)))}";
  tl.fromTo(QS,{{y:0}},{{y:-8,duration:1.0,repeat:2,yoyo:true,ease:"sine.inOut",stagger:0.15}},{t_como:.2f});
  tl.fromTo("#{p}-B .mx",{{opacity:0}},{{opacity:1,duration:0.08,repeat:5,yoyo:true,stagger:0.17}},{t_conf:.2f});
  tl.fromTo("#{p}-B .mx",{{opacity:0}},{{opacity:0.9,duration:0.2,immediateRender:false}},{t_conf + 1.4:.2f});
  tl.fromTo(QS,{{x:-5}},{{x:5,duration:0.05,repeat:9,yoyo:true,ease:"none",stagger:0.12,immediateRender:false}},{t_conf:.2f});
  tl.fromTo("#{p}v-olho",{{x:0,y:0}},{{x:2,y:-3,duration:0.3}},{t_como:.2f});
  tl.fromTo("#{p}v-cabW",{{rotation:0,{pescoco("casa", "sentado")}}},{{rotation:-8,{pescoco("casa", "sentado")},duration:0.6,ease:"power2.inOut"}},{t_como + 0.1:.2f});
""" + G.vida_gente(p + "o", dur, (9.6, 11.3)) + G.vida_gente(p + "v", dur, (14.6, 15.8))
    return comp(p, dur, svg, html, js, extra, seed=12)


from arte2 import SIL_CER


def cursor(cor):
    return f'<path d="M0 0 L0 46 L12 35 L21 55 L30 51 L21 31 L38 31 Z" fill="{cor}" stroke="#fff" stroke-width="3.5" stroke-linejoin="round"/>'


def estrela(r, cor):
    pts = " ".join(f"{(r if k % 2 == 0 else r * .45) * math.cos(-math.pi / 2 + k * math.pi / 5):.1f},{(r if k % 2 == 0 else r * .45) * math.sin(-math.pi / 2 + k * math.pi / 5):.1f}" for k in range(10))
    return f'<polygon points="{pts}" fill="{cor}" stroke="#fff6c8" stroke-width="3" stroke-linejoin="round"/>'


# ---------------------------------------------------------------- mapear 3: fatias, microscópio, IA e voluntários
def mapear_3():
    CE, SG = "mapear", 3
    p = "mapear_3"
    ini, dur = seg(CE, SG)
    t_fat, t_cam, t_foto, t_mic, t_ia, t_tra, t_neu, t_cen, t_pes, t_vol, t_corr, t_err, t_jogo = (
        T(CE, SG, "fatiado"), T(CE, SG, "camadas"), T(CE, SG, "fotografado"), T(CE, SG, "microscopio"), T(CE, SG, "inteligencia"),
        T(CE, SG, "tracou"), T(CE, SG, "neuronio"), T(CE, SG, "ecent"), T(CE, SG, "pesquisadores"), T(CE, SG, "voluntarios"),
        T(CE, SG, "corrigiram"), T(CE, SG, "erros"), T(CE, SG, "como"))
    N, X0 = 9, 560
    fat = []
    for k in reversed(range(N)):
        f = 0.55 + 0.45 * math.sin(math.pi * (k + .5) / N)
        sx, sy = 1.3 * f, 0.30 * f
        yc = 430 + k * 22
        rg = random.Random(k)
        dots = "".join(f'<circle cx="{rg.uniform(-150, 150) * f:.0f}" cy="{rg.uniform(-26, 26) * f:.0f}" r="{rg.uniform(3, 6):.1f}" fill="{rg.choice(["#3be0ff", "#ff4fa3", "#8d7bff", "#ffd27a"])}"/>' for _ in range(14))
        fat.append(f'<g transform="translate({X0} {yc})"><g id="{p}-s{k}"><path transform="translate(0 14) scale({sx:.3f} {sy:.3f})" d="{SIL_CER}" fill="#13235e"/>'
                   f'<path transform="scale({sx:.3f} {sy:.3f})" d="{SIL_CER}" fill="url(#{p}-fat)" stroke="#7fdcff" stroke-width="3" vector-effect="non-scaling-stroke"/>{dots}</g></g>')
    # painel da foto do microscópio
    PX, PY, PW = 1100, 180, 680
    rg = random.Random(21)
    cel = []
    t_ = 0
    while len(cel) < 140 and t_ < 20000:
        t_ += 1
        r = rg.uniform(20, 58)
        x, y = rg.uniform(PX, PX + PW), rg.uniform(PY, PY + PW)
        if all(math.hypot(x - a, y - b) > r + c + 4 for a, b, c in cel):
            cel.append((round(x), round(y), round(r)))
    cores = ["#3be0ff", "#ff4fa3", "#8d7bff", "#ffb23e", "#38e8a8", "#5fb7ff", "#ff9bd0"]
    dentro = [i for i, (x, y, r) in enumerate(cel) if PX + 70 < x < PX + PW - 70 and PY + 70 < y < PY + PW - 70 and r > 34]
    erros = random.Random(4).sample(dentro, 7)
    base = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{"#9c9cae" if i % 3 else "#868698"}" stroke="#15151f" stroke-width="6"/>'
                   f'<ellipse cx="{x - r * .3:.0f}" cy="{y - r * .2:.0f}" rx="{r * .22:.0f}" ry="{r * .12:.0f}" fill="#55556a" opacity=".7"/>' for i, (x, y, r) in enumerate(cel))
    ordem = sorted(range(len(cel)), key=lambda i: cel[i][1])
    cl = "".join(f'<circle class="cl" cx="{cel[i][0]}" cy="{cel[i][1]}" r="{cel[i][2] - 3}" fill="{cores[i % 7]}" opacity="0"/>' if i not in erros else
                 f'<circle class="cl" cx="{cel[i][0]}" cy="{cel[i][1]}" r="{cel[i][2] - 3}" fill="#ff2a55" opacity="0"/>' for i in ordem)
    ok = "".join(f'<circle id="{p}-ok{j}" cx="{cel[i][0]}" cy="{cel[i][1]}" r="{cel[i][2] - 3}" fill="{cores[i % 7]}" opacity="0"/>'
                 f'<g id="{p}-x{j}" opacity="0" stroke="#fff" stroke-width="7" stroke-linecap="round"><path d="M{cel[i][0] - 14} {cel[i][1] - 14} l28 28 M{cel[i][0] + 14} {cel[i][1] - 14} l-28 28"/></g>'
                 f'<circle id="{p}-bu{j}" cx="{cel[i][0]}" cy="{cel[i][1]}" r="{cel[i][2]}" fill="none" stroke="#fff6c8" stroke-width="6" opacity="0"/>' for j, i in enumerate(erros))
    origens = [(1000, 1150), (1960, 1000), (1990, 300), (1300, -80), (900, -60), (1990, 650), (1700, 1160)]
    curs = "".join(f'<g id="{p}-c{j}" opacity="0"><g transform="scale(1.3)">{cursor(cores[(j * 2) % 7])}</g></g>' for j in range(7))
    estrelas = "".join(f'<g transform="translate({x} {y})"><g class="st" opacity="0">{estrela(r, c)}</g></g>' for x, y, r, c in
                       [(1080, 160, 34, "#ffd23e"), (1785, 195, 28, "#ff9bd0"), (1780, 852, 36, "#38e8a8"), (1070, 860, 26, "#3be0ff"), (1440, 130, 30, "#ffd23e"), (1792, 560, 24, "#ffd23e")])
    extra = (f'<linearGradient id="{p}-fat" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a6fa8"/><stop offset="1" stop-color="#3a2a8c"/></linearGradient>'
             f'<linearGradient id="{p}-mic" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3a3a8a"/><stop offset=".5" stop-color="#7a7ad0"/><stop offset="1" stop-color="#2a2a6a"/></linearGradient>'
             f'<linearGradient id="{p}-feixe" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bff4ff" stop-opacity=".9"/><stop offset="1" stop-color="#7fe6ff" stop-opacity=".15"/></linearGradient>'
             f'<clipPath id="{p}-pcp"><rect x="{PX}" y="{PY}" width="{PW}" height="{PW}" rx="10"/></clipPath>')
    f0 = 0.55 + 0.45 * math.sin(math.pi * .5 / N)
    hw = 210 * 1.3 * f0
    svg = f"""
<ellipse cx="{X0}" cy="860" rx="320" ry="28" fill="#05031a" opacity=".45"/>
<g id="{p}-pilha">{"".join(fat)}</g>
<rect id="{p}-lam" x="200" y="300" width="720" height="8" rx="4" fill="#bff4ff" opacity="0" filter="url(#{p}-glow)"/>
<polygon id="{p}-feixe" points="{X0 - 12},236 {X0 + 12},236 {X0 + hw:.0f},300 {X0 - hw:.0f},300" fill="url(#{p}-feixe)" opacity="0"/>
<g transform="translate({X0} 0)"><g id="{p}-micro"><g filter="url(#{p}-sombra)">
 <rect x="-72" y="-260" width="144" height="340" rx="22" fill="url(#{p}-mic)" stroke="#8d7bff" stroke-width="4"/>
 <rect x="-96" y="58" width="192" height="30" rx="12" fill="url(#{p}-mic)" stroke="#bff4ff" stroke-width="3"/>
 <rect x="-82" y="102" width="164" height="26" rx="10" fill="url(#{p}-mic)" stroke="#8d7bff" stroke-width="3"/>
 <path d="M-60 132 L60 132 L22 230 L-22 230 Z" fill="url(#{p}-mic)" stroke="#8d7bff" stroke-width="3"/></g>
 <rect x="-40" y="-120" width="80" height="12" rx="6" fill="#3be0ff" opacity=".7"/><rect x="-40" y="-90" width="50" height="12" rx="6" fill="#ffb23e" opacity=".7"/>
 <circle id="{p}-ponta" cx="0" cy="234" r="11" fill="#bff4ff" filter="url(#{p}-glow)"/></g></g>
<g id="{p}-fant" opacity="0"><path transform="translate({X0} 430) scale({1.3 * f0:.3f} {0.3 * f0:.3f})" d="{SIL_CER}" fill="none" stroke="#bff4ff" stroke-width="4" vector-effect="non-scaling-stroke"/></g>
<g id="{p}-painel" opacity="0"><rect x="{PX - 16}" y="{PY - 16}" width="{PW + 32}" height="{PW + 32}" rx="18" fill="#0e0c26" stroke="#8d7bff" stroke-width="4" filter="url(#{p}-sombra)"/>
 <g clip-path="url(#{p}-pcp)"><rect x="{PX}" y="{PY}" width="{PW}" height="{PW}" fill="#3a3a48"/>{base}<g>{cl}</g>{ok}
 <rect id="{p}-scan" x="{PX}" y="{PY}" width="{PW}" height="10" fill="#3be0ff" opacity="0" filter="url(#{p}-glow)"/></g>
 <rect id="{p}-borda" x="{PX - 16}" y="{PY - 16}" width="{PW + 32}" height="{PW + 32}" rx="18" fill="none" stroke="#38e8a8" stroke-width="10" opacity="0" filter="url(#{p}-glow)"/></g>
{curs}{estrelas}
<rect id="{p}-flash" width="1920" height="1080" fill="#eef8ff" opacity="0"/>"""
    html = "".join(mono(f"{p}-l{k}", txt, "left:0;right:0;text-align:center;top:910px", cor, 76) for k, (txt, cor) in enumerate(
        [("CAMADAS FINÍSSIMAS", "#bff4ff"), ("MICROSCÓPIO ELETRÔNICO", "#c9b8ff"), ("INTELIGÊNCIA ARTIFICIAL", "#7fe6ff"),
         ("PESQUISADORES E VOLUNTÁRIOS", "#ffd27a"), ("COMO NUM JOGO", "#7ff5c8")]))
    js = f"""
  camK("#{p}-cam",620,520,[[0,1.5],[{t_cam + 0.6:.2f},1.25,"sine.inOut"],[{t_mic + 1.3:.2f},1.0],[{dur:.2f},1.0]]);
  tl.fromTo("#{p}-pilha",{{opacity:0,y:40}},{{opacity:1,y:0,duration:0.7,ease:"power3.out"}},0.05);
  tl.fromTo("#{p}-lam",{{opacity:0,y:0}},{{opacity:1,y:240,duration:0.55,ease:"power1.inOut"}},{t_fat - 0.1:.2f});
  some("#{p}-lam",{t_fat + 0.45:.2f},0.15);
  {";".join(f'tl.fromTo("#{p}-s{k}",{{y:0}},{{y:{(300 + k * 62) - (430 + k * 22)},duration:0.9,ease:"back.out(1.4)"}},{t_cam - 0.2 + (8 - k) * 0.04:.2f})' for k in range(N))};
  tl.fromTo("#{p}-pilha",{{x:0}},{{x:0}},0);
  rise("#{p}-l0 span",{t_cam:.2f});
  tl.fromTo("#{p}-micro",{{y:-520}},{{y:0,duration:0.8,ease:"back.out(1.2)"}},{t_foto - 0.5:.2f});
  sai("#{p}-l0 span",{t_mic - 0.4:.2f},0.4); rise("#{p}-l1 span",{t_mic:.2f});
  tl.fromTo("#{p}-feixe",{{opacity:0}},{{opacity:0.9,duration:0.12,repeat:5,yoyo:true}},{t_foto:.2f});
  tl.fromTo("#{p}-flash",{{opacity:0}},{{opacity:0.6,duration:0.06,yoyo:true,repeat:1}},{t_foto + 0.1:.2f});
  tl.fromTo("#{p}-flash",{{opacity:0}},{{opacity:0.6,duration:0.06,yoyo:true,repeat:1,immediateRender:false}},{t_mic + 0.6:.2f});
  tl.fromTo("#{p}-painel",{{opacity:0,scale:0.25,svgOrigin:"{PX + PW / 2} {PY + PW / 2}"}},{{opacity:1,scale:1,svgOrigin:"{PX + PW / 2} {PY + PW / 2}",duration:0.8,ease:"back.out(1.4)"}},{t_mic + 1.3:.2f});
  tl.fromTo("#{p}-feixe",{{opacity:0.9}},{{opacity:0.35,duration:0.3,immediateRender:false}},{t_mic + 1.3:.2f});
  sai("#{p}-l1 span",{t_ia - 0.4:.2f},0.4); rise("#{p}-l2 span",{t_ia:.2f});
  tl.fromTo("#{p}-scan",{{opacity:0,y:0}},{{opacity:1,y:{PW - 10},duration:{t_neu + 0.6 - t_ia:.2f},ease:"none"}},{t_ia:.2f});
  some("#{p}-scan",{t_neu + 0.6:.2f},0.3);
  tl.fromTo("#{p}-painel .cl",{{opacity:0}},{{opacity:0.78,duration:0.25,stagger:{(t_neu + 0.5 - t_ia) / len(cel):.4f}}},{t_ia:.2f});
  {";".join(f'entra("#{p}-x{j}",{t_neu + 0.2:.2f},0.2)' for j in range(7))};
  sai("#{p}-l2 span",{t_cen - 0.2:.2f},0.4); rise("#{p}-l3 span",{t_pes - 0.3:.2f});
  var CO={json.dumps(origens)}, CD={json.dumps([[cel[i][0] - 6, cel[i][1] - 4] for i in erros])};
  for(var j=0;j<7;j++){{
    tl.set("#{p}-c"+j,{{x:CO[j][0],y:CO[j][1]}},0);
    tl.fromTo("#{p}-c"+j,{{opacity:0}},{{opacity:1,duration:0.2}},{t_cen:.2f}+j*0.28);
    tl.to("#{p}-c"+j,{{x:CD[j][0],y:CD[j][1],duration:1.3,ease:"power2.inOut"}},{t_cen:.2f}+j*0.28);
    var tc={t_corr:.2f}+j*0.22;
    tl.fromTo("#{p}-c"+j,{{scale:1,transformOrigin:"0% 0%"}},{{scale:0.8,transformOrigin:"0% 0%",duration:0.08,yoyo:true,repeat:1}},tc);
    tl.fromTo("#{p}-ok"+j,{{opacity:0}},{{opacity:0.9,duration:0.15}},tc+0.05);
    tl.fromTo("#{p}-x"+j,{{opacity:1}},{{opacity:0,duration:0.1,immediateRender:false}},tc+0.05);
    tl.fromTo("#{p}-bu"+j,{{opacity:1,scale:1,transformOrigin:"50% 50%"}},{{opacity:0,scale:2.2,transformOrigin:"50% 50%",duration:0.6,ease:"power2.out",immediateRender:false}},tc+0.05);
  }}
  sai("#{p}-l3 span",{t_jogo - 0.4:.2f},0.4); rise("#{p}-l4 span",{t_jogo:.2f});
  tl.fromTo("#{p}-borda",{{opacity:0}},{{opacity:1,duration:0.2,repeat:3,yoyo:true}},{t_jogo:.2f});
  tl.fromTo("#{p}-borda",{{opacity:0}},{{opacity:0.8,duration:0.3,immediateRender:false}},{t_jogo + 0.9:.2f});
  tl.fromTo("#{p} .st",{{opacity:0,scale:0,rotation:-90,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,rotation:0,transformOrigin:"50% 50%",duration:0.6,ease:"elastic.out(1,0.45)",stagger:0.08}},{t_jogo:.2f});
"""
    js = js.replace(f'"#{p} .st"', f'"#{p}-cam .st"').replace(f'tl.fromTo("#{p}-pilha",{{x:0}},{{x:0}},0);', "")
    return comp(p, dur, svg, html, js, extra, seed=13)


# ---------------------------------------------------------------- mapear 4: 33 anos contra 50 mil, câmera recua em log
def mapear_4():
    CE, SG = "mapear", 4
    p = "mapear_4"
    ini, dur = seg(CE, SG)
    t_anos, t_trab, t_sem, t_ia, t_quase, t_50, t_mil = (T(CE, SG, "anos"), T(CE, SG, "trabalho"), T(CE, SG, "sem"), T(CE, SG, "inteligencia"),
                                                        T(CE, SG, "quase"), T(CE, SG, "50"), T(CE, SG, "mil"))
    PIT, CEL = 70, 60
    S0 = 6 * PIT - 10                      # lado do bloco de 33
    S = S0 * math.sqrt(50000 / 33)         # lado do bloco de 50 mil (mesma escala de área)
    CHAO, CX = 760, 955
    zf = 800 / S
    ox = (820 - CX * zf) / (1 - zf)
    oy = (900 - CHAO * zf) / (1 - zf)
    L = ox + (1040 - ox) / zf
    cel = []
    for i in range(33):
        r, c = divmod(i, 6)
        cel.append(f'<g transform="translate({750 + c * PIT + 30} {CHAO - CEL - r * PIT + 30})"><rect class="cc" x="-30" y="-30" width="{CEL}" height="{CEL}" rx="9" fill="#3be0ff" opacity="0"/></g>')
    extra = (f'<pattern id="{p}-pat" patternUnits="userSpaceOnUse" x="{L:.1f}" y="{CHAO}" width="{PIT}" height="{PIT}"><rect x="5" y="5" width="{CEL}" height="{CEL}" rx="9" fill="#ff4f7d"/></pattern>'
             f'<pattern id="{p}-pat2" patternUnits="userSpaceOnUse" x="{L:.1f}" y="{CHAO}" width="{S0 * 1.12:.1f}" height="{S0 * 1.12:.1f}"><rect x="{S0 * .06:.1f}" y="{S0 * .06:.1f}" width="{S0}" height="{S0}" rx="30" fill="#ffd0dc" fill-opacity=".22" stroke="#ffe3ea" stroke-width="16"/></pattern>')
    svg = f"""
<line x1="-60000" y1="{CHAO + 6}" x2="80000" y2="{CHAO + 6}" stroke="#8d7bff" stroke-width="3" vector-effect="non-scaling-stroke" opacity=".7"/>
<g id="{p}-bloco">{"".join(cel)}</g>
<g transform="translate(-40 0)"><g id="{p}-escala">
 {humano(p + "g", "trabalho", "sentado", 1290, CHAO, 0.5, cena=p)}
 <rect x="1330" y="{CHAO - 104}" width="170" height="14" rx="6" fill="#2a1d70" stroke="#8d7bff" stroke-width="3"/>
 <path d="M1350 {CHAO - 90} L1350 {CHAO} M1480 {CHAO - 90} L1480 {CHAO}" stroke="#8d7bff" stroke-width="6" stroke-linecap="round"/>
 <g transform="translate(1418 {CHAO - 104})"><g id="{p}-tela"><path d="M-8 0 L-30 -66 L36 -66 L52 0 Z" fill="#3a3a8a" stroke="#bff4ff" stroke-width="3" stroke-linejoin="round"/><path d="M-20 -54 L28 -54 L38 -12 L-6 -12 Z" fill="#3be0ff" opacity=".55"/></g></g>
</g>
</g><g transform="translate(750 {CHAO + 34})"><g id="{p}-leg" opacity="0"><rect x="0" y="0" width="{CEL}" height="{CEL}" rx="9" fill="#3be0ff"/>
 <text x="{CEL + 26}" y="{CEL - 10}" font-family="IBM Plex Mono" font-weight="500" font-size="54" letter-spacing="6" fill="#bff4ff">= 1 ANO</text></g></g>
<circle id="{p}-anel" cx="{CX}" cy="{CHAO - S0 / 2}" r="{0.9 * 45 / zf:.0f}" fill="none" stroke="#3be0ff" stroke-width="5" vector-effect="non-scaling-stroke" opacity="0"/>
<rect id="{p}-big" x="{L:.1f}" y="{CHAO - S0}" width="{S0}" height="{S0}" fill="url(#{p}-pat)" stroke="#ff9bb0" stroke-width="4" vector-effect="non-scaling-stroke" opacity="0"/>
<rect id="{p}-big2" x="{L:.1f}" y="{CHAO - S0}" width="{S0}" height="{S0}" fill="url(#{p}-pat2)" opacity="0"/>"""
    html = (texto(f"{p}-n1", f'<span id="{p}-n1v">0</span>', "left:110px;top:70px;font-size:170px;color:#bff4ff") +
            mono(f"{p}-a1", "ANOS", "left:120px;top:300px", "#bff4ff", 50) +
            mono(f"{p}-a2", "TRABALHO HUMANO", "left:120px;top:375px", "#7fe6ff", 44) +
            mono(f"{p}-a3", "SEM A INTELIGÊNCIA", "left:120px;top:450px", "#ff9bb0", 42) +
            mono(f"{p}-a4", "ARTIFICIAL", "left:120px;top:505px", "#ff9bb0", 42) +
            mono(f"{p}-a5", "QUASE", "left:124px;top:562px", "#ffd27a", 44) +
            texto(f"{p}-n2", f'<span id="{p}-n2v">33</span>', "left:110px;top:588px;font-size:160px;color:#ffd0dc") +
            f'<div id="{p}-seta" style="position:absolute;left:640px;top:690px;width:380px;height:6px;background:#ff9bb0;border-radius:3px;transform:scaleX(0);transform-origin:0 50%;box-shadow:0 0 14px #ff4f7d"><i style="position:absolute;right:-6px;top:-9px;border-left:22px solid #ff9bb0;border-top:12px solid transparent;border-bottom:12px solid transparent"></i></div>' +
            mono(f"{p}-a6", "ANOS", "left:124px;top:790px", "#ff9bb0", 46) +
            mono(f"{p}-a7", "33 ANOS", "left:798px;width:300px;text-align:center;top:966px", "#7fe6ff", 50) +
            f'<div id="{p}-lupa" style="position:absolute;left:868px;top:800px;width:160px;height:160px;opacity:0"><svg width="160" height="160" viewBox="0 0 240 240">'
            f'<circle cx="120" cy="120" r="114" fill="#120c3a" stroke="#3be0ff" stroke-width="6"/><line x1="30" y1="182" x2="210" y2="182" stroke="#8d7bff" stroke-width="3"/>'
            + "".join(f'<rect x="{54 + (i % 6) * 22}" y="{158 - (i // 6) * 22}" width="18" height="18" rx="3" fill="#3be0ff"/>' for i in range(33)) + '</svg></div>')
    js = f"""
  camK("#{p}-cam",{ox:.1f},{oy:.1f},[[0,1.1],[{t_sem:.2f},1.0,"sine.inOut"],[{t_mil + 0.1:.2f},{zf:.5f},"power2.inOut"],[{dur:.2f},{zf * 0.97:.5f},"sine.inOut"]]);
  rise("#{p}-n1 > span",0.0,0.6);
  tl.fromTo("#{p}-bloco .cc",{{opacity:0,scale:0.2,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.45,ease:"back.out(2.5)",stagger:0.05}},0.1);
  contar("{p}-n1v",0.1,1.75,0,33);
  rise("#{p}-a1 span",{t_anos:.2f}); rise("#{p}-a2 span",{t_trab:.2f});
  pop("#{p}-leg",{t_anos:.2f},0.4,0.6); some("#{p}-leg",{t_sem + 0.4:.2f},0.4);
  tl.fromTo("#{p}g-olho",{{x:0}},{{x:3,duration:0.2}},0.1);
  tl.set("#{p}g-braco",{{rotation:-60,{ombro("trabalho", "sentado")}}},0);
  tl.fromTo("#{p}g-braco",{{rotation:-60,{ombro("trabalho", "sentado")}}},{{rotation:-66,{ombro("trabalho", "sentado")},duration:0.16,repeat:13,yoyo:true,ease:"sine.inOut"}},0.1);
  entra("#{p}-big",{t_sem:.2f},0.3); entra("#{p}-big2",{t_sem + 2.5:.2f},1.5);
  rise("#{p}-a3 span",{t_sem:.2f}); rise("#{p}-a4 span",{t_ia:.2f});
  rise("#{p}-n2 > span",{t_sem + 0.3:.2f}); rise("#{p}-a6 span",{t_sem + 0.5:.2f});
  entra("#{p}-anel",{t_mil - 1.0:.2f},0.6); rise("#{p}-a7 span",{t_mil - 0.9:.2f}); pop("#{p}-lupa",{t_mil - 0.9:.2f},0.4,0.6);
  var G={{l:Math.log({S0})}};
  tl.fromTo(G,{{l:Math.log({S0})}},{{l:Math.log({S:.1f}),duration:{t_mil + 0.1 - t_sem:.2f},ease:"power2.inOut",onUpdate:function(){{
    var s=Math.exp(G.l), e=document.getElementById("{p}-big"); e.setAttribute("width",s); e.setAttribute("height",s); e.setAttribute("y",{CHAO}-s);
    var u=(G.l-Math.log({S0}))/(Math.log({S:.1f})-Math.log({S0})), z=gsap.getProperty("#{p}-cam","scale"), xw={ox:.1f}+(1470+(1040-1470)*u-{ox:.1f})/z;
    ["{p}-big","{p}-big2","{p}-pat","{p}-pat2"].forEach(function(i){{document.getElementById(i).setAttribute("x",xw);}}); var e2=document.getElementById("{p}-big2"); e2.setAttribute("width",s); e2.setAttribute("height",s); e2.setAttribute("y",{CHAO}-s);
    var v=33*Math.pow(s/{S0},2); document.getElementById("{p}-n2v").textContent=(v>49990?50000:Math.round(v)).toLocaleString("pt-BR");}}}},{t_sem:.2f});
  rise("#{p}-a5 span",{t_quase:.2f});
  tl.fromTo("#{p}-seta",{{scaleX:0}},{{scaleX:1,duration:0.5,ease:"power2.out"}},{t_mil - 0.2:.2f});
  tl.fromTo("#{p}-n2",{{scale:1,transformOrigin:"0% 50%"}},{{scale:1.12,transformOrigin:"0% 50%",duration:0.25,yoyo:true,repeat:1}},{t_mil:.2f});
""" + G.vida_gente(p + "g", dur, (2.6, 5.0))
    return comp(p, dur, svg, html, js, extra, seed=15)
    # ponytail: contador de 50.000 só vale porque o crescimento termina em S exato; se mudar S0, conferir o arredondamento


# ---------------------------------------------------------------- mapear 6: página da Nature 2024, simulação prevê a mosca comendo
def mapear_6():
    CE, SG = "mapear", 6
    p = "mapear_6"
    ini, dur = seg(CE, SG)
    t_atv, t_sim, t_acu, t_mod, t_prev, t_mosca, t_comer, t_test, t_verd, t_vprev, t_conf = (
        T(CE, SG, "ativaram"), T(CE, SG, "simulacao"), T(CE, SG, "acucar"), T(CE, SG, "modelo"), T(CE, SG, "previ"),
        T(CE, SG, "mosca"), T(CE, SG, "comer"), T(CE, SG, "testaram"), T(CE, SG, "verdade"), T(CE, SG, "previsoes"), T(CE, SG, "confirmaram"))
    W, IH = 600, 2126 / 1600
    mk = [("h1", 1140, 786, 270, 40, "#ffb23e"), ("h2", 576, 822, 870, 40, "#ffb23e"), ("h3", 576, 856, 880, 40, "#ffb23e"), ("h4", 576, 891, 160, 40, "#ffb23e"),
          ("v1", 1326, 925, 128, 40, "#38e8a8"), ("v2", 576, 960, 860, 40, "#38e8a8")]
    pg = pagina(p, "shiu2024", W, IH, mk)
    rede_svg, pts, are = rede_rica(f"{p}-r", 11, pre=p)
    esq = min(range(len(pts)), key=lambda k: pts[k][0] + 0.3 * pts[k][1])
    dire = max(range(len(pts)), key=lambda k: pts[k][0] - 0.3 * pts[k][1])
    cam = caminho(pts, are, esq, dire)
    NX, NY, NE = 1170, 450, 0.62
    gx, gy = NX + pts[dire][0] * NE, NY + pts[dire][1] * NE
    sx, sy = NX + pts[esq][0] * NE, NY + pts[esq][1] * NE
    chk = [cam[int(len(cam) * f)] for f in (0.25, 0.5, 0.75)] + [cam[-1]]
    checks = "".join(f'<g transform="translate({NX + x * NE:.0f} {NY + y * NE:.0f})"><g class="ck" opacity="0"><circle r="30" fill="#38e8a8" stroke="#eafff6" stroke-width="4"/><path d="M-13 1 L-4 11 L14 -10" fill="none" stroke="#0b2a20" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g></g>' for x, y in chk)
    extra = mosca_defs(p) + rede_defs(p) + f'<linearGradient id="{p}-acuG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#d9dcef"/></linearGradient>'
    acucar = (f'<path id="{p}-acuL" d="M{sx - 10:.0f} {sy + 128:.0f} L{sx:.0f} {sy + 40:.0f}" stroke="#ffd27a" stroke-width="5" stroke-dasharray="10 8" opacity="0"/>'
              f'<g transform="translate({sx - 10:.0f} {sy + 170:.0f})"><g id="{p}-acu" opacity="0">'
              f'<polygon points="0,-40 46,-18 0,4 -46,-18" fill="url(#{p}-acuG)" stroke="#fff6c8" stroke-width="3"/><polygon points="-46,-18 0,4 0,54 -46,32" fill="#cfd3ea" stroke="#fff6c8" stroke-width="3"/>'
              f'<polygon points="0,4 46,-18 46,32 0,54" fill="#b7bcdc" stroke="#fff6c8" stroke-width="3"/></g></g>')
    svg = f"""
<g transform="translate(110 150) rotate(-2)"><g id="{p}-pg">{pg}</g></g>
<g id="{p}-sim" opacity="0">
 <g transform="translate({NX} {NY}) scale({NE})"><g id="{p}-redeW">{rede_svg}</g></g>
 <circle id="{p}-pulso" r="16" fill="#ffd23e" filter="url(#{p}-glow)" opacity="0"/>
 <circle id="{p}-ini" cx="{sx:.0f}" cy="{sy:.0f}" r="34" fill="none" stroke="#ffb23e" stroke-width="9" opacity="0"/>
 {acucar}
 <path id="{p}-liga" d="M{gx:.0f} {gy:.0f} C {gx + 120:.0f} {gy - 40:.0f} 1460 600 1532 560" fill="none" stroke="#38e8a8" stroke-width="7" stroke-dasharray="500" stroke-dashoffset="500" stroke-linecap="round" filter="url(#{p}-glow)"/>
 <g transform="translate(1660 560)"><g id="{p}-mosca"><g transform="scale(-1.3 1.3)"><g id="{p}-moscaBob">{mosca_rica(p + "-mo", p)}</g></g></g></g>
 <g id="{p}-fa" opacity="0" fill="#ffd23e" filter="url(#{p}-glow)"><circle cx="1490" cy="600" r="9"/><circle cx="1468" cy="628" r="6"/><circle cx="1480" cy="660" r="8"/><circle cx="1450" cy="590" r="5"/></g>
 {checks}
</g>
<g transform="translate(1640 270) rotate(4)"><g id="{p}-foto" opacity="0"><g filter="url(#{p}-sombra)"><rect x="-170" y="-130" width="340" height="300" rx="8" fill="#fffaf0"/></g>
 <image href="assets/mosca.jpg" x="-152" y="-112" width="304" height="228" preserveAspectRatio="xMidYMid slice"/></g></g>"""
    html = (tit(f"{p}-a1", "simulação", "left:1010px;top:250px;font-size:130px;color:#bff4ff") +
            tit(f"{p}-a2", "açúcar", "left:1010px;top:440px;font-size:150px;color:#ffd27a") +
            mono(f"{p}-b0", "AÇÚCAR", f"left:{sx - 160:.0f}px;width:300px;text-align:center;top:{sy + 236:.0f}px", "#ffd27a", 40) +
            mono(f"{p}-b1", "COMER", "left:760px;width:1100px;text-align:center;top:920px", "#ffd27a", 56) +
            mono(f"{p}-b2", "MOSCAS DE VERDADE", "left:760px;width:1100px;text-align:center;top:920px", "#7ff5c8", 56) +
            mono(f"{p}-b3", "PREVISÕES SE CONFIRMARAM", "left:760px;width:1100px;text-align:center;top:920px", "#7ff5c8", 56))
    js = f"""
  camK("#{p}-cam",380,390,[[0,1.62],[{t_mod:.2f},1.5,"sine.inOut"],[{t_mod + 1.5:.2f},1.0],[{dur:.2f},1.0]]);
  tl.fromTo("#{p}-pg",{{y:420,rotation:-5,opacity:0}},{{y:0,rotation:0,opacity:1,duration:0.9,ease:"expo.out"}},0.0);
  rise("#{p}-a1 span",{t_sim:.2f}); rise("#{p}-a2 span",{t_acu:.2f});
  marca("#{p}-h1",{t_acu - 0.6:.2f},0.35); marca("#{p}-h2",{t_acu - 0.25:.2f},0.6); marca("#{p}-h3",{t_acu + 0.35:.2f},0.6); marca("#{p}-h4",{t_acu + 0.95:.2f},0.2);
  sai("#{p}-a1 span",{t_mod - 0.1:.2f}); sai("#{p}-a2 span",{t_mod:.2f});
  entra("#{p}-sim",{t_mod + 0.2:.2f},0.8);
  tl.fromTo("#{p}-redeW",{{scale:0.4,opacity:0,transformOrigin:"50% 50%"}},{{scale:1,opacity:1,transformOrigin:"50% 50%",duration:1.2,ease:"power3.out"}},{t_mod + 0.2:.2f});
  tl.fromTo("#{p}-r .lobo",{{opacity:0}},{{opacity:1,duration:0.8}},{t_mod + 0.3:.2f});
  tl.fromTo("#{p}-r .eds",{{opacity:0}},{{opacity:1,duration:0.8}},{t_mod + 0.5:.2f});
  tl.fromTo("#{p}-mosca",{{x:400}},{{x:0,duration:1.0,ease:"power3.out"}},{t_mod + 0.6:.2f});
  tl.fromTo("#{p}-moscaBob",{{y:0,rotation:-2,transformOrigin:"50% 50%"}},{{y:-8,rotation:2,transformOrigin:"50% 50%",duration:0.5,repeat:18,yoyo:true,ease:"sine.inOut"}},{t_mod + 1.6:.2f});
  tl.fromTo("#{p}-mo-asas",{{scaleY:1,transformOrigin:"50% 100%"}},{{scaleY:0.3,transformOrigin:"50% 100%",duration:0.05,repeat:{2 * int((dur - t_mod - 0.6) / 0.1) - 1},yoyo:true,ease:"none"}},{t_mod + 0.6:.2f});
  pop("#{p}-acu",{t_prev - 0.2:.2f},0.3,0.7); entra("#{p}-acuL",{t_prev:.2f},0.3); rise("#{p}-b0 span",{t_prev:.2f});
  tl.fromTo("#{p}-ini",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.4,ease:"back.out(3)"}},{t_prev:.2f});
  var cam={json.dumps([[round(NX + x * NE, 1), round(NY + y * NE, 1)] for x, y in cam])}, xs=cam.map(function(q){{return q[0];}}), ys=cam.map(function(q){{return q[1];}});
  tl.set("#{p}-pulso",{{x:xs[0],y:ys[0]}},0);
  [0,1].forEach(function(k){{
    var t0={t_prev + 0.3:.2f}+k*1.3;
    tl.fromTo("#{p}-pulso",{{opacity:0}},{{opacity:1,duration:0.1}},t0);
    tl.to("#{p}-pulso",{{keyframes:{{x:xs,y:ys,easeEach:"none"}},duration:1.1,ease:"none",immediateRender:false}},t0);
    tl.fromTo("#{p}-pulso",{{opacity:1}},{{opacity:0,duration:0.1,immediateRender:false}},t0+1.05);
  }});
  traco("#{p}-liga",{t_comer - 0.6:.2f},0.6,500);
  tl.fromTo("#{p}-mo-prob",{{attr:{{d:"M104 10 q 14 6 20 20"}}}},{{attr:{{d:"M104 10 q 34 10 50 46"}},duration:0.35,ease:"back.out(2)"}},{t_comer - 0.1:.2f});
  tl.fromTo("#{p}-fa",{{opacity:0,scale:0.5,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.3,ease:"back.out(3)"}},{t_comer:.2f});
  rise("#{p}-b1 span",{t_comer - 0.2:.2f});
  sai("#{p}-b1 span",{t_test - 0.3:.2f},0.4);
  marca("#{p}-v1",{t_test:.2f},0.3); marca("#{p}-v2",{t_test + 0.3:.2f},0.8);
  pop("#{p}-foto",{t_test + 0.6:.2f},0.4,0.8);
  rise("#{p}-b2 span",{t_verd - 0.5:.2f});
  sai("#{p}-b2 span",{t_vprev - 0.4:.2f},0.4); rise("#{p}-b3 span",{t_vprev:.2f});
  tl.fromTo("#{p}-sim .ck",{{opacity:0,scale:0,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.6,ease:"elastic.out(1,0.45)",stagger:0.3}},{t_conf - 0.4:.2f});
"""
    return comp(p, dur, svg, html, js, extra, seed=8)


# ---------------------------------------------------------------- mapear 7: o cérebro virou mapa e o mapa se comporta como cérebro
def mapear_7():
    CE, SG = "mapear", 7
    p = "mapear_7"
    ini, dur = seg(CE, SG)
    t_rep, t_um, t_vir, t_mapa, t_mapa2, t_comp, t_comecou, t_compo, t_cer2 = (
        0.0, T(CE, SG, "um"), T(CE, SG, "virou"), T(CE, SG, "mapa"), T(CE, SG, "mapa", 1), T(CE, SG, "computador"),
        T(CE, SG, "comecou"), T(CE, SG, "comportar"), T(CE, SG, "cerebro", 1))
    rede_svg, pts, are = rede_rica(f"{p}-r", 11, pre=p)
    NX, NY, NE = 960, 400, 0.78
    rg = random.Random(9)
    cams = []
    for _ in range(12):
        a_, b_ = rg.sample(range(len(pts)), 2)
        c = caminho(pts, are, a_, b_)
        if len(c) > 4:
            cams.append([[round(NX + x * NE, 1), round(NY + y * NE, 1)] for x, y in c])
    cams = cams[:6]
    grade = "".join(f'<line x1="{x}" y1="110" x2="{x}" y2="690"/>' for x in range(480, 1441, 80)) + "".join(f'<line x1="470" y1="{y}" x2="1450" y2="{y}"/>' for y in range(120, 691, 80))
    pulsos = "".join(f'<circle id="{p}-pl{k}" r="11" fill="#ffd23e" filter="url(#{p}-glow)" opacity="0"/>' for k in range(len(cams)))
    extra = rede_defs(p) + monitor_defs(p) + cer_defs(p) + f'<radialGradient id="{p}-bloom" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#3be0ff" stop-opacity=".45"/><stop offset="1" stop-color="#3be0ff" stop-opacity="0"/></radialGradient>'
    svg = f"""
<ellipse id="{p}-bloom" cx="960" cy="400" rx="640" ry="420" fill="url(#{p}-bloom)" opacity="0"/>
<g id="{p}-mon" opacity="0">{monitor(p, 450, 100, 1020, 600)}</g>
<g id="{p}-grade" stroke="#4a5aff" stroke-width="2" opacity="0">{grade}</g>
<g transform="translate({NX} {NY}) scale({NE})"><g id="{p}-redeW" opacity="0">{rede_svg}</g></g>
{pulsos}
<g transform="translate(960 400) scale(1.25)"><g id="{p}-cerW">{cerebro_card(p + "-bc", gl=p + "-glow", cer=p + "-cer")}</g></g>
<g transform="translate(960 400) scale(1.25)"><g id="{p}-contorno" opacity="0"><path transform="scale(1 1.38)" d="{SIL_CER}" fill="none" stroke="#ff9fd0" stroke-width="5" vector-effect="non-scaling-stroke" stroke-dasharray="16 10" filter="url(#{p}-glow)"/></g></g>"""
    html = (mono(f"{p}-a1", "UM CÉREBRO", "left:0;right:0;text-align:center;top:850px", "#bff4ff", 60) +
            mono(f"{p}-a2", "VIROU UM MAPA", "left:0;right:0;text-align:center;top:850px", "#c9b8ff", 60) +
            tit(f"{p}-f1", "O mapa começou a se comportar", "left:0;right:0;text-align:center;top:822px;font-size:92px;color:#eef1f7") +
            tit(f"{p}-f2", "como um cérebro", "left:0;right:0;text-align:center;top:935px;font-size:92px;color:#ffd98a"))
    js = f"""
  camK("#{p}-cam",960,420,[[0,1.18],[{t_vir:.2f},1.06,"sine.inOut"],[{t_comp:.2f},1.0],[{dur:.2f},0.96,"sine.inOut"]]);
  tl.fromTo("#{p}-cerW",{{opacity:0,scale:0.6,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:1.0,ease:"back.out(1.5)"}},0.1);
  tl.fromTo("#{p}-cerW",{{y:0}},{{y:-10,duration:0.9,repeat:1,yoyo:true,ease:"sine.inOut",immediateRender:false}},1.1);
  rise("#{p}-a1 span",{t_um:.2f});
  tl.fromTo("#{p}-cerW",{{scale:1}},{{scale:1.08,duration:0.2,repeat:1,yoyo:true,immediateRender:false}},{T(CE, SG, "cerebro"):.2f});
  tl.fromTo("#{p}-cerW",{{opacity:1,scaleY:1}},{{opacity:0,scaleY:0.15,duration:0.6,ease:"power2.in",immediateRender:false}},{t_vir:.2f});
  sai("#{p}-a1 span",{t_vir - 0.2:.2f},0.35); rise("#{p}-a2 span",{t_vir:.2f});
  entra("#{p}-redeW",{t_vir + 0.3:.2f},0.3);
  tl.fromTo("#{p}-r .no",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,transformOrigin:"50% 50%",duration:0.4,ease:"back.out(2.4)",stagger:{{each:0.006}}}},{t_vir + 0.3:.2f});
  tl.fromTo("#{p}-r .eds",{{opacity:0}},{{opacity:1,duration:0.8}},{t_mapa:.2f});
  tl.fromTo("#{p}-r .lobo",{{opacity:0}},{{opacity:0.6,duration:0.8}},{t_mapa:.2f});
  tl.fromTo("#{p}-grade",{{opacity:0}},{{opacity:0.35,duration:0.8}},{t_mapa2:.2f});
  entra("#{p}-mon",{t_comp - 0.5:.2f},0.4);
  tl.fromTo("#{p}-mon",{{scale:1.35,svgOrigin:"960 400"}},{{scale:1,svgOrigin:"960 400",duration:0.9,ease:"power3.out"}},{t_comp - 0.5:.2f});
  entra("#{p}-bloom",{t_comp:.2f},0.8);
  sai("#{p}-a2 span",{t_comecou - 0.45:.2f},0.4);
  rise("#{p}-f1 span",{t_comecou:.2f},0.8); rise("#{p}-f2 span",{T(CE, SG, "como"):.2f},0.8);
  var P={json.dumps(cams)};
  P.forEach(function(c,k){{
    var xs=c.map(function(q){{return q[0];}}), ys=c.map(function(q){{return q[1];}});
    tl.set("#{p}-pl"+k,{{x:xs[0],y:ys[0]}},0);
    [0,1].forEach(function(r){{
      var t0={t_compo:.2f}+k*0.22+r*1.6;
      tl.fromTo("#{p}-pl"+k,{{opacity:0}},{{opacity:1,duration:0.12}},t0);
      tl.to("#{p}-pl"+k,{{keyframes:{{x:xs,y:ys,easeEach:"none"}},duration:1.3,ease:"none",immediateRender:false}},t0);
      tl.fromTo("#{p}-pl"+k,{{opacity:1}},{{opacity:0,duration:0.15,immediateRender:false}},t0+1.2);
    }});
  }});
  tl.fromTo("#{p}-r .g2",{{opacity:1}},{{opacity:0.35,duration:0.15,repeat:9,yoyo:true,ease:"none"}},{t_compo:.2f});
  tl.fromTo("#{p}-contorno",{{opacity:0,scale:1.15,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.9,ease:"power2.out"}},{t_cer2 - 0.3:.2f});
"""
    return comp(p, dur, svg, html, js, extra, seed=19, fundo=("#2c1a6a", "#171049", "#0a0a24"))


# ---------------------------------------------------------------- mapear 8: uma mosca, modelo simplificado, não é copiar uma consciência
def mapear_8():
    CE, SG = "mapear", 8
    p = "mapear_8"
    ini, dur = seg(CE, SG)
    t_simp, t_mapi, t_con, t_nao, t_cop, t_consc, t_guard, t_img, t_cer, t_rod, t_comp, t_ela = (
        T(CE, SG, "simplificado"), T(CE, SG, "mapi"), T(CE, SG, "conexoes"), T(CE, SG, "nao"), T(CE, SG, "copiar"), T(CE, SG, "consciencia"),
        T(CE, SG, "guard"), T(CE, SG, "imagem"), T(CE, SG, "cerebro"), T(CE, SG, "rodando"), T(CE, SG, "computador"), T(CE, SG, "ela"))
    rede_svg, pts, are = rede_rica(f"{p}-r", 11, n=90, pre=p)
    NX, NY, NE = 960, 470, 0.6
    pp = p + "h"
    # consciência = a pessoa e as lembranças dela (orbes do gente.py) girando em volta da cabeça
    HX, HY = 1660, 300
    TX, TY = anc("casa", "em_pe", "cabeca_topo")
    TX, TY = 1665 - TX * 0.97, 880 + TY * 0.97          # topo da cabeça na tela (pessoa espelhada)
    ORB = [("coracao", "#ff4fa3"), ("nota", "#8d7bff"), ("bolo", "#ffb23e"), ("sol", "#ffd23e"), ("carro", "#3be0ff"), ("relogio", "#38e8a8")]
    ANG = [math.radians(a) for a in (-150, -120, -90, -60, -30, 0)]
    fios8 = "".join(f'<line x1="{TX:.0f}" y1="{TY + 12:.0f}" x2="{HX + 175 * math.cos(a):.0f}" y2="{HY + 175 * math.sin(a):.0f}" stroke="{c}" stroke-width="4" stroke-dasharray="6 6" stroke-linecap="round"/>' for a, (_, c) in zip(ANG, ORB))
    aura = "".join(G.orbe(f"{p}-ob{k}", sim, HX + 175 * math.cos(a), HY + 175 * math.sin(a), cor, 40) for k, (a, (sim, cor)) in enumerate(zip(ANG, ORB)))
    extra = (mosca_defs(p) + rede_defs(p) + monitor_defs(p) + cer_defs(p) +
             f'<radialGradient id="{p}-aur" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffd0ea" stop-opacity=".55"/><stop offset="1" stop-color="#ff9bd0" stop-opacity="0"/></radialGradient>')
    pontos = "".join(f'<circle class="pt" cx="{960 + x}" cy="{400 + y}" r="7" fill="#ffd23e" filter="url(#{p}-glow)" opacity="0"/>' for x, y in
                     [(-150, -40), (-90, 30), (-40, -70), (40, 40), (100, -30), (160, 50), (-170, 60), (0, 0), (120, 90), (-110, -100)])
    tela = (f'<g transform="translate(960 400) scale(.78)">{cerebro_card(p + "-bc", gl=p + "-glow", cer=p + "-cer")}</g>{pontos}')
    svg = f"""<g id="{p}-A">
 <g transform="translate(360 500)"><g id="{p}-mosca"><g transform="scale(1.75)"><g id="{p}-moscaBob">{mosca_rica(p + "-mo", p)}</g></g></g></g>
 <path d="M600 470 L 660 470" stroke="#8d7bff" stroke-width="6" stroke-linecap="round"/><path d="M646 452 L670 470 L646 488" fill="none" stroke="#8d7bff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
 <g transform="translate({NX} {NY}) scale({NE})"><g id="{p}-redeW">{rede_svg}</g></g>
 <g transform="translate({NX} {NY}) scale({NE})"><g id="{p}-copia" opacity="0"><g opacity=".7">{rede_svg.replace(f'id="{p}-r"', f'id="{p}-r2"')}</g></g></g>
 <ellipse id="{p}-aura" cx="{HX}" cy="{HY}" rx="260" ry="210" fill="url(#{p}-aur)" opacity="0"/>
 <g id="{p}-fios" opacity="0">{fios8}</g>
 {humano(pp, "casa", "em_pe", 1665, 880, 0.97, espelho=True, cena=p)}
 <g id="{p}-orb" opacity="0">{aura}</g>
 <g id="{p}-bar" opacity="0"><line x1="1320" y1="200" x2="1320" y2="800" stroke="#ff4f7d" stroke-width="8" stroke-dasharray="20 14" filter="url(#{p}-glow)"/></g>
 <g transform="translate(1320 470)"><g id="{p}-xx" opacity="0" stroke="#ff4f7d" stroke-width="26" stroke-linecap="round" filter="url(#{p}-glow)"><path d="M-66 -66 L66 66 M66 -66 L-66 66"/></g></g>
</g>
<g id="{p}-B" opacity="0">
 <g transform="translate(960 470)"><g id="{p}-polar"><g transform="translate(-960 -470)">
  <g filter="url(#{p}-sombra)"><rect x="470" y="96" width="980" height="784" rx="10" fill="#fffaf0"/></g>
  <rect x="500" y="126" width="920" height="630" rx="4" fill="#1a1050"/>
  <g transform="translate(960 420) scale(.82) translate(-960 -420)">{monitor(p, 610, 190, 700, 420, tela)}</g>
 </g></g></g>
</g>
<rect id="{p}-flash" width="1920" height="1080" fill="#fff" opacity="0"/>"""
    html = "".join(mono(f"{p}-l{k}", txt, f"left:0;right:0;text-align:center;top:{top}px", cor, tam) for k, (txt, cor, top, tam) in enumerate(
        [("BEM SIMPLIFICADO", "#bff4ff", 900, 56), ("MAPEAR CONEXÕES", "#c9b8ff", 900, 56), ("NÃO É COPIAR UMA CONSCIÊNCIA", "#ff9bb0", 900, 56),
         ("GUARDE ESSA IMAGEM", "#ffd27a", 920, 56), ("UM CÉREBRO RODANDO DENTRO DE UM COMPUTADOR", "#bff4ff", 930, 44), ("ELA VAI VOLTAR", "#ffd27a", 920, 64)]))
    js = f"""
  camK("#{p}-A",60,500,[[0,1.6],[0.9,1.55,"none"],[{t_mapi - 0.2:.2f},1.0,"power2.inOut"],[{t_guard:.2f},1.0]]);
  tl.fromTo("#{p}-moscaBob",{{y:0,rotation:-2,transformOrigin:"50% 50%"}},{{y:-10,rotation:2,transformOrigin:"50% 50%",duration:0.55,repeat:12,yoyo:true,ease:"sine.inOut"}},0);
  tl.fromTo("#{p}-mo-asas",{{scaleY:1,transformOrigin:"50% 100%"}},{{scaleY:0.3,transformOrigin:"50% 100%",duration:0.05,repeat:{2 * int(t_guard / 0.1) - 1},yoyo:true,ease:"none"}},0);
  entra("#{p}-r .lobo",0,0.4); entra("#{p}-r .eds",0,0.4);
  rise("#{p}-l0 span",{t_simp:.2f});
  tl.fromTo("#{p}-r .g0",{{opacity:0.5}},{{opacity:0,duration:0.6}},{t_simp + 0.2:.2f});
  tl.fromTo("#{p}-r .e0",{{opacity:0.4}},{{opacity:0,duration:0.6}},{t_simp + 0.2:.2f});
  sai("#{p}-l0 span",{t_mapi - 0.4:.2f},0.4); rise("#{p}-l1 span",{t_mapi:.2f});
  tl.fromTo("#{p}-r .e2",{{opacity:0.9}},{{opacity:0.3,duration:0.2,repeat:5,yoyo:true}},{t_con:.2f});
  tl.fromTo("#{p}-r .g2",{{opacity:1}},{{opacity:0.4,duration:0.2,repeat:5,yoyo:true}},{t_con:.2f});
  entra("#{p}-aura",{t_nao - 0.4:.2f},0.6); entra("#{p}-orb",{t_nao - 0.3:.2f},0.6); entra("#{p}-fios",{t_nao - 0.3:.2f},0.6);
  tl.fromTo("{",".join(f"#{p}-ob{k}" for k in range(len(ORB)))}",{{y:0}},{{y:-10,duration:0.7,repeat:3,yoyo:true,ease:"sine.inOut",stagger:0.12}},{t_nao - 0.3:.2f});
  sai("#{p}-l1 span",{t_nao - 0.45:.2f},0.4); rise("#{p}-l2 span",{t_nao:.2f});
  entra("#{p}-copia",{t_cop - 0.1:.2f},0.2);
  tl.fromTo("#{p}-copia",{{x:0}},{{x:190,duration:{t_consc - t_cop + 0.1:.2f},ease:"power2.in",immediateRender:false}},{t_cop - 0.1:.2f});
  entra("#{p}-bar",{t_consc - 0.05:.2f},0.1);
  tl.fromTo("#{p}-xx",{{opacity:0,scale:2.2,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.3,ease:"back.out(3)"}},{t_consc:.2f});
  tl.fromTo("#{p}-copia",{{x:190}},{{x:30,duration:0.8,ease:"power3.out",immediateRender:false}},{t_consc + 0.05:.2f});
  some("#{p}-copia",{t_consc + 0.5:.2f},0.5);
  tl.fromTo("#{pp}-olho",{{x:0}},{{x:3,duration:0.3}},{t_cop:.2f});
  tl.fromTo("#{p}-A",{{opacity:1}},{{opacity:0,duration:0.5}},{t_guard - 0.2:.2f});
  sai("#{p}-l2 span",{t_guard - 0.4:.2f},0.4); rise("#{p}-l3 span",{t_guard:.2f});
  entra("#{p}-B",{t_guard + 0.1:.2f},0.5);
  tl.fromTo("#{p}-polar",{{scale:1.25,rotation:0,transformOrigin:"50% 50%"}},{{scale:1,rotation:0,transformOrigin:"50% 50%",duration:1.2,ease:"power3.out"}},{t_guard + 0.1:.2f});
  tl.fromTo("#{p}-B .pt",{{opacity:0}},{{opacity:1,duration:0.18,repeat:21,yoyo:true,stagger:{{each:0.13,from:"random"}}}},{t_guard + 0.5:.2f});
  tl.fromTo("#{p}-flash",{{opacity:0}},{{opacity:0.85,duration:0.06,yoyo:true,repeat:1}},{t_img - 0.1:.2f});
  tl.fromTo("#{p}-polar",{{rotation:0}},{{rotation:-4,duration:0.5,ease:"back.out(2)",immediateRender:false}},{t_img:.2f});
  sai("#{p}-l3 span",{t_cer - 0.35:.2f},0.35); rise("#{p}-l4 span",{t_cer:.2f});
  sai("#{p}-l4 span",{t_ela - 0.3:.2f},0.35); rise("#{p}-l5 span",{t_ela:.2f},0.8);
  tl.fromTo("#{p}-polar",{{scale:1,y:0}},{{scale:0.9,y:-20,duration:1.4,ease:"power2.inOut",immediateRender:false}},{t_ela:.2f});
""" + G.vida_gente(pp, dur, (1.2, 3.4, 6.2))
    return comp(p, dur, svg, html, js, extra, seed=22)


# ---------------------------------------------------------------- lista de cenas
_FN = {("escrever", 0): escrever_0, ("escrever", 2): escrever_2, ("escrever", 5): escrever_5, ("escrever", 7): escrever_7,
       ("mapear", 0): mapear_0, ("mapear", 3): mapear_3, ("mapear", 4): mapear_4, ("mapear", 6): mapear_6, ("mapear", 7): mapear_7,
       ("mapear", 8): mapear_8}
MAPA = {k: f"{k[0]}_{k[1]}" for k in _FN}
CENAS = [(MAPA[k], fn, seg(*k)[1]) for k, fn in _FN.items()]

if __name__ == "__main__":
    print(escreve_cenas(CENAS, PASTA))
    for k, v in TEMPOS.items():
        print(k, " ".join(f"{w}{'#' + str(n) if n else ''}={t}" for w, n, t in v))
