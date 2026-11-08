# claude-code-video-studio

**English** · [Português](README.pt-BR.md)

Pipeline to make a narrated explainer video entirely on your machine, with Claude Code directing: script, voice, music,
animated scenes, assembly, sped-up version and cover. No paid API. Voice on OmniVoice, music on MusicGen, scenes in
HTML/SVG/GSAP rendered by [HyperFrames](https://github.com/heygen-com/hyperframes), cover on SDXL via ComfyUI.

[<img src="media/player.gif" width="720" alt="Watch: The contract you never signed (13:15, in Brazilian Portuguese)">](https://github.com/lewislf/claude-code-video-studio/releases/download/sua-mente/sua-mente-1080p.mp4)

Made with this: *Sua mente em termos de uso* ("Your mind under terms of use"), 13 minutes on neurotechnology, in Brazilian
Portuguese (assignment for Computers and Society, UFES). Full code in [`examples/sua-mente/`](examples/sua-mente/).

Click the player to watch in 1080p (552 MB), or the [light 27 MB copy](https://github.com/lewislf/claude-code-video-studio/releases/download/sua-mente/sua-mente-celular.mp4). Description and chapters in the [release](https://github.com/lewislf/claude-code-video-studio/releases/tag/sua-mente).

## How it works

A video is a folder with a `script.py`. The script is the single source: the voice, the timing of each scene and the assembly all come from it.

```python
SCENES = [
  ("sky", "The sky", [
    ("Look up on a clear day. The sky is blue.", 0.5, {"a": "sky"}),
    ("But sunlight is white.", 1.4, {"a": "prism"}),
  ]),
]
```

Each segment (spoken text, pause, visual) becomes a clip with the exact duration of the speech. Scenes are Python functions that
return HTML; `word("sky", 0, "blue")` gives the instant the voice says "blue", and the animation fires there.

```
script.py ──> tts.py ──> assets/voice/*.wav + durations.json ──> transcribe.py ──> words/*.json
                                   │                                                  │
                                   └──────────> scenes/<group>/build_*.py <───────────┘
                                                        │  scenes.py render
music.py ──> assets/music.mp3 ──> assemble.py <── assets/clips/*.mp4
                                        │
             progress_bar.sh ──> deliver.sh ──> renders/v1-bar-1.35x.mp4 (+ mobile)
```

The narration language is `LANG` in `script.py` (ISO code, default `"en"`). Any language OmniVoice supports works; the example
video is pt-BR. The bundled reference voice (`studio/voices/deep_narrator.wav`) is a Portuguese sample; `LANG` sets the language
of the generated speech, and you can point `VOICE` at your own reference clip.

## Start a video

```bash
cp -r template ~/videos/my-video && cd ~/videos/my-video
ST=~/claude-code-video-studio/studio; PY=<python with omnivoice, faster-whisper and transformers>

$PY $ST/tts.py generate && $PY $ST/tts.py pick          # voice, 3 takes per sentence, keeps the one whisper understands best
python3 $ST/transcribe.py                               # timing of each word
$PY $ST/music.py                                        # music
python3 $ST/scenes.py render g1                         # scenes of group g1 -> clips
python3 $ST/assemble.py                                 # renders/v1.mp4
$ST/progress_bar.sh v1 v1-bar && $ST/deliver.sh v1-bar  # progress bar and 1.35x version
```

With Claude Code it is easier to ask: copy `skills/` to `~/.claude/skills/` and say "make a narrated video about X".
The `narrated-video` skill knows the steps; scenes go to subagents with the `studio/AGENT.md` briefing; the `ai-cover` skill
makes the thumbnail.

| Folder | What it has |
|---|---|
| `studio/` | the pipeline (voice, words, music, scenes, assembly, patching, delivery) and the scene engine |
| `template/` | minimal 20 s project to copy |
| `skills/` | `narrated-video` and `ai-cover` for Claude Code |
| `examples/sua-mente/` | the UFES video as it was made: 72 scenes, script, briefings. Does not run without the assets (voice, article pages, trailers), which were left out of the repo |

## Requirements

NVIDIA GPU (tested on an 8 GB RTX 5070), Linux with `systemd-run` (the scripts set memory caps), ffmpeg, Node (for
`npx hyperframes`), a Python with `omnivoice`, `faster-whisper` and `transformers`, and ComfyUI with SDXL base for the cover.
`taskline`, if installed, shows progress.

Voice and music are AI-generated; say so in the video description.

## Credits

Made by [lewislf](https://github.com/lewislf) and [FeLiPeOLi7](https://github.com/FeLiPeOLi7).

## License

Code under [MIT](LICENSE). The film and trailer clips cited in `examples/sua-mente/video-v2/assets/CREDITOS.md`
belong to their owners and are not in the repo. The fly photo
`examples/sua-mente/cenas-v5/g3_escrever_mapear/assets/mosca.jpg` is by Alexis (iNaturalist), CC BY 4.0. The first page of Ryan et al. 2015, embedded in one scene of the example, is credited in `examples/sua-mente/README.md`.
