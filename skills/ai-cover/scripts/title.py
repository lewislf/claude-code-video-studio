"""Puts a cover title (white Montserrat 900, cyan/magenta edge, dark veil at the top) over an image and saves 1280x720.

  python3 title.py image.png "WHO HOLDS THE KEY?" out.png [--fs 100] [--no-veil]
"""
import argparse, base64, os, subprocess, tempfile

ap = argparse.ArgumentParser()
ap.add_argument("image"); ap.add_argument("text"); ap.add_argument("out")
ap.add_argument("--fs", type=int, default=100, help="font size (lower it if the text does not fit on one line)")
ap.add_argument("--no-veil", action="store_true")
a = ap.parse_args()

b = base64.b64encode(open(a.image, "rb").read()).decode()
veil = "" if a.no_veil else '<div class="v"></div>'
html = (f'<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@900&display=swap" rel="stylesheet">'
        f'<style>html,body{{margin:0;width:1280px;height:720px;overflow:hidden;background:#000;position:relative}}'
        f'.f{{position:absolute;inset:0;background:url(data:image/png;base64,{b}) center/cover}}'
        f'.v{{position:absolute;inset:0;background:linear-gradient(180deg,#05030ff0 0%,#05030fb0 22%,#05030f00 42%)}}'
        f'.t{{position:absolute;left:0;right:0;top:18px;text-align:center;font:900 {a.fs}px/1 Montserrat,sans-serif;letter-spacing:-1px;color:#fff;white-space:nowrap;'
        f'text-shadow:-3px 0 #3be0ff,3px 0 #ff4fa3,0 6px 18px #000a,0 0 2px #000}}</style>'
        f'<div class="f"></div>{veil}<div class="t">{a.text}</div>')
with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
    f.write(html)
subprocess.run(["google-chrome", "--headless=new", "--hide-scrollbars", "--window-size=1280,720", "--virtual-time-budget=4000",
                f"--screenshot={os.path.abspath(a.out)}", f"file://{f.name}"], check=True, capture_output=True)
os.remove(f.name)
print(a.out)
