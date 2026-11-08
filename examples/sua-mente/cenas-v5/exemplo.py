"""Cena-piloto no padrão v5: contrato, segmento 3 ("Quem assinou foi a pessoa de fora...").

  python3 exemplo.py     # escreve compositions/ e index.html desta pasta
"""
from motor import *

CE, SG = "contrato", 3


def contrato_3():
    p = "K3"
    ini, dur = seg(CE, SG)
    T = lambda w, n=0, d=None: palavra(CE, SG, w, n, d)
    t_ass, t_fora, t_trab, t_sofre, t_ob, t_dentro, t_nunca, t_nada, t_nasceu, t_emp = (
        T("assinou"), T("pessoa"), T("trabalha"), T("sofre"), T("obedece"), T("dentro", 1), T("nunca"), T("nada"), T("nasceu"), T("empregada"))
    extra = f"""<linearGradient id="{p}-papel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#e9dcc2"/></linearGradient>
<linearGradient id="{p}-parede" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1c1a58"/><stop offset="1" stop-color="#2a2878"/></linearGradient>
<linearGradient id="{p}-luzp" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffe9a8" stop-opacity=".65"/><stop offset="1" stop-color="#ffe9a8" stop-opacity="0"/></linearGradient>"""
    linhas = "".join(f'<rect x="-210" y="{-250 + k * 34}" width="{360 if k % 3 else 270}" height="10" rx="5" fill="#8a7f68" opacity=".45"/>' for k in range(7))
    svg = f"""
<g id="{p}-mundo">
 <rect x="-600" y="-200" width="3300" height="1400" fill="url(#{p}-parede)"/>
 <g id="{p}-porta" opacity="0"><rect x="80" y="190" width="340" height="680" rx="14" fill="#14123a" stroke="#8d7bff" stroke-width="8" filter="url(#{p}-glow)"/>
  <polygon points="80,190 420,190 420,870 80,870" fill="url(#{p}-luzp)"/><text x="250" y="150" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="40" fill="#38e8a8" filter="url(#{p}-glow)">SAÍDA</text></g>
 <ellipse cx="740" cy="905" rx="300" ry="26" fill="#05031a" opacity=".5"/>
 <g transform="translate(428 360)"><g id="{p}-fora" opacity="0"><g transform="scale(1.75)">{pessoa(p + "f", glow=p + "-glow")}</g></g></g>
 <g id="{p}-mesa" opacity="0">
  <rect x="2200" y="640" width="860" height="40" rx="12" fill="#3a2a8c"/><rect x="2260" y="680" width="40" height="230" fill="#2a1d70"/><rect x="2960" y="680" width="40" height="230" fill="#2a1d70"/>
  <rect x="2330" y="500" width="260" height="140" rx="14" fill="#0e0c26" stroke="#8d7bff" stroke-width="6"/>
  <g id="{p}-pilha"></g>
  <ellipse cx="2630" cy="905" rx="420" ry="26" fill="#05031a" opacity=".5"/>
 </g>
 <g transform="translate(2271 250)"><g id="{p}-dentro" opacity="0"><g transform="scale(1.75)" opacity=".8">{pessoa(p + "d", glow=p + "-glow")}</g></g></g>
 <g id="{p}-gotas" opacity="0" fill="#7fe6ff"><path d="M2840 330 q-12 26 0 36 q12 -10 0 -36z"/><path d="M2800 400 q-10 22 0 30 q10 -8 0 -30z"/></g>
 <g transform="translate(1330 470)"><g id="{p}-folha" opacity="0">
  <g filter="url(#{p}-sombra)"><rect x="-260" y="-330" width="520" height="660" rx="16" fill="url(#{p}-papel)"/></g>{linhas}
  <text x="-210" y="150" font-family="EB Garamond" font-weight="700" font-size="34" fill="#5a4a30">CONTRATO</text>
  <line x1="-210" y1="260" x2="-20" y2="260" stroke="#3a3a3a" stroke-width="4"/><line x1="40" y1="260" x2="230" y2="260" stroke="#3a3a3a" stroke-width="4"/>
  <path id="{p}-assin" d="M-205 252 C -180 200 -160 270 -140 230 S -100 210 -80 250 S -50 230 -28 246" fill="none" stroke="#1d2f9a" stroke-width="7" stroke-linecap="round" stroke-dasharray="320" stroke-dashoffset="320"/>
  <g id="{p}-vazio" opacity="0"><circle cx="135" cy="238" r="30" fill="#ff4f7d"/><text x="135" y="251" text-anchor="middle" font-family="IBM Plex Mono" font-weight="700" font-size="40" fill="#fff">?</text></g>
 </g></g>
 <g id="{p}-cracha" opacity="0" transform="translate(0 0)"><g transform="translate(2630 520)"><rect x="-120" y="0" width="240" height="120" rx="14" fill="#fffaf0" stroke="#ffb23e" stroke-width="6"/><rect x="-100" y="22" width="60" height="60" rx="8" fill="#8d7bff"/><rect x="-24" y="30" width="110" height="12" rx="6" fill="#8a7f68"/><rect x="-24" y="56" width="80" height="10" rx="5" fill="#bfb49a"/><path d="M0 -300 L-60 0 M0 -300 L60 0" stroke="#ffb23e" stroke-width="6"/></g></g>
</g>"""
    pilha = "".join(f'<rect x="{2720 + (k % 3) * 8}" y="{628 - k * 14}" width="150" height="12" rx="3" fill="#fffaf0" transform="rotate({(k % 3 - 1) * 2} 2795 {628 - k * 14})"/>' for k in range(9))
    svg = svg.replace(f'<g id="{p}-pilha"></g>', f'<g id="{p}-pilha" opacity="0">{pilha}</g>')
    html = (texto(f"{p}-t1", "DE FORA", "left:540px;top:900px;font-size:76px;color:#bff4ff;letter-spacing:.12em") +
            texto(f"{p}-t2", "DE DENTRO", "left:2400px;top:900px;font-size:76px;color:#c9b8ff;letter-spacing:.12em") +
            texto(f"{p}-t3", "NASCEU EMPREGADA", "left:0;right:0;text-align:center;top:70px;font-size:96px;color:#ffd98a"))
    js = f"""
  camZ("#{p}-cam", 0, 3.0, 1.0, 1.0, 960, 540);
  entra("#{p}-porta", 0.1, 0.6); pop("#{p}-fora", 0.2, 0.5, 0.8);
  entra("#{p}-folha", {t_ass - 0.15:.2f}, 0.35); tl.fromTo("#{p}-folha",{{scale:0.5,transformOrigin:"50% 50%"}},{{scale:1,duration:0.7,ease:"elastic.out(1,0.5)",immediateRender:false}},{t_ass - 0.15:.2f});
  tl.fromTo("#{p}-assin",{{attr:{{"stroke-dashoffset":320}}}},{{attr:{{"stroke-dashoffset":0}},duration:0.9,ease:"power2.inOut"}},{t_ass + 0.25:.2f});
  rise("#{p}-t1 span", {t_fora:.2f});
  ["#{p}-mundo","#{p}-t1","#{p}-t2"].forEach(function(s){{tl.fromTo(s,{{x:0}},{{x:-1380,duration:1.3,ease:"power3.inOut",immediateRender:false}},{t_trab - 0.25:.2f});}});
  entra("#{p}-mesa", {t_trab - 0.4:.2f}, 0.3);
  pop("#{p}-dentro", {t_trab - 0.1:.2f}, 0.5, 0.8);
  entra("#{p}-pilha", {t_trab:.2f}, 0.1);
  tl.fromTo("#{p}-pilha rect",{{y:-160,opacity:0}},{{y:0,opacity:1,duration:0.35,ease:"bounce.out",stagger:0.34}},{t_trab:.2f});
  entra("#{p}-gotas", {t_sofre:.2f}, 0.2); tl.fromTo("#{p}-gotas",{{y:0}},{{y:34,duration:0.9,repeat:3,ease:"power1.in"}},{t_sofre:.2f}); some("#{p}-gotas", {t_ob:.2f}, 0.3);
  tl.fromTo("#{p}-dentro",{{y:0}},{{y:10,duration:0.28,repeat:5,yoyo:true,ease:"sine.inOut"}},{t_ob:.2f});
  rise("#{p}-t2 span", {t_dentro:.2f});
  entra("#{p}-vazio", {t_nunca:.2f}, 0.2);
  tl.fromTo("#{p}-dentro",{{rotation:0,transformOrigin:"50% 50%"}},{{rotation:3,duration:0.12,repeat:7,yoyo:true,ease:"none"}},{t_nunca + 0.3:.2f});
  rise("#{p}-t3 span", {t_nasceu:.2f}, 0.9);
  entra("#{p}-cracha", {t_nasceu:.2f}, 0.1);
  tl.fromTo("#{p}-cracha",{{y:-380}},{{y:0,duration:0.9,ease:"bounce.out",immediateRender:false}},{t_nasceu:.2f});
  camZ("#{p}-cam", {t_nunca - 0.2:.2f}, {max(0.5, dur - t_nunca + 0.2):.2f}, 1.0, 1.12, 960, 620, "power1.inOut");
""" + vida_pessoa(p + "f", dur) + vida_pessoa(p + "d", dur, (3.0, 7.3, 10.2))
    return composicao(p, dur, svg, html, js, extra)


CENAS = [("K3", contrato_3, seg(CE, SG)[1])]

if __name__ == "__main__":
    print(escreve_cenas(CENAS, AQUI))
