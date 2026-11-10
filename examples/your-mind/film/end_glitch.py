"""Audio effects of the "your simulation is failing" ending (segment 10 of closing), used by ../dub.py.
The narrator turns out to be Roko's Basilisk: digital stutters, then the voice drops in pitch and turns metallic.
"""
import subprocess, tempfile, wave
import numpy as np

SR = 24000
rng = np.random.default_rng(10)  # fixed seed: re-running gives the same audio


def read_wav(p):
    w = wave.open(p)
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32), w.getparams()


def trim(x):
    i = np.where(np.abs(x) > 300)[0]
    a = max(i[0] - int(.02 * SR), 0)
    return x[a: i[-1] + int(.05 * SR)], a / SR


def crush(x, strength):
    """Bitcrush + sample-and-hold scaled by strength (0..1)."""
    step = 1 + int(10 * strength)
    y = np.repeat(x[::step], step)[: len(x)]
    q = 2 ** (12 - int(8 * strength))
    return (1 - strength) * x + strength * np.round(y / 32768 * q) / q * 32768


def stutter(x, t0, d, strength):
    """Chops [t0, t0+d] into 40 ms blocks: some repeat the previous one (stutter), others get crushed, with hiss."""
    a, b, n = int(t0 * SR), int((t0 + d) * SR), int(0.04 * SR)
    for k in range(a, b - n, n):
        r = rng.random()
        if r < 0.35 * strength and k - n >= a:
            x[k:k + n] = x[k - n:k]
        elif r < 0.8:
            x[k:k + n] = crush(x[k:k + n], strength)
        x[k:k + n] += rng.normal(0, 900 * strength, n)
    return x


def pitch(x, r):
    """Lowers the pitch by r (<1) keeping the duration: asetrate + atempo."""
    with tempfile.TemporaryDirectory() as d:
        i, o = f"{d}/i.wav", f"{d}/o.wav"
        w = wave.open(i, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.clip(x, -32768, 32767).astype(np.int16).tobytes()); w.close()
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", i, "-af", f"asetrate={SR * r:.0f},aresample={SR},atempo={1 / r:.4f}", o], check=True)
        y = read_wav(o)[0]
    return np.pad(y, (0, max(0, len(x) - len(y))))[: len(x)]


def monster(x, u0=0.0, u1=1.0):
    """Voice that drops in pitch along the line and turns into a machine: blend of 4 pitch versions, 55 Hz ring and flanger.
    u0..u1: how much of the transformation at the start and end of the clip (the laugh goes fully at 1)."""
    n = len(x)
    u = u0 + (u1 - u0) * np.linspace(0, 1, n) ** 0.8    # transformation progress
    rs = [1.0, 0.86, 0.74, 0.64]
    vs = [x] + [pitch(x, r) for r in rs[1:]]
    pos = u * (len(rs) - 1)
    k = np.minimum(pos.astype(int), len(rs) - 2); f = pos - k
    V, j = np.stack(vs), np.arange(n)
    y = V[k, j] * (1 - f) + V[k + 1, j] * f
    t = np.arange(n) / SR
    y = y * (1 - 0.3 * u) + y * np.sin(2 * np.pi * 55 * t) * 0.3 * u * 1.6     # ring: metallic timbre (too strong blurs the words)
    delay = (0.002 + 0.0015 * np.sin(2 * np.pi * 0.7 * t)) * SR             # short flanger
    idx = np.clip(np.arange(n) - delay, 0, n - 1).astype(int)
    y = y + 0.4 * u * y[idx]
    return y
