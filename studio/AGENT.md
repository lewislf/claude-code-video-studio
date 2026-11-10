# Briefing for scene builders

You build animated scenes (HyperFrames, SVG + GSAP) for a narrated video. Each script segment becomes a scene with the exact
duration of the speech, and each sentence triggers a camera move or a transformation on the right word. Nothing stays still.

Whoever called you passes: the project (folder with `script.py`), the group (`scenes/<group>/`) and which segments are yours. If the
project has a `DIRECTION.md` (style, what the user rejected), it overrides this file.

Read before writing code:
1. `studio/GOTCHAS.md` (transform, id and memory traps; every one of them already cost rework)
2. `studio/engine.py` (`seg`, `word`, `camZ`, `pop`, `rise`, `countUp`, `text`, `label`, `composition`, `write_scenes`)
3. `template/scenes/g1/build_g1.py` (the minimal build) and, for finish, the scenes in `examples/your-mind/scenes/g*/`
4. the project's `script.py` (text and visual of each segment) and `words/<scene>.json` (time per word)

Hard rules:
- Each scene lasts exactly the segment (`seg(scene, i)[1]`). Events via `word(scene, i, "prefix")`.
- Only text that is in the narration (or numbers and proper names said in it), >= 40 px, rising through a mask. No period on screen.
  Never an em-dash (U+2014) in any text (code, comment, screen).
- Big main object, depth, a character when it makes sense (`studio/people.py`). No empty scene, no lone icon.
  No AI-generated image inside the video.
- Prefix every id with the scene id. No GSAP `x/y/scale` on an element that has a `transform` attribute (outer + inner group).
- Write only in `scenes/<group>/`. Do not touch other groups or the script. Do not commit.
- Do not render. To look at frames: `studio/snap.sh scenes/<group> <out> <t1,t2,...>` (global lock, memory cap) and
  `studio/check.sh scenes/<group>`. Build the HTML with `python3 studio/scenes.py build <group>` from inside the project.
- Loop per scene: write, `check`, snapshot at >= 6 instants (including every event word), look at the contact sheet,
  fix. If you have the Agent tool, ask `visual-validator` for a critique and require PASS. Otherwise be the harsh critic
  yourself: cut-off edges, loose elements, text over art, empty space, unreadable text.

Delivery (`scenes/<group>/build_<group>.py`):
- `SCENES = [(id, function, duration), ...]` with ids in the form `<scene>_<seg>`, unique.
- `MAP = {(scene, seg): id}` linking each segment to its clip.
- Short report: which scenes, what each one shows, what is weak, what the critic flagged and was not resolved.
