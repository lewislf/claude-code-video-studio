"""Grupo g4_ler: cena "ler", segmentos 0, 1, 3, 4, 5, 6, 8, 9, 10 e 11 (2, 7 e 12 já existem: D, E e F da v3).

  python3 build_g4_ler.py     # escreve compositions/ e index.html desta pasta

Rodada 2: a cabeça de perfil com cérebro rosa ficou só no ler_0 (o tema "ler o cérebro"). Onde a narração fala de gente
(a mulher no hospital, os pacientes, os voluntários, "você") entra a pessoa de verdade de gente.py, em cenários de vida:
quarto de hospital, cadeira de rodas, ressonância, sala de casa. As páginas reais dos artigos (ler_3, ler_8) ficam.
"""
import math, os, random, re, sys

AQUI_G = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI_G, ".."))
from motor import *  # noqa: E402,F401
from arte2 import mosca_rica, mosca_defs, H_LINHA, CEREBRO_LAT, cerebro_lateral  # noqa: E402
from gente import gente, quadro, orbe, cabeca, CASA, PELE, CABELO, GRAVATA, ANCORAS  # noqa: E402

CE = "ler"

# variações da mesma pessoa (troca de cor sobre gente(..., "casa"/"trabalho"))
# (hex base de gente.py; sombra e luz são camadas neutras por cima, então trocar o base recolore a peça inteira)
AVENTAL = {CASA["torso"]: "#8fcde6", CASA["calca"]: "#6fa8c8", CASA["sapato"]: "#dfe8f2", CABELO: "#2a1812"}   # a mulher: avental de hospital
VOLUNT = {CASA["torso"]: "#2fb88a"}                               # voluntário: moletom verde
CIENT2 = {GRAVATA: "#2bb8d8", CABELO: "#c4c0d4"}                  # segundo cientista: gravata ciano, cabelo grisalho


def tinge(svg, mapa):
    for a, b in mapa.items():
        svg = svg.replace(a, b)
    return svg


def vida_g(p, dur, piscadas=(2.0, 5.3, 8.8, 12.1), quadril=-230):
    """Como gente.vida_gente, com a respiração por svgOrigin (a caixa de {p}-tor contém os retângulos de recorte de
    19998 px do SVG gerado, então transformOrigin em % gira/estica a partir de um ponto a 10 mil px do corpo)."""
    n = max(1, int(dur / 1.7))
    js = (f'tl.fromTo("#{p}-tor",{{scaleY:1,svgOrigin:"0 {quadril}"}},{{scaleY:1.012,svgOrigin:"0 {quadril}",duration:1.7,repeat:{n},yoyo:true,ease:"sine.inOut"}},0);'
          f'tl.fromTo("#{p}-cab",{{y:0}},{{y:-5,duration:1.7,repeat:{n},yoyo:true,ease:"sine.inOut"}},0.2);')
    for t in piscadas:
        if t < dur - 0.3:
            js += f'tl.fromTo("#{p}-olho",{{scaleY:1,transformOrigin:"50% 50%"}},{{scaleY:0.08,transformOrigin:"50% 50%",duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t:.2f});'
    return js


def na_cabeca(svg, p, dentro):
    """Desenha `dentro` (coordenadas locais da pessoa) no fim de {p}-cab, por cima do cabelo e do rosto: acompanha o
    balanço da cabeça."""
    i = svg.index(f'<g id="{p}-cab">')
    prof = 0
    for m in re.finditer(r"<g\b|</g>", svg[i:]):
        prof += 1 if m.group(0) != "</g>" else -1
        if prof == 0:
            j = i + m.start()
            return svg[:j] + dentro + svg[j:]
    raise ValueError(p)


def cab_em_pe(variante="casa"):
    a = ANCORAS[("casa" if variante == "casa" else "trabalho", "em_pe", 30)]
    return a["cabeca_centro"], a["cabeca_topo"]


def raio_x(p, idc):
    """Cérebro rosa visto através do crânio (da testa para cima) da pessoa em pé. Id {idc} começa invisível."""
    (cx, cy), _ = cab_em_pe()
    ex, ey = cx - 4, cy - 30                    # crânio, da sobrancelha (y ~ cy - 8) para cima: os olhos ficam à vista
    return (f'<clipPath id="{idc}-cp"><ellipse cx="{ex}" cy="{ey}" rx="40" ry="22"/></clipPath>'
            f'<g id="{idc}" opacity="0" clip-path="url(#{idc}-cp)"><ellipse cx="{ex}" cy="{ey}" rx="40" ry="22" fill="#ff9fb4" opacity=".35"/>'
            f'<g transform="translate({ex} {ey + 6}) scale(.56) translate(-191 -90)">{cerebro_lateral(idc + "c")}</g></g>')


def fones(variante="casa"):
    """Fone de ouvido na cabeça em pé (giro 30): arco por cima do cabelo e concha na orelha visível (lado esquerdo)."""
    (cx, cy), (tx_, ty_) = cab_em_pe(variante)
    ex, ey = cx - 40, cy + 8
    return (f'<path d="M {ex + 2} {ey - 6} C {ex - 8} {ty_ - 18} {cx + 34} {ty_ - 14} {cx + 30} {ty_ + 18}" fill="none" stroke="#2a2a6a" stroke-width="9" stroke-linecap="round"/>'
            f'<path d="M {ex + 2} {ey - 6} C {ex - 8} {ty_ - 18} {cx + 34} {ty_ - 14} {cx + 30} {ty_ + 18}" fill="none" stroke="#8d7bff" stroke-width="2.5" stroke-linecap="round"/>'
            f'<ellipse cx="{ex}" cy="{ey}" rx="12" ry="17" fill="#2a2a6a" stroke="#8d7bff" stroke-width="3.5"/>'
            f'<ellipse cx="{ex - 2}" cy="{ey}" rx="5" ry="9" fill="#3be0ff" opacity=".8"/>')


def braco_js(g, t0, ang, dur, rep=0, variante="trabalho", pose="em_pe"):
    """Gira {g}-braco no ombro (svgOrigin local; % erra pelos retângulos de recorte)."""
    ox, oy = ANCORAS[("casa" if variante == "casa" else "trabalho", pose, 30)]["ombro_braco"]
    yo = ",yoyo:true" if rep else ""
    return (f'tl.fromTo("#{g}-braco",{{rotation:0,svgOrigin:"{ox} {oy}"}},{{rotation:{ang},svgOrigin:"{ox} {oy}",duration:{dur},repeat:{rep}{yo},'
            f'ease:"sine.inOut",immediateRender:false}},{t0:.2f});')


def deitada(svg, tx, ty, s):
    """Pessoa em pé (gente em_pe) deitada de barriga para cima, cabeça para a direita, pés em (tx, ty)."""
    return f'<g transform="translate({tx} {ty}) rotate(90) scale({-s} {s})">{svg}</g>'


def ela(p, pose="em_pe", glow=None, **kw):
    return tinge(gente(p, "casa", pose, glow=glow, **kw), AVENTAL)


def T(sg):
    return lambda w, n=0, d=None: palavra(CE, sg, w, n, d)


# ---------------------------------------------------------------- JS de apoio do grupo
LIB = r"""
  function _fz(sel,s,px,py,cx,cy){var e=document.querySelector(sel);if(e)e.setAttribute("transform","translate("+(cx-s*px).toFixed(2)+" "+(cy-s*py).toFixed(2)+") scale("+s.toFixed(5)+")");}
  function focoIni(sel,a,cx,cy){_fz(sel,a[2],a[0],a[1],cx,cy);}
  function foco(sel,t,dur,a,b,cx,cy,ease){var o={u:0};tl.fromTo(o,{u:0},{u:1,duration:dur,ease:ease||"power3.inOut",immediateRender:false,onUpdate:function(){
    var la=Math.log(a[2]),s=Math.exp(la+(Math.log(b[2])-la)*o.u),px=a[0]+(b[0]-a[0])*o.u,py=a[1]+(b[1]-a[1])*o.u;
    _fz(sel,s,px,py,cx,cy);}},t);}
  function marca(sel,t,dur){tl.fromTo(sel,{scaleX:0,transformOrigin:"0% 50%"},{scaleX:1,transformOrigin:"0% 50%",duration:dur||0.6,ease:"power2.inOut"},t);}
  function traco(sel,t,dur,len){tl.fromTo(sel,{attr:{"stroke-dashoffset":len}},{attr:{"stroke-dashoffset":0},duration:dur,ease:"power2.inOut"},t);}
  function pulsa(sel,t,dur,s,rep){tl.fromTo(sel,{scale:1,transformOrigin:"50% 50%"},{scale:s,transformOrigin:"50% 50%",duration:dur,repeat:rep,yoyo:true,ease:"sine.inOut",immediateRender:false},t);}
  function opa(sel,t,dur,a,b){tl.fromTo(sel,{opacity:a},{opacity:b,duration:dur,ease:"sine.inOut",immediateRender:false},t);}
  function olha(sel,t,x0,x1){tl.fromTo(sel,{x:x0},{x:x1,duration:0.35,ease:"power2.inOut",immediateRender:false},t);}
  function porta(sel,t,dur,a,b,ease){tl.fromTo(sel,{scaleX:a,transformOrigin:"100% 50%"},{scaleX:b,transformOrigin:"100% 50%",duration:dur,ease:ease||"power2.inOut",immediateRender:false},t);}
"""


def bob_js(sel, dur):
    """Mesmo balanço de motor.vida_pessoa, para sobreposições que precisam acompanhar a cabeça."""
    return f'tl.fromTo("{sel}",{{y:0}},{{y:-5,duration:1.6,repeat:{max(1, int(dur / 1.6))},yoyo:true,ease:"sine.inOut"}},0);'


def cena(p, dur, svg, html, js, extra=""):
    return composicao(p, dur, svg, html, LIB + js, extra)


def tx(id_, txt, left, top, tam, cor="#eef1f7", cls="tit", extra=""):
    est = f"left:{left}px;top:{top}px;font-size:{tam}px;color:{cor}"
    if cls == "pill2":
        est += ";letter-spacing:.14em"
    return texto(id_, txt, est + extra, cls)


def centro(id_, txt, top, tam, cor="#eef1f7", cls="tit", left=0, larg=1920):
    return texto(id_, txt, f"left:{left}px;width:{larg}px;text-align:center;top:{top}px;font-size:{tam}px;color:{cor}" +
                 (";letter-spacing:.14em" if cls == "pill2" else ""), cls)


def em(tx_, ty, s, dentro, cer=False):
    """Coloca `dentro` no sistema local da pessoa (mesmo translate/scale de `pessoa`). cer=True: no sistema do cérebro."""
    if cer:
        dentro = f'<g transform="translate(196 118) scale(.82) translate(-196 -118)">{dentro}</g>'
    return f'<g transform="translate({tx_} {ty}) scale({s})">{dentro}</g>'


# ---------------------------------------------------------------- cenário fixo: pessoa, porta, máquina
PX, PY, PS = -165, 190, 2.5          # pessoa nas cenas da porta: caixa x 110..585, y 260..820
CER_W = (PX + 193 * PS, PY + 91 * PS)  # centro do cérebro em coordenadas do mundo


def trio_defs(p):
    return f"""<linearGradient id="{p}-chao" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b1e54"/><stop offset="1" stop-color="#090b26"/></linearGradient>
<linearGradient id="{p}-maqG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e4e8ff"/><stop offset="1" stop-color="#8e96d0"/></linearGradient>
<linearGradient id="{p}-folG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2c2a88"/><stop offset="1" stop-color="#1a1856"/></linearGradient>
<linearGradient id="{p}-luzG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff6c8"/><stop offset="1" stop-color="#9af0ff"/></linearGradient>
<linearGradient id="{p}-cunG" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff2b8" stop-opacity=".75"/><stop offset="1" stop-color="#fff2b8" stop-opacity="0"/></linearGradient>
<radialGradient id="{p}-tunG" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#bff6ff" stop-opacity="1"/><stop offset=".5" stop-color="#3be0ff" stop-opacity=".55"/><stop offset="1" stop-color="#3be0ff" stop-opacity="0"/></radialGradient>
<radialGradient id="{p}-tunVG" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffc2cf" stop-opacity="1"/><stop offset=".5" stop-color="#ff4f7d" stop-opacity=".6"/><stop offset="1" stop-color="#ff4f7d" stop-opacity="0"/></radialGradient>"""


def chao(p, y=838):
    return (f'<rect x="-400" y="{y}" width="2720" height="600" fill="url(#{p}-chao)"/>'
            f'<line x1="-400" y1="{y + 2}" x2="2320" y2="{y + 2}" stroke="#8d7bff" stroke-width="3" opacity=".35"/>')


def quarto_defs(p):
    return f"""<linearGradient id="{p}-parede" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#232a6e"/><stop offset="1" stop-color="#121644"/></linearGradient>
<linearGradient id="{p}-manta" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a82e0"/><stop offset="1" stop-color="#2c4a9a"/></linearGradient>
<linearGradient id="{p}-tela" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16143a"/><stop offset="1" stop-color="#0b1c40"/></linearGradient>"""


def porta_svg(p, luz=0.0):
    """Porta em pé no meio (x 860..1080, y 380..840). Folha com dobradiça à direita: {p}-folha (scaleX abre)."""
    return f"""<g id="{p}-porta"><rect x="840" y="830" width="260" height="14" rx="6" fill="#05031a" opacity=".6"/>
<rect x="866" y="386" width="208" height="454" fill="#06051a"/>
<rect id="{p}-luz" x="866" y="386" width="208" height="454" fill="url(#{p}-luzG)" opacity="{luz}"/>
<polygon id="{p}-cunha" points="866,840 920,840 780,940 520,940" fill="url(#{p}-cunG)" opacity="{luz}"/>
<g id="{p}-folha"><rect x="870" y="390" width="200" height="450" fill="url(#{p}-folG)" stroke="#8d7bff" stroke-width="4"/>
<rect x="892" y="420" width="156" height="170" rx="8" fill="none" stroke="#5a5ad0" stroke-width="4"/><rect x="892" y="620" width="156" height="190" rx="8" fill="none" stroke="#5a5ad0" stroke-width="4"/>
<circle cx="896" cy="612" r="11" fill="#ffb23e"/></g>
<rect x="856" y="376" width="228" height="468" fill="none" stroke="#8d7bff" stroke-width="12" filter="url(#{p}-glow)"/></g>"""


def maquina(p):
    """Máquina de ressonância (x 1160..1820, y 330..840): carcaça, túnel com anel ciano, mesa."""
    return f"""<g id="{p}-maq"><ellipse cx="1500" cy="846" rx="380" ry="22" fill="#05031a" opacity=".6"/>
<rect x="1250" y="674" width="40" height="166" rx="6" fill="#3a3a8a" stroke="#8d7bff" stroke-width="3"/><rect x="1176" y="674" width="24" height="166" rx="6" fill="#3a3a8a" stroke="#8d7bff" stroke-width="3"/><rect x="1160" y="832" width="150" height="10" rx="5" fill="#8d7bff" opacity=".7"/>
<g filter="url(#{p}-sombra)"><rect x="1300" y="330" width="520" height="510" rx="96" fill="url(#{p}-maqG)"/></g>
<rect x="1300" y="782" width="520" height="18" fill="#8d7bff" opacity=".55"/>
<circle cx="1560" cy="560" r="184" fill="#b4bbe8"/><circle cx="1560" cy="560" r="168" fill="#0b0a24"/>
<circle cx="1560" cy="560" r="120" fill="#14123a"/>
<circle id="{p}-tun" cx="1560" cy="560" r="150" fill="url(#{p}-tunG)" opacity=".25"/>
<circle id="{p}-tunV" cx="1560" cy="560" r="150" fill="url(#{p}-tunVG)" opacity="0"/>
<circle id="{p}-anel" cx="1560" cy="560" r="168" fill="none" stroke="#3be0ff" stroke-width="10" opacity=".35" filter="url(#{p}-glow)"/>
<circle id="{p}-anelV" cx="1560" cy="560" r="168" fill="none" stroke="#ff4f7d" stroke-width="12" opacity="0" filter="url(#{p}-glow)"/>
<rect x="1160" y="640" width="430" height="34" rx="12" fill="#dfe4ff" stroke="#8d7bff" stroke-width="3"/>
<path d="M1336 372 Q1560 330 1784 372" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="10" stroke-linecap="round"/></g>"""


def pessoa_porta(p):
    return f'<ellipse cx="360" cy="846" rx="230" ry="18" fill="#05031a" opacity=".55"/>' + pessoa(p, PX, PY, PS)


# ---------------------------------------------------------------- ler 0: "Arquivo três. Ler."
def ler_0():
    p, sg = "ler_0", 0
    ini, dur = seg(CE, sg)
    t = T(sg)
    t_arq, t_3, t_ler = t("arquivo"), t("3"), t("le")
    extra = f"""<linearGradient id="{p}-frente" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a3aa6"/><stop offset="1" stop-color="#2c2380"/></linearGradient>
<linearGradient id="{p}-papel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#e9dcc2"/></linearGradient>
<radialGradient id="{p}-haloG" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ff9fb4" stop-opacity=".8"/><stop offset="1" stop-color="#ff9fb4" stop-opacity="0"/></radialGradient>"""
    tx_, ty_, s_ = 238, 288, 2.2
    svg = f"""<g id="{p}-pasta">
<ellipse cx="960" cy="940" rx="620" ry="30" fill="#05031a" opacity=".55" filter="url(#{p}-blur6)"/>
<rect x="410" y="96" width="400" height="150" rx="24" fill="#2a1d70" stroke="#8d7bff" stroke-width="5"/>
<text x="446" y="178" font-family="IBM Plex Mono" font-weight="700" font-size="48" letter-spacing="5" fill="#3be0ff">ARQUIVO</text>
<g id="{p}-n3"><circle cx="740" cy="160" r="40" fill="#ffb23e"/><text x="740" y="178" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="54" fill="#1a1050">3</text></g>
<rect x="410" y="232" width="1100" height="672" rx="26" fill="#211862"/>
<g filter="url(#{p}-sombra)"><rect x="470" y="196" width="980" height="560" rx="10" fill="url(#{p}-papel)" transform="rotate(-2 960 480)"/>
<rect x="500" y="214" width="940" height="560" rx="10" fill="#f4ecd8" transform="rotate(1.6 960 480)"/></g>
<g fill="#8a7f68" opacity=".45"><rect x="980" y="238" width="380" height="12" rx="6"/><rect x="980" y="266" width="300" height="12" rx="6"/></g>
<g filter="url(#{p}-sombra)"><rect x="400" y="292" width="1120" height="620" rx="26" fill="url(#{p}-frente)"/></g>
<rect x="400" y="292" width="1120" height="620" rx="26" fill="none" stroke="#8d7bff" stroke-width="6" filter="url(#{p}-glow)"/>
<ellipse id="{p}-halo" cx="{tx_ + 193 * s_:.0f}" cy="{ty_ + 91 * s_:.0f}" rx="230" ry="160" fill="url(#{p}-haloG)" opacity="0"/>
{pessoa(p, tx_, ty_, s_)}
<g id="{p}-scan" opacity="0"><rect x="470" y="340" width="470" height="8" rx="4" fill="#3be0ff" filter="url(#{p}-glow)"/><rect x="470" y="300" width="470" height="44" fill="#3be0ff" opacity=".12"/></g>
</g>"""
    html = tx(f"{p}-ler", "Ler", 1000, 420, 270)
    js = f"""
  camZ("#{p}-cam", 0, {dur:.2f}, 1.0, 1.05, 960, 540, "none");
  tl.fromTo("#{p}-pasta",{{y:780,rotation:5,transformOrigin:"50% 50%"}},{{y:0,rotation:0,transformOrigin:"50% 50%",duration:0.9,ease:"expo.out"}},{max(0.05, t_arq - 0.15):.2f});
  pop("#{p}-n3", {t_3:.2f}, 0.2, 0.7);
  rise("#{p}-ler > span", {t_ler:.2f}, 0.8);
  tl.fromTo("#{p}-scan",{{y:0,opacity:0}},{{y:470,opacity:1,duration:0.7,ease:"power1.inOut"}},{t_ler - 0.1:.2f});
  some("#{p}-scan", {t_ler + 0.6:.2f}, 0.15);
  opa("#{p}-halo", {t_ler:.2f}, 0.4, 0, 1);
  pulsa("#{p}-cer", {t_ler + 0.1:.2f}, 0.22, 1.07, 1);
""" + vida_pessoa(p, dur, (1.3,))
    return cena(p, dur, svg, html, js, extra)


# ---------------------------------------------------------------- ler 1: a mosca na fruta, e uma pessoa viva olhando para ela
def ler_1():
    p, sg = "ler_1", 1
    ini, dur = seg(CE, sg)
    t = T(sg)
    t_cer, t_mosca, t_ler, t_cer2, t_vivo = t("cerebro"), t("mosca"), t("ler"), t("cerebro", 1), t("vivo")
    FX, FY, FR = 600, 780, 150          # fruta; o chão fica em y = FY + FR
    CHAO = FY + FR
    MX, MY, MS = 540, 566, 0.9          # mosca em pé no alto da fruta
    GX, GS = 1390, 1.12                 # pessoa espelhada (olha para a esquerda, para a mosca)
    gp = f"{p}-g"
    extra = mosca_defs(p + "m") + trio_defs(p) + f"""<radialGradient id="{p}-fruta" cx="38%" cy="30%" r="80%"><stop offset="0" stop-color="#ffc35a"/><stop offset=".6" stop-color="#ff8a2a"/><stop offset="1" stop-color="#d9501c"/></radialGradient>
<radialGradient id="{p}-haloG" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ff9fb4" stop-opacity=".7"/><stop offset="1" stop-color="#ff9fb4" stop-opacity="0"/></radialGradient>
<linearGradient id="{p}-scanG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3be0ff" stop-opacity="0"/><stop offset=".8" stop-color="#3be0ff" stop-opacity=".35"/><stop offset="1" stop-color="#bff6ff" stop-opacity="1"/></linearGradient>"""
    fruta = (f'<g transform="translate({FX} {FY})"><ellipse cx="0" cy="{FR + 2}" rx="{FR * 1.2:.0f}" ry="20" fill="#05031a" opacity=".55"/>'
             f'<circle r="{FR}" fill="url(#{p}-fruta)" filter="url(#{p}-sombra)"/><ellipse cx="-50" cy="-56" rx="38" ry="64" fill="#fff" opacity=".28" transform="rotate(28 -50 -56)"/>'
             f'<g transform="rotate(32)"><path d="M0 -144 C-4 -174 12 -192 32 -200" stroke="#4b7a2a" stroke-width="12" fill="none" stroke-linecap="round"/>'
             f'<path d="M18 -177 C66 -204 114 -180 102 -150 C72 -150 42 -158 18 -177 Z" fill="#58b84a" transform="translate(-14 26)"/></g></g>')
    sombra_mosca = f'<ellipse cx="{MX + 6}" cy="{MY + 80}" rx="92" ry="12" fill="#5a1a08" opacity=".45" filter="url(#{p}-blur6)"/>'
    mosca = (f'<g transform="translate({MX} {MY}) scale({MS})"><g id="{p}-moscaB"><g filter="url(#{p}-sombra)">{mosca_rica(p + "-mo", p + "m")}</g></g></g>')
    corpo = na_cabeca(gente(gp, "casa", "em_pe", glow=f"{p}-glow"), gp, raio_x(gp, f"{p}-cx"))
    # cabeça da pessoa em coordenadas do mundo (para halo e varredura)
    (acx, acy), (_, aty) = cab_em_pe()
    hx0, hx1 = GX - GS * (acx + 52), GX - GS * (acx - 52)
    hy0, hy1 = CHAO + GS * aty, CHAO + GS * (acy + 56)
    hcx, hcy = (hx0 + hx1) / 2, (hy0 + hy1) / 2
    svg = f"""{chao(p, CHAO)}
<ellipse id="{p}-halo" cx="{hcx:.0f}" cy="{hcy:.0f}" rx="240" ry="200" fill="url(#{p}-haloG)" opacity="0"/>
<g transform="translate({GX} {CHAO}) scale({-GS} {GS})"><g id="{p}-gW">{corpo}</g></g>
<clipPath id="{p}-scc"><ellipse cx="{hcx:.0f}" cy="{hcy:.0f}" rx="{GS * 56:.0f}" ry="{GS * 62:.0f}"/></clipPath><g clip-path="url(#{p}-scc)"><g id="{p}-scan" opacity="0"><rect x="{hx0 - 150:.0f}" y="{hy0 - 20:.0f}" width="150" height="{hy1 - hy0 + 40:.0f}" fill="url(#{p}-scanG)"/></g></g>
{fruta}{sombra_mosca}{mosca}"""
    html = (tx(f"{p}-m1", "Mapear o cérebro", 1040, 330, 100) + tx(f"{p}-m2", "de uma mosca", 1040, 470, 100, "#9af0ff") +
            tx(f"{p}-t1", "Ler um cérebro", 110, 110, 124) +
            tx(f"{p}-t2", 'humano <span style="color:#ff9fb4">vivo</span>', 110, 270, 124))
    A0, A1, B0, B1 = "[740,700,2.0]", "[740,700,2.1]", "[960,540,1.0]", "[960,540,1.04]"
    C = "960,540"
    js = f"""
  focoIni("#{p}-cam",{A0},{C});
  foco("#{p}-cam",0,{t_ler - 0.25:.2f},{A0},{A1},{C},"none");
  foco("#{p}-cam",{t_ler - 0.25:.2f},1.4,{A1},{B0},{C},"power3.inOut");
  foco("#{p}-cam",{t_ler + 1.15:.2f},{dur - t_ler - 1.15:.2f},{B0},{B1},{C},"none");
  tl.fromTo("#{p}-mo-asas",{{scaleY:1,transformOrigin:"50% 100%"}},{{scaleY:0.35,transformOrigin:"50% 100%",duration:0.05,repeat:15,yoyo:true,ease:"none"}},{t_mosca:.2f});
  tl.fromTo("#{p}-moscaB",{{y:0}},{{y:-6,duration:0.8,repeat:6,yoyo:true,ease:"sine.inOut"}},0);
  tl.fromTo("#{p}-mo-cerebro",{{opacity:0}},{{opacity:1,duration:0.3}},{t_cer:.2f});
  pulsa("#{p}-mo-cerebro",{t_mosca:.2f},0.2,1.8,3);
  rise("#{p}-m1 > span",{max(0.1, t_cer - 0.4):.2f}); rise("#{p}-m2 > span",{t_mosca - 0.1:.2f});
  some("#{p}-m1",{t_ler - 0.4:.2f},0.3); some("#{p}-m2",{t_ler - 0.4:.2f},0.3);
  rise("#{p}-t1 > span",{t_ler + 0.3:.2f});
  rise("#{p}-t2 > span",{t_vivo - 0.25:.2f},0.8);
  entra("#{p}-scan",{t_cer2 - 0.1:.2f},0.15);
  tl.fromTo("#{p}-scan",{{x:0}},{{x:{hx1 - hx0 + 150:.0f},duration:0.8,ease:"power1.inOut",immediateRender:false}},{t_cer2 - 0.1:.2f});
  some("#{p}-scan",{t_cer2 + 0.65:.2f},0.15);
  tl.fromTo("#{p}-cx",{{opacity:0}},{{opacity:0.8,duration:0.6,immediateRender:false}},{t_cer2 + 0.1:.2f});
  opa("#{p}-halo",{t_vivo - 0.2:.2f},0.4,0,1);
  pulsa("#{p}-halo",{t_vivo + 0.2:.2f},0.35,1.12,1);
  pulsa("#{p}-cx",{t_vivo:.2f},0.3,1.05,1);
""" + vida_g(gp, dur, (1.6, t_vivo + 0.3))
    return cena(p, dur, svg, html, js, extra)


# ---------------------------------------------------------------- página de artigo com câmera
def pagina(p, img, w, h, painel, marcas, adornos=""):
    """Painel com a página real (`assets/docs/img.png`) recortada. marcas: [(id, x, y, w, h)] em px da página."""
    x0, y0, pw, ph = painel
    rects = "".join(f'<rect id="{p}-{k}" x="{x}" y="{y}" width="{ww}" height="{hh}" rx="6" fill="#ffd23e" opacity=".55" style="mix-blend-mode:multiply"/>'
                    for k, x, y, ww, hh in marcas)
    fd = "".join(f'<linearGradient id="{p}-fd{k}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="#fff" stop-opacity=".97"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                 for k, x1, y1, x2, y2 in [("L", 0, 0, 1, 0), ("R", 1, 0, 0, 0), ("T", 0, 0, 0, 1), ("B", 0, 1, 0, 0)])
    return f"""{fd}<clipPath id="{p}-clip"><rect x="{x0}" y="{y0}" width="{pw}" height="{ph}" rx="26"/></clipPath>
<g filter="url(#{p}-sombra)"><rect x="{x0}" y="{y0}" width="{pw}" height="{ph}" rx="26" fill="#0e0c26"/></g>
<g clip-path="url(#{p}-clip)"><g id="{p}-pgW"><g id="{p}-pg">
<rect x="0" y="0" width="{w}" height="{h}" fill="#fff"/>
<image href="assets/docs/{img}.png" x="0" y="0" width="{w}" height="{h}"/>{rects}{adornos}</g></g>
<rect x="{x0}" y="{y0}" width="90" height="{ph}" fill="url(#{p}-fdL)"/><rect x="{x0 + pw - 90}" y="{y0}" width="90" height="{ph}" fill="url(#{p}-fdR)"/>
<rect x="{x0}" y="{y0}" width="{pw}" height="70" fill="url(#{p}-fdT)"/><rect x="{x0}" y="{y0 + ph - 70}" width="{pw}" height="70" fill="url(#{p}-fdB)"/></g>
<rect x="{x0}" y="{y0}" width="{pw}" height="{ph}" rx="26" fill="none" stroke="#8d7bff" stroke-width="6" filter="url(#{p}-glow)"/>"""


# ---------------------------------------------------------------- ler 3: Owen 2006, página real
def ler_3():
    p, sg = "ler_3", 3
    ini, dur = seg(CE, sg)
    t = T(sg)
    t_adr, t_owen, t_maq, t_res, t_img, t_voc, t_jog, t_ten = t("adrian"), t("owen"), t("maquina"), t("ressonancia"), t("imagine"), t("voce"), t("jogando"), t("tenis")
    W, H = 1600, 2037
    marcas = [("m0", 92, 196, 690, 58), ("m1", 92, 262, 408, 58), ("m2", 92, 338, 196, 32),
              ("m4", 1052, 131, 456, 29), ("m5", 1052, 159, 456, 29)]
    ador = (f'<rect id="{p}-fig" x="346" y="1197" width="678" height="506" fill="none" stroke="#3be0ff" stroke-width="7" stroke-dasharray="2400" stroke-dashoffset="2400"/>'
            f'<g id="{p}-scan" opacity="0"><rect x="346" y="1197" width="678" height="10" fill="#3be0ff"/><rect x="346" y="1157" width="678" height="40" fill="#3be0ff" opacity=".18"/></g>'
            f'<circle id="{p}-bb0" cx="525" cy="1293" r="46" fill="none" stroke="#ffb23e" stroke-width="7" opacity="0"/>'
            f'<circle id="{p}-bb1" cx="519" cy="1518" r="46" fill="none" stroke="#ffb23e" stroke-width="7" opacity="0"/>')
    svg = pagina(p, "owen2006", W, H, (60, 60, 1120, 960), marcas, ador)
    C = "620,540"
    K0, K1, K2, K3, K4 = "[800,690,0.71]", "[525,470,1.08]", "[685,1490,1.3]", "[1308,345,2.0]", "[1308,350,2.12]"
    L = 1240
    html = (tx(f"{p}-a1", "Adrian", L, 210, 150) + tx(f"{p}-a2", "Owen", L, 390, 150, "#ffd98a") +
            tx(f"{p}-b1", "MÁQUINA DE", L, 300, 52, "#3be0ff", "pill2") + tx(f"{p}-b2", "ressonância", L, 380, 108) +
            tx(f"{p}-c1", "Imagine que", L, 170, 104) + tx(f"{p}-c2", "você está", L, 310, 104) +
            tx(f"{p}-c3", 'jogando <b style="color:#ffd98a">tênis</b>', L, 450, 96) +
            tx(f"{p}-src", "SCIENCE · 2006", L, 920, 46, "#ffb23e", "pill2"))
    js = f"""
  tl.fromTo("#{p}-pgW",{{y:1000,rotation:-6,transformOrigin:"50% 50%"}},{{y:0,rotation:0,transformOrigin:"50% 50%",duration:1.0,ease:"expo.out"}},0.05);
  focoIni("#{p}-pg",{K0},{C});
  marca("#{p}-m0",0.8,0.5); marca("#{p}-m1",1.15,0.4);
  rise("#{p}-src > span",0.9);
  foco("#{p}-pg",{t_adr - 0.35:.2f},1.2,{K0},{K1},{C});
  marca("#{p}-m2",{t_adr + 0.4:.2f},0.4);
  rise("#{p}-a1 > span",{t_adr:.2f}); rise("#{p}-a2 > span",{t_owen + 0.15:.2f});
  some("#{p}-a1",{t_maq - 0.3:.2f},0.3); some("#{p}-a2",{t_maq - 0.3:.2f},0.3);
  foco("#{p}-pg",{t_maq - 0.3:.2f},1.3,{K1},{K2},{C});
  rise("#{p}-b1 > span",{t_maq:.2f}); rise("#{p}-b2 > span",{t_res:.2f});
  traco("#{p}-fig",{t_maq + 0.4:.2f},0.9,2400);
  entra("#{p}-scan",{t_res - 0.1:.2f},0.2);
  tl.fromTo("#{p}-scan",{{y:0}},{{y:496,duration:0.7,repeat:1,yoyo:true,ease:"sine.inOut"}},{t_res - 0.1:.2f});
  some("#{p}-scan",{t_res + 1.3:.2f},0.2);
  pop("#{p}-bb0",{t_res + 0.5:.2f},0.3); pop("#{p}-bb1",{t_res + 0.75:.2f},0.3);
  some("#{p}-b1",{t_img - 0.4:.2f},0.3); some("#{p}-b2",{t_img - 0.4:.2f},0.3);
  foco("#{p}-pg",{t_img - 0.35:.2f},1.2,{K2},{K3},{C});
  foco("#{p}-pg",{t_img + 0.85:.2f},{dur - t_img - 0.85:.2f},{K3},{K4},{C},"none");
  marca("#{p}-m4",{t_img + 0.3:.2f},0.6); marca("#{p}-m5",{t_voc + 0.3:.2f},0.6);
  rise("#{p}-c1 > span",{t_img:.2f}); rise("#{p}-c2 > span",{t_voc:.2f}); rise("#{p}-c3 > span",{t_jog - 0.1:.2f},0.6);
"""
    return cena(p, dur, svg, html, js)


# ---------------------------------------------------------------- ler 4: no quarto de hospital, o exame dela igual ao de pessoas saudáveis
def ler_4():
    p, sg = "ler_4", 4
    ini, dur = seg(CE, sg)
    t = T(sg)
    t_resp, t_mesmo, t_pess, t_ela, t_ouv, t_presa, t_prop, t_sem, t_avi = (t("responde"), t("mesmo"), t("pessoas"), t("ela"), t("ouvindo"),
                                                                           t("presa"), t("proprio"), t("sem"), t("avisar"))
    gp = f"{p}-g"
    TX, TY, S = 831, 640, 1.0                       # pés dela; deitada: (x, y) local vira (TX - y, TY - x); cabeça em x ~ 1275..1375
    ear = (TX + 482, TY - 6)                        # cabeça (mundo), para onde as ondas convergem
    extra = quarto_defs(p) + f"""<radialGradient id="{p}-blobG" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff2b0"/><stop offset=".45" stop-color="#ffb23e" stop-opacity=".9"/><stop offset="1" stop-color="#ff7a2a" stop-opacity="0"/></radialGradient>
<clipPath id="{p}-tl"><rect x="176" y="126" width="798" height="300"/></clipPath>"""
    SC = 1.25
    painel = lambda k, cx: (f'<g transform="translate({cx - 192 * SC:.1f} {300 - 84 * SC:.1f}) scale({SC})">{cerebro_lateral(f"{p}-c{k}")}'
                            f'<g id="{p}-bl{k}" opacity="0"><circle cx="205" cy="58" r="30" fill="url(#{p}-blobG)"/></g></g>')
    bl = lambda cx: (cx + (205 - 192) * SC, 300 + (58 - 84) * SC)
    (ax_, ay_), (bx_, by_) = bl(375), bl(775)

    def rotulo_svg(k, linhas, cx, cor):
        tsp = "".join(f'<text x="{cx}" y="{y}" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="44" letter-spacing="6" fill="{cor}">{s}</text>'
                      for s, y in linhas)
        return f'<clipPath id="{p}-lc{k}"><rect x="{cx - 200}" y="428" width="400" height="104"/></clipPath><g clip-path="url(#{p}-lc{k})"><g id="{p}-lb{k}">{tsp}</g></g>'

    monitor = f"""<g filter="url(#{p}-sombra)"><rect x="555" y="560" width="40" height="236" fill="#3a3a8a" stroke="#8d7bff" stroke-width="3"/><rect x="480" y="788" width="190" height="16" rx="8" fill="#3a3a8a" stroke="#8d7bff" stroke-width="3"/><rect x="150" y="100" width="850" height="460" rx="28" fill="#14122e" stroke="#8d7bff" stroke-width="8"/></g>
<rect x="176" y="126" width="798" height="408" rx="14" fill="url(#{p}-tela)"/>
<line x1="575" y1="150" x2="575" y2="510" stroke="#3a3a8a" stroke-width="4"/>
<g clip-path="url(#{p}-tl)">{painel("a", 375)}{painel("b", 775)}</g>
{rotulo_svg("a", [("DELA", 492)], 375, "#ffd98a")}{rotulo_svg("b", [("PESSOAS", 466), ("SAUDÁVEIS", 516)], 775, "#3be0ff")}
<path id="{p}-arco" d="M{ax_:.0f} {ay_ - 30:.0f} Q 575 120 {bx_:.0f} {by_ - 30:.0f}" fill="none" stroke="#ffb23e" stroke-width="7" stroke-linecap="round" stroke-dasharray="700" stroke-dashoffset="700" filter="url(#{p}-glow)"/>"""
    cama = f"""<ellipse cx="1060" cy="936" rx="480" ry="22" fill="#05031a" opacity=".55"/>
<g fill="#4a4ab0"><rect x="690" y="780" width="20" height="140"/><rect x="1410" y="780" width="20" height="140"/></g>
<circle cx="700" cy="922" r="15" fill="#2a2a6a" stroke="#8d7bff" stroke-width="3"/><circle cx="1420" cy="922" r="15" fill="#2a2a6a" stroke="#8d7bff" stroke-width="3"/>
<rect x="660" y="742" width="800" height="46" rx="14" fill="#2a2a6a" stroke="#8d7bff" stroke-width="3"/>
<rect x="1452" y="586" width="34" height="236" rx="14" fill="#3a3a8a" stroke="#8d7bff" stroke-width="4"/>
<rect x="640" y="696" width="820" height="56" rx="22" fill="#dfe4ff"/>
<ellipse cx="1335" cy="694" rx="118" ry="26" fill="#f4f6ff"/>"""
    mulher = deitada(ela(gp, "em_pe", glow=f"{p}-glow", sombra=False), TX, TY, S)
    manta = (f'<path d="M 650 752 L 650 640 C 680 604 740 600 792 598 C 800 540 884 534 894 596 C 980 590 1060 584 1214 602 C 1228 640 1230 700 1226 752 Z" fill="url(#{p}-manta)"/>'
             f'<path d="M 820 610 C 920 600 1060 600 1180 614" stroke="#fff" stroke-opacity=".28" stroke-width="10" fill="none" stroke-linecap="round"/>')
    borda = f'<rect id="{p}-borda" x="{TX - 40}" y="530" width="{600}" height="190" rx="95" fill="none" stroke="#ff4f7d" stroke-width="7" opacity="0" filter="url(#{p}-glow)"/>'
    # ondas de som: arcos (sem recorte) que encolhem até a orelha; círculo invisível centra a caixa na orelha
    a0, a1 = math.radians(200), math.radians(252)
    arco = (f'M{ear[0] + 300 * math.cos(a0):.0f} {ear[1] + 300 * math.sin(a0):.0f} A300 300 0 0 1 '
            f'{ear[0] + 300 * math.cos(a1):.0f} {ear[1] + 300 * math.sin(a1):.0f}')
    ondas = "".join(f'<g id="{p}-o{k}" opacity="0"><circle cx="{ear[0]}" cy="{ear[1]}" r="300" fill="none"/>'
                    f'<path d="{arco}" fill="none" stroke="#3be0ff" stroke-width="9" stroke-linecap="round" vector-effect="non-scaling-stroke"/></g>' for k in range(3))
    svg = f"""<rect x="-400" y="-300" width="2720" height="1100" fill="url(#{p}-parede)"/>{chao(p, 800)}
{monitor}{cama}{mulher}{manta}{borda}<g filter="url(#{p}-glow)">{ondas}</g>"""
    html = (tx(f"{p}-t0", "Ela estava ouvindo", 1000, 130, 96, "#9af0ff") + tx(f"{p}-t1", "Presa dentro", 1000, 150, 112) +
            tx(f"{p}-t2", "do próprio corpo", 1000, 300, 112) + tx(f"{p}-t3", "SEM CONSEGUIR AVISAR", 1006, 500, 48, "#ff4f7d", "pill2"))
    C = "960,540"
    K0, K1, KW, KD, KE = "[575,330,1.42]", "[575,330,1.5]", "[960,540,1.0]", "[1540,540,1.8]", "[1540,540,1.9]"
    ondas_js = "".join(
        f'tl.fromTo("#{p}-o{k}",{{scale:1.1,opacity:0,transformOrigin:"50% 50%"}},{{scale:0.14,opacity:1,transformOrigin:"50% 50%",duration:0.6,ease:"power1.in",repeat:2,immediateRender:false}},{t_ela + 0.2 + k * 0.2:.2f});'
        f'tl.set("#{p}-o{k}",{{opacity:0}},{t_presa - 0.1:.2f});' for k in range(3))
    borda_js = "".join(f'tl.fromTo("#{p}-borda",{{opacity:0}},{{opacity:1,duration:0.15,repeat:1,yoyo:true,immediateRender:false}},{t_presa + 0.2 + k * 0.9:.2f});' for k in range(3))
    js = f"""
  focoIni("#{p}-cam",{K0},{C});
  foco("#{p}-cam",0,{t_mesmo - 0.4:.2f},{K0},{K1},{C},"none");
  foco("#{p}-cam",{t_mesmo - 0.4:.2f},1.2,{K1},{KW},{C});
  foco("#{p}-cam",{t_ela - 0.35:.2f},1.4,{KW},{KD},{C});
  foco("#{p}-cam",{t_ela + 1.05:.2f},{dur - t_ela - 1.05:.2f},{KD},{KE},{C},"none");
  opa("#{p}-bla",{t_resp:.2f},0.25,0,1); pulsa("#{p}-bla",{t_resp:.2f},0.35,1.3,7);
  tl.fromTo("#{p}-lba",{{y:110}},{{y:0,duration:0.75,ease:"expo.out"}},{t_resp + 0.2:.2f});
  opa("#{p}-blb",{t_mesmo + 0.3:.2f},0.25,0,1); pulsa("#{p}-blb",{t_mesmo + 0.3:.2f},0.35,1.3,5);
  traco("#{p}-arco",{t_mesmo + 0.4:.2f},0.9,700);
  tl.fromTo("#{p}-lbb",{{y:110}},{{y:0,duration:0.75,ease:"expo.out"}},{t_pess:.2f});
  rise("#{p}-t0 > span",{t_ela + 0.45:.2f}); some("#{p}-t0",{t_presa - 0.3:.2f},0.3);
  rise("#{p}-t1 > span",{t_presa:.2f}); rise("#{p}-t2 > span",{t_prop:.2f}); rise("#{p}-t3 > span",{t_sem + 0.2:.2f});
  tl.fromTo("#{p}-borda",{{opacity:0}},{{opacity:0.55,duration:0.4,immediateRender:false}},{t_presa + 2.9:.2f});
""" + ondas_js + borda_js + vida_g(gp, dur, (1.5, 4.2, t_ouv + 0.1, t_avi - 0.5, t_avi - 0.2))
    return cena(p, dur, svg, html, js, extra)


# ---------------------------------------------------------------- ler 5: a discussão de anos, depois 241 leitos e um de cada quatro acende
def ler_5():
    p, sg = "ler_5", 5
    ini, dur = seg(CE, sg)
    t = T(sg)
    t_cont, t_disc, t_dur, t_2024, t_est, t_241, t_sin, t_um = (t("contestacao"), t("discussao"), t("durou"), t("2024"), t("estudo"), t("240"),
                                                                 t("sinais"), t("um", 2))
    cols, rows, x0, y0, px_, py_, ms = 22, 11, 124, 200, 76, 68, 0.235
    rng = random.Random(24)
    todos = [(r, c) for r in range(rows) for c in range(cols)][:241]
    acesos = set(rng.sample(todos, 60))
    leito = f"""<g id="{p}-leito"><rect x="-128" y="62" width="14" height="44" fill="#4a4ab0"/><rect x="110" y="62" width="14" height="44" fill="#4a4ab0"/>
<rect x="-136" y="54" width="268" height="16" rx="6" fill="#4a4ab0"/><rect x="124" y="-40" width="20" height="130" rx="9" fill="#6a7bd0"/>
<rect x="-140" y="26" width="270" height="32" rx="12" fill="#dfe4ff"/><ellipse cx="80" cy="24" rx="44" ry="13" fill="#f4f6ff"/>
<circle cx="80" cy="2" r="24" fill="{PELE}"/><path d="M 84 -22 C 110 -20 112 16 96 22 C 104 8 102 -10 84 -22 Z" fill="#3a2216"/>
<path d="M -132 30 L -132 0 C -122 -26 -98 -26 -90 -6 C -40 -14 20 -16 56 -4 L 60 30 Z" fill="#5a82e0"/></g>
<g id="{p}-aceso"><circle cx="80" cy="2" r="58" fill="#ffb23e" opacity=".35"/><circle cx="80" cy="2" r="27" fill="none" stroke="#ffd27a" stroke-width="7"/>
<circle cx="80" cy="-62" r="17" fill="#fff2b0"/></g>"""
    cel = lambda r, c: (x0 + px_ / 2 + c * px_, y0 + py_ / 2 + r * py_)
    ce = (5, 10)
    cells, lit = {}, []
    for (r, c) in todos:
        x, y = cel(r, c)
        d = max(abs(r - ce[0]), abs(c - ce[1]))
        u = f'transform="translate({x:.1f} {y + 6:.1f}) scale({ms})"'
        cells.setdefault(d, []).append(f'<use href="#{p}-leito" {u}/>')
        if (r, c) in acesos:
            lit.append(f'<use class="ac" href="#{p}-aceso" {u} opacity="0"/>')
    grade = "".join(f'<g id="{p}-d{d}" opacity="0">{"".join(us)}</g>' for d, us in sorted(cells.items()))
    rng.shuffle(lit)
    # debate: dois cientistas, um de frente para o outro
    ga, gb = f"{p}-ga", f"{p}-gb"
    deb = f"""<g id="{p}-deb">{chao(p, 930)}
<g transform="translate(640 930)"><g id="{ga}W">{gente(ga, "trabalho", "em_pe", glow=f"{p}-glow")}</g></g>
<g transform="translate(1290 930) scale(-1 1)"><g id="{gb}W">{tinge(gente(gb, "trabalho", "em_pe", glow=f"{p}-glow"), CIENT2)}</g></g>"""
    for k, (x, y, s, c) in enumerate([(860, 390, 230, "#ffb23e"), (1070, 340, 200, "#3be0ff"), (960, 560, 170, "#ff4fa3")]):
        deb += (f'<g transform="translate({x} {y})"><g id="{p}-q{k}" opacity="0"><rect x="-10" y="-10" width="20" height="20" fill="none"/>'
                f'<text x="0" y="{s * 0.34:.0f}" text-anchor="middle" font-size="{s}" font-weight="700" font-family="EB Garamond" fill="{c}" stroke="#05031a" stroke-width="6" paint-order="stroke">?</text></g></g>')
    deb += "</g>"
    svg = f"""{deb}<g id="{p}-grade">{grade}</g><g filter="url(#{p}-glow)">{"".join(lit)}</g>"""
    html = (centro(f"{p}-ano", f'<span id="{p}-anoN">2006</span>', 40, 150, "#ffd98a") +
            centro(f"{p}-n", f'<span id="{p}-nN">1</span> pacientes', 4, 104) +
            centro(f"{p}-u", "um de cada quatro", 4, 108, "#ffd98a") +
            centro(f"{p}-src", "BODIEN E OUTROS · NEJM · 2024", 990, 40, "#ffb23e", "pill2"))
    C = "960,540"
    KA, KB, KC, KD, KE = "[960,560,1.0]", "[960,560,1.07]", "[960,574,1.7]", "[960,574,1.0]", "[960,574,1.03]"
    aneis = "".join(f'entra("#{p}-d{d}",{t_est - 0.1 + d * 0.11:.2f},0.25);' for d in sorted(cells))
    braco = lambda g, t0: braco_js(g, t0, -38, 0.3, 3)
    js = f"""
  focoIni("#{p}-cam",{KA},{C});
  foco("#{p}-cam",0,{t_est - 0.6:.2f},{KA},{KB},{C},"none");
  foco("#{p}-cam",{t_est - 0.28:.2f},0.02,{KB},{KC},{C},"none");
  foco("#{p}-cam",{t_est - 0.25:.2f},2.0,{KC},{KD},{C},"power3.out");
  foco("#{p}-cam",{t_est + 1.8:.2f},{dur - t_est - 1.8:.2f},{KD},{KE},{C},"none");
  pop("#{p}-q0",{t_cont:.2f},0.3); pop("#{p}-q1",{t_disc - 0.4:.2f},0.3); pop("#{p}-q2",{t_disc + 0.3:.2f},0.3);
  {braco(ga, t_cont)}{braco(gb, t_disc - 0.4)}
  rise("#{p}-ano > span",{t_dur - 0.3:.2f});
  contar("{p}-anoN",{t_dur:.2f},{max(0.8, t_2024 + 0.4 - t_dur):.2f},2006,2024);
  some("#{p}-deb",{t_est - 0.6:.2f},0.3);
  some("#{p}-ano",{t_est - 0.5:.2f},0.3);
  {aneis}
  rise("#{p}-n > span",{t_241 - 0.3:.2f});
  contar("{p}-nN",{t_241 - 0.2:.2f},1.4,1,241);
  some("#{p}-n",{t_um - 0.25:.2f},0.25);
  tl.fromTo("#{p}-cam .ac",{{opacity:0}},{{opacity:1,duration:0.25,stagger:{{amount:1.4}}}},{t_sin:.2f});
  rise("#{p}-u > span",{t_um:.2f},0.8);
  rise("#{p}-src > span",{t_sin + 0.6:.2f});
""" + vida_g(ga, t_est, (1.9, 4.4)) + vida_g(gb, t_est, (3.1,))
    return cena(p, dur, svg, html, js, extra=leito)


# ---------------------------------------------------------------- ler 6: na cadeira de rodas, a única porta era uma máquina
def cadeira_rodas():
    """Cadeira de rodas vista de frente, no sistema local de gente(..., "sentado") (pés em y=0, assento em y ~ -160, de frente):
    fundo (encosto, assento, suportes, atrás do corpo) e rodas (grandes, dos lados do quadril, na frente)."""
    est = 'fill="#2a1d70" stroke="#8d7bff" stroke-width="4"'
    fundo = (''.join(f'<rect x="{x - 7}" y="-372" width="14" height="230" rx="7" {est}/><rect x="{x - 13 if x < 0 else x - 1}" y="-380" width="14" height="22" rx="7" fill="#14122e" stroke="#8d7bff" stroke-width="3"/>' for x in (-104, 104))
             + f'<rect x="-98" y="-350" width="196" height="196" rx="18" {est}/>'
             + '<rect x="-82" y="-336" width="164" height="168" rx="12" fill="#3a2a8a" opacity=".6"/>'
             + f'<rect x="-112" y="-174" width="224" height="24" rx="10" {est}/>'
             + ''.join(f'<path d="M {x} -152 L {x * 0.86:.0f} -8" stroke="#8d7bff" stroke-width="7" stroke-linecap="round"/>' for x in (-70, 70))
             + ''.join(f'<rect x="{x}" y="-9" width="84" height="10" rx="5" fill="#8d7bff"/>' for x in (-104, 20))
             + ''.join(f'<circle cx="{x}" cy="-12" r="11" fill="#14122e" stroke="#b4bbe8" stroke-width="4"/>' for x in (-98, 98))
             + ''.join(f'<rect x="{min(x, x * 1.3):.0f}" y="-222" width="{abs(x) * 0.3:.0f}" height="12" rx="6" {est}/>' for x in (-104, 104)))

    def roda(x):
        raios = "".join(f'<line x1="{x}" y1="-104" x2="{x + 26 * math.cos(math.radians(a)):.1f}" y2="{-104 + 92 * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 45))
        return (f'<ellipse cx="{x}" cy="-104" rx="32" ry="104" fill="none" stroke="#b4bbe8" stroke-width="10"/>'
                f'<ellipse cx="{x}" cy="-104" rx="24" ry="88" fill="none" stroke="#8d7bff" stroke-width="3.5"/>'
                f'<g stroke="#b4bbe8" stroke-width="2.5" opacity=".8">{raios}</g><circle cx="{x}" cy="-104" r="8" fill="#b4bbe8"/>')
    return fundo, roda(-132) + roda(132)


def ler_6():
    p, sg = "ler_6", 6
    ini, dur = seg(CE, sg)
    t = T(sg)
    t_pes, t_uni, t_porta, t_fora, t_cab, t_maq = t("pessoas"), t("unica"), t("porta"), t("fora"), t("cabeca"), t("uma")
    gp = f"{p}-g"
    GX, GY, GS = 330, 840, 1.05
    fundo, roda = cadeira_rodas()
    mulher = f'<g transform="translate({GX} {GY}) scale({GS})"><g id="{gp}W">{fundo}{ela(gp, "sentado", glow=f"{p}-glow", cadeira=False)}{roda}</g></g>'
    anc = ANCORAS[("casa", "sentado", 30)]
    mao = (GX + anc["mao_d"][0] * GS, GY + anc["mao_d"][1] * GS)
    soro = (f'<g><rect x="96" y="836" width="80" height="10" rx="5" fill="#8d7bff"/><line x1="136" y1="330" x2="136" y2="840" stroke="#b4bbe8" stroke-width="7"/>'
            f'<path d="M 112 330 L 160 330" stroke="#b4bbe8" stroke-width="6" stroke-linecap="round"/>'
            f'<rect x="108" y="338" width="56" height="92" rx="14" fill="#cfefff" fill-opacity=".75" stroke="#fff" stroke-width="3"/><rect x="114" y="380" width="44" height="44" rx="10" fill="#9fdcff" opacity=".8"/>'
            f'</g>')
    tubo = (f'<path d="M 136 430 C 136 560 {mao[0] - 80:.0f} {mao[1] - 40:.0f} {mao[0] + 4:.0f} {mao[1] + 2:.0f}" fill="none" stroke="#e8f4ff" stroke-width="4" opacity=".85"/>'
             f'<rect x="{mao[0] - 6:.0f}" y="{mao[1] - 4:.0f}" width="18" height="10" rx="3" fill="#f4f6ff" opacity=".9"/>')
    # lembranças que saem da cabeça dela pela porta
    hc = (GX + anc["cabeca_centro"][0] * GS, GY + anc["cabeca_centro"][1] * GS)
    orbes = "".join(orbe(f"{p}-o{k}", s, hc[0] + dx, hc[1] + dy, c, 40) for k, (s, c, dx, dy) in
                    enumerate([("coracao", "#ff4fa3", 120, -95), ("nota", "#3be0ff", 195, -35), ("sol", "#ffb23e", 200, 50)]))
    svg = chao(p) + maquina(p) + porta_svg(p, 0) + soro + mulher + tubo + f'<g id="{p}-orbes">{orbes}</g>'
    html = (tx(f"{p}-t1", "A única porta", 1060, 70, 120) + tx(f"{p}-t2", "uma máquina", 1180, 880, 120, "#9af0ff"))
    C = "960,540"
    K0, K1, K2 = "[560,560,1.35]", "[560,560,1.42]", "[960,580,1.0]"
    alvo = (1560, 560)
    orb_js = ""
    for k, (dx, dy) in enumerate([(120, -95), (195, -35), (200, 50)]):
        sx, sy = hc[0] + dx, hc[1] + dy
        orb_js += (f'pop("#{p}-o{k}",{t_pes + 0.2 + k * 0.25:.2f},0.3,0.6);'
                   f'tl.fromTo("#{p}-o{k}",{{x:0,y:0}},{{x:{966 - sx:.0f},y:{600 - sy:.0f},duration:1.3,ease:"power2.inOut",immediateRender:false}},{t_fora + 0.1 + k * 0.22:.2f});'
                   f'tl.fromTo("#{p}-o{k}",{{x:{966 - sx:.0f},y:{600 - sy:.0f},scale:1}},{{x:{alvo[0] - sx:.0f},y:{alvo[1] - sy:.0f},scale:0.4,duration:0.9,ease:"power2.in",immediateRender:false}},{t_maq - 0.5 + k * 0.12:.2f});'
                   f'tl.fromTo("#{p}-o{k}",{{opacity:1}},{{opacity:0,duration:0.2,immediateRender:false}},{t_maq + 0.3 + k * 0.12:.2f});')
    js = f"""
  focoIni("#{p}-cam",{K0},{C});
  foco("#{p}-cam",0,{t_cab - 0.3:.2f},{K0},{K1},{C},"none");
  foco("#{p}-cam",{t_cab - 0.3:.2f},1.6,{K1},{K2},{C});
  tl.set("#{p}-maq",{{opacity:0}},0);
  pop("#{p}-porta",{t_porta - 0.2:.2f},0.3,0.8);
  rise("#{p}-t1 > span",{t_uni:.2f});
  olha("#{gp}-olho",{t_porta + 0.1:.2f},0,3);
  porta("#{p}-folha",{t_fora:.2f},1.1,1,0.7);
  entra("#{p}-luz",{t_fora:.2f},0.6); entra("#{p}-cunha",{t_fora + 0.2:.2f},0.8);
  opa("#{p}-maq",{t_cab - 0.2:.2f},0.8,0,0.45); opa("#{p}-maq",{t_maq:.2f},0.4,0.45,1);
  tl.fromTo("#{p}-anel",{{opacity:0.35}},{{opacity:1,duration:0.3,immediateRender:false}},{t_maq:.2f});
  tl.fromTo("#{p}-tun",{{opacity:0.25}},{{opacity:1,duration:0.4,immediateRender:false}},{t_maq:.2f});
  pulsa("#{p}-anel",{t_maq + 0.3:.2f},0.25,1.04,1);
  rise("#{p}-t2 > span",{t_maq:.2f});
""" + orb_js + vida_g(gp, dur, (1.2, 5.3), quadril=-170)
    return cena(p, dur, svg, html, js, trio_defs(p))


# ---------------------------------------------------------------- ler 8: Tang 2023, página real
def ler_8():
    p, sg = "ler_8", 8
    ini, dur = seg(CE, sg)
    t = T(sg)
    (t_sem, t_uni, t_tex, t_res, t_mod, t_lin, t_rec, t_ide, t_ouv, t_ima) = (
        t("sem"), t("universidade"), t("texas"), t("ressonancia"), t("modelo"), t("linguagem"), t("reconstruir"), t("ideia"), t("ouviam"), t("imaginavam"))
    W, H = 1600, 2071
    marcas = [("h0", 182, 189, 1140, 38), ("h1", 638, 408, 412, 34), ("h1b", 588, 461, 402, 34),
              ("h2", 184, 1054, 506, 40), ("h3", 826, 1162, 326, 40), ("h4", 1176, 946, 154, 40), ("h4b", 184, 1000, 431, 40),
              ("h5", 1010, 1108, 360, 40), ("h5b", 184, 1162, 84, 40)]
    svg = pagina(p, "tang2023", W, H, (740, 60, 1120, 960), marcas)
    C = "1300,540"
    K0, K1, K2, K3 = "[800,690,0.71]", "[760,526,0.92]", "[790,1040,0.88]", "[790,1110,0.88]"
    L = 80
    html = (tx(f"{p}-a1", "Sem", L, 190, 150) + tx(f"{p}-a2", "cirurgia", L, 370, 150, "#9af0ff") +
            tx(f"{p}-b1", "Universidade", L, 250, 104) + tx(f"{p}-b2", "do Texas", L, 390, 104, "#ffd98a") +
            tx(f"{p}-c1", "Ressonância", L, 200, 104) + tx(f"{p}-c2", "e um modelo de", L, 350, 80) + tx(f"{p}-c3", "linguagem", L, 460, 104, "#9af0ff") +
            tx(f"{p}-d1", "Reconstruir", L, 170, 104) + tx(f"{p}-d2", "a ideia geral", L, 310, 104, "#ffd98a") +
            tx(f"{p}-d3", "ouviam ou", L, 480, 92) + tx(f"{p}-d4", "imaginavam", L, 600, 104, "#9af0ff") +
            tx(f"{p}-src1", "BIORXIV · PREPRINT", L, 860, 42, "#ffb23e", "pill2") + tx(f"{p}-src2", "2022", L, 924, 42, "#ffb23e", "pill2"))
    js = f"""
  tl.fromTo("#{p}-pgW",{{y:1000,rotation:6,transformOrigin:"50% 50%"}},{{y:0,rotation:0,transformOrigin:"50% 50%",duration:1.0,ease:"expo.out"}},0.05);
  focoIni("#{p}-pg",{K0},{C});
  rise("#{p}-a1 > span",{t_sem:.2f}); rise("#{p}-a2 > span",{t_sem + 0.3:.2f});
  rise("#{p}-src1 > span",0.9); rise("#{p}-src2 > span",1.05);
  foco("#{p}-pg",{t_sem + 0.6:.2f},1.2,{K0},{K1},{C});
  marca("#{p}-h0",{t_sem + 1.0:.2f},0.7);
  some("#{p}-a1",{t_uni - 0.3:.2f},0.3); some("#{p}-a2",{t_uni - 0.3:.2f},0.3);
  rise("#{p}-b1 > span",{t_uni:.2f}); rise("#{p}-b2 > span",{t_tex - 0.2:.2f});
  marca("#{p}-h1",{t_uni + 0.1:.2f},0.5); marca("#{p}-h1b",{t_uni + 0.45:.2f},0.5);
  some("#{p}-b1",{t_res - 0.3:.2f},0.3); some("#{p}-b2",{t_res - 0.3:.2f},0.3);
  foco("#{p}-pg",{t_res - 0.3:.2f},1.2,{K1},{K2},{C});
  foco("#{p}-pg",{t_res + 0.9:.2f},{dur - t_res - 0.9:.2f},{K2},{K3},{C},"none");
  rise("#{p}-c1 > span",{t_res:.2f}); marca("#{p}-h2",{t_res + 0.5:.2f},0.6);
  rise("#{p}-c2 > span",{t_mod - 0.2:.2f}); rise("#{p}-c3 > span",{t_lin:.2f}); marca("#{p}-h3",{t_mod + 0.2:.2f},0.5);
  some("#{p}-c1",{t_rec - 0.3:.2f},0.3); some("#{p}-c2",{t_rec - 0.3:.2f},0.3); some("#{p}-c3",{t_rec - 0.3:.2f},0.3);
  rise("#{p}-d1 > span",{t_rec:.2f}); marca("#{p}-h4",{t_rec + 0.1:.2f},0.4); marca("#{p}-h4b",{t_rec + 0.45:.2f},0.6);
  rise("#{p}-d2 > span",{t_ide:.2f});
  rise("#{p}-d3 > span",{t_ouv:.2f}); rise("#{p}-d4 > span",{t_ima:.2f});
  marca("#{p}-h5",{t_ouv:.2f},0.5); marca("#{p}-h5b",{t_ima:.2f},0.3);
"""
    return cena(p, dur, svg, html, js)


# ---------------------------------------------------------------- ler 9: o voluntário deitado na ressonância, 16 horas de treino, e o sistema falha
def _bez(a, b, c, d, n):
    out = []
    for k in range(n + 1):
        u = k / n
        out.append(tuple(round((1 - u) ** 3 * a[i] + 3 * (1 - u) ** 2 * u * b[i] + 3 * (1 - u) * u ** 2 * c[i] + u ** 3 * d[i]) for i in (0, 1)))
    return out


def ler_9():
    p, sg = "ler_9", 9
    ini, dur = seg(CE, sg)
    t = T(sg)
    t_nao, t_pal, t_por, t_cada, t_trei, t_16, t_hor, t_res, t_out, t_sis2, t_fal = (
        t("nao"), t("palavra"), t("palavra", 1), t("cada"), t("treinou"), t("16"), t("horas"), t("resistia"), t("outra"), t("sistema", 1), t("falhava"))
    gp = f"{p}-g"
    extra = trio_defs(p) + quarto_defs(p)
    vol = na_cabeca(tinge(gente(gp, "casa", "em_pe", glow=f"{p}-glow", sombra=False), VOLUNT), gp, fones())
    TX, TY, S = 1170, 650, 0.7
    mesa_extra = ('<rect x="1050" y="640" width="130" height="34" rx="12" fill="#dfe4ff" stroke="#8d7bff" stroke-width="3"/>'
                  '<rect x="1070" y="674" width="22" height="166" fill="#2a2a6a"/>')
    # monitor de controle na mesa, à esquerda
    chips1 = "".join(f'<rect id="{p}-w{k}" x="{x}" y="392" width="{w}" height="26" rx="8" fill="#9af0ff" opacity="0"/>'
                     for k, (x, w) in enumerate([(236, 44), (290, 30), (330, 58), (398, 36), (444, 50), (504, 28), (542, 46), (598, 26)]))
    chips2 = "".join(f'<rect id="{p}-i{k}" x="{x}" y="456" width="{w}" height="40" rx="12" fill="#ffd27a" opacity="0"/>' for k, (x, w) in enumerate([(236, 150), (398, 110), (520, 104)]))
    monitor = f"""<ellipse cx="430" cy="846" rx="320" ry="18" fill="#05031a" opacity=".55"/>
<rect x="160" y="690" width="560" height="22" rx="8" fill="#3a3a8a" stroke="#8d7bff" stroke-width="3"/><rect x="186" y="712" width="20" height="128" fill="#2a2a6a"/><rect x="674" y="712" width="20" height="128" fill="#2a2a6a"/>
<rect x="410" y="640" width="40" height="52" fill="#2a2a6a"/><rect x="360" y="682" width="140" height="12" rx="6" fill="#2a2a6a"/>
<g filter="url(#{p}-sombra)"><rect x="200" y="330" width="460" height="316" rx="22" fill="#14122e" stroke="#8d7bff" stroke-width="7"/></g>
<rect x="222" y="352" width="416" height="272" rx="10" fill="url(#{p}-tela)"/>
{chips1}{chips2}<rect x="236" y="548" width="388" height="22" rx="11" fill="#2a2a6a"/><rect id="{p}-barra" x="236" y="548" width="388" height="22" rx="11" fill="#38e8a8"/>
<rect id="{p}-telaV" x="222" y="352" width="416" height="272" rx="10" fill="#ff4f7d" opacity="0"/>"""
    cabo_pts = _bez((1300, 800), (1100, 838), (820, 838), (700, 760), 12)
    cabo = f'<path d="M1300 800 C 1100 838 820 838 700 760" fill="none" stroke="#5a5ad0" stroke-width="9" stroke-linecap="round"/>'
    pacotes = "".join(f'<circle id="{p}-pk{k}" cx="0" cy="0" r="10" fill="#3be0ff" opacity="0" filter="url(#{p}-glow)"/>' for k in range(3))
    relogio = f"""<g transform="translate(930 200) scale(.85)"><g id="{p}-rel"><circle r="96" fill="#eef1ff" stroke="#8d7bff" stroke-width="10"/><circle r="84" fill="#14122e"/>
<g fill="#8d7bff"><rect x="-4" y="-78" width="8" height="16"/><rect x="-4" y="62" width="8" height="16"/><rect x="62" y="-4" width="16" height="8"/><rect x="-78" y="-4" width="16" height="8"/></g>
<g id="{p}-pont"><line x1="0" y1="0" x2="0" y2="-64" stroke="#eef1f7" stroke-width="8" stroke-linecap="round"/></g><g id="{p}-pont2"><line x1="0" y1="0" x2="40" y2="0" stroke="#ffb23e" stroke-width="11" stroke-linecap="round"/></g><circle r="9" fill="#ffb23e"/></g></g>"""
    bal = (f'<g id="{p}-bal" opacity="0"><circle cx="1500" cy="575" r="10" fill="#2a1d70" stroke="#ff4fa3" stroke-width="4"/><circle cx="1462" cy="510" r="15" fill="#2a1d70" stroke="#ff4fa3" stroke-width="4"/><circle cx="1405" cy="430" r="22" fill="#2a1d70" stroke="#ff4fa3" stroke-width="4"/>'
           f'<ellipse cx="1200" cy="250" rx="180" ry="130" fill="#2a1d70" stroke="#ff4fa3" stroke-width="6" filter="url(#{p}-glow)"/>'
           + quadro(f"{p}-praia", "praia", 1200, 250, 0.82) + '</g>')
    svg = (chao(p) + monitor + cabo + maquina(p) + mesa_extra + deitada(vol, TX, TY, S) + pacotes + relogio + bal)
    html = (centro(f"{p}-t1", "Não era palavra por palavra", 50, 104) +
            tx(f"{p}-h", f'<span id="{p}-hN">0</span> horas', 1070, 130, 100, "#ffd98a") +
            centro(f"{p}-t2", "o sistema falhava", 880, 120, "#ff4f7d"))
    C = "960,540"
    K0, K1, K2, K3 = "[430,500,1.6]", "[430,500,1.66]", "[960,560,1.0]", "[1000,560,1.05]"
    w_js = "".join(f'tl.fromTo("#{p}-w{k}",{{opacity:0}},{{opacity:1,duration:0.12}},{t_pal + k * 0.14:.2f});' for k in range(8))
    i_js = "".join(f'pop("#{p}-i{k}",{t_por + k * 0.18:.2f},0.4,0.5);' for k in range(3))
    pk_js = ""
    xs, ys = [x for x, _ in cabo_pts], [y for _, y in cabo_pts]
    for j, t0 in enumerate([t_trei + 0.2 + k * 0.45 for k in range(int((t_res - 0.6 - t_trei) / 0.45))]):
        k = j % 3
        pk_js += (f'tl.set("#{p}-pk{k}",{{x:{xs[0]},y:{ys[0]},opacity:1}},{t0:.2f});'
                  f'tl.to("#{p}-pk{k}",{{keyframes:{{x:{xs},y:{ys}}},duration:1.2,ease:"none",immediateRender:false}},{t0:.2f});'
                  f'tl.set("#{p}-pk{k}",{{opacity:0}},{t0 + 1.2:.2f});')
    js = f"""
  focoIni("#{p}-cam",{K0},{C});
  foco("#{p}-cam",0,{t_cada - 0.3:.2f},{K0},{K1},{C},"none");
  foco("#{p}-cam",{t_cada - 0.3:.2f},1.4,{K1},{K2},{C});
  foco("#{p}-cam",{t_fal - 0.4:.2f},{dur - t_fal + 0.4:.2f},{K2},{K3},{C},"power2.inOut");
  tl.set("#{p}-tun",{{opacity:1}},0); tl.set("#{p}-anel",{{opacity:1}},0);
  rise("#{p}-t1 > span",{t_nao:.2f});
  some("#{p}-t1",{t_cada - 0.2:.2f},0.3);
  {w_js}{i_js}
  pop("#{p}-rel",{t_trei - 0.2:.2f},0.3,0.7);
  tl.fromTo("#{p}-pont",{{rotation:0,transformOrigin:"50% 100%"}},{{rotation:5760,transformOrigin:"50% 100%",duration:{t_hor + 0.4 - t_trei:.2f},ease:"power1.inOut"}},{t_trei:.2f});
  tl.fromTo("#{p}-pont2",{{rotation:0,transformOrigin:"0% 50%"}},{{rotation:480,transformOrigin:"0% 50%",duration:{t_hor + 0.4 - t_trei:.2f},ease:"power1.inOut"}},{t_trei:.2f});
  tl.fromTo("#{p}-barra",{{scaleX:0.02,transformOrigin:"0% 50%"}},{{scaleX:1,transformOrigin:"0% 50%",duration:{t_hor + 0.4 - t_trei:.2f},ease:"power1.inOut"}},{t_trei:.2f});
  rise("#{p}-h > span",{t_trei:.2f});
  contar("{p}-hN",{t_trei + 0.1:.2f},{t_hor + 0.3 - t_trei:.2f},0,16);
  pulsa("#{p}-anel",{t_16:.2f},0.2,1.05,3);
  some("#{p}-rel",{t_res - 0.6:.2f},0.3); some("#{p}-h",{t_res - 0.6:.2f},0.3);
  pop("#{p}-bal",{t_out - 0.6:.2f},0.3,0.7);
  some("#{p}-tun",{t_sis2:.2f},0.2); some("#{p}-anel",{t_sis2:.2f},0.2);
  tl.fromTo("#{p}-tunV",{{opacity:0}},{{opacity:1,duration:0.08,repeat:9,yoyo:true,ease:"steps(1)",immediateRender:false}},{t_sis2:.2f});
  tl.fromTo("#{p}-anelV",{{opacity:0}},{{opacity:1,duration:0.15,immediateRender:false}},{t_sis2:.2f});
  tl.fromTo("#{p}-telaV",{{opacity:0}},{{opacity:0.55,duration:0.08,repeat:5,yoyo:true,ease:"steps(1)",immediateRender:false}},{t_fal - 0.2:.2f});
  tl.fromTo("#{p}-telaV",{{opacity:0}},{{opacity:0.5,duration:0.2,immediateRender:false}},{t_fal + 0.3:.2f});
  tl.fromTo("#{p}-barra",{{fill:"#38e8a8"}},{{fill:"#ff4f7d",duration:0.2,immediateRender:false}},{t_fal - 0.2:.2f});
  tl.fromTo("#{p}-maq",{{x:0}},{{x:6,duration:0.05,repeat:9,yoyo:true,ease:"none",immediateRender:false}},{t_fal:.2f});
  rise("#{p}-t2 > span",{t_fal:.2f});
""" + "".join(f'tl.fromTo("#{p}-i{k}",{{x:0}},{{x:{(-1) ** k * 14},duration:0.06,repeat:7,yoyo:true,ease:"none",immediateRender:false}},{t_fal:.2f});' for k in range(3)) + pk_js + vida_g(gp, dur, (2.9, 6.8, t_out))
    return cena(p, dur, svg, html, js, extra)


# ---------------------------------------------------------------- ler 10: em casa, a máquina bate à porta e precisa da sua cooperação
def ler_10():
    p, sg = "ler_10", 10
    ini, dur = seg(CE, sg)
    t = T(sg)
    t_hoje, t_ler, t_mente, t_maq, t_prec, t_sua, t_coop = t("hoje"), t("ler"), t("mente"), t("maquina"), t("precisa"), t("sua", 1), t("cooperacao")
    gp = f"{p}-g"
    GX, GS, PASSO = 690, 0.72, 100                 # pessoa anda até a porta (braço girado leva a mão à maçaneta em x ~ 896)
    extra = trio_defs(p) + f"""<linearGradient id="{p}-par" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a2d7a"/><stop offset="1" stop-color="#241a5a"/></linearGradient>"""
    parede = (f'<rect x="-400" y="-300" width="1500" height="1140" fill="url(#{p}-par)"/>'
              f'<rect x="-400" y="800" width="1500" height="40" fill="#1c1450"/>'
              f'<rect x="1084" y="-300" width="16" height="1140" fill="#4a3a9a"/><line x1="1100" y1="-300" x2="1100" y2="840" stroke="#8d7bff" stroke-width="4" opacity=".6"/>'
              + quadro(f"{p}-qa", "familia", 220, 380, 0.85) + quadro(f"{p}-qb", "aniversario", 500, 340, 0.72) + quadro(f"{p}-qc", "cachorro", 470, 560, 0.62))
    toques = "".join(f'<circle id="{p}-k{k}" cx="1100" cy="600" r="20" fill="none" stroke="#ffb23e" stroke-width="7" opacity="0"/>' for k in range(3))
    # máquina menor e mais ao fundo, do lado de fora da casa (no ler_9 ela ocupa a direita inteira, em tamanho cheio)
    MS_, MTX, MTY = 0.7, 520, 838 - 846 * 0.7
    tun = (MTX + 1560 * MS_, MTY + 560 * MS_)
    maq = f'<g transform="translate({MTX} {MTY:.1f}) scale({MS_})">{maquina(p)}</g>'
    feixe = f'<path id="{p}-fx" d="M{tun[0] - 135:.0f} {tun[1] - 30:.0f} L1090 {tun[1] - 30:.0f}" fill="none" stroke="#3be0ff" stroke-width="10" stroke-linecap="round" stroke-dasharray="40 26" opacity="0" filter="url(#{p}-glow)"/>'
    pessoa_ = f'<g transform="translate({GX} 840) scale({GS})"><g id="{gp}W">{gente(gp, "casa", "em_pe", glow=f"{p}-glow")}</g></g>'
    pos = [("coracao", "#ff4fa3", 610, 292), ("bolo", "#ffb23e", 740, 268), ("carro", "#3be0ff", 870, 300)]
    orbes = "".join(orbe(f"{p}-o{k}", s, x, y, c, 40) for k, (s, c, x, y) in enumerate(pos))
    svg = chao(p) + parede + maq + porta_svg(p, 0) + toques + feixe + pessoa_ + orbes
    html = (tx(f"{p}-t1", "Hoje,", 250, 34, 110) + tx(f"{p}-t2", "a máquina precisa", 545, 34, 110) +
            centro(f"{p}-t3", "da sua cooperação", 905, 112, "#ffd98a"))
    C = "960,540"
    tq = "".join(f'tl.fromTo("#{p}-k{k}",{{attr:{{r:20}},opacity:1}},{{attr:{{r:80}},opacity:0,duration:0.45,ease:"power2.out",immediateRender:false}},{t_prec + k * 0.3:.2f});' for k in range(3))
    orb_js = ""
    for k, (_, _, x, y) in enumerate(pos):
        orb_js += (f'pop("#{p}-o{k}",{t_mente - 0.3 + k * 0.2:.2f},0.3,0.6);'
                   f'tl.fromTo("#{p}-o{k}",{{y:0}},{{y:-10,duration:0.7,repeat:1,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_mente + 0.4 + k * 0.2:.2f});'
                   f'tl.fromTo("#{p}-o{k}",{{x:0,y:0,scale:1}},{{x:{tun[0] - x:.0f},y:{tun[1] - y:.0f},scale:0.45,duration:1.1,ease:"power2.inOut",immediateRender:false}},{t_coop + 0.7 + k * 0.18:.2f});'
                   f'tl.fromTo("#{p}-o{k}",{{opacity:1}},{{opacity:0,duration:0.2,immediateRender:false}},{t_coop + 1.65 + k * 0.18:.2f});')
    js = f"""
  focoIni("#{p}-cam",[960,560,1.0],{C});
  foco("#{p}-cam",0,{t_coop:.2f},[960,560,1.0],[930,560,1.06],{C},"none");
  foco("#{p}-cam",{t_coop:.2f},1.4,[930,560,1.06],[1000,560,1.0],{C});
  tl.set("#{p}-tun",{{opacity:1}},0); tl.set("#{p}-anel",{{opacity:1}},0);
  rise("#{p}-t1 > span",{t_hoje:.2f});
  entra("#{p}-fx",{t_ler:.2f},0.3);
  tl.fromTo("#{p}-fx",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-132}},duration:0.6,repeat:4,ease:"none"}},{t_ler:.2f});
  pulsa("#{p}-anel",{t_ler:.2f},0.25,1.04,3);
  rise("#{p}-t2 > span",{t_maq:.2f});
  {tq}
  tl.fromTo("#{p}-porta",{{x:0}},{{x:5,duration:0.05,repeat:5,yoyo:true,ease:"none",immediateRender:false}},{t_prec:.2f});
  olha("#{gp}-olho",{t_prec + 0.2:.2f},0,3);
  rise("#{p}-t3 > span",{t_sua:.2f},0.8);
  some("#{p}-fx",{t_coop:.2f},0.3);
  tl.fromTo("#{gp}W",{{x:0}},{{x:{PASSO / GS:.0f},duration:0.7,ease:"power2.inOut",immediateRender:false}},{t_coop - 0.55:.2f});
  tl.fromTo("#{gp}W",{{y:0}},{{y:-10,duration:0.175,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false}},{t_coop - 0.55:.2f});
  {braco_js(gp, t_coop + 0.1, -35, 0.4, variante="casa")}
  porta("#{p}-folha",{t_coop + 0.4:.2f},1.0,1,0.16,"power3.out");
  entra("#{p}-luz",{t_coop + 0.4:.2f},0.5); entra("#{p}-cunha",{t_coop + 0.55:.2f},0.6);
""" + orb_js + vida_g(gp, dur, (1.4, 4.9))
    return cena(p, dur, svg, html, js, extra)


# ---------------------------------------------------------------- ler 11: "Hoje." (o rosto da pessoa de perto, na luz da porta)
def ler_11():
    p, sg = "ler_11", 11
    ini, dur = seg(CE, sg)
    S = 3.3
    hp = f"{p}-h"
    extra = f"""<linearGradient id="{p}-luzR" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff2b8" stop-opacity="0"/><stop offset="1" stop-color="#fff2b8" stop-opacity=".85"/></linearGradient>"""
    ombro = (f'<path d="M 860 1100 C 870 960 960 900 1120 890 C 1300 880 1420 930 1470 1100 Z" fill="{CASA["torso"]}"/>'
             f'<path d="M 860 1100 C 870 960 960 900 1060 892 C 1010 960 1000 1030 1000 1100 Z" fill="{CASA["torso2"]}" opacity=".55"/>')
    pescoco = (f'<rect x="1078" y="720" width="132" height="230" rx="40" fill="{PELE}"/>'
               f'<path d="M 1078 800 Q 1144 850 1210 800 L 1210 860 L 1078 860 Z" fill="#140a2e" opacity=".28"/>')
    svg = (f'<rect id="{p}-luz" x="1500" y="-100" width="900" height="1300" fill="url(#{p}-luzR)" opacity=".8"/>' + pescoco + ombro +
           f'<g transform="translate({1240 - 205 * S:.0f} {140 - 28 * S:.0f}) scale({S})"><g id="{p}-cabB">{cabeca(hp, CASA)}</g></g>')
    html = tx(f"{p}-t1", "Hoje", 100, 360, 250, "#ffd98a")
    C = "960,540"
    js = f"""
  focoIni("#{p}-cam",[1100,560,1.0],{C});
  foco("#{p}-cam",0,{dur:.2f},[1100,560,1.0],[1120,560,1.06],{C},"none");
  rise("#{p}-t1 > span",0.08,0.7);
  tl.fromTo("#{hp}-olho",{{x:0}},{{x:3,duration:0.3,ease:"power2.inOut"}},0.3);
  tl.fromTo("#{hp}-olho",{{scaleY:1,transformOrigin:"50% 50%"}},{{scaleY:0.08,transformOrigin:"50% 50%",duration:0.08,repeat:1,yoyo:true,immediateRender:false}},0.8);
  tl.fromTo("#{p}-luz",{{opacity:0.8}},{{opacity:0.45,duration:0.07,repeat:5,yoyo:true,ease:"steps(1)",immediateRender:false}},0.5);
"""
    out = cena(p, dur, svg, html, js, extra)
    # cena de 1,27 s: o fade de entrada padrão (0,4 s) comeria um terço; aqui ele é curto
    return out.replace(f'tl.fromTo("#{p}-preto", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.4', f'tl.fromTo("#{p}-preto", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.12')


SEGS = [(0, ler_0), (1, ler_1), (3, ler_3), (4, ler_4), (5, ler_5), (6, ler_6), (8, ler_8), (9, ler_9), (10, ler_10), (11, ler_11)]
CENAS = [(f"ler_{i}", fn, seg(CE, i)[1]) for i, fn in SEGS]
MAPA = {(CE, i): f"ler_{i}" for i, _ in SEGS}

if __name__ == "__main__":
    print(escreve_cenas(CENAS, AQUI_G))
