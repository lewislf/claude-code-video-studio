"""Clip for the "your simulation is failing" ending: the last frame of the door holds on screen and breaks down to black.

  python3 glitch.py <duration> <bursts> <collapse start> <black> out.mp4 [in.mp4]
  e.g.: python3 glitch.py 10 "1.2:0.25:0.4,3.0:0.4:0.7" 6.0 8.4 assets/clips/closing_10.mp4

bursts: t0:duration:strength (0..1). From the collapse start to black the strength rises to 1; after black two
flashes of noise remain. All deterministic (the "random" is a sine hash over band and frame), so re-rendering gives the same.
"""
import os, subprocess, sys, tempfile

FF = "ffmpeg"
BASE = ("assets/clips/closing_9.mp4", 3.6)  # lit frame of the door, before the ending fade


def strength(bursts, t_col, t_black):
    g = "+".join(f"{a}*between(T,{t0},{t0 + d})" for t0, d, a in bursts) or "0"
    col = f"clip((T-{t_col})/{t_black - t_col},0,1)"
    # on/off every 1/20 s, so the glitch "chokes" instead of staying continuous
    blink = "gt(abs(sin(floor(T*20)*91.7)),0.3)"
    return f"min(1,({g})*{blink}+{col}*(0.55+0.45*{blink}))"


def build_filter(dur, bursts, t_col, t_black, video=False):
    G = strength(bursts, t_col, t_black)
    h = lambda a, b: f"abs(sin(({a})*12.9898+({b})*78.233))"  # hash 0..1
    band = "floor(Y/(14+40*" + h("floor(T*15)", "3") + "))"
    shift = f"({G})*gt({h(band, 'floor(T*15)')},0.62)*({h(band + '+7', 'floor(T*15)')}-0.5)*420"
    rgb = f"({G})*26"
    xs = f"(X+{shift})"
    ex = lambda c, d: f"{c}(clip({xs}{d},0,W-1),Y)"
    zoom = f"zoompan=z='1+0.05*on/{dur * 30}':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.45':d=1:s=1920x1080:fps=30"  # slow push-in
    if video:  # the scene already has its own camera
        zoom = "scale=1920:1080"
    return (f"[0:v]{zoom},format=gbrp,"
            f"geq=r='{ex('r', '+' + rgb)}':g='{ex('g', '')}':b='{ex('b', '-' + rgb)}',"
            # noise and scanlines, scaled by strength
            f"noise=alls=28:allf=t,format=yuv420p,"
            f"eq=brightness='0.25*gt({G.replace('T', 't')},0.85)*gt(abs(sin(floor(t*24)*33.1)),0.6)':eval=frame,"
            f"drawbox=0:0:iw:ih:black:t=fill:enable='gte(t,{t_black})*not(between(t,{t_black + 0.35},{t_black + 0.42}))*not(between(t,{t_black + 0.9},{t_black + 0.94}))'[v]")


if __name__ == "__main__":
    dur, raw, t_col, t_black, out = float(sys.argv[1]), sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
    bursts = [tuple(map(float, r.split(":"))) for r in raw.split(",") if r]
    if len(sys.argv) > 6:  # over a video (the basilisk scene)
        inputs = ["-i", sys.argv[6], "-t", str(dur)]
    else:                  # over the still frame of the door
        png = os.path.join(tempfile.mkdtemp(), "glitch_base.png")
        subprocess.run([FF, "-loglevel", "error", "-y", "-ss", str(BASE[1]), "-i", BASE[0], "-frames:v", "1", "-update", "1", png], check=True)
        inputs = ["-loop", "1", "-framerate", "30", "-i", png, "-t", str(dur)]
    subprocess.run(["systemd-run", "--user", "--scope", "-q", "-p", "MemoryMax=3G", "-p", "MemorySwapMax=0",
                    FF, "-loglevel", "error", "-y", *inputs,
                    "-filter_complex", build_filter(dur, bursts, t_col, t_black, len(sys.argv) > 6), "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
                    "-g", "30", "-r", "30", "-pix_fmt", "yuv420p", out], check=True)
    print("ready:", out)
