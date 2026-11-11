# Traps already paid for (HyperFrames + GSAP + SVG in this project)

Read before writing a scene. Each item cost at least one round of fixes.

## Transforms (the source of almost every visual bug)

1. Never animate `x`, `y`, `scale` or `rotation` (GSAP) on an SVG element that also has `transform="translate(...) scale(...)"` as an
   attribute. GSAP reads the attribute, overwrites it, and the object ends up at (0,0). Always: an outer group with the static
   `transform`, an inner group with an `id` that GSAP animates. E.g. `<g transform="translate(870 716) scale(.9)"><g id="X-mouse">...</g></g>`.
   In that setup, `x` and `y` of the inner group are in units already scaled by the parent (divide by the scale if you want pixels).
2. The transform origin of an SVG group is the top left corner of its box, not the center. To scale from the
   center: `transformOrigin:"50% 50%"` and an invisible symmetric `<rect>` inside the group so the box is centered.
3. `svgOrigin:"x y"` uses global SVG coordinates and only works well on top-level groups. Inside a group with translate/scale
   it gets it wrong. For the camera use `camZ(...)` (it already does it right) on a top-level `#{id}-cam` group.
4. Never use a static `scale` in the attribute and a GSAP `scale` on the same element. Nest.
5. A repeated `fromTo` on the same target needs `immediateRender:false` on the later tweens, otherwise the first state shows up early
   (pinkish ghosts, elements visible before their time).
6. Loops (`repeat`) must be finite and end before another tween on the same target.
7. An initial `opacity` set only in CSS doesn't count; set `opacity="0"` in the attribute and animate to 1.

## IDs and filters

8. All compositions go into the same document. Prefix EVERY id with the scene id (`X-...`), including gradients, filters and
   clipPaths. `composition2` already defines `{id}-glow`, `{id}-blur6`, `{id}-blur40`, `{id}-shadow`, `{id}-vig`, `{id}-background`.
   A `url(#filter)` that doesn't exist can make the element vanish.
9. The root of a sub-composition doesn't take class-based styles. `composition2` already wraps it in `.scene`.

## Art

10. Mouse, isometric box, fly, head and brain: use the ready-made functions (`scenes-v4/build4.py`: `mouse`, `box`, `bolt`;
    `scenes-v3/build2.py`: `fly_rich`, `network_rich`, F corridor; `scenes/engine.py`: `person`). Don't redraw them.
11. No small loose icons. Each scene needs a big main object (>= 35% of the height) and depth
    (layers, shadow, glow, bokeh). An empty scene fails.
12. Brain: side view, fills the skull, frontal lobe above the eye, cerebellum at the back, brainstem going down to the neck.
13. Text: only words from the narration (numbers and proper names it mentions too). Minimum 40 px. Big title in EB Garamond;
    label in uppercase IBM Plex Mono. No period at the end of on-screen text. Text rises through a mask (`text()` + `rise()`).
14. Floor shadow attached to objects, glow (`-glow`) only on outlines and lights, never on a large mass.

## Camera and motion

15. Nothing stands still: every sentence gets camera (`camZ`) or a transformation (pop, rise, counter, an object that moves).
16. Pop = `pop()` (spring). Counter = `count_up()`. Events on the word: the time came from the narration and is now a fixed number
    in the scene's code.
17. Pull back/dive in: zoom in log space (`camZ`), not linear.
18. If the speech ends before the animation, the animation keeps going until the end of the segment; the last frame has to work as a still.

## Rendering and the machine

19. The machine has 14 GB and several sessions. Before any snapshot/render: `free -h` (>= 6 GB available) and run inside
    `systemd-run --user --scope -q -p MemoryMax=3500M -p MemorySwapMax=0 <command>`. Two agents never render at the same time
    (the coordinator renders). Agents only run `check` and `snapshot`, one at a time.
20. `npx hyperframes@0.8.185 snapshot --at t1,t2 -o folder` (times of the index.html project); the contact sheet comes out at `folder/contact-sheet*.jpg`.
21. Video inside a timed clip doesn't render: videos stay loose at the root (not the case for the new scenes, which are SVG).
