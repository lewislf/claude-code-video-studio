<p align="center">
  <img src=".claude-plugin/icon.png" alt="claude-code-video-studio mascot editing a video" width="220">
</p>

<h1 align="center">claude-code-video-studio</h1>

<p align="center"><b>Narrated explainer videos made on your own GPU, with Claude Code directing.</b></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT license"></a>
  <a href="#quick-start"><img src="https://img.shields.io/badge/Claude%20Code-plugin-D97757" alt="Claude Code plugin"></a>
  <img src="https://img.shields.io/badge/voice%20%C2%B7%20music%20%C2%B7%20render-local-2ea44f" alt="voice, music and render run locally">
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#what-you-get">What you get</a> ·
  <a href="#why-local">Why local</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#setup">Setup</a> ·
  <a href="README.pt-BR.md">Português</a>
</p>

Script, voice, music, animated scenes, assembly, sped-up version and cover, all on your machine. Voice on OmniVoice, music on
MusicGen, scenes in HTML/SVG/GSAP rendered by [HyperFrames](https://github.com/heygen-com/hyperframes), cover on SDXL via
ComfyUI. No voice, music or video API to pay for.

[<img src="media/player.gif" width="720" alt="Watch: Who holds the key to your mind? (13:15)">](https://github.com/lewislf/claude-code-video-studio/releases/download/your-mind/your-mind-en-1080p.mp4)

Made with this: *Your mind under terms of use*, 13 minutes on neurotechnology (assignment for Computers and Society,
UFES). It was made in Brazilian Portuguese and then dubbed into English with this pipeline. Full code in
[`examples/your-mind/`](examples/your-mind/).

Click the player to watch in 1080p (716 MB), or the [light 26 MB copy](https://github.com/lewislf/claude-code-video-studio/releases/download/your-mind/your-mind-en-phone.mp4). Description
and chapters in the [release](https://github.com/lewislf/claude-code-video-studio/releases/tag/your-mind); the
[original Portuguese cut](https://github.com/lewislf/claude-code-video-studio/releases/tag/sua-mente) has its own.

## Quick start

Install the skills as a Claude Code plugin:

```bash
claude plugin marketplace add lewislf/claude-code-video-studio
claude plugin install video-studio@claude-code-video-studio
```

Then ask in plain words. Some prompts that work:

- "make a narrated video about why the sky is blue, 3 minutes"
- "redo scene 12, the diagram is too small"
- "swap the voice for a British one"
- "make the final version at 1.35x and send it to my phone"
- "write the YouTube description with chapters" / "make a cover"

The `narrated-video` skill knows the steps; scenes go to subagents with the `studio/AGENT.md` briefing; the `ai-cover` skill
makes the thumbnail. The machine still needs the [setup](#setup) below.

## What you get

- one MP4 per video, with the narration over a low music bed and a thin progress bar;
- a sped-up cut (1.35x by default) and a light phone copy;
- the voice cloned from a reference clip, in any language OmniVoice speaks, with 3 takes per sentence and whisper picking the
  clearest one;
- scenes timed to the word: an animation fires on the instant the voice says it;
- patching: redo one scene (`patch.py`) or the whole audio (`swap_audio.py`) without rebuilding the rest;
- dubbing: a new language over the same timeline, with `.srt` subtitles (`examples/your-mind/dub.py`, how the example became
  English);
- YouTube title, description and chapters, and a 1280x720 cover.

## Why local

Similar projects, by what their READMEs say (November 2026):

| | Voice | Music | Visuals |
|---|---|---|---|
| **this repo** | OmniVoice, local, voice cloning | MusicGen, local | HyperFrames scenes written by Claude, rendered locally |
| [OpenMontage](https://github.com/calesthio/OpenMontage) | Piper offline, or cloud TTS | royalty-free library or Suno | stock footage, or paid image/video APIs |
| [video_explainer](https://github.com/prajwal-y/video_explainer) | ElevenLabs or Edge TTS (online) | MusicGen, local | Remotion |
| [Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video) | Edge TTS (online) or Index-TTS | your own files | ComfyUI images or image APIs |

The script still comes from Claude Code, so you need a Claude plan. Everything after it runs on your GPU.

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
video is pt-BR. The voice is cloned from a reference clip, and the clip's accent carries over, so the reference has to be in
the narration's language. `studio/voices/` has eight English references made with OmniVoice voice design (deep male US and UK,
older male US, low female US, two takes each) and one Portuguese (`deep_narrator`). Without `VOICE`, English uses
`en_deep_us_b` and other languages use `deep_narrator`; set `VOICE = "en_deep_uk_a"` to pick another, or point it at your own clip.

## Run it by hand

The same pipeline without the skills:

```bash
cp -r template ~/videos/my-video && cd ~/videos/my-video
ST=~/claude-code-video-studio/studio; PY=~/.venvs/studio/bin/python   # the env from Setup

$PY $ST/tts.py generate && $PY $ST/tts.py pick          # voice, 3 takes per sentence, keeps the one whisper understands best
python3 $ST/transcribe.py                               # timing of each word
$PY $ST/music.py                                        # music
python3 $ST/scenes.py render g1                         # scenes of group g1 -> clips
python3 $ST/assemble.py                                 # renders/v1.mp4
$ST/progress_bar.sh v1 v1-bar && $ST/deliver.sh v1-bar  # progress bar and 1.35x version
```

| Folder | What it has |
|---|---|
| `studio/` | the pipeline (voice, words, music, scenes, assembly, patching, delivery) and the scene engine |
| `template/` | minimal 20 s project to copy |
| `skills/` | `narrated-video` and `ai-cover` for Claude Code |
| `examples/your-mind/` | the UFES video in English: 72 scenes, script, dub, briefings. Rendering needs the assets (voice, article pages, trailers), which were left out of the repo |

## Setup

NVIDIA GPU (tested on an 8 GB RTX 5070), Linux with `systemd-run` (the scripts set memory caps), ffmpeg, Node 22+ (for
`npx hyperframes@0.8.185`). The voice, word timing and music share one Python 3.11 environment:

```bash
python3.11 -m venv ~/.venvs/studio
~/.venvs/studio/bin/pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu128
~/.venvs/studio/bin/pip install "omnivoice @ git+https://github.com/debpalash/VoiceStudio@73b83768bdc02dd7068c5c2fefcfa0530fa622e4" \
  faster-whisper transformers accelerate soundfile librosa
```

The environment takes about 9 GB. Tested from scratch with torch 2.11 (cu128), VoiceStudio at the pinned commit, faster-whisper
1.2.1 and transformers 5.22; the template video renders end to end. Install `torchvision` from the PyTorch index together with
torch: the copy pip pulls in for `omnivoice` does not match the cu128 build and breaks the import. The OmniVoice and MusicGen
weights download from Hugging Face on the first run. The cover needs ComfyUI with SDXL base (see `skills/ai-cover/SKILL.md`).
`taskline`, if installed, shows progress.

## What it runs and downloads

Everything runs on your machine. The plugin sends no data anywhere: no telemetry, no API calls of its own. It downloads:

- the OmniVoice, whisper and MusicGen weights from Hugging Face, on the first run of each step;
- `hyperframes@0.8.185` from npm through `npx`, to render the scenes and time the words (it uses a local headless Chrome);
- GSAP 3.14.2 from cdn.jsdelivr.net and the fonts from fonts.googleapis.com, loaded by the scene pages while they render;
- the Python packages in [Setup](#setup), when you install them.

The skills run the scripts in `studio/` with `python3`, `ffmpeg` and `systemd-run`, inside the video's own folder, and the
`ai-cover` skill talks to a ComfyUI server on `127.0.0.1`.

## Model licenses

The code here is MIT, but the models have their own terms, and they decide what you can do with the video:

- MusicGen weights (`facebook/musicgen-small`): CC-BY-NC 4.0, **non-commercial**. On a monetized channel, swap the music for
  a track you have rights to.
- OmniVoice: the `omnivoice` package (VoiceStudio) is AGPL-3.0; the `k2-fsa/OmniVoice` weights follow their model card.
- SDXL base: CreativeML Open RAIL++-M.

Voice and music are AI-generated; say so in the video description.

## Credits

Made by [lewislf](https://github.com/lewislf) and [FeLiPeOLi7](https://github.com/FeLiPeOLi7).

## License

Code under [MIT](LICENSE). The film and trailer clips cited in `examples/your-mind/film/assets/CREDITS.md`
belong to their owners and are not in the repo. The [fly photo](examples/your-mind/scenes/g3_writing_mapping/assets/fly.jpg) is by Alexis (iNaturalist), CC BY 4.0.
