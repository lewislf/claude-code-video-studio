"""A pessoa de verdade (personagem geométrico aprovado, teste_gente3/geometrico), quadros de memória e orbes de lembrança.

A arte vem de gente_svg.json, gerado por gente_gerar.py a partir do esboço em canvas (não editar o JSON à mão).
Duas variantes da MESMA pessoa: "casa" (moletom, jeans) e "trabalho" (camisa, gravata, crachá). Poses "sentado" e "em_pe".
giro: 0 = de frente; >= 15 usa a versão virada ~30 graus para a direita (padrão 25, como o personagem antigo de perfil).

    from gente import *
    svg = gente("X-g", "casa", "sentado")          # caixa local ~ x -150..190, topo da cabeça de pé y ~ -540, pés em y=0
    js += vida_gente("X-g", dur)                   # respira, pisca, balança a cabeça

Ids: {p} (raiz), {p}-corpo, {p}-pernas, {p}-tor (tronco), {p}-torso (path do tronco), {p}-bracoE, {p}-braco (braço do lado
direito da tela, pivô no ombro: data-pivo e ANCORAS[...]["ombro_braco"]), {p}-cabW > {p}-cab > {p}-olho (os dois olhos).
{p}-cabW leva transform="translate(0 0)" (identidade): os builds g3/g5/g7 procuram esse atributo para aninhar o grupo, e
como é identidade o GSAP pode sobrescrever sem deslocar a cabeça (GOTCHAS 1).
Troca de cor: cada peça usa um hex base (PELE, CABELO, CASA/TRAB torso, calca, sapato); sombra e luz são camadas neutras
com opacidade por cima, então .replace(hex_base, novo) recolore a peça inteira.
"""
import json
import os
import re

_D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gente_svg.json"), encoding="utf-8"))

PELE, PELE_E = "#e0a17a", "#b26e66"      # PELE_E não aparece no SVG (sombra virou camada neutra); fica por compatibilidade
CABELO = "#5b3523"
# torso2: tom de sombra do torso, informativo (não aparece literal no SVG). sola: hex próprio da sola.
CASA = dict(torso="#7b55d8", torso2="#5437a6", calca="#3f61aa", sapato="#e6e0f8", sola="#fbf9ff", cab="casa")
TRAB = dict(torso="#cdd4ec", torso2="#959bc8", calca="#3a3558", sapato="#4a3036", sola="#1c1015", cab="trabalho")
GRAVATA = "#a3305f"
RIM = {"casa": "#ff4fa3", "trabalho": "#5ee6ff"}

ANCORAS = {}
for _k, _v in _D.items():
    _var, _pose, _g = _k.split("|")
    ANCORAS[(_var, _pose, int(_g))] = {n: (tuple(p) if p else None) for n, p in _v["anc"].items()}


def _chave(variante, pose, giro):
    return ("casa" if variante == "casa" else "trabalho", "em_pe" if pose == "em_pe" else "sentado", 30 if giro >= 15 else 0)


def _filtro(p, cor):
    """Brilho neon na borda direita da silhueta (o mesmo do esboço: silhueta menos ela deslocada, borrada)."""
    return (f'<filter id="{p}-rim" x="-30%" y="-15%" width="160%" height="130%" color-interpolation-filters="sRGB">'
            f'<feOffset in="SourceAlpha" dx="-3.7" dy="0" result="d"/><feComposite in="SourceAlpha" in2="d" operator="out" result="b"/>'
            f'<feFlood flood-color="{cor}" flood-opacity=".9"/><feComposite in2="b" operator="in"/><feGaussianBlur stdDeviation="5.2" result="g"/>'
            f'<feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


def gente(p, variante="casa", pose="sentado", glow=None, cadeira=True, sombra=True, giro=25):
    k = _chave(variante, pose, giro)
    d = _D["|".join(map(str, k))]
    frag = d["svg"]
    if not cadeira:
        frag = re.sub(r"<!--cad-->.*?<!--/cad-->", "", frag, flags=re.S)
    frag = frag.replace("@P@", p)
    ob = ANCORAS[k]["ombro_braco"]
    # data-pivo antes do id e um path-guia invisível com stroke: o humano(cel=True) do g5 lê a cor do braço por regex e não
    # pode casar o '<g id="{p}-braco">...</g>' não guloso (o braço novo tem grupos aninhados e a troca quebraria o SVG)
    cor_b = (CASA if k[0] == "casa" else TRAB)["torso"]
    frag = frag.replace(f'<g id="{p}-braco">', f'<g data-pivo="{ob[0]} {ob[1]}" id="{p}-braco"><path d="M0 0" stroke="{cor_b}" fill="none" stroke-opacity="0"/>', 1)
    defs = d["defs"].replace("@P@", p) + _filtro(p, RIM[k[0]])
    rx = 125 if k[1] == "sentado" else 88
    sombra_svg = f'<ellipse cx="0" cy="0" rx="{rx}" ry="12" fill="#06021a" opacity=".55"/>' if sombra else ""
    return f'<g id="{p}"><defs>{defs}</defs>{sombra_svg}<g id="{p}-corpo" filter="url(#{p}-rim)">{frag}</g></g>'


def cabeca(p, v):
    """Só a cabeça nova (de pé, virada para a direita), encaixada na caixa local da cabeça antiga (x 110..300, y 28..252).
    Ids: {p}-cab e {p}-olho."""
    var = "casa" if v.get("cab", "casa") == "casa" else "trabalho"
    d = _D[f"{var}|em_pe|30"]
    s = d["svg"]
    i = s.index('<g id="@P@-cab">')
    prof, j = 0, i
    for m in re.finditer(r"<g\b|</g>", s[i:]):
        prof += 1 if m.group(0) != "</g>" else -1
        if prof == 0:
            j = i + m.end()
            break
    cab = s[i:j].replace("@P@", p)
    usados = set(re.findall(r"url\(#@P@-(k\d+)\)", s[i:j]))
    defs = "".join(m.group(0) for m in re.finditer(r'<clipPath id="@P@-(k\d+)".*?</clipPath>', d["defs"]) if m.group(1) in usados)
    cx, cy = d["anc"]["cabeca_centro"]
    esc = 2.2
    return (f'<g transform="translate(205 150) scale({esc}) translate({-cx} {-cy})"><defs>{defs.replace("@P@", p)}</defs>{cab}</g>')


def membro(a, b, larg, cor):
    return f'<path d="M {a[0]} {a[1]} L {b[0]} {b[1]}" stroke="{cor}" stroke-width="{larg}" stroke-linecap="round" fill="none"/>'


def vida_gente(p, dur, piscadas=(2.0, 5.3, 8.8, 12.1, 16.4, 20.2)):
    """JS: respiração no tronco, balanço de cabeça e piscadas, determinísticos."""
    # svgOrigin nos pés: os recortes M-9999 do desenho deixam o getBBox gigante e "50% 100%" jogava o tronco ~120 px para cima
    js = (f'tl.fromTo("#{p}-tor",{{scaleY:1,svgOrigin:"0 0"}},{{scaleY:1.006,svgOrigin:"0 0",duration:1.7,repeat:{max(1, int(dur / 1.7))},yoyo:true,ease:"sine.inOut"}},0);')
    js += (f'tl.fromTo("#{p}-cabW",{{y:0}},{{y:-3,duration:1.7,repeat:{max(1, int(dur / 1.7))},yoyo:true,ease:"sine.inOut"}},0.2);')
    for t in piscadas:
        if t < dur - 0.3:
            js += f'tl.fromTo("#{p}-olho",{{scaleY:1,transformOrigin:"50% 50%"}},{{scaleY:0.08,transformOrigin:"50% 50%",duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t});'
    return js


# ---------------------------------------------------------------- quadros e lembranças
def _fig(x, y, s, cor, camisa):
    return (f'<g transform="translate({x} {y}) scale({s})"><circle cx="0" cy="-34" r="14" fill="{cor}"/><path d="M -16 0 C -18 -16 -10 -24 0 -24 C 10 -24 18 -16 16 0 Z" fill="{camisa}"/>'
            f'<path d="M -6 -33 Q 0 -28 6 -33" stroke="#7a3a2a" stroke-width="2.4" fill="none" stroke-linecap="round"/></g>')


def cena_quadro(tipo):
    """Mini-ilustração (caixa 200x150) de um momento da vida."""
    if tipo == "familia":
        return ('<rect width="200" height="150" fill="#ffd9a8"/><circle cx="160" cy="30" r="16" fill="#fff3b0"/><rect y="110" width="200" height="40" fill="#8bd18b"/>'
                + _fig(60, 118, 1.5, PELE, "#ff7a8a") + _fig(105, 120, 1.7, PELE, "#6a8cff") + _fig(145, 122, 1.2, PELE, "#ffd23e")
                + '<path d="M 60 84 q 10 -10 20 0" stroke="#fff" stroke-width="3" fill="none"/>')
    if tipo == "aniversario":
        return ('<rect width="200" height="150" fill="#ffd1ec"/><rect x="40" y="86" width="120" height="40" rx="8" fill="#fff"/><rect x="40" y="86" width="120" height="14" rx="6" fill="#ff7ab8"/>'
                + "".join(f'<rect x="{62 + k * 24}" y="62" width="6" height="26" fill="#6a8cff"/><path d="M {65 + k * 24} 50 q 6 8 0 14 q -6 -6 0 -14" fill="#ffb23e"/>' for k in range(4))
                + '<path d="M 10 20 L 190 20" stroke="#ff4fa3" stroke-width="3"/>' + "".join(f'<path d="M {20 + k * 30} 20 l 8 18 l 8 -18 z" fill="{["#ffd23e", "#38e8a8", "#8d7bff", "#ff4f7d", "#3be0ff", "#ffb23e"][k]}"/>' for k in range(6)))
    if tipo == "carro":
        return ('<rect width="200" height="150" fill="#bfe6ff"/><rect y="104" width="200" height="46" fill="#7f8aa0"/><path d="M 30 104 L 44 78 L 118 78 L 142 98 L 176 102 L 176 118 L 30 118 Z" fill="#ff4f7d"/>'
                '<path d="M 52 80 L 114 80 L 134 98 L 50 98 Z" fill="#cfeaff"/><circle cx="64" cy="118" r="15" fill="#1a1030"/><circle cx="148" cy="118" r="15" fill="#1a1030"/><circle cx="64" cy="118" r="6" fill="#bbb"/><circle cx="148" cy="118" r="6" fill="#bbb"/>'
                '<path d="M 20 40 q 10 -10 22 0 M 150 30 q 12 -10 24 0" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round"/><g transform="translate(176 70)"><path d="M 0 0 l 22 8" stroke="#ffd23e" stroke-width="5"/><circle cx="-4" cy="-2" r="8" fill="none" stroke="#ffd23e" stroke-width="4"/></g>')
    if tipo == "formatura":
        return ('<rect width="200" height="150" fill="#d8c8ff"/>' + _fig(100, 130, 2.6, PELE, "#232344") + '<path d="M 60 40 L 100 22 L 140 40 L 100 58 Z" fill="#14122a"/><path d="M 80 48 L 80 62 Q 100 70 120 62 L 120 48" fill="#14122a"/><path d="M 140 40 L 146 70" stroke="#ffd23e" stroke-width="3"/>')
    if tipo == "praia":
        return ('<rect width="200" height="150" fill="#9fe0ff"/><circle cx="150" cy="34" r="18" fill="#ffe27a"/><rect y="90" width="200" height="60" fill="#ffe2a8"/><path d="M 0 88 q 20 -12 40 0 t 40 0 t 40 0 t 40 0 t 40 0 V 100 H 0 Z" fill="#3b9fe8"/>' + _fig(70, 140, 1.6, PELE, "#ff7a8a") + _fig(110, 142, 1.4, PELE, "#38e8a8"))
    if tipo == "cachorro":
        return ('<rect width="200" height="150" fill="#ffe9b8"/><ellipse cx="100" cy="104" rx="40" ry="26" fill="#c98d48"/><circle cx="142" cy="84" r="22" fill="#c98d48"/><path d="M 130 68 q -14 -8 -10 18 z M 156 66 q 14 -4 8 20 z" fill="#8a5a28"/><circle cx="148" cy="84" r="3" fill="#1a1030"/><ellipse cx="160" cy="92" rx="7" ry="5" fill="#1a1030"/><path d="M 62 96 q -24 -10 -20 -30" stroke="#c98d48" stroke-width="10" fill="none" stroke-linecap="round"/>')
    if tipo == "premio":
        return ('<rect width="200" height="150" fill="#2a2a6a"/><path d="M 70 40 H 130 V 70 Q 130 100 100 104 Q 70 100 70 70 Z" fill="#ffd23e"/><path d="M 70 48 H 54 Q 54 80 74 84 M 130 48 H 146 Q 146 80 126 84" stroke="#ffd23e" stroke-width="6" fill="none"/><rect x="92" y="104" width="16" height="22" fill="#e6b32e"/><rect x="72" y="124" width="56" height="14" rx="4" fill="#8a6a3a"/>')
    if tipo == "reuniao":
        return ('<rect width="200" height="150" fill="#cfd8ee"/><rect x="20" y="86" width="160" height="14" rx="5" fill="#6a5a46"/>' + _fig(50, 90, 1.4, PELE, "#4a5aa0") + _fig(100, 90, 1.4, PELE, "#232344") + _fig(150, 90, 1.4, PELE, "#8a4a6a") + '<rect x="70" y="20" width="60" height="38" rx="4" fill="#fff" stroke="#8a93a8" stroke-width="3"/><path d="M 78 50 L 92 38 L 104 44 L 122 28" stroke="#ff4f7d" stroke-width="4" fill="none"/>')
    if tipo == "planilha":
        return ('<rect width="200" height="150" fill="#f3f6ff"/>' + "".join(f'<rect x="14" y="{16 + r * 22}" width="172" height="2" fill="#bfc8e0"/>' for r in range(6)) + "".join(f'<rect x="{34 + c * 26}" y="{120 - [30, 60, 44, 86, 70, 100][c]}" width="16" height="{[30, 60, 44, 86, 70, 100][c]}" fill="{["#6a8cff", "#3be0ff", "#8d7bff", "#38e8a8", "#ffb23e", "#ff4f7d"][c]}"/>' for c in range(6)))
    if tipo == "cafe":
        return ('<rect width="200" height="150" fill="#e8d8c0"/><rect x="62" y="56" width="70" height="62" rx="10" fill="#fff"/><path d="M 132 70 q 26 0 22 22 q -4 14 -22 14" stroke="#fff" stroke-width="9" fill="none"/><rect x="68" y="62" width="58" height="12" rx="4" fill="#6a3a22"/><path d="M 84 46 q -8 -12 0 -22 M 104 44 q -8 -12 0 -22 M 120 46 q -8 -12 0 -22" stroke="#bbb" stroke-width="4" fill="none" stroke-linecap="round"/><rect x="50" y="118" width="94" height="10" rx="5" fill="#d0c0a8"/>')
    return '<rect width="200" height="150" fill="#888"/>'


def quadro(p, tipo, x, y, s=1.0, rot=0, moldura="#8a6a3a"):
    """Quadro pendurado (caixa 240x190 antes de s). Ids: {p}."""
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})"><g id="{p}"><rect x="-120" y="-95" width="240" height="190" rx="8" fill="{moldura}"/>'
            f'<rect x="-108" y="-83" width="216" height="166" rx="4" fill="#fffaf0"/><g transform="translate(-100 -75) scale(1)"><clipPath id="{p}-cp"><rect width="200" height="150"/></clipPath>'
            f'<g clip-path="url(#{p}-cp)">{cena_quadro(tipo)}</g></g></g></g>')


def orbe(p, simbolo, x, y, cor, r=46):
    """Bolha de lembrança: círculo translúcido com pictograma. simbolo: coracao, bolo, carro, sol, nota, relogio, raio, copo."""
    sim = {
        "coracao": '<path d="M 0 14 C -26 -4 -20 -26 0 -14 C 20 -26 26 -4 0 14 Z" fill="#fff"/>',
        "bolo": '<rect x="-16" y="0" width="32" height="14" rx="3" fill="#fff"/><rect x="-2" y="-14" width="4" height="14" fill="#fff"/><path d="M 0 -26 q 6 8 0 12 q -6 -4 0 -12" fill="#ffd23e"/>',
        "carro": '<path d="M -20 8 L -14 -6 L 8 -6 L 20 4 V 12 H -20 Z" fill="#fff"/><circle cx="-10" cy="12" r="5" fill="#fff"/><circle cx="12" cy="12" r="5" fill="#fff"/>',
        "sol": '<circle r="9" fill="#fff"/>' + "".join(f'<line x1="0" y1="-14" x2="0" y2="-22" stroke="#fff" stroke-width="3" transform="rotate({a})"/>' for a in range(0, 360, 45)),
        "nota": '<path d="M -8 10 V -16 L 14 -22 V 4" stroke="#fff" stroke-width="4" fill="none"/><circle cx="-12" cy="12" r="6" fill="#fff"/><circle cx="10" cy="6" r="6" fill="#fff"/>',
        "relogio": '<circle r="18" fill="none" stroke="#fff" stroke-width="4"/><path d="M 0 -10 V 0 L 8 6" stroke="#fff" stroke-width="4" fill="none" stroke-linecap="round"/>',
        "raio": '<path d="M 6 -22 L -14 4 L -2 4 L -8 22 L 14 -6 L 2 -6 Z" fill="#fff"/>',
        "copo": '<path d="M -14 -14 H 14 L 10 16 H -10 Z" fill="#fff"/><path d="M 14 -8 q 12 0 10 10 q -2 8 -12 6" stroke="#fff" stroke-width="3" fill="none"/>',
    }[simbolo]
    return (f'<g transform="translate({x} {y})"><g id="{p}"><circle r="{r}" fill="{cor}" fill-opacity=".38" stroke="{cor}" stroke-width="4"/>'
            f'<circle r="{r - 10}" fill="{cor}" fill-opacity=".25"/><circle cx="-{r * 0.3:.0f}" cy="-{r * 0.35:.0f}" r="{r * 0.16:.0f}" fill="#fff" opacity=".55"/>{sim}</g></g>')
