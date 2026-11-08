"""Scenes of group g1. Build: python3 $ST/scenes.py build g1 (from inside the project folder; ST = <repo>/studio)."""
from engine import *


def sky(p, scene, i, keyword, title):
    start, dur = seg(scene, i)
    t = word(scene, i, keyword)
    sun = f'<g transform="translate(1460 300)"><g id="{p}-sun" opacity="0"><circle r="120" fill="#ffd98a" filter="url(#{p}-glow)"/></g></g>'
    hill = '<path d="M-200 900 Q 500 760 1100 880 T 2200 860 L 2200 1300 L -200 1300 Z" fill="#14123a"/>'
    html = text(f"{p}-t", title, "left:0;right:0;text-align:center;top:120px")
    js = f'camZ("#{p}-cam", 0, {dur:.2f}, 1.0, 1.15, 960, 600, "power1.inOut"); pop("#{p}-sun", 0.2); rise("#{p}-t span", {t:.2f});'
    return composition(p, dur, sun + hill, html, js, bg=("#3b7bd8", "#1f3f9a", "#0b0a24"))


SCENES = [
    ("sky_0", lambda: sky("sky_0", "sky", 0, "blue", "BLUE"), seg("sky", 0)[1]),
    ("sky_1", lambda: sky("sky_1", "sky", 1, "white", "WHITE"), seg("sky", 1)[1]),
    ("rayleigh_0", lambda: sky("rayleigh_0", "rayleigh", 0, "Rayleigh", "RAYLEIGH"), seg("rayleigh", 0)[1]),
    ("rayleigh_1", lambda: sky("rayleigh_1", "rayleigh", 1, "blue", "BLUE REACHES YOU"), seg("rayleigh", 1)[1]),
]
MAP = {("sky", 0): "sky_0", ("sky", 1): "sky_1", ("rayleigh", 0): "rayleigh_0", ("rayleigh", 1): "rayleigh_1"}
