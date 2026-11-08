"""Grupo g6: realidade 2, 3, 4, 7, 8 e robo 0 a 4 no padrão v5.

  python3 build_g6_realidade_robo1.py      # escreve compositions/, index.html e tempos.json nesta pasta
"""
import os, sys, random, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from motor import *
from arte2 import mosca_defs, mosca_rica
from gente import gente, vida_gente, quadro, orbe, PELE, CABELO, CASA, TRAB, ANCORAS
from motor import composicao as _composicao_motor

AQUI = os.path.dirname(os.path.abspath(__file__))  # depois do import: motor também exporta AQUI (raiz de cenas-v5)

MONO = "font-family:'IBM Plex Mono',monospace;font-weight:500;letter-spacing:.14em"
T_ = lambda ce, sg: (lambda w, n=0: _hit(ce, sg, w, n))


def _hit(ce, sg, w, n=0):
    """palavra() que falha alto se a palavra não estiver no segmento (o fallback proporcional esconde erro)."""
    t = palavra(ce, sg, w, n, padrao=-1)
    assert t >= 0, f"palavra '{w}' não achada em {ce} {sg}"
    return t


# ------------------------------------------------------------------ gente de verdade (rodada 2)
PELES = [PELE, "#c68a5e", "#8d5a3a", "#e8b48a"]


def pessoa_v(p, var="casa", pose="em_pe", torso=None, calca=None, pele=0, cabelo=None, **kw):
    """gente() com roupa, pele e cabelo trocados pelo hex base de cada peça (sombra e luz são camadas neutras por cima)."""
    v = CASA if var == "casa" else TRAB
    s = gente(p, var, pose, **kw)
    for velho, novo in ((v["torso"], torso), (v["calca"], calca), (PELE, PELES[pele] if pele else None), (CABELO, cabelo)):
        if novo:
            s = s.replace(velho, novo)
    return s


def em(x, y, s, conteudo, esq=False, id_=None, op=None):
    """Posiciona arte de pés na origem: grupo externo estático, interno com id para o GSAP."""
    o = f' opacity="{op}"' if op is not None else ""
    g = f'<g transform="translate({x} {y}) scale({-s if esq else s} {s})">{conteudo}</g>'
    return f'<g id="{id_}"{o}>{g}</g>' if id_ else g


# Origens fixas (coordenadas locais da gente, giro 30) para girar/escalar peças do corpo. transformOrigin em % mede a caixa
# do grupo no GSAP e, com o desenho novo, sai uma caixa errada: a cabeça some ao girar e o tronco descola ao respirar.
ORIG = {"sentado": dict(nuca="-5 -345", olho="2 -388", tor="0 -161"), "em_pe": dict(nuca="0 -447", olho="7 -490", tor="3 -265")}


def vida(p, dur, piscadas=(2.0, 5.3, 8.8, 12.1, 16.4, 20.2), pose="em_pe"):
    """vida_gente com svgOrigin no lugar de transformOrigin (respira, balança a cabeça no -cabW, pisca)."""
    o = ORIG[pose]
    js = vida_gente(p, dur, ())
    js = js.replace('transformOrigin:"50% 100%"', f'svgOrigin:"{o["tor"]}"')
    for t in piscadas:
        if t < dur - 0.3:
            js += f'tl.fromTo("#{p}-olho",{{scaleY:1,svgOrigin:"{o["olho"]}"}},{{scaleY:0.08,svgOrigin:"{o["olho"]}",duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t});'
    return js


# variações de roupa para multidões (a 0 é a pessoa protagonista, moletom lilás)
ROUPAS = [("casa", None, None, 0, None), ("trabalho", None, None, 1, None),
          ("casa", "#38e8a8", "#3a2a5a", 2, "#241711"), ("trabalho", "#ffb23e", "#2f3f9a", 3, "#c9a050"),
          ("casa", "#ff4fa3", "#232344", 1, "#8a3a2a"), ("trabalho", "#3be0ff", "#3a2a20", 2, "#3a2a20"),
          ("casa", "#ffd23e", "#4a2a6a", 3, "#241711")]


def povo_defs(p, s=0.15):
    """Defs #{p}-pg0..6: pessoas pequenas em pé, pés em (0,0), cada uma com roupa e pele diferentes."""
    return "".join(f'<g id="{p}-pg{k}"><g transform="scale({s})">{pessoa_v(f"{p}-pg{k}x", r[0], "em_pe", r[1], r[2], r[3], r[4], sombra=False)}</g></g>'
                   for k, r in enumerate(ROUPAS))


def multidao(p, cols, lins, ex, ey, cx, cy, cls="m", pular=(), seed=1, offset=True):
    """Grade de pessoas pequenas (pés na linha). Fileira de trás primeiro para a da frente cobrir."""
    rr = random.Random(seed)
    out = []
    for j in range(lins):
        for i in range(cols):
            if (j, i) in pular:
                continue
            x = cx + (i - (cols - 1) / 2) * ex + (ex / 2 if offset and j % 2 else 0)
            out.append(f'<g transform="translate({x:.0f} {cy + (j - (lins - 1) / 2) * ey:.0f})"><use class="{cls}" href="#{p}-pg{rr.randint(1, 6)}"/></g>')
    return "".join(out)


# ------------------------------------------------------------------ peças compartilhadas
# dedos da mao_e da gente sentada (48.9,-190.7) por cima do objeto que cobre a caneca embutida no desenho
MAO = "".join(f'<rect x="{38 + k}" y="{-214 + k * 10}" width="26" height="11" rx="5.5" fill="{PELE}" stroke="#6a3b26" stroke-width="1.6"/>' for k in range(3))
def cubo(cx, cy, s, cor_t, cor_e, cor_d, traco, w=5, extra=""):
    top = f"M{cx} {cy - s} L{cx + s * 1.1} {cy - s * 0.45} L{cx} {cy + s * 0.1} L{cx - s * 1.1} {cy - s * 0.45} Z"
    esq = f"M{cx - s * 1.1} {cy - s * 0.45} L{cx} {cy + s * 0.1} L{cx} {cy + s} L{cx - s * 1.1} {cy + s * 0.55} Z"
    dir_ = f"M{cx + s * 1.1} {cy - s * 0.45} L{cx} {cy + s * 0.1} L{cx} {cy + s} L{cx + s * 1.1} {cy + s * 0.55} Z"
    return (f'<g {extra}><path d="{top}" fill="{cor_t}"/><path d="{esq}" fill="{cor_e}"/><path d="{dir_}" fill="{cor_d}"/>'
            f'<path d="{top} {esq} {dir_}" fill="none" stroke="{traco}" stroke-width="{w}" stroke-linejoin="round"/></g>')


def pessoa_dir(p, x0, y0, s, cena):
    """A pessoa olhando para a direita. Caixa final x0..x0+190s, y0..y0+224s."""
    return pessoa(p, x0 - 110 * s, y0 - 28 * s, s, glow=cena + "-glow")


def forum_janela(p, w=1100, h=700, linhas=9, esqueleto=False):
    """Janela de fórum reconstituída, centrada em (0,0). Ids: {p}-fl (linhas do post), {p}-fu (usuário), {p}-ft (título)."""
    x0, y0 = -w / 2, -h / 2
    ls = "".join(f'<rect class="fl" x="{x0 + 70}" y="{y0 + 330 + k * 38}" width="{(w - 140) * (0.62 if k % 4 == 3 else 0.95 - (k % 3) * 0.08):.0f}" height="16" rx="8" fill="#8d7bff" opacity=".55"/>' for k in range(linhas))
    sk = ls.replace('class="fl"', "") if esqueleto else ""
    return (f'<g filter="url(#{p}-sombra)"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="26" fill="#14123a" stroke="{LILAS}" stroke-width="6"/></g>'
            f'<rect x="{x0}" y="{y0}" width="{w}" height="96" rx="26" fill="#221e5c"/><rect x="{x0}" y="{y0 + 60}" width="{w}" height="36" fill="#221e5c"/>'
            f'<circle cx="{x0 + 50}" cy="{y0 + 48}" r="13" fill="{VERM}"/><circle cx="{x0 + 90}" cy="{y0 + 48}" r="13" fill="{AMBAR}"/><circle cx="{x0 + 130}" cy="{y0 + 48}" r="13" fill="{MENTA}"/>'
            f'<text x="{x0 + 190}" y="{y0 + 64}" font-family="IBM Plex Mono" font-weight="700" font-size="46" fill="#eef1f7" letter-spacing="4">LessWrong</text>'
            f'<text x="{-x0 - 50}" y="{y0 + 64}" text-anchor="end" font-family="IBM Plex Mono" font-weight="500" font-size="44" fill="{AMBAR}">2010</text>'
            f'<g id="{p}-fu"><circle cx="{x0 + 110}" cy="{y0 + 170}" r="44" fill="#2a2a8c" stroke="{CIANO}" stroke-width="5"/>'
            f'<circle cx="{x0 + 110}" cy="{y0 + 158}" r="15" fill="{CIANO}"/><path d="M{x0 + 84} {y0 + 196} q26 -26 52 0" fill="{CIANO}"/>'
            f'<text x="{x0 + 180}" y="{y0 + 186}" font-family="IBM Plex Mono" font-weight="700" font-size="50" fill="{CIANO}">Roko</text></g>'
            f'<g id="{p}-ft"><text x="{x0 + 70}" y="{y0 + 290}" font-family="EB Garamond" font-weight="700" font-size="62" fill="#eef1f7">experimento mental</text></g>'
            f'<g opacity=".18">{sk}</g><g id="{p}-fl">{ls}</g>')


def basilisco(p):
    """Criatura original: serpente-rei de neon (coroa de espinhos, um olho só com pupila em fenda, anéis do corpo atrás).
    Centrada em (0,0); cabeça ~ -330..330 x -360..300, corpo até ~ +-760 x 520.
    Ids: {p}-bcorpo (anéis), {p}-bcab (cabeça), {p}-bpal1/2 (pálpebras), {p}-bpu (pupila), {p}-biris, {p}-bolho (grupo do olho)."""
    bz = lambda t, a, b, c, d: (1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c + t ** 3 * d
    escamas = "".join(f'<path d="M{bz(t, -600, -300, 300, 600) - 30:.0f} {bz(t, 760, 520, 520, 760) - 50:.0f} q30 -24 60 0" fill="none" stroke="{MAGENTA}" stroke-width="5" opacity=".6"/>'
                      for t in [0.12 + k * 0.04 for k in range(20)])
    corpo = (f'<g id="{p}-bcorpo">'
             f'<path d="M-560 820 C-600 560 -380 520 -230 360 M560 820 C600 560 380 520 230 360" fill="none" stroke="#3a0f3a" stroke-width="120" stroke-linecap="round"/>'
             f'<path d="M-560 820 C-600 560 -380 520 -230 360 M560 820 C600 560 380 520 230 360" fill="none" stroke="{MAGENTA}" stroke-width="8" stroke-dasharray="46 22" filter="url(#{p}-glow)"/>'
             f'<path d="M-600 760 C-300 520 300 520 600 760" fill="none" stroke="#2a0a2e" stroke-width="150" stroke-linecap="round"/>'
             f'<path d="M-600 760 C-300 520 300 520 600 760" fill="none" stroke="{LILAS}" stroke-width="7" stroke-dasharray="50 24" filter="url(#{p}-glow)"/>{escamas}</g>')
    espinhos = "".join(f'<path d="M{x - 34} {-250 + abs(x) * 0.18:.0f} L{x + dx} {-250 - h + abs(x) * 0.18:.0f} L{x + 34} {-250 + abs(x) * 0.18:.0f} Z" fill="#2a0a2e" stroke="{AMBAR}" stroke-width="6" stroke-linejoin="round"/>'
                       for x, h, dx in [(-240, 90, -30), (-150, 140, -16), (-60, 190, -6), (0, 230, 0), (60, 190, 6), (150, 140, 16), (240, 90, 30)])
    cab_d = "M0 -280 C150 -280 300 -200 330 -60 C350 40 260 160 150 230 C90 270 40 300 0 300 C-40 300 -90 270 -150 230 C-260 160 -350 40 -330 -60 C-300 -200 -150 -280 0 -280 Z"
    cab = (f'<g id="{p}-bcab"><g filter="url(#{p}-glow)">{espinhos}</g>'
           f'<path d="{cab_d}" fill="url(#{p}-bpele)" stroke="{MAGENTA}" stroke-width="9" filter="url(#{p}-glow)"/>'
           f'<path d="M-250 -120 C-180 -60 -120 -70 -90 -40 M250 -120 C180 -60 120 -70 90 -40" fill="none" stroke="{MAGENTA}" stroke-width="6" opacity=".7"/>'
           f'<path d="M-200 110 Q-120 150 -60 120 M200 110 Q120 150 60 120 M-110 190 Q0 240 110 190" fill="none" stroke="{LILAS}" stroke-width="6" opacity=".7"/>'
           f'<path d="M-40 250 L-26 300 L-12 250 M40 250 L26 300 L12 250" fill="#fff" stroke="#ffd8e8" stroke-width="3"/>'
           f'<g id="{p}-bolho"><ellipse cx="0" cy="-10" rx="190" ry="120" fill="#0a0414" stroke="{AMBAR}" stroke-width="7" filter="url(#{p}-glow)"/>'
           f'<clipPath id="{p}-bcp"><ellipse cx="0" cy="-10" rx="186" ry="116"/></clipPath>'
           f'<g clip-path="url(#{p}-bcp)"><g id="{p}-bolhar"><circle id="{p}-biris" cx="0" cy="-10" r="106" fill="url(#{p}-biridg)"/>'
           f'<g transform="translate(0 -10)"><ellipse id="{p}-bpu" cx="0" cy="0" rx="20" ry="96" fill="#05020a"/></g>'
           f'<circle cx="34" cy="-52" r="16" fill="#fff" opacity=".85"/></g>'
           f'<rect id="{p}-bpal1" x="-200" y="-140" width="400" height="130" fill="#2a0a2e"/><rect id="{p}-bpal2" x="-200" y="-10" width="400" height="130" fill="#2a0a2e"/></g></g></g>')
    return corpo + cab


def basilisco_defs(p):
    return (f'<radialGradient id="{p}-bpele" cx="50%" cy="35%" r="75%"><stop offset="0" stop-color="#4a1050"/><stop offset="1" stop-color="#16061e"/></radialGradient>'
            f'<radialGradient id="{p}-biridg" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffe9a0"/><stop offset=".45" stop-color="{AMBAR}"/><stop offset=".8" stop-color="#ff4f7d"/><stop offset="1" stop-color="#5a0a20"/></radialGradient>'
            f'<radialGradient id="{p}-aura" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ff4fa3" stop-opacity=".45"/><stop offset="1" stop-color="#ff4fa3" stop-opacity="0"/></radialGradient>')


ESCURO = ("#2a0f3a", "#120828", "#05030f")

# camZ do motor faz tl.set(scale z0) no tempo 0 a cada chamada e o GSAP compensa a troca de svgOrigin (smoothOrigin),
# então a segunda e a terceira chamada deslocam a câmera. Esta versão só fixa o estado inicial na primeira chamada
# e desliga o smoothOrigin. Declarada depois de JS_LIB no mesmo escopo, ela substitui a do motor.
CAM = r"""
  function popO(sel,t,from,dur,o){
    tl.fromTo(sel,{scale:from||0.3,opacity:0,svgOrigin:o},{scale:1,opacity:1,svgOrigin:o,duration:dur||0.7,ease:"elastic.out(1,0.45)",immediateRender:false},t);
    tl.set(sel,{opacity:0},0);
  }
  function camZ(sel,t0,dur,z0,z1,ox,oy,ease){
    camZ.f=camZ.f||{};
    if(!camZ.f[sel]){camZ.f[sel]=1;tl.set(sel,{scale:z0,svgOrigin:ox+" "+oy,smoothOrigin:false},0);}
    var o={l:Math.log(z0)};
    tl.to(o,{l:Math.log(z1),duration:dur,ease:ease||"power3.inOut",onUpdate:function(){gsap.set(sel,{scale:Math.exp(o.l),svgOrigin:ox+" "+oy,smoothOrigin:false});},immediateRender:false},t0);
  }
"""


def composicao(i, dur, svg, html, js, extra="", **kw):
    return _composicao_motor(i, dur, svg, html, CAM + js, extra, **kw)


# ------------------------------------------------------------------ realidade 2: a página do Bostrom
def realidade_2():
    p, CE, SG = "realidade_2", "realidade", 2
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_cin, t_mas, t_ano, t_nick, t_arg, t_tir, t_sono = T("cinema"), T("Mas"), T("2003"), T("Nick"), T("argumento"), T("tirou"), T("sono")
    rr = random.Random(4)
    chuva = "".join(f'<rect x="{-520 + c * 44}" y="{-600 + r * 52 + rr.randint(0, 40)}" width="18" height="{rr.choice((22, 30, 38))}" rx="4" fill="{MENTA}" opacity="{rr.uniform(.2, .9):.2f}"/>'
                    for c in range(24) for r in range(24) if rr.random() < 0.55)
    fila = lambda y, xs: "".join(f'<rect x="{x - 64}" y="{y}" width="128" height="150" rx="34" fill="#0c0a26" stroke="#2a2878" stroke-width="4"/>' for x in xs)
    # a pessoa na poltrona do cinema, de pipoca na mão (coordenadas locais da gente, pés em 0)
    poltrona = ('<rect x="-128" y="-372" width="74" height="250" rx="30" fill="#3a1048" stroke="#7a2a6a" stroke-width="5"/>'
                '<rect x="-118" y="-168" width="236" height="52" rx="22" fill="#3a1048" stroke="#7a2a6a" stroke-width="5"/>')
    pipoca = ('<path d="M -14 -262 L 70 -262 L 60 -170 L -4 -170 Z" fill="#fff4e8" stroke="#e8d8c8" stroke-width="2"/>'
              '<path d="M 2 -262 L 10 -170 M 28 -262 L 28 -170 M 54 -262 L 46 -170" stroke="#ff4f7d" stroke-width="10"/>'
              + "".join(f'<circle cx="{cx}" cy="{cy}" r="13" fill="#fff3c4" stroke="#e8c070" stroke-width="2"/>' for cx, cy in ((-6, -266), (14, -276), (36, -272), (60, -264), (26, -288), (4, -284), (48, -282)))
              + MAO)
    espectador = em(290, 1040, 0.95, poltrona + gente(p + "s", "casa", "sentado", cadeira=False, sombra=False) + pipoca)
    poltronas = f'{fila(880, range(40, 1960, 150))}{espectador}{fila(960, range(-30, 1990, 160))}'
    # linhas do resumo na página (página 700 px de largura; imagem 1600 x 2264 -> fator .4375)
    f = 700 / 1600
    marcas = "".join(f'<rect class="mk" x="{326 * f:.1f}" y="{(648 + k * 41.2) * f:.1f}" width="{(1366 - 326) * f:.1f}" height="{38 * f:.1f}" rx="3" fill="{AMBAR}" opacity=".42"/>' for k in range(8))
    extra = (f'<radialGradient id="{p}-cone" cx="50%" cy="100%" r="100%"><stop offset="0" stop-color="#bff4ff" stop-opacity=".35"/><stop offset="1" stop-color="#bff4ff" stop-opacity="0"/></radialGradient>'
             f'<clipPath id="{p}-tela"><rect x="-540" y="-290" width="1080" height="580" rx="18"/></clipPath>'
             f'<radialGradient id="{p}-lua" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff3c4"/><stop offset="1" stop-color="#ffd27a"/></radialGradient>')
    svg = f"""
<g id="{p}-cine">
 <polygon points="960,1080 420,300 1500,300" fill="url(#{p}-cone)" opacity=".5"/>
 <g transform="translate(960 380)"><g filter="url(#{p}-sombra)"><rect x="-560" y="-310" width="1120" height="620" rx="26" fill="#0a0820" stroke="{LILAS}" stroke-width="8"/></g>
  <g id="{p}-telaL" opacity=".45"><g clip-path="url(#{p}-tela)"><rect x="-540" y="-290" width="1080" height="580" fill="#04140e"/><g id="{p}-chuva">{chuva}</g></g></g></g>
 <g id="{p}-polt">{poltronas}</g>
</g>
<g transform="translate(270 75) rotate(-2.5) scale(.9)"><g id="{p}-pag" opacity="0">
 <g filter="url(#{p}-sombra)"><rect x="-6" y="-6" width="712" height="1003" rx="8" fill="#fffaf0"/></g>
 <image href="assets/docs/bostrom2003.png" x="0" y="0" width="700" height="990.5"/>
 <g id="{p}-marcas" style="mix-blend-mode:multiply">{marcas}</g>
</g></g>
<g id="{p}-pw" opacity="0">
 <ellipse cx="1640" cy="1012" rx="320" ry="24" fill="#05031a" opacity=".55"/>
 <rect x="1650" y="500" width="230" height="240" rx="12" fill="#0a0e36" stroke="{LILAS}" stroke-width="7"/>
 <g id="{p}-lua" opacity="0"><circle cx="1790" cy="590" r="44" fill="url(#{p}-lua)" filter="url(#{p}-glow)"/><circle cx="1812" cy="578" r="39" fill="#0a0e36"/>
  <circle cx="1700" cy="560" r="4" fill="#fff"/><circle cx="1840" cy="690" r="3" fill="#fff"/><circle cx="1720" cy="680" r="3" fill="#fff"/></g>
 <path d="M1765 500 V740 M1650 620 H1880" stroke="{LILAS}" stroke-width="6"/>
 <rect x="1836" y="752" width="56" height="258" rx="16" fill="#2a1d70" stroke="{LILAS}" stroke-width="5"/>
 <rect x="1462" y="928" width="420" height="34" rx="10" fill="#1c1450" stroke="{LILAS}" stroke-width="4"/>
 <path d="M1490 960 V1006 M1860 960 V1006" stroke="{LILAS}" stroke-width="8" stroke-linecap="round"/>
 <rect x="1478" y="866" width="400" height="66" rx="20" fill="#5a5ab0"/>
 <ellipse cx="1800" cy="852" rx="56" ry="24" fill="#cfd0ff"/>
 <path d="M1600 862 H1876 V934 H1600 Q1578 900 1600 862 Z" fill="#3a3a9a"/><path d="M1620 876 H1860" stroke="#5a5ab0" stroke-width="5"/>
 {em(1560, 1008, 0.95, gente(p + "q", "casa", "sentado", cadeira=False, sombra=False), esq=True)}
</g>
"""
    html = (texto(f"{p}-t1", "2003", "left:1140px;top:90px;font-size:210px;color:#ffd98a", alt="1.15em") +
            texto(f"{p}-t2", "NICK BOSTROM", f"left:1150px;top:360px;font-size:66px;color:#bff4ff;{MONO}"))
    js = f"""
  camZ("#{p}-cam", 0, {t_mas:.2f}, 1.0, 1.08, 960, 380, "power1.inOut");
  tl.fromTo("#{p}-telaL",{{opacity:.45}},{{opacity:1,duration:0.5}},{t_cin - 0.3:.2f});
  tl.fromTo("#{p}-chuva",{{y:-260}},{{y:200,duration:{t_mas + 0.6:.2f},ease:"none"}},0);
  tl.fromTo("#{p}-cine",{{opacity:1,scale:1,svgOrigin:"960 540"}},{{opacity:0,scale:.7,svgOrigin:"960 540",duration:0.9,ease:"power3.in",immediateRender:false}},{t_mas - 0.1:.2f});
  tl.fromTo("#{p}-pag",{{opacity:0,y:700,rotation:-8}},{{opacity:1,y:0,rotation:0,duration:1.1,ease:"expo.out"}},{t_mas:.2f});
  rise("#{p}-t1 span", {t_ano:.2f}, 0.9);
  rise("#{p}-t2 span", {t_nick:.2f});
  tl.fromTo("#{p}-marcas .mk",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,transformOrigin:"0% 50%",duration:0.22,ease:"power2.inOut",stagger:0.12}},{t_arg:.2f});
  camZ("#{p}-cam", {t_arg - 0.2:.2f}, 1.0, 1.08, 1.75, 600, 380, "power3.inOut");
  some("#{p}-t1", {t_arg - 0.2:.2f}, 0.3); some("#{p}-t2", {t_arg - 0.2:.2f}, 0.3);
  camZ("#{p}-cam", {t_tir - 0.1:.2f}, 1.1, 1.75, 1.0, 600, 380, "power3.inOut");
  tl.to(["#{p}-t1","#{p}-t2"],{{opacity:1,duration:0.4}},{t_tir + 0.3:.2f});
  tl.set("#{p}s-cab",{{rotation:-7,svgOrigin:"-5 -345"}},0);
  tl.to("#{p}s-cab",{{svgOrigin:"-5 -345",rotation:-12,duration:0.5,ease:"back.out(2)"}},{t_cin:.2f});
  tl.fromTo("#{p}s-olho",{{scale:1,svgOrigin:"2 -388"}},{{scale:1.35,svgOrigin:"2 -388",duration:0.3,repeat:1,yoyo:true,immediateRender:false}},{t_cin + 0.1:.2f});
  tl.fromTo("#{p}-pw",{{opacity:0,y:60}},{{opacity:1,y:0,duration:0.8,ease:"expo.out"}},{t_tir:.2f});
  entra("#{p}-lua", {t_sono - 0.2:.2f}, 0.5);
  tl.fromTo("#{p}q-olho",{{scale:1,svgOrigin:"2 -388"}},{{scale:1.7,svgOrigin:"2 -388",duration:0.35,ease:"back.out(3)"}},{t_sono:.2f});
  tl.fromTo("#{p}q",{{x:0}},{{x:4,duration:0.06,repeat:11,yoyo:true,ease:"none",immediateRender:false}},{t_sono + 0.3:.2f});
""" + vida(p + "s", t_mas, (1.2, 3.4), "sentado") + vida(p + "q", dur, (), "sentado")
    return composicao(p, dur, svg, html, js, extra, seed=6)


# ------------------------------------------------------------------ realidade 3: as mentes se multiplicam
def sim_def(p, s=80, k=2.6):
    """Simulações: cubos de vidro com uma pessoa (antepassado) dentro. Defs #{p}-sim1..6 centradas em (0,0); precisa de povo_defs."""
    return "".join(f'<g id="{p}-sim{j}">{cubo(0, 0, s, "#4fd8ff1c", "#2a2a8c55", "#17175e55", CIANO, 4)}'
                   f'<g transform="translate(0 {s * 0.5:.0f}) scale({k / 2.6:.3f})"><use href="#{p}-pg{j}"/></g></g>' for j in range(1, 7))


def planeta(p, cx=960, cy=1500, r=900, n_torres=17, seed=2):
    rr = random.Random(seed)
    arco = lambda x: cy - math.sqrt(max(0, r * r - (x - cx) ** 2))
    torres = ""
    for k in range(n_torres):
        x = cx - 560 + k * 70 + rr.randint(-10, 10)
        h = rr.randint(50, 190) if abs(x - cx) > 60 else 0
        if h:
            yb = arco(x) + 12
            jan = "".join(f'<rect x="{x - 8 + (j % 2) * 12}" y="{yb - h + 14 + (j // 2) * 26:.0f}" width="7" height="11" fill="{AMBAR}" opacity=".8"/>' for j in range(2 * max(1, h // 30)))
            torres += f'<g class="tr"><rect x="{x - 22}" y="{yb - h:.0f}" width="44" height="{h}" rx="4" fill="#2a2878" stroke="{LILAS}" stroke-width="3"/>{jan}</g>'
    luzes = "".join(f'<circle class="lz" cx="{x:.0f}" cy="{y:.0f}" r="{rr.uniform(3, 7):.1f}" fill="{rr.choice((AMBAR, "#ffe9a0", CIANO))}"/>'
                    for x, y in [(cx + rr.uniform(-800, 800), cy - rr.uniform(500, 880)) for _ in range(260)] + [(cx + rr.uniform(-880, 880), cy + rr.uniform(-500, 880)) for _ in range(520)] if (x - cx) ** 2 + (y - cy) ** 2 < (r - 20) ** 2)
    return (f'<circle cx="{cx}" cy="{cy}" r="{r + 40}" fill="{CIANO}" opacity=".08" filter="url(#{p}-blur40)"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{p}-plan)" stroke="{CIANO}" stroke-width="6"/>'
            f'<g id="{p}-luzes">{luzes}</g><g id="{p}-torres">{torres}</g>'
            f'<g transform="translate({cx} {arco(cx)})"><g id="{p}-torreC"><path d="M-30 12 L-14 -110 L14 -110 L30 12 Z" fill="#2a2878" stroke="{CIANO}" stroke-width="4"/><circle cx="0" cy="-118" r="12" fill="{CIANO}" filter="url(#{p}-glow)"/></g></g>')


def realidade_3():
    p, CE, SG = "realidade_3", "realidade", 3
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_civ, t_sim, t_men, t_mos, t_esc, t_pod, t_mil, t_simu, t_ant = (T("civilização"), T("simular"), T("mentes"), T("mosca"), T("escala"),
                                                                     T("Epoderia"), T("milhões"), T("simulações"), T("antepassados"))
    extra = (povo_defs(p) + mosca_defs(p + "M") + sim_def(p) +
             f'<radialGradient id="{p}-plan" cx="45%" cy="20%" r="70%"><stop offset="0" stop-color="#3a3aa8"/><stop offset=".6" stop-color="#1c1a60"/><stop offset="1" stop-color="#0a0a2a"/></radialGradient>')
    # campo de simulações (aparece no recuo)
    campo, rc = [], random.Random(31)
    for gy in range(-760, 2300, 250):
        for gx in range(-1700, 3700, 260):
            x, y = gx + (gy // 250 % 2) * 130, gy
            if (x - 960) ** 2 + (y - 1500) ** 2 < 1050 ** 2 or (abs(x - 960) < 620 and -60 < y < 640):
                continue
            campo.append(f'<g transform="translate({x} {y})"><use class="sc" href="#{p}-sim{rc.randint(1, 6)}"/></g>')
    svg = f"""
<g id="{p}-campo">{''.join(campo)}</g>
<g id="{p}-plan">{planeta(p)}</g>
<g transform="translate(960 600)"><g id="{p}-feixe" opacity="0"><rect x="-9" y="-130" width="18" height="130" fill="{CIANO}" opacity=".85" filter="url(#{p}-glow)"/></g></g>
<g transform="translate(960 330)"><g id="{p}-cubo" opacity="0"><rect x="-200" y="-200" width="400" height="400" fill="none"/>
 {cubo(0, 0, 150, "#1e3a8add", "#2a2a8cee", "#17175eee", CIANO, 6, f'filter="url(#{p}-glow)"')}</g></g>
<g id="{p}-pw" opacity="0">{pessoa_dir(p + "s", 885, 235, 0.88, p)}</g>
<g transform="translate(470 380)"><g id="{p}-cuboM" opacity="0"><rect x="-150" y="-150" width="300" height="300" fill="none"/>
 {cubo(0, 0, 112, "#ffb23e1c", "#5a3a1a55", "#3a2a1055", AMBAR, 5, f'filter="url(#{p}-glow)"')}
 <g transform="translate(6 -6) scale(.6)">{mosca_rica(p + "-mosca", p + "M")}</g></g></g>
<g transform="translate(1450 380)"><g id="{p}-cuboR" opacity="0"><rect x="-150" y="-150" width="300" height="300" fill="none"/>
 {cubo(0, 0, 112, "#4fd8ff1c", "#2a2a8c55", "#17175e55", CIANO, 5, f'filter="url(#{p}-glow)"')}
 <g id="{p}-gradeR"><g transform="scale(.55)">{multidao(p, 5, 2, 80, 91, 0, 27, seed=3)}</g></g></g></g>
"""
    html = (texto(f"{p}-t1", "MILHÕES DE SIMULAÇÕES", "left:0;right:0;text-align:center;top:50px;font-size:104px;color:#eef1f7") +
            f'<div id="{p}-n" class="pill2" style="left:0;right:0;text-align:center;top:690px;font-size:92px;color:#ffd98a;opacity:0;font-weight:700">1</div>')
    js = f"""
  camZ("#{p}-cam", 0, {t_civ:.2f}, 1.25, 1.0, 960, 560, "power2.out");
  tl.fromTo("#{p}-torres .tr",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,transformOrigin:"50% 100%",duration:0.5,ease:"back.out(2)",stagger:0.11}},{max(0.4, t_civ - 1.6):.2f});
  tl.fromTo("#{p}-luzes .lz",{{opacity:0}},{{opacity:1,duration:0.2,stagger:{{amount:{t_civ + 1.2:.2f},from:"random"}}}},0.2);
  tl.fromTo("#{p}-torreC",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,transformOrigin:"50% 100%",duration:0.7,ease:"back.out(2)"}},{t_civ + 0.6:.2f});
  entra("#{p}-feixe", {t_sim:.2f}, 0.2);
  tl.fromTo("#{p}-feixe",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,transformOrigin:"50% 100%",duration:0.4,ease:"power2.out",immediateRender:false}},{t_sim:.2f});
  pop("#{p}-cubo", {t_sim + 0.2:.2f}, 0.4, 0.8);
  pop("#{p}-pw", {t_men:.2f}, 0.4, 0.8);
  pop("#{p}-cuboM", {t_mos - 0.2:.2f}, 0.4, 0.8);
  tl.fromTo("#{p}-mosca-asas",{{scaleY:1,transformOrigin:"50% 100%"}},{{scaleY:0.6,transformOrigin:"50% 100%",duration:0.05,repeat:11,yoyo:true,ease:"none",immediateRender:false}},{t_mos + 0.4:.2f});
  popO("#{p}-cuboR", {t_esc - 0.4:.2f}, 0.4, 0.8, "0 0");
  camZ("#{p}-cam", {t_esc:.2f}, 2.6, 1.0, 0.36, 960, 420, "power3.inOut");
  tl.fromTo("#{p}-campo .sc",{{scale:0,opacity:0,svgOrigin:"0 0"}},{{scale:1,opacity:1,svgOrigin:"0 0",duration:0.4,ease:"back.out(2)",stagger:{{amount:2.4,from:"center"}}}},{t_esc + 0.3:.2f});
  rise("#{p}-t1 span", {t_mil:.2f}, 0.9);
  entra("#{p}-n", {t_mil:.2f}, 0.3);
  contar("{p}-n", {t_mil:.2f}, {t_ant - t_mil + 0.6:.2f}, 1, 1000000, function(v){{return Math.round(v).toLocaleString("pt-BR");}});
  tl.fromTo("#{p}-campo",{{opacity:1}},{{opacity:0.55,duration:0.25,repeat:5,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_simu:.2f});
  camZ("#{p}-cam", {t_esc + 2.6:.2f}, {dur - t_esc - 2.6:.2f}, 0.36, 0.33, 960, 420, "none");
""" + vida_pessoa(p + "s", dur, (7.0, 10.0, 14.8))
    return composicao(p, dur, svg, html, js, extra, seed=11)


# ------------------------------------------------------------------ realidade 4: o trilema
def realidade_4():
    p, CE, SG = "realidade_4", "realidade", 4
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_pelo, t_tres, t_um, t_q1, t_ponto, t_dois, t_nao, t_tres2, t_q3, t_mentes, t_sua, t_simu = (
        T("pelo"), T("três"), T("Um", 1), T("quase"), T("ponto"), T("Dois"), T("não"), T("Três", 1), T("quase", 1), T("mentes"), T("sua"), T("simulação"))
    # legendas tiradas da fala (o "vis.itens" do roteiro parafraseia e o usuário rejeita texto diferente da narração)
    itens = ["Quase nenhuma civilização chega a esse ponto", "Não têm interesse em fazer essas simulações", "Quase todas as mentes como a sua estão dentro de uma simulação"]
    rr = random.Random(7)
    CX, CY, R = (400, 960, 1520), 540, 236
    extra = (povo_defs(p) + sim_def(p, 46, 1.5) +
             "".join(f'<clipPath id="{p}-cp{k}"><circle cx="{CX[k]}" cy="{CY}" r="{R - 6}"/></clipPath>' for k in range(3)) +
             f'<radialGradient id="{p}-plan" cx="45%" cy="25%" r="70%"><stop offset="0" stop-color="#3a3aa8"/><stop offset="1" stop-color="#0e0c3a"/></radialGradient>'
             f'<radialGradient id="{p}-dentro" cx="50%" cy="40%" r="60%"><stop offset="0" stop-color="#2a1e70"/><stop offset="1" stop-color="#0c0a26"/></radialGradient>')
    estrelas = lambda k: "".join(f'<circle cx="{CX[k] + rr.uniform(-220, 220):.0f}" cy="{CY + rr.uniform(-220, 120):.0f}" r="{rr.uniform(1.5, 3.5):.1f}" fill="#fff" opacity=".7"/>' for _ in range(24))
    # 1: planeta com cidade que se apaga
    c1 = CX[0]
    torres1 = "".join(f'<rect class="t1" x="{c1 - 120 + j * 34}" y="{CY - 40 - h}" width="26" height="{h}" rx="3" fill="#2a2878" stroke="{LILAS}" stroke-width="3"/>'
                      for j, h in enumerate((50, 90, 64, 120, 80, 100, 56, 74)))
    luzes1 = "".join(f'<circle class="l1" cx="{c1 + rr.uniform(-150, 150):.0f}" cy="{CY + rr.uniform(-20, 140):.0f}" r="5" fill="{AMBAR}"/>' for _ in range(40))
    p1 = (f'<circle cx="{c1}" cy="{CY + 150}" r="190" fill="url(#{p}-plan)" stroke="{CIANO}" stroke-width="5"/>'
          f'<g id="{p}-tor1">{torres1}</g><g id="{p}-luz1">{luzes1}</g>')
    # 2: servidor que não roda simulações
    c2 = CX[1]
    gav = "".join(f'<rect x="{c2 - 100}" y="{CY - 70 + j * 58}" width="200" height="46" rx="8" fill="#1c1a52" stroke="{LILAS}" stroke-width="3"/>'
                  f'<circle class="led" cx="{c2 + 74}" cy="{CY - 47 + j * 58}" r="8" fill="{MENTA}"/>' for j in range(5))
    sims2 = "".join(f'<use class="s2" href="#{p}-sim{j}" x="{c2 + dx}" y="{CY - 140 + dy}"/>' for j, (dx, dy) in zip((2, 4, 5), ((-110, 10), (0, -10), (110, 10))))
    p2 = (f'<rect x="{c2 - 120}" y="{CY - 90}" width="240" height="320" rx="14" fill="#0e0c2a" stroke="{CIANO}" stroke-width="5"/>{gav}'
          f'<g id="{p}-sims2">{sims2}</g>')
    # 3: multidão de pessoas (mentes como a sua) e você na frente, a pessoa protagonista
    c3 = CX[2]
    g3 = multidao(p, 9, 4, 58, 96, c3, CY + 40, cls="m3", pular=((3, 3), (3, 4), (2, 4), (2, 3)), seed=5)
    voce = (f'<g transform="translate({c3} {CY + 20})"><g id="{p}-voce"><ellipse cx="0" cy="40" rx="78" ry="120" fill="{AMBAR}" opacity=".32" filter="url(#{p}-blur6)"/>'
            f'{em(0, 120, 0.22, gente(p + "v", "casa", "em_pe", sombra=False))}</g></g>')
    p3 = f'<g id="{p}-g3">{g3}</g>{voce}'
    paineis = ""
    for k, conteudo in enumerate((p1, p2, p3)):
        paineis += (f'<g id="{p}-pn{k}" opacity="0"><circle cx="{CX[k]}" cy="{CY}" r="{R + 30}" fill="{CIANO}" opacity=".06" filter="url(#{p}-blur6)"/>'
                    f'<circle cx="{CX[k]}" cy="{CY}" r="{R}" fill="url(#{p}-dentro)"/>'
                    f'<g clip-path="url(#{p}-cp{k})">{estrelas(k)}{conteudo}</g>'
                    f'<circle id="{p}-aro{k}" cx="{CX[k]}" cy="{CY}" r="{R}" fill="none" stroke="{CIANO}" stroke-width="8" filter="url(#{p}-glow)"/>'
                    f'<g transform="translate({CX[k]} {CY - R - 16})"><g id="{p}-dg{k}"><circle r="56" fill="#14123a" stroke="{AMBAR}" stroke-width="6"/>'
                    f'<text y="26" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="80" fill="#ffd98a">{k + 1}</text></g></g></g>')
    svg = f'<g id="{p}-pan">{paineis}</g>'
    cap = "left:0;right:0;text-align:center;top:900px;font-size:76px;color:#eef1f7"
    html = (texto(f"{p}-t0", "PELO MENOS UMA DE TRÊS COISAS É VERDADE", f"left:0;right:0;text-align:center;top:60px;font-size:52px;color:#ffd98a;{MONO}") +
            texto(f"{p}-c0", itens[0], cap) + texto(f"{p}-c1", itens[1], cap) + texto(f"{p}-c2", itens[2], cap.replace("#eef1f7", "#ffd98a").replace("font-size:76px", "font-size:62px")))
    foco = lambda t, k, d=1.1: (f'tl.to("#{p}-pan",{{x:{(1 - k) * 560},duration:{d},ease:"power3.inOut"}},{t:.2f});' +
                                "".join(f'tl.to("#{p}-pn{j}",{{opacity:{1 if j == k else 0.28},duration:{d * 0.7:.2f}}},{t:.2f});' for j in range(3)))
    sai = lambda sel, t: f'tl.to("{sel} span",{{yPercent:-125,opacity:0,duration:0.45,ease:"power2.in"}},{t:.2f});'
    js = f"""
  camZ("#{p}-cam", 0, {t_um:.2f}, 1.06, 1.0, 960, 540, "power1.out");
  rise("#{p}-t0 span", {t_pelo:.2f}, 0.8);
  [0,1,2].forEach(function(k){{popO("#{p}-pn"+k, {t_pelo + 0.2:.2f}+k*0.25, 0.4, 0.8, {list(CX)}[k]+" {CY}");}});
  [0,1,2].forEach(function(k){{tl.fromTo("#{p}-dg"+k,{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,transformOrigin:"50% 50%",duration:0.6,ease:"elastic.out(1,0.45)",immediateRender:false}},{t_tres - 0.3:.2f}+k*0.25);}});
  {sai(f"#{p}-t0", t_um - 0.3)}
  camZ("#{p}-cam", {t_um:.2f}, 1.1, 1.0, 1.32, 960, 540);
  {foco(t_um, 0)}
  rise("#{p}-c0 span", {t_q1:.2f});
  tl.to("#{p}-luz1 .l1",{{opacity:0,duration:0.15,stagger:{{amount:1.0,from:"random"}}}},{t_ponto - 0.6:.2f});
  tl.to("#{p}-tor1 .t1",{{scaleY:0,transformOrigin:"50% 100%",duration:0.4,ease:"power2.in",stagger:0.08}},{t_ponto - 0.2:.2f});
  {sai(f"#{p}-c0", t_dois - 0.3)}
  {foco(t_dois, 1)}
  rise("#{p}-c1 span", {t_dois + 0.6:.2f});
  tl.fromTo("#{p}-sims2 .s2",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,transformOrigin:"50% 50%",duration:0.5,ease:"back.out(2)",stagger:0.15,immediateRender:false}},{t_dois + 0.4:.2f});
  tl.to("#{p}-sims2 .s2",{{scale:0,opacity:0,transformOrigin:"50% 50%",duration:0.35,ease:"back.in(2)",stagger:0.12}},{t_nao:.2f});
  tl.to("#{p}-pn1 .led",{{attr:{{fill:"#3a2a4a"}},duration:0.15,stagger:0.1}},{t_nao + 0.2:.2f});
  {sai(f"#{p}-c1", t_tres2 - 0.3)}
  {foco(t_tres2, 2)}
  rise("#{p}-c2 span", {t_q3:.2f});
  tl.fromTo("#{p}-g3 .m3",{{scale:0,svgOrigin:"0 0"}},{{scale:1,svgOrigin:"0 0",duration:0.3,ease:"back.out(2)",stagger:{{amount:1.0,from:"center"}},immediateRender:false}},{t_mentes - 0.3:.2f});
  tl.fromTo("#{p}-voce",{{scale:0,svgOrigin:"0 40"}},{{scale:1.6,svgOrigin:"0 40",duration:0.6,ease:"elastic.out(1,0.45)"}},{t_sua - 0.1:.2f});
  tl.fromTo("#{p}-voce",{{scale:1.6}},{{scale:1.25,duration:0.4,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_sua + 0.6:.2f});
  camZ("#{p}-cam", {t_simu - 0.3:.2f}, 1.2, 1.32, 1.0, 960, 540);
  tl.to("#{p}-pan",{{x:0,duration:1.2,ease:"power3.inOut"}},{t_simu - 0.3:.2f});
  tl.to(["#{p}-pn0","#{p}-pn1"],{{opacity:0.5,duration:0.8}},{t_simu - 0.3:.2f});
  tl.to("#{p}-aro2",{{attr:{{stroke:"#ffb23e"}},duration:0.5}},{t_simu:.2f});
""" + vida(p + "v", dur, (17.0, 19.4))
    return composicao(p, dur, svg, html, js, extra, seed=12)


# ------------------------------------------------------------------ realidade 7: o argumento não prova
def monitor(p, cx, cy):
    """Computador com um cérebro (a consciência que ele produziria) na tela. Caixa ~ cx-230..cx+230, cy-170..cy+238."""
    trilhas = "".join(f'<path d="M{cx + a} {cy + b} h{c} v{d}" fill="none" stroke="{CIANO}" stroke-width="3" opacity=".6"/><circle cx="{cx + a + c}" cy="{cy + b + d}" r="5" fill="{CIANO}"/>'
                      for a, b, c, d in ((-196, -110, 60, 30), (-196, 40, 50, -24), (196, -96, -58, 26), (196, 50, -46, -30), (-120, 96, 0, -20), (110, 96, 0, -24)))
    return (f'<g filter="url(#{p}-sombra)"><rect x="{cx - 230}" y="{cy - 170}" width="460" height="300" rx="22" fill="#14123a" stroke="{LILAS}" stroke-width="7"/></g>'
            f'<rect x="{cx - 206}" y="{cy - 146}" width="412" height="252" rx="10" fill="#08142a"/>'
            f'<clipPath id="{p}-tcp"><rect x="{cx - 206}" y="{cy - 146}" width="412" height="252" rx="10"/></clipPath>'
            f'<g id="{p}-tela" opacity=".25" clip-path="url(#{p}-tcp)">{trilhas}'
            f'<g transform="translate({cx} {cy - 34}) scale(1.3) translate(-192 -95)">{cerebro_lateral(p + "c")}</g></g>'
            f'<path d="M{cx - 40} {cy + 130} L{cx - 60} {cy + 220} L{cx + 60} {cy + 220} L{cx + 40} {cy + 130} Z" fill="#221e5c" stroke="{LILAS}" stroke-width="5"/>'
            f'<rect x="{cx - 140}" y="{cy + 216}" width="280" height="22" rx="11" fill="#221e5c" stroke="{LILAS}" stroke-width="5"/>')


def sala(p):
    """Sala de estar com quadros da vida na parede, sofá e abajur (a vida que talvez seja simulada)."""
    return (f'<rect x="-100" y="-100" width="2120" height="960" fill="#1a1046" opacity=".55"/>'
            f'<rect x="-100" y="860" width="2120" height="320" fill="#150d3a"/><path d="M-100 860 H2020" stroke="{LILAS}" stroke-width="6" opacity=".7"/>'
            f'<ellipse cx="1000" cy="950" rx="560" ry="62" fill="#3a1d7a" stroke="{LILAS}" stroke-width="4" opacity=".9"/>'
            f'<rect x="150" y="640" width="500" height="160" rx="44" fill="#4a2378"/><rect x="170" y="760" width="460" height="130" rx="28" fill="#5a2a8a"/>'
            f'<rect x="200" y="740" width="200" height="46" rx="20" fill="#6a3aa0"/><rect x="410" y="740" width="200" height="46" rx="20" fill="#6a3aa0"/>'
            f'<rect x="120" y="700" width="86" height="200" rx="34" fill="#4a2378"/><rect x="594" y="700" width="86" height="200" rx="34" fill="#4a2378"/>'
            f'<path d="M190 900 V930 M610 900 V930" stroke="#2a1450" stroke-width="12" stroke-linecap="round"/>'
            + quadro(f"{p}-qa", "familia", 330, 360, .9, -2) + quadro(f"{p}-qb", "praia", 640, 330, .8, 3) + quadro(f"{p}-qc", "cachorro", 1390, 340, .9, 2) +
            f'<polygon points="1660,540 1560,900 1840,900 1760,540" fill="{AMBAR}" opacity=".08"/>'
            f'<path d="M1710 540 V912" stroke="#c9b8ff" stroke-width="8"/><rect x="1650" y="904" width="120" height="16" rx="8" fill="#c9b8ff"/>'
            f'<path d="M1650 540 L1676 460 L1744 460 L1770 540 Z" fill="#ffd27a" stroke="{AMBAR}" stroke-width="4"/>')


def malha(p):
    """Malha de simulação sobre a sala: piso em perspectiva e paredes quadriculadas."""
    vx, vy = 960, 560
    k = (860 - vy) / (1180 - vy)  # linhas do piso começam no rodapé (y 860), não no ponto de fuga atrás da pessoa
    ls = [f'<line class="ml" x1="{vx + (x - vx) * k:.0f}" y1="860" x2="{x}" y2="1180" stroke="{CIANO}" stroke-width="3"/>' for x in range(-1400, 3400, 240)]
    ls += [f'<line class="ml" x1="-100" y1="{y}" x2="2020" y2="{y}" stroke="{CIANO}" stroke-width="3"/>' for y in (880, 920, 980, 1060)]
    ls += [f'<line class="ml" x1="{x}" y1="-100" x2="{x}" y2="860" stroke="{CIANO}" stroke-width="2.5"/>' for x in range(0, 1960, 160)]
    ls += [f'<line class="ml" x1="-100" y1="{y}" x2="2020" y2="{y}" stroke="{CIANO}" stroke-width="2.5"/>' for y in range(60, 860, 160)]
    return f'<g opacity=".6" filter="url(#{p}-glow)">{"".join(ls)}</g>'


def realidade_7():
    p, CE, SG = "realidade_7", "realidade", 7
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_at, t_nao, t_prova, t_simu, t_dep, t_apo, t_comp, t_cons, t_ning, t_sabe, t_poss = (
        T("atenção"), T("não"), T("prova"), T("simulação"), T("depende"), T("aposta"), T("computador"), T("consciência"), T("Eninguém"), T("sabe"), T("possível"))
    extra = f'<radialGradient id="{p}-moeda" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#ffe9a0"/><stop offset="1" stop-color="#d98a1e"/></radialGradient>'
    # caneca pela alça na mao_e da gente de pé (57.9,-227.4): alça antes do corpo (a mão cobre), corpo da caneca depois
    caneca = ('<path d="M 92 -246 q 22 0 20 18 q -2 14 -20 12" stroke="#fff4e8" stroke-width="8" fill="none"/>'
              '<rect x="48" y="-258" width="46" height="56" rx="9" fill="#fff4e8" stroke="#d8c8b0" stroke-width="3"/>'
              '<rect x="48" y="-236" width="46" height="10" fill="#ff4fa3" opacity=".8"/>'
              '<path d="M 62 -270 q -8 -12 0 -24 M 80 -270 q -8 -12 0 -24" stroke="#d9d0ff" stroke-width="4" fill="none" stroke-linecap="round" opacity=".7"/>')
    a1 = (f'<g id="{p}-sala">{sala(p)}{em(1000, 930, 0.82, caneca + gente(p + "s", "casa", "em_pe"))}</g>'
          f'<g id="{p}-malha" opacity="0">{malha(p)}</g>'
          f'<g id="{p}-caixa" opacity="0" filter="url(#{p}-glow)"><path d="M960 120 L1440 360 L1440 800 L960 1010 L480 800 L480 360 Z M480 360 L960 580 L1440 360 M960 580 L960 1010" fill="none" stroke="{CIANO}" stroke-width="10" stroke-linejoin="round" stroke-dasharray="40 26"/></g>'
          f'<rect id="{p}-faixa" x="-200" y="-200" width="2320" height="420" fill="#0b0a24" opacity="0"/>')
    a2 = (f'<ellipse cx="640" cy="905" rx="380" ry="28" fill="#05031a" opacity=".5"/>'
          f'<g transform="translate(640 560) scale(1.35)"><g id="{p}-mon">{monitor(p, 0, 0)}</g></g>'
          f'<g id="{p}-cerG" opacity="0"><circle cx="640" cy="514" r="150" fill="{MAGENTA}" opacity=".35" filter="url(#{p}-blur40)"/></g>'
          f'<path id="{p}-cabo" d="M955 600 C1080 700 1220 660 1330 540" fill="none" stroke="{CIANO}" stroke-width="8" stroke-dasharray="26 18" filter="url(#{p}-glow)" opacity="0"/>'
          f'<g transform="translate(1440 470) scale(1.3)"><g id="{p}-moeda" opacity="0"><circle r="88" fill="url(#{p}-moeda)" stroke="#fff3c4" stroke-width="6"/><circle r="64" fill="none" stroke="#b56a10" stroke-width="5"/>'
          f'<text y="26" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="80" fill="#8a4a08">?</text></g></g>'
          f'<ellipse cx="1730" cy="1004" rx="150" ry="16" fill="#05031a" opacity=".55"/>'
          f'<g id="{p}-rw">{em(1730, 1000, 0.8, gente(p + "r", "casa", "em_pe", sombra=False), esq=True)}</g>')
    svg = f'<g id="{p}-a1">{a1}</g><g id="{p}-a2" opacity="0">{a2}</g>'
    html = (texto(f"{p}-t1", "NÃO PROVA", "left:0;right:0;text-align:center;top:20px;font-size:170px;color:#ff4f7d") +
            texto(f"{p}-t2", "CONSCIÊNCIA", f"left:240px;width:800px;text-align:center;top:190px;font-size:64px;color:#ff9bd0;{MONO}"))
    js = f"""
  camZ("#{p}-cam", 0, {t_nao + 0.4:.2f}, 1.7, 1.0, 1000, 470, "power2.inOut");
  tl.fromTo("#{p}s-cab",{{rotation:0,svgOrigin:"0 -447"}},{{rotation:-9,svgOrigin:"0 -447",duration:0.5,ease:"back.out(2)"}},{t_at:.2f});
  tl.fromTo("#{p}s-olho",{{scale:1,svgOrigin:"7 -490"}},{{scale:1.4,svgOrigin:"7 -490",duration:0.3,repeat:1,yoyo:true,immediateRender:false}},{t_at + 0.1:.2f});
  tl.to("#{p}-sala",{{opacity:0.55,duration:0.5}},{t_nao:.2f});
  entra("#{p}-malha", {t_nao:.2f}, 0.3);
  tl.fromTo("#{p}-malha .ml",{{opacity:0}},{{opacity:1,duration:0.2,stagger:{{amount:0.6,from:"center"}}}},{t_nao:.2f});
  entra("#{p}-caixa", {t_nao + 0.2:.2f}, 0.4);
  tl.fromTo("#{p}-faixa",{{opacity:0}},{{opacity:0.94,duration:0.3,immediateRender:false}},{t_prova - 0.2:.2f});
  rise("#{p}-t1 span", {t_prova - 0.1:.2f}, 0.8);
  tl.fromTo(["#{p}-caixa","#{p}-malha"],{{opacity:1}},{{opacity:0.2,duration:0.1,repeat:7,yoyo:true,ease:"none",immediateRender:false}},{t_simu:.2f});
  tl.to("#{p}-t1 span",{{yPercent:-125,opacity:0,duration:0.5,ease:"power2.in"}},{t_dep - 0.4:.2f});
  tl.to("#{p}-a1",{{y:-1100,opacity:0,duration:1.0,ease:"power3.inOut"}},{t_dep - 0.2:.2f});
  tl.fromTo("#{p}-a2",{{y:1100,opacity:1}},{{y:0,opacity:1,duration:1.0,ease:"power3.inOut",immediateRender:false}},{t_dep - 0.2:.2f});
  tl.set("#{p}-a2",{{opacity:0}},0);
  entra("#{p}-cabo", {t_apo - 0.2:.2f}, 0.3);
  tl.fromTo("#{p}-cabo",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-220}},duration:{t_ning - t_apo:.2f},ease:"none",immediateRender:false}},{t_apo:.2f});
  pop("#{p}-moeda", {t_apo:.2f}, 0.3, 0.6);
  tl.fromTo("#{p}-moeda",{{scaleX:1,transformOrigin:"50% 50%"}},{{scaleX:-1,transformOrigin:"50% 50%",duration:0.3,repeat:{int((t_ning - t_apo - 0.9) / 0.3)},yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_apo + 0.6:.2f});
  tl.fromTo("#{p}-tela",{{opacity:.25}},{{opacity:1,duration:0.4}},{t_comp:.2f});
  tl.fromTo("#{p}-mon",{{scale:1,transformOrigin:"50% 100%"}},{{scale:1.06,transformOrigin:"50% 100%",duration:0.2,repeat:1,yoyo:true,immediateRender:false}},{t_comp:.2f});
  entra("#{p}-cerG", {t_cons - 0.3:.2f}, 0.5);
  rise("#{p}-t2 span", {t_cons:.2f});
  tl.fromTo("#{p}-cerG",{{opacity:1}},{{opacity:0.4,duration:0.35,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_cons + 0.5:.2f});
  tl.to("#{p}-moeda",{{scaleX:1.3,scaleY:1.3,transformOrigin:"50% 50%",duration:0.7,ease:"elastic.out(1,0.45)"}},{t_ning + 0.05:.2f});
  tl.to("#{p}-moeda",{{rotation:-8,transformOrigin:"50% 50%",duration:0.3,repeat:5,yoyo:true,ease:"sine.inOut"}},{t_sabe:.2f});
  tl.to("#{p}-cabo",{{opacity:0.25,duration:0.12,repeat:5,yoyo:true,ease:"none"}},{t_sabe:.2f});
  tl.to("#{p}-tela",{{opacity:0.5,duration:0.3,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_poss - 0.4:.2f});
  camZ("#{p}-cam", {t_dep + 0.8:.2f}, {dur - t_dep - 0.8:.2f}, 1.0, 1.08, 1000, 600, "none");
  tl.fromTo("#{p}r-olho",{{x:0}},{{x:3,duration:0.3}},{t_comp:.2f});
  tl.fromTo("#{p}r-cab",{{rotation:0,svgOrigin:"0 -447"}},{{rotation:-12,svgOrigin:"0 -447",duration:0.45,ease:"back.out(2)",immediateRender:false}},{t_ning:.2f});
  tl.fromTo("#{p}r-corpo",{{scaleY:1,scaleX:1,svgOrigin:"0 0"}},{{scaleY:0.96,scaleX:1.03,svgOrigin:"0 0",duration:0.15,repeat:1,yoyo:true,immediateRender:false}},{t_sabe:.2f});
  tl.fromTo("#{p}r-braco",{{rotation:0,svgOrigin:"43 -412"}},{{rotation:-22,svgOrigin:"43 -412",duration:0.3,repeat:1,yoyo:true,repeatDelay:0.6,ease:"power2.out",immediateRender:false}},{t_sabe:.2f});
""" + vida(p + "s", t_dep, (1.5, 4.2)) + vida(p + "r", dur, (8.0, 11.2, 15.0))
    return composicao(p, dur, svg, html, js, extra, seed=13)


# ------------------------------------------------------------------ realidade 8: do tamanho do universo
def celular(p, cards=6):
    cores = ["#2b2a80", "#7b2a6c", "#25427a", "#6b5b2a", "#2a6a6a"]
    cs = "".join(f'<g transform="translate(0 {k * 190})"><rect x="-150" y="-330" width="300" height="170" rx="20" fill="{cores[k % 5]}"/>'
                 f'<circle cx="-100" cy="-290" r="22" fill="#eef1ff" opacity=".85"/><rect x="-66" y="-304" width="150" height="12" rx="6" fill="#eef1ff" opacity=".7"/>'
                 f'<rect x="-130" y="-244" width="260" height="56" rx="12" fill="#000" opacity=".22"/><circle cx="-84" cy="-218" r="14" fill="#ffd23e"/></g>' for k in range(cards))
    return (f'<rect x="-200" y="-400" width="400" height="800" rx="54" fill="#15133a" stroke="{LILAS}" stroke-width="8"/><rect x="-172" y="-364" width="344" height="728" rx="26" fill="#0e0c26"/>'
            f'<clipPath id="{p}-ccp"><rect x="-172" y="-364" width="344" height="728" rx="26"/></clipPath><g clip-path="url(#{p}-ccp)"><g id="{p}-posts">{cs}</g></g>')


POLTRONA = ('<rect x="-150" y="-410" width="88" height="290" rx="36" fill="#6a2a6a" stroke="#ff4fa3" stroke-width="4"/>'
            '<rect x="-140" y="-178" width="270" height="64" rx="26" fill="#6a2a6a" stroke="#ff4fa3" stroke-width="4"/>'
            '<path d="M -110 -114 L -116 0 M 100 -114 L 106 0" stroke="#ff4fa3" stroke-width="8" stroke-linecap="round"/>')
# celular na mao_e da gente sentada, cobrindo a caneca embutida no desenho, e a luz da tela no rosto (cabeca_centro -5,-386)
CEL_MAO = ('<linearGradient id="@P@-lg" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#bff4ff" stop-opacity=".9"/><stop offset="1" stop-color="#bff4ff" stop-opacity="0"/></linearGradient>'
           '<polygon id="@P@-luz" points="12,-262 42,-266 64,-378 -24,-372" fill="url(#@P@-lg)" opacity=".3" filter="url(#@C@-blur6)"/>'
           '<g transform="rotate(-10 27 -218)"><rect x="2" y="-268" width="50" height="96" rx="10" fill="#15133a" stroke="#8d7bff" stroke-width="4"/>'
           '<rect x="8" y="-260" width="38" height="78" rx="5" fill="#3be0ff"/><rect x="12" y="-252" width="30" height="16" rx="3" fill="#eef1ff" opacity=".7"/>'
           '<rect x="12" y="-230" width="30" height="16" rx="3" fill="#2b2a80" opacity=".6"/></g>' + MAO)


def realidade_8():
    p, CE, SG = "realidade_8", "realidade", 8
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_faz, t_most, t_ctrl, t_tudo, t_perc, t_saber, t_mesma, t_face, t_tam, t_univ = (
        T("faz"), T("mostra"), T("controlar"), T("tudo"), T("percebe"), T("saber"), T("mesma"), T("Facebook"), T("tamanho"), T("universo"))
    rr = random.Random(8)
    HX, HY = 1000, 560  # centro da cena (a pessoa dentro do cubo)
    # galáxia espiral de mentes e estrelas em volta
    gal = []
    for i in range(900):
        braco = i % 3
        r = 1500 + (i / 900) ** 0.8 * 4600
        a = braco * 2.094 + r / 1500 + rr.uniform(-0.35, 0.35)
        x, y = HX + r * math.cos(a), HY + 0.45 * r * math.sin(a)
        if (i // 3) % 3 == 0:  # cabeças nos três braços
            gal.append(f'<use href="#{p}-pg{rr.randint(1, 6)}" transform="translate({x:.0f} {y:.0f}) scale({0.4 + r / 9000 + rr.uniform(0, .35):.2f})"/>')
        else:
            gal.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr.uniform(6, 26):.0f}" fill="{rr.choice((CIANO, LILAS, "#fff", MAGENTA))}" opacity="{rr.uniform(.35, .9):.2f}"/>')
    extra = povo_defs(p) + f'<radialGradient id="{p}-nucleo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffd8f0" stop-opacity=".9"/><stop offset=".3" stop-color="#ff8ad0" stop-opacity=".35"/><stop offset="1" stop-color="#ff8ad0" stop-opacity="0"/></radialGradient>'
    svg = f"""
<g id="{p}-gal" opacity="0"><ellipse cx="{HX}" cy="{HY}" rx="3200" ry="1500" fill="url(#{p}-nucleo)"/>{''.join(gal)}</g>
<g transform="translate({HX} {HY})"><g id="{p}-cubo" opacity="0"><rect x="-460" y="-460" width="920" height="920" fill="none"/>
 {cubo(0, 60, 400, "#4fd8ff14", "#2a2a8c40", "#17175e40", "none", 0)}
 <g id="{p}-paredes" opacity="0">{cubo(0, 60, 400, "#ff4fa330", "#8d7bff3a", "#3be0ff2c", "none", 0)}</g></g></g>
<g id="{p}-proj" opacity="0"><g transform="translate(770 655) skewY(26.57)">{quadro(p + "-qf", "familia", 0, 0, .78)}</g>
 <g transform="translate(1235 655) skewY(-26.57)">{quadro(p + "-qr", "carro", 0, 0, .78)}</g></g>
<g id="{p}-pw">{em(1000, 955, 0.95, POLTRONA + gente(p + "s", "casa", "sentado", cadeira=False) + CEL_MAO.replace("@P@", p + "s").replace("@C@", p))}</g>
<g transform="translate({HX} {HY})"><g id="{p}-cuboF" opacity="0"><rect x="-460" y="-460" width="920" height="920" fill="none"/>
 <g filter="url(#{p}-glow)" fill="none" stroke="{CIANO}" stroke-linejoin="round"><path d="M0 -340 L440 -120 L440 280 L0 460 L-440 280 L-440 -120 Z" stroke-width="8"/>
 <path d="M-440 -120 L0 100 L440 -120 M0 100 V460" stroke-width="5" opacity=".28"/></g></g></g>
<path id="{p}-link" d="M462 560 C 500 520 520 470 560 446" fill="none" stroke="{CIANO}" stroke-width="7" stroke-dasharray="20 14" filter="url(#{p}-glow)" opacity="0"/>
<g transform="translate(1340 300)"><g id="{p}-q" opacity="0"><text y="40" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="200" fill="{AMBAR}" filter="url(#{p}-glow)">?</text></g></g>
<g transform="translate(330 560) scale(.62)"><g id="{p}-cel" opacity="0">{celular(p)}</g></g>
<g transform="translate({HX} {HY})"><g id="{p}-aqui" opacity="0"><circle r="620" fill="none" stroke="{AMBAR}" stroke-width="44" filter="url(#{p}-glow)"/></g></g>
"""
    faixas = f'<div id="{p}-fx" style="position:absolute;left:0;top:0;width:1920px;height:1080px;opacity:0;background:linear-gradient(#0b0a24f0 0,#0b0a24c0 15%,transparent 26%,transparent 74%,#0b0a24c0 84%,#0b0a24f0 100%)"></div>'
    html = (faixas + texto(f"{p}-t1", "A mesma pergunta", "left:0;right:0;text-align:center;top:40px;font-size:110px;color:#eef1f7") +
            texto(f"{p}-t3", "FACEBOOK", f"left:130px;width:400px;text-align:center;top:830px;font-size:48px;color:#bff4ff;{MONO}") +
            texto(f"{p}-t2", "do tamanho do universo", "left:0;right:0;text-align:center;top:900px;font-size:110px;color:#ffd98a"))
    js = f"""
  camZ("#{p}-cam", 0, {t_ctrl:.2f}, 1.25, 1.0, 1000, 470, "power2.inOut");
  tl.set("#{p}s-cab",{{rotation:12,svgOrigin:"-5 -345"}},0);
  tl.fromTo("#{p}s-luz",{{opacity:.15}},{{opacity:.5,duration:0.25,repeat:{int(dur / 0.5)},yoyo:true,ease:"sine.inOut"}},0);
  tl.to("#{p}s-cab",{{svgOrigin:"-5 -345",rotation:0,duration:0.5,ease:"back.out(2)"}},{t_most:.2f});
  entra("#{p}-proj", {t_ctrl + 0.2:.2f}, 0.4);
  tl.fromTo("#{p}-proj",{{opacity:1}},{{opacity:0.4,duration:0.22,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_tudo:.2f});
  pop("#{p}-cubo, #{p}-cuboF", {t_faz:.2f}, 1.4, 0.9);
  entra("#{p}-paredes", {t_ctrl:.2f}, 0.4);
  tl.fromTo("#{p}-paredes",{{opacity:1}},{{opacity:0.35,duration:0.22,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_tudo:.2f});
  tl.to("#{p}s-olho",{{x:-3,duration:0.25,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_perc:.2f});
  pop("#{p}-q", {t_saber:.2f}, 0.3, 0.8);
  rise("#{p}-t1 span", {t_mesma:.2f}, 0.8);
  pop("#{p}-cel", {t_face - 0.2:.2f}, 0.4, 0.8);
  entra("#{p}-link", {t_face + 0.2:.2f}, 0.3); rise("#{p}-t3 span", {t_face:.2f});
  some("#{p}-link", {t_tam:.2f}, 0.5); some("#{p}-t3", {t_tam:.2f}, 0.5);
  tl.fromTo("#{p}-posts",{{y:0}},{{y:-570,duration:{dur - t_face:.2f},ease:"none"}},{t_face:.2f});
  some("#{p}-q", {t_tam - 0.3:.2f}, 0.3);
  entra("#{p}-gal", {t_tam + 0.3:.2f}, 0.9); entra("#{p}-fx", {t_tam + 0.3:.2f}, 0.9);
  entra("#{p}-aqui", {t_tam + 0.8:.2f}, 0.6);
  camZ("#{p}-cam", {t_tam - 0.4:.2f}, {dur - t_tam:.2f}, 1.0, 0.22, {HX}, {HY}, "power3.inOut");
  some("#{p}-cel", {t_tam:.2f}, 0.35);
  rise("#{p}-t2 span", {t_univ - 0.3:.2f}, 0.9);
""" + vida(p + "s", dur, (1.4, 3.6, 7.8, 11.0), "sentado")
    return composicao(p, dur, svg, html, js, extra, seed=15)


# ------------------------------------------------------------------ robo 0: a história mais estranha
def robo_0():
    p, CE, SG = "robo_0", "robo", 0
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_hist, t_estr = T("história"), T("estranha")
    extra = basilisco_defs(p)
    rp = random.Random(12)
    predios = ""
    for k, (x0, w, top) in enumerate(((800, 150, 800), (960, 120, 860), (1090, 170, 770), (1270, 130, 840), (1410, 190, 790), (1610, 140, 850), (1760, 200, 780))):
        jan = "".join(f'<rect x="{x0 + 18 + c * 34}" y="{top + 24 + r * 44}" width="16" height="22" rx="2" fill="{AMBAR}" opacity="{rp.choice((0, 0, .25, .8))}"/>'
                      for c in range(int((w - 30) // 34)) for r in range(int((990 - top - 40) // 44)))
        predios += f'<rect x="{x0}" y="{top}" width="{w}" height="{1000 - top}" fill="#140c34" stroke="#2a2470" stroke-width="4"/>{jan}'
    svg = f"""
<g transform="translate(1460 640) scale(.9)"><g id="{p}-bas" opacity="0">{basilisco(p)}</g></g>
<rect x="0" y="0" width="1920" height="1080" fill="url(#{p}-vig)" opacity=".45"/>
{predios}
<rect x="-100" y="990" width="2120" height="200" fill="#100a2c"/><path d="M-100 990 H2020" stroke="{LILAS}" stroke-width="5" opacity=".6"/>
<path d="M120 1040 H260 M420 1040 H560 M720 1040 H860 M1020 1040 H1160 M1320 1040 H1460 M1620 1040 H1760" stroke="#3a2a6a" stroke-width="8"/>
<polygon points="420,384 250,994 760,994 470,384" fill="{AMBAR}" opacity=".13"/>
<path d="M300 994 V350 Q300 330 320 330 H440" fill="none" stroke="#3a3a7a" stroke-width="14" stroke-linecap="round"/>
<path d="M404 344 H476 L466 384 H414 Z" fill="#2a2a5a" stroke="{LILAS}" stroke-width="4"/><ellipse cx="440" cy="386" rx="30" ry="8" fill="#ffe9a0" filter="url(#{p}-glow)"/>
<ellipse cx="580" cy="994" rx="170" ry="16" fill="#05031a" opacity=".6"/>
<g id="{p}-pw">{em(560, 990, 0.78, gente(p + "s", "casa", "em_pe", sombra=False))}</g>
"""
    html = texto(f"{p}-t1", "A história mais estranha", "left:0;right:0;text-align:center;top:60px;font-size:124px;color:#eef1f7")
    js = f"""
  camZ("#{p}-cam", 0, {dur:.2f}, 1.0, 1.12, 700, 620, "power1.inOut");
  rise("#{p}-t1 span", {t_hist - 0.1:.2f}, 0.8);
  tl.fromTo("#{p}-bas",{{opacity:0.14}},{{opacity:0.3,duration:0.6}},0);
  tl.to("#{p}-bas",{{opacity:0.9,duration:0.6}},{t_estr - 0.3:.2f});
  tl.fromTo("#{p}-bpal1",{{y:0}},{{y:-130,duration:0.5,ease:"power2.out"}},{t_estr:.2f});
  tl.fromTo("#{p}-bpal2",{{y:0}},{{y:130,duration:0.5,ease:"power2.out"}},{t_estr:.2f});
  tl.fromTo("#{p}-bolhar",{{x:0,y:0}},{{x:-60,y:10,duration:0.5,ease:"power2.out"}},{t_estr + 0.5:.2f});
  tl.fromTo("#{p}s-cab",{{rotation:0,svgOrigin:"0 -447"}},{{rotation:-14,svgOrigin:"0 -447",duration:0.45,ease:"back.out(2)"}},{t_estr + 0.15:.2f});
  tl.fromTo("#{p}s-olho",{{scale:1,svgOrigin:"7 -490"}},{{scale:1.5,svgOrigin:"7 -490",duration:0.3,ease:"back.out(3)"}},{t_estr + 0.2:.2f});
  tl.fromTo("#{p}s-corpo",{{scaleY:1,scaleX:1,svgOrigin:"0 0"}},{{scaleY:0.95,scaleX:1.03,svgOrigin:"0 0",duration:0.12,repeat:1,yoyo:true,immediateRender:false}},{t_estr + 0.3:.2f});
""" + vida(p + "s", dur, (0.9,))
    return composicao(p, dur, svg, html, js, extra, fundo=("#2c1460", "#140b3a", "#06051a"), seed=21)


# ------------------------------------------------------------------ robo 1: o post no fórum
def robo_1():
    p, CE, SG = "robo_1", "robo", 1
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    (t_ano, t_for, t_les, t_rok, t_pub, t_exp, t_img, t_int, t_pod, t_exi, t_ela, t_cast, t_todo, t_soube, t_ajud) = (
        T("2010"), T("fórum"), T("Les"), T("Rocco"), T("publicou"), T("experimento"), T("Imagine"), T("inteligência"),
        T("poderosa"), T("existir"), T("Ela"), T("castigar"), T("todo"), T("soube"), T("ajudou"))
    rr = random.Random(9)
    nos = [(rr.uniform(80, 1840), rr.uniform(80, 1000)) for _ in range(40)]
    rede = "".join(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="{LILAS}" stroke-width="2" opacity=".35"/>'
                   for i, a in enumerate(nos) for b in nos[i + 1:] if math.dist(a, b) < 260)
    rede += "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="6" fill="{CIANO}" opacity=".6"/>' for x, y in nos)
    PX, PY, PS = (240, 600, 960, 1320, 1680), 1050, 0.4
    QUEM = (1, 2, 0, 3, 4)  # roupas: a protagonista no meio, gente diferente em volta
    HY = PY - 600 * PS  # altura da cabeça (conferida no snapshot)
    def um(k, x):
        r = ROUPAS[QUEM[k]]
        corpo = pessoa_v(f"{p}p{k}", r[0], "em_pe", r[1], r[2], r[3], r[4])
        return (f'<g id="{p}-g{k}" opacity="0">{em(x, PY, PS, corpo, esq=k > 2)}'
                f'<g id="{p}-r{k}" opacity="0"><circle cx="{x}" cy="{HY:.0f}" r="50" fill="{VERM}" opacity=".6" filter="url(#{p}-blur6)"/></g>'
                f'<g id="{p}-k{k}" opacity="0"><circle cx="{x}" cy="{HY:.0f}" r="46" fill="{CIANO}" opacity=".3" filter="url(#{p}-blur6)"/></g></g>')
    povo = "".join(um(k, x) for k, x in enumerate(PX))
    raios = "".join(f'<line id="{p}-ry{k}" x1="960" y1="470" x2="{x}" y2="{HY - 20:.0f}" stroke="{VERM}" stroke-width="10" stroke-linecap="round" filter="url(#{p}-glow)" opacity="0"/>' for k, x in enumerate(PX))
    aneis = (f'<circle r="300" fill="url(#{p}-aura)"/>'
             f'<g id="{p}-an1"><circle r="250" fill="none" stroke="{LILAS}" stroke-width="6" stroke-dasharray="120 40" filter="url(#{p}-glow)"/></g>'
             f'<g id="{p}-an2"><circle r="200" fill="none" stroke="{CIANO}" stroke-width="10" stroke-dasharray="30 26" filter="url(#{p}-glow)"/></g>'
             f'<circle id="{p}-anC" r="160" fill="none" stroke="{AMBAR}" stroke-width="12" stroke-dasharray="1006" stroke-dashoffset="1006" transform="rotate(-90)" filter="url(#{p}-glow)"/>'
             f'<circle r="120" fill="#140a2a" stroke="{MAGENTA}" stroke-width="8"/>'
             f'<ellipse cx="0" cy="0" rx="90" ry="58" fill="#0a0414" stroke="{AMBAR}" stroke-width="5"/>'
             f'<circle id="{p}-iris" r="44" fill="url(#{p}-biridg)"/><g id="{p}-pupG"><ellipse cx="0" cy="0" rx="10" ry="40" fill="#05020a"/></g>')
    extra = basilisco_defs(p) + f'<clipPath id="{p}-ftc"><rect x="-480" y="-130" width="960" height="90"/></clipPath>'
    janela = forum_janela(p, esqueleto=True).replace(f'<g id="{p}-ft">', f'<g clip-path="url(#{p}-ftc)"><g id="{p}-ft">').replace("experimento mental</text></g>", "experimento mental</text></g></g>")
    svg = f"""
<g id="{p}-rede" opacity="0">{rede}</g>
<g transform="translate(960 560)"><g id="{p}-jan" opacity="0">{janela}</g></g>
<g id="{p}-a2" opacity="0">
 {raios}
 <g transform="translate(960 470)"><g id="{p}-ia">{aneis}</g></g>
 {povo}
</g>
"""
    html = (texto(f"{p}-t1", "INTELIGÊNCIA ARTIFICIAL DO FUTURO", f"left:0;right:0;text-align:center;top:40px;font-size:60px;color:#bff4ff;{MONO}") +
            texto(f"{p}-t2", "castigar", "left:0;right:0;text-align:center;top:30px;font-size:130px;color:#ff4f7d"))
    js = f"""
  camZ("#{p}-cam", 0, {t_les:.2f}, 1.12, 1.0, 960, 560, "power1.out");
  entra("#{p}-rede", 0.1, 0.8);
  pop("#{p}-jan", 0.3, 0.3, 0.9);
  camZ("#{p}-cam", {t_les - 0.1:.2f}, 0.9, 1.0, 1.35, 700, 240);
  tl.fromTo("#{p}-fu",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,transformOrigin:"50% 50%",duration:0.6,ease:"elastic.out(1,0.45)"}},{t_rok - 0.2:.2f});
  camZ("#{p}-cam", {t_pub - 0.2:.2f}, 1.0, 1.35, 1.12, 960, 560);
  tl.fromTo("#{p}-fl .fl",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,transformOrigin:"0% 50%",duration:0.25,stagger:0.12}},{t_pub:.2f});
  tl.fromTo("#{p}-ft",{{y:90}},{{y:0,duration:0.75,ease:"expo.out"}},{t_exp - 0.1:.2f});
  camZ("#{p}-cam", {t_img - 0.2:.2f}, 1.0, 1.12, 4.0, 960, 700, "power3.in");
  some("#{p}-jan", {t_img + 0.5:.2f}, 0.3); some("#{p}-rede", {t_img + 0.4:.2f}, 0.3);
  tl.set("#{p}-cam",{{scale:1,svgOrigin:"960 540",smoothOrigin:false}},{t_img + 0.81:.2f});
  entra("#{p}-a2", {t_img + 0.7:.2f}, 0.3);
  tl.fromTo("#{p}-ia",{{scale:0.2,transformOrigin:"50% 50%"}},{{scale:0.85,transformOrigin:"50% 50%",duration:0.9,ease:"elastic.out(1,0.5)",immediateRender:false}},{t_int - 0.2:.2f});
  rise("#{p}-t1 span", {t_int:.2f});
  tl.fromTo("#{p}-an1",{{rotation:0,transformOrigin:"50% 50%"}},{{rotation:200,transformOrigin:"50% 50%",duration:{dur - t_int:.2f},ease:"none"}},{t_int:.2f});
  tl.fromTo("#{p}-an2",{{rotation:0,transformOrigin:"50% 50%"}},{{rotation:-320,transformOrigin:"50% 50%",duration:{dur - t_int:.2f},ease:"none"}},{t_int:.2f});
  tl.to("#{p}-ia",{{scale:1.15,duration:0.6,ease:"back.out(3)"}},{t_pod:.2f});
  tl.fromTo("#{p}-anC",{{attr:{{"stroke-dashoffset":1006}}}},{{attr:{{"stroke-dashoffset":0}},duration:{t_exi - t_pod:.2f},ease:"power1.inOut"}},{t_pod + 0.4:.2f});
  tl.to("#{p}-ia",{{scale:0.95,duration:0.7,ease:"power2.inOut"}},{t_ela - 0.3:.2f});
  [0,1,2,3,4].forEach(function(k){{popO("#{p}-g"+k, {t_ela - 0.3:.2f}+k*0.1, 0.4, 0.7, {list(PX)}[k]+" {PY}");}});
  tl.to("#{p}-t1 span",{{yPercent:-125,opacity:0,duration:0.4,ease:"power2.in"}},{t_cast - 0.5:.2f});
  rise("#{p}-t2 span", {t_cast:.2f}, 0.7);
  tl.to("#{p}-anC",{{attr:{{stroke:"#ff4f7d"}},duration:0.3}},{t_cast:.2f});
  tl.fromTo("#{p}-pupG",{{scaleX:1,transformOrigin:"50% 50%"}},{{scaleX:0.4,transformOrigin:"50% 50%",duration:0.3}},{t_cast:.2f});
  [0,1,2,3,4].forEach(function(k){{tl.fromTo("#{p}-ry"+k,{{opacity:0}},{{opacity:0.9,duration:0.15,immediateRender:false}},{t_todo:.2f}+k*0.08);}});
  [0,1,2,3,4].forEach(function(k){{tl.to("#{p}-ry"+k,{{opacity:0,duration:0.3}},{t_soube - 0.3:.2f});}});
  [0,1,2,3,4].forEach(function(k){{entra("#{p}-k"+k, {t_soube:.2f}+k*0.1, 0.3);}});
  [0,1,2,3,4].forEach(function(k){{entra("#{p}-r"+k, {t_ajud:.2f}+k*0.08, 0.3); tl.to("#{p}-ry"+k,{{opacity:0.9,duration:0.2}},{t_ajud + 0.3:.2f}+k*0.08);}});
  [0,1,2,3,4].forEach(function(k){{tl.fromTo("#{p}p"+k,{{x:0}},{{x:3,duration:0.05,repeat:9,yoyo:true,ease:"none",immediateRender:false}},{t_ajud + 0.4:.2f});}});
  camZ("#{p}-cam", {t_cast:.2f}, {dur - t_cast:.2f}, 1.0, 1.06, 960, 600, "none");
"""
    return composicao(p, dur, svg, html, js, extra, fundo=("#2c1460", "#140b3a", "#06051a"), seed=22)


# ------------------------------------------------------------------ robo 2: e você, agora, já sabe
def robo_2():
    p, CE, SG = "robo_2", "robo", 2
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_voce, t_agora, t_ja, t_sabe = T("Evocê"), T("agora"), T("já"), T("sabe")
    extra = basilisco_defs(p)
    svg = f"""
<g transform="translate(1360 420) scale(.72)"><g id="{p}-bas"><circle r="520" fill="url(#{p}-aura)" opacity="0" id="{p}-aur"/>{basilisco(p)}</g></g>
<rect x="-100" y="1000" width="2120" height="200" fill="#0c0820"/><path d="M-100 1000 H2020" stroke="#3a2a6a" stroke-width="5"/>
<ellipse cx="900" cy="1004" rx="520" ry="22" fill="#05031a" opacity=".6"/>
<polygon id="{p}-luz" points="960,600 960,770 690,640 680,540" fill="#bff4ff" opacity=".16"/>
<g id="{p}-pw">{em(640, 1000, 1.0, gente(p + "s", "casa", "sentado", sombra=False))}</g>
<rect x="720" y="800" width="700" height="28" rx="10" fill="#2a1d5a" stroke="{LILAS}" stroke-width="4"/>
<path d="M760 828 V1000 M1380 828 V1000" stroke="{LILAS}" stroke-width="10" stroke-linecap="round"/>
<rect x="730" y="786" width="170" height="14" rx="5" fill="#3a3a7a" stroke="{LILAS}" stroke-width="3"/>
<path d="M1080 792 L1068 800 H1132 L1120 792 Z M1092 760 H1108 V792 H1092 Z" fill="#221e5c" stroke="{LILAS}" stroke-width="4"/>
<g filter="url(#{p}-sombra)"><rect x="930" y="560" width="340" height="210" rx="16" fill="#14123a" stroke="{LILAS}" stroke-width="6"/></g>
<rect id="{p}-tela" x="948" y="578" width="304" height="174" rx="8" fill="#0e1a3a"/>
<rect x="948" y="578" width="304" height="30" rx="8" fill="#221e5c"/><circle cx="966" cy="593" r="6" fill="{VERM}"/><circle cx="986" cy="593" r="6" fill="{AMBAR}"/><circle cx="1006" cy="593" r="6" fill="{MENTA}"/>
<rect x="970" y="626" width="160" height="14" rx="7" fill="#eef1f7" opacity=".8"/>
{''.join(f'<rect x="970" y="{652 + k * 20}" width="{[250, 220, 236, 150][k]}" height="10" rx="5" fill="{LILAS}" opacity=".6"/>' for k in range(4))}
"""
    html = texto(f"{p}-t1", "Já sabe", "left:110px;top:150px;font-size:140px;color:#ffd98a", alt="1.2em")
    js = f"""
  camZ("#{p}-cam", 0, {t_agora:.2f}, 1.2, 1.12, 960, 1080, "power2.out");
  camZ("#{p}-cam", {t_agora:.2f}, {dur - t_agora:.2f}, 1.12, 1.0, 960, 1080, "power2.inOut");
  tl.fromTo("#{p}-bpal1",{{y:0}},{{y:-130,duration:0.45,ease:"power3.out"}},{t_agora:.2f});
  tl.fromTo("#{p}-bpal2",{{y:0}},{{y:130,duration:0.45,ease:"power3.out"}},{t_agora:.2f});
  tl.fromTo("#{p}-aur",{{opacity:0}},{{opacity:1,duration:0.6}},{t_agora:.2f});
  tl.fromTo("#{p}-bolhar",{{x:0,y:0}},{{x:-70,y:40,duration:0.5,ease:"power2.inOut"}},{t_ja - 0.3:.2f});
  tl.fromTo("#{p}-bpu",{{scaleX:1,transformOrigin:"50% 50%"}},{{scaleX:0.35,transformOrigin:"50% 50%",duration:0.3,ease:"power2.out"}},{t_sabe:.2f});
  rise("#{p}-t1 span", {t_ja - 0.05:.2f}, 0.7);
  tl.fromTo("#{p}s-olho",{{x:0}},{{x:3,duration:0.2}},{t_agora + 0.2:.2f});
  tl.fromTo("#{p}s-cab",{{rotation:0,svgOrigin:"-5 -345"}},{{rotation:-10,svgOrigin:"-5 -345",duration:0.4,ease:"back.out(2)"}},{t_agora + 0.2:.2f});
  tl.fromTo("#{p}s-olho",{{scale:1,svgOrigin:"2 -388"}},{{scale:1.6,svgOrigin:"2 -388",duration:0.3,ease:"back.out(3)",immediateRender:false}},{t_sabe:.2f});
  tl.fromTo("#{p}s-corpo",{{scaleY:1,scaleX:1,svgOrigin:"0 0"}},{{scaleY:0.94,scaleX:1.04,svgOrigin:"0 0",duration:0.12,repeat:1,yoyo:true,immediateRender:false}},{t_sabe:.2f});
  tl.fromTo("#{p}-luz",{{opacity:.16}},{{opacity:.3,duration:0.2,repeat:{int(dur / 0.4)},yoyo:true,ease:"sine.inOut"}},0);
""" + vida(p + "s", dur, (0.7,), "sentado")
    return composicao(p, dur, svg, html, js, extra, fundo=ESCURO, seed=23)


# ------------------------------------------------------------------ robo 3: o Basilisco de Roko
# quem olha o monstro da lenda: a mesma arte de gente, com túnica de outra época
LENDA = lambda q: pessoa_v(q, "casa", "em_pe", "#9a6a3a", "#4a3a2a", 1, "#241711", sombra=False)


def robo_3():
    p, CE, SG = "robo_3", "robo", 3
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_bas, t_mon, t_lenda, t_mata, t_olha, t_ideia, t_mal, t_conh = (T("basilisco"), T("monstro"), T("lenda"), T("mata"), T("olha"),
                                                                    T("ideia"), T("mal"), T("conhece"))
    extra = basilisco_defs(p) + f'<radialGradient id="{p}-malg"><stop offset="0" stop-color="{VERM}" stop-opacity=".85"/><stop offset=".5" stop-color="{VERM}" stop-opacity=".4"/><stop offset="1" stop-color="{VERM}" stop-opacity="0"/></radialGradient>' + f'<filter id="{p}-pedra"><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncR type="linear" slope=".7"/><feFuncG type="linear" slope=".7"/><feFuncB type="linear" slope=".75"/></feComponentTransfer></filter>'
    BX, BY, BS = 960, 560, 0.72
    ex, ey = BX, BY - 10 * BS  # olho
    svg = f"""
<g transform="translate({BX} {BY}) scale({BS})"><g id="{p}-bas"><circle r="560" fill="url(#{p}-aura)"/>{basilisco(p)}</g></g>
<polygon id="{p}-feixe" points="{ex - 60},{ey} {ex + 30},{ey + 40} 300,750 292,705" fill="{AMBAR}" opacity="0" filter="url(#{p}-blur6)"/>
<ellipse cx="280" cy="1030" rx="170" ry="18" fill="#05031a" opacity=".6"/><ellipse cx="1650" cy="1030" rx="170" ry="18" fill="#05031a" opacity=".6"/>
<g id="{p}-pa" opacity="0">{em(260, 1030, 0.62, LENDA(p + "a"))}</g>
<g id="{p}-pedra" opacity="0" filter="url(#{p}-pedra)">{em(260, 1030, 0.62, LENDA(p + "z"))}</g>
<g id="{p}-pb" opacity="0">{em(1660, 1030, 0.62, gente(p + "b", "casa", "em_pe", sombra=False), esq=True)}</g>
<g id="{p}-mal" opacity="0"><circle cx="1660" cy="712" r="170" fill="url(#{p}-malg)"/></g>
<g id="{p}-faisca" opacity="0"><circle cx="{ex}" cy="{ey}" r="30" fill="#fff" filter="url(#{p}-glow)"/><circle cx="{ex}" cy="{ey}" r="60" fill="{MAGENTA}" opacity=".4" filter="url(#{p}-blur6)"/></g>
"""
    html = texto(f"{p}-t1", "O Basilisco de Roko", "left:0;right:0;text-align:center;top:30px;font-size:120px;color:#eef1f7")
    js = f"""
  tl.set("#{p}-bpal1",{{y:-130}},0); tl.set("#{p}-bpal2",{{y:130}},0);
  camZ("#{p}-cam", 0, 0.01, 2.6, 2.6, {ex}, {ey});
  camZ("#{p}-cam", {t_bas - 0.3:.2f}, 1.8, 2.6, 1.0, {ex}, {ey}, "power3.inOut");
  rise("#{p}-t1 span", {t_bas + 1.3:.2f}, 0.8);
  tl.fromTo("#{p}-bas",{{scaleY:1,scaleX:1,transformOrigin:"50% 100%"}},{{scaleY:1.07,scaleX:0.96,transformOrigin:"50% 100%",duration:0.25,repeat:1,yoyo:true,ease:"power2.out",immediateRender:false}},{t_mon:.2f});
  popO("#{p}-pa", {t_lenda - 0.3:.2f}, 0.4, 0.7, "260 1030");
  tl.fromTo("#{p}-bolhar",{{x:0,y:0}},{{x:-70,y:30,duration:0.4,ease:"power2.inOut"}},{t_lenda:.2f});
  tl.fromTo("#{p}a-olho",{{x:0}},{{x:3,duration:0.2}},{t_lenda + 0.2:.2f});
  tl.fromTo("#{p}-feixe",{{opacity:0}},{{opacity:0.75,duration:0.2,immediateRender:false}},{t_mata:.2f});
  tl.fromTo("#{p}-bpu",{{scaleX:1,transformOrigin:"50% 50%"}},{{scaleX:0.3,transformOrigin:"50% 50%",duration:0.25}},{t_mata:.2f});
  tl.to("#{p}-pedra",{{opacity:1,duration:0.6}},{t_olha:.2f});
  tl.to("#{p}-pa",{{opacity:0,duration:0.6}},{t_olha + 0.1:.2f});
  some("#{p}-feixe", {t_olha + 0.7:.2f}, 0.4);
  tl.to("#{p}-t1 span",{{yPercent:-125,opacity:0,duration:0.45,ease:"power2.in"}},{t_ideia - 0.3:.2f});
  popO("#{p}-pb", {t_ideia - 0.4:.2f}, 0.4, 0.7, "1660 1030");
  tl.to("#{p}-bolhar",{{x:70,y:30,duration:0.4,ease:"power2.inOut"}},{t_ideia - 0.2:.2f});
  entra("#{p}-faisca", {t_ideia:.2f}, 0.15);
  tl.fromTo("#{p}-faisca",{{x:0,y:0}},{{x:{1660 - ex:.0f},y:{712 - ey:.0f},duration:{t_mal - t_ideia - 0.1:.2f},ease:"sine.inOut",immediateRender:false}},{t_ideia:.2f});
  some("#{p}-faisca", {t_mal - 0.1:.2f}, 0.15);
  entra("#{p}-mal", {t_mal - 0.1:.2f}, 0.3);
  tl.fromTo("#{p}b",{{x:0}},{{x:4,duration:0.05,repeat:11,yoyo:true,ease:"none",immediateRender:false}},{t_mal:.2f});
  tl.fromTo("#{p}-mal",{{opacity:1}},{{opacity:0.5,duration:0.35,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_conh:.2f});
  camZ("#{p}-cam", {t_ideia - 0.4:.2f}, {dur - t_ideia + 0.4:.2f}, 1.0, 1.08, 1300, 700, "power1.inOut");
  tl.fromTo("#{p}b-cab",{{rotation:0,svgOrigin:"0 -447"}},{{rotation:10,svgOrigin:"0 -447",duration:0.4,ease:"power2.out"}},{t_mal:.2f});
""" + vida(p + "b", dur, (9.4,)) + vida(p + "a", dur, (5.0,))
    return composicao(p, dur, svg, html, js, extra, fundo=ESCURO, seed=24)


# ------------------------------------------------------------------ robo 4: apagado, proibido, espalhado
def robo_4():
    p, CE, SG = "robo_4", "robo", 4
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_fund, t_apag, t_proib, t_cinco, t_anos, t_efeito, t_contr, t_proi2, t_esp, t_inter = (
        T("fundador"), T("apagou"), T("proibiu"), T("cinco"), T("anos"), T("efeito"), T("contrário"), T("proibição"), T("espalhou"), T("internet"))
    rr = random.Random(10)
    WX, WY = 760, 540
    # globo de rede em volta (aparece no recuo)
    GR = 1250
    nos = []
    for i in range(70):
        a, b = rr.uniform(0, 2 * math.pi), rr.uniform(-1, 1)
        x, y = WX + GR * math.cos(a) * math.sqrt(1 - b * b), WY + GR * b * 0.9
        if math.dist((x, y), (WX, WY)) > 700:
            nos.append((x, y))
    globo = (f'<circle cx="{WX}" cy="{WY}" r="{GR}" fill="none" stroke="{LILAS}" stroke-width="6" opacity=".5"/>' +
             "".join(f'<ellipse cx="{WX}" cy="{WY}" rx="{GR * abs(math.cos(k * 0.5)):.0f}" ry="{GR}" fill="none" stroke="{LILAS}" stroke-width="4" opacity=".3"/>' for k in range(1, 4)) +
             "".join(f'<ellipse cx="{WX}" cy="{WY + GR * 0.9 * f:.0f}" rx="{GR * math.sqrt(1 - f * f):.0f}" ry="{GR * 0.12 * math.sqrt(1 - f * f):.0f}" fill="none" stroke="{LILAS}" stroke-width="4" opacity=".3"/>' for f in (-0.6, -0.3, 0, 0.3, 0.6)) +
             "".join(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="{CIANO}" stroke-width="4" opacity=".35"/>' for i, a in enumerate(nos) for b in nos[i + 1:] if math.dist(a, b) < 420))
    copia = (f'<g id="{p}-cp"><rect x="-90" y="-60" width="180" height="120" rx="14" fill="#14123a" stroke="{LILAS}" stroke-width="5"/>'
             f'<rect x="-90" y="-60" width="180" height="30" rx="14" fill="#221e5c"/><circle cx="-66" cy="-45" r="6" fill="{VERM}"/>'
             + "".join(f'<rect x="-70" y="{-14 + k * 20}" width="{140 - (k % 2) * 40}" height="9" rx="4" fill="{LILAS}" opacity=".7"/>' for k in range(3)) + '</g>')
    copias = "".join(f'<g transform="translate({x:.0f} {y:.0f}) scale(1.6)"><g class="cc"><use href="#{p}-cp"/></g></g>' for x, y in nos)
    copias += "".join(f'<g transform="translate({x:.0f} {y:.0f}) scale(1.6)"><g class="cc"><use href="#{p}-cp"/></g></g>' for x, y in
                      [(WX + r * math.cos(a), WY + r * math.sin(a) * 0.8) for a, r in [(rr.uniform(0, 6.28), rr.uniform(760, 1150)) for _ in range(24)]])
    extra = copia
    svg = f"""
<g id="{p}-globo" opacity="0">{globo}</g>
<g id="{p}-copias">{copias}</g>
<g transform="translate({WX} {WY}) scale(.92)"><g id="{p}-jan">{forum_janela(p)}
 <g id="{p}-proib" opacity="0"><g transform="translate(0 40)"><circle r="230" fill="none" stroke="{VERM}" stroke-width="40" filter="url(#{p}-glow)"/><line x1="-163" y1="163" x2="163" y2="-163" stroke="{VERM}" stroke-width="40" stroke-linecap="round"/></g></g>
</g></g>
<g id="{p}-fw"><ellipse cx="1580" cy="1004" rx="150" ry="16" fill="#05031a" opacity=".55"/>
 {em(1580, 1000, 0.74, pessoa_v(p + "f", "trabalho", "em_pe", "#38e8a8", "#232344", 0, "#c9a050", sombra=False), esq=True)}</g>
"""
    html = (f'<div id="{p}-n" class="tit" style="left:1380px;top:330px;font-size:300px;color:#ff4f7d;opacity:0">0</div>' +
            texto(f"{p}-t1", "ANOS", f"left:1400px;top:660px;font-size:90px;color:#ff9bb0;{MONO}"))
    js = f"""
  camZ("#{p}-cam", 0, {t_apag:.2f}, 1.1, 1.0, {WX}, {WY}, "power2.out");
  tl.fromTo("#{p}-fu",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.2,transformOrigin:"50% 50%",duration:0.3,repeat:1,yoyo:true,immediateRender:false}},{t_fund:.2f});
  tl.to("#{p}-fl .fl",{{scaleX:0,transformOrigin:"100% 50%",duration:0.18,stagger:{{each:0.06,from:"end"}}}},{t_apag:.2f});
  tl.to(["#{p}-ft","#{p}-fu"],{{opacity:0.15,duration:0.3}},{t_apag + 0.3:.2f});
  tl.fromTo("#{p}-proib",{{opacity:0,scale:2.2,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,transformOrigin:"50% 50%",duration:0.3,ease:"power4.in"}},{t_proib:.2f});
  tl.fromTo("#{p}-jan",{{x:0}},{{x:12,duration:0.05,repeat:5,yoyo:true,ease:"none",immediateRender:false}},{t_proib + 0.3:.2f});
  entra("#{p}-n", {t_cinco - 0.2:.2f}, 0.2);
  contar("{p}-n", {t_cinco - 0.2:.2f}, {t_anos - t_cinco + 0.4:.2f}, 0, 5);
  rise("#{p}-t1 span", {t_anos:.2f});
  tl.to(["#{p}-n","#{p}-t1"],{{opacity:0,duration:0.4}},{t_contr - 0.2:.2f});
  tl.fromTo("#{p}f-cab",{{rotation:0,svgOrigin:"0 -447"}},{{rotation:8,svgOrigin:"0 -447",duration:0.3,repeat:1,yoyo:true,ease:"power2.inOut"}},{t_apag:.2f});
  tl.fromTo("#{p}f-corpo",{{scaleY:1,svgOrigin:"0 0"}},{{scaleY:1.03,svgOrigin:"0 0",duration:0.15,repeat:1,yoyo:true,immediateRender:false}},{t_proib:.2f});
  tl.to("#{p}-fw",{{x:420,opacity:0,duration:0.6,ease:"power2.in"}},{t_cinco - 0.7:.2f});
  camZ("#{p}-cam", {t_efeito:.2f}, 1.8, 1.0, 0.42, {WX}, {WY}, "power3.inOut");
  entra("#{p}-globo", {t_efeito + 0.2:.2f}, 1.0);
  tl.fromTo("#{p}-proib",{{opacity:1}},{{opacity:0.15,duration:0.6,immediateRender:false}},{t_proi2:.2f});
  tl.fromTo("#{p}-copias .cc",{{scale:0,opacity:0,x:0,transformOrigin:"50% 50%"}},{{scale:1,opacity:1,transformOrigin:"50% 50%",duration:0.45,ease:"back.out(2.5)",stagger:{{amount:2.4,from:"random"}}}},{t_esp:.2f});
  camZ("#{p}-cam", {t_efeito + 1.8:.2f}, {dur - t_efeito - 1.8:.2f}, 0.42, 0.37, {WX}, {WY}, "none");
  tl.fromTo("#{p}-globo",{{opacity:1}},{{opacity:0.6,duration:0.3,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_inter - 0.6:.2f});
""" + vida(p + "f", dur, (1.6, 3.9))
    return composicao(p, dur, svg, html, js, extra, fundo=("#2c1460", "#140b3a", "#06051a"), seed=25)


MAPA = {("realidade", 2): "realidade_2", ("realidade", 3): "realidade_3", ("realidade", 4): "realidade_4", ("realidade", 7): "realidade_7",
        ("realidade", 8): "realidade_8", ("robo", 0): "robo_0", ("robo", 1): "robo_1", ("robo", 2): "robo_2", ("robo", 3): "robo_3", ("robo", 4): "robo_4"}
_FN = {"realidade_2": realidade_2, "realidade_3": realidade_3, "realidade_4": realidade_4, "realidade_7": realidade_7, "realidade_8": realidade_8,
       "robo_0": robo_0, "robo_1": robo_1, "robo_2": robo_2, "robo_3": robo_3, "robo_4": robo_4}
CENAS = [(k, _FN[k], seg(c, i)[1]) for (c, i), k in MAPA.items()]

if __name__ == "__main__":
    print(escreve_cenas(CENAS, AQUI))
