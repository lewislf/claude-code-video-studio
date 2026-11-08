# Direção visual do vídeo "Sua mente em termos de uso"

Adaptado do prompt do post https://x.com/finnardley/status/2114305886420086817 (explicador estilo Kurzgesagt feito só em código),
com o que já foi aprovado e rejeitado neste projeto. Vale para toda cena nova. As cenas A, B, D, E, F, C e M1 a M8 (pastas
`cenas-v3` e `cenas-v4`) são a referência de acabamento.

## O que o post faz e a gente copia

1. Cada frase da narração dispara um movimento de câmera ou uma transformação. Nada fica parado.
2. O evento acontece na palavra que o nomeia (tempo por palavra, não por segmento).
3. Forma de cada cena: o evento na palavra, recuar para mostrar escala, mergulhar para o pessoal ("você"), recuar de novo,
   a consequência com um contador ao vivo, uma escalada, um momento engraçado ou humano com o personagem, a volta ao começo.
4. Um personagem recorrente que olha para o que importa (olho acompanha o foco), pisca, respira e faz squash e stretch.
5. Texto grande que sobe por dentro de uma máscara (ease-out-quint), nunca aparece inteiro com fade.
6. Câmera: zoom interpolado em log, easeInOutCubic. Todo "pop" é mola amortecida.
7. Acabamento: vinheta, grão de filme, nebulosa com paralaxe, estrelas que piscam.
8. Mostrar contact sheet de cada cena antes de renderizar. Sempre.
9. Proibido: imagem ou vídeo de IA, personagens de terceiros, textos que não estão na narração, faixas de infográfico estáticas.

## O que muda para o nosso vídeo

Idioma e voz: português do Brasil, voz clonada já gravada. A duração de cada segmento é a da fala (`roteiro.json`,
`duracoes.json`). Nunca esticar a fala para caber a imagem; apertar a animação.

Tempos por palavra: `palavras/<cena>.json` (whisper small). Tempos em segundos da CENA; subtrair `ini` do segmento
para o tempo local. Use `motor.py::palavra(cena, seg, "texto")`.

Visual aprovado (manter):
- Fundo: gradiente radial roxo-escuro (#3a1d7a, #1a1050, #0b0a24), bokeh desfocado, poeira subindo. Vinheta. Neon ciano #3be0ff,
  lilás #8d7bff, âmbar #ffb23e, magenta #ff4fa3, menta #38e8a8, vermelho de alarme #ff4f7d.
- "A pessoa" é a cabeça humana de perfil em linha neon ciano (`arte2.cabeca_linha`) com o cérebro rosa em vista lateral dentro
  do crânio (`arte2.cerebro_lateral`), olho azul que pisca. É o personagem recorrente nos momentos do "você".
- O camundongo é o rato branco numa caixa isométrica de vidro (`camundongo-v2/arte/rato.svg.part`, `cenas-v4/build4.py`).
- A mosca-da-fruta, a rede de neurônios, o corredor de servidores, o cubo isométrico "você está aqui" são cenas prontas
  (`cenas-v3/build2.py`, `build3.py`). Reaproveitar peças, não redesenhar.
- Tipografia: títulos em EB Garamond 700 grande; rótulos em IBM Plex Mono maiúsculo com espaçamento, grandes (>= 40 px).

Rejeitado pelo usuário (nunca repetir):
- Cena vazia, com ícone pequeno solto, ou só texto sobre fundo liso.
- Rótulo pequeno dentro de caixinha de 28 px. Texto só quando for palavra da narração e em tamanho de leitura.
- Cabeça do Prismo, cérebro achatado em cima do olho, avatar de pixels, mosca que parece abelha.
- Elementos cortados pela borda sem intenção, objetos flutuando sem ligação, sobreposição de rótulo com a arte.
- Clipe de terceiros com texto na tela. (Trailers de Ruptura e Matrix ficam como estão, são ficção real.)
- Texto na tela que difere da narração.

Segmentos que NÃO se refazem: `ruptura`, `matrix`, `trio_ficcao` (trailers reais). As páginas de artigo reais (`doc`) mantêm a
imagem da fonte, mas ganham câmera, destaque animado do trecho citado, e rótulo grande no padrão novo.

## Estrutura de uma cena nova (padrão técnico)

- Uma composição HyperFrames por segmento (ou por grupo de segmentos contíguos), gerada em Python por `motor.composicao()`,
  que embrulha `build2.composicao2` (fundo, bokeh, poeira, vinheta, fade de entrada e saída).
- Duração exata do segmento. Fade de preto de 0,4 s no começo e no fim (já no `composicao2`).
- Câmera em um grupo `-cam`. Eventos por palavra com `at=palavra(...)`.
- Cada cena termina com um frame que funciona parado (a fala pode acabar antes da animação).
- Sem áudio dentro da composição (voz e música entram no vídeo final).

## Antes de entregar

1. `python3 build_<grupo>.py` e `npx hyperframes check` sem erro.
2. `npx hyperframes snapshot --at ...` em pelo menos 6 instantes por cena, ver o contact sheet.
3. Crítico (`visual-validator`) em tela cheia. Só passa com PASS ou itens menores.
4. Só então renderizar o clipe.

## Rodada 2: a pessoa de verdade e cenas com mais história (pedido do usuário)

O usuário viu o vídeo completo e disse: a imagem da cabeça de perfil com cérebro rosa "repete em vários lugares onde deveria haver
algo melhor". Ele quer um personagem humano de verdade em cenas de vida: sentado numa cadeira, em casa, com quadros na parede
mostrando momentos da vida (família, aniversário, comprar um carro, formatura), fragmentos coloridos de memória (sensações,
sentimentos); e, quando essa pessoa passa pela porta do trabalho, as memórias e fotos são TOTALMENTE outras, a mesma pessoa com roupa e
cabelo diferentes. Também: quando o texto falar em "abrir" uma pasta, mostrar nome, número e uma prévia (símbolo ou imagem) do tema.

Biblioteca nova: `cenas-v5/gente.py`
- `gente(p, "casa"|"trabalho", "sentado"|"em_pe", glow="<idcena>-glow")` é a MESMA pessoa em duas versões (moletom e cabelo bagunçado
  em casa; camisa, gravata, crachá, óculos e cabelo curto no trabalho). Caixa local ~ x -150..190, y -520..0 (pés em y=0).
  `vida_gente(p, dur)` dá respiração, balanço e piscadas.
- `quadro(p, tipo, x, y, s)` com tipos de casa: familia, aniversario, carro, formatura, praia, cachorro; de trabalho: premio, reuniao,
  planilha, cafe. `orbe(p, simbolo, x, y, cor)` com coracao, bolo, carro, sol, nota, relogio, raio, copo (lembranças em bolhas coloridas).
- Para outros contextos desenhe variações com as mesmas peças (cores de roupa, cadeira, mesa, cenário), sem criar outro estilo.

Quando usar o quê:
- Narração fala da EXPERIÊNCIA de uma pessoa (esquecer, trabalhar, sofrer, usar o feed, ser enganada): use `gente`, em ambientes
  com história (sala, escritório, rua, quarto, celular na mão), com expressão e movimento (andar até a porta, sentar, olhar o celular).
- Narração fala do CÉREBRO ou da MENTE como órgão (neurônios, implante, ressonância, cérebro lido): pode manter a cabeça de perfil
  com cérebro rosa (`motor.pessoa`), mas nunca a mesma composição repetida: varie ângulo, escala e entorno.
- Cada cena precisa de uma imagem diferente das outras do mesmo grupo. Se duas cenas seguidas usam a mesma figura no mesmo lugar,
  reprovado.
