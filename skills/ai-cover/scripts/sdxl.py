"""Generates illustrations with SDXL on a local ComfyUI: starts the server, queues, downloads the images, shuts down.

  python3 sdxl.py --out DIR [--n 2] [--style kurz|jack|"free style"] [--wait] name="scene" [name2="scene 2" ...]
  e.g.: python3 sdxl.py --out renders/art --style jack eye="a lone man looking up at a giant glowing eye in the sky"

Output: DIR/<name>_<seed>.png (1344x768). Refuses to run with less than 6 GB of free RAM (--wait waits up to 1 h).
"""
import argparse, json, os, subprocess, sys, time, urllib.request

COMFY, PORT = os.path.expanduser("~/ComfyUI"), 8199
URL = f"http://127.0.0.1:{PORT}"
STYLES = {
    "kurz": "flat vector illustration in the style of Kurzgesagt, bold clean shapes, smooth gradients, vibrant saturated colors, "
            "deep purple and navy night background with stars, glowing neon magenta, cyan and warm orange accents, "
            "dramatic rim lighting, highly detailed, professional digital art, youtube thumbnail, simple readable composition",
    "jack": "in the style of Samurai Jack by Genndy Tartakovsky, flat colors with no outlines, bold geometric shapes, "
            "strong silhouette, minimal detail, cinematic widescreen composition, dramatic negative space, limited palette, "
            "deep purple night sky with magenta and cyan glow, 2d animation background art",
}
NEG = "text, letters, words, watermark, signature, logo, photo, photorealistic, 3d render, blurry, lowres, jpeg artifacts, deformed, extra fingers, ugly"

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--n", type=int, default=2, help="variations (seeds) per scene")
ap.add_argument("--style", default="kurz", help="kurz, jack or a free-form style text")
ap.add_argument("--wait", action="store_true", help="wait for RAM to free up instead of refusing")
ap.add_argument("scenes", nargs="+", help='name="scene description in English"')
a = ap.parse_args()
style = STYLES.get(a.style, a.style)
scenes = dict(c.split("=", 1) for c in a.scenes)


def free_gb():
    return int(next(l for l in open("/proc/meminfo") if l.startswith("MemAvailable")).split()[1]) / 1048576


# the model (6.9 GB) goes through RAM before VRAM; with little free RAM the peak takes the machine down
for _ in range(360 if a.wait else 1):
    if free_gb() >= 6:
        break
    if not a.wait:
        sys.exit(f"only {free_gb():.1f} GB of free RAM (needs 6). Close tabs/sessions or use --wait.")
    time.sleep(10)
else:
    sys.exit("RAM did not free up in 1 h")


def graph(pos, seed):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": pos, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 1344, "height": 768, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0],
                                                    "seed": seed, "steps": 32, "cfg": 6.5, "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "cover"}},
    }


def api(path, data=None):
    req = urllib.request.Request(URL + path, data=json.dumps(data).encode() if data else None, headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=30).read()


os.makedirs(a.out, exist_ok=True)
srv = subprocess.Popen(["systemd-run", "--user", "--scope", "-q", "-p", "MemoryMax=8G", "-p", "MemorySwapMax=0",
                        f"{COMFY}/.venv/bin/python", "main.py", "--listen", "127.0.0.1", "--port", str(PORT), "--disable-auto-launch"],
                       cwd=COMFY, stdout=open("/tmp/comfy-sdxl.log", "w"), stderr=subprocess.STDOUT)
try:
    for _ in range(120):
        try:
            api("/system_stats"); break
        except Exception:
            time.sleep(1)
    queue = [(name, 1000 + 97 * k, None) for name in scenes for k in range(a.n)]
    queue = [(name, s, json.loads(api("/prompt", {"prompt": graph(f"{scenes[name]}, {style}", s)}))["prompt_id"]) for name, s, _ in queue]
    subprocess.run(["taskline", "set", "sdxl", "0", str(len(queue)), "--label", "SDXL: illustrations", "--stalled-after", "300"])
    for name, seed, pid in queue:
        while True:
            h = json.loads(api(f"/history/{pid}"))
            if pid in h and h[pid].get("outputs"):
                break
            if pid in h and h[pid].get("status", {}).get("status_str") == "error":
                subprocess.run(["taskline", "fail", "sdxl", name])
                sys.exit(f"error in {name}: {h[pid]['status']}")
            time.sleep(1)
        img = h[pid]["outputs"]["7"]["images"][0]
        data = urllib.request.urlopen(f"{URL}/view?filename={img['filename']}&subfolder={img['subfolder']}&type=output").read()
        open(f"{a.out}/{name}_{seed}.png", "wb").write(data)
        subprocess.run(["taskline", "add", "sdxl"])
        print(f"{a.out}/{name}_{seed}.png", flush=True)
    subprocess.run(["taskline", "done", "sdxl"])
finally:
    srv.terminate()
    srv.wait(timeout=30)
