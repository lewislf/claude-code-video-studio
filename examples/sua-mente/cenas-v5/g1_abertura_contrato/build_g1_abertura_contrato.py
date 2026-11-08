"""Cenas v5, grupo g1: fim da abertura e bloco do contrato (Ruptura).

  python3 build_g1_abertura_contrato.py     # escreve compositions/, index.html e tempos.json desta pasta

Motivo recorrente: a chave âmbar (M8) e a fechadura (porta do fim do corredor F).
"""
import math, os, random, re, sys
AQUI0 = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI0, ".."))
from motor import *  # noqa: F401,F403  (traz AQUI do motor, que aponta para cenas-v5)
AQUI = AQUI0
sys.path.insert(0, os.path.join(AQUI0, "../../cenas-v4"))
import build4 as b4  # noqa: E402  (caixa, rato, grad_caixa do camundongo aprovado)
from arte2 import mosca_rica, mosca_defs  # noqa: E402
from gente import gente, quadro, orbe, ANCORAS  # noqa: E402


def vida_gente(p, dur, piscadas=(2.0, 5.3, 8.8, 12.1, 16.4, 20.2)):
    """Como gente.vida_gente, sem a respiração em {p}-tor: o tronco novo tem paths de máscara de 19998 px (M-9999...),
    o getBBox fica gigante e scaleY com transformOrigin em % desloca o tronco ~150 px para cima (cabeça dentro da camisa).
    Fica o balanço da cabeça (em {p}-cab, só y) e as piscadas."""
    n = max(1, int(dur / 1.7))
    js = f'tl.fromTo("#{p}-cab",{{y:0}},{{y:-4,duration:1.7,repeat:{n},yoyo:true,ease:"sine.inOut"}},0.2);'
    for t in piscadas:
        if t < dur - 0.3:
            js += f'tl.fromTo("#{p}-olho",{{scaleY:1,transformOrigin:"50% 50%"}},{{scaleY:0.08,transformOrigin:"50% 50%",duration:0.09,repeat:1,yoyo:true,immediateRender:false}},{t});'
    return js

# ---------------------------------------------------------------- câmera por quadros-chave
# Cada quadro: [t, zoom, cx, cy(, ease)]. O ponto (cx, cy) fica no centro da tela. Zoom interpolado em log, easeInOutCubic.
CAM_JS = r"""
  function cam(sel, ks){
    var el=document.querySelector(sel);
    function ap(z,cx,cy){el.setAttribute("transform","translate(960 540) scale("+z+") translate("+(-cx)+" "+(-cy)+")");}
    ap(ks[0][1],ks[0][2],ks[0][3]);
    function seg(a,b){
      var o={u:0}, la=Math.log(a[1]), lb=Math.log(b[1]), ez=gsap.parseEase(b[4]||"power3.inOut");
      tl.fromTo(o,{u:0},{u:1,duration:Math.max(0.01,b[0]-a[0]),ease:"none",immediateRender:false,onUpdate:function(){
        var e=ez(o.u); ap(Math.exp(la+(lb-la)*e), a[2]+(b[2]-a[2])*e, a[3]+(b[3]-a[3])*e);}},a[0]);
    }
    for(var i=0;i+1<ks.length;i++){seg(ks[i],ks[i+1]);}
  }
  function olha(sel,t,x,dur){tl.to(sel,{x:x,duration:dur||0.35,ease:"power2.inOut"},t);}
"""
# só nas cenas com a pessoa nova (fora do CAM_JS para não mexer no HTML das outras cenas)
GENTE_JS = r"""
  // origem de transformação num ponto local (x, y) do grupo: a pessoa nova tem paths de máscara enormes e "50% 50%" cai longe
  function oG(sel,x,y){try{var b=document.querySelector(sel).getBBox();return (x-b.x)+"px "+(y-b.y)+"px";}catch(e){return "50% 100%";}}
  function popG(sel,t,x,y,from,dur){
    tl.fromTo(sel,{scale:from||0.3,opacity:0,transformOrigin:oG(sel,x,y)},{scale:1,opacity:1,duration:dur||0.7,ease:"elastic.out(1,0.45)",immediateRender:false},t);
    tl.set(sel,{opacity:0},0);
  }
"""


def comp(p, dur, svg_cam, html, js, extra="", fixo="", fundo=("#3a1d7a", "#1a1050", "#0b0a24"), seed=3):
    """Como motor.composicao, mas com `fixo` (svg fora da câmera, por cima) e a câmera por quadros-chave."""
    corpo = f'<g id="{p}-cam">{svg_cam}</g>{fixo}'
    return composicao2(p, dur, corpo, html, JS_LIB + CAM_JS + js, extra, fundo=fundo, seed=seed)


def T_(cena, sg):
    return lambda w, n=0, d=None: palavra(cena, sg, w, n, d)


# ---------------------------------------------------------------- peças do motivo e do escritório
def chave(p, k="chave", s=1.0, x=0, y=0, op=0):
    """Chave âmbar (desenho de cenas-v4/build4.py::cena_M8, com brilho). Centro local ~ (0, 60). Id animável {p}-{k}."""
    return (f'<g transform="translate({x} {y}) scale({s})"><g id="{p}-{k}" opacity="{op}"><rect x="-60" y="-50" width="120" height="220" fill="none"/>'
            f'<g filter="url(#{p}-glow)"><circle cx="0" cy="0" r="34" fill="none" stroke="{AMBAR}" stroke-width="12"/>'
            f'<path d="M0 34 L0 130 M0 100 L30 100 M0 124 L22 124" stroke="{AMBAR}" stroke-width="12" fill="none" stroke-linecap="round"/></g>'
            f'<circle cx="-12" cy="-14" r="6" fill="#fff3c8" opacity=".8"/></g></g>')


def fechadura(p, k="fech", s=1.0, x=0, y=0, op=1, luz=True):
    """Espelho de fechadura em linha âmbar, buraco aceso. Centro local (0, 0), caixa ~ 140 x 240."""
    miolo = AMBAR if luz else "#05031a"
    return (f'<g transform="translate({x} {y}) scale({s})"><g id="{p}-{k}" opacity="{op}"><rect x="-70" y="-120" width="140" height="240" fill="none"/>'
            f'<rect x="-62" y="-112" width="124" height="224" rx="40" fill="#14123a" stroke="{AMBAR}" stroke-width="7" filter="url(#{p}-glow)"/>'
            f'<g id="{p}-{k}-buraco"><circle cx="0" cy="-26" r="26" fill="{miolo}"/><polygon points="-14,-10 14,-10 26,62 -26,62" fill="{miolo}"/></g>'
            f'<circle cx="-40" cy="-90" r="5" fill="{AMBAR}" opacity=".7"/><circle cx="40" cy="90" r="5" fill="{AMBAR}" opacity=".7"/></g></g>')


def folha_svg(p, k="folha", linhas=7, titulo=True, miudas=0):
    """Folha de contrato (centro local 0,0; 520 x 660). Assinatura em {p}-assin (dasharray 320), linha vazia à direita.
    `miudas`: linhas de letra miúda entre o corpo e as assinaturas."""
    ls = "".join(f'<rect x="-210" y="{-250 + j * 34}" width="{360 if j % 3 else 270}" height="10" rx="5" fill="#8a7f68" opacity=".45"/>' for j in range(linhas))
    ls += "".join(f'<rect x="-210" y="{10 + j * 16}" width="{420 - (j % 4) * 30}" height="5" rx="2.5" fill="#8a7f68" opacity=".55"/>' for j in range(miudas))
    tit = '<rect x="-210" y="-300" width="200" height="20" rx="6" fill="#5a4a30" opacity=".75"/>' if titulo else ""
    return (f'<g id="{p}-{k}"><rect x="-260" y="-330" width="520" height="660" fill="none"/>'
            f'<g filter="url(#{p}-sombra)"><rect x="-260" y="-330" width="520" height="660" rx="16" fill="url(#{p}-papel)"/></g>{tit}{ls}'
            f'<line x1="-210" y1="260" x2="-20" y2="260" stroke="#3a3a3a" stroke-width="4"/><line x1="40" y1="260" x2="230" y2="260" stroke="#3a3a3a" stroke-width="4"/>'
            f'<path id="{p}-assin" d="M-205 252 C -180 200 -160 270 -140 230 S -100 210 -80 250 S -50 230 -28 246" fill="none" stroke="#1d2f9a" stroke-width="7" stroke-linecap="round" stroke-dasharray="320" stroke-dashoffset="320"/>'
            f'<g id="{p}-vazio" opacity="0"><circle cx="135" cy="228" r="40" fill="#ff4f7d"/><text x="135" y="246" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="52" fill="#fff">?</text></g></g>')


def grad_escritorio(p):
    return (f'<linearGradient id="{p}-papel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#e9dcc2"/></linearGradient>'
            f'<linearGradient id="{p}-parede" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a1850"/><stop offset=".72" stop-color="#2a2878"/><stop offset=".72" stop-color="#15134a"/><stop offset="1" stop-color="#0c0a2e"/></linearGradient>'
            f'<linearGradient id="{p}-luzp" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffe9a8" stop-opacity=".7"/><stop offset="1" stop-color="#ffe9a8" stop-opacity=".05"/></linearGradient>'
            f'<radialGradient id="{p}-tela" cx="50%" cy="40%" r="70%"><stop offset="0" stop-color="#3be0ff" stop-opacity=".55"/><stop offset="1" stop-color="#1a3b86" stop-opacity=".2"/></radialGradient>')


def porta(p, x, y=190, k="porta", aberta=0.0, fech=True):
    """Porta (340 x 680) com luz quente atrás e fechadura âmbar. {p}-{k}-folha é a folha da porta (scaleX para abrir)."""
    f = fechadura(p, k + "-fch", 0.5, x + 290, y + 360, 1, False) if fech else ""
    return (f'<g id="{p}-{k}"><rect x="{x - 20}" y="{y - 20}" width="380" height="720" rx="18" fill="#0c0a2e" stroke="#8d7bff" stroke-width="8" filter="url(#{p}-glow)"/>'
            f'<rect x="{x}" y="{y}" width="340" height="680" fill="url(#{p}-luzp)"/>'
            f'<g id="{p}-{k}-folha"><rect x="{x}" y="{y}" width="340" height="680" fill="#24206a" stroke="#4a46b0" stroke-width="4"/>'
            f'<rect x="{x + 40}" y="{y + 50}" width="260" height="250" rx="8" fill="none" stroke="#3a3690" stroke-width="5"/>'
            f'<rect x="{x + 40}" y="{y + 360}" width="200" height="260" rx="8" fill="none" stroke="#3a3690" stroke-width="5"/>{f}</g></g>')


def mesa(p, x0, larg=1000, y=640, k="mesa"):
    """Mesa vista de frente (tampo em y) com monitor à direita e sombra."""
    mx = x0 + larg - 330
    return (f'<g id="{p}-{k}"><ellipse cx="{x0 + larg / 2:.0f}" cy="{y + 268}" rx="{larg * 0.52:.0f}" ry="26" fill="#05031a" opacity=".55"/>'
            f'<rect x="{x0 + 60}" y="{y + 40}" width="40" height="230" fill="#22186a"/><rect x="{x0 + larg - 100}" y="{y + 40}" width="40" height="230" fill="#22186a"/>'
            f'<rect x="{x0}" y="{y}" width="{larg}" height="44" rx="12" fill="#3a2a8c" stroke="#5a4ad0" stroke-width="3"/>'
            f'<rect x="{mx + 110}" y="{y - 40}" width="40" height="40" fill="#2a1d70"/><rect x="{mx + 50}" y="{y - 10}" width="160" height="12" rx="6" fill="#2a1d70"/>'
            f'<rect x="{mx}" y="{y - 230}" width="260" height="180" rx="14" fill="#0e0c26" stroke="#8d7bff" stroke-width="6"/>'
            f'<rect id="{p}-{k}-tela" x="{mx + 14}" y="{y - 216}" width="232" height="152" rx="6" fill="url(#{p}-tela)"/></g>')


# ---------------------------------------------------------------- contrato 3: quem assinou foi a pessoa de fora
def contrato_3():
    CE, SG = "contrato", 3
    p = "contrato_3"
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_ass, t_fora, t_trab, t_sofre, t_ob, t_dentro, t_nunca, t_nada, t_nasceu, t_emp = (
        T("assinou"), T("pessoa"), T("trabalha"), T("sofre"), T("obedece"), T("dentro") - 0.15, T("nunca"), T("nada"), T("nasceu"), T("empregada"))
    SH = 1380  # deslocamento do mundo de fora para dentro
    pilha = "".join(f'<rect x="{2600 + (k % 3) * 8}" y="{628 - k * 15}" width="150" height="12" rx="3" fill="#fffaf0" stroke="#c9bb98" stroke-width="1.5" transform="rotate({(k % 3 - 1) * 2} 2675 {628 - k * 15})"/>' for k in range(9))
    DX, DY, DS = 2350, 900, 1.1                 # pessoa de dentro (camisa e gravata), sentada diante da mesa
    cc = ANCORAS[("trabalho", "sentado", 30)]["cabeca_centro"]
    nx, ny = DX + (cc[0] + 4) * DS, DY + (cc[1] + 52) * DS   # base do pescoço (gola) da pessoa nova
    cracha = (f'<g id="{p}-cracha" opacity="0"><path d="M{nx - 22:.0f} {ny:.0f} L{nx:.0f} {ny + 52:.0f} L{nx + 22:.0f} {ny:.0f}" fill="none" stroke="{AMBAR}" stroke-width="5" stroke-linejoin="round"/>'
              f'<g transform="translate({nx:.0f} {ny + 52:.0f}) scale(.36)"><g id="{p}-crachaB"><rect x="-150" y="-10" width="300" height="190" fill="none"/>'
              f'<rect x="-150" y="0" width="300" height="180" rx="18" fill="#fffaf0" stroke="{AMBAR}" stroke-width="7"/><rect x="-36" y="-14" width="72" height="26" rx="8" fill="{AMBAR}"/>'
              f'<rect x="-122" y="34" width="104" height="116" rx="10" fill="#2a2878"/>'
              f'<g transform="translate(-130 40) scale(.42)"><path d="{H_LINHA}" fill="none" stroke="#3be0ff" stroke-width="7" stroke-linecap="round"/></g>'
              f'<rect x="4" y="50" width="120" height="16" rx="8" fill="#8a7f68"/><rect x="4" y="84" width="90" height="14" rx="7" fill="#bfb49a"/><rect x="4" y="114" width="110" height="14" rx="7" fill="#bfb49a"/></g></g></g>')
    extra = grad_escritorio(p)
    svg = f"""
<g id="{p}-mundo">
 <rect x="-600" y="-300" width="4400" height="1600" fill="url(#{p}-parede)"/>
 {porta(p, 60, 180)}
 <ellipse cx="810" cy="870" rx="270" ry="24" fill="#05031a" opacity=".5"/>
 <g transform="translate(780 870) scale(1.05)"><g id="{p}-fora" opacity="0">{gente(p + "-gf", "casa", "em_pe", glow=p + "-glow")}</g></g>
 {mesa(p, 2150, 1000)}
 <g id="{p}-pilha" opacity="0">{pilha}</g>
 <g transform="translate({DX} {DY}) scale({DS})"><g id="{p}-dentro" opacity="0">{gente(p + "-gd", "trabalho", "sentado", glow=p + "-glow")}</g></g>
 <g id="{p}-gotas" opacity="0" fill="#7fe6ff"><path d="M2420 370 q-12 26 0 36 q12 -10 0 -36z"/><path d="M2450 420 q-10 22 0 30 q10 -8 0 -30z"/></g>
 {cracha}
</g>
<g transform="translate(1330 470)"><g id="{p}-folhaM"><g id="{p}-folhaW" opacity="0">{folha_svg(p)}<circle cx="0" cy="-306" r="20" fill="{VERM}" stroke="#fff3c8" stroke-width="4"/><circle cx="-6" cy="-312" r="6" fill="#fff" opacity=".7"/></g></g></g>"""
    html = (texto(f"{p}-t1", "DE FORA", "left:560px;width:520px;text-align:center;top:905px;font-size:80px;color:#bff4ff;letter-spacing:.12em") +
            texto(f"{p}-t2", "DE DENTRO", "left:920px;width:640px;text-align:center;top:930px;font-size:80px;color:#c9b8ff;letter-spacing:.12em") +
            texto(f"{p}-t3", "NASCEU EMPREGADA", "left:0;right:0;text-align:center;top:60px;font-size:104px;color:#ffd98a"))
    js = f"""
  cam("#{p}-cam", [[0,1.0,960,540],[{t_trab - 0.3:.2f},1.0,960,540],[{t_nunca - 0.2:.2f},1.0,960,540],[{dur:.2f},1.0,1030,540,"sine.inOut"]]);
  popG("#{p}-fora", 0.2, 0, 0, 0.5, 0.8);
  entra("#{p}-folhaW", {t_ass - 0.2:.2f}, 0.3); tl.fromTo("#{p}-folhaW",{{scale:0.5,transformOrigin:"50% 50%"}},{{scale:1,duration:0.7,ease:"elastic.out(1,0.5)",immediateRender:false}},{t_ass - 0.2:.2f});
  olha("#{p}-gf-olho", {t_ass:.2f}, 3);
  tl.fromTo("#{p}-assin",{{attr:{{"stroke-dashoffset":320}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.9,ease:"power2.inOut"}},{t_ass + 0.25:.2f});
  rise("#{p}-t1 span", {t_fora:.2f});
  tl.fromTo(["#{p}-mundo","#{p}-t1"],{{x:0}},{{x:-{SH},duration:1.3,ease:"power3.inOut",immediateRender:false}},{t_trab - 0.25:.2f});
  tl.fromTo("#{p}-folhaM",{{x:0,scale:1,transformOrigin:"50% 50%"}},{{x:-930,scale:0.8,transformOrigin:"50% 50%",duration:1.3,ease:"power3.inOut",immediateRender:false}},{t_trab - 0.25:.2f});
  popG("#{p}-dentro", {t_trab - 0.1:.2f}, 0, 0, 0.5, 0.8);
  entra("#{p}-pilha", {t_trab:.2f}, 0.1);
  tl.fromTo("#{p}-pilha rect",{{y:-160,opacity:0}},{{y:0,opacity:1,duration:0.35,ease:"bounce.out",stagger:0.3}},{t_trab:.2f});
  entra("#{p}-gotas", {t_sofre:.2f}, 0.2); tl.fromTo("#{p}-gotas",{{y:0}},{{y:40,duration:0.8,repeat:2,ease:"power1.in"}},{t_sofre:.2f}); some("#{p}-gotas", {t_ob + 0.4:.2f}, 0.3);
  tl.fromTo("#{p}-dentro",{{y:0}},{{y:8,duration:0.25,repeat:3,yoyo:true,ease:"sine.inOut"}},{t_ob:.2f});
  rise("#{p}-t2 span", {t_dentro:.2f});
  olha("#{p}-gd-olho", {t_nunca - 0.3:.2f}, -3);
  entra("#{p}-vazio", {t_nunca:.2f}, 0.15); tl.fromTo("#{p}-vazio",{{scale:2.2,transformOrigin:"50% 50%"}},{{scale:1,duration:0.6,ease:"back.out(3)",immediateRender:false}},{t_nunca:.2f});
  tl.fromTo("#{p}-folhaW",{{rotation:0}},{{rotation:2.5,duration:0.1,repeat:5,yoyo:true,ease:"none",immediateRender:false}},{t_nada:.2f});
  tl.fromTo("#{p}-dentro",{{rotation:0,transformOrigin:oG("#{p}-dentro",0,-200)}},{{rotation:3,duration:0.12,repeat:7,yoyo:true,ease:"none",immediateRender:false}},{t_nada:.2f});
  olha("#{p}-gd-olho", {t_nasceu - 0.2:.2f}, 0);
  tl.to("#{p}-t2 span",{{yPercent:125,duration:0.5,ease:"power2.in"}},{t_nasceu - 0.3:.2f});
  rise("#{p}-t3 span", {t_nasceu:.2f}, 0.9);
  entra("#{p}-cracha", {t_nasceu:.2f}, 0.1);
  tl.fromTo("#{p}-cracha",{{y:-260}},{{y:0,duration:0.9,ease:"bounce.out",immediateRender:false}},{t_nasceu:.2f});
  tl.fromTo("#{p}-crachaB",{{rotation:-8,transformOrigin:"50% 0%"}},{{rotation:0,duration:1.4,ease:"elastic.out(1,0.3)",immediateRender:false}},{t_nasceu + 0.7:.2f});
""" + vida_gente(p + "-gf", dur) + vida_gente(p + "-gd", dur, (3.6, 7.0, 10.4))
    return comp(p, dur, svg, html, GENTE_JS + js, extra)


# ---------------------------------------------------------------- contrato 2: olhe o contrato com calma
def contrato_2():
    CE, SG = "contrato", 2
    p = "contrato_2"
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_par, t_ali, t_mas, t_olhe, t_con, t_cal = T("parece"), T("alivio"), T("mas"), T("olhe"), T("contrato"), T("calma")
    GX, GY, GS = 520, 1475, 1.8                 # plano fechado: a pessoa de moletom em pé, cortada no quadril (barra do moletom), lendo a proposta
    cc = ANCORAS[("casa", "em_pe", 30)]["cabeca_centro"]
    bx, by = GX + cc[0] * GS, GY + cc[1] * GS     # cabeça
    big = "".join(f'<rect x="-150" y="{-104 + j * 34}" width="{300 - (j % 3) * 40}" height="12" rx="6" fill="#8a7f68" opacity=".75"/>' for j in range(7))
    extra = grad_escritorio(p) + f'<clipPath id="{p}-lc"><circle cx="0" cy="0" r="122"/></clipPath>'
    svg = f"""
<circle id="{p}-halo" cx="{bx:.0f}" cy="{by:.0f}" r="300" fill="#38e8a8" opacity="0" filter="url(#{p}-blur40)"/>
<g transform="translate({GX} {GY}) scale({GS})"><g id="{p}-pes">{gente(p + "-ga", "casa", "em_pe", glow=p + "-glow", sombra=False)}</g></g>
<g transform="translate(1380 520)"><g id="{p}-folhaW">{folha_svg(p, miudas=8)}</g></g>
<g transform="translate(1390 586)"><g id="{p}-lupa" opacity="0"><rect x="-150" y="-150" width="420" height="420" fill="none"/>
 <path d="M92 92 L210 210" stroke="#8d7bff" stroke-width="30" stroke-linecap="round"/><path d="M92 92 L210 210" stroke="#b9adff" stroke-width="10" stroke-linecap="round" opacity=".6"/>
 <g clip-path="url(#{p}-lc)"><circle r="122" fill="#fffaf0"/><rect id="{p}-marca" x="-160" y="-2" width="320" height="24" fill="#ff4f7d" opacity="0"/>{big}</g>
 <circle r="126" fill="none" stroke="#3be0ff" stroke-width="12" filter="url(#{p}-glow)"/><path d="M-80 -70 A 100 100 0 0 1 -20 -104" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round" opacity=".7"/></g></g>"""
    html = (texto(f"{p}-t1", "PARECE UM ALÍVIO", "left:0;right:0;text-align:center;top:28px;font-size:96px;color:#bff8e4") +
            texto(f"{p}-t2", "OLHE O CONTRATO", "left:560px;width:770px;top:960px;font-size:70px;color:#eef1f7") +
            texto(f"{p}-t3", "COM CALMA", "left:1290px;width:520px;top:960px;font-size:70px;color:#ffd98a"))
    js = f"""
  cam("#{p}-cam", [[0,1.0,960,540],[{t_mas:.2f},1.04,900,540,"sine.inOut"],[{t_con + 0.1:.2f},1.12,1100,540],[{dur:.2f},1.16,1110,540,"sine.inOut"]]);
  tl.set("#{p}-assin",{{attr:{{"stroke-dashoffset":0}}}},0);
  popG("#{p}-pes", 0.1, 0, -300, 0.6, 0.8); pop("#{p}-folhaW", 0.25, 0.6, 0.8);
  rise("#{p}-t1 span", {t_par:.2f});
  tl.fromTo("#{p}-halo",{{opacity:0}},{{opacity:0.45,duration:0.5,yoyo:true,repeat:1,ease:"sine.inOut"}},{t_ali:.2f});
  tl.fromTo("#{p}-ga-olho",{{scaleY:1,transformOrigin:"50% 50%"}},{{scaleY:0.1,transformOrigin:"50% 50%",duration:0.2,yoyo:true,repeat:1,repeatDelay:0.4,immediateRender:false}},{t_ali:.2f});
  tl.fromTo("#{p}-pes",{{y:0}},{{y:6,duration:0.45,yoyo:true,repeat:1,ease:"sine.inOut",immediateRender:false}},{t_ali:.2f});
  tl.to("#{p}-t1 span",{{yPercent:-125,duration:0.45,ease:"power2.in"}},{t_mas - 0.1:.2f});
  olha("#{p}-ga-olho", {t_mas:.2f}, 3);
  rise("#{p}-t2 span", {t_olhe:.2f});
  entra("#{p}-lupa", {t_olhe:.2f}, 0.2);
  tl.fromTo("#{p}-lupa",{{x:520,y:260,rotation:12,transformOrigin:"50% 50%"}},{{x:0,y:0,rotation:0,duration:0.9,ease:"power3.out",immediateRender:false}},{t_olhe:.2f});
  tl.fromTo("#{p}-lupa",{{x:0}},{{x:-40,duration:1.6,ease:"sine.inOut",yoyo:true,repeat:1,immediateRender:false}},{t_olhe + 0.9:.2f});
  rise("#{p}-t3 span", {t_cal - 0.2:.2f});
  tl.fromTo("#{p}-marca",{{opacity:0,scaleX:0,transformOrigin:"0% 50%"}},{{opacity:0.55,scaleX:1,duration:0.6,ease:"power2.out"}},{t_cal:.2f});
""" + vida_gente(p + "-ga", dur, (3.9,))
    return comp(p, dur, svg, html, GENTE_JS + js, extra)


# ---------------------------------------------------------------- contrato 4: essa escolha seria livre?
def contrato_4():
    CE, SG = "contrato", 4
    p = "contrato_4"
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_cons, t_ext, t_como, t_aceita, t_nunca, t_lemb, t_rec, t_cus, t_emp, t_essa, t_esc, t_livre = (
        T("consentimento"), T("extremo"), T("como"), T("aceita"), T("nunca"), T("lembrar"), T("recusar"), T("custasse"), T("emprego"),
        T("essa"), T("escolha"), T("livre"))
    PX, PY, S = 420, 970, 1.2                   # pessoa em pé (trabalho), pés em PY
    bx, by = PX + 260, PY - 600 * S             # a lembrança da assinatura, num orbe ao lado do rosto
    cc = ANCORAS[("trabalho", "em_pe", 30)]["cabeca_centro"]
    nx, ny = PX + (cc[0] + 4) * S, PY + (cc[1] + 48) * S     # base do pescoço (gola) da pessoa nova
    FX, FY = 1420, 545                          # folha
    cbx, cby = FX - 150, FY + 130               # centro da caixinha de aceite
    cracha = (f'<g id="{p}-cracha" opacity="0"><path id="{p}-cordao" d="M{nx - 22:.0f} {ny:.0f} L{nx:.0f} {ny + 58:.0f} L{nx + 22:.0f} {ny:.0f}" fill="none" stroke="{AMBAR}" stroke-width="5" stroke-linejoin="round"/>'
              f'<g transform="translate({nx:.0f} {ny + 58:.0f}) scale(.42)"><g id="{p}-crachaB"><rect x="-140" y="-12" width="280" height="190" fill="none"/>'
              f'<rect id="{p}-crachaF" x="-130" y="0" width="260" height="160" rx="16" fill="#fffaf0" stroke="{AMBAR}" stroke-width="7"/><rect x="-30" y="-12" width="60" height="22" rx="7" fill="{AMBAR}"/>'
              f'<rect x="-106" y="28" width="90" height="104" rx="9" fill="#2a2878"/><g transform="translate(-112 34) scale(.37)"><path d="{H_LINHA}" fill="none" stroke="#3be0ff" stroke-width="7"/></g>'
              f'<rect x="4" y="44" width="104" height="14" rx="7" fill="#8a7f68"/><rect x="4" y="76" width="78" height="12" rx="6" fill="#bfb49a"/><rect x="4" y="102" width="96" height="12" rx="6" fill="#bfb49a"/></g></g></g>')
    botao = lambda k, y, cor, icone: (f'<g transform="translate(1480 {y})"><g id="{p}-{k}" opacity="0"><rect x="-150" y="-150" width="300" height="300" fill="none"/>'
                                     f'<circle r="132" fill="#0e0c2e" stroke="{cor}" stroke-width="12" filter="url(#{p}-glow)"/><circle r="104" fill="{cor}" opacity=".16"/>'
                                     f'<path d="{icone}" fill="none" stroke="{cor}" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/></g></g>')
    extra = grad_escritorio(p)
    svg = f"""
<ellipse id="{p}-sombraP" cx="{PX + 20}" cy="{PY + 6}" rx="230" ry="22" fill="#05031a" opacity="0"/>
<ellipse id="{p}-sombraC" cx="{PX - 155}" cy="{PY + 4}" rx="62" ry="8" fill="#05031a" opacity="0"/>
<g transform="translate({PX} {PY}) scale({S})"><g id="{p}-pes">{gente(p + "-ga", "trabalho", "em_pe", glow=p + "-glow")}</g></g>
<g id="{p}-memW">{orbe(p + "-mem", "relogio", round(bx), round(by), AMBAR, 58)}</g>
{cracha}
<g transform="translate({FX} {FY})"><g id="{p}-folhaM"><g id="{p}-folhaW" opacity="0">{folha_svg(p, linhas=6, miudas=0)}
 <rect x="-200" y="80" width="100" height="100" rx="12" fill="#fffaf0" stroke="#3a3a3a" stroke-width="6"/>
 <path id="{p}-check" d="M-186 128 L-158 160 L-104 84" fill="none" stroke="#1faa7a" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="160" stroke-dashoffset="160"/>
 <rect x="-60" y="112" width="250" height="12" rx="6" fill="#8a7f68" opacity=".55"/><rect x="-60" y="140" width="190" height="12" rx="6" fill="#8a7f68" opacity=".55"/></g></g></g>
<path id="{p}-fio" d="M{bx:.0f} {by:.0f} C {bx + 260:.0f} {by - 160:.0f} {cbx - 220:.0f} {cby - 260:.0f} {cbx:.0f} {cby:.0f}" fill="none" stroke="{AMBAR}" stroke-width="7" stroke-dasharray="1400" stroke-dashoffset="1400" stroke-linecap="round" filter="url(#{p}-glow)"/>
{botao("sim", 360, MENTA, "M-52 4 L-14 44 L58 -44")}
{botao("nao", 760, VERM, "M-44 -44 L44 44 M44 -44 L-44 44")}"""
    html = (texto(f"{p}-t1", "CONSENTIMENTO", "left:0;right:0;text-align:center;top:34px;font-size:110px;color:#eef1f7") +
            texto(f"{p}-t2", "NUNCA VAI CONSEGUIR LEMBRAR", "left:720px;right:30px;text-align:center;top:940px;font-size:66px;color:#ffd98a") +
            texto(f"{p}-t3", "ESSA ESCOLHA SERIA LIVRE?", "left:0;right:0;text-align:center;top:34px;font-size:100px;color:#eef1f7"))
    js = f"""
  cam("#{p}-cam", [[0,0.95,{FX},{FY - 20}],[{t_ext - 0.05:.2f},0.99,{FX},{FY - 20},"sine.inOut"],[{t_ext + 0.35:.2f},1.3,{cbx + 60},{cby - 70},"power4.out"],[{t_como - 0.1:.2f},1.32,{cbx + 60},{cby - 70},"none"],
       [{t_aceita + 0.3:.2f},1.0,960,540],[{t_essa:.2f},1.0,960,540],[{dur:.2f},1.04,960,540,"sine.inOut"]]);
  entra("#{p}-folhaW", 0.05, 0.4);
  rise("#{p}-t1 span", {t_cons:.2f});
  tl.fromTo("#{p}-check",{{attr:{{"stroke-dashoffset":160}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.5,ease:"power2.out"}},{t_cons + 0.6:.2f});
  tl.to("#{p}-t1 span",{{yPercent:-125,duration:0.35,ease:"power2.in"}},{t_ext - 0.3:.2f});
  popG("#{p}-pes", {t_como:.2f}, 0, 0, 0.6, 0.8); tl.fromTo("#{p}-sombraP",{{opacity:0}},{{opacity:0.5,duration:0.5}},{t_como:.2f});
  entra("#{p}-mem", {t_aceita:.2f}, 0.3);
  tl.fromTo("#{p}-fio",{{attr:{{"stroke-dashoffset":1400}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.8,ease:"power2.inOut"}},{t_aceita:.2f});
  tl.fromTo("#{p}-assin",{{attr:{{"stroke-dashoffset":320}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.7,ease:"power2.inOut"}},{t_aceita + 0.5:.2f});
  rise("#{p}-t2 span", {t_nunca:.2f});
  tl.to("#{p}-mem",{{opacity:0.15,scale:0.4,transformOrigin:"50% 50%",duration:0.8,ease:"power2.in"}},{t_nunca + 0.2:.2f});
  tl.to("#{p}-fio",{{attr:{{"stroke-dashoffset":-1400}},duration:0.7,ease:"power2.in"}},{t_lemb:.2f});
  tl.to("#{p}-check",{{opacity:0.2,duration:0.5}},{t_lemb:.2f});
  olha("#{p}-ga-olho", {t_lemb:.2f}, -3);
  tl.to("#{p}-t2 span",{{yPercent:125,duration:0.4,ease:"power2.in"}},{t_rec - 0.3:.2f});
  tl.to("#{p}-folhaM",{{x:700,opacity:0,duration:0.6,ease:"power2.in"}},{t_rec - 0.3:.2f});
  pop("#{p}-sim", {t_rec - 0.1:.2f}, 0.4, 0.7); pop("#{p}-nao", {t_rec + 0.1:.2f}, 0.4, 0.7);
  olha("#{p}-ga-olho", {t_rec:.2f}, 3);
  tl.fromTo("#{p}-nao",{{scale:1}},{{scale:0.86,duration:0.15,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{t_rec + 0.8:.2f});
  entra("#{p}-cracha", {t_cus:.2f}, 0.1);
  tl.fromTo("#{p}-cracha",{{y:-200}},{{y:0,duration:0.7,ease:"bounce.out",immediateRender:false}},{t_cus:.2f});
  tl.to("#{p}-cordao",{{opacity:0,duration:0.15}},{t_emp:.2f});
  tl.to("#{p}-crachaF",{{attr:{{fill:"#8a8aa0"}},duration:0.3}},{t_emp:.2f});
  tl.to("#{p}-crachaB",{{x:-430,y:960,rotation:-74,transformOrigin:"50% 0%",duration:0.6,ease:"power2.in"}},{t_emp + 0.05:.2f});  // cai no chão ao lado do pé
  tl.fromTo("#{p}-sombraC",{{opacity:0}},{{opacity:0.55,duration:0.2,immediateRender:false}},{t_emp + 0.55:.2f});
  rise("#{p}-t3 span", {t_essa:.2f}, 0.9);
  tl.fromTo("#{p}-sim",{{scale:1}},{{scale:1.1,duration:0.45,yoyo:true,repeat:1,ease:"sine.inOut",immediateRender:false}},{t_esc:.2f});
  tl.fromTo("#{p}-nao",{{scale:1}},{{scale:1.1,duration:0.45,yoyo:true,repeat:1,ease:"sine.inOut",immediateRender:false}},{t_esc + 0.9:.2f});
  olha("#{p}-ga-olho", {t_esc:.2f}, -2); olha("#{p}-ga-olho", {t_esc + 0.9:.2f}, 3); olha("#{p}-ga-olho", {t_livre:.2f}, 0);
""" + vida_gente(p + "-ga", dur, (5.2, 9.6, 12.6))
    return comp(p, dur, svg, html, GENTE_JS + js, extra)


# ---------------------------------------------------------------- contrato 5: alguém pode guardar a chave
def contrato_5():
    CE, SG = "contrato", 5
    p = "contrato_5"
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_rup, t_fic, t_ning, t_div, t_mem, t_mas, t_lemb, t_tranc, t_alg, t_guar, t_chave, t_nao = (
        T("ruptura"), T("ficcao"), T("ninguem"), T("dividir"), T("memoria"), T("mas"), T("lembranca"), T("trancada"),
        T("alguem"), T("guardar"), T("chave"), T("nao"))
    PX, PY, S = 150, 170, 2.9
    ox, oy = PX + 215 * S, PY + 72 * S          # a lembrança
    AX, AY, AS = 2000, 200, 2.6                 # alguém (espelhado)
    kx, ky = AX - 200 * AS, AY + 92 * AS        # onde a chave fica guardada (dentro da cabeça de alguém)
    KS = 0.55
    cer = lambda k: f'<g transform="translate(196 118) scale(.82) translate(-196 -118)">{cerebro_lateral(p + k)}</g>'
    olho = (f'<g id="{p}-olho"><ellipse cx="257" cy="129" rx="9" ry="5.6" fill="#0a0820" stroke="#3be0ff" stroke-width="1.2"/><circle cx="259" cy="129" r="3.6" fill="#29b6ff"/><circle cx="260.2" cy="127.8" r="1.1" fill="#fff"/></g>'
            f'<path d="M 245 118 Q 257 111 269 119" fill="none" stroke="#3be0ff" stroke-width="2" stroke-linecap="round"/>')
    extra = (f'<clipPath id="{p}-cA"><rect x="60" y="0" width="134" height="300"/></clipPath><clipPath id="{p}-cB"><rect x="194" y="0" width="140" height="300"/></clipPath>'
             f'<radialGradient id="{p}-orbg"><stop offset="0" stop-color="#fffbe8"/><stop offset=".5" stop-color="#ffd98a"/><stop offset="1" stop-color="#ffb23e" stop-opacity="0"/></radialGradient>'
             f'<linearGradient id="{p}-sil" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c1450"/><stop offset="1" stop-color="#0a0828"/></linearGradient>')
    svg = f"""
<ellipse cx="{PX + 205 * S:.0f}" cy="{PY + 262 * S:.0f}" rx="270" ry="22" fill="#05031a" opacity=".5"/>
<g transform="translate({PX} {PY}) scale({S})"><g id="{p}-pes"><g id="{p}-bob">{cabeca_linha(p + "h", p + "-glow")}
 <g id="{p}-cerA" clip-path="url(#{p}-cA)">{cer("c1")}</g><g id="{p}-cerB" clip-path="url(#{p}-cB)">{cer("c2")}</g>
 <path id="{p}-corte" d="M194 22 L194 168" stroke="{AMBAR}" stroke-width="2.6" stroke-dasharray="7 6" fill="none" opacity="0" filter="url(#{p}-glow)"/>{olho}</g></g></g>
<g transform="translate({AX} {AY}) scale({-AS} {AS})"><g id="{p}-alg" opacity="0"><path d="{H_LINHA} Z" fill="url(#{p}-sil)" stroke="#8d7bff" stroke-width="3" stroke-linejoin="round" filter="url(#{p}-glow)"/></g></g>
<circle id="{p}-orb" cx="{ox:.0f}" cy="{oy:.0f}" r="34" fill="url(#{p}-orbg)" opacity="0"/>
{fechadura(p, "fch", 0.42, round(ox), round(oy), 0)}
{chave(p, "chave", KS, round(ox), round(oy - 60 * KS), 0)}"""
    dx, dy = (kx - ox) / KS, (ky - oy) / KS
    html = (texto(f"{p}-t1", "RUPTURA É FICÇÃO", "left:0;right:0;text-align:center;top:40px;font-size:100px;color:#eef1f7") +
            texto(f"{p}-t2", "TRANCADA", "left:0;right:0;text-align:center;top:40px;font-size:110px;color:#ffd98a;letter-spacing:.06em") +
            texto(f"{p}-t3", "A CHAVE", "left:0;right:0;text-align:center;top:40px;font-size:100px;color:#ffd98a") +
            texto(f"{p}-t4", "NÃO É TÃO FICCIONAL", "left:0;right:0;text-align:center;top:920px;font-size:88px;color:#eef1f7"))
    js = f"""
  cam("#{p}-cam", [[0,1.0,960,540],[{t_mas:.2f},1.06,820,540,"sine.inOut"],[{t_tranc - 0.1:.2f},2.2,{ox + 60:.0f},{oy + 50:.0f}],[{t_alg - 0.3:.2f},2.3,{ox + 60:.0f},{oy + 50:.0f},"none"],
       [{t_chave + 0.1:.2f},1.0,1080,540],[{dur:.2f},1.05,1080,560,"sine.inOut"]]);
  pop("#{p}-pes", 0.1, 0.6, 0.8);
  tl.fromTo("#{p}-corte",{{opacity:0}},{{opacity:1,duration:0.3}},{t_rup:.2f});
  tl.fromTo("#{p}-corte",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-130}},duration:{t_mem - t_rup:.2f},ease:"none"}},{t_rup:.2f});
  tl.fromTo("#{p}-cerA",{{x:0}},{{x:-9,duration:0.7,ease:"power3.out",immediateRender:false}},{t_rup + 0.2:.2f});
  tl.fromTo("#{p}-cerB",{{x:0}},{{x:9,duration:0.7,ease:"power3.out",immediateRender:false}},{t_rup + 0.2:.2f});
  rise("#{p}-t1 span", {t_rup:.2f});
  tl.to("#{p}-t1 span",{{yPercent:-125,duration:0.45,ease:"power2.in"}},{t_ning:.2f});
  tl.to("#{p}-cerA",{{x:-15,duration:0.18,yoyo:true,repeat:5,ease:"sine.inOut"}},{t_div:.2f});
  tl.to("#{p}-cerB",{{x:15,duration:0.18,yoyo:true,repeat:5,ease:"sine.inOut"}},{t_div:.2f});
  tl.to(["#{p}-cerA","#{p}-cerB"],{{x:0,duration:0.8,ease:"elastic.out(1,0.4)"}},{t_mem:.2f});
  tl.to("#{p}-corte",{{opacity:0,duration:0.4}},{t_mem + 0.2:.2f});
  tl.fromTo("#{p}-orb",{{opacity:0,scale:0.2,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.7,ease:"elastic.out(1,0.5)"}},{t_lemb:.2f});
  tl.fromTo("#{p}-orb",{{scale:1}},{{scale:1.25,duration:0.4,yoyo:true,repeat:1,ease:"sine.inOut",immediateRender:false}},{t_lemb + 0.8:.2f});
  pop("#{p}-fch", {t_tranc:.2f}, 1.8, 0.6);
  tl.to("#{p}-orb",{{scale:0.6,duration:0.4}},{t_tranc:.2f});
  rise("#{p}-t2 span", {t_tranc:.2f});
  tl.to("#{p}-t2 span",{{yPercent:-125,duration:0.4,ease:"power2.in"}},{t_alg - 0.4:.2f});
  entra("#{p}-chave", {t_alg - 0.4:.2f}, 0.3);
  tl.fromTo("#{p}-chave",{{y:0}},{{y:-150,duration:0.5,ease:"power2.out",immediateRender:false}},{t_alg - 0.4:.2f});
  entra("#{p}-alg", {t_alg:.2f}, 0.6);
  tl.to("#{p}-chave",{{keyframes:{{x:[0,{dx * 0.45:.0f},{dx:.0f}],y:[-150,{dy - 520:.0f},{dy:.0f}],easeEach:"sine.inOut"}},rotation:360,transformOrigin:"50% 30%",duration:{max(0.8, t_chave - t_alg + 0.2):.2f},ease:"power1.inOut"}},{t_alg + 0.1:.2f});
  tl.fromTo("#{p}-chave",{{scale:1}},{{scale:2.6,duration:0.6,ease:"elastic.out(1,0.5)",immediateRender:false}},{t_chave + 0.3:.2f});
  rise("#{p}-t3 span", {t_chave:.2f});
  rise("#{p}-t4 span", {t_nao:.2f}, 0.9);
  olha("#{p}-olho", {t_chave:.2f}, 3);
  tl.fromTo("#{p}-bob",{{y:0}},{{y:-4,duration:1.6,repeat:8,yoyo:true,ease:"sine.inOut"}},0);
"""
    return comp(p, dur, svg, html, js, extra, seed=9)


# ---------------------------------------------------------------- contrato 0: casa e trabalho lado a lado, a porta que apaga a memória
def contrato_0():
    CE, SG = "contrato", 0
    p = "contrato_0"
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_prop, t_ben, t_est, t_ao, t_sair, t_esc, t_esq, t_tudo, t_dentro, t_cob, t_trab, t_conf, t_nao, t_casa = (
        T("proposta"), T("beneficio"), T("estranho"), T("ao"), T("sair"), T("escritorio"), T("esquece"), T("tudo"), T("dentro"),
        T("cobrancas"), T("trabalho"), T("conflitos"), T("nao"), T("casa"))
    CH, PX0, LIM, OX = 880, 1300, 2000, 2520     # chão, cadeira, plano da porta (casa | trabalho), lugar no escritório
    S = 1.1
    # horários da caminhada: entra 3.75 -> 5.35 e sai 5.6 -> 8.4; w_porta e w_sai são os instantes
    # em que o meio do corpo cruza o plano da porta (na volta coincide com "esquece")
    w_lev, w_mesa, w_volta, w_cad = 3.75, 5.35, 5.6, 8.4
    inv = lambda f: math.sqrt(f / 2) if f < 0.5 else 1 - math.sqrt((1 - f) / 2)     # inverso de power1.inOut (o ease de anda)
    w_porta = w_lev + (w_mesa - w_lev) * inv((LIM - PX0) / (OX - PX0))
    w_sai = w_volta + (w_cad - w_volta) * inv((OX - LIM) / (OX - PX0))

    def pessoa_g(k, var, pose, x, flip=False, op=0):
        return (f'<g transform="translate({x} {CH}) scale({-S if flip else S} {S})"><g id="{p}-w{k}" opacity="{op}">'
                f'{gente(f"{p}-g{k}", var, pose, glow=p + "-glow", cadeira=False)}</g></g>')

    def cadeira_fixa(x):
        """Só a cadeira do desenho sentado (com os clipPaths e o rim dela), para continuar no lugar quando a pessoa levanta."""
        g = gente(f"{p}-ch", "casa", "sentado")
        defs = g[g.index("<defs>"):g.index("</defs>") + 7]
        cad = re.search(r"<!--cad-->.*?<!--/cad-->", g, re.S).group(0)
        return f'<g transform="translate({x} {CH}) scale({S})">{defs}<g filter="url(#{p}-ch-rim)">{cad}</g></g>'
    casa_q = [("familia", 260, 250, -2), ("aniversario", 550, 230, 2), ("carro", 840, 260, -1), ("formatura", 390, 520, 1), ("praia", 710, 540, -2)]
    trab_q = [("premio", 2900, 240, 1), ("reuniao", 3180, 220, -1), ("planilha", 3460, 240, 2), ("cafe", 3740, 225, -2)]
    quadros_c = "".join(quadro(f"{p}-qc{k}", t, x, y, 1.0, r) for k, (t, x, y, r) in enumerate(casa_q))
    quadros_t = "".join(quadro(f"{p}-qt{k}", t, x, y, 0.95, r, moldura="#5a6a9a") for k, (t, x, y, r) in enumerate(trab_q))
    orb_c = [("coracao", 1095, 320, "#ff4fa3"), ("sol", 1250, 245, "#ffd23e"), ("bolo", 1430, 255, "#ffb23e"), ("carro", 1050, 480, "#ff7a5a"), ("nota", 1590, 360, "#ff9bd0")]
    orb_t = [("relogio", 2290, 200, "#3be0ff"), ("raio", 2470, 115, "#8d7bff"), ("copo", 2710, 390, "#38e8a8"), ("relogio", 2670, 185, "#6a8cff")]   # fora do caminho da cabeça
    orbes_c = "".join(f'<g id="{p}-oc{k}w">{orbe(f"{p}-oc{k}", s_, x, y, c, 64)}</g>' for k, (s_, x, y, c) in enumerate(orb_c))
    orbes_t = "".join(f'<g id="{p}-ot{k}w">{orbe(f"{p}-ot{k}", s_, x, y, c, 64)}</g>' for k, (s_, x, y, c) in enumerate(orb_t))
    # cobranças: folhas com cifrão que caem e se apoiam na porta, do lado do escritório
    fatura = lambda k, x, rot: (f'<g transform="translate({x} {CH - 100}) rotate({rot})"><g id="{p}-f{k}" opacity="0"><rect x="-80" y="-100" width="160" height="200" rx="10" fill="#fffaf0" stroke="#c9bb98" stroke-width="3"/>'
                                f'<circle cx="0" cy="-30" r="44" fill="#ff4f7d"/><text x="0" y="-4" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="74" fill="#fff">$</text>'
                                f'<rect x="-56" y="34" width="112" height="10" rx="5" fill="#8a7f68" opacity=".6"/><rect x="-56" y="56" width="80" height="10" rx="5" fill="#8a7f68" opacity=".6"/></g></g>')
    faturas = fatura(0, 2250, -8) + fatura(1, 2390, 6) + fatura(2, 2320, -2) + fatura(3, 2470, 10) + fatura(4, 2560, -14)
    # conflitos: faíscas vermelhas
    faisca = lambda k, x, y, s: (f'<g transform="translate({x} {y}) scale({s})"><g id="{p}-z{k}" opacity="0"><rect x="-70" y="-70" width="140" height="140" fill="none"/>'
                                 f'<g stroke="#ff4f7d" stroke-width="9" stroke-linecap="round" filter="url(#{p}-glow)">'
                                 + "".join(f'<path d="M{24 * math.cos(a):.0f} {24 * math.sin(a):.0f} L{62 * math.cos(a + 0.12):.0f} {62 * math.sin(a + 0.12):.0f}"/>' for a in [j * math.pi / 4 + 0.2 for j in range(8)])
                                 + f'</g><path d="M-14 -22 L6 -4 L-8 2 L12 22" fill="none" stroke="#fff3f6" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g></g>')
    faiscas = faisca(0, 2300, 520, 1.2) + faisca(1, 2560, 420, 1.0) + faisca(2, 2440, 650, 0.9) + faisca(3, 2700, 600, 1.1) + faisca(4, 2230, 360, 0.8)
    extra = grad_escritorio(p) + (
        f'<linearGradient id="{p}-pcasa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a1f5e"/><stop offset="1" stop-color="#5a2f6e"/></linearGradient>'
        f'<linearGradient id="{p}-ptrab" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16285a"/><stop offset="1" stop-color="#22407a"/></linearGradient>'
        f'<linearGradient id="{p}-chao" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a1240"/><stop offset="1" stop-color="#07061a"/></linearGradient>'
        f'<radialGradient id="{p}-abaj"><stop offset="0" stop-color="#ffe2a0" stop-opacity=".5"/><stop offset="1" stop-color="#ffe2a0" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="{p}-clC"><rect x="-900" y="-900" width="{LIM + 900}" height="2700"/></clipPath>'
        f'<clipPath id="{p}-clT"><rect x="{LIM}" y="-900" width="2900" height="2700"/></clipPath>')
    svg = f"""
<rect x="-900" y="-900" width="2900" height="1780" fill="url(#{p}-pcasa)"/>
<rect x="2000" y="-900" width="2900" height="1780" fill="url(#{p}-ptrab)"/>
<rect x="-900" y="{CH}" width="5800" height="900" fill="url(#{p}-chao)"/><rect x="-900" y="{CH - 6}" width="5800" height="10" fill="#8d7bff" opacity=".35"/>
<ellipse cx="900" cy="300" rx="900" ry="420" fill="url(#{p}-abaj)"/>
<ellipse cx="{PX0 + 20}" cy="{CH + 30}" rx="330" ry="40" fill="#7a3a6a" opacity=".55"/>
<g id="{p}-qc">{quadros_c}</g>
<g id="{p}-qt">{quadros_t}</g>
{mesa(p, 2700, 1000)}
<path d="M2000 -900 L2000 180" stroke="#8d7bff" stroke-width="6" opacity=".45"/>
{faturas}
{faiscas}
{porta(p, 1830, 200)}
<rect id="{p}-flare" x="1830" y="200" width="340" height="680" fill="#fff4d0" opacity="0" filter="url(#{p}-blur6)"/>
{cadeira_fixa(PX0)}
{pessoa_g("A", "casa", "sentado", PX0, op=1)}
<!-- a travessia: a mesma pessoa em dois desenhos andando juntos, casa recortada à esquerda do plano da porta e trabalho
     à direita; no meio da porta o corpo é metade moletom, metade camisa -->
<g clip-path="url(#{p}-clC)">{pessoa_g("B", "casa", "em_pe", PX0)}{pessoa_g("E", "casa", "em_pe", OX, flip=True)}</g>
<g clip-path="url(#{p}-clT)">{pessoa_g("C", "trabalho", "em_pe", PX0)}{pessoa_g("D", "trabalho", "em_pe", OX, flip=True)}</g>
<g id="{p}-veu" opacity="0"><rect x="{LIM - 14}" y="200" width="28" height="680" fill="#fff4d0" opacity=".55" filter="url(#{p}-blur6)"/><rect x="{LIM - 5}" y="200" width="10" height="680" fill="#fffbea"/></g>
<g id="{p}-oc">{orbes_c}</g>
<g id="{p}-ot">{orbes_t}</g>
<g transform="translate(1650 600) scale(.42)"><g id="{p}-folhaM"><g id="{p}-folhaW" opacity="0">{folha_svg(p, miudas=6)}
 <g transform="translate(140 175)"><g id="{p}-selo" opacity="0"><rect x="-80" y="-80" width="160" height="160" fill="none"/>
  <path d="{' '.join(('M' if j == 0 else 'L') + f'{(70 if j % 2 == 0 else 52) * math.cos(j * 3.14159 / 12):.1f} {(70 if j % 2 == 0 else 52) * math.sin(j * 3.14159 / 12):.1f}' for j in range(24))} Z" fill="{AMBAR}" stroke="#fff3c8" stroke-width="4"/>
  <circle r="36" fill="none" stroke="#fff3c8" stroke-width="5"/></g></g></g></g></g>"""
    html = (texto(f"{p}-t1", "PROPOSTA DE EMPREGO", "left:0;right:0;text-align:center;top:40px;font-size:96px;color:#eef1f7") +
            texto(f"{p}-t2", "BENEFÍCIO ESTRANHO", "left:0;right:0;text-align:center;top:40px;font-size:96px;color:#ffd98a") +
            texto(f"{p}-t3", "VOCÊ ESQUECE TUDO", "left:0;right:0;text-align:center;top:40px;font-size:100px;color:#bff4ff") +
            texto(f"{p}-t4", '<i style="background:#ff4f7d;width:26px;height:26px"></i>COBRANÇAS', "left:520px;top:940px;font-size:66px;color:#ff9bb0", cls="pill2") +
            texto(f"{p}-t5", '<i style="background:#ff4f7d;width:26px;height:26px"></i>CONFLITOS', "left:1140px;top:940px;font-size:66px;color:#ff9bb0", cls="pill2") +
            texto(f"{p}-t6", "NÃO VÃO PARA CASA", "left:0;right:0;text-align:center;top:40px;font-size:100px;color:#ffd98a"))
    some_ = lambda k, t: f'tl.fromTo("#{p}-w{k}",{{opacity:1}},{{opacity:0,duration:0.02,immediateRender:false}},{t:.2f});'
    mostra = lambda k, t: f'tl.fromTo("#{p}-w{k}",{{opacity:0}},{{opacity:1,duration:0.02,immediateRender:false}},{t:.2f});'
    anda = lambda k, t0, t1, dx: (f'tl.fromTo("#{p}-w{k}",{{x:0}},{{x:{dx / S:.0f},duration:{t1 - t0:.2f},ease:"power1.inOut",immediateRender:false}},{t0:.2f});'
                                  f'tl.fromTo("#{p}-g{k}",{{y:0}},{{y:-10,duration:0.18,yoyo:true,repeat:{max(1, int((t1 - t0) / 0.18) - 1)},ease:"sine.inOut",immediateRender:false}},{t0:.2f});')
    js = f"""
  cam("#{p}-cam", [[0,0.86,1100,540],[{w_lev - 0.2:.2f},0.9,1120,540,"sine.inOut"],[{w_porta - 0.3:.2f},0.7,1960,560],[{w_porta + 0.25:.2f},0.7,2060,560,"none"],
       [{w_mesa + 0.15:.2f},1.0,2900,540],[{w_volta + 0.3:.2f},1.0,2880,540,"none"],[{w_sai - 0.25:.2f},0.75,2060,540],[{w_sai + 0.2:.2f},0.75,1980,540,"none"],
       [{t_esq + 0.6:.2f},0.8,2000,540],[{t_dentro + 0.3:.2f},0.8,2000,540,"none"],[{t_cob + 0.4:.2f},1.0,2560,540],
       [{t_nao - 0.2:.2f},1.06,2560,540,"sine.inOut"],[{t_casa - 0.2:.2f},0.92,1170,540],[{dur:.2f},0.93,1170,540,"sine.inOut"]]);
  tl.fromTo("#{p}-qc > g",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.6,ease:"back.out(2)",stagger:0.12}},0.15);
  tl.fromTo("#{p}-oc > g",{{opacity:0}},{{opacity:1,duration:0.4,stagger:0.1}},0.4);
"""
    for k in range(len(orb_c)):
        js += f'  tl.fromTo("#{p}-oc{k}",{{y:0}},{{y:-14,duration:{1.1 + 0.17 * k:.2f},yoyo:true,repeat:{int(dur / (1.1 + 0.17 * k))},ease:"sine.inOut"}},0);\n'
    for k in range(len(orb_t)):
        js += f'  tl.fromTo("#{p}-ot{k}",{{y:0}},{{y:-12,duration:{0.9 + 0.15 * k:.2f},yoyo:true,repeat:{int(dur / (0.9 + 0.15 * k))},ease:"sine.inOut"}},0);\n'
    js += f"""
  entra("#{p}-folhaW", {t_prop - 0.1:.2f}, 0.3); tl.fromTo("#{p}-folhaW",{{scale:0.4,rotation:-8,transformOrigin:"50% 50%"}},{{scale:1,rotation:0,duration:0.8,ease:"elastic.out(1,0.5)",immediateRender:false}},{t_prop - 0.1:.2f});
  olha("#{p}-gA-olho", {t_prop:.2f}, 3);
  rise("#{p}-t1 span", {t_prop:.2f});
  tl.to("#{p}-t1 span",{{yPercent:-125,duration:0.35,ease:"power2.in"}},{t_ben - 0.35:.2f});
  rise("#{p}-t2 span", {t_ben:.2f});
  tl.fromTo("#{p}-selo",{{opacity:0,scale:2.6,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.35,ease:"power4.in",immediateRender:false}},{t_ben:.2f});
  tl.fromTo("#{p}-folhaW",{{y:0}},{{y:10,duration:0.08,yoyo:true,repeat:1,immediateRender:false}},{t_ben + 0.35:.2f});
  tl.fromTo("#{p}-selo",{{rotation:0}},{{rotation:14,duration:0.12,yoyo:true,repeat:3,ease:"sine.inOut",immediateRender:false}},{t_est - 0.4:.2f});
  tl.to("#{p}-folhaM",{{y:-500,x:200,rotation:20,opacity:0,duration:0.5,ease:"power2.in"}},{w_lev - 0.3:.2f});
  tl.to("#{p}-t2 span",{{yPercent:-125,duration:0.35,ease:"power2.in"}},{w_porta + 0.1:.2f});
  {some_("A", w_lev)} {mostra("B", w_lev)} {mostra("C", w_lev)} {anda("B", w_lev, w_mesa, OX - PX0)} {anda("C", w_lev, w_mesa, OX - PX0)} {some_("B", w_mesa)}
  tl.fromTo("#{p}-veu",{{opacity:0}},{{opacity:0.85,duration:0.25,yoyo:true,repeat:1,ease:"sine.inOut"}},{w_porta - 0.25:.2f});
  tl.to("#{p}-porta-folha",{{scaleX:0.12,transformOrigin:"0% 50%",duration:0.5,ease:"power2.inOut"}},{w_lev + 0.2:.2f});
  tl.to("#{p}-oc",{{x:120,y:-75,duration:{w_porta - w_lev:.2f},ease:"power1.inOut"}},{w_lev:.2f});
  tl.to("#{p}-oc",{{opacity:0.22,duration:0.4}},{w_lev + 0.2:.2f});
  tl.fromTo("#{p}-flare",{{opacity:0}},{{opacity:0.45,duration:0.15,yoyo:true,repeat:1}},{w_porta - 0.12:.2f});
  {some_("C", w_volta)}
  tl.fromTo("#{p}-ot > g",{{opacity:0,scale:0.3,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.5,ease:"back.out(2.4)",stagger:0.13}},{w_porta + 0.25:.2f});
  tl.fromTo("#{p}-qt > g",{{scale:1}},{{scale:1.08,transformOrigin:"50% 50%",duration:0.2,yoyo:true,repeat:1,stagger:0.1,immediateRender:false}},{w_mesa - 0.2:.2f});
  olha("#{p}-gC-olho", {w_mesa:.2f}, 3);
  {mostra("D", w_volta)} {mostra("E", w_volta)} {anda("D", w_volta, w_cad, OX - PX0)} {anda("E", w_volta, w_cad, OX - PX0)} {some_("D", w_cad)}
  tl.fromTo("#{p}-veu",{{opacity:0}},{{opacity:0.85,duration:0.3,yoyo:true,repeat:1,ease:"sine.inOut",immediateRender:false}},{w_sai - 0.3:.2f});
  tl.to("#{p}-ot",{{y:-30,duration:{w_sai - w_volta:.2f},ease:"power1.inOut"}},{w_volta:.2f});
  tl.fromTo("#{p}-flare",{{opacity:0}},{{opacity:0.6,duration:0.15,yoyo:true,repeat:1,immediateRender:false}},{w_sai - 0.12:.2f});
  tl.to("#{p}-ot > g",{{scale:1.7,opacity:0,transformOrigin:"50% 50%",duration:0.45,ease:"power2.out",stagger:0.07}},{t_esq:.2f});
  rise("#{p}-t3 span", {t_esq:.2f});
  {some_("E", w_cad + 0.05)} {mostra("A", w_cad + 0.05)}
  tl.fromTo("#{p}-gA",{{y:0}},{{y:10,duration:0.12,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{w_cad + 0.05:.2f});
  tl.to("#{p}-oc",{{opacity:1,duration:0.45}},{w_cad - 0.1:.2f});
  tl.to("#{p}-oc",{{x:0,y:0,duration:{w_cad - w_sai:.2f},ease:"power1.inOut"}},{w_sai + 0.1:.2f});
  tl.fromTo("#{p}-qt > g",{{opacity:1}},{{opacity:0.55,duration:0.2,yoyo:true,repeat:1,stagger:0.08,immediateRender:false}},{t_dentro - 0.2:.2f});
  tl.to("#{p}-t3 span",{{yPercent:-125,duration:0.35,ease:"power2.in"}},{t_cob - 0.4:.2f});
  rise("#{p}-t4 span", {t_cob:.2f});
"""
    for k in range(5):
        js += (f'  entra("#{p}-f{k}", {t_cob + 0.1 + k * 0.22:.2f}, 0.1); tl.fromTo("#{p}-f{k}",{{y:-900,rotation:{(-1) ** k * 30}}},{{y:0,rotation:0,duration:0.6,ease:"bounce.out",immediateRender:false}},{t_cob + 0.1 + k * 0.22:.2f});\n')
    js += f"""
  tl.fromTo("#{p}-f0, #{p}-f1, #{p}-f2, #{p}-f3, #{p}-f4",{{x:0}},{{x:-4,duration:0.07,yoyo:true,repeat:5,ease:"none",immediateRender:false}},{t_trab:.2f});
  rise("#{p}-t5 span", {t_conf:.2f});
"""
    for k in range(5):
        js += (f'  tl.fromTo("#{p}-z{k}",{{opacity:0,scale:0.2,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.35,ease:"back.out(3)",immediateRender:false}},{t_conf + k * 0.12:.2f});\n'
               f'  tl.fromTo("#{p}-z{k}",{{rotation:0}},{{rotation:{(-1) ** k * 25},duration:0.1,yoyo:true,repeat:5,ease:"none",immediateRender:false}},{t_conf + 0.35 + k * 0.12:.2f});\n')
    js += f"""
  tl.to(["#{p}-t4 span","#{p}-t5 span"],{{yPercent:-125,duration:0.35,ease:"power2.in"}},{t_nao - 0.35:.2f});
  tl.to("#{p}-porta-folha",{{scaleX:1,transformOrigin:"0% 50%",duration:0.3,ease:"power3.in"}},{t_nao - 0.2:.2f});
  tl.to("#{p}-z0, #{p}-z4",{{x:-70,duration:0.15,yoyo:true,repeat:1,ease:"power2.in"}},{t_nao + 0.1:.2f});
  tl.to("#{p}-f0, #{p}-f1, #{p}-f2, #{p}-f3, #{p}-f4, #{p}-z0, #{p}-z1, #{p}-z2, #{p}-z3, #{p}-z4",{{opacity:0,duration:0.4}},{t_casa - 0.5:.2f});  // ficam do lado de lá: nada espia pela borda no fim
  rise("#{p}-t6 span", {t_nao:.2f}, 0.9);
  olha("#{p}-gA-olho", {t_casa:.2f}, 0);
""" + "".join(vida_gente(f"{p}-g{k}", dur) for k in "ABCDE")
    return comp(p, dur, svg, html, GENTE_JS + js, extra, seed=5)


# ---------------------------------------------------------------- abertura 4: quem tem o poder de entrar na sua mente?
def abertura_4():
    CE, SG = "abertura", 4
    p = "abertura_4"
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_perg, t_quem, t_entrar, t_mente, t_tranc, t_escr, t_ler, t_decid, t_real, t_enx = (
        T("pergunta"), T("quem"), T("entrar"), T("mente"), T("trancar"), T("escrever"), T("ler"), T("decidir"), T("realidade"), T("enxergar"))
    PX, PY, S = 380, 150, 3.0
    W = lambda lx, ly: (PX + lx * S, PY + ly * S)
    fx, fy = W(193, 90)                         # a única fechadura, no centro do cérebro (CEREBRO_LAT já escalado por .82)
    KS = 0.6                                    # escala da chave; a ponta (local 0,130) entra no buraco (fechadura local 0,-26 * .4)
    kx, ky = fx, fy - 10 - 130 * KS
    ex, ey = W(226, 54)                         # ponto escrito pela luz
    ox, oy = W(257, 129)                        # olho
    QX0, QX1, QY0, QY1 = 1380, 1640, 330, 560   # quadro da realidade
    rg = random.Random(4)
    morros = (f'<path d="M{QX0} {QY1} L{QX0 + 60} {QY0 + 140} L{QX0 + 120} {QY0 + 180} L{QX0 + 180} {QY0 + 110} L{QX1} {QY0 + 170} L{QX1} {QY1} Z" fill="#ff4fa3" opacity=".55"/>'
              f'<circle cx="{QX1 - 70}" cy="{QY0 + 70}" r="32" fill="#ffd98a"/>')
    extra = (f'<linearGradient id="{p}-ceu" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a1060"/><stop offset="1" stop-color="#ff4fa3" stop-opacity=".5"/></linearGradient>'
             f'<linearGradient id="{p}-scan" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#38e8a8" stop-opacity="0"/><stop offset=".7" stop-color="#38e8a8" stop-opacity=".3"/><stop offset=".9" stop-color="#bfffe8" stop-opacity=".8"/><stop offset="1" stop-color="#38e8a8" stop-opacity="0"/></linearGradient>'
             f'<clipPath id="{p}-cpc"><path transform="translate({PX} {PY}) scale({S}) translate(196 118) scale(.82) translate(-196 -118)" d="{CEREBRO_LAT}"/></clipPath>'
             f'<clipPath id="{p}-cpq"><rect x="{QX0}" y="{QY0}" width="{QX1 - QX0}" height="{QY1 - QY0}" rx="10"/></clipPath>')
    svg = f"""
<ellipse cx="{PX + 205 * S:.0f}" cy="{PY + 262 * S:.0f}" rx="300" ry="24" fill="#05031a" opacity=".5"/>
<g transform="translate({PX} {PY}) scale({S})"><g id="{p}-pes">{pessoa(p + "a", glow=p + "-glow")}</g></g>
<circle id="{p}-mem" cx="{fx:.0f}" cy="{fy:.0f}" r="70" fill="#ffd98a" opacity="0" filter="url(#{p}-blur6)"/>
{fechadura(p, "fch", 0.4, round(fx), round(fy), 0, luz=False)}
<g id="{p}-escr" opacity="0"><path d="M{ex + 60:.0f} -60 C {ex + 60:.0f} 120 {ex + 10:.0f} 200 {ex:.0f} {ey:.0f}" fill="none" stroke="#9aa6d0" stroke-width="10" stroke-linecap="round"/>
 <path id="{p}-raio" d="M{ex + 60:.0f} -60 C {ex + 60:.0f} 120 {ex + 10:.0f} 200 {ex:.0f} {ey:.0f}" fill="none" stroke="#7fe6ff" stroke-width="12" stroke-linecap="round" stroke-dasharray="70 600" stroke-dashoffset="70" filter="url(#{p}-glow)"/>
 <circle id="{p}-anel" cx="{ex:.0f}" cy="{ey:.0f}" r="30" fill="none" stroke="#7fe6ff" stroke-width="6"/></g>
<g clip-path="url(#{p}-cpc)"><rect id="{p}-varre" x="{PX + 100 * S:.0f}" y="{PY:.0f}" width="120" height="{180 * S:.0f}" fill="url(#{p}-scan)" opacity="0"/></g>
<g id="{p}-real" opacity="0"><polygon points="{ox + 10:.0f},{oy - 6:.0f} {QX0},{QY0 + 20} {QX0},{QY1 - 20} {ox + 10:.0f},{oy + 6:.0f}" fill="#ff4fa3" opacity=".22"/>
 <rect x="{QX0}" y="{QY0}" width="{QX1 - QX0}" height="{QY1 - QY0}" rx="10" fill="url(#{p}-ceu)"/>
 <g clip-path="url(#{p}-cpq)"><g id="{p}-paisagem">{morros}</g></g>
 <rect x="{QX0}" y="{QY0}" width="{QX1 - QX0}" height="{QY1 - QY0}" rx="10" fill="none" stroke="#ff4fa3" stroke-width="9" filter="url(#{p}-glow)"/></g>
{chave(p, "chave", KS, round(kx), round(ky), 0)}"""
    lab = lambda k, txt, cor, top: texto(f"{p}-l{k}", f'<i style="background:{cor};width:26px;height:26px"></i>{txt}', f"left:90px;top:{top}px;font-size:62px;color:{cor}", cls="pill2")
    html = (texto(f"{p}-t0", "UMA PERGUNTA", "left:0;right:0;text-align:center;top:60px;font-size:60px;color:#ffd98a;letter-spacing:.2em", cls="pill2") +
            texto(f"{p}-t1", "QUEM TEM O PODER", "left:0;right:0;text-align:center;top:22px;font-size:84px;color:#eef1f7") +
            texto(f"{p}-t2", "DE ENTRAR NA SUA MENTE?", "left:0;right:0;text-align:center;top:122px;font-size:84px;color:#eef1f7") +
            lab(0, "TRANCAR", "#ffd27a", 330) + lab(1, "ESCREVER", "#7fe6ff", 440) + lab(2, "LER", "#7ff0c8", 550) + lab(3, "DECIDIR", "#ff9bd0", 660))
    kdx, kdy = -520 / KS, -260 / KS
    js = f"""
  cam("#{p}-cam", [[0,1.0,960,560],[{t_entrar - 0.2:.2f},1.0,960,560,"none"],[{t_mente + 0.5:.2f},1.25,{fx + 60:.0f},480],
       [{t_escr:.2f},1.3,980,470,"sine.inOut"],[{t_real - 0.3:.2f},1.22,1010,480],[{dur:.2f},1.12,1000,500,"sine.inOut"]]);
  pop("#{p}-pes", 0.2, 0.6, 0.8);
  rise("#{p}-t0 span", {t_perg - 0.4:.2f});
  tl.to("#{p}-t0 span",{{yPercent:-125,duration:0.3,ease:"power2.in"}},{t_quem - 0.3:.2f});
  rise("#{p}-t1 span", {t_quem:.2f}); rise("#{p}-t2 span", {t_entrar - 0.3:.2f});
  tl.to(["#{p}-t1 span","#{p}-t2 span"],{{yPercent:-125,duration:0.4,ease:"power2.in"}},{t_tranc - 0.5:.2f});
  pop("#{p}-fch", {t_entrar - 0.3:.2f}, 0.4, 0.6);
  entra("#{p}-chave", {t_entrar - 0.1:.2f}, 0.3);
  tl.fromTo("#{p}-chave",{{x:{kdx:.0f},y:{kdy:.0f},rotation:-40,transformOrigin:"50% 82%"}},{{x:0,y:0,rotation:0,duration:0.9,ease:"power3.out",immediateRender:false}},{t_entrar - 0.1:.2f});
  tl.to("#{p}-chave",{{rotation:90,transformOrigin:"50% 82%",duration:0.35,ease:"back.out(2)"}},{t_mente:.2f});
  tl.to("#{p}-fch-buraco > *",{{attr:{{fill:"#ffb23e"}},duration:0.15}},{t_mente + 0.2:.2f});
  tl.to("#{p}-chave",{{rotation:0,transformOrigin:"50% 82%",duration:0.3,ease:"back.out(2)"}},{t_tranc + 0.25:.2f});
  tl.to("#{p}-fch-buraco > *",{{attr:{{fill:"#05031a"}},duration:0.15}},{t_tranc + 0.45:.2f});
  tl.to("#{p}-chave",{{opacity:0,y:-60,duration:0.5}},{t_tranc + 0.8:.2f});
  tl.fromTo("#{p}a-cer",{{opacity:0.95}},{{opacity:1,duration:0.2}},{t_mente:.2f});
  olha("#{p}a-olho", {t_entrar:.2f}, -3); olha("#{p}a-olho", {t_tranc:.2f}, 0);
  tl.fromTo("#{p}-mem",{{opacity:0}},{{opacity:0.75,duration:0.4}},{t_tranc - 0.2:.2f});
  tl.to("#{p}-mem",{{opacity:0.3,duration:0.5}},{t_tranc + 0.5:.2f});
  tl.fromTo("#{p}-fch",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.18,duration:0.18,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{t_tranc + 0.45:.2f});
  rise("#{p}-l0 span", {t_tranc:.2f});
  entra("#{p}-escr", {t_escr - 0.3:.2f}, 0.3);
  tl.fromTo("#{p}-raio",{{attr:{{"stroke-dashoffset":70}}}},{{attr:{{"stroke-dashoffset":-560}},duration:0.7,ease:"power1.in",repeat:2,repeatDelay:0.25}},{t_escr - 0.1:.2f});
  tl.fromTo("#{p}-anel",{{scale:0.4,opacity:1,transformOrigin:"50% 50%"}},{{scale:3,opacity:0,duration:0.8,repeat:2,repeatDelay:0.15,ease:"power2.out",immediateRender:false}},{t_escr + 0.55:.2f});
  rise("#{p}-l1 span", {t_escr:.2f});
  tl.fromTo("#{p}-varre",{{opacity:0,x:0}},{{opacity:1,x:{130 * S:.0f},duration:0.9,ease:"sine.inOut",yoyo:true,repeat:3}},{t_ler - 0.1:.2f});
  rise("#{p}-l2 span", {t_ler:.2f});
  entra("#{p}-real", {t_decid:.2f}, 0.4);
  tl.fromTo("#{p}-real",{{scale:0.6,transformOrigin:"0% 50%"}},{{scale:1,duration:0.7,ease:"elastic.out(1,0.6)",immediateRender:false}},{t_decid:.2f});
  rise("#{p}-l3 span", {t_decid:.2f});
  olha("#{p}a-olho", {t_decid:.2f}, 3);
  tl.fromTo("#{p}-paisagem",{{x:0}},{{x:-120,duration:0.5,ease:"power3.inOut",yoyo:true,repeat:1,immediateRender:false}},{t_real:.2f});
  tl.to("#{p}-paisagem path",{{attr:{{fill:"#38e8a8"}},duration:0.3}},{t_enx:.2f});
  tl.to("#{p}-real rect",{{attr:{{stroke:"#38e8a8"}},duration:0.3}},{t_enx:.2f});
""" + vida_pessoa(p + "a", dur)
    return comp(p, dur, svg, html, js, extra, seed=4)


# ---------------------------------------------------------------- abertura 6: pedaços reais
def _dentro(pt, poly):
    x, y = pt
    c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def abertura_6():
    CE, SG = "abertura", 6
    p = "abertura_6"
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_cien, t_fez, t_ped, t_mas, t_ped2, t_reais = T("ciencia"), T("fez"), T("pedacos"), T("mas"), T("pedacos", 1), T("reais")
    S, TX, TY = 5.2, 960 - 192 * 5.2, 430 - 98 * 5.2
    cacos = [[(116, 30), (190, 30), (178, 88), (116, 100)], [(190, 30), (268, 30), (268, 82), (226, 92), (178, 88)],
             [(116, 100), (178, 88), (168, 162), (116, 162)], [(178, 88), (226, 92), (216, 162), (168, 162)], [(226, 92), (268, 82), (268, 162), (216, 162)]]
    reais = (1, 2, 4)
    rg = random.Random(6)
    pts = []
    while len(pts) < 90:
        x, y = rg.uniform(124, 260), rg.uniform(40, 128)
        if ((x - 192) / 66) ** 2 + ((y - 84) / 44) ** 2 < 1 and all((x - a) ** 2 + (y - b) ** 2 > 40 for a, b in pts):
            pts.append((round(x, 1), round(y, 1)))
    extra = "".join(f'<clipPath id="{p}-cp{k}"><polygon points="{" ".join(f"{x},{y}" for x, y in c)}"/></clipPath>' for k, c in enumerate(cacos))
    partes = ""
    for k, c in enumerate(cacos):
        cx = sum(x for x, _ in c) / len(c); cy = sum(y for _, y in c) / len(c)
        dots = "".join(f'<circle class="n" cx="{x}" cy="{y}" r="1.5" fill="#ffb23e"/>' for x, y in pts if _dentro((x, y), c)) if k in reais else ""
        partes += (f'<g id="{p}-c{k}"><rect x="{cx - 50:.0f}" y="{cy - 50:.0f}" width="100" height="100" fill="none"/><g class="corpo" clip-path="url(#{p}-cp{k})">'
                   f'{cerebro_lateral(p + f"b{k}")}{dots}</g></g>')
    svg = f"""
<ellipse cx="960" cy="840" rx="380" ry="28" fill="#05031a" opacity=".45"/>
<g transform="translate({TX:.0f} {TY:.0f}) scale({S})"><g id="{p}-fant" opacity="0" fill="none" stroke="#b9adff" stroke-width=".9" stroke-dasharray="2.5 2.5"><path d="{CEREBRO_LAT}"/><ellipse cx="150" cy="138" rx="27" ry="17"/></g>
<g id="{p}-cer">{partes}</g></g>"""
    html = (texto(f"{p}-t1", "PEDAÇOS", "left:0;width:1000px;text-align:right;top:870px;font-size:124px;color:#eef1f7") +
            texto(f"{p}-t2", "REAIS", "left:1040px;top:870px;font-size:124px;color:#ffd98a"))
    js = f"""
  cam("#{p}-cam", [[0,0.95,960,520],[{t_ped:.2f},1.0,960,520,"sine.inOut"],[{t_mas + 0.3:.2f},1.03,960,520],[{dur:.2f},1.06,960,530,"sine.inOut"]]);
  pop("#{p}-cer", 0.1, 0.6, 0.9);
  tl.fromTo("#{p}-cer .n",{{opacity:0.15}},{{opacity:1,duration:0.18,repeat:9,yoyo:true,ease:"none",stagger:{{each:0.02,from:"random"}}}},{t_cien:.2f});
  entra("#{p}-fant", {t_fez:.2f}, 0.4);
"""
    for k, c in enumerate(cacos):
        cx = sum(x for x, _ in c) / len(c) - 192; cy = sum(y for _, y in c) / len(c) - 96
        n = math.hypot(cx, cy) or 1
        dx, dy = cx / n * 10, cy / n * 10
        js += f'  tl.to("#{p}-c{k}",{{x:{dx:.1f},y:{dy:.1f},duration:0.7,ease:"power3.out"}},{t_fez + 0.1:.2f});\n'
        if k not in reais:
            js += f'  tl.to("#{p}-c{k} .corpo",{{opacity:0.12,duration:0.5}},{t_ped:.2f});\n'
        else:
            js += (f'  tl.fromTo("#{p}-c{k}",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.08,duration:0.25,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{t_ped2 + 0.1 * k:.2f});\n'
                   f'  tl.to("#{p}-c{k}",{{x:{dx * 0.5:.1f},y:{dy * 0.5:.1f},duration:0.9,ease:"elastic.out(1,0.5)"}},{t_reais:.2f});\n')
    js += f"""  rise("#{p}-t1 span", {t_ped:.2f}); rise("#{p}-t2 span", {t_reais - 0.15:.2f});
  tl.fromTo("#{p}-cer .n",{{attr:{{r:1.5}}}},{{attr:{{r:2.4}},duration:0.3,yoyo:true,repeat:3,immediateRender:false}},{t_reais:.2f});
"""
    return comp(p, dur, svg, html, js, extra, seed=6)


# ---------------------------------------------------------------- abertura 7: os arquivos abertos um por um, cada um com a prévia do tema
def _prev_escrever(p):
    """Camundongo na caixa isométrica com a fibra de luz (cenas-v4 M3). Caixa local do cartão: 400 x 300 centrada em 0,0."""
    return (f'<g transform="translate(0 22) scale(.33) translate(-960 -490)">{b4.caixa(p)}'
            f'<circle id="{p}-e-halo" cx="1060" cy="470" r="120" fill="url(#{p}-hg)" opacity="0"/>'
            f'<g transform="translate(900 700) scale(1.15)"><g id="{p}-e-rato">{b4.rato(p)}</g></g>'
            f'<path d="M1010 -120 C 1010 160 1040 300 1052 430" fill="none" stroke="#9aa6d0" stroke-width="14" stroke-linecap="round"/>'
            f'<path id="{p}-e-luz" d="M1010 -120 C 1010 160 1040 300 1052 430" fill="none" stroke="#7fe6ff" stroke-width="16" stroke-linecap="round" stroke-dasharray="90 800" stroke-dashoffset="90" filter="url(#{p}-glow)"/>'
            f'<circle id="{p}-e-anel" cx="1052" cy="456" r="40" fill="none" stroke="#7fe6ff" stroke-width="8" opacity="0"/></g>')


def _prev_mapear(p):
    """Rede de neurônios (cenas-v3 A) atrás e a mosca-da-fruta (arte2) na frente."""
    rede_s, _, _ = b2.rede_rica(f"{p}-r", 11, n=80, pre=p)
    rede_s = rede_s.replace(' opacity="0">', '>', 2)  # lobo e arestas visíveis desde o início
    return (f'<g transform="translate(-30 -10) scale(.46)"><g id="{p}-m-rede">{rede_s}</g></g>'
            f'<g transform="translate(70 62) scale(.62)"><g id="{p}-m-mosca">{mosca_rica(p + "-mo", pre=p)}</g></g>')


def _prev_ler(p):
    """A cabeça com cérebro, eletrodo e o monitor que lê os sinais (cenas-v3 E)."""
    alvos = [(84, -40), (140, -54), (128, 6), (76, 2)]
    al = "".join(f'<circle id="{p}-l-al{k}" cx="{x}" cy="{y}" r="13" fill="none" stroke="{CIANO}" stroke-width="4" opacity=".7"/>' for k, (x, y) in enumerate(alvos))
    return (f'<g transform="translate(-338 -164) scale(1.22)">{pessoa(p + "L", glow=p + "-glow")}'
            f'<rect x="150" y="34" width="34" height="20" rx="6" fill="{AMBAR}" transform="rotate(-18 167 44)" filter="url(#{p}-glow)"/></g>'
            f'<path d="M-140 -112 C -40 -190 30 -150 44 -76" fill="none" stroke="#7a8cff" stroke-width="6" stroke-linecap="round"/>'
            f'<path id="{p}-l-sinal" d="M-140 -112 C -40 -190 30 -150 44 -76" fill="none" stroke="#ffd23e" stroke-width="9" stroke-linecap="round" stroke-dasharray="26 200" stroke-dashoffset="0" filter="url(#{p}-glow)"/>'
            f'<rect x="40" y="-86" width="140" height="112" rx="12" fill="#1a1850" stroke="{LILAS}" stroke-width="5"/><rect x="50" y="-76" width="120" height="92" rx="6" fill="#0b1c40"/>{al}'
            f'<rect x="100" y="26" width="20" height="26" fill="#1a1850" stroke="{LILAS}" stroke-width="3"/><rect x="74" y="50" width="72" height="10" rx="5" fill="#1a1850" stroke="{LILAS}" stroke-width="3"/>'
            f'<g transform="translate(60 -64)"><g id="{p}-l-cur"><path d="M0 0 L0 24 L7 18 L12 29 L18 26 L12 16 L22 16 Z" fill="#fff" stroke="#1a0f3a" stroke-width="2"/></g></g>')


def _prev_influenciar(p):
    """Celular com o feed rolando (cenas-v3 C) e curtidas subindo."""
    cores_p = ["#2b2a80", "#7b2a6c", "#25427a", "#6b5b2a", "#2a6a6a"]
    cards = "".join(
        f'<g transform="translate(0 {k * 190})"><rect x="-150" y="-330" width="300" height="170" rx="20" fill="{cores_p[k % 5]}"/>'
        f'<circle cx="-100" cy="-290" r="22" fill="#eef1ff" opacity=".85"/><rect x="-66" y="-304" width="150" height="12" rx="6" fill="#eef1ff" opacity=".7"/><rect x="-66" y="-282" width="100" height="10" rx="5" fill="#eef1ff" opacity=".4"/>'
        f'<rect x="-130" y="-244" width="260" height="56" rx="12" fill="#000" opacity=".22"/><circle cx="-84" cy="-218" r="14" fill="#ffd23e"/><path d="M-60 -196 L-20 -236 L20 -204 L50 -226 L112 -196 Z" fill="#fff" opacity=".35"/>'
        f'<path d="M110 -176 c-8 -10 -22 -2 -14 8 l14 12 l14 -12 c8 -10 -6 -18 -14 -8 Z" fill="#ff4f7d" transform="translate(-10 -16)"/></g>' for k in range(9))
    cor = lambda x, y, s: f'<g transform="translate({x} {y}) scale({s})"><path d="M0 14 C -26 -4 -20 -26 0 -14 C 20 -26 26 -4 0 14 Z" fill="#ff4fa3" filter="url(#{p}-glow)"/></g>'
    return (f'<g transform="translate(-10 6) rotate(-7) scale(.34)"><rect x="-200" y="-400" width="400" height="800" rx="54" fill="#15133a" stroke="{LILAS}" stroke-width="10"/>'
            f'<rect x="-172" y="-364" width="344" height="728" rx="26" fill="#0e0c26"/><clipPath id="{p}-i-cp"><rect x="-172" y="-364" width="344" height="728" rx="26"/></clipPath>'
            f'<g clip-path="url(#{p}-i-cp)"><g id="{p}-i-posts">{cards}</g></g></g>'
            f'<g id="{p}-i-cor">{cor(-120, 40, 1.6)}{cor(120, -20, 2.1)}{cor(130, 90, 1.3)}{cor(-130, -80, 1.2)}</g>')


def _prev_robo(p):
    """O robô mau: cabeça de robô grande, olhos vermelhos."""
    return (f'<g transform="scale(2.5)"><g id="{p}-r-cab"><rect x="-46" y="-36" width="92" height="76" rx="14" fill="#2a0a1a" stroke="#ff4f7d" stroke-width="5"/>'
            f'<circle id="{p}-r-o1" cx="-18" cy="0" r="10" fill="#ff4f7d" filter="url(#{p}-glow)"/><circle id="{p}-r-o2" cx="18" cy="0" r="10" fill="#ff4f7d" filter="url(#{p}-glow)"/>'
            f'<path d="M-20 24 L-10 20 L0 24 L10 20 L20 24" fill="none" stroke="#ff4f7d" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M0 -36 L0 -50" stroke="#ff4f7d" stroke-width="5"/><circle cx="0" cy="-54" r="6" fill="#ff4f7d"/>'
            f'<rect x="-58" y="-10" width="12" height="26" rx="4" fill="#5a1030"/><rect x="46" y="-10" width="12" height="26" rx="4" fill="#5a1030"/></g></g>')


def abertura_7():
    CE, SG = "abertura", 7
    p = "abertura_7"
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_abrir, t_um, t_sep, t_ja, t_medo, t_conc, t_desc, t_per, t_nao, t_robo = (
        T("abrir"), T("um"), T("separar"), T("ja"), T("medo"), T("conclusao"), T("desconfortavel"), T("perigo"), T("nao"), T("robo"))
    FX, RX, BY = [320, 760, 1200, 1640], 2200, 800
    abre = [t_abrir, t_abrir + 1.04, t_abrir + 2.08, t_abrir + 3.12]
    # (número, nome, cor do tema, cor da pasta, prévia)
    arq = [("1", "ESCREVER", "#7fe6ff", "#c9a46a", _prev_escrever(p)), ("2", "MAPEAR", "#38e8a8", "#b99ae0", _prev_mapear(p)),
           ("3", "LER", "#ffd27a", "#c9a46a", _prev_ler(p)), ("4", "INFLUENCIAR", "#ff7ac0", "#b99ae0", _prev_influenciar(p)),
           ("", "ROBÔ MAU", "#ff4f7d", "#8a3a4a", _prev_robo(p))]

    def pasta(k, x):
        num, nome, cor, cp, prev = arq[k]
        frente = (f'<text x="0" y="-132" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="44" letter-spacing="8" fill="#2a1a0a" opacity=".85">ARQUIVO</text>'
                  f'<circle cx="0" cy="-62" r="54" fill="{cor}" stroke="#2a1a0a" stroke-width="6"/>'
                  f'<text x="0" y="-36" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="84" fill="#1a0f2e">{num}</text>') if num else (
                  f'<g transform="translate(0 -92) scale(1.1)"><circle r="44" fill="none" stroke="#2a0a14" stroke-width="10"/><path d="M-31 -31 L31 31" stroke="#2a0a14" stroke-width="10"/></g>')
        return (f'<ellipse cx="{x}" cy="{BY + 8}" rx="190" ry="20" fill="#05031a" opacity=".55"/>'
                f'<ellipse id="{p}-g{k}" cx="{x}" cy="{BY + 4}" rx="230" ry="44" fill="{cor}" opacity="0" filter="url(#{p}-blur6)"/>'
                f'<g transform="translate({x} {BY})"><g id="{p}-p{k}" opacity="0"><rect x="-210" y="-480" width="420" height="560" fill="none"/>'
                f'<path d="M-150 -210 L-150 0 L150 0 L150 -210 L-24 -210 L-40 -240 L-140 -240 L-150 -226 Z" fill="{cp}" stroke="#05031a" stroke-width="3"/>'
                f'<g transform="translate(0 -320)"><g id="{p}-c{k}" opacity="0"><rect x="-200" y="-150" width="400" height="300" fill="none"/>'
                f'<circle r="230" fill="{cor}" opacity=".18" filter="url(#{p}-blur40)"/>'
                f'<rect x="-200" y="-150" width="400" height="300" rx="20" fill="#0d0b2c"/>'
                f'<g clip-path="url(#{p}-cc)">{prev}</g>'
                f'<rect x="-200" y="-150" width="400" height="300" rx="20" fill="none" stroke="{cor}" stroke-width="7" filter="url(#{p}-glow)"/></g></g>'
                f'<g id="{p}-fr{k}"><path d="M-158 -190 L158 -190 L150 0 L-150 0 Z" fill="{cp}" stroke="#05031a" stroke-width="3"/>'
                f'<path d="M-158 -190 L158 -190 L157 -180 L-157 -180 Z" fill="#fff" opacity=".3"/>{frente}</g>'
                f'<text x="0" y="78" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="50" letter-spacing="3" fill="{cor}" stroke="#05031a" stroke-width="8" paint-order="stroke">{nome}</text></g></g>')
    pastas = "".join(pasta(k, x) for k, x in enumerate(FX)) + pasta(4, RX)
    armarios = "".join(f'<g opacity=".5"><rect x="{x}" y="120" width="250" height="500" rx="8" fill="#1c1660" stroke="#4a46b0" stroke-width="4"/>'
                       + "".join(f'<rect x="{x + 20}" y="{140 + d * 158}" width="210" height="138" rx="6" fill="#241e78" stroke="#3a3690" stroke-width="3"/>'
                                 f'<rect x="{x + 95}" y="{196 + d * 158}" width="60" height="14" rx="7" fill="#8d7bff" opacity=".7"/>' for d in range(3)) + '</g>'
                       for x in range(-260, 2800, 300))
    extra = (b4.grad_caixa(p, "c") + mosca_defs(p) +
             f'<radialGradient id="{p}-hg"><stop offset="0" stop-color="#bff4ff" stop-opacity=".95"/><stop offset="1" stop-color="#7fe6ff" stop-opacity="0"/></radialGradient>'
             f'<radialGradient id="{p}-lobo" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="#3b5bff" stop-opacity=".28"/><stop offset="1" stop-color="#3b5bff" stop-opacity=".04"/></radialGradient>'
             f'<clipPath id="{p}-cc"><rect x="-200" y="-150" width="400" height="300" rx="20"/></clipPath>'
             f'<linearGradient id="{p}-mesa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a1d70"/><stop offset="1" stop-color="#0e0a30"/></linearGradient>'
             f'<radialGradient id="{p}-lm"><stop offset="0" stop-color="#ffe9a8" stop-opacity=".3"/><stop offset="1" stop-color="#ffe9a8" stop-opacity="0"/></radialGradient>')
    svg = f"""
<ellipse cx="1260" cy="560" rx="1400" ry="560" fill="url(#{p}-lm)"/>{armarios}
<polygon points="-700,1400 3200,1400 2700,640 -200,640" fill="url(#{p}-mesa)" stroke="#5a4ad0" stroke-width="4"/>
<path d="M-200 640 L2700 640" stroke="#8d7bff" stroke-width="6" filter="url(#{p}-glow)"/>
{pastas}"""
    html = (texto(f"{p}-t1", '<i style="background:#38e8a8;width:26px;height:26px"></i>JÁ ACONTECEU', "left:310px;width:800px;text-align:center;top:190px;font-size:62px;color:#7ff0c8", cls="pill2") +
            texto(f"{p}-t2", '<i style="background:#ff4f7d;width:26px;height:26px"></i>SÓ MEDO', "left:1470px;width:420px;text-align:center;top:190px;font-size:62px;color:#ff9bb0", cls="pill2") +
            texto(f"{p}-t3", "O PERIGO", "left:0;right:0;text-align:center;top:40px;font-size:124px;color:#eef1f7"))
    ks = [[0, 1.0, 980, 560], [abre[0] - 0.45, 1.0, 980, 560, "none"]]
    for k in range(4):
        ks.append([abre[k] + 0.15, 1.3, FX[k], 570])
        if k < 3:
            ks.append([abre[k + 1] - 0.45, 1.3, FX[k], 570, "none"])
    ks += [[abre[3] + 0.55, 1.3, FX[3], 570, "none"], [abre[3] + 1.2, 0.8, 1290, 540], [t_conc - 0.2, 0.8, 1290, 540, "none"],
           [t_desc + 0.1, 1.3, 2120, 570], [dur, 1.36, 2100, 560, "sine.inOut"]]
    ks_js = "[" + ",".join("[" + ",".join(f'"{v}"' if isinstance(v, str) else f"{v:.2f}" for v in kf) + "]" for kf in ks) + "]"
    js = f"""
  cam("#{p}-cam", {ks_js});
"""
    for k in range(4):
        t0 = 0.25 + k * 0.28
        js += (f'  entra("#{p}-p{k}", {t0:.2f}, 0.1); tl.fromTo("#{p}-p{k}",{{y:-760,rotation:{(-1) ** k * 7}}},{{y:0,rotation:0,duration:0.75,ease:"bounce.out",immediateRender:false}},{t0:.2f});\n')
    for k in range(5):
        ta = abre[k] if k < 4 else t_medo - 0.05
        js += (f'  tl.fromTo("#{p}-fr{k}",{{y:0}},{{y:14,duration:0.16,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{ta:.2f});\n'
               f'  tl.fromTo("#{p}-c{k}",{{opacity:0,y:200,scale:0.45,transformOrigin:"50% 100%"}},{{opacity:1,y:0,scale:1,duration:0.75,ease:"back.out(1.6)",immediateRender:false}},{ta:.2f});\n'
               f'  tl.fromTo("#{p}-g{k}",{{opacity:0}},{{opacity:0.6,duration:0.4}},{ta + 0.1:.2f});\n')
    js += f"""
  tl.fromTo("#{p}-e-luz",{{attr:{{"stroke-dashoffset":90}}}},{{attr:{{"stroke-dashoffset":-700}},duration:0.6,ease:"power1.in",repeat:3,repeatDelay:0.15}},{abre[0] + 0.25:.2f});
  tl.fromTo("#{p}-e-halo",{{opacity:0}},{{opacity:0.9,duration:0.3,yoyo:true,repeat:5,ease:"sine.inOut"}},{abre[0] + 0.75:.2f});
  tl.fromTo("#{p}-e-anel",{{opacity:0.9,scale:0.5,svgOrigin:"1052 456"}},{{opacity:0,scale:5,svgOrigin:"1052 456",duration:0.9,repeat:2,ease:"power2.out"}},{abre[0] + 0.75:.2f});
  tl.fromTo("#{p}-e-rato",{{y:0}},{{y:-6,duration:0.3,yoyo:true,repeat:5,ease:"sine.inOut"}},{abre[0] + 0.8:.2f});
  tl.fromTo("#{p}-m-rede .g2 circle",{{opacity:0.3}},{{opacity:1,duration:0.16,repeat:13,yoyo:true,ease:"none",stagger:{{each:0.03,from:"random"}}}},{abre[1] + 0.2:.2f});
  tl.fromTo("#{p}-mo-asas",{{scaleY:1,transformOrigin:"50% 100%"}},{{scaleY:0.55,transformOrigin:"50% 100%",duration:0.05,repeat:39,yoyo:true,ease:"none"}},{abre[1] + 0.2:.2f});
  tl.fromTo("#{p}-m-mosca",{{y:0}},{{y:-10,duration:0.5,repeat:5,yoyo:true,ease:"sine.inOut"}},{abre[1] + 0.2:.2f});
  tl.fromTo("#{p}-l-sinal",{{attr:{{"stroke-dashoffset":0}}}},{{attr:{{"stroke-dashoffset":-226}},duration:0.55,repeat:7,ease:"none"}},{abre[2] + 0.2:.2f});
  tl.to("#{p}-l-cur",{{keyframes:{{x:[0,24,24,80,80,68,68,16],y:[0,24,24,10,10,70,70,66],easeEach:"power2.inOut"}},duration:2.6,ease:"none"}},{abre[2] + 0.3:.2f});
  tl.fromTo("#{p}-l-al0, #{p}-l-al1, #{p}-l-al2, #{p}-l-al3",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.5,transformOrigin:"50% 50%",duration:0.25,yoyo:true,repeat:1,stagger:0.62,ease:"back.out(3)",immediateRender:false}},{abre[2] + 0.6:.2f});
  tl.fromTo("#{p}-i-posts",{{y:0}},{{y:-950,duration:3.4,ease:"power1.inOut"}},{abre[3] + 0.2:.2f});
  tl.fromTo("#{p}-i-cor > g",{{y:40,opacity:0}},{{y:-60,opacity:1,duration:0.9,stagger:0.25,ease:"power2.out",repeat:1,repeatDelay:0.2}},{abre[3] + 0.4:.2f});
  rise("#{p}-t1 span", {abre[3] + 0.9:.2f});
  entra("#{p}-p4", {t_medo - 0.45:.2f}, 0.1); tl.fromTo("#{p}-p4",{{y:-760,rotation:-8}},{{y:0,rotation:0,duration:0.6,ease:"bounce.out",immediateRender:false}},{t_medo - 0.45:.2f});
  rise("#{p}-t2 span", {t_medo:.2f});
  tl.fromTo("#{p}-p4",{{rotation:0,transformOrigin:"50% 100%"}},{{rotation:2.5,duration:0.08,yoyo:true,repeat:11,ease:"none",immediateRender:false}},{t_medo + 0.8:.2f});
  tl.fromTo("#{p}-r-o1, #{p}-r-o2",{{opacity:1}},{{opacity:0.25,duration:0.12,yoyo:true,repeat:9,ease:"steps(1)"}},{t_medo + 0.6:.2f});
  tl.to(["#{p}-t1 span","#{p}-t2 span"],{{yPercent:-125,duration:0.4,ease:"power2.in"}},{t_conc - 0.3:.2f});
  tl.fromTo("#{p}-r-cab",{{x:-3}},{{x:3,duration:0.05,yoyo:true,repeat:13,ease:"none",immediateRender:false}},{t_desc:.2f});
  rise("#{p}-t3 span", {t_per - 0.1:.2f});
  tl.to("#{p}-p4",{{y:620,rotation:16,opacity:0,duration:0.8,ease:"power3.in"}},{t_nao:.2f});
  tl.to("#{p}-g4",{{opacity:0,duration:0.5}},{t_nao:.2f});
"""
    return comp(p, dur, svg, html, js, extra, seed=7)


# ---------------------------------------------------------------- abertura 8: quem tem a chave? (corredor F)
def corredor(p):
    """Corredor de servidores da cena F (cenas-v3/build2.py::cena_F2), com ids prefixados. Ponto de fuga em (960, 500)."""
    extra = (f'<radialGradient id="{p}-fim" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#9af0ff" stop-opacity=".9"/><stop offset=".4" stop-color="#6a8cff" stop-opacity=".4"/><stop offset="1" stop-color="#6a8cff" stop-opacity="0"/></radialGradient>'
             f'<linearGradient id="{p}-teto" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0828"/><stop offset="1" stop-color="#1c1a58"/></linearGradient>'
             f'<linearGradient id="{p}-chao" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#06051a"/><stop offset="1" stop-color="#26246a"/></linearGradient>'
             f'<linearGradient id="{p}-rack" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1a1856"/><stop offset="1" stop-color="#2c2a88"/></linearGradient>')

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
        q_ = pontos(lado)
        us = [1 - 1 / (1 + 0.5 * i) for i in range(0, 26)]
        for i in range(len(us) - 1):
            a, bb = us[i], us[i + 1]
            q = [q_(a, 0.03), q_(bb, 0.03), q_(bb, 0.97), q_(a, 0.97)]
            pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in q)
            partes.append(f'<polygon points="{pts}" fill="url(#{p}-rack)" stroke="#5a5ad0" stroke-width="3"/><polygon points="{pts}" fill="#05031a" opacity="{0.18 + 0.7 * (a ** 0.8):.2f}"/>')
            x1, y1 = q_(a, 0.025); x2, y2 = q_(bb, 0.025)
            cabos.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#ff4fa3" stroke-width="{max(2, 8 * (1 - a)):.1f}" opacity=".7"/>')
            for r in range(11):
                for c in range(3):
                    uu = a + (bb - a) * (0.18 + 0.3 * c); vv = 0.10 + 0.08 * r
                    x, y = q_(uu, vv)
                    tam = max(2.2, 20 * (1 - uu) ** 1.3)
                    cor = CIANO if (i + r + c) % 4 else (AMBAR if (r + c) % 2 else MAGENTA)
                    leds.append(f'<rect class="led" x="{x - tam:.1f}" y="{y - tam * 0.5:.1f}" width="{tam * 2:.1f}" height="{tam:.1f}" rx="{tam * 0.2:.1f}" fill="{cor}"/>')
    tiras = "".join(f'<polygon points="{960 + dx * 0.06:.0f},430 {960 - dx * 0.06:.0f},430 {960 - dx:.0f},-40 {960 + dx:.0f},-40" fill="#cfe8ff" opacity=".16"/>' for dx in (170, 520, 880))
    guias = "".join(f'<line x1="{x}" y1="1120" x2="{960 + (x - 960) * 0.12:.0f}" y2="590" stroke="#6ad8ff" stroke-width="3" opacity=".22"/>' for x in (260, 560, 960, 1360, 1660))
    svg = (f'<polygon points="0,-40 1920,-40 1080,430 840,430" fill="url(#{p}-teto)"/><polygon points="0,1120 1920,1120 1080,590 840,590" fill="url(#{p}-chao)"/>'
           f'<ellipse id="{p}-nevoa" cx="960" cy="510" rx="520" ry="330" fill="url(#{p}-fim)"/>{tiras}<g>{"".join(partes)}</g><g>{guias}</g>'
           f'<rect x="905" y="470" width="110" height="120" rx="8" fill="#cfeaff" opacity=".85" filter="url(#{p}-glow)"/><g>{"".join(cabos)}</g><g id="{p}-leds">{"".join(leds)}</g>')
    return svg, extra


def abertura_8():
    CE, SG = "abertura", 8
    p = "abertura_8"
    ini, dur = seg(CE, SG)
    T = T_(CE, SG)
    t_guar, t_perg, t_quem, t_chave = T("guarde"), T("pergunta"), T("quem"), T("chave")
    cor, extra = corredor(p)
    svg = cor + f'<g id="{p}-porta">{fechadura(p, "fch", 0.5, 960, 530, 1, luz=False)}</g>'
    fixo = (f'<linearGradient id="{p}-faixa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05041a" stop-opacity="0"/><stop offset="1" stop-color="#05041a" stop-opacity=".85"/></linearGradient>'
            f'<radialGradient id="{p}-halo"><stop offset="0" stop-color="#ffb23e" stop-opacity=".55"/><stop offset="1" stop-color="#ffb23e" stop-opacity="0"/></radialGradient>'
            f'<circle id="{p}-hk" cx="1440" cy="400" r="330" fill="url(#{p}-halo)" opacity="0"/>'
            f'<rect x="0" y="760" width="1920" height="320" fill="url(#{p}-faixa)"/>{chave(p, "chave", 2.4, 1440, 260, 0)}')
    html = (texto(f"{p}-t1", "GUARDE UMA PERGUNTA", "left:0;right:0;text-align:center;top:60px;font-size:60px;color:#ffd98a;letter-spacing:.2em", cls="pill2") +
            texto(f"{p}-t2", "QUEM TEM A CHAVE?", "left:0;right:0;text-align:center;top:850px;font-size:140px;color:#eef1f7"))
    js = f"""
  cam("#{p}-cam", [[0,1.5,960,525],[{dur:.2f},2.9,960,530,"sine.inOut"]]);
  tl.fromTo("#{p}-nevoa",{{opacity:0.7}},{{opacity:1,duration:0.8,repeat:5,yoyo:true,ease:"sine.inOut"}},0);
  tl.fromTo("#{p}-leds .led",{{opacity:1}},{{opacity:0.15,duration:0.18,repeat:14,yoyo:true,ease:"steps(1)",stagger:{{each:0.0035,from:"random"}}}},0.1);
  rise("#{p}-t1 span", {t_guar:.2f});
  tl.to("#{p}-t1 span",{{yPercent:-125,duration:0.35,ease:"power2.in"}},{t_quem - 0.45:.2f});
  rise("#{p}-t2 span", {t_quem:.2f}, 0.9);
  tl.to("#{p}-fch-buraco > *",{{attr:{{fill:"#ffb23e"}},duration:0.2}},{t_chave:.2f});
  entra("#{p}-hk", {t_chave - 0.1:.2f}, 0.5);
  entra("#{p}-chave", {t_chave - 0.15:.2f}, 0.2);
  tl.fromTo("#{p}-chave",{{scale:0.3,rotation:-120,transformOrigin:"50% 30%"}},{{scale:1,rotation:0,duration:1.1,ease:"elastic.out(1,0.45)",immediateRender:false}},{t_chave - 0.15:.2f});
  tl.fromTo("#{p}-chave",{{rotation:0}},{{rotation:8,duration:0.9,yoyo:true,repeat:1,ease:"sine.inOut",immediateRender:false}},{t_chave + 1.0:.2f});
"""
    return comp(p, dur, svg, html, js, extra, fixo=fixo, fundo=("#1c1450", "#0d0a30", "#05041a"), seed=21)


CENAS_FN = [("abertura", 4, abertura_4), ("abertura", 6, abertura_6), ("abertura", 7, abertura_7), ("abertura", 8, abertura_8),
            ("contrato", 0, contrato_0), ("contrato", 2, contrato_2), ("contrato", 3, contrato_3), ("contrato", 4, contrato_4), ("contrato", 5, contrato_5)]
CENAS = [(f.__name__, f, seg(c, s)[1]) for c, s, f in CENAS_FN]
MAPA = {(c, s): f.__name__ for c, s, f in CENAS_FN}

if __name__ == "__main__":
    print(escreve_cenas(CENAS, AQUI))
