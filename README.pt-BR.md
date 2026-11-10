# claude-code-video-studio

[English](README.md) · **Português**

Pipeline pra fazer vídeo explicativo narrado inteiro na sua máquina, com o Claude Code dirigindo: roteiro, voz, trilha,
cenas animadas, montagem, versão acelerada e capa. Nenhuma API paga. Voz no OmniVoice, música no MusicGen, cenas em
HTML/SVG/GSAP renderizadas pelo [HyperFrames](https://github.com/heygen-com/hyperframes), capa no SDXL via ComfyUI.

[<img src="media/player-pt-BR.gif" width="720" alt="Assistir: O contrato que você nunca assinou (13:15)">](https://github.com/lewislf/claude-code-video-studio/releases/download/sua-mente/sua-mente-1080p.mp4)

Feito com isto: *Sua mente em termos de uso*, 13 minutos sobre neurotecnologia, em português (trabalho de Computação e
Sociedade, UFES). O código completo, já da versão dublada em inglês, está em [`examples/your-mind/`](examples/your-mind/).

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
o vídeo de exemplo é em pt-BR. A voz é clonada de um clipe de referência e o sotaque do clipe vem junto, então a referência
tem que estar no idioma da narração. Em `studio/voices/` há oito referências em inglês feitas com o voice design do OmniVoice
(masculina grave americana e britânica, masculina mais velha americana, feminina grave americana, duas versões de cada) e uma
em português (`deep_narrator`). Sem `VOICE`, inglês usa `en_deep_us_b` e os outros idiomas usam `deep_narrator`; `VOICE = "en_deep_uk_a"`
escolhe outra, ou aponte pra um clipe seu.

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
| `examples/your-mind/` | o vídeo da UFES em inglês: 72 cenas, roteiro, dublagem, briefings. O render precisa dos assets (voz, páginas de artigo, trailers), que ficaram fora do repo |

## Requisitos

GPU NVIDIA (testado numa RTX 5070 de 8 GB), Linux com `systemd-run` (os scripts põem teto de memória), ffmpeg, Node (pro
`npx hyperframes`), um Python com `omnivoice`, `faster-whisper` e `transformers`, e ComfyUI com o SDXL base pra capa.
O `taskline`, se instalado, mostra o progresso.

Voz e música são geradas por IA; diga isso na descrição do vídeo.

## Créditos

Feito por [lewislf](https://github.com/lewislf) e [FeLiPeOLi7](https://github.com/FeLiPeOLi7).

## Licença

Código sob [MIT](LICENSE). Os trechos de filmes e trailers citados em `examples/your-mind/film/assets/CREDITS.md`
pertencem aos seus donos e não estão no repo. A foto da mosca
`examples/your-mind/scenes/g3_writing_mapping/assets/fly.jpg` é de Alexis (iNaturalist), CC BY 4.0.
