"""Cenas v5, grupo g2_trancada: os 9 segmentos da cena "trancada" (memória que existe, mas está sem acesso).

  python3 build_g2_trancada.py     # escreve compositions/ e index.html desta pasta

Metáfora: a porta e o cadeado. Rodada 2: a pessoa de verdade (gente.py) vive cada cena num ambiente diferente
(corredor e cozinha, sala, quarto à noite, consultório, rua de madrugada); a cabeça com cérebro rosa fica só no
segmento 2, onde a narração fala do cérebro. O camundongo da caixa isométrica volta no segmento do MIT.
"""
import base64, math, os, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
sys.path.insert(0, os.path.join(AQUI, "../../cenas-v4"))
from motor import *  # noqa: E402,F401
from build4 import rato, caixa, grad_caixa, bolt  # noqa: E402
import gente as G  # noqa: E402
AQUI = os.path.dirname(os.path.abspath(__file__))  # motor e build4 também definem AQUI; vale o desta pasta

CE = "trancada"
DOCS = os.path.join(AQUI, "assets/docs")

# ---------------------------------------------------------------- JS próprio: câmera e transformações por atributo
# Tudo que se move por translate/scale aqui é escrito direto no atributo `transform` (sem x/y/scale do GSAP),
# então não existe briga entre atributo e GSAP (GOTCHAS 1 a 4). Estados encadeados: o fim de um passo é o começo do outro.
JS2 = r"""
  function _el(s){return document.querySelector(s);}
  function camT(st){var z=st[0];return "translate("+(st[3]-z*st[1]).toFixed(2)+" "+(st[4]-z*st[2]).toFixed(2)+") scale("+z.toFixed(4)+")";}
  function camK(sel,t0,dur,a,b,ease){var e=_el(sel),o={k:0};
    tl.fromTo(o,{k:0},{k:1,duration:dur,ease:ease||"power3.inOut",immediateRender:false,onUpdate:function(){var k=o.k;
      var z=Math.exp(Math.log(a[0])+(Math.log(b[0])-Math.log(a[0]))*k);
      e.setAttribute("transform",camT([z,a[1]+(b[1]-a[1])*k,a[2]+(b[2]-a[2])*k,a[3]+(b[3]-a[3])*k,a[4]+(b[4]-a[4])*k]));}},t0);}
  function trT(st){return "translate("+st[0].toFixed(2)+" "+st[1].toFixed(2)+") rotate("+(st[3]||0).toFixed(2)+") scale("+st[2].toFixed(4)+")";}
  function trK(sel,t0,dur,a,b,ease){var e=_el(sel),o={k:0};
    tl.fromTo(o,{k:0},{k:1,duration:dur,ease:ease||"power3.inOut",immediateRender:false,onUpdate:function(){var k=o.k,r=[];
      for(var i=0;i<4;i++){r.push((a[i]||0)+((b[i]||0)-(a[i]||0))*k);} e.setAttribute("transform",trT(r));}},t0);}
"""


def cam(p, ini, passos):
    """Câmera em #{p}-cam. Estado (z, Px, Py[, Sx, Sy]): o ponto P do mundo aparece em S na tela com zoom z.
    passos: [(t0, dur, estado, ease)]. Devolve o JS (o estado inicial é aplicado na hora)."""
    def full(st):
        return list(st) + [960, 540] if len(st) == 3 else list(st)
    a = full(ini)
    js = f'_el("#{p}-cam").setAttribute("transform",camT({a}));'
    for t0, d, st, *ease in passos:
        b = full(st)
        js += f'camK("#{p}-cam",{t0:.2f},{d:.2f},{a},{b},"{ease[0] if ease else "power3.inOut"}");'
        a = b
    return js


def mov(sel, ini, passos):
    """Movimento por atributo de um grupo: estado (x, y, s[, rot]). Devolve (atributo inicial, JS)."""
    a = list(ini) + [0] * (4 - len(ini))
    js = ""
    for t0, d, st, *ease in passos:
        b = list(st) + [0] * (4 - len(st))
        js += f'trK("{sel}",{t0:.2f},{d:.2f},{a},{b},"{ease[0] if ease else "power3.inOut"}");'
        a = b
    x, y, s, r = list(ini) + [0] * (4 - len(ini))
    return f'translate({x} {y}) rotate({r}) scale({s})', js


def comp(p, dur, svg, html, js, extra="", **kw):
    return composicao(p, dur, svg, html, JS2 + js, extra, **kw)


# ---------------------------------------------------------------- peças de arte da cena
def cadeado(p, k, cor=AMBAR):
    """Cadeado centrado em (0,0), ~120 x 150. Ids: {p}-cad{k} (todo), {p}-arg{k} (argola, sobe para abrir)."""
    return (f'<g id="{p}-cad{k}"><rect x="-70" y="-95" width="140" height="190" fill="none" opacity="0"/>'
            f'<g id="{p}-arg{k}"><path d="M-38 -6 L-38 -46 A38 38 0 0 1 38 -46 L38 -6" fill="none" stroke="#d9dcf0" stroke-width="15" stroke-linecap="round"/></g>'
            f'<rect x="-60" y="-12" width="120" height="96" rx="18" fill="{cor}" stroke="#fff3c8" stroke-width="4"/>'
            f'<rect x="-60" y="-12" width="120" height="30" rx="14" fill="#fff" opacity=".22"/>'
            f'<circle cx="0" cy="26" r="13" fill="#2a1446"/><path d="M-6 30 L-9 58 L9 58 L6 30 Z" fill="#2a1446"/></g>')


def orbe(p, k, cor=AMBAR, r=34):
    """Lembrança: esfera de luz centrada em (0,0). Ids {p}-orb{k} e {p}-orbh{k} (halo)."""
    return (f'<g id="{p}-orb{k}"><circle id="{p}-orbh{k}" r="{r * 2.1:.0f}" fill="{cor}" opacity=".22" filter="url(#{p}-blur6)"/>'
            f'<circle r="{r}" fill="{cor}"/><circle cx="{-r * .3:.0f}" cy="{-r * .32:.0f}" r="{r * .38:.0f}" fill="#fff" opacity=".55"/></g>')


def chave(cor=AMBAR):
    """Chave apontando para a direita, cabo em (0,0), ~250 de comprimento."""
    return (f'<circle cx="0" cy="0" r="38" fill="none" stroke="{cor}" stroke-width="16"/>'
            f'<path d="M38 0 L230 0 M190 0 L190 36 M222 0 L222 28" stroke="{cor}" stroke-width="16" fill="none" stroke-linecap="round"/>')


def porta_frente(p, k, x, y, w, h, folha="#2a2068", borda=LILAS):
    """Porta de frente: batente (com brilho), vão e folha. A folha {p}-fl{k} abre com scaleX a partir da dobradiça (esquerda)."""
    return (f'<g filter="url(#{p}-sombra)"><rect x="{x - 26}" y="{y - 26}" width="{w + 52}" height="{h + 26}" rx="10" fill="#1d1752"/></g>'
            f'<rect x="{x - 26}" y="{y - 26}" width="{w + 52}" height="{h + 26}" rx="10" fill="none" stroke="{borda}" stroke-width="6" filter="url(#{p}-glow)"/>'
            f'@VAO{k}@'
            f'<g id="{p}-fl{k}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{folha}" stroke="#5a4cc0" stroke-width="4"/>'
            f'<rect x="{x + w * .14:.0f}" y="{y + h * .07:.0f}" width="{w * .72:.0f}" height="{h * .36:.0f}" rx="8" fill="none" stroke="#5a4cc0" stroke-width="4"/>'
            f'<rect x="{x + w * .14:.0f}" y="{y + h * .52:.0f}" width="{w * .72:.0f}" height="{h * .4:.0f}" rx="8" fill="none" stroke="#5a4cc0" stroke-width="4"/>'
            f'<circle cx="{x + w * .86:.0f}" cy="{y + h * .5:.0f}" r="{max(6, w * .045):.0f}" fill="{AMBAR}"/></g>')


def parede(p, chao=900, cor=("#24206a", "#1a1650")):
    return (f'<rect x="-1500" y="-1500" width="4920" height="{chao + 1500}" fill="url(#{p}-par)"/>'
            f'<rect x="-1500" y="{chao}" width="4920" height="1600" fill="#100c34"/>'
            f'<rect x="-1500" y="{chao - 6}" width="4920" height="12" fill="#3a3290"/>')


def defs_parede(p, a="#2a2474", b="#18144a"):
    return f'<linearGradient id="{p}-par" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{b}"/><stop offset="1" stop-color="{a}"/></linearGradient>'


def bolha(p, k, conteudo, x=330, y=-40):
    """Balão de pensamento em coordenadas locais da pessoa (sai do topo da cabeça). Id {p}-bol{k}."""
    return (f'<g id="{p}-bol{k}"><circle cx="262" cy="34" r="9" fill="#eef1f7" opacity=".85"/><circle cx="286" cy="8" r="14" fill="#eef1f7" opacity=".9"/>'
            f'<ellipse cx="{x}" cy="{y}" rx="78" ry="58" fill="#eef1f7"/><g transform="translate({x} {y})">{conteudo}</g></g>')


def T(sg):
    return lambda w, n=0, d=None: palavra(CE, sg, w, n, d)


def tit(id_, txt, estilo, tam=96, cor="#eef1f7", mono=False):
    fam = "font-family:'IBM Plex Mono',monospace;font-weight:700;letter-spacing:.08em;" if mono else ""
    return texto(id_, txt, f"{estilo};font-size:{tam}px;color:{cor};{fam}")



# ---------------------------------------------------------------- rodada 2: a pessoa de verdade (gente.py) e ambientes com história
# Personagem novo (gente.py, giro 25 -> ANCORAS de giro 30). Os grupos dele têm caixa gigante (máscaras M-9999), então toda
# rotação/escala em grupo que contenha a pessoa usa svgOrigin em px no sistema local dela, nunca transformOrigin em %.
def anc(pose):
    return G.ANCORAS[("casa", pose, 30)]


def pescoco(pose):
    cx, cy = anc(pose)["cabeca_centro"]
    return f"{cx} {cy + 45}"


def ombro(pose):
    return "%s %s" % anc(pose)["ombro_braco"]


def humano(p, var="casa", pose="em_pe", cadeira=True, caneca=True, mao=""):
    """Pessoa de gente.py dentro de {p}-flip (scaleX -1 com svgOrigin "0 0" vira para trás). Ids de gente com prefixo {p}-g.
    caneca=False tira a caneca que a pose sentada traz na mão. mao entra no fim de {p}-g-braco (gira junto com o braço)."""
    g = p + "-g"
    s = G.gente(g, var, pose, cadeira=cadeira)
    if not caneca and pose != "em_pe":
        i = s.index('<path d="M 14,-254 C 0,-254 0,-232 14,-232"')
        j = s.index('/>', s.rindex('stroke="#a98bff"')) + 2
        assert 0 < j - i < 6000
        s = s[:i] + s[j:]
    if mao:
        i = s.rindex("<g", 0, s.index(f'id="{g}-braco"'))
        prof = 0
        for m in re.finditer(r"<g\b|</g>", s[i:]):
            prof += -1 if m.group(0) == "</g>" else 1
            if prof == 0:
                break
        k = i + m.start()
        s = s[:k] + mao + s[k:]
    return f'<g id="{p}-flip">{s}</g>'


def vida_h(p, dur, pisc=(2.0, 5.3, 8.8, 12.1, 16.4)):
    """JS: respiração, balanço da cabeça e piscadas (vida_gente já usa svgOrigin)."""
    return G.vida_gente(p + "-g", dur, pisc)


def bol_xy(pose="em_pe"):
    """Centro do balão de pensamento no sistema local da pessoa (acima e à direita de cabeca_topo)."""
    tx, ty = anc(pose)["cabeca_topo"]
    return tx + 175, ty - 175


def bolha_h(p, k, conteudo, sentado=False, rx=100, ry=75):
    """Balão de pensamento no sistema local da pessoa, saindo do topo da cabeça (ANCORAS cabeca_topo). Id {p}-bol{k}."""
    pose = "sentado" if sentado else "em_pe"
    tx, ty = anc(pose)["cabeca_topo"]
    x, y = bol_xy(pose)
    return (f'<g id="{p}-bol{k}"><circle cx="{tx + 50:.0f}" cy="{ty - 22:.0f}" r="11" fill="#eef1f7" opacity=".85"/><circle cx="{tx + 88:.0f}" cy="{ty - 62:.0f}" r="17" fill="#eef1f7" opacity=".92"/>'
            f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rx}" ry="{ry}" fill="#eef1f7"/><g transform="translate({x:.0f} {y:.0f})">{conteudo}</g></g>')


def comodo(p, k, x0, x1, c1, c2, topo=-700, chao=900, piso="#241638", rodape="#6a4a8a", piso_h=700):
    """Parede com gradiente, chão e rodapé. Devolve (svg, defs)."""
    defs = f'<linearGradient id="{p}-cm{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c2}"/><stop offset="1" stop-color="{c1}"/></linearGradient>'
    svg = (f'<rect x="{x0}" y="{topo}" width="{x1 - x0}" height="{chao - topo}" fill="url(#{p}-cm{k})"/>'
           f'<rect x="{x0}" y="{chao}" width="{x1 - x0}" height="{piso_h}" fill="{piso}"/>'
           f'<rect x="{x0}" y="{chao - 10}" width="{x1 - x0}" height="14" fill="{rodape}"/>')
    return svg, defs


def vao(p, k, x0, x1, ytop, chao=900, lado=1, topo=-700, aberta=True, cor="#4a3a9a"):
    """Porta numa parede vista em corte. Folha fechada {p}-dc{k}; folha aberta {p}-do{k} (dobradiça do lado `lado`)."""
    w = x1 - x0
    xa = x1 if lado > 0 else x0
    xb = xa + lado * 110
    cy = (ytop + chao) / 2
    return (f'<rect x="{x0}" y="{topo}" width="{w}" height="{chao - topo}" fill="#1a1448"/>'
            f'<rect x="{x0}" y="{ytop}" width="{w}" height="{chao - ytop}" fill="#0c0a26"/>'
            f'<rect x="{x0 - 8}" y="{ytop - 8}" width="{w + 16}" height="{chao - ytop + 8}" fill="none" stroke="{LILAS}" stroke-width="6" filter="url(#{p}-glow)"/>'
            f'<g id="{p}-dc{k}" opacity="{0 if aberta else 1}"><rect x="{x0}" y="{ytop}" width="{w}" height="{chao - ytop}" fill="{cor}" stroke="#8d7bff" stroke-width="3"/>'
            f'<circle cx="{xa - lado * 14}" cy="{cy + 10:.0f}" r="7" fill="{AMBAR}"/></g>'
            f'<g id="{p}-do{k}" opacity="{1 if aberta else 0}"><polygon points="{xa},{ytop} {xb},{ytop + 34} {xb},{chao - 16} {xa},{chao}" fill="{cor}" stroke="#8d7bff" stroke-width="4"/>'
            f'<circle cx="{xa + lado * 92}" cy="{cy + 10:.0f}" r="7" fill="{AMBAR}"/></g>')


def janela(x, y, w, h, ceu=("#101a4a", "#3a2a7a"), lua=True, moldura="#d9cfe8", cortina="#ff8fb8"):
    ls = (f'<circle cx="{x + w * .72:.0f}" cy="{y + h * .3:.0f}" r="{min(w, h) * .12:.0f}" fill="#fff3c8"/>' if lua else
          f'<ellipse cx="{x + w * .3:.0f}" cy="{y + h * .3:.0f}" rx="{w * .16:.0f}" ry="{h * .06:.0f}" fill="#fff" opacity=".8"/>')
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{ceu[0]}"/><rect x="{x}" y="{y + h * .5:.0f}" width="{w}" height="{h * .5:.0f}" fill="{ceu[1]}" opacity=".7"/>{ls}'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{moldura}" stroke-width="14"/>'
            f'<path d="M{x + w / 2} {y} V{y + h} M{x} {y + h / 2} H{x + w}" stroke="{moldura}" stroke-width="8"/>'
            f'<rect x="{x - 34}" y="{y - 20}" width="40" height="{h + 50}" rx="10" fill="{cortina}" opacity=".85"/><rect x="{x + w - 6}" y="{y - 20}" width="40" height="{h + 50}" rx="10" fill="{cortina}" opacity=".85"/>'
            f'<rect x="{x - 50}" y="{y - 30}" width="{w + 100}" height="12" rx="6" fill="{moldura}"/>')


def luminaria(p, k, x, y, topo=-700, cor="#ffb23e"):
    """Luminária pendente com cone de luz. Id do brilho {p}-luz{k}."""
    return (f'<g id="{p}-luz{k}" opacity=".9"><polygon points="{x - 50},{y + 46} {x + 50},{y + 46} {x + 260},{y + 640} {x - 260},{y + 640}" fill="{cor}" opacity=".10"/>'
            f'<ellipse cx="{x}" cy="{y + 50}" rx="120" ry="40" fill="{cor}" opacity=".25" filter="url(#{p}-blur6)"/></g>'
            f'<path d="M{x} {topo} V{y}" stroke="#6a4a5a" stroke-width="6"/><path d="M{x - 44} {y} L{x + 44} {y} L{x + 70} {y + 50} L{x - 70} {y + 50} Z" fill="{cor}"/>'
            f'<ellipse cx="{x}" cy="{y + 50}" rx="66" ry="10" fill="#fff3c8"/>')


def mesa(x0, x1, ytop, chao=900, cor="#6a3e2a", perna="#4a2a1e"):
    return (f'<rect x="{x0}" y="{ytop}" width="{x1 - x0}" height="24" rx="8" fill="{cor}"/>'
            f'<rect x="{x0 + 20}" y="{ytop + 24}" width="22" height="{chao - ytop - 24}" fill="{perna}"/><rect x="{x1 - 42}" y="{ytop + 24}" width="22" height="{chao - ytop - 24}" fill="{perna}"/>')


def abajur(x, ytop, cor="#ffd27a"):
    return (f'<ellipse cx="{x}" cy="{ytop - 110}" rx="110" ry="80" fill="{cor}" opacity=".18"/><rect x="{x - 8}" y="{ytop - 90}" width="16" height="90" fill="#c9b8a0"/>'
            f'<path d="M{x - 50} {ytop - 90} L{x + 50} {ytop - 90} L{x + 34} {ytop - 160} L{x - 34} {ytop - 160} Z" fill="{cor}"/><ellipse cx="{x}" cy="{ytop - 4}" rx="34" ry="8" fill="#c9b8a0"/>')


def planta(x, chao=900, s=1.0):
    folhas = "".join(f'<ellipse cx="0" cy="-60" rx="22" ry="62" fill="{c}" transform="translate(0 -110) rotate({a})"/>'
                     for a, c in [(-50, "#2f9a70"), (-20, "#38b87e"), (10, "#2f9a70"), (40, "#38b87e"), (70, "#2a8a66")])
    return (f'<g transform="translate({x} {chao}) scale({s})">{folhas}<path d="M-44 -110 L44 -110 L34 0 L-34 0 Z" fill="#c96a4a"/>'
            f'<rect x="-50" y="-118" width="100" height="16" rx="6" fill="#e07a58"/></g>')


def poltrona(x, chao, s, cor="#c9506a", cor2="#a03a56"):
    return (f'<g transform="translate({x} {chao}) scale({s})"><rect x="-150" y="-410" width="74" height="300" rx="30" fill="{cor2}"/>'
            f'<rect x="-130" y="-176" width="270" height="70" rx="24" fill="{cor}"/><rect x="-118" y="-106" width="18" height="106" fill="#3a2030"/><rect x="112" y="-106" width="18" height="106" fill="#3a2030"/></g>')


def quadro_escuro():
    """Moldura com a lembrança apagada: fundo escuro rachado de vermelho (caixa 120 x 92, centrada)."""
    return ('<rect x="-62" y="-48" width="124" height="96" rx="6" fill="#8a6a3a"/><rect x="-54" y="-40" width="108" height="80" fill="#2a0c1c"/>'
            f'<path d="M-40 -30 L-10 2 L-24 30 M-10 2 L22 -10 L44 26 M22 -10 L30 -34" stroke="{VERM}" stroke-width="4" fill="none" stroke-linecap="round"/>')


def gota(x, y, s=1.0):
    return f'<path transform="translate({x} {y}) scale({s})" d="M0 -16 C 8 -4 12 2 12 8 A12 12 0 0 1 -12 8 C -12 2 -8 -4 0 -16 Z" fill="#9fe6ff"/>'



# ================================================================ 0 casa: sai do corredor, entra na cozinha e esquece o que ia fazer
def trancada_0():
    p = "trancada_0"
    ini, dur = seg(CE, 0)
    t = T(0)
    t_voce, t_entrou, t_esq, t_que = t("Você"), t("entrou"), t("esqueceu"), t("que", 0)
    g = p + "-g"
    S = 0.85
    w0, d0 = comodo(p, 0, -700, 1000, "#3c2d80", "#271c5c", piso="#22163a")
    w1, d1 = comodo(p, 1, 1060, 2700, "#8a4a62", "#55294a", piso="#3a2028", rodape="#c08a6a")
    corredor = (G.quadro(f"{p}-q0", "familia", 330, 400, .85) + G.quadro(f"{p}-q1", "praia", 660, 370, .7, rot=2)
                + mesa(90, 300, 700) + abajur(195, 700) + planta(880, s=.9))
    azulejo = "".join(f'<path d="M1160 {y} H1670" stroke="#f0d8c8" stroke-width="2" opacity=".25"/>' for y in range(590, 690, 32))
    cozinha = (janela(1230, 320, 260, 230) + luminaria(p, 0, 1360, 250)
               + f'<rect x="1160" y="560" width="510" height="130" fill="#f0d8c8" opacity=".14"/>{azulejo}'
               + '<rect x="1530" y="330" width="170" height="170" rx="8" fill="#b8665a"/><path d="M1615 340 V490" stroke="#8a4a42" stroke-width="4"/>'
               + '<rect x="1170" y="704" width="490" height="196" fill="#b8665a"/>'
               + "".join(f'<rect x="{x}" y="720" width="104" height="166" rx="6" fill="none" stroke="#8a4a42" stroke-width="4"/><circle cx="{x + 88}" cy="800" r="5" fill="#f0d8c8"/>' for x in (1186, 1306, 1426, 1546))
               + '<rect x="1150" y="686" width="530" height="22" rx="6" fill="#efe2cf"/>'
               + '<rect x="1284" y="632" width="36" height="54" rx="4" fill="#bff4ff" opacity=".35" stroke="#bff4ff" stroke-width="3"/>'
               + '<path d="M1540 686 Q1540 640 1580 640 Q1620 640 1620 686 Z" fill="#ff8a6a"/><path d="M1620 660 l26 -14" stroke="#ff8a6a" stroke-width="8" stroke-linecap="round"/>'
               + '<rect x="1726" y="420" width="180" height="480" rx="18" fill="#dfe6f2"/><path d="M1726 570 H1906" stroke="#9aa6c0" stroke-width="5"/>'
               + '<rect x="1746" y="470" width="10" height="70" rx="5" fill="#9aa6c0"/><rect x="1746" y="600" width="10" height="110" rx="5" fill="#9aa6c0"/>')
    porta = vao(p, 0, 1000, 1060, 380, lado=1)
    tr0, js_mov = mov(f"#{p}-pw", (460, 900, S), [(t_entrou - 0.05, 1.3, (1330, 900, S), "power1.inOut")])
    interrog = f'<g id="{p}-int" opacity="0"><text x="0" y="34" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="120" fill="{MAGENTA}">?</text></g>'
    item = f'<g id="{p}-item">{G.orbe(p + "-oc", "copo", 0, 0, CIANO, 50)}</g>'
    svg = f"""{w0}{w1}{corredor}{cozinha}{porta}
<g id="{p}-pw" transform="{tr0}">{humano(p, "casa", "em_pe")}{bolha_h(p, 0, item + interrog)}</g>"""
    html = (tit(f"{p}-t1", "VOCÊ JÁ ENTROU NUM CÔMODO", "left:0;right:0;text-align:center;top:950px", 64, "#bff4ff", True) +
            tit(f"{p}-t2", "O QUE IA FAZER LÁ?", "left:110px;top:920px", 100, "#ffd98a"))
    js = cam(p, (1.0, 760, 540), [
        (0, t_entrou, (1.06, 720, 560), "sine.inOut"),
        (t_entrou - 0.1, 1.5, (1.12, 1420, 560), "power2.inOut"),
        (t_entrou + 1.4, dur - t_entrou - 1.4, (1.16, 1400, 570), "sine.inOut")])
    js += js_mov + f"""
  pop("#{p}-bol0", 0.5, 0.3, 0.8);
  tl.fromTo("#{p}-item",{{rotation:-8,transformOrigin:"50% 50%"}},{{rotation:8,duration:0.5,repeat:5,yoyo:true,ease:"sine.inOut"}},0.9);
  tl.fromTo("#{g}-corpo",{{y:0}},{{y:-12,duration:0.16,repeat:7,yoyo:true,ease:"sine.inOut"}},{t_entrou - 0.05:.2f});
  rise("#{p}-t1 span", {t_voce:.2f});
  some("#{p}-t1", {t_esq - 0.1:.2f}, 0.3);
  tl.fromTo("#{g}-olho",{{x:0}},{{x:2,duration:0.3}},{t_voce:.2f});
  tl.fromTo("#{p}-item",{{opacity:1,scale:1,transformOrigin:"50% 50%"}},{{opacity:0,scale:0.2,transformOrigin:"50% 50%",duration:0.35,ease:"back.in(2)",immediateRender:false}},{t_esq:.2f});
  pop("#{p}-int", {t_esq + 0.3:.2f}, 0.2, 0.7);
  tl.fromTo("#{p}-int",{{rotation:-10,transformOrigin:"50% 50%"}},{{rotation:10,duration:0.35,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_esq + 1.0:.2f});
  tl.fromTo("#{g}-olho",{{x:2}},{{x:-2,duration:0.2,repeat:2,yoyo:true,immediateRender:false}},{t_esq + 0.1:.2f});
  tl.fromTo("#{p}-flip",{{scaleX:1,svgOrigin:"0 0"}},{{scaleX:-1,svgOrigin:"0 0",duration:0.3,ease:"power2.inOut"}},{t_esq + 0.55:.2f});
  tl.fromTo("#{g}-braco",{{rotation:0,svgOrigin:"{ombro("em_pe")}"}},{{rotation:-155,svgOrigin:"{ombro("em_pe")}",duration:0.45,ease:"back.out(1.6)"}},{t_que + 0.1:.2f});
  rise("#{p}-t2 span", {t_que - 0.05:.2f}, 0.8);
""" + vida_h(p, dur, (1.6, 4.0))
    return comp(p, dur, svg, html, js, d0 + d1)


# ================================================================ 4 doc: MIT 2015, camundongos com amnésia
def trancada_4():
    p = "trancada_4"
    ini, dur = seg(CE, 4)
    t = T(4)
    t_mit, t_cam, t_amn, t_lemb, t_perd, t_cien, t_acen, t_luz, t_neu, t_mem = (
        t("MIT"), t("Camundongos"), t("amnésia"), t("lembranças"), t("perdidas"), t("cientistas"), t("acenderam"), t("luz"), t("neurônios"), t("memória"))
    b64 = base64.b64encode(open(os.path.join(DOCS, "ryan2015.png"), "rb").read()).decode()
    PW = 700
    PH = PW * 2071 / 1600
    k = PW / 1600
    hl_y, hl_h = 1408 * k, 104 * k  # "One Sentence Summary: Memory can be retrieved by optogenetic activation..."
    pagina = (f'<g transform="translate(150 96) rotate(-2.5 {PW / 2} {PH / 2:.0f})"><g id="{p}-pg">'
              f'<g filter="url(#{p}-sombra)"><rect x="-10" y="-10" width="{PW + 20}" height="{PH + 20:.0f}" rx="6" fill="#fffdf6"/></g>'
              f'<image href="data:image/png;base64,{b64}" x="0" y="0" width="{PW}" height="{PH:.0f}"/>'
              f'<g id="{p}-hl"><rect x="{180 * k:.1f}" y="{hl_y:.1f}" width="{1240 * k:.1f}" height="{hl_h:.1f}" rx="6" fill="{AMBAR}" opacity=".38"/></g>'
              f'<rect x="{180 * k - 8:.1f}" y="{hl_y - 8:.1f}" width="{1240 * k + 16:.1f}" height="{hl_h + 16:.1f}" rx="10" fill="none" stroke="{AMBAR}" stroke-width="5" id="{p}-hlb" opacity="0"/>'
              f'</g></g>')
    # camundongo na caixa (arte aprovada do build4), à direita
    CS = 0.72
    CX, CY = 1400 - CS * 960, 650 - CS * 490
    cabeca = (CX + CS * 1052, CY + CS * 440)
    neur = "".join(f'<circle class="n" cx="{x * 1.7:.0f}" cy="{y * 1.7:.0f}" r="9" fill="#9aa0c8"/>' for x, y in
                   [(-40, -14), (-18, 16), (6, -22), (28, 10), (46, -12), (-30, 34), (14, 36), (-52, 8)])
    svg = f"""{pagina}
<g id="{p}-box" opacity="0"><g transform="translate({CX:.1f} {CY:.1f}) scale({CS})">{caixa(p)}
 <g transform="translate(900 700) scale(1.15)"><g id="{p}-ratoW"><g id="{p}-bob">{rato(p)}</g></g></g>
 <path id="{p}-cabo" d="M1052 -200 C 1052 100 1052 300 1052 440" fill="none" stroke="#9aa6d0" stroke-width="12" stroke-linecap="round" stroke-dasharray="700" stroke-dashoffset="700"/>
 <path id="{p}-luzf" d="M1052 -200 C 1052 100 1052 300 1052 440" fill="none" stroke="#7fe6ff" stroke-width="14" stroke-linecap="round" stroke-dasharray="90 800" stroke-dashoffset="90" filter="url(#{p}-glow)" opacity="0"/>
</g></g>
<circle id="{p}-halo" cx="{cabeca[0]:.0f}" cy="{cabeca[1] + 14:.0f}" r="40" fill="#7fe6ff" opacity="0" filter="url(#{p}-glow)"/>
<g transform="translate(1690 260)"><g id="{p}-bolW" opacity="0">
 <circle cx="-150" cy="215" r="12" fill="#eef1f7" opacity=".8"/><circle cx="-118" cy="168" r="18" fill="#eef1f7" opacity=".85"/>
 <circle r="140" fill="#141040" stroke="#eef1f7" stroke-width="6"/>
 <g id="{p}-nos">{neur}</g>
 <g id="{p}-orbW" opacity=".25">{orbe(p, 0, AMBAR, 30)}</g>
 <g transform="translate(0 4) scale(.55)"><g id="{p}-cadW">{cadeado(p, 0, "#8d8fb0")}</g></g>
 <g id="{p}-aneis" opacity="0" fill="none" stroke="{AMBAR}" stroke-width="6"><circle id="{p}-a1" r="60"/><circle id="{p}-a2" r="60"/></g>
</g></g>"""
    html = (tit(f"{p}-t1", "2015", "left:1240px;top:170px", 230, "#ffd98a") +
            tit(f"{p}-t2", "MIT", "left:1280px;top:480px", 160, "#bff4ff", True) +
            tit(f"{p}-t3", "AMNÉSIA", "right:90px;top:900px;text-align:right", 80, "#c9b8ff", True) +
            tit(f"{p}-t4", "A MEMÓRIA VOLTOU", "right:60px;top:895px;text-align:right", 88, "#ffd98a"))
    hx, hy = 150 + 180 * k + 620 * k, 96 + hl_y + 20
    js = cam(p, (1.0, 960, 540), [
        (0.2, 1.4, (1.05, 860, 540), "sine.inOut"),
        (1.6, 2.4, (1.7, hx, hy, 560, 640), "power3.inOut"),
        (t_cam - 0.6, 1.2, (1.0, 960, 540, 960, 540), "power3.inOut"),
        (t_cien - 0.5, dur - t_cien + 0.5, (1.03, 1000, 540), "sine.inOut")])
    js += f"""
  tl.fromTo("#{p}-pg",{{y:420,opacity:0}},{{y:0,opacity:1,duration:1.0,ease:"expo.out"}},0.05);
  rise("#{p}-t1 span", 0.35, 0.9);
  tl.fromTo("#{p}-hl",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,transformOrigin:"0% 50%",duration:1.6,ease:"power2.inOut"}},1.9);
  entra("#{p}-hlb", 3.4, 0.3);
  rise("#{p}-t2 span", {t_mit:.2f});
  some("#{p}-t1", {t_cam - 0.7:.2f}, 0.3); some("#{p}-t2", {t_cam - 0.7:.2f}, 0.3);
  entra("#{p}-box", {t_cam - 0.3:.2f}, 0.5);
  tl.fromTo("#{p}-ratoW",{{x:-260}},{{x:0,duration:1.2,ease:"power2.out"}},{t_cam - 0.3:.2f});
  tl.fromTo("#{p}-bob",{{y:0}},{{y:-5,duration:0.8,repeat:{int((dur - t_cam) / 0.8)},yoyo:true,ease:"sine.inOut"}},{t_cam:.2f});
  rise("#{p}-t3 span", {t_amn:.2f});
  some("#{p}-t3", {t_mem - 0.4:.2f}, 0.3);
  pop("#{p}-bolW", {t_lemb:.2f}, 0.4, 0.8);
  tl.fromTo("#{p}-orbW",{{opacity:0.7}},{{opacity:0.18,duration:0.9}},{t_perd:.2f});
  tl.fromTo("#{p}-cadW",{{rotation:-8,transformOrigin:"50% 50%"}},{{rotation:8,duration:0.12,repeat:5,yoyo:true,ease:"none"}},{t_perd:.2f});
  tl.fromTo("#{p}-cabo",{{attr:{{"stroke-dashoffset":700}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.9,ease:"power2.out"}},{t_cien - 0.3:.2f});
  [0,1].forEach(function(j){{
    tl.fromTo("#{p}-luzf",{{opacity:0,attr:{{"stroke-dashoffset":90}}}},{{opacity:1,attr:{{"stroke-dashoffset":-650}},duration:0.8,ease:"power1.in",immediateRender:false}},{t_acen:.2f}+j*1.0);
  }});
  tl.fromTo("#{p}-halo",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:0.75,scale:1.6,transformOrigin:"50% 50%",duration:0.45,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_luz:.2f});
  tl.fromTo("#{p}-nos .n",{{attr:{{fill:"#9aa0c8"}}}},{{attr:{{fill:"#7fe6ff"}},duration:0.2,stagger:0.07}},{t_neu:.2f});
  tl.fromTo("#{p}-arg0",{{y:0}},{{y:-30,duration:0.35,ease:"back.out(3)"}},{t_mem - 0.15:.2f});
  tl.fromTo("#{p}-cadW",{{opacity:1,y:0}},{{opacity:0,y:80,duration:0.6,ease:"power2.in",immediateRender:false}},{t_mem + 0.3:.2f});
  tl.fromTo("#{p}-orbW",{{opacity:0.18,scale:1,transformOrigin:"50% 50%"}},{{opacity:1,scale:1.5,transformOrigin:"50% 50%",duration:0.7,ease:"elastic.out(1,0.5)",immediateRender:false}},{t_mem:.2f});
  entra("#{p}-aneis", {t_mem:.2f}, 0.1);
  ["a1","a2"].forEach(function(q,i){{tl.fromTo("#{p}-"+q,{{scale:0.6,opacity:0.9,transformOrigin:"50% 50%"}},{{scale:2.0,opacity:0,transformOrigin:"50% 50%",duration:1.0,ease:"power2.out"}},{t_mem:.2f}+i*0.4);}});
  rise("#{p}-t4 span", {t_mem:.2f}, 0.8);
  tl.fromTo("#{p}-rPalpebra",{{y:-52}},{{y:0,duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t_amn + 1.2:.2f});
  tl.fromTo("#{p}-rPalpebra",{{y:-52}},{{y:0,duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t_luz + 0.6:.2f});
"""
    return comp(p, dur, svg, html, js, grad_caixa(p, "c"))


def pw(cx, cy, s):
    """Estado (x, y, s) que põe o centro da cabeça da pessoa em (cx, cy) com escala s."""
    return (round(cx - s * 205, 2), round(cy - s * 140, 2), s)


def cerebro_em(cx, cy, s):
    """Centro do cérebro no mundo para a pessoa com cabeça centrada em (cx, cy), escala s."""
    return cx - 13 * s, cy - 56 * s


def cacos(p, k, cor=AMBAR, r=30):
    """Lembrança que se parte: 5 cacos {p}-cc{k}-i em volta de (0,0)."""
    pts = [(-1, -1), (1, -1), (1.2, .6), (-.2, 1.2), (-1.2, .4)]
    out = ""
    for i, (dx, dy) in enumerate(pts):
        out += (f'<g id="{p}-cc{k}-{i}"><path d="M0 0 L{dx * r:.0f} {dy * r:.0f} L{pts[(i + 1) % 5][0] * r:.0f} {pts[(i + 1) % 5][1] * r:.0f} Z" '
                f'fill="{cor}" stroke="#fff3c8" stroke-width="2"/></g>')
    return out


# ================================================================ 1 doc: efeito da porta (Radvansky e Copeland, 2006)
# Sala de estar. A pessoa leva a lembrança no balão, atravessa a porta da direita para o outro cômodo e a lembrança se parte.
def trancada_1():
    p = "trancada_1"
    ini, dur = seg(CE, 1)
    t = T(1)
    t_efe, t_2006, t_est, t_atr, t_atrap, t_lemb, t_voce = t("efeito"), t("2006"), t("estudo"), t("atravessar"), t("atrapalhar"), t("lembrança"), t("você")
    g = p + "-g"
    X, Y, W, H = 1370, 300, 320, 600
    outro = (f'<rect x="{X}" y="{Y}" width="{W}" height="{H}" fill="url(#{p}-vg)"/>'
             f'<polygon points="{X},{Y + H} {X + W},{Y + H} {X + W * .78},{Y + H - 150} {X + W * .22},{Y + H - 150}" fill="#3a2a30"/>'
             f'<rect x="{X + W * .3:.0f}" y="{Y + 110}" width="{W * .4:.0f}" height="{H * .3:.0f}" fill="#bfe6ff" opacity=".25"/>'
             f'<rect x="{X + W * .3:.0f}" y="{Y + 110}" width="{W * .4:.0f}" height="{H * .3:.0f}" fill="none" stroke="#d9cfe8" stroke-width="5" opacity=".5"/>')
    porta = porta_frente(p, 0, X, Y, W, H).replace("@VAO0@", outro)
    w0, d0 = comodo(p, 0, -700, 2700, "#3c2d80", "#241a58", piso="#22163a")
    tapete = '<ellipse cx="760" cy="960" rx="560" ry="46" fill="#ff8fb8" opacity=".22"/><ellipse cx="760" cy="960" rx="500" ry="36" fill="none" stroke="#ff8fb8" stroke-width="4" opacity=".4"/>'
    sala = (tapete + G.quadro(f"{p}-q0", "familia", 1205, 430, .55)
            + poltrona(660, 900, .8) + planta(1820, s=.95))
    c0 = (900, 900, .85)
    dentro = (1500, 845, .42)
    tr0, js_mov = mov(f"#{p}-pw", c0, [(t_atr - 0.1, 1.5, dentro, "power1.inOut")])
    lemb = f'<g id="{p}-orbW">{G.orbe(p + "-ob", "relogio", 0, 0, AMBAR, 52)}</g><g id="{p}-cac" opacity="0">{cacos(p, 0, AMBAR, 40)}</g>'
    svg = f"""{w0}{sala}
<ellipse cx="{X + W / 2}" cy="905" rx="230" ry="18" fill="#05031a" opacity=".5"/>
{porta}
<g id="{p}-pw" transform="{tr0}">{humano(p, "casa", "em_pe")}{bolha_h(p, 0, lemb)}</g>"""
    img = os.path.join(DOCS, "radvansky2006.png")
    if os.path.exists(img):  # página real, se alguém soltar o PNG em assets/docs
        b64 = base64.b64encode(open(img, "rb").read()).decode()
        miolo = f'<img src="data:image/png;base64,{b64}" style="width:100%;display:block;border-radius:6px">'
    else:  # ficha da citação real (a página não está no repositório: ver CREDITOS.md de video-v2)
        miolo = ("<div style=\"font:700 44px 'IBM Plex Mono',monospace;letter-spacing:.06em;color:#ffb23e\">MEMORY &amp; COGNITION</div>"
                 "<div style=\"font:700 64px 'EB Garamond',serif;line-height:1.05;color:#fffaf0;margin:26px 0 22px;white-space:normal\">"
                 f"Walking through doorways <span id=\"{p}-mk\" style=\"background:linear-gradient(#ffb23e66,#ffb23e66) no-repeat 0 85%/0% 40%\">causes forgetting</span></div>"
                 "<div style=\"font:500 44px 'IBM Plex Mono',monospace;color:#c9b8ff\">Radvansky e Copeland</div>")
    card = (f'<div id="{p}-card" style="position:absolute;left:60px;top:430px;width:600px;padding:40px 44px;border-radius:22px;'
            f'background:rgba(16,12,52,.94);border:4px solid #8d7bff;box-shadow:0 30px 80px rgba(0,0,0,.6);opacity:0">{miolo}</div>')
    html = (tit(f"{p}-t1", "EFEITO DA PORTA", "left:70px;top:116px", 86, "#ffd98a") +
            tit(f"{p}-t2", "2006", "left:76px;top:262px", 120, "#bff4ff", True) + card)
    js = cam(p, (1.0, 960, 540), [
        (0, t_atr, (1.05, 940, 560), "sine.inOut"),
        (t_atr - 0.2, 1.8, (1.18, 1300, 590), "power2.inOut"),
        (t_voce - 0.3, dur - t_voce + 0.3, (1.85, 1530, 640), "power3.inOut")])
    js += js_mov + f"""
  pop("#{p}-bol0", 0.3, 0.3, 0.8);
  tl.fromTo("#{p}-orbW",{{rotation:-6,transformOrigin:"50% 50%"}},{{rotation:6,duration:0.6,repeat:7,yoyo:true,ease:"sine.inOut"}},0.9);
  tl.fromTo("#{g}-olho",{{x:0}},{{x:2,duration:0.3}},0.6);
  rise("#{p}-t1 span", {t_efe:.2f}, 0.8);
  tl.fromTo("#{p}-fl0",{{scaleX:1,transformOrigin:"0% 50%"}},{{scaleX:0.06,transformOrigin:"0% 50%",duration:0.6,ease:"power2.inOut"}},{t_efe + 0.6:.2f});
  rise("#{p}-t2 span", {t_2006:.2f}, 0.8);
  tl.fromTo("#{p}-card",{{opacity:0,y:60}},{{opacity:1,y:0,duration:0.8,ease:"expo.out"}},{t_est:.2f});
  tl.fromTo("#{p}-mk",{{backgroundSize:"0% 40%"}},{{backgroundSize:"100% 40%",duration:0.9,ease:"power2.inOut"}},{t_atr:.2f});
  tl.fromTo("#{g}-corpo",{{y:0}},{{y:-12,duration:0.17,repeat:7,yoyo:true,ease:"sine.inOut"}},{t_atr - 0.1:.2f});
  tl.fromTo("#{p}-orbW",{{opacity:1}},{{opacity:0,duration:0.15,immediateRender:false}},{t_lemb - 0.3:.2f});
  entra("#{p}-cac", {t_lemb - 0.3:.2f}, 0.05);
  [[-30,-24],[32,-26],[38,18],[-6,32],[-40,14]].forEach(function(d,i){{
    tl.fromTo("#{p}-cc0-"+i,{{x:0,y:0,rotation:0,transformOrigin:"50% 50%"}},{{x:d[0],y:d[1],rotation:(i%2?90:-90),duration:1.1,ease:"power2.out"}},{t_lemb - 0.3:.2f});
  }});
  tl.fromTo("#{p}-cac",{{opacity:1}},{{opacity:0.35,duration:0.8,immediateRender:false}},{t_lemb + 0.8:.2f});
  some("#{p}-card", {t_voce - 0.4:.2f}, 0.4); some("#{p}-t2", {t_voce - 0.4:.2f}, 0.4); some("#{p}-t1", {t_voce - 0.4:.2f}, 0.4);
  tl.fromTo("#{g}-olho",{{x:2}},{{x:-2,duration:0.25,repeat:3,yoyo:true,immediateRender:false}},{t_lemb:.2f});
""" + vida_h(p, dur, (1.4, 4.4, 9.4))
    return comp(p, dur, svg, html, js, d0 + f'<linearGradient id="{p}-vg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a2a3a"/><stop offset=".7" stop-color="#7a4a5a"/><stop offset="1" stop-color="#8a5a62"/></linearGradient>')


# ================================================================ 2 episódios: a porta marca o fim de um; lembrar é abrir um caminho
def trancada_2():
    p = "trancada_2"
    ini, dur = seg(CE, 2)
    t = T(2)
    (t_cer, t_epi, t_porta, t_fim, t_efe, t_peq, t_nem, t_apa, t_lemb, t_abrir, t_cam, t_pode, t_falh) = (
        t("cérebro"), t("episódios"), t("porta"), t("fim"), t("efeito"), t("pequeno"), t("nem"), t("aparece"),
        t("Lembrar"), t("abrir"), t("caminho"), t("pode"), t("falhar"))
    cx, cy, s = 300, 530, 1.9
    bx, by = cerebro_em(cx, cy, s)
    EW, EG, E0, EY, EH = 250, 64, 600, 380, 300
    cores = [(LILAS, "#2c2470"), (MENTA, "#123f3c"), (AMBAR, "#4a3216"), (MAGENTA, "#4a1636")]
    eps, portas = "", ""
    for i, (c, f) in enumerate(cores):
        x = E0 + i * (EW + EG)
        tipo = ["familia", "aniversario", "carro", "formatura"][i]
        sc = (EH - 28) / 150
        obj = (f'<clipPath id="{p}-ec{i}"><rect x="{x + 14}" y="{EY + 14}" width="{EW - 28}" height="{EH - 28}" rx="12"/></clipPath>'
               f'<rect x="{x + 14}" y="{EY + 14}" width="{EW - 28}" height="{EH - 28}" rx="12" fill="#fffaf0"/>'
               f'<g clip-path="url(#{p}-ec{i})"><g transform="translate({x + 14 - (200 * sc - EW + 28) / 2:.1f} {EY + 14}) scale({sc:.3f})">{G.cena_quadro(tipo)}</g></g>')
        eps += (f'<g id="{p}-ep{i}"><g filter="url(#{p}-sombra)"><rect x="{x}" y="{EY}" width="{EW}" height="{EH}" rx="18" fill="{f}"/></g>'
                f'{obj}'
                f'<rect x="{x}" y="{EY}" width="{EW}" height="{EH}" rx="18" fill="none" stroke="{c}" stroke-width="5"/></g>')
        if i < 3:
            dx = x + EW + EG / 2
            portas += (f'<g id="{p}-pt{i}"><rect x="{dx - 26}" y="{EY - 30}" width="52" height="{EH + 60}" rx="6" fill="#1d1752" stroke="{LILAS}" stroke-width="5"/>'
                       f'<g id="{p}-pf{i}"><rect x="{dx - 18}" y="{EY - 20}" width="36" height="{EH + 40}" fill="#3a2f9a"/><circle cx="{dx + 10}" cy="{EY + EH / 2}" r="6" fill="{AMBAR}"/></g></g>')
    xs = [E0 + i * (EW + EG) + EW / 2 for i in range(4)]
    ym = EY + EH / 2
    cam_d = f"M{bx:.0f} {by:.0f} C {bx + 120:.0f} {by - 160:.0f} {E0 - 80} {ym} {xs[0]:.0f} {ym}" + "".join(f" L{x:.0f} {ym}" for x in xs[1:])
    falha_x = E0 + 2 * (EW + EG) + EW + EG / 2
    svg = f"""<g id="{p}-pw" transform="translate({pw(cx, cy, s)[0]} {pw(cx, cy, s)[1]}) scale({s})">{pessoa(p)}</g>
<g id="{p}-eps">{eps}</g>{portas}
<path id="{p}-cam1" d="{cam_d}" fill="none" stroke="#bff4ff" stroke-width="12" stroke-linecap="round" stroke-dasharray="2400" stroke-dashoffset="2400" filter="url(#{p}-glow)"/>
<g id="{p}-x" opacity="0" stroke="{VERM}" stroke-width="18" stroke-linecap="round" filter="url(#{p}-glow)"><path d="M{falha_x - 50} {ym - 50} L{falha_x + 50} {ym + 50} M{falha_x + 50} {ym - 50} L{falha_x - 50} {ym + 50}"/></g>"""
    html = (tit(f"{p}-t1", "EPISÓDIOS", "left:0;right:0;text-align:center;top:120px", 120, "#eef1f7") +
            tit(f"{p}-t2", "O EFEITO É PEQUENO", "left:0;right:0;text-align:center;top:140px", 64, "#c9b8ff", True) +
            tit(f"{p}-t3", "LEMBRAR É ABRIR UM CAMINHO", "left:0;right:0;text-align:center;top:110px", 104, "#bff4ff") +
            tit(f"{p}-t4", "E O CAMINHO PODE FALHAR", "left:0;right:0;text-align:center;top:800px", 80, "#ff9bb0", True))
    js = cam(p, (1.5, 360, 520), [
        (t_cer + 0.3, 1.7, (1.0, 960, 540), "power3.inOut"),
        (t_epi + 0.3, t_peq - t_epi - 0.5, (1.04, 940, 540), "sine.inOut"),
        (t_peq - 0.2, 1.4, (0.95, 960, 540), "power3.inOut"),
        (t_lemb - 0.4, 1.4, (1.0, 960, 560), "power3.inOut"),
        (t_abrir, dur - t_abrir, (1.03, 960, 550), "sine.inOut")])
    js += f"""
  tl.fromTo("#{p}-cer",{{opacity:0.95}},{{opacity:0.5,duration:0.4,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_cer:.2f});
  tl.fromTo("#{p}-ep0,#{p}-ep1,#{p}-ep2,#{p}-ep3",{{opacity:0,scale:0.5,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.7,ease:"elastic.out(1,0.55)",stagger:0.22}},{t_cer + 0.7:.2f});
  rise("#{p}-t1 span", {t_epi:.2f}, 0.8);
  some("#{p}-t1", {t_efe - 0.2:.2f}, 0.3);
  tl.fromTo("#{p}-pt0,#{p}-pt1,#{p}-pt2",{{opacity:0,y:-320}},{{opacity:1,y:0,duration:0.55,ease:"bounce.out",stagger:0.18}},{t_porta - 0.1:.2f});
  tl.fromTo("#{p}-ep0",{{opacity:1}},{{opacity:0.45,duration:0.6,immediateRender:false}},{t_fim:.2f});
  rise("#{p}-t2 span", {t_efe:.2f});
  tl.fromTo("#{p}-pt1",{{opacity:1}},{{opacity:0.25,duration:0.12,repeat:5,yoyo:true,ease:"none",immediateRender:false}},{t_nem:.2f});
  some("#{p}-t2", {t_lemb - 0.4:.2f}, 0.3);
  tl.fromTo("#{p}-ep0",{{opacity:0.45}},{{opacity:1,duration:0.6,immediateRender:false}},{t_lemb:.2f});
  rise("#{p}-t3 span", {t_lemb:.2f}, 0.8);
  tl.fromTo("#{p}-cam1",{{attr:{{"stroke-dashoffset":2400}}}},{{attr:{{"stroke-dashoffset":1180}},duration:{t_cam - t_lemb:.2f},ease:"power1.inOut"}},{t_lemb:.2f});
  tl.fromTo("#{p}-pf0,#{p}-pf1",{{scaleX:1,transformOrigin:"0% 50%"}},{{scaleX:0.1,transformOrigin:"0% 50%",duration:0.35,stagger:0.45}},{t_abrir:.2f});
  tl.fromTo("#{p}-cam1",{{attr:{{"stroke-dashoffset":1180}}}},{{attr:{{"stroke-dashoffset":620}},duration:1.0,ease:"power1.in",immediateRender:false}},{t_cam:.2f});
  tl.fromTo("#{p}-cam1",{{stroke:"#bff4ff"}},{{stroke:"#ff4f7d",duration:0.2,immediateRender:false}},{t_falh:.2f});
  pop("#{p}-x", {t_falh:.2f}, 0.3, 0.6);
  tl.fromTo("#{p}-pt2",{{x:-6}},{{x:6,duration:0.05,repeat:9,yoyo:true,ease:"none",immediateRender:false}},{t_falh:.2f});
  some("#{p}-t3", {t_pode - 0.5:.2f}, 0.3);
  rise("#{p}-t4 span", {t_pode - 0.6:.2f}, 0.7);
  tl.fromTo("#{p}-olho",{{x:0}},{{x:3,duration:0.4}},{t_epi:.2f});
""" + vida_pessoa(p, dur, (2.0, 6.2, 9.9, 13.2, 16.6))
    return comp(p, dur, svg, html, js)


# ================================================================ 3 trauma: quarto à noite, a pessoa não lembra, mas o corpo reage
# A cama, o abajur, a xícara, o rádio e a janela estão na cena desde o começo; cada um vira o gatilho na sua palavra.
def trancada_3():
    p = "trancada_3"
    ini, dur = seg(CE, 3)
    t = T(3)
    (t_ser, t_viol, t_pode, t_lemb, t_corpo, t_che, t_som, t_lug, t_volta, t_sem) = (
        t("sério"), t("violência"), t("pode"), t("lembrar"), t("corpo"), t("cheiro"), t("som"), t("lugar"), t("volta"), t("sem"))
    g = p + "-g"
    PX, S = 470, .95
    hx, hy = PX + S * anc("sentado")["cabeca_centro"][0], 900 + S * anc("sentado")["cabeca_centro"][1]  # centro da cabeça
    w0, d0 = comodo(p, 0, -700, 2700, "#2c2266", "#120e34", piso="#1a1230", rodape="#4a3a7a")
    cama = ('<rect x="230" y="560" width="34" height="340" rx="12" fill="#4a2e6a" stroke="#8d7bff" stroke-width="4"/>'
            '<rect x="240" y="800" width="420" height="52" rx="10" fill="#4a2e6a"/><rect x="250" y="852" width="20" height="48" fill="#2a1a40"/><rect x="630" y="852" width="20" height="48" fill="#2a1a40"/>'
            '<rect x="252" y="742" width="400" height="62" rx="18" fill="#d9d0ff"/><ellipse cx="318" cy="730" rx="54" ry="24" fill="#f4f0ff"/>'
            '<path d="M340 736 Q 480 724 652 744 L 652 812 Q 480 822 340 810 Z" fill="#5a4ab0"/><path d="M360 760 Q 500 750 640 768" stroke="#8d7bff" stroke-width="4" fill="none" opacity=".6"/>')
    mesinha = (mesa(980, 1160, 720, cor="#5a3a5a", perna="#3a2440") + abajur(1030, 720)
               + '<rect x="1092" y="684" width="38" height="36" rx="6" fill="#fffaf0"/><path d="M1130 692 q12 0 10 12 q-2 8 -10 6" stroke="#fffaf0" stroke-width="5" fill="none"/>'
               + f'<g id="{p}-vap" opacity=".45" fill="none" stroke="#e8e0ff" stroke-width="5" stroke-linecap="round"><path d="M1102 676 q-10 -18 0 -34 q10 -16 0 -32"/><path d="M1120 676 q-10 -18 0 -34 q10 -16 0 -32"/></g>')
    comoda = ('<rect x="1230" y="640" width="290" height="260" rx="10" fill="#3a2a5a" stroke="#6a5ab0" stroke-width="4"/>'
              + "".join(f'<rect x="1250" y="{y}" width="250" height="68" rx="6" fill="none" stroke="#6a5ab0" stroke-width="4"/><circle cx="1375" cy="{y + 34}" r="7" fill="#c9b8ff"/>' for y in (662, 742, 822))
              + '<rect x="1300" y="548" width="150" height="92" rx="14" fill="#c96a4a"/><circle cx="1340" cy="594" r="26" fill="#3a1a1a"/><circle cx="1340" cy="594" r="12" fill="#6a3a2a"/>'
              + '<rect x="1384" y="570" width="50" height="14" rx="4" fill="#ffd27a"/><rect x="1384" y="600" width="50" height="10" rx="4" fill="#3a1a1a"/><path d="M1420 548 L1460 488" stroke="#c9cce8" stroke-width="5" stroke-linecap="round"/>'
              + f'<g id="{p}-ondas" opacity="0" fill="none" stroke="{MAGENTA}" stroke-width="7" stroke-linecap="round"><path d="M1470 566 q16 28 0 56"/><path d="M1492 548 q26 46 0 92"/><path d="M1514 530 q36 64 0 128"/></g>')
    jan = (janela(1590, 220, 260, 300, ceu=("#0a0f30", "#1a1a50"), cortina="#6a5ab0")
           + f'<g id="{p}-jan" opacity="0"><rect x="1590" y="220" width="260" height="300" fill="{MAGENTA}" opacity=".5"/>'
           + '<path d="M1640 520 V330 M1620 330 H1670" stroke="#1a0820" stroke-width="10"/><rect x="1700" y="390" width="120" height="130" fill="#1a0820"/></g>')
    quadros = (G.quadro(f"{p}-q0", "praia", 250, 390, .8) + f'<g transform="translate(250 390) scale(1.6)"><g id="{p}-qe" opacity="0">{quadro_escuro()}</g></g>')
    objs = [(1110, 650), (1375, 594), (1720, 370)]       # xícara, rádio, janela
    labs = [("UM CHEIRO", t_che, 1070), ("UM SOM", t_som, 1375), ("UM LUGAR", t_lug, 1720)]
    halos = "".join(f'<circle id="{p}-h{i}" cx="{x}" cy="{y}" r="110" fill="{MAGENTA}" opacity="0" filter="url(#{p}-blur6)"/>' for i, (x, y) in enumerate(objs))
    linhas = "".join(f'<path id="{p}-l{i}" d="M{x} {y} C {x - 200} {y - 160} {hx + 260:.0f} {hy - 160:.0f} {hx + 40:.0f} {hy:.0f}" fill="none" stroke="{MAGENTA}" stroke-width="7" stroke-dasharray="40 1400" stroke-dashoffset="40" opacity="0" filter="url(#{p}-glow)"/>' for i, (x, y) in enumerate(objs))
    ecg = "M-200 1035 " + " ".join("h140 l14 -50 l18 100 l14 -70 l10 20" for _ in range(16))
    raios = "".join(f'<g transform="translate({hx + dx:.0f} {hy + dy:.0f}) rotate({r})">{bolt(0, 0, 1.0, VERM)}</g>' for dx, dy, r in [(-150, -60, -20), (150, -90, 25), (10, -190, 0)])
    gotas = "".join(gota(hx + dx, hy + dy, 1.2) for dx, dy in [(-50, -40), (62, -10), (-20, 30)])
    bol = f'<g id="{p}-orbW" opacity="0">{orbe(p, 0, VERM, 40)}</g><g transform="scale(.55)"><g id="{p}-cadW" opacity="0">{cadeado(p, 0)}</g></g>'
    extra = (f'<radialGradient id="{p}-vr" cx="50%" cy="50%" r="70%"><stop offset=".35" stop-color="#ff1f5a" stop-opacity="0"/><stop offset="1" stop-color="#ff1f5a" stop-opacity="1"/></radialGradient>'
             f'<radialGradient id="{p}-mr"><stop offset="0" stop-color="#ff4f7d" stop-opacity=".8"/><stop offset="1" stop-color="#ff4f7d" stop-opacity="0"/></radialGradient>')
    svg = f"""{w0}{quadros}{jan}{comoda}{mesinha}{cama}{halos}
<circle id="{p}-medo" cx="{hx:.0f}" cy="{hy + 60:.0f}" r="300" fill="url(#{p}-mr)" opacity="0"/>
<g id="{p}-raios" opacity="0">{raios}</g>
<g transform="translate({PX} 900) scale({S})"><g id="{p}-tre">{humano(p, "casa", "sentado", cadeira=False, caneca=False)}{bolha_h(p, 0, bol, sentado=True)}</g></g>
<g id="{p}-gotas" opacity="0">{gotas}</g>
{linhas}
<path id="{p}-ecg" d="{ecg}" fill="none" stroke="{VERM}" stroke-width="6" stroke-linejoin="round" stroke-dasharray="12000" stroke-dashoffset="12000" filter="url(#{p}-glow)"/>
<rect id="{p}-fl" x="-400" y="-400" width="2720" height="1880" fill="#ff2a63" opacity="0"/>
<rect id="{p}-vm" x="-400" y="-400" width="2720" height="1880" fill="url(#{p}-vr)" opacity="0"/>"""
    html = (tit(f"{p}-t0", "PODE NÃO CONSEGUIR LEMBRAR", "left:0;right:0;text-align:center;top:60px", 64, "#eef1f7", True) +
            tit(f"{p}-t1", "O CORPO REAGE", "left:0;right:0;text-align:center;top:36px", 110, "#ff9bb0") +
            "".join(tit(f"{p}-n{i}", nome, f"left:{x - 160}px;width:320px;text-align:center;top:908px", 52, "#ffd2e6", True) for i, (nome, _, x) in enumerate(labs)) +
            tit(f"{p}-t2", "SEM AVISO", "left:1010px;top:236px", 84, "#ff4f7d", True))
    js = cam(p, (1.0, 960, 540), [
        (1.0, 1.8, (1.25, 700, 505), "power3.inOut"),
        (t_viol + 0.2, 2.2, (1.28, 710, 505), "power3.inOut"),
        (t_corpo - 0.6, 1.4, (1.0, 960, 540), "power3.inOut"),
        (t_volta - 0.1, 0.2, (1.03, 960, 540), "power4.out"),
        (t_volta + 0.1, 0.8, (1.0, 960, 540), "power2.out")])
    js += f"""
  pop("#{p}-bol0", 0.4, 0.3, 0.8);
  entra("#{p}-orbW", 0.6, 0.5);
  tl.fromTo("#{p}-orbW",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.2,duration:0.5,repeat:3,yoyo:true,ease:"sine.inOut"}},0.6);
  tl.fromTo("#{p}-vap",{{y:0}},{{y:-10,duration:1.2,repeat:{int(dur / 1.2)},yoyo:true,ease:"sine.inOut"}},0);
  tl.fromTo("#{p}-fl",{{opacity:0}},{{opacity:0.5,duration:0.06}},{t_viol:.2f});
  tl.fromTo("#{p}-fl",{{opacity:0.5}},{{opacity:0,duration:0.5,immediateRender:false}},{t_viol + 0.06:.2f});
  entra("#{p}-raios", {t_viol:.2f}, 0.05); some("#{p}-raios", {t_viol + 0.6:.2f}, 0.3);
  tl.fromTo("#{p}-tre",{{x:-4}},{{x:4,duration:0.05,repeat:9,yoyo:true,ease:"none"}},{t_viol:.2f});
  tl.fromTo("#{g}-cab",{{rotation:0,svgOrigin:"{pescoco("sentado")}"}},{{rotation:-6,svgOrigin:"{pescoco("sentado")}",duration:0.3,ease:"back.out(2)"}},{t_viol:.2f});
  rise("#{p}-t0 span", {t_pode:.2f});
  pop("#{p}-cadW", {t_lemb - 0.2:.2f}, 2.2, 0.6);
  tl.fromTo("#{p}-orbW",{{opacity:1}},{{opacity:0,duration:0.4,immediateRender:false}},{t_lemb:.2f});
  entra("#{p}-qe", {t_lemb:.2f}, 0.6);
  tl.fromTo("#{g}-olho",{{x:0}},{{x:-3,duration:0.3,repeat:3,yoyo:true}},{t_lemb + 0.6:.2f});
  some("#{p}-t0", {t_corpo - 0.6:.2f}, 0.3);
  rise("#{p}-t1 span", {t_corpo - 0.1:.2f}, 0.8);
  entra("#{p}-gotas", {t_corpo:.2f}, 0.4);
  tl.fromTo("#{p}-gotas",{{y:0}},{{y:16,duration:1.4,repeat:{int((dur - t_corpo) / 1.4)},ease:"power1.in"}},{t_corpo:.2f});
  tl.fromTo("#{p}-ecg",{{attr:{{"stroke-dashoffset":12000}}}},{{attr:{{"stroke-dashoffset":2200}},duration:{dur - t_corpo:.2f},ease:"none"}},{t_corpo - 0.2:.2f});
  tl.fromTo("#{p}-tre",{{x:-2}},{{x:2,duration:0.06,repeat:{int((dur - t_corpo) / 0.06) - 2},yoyo:true,ease:"none",immediateRender:false}},{t_corpo + 0.1:.2f});
  tl.fromTo("#{p}-ondas path",{{opacity:0.2}},{{opacity:1,duration:0.15,stagger:0.08,repeat:5,yoyo:true,immediateRender:false}},{t_som:.2f});
  entra("#{p}-ondas", {t_som:.2f}, 0.05);
  tl.fromTo("#{p}-vap",{{opacity:0.45,attr:{{stroke:"#e8e0ff"}}}},{{opacity:1,attr:{{stroke:"#ff4fa3"}},duration:0.3,immediateRender:false}},{t_che:.2f});
  tl.fromTo("#{p}-jan",{{opacity:0}},{{opacity:1,duration:0.12,repeat:3,yoyo:true,ease:"none"}},{t_lug:.2f});
  tl.fromTo("#{p}-jan",{{opacity:0}},{{opacity:0.8,duration:0.3,immediateRender:false}},{t_lug + 0.6:.2f});
""" + "".join(f"""
  tl.fromTo("#{p}-h{i}",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:0.55,scale:1,transformOrigin:"50% 50%",duration:0.5,ease:"power3.out"}},{tt - 0.05:.2f});
  rise("#{p}-n{i} span", {tt:.2f}, 0.6);
  tl.fromTo("#{p}-l{i}",{{opacity:1,attr:{{"stroke-dashoffset":40}}}},{{opacity:1,attr:{{"stroke-dashoffset":-1300}},duration:0.7,ease:"power1.in"}},{tt + 0.15:.2f});
  tl.fromTo("#{p}-l{i}",{{opacity:1}},{{opacity:0,duration:0.1,immediateRender:false}},{tt + 0.85:.2f});
  tl.fromTo("#{p}-cadW",{{rotation:-9,transformOrigin:"50% 50%"}},{{rotation:9,duration:0.07,repeat:5,yoyo:true,ease:"none",immediateRender:false}},{tt + 0.8:.2f});""" for i, (_, tt, _x) in enumerate(labs)) + f"""
  tl.fromTo("#{p}-medo",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:1,scale:1.15,transformOrigin:"50% 50%",duration:0.5,ease:"power4.out"}},{t_volta:.2f});
  tl.fromTo("#{p}-vm",{{opacity:0}},{{opacity:0.85,duration:0.5,ease:"power2.out"}},{t_volta:.2f});
  tl.fromTo("#{p}-medo",{{scale:1.15}},{{scale:0.95,duration:0.4,repeat:{int((dur - t_volta - 0.5) / 0.4)},yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_volta + 0.5:.2f});
  rise("#{p}-t2 span", {t_sem:.2f}, 0.6);
""" + vida_h(p, dur, (1.2, 3.4, 8.6, 12.9))
    return comp(p, dur, svg, html, js, d0 + extra, fundo=("#3a1238", "#1c0a30", "#0a0614"), seed=21)


# ================================================================ 5 frase: não tinha sido apagada, só estava sem acesso
def trancada_5():
    p = "trancada_5"
    ini, dur = seg(CE, 5)
    t = T(5)
    t_tinha, t_apag, t_so, t_sem = t("tinha"), t("apagada"), t("Só"), t("sem")
    X, Y, W, H = 770, 210, 380, 620
    luz = (f'<rect x="{X}" y="{Y}" width="{W}" height="{H}" fill="#ffd27a"/>')
    porta = porta_frente(p, 0, X, Y, W, H).replace("@VAO0@", luz)
    frestas = (f'<g id="{p}-fresta" opacity=".35" filter="url(#{p}-glow)"><rect x="{X - 4}" y="{Y}" width="8" height="{H}" fill="#ffd27a"/>'
               f'<rect x="{X + W - 4}" y="{Y}" width="8" height="{H}" fill="#ffd27a"/><rect x="{X}" y="{Y + H - 6}" width="{W}" height="10" fill="#ffd27a"/></g>'
               f'<polygon id="{p}-feixe" points="{X},{Y + H} {X + W},{Y + H} {X + W + 260},1080 {X - 260},1080" fill="url(#{p}-fx)" opacity=".3"/>')
    passo = (W + 52) / 9
    corrente = (f'<g id="{p}-corr"><rect x="{X - 44}" y="{Y + H * .5 - 40:.0f}" width="26" height="80" rx="6" fill="#9aa0c8" stroke="#eef1f7" stroke-width="3"/>'
                f'<rect x="{X + W + 18}" y="{Y + H * .5 - 40:.0f}" width="26" height="80" rx="6" fill="#9aa0c8" stroke="#eef1f7" stroke-width="3"/>'
                f'<g fill="none" stroke="#c9cce8" stroke-width="14">' +
                "".join(f'<ellipse cx="{X - 26 + i * passo:.0f}" cy="{Y + H * .5:.0f}" rx="{passo * .62:.0f}" ry="15"/>' for i in range(10)) + '</g></g>')
    svg = f"""{parede(p, 860)}
{frestas}
{porta}
<g transform="translate({X + W / 2 + 1} {Y + H * .5 + 60})"><g id="{p}-cadW" opacity="0"><g transform="scale(1.4)">{cadeado(p, 0)}</g></g></g>
{corrente}"""
    extra = defs_parede(p) + f'<linearGradient id="{p}-fx" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd27a" stop-opacity=".8"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></linearGradient>'
    html = (tit(f"{p}-t1", "NÃO TINHA SIDO APAGADA", "left:0;right:0;text-align:center;top:40px", 92, "#ffd98a") +
            tit(f"{p}-t2", "SÓ ESTAVA SEM ACESSO", "left:0;right:0;text-align:center;top:920px", 92, "#bff4ff"))
    js = cam(p, (1.0, 960, 540), [(0, dur, (1.12, 960, 520), "sine.inOut")])
    js += f"""
  rise("#{p}-t1 span", {t_tinha:.2f}, 0.8);
  tl.fromTo("#{p}-fl0",{{scaleX:1,transformOrigin:"0% 50%"}},{{scaleX:0.82,transformOrigin:"0% 50%",duration:0.5,ease:"power2.out"}},{t_apag - 0.2:.2f});
  tl.fromTo("#{p}-fresta",{{opacity:0.35}},{{opacity:1,duration:0.5}},{t_apag - 0.2:.2f});
  tl.fromTo("#{p}-feixe",{{opacity:0.3}},{{opacity:1,duration:0.6}},{t_apag - 0.2:.2f});
  tl.fromTo("#{p}-fl0",{{scaleX:0.82}},{{scaleX:1,transformOrigin:"0% 50%",duration:0.2,ease:"power4.in",immediateRender:false}},{t_so - 0.1:.2f});
  tl.fromTo("#{p}-fresta",{{opacity:1}},{{opacity:0.6,duration:0.3,immediateRender:false}},{t_so:.2f});
  tl.fromTo("#{p}-feixe",{{opacity:1}},{{opacity:0.45,duration:0.3,immediateRender:false}},{t_so:.2f});
  tl.fromTo("#{p}-corr ellipse, #{p}-corr rect",{{opacity:0,y:-60}},{{opacity:1,y:0,duration:0.25,stagger:0.04,ease:"power2.out"}},{t_so + 0.1:.2f});
  tl.fromTo("#{p}-cadW",{{opacity:0,y:-500}},{{opacity:1,y:0,duration:0.55,ease:"bounce.out"}},{t_sem - 0.45:.2f});
  rise("#{p}-t2 span", {t_sem:.2f}, 0.8);
  tl.fromTo("#{p}-fresta",{{opacity:0.6}},{{opacity:0.95,duration:0.9,repeat:2,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_sem + 0.3:.2f});
"""
    return comp(p, dur, svg, html, js, extra)


# ================================================================ 6 remédio: consultório, a paciente toma o propranolol antes de relembrar
def trancada_6():
    p = "trancada_6"
    ini, dur = seg(CE, 6)
    t = T(6)
    (t_mexer, t_pess, t_pac, t_estr, t_rem, t_prop, t_rel, t_trau, t_dim, t_carga, t_emo) = (
        t("mexer"), t("pessoas"), t("pacientes"), t("estresse"), t("remédio"), t("propranolol"), t("relembrar"), t("trauma"), t("diminuir"), t("carga"), t("emocional"))
    g = p + "-g"
    PX, S = 600, 1.0
    bx, by = PX + S * bol_xy("sentado")[0], 900 + S * bol_xy("sentado")[1]          # centro do balão
    cc = anc("sentado")["cabeca_centro"]
    mx, my = PX + S * (cc[0] + 22), 900 + S * (cc[1] + 30)          # boca
    w0, d0 = comodo(p, 0, -700, 2700, "#1f4a6a", "#12284a", piso="#14223a", rodape="#3a7a9a")
    sala = (G.quadro(f"{p}-q0", "formatura", 220, 330, .7, moldura="#c9a24a") + G.quadro(f"{p}-q1", "praia", 220, 560, .55)
            + G.quadro(f"{p}-q2", "premio", 1300, 215, .5, moldura="#c9a24a") + G.quadro(f"{p}-q3", "cafe", 1520, 215, .5)
            + '<circle cx="1760" cy="200" r="54" fill="#eef1f7" stroke="#9aa6c0" stroke-width="8"/><path d="M1760 168 V200 L1784 214" stroke="#14223a" stroke-width="7" fill="none" stroke-linecap="round"/>'
            + planta(1070, s=.8) + poltrona(PX, 900, 1.0, "#3a8a9a", "#2a6a7a")
            + mesa(1180, 1640, 720, cor="#8a6a4a", perna="#5a4232")
            + '<rect x="1230" y="700" width="120" height="20" rx="3" fill="#fffaf0" transform="rotate(-4 1290 710)"/><path d="M1240 706 H1330" stroke="#9aa6c0" stroke-width="3" transform="rotate(-4 1290 710)"/>'
            + '<rect x="1430" y="640" width="52" height="80" rx="6" fill="#bff4ff" opacity=".45" stroke="#eef1f7" stroke-width="3"/><rect x="1434" y="676" width="44" height="40" rx="4" fill="#3be0ff" opacity=".35"/>'
            + '<rect x="1540" y="670" width="44" height="50" rx="6" fill="#ff8a6a"/><path d="M1550 670 L1546 630 M1562 670 L1566 626 M1574 670 L1584 634" stroke="#eef1f7" stroke-width="4" stroke-linecap="round"/>')
    pil0 = (1430, 380, 1.0)
    tr_p, js_p = mov(f"#{p}-pilW", pil0, [(t_rel - 0.4, 0.9, (mx, my, 0.12), "power2.in")])
    ch0 = (bx - 330, by - 200, 0.5, -30)
    tr_c, js_c = mov(f"#{p}-chW", ch0, [(t_mexer - 0.3, 0.9, (bx - 120, by + 13, 0.5, 0), "power3.out")])
    medidor = (f'<g id="{p}-med" opacity="0"><rect x="1700" y="300" width="90" height="500" rx="45" fill="#140f3a" stroke="{LILAS}" stroke-width="5"/>'
               f'<g transform="translate(1745 790)"><g id="{p}-nivel"><rect x="-33" y="-470" width="66" height="470" rx="33" fill="url(#{p}-cg)"/></g></g></g>')
    bol = (f'<g id="{p}-orbW" opacity="0"><g id="{p}-orbR">{orbe(p, 0, VERM, 40)}</g><g id="{p}-orbC" opacity="0">{orbe(p, 1, LILAS, 40)}</g></g>'
           f'<g transform="translate(0 4) scale(.5)"><g id="{p}-cadW">{cadeado(p, 0)}</g></g>')
    svg = f"""{w0}{sala}
<g transform="translate({PX} 900) scale({S})"><g id="{p}-tre">{humano(p, "casa", "sentado", cadeira=False)}{bolha_h(p, 0, bol, sentado=True)}</g></g>
<g id="{p}-chW" transform="{tr_c}"><g id="{p}-ch" opacity="0">{chave("#d9dcf0")}</g></g>
<path id="{p}-traj" d="M{pil0[0] - 150} {pil0[1] + 20} C {pil0[0] - 420} {pil0[1] - 180} {mx + 300:.0f} {my - 260:.0f} {mx + 40:.0f} {my - 10:.0f}" fill="none" stroke="{AMBAR}" stroke-width="7" stroke-linecap="round" stroke-dasharray="4 26" opacity="0" filter="url(#{p}-glow)"/>
<g id="{p}-pilW" transform="{tr_p}"><g id="{p}-pil" opacity="0"><rect x="-190" y="-80" width="380" height="160" fill="none" opacity="0"/>
 <g filter="url(#{p}-sombra)"><path d="M0 -70 L-110 -70 A70 70 0 0 0 -110 70 L0 70 Z" fill="#fffaf0"/><path d="M0 -70 L110 -70 A70 70 0 0 1 110 70 L0 70 Z" fill="{AMBAR}"/></g>
 <rect x="-150" y="-52" width="250" height="22" rx="11" fill="#fff" opacity=".5"/></g></g>
{medidor}"""
    extra = d0 + f'<linearGradient id="{p}-cg" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{AMBAR}"/><stop offset="1" stop-color="{VERM}"/></linearGradient>'
    html = (tit(f"{p}-t1", "ESTRESSE PÓS-TRAUMÁTICO", "left:0;right:0;text-align:center;top:60px", 72, "#ff9bb0", True) +
            tit(f"{p}-t2", "PROPRANOLOL", "left:1000px;right:60px;text-align:center;top:470px", 110, "#ffd98a") +
            tit(f"{p}-t4", "RELEMBRAR O TRAUMA", "left:1000px;right:60px;text-align:center;top:480px", 60, "#ff9bb0", True) +
            tit(f"{p}-t3", "CARGA EMOCIONAL", "right:250px;top:920px;text-align:right", 72, "#c9b8ff", True))
    js = cam(p, (1.0, 960, 540), [
        (0.8, 1.6, (1.45, bx - 60, by + 80), "power3.inOut"),
        (t_pac - 0.5, 1.4, (1.0, 960, 540), "power3.inOut"),
        (t_rem - 0.3, 1.3, (1.06, 1100, 520), "power3.inOut"),
        (t_rel - 0.5, 1.5, (1.25, 860, 495), "power3.inOut"),
        (t_dim - 0.4, dur - t_dim + 0.4, (1.0, 1000, 540), "sine.inOut")])
    js += js_p + js_c + f"""
  pop("#{p}-bol0", 0.3, 0.3, 0.8);
  entra("#{p}-orbW", {t_rel + 0.3:.2f}, 0.4);
  entra("#{p}-ch", {t_mexer - 0.3:.2f}, 0.4);
  tl.fromTo("#{p}-ch",{{rotation:0,transformOrigin:"0% 50%"}},{{rotation:14,transformOrigin:"0% 50%",duration:0.18,repeat:5,yoyo:true,ease:"sine.inOut"}},{t_mexer + 0.7:.2f});
  tl.fromTo("#{p}-cadW",{{rotation:-6,transformOrigin:"50% 50%"}},{{rotation:6,duration:0.09,repeat:7,yoyo:true,ease:"none"}},{t_mexer + 0.7:.2f});
  some("#{p}-ch", {t_pess + 0.6:.2f}, 0.4);
  tl.fromTo("#{g}-olho",{{x:0}},{{x:-2,duration:0.3}},{t_mexer:.2f});
  rise("#{p}-t1 span", {t_estr - 0.2:.2f}, 0.8);
  tl.fromTo("#{p}-tre",{{x:-3}},{{x:3,duration:0.05,repeat:15,yoyo:true,ease:"none"}},{t_estr + 0.3:.2f});
  some("#{p}-t1", {t_rem - 0.5:.2f}, 0.3);
  pop("#{p}-pil", {t_rem:.2f}, 0.2, 0.9);
  tl.fromTo("#{p}-pil",{{rotation:-12,transformOrigin:"50% 50%"}},{{rotation:12,duration:0.8,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_rem + 0.8:.2f});
  tl.fromTo("#{g}-olho",{{x:-2}},{{x:3,duration:0.4,immediateRender:false}},{t_rem:.2f});
  rise("#{p}-t2 span", {t_prop:.2f}, 0.8);
  some("#{p}-t2", {t_rel - 0.4:.2f}, 0.3);
  tl.fromTo("#{g}-cab",{{rotation:0,svgOrigin:"{pescoco("sentado")}"}},{{rotation:-7,svgOrigin:"{pescoco("sentado")}",duration:0.3,repeat:1,yoyo:true,repeatDelay:0.2,ease:"power2.out"}},{t_rel + 0.4:.2f});
  tl.fromTo("#{p}-pil",{{opacity:1}},{{opacity:0,duration:0.15,immediateRender:false}},{t_rel + 0.45:.2f});
  tl.fromTo("#{p}-arg0",{{y:0}},{{y:-30,duration:0.35,ease:"back.out(3)"}},{t_rel:.2f});
  tl.fromTo("#{p}-cadW",{{opacity:1}},{{opacity:0,duration:0.3,immediateRender:false}},{t_rel + 0.4:.2f});
  tl.fromTo("#{p}-orbR",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.5,duration:0.35,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_trau + 0.1:.2f});
  tl.fromTo("#{p}-orbR",{{opacity:1}},{{opacity:0,duration:1.2,immediateRender:false}},{t_dim:.2f});
  tl.fromTo("#{p}-orbC",{{opacity:0,scale:1.4,transformOrigin:"50% 50%"}},{{opacity:1,scale:0.8,transformOrigin:"50% 50%",duration:1.4,ease:"power2.inOut"}},{t_dim:.2f});
  tl.fromTo("#{p}-med",{{opacity:0,x:120}},{{opacity:1,x:0,duration:0.7,ease:"expo.out"}},{t_dim - 0.2:.2f});
  entra("#{p}-traj", {t_rem + 0.2:.2f}, 0.5); some("#{p}-traj", {t_rel - 0.1:.2f}, 0.3);
  tl.fromTo("#{p}-traj",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-120}},duration:{t_rel - t_rem:.2f},ease:"none"}},{t_rem + 0.2:.2f});
  rise("#{p}-t4 span", {t_rel + 0.3:.2f}, 0.7); some("#{p}-t4", {t_dim - 0.3:.2f}, 0.3);
  tl.fromTo("#{p}-nivel",{{scaleY:1,transformOrigin:"50% 100%"}},{{scaleY:0.32,transformOrigin:"50% 100%",duration:2.0,ease:"power2.inOut"}},{t_dim:.2f});
  rise("#{p}-t3 span", {t_carga:.2f}, 0.8);
""" + vida_h(p, dur, (3.0, 5.2, 9.6, 13.4, 17.8))
    return comp(p, dur, svg, html, js, extra, seed=5)


# ================================================================ 7 placar: 2018 positivo, 2015 não repetiu, ciência discutindo
def trancada_7():
    p = "trancada_7"
    ini, dur = seg(CE, 7)
    t = T(7)
    t_2018, t_pos, t_outro, t_2015, t_nao, t_rep, t_ant, t_cien = t("2018"), t("positivo"), t("Outro"), t("2015"), t("não"), t("repetir"), t("anterior"), t("ciência")
    PX, PY, L = 960, 300, 500

    def prato(k, ano, sim):
        marca = (f'<g id="{p}-mk{k}" opacity="0"><circle cx="240" cy="-180" r="44" fill="{MENTA if sim else VERM}"/>'
                 + (f'<path d="M218 -180 L234 -164 L264 -196" fill="none" stroke="#08261c" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>' if sim else
                    f'<path d="M222 -198 L258 -162 M258 -198 L222 -162" stroke="#3a0818" stroke-width="12" stroke-linecap="round"/>') + '</g>')
        rot = ("RESULTADO POSITIVO" if sim else "NÃO CONSEGUIU REPETIR")
        return (f'<g id="{p}-pr{k}" transform="translate({PX + (-L if k == 0 else L)} {PY})">'
                f'<path d="M0 0 L-300 300 M0 0 L300 300" stroke="#c9cce8" stroke-width="5"/>'
                f'<path d="M-330 300 L330 300 Q 300 350 0 352 Q -300 350 -330 300 Z" fill="#8d7bff" stroke="#c9b8ff" stroke-width="5"/>'
                f'<g id="{p}-cd{k}" opacity="0"><g filter="url(#{p}-sombra)"><rect x="-310" y="80" width="620" height="218" rx="20" fill="#16123e" stroke="{MENTA if sim else VERM}" stroke-width="6"/></g>'
                f'<text id="{p}-ano{k}" x="0" y="200" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="120" fill="#fffaf0">{ano}</text>'
                f'<text x="0" y="268" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="44" fill="{MENTA if sim else "#ff9bb0"}" id="{p}-rt{k}" opacity="0">{rot}</text>'
                f'<g transform="translate(0 290)">{marca}</g></g></g>')
    svg = f"""<ellipse cx="{PX}" cy="905" rx="300" ry="24" fill="#05031a" opacity=".5"/>
<path d="M{PX - 150} 900 L{PX + 150} 900 L{PX + 90} 860 L{PX - 90} 860 Z" fill="#3a2f9a" stroke="{LILAS}" stroke-width="5"/>
<rect x="{PX - 18}" y="{PY}" width="36" height="566" fill="#2a2068" stroke="{LILAS}" stroke-width="5"/>
<g id="{p}-trave" transform="rotate(0 {PX} {PY})"><rect x="{PX - L - 20}" y="{PY - 14}" width="{2 * L + 40}" height="28" rx="14" fill="#c9b8ff" stroke="#fff" stroke-width="3"/>
 <circle cx="{PX - L}" cy="{PY}" r="14" fill="{AMBAR}"/><circle cx="{PX + L}" cy="{PY}" r="14" fill="{AMBAR}"/></g>
<circle cx="{PX}" cy="{PY}" r="34" fill="{AMBAR}" filter="url(#{p}-glow)"/>
{prato(0, "2018", True)}{prato(1, "2015", False)}"""
    html = tit(f"{p}-t1", "A CIÊNCIA AINDA ESTÁ DISCUTINDO", "left:0;right:0;text-align:center;top:70px", 92, "#eef1f7")
    # balança: ângulo da trave em graus; pratos penduram nas pontas (só posição, sempre na vertical)
    bal = f"""
  function bal(a){{var r=a*Math.PI/180,c=Math.cos(r),s=Math.sin(r);
    _el("#{p}-trave").setAttribute("transform","rotate("+a.toFixed(3)+" {PX} {PY})");
    _el("#{p}-pr0").setAttribute("transform","translate("+({PX}-{L}*c).toFixed(2)+" "+({PY}-{L}*s).toFixed(2)+")");
    _el("#{p}-pr1").setAttribute("transform","translate("+({PX}+{L}*c).toFixed(2)+" "+({PY}+{L}*s).toFixed(2)+")");}}
  function balK(t0,d,a0,a1,ease){{var o={{a:a0}};tl.fromTo(o,{{a:a0}},{{a:a1,duration:d,ease:ease||"power2.inOut",immediateRender:false,onUpdate:function(){{bal(o.a);}}}},t0);}}
  bal(0);"""
    osc = "".join(f'balK({t_cien + 0.2 + i * 0.55:.2f},0.55,{a:.1f},{b:.1f},"sine.inOut");' for i, (a, b) in enumerate([(7, -6), (-6, 5), (5, -4), (-4, 3), (3, -2), (-2, 1)]))
    js = cam(p, (1.0, 960, 520), [
        (0, 1.2, (1.03, 940, 560), "power3.inOut"),
        (t_outro - 0.2, 1.2, (1.03, 980, 560), "power3.inOut"),
        (t_ant - 0.2, 1.3, (0.95, 960, 560), "power3.inOut"),
        (t_ant + 1.1, dur - t_ant - 1.1, (1.0, 960, 540), "sine.inOut")])
    js += bal + f"""
  tl.fromTo("#{p}-cd0",{{opacity:0,y:-500}},{{opacity:1,y:0,duration:0.7,ease:"bounce.out"}},{t_2018 - 0.4:.2f});
  balK({t_2018 + 0.2:.2f},0.8,0,-8,"back.out(2)");
  pop("#{p}-mk0", {t_pos - 0.1:.2f}, 0.2, 0.7);
  entra("#{p}-rt0", {t_pos - 0.6:.2f}, 0.4);
  tl.fromTo("#{p}-cd1",{{opacity:0,y:-500}},{{opacity:1,y:0,duration:0.7,ease:"bounce.out"}},{t_2015 - 0.4:.2f});
  balK({t_2015 + 0.2:.2f},0.8,-8,7,"back.out(2)");
  pop("#{p}-mk1", {t_rep - 0.2:.2f}, 0.2, 0.7);
  entra("#{p}-rt1", {t_nao:.2f}, 0.4);
  {osc}
  rise("#{p}-t1 span", {t_cien:.2f}, 0.9);
"""
    return comp(p, dur, svg, html, js, seed=13)


# ================================================================ 8 quem decide: na rua, de madrugada; a lembrança sai do cadeado e vira o sol
def trancada_8():
    p = "trancada_8"
    ini, dur = seg(CE, 8)
    t = T(8)
    t_sofre, t_lib, t_perg, t_quem, t_qual, t_dem = t("sofre"), t("libertação"), t("pergunta"), t("Quem", 1), t("qual"), t("demais")
    ops = [("O PACIENTE?", t("paciente")), ("O MÉDICO?", t("médico")), ("O EMPREGADOR?", t("empregador")), ("O ESTADO?", t("estado"))]
    g = p + "-g"
    PX, S = 520, .8
    bx, by = PX + S * bol_xy()[0], 900 + S * bol_xy()[1]
    SOL = (1730, 150)
    ys = [330, 450, 570, 690]
    ox, oy = anc("em_pe")["ombro_braco"]
    mxl, myl = anc("em_pe")["mao_e"]
    a_braco = math.degrees(math.atan2(myl - oy, mxl - ox))          # braço pendurado (~85 graus)
    OX, OY = PX + S * ox, 900 + S * oy
    ang = [round(math.degrees(math.atan2(y + 40 - OY, 1300 - OX)) - a_braco, 1) for y in ys]   # rotação do braço por opção
    chave_mao = (f'<g transform="translate({mxl} {myl}) rotate({a_braco:.1f})"><g id="{p}-kW" opacity="0">'
                 f'<g transform="scale(1.06) translate(36 0)">{chave()}</g><rect x="-11" y="-14" width="22" height="28" rx="10" fill="{G.PELE}"/></g></g>')
    ceu = (f'<rect x="-700" y="-700" width="3400" height="1600" fill="url(#{p}-ceu)"/>'
           f'<rect id="{p}-aur" x="-700" y="-700" width="3400" height="1600" fill="url(#{p}-aurg)" opacity="0"/>')
    import random
    rnd = random.Random(8)
    sky = ""
    x = 880
    while x < 2600:
        w, h = rnd.randint(90, 170), rnd.randint(50, 110)
        sky += f'<rect x="{x}" y="{900 - h}" width="{w}" height="{h}" fill="#221a4c"/>'
        sky += "".join(f'<rect x="{x + 14 + k * 28}" y="{900 - h + 18}" width="12" height="14" fill="#ffd27a" opacity=".55"/>' for k in range((w - 20) // 28) if rnd.random() < .5)
        x += w + rnd.randint(6, 30)
    casa = ('<path d="M-420 380 L-60 200 L320 380 Z" fill="#6a3a5a"/><rect x="-400" y="380" width="700" height="520" fill="#5a3a6a"/>'
            '<rect x="20" y="470" width="130" height="130" fill="#ffd27a" opacity=".9"/><path d="M85 470 V600 M20 535 H150" stroke="#5a3a6a" stroke-width="8"/>'
            '<rect x="170" y="690" width="96" height="210" fill="#3a2244" stroke="#c9a2c8" stroke-width="5"/><circle cx="252" cy="800" r="7" fill="#ffb23e"/>'
            '<rect x="-300" y="470" width="130" height="130" fill="#ffd27a" opacity=".6"/>')
    poste = ('<rect x="352" y="360" width="10" height="540" fill="#2a2244"/><path d="M357 360 Q357 330 390 330" stroke="#2a2244" stroke-width="10" fill="none"/>'
             f'<ellipse cx="398" cy="340" rx="26" ry="12" fill="#fff3c8"/><polygon points="380,346 416,346 520,900 280,900" fill="#ffd27a" opacity=".07"/>')
    rua = ('<rect x="-700" y="900" width="3400" height="60" fill="#3a2e5a"/><rect x="-700" y="958" width="3400" height="10" fill="#5a4a8a"/>'
           '<rect x="-700" y="968" width="3400" height="600" fill="#14102a"/>' + "".join(f'<rect x="{x}" y="1030" width="90" height="12" rx="6" fill="#eef1f7" opacity=".4"/>' for x in range(-200, 2600, 200)))
    raios = "".join(f'<path d="M{math.cos(math.radians(a)) * 110:.0f} {math.sin(math.radians(a)) * 110:.0f} L{math.cos(math.radians(a)) * 165:.0f} {math.sin(math.radians(a)) * 165:.0f}"/>' for a in range(0, 360, 30))
    sol0 = (bx, by, S)
    tr_s, js_s = mov(f"#{p}-solW", sol0, [(t_lib + 0.1, 1.4, (SOL[0], SOL[1], 2.4), "power2.inOut")])
    bol = f'<g id="{p}-orbW">{orbe(p, 0, VERM, 38)}</g><g transform="translate(0 4) scale(.5)"><g id="{p}-cadW">{cadeado(p, 0)}</g></g>'
    svg = f"""{ceu}
<g transform="translate({SOL[0]} {SOL[1]})"><g id="{p}-raios" opacity="0" stroke="{AMBAR}" stroke-width="10" stroke-linecap="round" filter="url(#{p}-glow)">{raios}</g></g>
<g id="{p}-solW" transform="{tr_s}"><g id="{p}-sol" opacity="0">{orbe(p, 1, AMBAR, 34)}</g></g>
{sky}{casa}{poste}{rua}
<g transform="translate({PX} 900) scale({S})">{humano(p, "casa", "em_pe", mao=chave_mao)}{bolha_h(p, 0, bol)}</g>"""
    extra = (f'<linearGradient id="{p}-ceu" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0e0a30"/><stop offset=".55" stop-color="#2a1d6a"/><stop offset="1" stop-color="#4a2a7a"/></linearGradient>'
             f'<linearGradient id="{p}-aurg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a2a8a" stop-opacity="0"/><stop offset=".45" stop-color="#ff7ab8" stop-opacity=".35"/><stop offset=".62" stop-color="#ffb23e" stop-opacity=".8"/></linearGradient>')
    html = (tit(f"{p}-t0", "LIBERTAÇÃO", "right:70px;top:440px;text-align:right", 110, "#ffd98a") +
            tit(f"{p}-t1", "QUEM DECIDE", "left:0;right:0;text-align:center;top:40px", 120, "#eef1f7") +
            tit(f"{p}-t2", "QUAL LEMBRANÇA DÓI DEMAIS?", "left:0;right:0;text-align:center;top:190px", 60, "#ff9bb0", True) +
            "".join(tit(f"{p}-o{i}", nome, f"left:1280px;top:{y}px", 64, "#3a1d6a", True) for i, ((nome, _), y) in enumerate(zip(ops, ys))))
    js = cam(p, (1.35, bx - 60, by + 160), [
        (0.2, t_lib - 0.2, (1.42, bx - 60, by + 150), "sine.inOut"),
        (t_lib + 0.1, 1.6, (1.0, 960, 540), "power3.inOut"),
        (ops[3][1], dur - ops[3][1], (1.04, 980, 540), "sine.inOut")])
    gira = ""
    a0 = ang[0]
    om = ombro("em_pe")
    for i, (nome, tt) in enumerate(ops):
        gira += ((f'tl.fromTo("#{g}-braco",{{rotation:{a0},svgOrigin:"{om}"}},{{rotation:{ang[i]},svgOrigin:"{om}",duration:0.45,ease:"back.out(2)",immediateRender:false}},{tt - 0.15:.2f});' if i else "")
                 + f'rise("#{p}-o{i} span", {tt - 0.1:.2f}, 0.6);'
                 f'tl.fromTo("#{p}-o{i}",{{color:"#3a1d6a"}},{{color:"#fffaf0",duration:0.2}},{tt:.2f});'
                 + (f'tl.fromTo("#{p}-o{i - 1}",{{color:"#fffaf0"}},{{color:"#5a3a8a",duration:0.2,immediateRender:false}},{tt:.2f});' if i else ""))
        a0 = ang[i]
    js += js_s + f"""
  pop("#{p}-bol0", 0.2, 0.4, 0.7);
  tl.fromTo("#{p}-orbW",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.3,duration:0.3,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_sofre - 0.4:.2f});
  tl.fromTo("#{g}-olho",{{x:0}},{{x:-2,duration:0.3}},{t_sofre:.2f});
  tl.fromTo("#{p}-arg0",{{y:0}},{{y:-34,duration:0.35,ease:"back.out(3)"}},{t_lib - 0.3:.2f});
  tl.fromTo("#{p}-cadW",{{opacity:1,y:0,rotation:0,transformOrigin:"50% 50%"}},{{opacity:0,y:260,rotation:40,transformOrigin:"50% 50%",duration:0.9,ease:"power2.in",immediateRender:false}},{t_lib + 0.1:.2f});
  tl.fromTo("#{p}-orbW",{{opacity:1}},{{opacity:0,duration:0.2,immediateRender:false}},{t_lib + 0.1:.2f});
  entra("#{p}-sol", {t_lib + 0.05:.2f}, 0.2);
  tl.fromTo("#{p}-bol0",{{opacity:1}},{{opacity:0,duration:0.4,immediateRender:false}},{t_lib + 0.8:.2f});
  tl.fromTo("#{p}-aur",{{opacity:0}},{{opacity:1,duration:1.6,ease:"power2.out"}},{t_lib + 0.3:.2f});
  tl.fromTo("#{p}-raios",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:0.9,scale:1,transformOrigin:"50% 50%",duration:0.8,ease:"expo.out"}},{t_lib + 1.3:.2f});
  tl.fromTo("#{p}-raios",{{rotation:0,transformOrigin:"50% 50%"}},{{rotation:40,duration:{dur - t_lib - 1.3:.2f},ease:"none",immediateRender:false}},{t_lib + 1.3:.2f});
  tl.fromTo("#{g}-braco",{{rotation:0,svgOrigin:"{ombro("em_pe")}"}},{{rotation:-130,svgOrigin:"{ombro("em_pe")}",duration:0.5,ease:"back.out(1.6)"}},{t_lib:.2f});
  tl.fromTo("#{g}-braco",{{rotation:-130,svgOrigin:"{ombro("em_pe")}"}},{{rotation:{ang[0]},svgOrigin:"{ombro("em_pe")}",duration:0.6,ease:"power2.inOut",immediateRender:false}},{t_perg - 0.6:.2f});
  rise("#{p}-t0 span", {t_lib:.2f}, 0.8);
  some("#{p}-t0", {t_perg - 0.7:.2f}, 0.3);
  pop("#{p}-kW", {t_perg - 0.2:.2f}, 0.3, 0.9);
  rise("#{p}-t1 span", {t_quem:.2f}, 0.8);
  rise("#{p}-t2 span", {t_qual:.2f}, 0.8);
  tl.fromTo("#{g}-olho",{{x:-2}},{{x:3,duration:0.4,immediateRender:false}},{t_perg:.2f});
  {gira}
  tl.fromTo("#{g}-braco",{{rotation:{ang[3]},svgOrigin:"{ombro("em_pe")}"}},{{rotation:{ang[3] - 5},svgOrigin:"{ombro("em_pe")}",duration:0.8,repeat:1,yoyo:true,ease:"sine.inOut",immediateRender:false}},{ops[3][1] + 0.6:.2f});
""" + vida_h(p, dur, (1.8, 4.2, 7.0, 10.9, 13.9))
    return comp(p, dur, svg, html, js, extra, seed=8)


CENAS = [(f"{CE}_{i}", fn, seg(CE, i)[1]) for i, fn in enumerate([trancada_0, trancada_1, trancada_2, trancada_3, trancada_4, trancada_5, trancada_6, trancada_7, trancada_8])]
MAPA = {(CE, int(k.split("_")[1])): k for k, _, _ in CENAS}

if __name__ == "__main__":
    print(escreve_cenas(CENAS, AQUI))
