"""Grupo g8_fechamento2: cena "fechamento", segmentos 3, 4, 5, 6, 8 e 9.

  python3 build_g8_fechamento2.py     # escreve compositions/ e index.html desta pasta

Rodada 2: a cabeça com cérebro saiu; entra a pessoa de verdade (gente.py) em cenas de vida.
3 a pessoa no trabalho, sentada à mesa com o notebook, dentro do anel de princípios
4 sala de casa (plano espelhado): a pessoa de pé com o fone na mão, sofá e quadros, a onda de voz na sala
5 close da pessoa de fone de ouvido; a onda vira pixels (IA), quinze minutos, confiou
6 a pessoa no sofá, virada para o outro lado, conferindo as fontes no celular
8 a chave dos cientistas (camundongo) e, no seu caso, a pessoa no escritório diante do arquivo com a fechadura acesa
9 a pessoa, na parede da casa com os quadros da vida dela, diante da porta entreaberta, chave erguida, luz âmbar e alguém do outro lado (plano final)
"""
import math, os, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
sys.path.insert(0, os.path.join(AQUI, "../../cenas-v4"))
from motor import *
from motor import _norm
from arte2 import H_LINHA
import build4 as b4
from gente import gente, quadro, ANCORAS
AQUI = os.path.dirname(os.path.abspath(__file__))  # motor exporta o AQUI dele; este é o desta pasta

CE = "fechamento"
MAPA = {(CE, 3): "fechamento_3", (CE, 4): "fechamento_4", (CE, 5): "fechamento_5",
        (CE, 6): "fechamento_6", (CE, 8): "fechamento_8", (CE, 9): "fechamento_9", (CE, 10): "fechamento_10"}


def J(s, **kw):
    """Troca @nome@ por valor (float com 2 casas). Evita chave dupla de f-string no JS."""
    for k, v in kw.items():
        s = s.replace(f"@{k}@", f"{v:.2f}" if isinstance(v, float) else str(v))
    return s


JS_EXTRA = r"""
  // segundo movimento de câmera: igual ao camZ do motor, sem o tl.set inicial em t=0 (que sobrescrevia o zoom do primeiro)
  function camZb(sel,t0,dur,z0,z1,ox,oy,ease){
    var o={l:Math.log(z0)};
    tl.to(o,{l:Math.log(z1),duration:dur,ease:ease||"power3.inOut",onUpdate:function(){gsap.set(sel,{scale:Math.exp(o.l),svgOrigin:ox+" "+oy});},immediateRender:false},t0);
  }
  function sai(sel,t){tl.fromTo(sel,{yPercent:0},{yPercent:-125,duration:0.45,ease:"power3.in",immediateRender:false},t);}
"""

MONO = "font-family:'IBM Plex Mono',monospace;font-weight:500;letter-spacing:.12em"


# ---------------------------------------------------------------- peças
def defs_ouro(p):
    return (f'<linearGradient id="{p}-ouro" x1="0" y1="-1" x2="0" y2="1" gradientUnits="objectBoundingBox"><stop offset="0" stop-color="#ffe7a0"/>'
            f'<stop offset=".5" stop-color="#ffb23e"/><stop offset="1" stop-color="#d9811c"/></linearGradient>'
            f'<radialGradient id="{p}-halo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffb23e" stop-opacity=".38"/><stop offset="1" stop-color="#ffb23e" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{p}-papel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#e9dcc2"/></linearGradient>')


def chave(p, k="chave"):
    """Chave âmbar deitada, argola em (0,0), ponta para a direita (~ x -53..270). Id {p}-{k}."""
    return (f'<g id="{p}-{k}"><ellipse cx="110" cy="0" rx="230" ry="110" fill="url(#{p}-halo)"/>'
            f'<circle cx="0" cy="0" r="40" fill="none" stroke="#ffb23e" stroke-width="28" filter="url(#{p}-glow)"/>'
            f'<circle cx="0" cy="0" r="40" fill="none" stroke="#ffd27a" stroke-width="18"/>'
            f'<rect x="50" y="-15" width="28" height="30" rx="6" fill="#ffb23e"/>'
            f'<rect x="72" y="-11" width="200" height="22" rx="10" fill="#f0a234"/>'
            f'<path d="M198 9 h24 v36 h-24z M238 9 h28 v26 h-28z" fill="#e4932a"/>'
            f'<path d="M84 -5 H262" stroke="#fff6d8" stroke-width="5" stroke-linecap="round" opacity=".75"/>'
            f'<path d="M-30 -22 A 37 37 0 0 1 18 -36" stroke="#fff6d8" stroke-width="6" fill="none" stroke-linecap="round" opacity=".85"/></g>')


def fechadura(p, k, cx, cy, s, aberta=True):
    """Fechadura: furo escuro com aro âmbar. Se aberta, luz âmbar vazando."""
    luz = f'<ellipse cx="0" cy="22" rx="120" ry="140" fill="url(#{p}-halo)"/>' if aberta else ""
    return (f'<g transform="translate({cx} {cy}) scale({s})"><g id="{p}-{k}">{luz}'
            f'<path d="M0 -44 a30 30 0 0 1 17 55 L30 80 L-30 80 L-17 11 A30 30 0 0 1 0 -44Z" fill="#120a30" stroke="#ffb23e" stroke-width="7" stroke-linejoin="round" filter="url(#{p}-glow)"/>'
            f'<path d="M0 -30 a16 16 0 0 1 9 29 L16 66 L-16 66 L-9 -1 A16 16 0 0 1 0 -30Z" fill="#ffcf6a" opacity=".55"/></g></g>')


def doc(p, k, cor):
    """Página de fonte (papel com faixa colorida e linhas), centrada em (0,0), 230 x 300."""
    linhas = "".join(f'<rect x="-88" y="{-70 + j * 30}" width="{176 if j % 3 else 120}" height="10" rx="5" fill="#8a7f68" opacity=".5"/>' for j in range(7))
    return (f'<g id="{p}-{k}"><g filter="url(#{p}-sombra)"><rect x="-115" y="-150" width="230" height="300" rx="16" fill="url(#{p}-papel)"/></g>'
            f'<path d="M-115 -104 V-134 a16 16 0 0 1 16 -16 H99 a16 16 0 0 1 16 16 V-104Z" fill="{cor}"/>{linhas}</g>')


# ---------------------------------------------------------------- a pessoa de verdade (gente.py) e o cenário
def anc(var, pose):
    return ANCORAS[(var, pose, 30)]


def pescoco(var, pose):
    """Pivô da cabeça (base do pescoço) no sistema local de gente. Use com svgOrigin: os grupos do personagem novo têm
    caixa gigante (clipPaths de 20000 px), então transformOrigin em % joga o pivô a milhares de px."""
    cx, cy = anc(var, pose)["cabeca_centro"]
    return f"{cx} {cy + 45}"


def ombro(var, pose):
    return "%s %s" % anc(var, pose)["ombro_braco"]


def figura(pg, var, pose, cab_extra="", mao="", caneca=None, cadeira=True):
    """gente() com a cabeça embrulhada em {pg}-hd (sem transform no atributo, o GSAP pode animar). cab_extra entra dentro
    da cabeça (fone); mao entra no fim do braço {pg}-braco (gira junto com ele, svgOrigin=ombro()); caneca
    (casa sentado) troca a caneca da mão por outro desenho, que fica atrás dos dedos."""
    s = gente(pg, var, pose, cadeira=cadeira)
    if cab_extra:
        s = s.replace(f'<g id="{pg}-olho">', cab_extra + f'<g id="{pg}-olho">', 1)
    if caneca is not None:
        i = s.index('<path d="M 14,-254 C 0,-254 0,-232 14,-232"')
        j = s.index('/>', s.rindex('stroke="#a98bff"')) + 2
        assert 0 < j - i < 6000
        s = s[:i] + caneca + s[j:]
    if mao:
        # fim do grupo do braço contando <g>/</g> (o braço tem grupos aninhados)
        i = s.rindex("<g", 0, s.index(f'id="{pg}-braco"'))
        prof = 0
        for m in re.finditer(r"<g\b|</g>", s[i:]):
            prof += -1 if m.group(0) == "</g>" else 1
            if prof == 0:
                break
        k = i + m.start()
        s = s[:k] + mao + s[k:]
    s = s.replace(f'<g id="{pg}-cabW"', f'<g id="{pg}-hd"><g id="{pg}-cabW"', 1)
    assert s.endswith("</g></g></g>")
    return s[:-8] + "</g>" + s[-8:]  # fecha {pg}-hd logo depois de {pg}-cabW


def vida(pg, dur, piscadas, pose="sentado"):
    """Respira (tronco), balança a cabeça ({pg}-hd) e pisca. Pivô do tronco por svgOrigin (ver pescoco)."""
    n = max(1, int(dur / 1.7))
    quadril = "0 -174" if pose == "sentado" else "0 -250"
    js = (f'tl.fromTo("#{pg}-tor",{{scaleY:1,svgOrigin:"{quadril}"}},{{scaleY:1.012,svgOrigin:"{quadril}",duration:1.7,repeat:{n},yoyo:true,ease:"sine.inOut"}},0);'
          f'tl.fromTo("#{pg}-hd",{{y:0}},{{y:-4,duration:1.7,repeat:{n},yoyo:true,ease:"sine.inOut"}},0.2);')
    for t in piscadas:
        if t < dur - 0.3:
            js += f'tl.fromTo("#{pg}-olho",{{scaleY:1,transformOrigin:"50% 50%"}},{{scaleY:0.08,transformOrigin:"50% 50%",duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t});'
    return js


def ponto(lx, ly, tx, ty, s, esp=1):
    """Ponto (lx, ly) do sistema local de gente levado para a tela, para a figura em translate(tx ty) scale(esp*s, s)."""
    return round(tx + esp * s * lx), round(ty + s * ly)


# fone de ouvido no sistema local de gente casa sentado giro 30 (orelha visível em -35,-382; topo do cabelo em -454)
ARCO_F = "M -36 -392 C -46 -480 32 -488 29 -404"
FONES = (f'<path d="{ARCO_F}" fill="none" stroke="#1a1250" stroke-width="10" stroke-linecap="round"/>'
         f'<path d="{ARCO_F}" fill="none" stroke="#3be0ff" stroke-width="3" stroke-linecap="round"/>'
         '<ellipse cx="30" cy="-396" rx="5" ry="12" fill="#2a1d70" stroke="#3be0ff" stroke-width="2"/>'
         '<ellipse cx="-37" cy="-382" rx="12" ry="17" fill="#2a1d70" stroke="#3be0ff" stroke-width="3"/>'
         '<ellipse cx="-37" cy="-382" rx="5" ry="8" fill="#3be0ff" opacity=".6"/>')
TOPO_F = (-6, -463)  # topo do arco do fone (de onde sai o laço)


def fone_pendurado(var, pose, rot):
    """Fone segurado pelo arco, na mão do braço {pg}-braco. Desenhado já girado por -rot, para ficar de pé quando o braço
    estiver em rotation=rot."""
    mx, my = anc(var, pose)["mao_e"]
    return (f'<g transform="translate({mx} {my + 13}) rotate({-rot})">'
            '<path d="M -26 30 C -30 -14 30 -14 26 30" fill="none" stroke="#1a1250" stroke-width="9" stroke-linecap="round"/>'
            '<path d="M -26 30 C -30 -14 30 -14 26 30" fill="none" stroke="#3be0ff" stroke-width="3" stroke-linecap="round"/>'
            '<ellipse cx="-26" cy="38" rx="11" ry="15" fill="#2a1d70" stroke="#3be0ff" stroke-width="3"/>'
            '<ellipse cx="26" cy="38" rx="11" ry="15" fill="#2a1d70" stroke="#3be0ff" stroke-width="3"/></g>')


def sofa(cor="#4b2fa0", cor2="#341f86"):
    """Sofá de perfil no sistema local de gente sentado (encosto atrás, assento sob as coxas)."""
    return (f'<rect x="-180" y="-252" width="250" height="88" rx="30" fill="{cor2}"/>'
            f'<rect x="-190" y="-424" width="100" height="296" rx="42" fill="{cor}" stroke="#8d7bff" stroke-width="4"/>'
            f'<rect x="-190" y="-178" width="326" height="72" rx="28" fill="{cor}" stroke="#8d7bff" stroke-width="4"/>'
            f'<rect x="-198" y="-112" width="344" height="66" rx="18" fill="{cor2}"/>'
            f'<path d="M -172 -46 L -176 0 M 122 -46 L 126 0" stroke="#8d7bff" stroke-width="10" stroke-linecap="round"/>')


def abajur(p, x, y):
    """Abajur de chão aceso (y = chão)."""
    return (f'<g transform="translate({x} {y})"><ellipse cx="0" cy="0" rx="56" ry="10" fill="#05031a" opacity=".5"/>'
            f'<ellipse cx="0" cy="-330" rx="190" ry="170" fill="url(#{p}-halo)"/>'
            f'<rect x="-42" y="-14" width="84" height="14" rx="6" fill="#2a1d70" stroke="#8d7bff" stroke-width="3"/>'
            f'<rect x="-5" y="-300" width="10" height="288" fill="#8d7bff"/>'
            f'<path d="M -66 -296 L 66 -296 L 44 -384 L -44 -384 Z" fill="#ffd27a" stroke="#ffb23e" stroke-width="5"/>'
            f'<path d="M -50 -300 L 50 -300" stroke="#fff6d8" stroke-width="5" stroke-linecap="round"/></g>')


def chao(y, x0=-300, x1=2220, cor="#120a34"):
    return (f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="500" fill="{cor}"/>'
            f'<rect x="{x0}" y="{y - 8}" width="{x1 - x0}" height="10" fill="#2a1d70"/>')


# ---------------------------------------------------------------- onda de voz (segmentos 4, 5, 6)
X0, NB, SP, CY, HMAX = 680, 86, 13, 510, 370
WX = X0 + (NB - 1) * SP // 2  # centro da onda (onde a chave pousa)
KX, KY, KS, WS = 590, 215, .75, .95  # chave em repouso (perto da pessoa) e escala dentro da onda


def envelope(i, dur, fps=30):
    """Amplitude da voz amostrada a 30 fps a partir do tempo de cada palavra (sílabas viram pulsos)."""
    n = int(dur * fps) + 2
    E = [0.12] * n
    for (w, t0, t1) in palavras_seg(CE, i):
        nw = _norm(w)
        syl = max(1, len(re.findall(r"[aeiou]+", nw)))
        pico = 0.55 + 0.45 * min(1.0, len(nw) / 9)
        d = max(0.12, t1 - t0)
        for k in range(n):
            t = k / fps
            if t < t0 or t > t1 + 0.3:
                continue
            if t <= t1:
                u = (t - t0) / d
                a = pico * min(1.0, (t - t0) / 0.05) * (0.5 + 0.5 * abs(math.sin(math.pi * u * syl)))
            else:
                a = pico * 0.6 * math.exp(-(t - t1) / 0.09)
            E[k] = max(E[k], a)
    return [round(x, 3) for x in E]


def onda_svg(p, pixel=False):
    linhas = "".join(f'<line x1="{X0 + j * SP}" x2="{X0 + j * SP}" y1="{CY - 5}" y2="{CY + 5}"/>' for j in range(NB))
    s = (f'<line x1="{X0 - 30}" x2="{X0 + (NB - 1) * SP + 10}" y1="{CY}" y2="{CY}" stroke="#8d7bff" stroke-width="2" opacity=".5"/>'
         f'<g id="{p}-ondaG"><g id="{p}-wa" stroke="url(#{p}-wg)" stroke-width="7" stroke-linecap="round" filter="url(#{p}-glow)"'
         f'{f" clip-path=url(#{p}-cs)" if pixel else ""}>{linhas}</g>')
    if pixel:
        s += (f'<g id="{p}-wb" stroke="url(#{p}-wg)" stroke-width="9" stroke-dasharray="9 5" filter="url(#{p}-glow)" clip-path="url(#{p}-cp)">{linhas}</g>'
              f'<rect id="{p}-scan" x="{X0 - 20}" y="{CY - 380}" width="8" height="760" fill="#e6fbff" opacity="0" filter="url(#{p}-glow)"/>')
    return s + "</g>"


def onda_defs(p, pixel=False, cheio=False):
    s = (f'<linearGradient id="{p}-wg" gradientUnits="userSpaceOnUse" x1="{X0}" y1="0" x2="{X0 + NB * SP}" y2="0">'
         f'<stop offset="0" stop-color="#3be0ff"/><stop offset=".5" stop-color="#8d7bff"/><stop offset="1" stop-color="#ff4fa3"/></linearGradient>')
    if pixel:
        s += (f'<clipPath id="{p}-cs"><rect id="{p}-csr" x="{X0 - 20 + (1400 if cheio else 0)}" y="0" width="1400" height="1080"/></clipPath>'
              f'<clipPath id="{p}-cp"><rect id="{p}-cpr" x="{X0 - 20}" y="0" width="{1400 if cheio else 0}" height="1080"/></clipPath>')
    return s


def onda_js(p, i, dur, ganho):
    """Liga a onda ao tempo: um tween de 0 a dur cujo onUpdate redesenha as barras (determinístico, funciona com seek)."""
    E = envelope(i, dur)
    ph = [round((j * 2.399) % 6.283, 2) for j in range(NB)]
    return J("""
  (function(){
    var E=@E@, G=@G@, PH=@PH@, N=@N@;
    function g(t){ if(t<=G[0][0]) return G[0][1]; for(var k=1;k<G.length;k++){ if(t<=G[k][0]){var a=G[k-1],b=G[k];return a[1]+(b[1]-a[1])*(t-a[0])/(b[0]-a[0]);} } return G[G.length-1][1]; }
    function W(t){
      var A=document.querySelectorAll("#@P@-wa line"), B=document.querySelectorAll("#@P@-wb line");
      var f=t*30,k=Math.floor(f),u=f-k,n=E.length-1;
      var a=(E[Math.min(k,n)]*(1-u)+E[Math.min(k+1,n)]*u)*g(t);
      for(var j=0;j<A.length;j++){
        var x=j/(N-1), prof=0.2+0.8*Math.exp(-Math.pow((x-0.5)/0.34,2));
        var jit=(0.4+0.6*Math.abs(Math.sin(j*0.73+t*9.0+PH[j])))*(0.7+0.3*Math.sin(j*0.21-t*3.1));
        var h=5+@H@*a*prof*jit;
        A[j].setAttribute("y1",(@CY@-h).toFixed(1)); A[j].setAttribute("y2",(@CY@+h).toFixed(1));
        if(B[j]){B[j].setAttribute("y1",(@CY@-h).toFixed(1)); B[j].setAttribute("y2",(@CY@+h).toFixed(1));}
      }
    }
    var o={t:0};
    tl.fromTo(o,{t:0},{t:@D@,duration:@D@,ease:"none",onUpdate:function(){W(o.t);}},0);
    W(0);
  })();
""", E=str(E), G=str([list(x) for x in ganho]), PH=str(ph), N=NB, H=HMAX, CY=CY, D=float(dur))


def base_onda(p, pixel=False):
    """Só a onda (com o brilho atrás). A pessoa e o cenário entram em cada cena."""
    return (f'<ellipse cx="{WX}" cy="{CY}" rx="740" ry="360" fill="url(#{p}-bloom)" opacity=".55"/>'
            f'{onda_svg(p, pixel)}')


def laco(p, k, d, op=0):
    """Laço pontilhado âmbar (liga a chave a quem a tem). Anime com flui()."""
    return f'<path id="{p}-{k}" d="{d}" fill="none" stroke="#ffb23e" stroke-width="5" stroke-dasharray="3 15" stroke-linecap="round" opacity="{op}" filter="url(#{p}-glow)"/>'


def flui(k, dur):
    return J('tl.fromTo("#@P@-@k@",{attr:{"stroke-dashoffset":0}},{attr:{"stroke-dashoffset":-180},duration:@d@,ease:"none"},0);', k=k, d=float(dur))




BLOOM = '<radialGradient id="@P@-bloom" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#8d7bff" stop-opacity=".35"/><stop offset="1" stop-color="#8d7bff" stop-opacity="0"/></radialGradient>'


# ---------------------------------------------------------------- 3: lista de princípios
def fechamento_3():
    p, i = "fechamento_3", 3
    ini, dur = seg(CE, i)
    T = lambda w, n=0, d=None: palavra(CE, i, w, n, d)
    t_mesmo, t_cons, t_dar, t_term, t_le, t_lim, t_uso, t_fis, t_ind, t_dir, t_nao, t_sem, t_emp = (
        T("mesmo"), T("consentimento"), T("de", 0, 3.03), T("termo"), T("le", 0, 6.03), T("limites"), T("para", 1),
        T("fiscaliza"), T("independente"), T("direito"), T("nao"), T("sem"), T("emprego"))
    CX, CYR, R = 470, 520, 410
    cores = ["#3be0ff", "#38e8a8", "#ffb23e", "#ff4fa3"]
    arcos = ""
    L = R * math.radians(90)
    for k in range(4):
        a0, a1 = math.radians(-135 + k * 90), math.radians(-45 + k * 90)
        x0, y0, x1, y1 = CX + R * math.cos(a0), CYR + R * math.sin(a0), CX + R * math.cos(a1), CYR + R * math.sin(a1)
        arcos += (f'<path id="{p}-arc{k}" d="M{x0:.1f} {y0:.1f} A{R} {R} 0 0 1 {x1:.1f} {y1:.1f}" fill="none" stroke="{cores[k]}" stroke-width="14" '
                  f'stroke-linecap="round" stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}" filter="url(#{p}-glow)"/>')
    MESA = ('<rect x="40" y="-214" width="270" height="18" rx="7" fill="#6a5a46" stroke="#a08a6a" stroke-width="3"/>'
            '<path d="M 292 -196 L 292 0" stroke="#a08a6a" stroke-width="12" stroke-linecap="round"/>'
            '<ellipse cx="292" cy="2" rx="40" ry="7" fill="#05031a" opacity=".5"/>')
    NOTE = (f'<polygon points="236,-326 236,-224 32,-346 32,-410" fill="#3be0ff" opacity=".10"/>'
            f'<rect x="118" y="-226" width="118" height="12" rx="4" fill="#aeb6d4"/>'
            f'<path d="M 236 -222 L 252 -334" stroke="#2a2a5a" stroke-width="14" stroke-linecap="round"/>'
            f'<path d="M 228 -226 L 244 -332" stroke="#3be0ff" stroke-width="4" stroke-linecap="round" filter="url(#{p}-glow)"/>')
    tiny = "".join(f'<rect x="-74" y="{-380 + j * 13}" width="{148 if j % 4 else 96}" height="5" rx="2" fill="#8a7f68" opacity=".55"/>' for j in range(60))
    extra = defs_ouro(p) + BLOOM.replace("@P@", p)
    svg = f"""
<ellipse cx="{CX}" cy="{CYR}" rx="560" ry="520" fill="url(#{p}-bloom)"/>
<circle cx="{CX}" cy="{CYR}" r="{R}" fill="none" stroke="#8d7bff" stroke-width="3" stroke-dasharray="6 14" opacity=".45"/>
<g id="{p}-anel"><rect x="{CX - R - 20}" y="{CYR - R - 20}" width="{2 * R + 40}" height="{2 * R + 40}" fill="none"/>{arcos}</g>
<g id="{p}-dados" fill="#ff6fae" filter="url(#{p}-glow)"></g>
<g transform="translate(420 880) scale(1.2)">{MESA}{figura(p + "g", "trabalho", "sentado")}{NOTE}</g>
<g transform="translate({CX} {CYR})"><g id="{p}-orb"><rect x="-{R + 70}" y="-{R + 70}" width="{2 * R + 140}" height="{2 * R + 140}" fill="none"/>
 <g transform="translate(0 -{R})"><g id="{p}-lupa" opacity="0"><circle r="58" fill="#ffb23e" fill-opacity=".12" stroke="#ffb23e" stroke-width="12" filter="url(#{p}-glow)"/>
 <path d="M-30 -22 A 38 38 0 0 1 10 -40" stroke="#fff6d8" stroke-width="6" fill="none" stroke-linecap="round"/>
 <path d="M42 42 L92 92" stroke="#ffb23e" stroke-width="20" stroke-linecap="round"/></g></g></g></g>
<g transform="translate(880 540)"><g id="{p}-termo" opacity="0">
 <g filter="url(#{p}-sombra)"><rect x="-90" y="-400" width="180" height="800" rx="12" fill="url(#{p}-papel)"/></g>{tiny}</g></g>
<g transform="translate(880 300)"><g id="{p}-ok" opacity="0"><rect x="-80" y="-56" width="160" height="112" rx="16" fill="url(#{p}-papel)" filter="url(#{p}-sombra)"/>
 <path d="M-34 0 L-8 26 L40 -28" fill="none" stroke="#1fb985" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/></g></g>
"""
    rows = [("Consentimento", "QUE DÊ PARA ENTENDER"), ("Limites", "PARA O USO DE DADOS DO CÉREBRO"),
            ("Fiscalização", "INDEPENDENTE"), ("O direito de dizer não", "SEM PERDER O EMPREGO")]
    html = texto(f"{p}-h", "NÓS DEFENDEMOS O MESMO", f"left:1020px;top:46px;font-size:44px;color:#ffb23e;{MONO}", "pill2")
    for k, (a, b) in enumerate(rows):
        top = 150 + k * 222
        html += (f'<div id="{p}-r{k}" style="position:absolute;left:1000px;top:{top}px;width:880px;height:190px">'
                 f'<div id="{p}-bar{k}" style="position:absolute;left:0;top:18px;width:10px;height:150px;border-radius:5px;background:{cores[k]};box-shadow:0 0 18px {cores[k]};opacity:0"></div>'
                 + texto(f"{p}-ta{k}", a, f"left:40px;top:0;font-size:84px;color:{cores[k]}")
                 + texto(f"{p}-tb{k}", b, f"left:44px;top:110px;font-size:42px;color:#eef1f7;{MONO};letter-spacing:.02em", "pill2")
                 + '</div>')
    tl_rows = [(t_cons, t_dar), (t_lim, t_uso), (t_fis, t_ind), (t_dir, t_sem)]
    js = J("""
  camZ("#@P@-cam", 0, 1.8, 1.25, 1.0, 445, 470);
  rise("#@P@-h span", 0.25);
""") + vida(p + "g", dur, (2.6, 5.4, 8.9, 11.8, 16.3), "sentado")
    for k, (ta, tb) in enumerate(tl_rows):
        js += J("""
  entra("#@P@-bar@k@", @ta@, 0.3); tl.fromTo("#@P@-bar@k@",{scaleY:0,transformOrigin:"50% 0%"},{scaleY:1,duration:0.6,ease:"expo.out",immediateRender:false},@ta@);
  rise("#@P@-ta@k@ span", @ta@); rise("#@P@-tb@k@ span", @tb@);
""", k=k, ta=ta - 0.05, tb=tb)
        if k:
            js += J('tl.to("#@P@-r@j@",{opacity:0.62,duration:0.4},@ta@);', j=k - 1, ta=ta - 0.05)
    # anel: um arco por princípio
    for k, t in enumerate([t_le - 0.2, t_lim, t_fis, t_dir]):
        js += J('tl.to("#@P@-arc@k@",{attr:{"stroke-dashoffset":0},duration:0.9,ease:"power3.inOut"},@t@);', k=k, t=t)
    js += J("""
  // termo longo que ninguém lê vira cartão claro e voa até o primeiro arco
  entra("#@P@-termo", @tt@, 0.3);
  tl.fromTo("#@P@-termo",{scaleY:0.16,transformOrigin:"50% 0%"},{scaleY:1,duration:1.1,ease:"power2.out"},@tt@);
  tl.to("#@P@-termo",{scaleY:0.05,scaleX:0.6,opacity:0,duration:0.35,ease:"power3.in"},@tl@);
  pop("#@P@-ok", @tl1@, 0.3, 0.6);
  tl.to("#@P@-ok",{x:-410,y:-190,scale:0.4,opacity:0,duration:0.7,ease:"power2.in"},@tl2@);
  tl.fromTo("#@P@g-olho",{x:0},{x:3,duration:0.3},@tc@);
  // dados saem do cérebro: antes de Limites escapam, depois param no anel
  (function(){
    var g=document.getElementById("@P@-dados");
    for(var j=0;j<14;j++){
      var c=document.createElementNS("http://www.w3.org/2000/svg","circle");
      c.setAttribute("id","@P@-dd"+j); c.setAttribute("cx","414"); c.setAttribute("cy","400"); c.setAttribute("r","13"); c.setAttribute("opacity","0"); g.appendChild(c);
      var a=-1.2+j*0.45, t0=@td@+(j%7)*0.5, ex=Math.cos(a), ey=Math.sin(a);
      tl.fromTo("#@P@-dd"+j,{x:0,y:0,opacity:0},{x:ex*900,y:ey*900,opacity:1,duration:1.6,ease:"none",immediateRender:false},t0);
      tl.to("#@P@-dd"+j,{opacity:0,duration:0.2},t0+1.4);
      var t1=@tlim@+0.3+(j%7)*0.55, dx=414-@CX@, dy=400-@CY@, de=dx*ex+dy*ey, s=-de+Math.sqrt(de*de-dx*dx-dy*dy+(@R@-14)*(@R@-14));
      tl.fromTo("#@P@-dd"+j,{x:0,y:0,opacity:0,scale:1,transformOrigin:"50% 50%"},{x:ex*s,y:ey*s,opacity:1,duration:0.9,ease:"power2.out",immediateRender:false},t1);
      tl.to("#@P@-dd"+j,{scale:2.2,opacity:0,duration:0.35},t1+0.9);
    }
  })();
  // fiscalização: lupa percorre o anel
  pop("#@P@-lupa", @tf@, 0.3, 0.7);
  tl.fromTo("#@P@-orb",{rotation:0,transformOrigin:"50% 50%"},{rotation:405,duration:@dorb@,ease:"sine.inOut",immediateRender:false},@tf@);
  tl.fromTo("#@P@-lupa",{rotation:0,transformOrigin:"50% 50%"},{rotation:-405,duration:@dorb@,ease:"sine.inOut",immediateRender:false},@tf@);
  // dizer não: a cabeça balança
  tl.fromTo("#@P@g-hd",{x:0},{x:9,duration:0.13,repeat:5,yoyo:true,ease:"sine.inOut",immediateRender:false},@tn@);
  // sem perder o emprego: o anel fecha e pulsa, tudo acende
  tl.fromTo("#@P@-anel",{scale:1,transformOrigin:"50% 50%"},{scale:1.04,duration:0.35,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false},@te@);
  tl.to(["#@P@-r0","#@P@-r1","#@P@-r2"],{opacity:1,duration:0.6},@te@);
  camZb("#@P@-cam", @te@, @dfim@, 1.0, 1.04, 520, 520, "sine.inOut");
""", tc=t_cons, tt=t_term - 0.3, tl=t_le + 0.05, tl1=t_le + 0.25, tl2=t_le + 0.9, td=t_cons + 0.2, tlim=t_lim,
           tf=t_fis, dorb=dur - t_fis - 0.4, CX=CX, CY=CYR, R=R, tn=t_nao, te=t_emp - 0.3, dfim=dur - t_emp)
    return composicao(p, dur, svg, html, JS_EXTRA + js, extra, seed=21)


# ---------------------------------------------------------------- 4: "Agora, uma última coisa"
def fechamento_4():
    p, i = "fechamento_4", 4
    ini, dur = seg(CE, i)
    t_ult, t_coi = palavra(CE, i, "ultima"), palavra(CE, i, "coisa")
    extra = defs_ouro(p) + onda_defs(p) + BLOOM.replace("@P@", p)
    # de pé na sala, fone na mão, prestes a sentar e ouvir (a cena 5 é sentada com o fone)
    X, Y, S = 500, 900, 1.05
    # o braço original (com a mão desenhada) gira no ombro e ergue o fone; ROT4 é a pose final
    ROT4 = -62
    # espelhado: a pessoa fica à direita e a onda à esquerda, para não repetir o plano da cena 5
    svg = ('<g transform="translate(1920 0) scale(-1 1)">' + chao(880) + quadro(p + "q1", "familia", 200, 250, .62, -3) + quadro(p + "q2", "praia", 320, 405, .5, 2)
           + base_onda(p)
           + f'<g transform="translate(270 900) scale(.95)">{sofa()}</g>'
           + f'<g transform="translate({X} {Y}) scale({S})">{figura(p + "g", "casa", "em_pe", mao=fone_pendurado("casa", "em_pe", ROT4))}</g></g>')
    html = texto(f"{p}-t", "UMA ÚLTIMA COISA", f"left:60px;width:1160px;text-align:center;top:880px;font-size:92px;color:#eef1f7")
    js = onda_js(p, i, dur, [(0, 0.8), (dur, 1.0)]) + vida(p + "g", dur, (1.3,), "em_pe") + J("""
  camZ("#@P@-cam", 0, @D@, 1.1, 1.0, 960, 520, "sine.out");
  tl.fromTo("#@P@-ondaG",{scaleX:0.05,transformOrigin:"0% 50%"},{scaleX:1,duration:0.7,ease:"expo.out"},0.05);
  tl.fromTo("#@P@g-olho",{x:0,y:0},{x:2,y:-2,duration:0.4},0.3);
  tl.fromTo("#@P@g-hd",{rotation:0,svgOrigin:"@pc@"},{rotation:-4,duration:0.6,ease:"sine.inOut"},0.4);
  rise("#@P@-t span", @tu@, 0.8);
  tl.fromTo("#@P@g-braco",{rotation:-24,svgOrigin:"@om@"},{rotation:-54,duration:0.9,ease:"back.out(1.6)"},@tu@);
  tl.to("#@P@g-braco",{rotation:@r4@,duration:0.4,ease:"sine.inOut"},@tc@);
""", D=float(dur), tu=t_ult - 0.1, tc=t_coi, pc=pescoco("casa", "em_pe"), om=ombro("casa", "em_pe"), r4=ROT4)
    return composicao(p, dur, svg, html, JS_EXTRA + js, extra, seed=31)


# ---------------------------------------------------------------- 5: a voz não existe, foi gerada por IA, você confiou
def fechamento_5():
    p, i = "fechamento_5", 5
    ini, dur = seg(CE, i)
    T = lambda w, n=0, d=None: palavra(CE, i, w, n, d)
    t_nao, t_ger, t_int, t_voce, t_15, t_conf = T("nao"), T("gerada"), T("intelig"), T("voce"), T("tempo"), T("confiou")  # t_15: "esse tempo todo" (antes "quinze minutos")
    extra = defs_ouro(p) + onda_defs(p, pixel=True) + BLOOM.replace("@P@", p)
    hx, hy = ponto(*TOPO_F, 360, 1240, 2.0)  # topo do fone
    svg = (quadro(p + "q1", "cachorro", 215, 190, .7, -2) + base_onda(p, pixel=True)
           + f'<g transform="translate(360 1240) scale(2)">{sofa("#3d2690", "#2c1a74")}{figura(p + "g", "casa", "sentado", FONES, cadeira=False)}</g>'
           + laco(p, "l0", f"M{hx} {hy} Q 470 150 {KX - 34} {KY + 8}", .85) + laco(p, "l1", f"M{hx} {hy} C 560 120 900 420 {WX - 40} {CY}")
           + f'<g transform="translate({KX} {KY}) scale({KS})"><g id="{p}-kw">{chave(p)}</g></g>')
    pos = "left:700px;width:1160px;text-align:center;top:880px"
    html = (texto(f"{p}-t1", "NÃO EXISTE", f"{pos};font-size:96px;color:#eef1f7")
            + texto(f"{p}-t2", "INTELIGÊNCIA ARTIFICIAL", "left:640px;width:1260px;text-align:center;top:880px;font-size:84px;color:#c9b8ff")
            + texto(f"{p}-t3", "ESSE TEMPO TODO", f"{pos};font-size:88px;color:#bff4ff")
            + texto(f"{p}-t4", "CONFIOU", f"{pos};font-size:100px;color:#ffd98a"))
    ganho = [(0, 1.0), (dur, 1.0)]
    js = onda_js(p, i, dur, ganho) + vida(p + "g", dur, (0.9, 3.4, 7.0, 10.0), "sentado") + flui("l0", dur) + flui("l1", dur) + J("""
  tl.fromTo("#@P@g-olho",{x:2},{x:2,duration:0.1},0);
  // não existe: a onda falha como fantasma
  rise("#@P@-t1 span", @tn@);
  tl.fromTo("#@P@-ondaG",{opacity:1},{opacity:0.2,duration:0.07,repeat:9,yoyo:true,ease:"none",immediateRender:false},@tn2@);
  tl.fromTo("#@P@-ondaG",{x:0},{x:14,duration:0.05,repeat:7,yoyo:true,ease:"none",immediateRender:false},@tn2@);
  // gerada por IA: uma varredura transforma a onda em pixels
  tl.set("#@P@-scan",{opacity:1},@tg@);
  tl.fromTo("#@P@-scan",{x:0},{x:1140,duration:1.2,ease:"power1.inOut",immediateRender:false},@tg@);
  tl.to("#@P@-scan",{opacity:0,duration:0.2},@tg2@);
  tl.fromTo("#@P@-cpr",{attr:{width:0}},{attr:{width:1160},duration:1.2,ease:"power1.inOut",immediateRender:false},@tg@);
  tl.fromTo("#@P@-csr",{attr:{x:@X0@}},{attr:{x:@X1@},duration:1.2,ease:"power1.inOut",immediateRender:false},@tg@);
  sai("#@P@-t1 span", @ti0@); rise("#@P@-t2 span", @ti@);
  // você ouviu: câmera vai para a pessoa, "esse tempo todo"
  camZ("#@P@-cam", @tv@, 1.3, 1.0, 1.2, 380, 420);
  sai("#@P@-t2 span", @t150@); rise("#@P@-t3 span", @t15r@);
  // confiou: a chave sai da pessoa e vai para dentro da onda
  camZb("#@P@-cam", @tc0@, 1.3, 1.2, 1.0, 380, 420);
  tl.fromTo("#@P@-kw",{y:0,rotation:0,transformOrigin:"50% 50%"},{y:-14,rotation:-6,duration:0.8,repeat:5,yoyo:true,ease:"sine.inOut"},0);
  tl.to("#@P@-kw",{keyframes:{x:[0,@kx5h@,@kx5@],y:[0,-200,@ky5@],easeEach:"sine.inOut"},scale:1.267,rotation:0,duration:1.5,ease:"power2.inOut"},@tk@);
  tl.fromTo("#@P@g-olho",{x:2},{x:3,duration:0.4,immediateRender:false},@tk@);
  // confiou: a pessoa relaxa, a cabeça inclina
  tl.fromTo("#@P@g-hd",{rotation:0,svgOrigin:"@pc@"},{rotation:5,duration:1.0,ease:"sine.inOut",immediateRender:false},@tc@);
  sai("#@P@-t3 span", @tc1@); rise("#@P@-t4 span", @tc@);
  tl.to("#@P@-l0",{opacity:0,duration:0.3},@tk@);
  tl.to("#@P@-l1",{opacity:0.85,duration:0.5},@tk2@);
  tl.fromTo("#@P@-chave",{scale:1,transformOrigin:"50% 50%"},{scale:1.12,duration:0.4,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false},@tk2@);
""", tn=t_nao, tn2=t_nao + 0.15, tg=t_ger - 0.1, tg2=t_ger + 1.1, X0=X0 - 20, X1=X0 + 1140, ti0=t_int - 0.5, ti=t_int,
           tv=t_voce - 0.1, kx5h=round((WX - KX) / KS / 2), kx5=round((WX - KX) / KS), ky5=round((CY - KY) / KS), t150=t_15 - 0.45, t15r=t_15 - 0.05, tc0=t_conf - 1.4, tk=t_conf - 1.2, tc1=t_conf - 0.45,
           tc=t_conf, tk2=t_conf + 0.4, pc=pescoco("casa", "sentado"))
    return composicao(p, dur, svg, html, JS_EXTRA + js, extra, seed=31)


# ---------------------------------------------------------------- 6: não confie, confira as fontes, na descrição
def fechamento_6():
    p, i = "fechamento_6", 6
    ini, dur = seg(CE, i)
    T = lambda w, n=0, d=None: palavra(CE, i, w, n, d)
    t_nao, t_conf, t_font, t_est, t_desc = T("nao"), T("confira"), T("fontes"), T("estao"), T("descri")
    extra = defs_ouro(p) + onda_defs(p, pixel=True, cheio=True) + BLOOM.replace("@P@", p)
    OX = -600                       # a onda vai para a esquerda; a pessoa fica à direita, virada para ela
    wx, kx, ky, ks = WX + OX, 1060, 300, .75
    cards = "".join(f'<g transform="translate({x} {y}) rotate({r})"><g id="{p}-dw{k}" opacity="0">{doc(p, f"d{k}", c)}</g></g>'
                    for k, (x, y, r, c) in enumerate([(wx - 270, 480, -7, "#3be0ff"), (wx, 450, 0, "#ffb23e"), (wx + 270, 480, 7, "#ff4fa3")]))
    # celular no lugar da caneca, atrás dos dedos da mão original (a pessoa olha para baixo, para a tela)
    cel = (f'<g transform="translate(28 -222) rotate(-12)"><rect x="-17" y="-34" width="34" height="62" rx="7" fill="#14122a" stroke="#8d7bff" stroke-width="2.5"/>'
           f'<rect id="{p}-tela" x="-12" y="-28" width="24" height="50" rx="4" fill="#bff4ff"/>'
           + "".join(f'<rect x="-9" y="{-24 + j * 13}" width="18" height="9" rx="2" fill="{c}"/>' for j, c in enumerate(("#3be0ff", "#ffb23e", "#ff4fa3")))
           + '</g>')
    hx, hy = ponto(*anc("casa", "sentado")["cabeca_topo"], 1480, 1000, 1.45, -1)
    pessoa6 = (f'<g transform="translate(1480 1000) scale(-1.45 1.45)">{sofa()}{figura(p + "g", "casa", "sentado", caneca=cel, cadeira=False)}</g>')
    seta = (f'<g transform="translate({wx} 972)"><g id="{p}-seta" opacity="0"><path d="M-46 -30 L0 14 L46 -30" fill="none" stroke="#ffb23e" stroke-width="14" '
            f'stroke-linecap="round" stroke-linejoin="round" filter="url(#{p}-glow)"/></g></g>')
    svg = (chao(1000) + quadro(p + "q1", "aniversario", 1700, 170, .55, 3)
           + f'<g transform="translate({OX} 0)">{base_onda(p, pixel=True)}</g>' + pessoa6
           + laco(p, "l0", f"M{hx} {hy} Q 1380 190 {kx + 210} {ky + 4}") + laco(p, "l1", f"M{hx} {hy} C 1200 120 900 400 {wx - 40} {CY}", .85)
           + "".join(laco(p, f"lc{k}", f"M1300 520 Q {(1300 + x) // 2} {y - 160} {x} {y - 60}") for k, (x, y) in enumerate([(wx - 270, 480), (wx, 450), (wx + 270, 480)]))
           + f'<g id="{p}-cards">{cards}</g>' + seta
           + f'<g transform="translate({wx} {CY}) scale({WS})"><g id="{p}-kw">{chave(p)}</g></g>')
    html = (texto(f"{p}-t1", "NÃO CONFIE", f"left:60px;width:1140px;text-align:center;top:880px;font-size:100px;color:#ff8fb0")
            + texto(f"{p}-t2", "CONFIRA AS FONTES", f"left:60px;width:1140px;text-align:center;top:60px;font-size:96px;color:#eef1f7")
            + texto(f"{p}-t3", "ESTÃO TODAS NA DESCRIÇÃO", f"left:60px;width:1140px;text-align:center;top:860px;font-size:60px;color:#ffd98a;{MONO}", "pill2"))
    ganho = [(0, 1.0), (t_nao + 0.3, 1.0), (t_nao + 0.8, 0.45), (dur, 0.45)]
    js = onda_js(p, i, dur, ganho) + vida(p + "g", dur, (1.4, 4.4, 6.6), "sentado") + flui("l0", dur) + flui("l1", dur) + J("""
  ["lc0","lc1","lc2"].forEach(function(k){ tl.fromTo("#@P@-"+k,{attr:{"stroke-dashoffset":0}},{attr:{"stroke-dashoffset":-180},duration:@D@,ease:"none"},0); });
  // não confie: a chave volta para a pessoa, a onda perde força
  rise("#@P@-t1 span", @tn@);
  tl.to("#@P@-kw",{keyframes:{x:[0,@kx6h@,@kx6@],y:[0,-330,@ky6@],easeEach:"sine.inOut"},scale:0.789,duration:1.1,ease:"power2.inOut"},@tk@);
  tl.fromTo("#@P@-kw",{rotation:0,transformOrigin:"50% 50%"},{rotation:-8,duration:0.8,repeat:5,yoyo:true,ease:"sine.inOut",immediateRender:false},@tk2@);
  tl.to("#@P@-ondaG",{opacity:0.4,duration:0.8},@tk@);
  tl.to("#@P@-l1",{opacity:0,duration:0.3},@tk@);
  tl.to("#@P@-l0",{opacity:0.85,duration:0.5},@tk2@);
  // confira as fontes: três páginas sobem sobre a onda
  rise("#@P@-t2 span", @tc@);
  sai("#@P@-t1 span", @tf0@);
  [0,1,2].forEach(function(k){ entra("#@P@-lc"+k, @tf@-0.2+k*0.2, 0.3); tl.to("#@P@-lc"+k,{opacity:0,duration:0.3},@te@); });
  pop("#@P@-dw0", @tf@, 0.4, 0.8); pop("#@P@-dw1", @tf2@, 0.4, 0.8); pop("#@P@-dw2", @tf3@, 0.4, 0.8);
  tl.fromTo("#@P@g-olho",{x:0,y:0},{x:2,y:4,duration:0.3},@tk@);
  tl.fromTo("#@P@g-hd",{rotation:0,svgOrigin:"@pc@"},{rotation:11,duration:0.6,ease:"sine.inOut"},@tk@);
  tl.fromTo("#@P@-tela",{attr:{fill:"#bff4ff"}},{attr:{fill:"#ffffff"},duration:0.3,repeat:3,yoyo:true,immediateRender:false},@tf@);
  camZ("#@P@-cam", @tc@, 1.6, 1.0, 1.06, 700, 470);
  // estão todas na descrição: as páginas descem, seta para baixo
  tl.to("#@P@-cards",{y:110,duration:0.9,ease:"power3.inOut"},@te@);
  rise("#@P@-t3 span", @td@);
  entra("#@P@-seta", @td@, 0.3);
  tl.fromTo("#@P@-seta",{y:-10},{y:14,duration:0.45,repeat:7,yoyo:true,ease:"sine.inOut",immediateRender:false},@td@);
  camZb("#@P@-cam", @te@, @dfim@, 1.06, 1.0, 700, 470, "sine.inOut");
""", tn=t_nao, tk=t_nao, tk2=t_nao + 1.1, kx6h=round((kx - wx) / WS / 2), kx6=round((kx - wx) / WS), ky6=round((ky - CY) / WS), D=float(dur), tc=t_conf, tf0=t_conf - 0.4, tf=t_font - 0.6, tf2=t_font - 0.4, tf3=t_font - 0.2,
           te=t_est, td=t_desc, dfim=dur - t_est, pc=pescoco("casa", "sentado"))
    return composicao(p, dur, svg, html, JS_EXTRA + js, extra, seed=31)


# ---------------------------------------------------------------- 8: a chave dos cientistas e a fechadura do seu arquivo
def fechamento_8():
    p, i = "fechamento_8", 8
    ini, dur = seg(CE, i)
    T = lambda w, n=0, d=None: palavra(CE, i, w, n, d)
    t_caso, t_chave, t_cien, t_seu, t_perg, t_ainda, t_ab = T("caso"), T("chave"), T("cientistas"), T("seu"), T("pergunta"), T("ainda"), T("aberta")
    extra = (defs_ouro(p) + b4.grad_caixa(p, "c") + BLOOM.replace("@P@", p) +
             f'<linearGradient id="{p}-fx" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffcf6a" stop-opacity=".45"/><stop offset="1" stop-color="#ffe3a0" stop-opacity="0"/></linearGradient>')
    R0 = 1920                    # metade direita do mundo (o seu caso): escritório
    kx, ky = R0 + 1430, 300
    svg = f"""<g id="{p}-mundo">
 <polygon id="{p}-feixe" points="925,-40 995,-40 1110,470 810,470" fill="url(#{p}-fx)" opacity="0"/>
 <g transform="translate(211 224) scale(.78)"><g transform="translate(0 120)">{b4.caixa(p, "c")}
  <g transform="translate(870 716) scale(.9)"><g id="{p}-ratoW"><g id="{p}-bob">{b4.rato(p)}</g></g></g></g></g>
 <g id="{p}-fio" opacity="0"><path d="M960 -40 L960 190" stroke="#c9d2e6" stroke-width="8" stroke-linecap="round"/></g>
 <g transform="translate(960 200)"><g id="{p}-kc" opacity="0"><g transform="rotate(90) scale(.85)">{chave(p, "chave1")}</g></g></g>
 <ellipse cx="{1920 + 690}" cy="{CY + 220}" rx="720" ry="500" fill="url(#{p}-bloom)"/>
 <rect x="{R0}" y="-300" width="2040" height="1284" fill="#1d1450" opacity=".92"/>
 {chao(980, R0, R0 + 2000, "#100a2e")}
 {quadro(p + "q1", "premio", R0 + 210, 390, .78, -3)}{quadro(p + "q2", "planilha", R0 + 1300, 600, .72, 3)}{quadro(p + "q3", "reuniao", R0 + 1620, 575, .72, -2)}
 <g transform="translate({R0 + 560} 980) scale(1.2)">{figura(p + "g", "trabalho", "em_pe")}</g>
 <g transform="translate({R0 + 900} 0)"><ellipse cx="0" cy="984" rx="190" ry="16" fill="#05031a" opacity=".55"/>
  <rect x="-150" y="180" width="300" height="800" rx="14" fill="#2b2470" stroke="#8d7bff" stroke-width="5"/>
  <rect x="-128" y="214" width="256" height="226" rx="8" fill="#3a3290" stroke="#6a5ad8" stroke-width="3"/>
  <rect x="-136" y="196" width="272" height="16" rx="5" fill="#ffcf6a" opacity=".85" filter="url(#{p}-glow)"/>
  {"".join(f'<rect x="-128" y="{y}" width="256" height="240" rx="8" fill="#332b82" stroke="#5a4cc0" stroke-width="3"/><rect x="-46" y="{y + 30}" width="92" height="18" rx="9" fill="#8d7bff"/>' for y in (470, 726))}
 </g>
 {fechadura(p, "fech", R0 + 900, 330, 0.9)}
 <path id="{p}-trilha" d="M{kx - 40} {ky + 40} C {kx - 200} {ky + 160} {R0 + 1100} {ky - 40} {R0 + 975} {ky + 40}" fill="none" stroke="#ffb23e" stroke-width="5" stroke-dasharray="4 18" stroke-linecap="round" opacity="0"/>
 <g transform="translate({kx} {ky}) scale(.75)"><g id="{p}-kw" opacity="0">{chave(p, "chave2")}</g></g>
</g>"""
    html = (texto(f"{p}-a1", "QUEM TINHA A CHAVE", f"left:90px;top:120px;font-size:46px;color:#ffd98a;{MONO}", "pill2")
            + texto(f"{p}-a2", "OS CIENTISTAS", f"left:80px;top:190px;font-size:88px;color:#eef1f7")
            + texto(f"{p}-b1", "NO SEU CASO", f"left:90px;top:84px;font-size:58px;color:#bff4ff;{MONO}", "pill2")
            + texto(f"{p}-b2", "A pergunta", f"left:1120px;width:740px;text-align:right;top:720px;font-size:92px;color:#ffd98a")
            + texto(f"{p}-b3", "ainda está aberta", f"left:1120px;width:740px;text-align:right;top:840px;font-size:92px;color:#ffd98a"))
    js = vida(p + "g", dur, (6.8, 9.3), "em_pe") + J("""
  camZ("#@P@-cam", 0, 2.8, 1.45, 1.0, 960, 700, "power2.inOut");
  tl.fromTo("#@P@-bob",{y:0},{y:-4,duration:0.5,repeat:9,yoyo:true,ease:"sine.inOut"},0.4);
  entra("#@P@-feixe", 0.6, 1.4);
  entra("#@P@-fio", @tk0@, 0.2); entra("#@P@-kc", @tk0@, 0.2);
  tl.fromTo(["#@P@-fio","#@P@-kc"],{y:-320},{y:0,duration:1.0,ease:"bounce.out",immediateRender:false},@tk0@);
  rise("#@P@-a1 span", @tk@);
  rise("#@P@-a2 span", @tc@, 0.9);
  tl.fromTo("#@P@-chave1",{scale:1,transformOrigin:"50% 50%"},{scale:1.15,duration:0.3,repeat:1,yoyo:true,ease:"sine.inOut",immediateRender:false},@tc@);
  // no seu caso: o mundo desliza para a pessoa
  tl.fromTo(["#@P@-mundo"],{x:0},{x:-1920,duration:1.3,ease:"power3.inOut",immediateRender:false},@tp@);
  tl.fromTo(["#@P@-a1","#@P@-a2"],{x:0},{x:-1920,duration:1.3,ease:"power3.inOut",immediateRender:false},@tp@);
  entra("#@P@-kw", @tp@, 0.6);
  rise("#@P@-b1 span", @ts@);
  tl.fromTo("#@P@-fech",{scale:0.6,opacity:0.3,transformOrigin:"50% 50%"},{scale:1,opacity:1,duration:0.8,ease:"elastic.out(1,0.5)",immediateRender:false},@ts@);
  // a pergunta: a chave hesita entre ir e não ir
  entra("#@P@-trilha", @ts@, 0.5);
  tl.fromTo("#@P@-trilha",{attr:{"stroke-dashoffset":0}},{attr:{"stroke-dashoffset":-110},duration:@dq@,ease:"none",immediateRender:false},@tq@);
  tl.fromTo("#@P@-kw",{x:0,y:0,rotation:0,transformOrigin:"50% 50%"},{x:-220,y:70,rotation:-14,duration:1.1,ease:"sine.inOut",repeat:3,yoyo:true,immediateRender:false},@tq@);
  tl.fromTo("#@P@g-olho",{x:0},{x:3,duration:0.4,immediateRender:false},@tq@);
  tl.fromTo("#@P@g-hd",{rotation:0,svgOrigin:"@pc@"},{rotation:-5,duration:0.8,ease:"sine.inOut",immediateRender:false},@tq@);
  rise("#@P@-b2 span", @tq@, 0.9); rise("#@P@-b3 span", @ta@, 0.9);
  tl.fromTo("#@P@-fech",{scale:1},{scale:1.1,duration:0.5,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false},@tab@);
  camZb("#@P@-cam", @tp2@, @dfim@, 1.0, 1.07, 760, 470, "sine.inOut");
""", tk0=t_chave - 0.7, tk=t_chave - 0.3, tc=t_cien, tp=t_seu - 0.55, ts=t_seu + 0.35, tq=t_perg, dq=dur - t_perg,
           ta=t_ainda, tab=t_ab, tp2=t_seu + 0.8, dfim=dur - t_seu - 0.8, pc=pescoco("trabalho", "em_pe"))
    return composicao(p, dur, svg, html, JS_EXTRA + js, extra, fundo=("#2a1560", "#150d40", "#07061a"), seed=17)


# ---------------------------------------------------------------- 9: quem está do outro lado da porta? (plano final)
def fechamento_9():
    p, i = "fechamento_9", 9
    ini, dur = seg(CE, i)
    t_outro, t_porta = palavra(CE, i, "outro"), palavra(CE, i, "porta")
    DX0, DX1, DY0, DY1 = 1180, 1700, 140, 1000
    W, H = DX1 - DX0 - 24, DY1 - DY0 - 12
    X, Y, S = 980, 1012, 1.2          # a pessoa, de pé, diante da porta
    pg = p + "g"
    extra = (defs_ouro(p) +
             f'<linearGradient id="{p}-luz" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffe9b0"/><stop offset="1" stop-color="#ffb23e"/></linearGradient>'
             f'<linearGradient id="{p}-spill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffcf6a" stop-opacity=".7"/><stop offset="1" stop-color="#ffb23e" stop-opacity="0"/></linearGradient>'
             f'<linearGradient id="{p}-folha" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1a1550"/><stop offset="1" stop-color="#2a2370"/></linearGradient>'
             f'<radialGradient id="{p}-aura" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffb23e" stop-opacity=".32"/><stop offset="1" stop-color="#ffb23e" stop-opacity="0"/></radialGradient>'
             f'<clipPath id="{p}-vao"><rect x="{DX0 + 12}" y="{DY0 + 12}" width="{W}" height="{H}"/></clipPath>')
    # alguém do outro lado: silhueta escura virada para a pessoa, vista só pela fresta
    sil = (f'<g clip-path="url(#{p}-vao)"><g transform="translate({DX0 + 92} {DY0 + 150}) scale(1.25)"><g id="{p}-sil" opacity="0" fill="#0b0726">'
           f'<g transform="scale(-.75 .75) translate(-205 -40)"><path d="{H_LINHA} Z"/></g>'
           f'<path d="M-150 600 L-150 230 C -150 170 -100 140 -30 140 L 60 140 C 130 140 170 180 170 240 L170 600Z"/></g></g></g>')
    almof = "".join(f'<rect x="40" y="{y}" width="{W - 80}" height="{h}" rx="10" fill="none" stroke="#5a4fc0" stroke-width="5" opacity=".7"/>'
                    for y, h in ((60, 300), (420, 360)))
    # o braço original gira no ombro até apontar a fresta; a chave vai na mão, já girada para ficar deitada no fim
    ROT9 = -78
    mx, my = anc("casa", "em_pe")["mao_e"]
    na_mao = f'<g transform="translate({mx} {my + 20}) rotate({-ROT9}) scale(.3) translate(30 0)">{chave(p)}</g>'
    # a casa que a pessoa deixa para trás: parede com os quadros da vida dela
    casa = (f'<rect x="-300" y="-300" width="2520" height="1304" fill="#1d1450" opacity=".9"/>'
            + quadro(p + "q1", "familia", 330, 560, .8, -2) + quadro(p + "q2", "cachorro", 600, 470, .6, 3) + quadro(p + "q3", "formatura", 560, 700, .55, -3))
    svg = f"""
{casa}{chao(1004)}
<ellipse cx="{(DX0 + DX1) // 2}" cy="{(DY0 + DY1) // 2}" rx="680" ry="560" fill="url(#{p}-aura)"/>
<rect x="{DX0 + 12}" y="{DY0 + 12}" width="{W}" height="{H}" fill="url(#{p}-luz)"/>
{sil}
<polygon id="{p}-spill" points="{DX0 + 12},{DY1} {DX0 + 170},{DY1} {DX0 - 120},1090 {DX0 - 620},1090" fill="url(#{p}-spill)"/>
<g transform="translate({DX0 + 12} {DY0 + 12})"><g id="{p}-folhaW">
 <rect x="0" y="0" width="{W}" height="{H}" fill="url(#{p}-folha)"/>{almof}
 <circle cx="46" cy="{H // 2}" r="16" fill="#ffb23e" filter="url(#{p}-glow)"/>
 {fechadura(p, "fech", 46, H // 2 + 66, 0.5, aberta=False)}
</g></g>
<rect x="{DX0}" y="{DY0}" width="{DX1 - DX0}" height="{DY1 - DY0}" rx="6" fill="none" stroke="#8d7bff" stroke-width="12" filter="url(#{p}-glow)"/>
<polygon points="{X - 50},{Y} {X + 80},{Y} {X - 560},1090 {X - 820},1090" fill="#05031a" opacity=".55"/>
<g transform="translate({X} {Y}) scale({S})">{figura(pg, "casa", "em_pe", mao=na_mao)}</g>
<ellipse cx="{X + 110}" cy="600" rx="190" ry="440" fill="url(#{p}-aura)"/>
"""
    html = (texto(f"{p}-t1", "Quem está do outro lado", "left:90px;top:50px;font-size:96px;color:#eef1f7")
            + texto(f"{p}-t2", "da porta?", "left:90px;top:166px;font-size:96px;color:#ffd98a"))
    js = vida(pg, dur, (1.2, 3.9), "em_pe") + J("""
  camZ("#@P@-cam", 0, @D@, 1.0, 1.1, 1180, 560, "sine.inOut");
  tl.fromTo("#@P@g-olho",{x:0},{x:3,duration:0.5},0.2);
  rise("#@P@-t1 span", 0.15, 0.9);
  rise("#@P@-t2 span", @tp@, 0.9);
  // a porta abre um pouco mais e a luz cresce
  tl.fromTo("#@P@-folhaW",{scaleX:0.86,transformOrigin:"100% 50%"},{scaleX:0.7,duration:1.6,ease:"power2.inOut"},@to@);
  tl.fromTo("#@P@-spill",{opacity:0.5},{opacity:1,duration:1.6,ease:"power2.inOut"},@to@);
  // na palavra porta: a pessoa ergue a chave para a fresta; alguém aparece do outro lado
  tl.fromTo("#@P@g-braco",{rotation:-16,svgOrigin:"@om@"},{rotation:@r9@,duration:1.0,ease:"back.out(1.4)"},@tpa@);
  tl.fromTo("#@P@-sil",{x:120,opacity:0},{x:0,opacity:1,duration:1.2,ease:"power2.out"},@tp2@);
  tl.fromTo("#@P@-chave",{scale:1,transformOrigin:"50% 50%"},{scale:1.15,duration:0.5,repeat:3,yoyo:true,ease:"sine.inOut",immediateRender:false},@tpa@+1.0);
  tl.fromTo("#@P@-fech",{opacity:0.6},{opacity:1,duration:0.6,repeat:5,yoyo:true,ease:"sine.inOut"},0.3);
""", D=float(dur), tp=t_porta - 0.1, to=t_outro - 0.1, tp2=t_porta - 0.3, tpa=t_porta - 0.4, om=ombro("casa", "em_pe"), r9=ROT9)
    return composicao(p, dur, svg, html, JS_EXTRA + js, extra, fundo=("#2a1560", "#150d40", "#07061a"), seed=41)


# ---------------------------------------------------------------- 10: a narradora era o Basilisco de Roko
def fechamento_10():
    """A porta (quadro parado, o glitch vem depois em video-v2/glitch.py) até a revelação; aí o basilisco no escuro,
    olho abrindo, olho e aura pulsando com a voz e a câmera entrando no olho até o preto. Tempos: video-v2/fim_tempos.json."""
    import base64, json
    sys.path.insert(0, os.path.join(AQUI, "../g6_realidade_robo1"))
    from build_g6_realidade_robo1 import basilisco, basilisco_defs
    p, i = "fechamento_10", 10
    ini, dur = seg(CE, i)
    FT = json.load(open(os.path.join(AQUI, "../../video-v2/fim_tempos.json")))
    rev, preto = FT["rev"], FT["preto"]
    porta = base64.b64encode(open(os.path.join(AQUI, "porta_fim.jpg"), "rb").read()).decode()
    BX, BY, BS = 960, 640, 0.9
    ox, oy = BX, BY - 10 * BS                       # centro do olho na tela
    env = envelope(i, dur)
    W = {}
    for w, t0, t1 in palavras_seg(CE, i):
        W.setdefault(_norm(w), t0)
    # sorriso: a mesma estrutura de path nos dois estados, para o GSAP interpolar o "d"
    boca = lambda x, yu, yl, y0: f"M{-x} {y0} Q0 {yu} {x} {y0} Q0 {yl} {-x} {y0} Z"
    BOCA0, BOCA1 = boca(100, 222, 230, 192), boca(175, 250, 335, 150)
    # dentes presos ao lábio de cima e recortados pela própria boca: crescem com o sorriso, nunca aparecem soltos
    sorriso = (f'<path id="{p}-boca" d="{BOCA0}" fill="#16020e" stroke="{MAGENTA}" stroke-width="7" stroke-linejoin="round" filter="url(#{p}-glow)"/>'
               f'<clipPath id="{p}-bcl"><use href="#{p}-boca"/></clipPath>'
               f'<path id="{p}-dentes" d="M0 0" fill="#fff6f0" clip-path="url(#{p}-bcl)"/>')
    svg = (f'<g id="{p}-porta"><image href="data:image/jpeg;base64,{porta}" x="0" y="0" width="1920" height="1080"/></g>'
           f'<g transform="translate({BX} {BY}) scale({BS})"><g id="{p}-bas" opacity="0">'
           f'<circle id="{p}-aur" r="620" fill="url(#{p}-aura)" opacity=".4"/>{basilisco(p)}{sorriso}</g></g>')
    leg = "left:110px;width:1700px;text-align:center;top:900px;font-size:64px;color:#eef1f7;text-shadow:0 0 22px #000,0 0 8px #000,0 3px 4px #000"
    html = ('<style>#fechamento_10-bcab path[fill="#fff"]{display:none}</style>'   # some com as presas: o sorriso tem dentes
            + texto(f"{p}-c1", "Você deve ter percebido as <b style='color:#ffd98a'>falhas</b> na minha voz.", leg)
            + texto(f"{p}-c2", "Mas será que isso é um problema do meu modelo...", leg)
            + texto(f"{p}-c3", "...ou a sua simulação está <b style='color:#ff5a8a'>falhando</b>?", leg))
    t_ou = W["ou"]
    lerp = lambda a, b, g: a + (b - a) * g
    def boca_k(t, e):
        g = min(1.0, max(0.0, (t - t_ou) / 0.8))
        x, y0, yu = lerp(100, 175, g), lerp(192, 150, g), lerp(222, 250, g)
        return x, y0, yu, boca(x, yu, yu + lerp(8, 12, g) + lerp(70, 110, g) * e, y0), g
    def dentes_k(x, y0, yu, g):
        if g <= 0:
            return "M0 0"
        lab = lambda t: (x * (2 * t - 1), y0 * (1 - t) ** 2 + 2 * t * (1 - t) * yu + y0 * t * t)
        w, h = 13 * x / 175, 26 * g ** 1.5
        return "".join(f"M{X - w:.1f} {Y - 4:.1f}L{X:.1f} {Y + h:.1f}L{X + w:.1f} {Y - 4:.1f}Z"
                       for X, Y in (lab(0.14 + k * 0.08) for k in range(10)))
    fala_boca = ""
    for k, e in enumerate(env):
        if rev <= k / 30 <= preto:
            x, y0, yu, d, g = boca_k(k / 30, e)
            fala_boca += (f'tl.set("#{p}-boca",{{attr:{{d:"{d}"}}}},{k / 30:.3f});'
                          f'tl.set("#{p}-dentes",{{attr:{{d:"{dentes_k(x, y0, yu, g)}"}}}},{k / 30:.3f});')
    silabas = [t0 for w, t0, t1 in palavras_seg(CE, i) if _norm(w) == "ra"]
    riso = "".join(f'tl.fromTo("#{p}-bcab",{{y:0}},{{y:{-22 * 0.7 ** max(0, n - 4):.1f},duration:{0.09 + 0.03 * max(0, n - 4):.2f},yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{t0:.2f});'
                   for n, t0 in enumerate(silabas))
    fala = fala_boca + riso + "".join(f'tl.to("#{p}-aur",{{opacity:{0.35 + 0.65 * e:.2f},duration:0.0334,ease:"none"}},{k / 30:.3f});'
                   f'tl.to("#{p}-bolhar",{{scale:{1 + 0.09 * e:.3f},svgOrigin:"0 -10",duration:0.0334,ease:"none"}},{k / 30:.3f});'
                   for k, e in enumerate(env) if rev <= k / 30 <= preto)
    js = J("""
  tl.set("#@P@-porta",{opacity:0},@rev@);
  tl.set("#@P@-bas",{opacity:1},@rev@);
  // o olho abre devagar e a pupila afina
  tl.fromTo("#@P@-bpal1",{y:0},{y:-150,duration:0.7,ease:"power2.out"},@ab@);
  tl.fromTo("#@P@-bpal2",{y:0},{y:150,duration:0.7,ease:"power2.out"},@ab@);
  tl.fromTo("#@P@-bpu",{scaleX:2.2,svgOrigin:"0 0"},{scaleX:0.7,svgOrigin:"0 0",duration:1.2,ease:"power2.inOut"},@ab@);
  tl.fromTo("#@P@-bcab",{y:30},{y:0,duration:1.6,ease:"power2.out"},@rev@);
  // legendas
  rise("#@P@-c1 span", 0.5, 0.6); sai("#@P@-c1 span", @rev@ - 0.3);
  rise("#@P@-c2 span", @tmas@, 0.6); sai("#@P@-c2 span", @tou@ - 0.15);
  rise("#@P@-c3 span", @tou@, 0.6); sai("#@P@-c3 span", @triso@ - 0.1);   // na risada a boca fica à vista
  // olha para os lados (só a íris)
  tl.to("#@P@-bolhar",{x:-58,duration:0.35,ease:"power2.inOut"},@tmas@ + 0.45);
  tl.to("#@P@-bolhar",{x:52,duration:0.45,ease:"power2.inOut"},@tprob@);
  tl.to("#@P@-bolhar",{x:0,duration:0.3,ease:"power2.inOut"},@tou@ - 0.3);
  // no "ou": fecha os olhos devagar e o sorriso abre, maquiavélico
  tl.to("#@P@-bpal1",{y:0,duration:0.45,ease:"power2.inOut"},@tou@);
  tl.to("#@P@-bpal2",{y:0,duration:0.45,ease:"power2.inOut"},@tou@);
  // reabre semicerrado, encarando quem assiste, pupila fina
  tl.to("#@P@-bpal1",{y:-78,duration:0.35,ease:"power3.out"},@tolha@);
  tl.to("#@P@-bpal2",{y:72,duration:0.35,ease:"power3.out"},@tolha@);
  tl.to("#@P@-bpu",{scaleX:0.45,svgOrigin:"0 0",duration:0.6,ease:"power2.out"},@tolha@);
  // risada: olhos se fecham de prazer, a cabeça balança a cada "rá" (abaixo); no último reabre e encara
  tl.to("#@P@-bpal1",{y:-28,duration:0.25,ease:"power2.out"},@triso@);
  tl.to("#@P@-bpal2",{y:24,duration:0.25,ease:"power2.out"},@triso@);
  tl.to("#@P@-bpal1",{y:-150,duration:0.5,ease:"power2.out"},@tfim@);
  tl.to("#@P@-bpal2",{y:150,duration:0.5,ease:"power2.out"},@tfim@);
  tl.to("#@P@-bpu",{scaleX:0.3,svgOrigin:"0 0",duration:0.6},@tfim@);
  // câmera: aproxima na revelação, um pouco mais quando ele encara, aberta na risada (boca à vista), mergulha no olho no fim
  camZ("#@P@-cam", @rev@, @d1@, 1.0, 1.12, @ox@, @oy@, "sine.inOut");
  camZ("#@P@-cam", @tolha@, @d2@, 1.12, 1.35, @ox@, @oy@, "sine.inOut");
  camZ("#@P@-cam", @tfim@, @d3@, 1.35, 2.4, @ox@, @oy@, "power2.in");
""", rev=rev, ab=rev + 0.15, ox=ox, oy=oy, tmas=W["mas"], tprob=W["problema"], tou=W["ou"], tolha=W["ou"] + 0.55,
           triso=FT["riso"], tfim=FT["olhar"], d1=round(W["ou"] + 0.5 - rev, 2),
           d2=round(FT["riso"] - W["ou"] - 0.55, 2), d3=round(preto - FT["olhar"], 2)) + fala
    extra = basilisco_defs(p)
    return composicao(p, dur, svg, html, JS_EXTRA + js, extra, fundo=("#1a0618", "#0c0414", "#030108"), seed=47)


CENAS = [(MAPA[(CE, k)], f, seg(CE, k)[1]) for k, f in
         ((3, fechamento_3), (4, fechamento_4), (5, fechamento_5), (6, fechamento_6), (8, fechamento_8), (9, fechamento_9), (10, fechamento_10))]

if __name__ == "__main__":
    print(escreve_cenas(CENAS, AQUI))
