"""Generates figure_svg.json from the approved canvas drawing (figure_sketch/sketch.html).

Runs drawPerson in headless Chrome with a recording context that mimics ctx/Path2D and emits SVG:
path with a transform matrix, clipPath for clip, evenodd cutout for the cut shadow. MARK() becomes a group with an id.
Each shadow/light of a piece comes out as a base hex + a neutral layer with opacity, so swapping the hex recolors the piece.

    python3 figure_make.py        # rewrites figure_svg.json
"""
import json, os, re, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "figure_sketch", "sketch.html")
OUTPUT = os.path.join(HERE, "figure_svg.json")
K = 0.815          # scale: top of the standing head ~ -540
SKETCH_SCALE = 1.1   # scale at which the sketch was approved (shadows/rim in screen px)

RECORDER = r"""
const F=v=>{const r=Math.round(v*100)/100;return Object.is(r,-0)?'0':String(r);};
class Rec2D{
  constructor(d){this.d=(typeof d==='string')?d:(d&&d.d)||'';}
  moveTo(x,y){this.d+=`M${F(x)} ${F(y)}`;} lineTo(x,y){this.d+=`L${F(x)} ${F(y)}`;}
  bezierCurveTo(a,b,c,d,e,f){this.d+=`C${F(a)} ${F(b)} ${F(c)} ${F(d)} ${F(e)} ${F(f)}`;}
  quadraticCurveTo(a,b,c,d){this.d+=`Q${F(a)} ${F(b)} ${F(c)} ${F(d)}`;}
  closePath(){this.d+='Z';}
  rect(x,y,w,h){this.d+=`M${F(x)} ${F(y)}h${F(w)}v${F(h)}h${F(-w)}Z`;}
  roundRect(x,y,w,h,r){ if(w<0){x+=w;w=-w;} if(h<0){y+=h;h=-h;} r=Math.min(r,w/2,h/2);
    this.d+=`M${F(x+r)} ${F(y)}H${F(x+w-r)}A${F(r)} ${F(r)} 0 0 1 ${F(x+w)} ${F(y+r)}V${F(y+h-r)}A${F(r)} ${F(r)} 0 0 1 ${F(x+w-r)} ${F(y+h)}H${F(x+r)}A${F(r)} ${F(r)} 0 0 1 ${F(x)} ${F(y+h-r)}V${F(y+r)}A${F(r)} ${F(r)} 0 0 1 ${F(x+r)} ${F(y)}Z`; }
  ellipse(x,y,rx,ry){ this.d+=`M${F(x-rx)} ${F(y)}A${F(rx)} ${F(ry)} 0 1 0 ${F(x+rx)} ${F(y)}A${F(rx)} ${F(ry)} 0 1 0 ${F(x-rx)} ${F(y)}Z`; }
  arc(x,y,r){ this.ellipse(x,y,r,r); }
  addPath(p){this.d+=' '+p.d;}
}
window.Path2D=Rec2D;
const hex2=c=>{c=c.trim().toLowerCase(); let m=/^#([0-9a-f]{6})$/.exec(c); if(m) return {h:c,a:1};
  m=/^rgba?\(([^)]+)\)$/.exec(c); const v=m[1].split(',').map(Number);
  return {h:'#'+v.slice(0,3).map(x=>x.toString(16).padStart(2,'0')).join(''), a:v.length>3?v[3]:1};};
const rgb=h=>[1,3,5].map(i=>parseInt(h.substr(i,2),16));
let COLOR_MAP={};
function buildMap(pals){
  const neutralDark='#140a2e', neutralLight='#ffffff';
  for(const p of pals){ const B=rgb(p.b);
    for(const k of['s','l','d']){ const h=p[k]; if(!h||COLOR_MAP[h]||h===p.b||h==='#ffffff') continue;
      const S=rgb(h), lum=c=>c[0]*.3+c[1]*.59+c[2]*.11, O=lum(S)>lum(B)?neutralLight:neutralDark, Oc=rgb(O);
      const num=[0,1,2].reduce((t,i)=>t+(S[i]-B[i])*(Oc[i]-B[i]),0), den=[0,1,2].reduce((t,i)=>t+(Oc[i]-B[i])**2,0);
      COLOR_MAP[h]={b:p.b,o:O,a:Math.max(0,Math.min(1,num/den))};
    } }
}
class RecCtx{
  constructor(){this.m=new DOMMatrix();this.st=[];this.out=[];this.defs=[];this.open=0;this.nk=0;this.cur=new Rec2D();
    this.fillStyle='#000';this.strokeStyle='#000';this.lineWidth=1;this.lineCap='butt';this.lineJoin='miter';this.pend=null;}
  save(){this.st.push({m:this.m,o:this.open,fs:this.fillStyle,ss:this.strokeStyle,lw:this.lineWidth,lc:this.lineCap,lj:this.lineJoin});this.open=0;}
  restore(){for(;this.open>0;this.open--)this.out.push('</g>');const s=this.st.pop();this.m=s.m;this.open=s.o;
    this.fillStyle=s.fs;this.strokeStyle=s.ss;this.lineWidth=s.lw;this.lineCap=s.lc;this.lineJoin=s.lj;}
  translate(x,y){this.m=this.m.translate(x,y);} scale(a,b){this.m=this.m.scale(a,b);} rotate(r){this.m=this.m.rotate(r*180/Math.PI);}
  getTransform(){return DOMMatrix.fromMatrix(this.m);} setTransform(a,b,c,d,e,f){this.m=(a instanceof DOMMatrix)?DOMMatrix.fromMatrix(a):new DOMMatrix([a,b,c,d,e,f]);}
  beginPath(){this.cur=new Rec2D();} ellipse(...a){this.cur.ellipse(...a);} arc(...a){this.cur.arc(...a);}
  moveTo(...a){this.cur.moveTo(...a);} lineTo(...a){this.cur.lineTo(...a);} roundRect(...a){this.cur.roundRect(...a);}
  mat(){const m=this.m;return `matrix(${[m.a,m.b,m.c,m.d,m.e,m.f].map(v=>(Math.round(v*10000)/10000)).join(' ')})`;}
  fill(p,rule){if(typeof p==='string'){rule=p;p=null;} this.emit((p||this.cur).d,this.fillStyle,rule,false);}
  stroke(p){this.emit((p||this.cur).d,this.strokeStyle,null,true);}
  clip(p,rule){if(typeof p==='string'){rule=p;p=null;} const id='@P@-k'+(this.nk++);
    this.defs.push(`<clipPath id="${id}" clipPathUnits="userSpaceOnUse"><path d="${(p||this.cur).d}" transform="${this.mat()}"${rule==='evenodd'?' clip-rule="evenodd"':''}/></clipPath>`);
    this.out.push(`<g clip-path="url(#${id})">`); this.open++;}
  emit(d,color,rule,isStroke){
    const c=hex2(color), T=` transform="${this.mat()}"`, R=rule==='evenodd'?' fill-rule="evenodd"':'';
    const at=(h,op)=>isStroke?`fill="none" stroke="${h}"${op<1?` stroke-opacity="${F(op)}"`:''} stroke-width="${F(this.lineWidth)}" stroke-linecap="${this.lineCap}" stroke-linejoin="${this.lineJoin}"`
                       :`fill="${h}"${op<1?` fill-opacity="${F(op)}"`:''}${R}`;
    if(this.pend){ this.out.push(`<g${T}><path id="@P@-${this.pend}" d="${d}" ${at(c.h,c.a)}/></g>`); this.pend=null; return; }
    const mp=COLOR_MAP[c.h];
    if(!mp){ this.out.push(`<path d="${d}"${T} ${at(c.h,c.a)}/>`); return; }
    const g=c.a<1; if(g) this.out.push(`<g opacity="${F(c.a)}">`);
    this.out.push(`<path d="${d}"${T} ${at(mp.b,1)}/><path d="${d}"${T} ${at(mp.o,mp.a)}/>`);
    if(g) this.out.push('</g>');
  }
}
"""

MAIN = r"""
buildMap([SKIN,FACE,HAIR,HOOD,JEANS,SHIRT,PANTS,OXF,SNEAK,TIE,WOOD,MUG]);
ZK=__K__/__E__;
const RES={};
for(const v of['home','work']) for(const pose of['sitting','standing']) for(const turn of[0,30]){
  const rc=new RecCtx(); RIM=v==='home'?'#ff4fa3':'#5ee6ff';
  MARK=(name,open)=>{
    if(name==='torso-path'){rc.pend='torso';return;}
    if(name==='chair'){rc.out.push(open?'<!--chair-->':'<!--/chair-->');return;}
    if(name==='headW'){rc.out.push(open?'<g id="@P@-headW" transform="translate(0 0)">':'</g>');return;}
    rc.out.push(open?`<g id="@P@-${name}">`:'</g>');
  };
  ANC={};
  drawPerson(rc,v,0,0,__K__,{pose:pose==='standing'?'standing':'sitting',turn});
  if(rc.open||rc.st.length) throw new Error('unbalanced stack '+v+pose);
  const a=Object.values(ANC)[0], k=__K__;
  const S=p=>p&&[Math.round(p[0]*k*10)/10,Math.round(p[1]*k*10)/10];
  RES[`${v}|${pose}|${turn}`]={svg:rc.out.join(''),defs:rc.defs.join(''),
    anc:{hand_r:S(a.hand_right),hand_l:S(a.hand_left),lap:S(a.lap),head_center:S(a.head_center),head_top:S(a.head_top),shoulder_arm:S(a.shoulder_arm)}};
}
document.getElementById('output').textContent=JSON.stringify(RES);
"""


def main():
    src = open(SOURCE, encoding="utf-8").read()
    body = src.split("<script>", 1)[1].split("// ---------------- BACKGROUND", 1)[0]
    page = ('<!doctype html><meta charset="utf-8"><pre id="output"></pre><script>' + RECORDER + body
           + MAIN.replace("__K__", str(K)).replace("__E__", str(SKETCH_SCALE)) + "</script>")
    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "export.html")
        open(f, "w", encoding="utf-8").write(page)
        dom = subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", f"--user-data-dir={tmp}/profile",
                              "--dump-dom", "file://" + f], capture_output=True, text=True, timeout=120).stdout
    m = re.search(r'<pre id="output">(.*?)</pre>', dom, re.S)
    txt = m.group(1).replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&amp;", "&") if m else ""
    if not txt:
        raise SystemExit("exporter returned nothing (JS error in headless?)")
    data = json.loads(txt)
    json.dump(data, open(OUTPUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    for k, v in data.items():
        print(k, len(v["svg"]) // 1024, "KB", v["anc"])


if __name__ == "__main__":
    main()
