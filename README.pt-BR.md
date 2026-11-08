# claude-code-video-studio

[English](README.md) · **Português**

Pipeline pra fazer vídeo explicativo narrado inteiro na sua máquina, com o Claude Code dirigindo: roteiro, voz, trilha,
cenas animadas, montagem, versão acelerada e capa. Nenhuma API paga. Voz no OmniVoice, música no MusicGen, cenas em
HTML/SVG/GSAP renderizadas pelo [HyperFrames](https://github.com/heygen-com/hyperframes), capa no SDXL via ComfyUI.

[<img src="media/player.gif" width="720" alt="Assistir: O contrato que você nunca assinou (13:15)">](https://github.com/lewislf/claude-code-video-studio/releases/download/sua-mente/sua-mente-1080p.mp4)

Feito com isto: *Sua mente em termos de uso*, 13 minutos sobre neurotecnologia, em português (trabalho de Computação e
Sociedade, UFES). Código completo em [`examples/sua-mente/`](examples/sua-mente/).

Clique no player pra assistir em 1080p (552 MB), ou a [cópia leve de 27 MB](https://github.com/lewislf/claude-code-video-studio/releases/download/sua-mente/sua-mente-celular.mp4). Descrição e capítulos na [release](https://github.com/lewislf/claude-code-video-studio/releases/tag/sua-mente).

## Como funciona

Um vídeo é uma pasta com um `script.py`. O roteiro é a fonte única: dele saem a voz, o tempo de cada cena e a montagem.

```python
SCENES = [
  ("sky", "The sky", [
    ("Look up on a clear day. The sky is blue.", 0.5, {"a": "sky"}),
    ("But sunlight is white.", 1.4, {"a": "prism"}),
  ]),
]
```

Cada segmento (texto falado, pausa, visual) vira um clipe com a duração exata da fala. As cenas são funções Python que
devolvem HTML; `word("sky", 0, "blue")` dá o instante em que a voz diz "blue", e a animação dispara ali.

```
script.py ──> tts.py ──> assets/voice/*.wav + durations.json ──> transcribe.py ──> words/*.json
                                   │                                                  │
                                   └──────────> scenes/<group>/build_*.py <───────────┘
                                                        │  scenes.py render
music.py ──> assets/music.mp3 ──> assemble.py <── assets/clips/*.mp4
                                        │
             progress_bar.sh ──> deliver.sh ──> renders/v1-bar-1.35x.mp4 (+ mobile)
```

O idioma da narração é o `LANG` do `script.py` (código ISO, padrão `"en"`). Funciona qualquer idioma que o OmniVoice suporte;
o vídeo de exemplo é em pt-BR. A voz de referência que vem no repo (`studio/voices/deep_narrator.wav`) é uma
amostra em português; o `LANG` define o idioma da fala gerada, e dá pra apontar o `VOICE` pra um clipe de referência seu.

## Começar um vídeo

```bash
cp -r template ~/videos/meu-video && cd ~/videos/meu-video
ST=~/claude-code-video-studio/studio; PY=<python com omnivoice, faster-whisper e transformers>

$PY $ST/tts.py generate && $PY $ST/tts.py pick          # voz, 3 tentativas por frase, fica a que o whisper entende melhor
python3 $ST/transcribe.py                               # tempo de cada palavra
$PY $ST/music.py                                        # trilha
python3 $ST/scenes.py render g1                         # cenas do grupo g1 -> clipes
python3 $ST/assemble.py                                 # renders/v1.mp4
$ST/progress_bar.sh v1 v1-bar && $ST/deliver.sh v1-bar  # barra de progresso e versão 1,35x
```

Com o Claude Code, é mais fácil pedir: copie `skills/` pra `~/.claude/skills/` e diga "faz um vídeo narrado sobre X".
A skill `narrated-video` sabe as etapas; as cenas vão pra subagentes com o briefing `studio/AGENT.md`; a skill `ai-cover`
gera a thumbnail.

| Pasta | O que tem |
|---|---|
| `studio/` | o pipeline (voz, palavras, música, cenas, montagem, remendo, entrega) e o motor das cenas |
| `template/` | projeto mínimo de 20 s pra copiar |
| `skills/` | `narrated-video` e `ai-cover` pro Claude Code |
| `examples/sua-mente/` | o vídeo da UFES como foi feito: 72 cenas, roteiro, briefings. Não roda sem os assets (voz, páginas de artigo, trailers), que ficaram fora do repo |

## Requisitos

GPU NVIDIA (testado numa RTX 5070 de 8 GB), Linux com `systemd-run` (os scripts põem teto de memória), ffmpeg, Node (pro
`npx hyperframes`), um Python com `omnivoice`, `faster-whisper` e `transformers`, e ComfyUI com o SDXL base pra capa.
O `taskline`, se instalado, mostra o progresso.

Voz e música são geradas por IA; diga isso na descrição do vídeo.

## Créditos

Feito por [lewislf](https://github.com/lewislf) e [FeLiPeOLi7](https://github.com/FeLiPeOLi7).

## Licença

Código sob [MIT](LICENSE). Os trechos de filmes e trailers citados em `examples/sua-mente/video-v2/assets/CREDITOS.md`
pertencem aos seus donos e não estão no repo. A foto da mosca
`examples/sua-mente/cenas-v5/g3_escrever_mapear/assets/mosca.jpg` é de Alexis (iNaturalist), CC BY 4.0. A primeira página de Ryan et al. 2015, embutida numa cena do exemplo, tem o crédito em `examples/sua-mente/README.md`.
