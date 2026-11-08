"""Gera index.html e compositions/*.html a partir de roteiro.py, num dos três estilos.

  python build.py doc     imagens reais (fotos livres e páginas dos artigos) + ilustração
  python build.py 3d      cenas 3D (assets/r3.js) no lugar das ilustrações conceituais
  python build.py misto   os dois juntos + trechos dos trailers de Ruptura e Matrix

Os tempos vêm de assets/voz/duracoes.json (tts.py escolher); sem ele, estima pela fala.
Cada segmento declara um assunto ("a"); o estilo escolhe o renderizador.
"""
import json, os, random, sys
from roteiro import CENAS

ESTILO = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "misto"
V3 = "--v3" in sys.argv  # troca segmentos pelas cenas novas (cenas-v3), cortadas em assets/cenas3/
assert ESTILO in ("doc", "3d", "misto"), ESTILO
W, H = 1920, 1080
AQUI = os.path.dirname(os.path.abspath(__file__))
DUR_JSON = os.path.join(AQUI, "assets/voz/duracoes.json")
MUSICA = "assets/musica.mp3"
XF = 0.45  # crossfade entre segmentos (s)

ESCURO, TINTA, APOIO = "#0b0d12", "#eef1f7", "#8a93a8"
PAPEL, NANQUIM, VERMELHO = "#efe8da", "#1b1b1b", "#8e1b1b"
CIANO, AMBAR, LILAS = "#5ad1c6", "#f2b84b", "#a78bfa"
ROTULO = {"ficcao": ("FICÇÃO", AMBAR), "pesquisa": ("PESQUISA", CIANO), "caso": ("CASO REAL", CIANO),
          "argumento": ("ARGUMENTO", LILAS), "ilustracao": ("ILUSTRAÇÃO", APOIO)}
CRED = {
    "camundongo": "Foto: Rama · CC BY-SA 2.0 FR", "mosca": "Foto: Alexis / iNaturalist · CC BY 4.0",
    "flywire": "FlyWire · Dorkenwald e outros, Nature 2024 · CC BY 4.0", "ressonancia": "Asnaebsa · CC BY-SA 4.0",
    "bostrom": "Future of Humanity Institute · CC BY 4.0", "owen": "Martin R. Coleman · CC BY-SA 4.0",
    "neuronios": "NIH · domínio público", "aparelho_rm": "Jan Ainali · CC BY 3.0",
    "servidores": "BalticServers.com · CC BY-SA 3.0",
}
RETRATO = {"owen2006": ("owen", "Adrian Owen"), "bostrom2003": ("bostrom", "Nick Bostrom")}
TRAILER = {
    "ruptura": ("assets/trailers/severance_h264.mp4", [(24, 3.2), (39.5, 2.6), (33.5, 3), (147, 3.4), (9, 3), (63, 2.5)],
                "Ruptura (Severance) · Apple TV+ · trailer oficial"),
    "matrix": ("assets/trailers/matrix_h264.mp4", [(84, 3.4), (72, 3), (18.5, 2.6), (114, 3), (135, 3), (42, 3)],
               "Matrix (The Matrix) · Warner Bros. · trailer"),
}


def tempos():
    """{cena: [(inicio, duracao), ...]} em segundos locais da cena."""
    if os.path.exists(DUR_JSON):
        return {k: [tuple(x) for x in v] for k, v in json.load(open(DUR_JSON)).items()}
    out = {}
    for cena, _, segs in CENAS:
        t, lst = 0.0, []
        for texto, pausa, _ in segs:
            d = len(texto.split()) / 2.3 + 0.3
            lst.append((t, d + pausa))
            t += d + pausa
        out[cena] = lst
    return out


# ---------------------------------------------------------------- ajudantes
# Cada visual devolve (html, tweens). {t0} e {d} viram o início e a duração do
# segmento; ids levam o prefixo p do segmento.

def palavras(txt, cls="pal"):
    return " ".join(f'<span class="{cls}">{w}</span>' for w in txt.split())


def entra(sel, quando, passo=0.07):
    return f'tl.fromTo("{sel} .pal",{{opacity:0,y:18,filter:"blur(8px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.35,stagger:{passo},ease:"power2.out"}},{quando});'


def surge(sel, quando, dur=0.5, de="opacity:0,y:30", ease="expo.out"):
    para = ",".join(f"{k.split(':')[0]}:{'1' if k.startswith(('opacity', 'scale')) else '0'}" for k in de.split(","))
    return f'tl.fromTo("{sel}",{{{de}}},{{{para},duration:{dur},ease:"{ease}"}},{quando});'


def tam_frase(txt):
    n = len(txt)
    return "frase-g" if n <= 22 else ("frase" if n <= 60 else "frase frase-p")


def fundo_3d(p, cena, opts, extra=""):
    html = f'<div class="seg preto"><canvas id="{p}-cv" class="cheio" width="1920" height="1080"></canvas>{extra}</div>'
    tw = [f'(function(){{var o={{t:0}},cv=document.querySelector("#{p}-cv");tl.fromTo(o,{{t:0}},{{t:{{d}}+{XF},duration:{{d}}+{XF},ease:"none",'
          f'onUpdate:function(){{R3.draw(cv,"{cena}",o.t,{{d}},{json.dumps(opts)});}}}},{{t0}});}})();']
    return html, tw


def foto(p, img, extra="", z=(1.04, 1.16), filtro="", pos="50% 50%", ext="jpg"):
    html = (f'<div class="seg preto"><img id="{p}-kb" class="kb" src="assets/img/{img}.{ext}" style="object-position:{pos};filter:{filtro}">'
            f'<div class="sombra-b"></div>{extra}<div class="credito">{CRED.get(img, "")}</div></div>')
    tw = [f'tl.fromTo("#{p}-kb",{{scale:{z[0]}}},{{scale:{z[1]},duration:{{d}}+{XF},ease:"none"}},{{t0}});']
    return html, tw


SUBST = {  # (cena, índice do segmento) -> cena nova; ms = início no clipe; ext = continua no segmento seguinte
    ("mapear", 1): dict(a="cena3", clip="A", ms=0, ext=True), ("mapear", 2): dict(a="cena3", clip="A", ms=11.66, ext=False),
    ("mapear", 5): dict(a="cena3", clip="B", ms=0, ext=False),
    ("ler", 2): dict(a="cena3", clip="D", ms=0, ext=False), ("ler", 7): dict(a="cena3", clip="E", ms=0, ext=False),
    ("ler", 12): dict(a="cena3", clip="F", ms=0, ext=False),
    ("abertura", 0): dict(a="cena3", clip="M1", ms=0, ext=True), ("abertura", 1): dict(a="cena3", clip="M1", ms=10.99, ext=False),
    ("abertura", 2): dict(a="cena3", clip="M2", ms=0, ext=False), ("abertura", 3): dict(a="cena3", clip="M3", ms=0, ext=False),
    ("escrever", 1): dict(a="cena3", clip="M4", ms=0, ext=False), ("escrever", 3): dict(a="cena3", clip="M5", ms=0, ext=False),
    ("escrever", 4): dict(a="cena3", clip="M6", ms=0, ext=False), ("escrever", 6): dict(a="cena3", clip="M7", ms=0, ext=False),
    ("fechamento", 7): dict(a="cena3", clip="M8", ms=0, ext=False),
    ("realidade", 0): dict(a="cena3", clip="C", ms=0, ext=False),
    ("realidade", 5): dict(a="cena3", clip="C", ms=7.45, ext=True), ("realidade", 6): dict(a="cena3", clip="C", ms=19.75, ext=False),
}


_MAPA5 = os.path.join(AQUI, "assets/cenas3/mapa_v5.json")
if os.path.exists(_MAPA5):  # cenas v5 (uma por segmento), cortadas por cenas-v5/montar.py
    for _c, _d in json.load(open(_MAPA5)).items():
        for _i, _id in _d.items():
            if os.path.exists(os.path.join(AQUI, f"assets/cenas3/{_id}.mp4")):
                SUBST[(_c, int(_i))] = dict(a="cena3", clip=_id, ms=0, ext=False)


def v_cena3(p, s):
    """Cena nova (vídeo sem áudio). O <video> fica solto na raiz da cena, como os trailers."""
    d = s["_d"] + (XF if s["ext"] else 0)
    s["_soltos"].append(f'<video id="{p}-c3" class="clip vid" src="assets/cenas3/{s["clip"]}.mp4" muted data-start="{s["_t0"]:.2f}" data-duration="{d:.2f}" data-media-start="{s["ms"]}"></video>')
    return '<div class="seg"></div>', []


def video(p, s, chave):
    """Trechos do trailer em sequência. Os <video> ficam soltos na raiz da cena
    (s["_soltos"]), atrás do segmento, porque vídeo dentro de clipe temporizado não renderiza."""
    arq, cortes, fonte = TRAILER[chave]
    t, d, i = s["_t0"], s["_d"] + XF, 0
    fim = t + d
    while t < fim - 0.05:
        ms, dur = cortes[i % len(cortes)]
        dur = min(dur, fim - t)
        s["_soltos"].append(f'<video id="{p}-v{i}" class="clip vid" src="{arq}" muted data-start="{t:.2f}" data-duration="{dur:.2f}" data-media-start="{ms}"></video>')
        t += dur; i += 1
    html = f'<div class="seg"><div class="faixa-fic">{fonte}</div></div>'
    return html, []


# ---------------------------------------------------------------- visuais base
def svg_porta(p, fase):
    luz = "1" if fase in ("atravessa", "fresta", "fecha") else "0"
    return f'''
<svg class="cheio" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice">
  <defs><linearGradient id="{p}-chao" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14171f"/><stop offset="1" stop-color="#05060a"/></linearGradient></defs>
  <rect width="1920" height="1080" fill="#07080c"/>
  <polygon points="0,1080 1920,1080 1180,700 740,700" fill="url(#{p}-chao)"/>
  <polygon points="0,0 1920,0 1180,250 740,250" fill="#0d1016"/>
  <polygon points="0,0 740,250 740,700 0,1080" fill="#10131a"/>
  <polygon points="1920,0 1180,250 1180,700 1920,1080" fill="#0e1118"/>
  <rect x="740" y="250" width="440" height="450" fill="#1a1e27"/>
  <rect id="{p}-luz" x="955" y="300" width="10" height="400" fill="#dfe8f5" opacity="{luz}"/>
  <g id="{p}-folhaE"><rect x="800" y="300" width="160" height="400" fill="#2a303c" stroke="#3a4150" stroke-width="3"/><rect x="935" y="480" width="8" height="46" rx="3" fill="#8a93a8"/></g>
  <g id="{p}-folhaD"><rect x="960" y="300" width="160" height="400" fill="#262b36" stroke="#3a4150" stroke-width="3"/><rect x="977" y="480" width="8" height="46" rx="3" fill="#8a93a8"/></g>
  <rect x="790" y="292" width="340" height="10" fill="#3a4150"/>
  <rect x="770" y="240" width="380" height="8" fill="#e8eef8" opacity=".55"/>
</svg>'''


def texto_baixo(p, s, quando="{t0}+0.6"):
    if not s.get("texto"):
        return "", []
    return f'<div id="{p}-txt" class="frase baixo sombra">{palavras(s["texto"])}</div>', [entra(f"#{p}-txt", quando)]


def v_porta(p, s):
    fase = s.get("fase", "fechada")
    txt, ttw = texto_baixo(p, s)
    html = f'<div class="seg escuro"><div id="{p}-cam" class="cam">{svg_porta(p, fase)}</div>{txt}</div>'
    tw = [f'tl.fromTo("#{p}-cam",{{scale:1.45}},{{scale:1.75,duration:{{d}},ease:"power1.inOut"}},{{t0}});']
    E, D = f'"#{p}-folhaE"', f'"#{p}-folhaD"'
    if fase == "atravessa":
        tw += [f'tl.fromTo({E},{{scaleX:1,svgOrigin:"800 0"}},{{scaleX:0.12,svgOrigin:"800 0",duration:1.2,ease:"power2.inOut"}},{{t0}}+1);',
               f'tl.fromTo({D},{{scaleX:1,svgOrigin:"1120 0"}},{{scaleX:0.12,svgOrigin:"1120 0",duration:1.2,ease:"power2.inOut"}},{{t0}}+1);',
               f'tl.fromTo("#{p}-luz",{{attr:{{x:955,width:10}}}},{{attr:{{x:800,width:320}},duration:1.2,ease:"power2.inOut"}},{{t0}}+1);']
    elif fase == "fresta":
        tw += [f'tl.fromTo({D},{{scaleX:1,svgOrigin:"1120 0"}},{{scaleX:0.8,svgOrigin:"1120 0",duration:2,ease:"power2.inOut"}},{{t0}}+0.5);',
               f'tl.fromTo("#{p}-luz",{{attr:{{width:10}}}},{{attr:{{width:40}},duration:2,ease:"power2.inOut"}},{{t0}}+0.5);']
    elif fase == "fecha":
        tw += [f'tl.fromTo({E},{{scaleX:0.4,svgOrigin:"800 0"}},{{scaleX:1,svgOrigin:"800 0",duration:2.5,ease:"power2.inOut"}},{{t0}});',
               f'tl.fromTo({D},{{scaleX:0.4,svgOrigin:"1120 0"}},{{scaleX:1,svgOrigin:"1120 0",duration:2.5,ease:"power2.inOut"}},{{t0}});',
               f'tl.fromTo("#{p}-luz",{{opacity:1}},{{opacity:0,duration:0.4}},{{t0}}+2.3);']
    return html, tw + ttw


def svg_rato(p):
    return f'''<g id="{p}-rato">
  <ellipse cx="0" cy="0" rx="62" ry="38" fill="#f4f1ea" stroke="{NANQUIM}" stroke-width="4"/>
  <circle cx="58" cy="-18" r="26" fill="#f4f1ea" stroke="{NANQUIM}" stroke-width="4"/>
  <circle cx="48" cy="-44" r="14" fill="#f2c9c4" stroke="{NANQUIM}" stroke-width="3"/>
  <circle cx="68" cy="-22" r="4" fill="{NANQUIM}"/>
  <path d="M-60 6 C -120 20, -150 -30, -190 -6" fill="none" stroke="{NANQUIM}" stroke-width="4"/>
</g>'''


def sobre(p, s, escuro=False):
    if not s.get("sobre"):
        return "", []
    return (f'<div id="{p}-sob" class="mono sobre{" claro" if escuro else ""}">{s["sobre"]}</div>',
            [surge(f"#{p}-sob", "{t0}+0.4", 0.8, "opacity:0")])


def v_camundongo(p, s):
    est = s.get("estado", "calma")
    rato = "" if est == "vazia" else svg_rato(p)
    sob, stw = sobre(p, s)
    html = f'''<div class="seg papel"><svg class="cheio" viewBox="0 0 1920 1080">
  <polygon points="460,820 1460,820 1300,560 620,560" fill="#e2d9c6" stroke="{NANQUIM}" stroke-width="5"/>
  <polyline points="620,560 620,300 1300,300 1300,560" fill="none" stroke="{NANQUIM}" stroke-width="5"/>
  <line x1="460" y1="820" x2="460" y2="520" stroke="{NANQUIM}" stroke-width="5"/><line x1="1460" y1="820" x2="1460" y2="520" stroke="{NANQUIM}" stroke-width="5"/>
  <line x1="460" y1="520" x2="620" y2="300" stroke="{NANQUIM}" stroke-width="5"/><line x1="1460" y1="520" x2="1300" y2="300" stroke="{NANQUIM}" stroke-width="5"/>
  <circle id="{p}-azul" cx="960" cy="520" r="420" fill="{CIANO}" opacity="0"/>
  <g transform="translate(960 700)">{rato}</g>
  <g id="{p}-tremor" opacity="0" stroke="{VERMELHO}" stroke-width="5" fill="none">
    <path d="M840 600 l-30 -20"/><path d="M830 650 l-40 0"/><path d="M1090 600 l30 -20"/><path d="M1100 650 l40 0"/></g>
</svg>{sob}</div>'''
    tw = stw
    if est == "calma":
        tw.append(f'tl.fromTo("#{p}-rato",{{x:-260}},{{x:220,duration:{{d}},ease:"sine.inOut"}},{{t0}});')
    elif est == "medo":
        tw += [f'tl.fromTo("#{p}-tremor",{{opacity:0}},{{opacity:1,duration:0.15}},{{t0}}+0.6);',
               f'tl.fromTo("#{p}-rato",{{x:-3}},{{x:3,duration:0.06,repeat:30,yoyo:true,ease:"none"}},{{t0}}+0.6);']
    else:
        tw.append(f'tl.fromTo("#{p}-azul",{{opacity:0.22}},{{opacity:0,duration:{{d}},ease:"power1.in"}},{{t0}});')
    return html, tw


def v_frase(p, s):
    mundo = s.get("mundo", "escuro")
    html = f'<div class="seg {mundo}"><div id="{p}-txt" class="{tam_frase(s["texto"])} meio">{palavras(s["texto"])}</div></div>'
    return html, [entra(f"#{p}-txt", "{t0}+0.2", 0.09)]


def v_flash(p, s):
    html = f'''<div class="seg escuro"><div id="{p}-cl" class="cheio" style="background:{CIANO};opacity:0"></div>
  <div id="{p}-txt" class="frase-g meio" style="color:{CIANO}">{palavras(s["texto"])}</div></div>'''
    tw = [f'tl.fromTo("#{p}-cl",{{opacity:0}},{{opacity:0.9,duration:0.08}},{{t0}}+0.2);',
          f'tl.to("#{p}-cl",{{opacity:0,duration:0.5,ease:"power2.out"}},{{t0}}+0.3);', entra(f"#{p}-txt", "{t0}+0.5")]
    return html, tw


def v_pergunta(p, s):
    its = "".join(f'<div id="{p}-l{i}" class="perg-l"><span>{i+1:02d}</span>{w}</div>' for i, w in enumerate(s["linhas"]))
    html = f'''<div class="seg escuro"><div class="perg"><div id="{p}-q" class="mono perg-t">QUEM TEM O PODER DE ENTRAR NA SUA MENTE?</div>{its}</div></div>'''
    n = len(s["linhas"])
    tw = [surge(f"#{p}-q", "{t0}+0.3", 0.6, "opacity:0")]
    tw += [surge(f"#{p}-l{i}", f"{{t0}}+{{d}}*{0.3 + i * 0.55 / n:.2f}", 0.5, "opacity:0,x:-40") for i in range(n)]
    return html, tw


def painel(i, ano, nome, linha, fundo=""):
    return (f'<div id="P{i}" class="painel">{fundo}<div class="painel-c"><div class="mono">{ano}</div>'
            f'<div class="painel-n">{nome}</div><div class="painel-l">{linha}</div></div></div>')


TRIO = [("2022", "Ruptura", "divide a sua memória em duas"), ("1999", "Matrix", "fabrica o mundo que você vê"),
        ("2010", "Basilisco de Roko", "castiga quem não obedece")]


ICONES = (
    f'<svg class="icone" viewBox="0 0 400 400"><path d="M200 60 C120 60 80 120 84 190 C88 240 110 270 126 300 V350 H200 Z" fill="#2b2216"/><path d="M200 60 C280 60 320 120 316 190 C312 240 290 270 274 300 V350 H200 Z" fill="#121a24"/><line x1="200" y1="40" x2="200" y2="370" stroke="{AMBAR}" stroke-width="3" stroke-dasharray="12 9"/></svg>',
    '<svg class="icone" viewBox="0 0 400 400">' + "".join(f'<text x="{40 + i * 46}" y="{60 + (i * 53) % 90}" fill="#3fd16a" font-family="IBM Plex Mono" font-size="34" writing-mode="tb">{"ｱｶｻﾀﾅﾊﾏﾔﾗﾜ"[i % 10] * 5}</text>' for i in range(8)) + "</svg>",
    f'<svg class="icone" viewBox="0 0 400 400"><path d="M60 200 Q200 90 340 200 Q200 310 60 200 Z" fill="#120a0a" stroke="{VERMELHO}" stroke-width="3"/><circle cx="200" cy="200" r="70" fill="{VERMELHO}"/><ellipse cx="200" cy="200" rx="9" ry="56" fill="#000"/></svg>',
)


def v_trio_ficcao(p, s, fundos=ICONES):
    pn = "".join(painel(i, *TRIO[i], fundos[i]).replace(f'id="P{i}"', f'id="{p}-p{i}"') for i in range(3))
    html = f'<div class="seg preto"><div class="trio">{pn}</div></div>'
    tw = [surge(f"#{p}-p{i}", f"{{t0}}+{{d}}*{0.12 + i * 0.27:.2f}", 0.7, "opacity:0,y:60") for i in range(3)]
    return html, tw


def v_arquivos_mesa(p, s):
    nomes = ["1 · ESCREVER", "2 · MAPEAR", "3 · LER", "4 · INFLUENCIAR", "A REALIDADE", "O ROBÔ MAU"]
    ps = "".join(f'<div id="{p}-a{i}" class="mini-pasta" style="left:{150 + i * 270}px;top:{330 + (i % 2) * 70}px;transform:rotate({(-1) ** i * 3}deg)">'
                 f'<div class="mini-aba"></div><div class="mini-c">{n}</div></div>' for i, n in enumerate(nomes))
    html = f'<div class="seg escuro"><div class="mesa"></div>{ps}</div>'
    tw = [surge(f"#{p}-a{i}", f"{{t0}}+{0.3 + i * 0.35:.2f}", 0.7, "opacity:0,y:400") for i in range(6)]
    return html, tw


def v_titulo(p, s):
    html = f'''<div class="seg preto"><div class="centro">
  <div id="{p}-q" class="frase" style="color:{APOIO}">{palavras(s["texto"])}</div>
  <div id="{p}-t" class="titulo-filme">{s["titulo"]}</div><div id="{p}-li" class="titulo-linha"></div></div></div>'''
    tw = [entra(f"#{p}-q", "{t0}+0.1", 0.12),
          f'tl.fromTo("#{p}-t",{{opacity:0,scale:1.12,filter:"blur(14px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:1.6,ease:"expo.out"}},{{t0}}+1.4);',
          f'tl.fromTo("#{p}-li",{{scaleX:0}},{{scaleX:1,duration:1.2,ease:"power2.inOut"}},{{t0}}+2);']
    return html, tw


def v_escritorio(p, s):
    feed = ""
    if s.get("tela") == "feed":
        feed = f'<g id="{p}-feed">' + "".join(f'<rect x="830" y="{330+i*70}" width="260" height="50" rx="6" fill="#3d4658"/>' for i in range(8)) + "</g>"
    html = f'''<div class="seg escuro"><div id="{p}-cam" class="cam"><svg class="cheio" viewBox="0 0 1920 1080">
  <rect width="1920" height="1080" fill="#090b10"/>
  <rect x="0" y="0" width="1920" height="640" fill="#0f1218"/>
  <polygon points="1360,330 1180,760 1640,760" fill="#f2e6c8" opacity=".10"/>
  <rect x="300" y="640" width="1320" height="40" fill="#1c1f26"/>
  <rect x="380" y="680" width="40" height="400" fill="#15171c"/><rect x="1500" y="680" width="40" height="400" fill="#15171c"/>
  <rect x="800" y="300" width="320" height="300" rx="8" fill="#1a2030" stroke="#2c3344" stroke-width="6"/>
  <clipPath id="{p}-tc"><rect x="812" y="312" width="296" height="276"/></clipPath>
  <g clip-path="url(#{p}-tc)"><rect x="812" y="312" width="296" height="276" fill="#2a3550"/>{feed}</g>
  <rect x="940" y="600" width="40" height="40" fill="#20242d"/>
  <path d="M1360 330 l-60 -150 l120 0 z" fill="#2a2e38"/><circle cx="1360" cy="330" r="10" fill="#f2e6c8"/>
  <line x1="1360" y1="180" x2="1430" y2="640" stroke="#2a2e38" stroke-width="10"/>
</svg></div></div>'''
    tw = [f'tl.fromTo("#{p}-cam",{{scale:1.15,x:-40}},{{scale:1.0,x:0,duration:{{d}},ease:"power1.inOut"}},{{t0}});']
    if feed:
        tw.append(f'tl.fromTo("#{p}-feed",{{y:0}},{{y:-420,duration:{{d}},ease:"none"}},{{t0}});')
    return html, tw


def v_ruptura(p, s):
    html = f'''<div class="seg escuro"><svg class="cheio" viewBox="0 0 1920 1080">
  <g id="{p}-e"><path d="M960 220 C 760 220, 650 360, 660 520 C 670 640, 720 700, 760 760 L 760 880 L 960 880 Z" fill="#2b2216"/></g>
  <g id="{p}-d"><path d="M960 220 C 1160 220, 1270 360, 1260 520 C 1250 640, 1200 700, 1160 760 L 1160 880 L 960 880 Z" fill="#121a24"/></g>
  <line id="{p}-corte" x1="960" y1="180" x2="960" y2="920" stroke="{AMBAR}" stroke-width="4" stroke-dasharray="20 14"/>
  <text x="560" y="980" class="svg-leg" fill="{TINTA}" text-anchor="middle">LÁ FORA</text>
  <text x="1360" y="980" class="svg-leg" fill="{TINTA}" text-anchor="middle">LÁ DENTRO</text></svg></div>'''
    tw = [f'tl.fromTo("#{p}-corte",{{attr:{{"stroke-dashoffset":740}}}},{{attr:{{"stroke-dashoffset":0}},duration:1.6,ease:"power2.inOut"}},{{t0}}+0.4);',
          f'tl.fromTo("#{p}-e",{{x:0}},{{x:-160,duration:1.2,ease:"expo.inOut"}},{{t0}}+{{d}}*0.4);',
          f'tl.fromTo("#{p}-d",{{x:0}},{{x:160,duration:1.2,ease:"expo.inOut"}},{{t0}}+{{d}}*0.4);']
    return html, tw


def v_contrato(p, s):
    html = f'''<div class="seg papel"><div id="{p}-c" class="doc contrato">
  <div class="doc-topo"><span>CONTRATO DE TRABALHO</span><span>LUMON</span></div>
  <div class="doc-linhas">{"<i></i>" * 5}</div>
  <div id="{p}-s1" class="ass"><span>Pessoa de fora</span><b class="ok">assinou</b></div>
  <div id="{p}-s2" class="ass"><span>Pessoa de dentro</span><b class="nao">nunca concordou</b></div>
</div></div>'''
    tw = [f'tl.fromTo("#{p}-c",{{y:300,opacity:0}},{{y:0,opacity:1,duration:0.8,ease:"expo.out"}},{{t0}}+0.1);',
          surge(f"#{p}-s1", "{t0}+{d}*0.25", 0.4, "opacity:0,x:-30"), surge(f"#{p}-s2", "{t0}+{d}*0.55", 0.4, "opacity:0,x:-30")]
    return html, tw


def v_doc(p, s):
    """Página real do artigo à esquerda (se existir) e a ficha à direita."""
    img = s.get("img")
    real = img and os.path.exists(os.path.join(AQUI, f"assets/docs/{img}.png"))
    carimbo = f'<div id="{p}-car" class="carimbo">{s["carimbo"]}</div>' if s.get("carimbo") else ""
    ret = ""
    if img in RETRATO and ESTILO != "3d":
        f, nome = RETRATO[img]
        ret = f'<div id="{p}-ret" class="retrato"><img src="assets/img/{f}.jpg"><span>{nome}<br><i>{CRED[f]}</i></span></div>'
    if real:
        pagina = f'<div id="{p}-pg" class="pagina"><img id="{p}-im" src="assets/docs/{img}.png">{carimbo}</div>'
    else:
        pagina = f'<div id="{p}-pg" class="pagina falsa"><div class="doc-topo"><span>{s["revista"]}</span><span>{s["ano"]}</span></div><div class="doc-linhas">{"<i></i>" * 14}</div>{carimbo}</div>'
    html = f'''<div class="seg papel">{pagina}
  <div id="{p}-fi" class="ficha"><div class="mono ficha-r">{s["revista"]} · {s["ano"]}</div>
    <div class="ficha-t"><span id="{p}-marca" class="marca"></span><span class="tt">{s["titulo"]}</span></div>
    <div class="ficha-a">{s["autores"]}</div>{ret}</div></div>'''
    tw = [f'tl.fromTo("#{p}-pg",{{y:500,rotation:-7,opacity:0}},{{y:0,rotation:-2.5,opacity:1,duration:1,ease:"expo.out"}},{{t0}}+0.05);',
          surge(f"#{p}-fi", "{t0}+0.5", 0.8, "opacity:0,x:60")]
    if real:
        tw.append(f'tl.fromTo("#{p}-im",{{y:0,scale:1}},{{y:-260,scale:1.12,duration:{{d}}+{XF},ease:"power1.inOut"}},{{t0}}+0.4);')
    tw.append(f'tl.fromTo("#{p}-marca",{{scaleX:0}},{{scaleX:1,duration:0.7,ease:"power2.inOut"}},{{t0}}+1.4);')
    if ret:
        tw.append(surge(f"#{p}-ret", "{t0}+{d}*0.4", 0.6, "opacity:0,y:30"))
    if carimbo:
        tw.append(f'tl.fromTo("#{p}-car",{{scale:2.6,opacity:0,rotation:-24}},{{scale:1,opacity:1,rotation:-12,duration:0.25,ease:"power4.in"}},{{t0}}+{{d}}*0.5);')
    return html, tw


def v_episodios(p, s):
    blocos = "".join(
        f'<rect id="{p}-e{i}" x="{180+i*400}" y="470" width="330" height="140" rx="10" fill="{"#c9bfa9" if i else NANQUIM}"/>'
        f'<rect id="{p}-pt{i}" x="{530+i*400}" y="420" width="20" height="240" fill="{VERMELHO}"/>' for i in range(4))
    html = f'<div class="seg papel"><svg class="cheio" viewBox="0 0 1920 1080">{blocos}<text x="345" y="700" class="svg-leg">episódio</text><text x="1140" y="390" class="svg-leg" fill="{VERMELHO}">portas</text></svg></div>'
    tw = [f'tl.fromTo("#{p}-e{i}",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.5,ease:"expo.out"}},{{t0}}+{0.3+i*0.6:.1f});' for i in range(4)]
    tw += [f'tl.fromTo("#{p}-pt{i}",{{scaleY:0,transformOrigin:"50% 50%"}},{{scaleY:1,duration:0.4,ease:"back.out"}},{{t0}}+{0.6+i*0.6:.1f});' for i in range(4)]
    return html, tw


def v_trauma(p, s):
    ws = ["um cheiro", "um som", "um lugar"]
    its = "".join(f'<div id="{p}-w{i}" class="trauma-w" style="left:{240 + i * 520}px">{w}</div>' for i, w in enumerate(ws))
    ecg = "M0 540 " + " ".join(f"h120 l20 -150 l25 300 l20 -190 l15 40" for _ in range(9))
    html = f'''<div class="seg preto"><svg class="cheio" viewBox="0 0 1920 1080">
  <path id="{p}-ecg" d="{ecg}" fill="none" stroke="{VERMELHO}" stroke-width="5" stroke-dasharray="3200" stroke-dashoffset="3200"/></svg>
  <div id="{p}-fl" class="cheio" style="background:{VERMELHO};opacity:0"></div>{its}</div>'''
    tw = [f'tl.fromTo("#{p}-ecg",{{attr:{{"stroke-dashoffset":3200}}}},{{attr:{{"stroke-dashoffset":0}},duration:{{d}},ease:"none"}},{{t0}});']
    for i in range(3):
        q = f"{{t0}}+{{d}}*{0.42 + i * 0.12:.2f}"
        tw += [f'tl.fromTo("#{p}-w{i}",{{opacity:0,scale:1.3}},{{opacity:1,scale:1,duration:0.2,ease:"power4.out"}},{q});']
    tw += [f'tl.fromTo("#{p}-fl",{{opacity:0}},{{opacity:0.35,duration:0.06,repeat:3,yoyo:true}},{{t0}}+{{d}}*0.8);']
    return html, tw


def v_remedio(p, s):
    html = f'''<div class="seg papel"><svg class="cheio" viewBox="0 0 1920 1080">
  <g id="{p}-pil" transform="rotate(-25 760 540)"><rect x="560" y="470" width="400" height="140" rx="70" fill="#fbf8f1" stroke="{NANQUIM}" stroke-width="6"/>
  <path d="M760 470 v140" stroke="{NANQUIM}" stroke-width="4"/><path d="M630 470 a70 70 0 0 0 0 140 h130 v-140 z" fill="{CIANO}" opacity=".55"/></g></svg>
  <div id="{p}-t" class="remedio"><div class="mono" style="color:{VERMELHO}">BETABLOQUEADOR</div><div class="remedio-n">propranolol</div>
  <div class="remedio-l">remédio comum para pressão,<br>tomado antes de relembrar o trauma</div></div></div>'''
    tw = [f'tl.fromTo("#{p}-pil",{{opacity:0,y:-200}},{{opacity:1,y:0,duration:0.9,ease:"bounce.out"}},{{t0}}+0.2);',
          surge(f"#{p}-t", "{t0}+{d}*0.3", 0.7, "opacity:0,x:60")]
    return html, tw


def v_placar(p, s):
    rows = "".join(f'<div id="{p}-r{i}" class="placar-l"><b>{a}</b><span>{au}</span><i class="{"ok" if i == 0 else "nao"}">{r}</i></div>'
                   for i, (a, au, r) in enumerate(s["itens"]))
    html = f'<div class="seg papel"><div class="placar"><div class="mono ress-t">PROPRANOLOL E TRAUMA · O QUE OS ESTUDOS DIZEM</div>{rows}<div id="{p}-x" class="placar-x">em discussão</div></div></div>'
    tw = [surge(f"#{p}-r{i}", f"{{t0}}+{{d}}*{0.1 + i * 0.35:.2f}", 0.6, "opacity:0,x:-50") for i in range(len(s["itens"]))]
    tw.append(surge(f"#{p}-x", "{t0}+{d}*0.78", 0.5, "opacity:0"))
    return html, tw


def v_quem_decide(p, s):
    pos = [(480, 330), (1440, 330), (480, 790), (1440, 790)]
    its = "".join(f'<div id="{p}-q{i}" class="decide" style="left:{x-300}px;top:{y-60}px">{w}</div>' for i, (w, (x, y)) in enumerate(zip(s["itens"], pos)))
    html = f'''<div class="seg escuro"><svg class="cheio" viewBox="0 0 1920 1080"><g id="{p}-ch" stroke="{AMBAR}" stroke-width="12" fill="none">
  <circle cx="960" cy="440" r="80"/><path d="M960 520 v240 m0 -80 h60 m-60 -50 h45"/></g></svg>
  <div class="mono decide-t">QUEM DECIDE QUAL LEMBRANÇA DÓI DEMAIS?</div>{its}</div>'''
    tw = [f'tl.fromTo("#{p}-ch",{{rotation:-30,opacity:0,svgOrigin:"960 600"}},{{rotation:0,opacity:1,svgOrigin:"960 600",duration:1,ease:"expo.out"}},{{t0}}+0.2);']
    tw += [surge(f"#{p}-q{i}", f"{{t0}}+{{d}}*{0.45 + i * 0.12:.2f}", 0.4, "opacity:0,scale:1.3", "power4.out") for i in range(4)]
    return html, tw


def v_arquivo(p, s):
    html = f'''<div class="seg escuro"><div id="{p}-pasta" class="pasta">
  <div class="aba">ARQUIVO {s["n"]}</div><div class="pasta-c"><div class="mono">CASO EM ANÁLISE</div><div class="pasta-nome" style="font-size:{min(170, int(1250/len(s["nome"])))}px">{s["nome"]}</div></div></div></div>'''
    tw = [f'tl.fromTo("#{p}-pasta",{{y:600,rotation:4}},{{y:0,rotation:-1.5,duration:0.8,ease:"expo.out"}},{{t0}}+0.05);',
          f'tl.fromTo("#{p}-pasta",{{scale:1}},{{scale:1.08,duration:{{d}},ease:"power1.in"}},{{t0}}+0.8);']
    return html, tw


def v_neuronios(p, s):
    r = random.Random(7)
    pts = [(r.randint(160, 1760), r.randint(140, 940)) for _ in range(46)]
    ligs = "".join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>' for a, b in zip(pts, pts[1:] + pts[:1]) if abs(a[0]-b[0]) < 700)
    acesos = set(range(0, 46, 6))
    nos = "".join(f'<circle class="{"ac" if i in acesos else ""}" cx="{x}" cy="{y}" r="{14 if i in acesos else 9}"/>' for i, (x, y) in enumerate(pts))
    html = f'''<div class="seg escuro"><svg class="cheio" viewBox="0 0 1920 1080">
  <g stroke="#2b3342" stroke-width="2">{ligs}</g><g id="{p}-nos" fill="#3b4558">{nos}</g></svg>
  <div id="{p}-leg" class="legenda-g">{s["legenda"]}</div></div>'''
    tw = [f'tl.fromTo("#{p}-nos .ac",{{fill:"#3b4558"}},{{fill:"{CIANO}",duration:0.25,stagger:0.05}},{{t0}}+{{d}}*0.25);',
          surge(f"#{p}-leg", "{t0}+{d}*0.55", 0.5, "opacity:0")]
    return html, tw


def v_caixas(p, s):
    def caixa(x, rot):
        return f'<rect x="{x}" y="380" width="520" height="360" rx="6" fill="#e2d9c6" stroke="{NANQUIM}" stroke-width="5"/><text x="{x+20}" y="360" class="svg-leg">{rot}</text>'
    html = f'''<div class="seg papel"><svg class="cheio" viewBox="0 0 1920 1080">
  {caixa(240, "caixa A · tranquila")}{caixa(1160, "caixa B · choque")}
  <path id="{p}-raio" d="M1420 420 l-60 140 l70 0 l-60 150" fill="none" stroke="{VERMELHO}" stroke-width="10" opacity="0"/>
  <path id="{p}-arco" d="M1420 380 C 1300 120, 620 120, 500 380" fill="none" stroke="{CIANO}" stroke-width="10" stroke-dasharray="1400" stroke-dashoffset="1400"/>
  <circle id="{p}-mem" cx="500" cy="560" r="90" fill="{CIANO}" opacity="0"/>
</svg></div>'''
    tw = [f'tl.fromTo("#{p}-raio",{{opacity:0}},{{opacity:1,duration:0.05,repeat:5,yoyo:true}},{{t0}}+{{d}}*0.35);',
          f'tl.fromTo("#{p}-arco",{{attr:{{"stroke-dashoffset":1400}}}},{{attr:{{"stroke-dashoffset":0}},duration:1,ease:"power2.inOut"}},{{t0}}+{{d}}*0.6);',
          f'tl.fromTo("#{p}-mem",{{opacity:0}},{{opacity:0.6,duration:0.4}},{{t0}}+{{d}}*0.6+0.9);']
    return html, tw


def v_citacao(p, s):
    html = f'''<div class="seg escuro"><div class="centro"><div id="{p}-q" class="citacao">“{s["texto"]}”</div>
  <div id="{p}-f" class="fonte-c">{s["fonte"]}</div></div></div>'''
    tw = [f'tl.fromTo("#{p}-q",{{opacity:0,filter:"blur(10px)"}},{{opacity:1,filter:"blur(0px)",duration:0.8}},{{t0}}+0.2);',
          surge(f"#{p}-f", "{t0}+1.2", 0.5, "opacity:0")]
    return html, tw


def v_ressalva(p, s):
    linhas = "".join(f'<div id="{p}-r{i}" class="ress-l"><span>×</span>{l}</div>' for i, l in enumerate(s["linhas"]))
    html = f'<div class="seg papel"><div class="ress"><div class="mono ress-t">O QUE ISSO NÃO PROVA</div>{linhas}</div></div>'
    n = len(s["linhas"])
    tw = [f'tl.fromTo("#{p}-r{i}",{{opacity:0,filter:"blur(6px)"}},{{opacity:1,filter:"blur(0px)",duration:0.35}},{{t0}}+{{d}}*{0.08+i*0.8/n:.2f});' for i in range(n)]
    return html, tw


def v_mosca(p, s):
    return foto(p, "mosca", f'<div id="{p}-esc" class="mono sobre claro">DROSOPHILA MELANOGASTER · ~3 mm</div>', (1.0, 1.25), pos="50% 45%")


def numeros(p, s):
    if not s.get("num"):
        return "", []
    html = (f'<div class="nums"><div id="{p}-n1"><b>{s["num"]}</b><span>{s["leg"]}</span></div>'
            f'<div id="{p}-n2"><b>{s["num2"]}</b><span>{s["leg2"]}</span></div></div><div class="fonte">{s["fonte"]}</div>')
    return html, [surge(f"#{p}-n1", "{t0}+{d}*0.45", 0.6), surge(f"#{p}-n2", "{t0}+{d}*0.65", 0.6)]


def v_conectoma(p, s):
    nh, ntw = numeros(p, s)
    if s.get("modo") == "simula":
        return v_neuronios(p, {"legenda": "cérebro de mosca, simulado"})
    html, tw = foto(p, "flywire", nh, (1.0, 1.1), ext="jpg")
    return html, tw + ntw


def v_fatias(p, s):
    fs = "".join(f'<div class="fatia" id="{p}-f{i}" style="transform:translate({i*14}px,{-i*16}px)"></div>' for i in range(14))
    html = f'''<div class="seg escuro"><div class="fatias">{fs}<div id="{p}-scan" class="scan"></div></div>
  <div class="passos"><div id="{p}-a">microscópio eletrônico</div><div id="{p}-b">IA traça cada neurônio</div><div id="{p}-c">humanos corrigem os erros</div></div></div>'''
    tw = [f'tl.fromTo("#{p}-f{i}",{{opacity:0,y:-80}},{{opacity:1,y:0,duration:0.3}},{{t0}}+{0.1 + i * 0.07:.2f});' for i in range(14)]
    tw += [f'tl.fromTo("#{p}-scan",{{y:0}},{{y:500,duration:2,repeat:2,yoyo:true,ease:"sine.inOut"}},{{t0}}+1.2);']
    tw += [surge(f"#{p}-{c}", f"{{t0}}+{{d}}*{q}", 0.5, "opacity:0,x:40") for c, q in (("a", 0.15), ("b", 0.4), ("c", 0.65))]
    return html, tw


def v_comparacao(p, s):
    html = f'''<div class="seg escuro"><div class="comp">
  <div class="comp-l"><span>{s["l1"]}</span><div class="barra"><i id="{p}-b1" style="background:{CIANO}"></i></div><b id="{p}-n1">{s["a1"]}</b></div>
  <div class="comp-l"><span>{s["l2"]}</span><div class="barra"><i id="{p}-b2" style="background:{VERMELHO}"></i></div><b id="{p}-n2">{s["a2"]}</b></div>
  <div class="mono comp-nota">escala: a barra de cima mal aparece</div></div><div class="fonte">{s["fonte"]}</div></div>'''
    tw = [f'tl.fromTo("#{p}-b1",{{width:"0%"}},{{width:"0.4%",duration:0.6}},{{t0}}+{{d}}*0.15);',
          surge(f"#{p}-n1", "{t0}+{d}*0.2", 0.4, "opacity:0"),
          f'tl.fromTo("#{p}-b2",{{width:"0%"}},{{width:"100%",duration:2.2,ease:"power2.inOut"}},{{t0}}+{{d}}*0.5);',
          surge(f"#{p}-n2", "{t0}+{d}*0.5+2", 0.4, "opacity:0")]
    return html, tw


def v_hospital(p, s):
    html = f'''<div class="seg escuro"><svg class="cheio" viewBox="0 0 1920 1080">
  <rect width="1920" height="1080" fill="#0c1016"/>
  <rect x="300" y="620" width="1100" height="60" rx="20" fill="#1d2430"/><rect x="300" y="560" width="220" height="70" rx="30" fill="#2a3242"/>
  <rect x="1460" y="260" width="320" height="220" rx="10" fill="#111821" stroke="#2c3344" stroke-width="5"/>
  <path id="{p}-ecg" d="M1480 380 h60 l20 -50 l20 90 l20 -40 h60 l20 -50 l20 90 l20 -40 h60" fill="none" stroke="{CIANO}" stroke-width="5" stroke-dasharray="600" stroke-dashoffset="600"/>
</svg><div class="mono local">{s["local"]}</div><div class="fonte">imagem ilustrativa · a paciente não é mostrada</div></div>'''
    tw = [f'tl.fromTo("#{p}-ecg",{{attr:{{"stroke-dashoffset":600}}}},{{attr:{{"stroke-dashoffset":0}},duration:2.5,repeat:6,ease:"none"}},{{t0}});']
    return html, tw


def svg_cerebro(x, y, esc, idp, cor="#c9bfa9"):
    return (f'<g transform="translate({x} {y}) scale({esc})"><path d="M-120 20 C -140 -80, -40 -130, 10 -110 C 80 -140, 150 -60, 130 10 C 150 60, 90 110, 20 100 C -40 120, -110 90, -120 20 z" '
            f'fill="{cor}" stroke="{NANQUIM}" stroke-width="5"/><circle id="{idp}" cx="0" cy="-60" r="28" fill="{AMBAR}" opacity="0"/></g>')


def v_cerebros(p, s):
    html = f'''<div class="seg papel"><svg class="cheio" viewBox="0 0 1920 1080">
  {svg_cerebro(560, 500, 2.2, p+"-c0")}{svg_cerebro(1360, 500, 2.2, p+"-c1")}
  <text x="560" y="850" class="svg-leg" text-anchor="middle">paciente</text><text x="1360" y="850" class="svg-leg" text-anchor="middle">voluntária saudável</text>
  <text x="960" y="180" class="svg-leg" text-anchor="middle">"imagine que está jogando tênis"</text></svg></div>'''
    tw = [f'tl.fromTo("#{p}-c1",{{opacity:0,scale:0.5,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.5,ease:"back.out"}},{{t0}}+{{d}}*0.2);',
          f'tl.fromTo("#{p}-c0",{{opacity:0,scale:0.5,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.5,ease:"back.out"}},{{t0}}+{{d}}*0.45);']
    return html, tw


def v_quatro(p, s):
    cs = "".join(svg_cerebro(360 + i*400, 520, 1.2, f"{p}-c{i}") for i in range(4))
    html = f'''<div class="seg papel"><svg class="cheio" viewBox="0 0 1920 1080">{cs}
  <text id="{p}-t" x="360" y="760" class="svg-grande" text-anchor="middle" opacity="0">sinais de consciência</text></svg>
  <div id="{p}-n" class="quatro-n">1 em cada 4</div><div class="fonte escura">{s["fonte"]}</div></div>'''
    tw = [f'tl.fromTo("#{p}-c0",{{opacity:0}},{{opacity:1,duration:0.3}},{{t0}}+{{d}}*0.6);',
          f'tl.fromTo("#{p}-t",{{opacity:0}},{{opacity:1,duration:0.3}},{{t0}}+{{d}}*0.62);',
          surge(f"#{p}-n", "{t0}+{d}*0.7", 0.6, "opacity:0,scale:1.4", "power4.out")]
    return html, tw


def v_cursor(p, s):
    html = f'''<div class="seg papel"><div class="tela-mock"><div class="alvo"></div><div id="{p}-cur" class="cursor"></div></div><div class="fonte escura">{s["fonte"]}</div></div>'''
    tw = [f'tl.fromTo("#{p}-cur",{{x:-380,y:180}},{{x:300,y:-120,duration:{{d}}*0.7,ease:"power2.inOut"}},{{t0}}+0.4);']
    return html, tw


def v_servidores(p, s):
    html, tw = foto(p, "servidores", f'<div id="{p}-q" class="frase baixo sombra">{palavras("Quem guarda esses dados?")}</div>', (1.05, 1.25))
    return html, tw + [entra(f"#{p}-q", "{t0}+{d}*0.3")]


def v_feeds(p, s):
    def feed(i, cor):
        return f'<div class="fone"><div class="mono">GRUPO {i}</div>' + "".join(f'<div class="post" style="background:{cor}"></div>' for _ in range(5)) + "</div>"
    html = f'''<div class="seg escuro"><div class="mono data-topo">{s["data"]}</div><div class="fones">
  <div id="{p}-f1">{feed("A · menos posts felizes", "#3a3f4a")}</div>
  <div id="{p}-f2">{feed("B · menos posts tristes", "#7b6a3e")}</div></div>
  <div id="{p}-num" class="num-lado">{s["numero"]}<span>pessoas</span></div><div class="fonte">ilustração · Kramer e outros, PNAS, 2014</div></div>'''
    tw = [f'tl.fromTo("#{p}-f1",{{y:500}},{{y:0,duration:0.8,ease:"expo.out"}},{{t0}}+{{d}}*0.45);',
          f'tl.fromTo("#{p}-f2",{{y:500}},{{y:0,duration:0.8,ease:"expo.out"}},{{t0}}+{{d}}*0.7);',
          f'(function(){{var o={{v:0}};tl.fromTo(o,{{v:0}},{{v:689003,duration:1.6,ease:"power3.out",onUpdate:function(){{document.querySelector("#{p}-num").firstChild.textContent=Math.round(o.v).toLocaleString("pt-BR");}}}},{{t0}}+{{d}}*0.15);}})();']
    return html, tw


def v_termos(p, s):
    html = f'''<div class="seg escuro"><div class="termos"><div id="{p}-rol" class="rol">{"<i></i>" * 80}</div></div>
  <div id="{p}-ck" class="aceito">☑ Li e aceito a Política de Uso de Dados</div></div>'''
    tw = [f'tl.fromTo("#{p}-rol",{{y:0}},{{y:-2600,duration:{{d}},ease:"power1.in"}},{{t0}});',
          f'tl.fromTo("#{p}-ck",{{opacity:0,scale:1.3}},{{opacity:1,scale:1,duration:0.2,ease:"power4.in"}},{{t0}}+{{d}}*0.6);']
    return html, tw


def v_simulacao(p, s):
    r = random.Random(4)
    if s.get("fase") == "revela":
        cel = "".join(f'<rect x="{80 + (i % 12) * 150}" y="{60 + (i // 12) * 150}" width="130" height="130" fill="#141a26" stroke="{CIANO}" stroke-opacity=".35"/>' for i in range(72))
        html = f'''<div class="seg preto"><svg class="cheio" viewBox="0 0 1920 1080"><g id="{p}-g">{cel}<rect x="830" y="510" width="130" height="130" fill="{AMBAR}" opacity=".9"/></g></svg>
  <div id="{p}-v" class="mono voce">VOCÊ?</div></div>'''
        tw = [f'tl.fromTo("#{p}-g",{{scale:7,svgOrigin:"895 575"}},{{scale:1,svgOrigin:"895 575",duration:{{d}}*0.8,ease:"power2.inOut"}},{{t0}});',
              surge(f"#{p}-v", "{t0}+{d}*0.6", 0.5, "opacity:0")]
        return html, tw
    ls = "".join(f'<line x1="{960 + (i - 10) * 30}" y1="560" x2="{960 + (i - 10) * 260}" y2="1080"/>' for i in range(21))
    hs = "".join(f'<line x1="0" y1="{560 + k * k * 8}" x2="1920" y2="{560 + k * k * 8}"/>' for k in range(1, 12))
    blocos = "".join(f'<rect x="{r.randint(100, 1800)}" y="{560 - (h := r.randint(40, 300))}" width="{r.randint(30, 90)}" height="{h}" fill="#141a26" stroke="{CIANO}" stroke-opacity=".3"/>' for _ in range(40))
    html = f'''<div class="seg preto"><svg class="cheio" viewBox="0 0 1920 1080"><g id="{p}-c">{blocos}</g>
  <g id="{p}-g" stroke="{CIANO}" stroke-opacity=".35" stroke-width="2">{ls}{hs}</g></svg></div>'''
    tw = [f'tl.fromTo("#{p}-c",{{scale:1}},{{scale:1.15,svgOrigin:"960 560",duration:{{d}},ease:"none"}},{{t0}});',
          f'tl.fromTo("#{p}-g",{{opacity:0}},{{opacity:1,duration:1.5}},{{t0}}+0.3);']
    return html, tw


def v_matrix(p, s):
    r = random.Random(9)
    cols = "".join(f'<div class="col" id="{p}-k{i}" style="left:{i * 48}px">' + "".join(chr(0x30A0 + r.randint(0, 90)) for _ in range(40)) + "</div>" for i in range(40))
    html = f'<div class="seg preto">{cols}<div class="faixa-fic">{s["fonte"]}</div></div>'
    tw = [f'tl.fromTo("#{p}-k{i}",{{y:{-1800 - r.randint(0, 800)}}},{{y:{200 + r.randint(0, 400)},duration:{{d}}+{XF},ease:"none"}},{{t0}});' for i in range(40)]
    return html, tw


def v_multiplica(p, s):
    if s.get("fase") == "uma":
        pts = "".join(f'<circle cx="{60 + (i % 30) * 62}" cy="{60 + (i // 30) * 62}" r="20" fill="{CIANO}" opacity=".55"/>' for i in range(30 * 17))
        html = f'''<div class="seg preto"><svg class="cheio" viewBox="0 0 1920 1080"><g id="{p}-g">{pts}<circle cx="{60 + 19 * 62}" cy="{60 + 9 * 62}" r="22" fill="{AMBAR}"/></g></svg>
  <div class="legenda-b"><span style="color:{CIANO}">● simuladas</span>   <span style="color:{AMBAR}">● real</span></div></div>'''
        tw = [f'tl.fromTo("#{p}-g",{{scale:1}},{{scale:5,svgOrigin:"{60 + 19 * 62} {60 + 9 * 62}",duration:{{d}},ease:"power2.in"}},{{t0}});']
        return html, tw
    pts = "".join(f'<circle class="m" cx="{60 + (i % 30) * 62}" cy="{60 + (i // 30) * 62}" r="20" fill="{CIANO}"/>' for i in range(30 * 17))
    html = f'<div class="seg preto"><svg class="cheio" viewBox="0 0 1920 1080"><g id="{p}-g">{pts}</g></svg><div id="{p}-n" class="contador">1</div></div>'
    tw = [f'tl.fromTo("#{p}-g .m",{{opacity:0,scale:0,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.2,stagger:{{each:0.012,from:"center",grid:[17,30]}}}},{{t0}}+0.6);',
          f'(function(){{var o={{v:1}};tl.fromTo(o,{{v:1}},{{v:6,duration:{{d}}-1,ease:"power1.in",onUpdate:function(){{document.querySelector("#{p}-n").textContent=Math.round(Math.pow(10,o.v)).toLocaleString("pt-BR")+" mentes";}}}},{{t0}}+0.6);}})();']
    return html, tw


def v_trilema(p, s):
    its = "".join(f'<div id="{p}-i{i}" class="tri"><b>{i+1}</b>{t}</div>' for i, t in enumerate(s["itens"]))
    html = f'<div class="seg escuro"><div class="mono tri-t">PELO MENOS UMA É VERDADE</div><div class="tris">{its}</div></div>'
    tw = [surge(f"#{p}-i{i}", f"{{t0}}+{{d}}*{0.2 + i * 0.25:.2f}", 0.6, "opacity:0,y:60") for i in range(3)]
    tw.append(f'tl.fromTo("#{p}-i2",{{borderColor:"rgba(167,139,250,.25)"}},{{borderColor:"rgba(242,184,75,1)",duration:0.5}},{{t0}}+{{d}}*0.9);')
    return html, tw


def v_forum(p, s):
    html = f'''<div class="seg escuro"><div id="{p}-post" class="post-f">
  <div class="post-h"><b>LessWrong</b><span>julho de 2010</span></div>
  <div class="post-u">postado por <b>Roko</b></div>
  <div class="post-t">Um experimento mental sobre uma IA do futuro</div>
  <div class="doc-linhas escuras">{"<i></i>" * 8}</div></div><div class="fonte">reconstituição · o post original foi apagado</div></div>'''
    tw = [f'tl.fromTo("#{p}-post",{{y:300,opacity:0,rotationX:30}},{{y:0,opacity:1,rotationX:0,duration:1,ease:"expo.out"}},{{t0}}+0.2);',
          f'tl.fromTo("#{p}-post",{{scale:1}},{{scale:1.12,duration:{{d}},ease:"none"}},{{t0}}+1);']
    return html, tw


def v_basilisco(p, s):
    txt = f'<div id="{p}-txt" class="frase baixo sombra">{palavras(s["texto"])}</div>' if s.get("texto") else ""
    html = f'''<div class="seg preto"><svg class="cheio" viewBox="0 0 1920 1080">
  <defs><radialGradient id="{p}-ir"><stop offset="0" stop-color="#000"/><stop offset=".35" stop-color="#000"/><stop offset=".4" stop-color="{VERMELHO}"/><stop offset="1" stop-color="#2a0505"/></radialGradient></defs>
  <g id="{p}-olho"><path d="M560 500 Q960 200 1360 500 Q960 800 560 500 Z" fill="#120a0a" stroke="{VERMELHO}" stroke-width="4"/>
  <circle cx="960" cy="500" r="190" fill="url(#{p}-ir)"/><ellipse id="{p}-pu" cx="960" cy="500" rx="22" ry="150" fill="#000"/></g>
  <rect id="{p}-pa" x="500" y="150" width="920" height="350" fill="#000"/><rect id="{p}-pb" x="500" y="500" width="920" height="350" fill="#000"/></svg>{txt}</div>'''
    tw = [f'tl.fromTo("#{p}-pa",{{y:0}},{{y:-360,duration:1.4,ease:"power2.inOut"}},{{t0}}+0.4);',
          f'tl.fromTo("#{p}-pb",{{y:0}},{{y:360,duration:1.4,ease:"power2.inOut"}},{{t0}}+0.4);',
          f'tl.fromTo("#{p}-pu",{{attr:{{rx:22}}}},{{attr:{{rx:8}},duration:0.6}},{{t0}}+1.8);',
          f'tl.fromTo("#{p}-olho",{{scale:1}},{{scale:1.25,svgOrigin:"960 500",duration:{{d}}+{XF},ease:"none"}},{{t0}});']
    if txt:
        tw.append(entra(f"#{p}-txt", "{t0}+1"))
    return html, tw


def v_proibido(p, s):
    copias = "".join(f'<div class="copia" id="{p}-c{i}" style="left:{(i * 397) % 1700}px;top:{(i * 263) % 900}px">post apagado · cópia {i+1}</div>' for i in range(24))
    html = f'''<div class="seg escuro">{copias}<div id="{p}-post" class="post-f pequeno"><div class="post-h"><b>LessWrong</b><span>2010</span></div>
  <div class="doc-linhas escuras">{"<i></i>" * 6}</div><div id="{p}-car" class="carimbo">APAGADO</div></div>
  <div id="{p}-anos" class="mono ban">ASSUNTO PROIBIDO POR 5 ANOS</div></div>'''
    tw = [surge(f"#{p}-post", "{t0}+0.1", 0.6),
          f'tl.fromTo("#{p}-car",{{scale:2.6,opacity:0,rotation:-24}},{{scale:1,opacity:1,rotation:-12,duration:0.25,ease:"power4.in"}},{{t0}}+1);',
          surge(f"#{p}-anos", "{t0}+1.6", 0.4, "opacity:0"),
          f'tl.fromTo("#{p} .copia",{{opacity:0,scale:0.6}},{{opacity:0.75,scale:1,duration:0.25,stagger:0.12}},{{t0}}+{{d}}*0.5);']
    return html, tw


def v_livro(p, s):
    html = f'''<div class="seg papel"><div id="{p}-l" class="livro"><div class="livro-a">Giancarlo Guizzardi</div>
  <div class="livro-t">Quem tem medo do robô mau?</div><div class="livro-r"><svg viewBox="0 0 200 200" width="200"><rect x="50" y="60" width="100" height="90" rx="12" fill="none" stroke="{TINTA}" stroke-width="6"/>
  <circle cx="80" cy="100" r="9" fill="{TINTA}"/><circle cx="120" cy="100" r="9" fill="{TINTA}"/><path d="M100 60 v-25" stroke="{TINTA}" stroke-width="6"/><circle cx="100" cy="30" r="7" fill="{TINTA}"/></svg></div></div>
  <div id="{p}-n" class="livro-nota"><div class="mono" style="color:{VERMELHO}">A IDEIA CENTRAL</div><div>separar o que a IA <b>faz</b><br>do que a gente <b>imagina</b> que ela faça</div>
  <div class="mono pq">formado na UFES</div></div><div class="fonte escura">capa ilustrativa, não é a capa do livro</div></div>'''
    tw = [f'tl.fromTo("#{p}-l",{{rotationY:-35,x:-200,opacity:0}},{{rotationY:-12,x:0,opacity:1,duration:1.2,ease:"expo.out"}},{{t0}}+0.2);',
          surge(f"#{p}-n", "{t0}+{d}*0.45", 0.7, "opacity:0,x:50")]
    return html, tw


def v_pessoas(p, s):
    grupos = ["laboratórios", "empresas", "plataformas"]
    gs = "".join(f'<div id="{p}-g{i}" class="grupo"><div class="silhuetas">{"<i></i>" * 3}</div><div>{g}</div></div>' for i, g in enumerate(grupos))
    html = f'''<div class="seg escuro"><div id="{p}-rob" class="robo-x"><svg viewBox="0 0 200 200" width="420"><rect x="50" y="60" width="100" height="90" rx="12" fill="none" stroke="{APOIO}" stroke-width="5"/>
  <circle cx="80" cy="100" r="9" fill="{VERMELHO}"/><circle cx="120" cy="100" r="9" fill="{VERMELHO}"/></svg></div><div class="grupos">{gs}</div></div>'''
    tw = [f'tl.fromTo("#{p}-rob",{{opacity:1}},{{opacity:0,scale:0.7,filter:"blur(12px)",duration:1}},{{t0}}+{{d}}*0.25);']
    tw += [surge(f"#{p}-g{i}", f"{{t0}}+{{d}}*{0.4 + i * 0.12:.2f}", 0.6, "opacity:0,y:50") for i in range(3)]
    return html, tw


def v_fechadura(p, s):
    icones = ""
    if s.get("fase") == "quatro":
        icones = "".join(f'<text id="{p}-i{i}" x="{x}" y="{y}" class="svg-grande" text-anchor="middle">{w}</text>'
                         for i, (w, x, y) in enumerate([("escrever", 400, 260), ("mapear", 1520, 260), ("ler", 400, 900), ("escolher", 1520, 900)]))
    html = f'''<div class="seg papel"><svg class="cheio" viewBox="0 0 1920 1080">
  <g id="{p}-f"><circle cx="960" cy="440" r="150" fill="{NANQUIM}"/><polygon points="890,520 1030,520 1080,820 840,820" fill="{NANQUIM}"/></g>{icones}</svg></div>'''
    tw = [f'tl.fromTo("#{p}-f",{{scale:0.7,opacity:0,svgOrigin:"960 600"}},{{scale:1,opacity:1,svgOrigin:"960 600",duration:0.8,ease:"expo.out"}},{{t0}}+0.1);']
    if icones:
        tw += [f'tl.fromTo("#{p}-i{i}",{{opacity:0}},{{opacity:1,duration:0.3}},{{t0}}+{{d}}*{0.05 + i * 0.12:.2f});' for i in range(4)]
    return html, tw


def v_direitos(p, s):
    ws = ["privacidade mental", "liberdade cognitiva", "integridade mental"]
    html = f'<div class="seg papel"><div class="direitos">' + "".join(f'<div id="{p}-d{i}">{w}</div>' for i, w in enumerate(ws)) + f'</div><div class="fonte escura">{s["fonte"]}</div></div>'
    tw = [f'tl.fromTo("#{p}-d{i}",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:0.4}},{{t0}}+{{d}}*{0.3+i*0.12:.2f});' for i in range(3)]
    return html, tw


def v_lista(p, s):
    its = "".join(f'<div id="{p}-l{i}" class="item"><span>✓</span>{t}</div>' for i, t in enumerate(s["itens"]))
    html = f'<div class="seg escuro"><div class="mono lista-t">O QUE NÓS DEFENDEMOS</div><div class="lista">{its}</div></div>'
    n = len(s["itens"])
    tw = [f'tl.fromTo("#{p}-l{i}",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:0.4,ease:"expo.out"}},{{t0}}+{{d}}*{0.1+i*0.8/n:.2f});' for i in range(n)]
    return html, tw


def v_onda(p, s):
    r = random.Random(3)
    barras = "".join(f'<rect class="b" x="{360+i*30}" y="300" width="16" height="160" rx="8" fill="{TINTA}" style="transform-origin:{368+i*30}px 380px"/>' for i in range(40))
    alt = [round(0.15 + r.random() * 0.85, 2) for _ in range(40)]
    txt = f'<div id="{p}-txt" class="frase baixo">{palavras(s["texto"])}</div>' if s.get("texto") else ""
    html = f'<div class="seg preto"><svg class="cheio" viewBox="0 0 1920 1080"><g id="{p}-ondas">{barras}</g></svg>{txt}</div>'
    tw = [f'tl.fromTo("#{p}-ondas .b",{{scaleY:0.1}},{{scaleY:function(i){{return {alt}[i];}},duration:0.18,stagger:0.02,repeat:15,yoyo:true}},{{t0}}+0.1);']
    if txt:
        tw.append(entra(f"#{p}-txt", "{t0}+0.4"))
    return html, tw


BASE = {k[2:]: v for k, v in list(globals().items()) if k.startswith("v_")}


# ---------------------------------------------------------------- por estilo
def d_camundongo(p, s):
    est = s.get("estado", "calma")
    sob, stw = sobre(p, s, True)
    if est == "vazia":
        return foto(p, "camundongo", sob, (1.15, 1.0), "grayscale(1) brightness(.6)")
    if est == "medo":
        html, tw = foto(p, "camundongo", f'<div id="{p}-v" class="cheio" style="background:{VERMELHO};mix-blend-mode:multiply;opacity:0"></div>{sob}', (1.35, 1.5), "contrast(1.2)")
        tw += [f'tl.fromTo("#{p}-v",{{opacity:0}},{{opacity:0.55,duration:0.12}},{{t0}}+0.5);',
               f'tl.fromTo("#{p}-kb",{{x:-6}},{{x:6,duration:0.05,repeat:24,yoyo:true,ease:"none"}},{{t0}}+0.5);']
        return html, tw + stw
    html, tw = foto(p, "camundongo", sob, (1.0, 1.18))
    return html, tw + stw


def d_neuronios(p, s):
    html, tw = foto(p, "neuronios", f'<div id="{p}-leg" class="legenda-g">{s["legenda"]}</div>', (1.0, 1.3))
    return html, tw + [surge(f"#{p}-leg", "{t0}+{d}*0.5", 0.6, "opacity:0")]


def d_hospital(p, s):
    return foto(p, "aparelho_rm", f'<div class="mono local">{s["local"]}</div><div class="fonte" style="bottom:96px">o aparelho, não a paciente</div>', (1.0, 1.15), "brightness(.7) saturate(.6)")


def d_cerebros(p, s):
    html, tw = foto(p, "ressonancia", f'<div id="{p}-q" class="frase baixo sombra">{palavras("“Imagine que você está jogando tênis.”")}</div>', (1.0, 1.2), "brightness(.8)")
    return html, tw + [entra(f"#{p}-q", "{t0}+0.4")]


def t_porta(p, s):
    txt, ttw = texto_baixo(p, s)
    h, tw = fundo_3d(p, "porta", {"fase": s.get("fase", "fechada")}, txt)
    return h, tw + ttw


def t_neuronios(p, s):
    h, tw = fundo_3d(p, "neuronios", {}, f'<div id="{p}-leg" class="legenda-g">{s["legenda"]}</div>')
    return h, tw + [surge(f"#{p}-leg", "{t0}+{d}*0.55", 0.6, "opacity:0")]


def t_conectoma(p, s):
    nh, ntw = numeros(p, s)
    leg = f'<div class="legenda-b">neurônios do sabor <span style="color:{CIANO}">→</span> neurônios que movem a boca</div>' if s.get("modo") == "simula" else ""
    h, tw = fundo_3d(p, "conectoma", {"modo": s.get("modo", "mapa")}, nh + leg)
    return h, tw + ntw


def t_simulacao(p, s):
    extra = f'<div id="{p}-v" class="mono voce">VOCÊ ESTÁ AQUI?</div>' if s.get("fase") == "revela" else ""
    h, tw = fundo_3d(p, "simulacao", {"fase": s.get("fase", "mundo")}, extra)
    return h, tw + ([surge(f"#{p}-v", "{t0}+{d}*0.55", 0.5, "opacity:0")] if extra else [])


def t_multiplica(p, s):
    uma = s.get("fase") == "uma"
    extra = (f'<div class="legenda-b"><span style="color:{CIANO}">● simuladas</span>   <span style="color:{AMBAR}">● real</span></div>' if uma
             else f'<div id="{p}-n" class="contador">1</div>')
    h, tw = fundo_3d(p, "multiplica", {"fase": "uma" if uma else "cresce"}, extra)
    if not uma:
        tw.append(f'(function(){{var o={{v:0}};tl.fromTo(o,{{v:0}},{{v:3,duration:{{d}}-1,ease:"none",onUpdate:function(){{var e=1+2*o.v/3;document.querySelector("#{p}-n").textContent=Math.round(Math.min(729,Math.pow(9,e))).toLocaleString("pt-BR")+" mentes";}}}},{{t0}}+0.5);}})();')
    return h, tw


def t_servidores(p, s):
    h, tw = fundo_3d(p, "servidores", {}, f'<div id="{p}-q" class="frase baixo sombra">{palavras("Quem guarda esses dados?")}</div>')
    return h, tw + [entra(f"#{p}-q", "{t0}+{d}*0.3")]


def m_ruptura(p, s):
    return video(p, s, "ruptura")


def m_matrix(p, s):
    return video(p, s, "matrix")


def m_trio_ficcao(p, s):
    t0, d = s["_t0"], s["_d"] + XF
    for k, (chave, ms) in enumerate((("ruptura", 39), ("matrix", 84))):
        s["_soltos"].append(f'<video id="{p}-pv{k}" class="clip pv" src="{TRAILER[chave][0]}" muted data-start="{t0:.2f}" data-duration="{d:.2f}" '
                            f'data-media-start="{ms}" style="left:{k * 640}px;width:640px"></video>')
    html, tw = v_trio_ficcao(p, s, ("", "", ICONES[2]))
    html = html.replace('class="seg preto"', 'class="seg"').replace(f'id="{p}-p0" class="painel"', f'id="{p}-p0" class="painel vazado"') \
               .replace(f'id="{p}-p1" class="painel"', f'id="{p}-p1" class="painel vazado"')
    return html, tw


DOC = {k[2:]: v for k, v in list(globals().items()) if k.startswith("d_")}
TRES = {k[2:]: v for k, v in list(globals().items()) if k.startswith("t_")}
MISTO = {k[2:]: v for k, v in list(globals().items()) if k.startswith("m_")}


def visual(a):
    if ESTILO == "doc":
        return DOC.get(a) or BASE[a]
    if ESTILO == "3d":
        return TRES.get(a) or BASE[a]
    return MISTO.get(a) or TRES.get(a) or DOC.get(a) or BASE[a]


def rotulo_html(chave, escuro_fundo=True):
    r = ROTULO.get(chave)
    if not r:
        return ""
    return f'<div class="rotulo" style="color:{r[1]};border-color:{r[1]}">{r[0]}</div>'


CSS = f"""
#root{{position:absolute;inset:0;overflow:hidden;background:{ESCURO};font-family:"Inter",sans-serif}}
.seg{{position:absolute;inset:0;overflow:hidden}}
.escuro{{background:{ESCURO};color:{TINTA}}} .papel{{background:{PAPEL};color:{NANQUIM}}} .preto{{background:#000;color:{TINTA}}}
.cheio{{position:absolute;inset:0;width:100%;height:100%}} .cam{{position:absolute;inset:0;transform-origin:50% 55%}}
.kb{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:50% 50%}}
.vid{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}} .pv{{position:absolute;top:0;height:100%;object-fit:cover}}
.sombra-b{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.35) 0%,rgba(0,0,0,0) 30%,rgba(0,0,0,0) 55%,rgba(0,0,0,.75) 100%)}}
.credito{{position:absolute;left:72px;bottom:40px;font:400 20px "IBM Plex Mono",monospace;color:rgba(238,241,247,.6)}}
.faixa-fic{{position:absolute;right:72px;bottom:44px;font:400 24px "IBM Plex Mono",monospace;color:{AMBAR};background:rgba(0,0,0,.6);padding:8px 14px}}
.centro{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:36px;text-align:center;padding:0 200px}}
.meio{{position:absolute;left:180px;right:180px;top:50%;transform:translateY(-50%);text-align:center}}
.baixo{{position:absolute;left:180px;right:180px;bottom:120px;text-align:center}}
.sombra{{text-shadow:0 4px 30px rgba(0,0,0,.9)}}
.frase{{font-family:"EB Garamond",serif;font-size:84px;line-height:1.12;font-weight:500}} .frase-p{{font-size:68px}}
.frase-g{{font-family:"EB Garamond",serif;font-size:150px;line-height:1.05;font-weight:700;letter-spacing:-0.01em}}
.pal{{display:inline-block}}
.mono{{font-family:"IBM Plex Mono",monospace;letter-spacing:.2em;font-size:30px}}
.sobre{{position:absolute;left:0;right:0;top:70px;text-align:center;color:#5d5446}} .sobre.claro{{color:{TINTA};text-shadow:0 2px 12px #000}}
.titulo-filme{{font-family:"EB Garamond",serif;font-size:112px;font-weight:700;letter-spacing:.1em;color:{TINTA}}}
.titulo-linha{{width:900px;height:3px;background:{AMBAR};transform-origin:left}}
.rotulo{{position:absolute;left:72px;top:60px;font:500 28px "IBM Plex Mono",monospace;letter-spacing:.18em;border:2px solid;padding:10px 18px;z-index:5;background:rgba(11,13,18,.82)}}
.fonte{{position:absolute;right:72px;bottom:56px;font:400 26px "IBM Plex Mono",monospace;color:{APOIO}}} .fonte.escura{{color:#5d5446}}
.doc{{position:absolute;left:560px;top:110px;width:800px;height:860px;background:#fbf8f1;box-shadow:0 30px 60px rgba(0,0,0,.25);padding:64px;color:{NANQUIM}}}
.doc-topo{{display:flex;justify-content:space-between;font:600 28px "IBM Plex Mono",monospace;border-bottom:4px solid {NANQUIM};padding-bottom:16px;margin-bottom:40px}}
.doc-linhas i{{display:block;height:14px;background:#dcd5c6;margin:0 0 22px;border-radius:4px}} .doc-linhas i:nth-child(3n){{width:70%}}
.doc-linhas.escuras i{{background:#2c3342}}
.pagina{{position:absolute;left:150px;top:90px;width:760px;height:900px;overflow:hidden;background:#fff;box-shadow:0 40px 80px rgba(0,0,0,.35)}}
.pagina img{{width:100%;display:block;transform-origin:50% 0}} .pagina.falsa{{padding:60px}}
.ficha{{position:absolute;left:1010px;top:200px;width:780px;color:{NANQUIM}}}
.ficha-r{{color:{VERMELHO};margin-bottom:30px;font-size:28px}}
.ficha-t{{position:relative;font:700 60px/1.12 "EB Garamond",serif;margin-bottom:30px}}
.marca{{position:absolute;left:-12px;right:-12px;top:6px;bottom:0;background:{AMBAR};opacity:.45;transform-origin:left;z-index:0}} .tt{{position:relative;z-index:1}}
.ficha-a{{font:italic 36px "EB Garamond",serif;color:#4a443a}}
.retrato{{display:flex;align-items:center;gap:26px;margin-top:50px}} .retrato img{{width:170px;height:170px;object-fit:cover;border-radius:50%;filter:grayscale(.3)}}
.retrato span{{font:600 34px "EB Garamond",serif}} .retrato i{{font:400 18px "IBM Plex Mono",monospace;color:#7a705e;font-style:normal}}
.carimbo{{position:absolute;right:40px;top:380px;font:700 50px "IBM Plex Mono",monospace;color:{VERMELHO};border:6px solid {VERMELHO};padding:12px 22px;transform:rotate(-12deg);background:rgba(251,248,241,.7)}}
.svg-leg{{font:500 40px "IBM Plex Mono",monospace;fill:{NANQUIM}}} .escuro .svg-leg{{fill:{TINTA}}}
.svg-grande{{font:700 64px "EB Garamond",serif;fill:{NANQUIM}}}
.contrato .ass{{display:flex;justify-content:space-between;font:400 40px "EB Garamond",serif;border-top:2px solid #cfc6b4;padding:26px 0}}
.ok{{color:#177a3c}} .nao{{color:{VERMELHO}}}
.ress{{position:absolute;left:300px;right:300px;top:50%;transform:translateY(-50%)}}
.ress-t{{color:{VERMELHO};margin-bottom:40px}} .ress-l{{font:500 56px/1.25 "EB Garamond",serif;margin-bottom:28px}} .ress-l span{{color:{VERMELHO};margin-right:24px}}
.pasta{{position:absolute;left:460px;top:180px;width:1000px;height:720px}}
.aba{{width:360px;height:70px;background:#b99b62;border-radius:14px 14px 0 0;font:700 32px "IBM Plex Mono",monospace;color:#2b2112;padding:16px 30px;letter-spacing:.15em}}
.pasta-c{{height:650px;background:#caa96c;border-radius:0 14px 14px 14px;padding:80px;color:#2b2112;box-shadow:0 30px 80px rgba(0,0,0,.5)}}
.pasta-nome{{font:700 170px "EB Garamond",serif;margin-top:60px}}
.citacao{{font:italic 500 76px/1.2 "EB Garamond",serif;max-width:1400px}} .fonte-c{{font:400 30px "IBM Plex Mono",monospace;color:{APOIO}}}
.local{{position:absolute;left:72px;bottom:60px;color:{APOIO}}}
.tela-mock{{position:absolute;left:360px;top:160px;width:1200px;height:740px;background:#fbf8f1;border:14px solid #2a2e38;border-radius:24px}}
.alvo{{position:absolute;right:300px;top:200px;width:140px;height:140px;border-radius:50%;border:10px solid {CIANO}}}
.cursor{{position:absolute;left:600px;top:370px;width:0;height:0;border-left:30px solid transparent;border-right:30px solid transparent;border-bottom:70px solid {NANQUIM};rotate:-30deg}}
.fones{{position:absolute;left:260px;top:170px;display:flex;gap:100px}}
.fone{{width:420px;height:800px;background:#151922;border:10px solid #2a3040;border-radius:50px;padding:50px 34px;display:flex;flex-direction:column;gap:22px}} .fone .mono{{font-size:24px;letter-spacing:.05em;color:{APOIO}}}
.post{{height:110px;border-radius:14px}}
.data-topo{{position:absolute;left:0;right:0;top:80px;text-align:center;color:{APOIO}}}
.num-lado{{position:absolute;right:140px;top:430px;font:700 110px "EB Garamond",serif;text-align:right}} .num-lado span{{display:block;font:400 30px "IBM Plex Mono",monospace;color:{APOIO}}}
.termos{{position:absolute;left:560px;top:0;width:800px;height:1080px;overflow:hidden;background:#141821}}
.rol i{{display:block;height:12px;background:#2c3342;margin:24px 50px;border-radius:4px}} .rol i:nth-child(4n){{width:55%}}
.aceito{{position:absolute;left:0;right:0;bottom:120px;text-align:center;font:500 46px "Inter",sans-serif}}
.direitos{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:30px;font:700 104px "EB Garamond",serif}}
.lista-t{{position:absolute;left:300px;top:150px;color:{CIANO}}}
.lista{{position:absolute;left:300px;right:300px;top:54%;transform:translateY(-50%);display:flex;flex-direction:column;gap:44px}}
.item{{font:500 68px "EB Garamond",serif}} .item span{{color:{CIANO};margin-right:30px}}
.perg{{position:absolute;left:300px;right:200px;top:200px}} .perg-t{{color:{AMBAR};margin-bottom:60px}}
.perg-l{{font:600 96px/1.15 "EB Garamond",serif;margin-bottom:18px}} .perg-l span{{font:400 30px "IBM Plex Mono",monospace;color:{APOIO};margin-right:36px;vertical-align:middle}}
.trio{{position:absolute;inset:0;display:flex}} .painel{{flex:1;position:relative;overflow:hidden;border-right:2px solid #1a1d24;background:#0b0d12}}
.painel-c{{position:absolute;left:50px;right:40px;bottom:110px;text-shadow:0 2px 20px #000}} .painel-c .mono{{color:{AMBAR}}}
.painel-n{{font:700 76px "EB Garamond",serif;margin:14px 0}} .painel-l{{font:italic 40px "EB Garamond",serif;color:#cfd5e2}}
.icone{{position:absolute;left:120px;top:180px;width:400px;height:400px;opacity:.85}}
.painel.vazado{{background:linear-gradient(180deg,rgba(0,0,0,0) 40%,rgba(0,0,0,.85) 100%)}}
.mesa{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 60%,#2a2116 0%,#0b0d12 70%)}}
.mini-pasta{{position:absolute;width:250px;box-shadow:0 20px 40px rgba(0,0,0,.6)}} .mini-aba{{width:100px;height:28px;background:#b99b62;border-radius:8px 8px 0 0}}
.mini-c{{height:300px;background:#caa96c;border-radius:0 8px 8px 8px;padding:30px 22px;font:700 26px "IBM Plex Mono",monospace;color:#2b2112;letter-spacing:.06em}}
.trauma-w{{position:absolute;top:300px;width:440px;text-align:center;font:italic 600 80px "EB Garamond",serif}}
.remedio{{position:absolute;left:1080px;top:340px;width:700px}} .remedio-n{{font:700 120px "EB Garamond",serif}} .remedio-l{{font:400 44px/1.3 "EB Garamond",serif;color:#4a443a}}
.placar{{position:absolute;left:260px;right:260px;top:230px}} .placar-l{{display:flex;gap:50px;align-items:baseline;border-top:3px solid #cfc6b4;padding:40px 0}}
.placar-l b{{font:700 80px "EB Garamond",serif;width:200px}} .placar-l span{{font:400 46px "EB Garamond",serif;flex:1}} .placar-l i{{font:600 46px "EB Garamond",serif;font-style:normal}}
.placar-x{{margin-top:50px;font:italic 60px "EB Garamond",serif;color:{VERMELHO};text-align:center}}
.decide{{position:absolute;width:600px;text-align:center;font:600 76px "EB Garamond",serif}} .decide-t{{position:absolute;left:0;right:0;top:80px;text-align:center;color:{AMBAR}}}
.legenda-g{{position:absolute;left:0;right:0;bottom:120px;text-align:center;font:700 120px "EB Garamond",serif;color:{CIANO};text-shadow:0 4px 30px #000}}
.legenda-b{{position:absolute;left:0;right:0;bottom:80px;text-align:center;font:400 36px "IBM Plex Mono",monospace;color:{TINTA};text-shadow:0 2px 12px #000}}
.nums{{position:absolute;right:110px;top:250px;text-align:right;text-shadow:0 4px 30px #000}} .nums b{{display:block;font:700 130px/1 "EB Garamond",serif}}
.nums span{{display:block;font:400 32px "IBM Plex Mono",monospace;color:{CIANO};margin:8px 0 50px}}
.fatias{{position:absolute;left:260px;top:330px;width:700px;height:520px}} .fatia{{position:absolute;inset:0;background:rgba(90,209,198,.08);border:2px solid rgba(90,209,198,.5);transform-origin:50% 50%}}
.scan{{position:absolute;left:-30px;right:-30px;top:0;height:4px;background:{AMBAR};box-shadow:0 0 30px {AMBAR}}}
.passos{{position:absolute;left:1130px;top:330px;display:flex;flex-direction:column;gap:70px;font:600 58px "EB Garamond",serif}}
.comp{{position:absolute;left:200px;right:200px;top:290px}} .comp-l{{margin-bottom:80px}} .comp-l span{{font:400 34px "IBM Plex Mono",monospace;color:{APOIO}}}
.barra{{height:60px;background:#151922;margin:16px 0}} .barra i{{display:block;height:100%}} .comp-l b{{font:700 90px "EB Garamond",serif}}
.comp-nota{{color:{APOIO};font-size:24px}}
.quatro-n{{position:absolute;left:0;right:0;top:120px;text-align:center;font:700 130px "EB Garamond",serif;color:{VERMELHO}}}
.voce{{position:absolute;left:0;right:0;bottom:100px;text-align:center;color:{AMBAR};font-size:40px;text-shadow:0 2px 12px #000}}
.col{{position:absolute;top:0;width:40px;font:400 40px/1.1 "IBM Plex Mono",monospace;color:#3fd16a;text-shadow:0 0 12px #2fa04f;word-break:break-all;opacity:.85}}
.contador{{position:absolute;left:50%;top:40px;transform:translateX(-50%);padding:4px 34px;background:rgba(11,13,18,.88);white-space:nowrap;font:700 96px "EB Garamond",serif;color:{TINTA};text-shadow:0 4px 30px #000}}
.tri-t{{position:absolute;left:0;right:0;top:150px;text-align:center;color:{LILAS}}} .tris{{position:absolute;left:150px;right:150px;top:300px;display:flex;gap:50px}}
.tri{{flex:1;border:3px solid rgba(167,139,250,.25);padding:50px 40px;font:500 52px/1.2 "EB Garamond",serif;min-height:460px}} .tri b{{display:block;font:700 90px "EB Garamond",serif;color:{LILAS}}}
.post-f{{position:absolute;left:460px;top:200px;width:1000px;background:#151922;border:2px solid #2a3040;border-radius:16px;padding:50px;transform-origin:50% 50%}}
.post-f.pequeno{{left:560px;top:260px;width:800px}}
.post-h{{display:flex;justify-content:space-between;font:400 28px "IBM Plex Mono",monospace;color:{APOIO};margin-bottom:30px}} .post-h b{{color:{TINTA}}}
.post-u{{font:400 32px "Inter",sans-serif;color:{APOIO};margin-bottom:20px}} .post-u b{{color:{AMBAR}}}
.post-t{{font:700 64px/1.15 "EB Garamond",serif;margin-bottom:40px}}
.copia{{position:absolute;font:400 22px "IBM Plex Mono",monospace;color:{APOIO};border:1px solid #2a3040;padding:10px 14px;background:#11141b}}
.ban{{position:absolute;left:0;right:0;bottom:130px;text-align:center;color:{VERMELHO}}}
.livro{{position:absolute;left:300px;top:160px;width:540px;height:760px;background:#1b2433;color:{TINTA};padding:60px 50px;box-shadow:30px 40px 80px rgba(0,0,0,.35);transform-origin:0 50%}}
.livro-a{{font:400 30px "IBM Plex Mono",monospace;letter-spacing:.1em;color:{AMBAR}}} .livro-t{{font:700 76px/1.08 "EB Garamond",serif;margin:50px 0}}
.livro-r{{position:absolute;bottom:50px;right:50px}}
.livro-nota{{position:absolute;left:1000px;top:330px;width:760px;font:500 58px/1.25 "EB Garamond",serif}} .livro-nota .mono{{margin-bottom:30px}} .livro-nota .pq{{margin-top:40px;color:#5d5446;font-size:26px}}
.robo-x{{position:absolute;left:0;right:0;top:250px;display:flex;justify-content:center}}
.grupos{{position:absolute;left:150px;right:150px;top:330px;display:flex;justify-content:space-around;font:600 64px "EB Garamond",serif;text-align:center}}
.silhuetas{{display:flex;gap:16px;justify-content:center;margin-bottom:30px}} .silhuetas i{{width:80px;height:220px;background:#2a3040;border-radius:40px 40px 10px 10px}}
"""


def grain_vinheta(total):
    n = max(1, int(total / 0.5))
    return f"""<div id="grain-overlay" style="position:absolute;inset:0;pointer-events:none;z-index:100;overflow:hidden"><div class="grain-texture"></div></div>
      <div id="hf-vignette" style="position:absolute;inset:0;pointer-events:none;z-index:90"></div>
      <style>
        @keyframes hf-grain-noise {{0%,100%{{transform:translate(0,0)}}10%{{transform:translate(-5%,-5%)}}20%{{transform:translate(-10%,5%)}}30%{{transform:translate(5%,-10%)}}40%{{transform:translate(-5%,15%)}}50%{{transform:translate(-10%,5%)}}60%{{transform:translate(15%,0)}}70%{{transform:translate(0,10%)}}80%{{transform:translate(-15%,0)}}90%{{transform:translate(10%,5%)}}}}
        #grain-overlay .grain-texture{{position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");opacity:.11;animation:hf-grain-noise .5s steps(1) {n} both}}
        #hf-vignette{{background:radial-gradient(ellipse at center,transparent 50%,rgba(0,0,0,.6) 100%)}}
      </style>"""


def gerar():
    tp = tempos()
    os.makedirs(os.path.join(AQUI, "compositions"), exist_ok=True)
    hosts, audios, inicio = [], [], 0.0
    sem_rotulo = ("frase", "porta", "titulo", "flash", "onda", "arquivo", "pergunta", "arquivos_mesa")
    for cena, _, segs in CENAS:
        partes, tweens = [], []
        dur = tp[cena][-1][0] + tp[cena][-1][1]
        for i, (_, _, vis) in enumerate(segs):
            if V3 and (cena, i) in SUBST:
                vis = SUBST[(cena, i)]
            t0, d = tp[cena][i]
            p = f"{cena}-s{i}"
            vis = dict(vis, _t0=t0, _d=d, _soltos=[])
            html, tw = visual(vis["a"])(p, vis)
            partes += vis["_soltos"]
            rot = rotulo_html(vis.get("r")) if vis["a"] not in sem_rotulo or vis.get("r") else ""
            dd = d + (XF if i < len(segs) - 1 else 0)
            partes.append(f'<div id="{p}" class="clip" data-start="{t0:.2f}" data-duration="{dd:.2f}">{html}{rot}</div>')
            if i:
                tweens.append(f'tl.fromTo("#{p}",{{opacity:0}},{{opacity:1,duration:{XF},ease:"none"}},{t0:.2f});')
            tweens += [x.replace("{t0}", f"{t0:.2f}").replace("{d}", f"{d:.2f}") for x in tw]
        # entra e sai do preto na troca de cena
        tweens += [f'tl.fromTo("#{cena}-preto",{{opacity:1}},{{opacity:0,duration:0.6,ease:"none"}},0);',
                   f'tl.to("#{cena}-preto",{{opacity:1,duration:0.5,ease:"none"}},{dur - 0.5:.2f});']
        js = "\n    ".join(tweens)
        open(os.path.join(AQUI, f"compositions/{cena}.html"), "w").write(f"""<template>
  <style>{CSS}
  .preto-cena{{position:absolute;inset:0;background:#000;z-index:50;pointer-events:none}}</style>
  <div id="root" data-composition-id="{cena}" data-width="{W}" data-height="{H}">
    {chr(10).join(partes)}
    <div id="{cena}-preto" class="preto-cena"></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {js}
    window.__timelines["{cena}"] = tl;
  </script>
</template>
""")
        hosts.append(f'<div id="{cena}" data-composition-id="{cena}" data-composition-src="compositions/{cena}.html" data-start="{inicio:.2f}" data-duration="{dur:.2f}" data-track-index="1" data-width="{W}" data-height="{H}"></div>')
        if os.path.exists(os.path.join(AQUI, f"assets/voz/{cena}.wav")):
            audios.append(f'<audio id="voz-{cena}" src="assets/voz/{cena}.wav" data-start="{inicio:.2f}" data-duration="{dur:.2f}" data-track-index="2" data-volume="1"></audio>')
        inicio += dur
    if os.path.exists(os.path.join(AQUI, MUSICA)):
        audios.append(f'<audio id="musica" src="{MUSICA}" data-start="0" data-duration="{inicio:.2f}" data-track-index="3" data-volume="0.14" data-fade-in="2" data-fade-out="3"></audio>')
    three = '<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>\n    <script src="assets/r3.js"></script>' if ESTILO != "doc" else ""
    open(os.path.join(AQUI, "index.html"), "w").write(f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    {three}
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: {ESCURO}; }}
      #root {{ width: 100%; height: 100%; position: relative; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{inicio:.2f}" data-width="{W}" data-height="{H}">
      {(chr(10) + "      ").join(hosts + audios)}
      {grain_vinheta(inicio)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""")
    return inicio


if __name__ == "__main__":
    total = gerar()
    print(f"[{ESTILO}] duração total: {total:.1f} s ({total/60:.1f} min)", "(estimada)" if not os.path.exists(DUR_JSON) else "(voz real)")
