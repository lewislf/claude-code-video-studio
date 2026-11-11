# Visual direction for the video "Your mind under terms of use"

Adapted from the prompt in the post https://x.com/finnardley/status/2114305886420086817 (a Kurzgesagt-style explainer made in code only),
plus what has already been approved and rejected in this project. It applies to every new scene. Scenes A, B, D, E, F, C and M1 to M8
(folders `scenes-v3` and `scenes-v4`) are the reference for finish.

## What the post does and the figure copies

1. Every sentence of the narration triggers a camera move or a transformation. Nothing stands still.
2. The event happens on the word that names it (timing per word, not per segment).
3. Shape of each scene: the event on its word, pull back to show scale, dive in to the personal ("you"), pull back again,
   the consequence with a live counter, an escalation, a funny or human moment with the character, the return to the start.
4. A recurring character who looks at what matters (the eye follows the focus), blinks, breathes and does squash and stretch.
5. Big text rises from inside a mask (ease-out-quint), never fades in whole.
6. Camera: zoom interpolated in log space, easeInOutCubic. Every "pop" is a damped spring.
7. Finish: vignette, film grain, nebula with parallax, twinkling stars.
8. Show a contact sheet of each scene before rendering. Always.
9. Forbidden: AI images or video, third-party characters, text that is not in the narration, static infographic strips.

## What changes for our video

Language and voice: Brazilian Portuguese, a cloned voice already recorded (the English version is a dub placed on the same timings). Each segment lasts as long as its speech (`segments.json`,
`slots.json`). Never stretch the speech to fit the picture; tighten the animation.

Event timing: the times came from the narration (word-level timestamps from whisper small, in seconds of the SCENE, minus the
segment's `start` for local time). Today they are fixed numbers in the code of each scene.

Approved look (keep):
- Background: dark purple radial gradient (#3a1d7a, #1a1050, #0b0a24), blurred bokeh, rising dust. Vignette. Neon cyan #3be0ff,
  lilac #8d7bff, amber #ffb23e, magenta #ff4fa3, mint #38e8a8, alarm red #ff4f7d.
- "The person" is the human head in profile drawn in a neon cyan line (`art2.head_line`) with the pink brain in side view inside
  the skull (`art2.brain_side`), and a blue eye that blinks. It is the recurring character in the "you" moments.
- The mouse is the white mouse in an isometric glass box (`mouse-art/art/mouse.svg.part`, `scenes-v4/build4.py`).
- The fruit fly, the neuron network, the server corridor and the isometric "you are here" cube are finished scenes
  (`scenes-v3/build2.py`, `build3.py`). Reuse the pieces, don't redraw them.
- Type: titles in big EB Garamond 700; labels in IBM Plex Mono, uppercase, letter-spaced, large (>= 40 px).

Rejected by the user (never repeat):
- An empty scene, a small loose icon, or just text over a flat background.
- A small label inside a 28 px box. Text only when it is a word from the narration, and at reading size.
- The Prismo head, a brain squashed on top of the eye, a pixel avatar, a fly that looks like a bee.
- Elements cut by the frame edge by accident, objects floating with no connection, labels overlapping the art.
- Third-party clips with text on screen. (The Severance and Matrix trailers stay as they are, they are real fiction.)
- On-screen text that differs from the narration.

Segments that are NOT redone: the Severance, Matrix and fiction-trio segments (real trailers). The real article pages (`doc`) keep
the source image, but gain camera, an animated highlight of the quoted passage, and a big label in the new style.

## Structure of a new scene (technical standard)

- One HyperFrames composition per segment (or per group of contiguous segments), generated in Python by `engine.composition()`,
  which wraps `build2.composition2` (background, bokeh, dust, vignette, fade in and out).
- Exact duration of the segment. A 0.4 s fade from black at the start and at the end (already in `composition2`).
- Camera in a `-cam` group. Events placed with `at=<time>`, the time of the word in the narration.
- Every scene ends on a frame that works as a still (the speech may end before the animation).
- No audio inside the composition (voice and music go into the final video).

## Before delivering

1. `python3 build_<group>.py` and `npx hyperframes@0.8.185 check` with no errors.
2. `npx hyperframes@0.8.185 snapshot --at ...` at 6 or more moments per scene, look at the contact sheet.
3. Critic (`visual-validator`) at full screen. It only passes with PASS or minor items.
4. Only then render the clip.

## Round 2: a real person and scenes with more story (user request)

The user watched the full video and said the image of the profile head with the pink brain "repeats in several places where there
should be something better". He wants a real human character in life scenes: sitting in a chair, at home, with pictures on the wall
showing moments of a life (family, birthday, buying a car, graduation), colored fragments of memory (sensations, feelings); and
when this person walks through the door at work, the memories and photos are COMPLETELY different, the same person with different
clothes and hair. Also: when the text talks about "opening" a folder, show the name, the number and a preview (symbol or image) of
the topic.

New library: `scenes/figure.py`
- `figure(p, "home"|"work", "sitting"|"standing", glow="<scene_id>-glow")` is the SAME person in two versions (hoodie and messy hair
  at home; shirt, tie, badge, glasses and short hair at work). Local box ~ x -150..190, y -520..0 (feet at y=0).
  `figure_idle(p, dur)` adds breathing, sway and blinks.
- `picture(p, kind, x, y, s)` with home kinds: family, birthday, car, graduation, beach, dog; and work kinds: award, meeting,
  spreadsheet, coffee. `orb(p, symbol, x, y, color)` with heart, cake, car, sun, music note, clock, lightning, cup (memories in
  colored bubbles).
- For other contexts, draw variations with the same pieces (clothing colors, chair, table, setting), without creating another style.

When to use what:
- The narration talks about a person's EXPERIENCE (forgetting, working, suffering, scrolling the feed, being fooled): use `figure`,
  in settings with a story (living room, office, street, bedroom, phone in hand), with expression and movement (walking to the
  door, sitting down, looking at the phone).
- The narration talks about the BRAIN or the MIND as an organ (neurons, implant, MRI, brain being read): the profile head with the
  pink brain (`engine.person`) can stay, but never the same composition repeated: vary angle, scale and surroundings.
- Each scene needs an image different from the others in the same group. If two scenes in a row use the same figure in the same
  place, it fails.
