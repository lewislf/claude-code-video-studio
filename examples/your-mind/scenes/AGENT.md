# Instructions for whoever builds the v5 scenes

You build animated scenes (HyperFrames, SVG + GSAP) for the video "Your mind under terms of use" (UFES, Computers and Society).
The user rejected many of the video's old scenes (loose icons, text over a flat background, emptiness). You redo the ones
assigned to you, in the approved visual style, with the direction adapted from the post https://x.com/finnardley/status/2114305886420086817
(every sentence of the narration triggers camera or a transformation, events land on the words, nothing stands still).

Read, in this order, before writing code:
1. `scenes/DIRECTION.md` (what to do and what the user rejected)
2. `scenes/GOTCHAS.md` (transform/ID/memory traps, every one of them already cost rework)
3. `scenes/engine.py` (`seg`, `camZ`, `pop`, `rise`, `count_up`, `text`, `label`, `person`, `composition`, `write_scenes`)
4. `scenes/example_scene.py` (a complete pilot scene in the standard; copy its structure) and the approved scenes as the reference
   for finish: `scenes-v3/build2.py` (A fly, B monitor, F corridor), `scenes-v3/build3.py` (D, E head with brain, C feed and minds),
   `scenes-v4/build4.py` (mouse, isometric box, bolt). Reusable functions in `scenes-v3/art2.py`.
5. `scenes/segments.json` (text and duration of each segment). Event times came from the narration and are now fixed numbers
   in the code. For `doc` (a real article page) reuse
   the source image in `film/assets/`: it stays, but gains camera, an animated highlight of the quoted passage and a big title.

Hard rules:
- Each scene lasts exactly as long as its segment (`seg(scene, i)` returns `(start, dur)`). Event times are the times of the words
  in the narration, written as fixed numbers.
- Only text that is in the narration (or a number/proper name it mentions), >= 40 px, rising through a mask. No period at the end
  of on-screen text. Never the em dash "—" in any text you write (code, comment, on-screen text).
- A scene with a big main object, depth, and a character ("the person", the mouse, the fly) when it makes sense. No empty scene.
- Reuse the existing art; don't invent another character style. Forbidden: Prismo, third-party characters, AI images.
- Prefix every id with the scene id. No GSAP `x/y/scale` on an element with a `transform` attribute (outer + inner group).
- Write only inside your folder `scenes/<group>/` (create it). Copy `hyperframes.json` and `package.json` from `scenes-v4/`.
  Don't touch `film/`, `scenes-v3/`, `scenes-v4/`, or other groups. Don't commit/push.
- Machine with 14 GB and several sessions: do NOT run `npx hyperframes render`. To look at frames use ONLY
  `scenes/snap.sh <your-folder> <output> <t1,t2,...>` (global lock, one at a time, memory ceiling). `npx hyperframes check --json`
  can run directly (it's light).
- Cycle per scene: write -> `check` -> snapshot at >= 6 moments (including every word event) -> look at the contact sheet
  (use the Read tool on the images) -> fix -> ask the `visual-validator` agent for a critique if you have the Agent tool
  (pass PNG paths, the scene context and the user's rejections; demand PASS) -> only then move on. Without the Agent tool,
  be the harsh critic yourself: look for edge cuts, loose elements, text overlapping art, emptiness, unreadable text.

Delivery (file `scenes/<group>/build_<group>.py`):
- Defines `SCENES = [(scene_id, function, duration), ...]` and, in `__main__`, calls `write_scenes(SCENES, HERE)` (from `engine.py`).
- Scene ids in the form `<SCENE>_<seg>` (e.g. `contract_3`), unique. A `SEG_MAP = {(scene, seg): id}` linking video segment to id.
- Short final report: which scenes, what each one shows, what came out weak, what the critic pointed out that wasn't solved.
