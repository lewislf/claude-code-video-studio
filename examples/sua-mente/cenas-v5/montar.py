"""Renderiza os clipes de um grupo e corta uma cena por arquivo em ../video-v2/assets/cenas3/<id>.mp4.

  python3 montar.py g2_trancada [g4_ler ...]

Trava global (flock) com os snapshots dos agentes e teto de memória. Atualiza ../video-v2/assets/cenas3/mapa_v5.json
({cena: {seg: id}}), que o build.py do vídeo lê com --v3.
"""
import importlib.util, json, os, subprocess, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(AQUI, "../video-v2/assets/cenas3")
FF = "/home/linuxbrew/.linuxbrew/bin/ffmpeg"
MAPA_JSON = os.path.join(DEST, "mapa_v5.json")


def carrega(grupo):
    pasta = os.path.join(AQUI, grupo)
    arq = [f for f in os.listdir(pasta) if f.startswith("build_") and f.endswith(".py")][0]
    sys.path.insert(0, pasta); sys.path.insert(0, AQUI)
    spec = importlib.util.spec_from_file_location(arq[:-3], os.path.join(pasta, arq))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return pasta, m


for grupo in sys.argv[1:]:
    pasta, m = carrega(grupo)
    so = [x for x in os.environ.get('SO', '').split(',') if x]
    cenas = [c for c in m.CENAS if not so or c[0] in so]
    ini, total = m.escreve_cenas(cenas, pasta)
    saida = os.path.join(pasta, "clipes.mp4")
    cmd = (f'flock /tmp/claude-1002/snap.lock systemd-run --user --scope -q -p MemoryMax={os.environ.get("MEMCAP", "3500M")} -p MemorySwapMax=0 '
           f'bash -c \'cd "{pasta}" && npx hyperframes render --fps 30 --quality draft --workers {os.environ.get("WORKERS", "2")} {os.environ.get("RFLAGS", "")} -o clipes.mp4\'')
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if not os.path.exists(saida):
        print("FALHOU render", grupo, r.stdout[-400:], r.stderr[-400:]); continue
    t = json.load(open(os.path.join(pasta, "tempos.json")))
    for k, i0 in t["inicio"].items():
        d = t["dur"][k]
        subprocess.run([FF, "-loglevel", "error", "-y", "-ss", str(i0), "-t", str(d), "-i", saida, "-an", "-vf", "fps=30", "-c:v", "libx264",
                        "-preset", "slow", "-crf", "16", "-g", "15", "-pix_fmt", "yuv420p", "-movflags", "+faststart", os.path.join(DEST, f"{k}.mp4")], check=True)
    mapa = json.load(open(MAPA_JSON)) if os.path.exists(MAPA_JSON) else {}
    for (cena, seg), idc in m.MAPA.items():
        if so and idc not in so: continue
        mapa.setdefault(cena, {})[str(seg)] = idc
    json.dump(mapa, open(MAPA_JSON, "w"), indent=1)
    os.remove(saida)
    print("ok", grupo, len(t["inicio"]), "cenas")
