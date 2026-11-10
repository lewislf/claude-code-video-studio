# Your mind under terms of use

13 min video (at 1.35x) on neurotechnology, made for the Computers and Society course at UFES. It was first made in
Brazilian Portuguese; this folder is the English version: English narration, on-screen text and subtitles over the same
72 scenes and the same timeline. This is the project `studio/` came out of, so it does not use `studio/` except for the
voice (`studio/tts.py` with the `en_deep_us_b` voice).

Watch it in the [`your-mind` release](https://github.com/lewislf/claude-code-video-studio/releases/tag/your-mind).

## Layout

- `script.py`: the narration, one entry per scene with its segments. Segment i of each scene starts where segment i
  started in the Portuguese cut (`film/assets/voice/slots.json`), so the visuals did not have to move.
- `dub.py`: fits each English segment into its slot (sped up with atempo up to 1.15x, the rest is reported in
  `out/fit.tsv`), rebuilds the glitch ending with `film/end_glitch.py`, mixes the music and writes the `.srt`.
- `word_times.py`: per-word times of the closing narration, which drive the last group of scenes.
- `rebuild.sh`: everything after `tts.py generate/pick`, from the voice to `out/your-mind-en-1080p.mp4` and the phone copy.
- `render_all.sh`: renders the scenes and cuts them into `film/assets/clips/`. `trailers.py` does the same for the three
  fiction-trailer segments.
- `scenes/g1..g8/`: the 72 scenes, one per narration segment, on top of `scenes/engine.py` and `scenes/figure.py`.
  `AGENT.md`, `DIRECTION.md` and `GOTCHAS.md` are the briefings the scene subagents got, including what was rejected along
  the way.
- `scenes-v3/`, `scenes-v4/`, `mouse-art/`: art reused by the scenes (fly, brain, mouse, box).
- `film/`: final assembly, the ending glitch, music, covers, thumbnail and the YouTube description.

## What is not in the repo

The generated voice, the music, the pages of the cited articles, the trailer footage (`film/renders/v2-mixed.mp4`), the
laugh take of the ending and the renders, about 1.3 GB. The scene builds run without them and write HyperFrames
compositions (the article pages show up blank); rendering the final video needs them.

```bash
cd scenes/g2_locked && python3 build_g2_locked.py   # writes compositions/
cd ../.. && ./render_all.sh                          # renders every group but g8 into film/assets/clips/
```
