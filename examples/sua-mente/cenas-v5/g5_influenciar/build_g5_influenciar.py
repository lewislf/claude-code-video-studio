"""Grupo g5: cena "influenciar" inteira (segmentos 0 a 8), no padrão v5.

  python3 build_g5_influenciar.py     # escreve compositions/ e index.html desta pasta

Tema: influenciar sem tocar no cérebro, só controlando a tela e o feed (experimento do Facebook, 2012).
"""
import math, os, random, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
from motor import *  # noqa: E402,F401
from gente import gente, vida_gente as _vida_gente, quadro, orbe, ANCORAS, PELE, CABELO, CASA, TRAB, GRAVATA  # noqa: E402
AQUI = os.path.dirname(os.path.abspath(__file__))  # o motor traz o AQUI de cenas-v5; aqui vale a pasta do grupo

CE = "influenciar"

# camZ do motor grava um set em t=0 a cada chamada e a 1a renderização do tween é preguiçosa: num seek direto (snapshot,
# render em blocos) o último set vence e a câmera aparece no zoom errado. Esta versão guarda um estado por seletor.
CAM_JS = r"""
  var __cam={};
  function camZ(sel,t0,dur,z0,z1,ox,oy,ease){
    if(!__cam[sel]){__cam[sel]={l:Math.log(z0)};tl.set(sel,{scale:z0,svgOrigin:ox+" "+oy},0);}
    var o=__cam[sel];
    tl.to(o,{l:Math.log(z1),duration:dur,ease:ease||"power3.inOut",lazy:false,immediateRender:false,onUpdate:function(){gsap.set(sel,{scale:Math.exp(o.l),svgOrigin:ox+" "+oy});}},t0);
  }
"""
_composicao = composicao


def composicao(i, dur, svg, html, js, extra="", **kw):
    return _composicao(i, dur, svg, html, CAM_JS + js, extra, **kw)


def ID(i):
    return f"{CE}_{i}"


def D(i):
    return seg(CE, i)[1]


def T(i, w, n=0, d=None):
    """Tempo local da palavra, preso dentro do segmento (os tempos do whisper escorregam perto das bordas)."""
    return round(min(max(palavra(CE, i, w, n, d), 0.05), D(i) - 0.4), 2)


def ft(sel, a, b, t):
    return f'tl.fromTo("{sel}",{a},{b},{t:.2f});\n'


# ---------------------------------------------------------------- peças do feed (mesma linguagem do celular da cena C)
COR_T = {"feliz": ("#7b2a6c", "#6b5b2a"), "triste": ("#25427a", "#2b2a80"), "neutro": ("#2a6a6a", "#3a2a8c")}


def cartao(tipo, k=0):
    """Cartão de post 300x170 (x -150..150, y 0..170): avatar, nome, ilustração. feliz = sol sorrindo, triste = nuvem com chuva."""
    cor = COR_T[tipo][k % 2]
    s = (f'<rect x="-150" y="0" width="300" height="170" rx="20" fill="{cor}"/>'
         '<circle cx="-110" cy="34" r="20" fill="#eef1ff" opacity=".85"/><rect x="-80" y="22" width="150" height="12" rx="6" fill="#eef1ff" opacity=".7"/>'
         '<rect x="-80" y="42" width="96" height="10" rx="5" fill="#eef1ff" opacity=".4"/><rect x="-132" y="66" width="264" height="90" rx="12" fill="#000" opacity=".22"/>')
    if tipo == "feliz":
        raios = "".join(f'<line x1="0" y1="-40" x2="0" y2="-50" transform="rotate({a})"/>' for a in range(0, 360, 45))
        s += (f'<g transform="translate(0 111)"><g stroke="#ffd23e" stroke-width="5" stroke-linecap="round">{raios}</g>'
              '<circle r="31" fill="#ffd23e"/><circle cx="-10" cy="-7" r="4" fill="#5a3a00"/><circle cx="10" cy="-7" r="4" fill="#5a3a00"/>'
              '<path d="M-14 6 Q0 20 14 6" fill="none" stroke="#5a3a00" stroke-width="4.5" stroke-linecap="round"/></g>'
              '<path d="M110 -176 c-8 -10 -22 -2 -14 8 l14 12 l14 -12 c8 -10 -6 -18 -14 -8 Z" fill="#ff4f7d" transform="translate(0 312)"/>')
    elif tipo == "triste":
        s += ('<g transform="translate(0 104)"><g stroke="#7fb4ff" stroke-width="4" stroke-linecap="round"><line x1="-18" y1="22" x2="-24" y2="40"/><line x1="0" y1="24" x2="-6" y2="44"/><line x1="18" y1="22" x2="12" y2="40"/></g>'
              '<circle cx="-22" cy="0" r="20" fill="#a9b8d8"/><circle cx="4" cy="-10" r="25" fill="#a9b8d8"/><circle cx="28" cy="2" r="18" fill="#a9b8d8"/><rect x="-40" y="0" width="84" height="20" rx="10" fill="#a9b8d8"/>'
              '<circle cx="-6" cy="0" r="3.5" fill="#2a3050"/><circle cx="14" cy="0" r="3.5" fill="#2a3050"/><path d="M-8 14 Q4 6 16 14" fill="none" stroke="#2a3050" stroke-width="3.5" stroke-linecap="round"/></g>')
    else:
        s += ('<circle cx="-84" cy="96" r="14" fill="#ffd23e"/><path d="M-60 146 L-20 106 L20 138 L50 116 L112 146 Z" fill="#fff" opacity=".35"/>')
    return s


def celular(p, nome, tipos, tint="#2a3a8c", extra=""):
    """Celular da cena C (400x800, centro em 0,0) com cartões. Ids: {p}-{nome}posts, {p}-{nome}c{k}, {p}-{nome}tint."""
    cards = "".join(f'<g transform="translate(0 {-344 + k * 190})"><g id="{p}-{nome}c{k}">{cartao(t, k)}</g></g>' for k, t in enumerate(tipos))
    return (f'<g filter="url(#{p}-sombra)"><rect x="-200" y="-400" width="400" height="800" rx="54" fill="#15133a" stroke="{LILAS}" stroke-width="8"/>'
            f'<rect x="-172" y="-364" width="344" height="728" rx="26" fill="#0e0c26"/></g>'
            f'<clipPath id="{p}-{nome}cp"><rect x="-172" y="-364" width="344" height="728" rx="26"/></clipPath>'
            f'<g clip-path="url(#{p}-{nome}cp)"><g id="{p}-{nome}posts">{cards}{extra}</g>'
            f'<rect id="{p}-{nome}tint" x="-172" y="-364" width="344" height="728" fill="{tint}" opacity="0"/></g>'
            f'<rect x="-50" y="-386" width="100" height="10" rx="5" fill="#2a2870"/>')


TROCA = '<g transform="translate(0 -344)"><g id="{p}-troca">' + cartao("triste").replace("{", "{{").replace("}", "}}") + '</g></g>'


def gente_multidao(p, cols=26, lin=7, cls="m"):
    """Grade de pessoas pequenas (roupas variadas), pés em y = 540 + r*80."""
    rng = random.Random(21)
    return "".join(f'<use class="{cls}" href="#{p}-pp{(c * 5 + r * 3 + rng.randint(0, 7)) % 8}" x="{960 + (c - (cols - 1) / 2) * 68 + rng.randint(-8, 8):.0f}" y="{540 + r * 80 + rng.randint(-5, 5)}"/>'
                   for r in range(lin) for c in range(cols))


def pagina(p, img, nome, realces):
    """Página real (1600x2142) em coordenadas da imagem, com folha, sombra e retângulos de destaque (largura animada)."""
    rs = "".join(f'<rect id="{p}-{nome}h{k}" x="{x}" y="{y}" width="0" height="{h}" fill="#ffd23e" opacity=".55" style="mix-blend-mode:multiply"/>'
                 for k, (x, y, w, h) in enumerate(realces))
    return (f'<rect x="-14" y="-14" width="1628" height="2170" rx="10" fill="#fffdf6" filter="url(#{p}-sombra)"/>'
            f'<image href="assets/docs/{img}.png" x="0" y="0" width="1600" height="2142"/>{rs}')


def realca(p, nome, realces, t0, passo=0.45, off=0):
    return "".join(f'tl.fromTo("#{p}-{nome}h{k + off}",{{attr:{{width:0}}}},{{attr:{{width:{w}}},duration:{passo:.2f},ease:"power1.inOut"}},{t0 + k * passo:.2f});\n'
                   for k, (x, y, w, h) in enumerate(realces))


# ---------------------------------------------------------------- a pessoa de verdade (gente.py) com expressão e celular
# Outras pessoas (não "você") = mesma arte de gente.py com outra paleta. Chaves = hex base de gente.py.
OUTRA_A = {CASA["torso"]: "#2bb3a0", CASA["calca"]: "#3a3a4a", CASA["sapato"]: "#ffd23e", CABELO: "#1a1010", PELE: "#c68a5e"}
OUTRA_B = {CASA["torso"]: "#ff7a5a", CASA["calca"]: "#4a3a7a", CABELO: "#d9a441", PELE: "#f6d2b8"}
OPERADOR = {TRAB["torso"]: "#4a4f6e", CABELO: "#cfcdd8", PELE: "#c99372", GRAVATA: "#ffb23e"}   # o senhor da mesa
_BOCA_RIR = ('<path d="M -11,34 Q 0,44 11,33 Q 0,40 -11,34 Z" fill="#6e2836"/>'
             '<path d="M -11.5,34.2 Q 0,43 11,33.2" fill="none" stroke="#6e2836" stroke-width="2.4" stroke-linecap="round"/>')
_LABIO = '<path d="M -4.5,45 Q 0,46.6 4.5,45" fill="none" stroke="#140a2e" stroke-opacity=".27" stroke-width="1.6" stroke-linecap="round"/>'
_BOCA_N = '<path d="M -9.5,37.6 Q 0,39.4 9.5,37.2" fill="none" stroke="#6e2836" stroke-width="2.4" stroke-linecap="round"/>' + _LABIO
_BOCA_T = ('<path d="M -10,42 Q 0,33.6 10,41.4" fill="none" stroke="#6e2836" stroke-width="2.4" stroke-linecap="round"/>'
           '<path d="M -4,46 Q 0,47 4,46" fill="none" stroke="#140a2e" stroke-opacity=".22" stroke-width="1.4" stroke-linecap="round"/>')
_BIG = "M-9999 -9999h19998v19998h-19998Z "


def _fim_grupo(s, i):
    """Índice logo depois do </g> que fecha o <g ...> que começa em s[i]."""
    prof = 0
    for m in re.finditer(r"<g\b|</g>", s[i:]):
        prof += 1 if m.group(0) != "</g>" else -1
        if prof == 0:
            return i + m.end()
    raise ValueError("grupo sem fim")


def _limb(A, B, C, wa, wb, wc):
    """Porta do limb() do esboço aprovado: membro com cotovelo suave, ponta A arredondada."""
    def nrm(p, q):
        dx, dy = q[0] - p[0], q[1] - p[1]
        l = math.hypot(dx, dy)
        return (-dy / l, dx / l)
    n1, n2 = nrm(A, B), nrm(B, C)
    nb = (n1[0] + n2[0], n1[1] + n2[1])
    L = math.hypot(*nb)
    nb = (nb[0] / L, nb[1] / L)

    def side(s):
        return [(A[0] + n1[0] * wa * s, A[1] + n1[1] * wa * s), (B[0] + nb[0] * wb * s, B[1] + nb[1] * wb * s), (C[0] + n2[0] * wc * s, C[1] + n2[1] * wc * s)]

    def seg(a, b, c):
        t = ((c[0] - a[0]) / 6, (c[1] - a[1]) / 6)
        return (f"C{a[0] + (b[0] - a[0]) / 3:.1f} {a[1] + (b[1] - a[1]) / 3:.1f} {b[0] - t[0]:.1f} {b[1] - t[1]:.1f} {b[0]:.1f} {b[1]:.1f}"
                f"C{b[0] + t[0]:.1f} {b[1] + t[1]:.1f} {c[0] - (c[0] - b[0]) / 3:.1f} {c[1] - (c[1] - b[1]) / 3:.1f} {c[0]:.1f} {c[1]:.1f}")
    o, i = side(1), side(-1)[::-1]
    d = (B[0] - A[0], B[1] - A[1])
    dl = math.hypot(*d)
    return (f"M{o[0][0]:.1f} {o[0][1]:.1f}" + seg(*o) + f"L{i[0][0]:.1f} {i[0][1]:.1f}" + seg(*i)
            + f"Q{A[0] - d[0] / dl * wa * 1.5:.1f} {A[1] - d[1] / dl * wa * 1.5:.1f} {o[0][0]:.1f} {o[0][1]:.1f}Z")


def _peca(cid, d, cor, li=3.3, sh=8, rim=None):
    """piece() do esboço: hex base + luz/sombra recortadas como camadas neutras (a troca de hex recolore)."""
    s = f'<clipPath id="{cid}"><path d="{d}"/></clipPath><path d="{d}" fill="{cor}"/><g clip-path="url(#{cid})">'
    if li:
        s += f'<path d="{_BIG}{d}" transform="translate({li} {li})" fill="#ffffff" fill-opacity=".26" fill-rule="evenodd"/>'
    if sh:
        s += f'<path d="{_BIG}{d}" transform="translate({-sh} {-sh * .35:.1f})" fill="#140a2e" fill-opacity=".33" fill-rule="evenodd"/>'
    if rim:
        s += f'<path d="{_BIG}{d}" transform="translate(-2 0)" fill="{rim}" fill-rule="evenodd"/>'
    return s + "</g>"


def _fone(p, cx, cy, ang, L=38, W=14, frente=False):
    """Celular inclinado (eixo longo vertical girado `ang` graus). A tela ({p}-tela) fica no lado -x local, que aponta
    para o rosto; um brilho suave sai dela."""
    if frente:   # tela de frente para quem vê: lê como celular na hora
        return (f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({ang})">'
                f'<ellipse cx="0" cy="-6" rx="{W * 1.6:.0f}" ry="{L * .8:.0f}" fill="url(#{p}-lzg)"/>'
                f'<rect x="{-W / 2}" y="{-L / 2}" width="{W}" height="{L}" rx="5" fill="#1b1846" stroke="#8d7bff" stroke-width="1.8"/>'
                f'<rect id="{p}-tela" x="{-W / 2 + 2.2}" y="{-L / 2 + 4}" width="{W - 4.4}" height="{L - 8}" rx="2.5" fill="#3be0ff"/>'
                + "".join(f'<rect x="{-W / 2 + 4}" y="{-L / 2 + 7 + k * 9}" width="{W - 8}" height="6" rx="1.5" fill="#0e0c26" opacity=".35"/>' for k in range(int((L - 12) // 9)))
                + "</g>")
    return (f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({ang})">'
            f'<ellipse cx="-14" cy="0" rx="26" ry="{L * .75:.0f}" fill="url(#{p}-lzg)"/>'
            f'<rect x="{-W / 2}" y="{-L / 2}" width="{W}" height="{L}" rx="4" fill="#1b1846" stroke="#8d7bff" stroke-width="1.6"/>'
            f'<rect x="{W / 2 - 4.5}" y="{-L / 2 + 5}" width="2" height="7" rx="1" fill="#8d7bff" opacity=".7"/>'
            f'<rect id="{p}-tela" x="{-W / 2 - 1.2}" y="{-L / 2 + 2}" width="4.2" height="{L - 4}" rx="2" fill="#3be0ff"/></g>')


def _braco_fone(p, cor, pele, ob):
    """Braço do lado direito da tela dobrado, celular na altura do peito (pessoa de pé, giro 30). Ponto de partida: ombro."""
    S = ob
    E = (S[0] + 4, S[1] + 84)
    W = (E[0] + 54, E[1] - 36)
    u = ((W[0] - E[0]), (W[1] - E[1]))
    ul = math.hypot(*u)
    u = (u[0] / ul, u[1] / ul)
    W2 = (W[0] - u[0] * 9, W[1] - u[1] * 9)
    manga = _limb(S, E, W2, 19.5, 17.5, 15.0)
    punho = _limb(W2, ((W2[0] + W[0]) / 2, (W2[1] + W[1]) / 2), W, 15.0, 14.2, 13.4)
    H = (W[0] + u[0] * 9, W[1] + u[1] * 9)              # centro da mão
    # mão desenhada no sistema do aparelho (eixo longo = y local, tela no lado -x, que aponta para o rosto):
    # palma atrás, quatro dedos cruzando as costas do aparelho, polegar dobrando sobre a borda da tela
    C = (H[0] + 4, H[1] - 14)
    dobra = "#140a2e"
    palma = (f'<path d="M 2,4 C 14,0 22,10 19,22 C 16,30 4,31 -2,25 C -5,18 -4,8 2,4 Z" fill="{pele}"/>'
             f'<path d="M 2,4 C 14,0 22,10 19,22 C 16,30 4,31 -2,25 C -5,18 -4,8 2,4 Z" fill="{dobra}" fill-opacity=".16"/>')
    dedos = "".join(f'<path d="M {14 - k:.0f},{y} L {-1 - k * .6:.1f},{y + 1.2:.1f}" stroke="{pele}" stroke-width="5.4" stroke-linecap="round"/>'
                    f'<path d="M {13 - k:.0f},{y + 2.6:.1f} L {1 - k * .6:.1f},{y + 3.4:.1f}" stroke="{dobra}" stroke-opacity=".22" stroke-width="1.1" stroke-linecap="round"/>'
                    for k, y in enumerate((-6, 0, 6, 12)))
    polegar = (f'<path d="M 6,24 Q -4,22 -9.5,13" fill="none" stroke="{pele}" stroke-width="6" stroke-linecap="round"/>'
               f'<path d="M 4,26 Q -5,23 -10,15" fill="none" stroke="{dobra}" stroke-opacity=".2" stroke-width="1.2" stroke-linecap="round"/>')
    fone = (f'<g transform="translate({C[0]:.1f} {C[1]:.1f}) rotate(53)">'
            f'<ellipse cx="-16" cy="-2" rx="28" ry="32" fill="url(#{p}-lzg)"/>{palma}'
            f'<rect x="-7.5" y="-21" width="15" height="42" rx="4" fill="#1b1846" stroke="#8d7bff" stroke-width="1.6"/>'
            f'<rect id="{p}-tela" x="-8.7" y="-19" width="4.2" height="38" rx="2" fill="#3be0ff"/>{dedos}{polegar}</g>')
    mao = dedos = ""
    return (f'<g id="{p}-braco">' + _peca(f"{p}-xm", manga, cor, rim="#ff4fa3")
            + f'<g clip-path="url(#{p}-xm)"><path d="M {E[0] - 14:.0f},{E[1] - 4:.0f} Q {E[0]:.0f},{E[1] + 4:.0f} {E[0] + 12:.0f},{E[1] - 8:.0f}" fill="none" stroke="#140a2e" stroke-opacity=".3" stroke-width="3" stroke-linecap="round"/></g>'
            + _peca(f"{p}-xp", punho, cor, li=0, sh=3) + f'<path d="{punho}" fill="#140a2e" fill-opacity=".3"/>'
            + mao + fone + dedos + "</g>")


def _olhar_baixo(s, p, dx=0.0, dy=3.4, palp=4.0):
    """Olhos para o aparelho na mão: pupila desce e a pálpebra de cima pesa (estático, construído no SVG).
    dx/dy desloca a pupila no sistema do olho (dx > 0 = para onde a pessoa está virada); palp baixa a pálpebra."""
    i = s.index(f'<g id="{p}-olho"')
    j = _fim_grupo(s, i)
    o = s[i:j]
    o = re.sub(r'(<path d="M-?[\d.]+ -?[\d.]+A[^"]*" transform="matrix\(([^)]*)\))',
               lambda m: f"{m.group(1)} translate({dx if float(m.group(2).split()[0]) > 0 else -dx} {dy})", o)
    for pat in (r"(Q 0,)(-?[\d.]+)( -9,0\.5)", r"(Q -1,)(-?[\d.]+)( 10,-0\.5)", r"(Q 0,)(-?[\d.]+)( 9,0\.5)"):
        o = re.sub(pat, lambda m: f"{m.group(1)}{float(m.group(2)) + palp:.2f}{m.group(3)}", o)
    return s[:i] + o + s[j:]


def humano(p, variante="casa", pose="sentado", cel=False, cores=None, cadeira=False, humor="feliz", sombra=True, oculos=False, luz=None, olhar=None):
    """gente() com boca trocável ({p}-bocaF/N/T), sobrancelhas animáveis ({p}-sobD, {p}-sobE) e, se cel, celular na mão
    ({p}-tela = tela do aparelho; sentado: no lugar da caneca; de pé: braço dobrado na altura do peito), olhar e cabeça
    baixos para o aparelho. luz (padrão = cel): brilho de tela no rosto ({p}-luzc). Mesma caixa local de gente()."""
    k = ("casa" if variante == "casa" else "trabalho", "em_pe" if pose == "em_pe" else "sentado", 30)
    anc = ANCORAS[k]
    luz = cel if luz is None else luz
    s = gente(p, variante, pose, glow=None, cadeira=cadeira, sombra=sombra)
    pele = (cores or {}).get(PELE, PELE)
    # boca: os paths depois do nariz com a mesma matriz do nariz
    tn = re.search(r'<path d="M 2,5 C 6,12[^>]*transform="([^"]*)"', s).group(1)
    ini = s.index(f'<g id="{p}-cab">')
    fim = _fim_grupo(s, ini)
    cab = s[ini:fim]
    pos = cab.index('<path d="M-4 22A3')
    pos = cab.index("/>", cab.index("/>", pos) + 2) + 2               # depois dos 2 paths do brilho do nariz
    boca_re = re.compile(r'<path d="([^"]*)" transform="' + re.escape(tn) + r'"([^>]*)/>')
    resto, orig = cab[pos:], ""
    while True:
        m = boca_re.match(resto)
        if not m:
            break
        orig += f'<path d="{m.group(1)}"{m.group(2)}/>'
        resto = resto[m.end():]
    casa = k[0] == "casa"
    bF = orig if casa else _BOCA_RIR + _LABIO
    bN = _BOCA_N if casa else orig
    op = {"feliz": (1, 0, 0), "neutro": (0, 1, 0), "triste": (0, 0, 1)}[humor]
    boca = (f'<g transform="{tn}"><g id="{p}-bocaF" opacity="{op[0]}">{bF}</g><g id="{p}-bocaN" opacity="{op[1]}">{bN}</g>'
            f'<g id="{p}-bocaT" opacity="{op[2]}">{_BOCA_T}</g></g>')
    cab = cab[:pos] + boca + resto
    # sobrancelhas: par (cor + sombra) com a mesma matriz vira grupo animável sem transform no atributo
    lados = iter(("D", "E"))

    def _sob(m):
        return f'<g transform="{m.group(2)}"><g id="{p}-sob{next(lados)}"><path d="{m.group(1)}"{m.group(3)}/><path d="{m.group(1)}"{m.group(4)}/></g></g>'
    cab = re.sub(r'<path d="(M [56],-2[03][^"]*)" transform="([^"]*)"([^>]*)/><path d="\1" transform="\2"([^>]*)/>', _sob, cab, count=2)
    cx, cy = anc["cabeca_centro"]
    extra_cab = ""
    if oculos:
        olhos = list(dict.fromkeys(re.findall(r'<path d="M -9.5,0.8 Q -1,-11.5[^>]*transform="matrix\(([^)]*)\)"', cab)))
        lentes = []
        for mt in olhos:
            a, b_, c_, d_, e, f = map(float, mt.split())
            lentes.append((e, f + 1, abs(a) * 13.5, d_ * 11.5))
        lentes.sort()
        (x1, y1, rx1, ry1), (x2, y2, rx2, ry2) = lentes
        extra_cab = (f'<g fill="#bff4ff" fill-opacity=".16" stroke="#241c34" stroke-width="2.2">'
                     f'<ellipse cx="{x1:.1f}" cy="{y1:.1f}" rx="{rx1:.1f}" ry="{ry1:.1f}"/><ellipse cx="{x2:.1f}" cy="{y2:.1f}" rx="{rx2:.1f}" ry="{ry2:.1f}"/></g>'
                     f'<path d="M {x1 + rx1:.1f},{y1 - 1:.1f} Q {(x1 + rx1 + x2 - rx2) / 2:.1f},{y1 - 4:.1f} {x2 - rx2:.1f},{y2 - 1:.1f} M {x1 - rx1:.1f},{y1 - 2:.1f} L {x1 - rx1 - 14:.1f},{y1 - 5:.1f}" '
                     f'fill="none" stroke="#241c34" stroke-width="2.2" stroke-linecap="round"/>'
                     f'<path d="M {x2 - rx2 * .5:.1f},{y2 - ry2 * .5:.1f} l 5,-2" stroke="#ffffff" stroke-opacity=".7" stroke-width="1.6" stroke-linecap="round"/>')
    if cel:   # cabeça inclina para o aparelho: grupo estático por dentro do {p}-cab (o GSAP anima só o {p}-cabW por fora)
        cab = cab.replace(f'<g id="{p}-cab">', f'<g id="{p}-cab"><g transform="rotate(7 {cx} {cy + 46})">', 1)[:-4] + extra_cab + "</g></g>"
    elif extra_cab:
        cab = cab[:-4] + extra_cab + "</g>"
    s = s[:ini] + cab + s[fim:]
    if cel:
        s = _olhar_baixo(s, p)
    elif olhar:
        s = _olhar_baixo(s, p, *olhar)
    if cel:
        if k[1] == "sentado":   # troca a caneca pelo celular, por baixo dos dedos que já a seguravam
            i = s.index(f'id="{p}-braco"')
            j = _fim_grupo(s, s.rindex("<g", 0, i))
            br = s[i:j]
            caneca = re.compile(r'<g clip-path="url\(#[^"]+\)">(?:<path [^>]*#ffb347[^>]*/>)+</g>|<path [^>]*(?:#ffb347|#7a3d1c|#4a2412|#a98bff)[^>]*/>')
            m0 = caneca.search(br)
            br = br[:m0.start()] + "@FONE@" + caneca.sub("", br[m0.start():])
            br = re.sub(r'<g opacity="[^"]*"></g>', "", br)
            mx, my = anc["mao_e"]
            br = br.replace("@FONE@", _fone(p, mx - 24, my - 22, -16, 46, 26, frente=True))
            s = s[:i] + br + s[j:]
        else:
            i = s.rindex("<g", 0, s.index(f'id="{p}-braco"'))
            j = _fim_grupo(s, i)
            s = s[:i] + _braco_fone(p, CASA["torso"] if casa else TRAB["torso"], PELE, anc["ombro_braco"]) + s[j:]
    defs = (f'<filter id="{p}-lzb" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="9"/></filter>'
            f'<radialGradient id="{p}-lzg"><stop offset="0" stop-color="#3be0ff" stop-opacity=".45"/><stop offset="1" stop-color="#3be0ff" stop-opacity="0"/></radialGradient>')
    s = s.replace("</defs>", defs + "</defs>", 1)
    if luz:   # fora do corpo (o filtro de rim não pega no brilho); estático, segue o rosto inclinado
        dx = 16 if cel else 14
        s = s[:-4] + (f'<ellipse id="{p}-luzc" cx="{cx + dx:.0f}" cy="{cy + (20 if cel else 6):.0f}" rx="40" ry="46" fill="#3be0ff" opacity=".22" '
                      f'filter="url(#{p}-lzb)" style="mix-blend-mode:screen"/>') + "</g>"
    for a, b in (cores or {}).items():
        s = s.replace(a, b)
    return s


def vida_gente(p, dur, piscadas=(2.0, 5.3, 8.8, 12.1, 16.4, 20.2)):
    """gente.vida_gente sem a respiração no {p}-tor: a caixa do tronco inclui os recortes de 19998 px (M-9999...), então
    transformOrigin "50% 100%" cai em y ~ +9999 e o scaleY joga o tronco ~120 px para cima (capuz sobre a cabeça)."""
    return re.sub(r'tl\.fromTo\("#[^"]*-tor".*?\);', "", _vida_gente(p, dur, piscadas), count=1)


def humor_js(p, de, para, t, dur=0.3):
    """Troca a boca de `de` para `para` no instante t (feliz/neutro/triste); triste também ergue a ponta de dentro das sobrancelhas."""
    k = {"feliz": "F", "neutro": "N", "triste": "T"}
    sob = f"#{p}-sobD, #{p}-sobE"
    js = ft(f"#{p}-boca{k[de]}", "{opacity:1}", "{opacity:0,duration:%.2f,immediateRender:false}" % dur, t)
    js += ft(f"#{p}-boca{k[para]}", "{opacity:0}", "{opacity:1,duration:%.2f,immediateRender:false}" % dur, t)
    if para == "triste":
        js += ft(sob, "{rotation:0,y:0,transformOrigin:'0% 50%'}", "{rotation:14,y:-2.5,transformOrigin:'0% 50%',duration:0.4,immediateRender:false}", t)
    if de == "triste":
        js += ft(sob, "{rotation:14,y:-2.5,transformOrigin:'0% 50%'}", "{rotation:0,y:0,transformOrigin:'0% 50%',duration:0.4,immediateRender:false}", t)
    return js


def olhar_cel(p):
    """O olhar para o aparelho já vem desenhado no SVG (humano(cel=True)); mantida para não mexer nas cenas."""
    return ""


def tela_js(p, cores, t0, passo=0.5):
    """A telinha do aparelho muda de cor a cada post (feed rolando)."""
    return "".join(f'tl.to("#{p}-tela",{{attr:{{fill:"{c}"}},duration:0.15}},{t0 + k * passo:.2f});\n' for k, c in enumerate(cores))


def chao(y, op=.55):
    return (f'<rect x="-400" y="{y}" width="2720" height="700" fill="#0b0824" opacity="{op}"/>'
            f'<rect x="-400" y="{y}" width="2720" height="4" fill="#4a3aa0" opacity=".6"/>')


def sofa(cor="#b0466e", esc="#7a2a50"):
    """Sofá de lado (pessoa sentada com pés em y=0 voltada para a direita). Desenhe antes da pessoa."""
    return (f'<rect x="-196" y="-250" width="360" height="110" rx="26" fill="{esc}"/>'
            f'<rect x="-196" y="-400" width="96" height="290" rx="40" fill="{cor}"/>'
            f'<rect x="-170" y="-330" width="80" height="120" rx="30" fill="#ffd23e" opacity=".85" transform="rotate(-10 -130 -270)"/>'
            f'<rect x="-196" y="-168" width="370" height="92" rx="24" fill="{cor}"/><rect x="-186" y="-176" width="350" height="34" rx="16" fill="#d0628e"/>'
            f'<rect x="-176" y="-80" width="20" height="80" rx="6" fill="#3a1a30"/><rect x="140" y="-80" width="20" height="80" rx="6" fill="#3a1a30"/>')


def abajur(p, x, y, alt=420, cor="#ffd27a"):
    return (f'<g transform="translate({x} {y})"><ellipse cx="0" cy="-{alt - 30}" rx="150" ry="150" fill="{cor}" opacity=".16" filter="url(#{p}-blur40)"/>'
            f'<path d="M -6 0 L -6 -{alt - 60} L 6 -{alt - 60} L 6 0 Z" fill="#2a1d70"/><ellipse cx="0" cy="0" rx="50" ry="10" fill="#2a1d70"/>'
            f'<path d="M -54 -{alt - 60} L -34 -{alt} L 34 -{alt} L 54 -{alt - 60} Z" fill="{cor}"/></g>')


def pessoinha(camisa, calca, pele, cabelo, cel=False):
    """Figura pequena de frente (pés em y=0, altura ~88). Para multidão via <use>."""
    s = (f'<rect x="-10" y="-36" width="8" height="36" rx="3" fill="{calca}"/><rect x="2" y="-36" width="8" height="36" rx="3" fill="{calca}"/>'
         f'<path d="M -14 -34 L -14 -58 Q -14 -66 -6 -66 L 6 -66 Q 14 -66 14 -58 L 14 -34 Z" fill="{camisa}"/>')
    if cel:
        s += (f'<path d="M -13 -60 L -6 -44 L 0 -46 M 13 -60 L 6 -44 L 0 -46" stroke="{camisa}" stroke-width="6" stroke-linecap="round" fill="none"/>'
              f'<rect x="-5" y="-54" width="10" height="13" rx="2" fill="#bff4ff"/><circle cx="0" cy="-62" r="16" fill="#3be0ff" opacity=".22"/>'
              f'<circle cx="0" cy="-74" r="10" fill="{pele}"/><path d="M -10 -76 Q -10 -86 0 -86 Q 10 -86 10 -76 Q 4 -81 -10 -76 Z" fill="{cabelo}"/>')
    else:
        s += (f'<path d="M -14 -60 L -18 -36 M 14 -60 L 18 -36" stroke="{camisa}" stroke-width="6" stroke-linecap="round"/>'
              f'<circle cx="-18" cy="-34" r="3.5" fill="{pele}"/><circle cx="18" cy="-34" r="3.5" fill="{pele}"/>'
              f'<circle cx="0" cy="-77" r="10" fill="{pele}"/><path d="M -10 -78 Q -11 -89 0 -89 Q 11 -89 10 -78 Q 3 -84 -10 -78 Z" fill="{cabelo}"/>'
              f'<path d="M -4 -74 Q 0 -71 4 -74" stroke="#7a3a2a" stroke-width="1.6" fill="none" stroke-linecap="round"/>')
    return s


PAL_GENTE = [("#ff7a8a", "#2f3f9a", PELE, CABELO), ("#38e8a8", "#3a3a4a", "#c68a5e", "#1a1010"), ("#ffd23e", "#4a3a7a", "#f6d2b8", "#d9a441"),
             ("#6a8cff", "#232344", "#8a5a3a", "#14100c"), ("#ff9f43", "#2a5a6a", "#e8b48c", "#5a2a1a"), ("#c77dff", "#3a2a2a", "#a86b45", "#2a1a10"),
             ("#f3f6ff", "#2a3a8a", PELE, "#241711"), ("#ff4fa3", "#1e2a4a", "#d9a07a", "#8a4a20")]


def gente_defs(p, cel=False):
    return "".join(f'<g id="{p}-pp{k}">{pessoinha(*c, cel=cel)}</g>' for k, c in enumerate(PAL_GENTE))


def mesa_laptop(p):
    """Mesa com notebook à frente da pessoa sentada (desenhe antes dela; a mão pousa no teclado)."""
    return ('<rect x="440" y="-200" width="18" height="200" fill="#3a2a6a"/><rect x="166" y="-200" width="16" height="200" fill="#3a2a6a"/>'
            '<rect x="100" y="-216" width="390" height="22" rx="6" fill="#6a4a9a"/>'
            '<rect x="96" y="-228" width="210" height="12" rx="4" fill="#c9d0ea"/>'
            f'<polygon id="{p}-luzl" points="316,-236 340,-392 60,-450 50,-400" fill="#3be0ff" opacity=".14"/>'
            '<path d="M 304 -224 L 342 -392" stroke="#c9d0ea" stroke-width="16" stroke-linecap="round"/>'
            f'<path id="{p}-tl" d="M 296 -232 L 332 -386" stroke="#3be0ff" stroke-width="6" stroke-linecap="round"/>'
            '<g transform="translate(410 -216)"><rect x="-18" y="-40" width="36" height="40" rx="6" fill="#ff7a8a"/><path d="M 18 -32 q 14 2 10 16 q -2 8 -10 6" stroke="#ff7a8a" stroke-width="6" fill="none"/>'
            '<path d="M -4 -50 q -6 -10 0 -18 M 8 -50 q -6 -10 0 -18" stroke="#eef1ff" stroke-width="3" fill="none" opacity=".6"/></g>')


def poltrona(cor="#2a8a9a", esc="#1a5a6a"):
    """Poltrona de lado (pessoa sentada, pés em y=0). Desenhe antes da pessoa."""
    return (f'<rect x="-190" y="-270" width="300" height="120" rx="30" fill="{esc}"/>'
            f'<path d="M -200 -150 L -200 -390 Q -200 -440 -150 -440 Q -100 -440 -100 -390 L -100 -150 Z" fill="{cor}"/>'
            f'<rect x="-200" y="-176" width="350" height="96" rx="26" fill="{cor}"/><rect x="-190" y="-184" width="330" height="30" rx="14" fill="#3bb0c0"/>'
            '<rect x="-180" y="-84" width="18" height="84" rx="5" fill="#123a44"/><rect x="120" y="-84" width="18" height="84" rx="5" fill="#123a44"/>')


def cama_fundo():
    return ('<rect x="-236" y="-440" width="64" height="420" rx="22" fill="#4a2f9a" stroke="#8d7bff" stroke-width="4"/>'
            '<rect x="-236" y="-182" width="600" height="44" rx="16" fill="#e8e4ff"/>'
            '<rect x="-206" y="-282" width="120" height="96" rx="34" fill="#fffaf0" transform="rotate(-14 -146 -234)"/>')


def cama_frente():
    return ('<path d="M -60 -150 C -40 -214 130 -216 170 -184 C 220 -176 300 -180 364 -176 L 364 -128 L -60 -128 Z" fill="#ff7a8a"/>'
            '<path d="M -40 -164 C 0 -196 100 -200 150 -182" stroke="#ffb0bc" stroke-width="6" fill="none" stroke-linecap="round"/>'
            '<rect x="-236" y="-140" width="600" height="140" rx="14" fill="#3a2a8c"/><rect x="-236" y="-140" width="600" height="14" rx="6" fill="#ff5a70"/>'
            '<rect x="-236" y="-8" width="600" height="8" rx="3" fill="#2a1d70"/>')


def janela_noite(x, y, w, h):
    return (f'<g transform="translate({x} {y})"><rect width="{w}" height="{h}" rx="10" fill="#0e1240" stroke="#8d7bff" stroke-width="8"/>'
            f'<circle cx="{w * .7:.0f}" cy="{h * .32:.0f}" r="{h * .14:.0f}" fill="#fff3b0"/><circle cx="{w * .7 + h * .07:.0f}" cy="{h * .28:.0f}" r="{h * .12:.0f}" fill="#0e1240"/>'
            + "".join(f'<circle cx="{w * a:.0f}" cy="{h * b:.0f}" r="2.5" fill="#fff"/>' for a, b in ((.2, .2), (.35, .55), (.15, .7), (.55, .8), (.85, .65)))
            + f'<path d="M {w / 2} 0 V {h} M 0 {h / 2} H {w}" stroke="#8d7bff" stroke-width="6"/></g>')


def banco_onibus():
    return ('<rect x="-160" y="-420" width="74" height="300" rx="22" fill="#2a6ad0"/><rect x="-150" y="-406" width="54" height="40" rx="10" fill="#7fb4ff"/>'
            '<rect x="-160" y="-176" width="320" height="56" rx="18" fill="#2a6ad0"/><rect x="-40" y="-120" width="18" height="120" fill="#5a6a8a"/>')


def onibus_janelas(p, x0, x1, y0, y1):
    """Faixa de janelas do ônibus com a cidade passando ({p}-cid anda para a esquerda)."""
    w = x1 - x0
    rng = random.Random(5)
    predios = ""
    xx = 0
    while xx < 2 * w + 400:
        bw, bh = rng.randint(60, 130), rng.randint(90, int((y1 - y0) * .85))
        predios += f'<rect x="{xx}" y="{y1 - y0 - bh}" width="{bw}" height="{bh}" fill="{rng.choice(["#2a2f7a", "#35308a", "#24286a"])}"/>'
        predios += "".join(f'<rect x="{xx + 12 + c * 22}" y="{y1 - y0 - bh + 14 + r * 26}" width="10" height="12" fill="#ffd27a" opacity="{rng.choice([.2, .7, .9])}"/>'
                           for r in range(max(1, bh // 26 - 1)) for c in range(max(1, (bw - 16) // 22)))
        xx += bw + rng.randint(6, 24)
    return (f'<clipPath id="{p}-jcp"><rect x="{x0}" y="{y0}" width="{w}" height="{y1 - y0}" rx="18"/></clipPath>'
            f'<rect x="{x0}" y="{y0}" width="{w}" height="{y1 - y0}" rx="18" fill="#3a5ab8"/>'
            f'<g clip-path="url(#{p}-jcp)"><g transform="translate({x0} {y0})"><g id="{p}-cid">{predios}</g></g></g>'
            + "".join(f'<rect x="{x0 + k * w / 3 - 8:.0f}" y="{y0 - 6}" width="16" height="{y1 - y0 + 12}" fill="#c9d0ea"/>' for k in range(1, 3))
            + f'<rect x="{x0 - 8}" y="{y0 - 8}" width="{w + 16}" height="{y1 - y0 + 16}" rx="22" fill="none" stroke="#c9d0ea" stroke-width="12"/>')


def cozinha(x0, x1, ytop, ychao):
    """Bancada (atrás da pessoa), armários altos, janela com sol. Coordenadas globais."""
    w = x1 - x0
    return (f'<rect x="{x0}" y="{ytop - 480}" width="{w}" height="150" rx="10" fill="#e8d8c0"/>'
            + "".join(f'<rect x="{x0 + 10 + k * (w - 20) / 3:.0f}" y="{ytop - 470}" width="{(w - 20) / 3 - 10:.0f}" height="130" rx="8" fill="#f6ead8"/><circle cx="{x0 + (k + .5) * (w - 20) / 3 + 10:.0f}" cy="{ytop - 350}" r="5" fill="#a08a6a"/>' for k in range(3))
            + f'<g transform="translate({x0 + w * .38:.0f} {ytop - 300})"><rect width="{w * .4:.0f}" height="220" rx="8" fill="#ffe9b0" stroke="#f6ead8" stroke-width="10"/>'
            f'<circle cx="{w * .28:.0f}" cy="90" r="42" fill="#ffb23e"/><path d="M 0 180 Q {w * .1:.0f} 150 {w * .2:.0f} 170 T {w * .4:.0f} 160 V 220 H 0 Z" fill="#8bd18b"/></g>'
            f'<rect x="{x0}" y="{ytop}" width="{w}" height="22" rx="6" fill="#d0c0a8"/><rect x="{x0 + 10}" y="{ytop + 22}" width="{w - 20}" height="{ychao - ytop - 22}" fill="#b98a5e"/>'
            + "".join(f'<rect x="{x0 + 22 + k * (w - 44) / 3:.0f}" y="{ytop + 36}" width="{(w - 44) / 3 - 12:.0f}" height="{ychao - ytop - 60}" rx="8" fill="#c99a6e"/>' for k in range(3))
            + f'<g transform="translate({x1 - 90} {ytop})"><path d="M -34 0 L -30 -60 Q 0 -74 30 -60 L 34 0 Z" fill="#ff4f7d"/><path d="M 30 -50 q 22 4 18 26" stroke="#ff4f7d" stroke-width="7" fill="none"/>'
            f'<path d="M -6 -80 q -8 -14 0 -26 M 10 -80 q -8 -14 0 -26" stroke="#eef1ff" stroke-width="4" fill="none" opacity=".7"/></g>')


# ---------------------------------------------------------------- 0: "Arquivo quatro. Influenciar."
def cena0():
    i = 0; p = ID(i); dur = D(i)
    t_arq, t_4, t_inf = T(i, "arquivo"), T(i, "4"), T(i, "influenciar")
    extra = (f'<linearGradient id="{p}-pT" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9a35a"/><stop offset="1" stop-color="#a5672b"/></linearGradient>'
             f'<linearGradient id="{p}-pF" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3c983"/><stop offset="1" stop-color="#d39a50"/></linearGradient>'
             f'<radialGradient id="{p}-luz" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#3be0ff" stop-opacity=".55"/><stop offset="1" stop-color="#3be0ff" stop-opacity="0"/></radialGradient>')
    svg = f"""<g id="{p}-pastaY">
 <ellipse cx="960" cy="935" rx="620" ry="30" fill="#05031a" opacity=".55" filter="url(#{p}-blur6)"/>
 <path d="M410 300 L410 244 Q410 222 432 222 L842 222 Q864 222 872 244 L892 300 L1510 300 L1510 900 L410 900 Z" fill="url(#{p}-pT)" stroke="#ffe0a0" stroke-width="5"/>
 <clipPath id="{p}-tabcp"><rect x="420" y="226" width="460" height="74"/></clipPath>
 <g clip-path="url(#{p}-tabcp)"><g id="{p}-tabT"><text x="446" y="268" font-family="IBM Plex Mono" font-weight="700" font-size="46" letter-spacing="5" fill="#3a2412">ARQUIVO 4</text></g></g>
 <rect x="460" y="282" width="1000" height="600" rx="8" fill="#fffaf0" transform="rotate(-2 960 580)"/>
 <rect x="470" y="292" width="980" height="590" rx="8" fill="#efe6d2" transform="rotate(1.6 960 580)"/>
 <ellipse id="{p}-brilho" cx="960" cy="330" rx="420" ry="260" fill="url(#{p}-luz)" opacity="0"/>
 <g transform="translate(960 650) scale(.56)"><g id="{p}-celY">{celular(p, "a", ["feliz", "neutro", "triste", "feliz", "neutro", "triste", "feliz", "neutro"])}</g></g>
 <path d="M380 452 L1540 452 L1504 912 L416 912 Z" fill="url(#{p}-pF)" stroke="#ffe0a0" stroke-width="5" stroke-linejoin="round"/>
 <path d="M396 470 L1524 470" stroke="#fff6dc" stroke-width="4" opacity=".6"/>
 <clipPath id="{p}-ticp"><rect x="420" y="560" width="1080" height="260"/></clipPath>
 <g clip-path="url(#{p}-ticp)"><g id="{p}-tit"><text x="960" y="760" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="190" fill="#2a1650">Influenciar</text></g></g>
</g>"""
    js = (f'camZ("#{p}-cam", 0, {dur:.2f}, 1.0, 1.1, 960, 560, "power1.inOut");\n'
          + ft(f"#{p}-pastaY", "{y:760,rotation:3,transformOrigin:'50% 50%'}", "{y:0,rotation:0,transformOrigin:'50% 50%',duration:0.8,ease:'expo.out'}", 0.0)
          + ft(f"#{p}-tabT", "{y:80}", "{y:0,duration:0.7,ease:'expo.out'}", max(0.3, t_arq + 0.1))
          + ft(f"#{p}-celY", "{y:0}", "{y:-400,duration:0.9,ease:'back.out(1.5)'}", t_inf - 0.35)
          + ft(f"#{p}-brilho", "{opacity:0}", "{opacity:1,duration:0.6}", t_inf - 0.2)
          + ft(f"#{p}-aposts", "{y:0}", "{y:-420,duration:%.2f,ease:'none'}" % (dur - t_inf + 0.3), t_inf - 0.3)
          + ft(f"#{p}-tit", "{y:260}", "{y:0,duration:0.8,ease:'expo.out'}", t_inf))
    return composicao(p, dur, svg, "", js, extra, seed=4)


# ---------------------------------------------------------------- 1: laboratório, implante, ressonância... só um feed
def cena1():
    i = 1; p = ID(i); dur = D(i)
    t_lab, t_imp, t_res, t_prox, t_so, t_feed = T(i, "laboratorio"), T(i, "implante"), T(i, "ressonancia"), T(i, "proximo"), T(i, "so"), T(i, "feed")
    extra = (f'<radialGradient id="{p}-anel" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#8d7bff"/><stop offset="1" stop-color="#3a2a8c"/></radialGradient>'
             f'<linearGradient id="{p}-vidro" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#bff4ff" stop-opacity=".18"/><stop offset="1" stop-color="#bff4ff" stop-opacity=".05"/></linearGradient>')
    frasco = (f'<ellipse cx="0" cy="178" rx="170" ry="16" fill="#05031a" opacity=".5"/>'
              f'<path d="M-112 60 L112 60 L150 130 Q160 160 130 160 L-130 160 Q-160 160 -150 130 Z" fill="{MENTA}" opacity=".75"/>'
              f'<g id="{p}-bolhas" fill="#d8fff0">' + "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in [(-40, 120, 9), (20, 100, 7), (60, 135, 10), (-80, 140, 6), (0, 80, 5)]) + '</g>'
              f'<path d="M-50 -170 L-50 -60 L-150 130 Q-160 160 -130 160 L130 160 Q160 160 150 130 L50 -60 L50 -170 Z" fill="url(#{p}-vidro)" stroke="{CIANO}" stroke-width="8" stroke-linejoin="round" filter="url(#{p}-glow)"/>'
              f'<rect x="-66" y="-190" width="132" height="22" rx="10" fill="#15133a" stroke="{CIANO}" stroke-width="6"/>'
              f'<path d="M-24 -40 L-60 40" stroke="#fff" stroke-opacity=".4" stroke-width="10" stroke-linecap="round"/>')
    rm = (f'<ellipse cx="0" cy="200" rx="250" ry="18" fill="#05031a" opacity=".5"/>'
          f'<circle r="180" fill="url(#{p}-anel)" stroke="#c9b8ff" stroke-width="6" filter="url(#{p}-sombra)"/>'
          f'<circle r="96" fill="#0b0a24" stroke="{CIANO}" stroke-width="6" filter="url(#{p}-glow)"/>'
          f'<rect x="-250" y="40" width="500" height="30" rx="12" fill="#eef1ff"/><rect x="-40" y="70" width="80" height="120" fill="#2a2870"/>'
          f'<path d="M-130 -120 A180 180 0 0 1 60 -170" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="12" stroke-linecap="round"/>')
    chip = (f'<g id="{p}-chip"><path d="M196 34 C 196 0 230 -10 250 -30" fill="none" stroke="{AMBAR}" stroke-width="3" stroke-linecap="round"/>'
            f'<rect x="180" y="26" width="34" height="20" rx="5" fill="{AMBAR}" filter="url(#{p}-glow)" transform="rotate(-12 197 36)"/></g>')
    svg = f"""<g id="{p}-trio">
 <g transform="translate(400 470)"><g id="{p}-lab">{frasco}</g></g>
 <g transform="translate(632 246) scale(1.6)"><g id="{p}-impW">{pessoa(p + "i", glow=p + "-glow")}{chip}</g></g>
 <g transform="translate(1520 470)"><g id="{p}-rm">{rm}</g></g>
</g>
<g id="{p}-casa" opacity="0">
 {chao(905)}
 <ellipse id="{p}-halo" cx="1440" cy="540" rx="380" ry="440" fill="#3be0ff" opacity="0" filter="url(#{p}-blur40)"/>
 {quadro(p + "-q1", "familia", 330, 300, .9, -2)}{quadro(p + "-q2", "praia", 610, 270, .75, 3)}
 {abajur(p, 190, 905, 470)}
 <g transform="translate(560 905)"><g id="{p}-g">{sofa()}{humano(p + "g", "casa", "sentado", cel=True)}</g></g>
 <polygon id="{p}-feixe" points="668,560 1270,250 1270,830" fill="#3be0ff" opacity="0"/>
 <g transform="translate(1440 540) scale(.72)"><g id="{p}-cel">{celular(p, "f", ["feliz", "neutro", "triste", "feliz", "neutro", "feliz", "triste", "neutro"])}</g></g>
</g>"""
    html = (texto(f"{p}-l1", "LABORATÓRIO", "left:140px;width:520px;text-align:center;top:720px;font-size:46px;color:#bff4ff", "pill2")
            + texto(f"{p}-l2", "IMPLANTE", "left:700px;width:520px;text-align:center;top:720px;font-size:46px;color:#ffd98a", "pill2")
            + texto(f"{p}-l3", "RESSONÂNCIA", "left:1260px;width:520px;text-align:center;top:720px;font-size:46px;color:#c9b8ff", "pill2")
            + texto(f"{p}-t", "Só um feed", "left:1000px;width:980px;text-align:center;top:40px;font-size:120px;color:#ffffff"))
    js = (f'camZ("#{p}-cam", 0, {t_res + 0.6:.2f}, 1.45, 1.0, 400, 470);\n'
          f'camZ("#{p}-cam", {t_res + 0.6:.2f}, {dur - t_res - 0.6:.2f}, 1.0, 1.05, 400, 470, "power1.inOut");\n'
          f'pop("#{p}-lab", 0.25, 0.4, 0.8); rise("#{p}-l1 span", {t_lab:.2f});\n'
          + ft(f"#{p}-bolhas", "{y:0}", "{y:-60,duration:0.9,repeat:7,ease:'power1.in'}", t_lab)
          + f'pop("#{p}-impW", {t_imp - 0.1:.2f}, 0.4, 0.8); rise("#{p}-l2 span", {t_imp:.2f});\n'
          + ft(f"#{p}-chip", "{opacity:1}", "{opacity:0.35,duration:0.3,repeat:9,yoyo:true,ease:'sine.inOut'}", t_imp + 0.6)
          + f'pop("#{p}-rm", {t_res - 0.1:.2f}, 0.4, 0.8); rise("#{p}-l3 span", {t_res:.2f});\n'
          + ft(f"#{p}-trio", "{opacity:1,y:0,scale:1,svgOrigin:'960 470'}", "{opacity:0,y:90,scale:0.82,svgOrigin:'960 470',duration:0.9,ease:'power2.inOut',immediateRender:false}", t_prox)
          + "".join(some(f"#{p}-l{k} span", t_prox) for k in (1, 2, 3))
          + f'entra("#{p}-casa", {t_prox + 0.3:.2f}, 0.4);\n'
          + ft(f"#{p}-g", "{x:-500}", "{x:0,duration:1.0,ease:'expo.out',immediateRender:false}", t_prox + 0.3)
          + ft(f"#{p}-cel", "{y:900}", "{y:0,duration:1.0,ease:'back.out(1.2)',immediateRender:false}", t_prox + 0.5)
          + ft(f"#{p}-halo", "{opacity:0}", "{opacity:0.22,duration:0.8}", t_prox + 0.9)
          + ft(f"#{p}-feixe", "{opacity:0}", "{opacity:0.12,duration:0.6}", t_feed - 0.2)
          + ft(f"#{p}-fposts", "{y:0}", "{y:-500,duration:%.2f,ease:'none'}" % (dur - t_prox), t_prox + 0.4)
          + olhar_cel(p + "g") + tela_js(p + "g", ["#ffd23e", "#8d7bff", "#7fb4ff", "#ffd23e", "#38e8a8"], t_prox + 0.6, 0.55)
          + f'rise("#{p}-t span", {t_so:.2f}, 0.9);\n'
          + vida_pessoa(p + "i", dur) + vida_gente(p + "g", dur, (t_prox + 1.4, t_prox + 3.0)))
    return composicao(p, dur, svg, html, js, extra, seed=6)


def some(sel, t):
    return f'tl.to("{sel}",{{yPercent:-125,duration:0.45,ease:"power2.in"}},{t:.2f});\n'


# ---------------------------------------------------------------- 2: janeiro de 2012, 689 mil pessoas, menos felizes / menos tristes
def cena2():
    i = 2; p = ID(i); dur = D(i)
    t_jan, t_sem, t_fb, t_mud, t_num, t_pes = T(i, "janeiro"), T(i, "semana"), T(i, "facebook"), T(i, "mudou"), T(i, "680"), T(i, "pessoas")
    t_umas, t_men1, t_fel, t_out, t_men2, t_pub2 = T(i, "para"), T(i, "menos"), T(i, "felizes"), T(i, "outras"), T(i, "menos", 1), T(i, "publicacoes", 1)
    extra = gente_defs(p)
    dias = "".join(f'<rect id="{p}-d{k}" x="{565 + k * 116}" y="480" width="96" height="96" rx="16" fill="#2a2870" stroke="#4a4ab0" stroke-width="4"/>' for k in range(7))
    dias += "".join(f'<rect x="{565 + k * 116}" y="604" width="96" height="96" rx="16" fill="#1e1c5a" opacity=".6"/>' for k in range(7))
    aneis = "".join(f'<rect x="{620 + k * 140}" y="306" width="18" height="70" rx="9" fill="#eef1ff" stroke="#15133a" stroke-width="4"/>' for k in range(5))
    tL = ["feliz", "neutro", "feliz", "triste", "feliz", "neutro", "feliz", "triste"]
    tR = ["triste", "neutro", "triste", "feliz", "triste", "neutro", "triste", "feliz"]
    svg = f"""
<g id="{p}-cal"><g filter="url(#{p}-sombra)"><rect x="520" y="330" width="880" height="420" rx="34" fill="#15133a" stroke="{LILAS}" stroke-width="8"/></g>
 <rect x="524" y="334" width="872" height="100" rx="30" fill="#7b2a6c"/><rect x="524" y="404" width="872" height="30" fill="#7b2a6c"/>{aneis}{dias}
 <rect id="{p}-semana" x="550" y="466" width="822" height="124" rx="24" fill="none" stroke="{AMBAR}" stroke-width="8" opacity="0" filter="url(#{p}-glow)"/></g>
<g id="{p}-g1" opacity="0">
 {chao(880)}
 {janela_noite(170, 150, 300, 230)}
 <g transform="translate(990 880)"><rect x="-70" y="-190" width="140" height="190" rx="10" fill="#4a2f9a"/><rect x="-60" y="-120" width="120" height="8" fill="#2a1d70"/></g>
 {abajur(p, 990, 690, 220, "#ffd27a")}
 <g transform="translate(520 880) scale(1.05)">{cama_fundo()}{humano(p + "b", "casa", "sentado", cel=True)}{cama_frente()}</g>
 <polygon id="{p}-feixe" points="640,540 1200,180 1200,900" fill="#3be0ff" opacity=".1"/>
 <g transform="translate(1380 540) scale(.9)">{celular(p, "m", ["feliz", "neutro", "feliz", "triste", "neutro", "feliz"], extra=TROCA.format(p=p))}</g>
</g>
<g id="{p}-mult" opacity="0">{gente_multidao(p)}</g>
<g id="{p}-dois" opacity="0">
 <g><clipPath id="{p}-pLcp"><rect x="30" y="96" width="900" height="790" rx="30"/></clipPath>
  <rect x="30" y="96" width="900" height="790" rx="30" fill="#120c40" opacity=".85"/>
  <g clip-path="url(#{p}-pLcp)">{onibus_janelas(p, 60, 900, 130, 400)}<rect x="30" y="840" width="900" height="60" fill="#2a2440"/>
   <rect x="452" y="96" width="16" height="760" fill="#ffd23e"/>
   <g transform="translate(200 850) scale(.85)">{banco_onibus()}{humano(p + "L", "casa", "sentado", cel=True, cores=OUTRA_A)}</g></g>
  <rect x="30" y="96" width="900" height="790" rx="30" fill="none" stroke="{LILAS}" stroke-width="6"/>
  <g transform="translate(690 500) scale(.66)">{celular(p, "L", tL, "#1a2a6c")}</g></g>
 <g id="{p}-ladoR"><clipPath id="{p}-pRcp"><rect x="990" y="96" width="900" height="790" rx="30"/></clipPath>
  <rect x="990" y="96" width="900" height="790" rx="30" fill="#2a1a40" opacity=".85"/>
  <g clip-path="url(#{p}-pRcp)">{cozinha(1000, 1520, 640, 860)}<rect x="990" y="850" width="900" height="50" fill="#3a2a3a"/>
   <g transform="translate(1180 860) scale(.78)">{humano(p + "R", "casa", "em_pe", cel=True, cores=OUTRA_B, humor="neutro")}</g></g>
  <rect x="990" y="96" width="900" height="790" rx="30" fill="none" stroke="{LILAS}" stroke-width="6"/>
  <g transform="translate(1680 500) scale(.66)">{celular(p, "R", tR, "#ffb23e")}</g></g>
</g>"""
    html = (texto(f"{p}-t1", "Janeiro de 2012", "left:0;right:0;text-align:center;top:110px;font-size:120px;color:#ffd98a")
            + texto(f"{p}-n", f'<b id="{p}-nv" style="font-weight:700">0</b>', "left:0;right:0;text-align:center;top:40px;font-size:170px;color:#ffffff")
            + texto(f"{p}-np", "PESSOAS", "left:0;right:0;text-align:center;top:262px;font-size:60px;color:#3be0ff", "pill2")
            + texto(f"{p}-lL", "MENOS PUBLICAÇÕES FELIZES", "left:20px;width:900px;text-align:center;top:905px;font-size:48px;color:#9fb8ff;letter-spacing:.01em", "pill2")
            + texto(f"{p}-lR", "MENOS PUBLICAÇÕES TRISTES", "left:980px;width:900px;text-align:center;top:905px;font-size:48px;color:#ffd98a;letter-spacing:.01em", "pill2"))
    js = (f'camZ("#{p}-cam", 0, {t_fb:.2f}, 1.12, 1.0, 960, 540, "power2.out");\n'
          f'camZ("#{p}-cam", {t_fb:.2f}, {t_umas - t_fb:.2f}, 1.0, 1.04, 960, 540, "none");\n'
          f'camZ("#{p}-cam", {t_umas:.2f}, {dur - t_umas:.2f}, 1.04, 1.0, 960, 540, "power1.inOut");\n'
          f'rise("#{p}-t1 span", {t_jan:.2f}); pop("#{p}-cal", 0.05, 0.6, 0.9);\n'
          + "".join(ft(f"#{p}-d{k}", "{fill:'#2a2870'}", "{fill:'#ffb23e',duration:0.15,immediateRender:false}", t_sem - 0.6 + k * 0.17) for k in range(7))
          + ft(f"#{p}-semana", "{opacity:0}", "{opacity:1,duration:0.3}", t_sem + 0.6)
          + some(f"#{p}-t1 span", t_fb - 0.2)
          + ft(f"#{p}-cal", "{opacity:1}", "{opacity:0,y:-200,duration:0.5,ease:'power2.in',immediateRender:false}", t_fb - 0.2)
          + f'entra("#{p}-g1", {t_fb:.2f}, 0.3);\n'
          + ft(f"#{p}-g1", "{scale:1.2,svgOrigin:'960 650'}", "{scale:1,svgOrigin:'960 650',duration:0.9,ease:'expo.out',immediateRender:false}", t_fb)
          + ft(f"#{p}-mposts", "{y:0}", "{y:-300,duration:3,ease:'none'}", t_fb)
          + f'tl.set("#{p}-troca",{{x:380}},0);\n'
          + ft(f"#{p}-mc0", "{x:0}", "{x:-380,duration:0.4,ease:'power2.in'}", t_mud)
          + ft(f"#{p}-troca", "{x:380}", "{x:0,duration:0.5,ease:'back.out(1.4)',immediateRender:false}", t_mud + 0.25)
          + olhar_cel(p + "b") + tela_js(p + "b", ["#ffd23e", "#8d7bff", "#ffd23e"], t_fb + 0.2, 0.6)
          + f'tl.to("#{p}b-tela",{{attr:{{fill:"#7fb4ff"}},duration:0.2}},{t_mud + 0.3:.2f});\n'
          + humor_js(p + "b", "feliz", "neutro", t_mud + 0.5)
          + ft(f"#{p}-g1", "{scale:1,opacity:1,svgOrigin:'960 650'}", "{scale:0.06,opacity:0,svgOrigin:'960 650',duration:0.9,ease:'power2.in',immediateRender:false}", t_num - 0.2)
          + f'entra("#{p}-mult", {t_num:.2f}, 0.3);\n'
          + ft(f"#{p}-mult .m", "{scale:0,transformOrigin:'50% 50%'}", "{scale:1,transformOrigin:'50% 50%',duration:0.3,ease:'back.out(2)',stagger:{amount:1.6,from:'center',grid:[7,26]}}", t_num)
          + ft(f"#{p}-mult", "{scale:1.4,svgOrigin:'960 650'}", "{scale:1,svgOrigin:'960 650',duration:2.6,ease:'power2.out',immediateRender:false}", t_num)
          + f'rise("#{p}-n span", {t_num:.2f});\n'
          + f'contar("{p}-nv", {t_num:.2f}, 1.5, 0, 689, function(v){{return Math.round(v)+" mil";}});\n'
          + f'rise("#{p}-np span", {t_pes:.2f});\n'
          + some(f"#{p}-n span", t_umas - 0.3) + some(f"#{p}-np span", t_umas - 0.3)
          + ft(f"#{p}-mult", "{opacity:1}", "{opacity:0,duration:0.5,immediateRender:false}", t_umas - 0.3)
          + f'entra("#{p}-dois", {t_umas:.2f}, 0.4);\n'
          + ft(f"#{p}-dois", "{x:-300}", "{x:0,duration:0.9,ease:'expo.out',immediateRender:false}", t_umas)
          + ft(f"#{p}-ladoR", "{opacity:0.25}", "{opacity:1,duration:0.5,immediateRender:false}", t_out - 0.3)
          + ft(f"#{p}-ladoR", "{opacity:1}", "{opacity:0.25,duration:0.01}", 0)
          + ft(f"#{p}-Lposts", "{y:0}", "{y:-380,duration:%.2f,ease:'none'}" % (dur - t_umas), t_umas)
          + ft(f"#{p}-Rposts", "{y:0}", "{y:-380,duration:%.2f,ease:'none'}" % (dur - t_umas), t_umas)
          + f'rise("#{p}-lL span", {t_men1:.2f});\n'
          + "".join(ft(f"#{p}-Lc{k}", "{x:0,opacity:1}", "{x:-360,opacity:0,duration:0.45,ease:'power2.in'}", t_men1 + 0.3 + n * 0.3) for n, k in enumerate(k for k, t in enumerate(tL) if t == "feliz"))
          + ft(f"#{p}-Ltint", "{opacity:0}", "{opacity:0.35,duration:0.8}", t_fel - 0.3)
          + humor_js(p + "L", "feliz", "triste", t_fel - 0.2, 0.4)
          + ft(f"#{p}L-luzc", "{attr:{fill:'#3be0ff'}}", "{attr:{fill:'#3b5bff'},duration:0.8}", t_fel - 0.3)
          + ft(f"#{p}-cid", "{x:0}", "{x:-900,duration:%.2f,ease:'none'}" % (dur - t_umas), t_umas)
          + olhar_cel(p + "L") + olhar_cel(p + "R")
          + f'rise("#{p}-lR span", {t_men2:.2f});\n'
          + "".join(ft(f"#{p}-Rc{k}", "{x:0,opacity:1}", "{x:360,opacity:0,duration:0.45,ease:'power2.in'}", t_men2 + 0.3 + n * 0.25) for n, k in enumerate(k for k, t in enumerate(tR) if t == "triste"))
          + ft(f"#{p}-Rtint", "{opacity:0}", "{opacity:0.18,duration:0.8}", t_pub2)
          + humor_js(p + "R", "neutro", "feliz", t_pub2, 0.35)
          + ft(f"#{p}R-luzc", "{attr:{fill:'#3be0ff'}}", "{attr:{fill:'#ffd23e'},duration:0.8}", t_pub2)
          + vida_gente(p + "b", dur, (t_fb + 1.0, t_fb + 2.6)) + vida_gente(p + "L", dur, (9.4, 12.2, 14.8)) + vida_gente(p + "R", dur, (10.1, 13.3, 15.5)))
    return composicao(p, dur, svg, html, js, extra, seed=11)


# ---------------------------------------------------------------- 3: "Ninguém foi avisado."
def cena3():
    i = 3; p = ID(i); dur = D(i)
    t_nin, t_foi, t_av = T(i, "ninguem"), T(i, "foi"), T(i, "avisado")
    extra = gente_defs(p, cel=True) + f'<linearGradient id="{p}-sino" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe08a"/><stop offset="1" stop-color="#e08a1e"/></linearGradient>'
    rng = random.Random(3)
    fila = ""
    for r in range(6):
        e = 1.0 + r * 0.42
        y = 420 + r * 124
        n = int(2200 / (54 * e)) + 2
        fila += f'<g opacity="{0.45 + r * 0.11:.2f}">' + "".join(
            f'<use href="#{p}-pp{rng.randint(0, 7)}" transform="translate({-140 + (c + (r % 2) * .5) * 54 * e + rng.randint(-6, 6):.0f} {y + rng.randint(-6, 6)}) scale({e:.2f})"/>'
            for c in range(n)) + '</g>'
    svg = f"""<g id="{p}-mult">{fila}</g>
<ellipse cx="960" cy="420" rx="320" ry="320" fill="#0b0a24" opacity=".75" filter="url(#{p}-blur40)"/>
<rect x="-100" y="760" width="2120" height="420" fill="#0b0a24" opacity=".8" filter="url(#{p}-blur40)"/>
<g transform="translate(960 400) scale(.9)"><g id="{p}-sino">
 <g id="{p}-sinoB"><circle cx="0" cy="-172" r="22" fill="url(#{p}-sino)"/>
 <path d="M-130 90 C-130 -40 -110 -150 0 -158 C110 -150 130 -40 130 90 L166 136 L-166 136 Z" fill="url(#{p}-sino)" stroke="#fff3c8" stroke-width="6" stroke-linejoin="round" filter="url(#{p}-sombra)"/>
 <circle cx="0" cy="166" r="34" fill="#e08a1e"/><path d="M-80 -60 C-74 -110 -40 -134 -6 -136" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="14" stroke-linecap="round"/></g>
 <circle cx="0" cy="0" r="250" fill="none" stroke="{VERM}" stroke-width="30" stroke-dasharray="1571" stroke-dashoffset="1571" id="{p}-aro" transform="rotate(-135)" filter="url(#{p}-glow)"/>
 <line id="{p}-barra" x1="-177" y1="-177" x2="177" y2="177" stroke="{VERM}" stroke-width="30" stroke-linecap="round" stroke-dasharray="500" stroke-dashoffset="500"/>
</g></g>"""
    html = f'<div style="position:absolute;left:0;right:0;bottom:0;height:330px;background:linear-gradient(rgba(8,6,28,0),rgba(8,6,28,.96) 40%)"></div>' + texto(f"{p}-t", "Ninguém foi avisado", "left:0;right:0;text-align:center;top:830px;font-size:130px;color:#ffffff")
    js = (f'camZ("#{p}-cam", 0, {dur:.2f}, 1.0, 1.1, 960, 400, "power1.inOut");\n'
          f'pop("#{p}-sino", 0.1, 0.4, 0.8);\n'
          + ft(f"#{p}-sinoB", "{rotation:-12,transformOrigin:'50% 0%'}", "{rotation:12,transformOrigin:'50% 0%',duration:0.16,repeat:5,yoyo:true,ease:'sine.inOut'}", 0.3)
          + ft(f"#{p}-mult", "{scale:1.15,svgOrigin:'960 540'}", "{scale:1,svgOrigin:'960 540',duration:%.2f,ease:'power2.out'}" % dur, 0)
          + f'rise("#{p}-t span", {t_nin:.2f}, 0.8);\n'
          + ft(f"#{p}-aro", "{attr:{'stroke-dashoffset':1571}}", "{attr:{'stroke-dashoffset':0},duration:0.5,ease:'power2.inOut'}", t_foi - 0.3)
          + ft(f"#{p}-barra", "{attr:{'stroke-dashoffset':500}}", "{attr:{'stroke-dashoffset':0},duration:0.3,ease:'power2.in'}", t_av)
          + ft(f"#{p}-sinoB", "{opacity:1}", "{opacity:0.7,duration:0.3,immediateRender:false}", t_av + 0.2))
    return composicao(p, dur, svg, html, js, extra, fundo=("#2c1460", "#160c40", "#08061c"), seed=13)


# ---------------------------------------------------------------- 4: página do estudo (Kramer, Guillory e Hancock, PNAS 2014)
R_AUT = [(105, 287, 760, 30)]
R_FRASE = [(594, 744, 180, 29), (105, 771, 669, 29), (105, 798, 250, 29)]


def cena4():
    i = 4; p = ID(i); dur = D(i)
    t_pes, t_med, t_esc, t_quem, t_menos, t_escr, t_men2, t_pos, t_mais, t_neg = (
        T(i, "pesquisadores"), T(i, "mediram"), T(i, "escreveram"), T(i, "quem"), T(i, "menos"), T(i, "escrever", 1),
        T(i, "menos", 1), T(i, "positivas"), T(i, "mais"), T(i, "negativas"))
    S, X0, Y0 = 0.42, 624, 150
    ox, oy = 470, Y0 + 785 * S    # ponto de tela onde a frase citada fica depois do deslize
    svg = f"""<g id="{p}-pgx"><g id="{p}-pgy"><g transform="translate({X0} {Y0}) scale({S})">{pagina(p, "kramer2014", "k", R_AUT + R_FRASE)}
 <g id="{p}-scan" opacity="0"><rect x="0" y="-8" width="1600" height="16" fill="{CIANO}" opacity=".75" filter="url(#{p}-glow)"/><rect x="0" y="-160" width="1600" height="152" fill="{CIANO}" opacity=".1"/></g>
</g></g></g>"""
    painel = f"""<div id="{p}-pan" style="position:absolute;left:1090px;top:150px;width:740px;height:780px;background:#0e0c26;border:4px solid #8d7bff;border-radius:34px;box-shadow:0 24px 70px rgba(0,0,0,.7);opacity:0;overflow:hidden">
 {texto(p + "-pt", "PALAVRAS", "left:0;right:0;text-align:center;top:44px;font-size:56px;color:#eef1f7", "pill2")}
 <div style="position:absolute;left:60px;right:60px;top:590px;height:6px;background:#4a4ab0;border-radius:3px"></div>
 <div id="{p}-gp" style="position:absolute;left:110px;top:210px;width:190px;height:380px;border:4px dashed #38e8a8;border-bottom:none;border-radius:16px 16px 0 0;opacity:0"></div>
 <div id="{p}-gn" style="position:absolute;left:450px;top:290px;width:190px;height:300px;border:4px dashed #ff4f7d;border-bottom:none;border-radius:16px 16px 0 0;opacity:0"></div>
 <div id="{p}-bp" style="position:absolute;left:110px;bottom:190px;width:190px;height:380px;background:linear-gradient(#38e8a8,#14705a);border-radius:16px 16px 0 0"></div>
 <div id="{p}-bn" style="position:absolute;left:450px;bottom:190px;width:190px;height:300px;background:linear-gradient(#ff4f7d,#8a1838);border-radius:16px 16px 0 0"></div>
 <div id="{p}-sp" style="position:absolute;left:175px;top:140px;width:0;height:0;border-left:30px solid transparent;border-right:30px solid transparent;border-top:46px solid #38e8a8;opacity:0"></div>
 <div id="{p}-sn" style="position:absolute;left:515px;top:150px;width:0;height:0;border-left:30px solid transparent;border-right:30px solid transparent;border-bottom:46px solid #ff4f7d;opacity:0"></div>
 {texto(p + "-lp", "POSITIVAS", "left:25px;width:360px;text-align:center;top:625px;font-size:46px;color:#38e8a8;letter-spacing:.03em", "pill2")}
 {texto(p + "-ln", "NEGATIVAS", "left:365px;width:360px;text-align:center;top:625px;font-size:46px;color:#ff7d9a;letter-spacing:.03em", "pill2")}
</div>"""
    html = texto(f"{p}-t", "O QUE ESSAS PESSOAS ESCREVERAM", "left:0;right:0;text-align:center;top:14px;font-size:56px;color:#ffd98a", "pill2") + painel
    js = (f'camZ("#{p}-cam", 0, {t_quem:.2f}, 1.0, 1.15, {ox}, {oy:.0f}, "power1.inOut");\n'
          f'camZ("#{p}-cam", {t_quem:.2f}, 1.7, 1.15, 2.2, {ox}, {oy:.0f});\n'
          f'camZ("#{p}-cam", {t_quem + 1.7:.2f}, {dur - t_quem - 1.7:.2f}, 2.2, 2.35, {ox}, {oy:.0f}, "none");\n'
          + ft(f"#{p}-pgy", "{y:700,rotation:-6,transformOrigin:'50% 50%'}", "{y:0,rotation:0,transformOrigin:'50% 50%',duration:1.1,ease:'expo.out'}", 0.0)
          + ft(f"#{p}-pgx", "{x:0}", "{x:-28,duration:%.2f,ease:'none'}" % t_quem, 0)
          + realca(p, "k", R_AUT, t_pes, 0.7)
          + f'rise("#{p}-t span", {t_med:.2f});\n'
          + ft(f"#{p}-scan", "{opacity:0}", "{opacity:1,duration:0.2}", t_med)
          + ft(f"#{p}-scan", "{y:420}", "{y:2000,duration:%.2f,ease:'power1.inOut'}" % (t_quem - t_med), t_med)
          + ft(f"#{p}-scan", "{opacity:1}", "{opacity:0,duration:0.3,immediateRender:false}", t_quem - 0.3)
          + some(f"#{p}-t span", t_quem - 0.2)
          + ft(f"#{p}-pgx", "{x:-28}", "{x:%d,duration:1.7,ease:'power3.inOut',immediateRender:false}" % (ox - (X0 + 440 * S)), t_quem)
          + realca(p, "k", R_FRASE, t_menos + 0.1, 0.55, len(R_AUT))
          + ft(f"#{p}-pan", "{opacity:0,x:500}", "{opacity:1,x:0,duration:0.8,ease:'expo.out'}", t_escr - 0.3)
          + f'rise("#{p}-pt span", {t_escr:.2f});\n'
          + ft(f"#{p}-gp", "{opacity:0}", "{opacity:0.7,duration:0.2}", t_men2)
          + ft(f"#{p}-bp", "{height:380}", "{height:310,duration:0.8,ease:'power2.inOut'}", t_men2)
          + ft(f"#{p}-sp", "{opacity:0,y:-30}", "{opacity:1,y:0,duration:0.5,ease:'back.out(2)'}", t_men2 + 0.3)
          + f'rise("#{p}-lp span", {t_pos:.2f});\n'
          + ft(f"#{p}-gn", "{opacity:0}", "{opacity:0.7,duration:0.2}", t_mais)
          + ft(f"#{p}-bn", "{height:300}", "{height:370,duration:0.8,ease:'power2.inOut'}", t_mais)
          + ft(f"#{p}-sn", "{opacity:0,y:30}", "{opacity:1,y:0,duration:0.5,ease:'back.out(2)'}", t_mais + 0.3)
          + f'rise("#{p}-ln span", {t_neg:.2f});\n')
    return composicao(p, dur, svg, html, js, seed=15)


# ---------------------------------------------------------------- 5: o efeito foi pequeno; ninguém perguntou; a política de uso que ninguém lê
def cena5():
    i = 5; p = ID(i); dur = D(i)
    t_peq, t_tam, t_nunca, t_prob, t_nin, t_perg = T(i, "pequeno"), T(i, "tamanho"), T(i, "nunca"), T(i, "problema", 1), T(i, "ninguem"), T(i, "perguntou")
    t_just, t_pol, t_ace, t_cri, t_aq = T(i, "justificativa"), T(i, "politica"), T(i, "aceita"), T(i, "criar"), T(i, "aquele")
    rng = random.Random(8)
    linhas, y = [], 300
    while y < 4400:
        for _ in range(rng.randint(5, 9)):
            linhas.append(f'<rect x="880" y="{y}" width="{rng.randint(560, 740)}" height="12" rx="6" fill="#8a7f68" opacity=".45"/>')
            y += 28
        y += 34
    extra = f'<linearGradient id="{p}-papel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#ece2cc"/></linearGradient>'
    svg = f"""
{chao(960)}
{quadro(p + "-q1", "formatura", 300, 250, .8, -3)}
<g transform="translate(230 960) scale(1.2)">{mesa_laptop(p)}{humano(p + "a", "casa", "sentado", cadeira=True, humor="neutro")}</g>
<g id="{p}-efeito"><g transform="translate(1300 440) scale(1.9)"><g id="{p}-ef">
 <rect x="-120" y="120" width="240" height="8" rx="4" fill="#4a4ab0"/>
 <rect x="-80" y="40" width="60" height="80" rx="8" fill="{MENTA}"/><rect x="20" y="42" width="60" height="78" rx="8" fill="{VERM}"/>
 <g id="{p}-lupa" opacity="0"><circle cx="0" cy="70" r="150" fill="#bff4ff" fill-opacity=".08" stroke="#eef1ff" stroke-width="16" filter="url(#{p}-glow)"/><path d="M106 176 L210 280" stroke="#eef1ff" stroke-width="34" stroke-linecap="round"/></g>
</g></g></g>
<g transform="translate(1260 470)"><g id="{p}-bal" opacity="0">
 <path d="M-300 -170 Q-300 -200 -270 -200 L270 -200 Q300 -200 300 -170 L300 130 Q300 160 270 160 L-150 160 L-260 240 L-210 160 L-270 160 Q-300 160 -300 130 Z" fill="#ffffff" fill-opacity=".05" stroke="#eef1ff" stroke-width="10" stroke-dasharray="34 22" stroke-linejoin="round"/>
 <text x="0" y="80" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="300" fill="#eef1ff" opacity=".55">?</text>
 <line id="{p}-x1" x1="-210" y1="-150" x2="210" y2="120" stroke="{VERM}" stroke-width="28" stroke-linecap="round" stroke-dasharray="500" stroke-dashoffset="500"/>
 <line id="{p}-x2" x1="210" y1="-150" x2="-210" y2="120" stroke="{VERM}" stroke-width="28" stroke-linecap="round" stroke-dasharray="500" stroke-dashoffset="500"/>
</g></g>
<g id="{p}-docX" opacity="0"><g id="{p}-docS">
 <rect x="820" y="120" width="860" height="4400" rx="14" fill="url(#{p}-papel)" filter="url(#{p}-sombra)"/>
 <clipPath id="{p}-hcp"><rect x="840" y="150" width="820" height="90"/></clipPath>
 <g clip-path="url(#{p}-hcp)"><g id="{p}-head"><text x="1250" y="220" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="50" letter-spacing="2" fill="#1a1050">POLÍTICA DE USO DE DADOS</text></g></g>
 <rect id="{p}-hl" x="860" y="166" width="0" height="74" rx="8" fill="#ffd23e" opacity=".5" style="mix-blend-mode:multiply"/>
 {"".join(linhas)}
</g></g>
<g id="{p}-rod"><g transform="translate(0 0)">
 <rect x="790" y="860" width="920" height="170" rx="26" fill="#15133a" stroke="{LILAS}" stroke-width="6" filter="url(#{p}-sombra)"/>
 <rect x="830" y="910" width="74" height="74" rx="12" fill="#0b0a24" stroke="#eef1ff" stroke-width="6"/>
 <path id="{p}-ck" d="M846 948 L864 968 L892 924" fill="none" stroke="{MENTA}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80"/>
 <g transform="translate(1300 947)"><g id="{p}-bt"><rect id="{p}-btr" x="-340" y="-50" width="680" height="100" rx="22" fill="#3b5bff"/>
 <text x="0" y="17" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="46" letter-spacing="4" fill="#ffffff">CRIAR A CONTA</text></g></g>
</g></g>"""
    html = (texto(f"{p}-t1", "PEQUENO", "left:900px;width:800px;text-align:center;top:170px;font-size:64px;color:#ffd98a", "pill2")
            + texto(f"{p}-t2", "Ninguém perguntou", "left:620px;width:1300px;text-align:center;top:60px;font-size:120px;color:#ffffff")
            + texto(f"{p}-t3", "Aquele texto", "left:70px;top:90px;font-size:110px;color:#ffffff")
            + texto(f"{p}-t4", "que ninguém lê", "left:70px;top:220px;font-size:110px;color:#ffd98a"))
    js = (f'camZ("#{p}-cam", 0, {t_aq - 0.2:.2f}, 1.0, 1.05, 960, 540, "none");\n'
          f'camZ("#{p}-cam", {t_aq - 0.2:.2f}, 1.0, 1.05, 0.72, 960, 540);\n'
          + ft(f"#{p}a-olho", "{x:0}", "{x:3,duration:0.5}", 0.2)
          + f'pop("#{p}-ef", 0.05, 0.5, 0.7);\n'
          + ft(f"#{p}-lupa", "{opacity:0,scale:0.4,transformOrigin:'50% 50%'}", "{opacity:1,scale:1,transformOrigin:'50% 50%',duration:0.6,ease:'back.out(2)'}", t_peq - 0.1)
          + f'rise("#{p}-t1 span", {t_peq:.2f});\n'
          + ft(f"#{p}-ef", "{scale:1}", "{scale:0.5,transformOrigin:'50% 50%',duration:0.9,ease:'power2.inOut',immediateRender:false}", t_tam)
          + ft(f"#{p}-efeito", "{opacity:1}", "{opacity:0,duration:0.5,immediateRender:false}", t_nunca + 0.4)
          + some(f"#{p}-t1 span", t_nunca + 0.4)
          + ft(f"#{p}-bal", "{opacity:0,scale:0.6,transformOrigin:'50% 50%'}", "{opacity:1,scale:1,transformOrigin:'50% 50%',duration:0.8,ease:'back.out(1.6)'}", t_prob)
          + ft(f"#{p}-bal", "{y:0}", "{y:-14,duration:0.9,repeat:2,yoyo:true,ease:'sine.inOut',immediateRender:false}", t_prob + 0.8)
          + f'rise("#{p}-t2 span", {t_nin:.2f});\n'
          + ft(f"#{p}-x1", "{attr:{'stroke-dashoffset':500}}", "{attr:{'stroke-dashoffset':0},duration:0.25,ease:'power2.in'}", t_perg)
          + ft(f"#{p}-x2", "{attr:{'stroke-dashoffset':500}}", "{attr:{'stroke-dashoffset':0},duration:0.25,ease:'power2.in'}", t_perg + 0.2)
          + ft(f"#{p}-bal", "{opacity:1}", "{opacity:0,duration:0.4,immediateRender:false}", t_just - 0.2)
          + some(f"#{p}-t2 span", t_just - 0.2)
          + f'entra("#{p}-docX", {t_just - 0.1:.2f}, 0.2);\n'
          + ft(f"#{p}-docX", "{x:1100}", "{x:0,duration:1.0,ease:'expo.out',immediateRender:false}", t_just - 0.1)
          + ft(f"#{p}-head", "{y:90}", "{y:0,duration:0.7,ease:'expo.out'}", t_just + 0.3)
          + ft(f"#{p}-hl", "{attr:{width:0}}", "{attr:{width:780},duration:0.8,ease:'power1.inOut'}", t_pol)
          + ft(f"#{p}-docS", "{y:0}", "{y:-2600,duration:%.2f,ease:'power1.in'}" % (t_aq - t_pol - 0.2), t_pol + 0.9)
          + ft(f"#{p}a-olho", "{x:3}", "{x:-2,duration:0.18,repeat:7,yoyo:true,ease:'sine.inOut',immediateRender:false}", t_pol + 1.4)
          + ft(f"#{p}-rod", "{y:300}", "{y:0,duration:0.7,ease:'expo.out'}", t_ace - 0.8)
          + ft(f"#{p}-ck", "{attr:{'stroke-dashoffset':80}}", "{attr:{'stroke-dashoffset':0},duration:0.3,ease:'power2.out'}", t_ace)
          + ft(f"#{p}-bt", "{scale:1,transformOrigin:'50% 50%'}", "{scale:0.9,transformOrigin:'50% 50%',duration:0.12,repeat:1,yoyo:true}", t_cri)
          + ft(f"#{p}-btr", "{fill:'#3b5bff'}", "{fill:'#1fae80',duration:0.2,immediateRender:false}", t_cri + 0.1)
          + ft(f"#{p}-q1", "{opacity:1}", "{opacity:0,duration:0.4,immediateRender:false}", t_aq - 0.2)
          + f'rise("#{p}-t3 span", {t_aq + 0.55:.2f}); rise("#{p}-t4 span", {t_aq + 0.95:.2f});\n'
          + ft(f"#{p}a-olho", "{scaleY:1,transformOrigin:'50% 50%'}", "{scaleY:0.3,transformOrigin:'50% 50%',duration:0.3,immediateRender:false}", t_aq + 0.6)
          + ft(f"#{p}a-braco", "{y:0}", "{y:7,duration:0.1,repeat:1,yoyo:true,immediateRender:false}", t_cri)
          + humor_js(p + "a", "neutro", "feliz", t_ace - 0.2) + humor_js(p + "a", "feliz", "neutro", t_aq + 0.4)
          + ft(f"#{p}-tl", "{attr:{stroke:'#3be0ff'}}", "{attr:{stroke:'#fffaf0'},duration:0.3}", t_just)
          + vida_gente(p + "a", dur, (2.6, 5.2, 9.0, 12.0)))
    return composicao(p, dur, svg, html, js, extra, seed=17)


# ---------------------------------------------------------------- 6: o estudo saiu em 2014; duas semanas depois, a nota de preocupação
R_CONS = [(128, 667, 646, 28), (105, 694, 669, 28), (105, 721, 255, 28)]


def cena6():
    i = 6; p = ID(i); dur = D(i)
    t_est, t_ano, t_duas, t_rev, t_pub, t_nota, t_preo, t_cons = (
        T(i, "estudo"), T(i, "2014"), T(i, "duas"), T(i, "propria"), T(i, "publicou"), T(i, "nota"), T(i, "preocupacao"), T(i, "consentimento"))
    S2, X2, Y2 = 0.44, 860, 100
    # zoom final 2,9 a 3,0 com a janela visível toda dentro da página B (sem a borda entre A e B no quadro):
    # esquerda visível = ox*(1-1/z) = 840..855 > 814 (borda da folha B após drift); direita < 1524
    ox, oy = 1282, 342   # já descontando o drift de -40 px da página
    dias = "".join(f'<circle id="{p}-d{k}" cx="{1030 + k * 54}" cy="720" r="18" fill="#2a2870" stroke="#4a4ab0" stroke-width="4"/>' for k in range(14))
    svg = f"""<g id="{p}-drift">
<g transform="translate(250 150) rotate(-3)"><g id="{p}-pA"><g transform="scale(.4)">{pagina(p, "kramer2014", "a", [])}<rect id="{p}-veu" x="-14" y="-14" width="1628" height="2170" rx="10" fill="#000" opacity="0"/></g></g></g>
<g id="{p}-cal">{dias}</g>
<g id="{p}-pB" opacity="0"><g transform="translate({X2} {Y2}) scale({S2})">{pagina(p, "pnas_concern", "b", R_CONS)}<rect x="-14" y="-14" width="84" height="2170" fill="#ffffff"/></g>
 <g transform="translate(1330 690) rotate(-9)"><g id="{p}-car" opacity="0">
  <rect x="-440" y="-62" width="880" height="124" rx="14" fill="#fff3f5" fill-opacity=".92" stroke="{VERM}" stroke-width="10"/>
  <text x="0" y="20" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="54" letter-spacing="3" fill="{VERM}">NOTA DE PREOCUPAÇÃO</text></g></g>
</g></g>"""
    html = (texto(f"{p}-ano", "2014", "left:1010px;top:250px;font-size:260px;color:#ffd98a")
            + texto(f"{p}-ds", "DUAS SEMANAS DEPOIS", "left:1000px;top:580px;font-size:52px;color:#bff4ff", "pill2")
            + f'<div id="{p}-faixa" style="position:absolute;left:250px;width:1420px;top:906px;height:118px;background:#0e0c26;border:3px solid #8d7bff;border-radius:28px;box-shadow:0 18px 50px rgba(0,0,0,.55);opacity:0"></div>'
            + texto(f"{p}-cons", "CONSENTIMENTO DOS PARTICIPANTES", "left:0;right:0;text-align:center;top:930px;font-size:60px;color:#ffd98a", "pill2"))
    js = (f'camZ("#{p}-cam", 0, {t_cons:.2f}, 1.0, 1.03, {ox:.0f}, {oy:.0f}, "none");\n'
          f'camZ("#{p}-cam", {t_cons:.2f}, 1.5, 1.03, 2.9, {ox:.0f}, {oy:.0f});\n'
          f'camZ("#{p}-cam", {t_cons + 1.5:.2f}, {dur - t_cons - 1.5:.2f}, 2.9, 3.0, {ox:.0f}, {oy:.0f}, "none");\n'
          + ft(f"#{p}-drift", "{x:0}", "{x:-40,duration:%.2f,ease:'none'}" % t_cons, 0)
          + ft(f"#{p}-pA", "{y:900,rotation:-8,transformOrigin:'50% 50%'}", "{y:0,rotation:0,transformOrigin:'50% 50%',duration:1.0,ease:'expo.out'}", max(0.05, t_est - 0.6))
          + f'rise("#{p}-ano span", {t_ano:.2f}, 0.9);\n'
          + f'rise("#{p}-ds span", {t_duas:.2f});\n'
          + f'tl.set("#{p}-cal",{{opacity:0}},0); entra("#{p}-cal", {t_duas - 0.2:.2f}, 0.3);\n'
          + ft(f"#{p}-cal circle", "{fill:'#2a2870',scale:1,transformOrigin:'50% 50%'}", "{fill:'#ffb23e',scale:1.25,transformOrigin:'50% 50%',duration:0.12,stagger:0.09}", t_duas + 0.1)
          + some(f"#{p}-ano span", t_rev) + some(f"#{p}-ds span", t_rev)
          + ft(f"#{p}-cal", "{opacity:1}", "{opacity:0,duration:0.4,immediateRender:false}", t_rev)
          + ft(f"#{p}-veu", "{opacity:0}", "{opacity:0.4,duration:0.6}", t_pub)
          # a página do estudo sai antes do zoom: sem ela atrás da nota não sobra emenda roxa na borda esquerda
          + ft(f"#{p}-pA", "{opacity:1}", "{opacity:0,duration:0.5,immediateRender:false}", t_cons - 0.6)
          + f'entra("#{p}-pB", {t_rev + 0.1:.2f}, 0.2);\n'
          + ft(f"#{p}-pB", "{x:1100,rotation:6,svgOrigin:'1200 600'}", "{x:0,rotation:0,svgOrigin:'1200 600',duration:1.1,ease:'expo.out',immediateRender:false}", t_rev + 0.1)
          + ft(f"#{p}-car", "{opacity:0,scale:2.6,transformOrigin:'50% 50%'}", "{opacity:1,scale:1,transformOrigin:'50% 50%',duration:0.28,ease:'power4.in'}", t_nota)
          + ft(f"#{p}-pB", "{y:0}", "{y:10,duration:0.08,repeat:1,yoyo:true,immediateRender:false}", t_nota + 0.28)
          + ft(f"#{p}-car", "{opacity:1}", "{opacity:0,duration:0.4,immediateRender:false}", t_cons)
          + realca(p, "b", R_CONS, t_cons + 0.4, 0.5)
          + ft(f"#{p}-faixa", "{opacity:0}", "{opacity:1,duration:0.6}", t_cons)
          + f'rise("#{p}-cons span", {t_cons + 0.1:.2f});\n')
    return composicao(p, dur, svg, html, js, seed=19)


# ---------------------------------------------------------------- 7: nenhum chip, nenhuma luz no cérebro; só alguém que controlava a tela
def cena7():
    i = 7; p = ID(i); dur = D(i)
    # os tempos do whisper adiantam ~1,4 s no início deste segmento ("Repare" e "nenhum" caíram no anterior): começo fixado à mão
    t_chip, t_luz, t_cer = 1.0, 2.1, 2.94
    t_so, t_cont, t_voce, t_via, t_med, t_reag = T(i, "so"), T(i, "controlava"), T(i, "voce"), T(i, "via"), T(i, "media"), T(i, "reagia")
    PX, PY, PS = -166, 176, 2.6
    mon = (f'<g filter="url(#{p}-sombra)"><rect x="1110" y="290" width="420" height="310" rx="24" fill="#15133a" stroke="{LILAS}" stroke-width="8"/>'
           f'<rect x="1290" y="600" width="60" height="70" fill="#2a2870"/><rect x="1220" y="664" width="200" height="22" rx="11" fill="#2a2870"/></g>'
           f'<rect x="1130" y="310" width="380" height="270" rx="12" fill="#0b1c40"/>'
           + "".join(f'<rect id="{p}-mc{k}" x="1146" y="{326 + k * 52}" width="128" height="40" rx="8" fill="{c}"/>' for k, c in enumerate(["#7b2a6c", "#25427a", "#6b5b2a"]))
           + "".join(f'<rect x="1296" y="{340 + k * 46}" width="196" height="8" rx="4" fill="#4a4ab0"/><circle id="{p}-k{k}" cx="{1330 + k * 50}" cy="{344 + k * 46}" r="13" fill="{c}"/>' for k, c in enumerate([AMBAR, CIANO, MAGENTA]))
           + f'<path id="{p}-graf" d="M1150 560 L1190 548 L1220 556 L1250 520 L1280 534 L1310 500 L1340 516 L1370 478 L1400 492 L1430 462 L1490 470" fill="none" stroke="{MENTA}" stroke-width="6" stroke-linejoin="round" stroke-dasharray="420" stroke-dashoffset="420" filter="url(#{p}-glow)"/>')
    rng = random.Random(9)
    predios, xx = "", -60
    while xx < 700:
        bw, bh = rng.randint(90, 160), rng.randint(260, 560)
        predios += f'<rect x="{xx}" y="{950 - bh}" width="{bw}" height="{bh}" fill="{rng.choice(["#24205e", "#2c2470", "#1e1a52"])}"/>'
        predios += "".join(f'<rect x="{xx + 16 + c * 30}" y="{950 - bh + 24 + r * 40}" width="14" height="18" fill="#ffd27a" opacity="{rng.choice([.15, .5, .85])}"/>'
                           for r in range(bh // 40 - 1) for c in range((bw - 24) // 30))
        xx += bw + rng.randint(10, 30)
    # pessoa de pé com o celular (mão no peito) e o celular grande ao lado como lupa do que ela vê
    GX, GS = 330, 1.22
    fone_x, fone_y = GX + 112.7 * GS, 950 - 382.6 * GS
    # o senhor na mesa, virado para a esquerda (para o monitor), atrás do tampo
    OX, OS = 1730, 1.3
    PELE_O, CAMISA_O = OPERADOR[PELE], OPERADOR[TRAB["torso"]]
    persiana = "".join(f'<rect x="1560" y="{292 + k * 22}" width="250" height="12" rx="3" fill="#8d7bff" opacity=".22"/>' for k in range(7))
    mao_t = lambda x, y, n: (f'<g transform="translate({x} {y})"><g id="{p}-mt{n}"><rect x="2" y="-9" width="26" height="15" rx="6" fill="{CAMISA_O}"/>'
                              f'<path d="M -14,0 C -14,-8 -2,-11 8,-8 L 8,5 C -2,7 -14,6 -14,0 Z" fill="{PELE_O}"/>'
                              f'<path d="M -12,2 L -4,3 M -11,-3 L -4,-3" stroke="#140a2e" stroke-opacity=".3" stroke-width="1.4" stroke-linecap="round"/></g></g>')
    svg = f"""
<g id="{p}-rua" opacity="0">
 {chao(950)}
 <g opacity=".85">{predios}</g>
 <g transform="translate(150 950)"><rect x="-8" y="-720" width="16" height="720" fill="#3a3a6a"/><path d="M 0 -716 Q 50 -756 104 -724" stroke="#3a3a6a" stroke-width="14" fill="none"/>
  <ellipse cx="108" cy="-712" rx="28" ry="12" fill="#ffd27a"/><polygon points="88,-706 128,-706 320,-30 -100,-30" fill="#ffd27a" opacity=".07"/>
  <ellipse cx="108" cy="-520" rx="160" ry="260" fill="#ffd27a" opacity=".1" filter="url(#{p}-blur40)"/></g>
 <ellipse cx="{GX + 20}" cy="952" rx="190" ry="16" fill="#ffd27a" opacity=".08"/>
 <g transform="translate({GX} 950) scale({GS})">{humano(p + "g", "casa", "em_pe", cel=True)}</g>
 <polygon points="{fone_x + 8:.0f},{fone_y - 10:.0f} 700,262 700,738 {fone_x + 8:.0f},{fone_y + 12:.0f}" fill="#3be0ff" opacity=".07"/>
 <path d="M {fone_x + 8:.0f} {fone_y - 10:.0f} L 700 262 M {fone_x + 8:.0f} {fone_y + 12:.0f} L 700 738" stroke="#3be0ff" stroke-width="2" stroke-dasharray="6 8" opacity=".45"/>
</g>
<g id="{p}-escr" opacity="0">
 <rect x="1040" y="230" width="1000" height="720" rx="34" fill="#1b1450" opacity=".9"/>
 <rect x="1040" y="230" width="1000" height="720" rx="34" fill="none" stroke="#4a3aa0" stroke-width="4" opacity=".7"/>
 <rect x="1546" y="278" width="278" height="170" rx="10" fill="#0e1240" stroke="#4a3aa0" stroke-width="6"/>{persiana}
 <ellipse cx="1330" cy="500" rx="330" ry="250" fill="#3be0ff" opacity=".08" filter="url(#{p}-blur40)"/>
 <g transform="translate({OX} 950) scale({-OS} {OS})">{humano(p + "o", "trabalho", "sentado", cores=OPERADOR, cadeira=True, humor="neutro", oculos=True, luz=True, olhar=(2.6, 1.2, 1.5))}</g>
 <path d="M 1052 712 L 1960 712 L 1960 744 L 1040 744 Z" fill="#5a46b0"/>
 <rect x="1040" y="744" width="920" height="18" fill="#3a2a8c"/>
 <rect x="1430" y="762" width="520" height="188" fill="#2a1d70"/>
 <rect x="1462" y="786" width="190" height="64" rx="8" fill="none" stroke="#4a3aa0" stroke-width="4"/><rect x="1462" y="866" width="190" height="64" rx="8" fill="none" stroke="#4a3aa0" stroke-width="4"/>
 <rect x="1532" y="812" width="50" height="10" rx="5" fill="#8d7bff" opacity=".6"/><rect x="1532" y="892" width="50" height="10" rx="5" fill="#8d7bff" opacity=".6"/>
 <rect x="1070" y="762" width="24" height="188" fill="#2a1d70"/>
 <ellipse cx="1470" cy="955" rx="460" ry="20" fill="#05031a" opacity=".5"/>
 <g transform="translate(-20 34)">{mon}</g>
 <ellipse cx="1660" cy="722" rx="140" ry="14" fill="#3be0ff" opacity=".12"/>
 <path d="M 1590 732 L 1766 732 L 1754 710 L 1602 710 Z" fill="#232060" stroke="#8d7bff" stroke-width="2.5" stroke-linejoin="round"/>
 <path d="M 1606 716 L 1750 716 M 1600 722 L 1756 722 M 1596 727 L 1760 727" stroke="#8d7bff" stroke-width="2.4" stroke-dasharray="7 4" opacity=".8"/>
 <g transform="translate(1520 714)"><path d="M -60 0 L -6 0 L -2 -8 L -56 -8 Z" fill="#eef1ff" opacity=".9"/><path d="M -58 -8 L -4 -8 L 0 -14 L -54 -14 Z" fill="#c9d0ea"/></g>
 <g transform="translate(1562 714)"><path d="M -16 0 L -14 -34 Q 0 -40 14 -34 L 16 0 Z" fill="#ff7a8a"/><path d="M 14 -28 q 14 2 10 16 q -2 6 -11 5" stroke="#ff7a8a" stroke-width="5" fill="none"/>
  <path d="M -4 -44 q -6 -10 0 -18 M 6 -44 q -6 -10 0 -18" stroke="#eef1ff" stroke-width="3" fill="none" opacity=".5"/></g>
 {mao_t(1640, 716, 0)}{mao_t(1708, 718, 1)}
 <path id="{p}-cabo" d="M1090 500 C 1030 500 1010 520 950 520" fill="none" stroke="{AMBAR}" stroke-width="8" stroke-linecap="round" stroke-dasharray="18 14" filter="url(#{p}-glow)"/>
 <path d="M{fone_x:.0f} {fone_y - 40:.0f} C 600 90 1100 80 1300 352" fill="none" stroke="{MAGENTA}" stroke-width="4" stroke-dasharray="10 12" opacity=".35"/>
 <path id="{p}-volta" d="M{fone_x:.0f} {fone_y - 40:.0f} C 600 90 1100 80 1300 352" fill="none" stroke="{MAGENTA}" stroke-width="8" stroke-linecap="round" stroke-dasharray="560 1200" stroke-dashoffset="560" opacity="0" filter="url(#{p}-glow)"/>
</g>
<g id="{p}-cab1">
{pessoa(p + "a", PX, PY, PS, glow=p + "-glow")}
<g transform="translate({PX} {PY}) scale({PS})">
 <g id="{p}-chip" opacity="0"><rect x="186" y="18" width="30" height="18" rx="4" fill="{AMBAR}" filter="url(#{p}-glow)" transform="rotate(-10 201 27)"/>
  <path d="M196 18 C 196 -10 220 -20 236 -40" fill="none" stroke="{AMBAR}" stroke-width="2.5"/>
  <path id="{p}-cx" d="M178 4 L226 48 M226 4 L178 48" stroke="{VERM}" stroke-width="6" stroke-linecap="round" stroke-dasharray="140" stroke-dashoffset="140"/></g>
 <g id="{p}-luz" opacity="0"><path d="M150 -90 C 150 -20 170 30 178 74" fill="none" stroke="#7fb4ff" stroke-width="4" stroke-linecap="round"/>
  <circle id="{p}-luzp" cx="178" cy="78" r="16" fill="#3b8bff" opacity=".8" filter="url(#{p}-glow)"/>
  <path id="{p}-lx" d="M154 54 L202 102 M202 54 L154 102" stroke="{VERM}" stroke-width="6" stroke-linecap="round" stroke-dasharray="140" stroke-dashoffset="140"/></g>
</g></g>
<g transform="translate(820 500) scale(.62)"><g id="{p}-cel" opacity="0">{celular(p, "f", ["feliz", "neutro", "triste", "feliz", "neutro", "triste", "feliz", "neutro"], extra=TROCA.format(p=p))}</g></g>"""
    html = (texto(f"{p}-t1", "Nenhum chip", "left:860px;top:250px;font-size:120px;color:#ffd98a")
            + texto(f"{p}-t2", "Nenhuma luz no cérebro", "left:840px;top:420px;font-size:92px;color:#bfd8ff")
            + texto(f"{p}-t3", "SÓ ALGUÉM", "left:1060px;width:860px;text-align:center;top:110px;font-size:64px;color:#ffd98a", "pill2"))
    js = (f'camZ("#{p}-cam", 0, {t_so:.2f}, 1.3, 1.34, 280, 540, "none");\n'
          f'camZ("#{p}-cam", {t_so:.2f}, 1.4, 1.34, 1.0, 280, 540);\n'
          f'camZ("#{p}-cam", {t_so + 1.4:.2f}, {dur - t_so - 1.4:.2f}, 1.0, 1.02, 280, 540, "none");\n'
          + ft(f"#{p}a-olho", "{x:0}", "{x:3,duration:0.4}", 0.1)
          + f'entra("#{p}-chip", {t_chip - 0.3:.2f}, 0.25); rise("#{p}-t1 span", {t_chip - 0.3:.2f});\n'
          + ft(f"#{p}-cx", "{attr:{'stroke-dashoffset':140}}", "{attr:{'stroke-dashoffset':0},duration:0.3}", t_chip + 0.3)
          + ft(f"#{p}-chip", "{opacity:1}", "{opacity:0,duration:0.4,immediateRender:false}", t_luz - 0.3)
          + f'entra("#{p}-luz", {t_luz - 0.2:.2f}, 0.25); rise("#{p}-t2 span", {t_luz - 0.2:.2f});\n'
          + ft(f"#{p}-luzp", "{scale:1,transformOrigin:'50% 50%'}", "{scale:1.6,transformOrigin:'50% 50%',duration:0.2,repeat:3,yoyo:true}", t_luz)
          + ft(f"#{p}-lx", "{attr:{'stroke-dashoffset':140}}", "{attr:{'stroke-dashoffset':0},duration:0.3}", t_cer)
          + ft(f"#{p}-luz", "{opacity:1}", "{opacity:0,duration:0.4,immediateRender:false}", t_so - 0.3)
          + some(f"#{p}-t1 span", t_so - 0.3) + some(f"#{p}-t2 span", t_so - 0.3)
          + ft(f"#{p}-cab1", "{x:0,opacity:1}", "{x:-500,opacity:0,duration:0.7,ease:'power2.in',immediateRender:false}", t_so - 0.1)
          + f'entra("#{p}-rua", {t_so + 0.2:.2f}, 0.5);\n'
          + ft(f"#{p}-rua", "{x:-300}", "{x:0,duration:1.1,ease:'expo.out',immediateRender:false}", t_so + 0.2)
          + f'entra("#{p}-escr", {t_so:.2f}, 0.2);\n'
          + ft(f"#{p}-escr", "{x:600}", "{x:0,duration:0.8,ease:'expo.out',immediateRender:false}", t_so)
          + f'entra("#{p}-cel", {t_so + 0.2:.2f}, 0.2);\n'
          + ft(f"#{p}-cel", "{y:700}", "{y:0,duration:1.0,ease:'back.out(1.3)',immediateRender:false}", t_so + 0.2)
          + f'rise("#{p}-t3 span", {T(i, "alguem"):.2f});\n'
          + "".join(ft(f"#{p}-k{k}", "{x:0}", "{x:%d,duration:0.6,repeat:3,yoyo:true,ease:'sine.inOut'}" % (90 - k * 70), t_cont + k * 0.15) for k in range(3))
          + "".join(ft(f"#{p}-mt{n}", "{y:0}", "{y:-4,duration:0.14,repeat:%d,yoyo:true,ease:'sine.inOut'}" % (13 - n * 2), t_cont - 0.2 + n * 0.07) for n in range(2))
          + humor_js(p + "o", "neutro", "feliz", t_med + 0.5, 0.35)
          + ft(f"#{p}-cabo", "{attr:{'stroke-dashoffset':0}}", "{attr:{'stroke-dashoffset':128},duration:0.5,repeat:%d,ease:'none'}" % int((dur - t_cont) / 0.5 - 1), t_cont)
          + f'tl.set("#{p}-troca",{{x:380}},0);\n'
          + ft(f"#{p}-fc0", "{x:0}", "{x:-380,duration:0.4,ease:'power2.in'}", t_voce)
          + ft(f"#{p}-troca", "{x:380}", "{x:0,duration:0.5,ease:'back.out(1.4)',immediateRender:false}", t_voce + 0.25)
          + ft(f"#{p}-mc0", "{fill:'#7b2a6c'}", "{fill:'#25427a',duration:0.2,immediateRender:false}", t_voce + 0.25)
          + ft(f"#{p}-fposts", "{y:0}", "{y:-380,duration:%.2f,ease:'power1.inOut'}" % (dur - t_via), t_via)
          + ft(f"#{p}-graf", "{attr:{'stroke-dashoffset':420}}", "{attr:{'stroke-dashoffset':0},duration:1.4,ease:'power1.inOut'}", t_med)
          + f'entra("#{p}-volta", {t_med - 0.2:.2f}, 0.1);\n'
          + ft(f"#{p}-volta", "{attr:{'stroke-dashoffset':560}}", "{attr:{'stroke-dashoffset':-1200},duration:1.1,repeat:1,ease:'none'}", t_med - 0.2)
          + olhar_cel(p + "g") + f'tl.to("#{p}g-tela",{{attr:{{fill:"#7fb4ff"}},duration:0.2}},{t_voce + 0.3:.2f});\n'
          + humor_js(p + "g", "feliz", "triste", t_voce + 0.5, 0.35)
          + ft(f"#{p}g-luzc", "{opacity:0.22}", "{opacity:0.45,duration:0.25,repeat:3,yoyo:true,immediateRender:false}", t_reag - 0.3)
          + vida_pessoa(p + "a", dur, (0.6, 3.6)) + vida_gente(p + "g", dur, (6.0, 8.8)) + vida_gente(p + "o", dur, (6.6, 9.4)))
    return composicao(p, dur, svg, html, js, seed=23)


# ---------------------------------------------------------------- 8: quem controla a tela escolhe o mundo que chega até ela
def cena8():
    i = 8; p = ID(i); dur = D(i)
    t_cont, t_nao, t_cab, t_ele, t_esc, t_mun, t_che = T(i, "controla"), T(i, "nao"), T(i, "cabeca"), T(i, "ele"), T(i, "escolhe"), T(i, "mundo"), T(i, "chega")
    GX, GY, GS = 250, 860, 1.15            # pessoa sentada na poltrona (pés em GY)
    EX, EY = GX + 14 * GS, GY - 385 * GS    # olho (o da frente, gente casa sentado giro 30)
    HX, HY = GX + ANCORAS[("casa", "sentado", 30)]["cabeca_centro"][0] * GS, GY + ANCORAS[("casa", "sentado", 30)]["cabeca_centro"][1] * GS
    tipos = ["feliz", "triste", "neutro", "triste", "feliz", "neutro", "neutro", "feliz", "triste"]
    novos = ["neutro", "feliz", "triste", "feliz", "triste", "feliz", "triste", "neutro", "feliz"]
    esc = (1, 4, 8)
    grade = "".join(f'<g transform="translate({1000 + (k % 3) * 300} {196 + (k // 3) * 186}) scale(.9)"><g id="{p}-g{k}">{cartao(t, k)}</g>'
                    f'<g id="{p}-n{k}" opacity="0">{cartao(novos[k], k + 1)}</g></g>' for k, t in enumerate(tipos))
    voa = "".join(f'<g transform="translate({1000 + (k % 3) * 300} {273 + (k // 3) * 186})"><g id="{p}-v{n}" opacity="0"><g transform="scale(.5) translate(0 -85)">{cartao(novos[k], k + 1)}</g></g></g>'
                  for n, k in enumerate(esc))
    extra = (f'<linearGradient id="{p}-tela" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16143a"/><stop offset="1" stop-color="#0b1c40"/></linearGradient>'
             f'<linearGradient id="{p}-feixe" gradientUnits="userSpaceOnUse" x1="{EX:.0f}" y1="0" x2="790" y2="0"><stop offset="0" stop-color="#3be0ff" stop-opacity=".5"/><stop offset="1" stop-color="#3be0ff" stop-opacity=".08"/></linearGradient>')
    svg = f"""
<ellipse id="{p}-bloom" cx="1300" cy="470" rx="640" ry="420" fill="#3be0ff" opacity="0" filter="url(#{p}-blur40)"/>
<polygon id="{p}-raio" points="{EX + 14:.0f},{EY:.0f} 790,190 790,760" fill="url(#{p}-feixe)" opacity="0"/>
<g filter="url(#{p}-sombra)"><rect x="760" y="150" width="1080" height="640" rx="30" fill="#15133a" stroke="{LILAS}" stroke-width="10"/></g>
<rect x="786" y="176" width="1028" height="588" rx="16" fill="url(#{p}-tela)"/>
<clipPath id="{p}-tcp"><rect x="786" y="176" width="1028" height="588" rx="16"/></clipPath>
<g clip-path="url(#{p}-tcp)"><g id="{p}-grade" opacity="0">{grade}</g><rect id="{p}-flash" x="786" y="176" width="1028" height="588" fill="#eef1ff" opacity="0"/>
 <g transform="translate(1300 320)"><g id="{p}-cur" opacity="0"><g transform="scale(1.6)"><path d="M0 0 L0 54 L16 40 L28 66 L40 60 L28 36 L50 36 Z" fill="#ffffff" stroke="#1a0f3a" stroke-width="3"/></g></g></g></g>
<rect x="1240" y="790" width="120" height="60" fill="#2a2870"/>
{chao(860, .45)}
<ellipse cx="330" cy="866" rx="300" ry="26" fill="#3a2a8c" opacity=".7"/>
<circle id="{p}-anel" cx="{HX:.0f}" cy="{HY - 8:.0f}" r="96" fill="none" stroke="{CIANO}" stroke-width="6" stroke-dasharray="16 14" opacity="0" filter="url(#{p}-glow)"/>
<g transform="translate({GX} {GY}) scale({GS})">{poltrona()}{humano(p + "a", "casa", "sentado", humor="neutro")}</g>
{voa}"""
    html = (texto(f"{p}-t1", "Quem controla a tela", "left:0;right:0;text-align:center;top:850px;font-size:96px;color:#ffffff")
            + texto(f"{p}-t2", "não precisa entrar na sua cabeça", "left:0;right:0;text-align:center;top:960px;font-size:72px;color:#bff4ff")
            + texto(f"{p}-t3", "Ele escolhe o mundo", "left:0;right:0;text-align:center;top:850px;font-size:96px;color:#ffd98a")
            + texto(f"{p}-t4", "que chega até ela", "left:0;right:0;text-align:center;top:960px;font-size:84px;color:#ffffff"))
    cur_js = (f'tl.set("#{p}-cur",{{x:0,y:0}},0);\n'
              + f'entra("#{p}-cur", {t_esc - 0.3:.2f}, 0.2);\n'
              + "".join(f'tl.to("#{p}-cur",{{x:{(k % 3) * 300 - 300 + 40},y:{(k // 3) * 186 - 124 + 60},duration:0.32,ease:"power2.inOut"}},{t_esc - 0.2 + n * 0.42:.2f});\n'
                        + ft(f"#{p}-n{k}", "{opacity:0,scale:1.15,transformOrigin:'50% 50%'}", "{opacity:1,scale:1,transformOrigin:'50% 50%',duration:0.3,ease:'back.out(2)'}", t_esc + 0.12 + n * 0.42)
                        for n, k in enumerate(esc)))
    outros = ",".join(f'"#{p}-g{k}"' for k in range(9) if k not in esc)
    js = (f'camZ("#{p}-cam", 0, {t_cab - 0.4:.2f}, 1.0, 1.02, {EX:.0f}, {EY:.0f}, "none");\n'
          f'camZ("#{p}-cam", {t_cab - 0.4:.2f}, 0.9, 1.02, 1.035, {EX:.0f}, {EY:.0f});\n'
          f'camZ("#{p}-cam", {t_ele:.2f}, 1.3, 1.035, 1.0, {EX:.0f}, {EY:.0f});\n'
          f'camZ("#{p}-cam", {t_ele + 1.3:.2f}, {dur - t_ele - 1.3:.2f}, 1.0, 1.05, {EX:.0f}, {EY:.0f}, "none");\n'
          + ft(f"#{p}a-olho", "{x:0}", "{x:3,duration:0.4}", 0.1)
          + f'rise("#{p}-t1 span", {t_cont - 0.2:.2f});\n'
          + ft(f"#{p}-flash", "{opacity:0}", "{opacity:0.7,duration:0.08}", t_cont + 0.5)
          + ft(f"#{p}-flash", "{opacity:0.7}", "{opacity:0,duration:0.5,immediateRender:false}", t_cont + 0.6)
          + ft(f"#{p}-grade", "{opacity:0}", "{opacity:1,duration:0.2}", t_cont + 0.55)
          + ft(f"#{p}-bloom", "{opacity:0}", "{opacity:0.2,duration:0.8}", t_cont + 0.55)
          + ft(f"#{p}-grade", "{y:0}", "{y:-20,duration:%.2f,ease:'none'}" % (dur - t_cont), t_cont)
          + f'rise("#{p}-t2 span", {t_nao:.2f});\n'
          + ft(f"#{p}-anel", "{opacity:0,scale:1.3,transformOrigin:'50% 50%'}", "{opacity:0.9,scale:1,transformOrigin:'50% 50%',duration:0.5,ease:'back.out(2)'}", t_cab - 0.4)
          + ft(f"#{p}-anel", "{rotation:0,transformOrigin:'50% 50%'}", "{rotation:40,transformOrigin:'50% 50%',duration:1.4,ease:'none',immediateRender:false}", t_cab - 0.4)
          + ft(f"#{p}-anel", "{opacity:0.9}", "{opacity:0,duration:0.4,immediateRender:false}", t_ele - 0.2)
          + some(f"#{p}-t1 span", t_ele - 0.25) + some(f"#{p}-t2 span", t_ele - 0.25)
          + f'rise("#{p}-t3 span", {t_ele:.2f});\n'
          + cur_js
          + f'tl.to([{outros}],{{opacity:0.25,duration:0.5}},{t_mun - 0.2:.2f});\n'
          + f'rise("#{p}-t4 span", {T(i, "que"):.2f});\n'
          + ft(f"#{p}-raio", "{opacity:0}", "{opacity:1,duration:0.6}", t_che - 0.3)
          + "".join(ft(f"#{p}-v{n}", "{x:0,y:0,scale:1,opacity:1}",
                       "{x:%.0f,y:%.0f,scale:0.15,opacity:0,duration:0.95,repeat:1,repeatDelay:0.2,ease:'power2.in',immediateRender:false}" % (EX - (1000 + (k % 3) * 300), EY - (273 + (k // 3) * 186)),
                       t_che - 0.2 + n * 0.25)
                    for n, k in enumerate(esc))
          + humor_js(p + "a", "neutro", "feliz", t_che + 0.7)
          + vida_gente(p + "a", dur, (2.0, 4.6, 7.4)))
    return composicao(p, dur, svg, html, js, extra, seed=29)


FUNCS = [cena0, cena1, cena2, cena3, cena4, cena5, cena6, cena7, cena8]
CENAS = [(ID(k), f, D(k)) for k, f in enumerate(FUNCS)]
MAPA = {(CE, k): ID(k) for k in range(len(FUNCS))}

if __name__ == "__main__":
    print(escreve_cenas(CENAS, AQUI))
