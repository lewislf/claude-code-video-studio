"""Peças da segunda rodada da cena A, depois da crítica: mosca que parece mosca, cérebro de verdade, mapa e profundidade."""
import json, math, random
from build import CIANO, MAGENTA, AMBAR, MENTA, LILAS, INFO, caminho


def mosca_defs(pre):
    return f"""<linearGradient id="{pre}-abd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e3b274"/><stop offset="1" stop-color="#b57a3c"/></linearGradient>
<radialGradient id="{pre}-tor" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#eab36b"/><stop offset="1" stop-color="#a5672b"/></radialGradient>
<radialGradient id="{pre}-olho" cx="38%" cy="30%" r="85%"><stop offset="0" stop-color="#ff7a8c"/><stop offset=".55" stop-color="#e0304f"/><stop offset="1" stop-color="#8a1030"/></radialGradient>
<linearGradient id="{pre}-asa" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eef7ff" stop-opacity=".9"/><stop offset="1" stop-color="#a8c8ff" stop-opacity=".3"/></linearGradient>"""


def mosca_rica(p, pre="A"):
    """Mosca-da-fruta de perfil, voltada para a direita. Caixa local ~ -150..140 x -110..90."""
    facetas = "".join(f'<circle cx="{76 + dx}" cy="{-6 + dy}" r="3" fill="#7a0e28" opacity=".5"/>' for dx in (-14, -5, 4, 13, 22) for dy in (-22, -12, -2, 8, 18) if (dx - 4) ** 2 + (dy - 2) ** 2 < 420)
    cerdas = "".join(f'<path d="M{-4 + k * 9} {-34 - (k % 2) * 2} l{1 + k % 3} -8"/>' for k in range(8))
    contorno = 'stroke="#5a3418" stroke-width="3" stroke-linejoin="round"'
    return f"""<g id="{p}">
<g id="{p}-asas">
<ellipse cx="-34" cy="-66" rx="112" ry="24" fill="url(#{pre}-asa)" transform="rotate(-14 -20 -62)" stroke="#fff" stroke-opacity=".65" stroke-width="2.6"/>
<path d="M-120 -50 L 70 -96 M -100 -56 L 40 -86" stroke="#fff" stroke-opacity=".5" stroke-width="2.4" fill="none"/>
<ellipse cx="-20" cy="-56" rx="96" ry="18" fill="url(#{pre}-asa)" opacity=".6" transform="rotate(-6 -10 -54)"/></g>
<g stroke="#7a5532" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" fill="none"><path d="M-10 30 L-22 58 L-44 78"/><path d="M12 34 L16 62 L8 90"/><path d="M38 28 L56 54 L84 66"/><path d="M-36 34 L-54 60 L-80 72"/></g>
<path d="M-150 8 C-150 -16 -110 -30 -60 -30 C-14 -30 8 -16 8 6 C8 26 -20 36 -62 36 C-116 36 -150 28 -150 8 Z" fill="url(#{pre}-abd)" {contorno}/>
<path d="M-132 -6 Q-124 8 -132 24 M-112 -18 Q-102 6 -112 32 M-92 -24 Q-82 6 -92 34 M-72 -28 Q-62 6 -72 36" stroke="#4a2c14" stroke-width="5" fill="none" stroke-linecap="round" opacity=".85"/>
<ellipse cx="-66" cy="-18" rx="62" ry="6" fill="#fff" opacity=".28"/>
<ellipse cx="16" cy="-6" rx="48" ry="40" fill="url(#{pre}-tor)" {contorno}/><g stroke="#4a2c14" stroke-width="2.4" fill="none" stroke-linecap="round" opacity=".7">{cerdas}</g>
<ellipse cx="2" cy="-26" rx="26" ry="8" fill="#fff" opacity=".22"/>
<g id="{p}-cab"><circle id="{p}-cabC" cx="68" cy="-4" r="38" fill="url(#{pre}-tor)" {contorno}/>
<path d="M88 -36 Q112 -64 138 -58" stroke="#4a2c14" stroke-width="5" fill="none" stroke-linecap="round"/><circle cx="140" cy="-58" r="6" fill="#4a2c14"/>
<g id="{p}-olhoG"><ellipse id="{p}-olho" cx="76" cy="-8" rx="31" ry="33" fill="url(#{pre}-olho)" stroke="#5a1028" stroke-width="3"/>{facetas}
<ellipse cx="88" cy="-22" rx="10" ry="8" fill="#fff" opacity=".8"/><ellipse cx="62" cy="6" rx="5" ry="4" fill="#fff" opacity=".35"/></g>
<ellipse id="{p}-cerebro" cx="58" cy="-4" rx="10" ry="9" fill="#3be0ff" opacity="0"/>
<path id="{p}-prob" d="M104 10 q 14 6 20 20" stroke="#4a2c14" stroke-width="7" fill="none" stroke-linecap="round"/></g></g>"""


def cerebro_card(p, gl="A-glow", cer="A-cer"):
    """Cérebro de mosca (dois lóbulos ópticos e o centro), desenhado em torno de (0,0), largura ~ 420."""
    dobras = ('<g fill="none" stroke="#9af0ff" stroke-width="5" stroke-linecap="round" opacity=".95">'
              '<path d="M-190 -20 C-160 -62 -128 -6 -96 -50 S -40 -28 -20 -64"/><path d="M-196 24 C-160 -4 -128 46 -92 12 S -36 36 -14 8"/>'
              '<path d="M-170 66 C-140 44 -110 82 -76 58 S -30 70 -10 52"/><path d="M190 -20 C160 -62 128 -6 96 -50 S 40 -28 20 -64"/>'
              '<path d="M196 24 C160 -4 128 46 92 12 S 36 36 14 8"/><path d="M170 66 C140 44 110 82 76 58 S 30 70 10 52"/>'
              '<path d=""/></g>')
    sil = "M-210 10 C-220 -50 -170 -100 -110 -96 C-80 -116 -30 -112 0 -104 C30 -112 80 -116 110 -96 C170 -100 220 -50 210 10 C210 60 160 96 100 90 C60 104 20 100 0 92 C-20 100 -60 104 -100 90 C-160 96 -210 60 -210 10 Z"
    return (f'<g id="{p}"><clipPath id="{p}-cp"><path transform="scale(1 1.38)" d="{sil}"/></clipPath><g filter="url(#{gl})"><path transform="scale(1 1.38)" vector-effect="non-scaling-stroke" d="{sil}" fill="url(#{cer})" stroke="#6ad8ff" stroke-width="7" stroke-linejoin="round"/></g>'
            f'<g clip-path="url(#{p}-cp)"><g transform="scale(1 1.38)">{dobras}</g></g></g>')


def curva(pontos, n=60):
    """Amostra uma sequência de bézier cúbicas [(p0,c1,c2,p1), ...] em n pontos por segmento."""
    out = []
    for (p0, c1, c2, p1) in pontos:
        for k in range(n):
            t = k / n
            u = 1 - t
            x = u ** 3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * p1[0]
            y = u ** 3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * p1[1]
            out.append((round(x, 1), round(y, 1)))
    out.append(pontos[-1][3])
    return out


ROSA, ROSA_E = "#ff9fa8", "#d8657a"
CIRC_NUVEM = [(-130, -50, 124), (-30, -118, 116), (84, -96, 108), (146, -14, 96), (-150, 70, 108), (-52, 108, 104), (60, 92, 96)]


def prismo_cabeca(p):
    """Cabeça de perfil (voltada à direita) inspirada no Prismo: rosa chapado, copa em nuvem, um olho azul grande, pescoço fino.
    Caixa local ~ x -290..215, y -250..250; o pescoço desce até y 900."""
    borda = "".join(f'<circle cx="{x}" cy="{y}" r="{r + 7}"/>' for x, y, r in CIRC_NUVEM)
    cheio = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in CIRC_NUVEM)
    rosto = "M 70 30 C 130 24 172 50 204 96 L 212 110 C 196 124 176 126 164 134 C 180 150 178 172 162 186 C 172 204 160 224 128 236 L 20 246 L -40 120 Z"
    return f"""<g id="{p}">
<linearGradient id="{p}-fade" gradientUnits="userSpaceOnUse" x1="0" y1="240" x2="0" y2="1000"><stop offset="0" stop-color="{ROSA}"/><stop offset=".6" stop-color="{ROSA}" stop-opacity=".7"/><stop offset="1" stop-color="{ROSA}" stop-opacity="0"/></linearGradient>
<path d="M 8 240 C 20 420 -30 520 20 640 C 50 720 0 820 30 940" fill="none" stroke="url(#{p}-fade)" stroke-width="26" stroke-linecap="round"/>
<path d="M 30 300 C 160 330 260 420 330 360 L 360 330" fill="none" stroke="url(#{p}-fade)" stroke-width="16" stroke-linecap="round"/>
<g fill="{ROSA_E}">{borda}</g><path d="{rosto}" fill="{ROSA_E}" stroke="{ROSA_E}" stroke-width="12" stroke-linejoin="round"/>
<g fill="{ROSA}">{cheio}</g><path d="{rosto}" fill="{ROSA}"/>
<path d="M 60 40 C 90 20 130 24 150 44" fill="none" stroke="{ROSA_E}" stroke-width="8" stroke-linecap="round"/>
<g id="{p}-olho"><ellipse cx="104" cy="74" rx="40" ry="24" fill="#0a0820"/><circle cx="112" cy="74" r="17" fill="#29b6ff"/><circle cx="118" cy="68" r="5.5" fill="#e8fbff"/></g>
<path d="M 176 168 Q 196 172 202 160" fill="none" stroke="{ROSA_E}" stroke-width="7" stroke-linecap="round"/>
</g>"""


def prismo_humano(p):
    """Perfil humano (voltado à direita) no estilo chapado do Prismo: pele rosa, copa em nuvem, olho azul com pálpebra preta.
    Mesma geometria do perfil aprovado (cabeca_E em build.py): caixa local ~ 600x720, nariz em (600,390)."""
    contorno = ("M 214 720 C 206 650 186 600 150 548 C 84 462 76 330 126 226 C 178 118 286 62 386 84 "
                "C 478 104 530 168 536 246 L 546 276 C 552 294 548 306 540 316 L 600 380 C 608 390 604 400 592 402 "
                "L 556 404 L 560 426 L 544 440 L 560 456 C 566 490 556 520 528 540 C 506 554 478 558 458 560 "
                "L 452 584 C 450 640 456 680 462 720 Z")
    bump = []
    for k in range(10):
        t = math.radians(188 + k * 16.5)
        bump.append((round(330 + 205 * math.cos(t)), round(238 + 158 * math.sin(t)), 50 if k % 2 else 44))
    borda = "".join(f'<circle cx="{x}" cy="{y}" r="{r + 6}"/>' for x, y, r in bump)
    cheio = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in bump)
    return f"""<g id="{p}">
<linearGradient id="{p}-pele" gradientUnits="userSpaceOnUse" x1="0" y1="500" x2="0" y2="720"><stop offset="0" stop-color="{ROSA}"/><stop offset="1" stop-color="{ROSA}" stop-opacity="0"/></linearGradient>
<linearGradient id="{p}-tr" gradientUnits="userSpaceOnUse" x1="0" y1="500" x2="0" y2="720"><stop offset="0" stop-color="{ROSA_E}"/><stop offset="1" stop-color="{ROSA_E}" stop-opacity="0"/></linearGradient>
<g fill="{ROSA_E}">{borda}</g>
<path d="{contorno}" fill="url(#{p}-pele)" stroke="url(#{p}-tr)" stroke-width="8" stroke-linejoin="round"/>
<g fill="{ROSA}">{cheio}</g><ellipse cx="330" cy="238" rx="205" ry="158" fill="{ROSA}"/>
<path d="M 468 258 Q 500 238 534 258" fill="none" stroke="{ROSA_E}" stroke-width="8" stroke-linecap="round"/>
<g id="{p}-olho"><ellipse cx="498" cy="294" rx="27" ry="18" fill="#0a0820"/><circle cx="506" cy="294" r="12.5" fill="#29b6ff"/><circle cx="511" cy="289" r="4" fill="#e8fbff"/></g>
<path d="M 392 318 C 358 300 346 372 380 396 C 406 410 424 362 404 340" fill="none" stroke="{ROSA_E}" stroke-width="7" stroke-linecap="round"/>
<path d="M 520 468 Q 540 474 554 464" fill="none" stroke="{ROSA_E}" stroke-width="6" stroke-linecap="round"/>
<path d="M 592 402 L 556 404 L 560 426 L 544 440" fill="none" stroke="{ROSA_E}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity=".7"/>
</g>"""


H_LINHA = "M150 250 C160 200 110 180 110 120 C110 50 190 28 244 62 C284 88 270 120 282 138 L300 160 L282 164 L284 182 C290 200 262 214 238 212 C232 226 236 240 240 252"
SIL_CER = "M-210 10 C-220 -50 -170 -100 -110 -96 C-80 -116 -30 -112 0 -104 C30 -112 80 -116 110 -96 C170 -100 220 -50 210 10 C210 60 160 96 100 90 C60 104 20 100 0 92 C-20 100 -60 104 -100 90 C-160 96 -210 60 -210 10 Z"


def cerebro_rosa(p, sx=1.0, sy=1.3):
    """Cérebro rosa com sulcos, centrado em (0,0), largura ~ 420*sx."""
    sulcos = ("M-160 -20 C-130 -64 -100 -4 -66 -48 S -10 -30 6 -70 M-170 30 C-140 -2 -104 52 -70 14 S -14 40 8 10 "
              "M-120 70 C-90 46 -60 84 -30 62 M20 -70 C40 -30 20 0 40 30 M60 -60 C90 -80 120 -40 150 -70 "
              "M40 20 C70 -6 100 44 134 8 S 170 20 184 -4 M60 66 C90 44 120 80 150 56")
    return (f'<g id="{p}" transform="scale({sx} {sy})"><path d="{SIL_CER}" fill="url(#{p}-g)" stroke="#d8657a" stroke-width="{7/sx:.1f}" stroke-linejoin="round"/>'
            f'<path d="{sulcos}" fill="none" stroke="#e07a8e" stroke-width="{6/sx:.1f}" stroke-linecap="round"/>'
            f'<path d="M-130 -60 C-90 -90 -30 -96 20 -88" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="{9/sx:.1f}" stroke-linecap="round"/></g>'
            f'<defs><radialGradient id="{p}-g" cx="40%" cy="30%" r="80%"><stop offset="0" stop-color="#ffc2c9"/><stop offset="1" stop-color="#ff8c9d"/></radialGradient></defs>')


def cabeca_linha(p, glow="E-glow"):
    """Perfil em linha contínua (card 5 aprovado) com preenchimento leve. Local: x 110..300, y 28..252."""
    return (f'<g id="{p}"><linearGradient id="{p}-pf" gradientUnits="userSpaceOnUse" x1="0" y1="150" x2="0" y2="252"><stop offset="0" stop-color="#4a4ab0" stop-opacity=".22"/><stop offset="1" stop-color="#4a4ab0" stop-opacity="0"/></linearGradient><path d="{H_LINHA} Z" fill="url(#{p}-pf)" stroke="none"/>'
            f'<path d="{H_LINHA}" fill="none" stroke="#3be0ff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" filter="url(#{glow})"/></g>')


CEREBRO_LAT = "M 262 84 C 262 56 226 36 188 38 C 150 38 122 62 122 98 C 122 118 134 126 150 124 C 164 122 176 128 192 130 C 210 130 222 116 238 108 C 252 102 262 96 262 84 Z"


def cerebro_lateral(p):
    """Cérebro em vista lateral, em coordenadas locais da cabeca_linha (x 110..300, y 28..252): lobo frontal acima do olho,
    temporal baixo, cerebelo atrás e tronco descendo pelo pescoço."""
    sulcos = ("M 134 84 C 148 66 160 90 176 70 S 204 66 220 52 M 146 106 C 162 90 178 112 196 94 S 224 96 244 78 "
              "M 200 108 C 214 100 226 110 240 100 M 176 52 C 184 66 178 80 188 92 M 228 60 C 236 70 232 82 246 90 M 138 112 C 150 104 160 114 172 108")
    return (f'<defs><radialGradient id="{p}-g" cx="40%" cy="30%" r="80%"><stop offset="0" stop-color="#ffc2c9"/><stop offset="1" stop-color="#ff8c9d"/></radialGradient></defs>'
            f'<g id="{p}"><path d="M 178 128 C 182 164 190 214 202 262" fill="none" stroke="#e8808f" stroke-width="13" stroke-linecap="round"/>'
            f'<ellipse cx="150" cy="138" rx="27" ry="17" fill="#f08a99" stroke="#d8657a" stroke-width="2.2"/><path d="M 130 134 Q 150 142 170 132 M 130 142 Q 150 150 170 140" fill="none" stroke="#d8657a" stroke-width="1.8"/>'
            f'<path d="{CEREBRO_LAT}" fill="url(#{p}-g)" stroke="#d8657a" stroke-width="2.4" stroke-linejoin="round"/>'
            f'<path d="{sulcos}" fill="none" stroke="#e07a8e" stroke-width="2.2" stroke-linecap="round"/>'
            f'<path d="M 142 70 C 166 46 206 42 238 54" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="3" stroke-linecap="round"/></g>')
