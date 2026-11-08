"""Grupo g7: robo 5 a 9 e fechamento 0 a 2 (cenas v5).

  python3 build_g7_robo2_fechamento1.py     # escreve compositions/ e index.html desta pasta

Peças reaproveitadas: chave e feixe da M8 (cenas-v4/build4.py), corredor com a porta da F2 (cenas-v3/build2.py),
raio (`bolt`, build4), a pessoa de perfil com cérebro (motor.pessoa, só no fechamento 1, onde a narração fala do cérebro),
a pessoa de verdade, quadros e orbes (cenas-v5/gente.py; outras pessoas com as mesmas peças via gente_var).
O robô mau e a fechadura são arte deste grupo, no mesmo traço neon.
"""
import os, random, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
from motor import *  # noqa: E402,F403
AQUI = os.path.dirname(os.path.abspath(__file__))  # motor também define AQUI (cenas-v5); aqui é a pasta do grupo
sys.path.insert(0, os.path.join(AQUI, "../../cenas-v4"))
from build4 import bolt  # noqa: E402
from gente import gente, vida_gente, quadro, orbe, PELE, CABELO, CASA, TRAB, ANCORAS  # noqa: E402

PELES = [PELE, "#c98e62", "#8d5a3b"]


def anc(variante="casa", pose="em_pe", giro=25):
    """Âncoras de gente.py (mao_d, mao_e, cabeca_centro, ombro_braco...) para a pessoa desenhada com estes parâmetros."""
    return ANCORAS[("casa" if variante == "casa" else "trabalho", "em_pe" if pose == "em_pe" else "sentado", 30 if giro >= 15 else 0)]


def piv(variante="casa", pose="em_pe", giro=25):
    """svgOrigin do ombro para girar {p}-braco (o grupo do braço não tem transform, então é coordenada local da pessoa)."""
    x, y = anc(variante, pose, giro)["ombro_braco"]
    return f"{x} {y}"


def gente_var(p, variante="casa", pose="em_pe", glow=None, pele=0, cabelo=None, roupa=None, calca=None, **kw):
    """A pessoa de gente.py com outra pele, cabelo ou roupa (troca do hex base de cada peça). roupa=(torso, ...): só o 1o vale."""
    # As máscaras do desenho novo são "M-9999 -9999h19998v19998..." recortadas por clip-path. O getBBox ignora o clip, então
    # todo transformOrigin em % (respiração do tronco, pop, achatamento) girava em torno de um ponto a milhares de px e o
    # tronco subia engolindo a cabeça. Um retângulo do tamanho da pessoa dá o mesmo desenho e uma caixa honesta.
    s = gente(p, variante, pose, glow=glow, **kw).replace("M-9999 -9999h19998v19998h-19998Z", "M-300 -640h600v700h-600Z")
    v = CASA if variante == "casa" else TRAB
    if pele:
        s = s.replace(PELE, PELES[pele])
    if cabelo:
        s = s.replace(CABELO, cabelo)
    if roupa:
        s = s.replace(v["torso"], roupa[0])
    if calca:
        s = s.replace(v["calca"], calca)
    return s


def vida(p, dur, piscadas, pose="em_pe"):
    """vida_gente com o pivô da respiração no quadril por svgOrigin (o {p}-tor não tem transform)."""
    return vida_gente(p, dur, piscadas).replace('transformOrigin:"50% 100%"', f'svgOrigin:"0 {-230 if pose == "em_pe" else -175}"')


def retrato(p, x, y, k, variante="casa", **kw):
    """Cabeça e ombros de uma pessoa em pé, de frente (foto/avatar): o ponto RET abaixo do centro da cabeça vai para (x, y)."""
    cx, cy = anc(variante, "em_pe", 0)["cabeca_centro"]
    return (f'<g transform="translate({x - cx * k:.1f} {y - (cy + RET) * k:.1f}) scale({k})">'
            f'{gente_var(p, variante, "em_pe", cadeira=False, sombra=False, giro=0, **kw)}</g>')


RET = 40   # ponytail: ajuste a olho no snapshot (antes era o (0,-575) do personagem antigo)


PLEX = "font-family:'IBM Plex Mono',monospace;font-weight:500;letter-spacing:.14em"

# JS extra: texto SVG que sobe por máscara (acompanha a câmera) e traço que se desenha
JS_G7 = r"""
  function sr(sel,t,h){tl.set(sel,{opacity:0},0);tl.fromTo(sel,{y:h,opacity:1},{y:0,opacity:1,duration:0.75,ease:"expo.out",immediateRender:false},t);}
  function draw(sel,t,d,L){tl.fromTo(sel,{attr:{"stroke-dashoffset":L}},{attr:{"stroke-dashoffset":0},duration:d,ease:"power2.inOut"},t);}
  function sai(sel,t){tl.fromTo(sel,{yPercent:0},{yPercent:-125,duration:0.45,ease:"power3.in",immediateRender:false},t);}
"""


def T_(cena, sg):
    return lambda w, n=0, d=None: palavra(cena, sg, w, n, d)


def srise(id_, x, y, txt, tam, cor, fam="EB Garamond", peso=700, anc="middle", esp=0, contorno=True):
    """Texto SVG preso à arte (segue a câmera), subindo por máscara. Anime com sr('#id', t, tam*1.3)."""
    return (f'<clipPath id="{id_}-m"><rect x="-4000" y="{y - tam * 1.0:.0f}" width="12000" height="{tam * 1.32:.0f}"/></clipPath>'
            f'<g clip-path="url(#{id_}-m)"><text id="{id_}" x="{x}" y="{y}" text-anchor="{anc}" font-family="{fam}" font-weight="{peso}" '
            f'font-size="{tam}" letter-spacing="{esp}" fill="{cor}" stroke="#05031a" stroke-width="{tam * 0.12 if contorno else 0:.1f}" paint-order="stroke" '
            f'stroke-linejoin="round" opacity="0">{txt}</text></g>')


def mono(id_, txt, estilo, cor, tam=56, dot=True):
    """Rótulo grande em IBM Plex Mono maiúsculo (sobe por máscara, `rise('#id span', t)`)."""
    d = (f'<i style="display:inline-block;width:{tam * .36:.0f}px;height:{tam * .36:.0f}px;border-radius:50%;background:{cor};'
         f'margin-right:{tam * .4:.0f}px;vertical-align:{tam * .08:.0f}px;box-shadow:0 0 18px {cor}"></i>') if dot else ""
    return texto(id_, d + txt, f"{estilo};{PLEX};font-size:{tam}px;color:{cor}")


# ---------------------------------------------------------------- arte deste grupo
def robo(p, glow, olho=VERM, cor=MAGENTA):
    """Robô mau em linha neon. Local: x -320..320, y -330..300 (base em y=300). Ids: {p}-olhos (olhos acesos)."""
    forma = ('<rect x="-170" y="-250" width="340" height="230" rx="44"/>'
             '<rect x="-204" y="-176" width="34" height="86" rx="12"/><rect x="170" y="-176" width="34" height="86" rx="12"/>'
             '<rect x="-56" y="-22" width="112" height="40" rx="8"/>'
             '<path d="M-205 14 L205 14 L165 296 L-165 296 Z"/>')
    bracos = "M-205 44 C-275 80 -305 150 -292 238 M205 44 C275 80 305 150 292 238"
    garras = "M-312 232 Q-326 262 -306 288 M-272 232 Q-258 262 -278 288 M312 232 Q326 262 306 288 M272 232 Q258 262 278 288"
    olhos = ('<path d="M-118 -178 L-30 -148 L-38 -116 L-112 -124 Z"/><path d="M118 -178 L30 -148 L38 -116 L112 -124 Z"/>'
             '<circle cx="0" cy="130" r="24"/><circle cx="0" cy="-312" r="17"/>')
    dentes = "".join(f'<line x1="{x}" y1="-82" x2="{x}" y2="-46" stroke="{cor}" stroke-width="3" opacity=".7"/>' for x in range(-64, 80, 32))
    return (f'<defs><linearGradient id="{p}-rbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#30268a"/><stop offset="1" stop-color="#120d3a"/></linearGradient>'
            f'<radialGradient id="{p}-rbo"><stop offset="0" stop-color="{olho}" stop-opacity=".85"/><stop offset="1" stop-color="{olho}" stop-opacity="0"/></radialGradient></defs>'
            f'<g id="{p}-robo"><path d="{bracos}" fill="none" stroke="#120d3a" stroke-width="30" stroke-linecap="round"/>'
            f'<g fill="url(#{p}-rbg)">{forma}</g>'
            f'<g fill="none" stroke="{cor}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round" filter="url(#{glow})">{forma}<path d="{bracos}"/><path d="{garras}"/>'
            f'<line x1="0" y1="-250" x2="0" y2="-294"/></g>'
            f'<rect x="-96" y="-84" width="192" height="40" rx="10" fill="#05031a" stroke="{cor}" stroke-width="4"/>{dentes}'
            f'<circle cx="0" cy="130" r="50" fill="#05031a" stroke="{cor}" stroke-width="5"/>'
            f'<g fill="#3a3466">{olhos}</g>'
            f'<g id="{p}-olhos"><circle cx="-74" cy="-146" r="86" fill="url(#{p}-rbo)" opacity=".6"/><circle cx="74" cy="-146" r="86" fill="url(#{p}-rbo)" opacity=".6"/>'
            f'<g fill="{olho}">{olhos}</g></g></g>')


def placa(p, glow, r=230):
    """Fechadura: placa redonda âmbar com o buraco. Centro (0,0), raio r. Ids: {p}-luz (buraco aceso)."""
    k = r / 230
    hole = (f"M{-34 * k:.1f} {4.5 * k:.1f} A{56 * k:.1f} {56 * k:.1f} 0 1 1 {34 * k:.1f} {4.5 * k:.1f} "
            f"L{58 * k:.1f} {120 * k:.1f} L{-58 * k:.1f} {120 * k:.1f} Z")
    # buraco: círculo centrado em (0,-40k); o path todo sobe 40k
    hole = f'<path d="{hole}" transform="translate(0 {-40 * k:.1f})"'
    paraf = "".join(f'<circle cx="{x * k:.0f}" cy="{y * k:.0f}" r="{11 * k:.1f}" fill="#ffcf6a" opacity=".75"/>' for x, y in ((-140, -140), (140, -140), (-140, 140), (140, 140)))
    return (f'<defs><radialGradient id="{p}-pl" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#5a3f1a"/><stop offset="1" stop-color="#1d1208"/></radialGradient>'
            f'<radialGradient id="{p}-pluz" cx="50%" cy="40%" r="60%"><stop offset="0" stop-color="#fffbe8"/><stop offset="1" stop-color="#ffb23e"/></radialGradient></defs>'
            f'<circle r="{r}" fill="url(#{p}-pl)"/>'
            f'<circle r="{r}" fill="none" stroke="{AMBAR}" stroke-width="{12 * k:.1f}" filter="url(#{glow})"/>'
            f'<circle r="{r * .84:.1f}" fill="none" stroke="#ffcf6a" stroke-width="{3 * k:.1f}" opacity=".45"/>{paraf}'
            f'{hole} fill="#05031a" stroke="#ffcf6a" stroke-width="{4 * k:.1f}"/>'
            f'{hole} id="{p}-luz" fill="url(#{p}-pluz)" opacity="0" filter="url(#{glow})"/>')


def chave(glow, cor=AMBAR):
    """Chave da M8 (cenas-v4): argola em (0,0), haste para baixo até (0,130)."""
    return (f'<g filter="url(#{glow})"><circle cx="0" cy="0" r="34" fill="none" stroke="{cor}" stroke-width="12"/>'
            f'<path d="M0 34 L0 130 M0 100 L30 100 M0 124 L22 124" stroke="{cor}" stroke-width="12" fill="none" stroke-linecap="round"/></g>')


def feixe_def(p):
    return (f'<linearGradient id="{p}-fx" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffcf6a" stop-opacity=".5"/>'
            f'<stop offset="1" stop-color="#ffe3a0" stop-opacity="0"/></linearGradient>')


def chao(p, y=880, cor="#26246a"):
    return (f'<linearGradient id="{p}-ch" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{cor}" stop-opacity=".75"/>'
            f'<stop offset="1" stop-color="{cor}" stop-opacity="0"/></linearGradient>')


def corredor(p, glow):
    """Corredor de servidores da F2 (cenas-v3/build2.py::cena_F2), com ids prefixados e a porta no fundo."""
    defs = f"""<defs><radialGradient id="{p}-fim" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#9af0ff" stop-opacity=".9"/><stop offset=".4" stop-color="#6a8cff" stop-opacity=".4"/><stop offset="1" stop-color="#6a8cff" stop-opacity="0"/></radialGradient>
<linearGradient id="{p}-teto" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0828"/><stop offset="1" stop-color="#1c1a58"/></linearGradient>
<linearGradient id="{p}-chao2" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#06051a"/><stop offset="1" stop-color="#26246a"/></linearGradient>
<linearGradient id="{p}-rack" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1a1856"/><stop offset="1" stop-color="#2c2a88"/></linearGradient></defs>"""

    def pontos(lado):
        def f(u, v):
            xb = 960 + lado * 960; xf = 960 + lado * 118
            yt0, yb0 = -40, 1120; yt1, yb1 = 410, 600
            x = xb + (xf - xb) * u
            yt = yt0 + (yt1 - yt0) * u; yb = yb0 + (yb1 - yb0) * u
            return x, yt + (yb - yt) * v
        return f
    partes, leds, cabos = [], [], []
    for lado in (-1, 1):
        f = pontos(lado)
        us = [1 - 1 / (1 + 0.5 * i) for i in range(0, 26)]
        for i in range(len(us) - 1):
            a, bb = us[i], us[i + 1]
            q = " ".join(f"{x:.0f},{y:.0f}" for x, y in [f(a, 0.03), f(bb, 0.03), f(bb, 0.97), f(a, 0.97)])
            partes.append(f'<polygon points="{q}" fill="url(#{p}-rack)" stroke="#5a5ad0" stroke-width="3"/>'
                          f'<polygon points="{q}" fill="#05031a" opacity="{0.18 + 0.7 * (a ** 0.8):.2f}"/>')
            x1, y1 = f(a, 0.025); x2, y2 = f(bb, 0.025)
            cabos.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#ff4fa3" stroke-width="{max(2, 8 * (1 - a)):.1f}" opacity=".7"/>')
            for r in range(11):
                for c in range(3):
                    uu = a + (bb - a) * (0.18 + 0.3 * c); vv = 0.10 + 0.08 * r
                    x, y = f(uu, vv)
                    tam = max(2.2, 20 * (1 - uu) ** 1.3)
                    cor = CIANO if (i + r + c) % 4 else (AMBAR if (r + c) % 2 else MAGENTA)
                    leds.append(f'<rect class="{p}-led" x="{x - tam:.1f}" y="{y - tam * 0.5:.1f}" width="{tam * 2:.1f}" height="{tam:.1f}" rx="{tam * 0.2:.1f}" fill="{cor}"/>')
    tiras = "".join(f'<polygon points="{960 + dx * 0.06:.0f},430 {960 - dx * 0.06:.0f},430 {960 - dx:.0f},-40 {960 + dx:.0f},-40" fill="#cfe8ff" opacity=".16"/>' for dx in (170, 520, 880))
    guias = "".join(f'<line x1="{x}" y1="1120" x2="{960 + (x - 960) * 0.12:.0f}" y2="590" stroke="#6ad8ff" stroke-width="3" opacity=".22"/>' for x in (260, 560, 960, 1360, 1660))
    porta = (f'<rect x="905" y="470" width="110" height="120" rx="8" fill="#0b0920"/>'
             f'<g transform="translate(960 530)"><g id="{p}-pluzg"><rect x="-55" y="-60" width="110" height="120" rx="8" fill="#cfeaff" opacity=".9" filter="url(#{glow})"/></g></g>'
             f'<rect x="905" y="470" width="110" height="120" rx="8" fill="none" stroke="#8d7bff" stroke-width="3"/>')
    return (defs + f'<polygon points="0,-40 1920,-40 1080,430 840,430" fill="url(#{p}-teto)"/><polygon points="0,1120 1920,1120 1080,590 840,590" fill="url(#{p}-chao2)"/>'
            f'<ellipse id="{p}-nevoa" cx="960" cy="510" rx="520" ry="330" fill="url(#{p}-fim)"/>{tiras}'
            f'<g>{"".join(partes)}</g><g>{guias}</g>{porta}<g>{"".join(cabos)}</g><g>{"".join(leds)}</g>')


def cena(p, dur, svg, html, js, extra="", **kw):
    return composicao(p, dur, svg, html, JS_G7 + js, extra, **kw)


# ================================================================ robo 5: a ideia não se sustenta
def robo_5():
    p, C, S = "robo_5", "robo", 5
    ini, dur = seg(C, S); T = T_(C, S)
    t_sus, t_sup, t_fra, t_maq, t_que = T("sustenta"), T("suposicoes"), T("frageis"), T("maquina"), T("querer")
    t_rej, t_for, t_ex, t_nen, t_evi, t_ame = T("rejeitada"), T("forum"), T("existe"), T("nenhuma"), T("evidencia"), T("ameaca")
    blocos = [(960, 120, 800), (978, 300, 720), (940, 420, 640), (988, 340, 560), (955, 470, 480)]
    extra = (chao(p) + f'<linearGradient id="{p}-blk" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5a46c8"/><stop offset="1" stop-color="#241a6e"/></linearGradient>'
             f'<radialGradient id="{p}-iris"><stop offset="0" stop-color="#ffd27a"/><stop offset=".45" stop-color="{VERM}"/><stop offset="1" stop-color="#5a0a20"/></radialGradient>')
    rng = random.Random(5)
    bl = ""
    for k, (cx, w, y) in enumerate(blocos):
        x0 = cx - w / 2
        pts = [(x0 + 8, y + 10)] + [(x0 + w * (j + 1) / 5 + rng.uniform(-14, 14), y + 14 + (j % 2) * 44 + rng.uniform(-8, 8)) for j in range(4)] + [(x0 + w - 8, y + 70)]
        crack = "M" + " L".join(f"{a:.0f} {b:.0f}" for a, b in pts)
        bl += (f'<g id="{p}-b{k}"><rect x="{x0:.0f}" y="{y}" width="{w}" height="80" rx="10" fill="url(#{p}-blk)" stroke="#8d7bff" stroke-width="5"/>'
               f'<line x1="{x0 + 14:.0f}" y1="{y + 10}" x2="{x0 + w - 14:.0f}" y2="{y + 10}" stroke="#cfc6ff" stroke-width="3" opacity=".5"/>'
               f'<path id="{p}-cr{k}" d="{crack}" fill="none" stroke="#f3eeff" stroke-width="4" stroke-linejoin="round" stroke-dasharray="900" stroke-dashoffset="900"/></g>')
    # íris recortada pela amêndoa (antes vazava em cima e embaixo); o fechamento achata o olho inteiro, contorno junto
    extra += f'<clipPath id="{p}-amd"><path d="M-205 0 Q0 -165 205 0 Q0 165 -205 0 Z"/></clipPath>'
    olho = (f'<g id="{p}-olho"><g id="{p}-palp"><path d="M-205 0 Q0 -165 205 0 Q0 165 -205 0 Z" fill="#2a0a1a"/>'
            f'<g clip-path="url(#{p}-amd)"><circle r="98" fill="url(#{p}-iris)"/><g id="{p}-pup"><circle r="34" fill="#05031a"/><circle r="34" fill="none" stroke="#ff9fb5" stroke-width="3" opacity=".6"/></g>'
            f'<circle cx="-34" cy="-40" r="14" fill="#fff" opacity=".7"/></g></g>'
            f'<path d="M-205 0 Q0 -165 205 0 Q0 165 -205 0 Z" fill="none" stroke="{VERM}" stroke-width="7" filter="url(#{p}-glow)"/></g>')
    bal = ""
    # gente do próprio fórum: cada post tem o avatar de uma pessoa diferente
    autores = [dict(variante="trabalho", pele=1, roupa=("#3a4a8a", "#2a3870")), dict(variante="casa", pele=0, cabelo="#c99a3a", roupa=("#2fa88a", "#1f8068")),
               dict(variante="casa", pele=2, cabelo="#140c08", roupa=("#d0408a", "#a02a68"))]
    for k, (x, y) in enumerate([(1330, 230), (1400, 440), (1310, 650)]):
        linhas = "".join(f'<rect x="{x + 110}" y="{y + 40 + j * 32}" width="{250 - j * 60}" height="14" rx="7" fill="#8d7bff" opacity=".55"/>' for j in range(3))
        extra += f'<clipPath id="{p}-av{k}"><circle cx="{x + 40}" cy="{y + 79}" r="52"/></clipPath>'
        av = (f'<circle cx="{x + 40}" cy="{y + 79}" r="52" fill="#3a2f8a"/><g clip-path="url(#{p}-av{k})">{retrato(f"{p}-a{k}", x + 40, y + 100, 0.66, glow=p + "-glow", **autores[k])}</g>'
              f'<circle cx="{x + 40}" cy="{y + 79}" r="52" fill="none" stroke="#cfc6ff" stroke-width="4"/>')
        bal += (f'<g id="{p}-bal{k}"><path d="M{x} {y} h380 a24 24 0 0 1 24 24 v110 a24 24 0 0 1 -24 24 h-300 l-40 40 v-40 h-40 a24 24 0 0 1 -24 -24 v-110 a24 24 0 0 1 24 -24 z" '
                f'fill="#1c1a58" stroke="#8d7bff" stroke-width="5" filter="url(#{p}-sombra)"/>{av}{linhas}'
                f'<g id="{p}-x{k}"><circle cx="{x + 370}" cy="{y + 10}" r="38" fill="{VERM}" filter="url(#{p}-glow)"/>'
                f'<path d="M{x + 354} {y - 6} l32 32 M{x + 386} {y - 6} l-32 32" stroke="#fff" stroke-width="8" stroke-linecap="round"/></g></g>')
    svg = f"""<g id="{p}-mundo">
<rect x="-300" y="880" width="2520" height="400" fill="url(#{p}-ch)"/>
<g transform="translate(960 560) scale(1.4)"><g id="{p}-fant" opacity="0" filter="url(#{p}-blur6)">{robo(p + "g", p + "-glow")}</g></g>
<ellipse id="{p}-som" cx="960" cy="886" rx="300" ry="24" fill="#05031a" opacity=".55"/>
<g id="{p}-torre">{bl}<g transform="translate(955 380)"><g id="{p}-olhoW">{olho}</g></g></g>
{bal}
</g>"""
    html = (texto(f"{p}-t1", "SUPOSIÇÕES", "left:70px;top:340px;font-size:90px;color:#e2dcff") +
            texto(f"{p}-t2", "FRÁGEIS", "left:70px;top:455px;font-size:90px;color:#c9b8ff") +
            texto(f"{p}-t3", "NENHUMA EVIDÊNCIA", "left:0;right:0;text-align:center;top:250px;font-size:128px;color:#ffd98a"))
    queda = ""
    rngq = random.Random(9)
    for k, (cx, w, y) in enumerate(blocos):
        dy = 880 - (y + 80) - (0 if k == 0 else rngq.uniform(0, 30))
        dx = [0, -330, 300, -560, 520][k]
        rot = [0, -14, 10, -24, 18][k]
        queda += f'tl.to("#{p}-b{k}",{{x:{dx},y:{dy:.0f},rotation:{rot},transformOrigin:"50% 50%",duration:0.75,ease:"bounce.out"}},{t_ex + 0.12 * (4 - k):.2f});'
    js = f"""
  camZ("#{p}-cam", 0, 3.0, 1.12, 1.0, 960, 560);
  camZ("#{p}-cam", 3.1, {t_ex - 3.3:.2f}, 1.0, 1.07, 960, 470, "sine.inOut");
  camZ("#{p}-cam", {t_ex:.2f}, 1.4, 1.07, 0.98, 960, 640);
  tl.fromTo("#{p}-pup",{{x:-34}},{{x:34,duration:1.1,repeat:5,yoyo:true,ease:"sine.inOut"}},0.3);
  tl.fromTo("#{p}-torre",{{rotation:-1.4,transformOrigin:"50% 100%"}},{{rotation:1.4,duration:0.55,repeat:{int((t_ex - 0.3 - t_sus) / 0.55) - 1},yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_sus:.2f});
  rise("#{p}-t1 span", {t_sup:.2f}); rise("#{p}-t2 span", {t_fra:.2f});
  {"".join(f'draw("#{p}-cr{k}", {t_fra + 0.12 * k:.2f}, 0.5, 900);' for k in range(5))}
  tl.fromTo("#{p}-fant",{{opacity:0}},{{opacity:0.32,duration:0.8}},{t_maq:.2f});
  tl.fromTo("#{p}-fant",{{opacity:0.32}},{{opacity:0,duration:0.8,immediateRender:false}},{t_que + 0.5:.2f});
  {"".join(f'pop("#{p}-bal{k}", {t_rej + 0.45 * k:.2f}, 0.4, 0.7); pop("#{p}-x{k}", {t_rej + 0.45 * k + 0.5:.2f}, 2.2, 0.45);' for k in range(3))}
  tl.fromTo("#{p}-pup",{{scale:1,transformOrigin:"50% 50%"}},{{scale:0.62,transformOrigin:"50% 50%",duration:0.3,immediateRender:false}},{t_rej:.2f});
  some("#{p}-t1", {t_ex - 0.3:.2f}, 0.4); some("#{p}-t2", {t_ex - 0.3:.2f}, 0.4);
  {"".join(f'some("#{p}-bal{k}", {t_ex - 0.3:.2f}, 0.4);' for k in range(3))}
  tl.to("#{p}-torre",{{rotation:9,duration:0.35,ease:"power2.in"}},{t_ex - 0.15:.2f});
  {queda}
  tl.to("#{p}-olhoW",{{y:420,x:-60,rotation:-8,duration:0.8,ease:"bounce.out"}},{t_ex + 0.1:.2f});
  tl.to("#{p}-olho",{{scaleY:0.04,transformOrigin:"50% 50%",duration:0.35,ease:"power2.in"}},{t_ex + 0.6:.2f});
  tl.to("#{p}-olho",{{opacity:0,duration:0.3}},{t_ex + 0.95:.2f});
  tl.fromTo("#{p}-som",{{attr:{{rx:300}}}},{{attr:{{rx:760}},duration:0.6}},{t_ex + 0.2:.2f});
  tl.fromTo("#{p}-mundo",{{y:0}},{{y:10,duration:0.06,repeat:7,yoyo:true,ease:"none"}},{t_ex + 0.75:.2f});
  rise("#{p}-t3 span", {t_nen:.2f}, 0.9);
"""
    return cena(p, dur, svg, html, js, extra, seed=5)


# ================================================================ robo 6: o medo de um robô mau
def robo_6():
    p, C, S = "robo_6", "robo", 6
    ini, dur = seg(C, S); T = T_(C, S)
    t_rep, t_medo, t_rob, t_pre, t_pes, t_rea, t_agi, t_hoj = T("repare"), T("medo"), T("robo"), T("pressionar"), T("pessoas"), T("reais"), T("agir"), T("hoje")
    extra = (chao(p, cor="#2a1d70") + f'<radialGradient id="{p}-ver" cx="72%" cy="40%" r="70%"><stop offset="0" stop-color="{VERM}" stop-opacity=".55"/><stop offset="1" stop-color="{VERM}" stop-opacity="0"/></radialGradient>'
             f'<clipPath id="{p}-tl"><rect x="1080" y="180" width="660" height="560" rx="14"/></clipPath>'
             f'<linearGradient id="{p}-luz" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe3a0" stop-opacity=".45"/><stop offset="1" stop-color="#ffe3a0" stop-opacity="0"/></linearGradient>')
    # rua à noite: prédios ao fundo, poste, calçada; o robô passa num telão na fachada da direita
    rng = random.Random(61)
    fundo = ""
    for x0, w, top in ((-40, 230, 300), (200, 180, 200), (390, 260, 340), (660, 200, 240), (870, 170, 390)):
        jan = "".join(f'<rect x="{x0 + 22 + c * 46}" y="{top + 30 + r * 58}" width="24" height="32" rx="3" fill="{"#ffe39a" if rng.random() < 0.35 else "#16124a"}" opacity=".7"/>'
                      for r in range(int((840 - top - 60) / 58)) for c in range(int((w - 30) / 46)))
        fundo += f'<rect x="{x0}" y="{top}" width="{w}" height="{840 - top}" fill="#1a1450" stroke="#3a2f8a" stroke-width="3"/>{jan}'
    fachada = (f'<rect x="1010" y="110" width="800" height="730" fill="#201a5e" stroke="#5a4ad0" stroke-width="4"/>'
               f'<rect x="1066" y="166" width="688" height="588" rx="20" fill="#05031a" stroke="#8d7bff" stroke-width="8" filter="url(#{p}-sombra)"/>'
               f'<rect x="1100" y="754" width="40" height="86" fill="#14103e"/><rect x="1680" y="754" width="40" height="86" fill="#14103e"/>')
    poste = (f'<polygon points="930,300 990,300 1060,840 860,840" fill="url(#{p}-luz)"/>'
             f'<path d="M 960 840 L 960 270 Q 960 240 990 240 L 1010 240" fill="none" stroke="#3a2f8a" stroke-width="14" stroke-linecap="round"/>'
             f'<ellipse cx="1004" cy="262" rx="30" ry="12" fill="#ffe3a0" filter="url(#{p}-glow)"/>')
    pes = ""
    tipos = [dict(variante="casa", pele=0), dict(variante="trabalho", pele=2, roupa=("#3a4a8a", "#2a3870")),
             dict(variante="casa", pele=1, cabelo="#140c08", roupa=("#2fa88a", "#1f8068"))]
    for k, x in enumerate((190, 470, 750)):
        pes += (f'<g transform="translate({x} 840) scale(.74)"><g id="{p}-sq{k}"><g id="{p}-pu{k}">'
                f'{gente_var(f"{p}-g{k}", glow=p + "-glow", **tipos[k])}</g></g></g>')
    ondas = "".join(f'<circle id="{p}-on{k}" cx="1410" cy="460" r="80" fill="none" stroke="{VERM}" stroke-width="10" opacity="0"/>' for k in range(3))
    svg = f"""<rect x="-200" y="840" width="2320" height="400" fill="url(#{p}-ch)"/>
<g opacity=".8">{fundo}</g>{fachada}
<rect id="{p}-verm" x="-200" y="-200" width="2320" height="1480" fill="url(#{p}-ver)" opacity="0"/>
<rect id="{p}-tela" x="1080" y="180" width="660" height="560" rx="14" fill="#3a0a24" opacity="0"/>
<g clip-path="url(#{p}-tl)"><g transform="translate(1410 470) scale(.86)"><g id="{p}-robW" opacity="0"><g id="{p}-rob">{robo(p, p + "-glow")}</g></g></g></g>
{ondas}{poste}
<rect x="-200" y="836" width="2320" height="8" fill="#3a2f8a"/>
{pes}"""
    html = (texto(f"{p}-t1", "MEDO", "left:110px;top:40px;font-size:180px;color:#ff8aa6") +
            texto(f"{p}-t3", "HOJE", "left:110px;top:60px;font-size:160px;color:#ffd98a") +
            mono(f"{p}-t2", "PESSOAS REAIS", "left:130px;top:910px", MENTA, 60))
    js = f"""
  camZ("#{p}-cam", 0, {t_medo - 0.2:.2f}, 1.0, 1.12, 700, 600, "sine.inOut");
  camZ("#{p}-cam", {t_medo - 0.1:.2f}, 0.8, 1.12, 0.96, 960, 600);
  camZ("#{p}-cam", {t_medo + 0.8:.2f}, {dur - t_medo - 0.8:.2f}, 0.96, 1.04, 700, 640, "sine.inOut");
  {"".join(f'tl.fromTo("#{p}-g{k}-olho",{{x:0}},{{x:3,duration:0.3}},{t_rep + 0.2 * k:.2f});' for k in range(3))}
  tl.fromTo("#{p}-tela",{{opacity:0}},{{opacity:1,duration:0.12,repeat:3,yoyo:true,ease:"steps(1)"}},{t_medo - 0.3:.2f});
  tl.set("#{p}-tela",{{opacity:1}},{t_medo + 0.2:.2f});
  tl.fromTo("#{p}-robW",{{opacity:0,y:420}},{{opacity:1,y:0,duration:1.1,ease:"power3.out"}},{t_medo - 0.15:.2f});
  tl.fromTo("#{p}-verm",{{opacity:0}},{{opacity:1,duration:0.8}},{t_medo:.2f});
  tl.fromTo("#{p}-olhos",{{opacity:0.2}},{{opacity:1,duration:0.12,repeat:4,yoyo:true,ease:"steps(1)"}},{t_rob:.2f});
  rise("#{p}-t1 span", {t_medo:.2f}, 0.8);
  {"".join(f'tl.fromTo("#{p}-pu{k}",{{x:-3}},{{x:3,duration:0.07,repeat:{int((t_pre - t_medo) / 0.07)},yoyo:true,ease:"none"}},{t_medo + 0.4:.2f});' for k in range(3))}
  tl.to("#{p}-rob",{{rotation:-6,transformOrigin:"50% 100%",duration:0.5,ease:"power2.out"}},{t_pre - 0.1:.2f});
  {"".join(f'tl.fromTo("#{p}-on{k}",{{attr:{{r:80}},opacity:0.9}},{{attr:{{r:1300}},opacity:0,duration:1.1,ease:"power1.out",immediateRender:false}},{t_pre + 0.25 * k:.2f});' for k in range(3))}
  {"".join(f'tl.fromTo("#{p}-sq{k}",{{scaleY:1,scaleX:1,svgOrigin:"0 0"}},{{scaleY:0.84,scaleX:1.06,svgOrigin:"0 0",duration:0.35,ease:"power2.out"}},{t_pre + 0.2 + 0.1 * k:.2f});' for k in range(3))}
  {"".join(f'tl.to("#{p}-sq{k}",{{scaleY:1,scaleX:1,duration:0.8,ease:"elastic.out(1,0.4)"}},{t_pes + 0.1 * k:.2f});' for k in range(3))}
  rise("#{p}-t2 span", {t_pes:.2f});
  some("#{p}-t1", {t_hoj - 0.45:.2f}, 0.3);
  {"".join(f'tl.fromTo("#{p}-sq{k}",{{x:0,y:0}},{{x:120,y:-50,duration:0.3,ease:"power2.out",immediateRender:false}},{t_agi + 0.12 * k:.2f}); tl.to("#{p}-sq{k}",{{y:0,duration:0.3,ease:"bounce.out"}},{t_agi + 0.3 + 0.12 * k:.2f});' for k in range(3))}
  rise("#{p}-t3 span", {t_hoj - 0.1:.2f}, 0.6);
  tl.fromTo("#{p}-rob",{{y:0}},{{y:-8,duration:1.2,repeat:2,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_pre + 0.6:.2f});
""" + "".join(vida(f"{p}-g{k}", dur, (1.4 + k, 4.6 + k * 0.5, 7.3 + k * 0.3)) for k in range(3))
    return cena(p, dur, svg, html, js, extra, seed=6)


# ================================================================ robo 7: Giancarlo Guizzardi e o livro
def robo_7():
    p, C, S = "robo_7", "robo", 7
    ini, dur = seg(C, S); T = T_(C, S)
    t_cie, t_gia, t_gui, t_ufes, t_liv, t_tit = T("cientista"), T("giancarlo"), T("guitzardi"), T("ufis"), T("livro"), T("titulo")
    t_q, t_medo, t_rob, t_prop, t_sep, t_ia, t_real, t_faz, t_ima = T("quem"), T("medo"), T("robo"), T("proposta"), T("separar"), T("inteligencia"), T("realmente"), T("faz"), T("imagina")
    extra = (chao(p) + f'<linearGradient id="{p}-capa" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2c2380"/><stop offset="1" stop-color="#0f0b33"/></linearGradient>'
             f'<linearGradient id="{p}-pag" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e9dcc2"/><stop offset="1" stop-color="#fffaf0"/></linearGradient>')
    livro = f"""<rect x="-246" y="-334" width="520" height="700" rx="12" fill="url(#{p}-pag)"/>
<g stroke="#bfb49a" stroke-width="2">{"".join(f'<line x1="262" y1="{-320 + j * 14}" x2="270" y2="{-318 + j * 14}"/>' for j in range(48))}</g>
<polygon points="-260,-350 -300,-330 -300,370 -260,350" fill="#1a1450" stroke="#8d7bff" stroke-width="4"/>
<rect x="-260" y="-350" width="520" height="700" rx="14" fill="url(#{p}-capa)" stroke="#ff4fa3" stroke-width="6" filter="url(#{p}-sombra)"/>
<rect x="-230" y="-320" width="460" height="640" rx="8" fill="none" stroke="#ff4fa3" stroke-width="2" opacity=".5"/>
{srise(p + "-c1", 0, -232, "Quem tem", 70, "#ffe9c4")}{srise(p + "-c2", 0, -158, "medo do", 70, "#ffe9c4")}{srise(p + "-c3", 0, -84, "robô mau?", 70, "#ff9fb5")}
<g transform="translate(0 176) scale(.42)"><g id="{p}-crob">{robo(p + "c", p + "-glow")}</g></g>"""
    # lado da direita do mundo (aparece depois de "separar"): o que faz x o que a gente imagina
    X = 1920
    barras = "".join(f'<rect id="{p}-bar{k}" x="{X + 200}" y="{430 + k * 62}" width="{w}" height="40" rx="10" fill="{CIANO}" opacity="{1 - k * 0.2:.1f}"/>'
                     for k, w in enumerate((440, 290, 170, 90)))
    monitor = (f'<rect x="{X + 150}" y="260" width="660" height="440" rx="26" fill="#0e0c26" stroke="#8d7bff" stroke-width="7" filter="url(#{p}-sombra)"/>'
               f'<rect x="{X + 200}" y="306" width="380" height="20" rx="10" fill="#8d7bff" opacity=".6"/><rect x="{X + 200}" y="346" width="260" height="20" rx="10" fill="#8d7bff" opacity=".6"/>'
               f'<rect id="{p}-cur" x="{X + 476}" y="340" width="14" height="32" fill="{CIANO}"/>{barras}'
               f'<rect x="{X + 440}" y="700" width="80" height="60" fill="#2a1d70"/><rect x="{X + 340}" y="756" width="280" height="22" rx="11" fill="#2a1d70"/>')
    rng = random.Random(71)
    estante = '<rect x="1170" y="220" width="710" height="660" rx="10" fill="#1a1450" stroke="#3a2f8a" stroke-width="5"/>'
    for yb in (400, 580, 760):
        x = 1190
        while x < 1850:
            w, h = rng.randint(22, 40), rng.randint(110, 160)
            estante += f'<rect x="{x}" y="{yb - h}" width="{w}" height="{h}" rx="4" fill="{rng.choice([CIANO, LILAS, MAGENTA, AMBAR, MENTA, "#6a8cff"])}" opacity=".5"/>'
            x += w + rng.randint(4, 10)
        estante += f'<rect x="1170" y="{yb}" width="710" height="14" fill="#3a2f8a"/>'
    guiz = gente_var(p + "-gz", "trabalho", "em_pe", glow=p + "-glow", cabelo="#b9b6c8", roupa=("#3a4a8a", "#2a3870"))
    nuvem = (f'<g id="{p}-nuv"><circle cx="{X + 1196}" cy="330" r="14" fill="#1c1a58" stroke="#8d7bff" stroke-width="4"/>'
             f'<circle cx="{X + 1240}" cy="292" r="22" fill="#1c1a58" stroke="#8d7bff" stroke-width="4"/>'
             f'<ellipse cx="{X + 1580}" cy="290" rx="320" ry="222" fill="#1c1a58" stroke="#8d7bff" stroke-width="6" filter="url(#{p}-sombra)"/>'
             f'<g transform="translate({X + 1580} 296) scale(.58)">{robo(p + "n", p + "-glow")}</g></g>')
    svg = f"""<rect x="-300" y="880" width="4600" height="400" fill="url(#{p}-ch)"/>
<g id="{p}-mundo">
<g opacity=".75">{estante}</g>
<g transform="translate(1070 905) scale(.8)"><g id="{p}-gzW" opacity="0">{guiz}</g></g>
<ellipse cx="1500" cy="930" rx="330" ry="22" fill="#05031a" opacity=".5"/>
<g transform="translate(1500 540)"><g id="{p}-livro" opacity="0">{livro}</g></g>
<rect id="{p}-div" x="{X + 957}" y="90" width="6" height="900" rx="3" fill="#eef1f7" filter="url(#{p}-glow)"/>
<g id="{p}-mon">{monitor}</g>
<g transform="translate({X + 1120} 900) scale(.82)"><g id="{p}-pesW">{gente_var(p + "p", "casa", "em_pe", glow=p + "-glow", pele=1, cabelo="#140c08", roupa=("#d0408a", "#a02a68"))}</g></g>
<g id="{p}-nuvW" opacity="0">{nuvem}</g>
{srise(p + "-s1", X + 530, 880, "REALMENTE FAZ", 80, "#bff4ff")}{srise(p + "-s2", X + 1600, 830, "IMAGINA", 92, "#ffb3c6")}
</g>"""
    html = (mono(f"{p}-t0", "O CIENTISTA DA COMPUTAÇÃO", "left:110px;top:250px", AMBAR, 44, dot=False) +
            texto(f"{p}-t1", "Giancarlo", "left:104px;top:330px;font-size:140px;color:#eef1f7") +
            texto(f"{p}-t2", "Guizzardi", "left:104px;top:480px;font-size:140px;color:#c9b8ff") +
            mono(f"{p}-t3", "UFES", "left:116px;top:700px", MENTA, 72))
    sai_js = "".join(f'some("#{p}-t{k}", {t_sep - 0.6:.2f}, 0.5);' for k in range(4))
    js = f"""
  camZ("#{p}-cam", 0, {t_tit:.2f}, 1.06, 1.0, 600, 540, "sine.inOut");
  camZ("#{p}-cam", {t_tit:.2f}, 1.5, 1.0, 1.32, 1460, 470);
  camZ("#{p}-cam", {t_prop - 0.2:.2f}, 1.0, 1.32, 1.0, 1460, 470);
  pop("#{p}-gzW", {t_cie:.2f}, 0.5, 0.8);
  tl.fromTo("#{p}-gz-olho",{{x:0,y:0}},{{x:3,y:1,duration:0.3}},{t_liv:.2f});
  tl.fromTo("#{p}-gz-braco",{{rotation:0,svgOrigin:"{piv("trabalho")}"}},{{rotation:-62,svgOrigin:"{piv("trabalho")}",duration:0.6,ease:"back.out(2)"}},{t_liv + 0.2:.2f});
  camZ("#{p}-cam", {t_sep + 1.2:.2f}, {dur - t_sep - 1.2:.2f}, 1.0, 1.05, 960, 560, "sine.inOut");
  rise("#{p}-t0 span", {t_cie:.2f}); rise("#{p}-t1 span", {t_gia:.2f}, 0.8); rise("#{p}-t2 span", {t_gui:.2f}, 0.8); rise("#{p}-t3 span", {t_ufes:.2f});
  tl.fromTo("#{p}-livro",{{opacity:0,y:-700,rotation:-18}},{{opacity:1,y:0,rotation:-4,duration:0.9,ease:"back.out(1.4)"}},{t_liv - 0.6:.2f});
  tl.fromTo("#{p}-livro",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.07,transformOrigin:"50% 50%",duration:0.25,repeat:1,yoyo:true,ease:"power2.out",immediateRender:false}},{t_liv + 0.3:.2f});
  tl.to("#{p}-livro",{{rotation:0,duration:1.0,ease:"sine.inOut"}},{t_tit:.2f});
  tl.fromTo("#{p}c-olhos",{{opacity:0.2}},{{opacity:1,duration:0.1,repeat:4,yoyo:true,ease:"steps(1)"}},{t_liv:.2f});
  sr("#{p}-c1", {t_q:.2f}, 92); sr("#{p}-c2", {t_medo:.2f}, 92); sr("#{p}-c3", {t_rob:.2f}, 92);
  {sai_js}
  tl.fromTo("#{p}-mundo",{{x:0}},{{x:-1920,duration:1.25,ease:"power3.inOut"}},{t_sep - 0.35:.2f});
  tl.fromTo("#{p}-div",{{scaleY:0,transformOrigin:"50% 0%"}},{{scaleY:1,transformOrigin:"50% 0%",duration:0.8,ease:"power2.inOut"}},{t_sep + 0.5:.2f});
  {"".join(f'tl.fromTo("#{p}-bar{k}",{{scaleX:0.05,transformOrigin:"0% 50%"}},{{scaleX:1,transformOrigin:"0% 50%",duration:0.6,ease:"power2.out"}},{t_ia + 0.18 * k:.2f});' for k in range(4))}
  tl.fromTo("#{p}-cur",{{opacity:1}},{{opacity:0,duration:0.25,repeat:13,yoyo:true,ease:"steps(1)"}},{t_ia + 0.4:.2f});
  sr("#{p}-s1", {t_real:.2f}, 104);
  tl.fromTo("#{p}-bar0",{{scaleX:1}},{{scaleX:1.12,duration:0.3,repeat:1,yoyo:true,immediateRender:false}},{t_faz:.2f});
  tl.fromTo("#{p}-nuvW",{{opacity:0,scale:0.4,transformOrigin:"20% 90%"}},{{opacity:1,scale:1,transformOrigin:"20% 90%",duration:0.8,ease:"elastic.out(1,0.5)"}},{t_ima - 0.25:.2f});
  tl.fromTo("#{p}n-olhos",{{opacity:0.2}},{{opacity:1,duration:0.1,repeat:4,yoyo:true,ease:"steps(1)"}},{t_ima + 0.5:.2f});
  sr("#{p}-s2", {t_ima:.2f}, 120);
  tl.fromTo("#{p}p-olho",{{x:0,y:0}},{{x:2,y:-3,duration:0.4}},{t_ima - 0.3:.2f});
""" + vida(p + "p", dur, (13.5, 15.4, 17.6)) + vida(p + "-gz", dur, (2.2, 4.4, 7.0)) + f'tl.fromTo("#{p}-crob",{{y:0}},{{y:-10,duration:0.9,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_tit + 1.4:.2f});'
    return cena(p, dur, svg, html, js, extra, seed=7)


# ================================================================ robo 8: quem decide são pessoas
def robo_8():
    p, C, S = "robo_8", "robo", 8
    ini, dur = seg(C, S); T = T_(C, S)
    t_sep, t_ima, t_nen, t_maq, t_mal = T("separacao"), T("imagem"), T("nenhum"), T("maquina"), T("malvada")
    t_lab, t_emp, t_pla, t_pes, t_dec, t_tes, t_mos, t_gua = T("laboratorios"), T("empresas"), T("plataformas"), T("pessoas"), T("decidiram"), T("testar"), T("mostrar"), T("guardar")
    extra = (chao(p, cor="#2a2878") + f'<linearGradient id="{p}-pr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c2a88"/><stop offset="1" stop-color="#16124a"/></linearGradient>'
             f'<clipPath id="{p}-cl"><rect x="-400" y="-400" width="400" height="800"/></clipPath><clipPath id="{p}-cr"><rect x="0" y="-400" width="400" height="800"/></clipPath>')

    def janelas(x0, y0, nc, nr, dx, dy, w, h, cls):
        out = ""
        for r in range(nr):
            for c in range(nc):
                x, y = x0 + c * dx, y0 + r * dy
                out += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#0e0c26"/><rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#ffe39a" opacity="0"/>'
        return out
    lab = (f'<g id="{p}-lab"><rect x="150" y="470" width="440" height="330" fill="url(#{p}-pr)" stroke="#8d7bff" stroke-width="5"/>'
           f'<polygon points="126,472 614,472 530,404 210,404" fill="#2a1d70" stroke="#8d7bff" stroke-width="5" stroke-linejoin="round"/>'
           f'{janelas(196, 516, 3, 2, 134, 104, 90, 70, p + "-jl")}<rect x="330" y="720" width="80" height="80" fill="#0e0c26" stroke="#8d7bff" stroke-width="4"/>'
           f'<g transform="translate(370 336)"><path d="M-46 30 L46 30 L60 50 Q66 64 50 64 L-50 64 Q-66 64 -60 50 Z" fill="{MENTA}" opacity=".35" id="{p}-liq"/>'
           f'<path d="M-30 -66 L30 -66 M-18 -66 L-18 -18 L-60 50 Q-66 64 -50 64 L50 64 Q66 64 60 50 L18 -18 L18 -66" fill="none" stroke="{MENTA}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round" filter="url(#{p}-glow)"/>'
           f'<g id="{p}-bol" opacity="0" fill="{MENTA}"><circle cx="-14" cy="20" r="8"/><circle cx="12" cy="0" r="6"/><circle cx="0" cy="-30" r="5"/></g></g></g>')
    emp = (f'<g id="{p}-emp"><rect x="740" y="300" width="440" height="500" fill="url(#{p}-pr)" stroke="{CIANO}" stroke-width="5"/>'
           f'<rect x="790" y="276" width="340" height="26" fill="#2a1d70" stroke="{CIANO}" stroke-width="4"/><line x1="960" y1="276" x2="960" y2="226" stroke="{CIANO}" stroke-width="5"/>'
           f'<circle id="{p}-ant" cx="960" cy="220" r="10" fill="{VERM}"/>'
           f'<rect x="784" y="334" width="352" height="190" rx="12" fill="#0e0c26" stroke="{CIANO}" stroke-width="5"/>'
           f'<g id="{p}-tela" opacity="0"><rect x="806" y="354" width="96" height="150" rx="8" fill="{MAGENTA}"/><rect x="914" y="354" width="96" height="150" rx="8" fill="{CIANO}"/><rect x="1022" y="354" width="96" height="150" rx="8" fill="{AMBAR}"/></g>'
           f'{janelas(790, 560, 4, 3, 90, 78, 60, 50, p + "-je")}</g>')
    leds = "".join(f'<rect class="{p}-led" x="{1372 + c * 140 + j * 30}" y="{482 + r * 36}" width="20" height="10" rx="3" fill="{CIANO if (r + j + c) % 3 else AMBAR}" opacity=".25"/>'
                   for c in range(3) for r in range(8) for j in range(3))
    racks = "".join(f'<rect x="{1360 + c * 140}" y="466" width="120" height="310" rx="8" fill="#0e0c26" stroke="#5a5ad0" stroke-width="3"/>' for c in range(3))
    pla = (f'<g id="{p}-pla"><rect x="1330" y="430" width="440" height="370" fill="url(#{p}-pr)" stroke="{MAGENTA}" stroke-width="5"/>'
           f'<rect x="1310" y="414" width="480" height="22" fill="#2a1d70" stroke="{MAGENTA}" stroke-width="4"/>'
           f'{racks}{leds}'
           f'<g transform="translate(1550 640)"><g id="{p}-cad" opacity="0"><path d="M-44 -30 L-44 -70 A44 44 0 0 1 44 -70 L44 -30" fill="none" stroke="{AMBAR}" stroke-width="16" filter="url(#{p}-glow)"/>'
           f'<rect x="-70" y="-34" width="140" height="110" rx="16" fill="{AMBAR}" stroke="#fff3c4" stroke-width="4"/><circle cy="10" r="14" fill="#5a3f1a"/><rect x="-5" y="12" width="10" height="34" fill="#5a3f1a"/></g></g></g>')
    pes = ""
    # quem decide: a pesquisadora de jaleco, o executivo de terno, o dev de moletom, cada um à esquerda do seu prédio
    tipos = [dict(variante="trabalho", pele=1, cabelo="#140c08"), dict(variante="trabalho", pele=0, roupa=("#2a2f5a", "#1c2048")),
             dict(variante="casa", pele=2, cabelo="#140c08", roupa=("#d0408a", "#a02a68"))]
    for k, cx in enumerate((168, 662, 1250)):
        pes += (f'<g transform="translate({cx} 862) scale(.7)"><g id="{p}-pw{k}" opacity="0">{gente_var(f"{p}{k}", glow=p + "-glow", **tipos[k])}</g></g>')
    rob = robo(p + "L", p + "-glow"), robo(p + "R", p + "-glow")
    svg = f"""<rect x="-300" y="800" width="2520" height="400" fill="url(#{p}-ch)"/>
<g id="{p}-pred" opacity="0">{lab}{emp}{pla}</g>
<g transform="translate(960 520) scale(1.2)"><g id="{p}-hL"><g clip-path="url(#{p}-cl)">{rob[0]}</g><path d="M0 -340 L-10 -200 L8 -60 L-8 80 L6 300" fill="none" stroke="#fff" stroke-width="7" stroke-linejoin="round" filter="url(#{p}-glow)"/></g>
<g id="{p}-hR"><g clip-path="url(#{p}-cr)">{rob[1]}</g><path d="M0 -340 L-10 -200 L8 -60 L-8 80 L6 300" fill="none" stroke="#fff" stroke-width="7" stroke-linejoin="round" filter="url(#{p}-glow)"/></g></g>
<line id="{p}-fenda" x1="960" y1="90" x2="960" y2="900" stroke="#ffffff" stroke-width="8" stroke-linecap="round" filter="url(#{p}-glow)" opacity="0"/>
{pes}"""

    def troca(i, cx, a, b, cor):
        sty = f"position:absolute;left:{cx - 300}px;width:600px;top:884px;height:1.3em;line-height:1.3em;overflow:hidden;text-align:center;{PLEX};font-size:64px;color:{cor};text-shadow:0 0 18px {cor}"
        return (f'<div style="{sty}"><span id="{p}-n{i}" style="display:block;position:absolute;left:0;right:0">{a}</span>'
                f'<span id="{p}-v{i}" style="display:block;position:absolute;left:0;right:0">{b}</span></div>')
    html = (troca(0, 370, "LABORATÓRIOS", "TESTAR", MENTA) + troca(1, 960, "EMPRESAS", "MOSTRAR", CIANO) + troca(2, 1550, "PLATAFORMAS", "GUARDAR", "#ff8ac4") +
            texto(f"{p}-t1", "PESSOAS", "left:0;right:0;text-align:center;top:40px;font-size:130px;color:#ffd98a"))
    acende = []
    for i, (t, sel) in enumerate(((t_lab, "lab"), (t_emp, "emp"), (t_pla, "pla"))):
        acende.append(f'tl.fromTo("#{p}-{sel}",{{opacity:0.3}},{{opacity:1,duration:0.35,immediateRender:false}},{t_lab + 0.12 * i:.2f});'
                      f'tl.fromTo("#{p}-{sel}",{{y:30}},{{y:0,duration:0.7,ease:"elastic.out(1,0.5)",immediateRender:false}},{t:.2f});'
                      f'rise("#{p}-n{i}", {t:.2f});')
    js = f"""
  camZ("#{p}-cam", 0, 3.0, 1.1, 1.0, 960, 520);
  camZ("#{p}-cam", 3.0, {dur - 3.0:.2f}, 1.0, 1.04, 960, 560, "sine.inOut");
  tl.fromTo("#{p}-hL",{{y:0}},{{y:-8,duration:1.0,repeat:1,yoyo:true,ease:"sine.inOut"}},0);
  tl.fromTo("#{p}-hR",{{y:0}},{{y:-8,duration:1.0,repeat:1,yoyo:true,ease:"sine.inOut"}},0);
  tl.fromTo("#{p}-fenda",{{opacity:1,scaleY:0,transformOrigin:"50% 0%"}},{{scaleY:1,transformOrigin:"50% 0%",duration:0.7,ease:"power2.inOut"}},{t_sep:.2f});
  some("#{p}-fenda", {t_ima + 0.2:.2f}, 0.4);
  tl.fromTo("#{p}-hL",{{x:0}},{{x:-360,duration:1.6,ease:"power3.out",immediateRender:false}},{t_ima:.2f});
  tl.fromTo("#{p}-hR",{{x:0}},{{x:360,duration:1.6,ease:"power3.out",immediateRender:false}},{t_ima:.2f});
  tl.fromTo("#{p}-pred",{{opacity:0}},{{opacity:0.3,duration:1.0}},{t_ima:.2f});
  tl.to(["#{p}L-olhos","#{p}R-olhos"],{{opacity:0,duration:0.12,repeat:4,yoyo:true,ease:"steps(1)"}},{t_maq:.2f});
  tl.to(["#{p}L-olhos","#{p}R-olhos"],{{opacity:0,duration:0.2}},{t_mal + 0.5:.2f});
  tl.to("#{p}-hL",{{x:-700,opacity:0,duration:0.7,ease:"power2.in"}},{t_mal + 0.4:.2f}); tl.to("#{p}-hR",{{x:700,opacity:0,duration:0.7,ease:"power2.in"}},{t_mal + 0.4:.2f});
  tl.set("#{p}-pred",{{opacity:1}},{t_lab - 0.01:.2f});
  tl.set(["#{p}-lab","#{p}-emp","#{p}-pla"],{{opacity:0.3}},{t_lab - 0.01:.2f});
  {"".join(acende)}
  tl.fromTo(".{p}-jl",{{opacity:0}},{{opacity:0.85,duration:0.2,stagger:0.04}},{t_lab + 0.05:.2f});
  tl.fromTo(".{p}-je",{{opacity:0}},{{opacity:1,duration:0.15,stagger:0.02}},{t_lab + 0.15:.2f});
  tl.fromTo(".{p}-led",{{opacity:0.25}},{{opacity:1,duration:0.1,stagger:{{each:0.003,from:"random"}}}},{t_lab + 0.25:.2f});
  tl.fromTo("#{p}-tela",{{opacity:0}},{{opacity:0.9,duration:0.3}},{t_lab + 0.15:.2f});
  tl.fromTo(".{p}-je",{{opacity:1}},{{opacity:0.4,duration:0.12,repeat:3,yoyo:true,ease:"steps(1)",immediateRender:false}},{t_emp:.2f});
  tl.fromTo(".{p}-led",{{opacity:1}},{{opacity:0.3,duration:0.1,repeat:3,yoyo:true,ease:"steps(1)",immediateRender:false}},{t_pla:.2f});
  rise("#{p}-t1 span", {t_pes:.2f}, 0.9);
  {"".join(f'pop("#{p}-pw{k}", {t_pes + 0.15 * k:.2f}, 0.4, 0.8);' for k in range(3))}
  {"".join(f'sai("#{p}-n{i}", {t:.2f}); rise("#{p}-v{i}", {t + 0.2:.2f});' for i, t in enumerate((t_tes, t_mos, t_gua)))}
  tl.fromTo("#{p}-liq",{{opacity:0.35}},{{opacity:1,duration:0.25,repeat:3,yoyo:true}},{t_tes:.2f});
  entra("#{p}-bol", {t_tes:.2f}, 0.2); tl.fromTo("#{p}-bol",{{y:0}},{{y:-40,duration:0.6,repeat:3,ease:"power1.out"}},{t_tes:.2f});
  tl.fromTo("#{p}-tela",{{opacity:0.9,scale:0.8,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.6,ease:"elastic.out(1,0.45)",immediateRender:false}},{t_mos:.2f});
  pop("#{p}-cad", {t_gua:.2f}, 1.8, 0.5);
  tl.to(".{p}-led",{{fill:"{AMBAR}",duration:0.3}},{t_gua + 0.2:.2f});
  tl.fromTo("#{p}-ant",{{opacity:1}},{{opacity:0.2,duration:0.3,repeat:{int(dur / 0.6) - 1},yoyo:true,ease:"steps(1)"}},0);
  {"".join(f'tl.fromTo("#{p}{k}-olho",{{x:0,y:0}},{{x:2,y:-3,duration:0.3,immediateRender:false}},{t_dec:.2f});' for k in range(3))}
""" + "".join(vida(f"{p}{k}", dur, (13.6 + k * 0.4, 15.8 + k * 0.3, 17.2)) for k in range(3))
    return cena(p, dur, svg, html, js, extra, seed=8)


# ================================================================ robo 9: quem segura a chave tem nome
def robo_9():
    p, C, S = "robo_9", "robo", 9
    ini, dur = seg(C, S); T = T_(C, S)
    t_rob, t_dis, t_quem, t_seg, t_cha, t_nom, t_end, t_mod = T("robo"), T("distracao"), T("quem"), T("segura"), T("chave"), T("nome"), T("endereco"), T("modelo")
    extra = (chao(p) + feixe_def(p) + f'<linearGradient id="{p}-fxr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VERM}" stop-opacity=".45"/><stop offset="1" stop-color="{VERM}" stop-opacity="0"/></linearGradient>'
             f'<linearGradient id="{p}-papel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#e9dcc2"/></linearGradient>')
    dono = dict(variante="trabalho", pele=0, roupa=("#2a2f5a", "#1c2048"))   # quem segura a chave: o mesmo da foto do crachá
    MAO = anc("trabalho")["mao_e"]   # mão do lado direito da tela; a chave vai atrás da pessoa e os dedos cobrem o topo da argola
    campo = lambda y, w: f'<rect x="1384" y="{y}" width="{w}" height="8" rx="4" fill="#bfb49a"/>'
    cracha = (f'<rect x="1100" y="430" width="720" height="470" rx="30" fill="url(#{p}-papel)" stroke="{AMBAR}" stroke-width="7" filter="url(#{p}-sombra)"/>'
              f'<rect x="1100" y="430" width="720" height="56" rx="28" fill="{AMBAR}"/><rect x="1100" y="458" width="720" height="28" fill="{AMBAR}"/>'
              f'<rect x="1420" y="404" width="80" height="44" rx="12" fill="#bfb49a" stroke="#8a7f68" stroke-width="4"/>'
              f'<rect x="1140" y="516" width="210" height="236" rx="16" fill="#14123a" stroke="#8d7bff" stroke-width="5"/>'
              f'<g clip-path="url(#{p}-foto)"><rect x="1140" y="516" width="210" height="236" fill="#3a2f8a"/>{retrato(p + "f", 1245, 646, 1.15, glow=p + "-glow", **dono)}</g>'
              f'{campo(612, 390)}{campo(712, 390)}<rect x="1140" y="862" width="640" height="8" rx="4" fill="#bfb49a"/>'
              f'{srise(p + "-r1", 1384, 584, "NOME", 50, "#2a1d70", fam="IBM Plex Mono", peso=600, anc="start", esp=6, contorno=False)}'
              f'{srise(p + "-r2", 1384, 684, "ENDEREÇO", 50, "#2a1d70", fam="IBM Plex Mono", peso=600, anc="start", esp=6, contorno=False)}'
              f'{srise(p + "-r3", 1140, 834, "MODELO DE NEGÓCIO", 50, "#a01a48", fam="IBM Plex Mono", peso=600, anc="start", esp=6, contorno=False)}')
    extra += f'<clipPath id="{p}-foto"><rect x="1140" y="516" width="210" height="236" rx="16"/></clipPath>'
    svg = f"""<rect x="-300" y="930" width="2520" height="400" fill="url(#{p}-ch)"/>
<polygon id="{p}-fr" points="300,-40 640,-40 800,930 140,930" fill="url(#{p}-fxr)"/>
<polygon id="{p}-fa" points="1090,-40 1410,-40 1650,930 850,930" fill="url(#{p}-fx)" opacity="0"/>
<ellipse cx="470" cy="932" rx="300" ry="20" fill="#05031a" opacity=".55"/>
<g transform="translate(470 600) scale(1.1)"><g id="{p}-rob"><g id="{p}-robS">{robo(p, p + "-glow")}</g></g></g>
<g transform="translate(-280 0)"><g id="{p}-ccW" opacity="0">{cracha}</g></g>
<ellipse cx="1716" cy="932" rx="130" ry="14" fill="#05031a" opacity=".55"/>
<g transform="translate(1700 930) scale(.82)"><g id="{p}-exW" opacity="0">
<g transform="translate({MAO[0] + 12:.1f} {MAO[1] + 32:.1f}) scale(1.1)"><g id="{p}-chave">{chave(p + "-glow")}</g></g>
{gente_var(p + "g", glow=p + "-glow", sombra=False, **dono)}</g></g>"""
    html = texto(f"{p}-t1", "DISTRAÇÃO", "left:100px;top:60px;font-size:130px;color:#ff8aa6")
    js = f"""
  camZ("#{p}-cam", 0, {t_quem:.2f}, 1.08, 1.0, 470, 600, "sine.inOut");
  camZ("#{p}-cam", {t_quem:.2f}, {dur - t_quem:.2f}, 1.0, 1.05, 1200, 660, "power2.inOut");
  tl.fromTo("#{p}-olhos",{{opacity:0.3}},{{opacity:1,duration:0.1,repeat:4,yoyo:true,ease:"steps(1)"}},{t_rob:.2f});
  tl.to("#{p}-robS",{{scale:0.62,transformOrigin:"50% 100%",duration:1.0,ease:"power3.inOut"}},{t_dis:.2f});
  tl.to("#{p}-rob",{{opacity:0.4,duration:0.8}},{t_dis + 0.3:.2f});
  tl.to("#{p}-olhos",{{opacity:0,duration:0.4}},{t_dis + 0.5:.2f});
  rise("#{p}-t1 span", {t_dis:.2f}, 0.8);
  tl.to("#{p}-fr",{{opacity:0,duration:0.6}},{t_quem - 0.3:.2f});
  tl.fromTo("#{p}-fa",{{opacity:0}},{{opacity:1,duration:0.7}},{t_quem - 0.2:.2f});
  tl.fromTo("#{p}-ccW",{{opacity:0,y:-900}},{{opacity:1,y:0,duration:0.9,ease:"bounce.out"}},{t_seg:.2f});
  tl.fromTo("#{p}-exW",{{opacity:0,x:260}},{{opacity:1,x:0,duration:0.7,ease:"power3.out"}},{t_quem - 0.2:.2f});
  tl.fromTo("#{p}-chave",{{rotation:-3,svgOrigin:"0 -30"}},{{rotation:-15,svgOrigin:"0 -30",duration:0.5,repeat:5,yoyo:true,ease:"sine.inOut"}},{t_cha:.2f});
  sr("#{p}-r1", {t_nom:.2f}, 66); sr("#{p}-r2", {t_end:.2f}, 66); sr("#{p}-r3", {t_mod:.2f}, 66);
""" + vida(p + "f", dur, (4.8, 7.2)) + vida(p + "g", dur, (3.2, 6.0))
    return cena(p, dur, svg, html, js, extra, fundo=("#2a1560", "#150d40", "#07061a"), seed=9)


# ================================================================ fechamento 0: então, quem tem a chave?
PL0 = (960, 400)   # centro da fechadura no fechamento 0


def fechamento_0():
    p, C, S = "fechamento_0", "fechamento", 0
    ini, dur = seg(C, S); T = T_(C, S)
    t_quem, t_cha = T("quem"), T("chave")
    svg = f"""<polygon id="{p}-feixe" points="700,-40 1220,-40 1360,820 560,820" fill="url(#{p}-fx)" opacity="0"/>
<ellipse cx="960" cy="690" rx="250" ry="24" fill="#05031a" opacity=".45"/>
<g transform="translate(420 400) rotate(-90) scale(2.2)"><g id="{p}-chave" opacity="0">{chave(p + "-glow")}</g></g>
<g transform="translate({PL0[0]} {PL0[1]})"><g id="{p}-placa" opacity="0">{placa(p, p + "-glow", 230)}</g></g>"""
    html = texto(f"{p}-t1", "QUEM TEM A CHAVE?", "left:0;right:0;text-align:center;top:760px;font-size:124px;color:#ffe9c4")
    js = f"""
  camZ("#{p}-cam", 0, {dur:.2f}, 1.0, 1.16, {PL0[0]}, {PL0[1]}, "sine.inOut");
  tl.fromTo("#{p}-feixe",{{opacity:0}},{{opacity:1,duration:0.6}},0.05);
  pop("#{p}-placa", 0.1, 0.6, 0.8);
  tl.fromTo("#{p}-chave",{{opacity:0,y:-220}},{{opacity:1,y:0,duration:0.9,ease:"power3.out"}},0.3);
  rise("#{p}-t1 span", {t_quem:.2f}, 0.8);
  tl.fromTo("#{p}-luz",{{opacity:0}},{{opacity:0.75,duration:0.25,repeat:1,yoyo:true}},{t_cha:.2f});
  tl.fromTo("#{p}-chave",{{x:0}},{{x:-10,duration:0.3,repeat:1,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_cha + 0.1:.2f});
"""
    return cena(p, dur, svg, html, js, feixe_def(p), fundo=("#2a1560", "#150d40", "#07061a"), seed=17)


# ================================================================ fechamento 1: a tecnologia chegou antes da pergunta
def cabeca_com_fechadura(p, tx, ty, s, r_pl=22):
    """A pessoa grande; a fechadura vai na nuca, sobre o cérebro. Devolve (svg, centro da placa, raio da placa em px)."""
    cx, cy = tx + 160 * s, ty + 82 * s
    return pessoa(p + "h", tx, ty, s, glow=p + "-glow"), (cx, cy), r_pl * s


def fechamento_1():
    p, C, S = "fechamento_1", "fechamento", 1
    ini, dur = seg(C, S); T = T_(C, S)
    t_mem, t_map, t_cer, t_ler, t_pen, t_esc, t_ve = T("memoria"), T("mapiar"), T("cerebro"), T("ler"), T("pensa"), T("escolher"), T("ve")
    t_tod, t_tec, t_che, t_ant, t_per, t_pri, t_con, t_dep, t_per2, t_pod = (T("todos"), T("tecnologia"), T("chegou"), T("antes"), T("pergunta"),
                                                                            T("primeiro"), T("consegue"), T("depois"), T("pergunta", 1), T("podia"))
    s, hx, hy = 3.1, 464, 146
    cab, (pcx, pcy), r = cabeca_com_fechadura(p, hx, hy, s)
    L = lambda u, v: (hx + u * s, hy + v * s)   # ponto local da pessoa -> tela
    bcx, bcy = L(192, 90)                       # centro do cérebro
    z0 = 230 / r
    sk = 2.2 / z0                     # escala da chave igual à do fechamento 0 no primeiro quadro
    kx = pcx + (420 - PL0[0]) / z0    # argola da chave no mesmo lugar relativo
    # malha (mapear) sobre o cérebro
    rng = random.Random(11)
    pts = []
    while len(pts) < 34:
        x, y = rng.uniform(-1, 1), rng.uniform(-1, 1)
        if x * x + y * y < 0.85:
            pts.append((bcx + x * 51.5 * s, bcy + y * 32 * s))
    lin = "".join(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}"/>'
                  for i, a in enumerate(pts) for b in pts[i + 1:] if (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 < 70 ** 2)
    malha = (f'<g id="{p}-malha" opacity="0"><g stroke="{CIANO}" stroke-width="2.5" opacity=".7">{lin}</g>'
             + "".join(f'<circle class="{p}-no" cx="{x:.0f}" cy="{y:.0f}" r="7" fill="{CIANO}" filter="url(#{p}-glow)"/>' for x, y in pts) + '</g>')
    ex, ey = L(257 + 9, 129)   # ponta da frente do olho (motor.pessoa: olho em 257,129, rx 9)
    tela = (f'<g id="{p}-tela" opacity="0"><path d="M{ex:.0f} {ey:.0f} L1450 410 M{ex:.0f} {ey:.0f} L1450 740" stroke="{MAGENTA}" stroke-width="4" stroke-dasharray="14 12" opacity=".8"/>'
            f'<rect x="1450" y="400" width="330" height="350" rx="22" fill="#0e0c26" stroke="{MAGENTA}" stroke-width="7" filter="url(#{p}-sombra)"/>'
            f'<rect x="1478" y="428" width="274" height="90" rx="10" fill="{MAGENTA}"/><rect x="1478" y="532" width="274" height="90" rx="10" fill="{CIANO}" opacity=".85"/>'
            f'<rect x="1478" y="636" width="274" height="90" rx="10" fill="{AMBAR}" opacity=".85"/></g>')
    ondas = "".join(f'<path id="{p}-on{k}" d="M{L(177, 50)[0] + k * 60:.0f} {L(177, 50)[1] - k * 6:.0f} q 30 -40 60 0 t 60 0 t 60 0 t 60 0" fill="none" stroke="{LILAS}" stroke-width="6" stroke-linecap="round" '
                    f'stroke-dasharray="300" stroke-dashoffset="300" filter="url(#{p}-glow)" transform="translate(0 {-k * 40})"/>' for k in range(3))
    rot = [("ESCREVER", AMBAR), ("MAPEAR", CIANO), ("LER", LILAS), ("ESCOLHER", MAGENTA)]
    SIMB = {"ESCREVER": '<path d="M -22 22 L -18 6 L 12 -24 L 26 -10 L -4 20 Z" fill="#fff"/><path d="M -22 22 L -4 20 L -18 6 Z" fill="#05031a" opacity=".35"/>',
            "MAPEAR": '<g stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round"><circle r="24"/><path d="M -24 0 H 24 M 0 -24 V 24 M -14 -17 Q 0 0 -14 17 M 14 -17 Q 0 0 14 17"/></g>',
            "LER": '<path d="M -28 0 Q 0 -26 28 0 Q 0 26 -28 0 Z" fill="none" stroke="#fff" stroke-width="5"/><circle r="9" fill="#fff"/>',
            "ESCOLHER": '<path d="M -24 -2 L -8 16 L 26 -20" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>'}
    orbs_v = "".join(f'<g id="{p}-ob{k}" opacity="0"><g transform="translate(170 {300 + 150 * k})"><g id="{p}-obi{k}"><circle r="72" fill="{c}" fill-opacity=".38" stroke="{c}" stroke-width="6" filter="url(#{p}-glow)"/>'
                     f'<circle r="60" fill="{c}" fill-opacity=".25"/><circle cx="-22" cy="-26" r="11" fill="#fff" opacity=".5"/><g transform="scale(1.5)">{SIMB[w]}</g></g></g></g>' for k, (w, c) in enumerate(rot))
    # rótulos dentro da arte, ao lado dos orbes: em HTML ficavam fora da câmera e desalinhavam quando ela dava zoom
    rot_svg = "".join(f'<g id="{p}-l{k}"><circle id="{p}-ld{k}" cx="290" cy="{300 + 150 * k}" r="10" fill="{c}" opacity="0" filter="url(#{p}-glow)"/>'
                      + srise(f"{p}-lt{k}", 320, 300 + 150 * k + 20, w, 56, c, fam="IBM Plex Mono", peso=500, anc="start", esp=7.8, contorno=False) + '</g>'
                      for k, (w, c) in enumerate(rot))
    svg = f"""<ellipse cx="{L(200, 0)[0]:.0f}" cy="{L(0, 256)[1]:.0f}" rx="300" ry="20" fill="#05031a" opacity=".45"/>
<g id="{p}-pes">{cab}</g>
<circle id="{p}-flash" cx="{L(209, 92)[0]:.0f}" cy="{L(209, 92)[1]:.0f}" r="150" fill="{AMBAR}" opacity="0" filter="url(#{p}-blur40)"/>
<g transform="translate({L(220, 36)[0]:.0f} {L(220, 36)[1]:.0f})"><g id="{p}-raio" opacity="0">{bolt(0, 0, 1.5)}</g></g>
{malha}
<clipPath id="{p}-clc"><ellipse cx="{bcx:.0f}" cy="{bcy:.0f}" rx="{59 * s:.0f}" ry="{40 * s:.0f}"/></clipPath>
<g clip-path="url(#{p}-clc)"><rect id="{p}-scan" x="{L(127, 48)[0]:.0f}" y="{L(127, 48)[1]:.0f}" width="22" height="{88 * s:.0f}" fill="{LILAS}" opacity="0" filter="url(#{p}-glow)"/></g>
<g id="{p}-ondas">{ondas}</g>
{tela}{orbs_v}{rot_svg}
<g id="{p}-lockW"><g transform="translate({kx:.1f} {pcy:.1f}) rotate(-90) scale({sk:.4f})"><g id="{p}-chW"><g id="{p}-chave">{chave(p + "-glow")}</g></g></g>
<g transform="translate({pcx:.1f} {pcy:.1f}) scale({r / 230:.4f})">{placa(p + "b", p + "-glow", 230)}</g></g>
<g transform="translate(1540 880) scale(.64)"><g id="{p}-r1W" opacity="0">{gente_var(p + "-r1", "trabalho", glow=p + "-glow", pele=2, cabelo="#140c08")}</g></g>
<g transform="translate(1750 880) scale(.64)"><g id="{p}-r2W" opacity="0">{gente_var(p + "-r2", "casa", glow=p + "-glow", pele=1, cabelo="#c99a3a", roupa=("#2fa88a", "#1f8068"))}</g></g>
<g transform="translate(1730 330)"><g id="{p}-q" opacity="0"><text x="0" y="60" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="210" fill="{MAGENTA}" stroke="#05031a" stroke-width="12" paint-order="stroke" filter="url(#{p}-glow)">?</text></g></g>"""

    html = (texto(f"{p}-a1", "ANTES DA", "left:100px;top:230px;font-size:112px;color:#eef1f7") +
             texto(f"{p}-a2", "PERGUNTA", "left:100px;top:360px;font-size:112px;color:#ffb3c6") +
             mono(f"{p}-a3", "PRIMEIRO", "left:100px;top:560px", AMBAR, 60) +
             mono(f"{p}-a4", "DEPOIS", "left:100px;top:660px", MAGENTA, 60))
    tl_l = [0.0, t_map, t_ler, t_esc]
    js = f"""
  camZ("#{p}-cam", 0, 2.3, {z0:.3f}, 1.0, {pcx:.1f}, {pcy:.1f}, "power3.inOut");
  camZ("#{p}-cam", 2.4, {t_che - 2.6:.2f}, 1.0, 1.04, 1060, 520, "sine.inOut");
  camZ("#{p}-cam", {t_che + 0.2:.2f}, 1.6, 1.04, 1.16, {pcx:.1f}, {pcy:.1f});
  camZ("#{p}-cam", {t_dep - 0.2:.2f}, 1.4, 1.16, 1.0, 960, 500);
  {"".join(f'sr("#{p}-lt{k}", {t:.2f}, 73); tl.fromTo("#{p}-ld{k}",{{opacity:0}},{{opacity:1,duration:0.3}},{t:.2f}); pop("#{p}-ob{k}", {t:.2f}, 0.5, 0.8);' for k, t in enumerate(tl_l))}
  tl.to("#{p}-lockW",{{opacity:0,duration:0.5}},2.0);
  tl.to("#{p}-pes",{{opacity:0.35,duration:0.5}},{t_tec - 0.4:.2f});
  tl.to("#{p}-malha",{{opacity:0,duration:0.4}},{t_tec - 0.4:.2f});
  tl.fromTo("#{p}-lockW",{{opacity:0}},{{opacity:1,duration:0.5,immediateRender:false}},{t_tec - 0.1:.2f});
  tl.fromTo("#{p}-raio",{{opacity:0,y:-160}},{{opacity:1,y:0,duration:0.35,ease:"power4.in"}},{t_mem - 0.3:.2f});
  tl.fromTo("#{p}-flash",{{opacity:0}},{{opacity:0.7,duration:0.2,repeat:1,yoyo:true}},{t_mem + 0.05:.2f});
  tl.to("#{p}-raio",{{opacity:0,duration:0.4}},{t_map:.2f});
  entra("#{p}-malha", {t_map:.2f}, 0.2);
  tl.fromTo(".{p}-no",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,transformOrigin:"50% 50%",duration:0.4,ease:"back.out(3)",stagger:0.03}},{t_map:.2f});
  tl.to("#{p}-malha",{{opacity:0.35,duration:0.5}},{t_ler:.2f});
  tl.fromTo("#{p}-scan",{{opacity:1,x:0}},{{x:{123 * s:.0f},duration:0.8,repeat:1,yoyo:true,ease:"sine.inOut"}},{t_ler:.2f});
  tl.to("#{p}-scan",{{opacity:0,duration:0.3}},{t_esc:.2f});
  {"".join(f'draw("#{p}-on{k}", {t_ler + 0.3 + 0.25 * k:.2f}, 0.8, 300);' for k in range(3))}
  pop("#{p}-tela", {t_esc:.2f}, 0.5, 0.8);
  tl.fromTo("#{p}h-olho",{{x:0}},{{x:3,duration:0.3}},{t_esc:.2f});
  {"".join(f'tl.fromTo("#{p}-l{k}",{{opacity:1}},{{opacity:0.35,duration:0.12,repeat:3,yoyo:true,ease:"steps(1)",immediateRender:false}},{t_tod + 0.12 * k:.2f});' for k in range(4))}
  tl.fromTo("#{p}-flash",{{opacity:0}},{{opacity:0.45,duration:0.3,repeat:1,yoyo:true,immediateRender:false}},{t_tod:.2f});
  {"".join(f'some("#{p}-l{k}", {t_tec - 0.2:.2f}, 0.4); some("#{p}-ob{k}", {t_tec - 0.2:.2f}, 0.4);' for k in range(4))}
  tl.to("#{p}-tela",{{opacity:0,duration:0.5}},{t_tec - 0.2:.2f}); tl.to("#{p}-ondas",{{opacity:0.25,duration:0.5}},{t_tec - 0.2:.2f});
  tl.to("#{p}-chW",{{y:{(pcx - kx - 130 * sk + 12) / sk:.1f},duration:0.7,ease:"power2.in"}},{t_che:.2f});
  rise("#{p}-a1 span", {t_ant:.2f}, 0.8); rise("#{p}-a2 span", {t_per:.2f}, 0.8);
  rise("#{p}-a3 span", {t_pri:.2f});
  tl.fromTo("#{p}-chave",{{scaleX:1,transformOrigin:"50% 50%"}},{{scaleX:0.12,duration:0.45,ease:"power2.inOut"}},{t_con - 0.2:.2f});
  tl.fromTo("#{p}b-luz",{{opacity:0}},{{opacity:1,duration:0.4}},{t_con:.2f});
  tl.fromTo("#{p}-flash",{{opacity:0}},{{opacity:0.55,duration:0.5,immediateRender:false}},{t_con:.2f});
  some("#{p}-a1", {t_dep - 0.3:.2f}, 0.4); some("#{p}-a2", {t_dep - 0.3:.2f}, 0.4);
  rise("#{p}-a4 span", {t_dep:.2f});
  pop("#{p}-r1W", {t_pri:.2f}, 0.5, 0.8);
  tl.fromTo("#{p}-r1-braco",{{rotation:0,svgOrigin:"{piv("trabalho")}"}},{{rotation:-150,svgOrigin:"{piv("trabalho")}",duration:0.5,ease:"back.out(2)"}},{t_con:.2f});
  tl.fromTo("#{p}-r1W",{{y:0}},{{y:-40,duration:0.22,repeat:1,yoyo:true,ease:"power2.out",immediateRender:false}},{t_con + 0.1:.2f});
  pop("#{p}-r2W", {t_dep + 0.2:.2f}, 0.5, 0.8);
  tl.fromTo("#{p}-r2-olho",{{x:0,y:0}},{{x:1,y:-3,duration:0.3}},{t_per2:.2f});
  tl.fromTo("#{p}-q",{{opacity:0,y:-160,rotation:-30,transformOrigin:"50% 50%"}},{{opacity:1,y:0,rotation:0,transformOrigin:"50% 50%",duration:0.9,ease:"back.out(1.6)"}},{t_per2 - 0.2:.2f});
  tl.fromTo("#{p}-q",{{rotation:0}},{{rotation:-12,duration:0.25,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_pod:.2f});
""" + vida_pessoa(p + "h", dur, (1.2, 4.4, 8.3, 12.0, 15.2)) + vida(p + "-r1", dur, (12.9, 15.6)) + vida(p + "-r2", dur, (15.0,))
    return cena(p, dur, svg, html, js, fundo=("#2a1560", "#150d40", "#07061a"), seed=18)


# ================================================================ fechamento 2: direitos novos para a mente
def fechamento_2():
    p, C, S = "fechamento_2", "fechamento", 2
    ini, dur = seg(C, S); T = T_(C, S)
    t_pes, t_def, t_dir, t_nov = T("pesquisadores"), T("defendem"), T("direitos"), T("novos")
    t_pri, t_lib, t_int = T("privacidade"), T("liberdade"), T("integridade")
    t_odi, t_nin, t_ent, t_cab, t_sem, t_sab = T("direito", 1), T("ninguem"), T("entrar"), T("cabeca"), T("sem"), T("saber")
    # a pessoa em casa, na poltrona, com os quadros da vida na parede e as lembranças em volta da cabeça
    gx, gy, gs = 1250, 880, 1.1
    hc = anc("casa", "sentado")["cabeca_centro"]
    hx, hy = gx + hc[0] * gs, gy + hc[1] * gs      # centro da cabeça da pessoa sentada (para o mergulho)
    CX, CY = 1370, 540                              # centro do domo
    cores = (CIANO, LILAS, MENTA)
    aneis = "".join(f'<circle id="{p}-an{k}" cx="{CX}" cy="{CY}" r="{380 + 45 * k}" fill="none" stroke="{c}" stroke-width="{9 - k * 2}" '
                    f'stroke-dasharray="{6.2832 * (380 + 45 * k):.0f}" stroke-dashoffset="{6.2832 * (380 + 45 * k):.0f}" filter="url(#{p}-glow)" transform="rotate(-90 {CX} {CY})"/>'
                    for k, c in enumerate(cores))
    domo = (f'<radialGradient id="{p}-dom" cx="50%" cy="50%" r="50%"><stop offset=".7" stop-color="{CIANO}" stop-opacity="0"/><stop offset="1" stop-color="{CIANO}" stop-opacity=".22"/></radialGradient>'
            f'<linearGradient id="{p}-par" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c2380"/><stop offset="1" stop-color="#1a1450"/></linearGradient>')
    sala = (f'<rect x="900" y="130" width="940" height="700" rx="18" fill="url(#{p}-par)" stroke="#5a4ad0" stroke-width="4"/>'
            f'<polygon points="900,830 1840,830 1900,985 840,985" fill="#2a2060" stroke="#5a4ad0" stroke-width="4" stroke-linejoin="round"/>'
            f'<ellipse cx="1310" cy="905" rx="330" ry="48" fill="{MAGENTA}" opacity=".18"/>'
            f'<g transform="translate(990 830)"><rect x="-34" y="-70" width="68" height="70" rx="10" fill="#8a5a3a"/>'
            f'<path d="M 0 -70 Q -60 -150 -40 -230 M 0 -70 Q 10 -170 0 -260 M 0 -70 Q 60 -140 50 -220" stroke="{MENTA}" stroke-width="14" fill="none" stroke-linecap="round" opacity=".85"/></g>'
            + quadro(p + "-q0", "familia", 1080, 250, .62) + quadro(p + "-q1", "aniversario", 1290, 235, .5)
            + quadro(p + "-q2", "formatura", 1480, 260, .6, rot=2) + quadro(p + "-q3", "praia", 1690, 245, .58, rot=-2))
    orbes = [("coracao", 1480, 470, MAGENTA), ("bolo", 1620, 410, AMBAR), ("nota", 1740, 540, LILAS), ("sol", 1590, 600, MENTA)]
    orb = "".join(f'<g transform="translate(0 0)"><g id="{p}-ob{k}" opacity="0">{orbe(f"{p}-o{k}", sm, x, y, c, 44)}</g></g>' for k, (sm, x, y, c) in enumerate(orbes))
    svg = f"""<circle id="{p}-domo" cx="{CX}" cy="{CY}" r="470" fill="url(#{p}-dom)" opacity="0"/>
{sala}
<g transform="translate({gx} {gy}) scale({gs})"><g id="{p}-gW">{gente_var(p + "-g", "casa", "sentado", glow=p + "-glow")}</g></g>
{orb}
{aneis}"""
    cor_svg = corredor(p + "c", p + "-glow")
    cad = (f'<g transform="translate(960 530)"><g id="{p}-cad" opacity="0"><g transform="scale(.2)">{placa(p + "k", p + "-glow", 230)}</g></g></g>')
    html = (f'<svg id="{p}-cor" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;opacity:0">'
            f'<rect width="1920" height="1080" fill="#05041a"/><g id="{p}-corz">{cor_svg}{cad}</g><rect width="1920" height="1080" fill="url(#{p}-vig)"/>'
            f'<linearGradient id="{p}-faixa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05041a" stop-opacity=".97"/><stop offset=".7" stop-color="#05041a" stop-opacity=".82"/><stop offset="1" stop-color="#05041a" stop-opacity="0"/></linearGradient>'
            f'<rect id="{p}-faixaR" width="1920" height="380" fill="url(#{p}-faixa)" opacity="0"/></svg>')
    html += (mono(f"{p}-t0", "PESQUISADORES", "left:90px;top:130px", AMBAR, 72) +
             texto(f"{p}-t1", "DIREITOS", "left:90px;top:100px;font-size:120px;color:#eef1f7") +
             texto(f"{p}-t2", "NOVOS", "left:90px;top:236px;font-size:120px;color:#ffd98a") +
             mono(f"{p}-l0", "PRIVACIDADE MENTAL", "left:90px;top:440px", CIANO, 50) +
             mono(f"{p}-l1", "LIBERDADE COGNITIVA", "left:90px;top:540px", LILAS, 50) +
             mono(f"{p}-l2", "INTEGRIDADE DA MENTE", "left:90px;top:640px", MENTA, 50) +
             texto(f"{p}-t3", "SEM VOCÊ SABER", "left:0;right:0;text-align:center;top:90px;font-size:124px;color:#ffe9c4"))
    js = f"""
  camZ("#{p}-cam", 0, {t_odi:.2f}, 1.08, 1.0, {CX}, {CY}, "sine.inOut");
  camZ("#{p}-cam", {t_odi:.2f}, 1.15, 1.0, 80.0, {hx:.1f}, {hy:.1f}, "power3.in");
  {"".join(f'pop("#{p}-ob{k}", {t_def + 0.25 * k:.2f}, 0.3, 0.8); tl.fromTo("#{p}-o{k}",{{y:0}},{{y:-12,duration:{1.3 + 0.2 * k:.1f},repeat:{int((t_odi - t_def) / (1.3 + 0.2 * k))},yoyo:true,ease:"sine.inOut"}},{t_def + 0.8 + 0.25 * k:.2f});' for k in range(len(orbes)))}
  tl.fromTo("#{p}-g-olho",{{x:0,y:0}},{{x:2,y:-3,duration:0.4}},{t_def + 0.3:.2f});
  rise("#{p}-t0 span", {t_pes:.2f}); sai("#{p}-t0 span", {t_dir - 0.35:.2f});
  rise("#{p}-t1 span", {t_dir:.2f}, 0.8); rise("#{p}-t2 span", {t_nov:.2f}, 0.8);
  entra("#{p}-domo", {t_pri:.2f}, 0.8);
  {"".join(f'draw("#{p}-an{k}", {t:.2f}, 1.0, {6.2832 * (380 + 45 * k):.0f}); rise("#{p}-l{k} span", {t:.2f});' for k, t in enumerate((t_pri, t_lib, t_int)))}
  {"".join(f'some("#{p}-{n}", {t_odi - 0.25:.2f}, 0.35);' for n in ("t1", "t2", "l0", "l1", "l2", "domo", "an0", "an1", "an2"))}
  tl.fromTo("#{p}-cor",{{opacity:0}},{{opacity:1,duration:0.35}},{t_odi + 1.1:.2f});
  tl.fromTo("#{p}-corz",{{scale:1,svgOrigin:"960 530"}},{{scale:3.3,svgOrigin:"960 530",duration:{dur - t_odi - 0.8:.2f},ease:"sine.inOut"}},{t_odi + 0.8:.2f});
  tl.fromTo("#{p}c-nevoa",{{opacity:0.7}},{{opacity:1,duration:0.8,repeat:5,yoyo:true,ease:"sine.inOut"}},{t_odi:.2f});
  tl.fromTo(".{p}c-led",{{opacity:1}},{{opacity:0.15,duration:0.18,repeat:12,yoyo:true,ease:"steps(1)",stagger:{{each:0.0105,from:"random"}}}},{t_odi + 0.8:.2f});
  tl.fromTo("#{p}c-pluzg",{{scaleX:1,transformOrigin:"50% 50%"}},{{scaleX:0.04,transformOrigin:"50% 50%",duration:0.9,ease:"power3.inOut"}},{t_sem:.2f});
  pop("#{p}-cad", {t_sab - 0.3:.2f}, 0.4, 0.8);
  entra("#{p}-faixaR", {t_sem - 0.3:.2f}, 0.4); rise("#{p}-t3 span", {t_sem:.2f}, 0.8);
""" + vida(p + "-g", dur, (1.4, 4.6, 7.4, 9.9), "sentado")
    return cena(p, dur, svg, html, js, domo, fundo=("#2a1560", "#150d40", "#07061a"), seed=19)


CENAS = [(k, f, seg(c, i)[1]) for k, f, c, i in [
    ("robo_5", robo_5, "robo", 5), ("robo_6", robo_6, "robo", 6), ("robo_7", robo_7, "robo", 7),
    ("robo_8", robo_8, "robo", 8), ("robo_9", robo_9, "robo", 9),
    ("fechamento_0", fechamento_0, "fechamento", 0), ("fechamento_1", fechamento_1, "fechamento", 1),
    ("fechamento_2", fechamento_2, "fechamento", 2)]]
MAPA = {("robo", 5): "robo_5", ("robo", 6): "robo_6", ("robo", 7): "robo_7", ("robo", 8): "robo_8", ("robo", 9): "robo_9",
        ("fechamento", 0): "fechamento_0", ("fechamento", 1): "fechamento_1", ("fechamento", 2): "fechamento_2"}

if __name__ == "__main__":
    print(escreve_cenas(CENAS, AQUI))
