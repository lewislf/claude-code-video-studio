# Traps already paid for (HyperFrames + GSAP + SVG)

Read before writing a scene. Each item cost at least one round of fixes.

## Transforms (the source of almost every visual bug)

1. Never animate `x`, `y`, `scale` or `rotation` (GSAP) on an SVG element that also has `transform="translate(...) scale(...)"` as
   an attribute. GSAP reads the attribute, overwrites it and the object ends up at (0,0). Always: outer group with the static
   `transform`, inner group with the `id` that GSAP animates. E.g.: `<g transform="translate(870 716) scale(.9)"><g id="X-mouse">...</g></g>`.
   In this setup, the inner group's `x` and `y` are in units already scaled by the parent (divide by the scale if you want pixels).
2. The transform origin of an SVG group is the top-left corner of its box, not the center. To scale from the center:
   `transformOrigin:"50% 50%"` and an invisible symmetric `<rect>` inside the group so the box is centered.
3. `svgOrigin:"x y"` uses global SVG coordinates and only works well on top-level groups. Inside a group with translate/scale
   it is off. For the camera use `camZ(...)` (already does it right) on a top-level `#{id}-cam` group.
4. Never use a static `scale` attribute and a GSAP `scale` on the same element. Nest.
5. Repeated `fromTo` on the same target needs `immediateRender:false` on the later tweens, otherwise the first state shows up early
   (pinkish ghosts, elements visible before their time).
6. Loops (`repeat`) must be finite and end before another tween on the same target.
7. An initial `opacity` set only in CSS does not count; set `opacity="0"` as an attribute and animate to 1.

## IDs and filters

8. All compositions go into the same document. Prefix EVERY id with the scene id (`X-...`), including gradients, filters and
   clipPaths. `composition` (engine.py) already defines `{id}-glow`, `{id}-blur6`, `{id}-blur40`, `{id}-shadow`, `{id}-vig`, `{id}-bg`.
   A `url(#filter)` that does not exist can make the element disappear.
9. The sub-composition root does not accept class styling. `composition` already wraps it in `.scene`.

## Art

10. Ready-made character: `people.py` (geometric person, variants "home"/"work", poses "sitting"/"standing").
    Reuse art already approved in the project instead of redrawing.
11. No small lone icons. Every scene needs a big main object (>= 35% of the height) and depth
    (layers, shadow, glow, bokeh). An empty scene is rejected.
12. Text: only words from the narration (numbers and proper names said in it too). Minimum 40 px. Big title in EB Garamond;
    label in uppercase IBM Plex Mono. No period in on-screen text. Text rises through a mask (`text()` + `rise()`).
13. Ground shadow touching objects, glow (`-glow`) only on outlines and lights, never on a large mass.

## Camera and motion

14. Nothing stays still: every sentence has a camera move (`camZ`) or a transformation (pop, rise, counter, moving object).
15. Pop = `pop()` (spring). Counter = `countUp()`. Events on a word: `word(scene, seg, "text")`.
16. Pull back / dive in: log zoom (`camZ`), not linear.
17. If the speech ends before the animation, the animation runs to the end of the segment; the last frame has to work as a still.

## Render and machine

18. Before any snapshot/render: `free -h` (>= 6 GB available) and run inside
    `systemd-run --user --scope -q -p MemoryMax=3500M -p MemorySwapMax=0 <command>`. Two agents never render at the same time
    (the coordinator renders). Agents only run `check` and `snapshot`, one at a time.
19. `npx hyperframes@0.8.185 snapshot --at t1,t2 -o folder` (times of the index.html project); the contact sheet lands in `folder/contact-sheet*.jpg`.
20. Video inside a timed clip does not render: videos sit loose at the root (not the case for the new scenes, which are SVG).
