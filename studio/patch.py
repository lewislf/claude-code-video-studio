"""Replaces only the segments that changed in a finished render, without reassembling the whole video.

  python3 patch.py v1 v2 contract_3 closing_1     # ids of the redone clips (assets/clips/<id>.mp4)

Re-encodes only the segments that use those clips; the rest of the video and the audio come from the source render.
Works because assemble.py closes each segment on a keyframe (every clip starts with an IDR).
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as M

src_name, out, clips = sys.argv[1], sys.argv[2], set(sys.argv[3:])
fr = lambda t: round(t * M.FPS)
targets = [k for k, (c, i, _, _) in enumerate(M.rows) if M.clip_for(c, i) in clips]
if not targets:
    sys.exit("no segment uses those clips")
src = os.path.abspath(f"renders/{src_name}.mp4")
lst, cursor = [], 0
for k in targets:
    c, i, a, b = M.rows[k]
    new, _ = M.segment_clip(c, i, a, b, k)
    if fr(a) > cursor:
        lst += [f"file '{src}'", f"inpoint {cursor / M.FPS:.4f}", f"outpoint {fr(a) / M.FPS:.4f}"]
    lst.append(f"file '{new}'")
    cursor = fr(b)
if cursor < fr(M.TOTAL):  # without this the final inpoint snaps back to the last keyframe and glues ~2 s of the old render at the end
    lst += [f"file '{src}'", f"inpoint {cursor / M.FPS:.4f}"]
open(f"{M.T}/list.txt", "w").write("\n".join(lst) + "\n")
video = f"{M.T}/video.mp4"
subprocess.run([M.FF, "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{M.T}/list.txt", "-map", "0:v", "-c", "copy", video], check=True)
final = f"renders/{out}.mp4"
subprocess.run([M.FF, "-loglevel", "error", "-y", "-i", video, "-i", src, "-map", "0:v", "-map", "1:a", "-c", "copy",
                "-t", f"{M.TOTAL:.2f}", "-movflags", "+faststart", final], check=True)
print(f"done: {final}, segments replaced: {targets}")
