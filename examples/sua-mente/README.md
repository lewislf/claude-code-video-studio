# Sua mente em termos de uso

13 min video (at 1.35x) for the Computers and Society course, UFES. The video itself is in Brazilian Portuguese, and so are
the file names, comments and briefings here. The code is frozen as it was used, with the original folder names so relative
paths still work. This is the project `studio/` came out of; it does not use `studio/`.

- `roteiro-v2.md`: the readable script. The source is `video-v2/roteiro.py`.
- `video-v2/`: voice (`tts.py`), cleanup, music, assembly (`montar_final.py`, `remendar.py`), the ending glitch, YouTube description.
- `cenas-v5/g1..g8/`: the 72 scenes, one per narration segment. `AGENTE.md`, `DIRECAO.md` and `GOTCHAS.md` are the briefings
  the subagents received, with what the user rejected along the way.
- `cenas-v3/`, `cenas-v4/`, `camundongo-v2/`: reused art (fly, brain, mouse, box).
- `teste-voz/vozes/`: the narrator's reference voice.

Left out of the repo (1.3 GB): generated voice, music, trailer clips, the renders and the pages of the cited articles, except one: the first page of Ryan et al. 2015 (author manuscript) is embedded in `cenas-v5/g2_trancada/compositions/trancada_4.html`. Credit: Ryan, T. J., Roy, D. S., Pignatelli, M., Arons, A. & Tonegawa, S. (2015). Engram cells retain memory under retrograde amnesia. Science 348, 1007-1013. https://doi.org/10.1126/science.aaa5542. The scripts
still point to `/tmp/claude-1002` and to the original machine's linuxbrew ffmpeg.
