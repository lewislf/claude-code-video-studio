# Instruções para quem for construir cenas v5

Você constrói cenas animadas (HyperFrames, SVG + GSAP) para o vídeo "Sua mente em termos de uso" (UFES, Computação e Sociedade).
O usuário reprovou muitas cenas antigas do vídeo (ícones soltos, texto sobre fundo liso, vazio). Você refaz as que lhe forem
atribuídas, no padrão visual aprovado, com a direção adaptada do post https://x.com/finnardley/status/2114305886420086817
(cada frase da narração dispara câmera ou transformação, eventos nas palavras, nada fica parado).

Leia, nesta ordem, antes de escrever código:
1. `cenas-v5/DIRECAO.md` (o que fazer e o que o usuário rejeitou)
2. `cenas-v5/GOTCHAS.md` (armadilhas de transformação/IDs/memória, todas já custaram retrabalho)
3. `cenas-v5/motor.py` (tempo por palavra, `camZ`, `pop`, `rise`, `contar`, `texto`, `pessoa`, `composicao`, `escreve_cenas`)
4. `cenas-v5/exemplo.py` (cena-piloto completa no padrão; copie a estrutura) e as cenas já aprovadas como referência de acabamento:
   `cenas-v3/build2.py` (A mosca, B monitor, F corredor), `cenas-v3/build3.py` (D, E cabeça com cérebro, C feed e mentes),
   `cenas-v4/build4.py` (camundongo, caixa isométrica, bolt). Funções reaproveitáveis em `cenas-v3/arte2.py`.
5. `cenas-v5/roteiro.json` (texto, duração e visual antigo de cada segmento) e `cenas-v5/palavras/<cena>.json` (tempo por palavra).
   Para `doc` (página de artigo real) veja como `video-v2/build.py::v_doc` e `foto` usam as imagens em `video-v2/assets/` e reutilize
   a imagem da fonte: ela fica, mas ganha câmera, destaque animado do trecho citado e título grande.

Regras duras:
- Cada cena tem a duração exata do segmento (`seg(cena, i)` devolve `(ini, dur)`). Tempos de evento por `palavra(...)`.
- Só texto que está na narração (ou número/nome próprio citado nela), >= 40 px, subindo por máscara. Sem ponto final em texto de tela.
  Nunca travessão "—" em nenhum texto que você escrever (código, comentário, texto de tela).
- Cena com objeto principal grande, profundidade, personagem ("a pessoa", o camundongo, a mosca) quando fizer sentido. Sem cena vazia.
- Reaproveite arte pronta; não invente outro estilo de personagem. Proibido: Prismo, personagens de terceiros, imagem de IA.
- Prefixe todos os ids com o id da cena. Nada de `x/y/scale` GSAP em elemento com `transform` no atributo (grupo externo + interno).
- Escreva só dentro da sua pasta `cenas-v5/<grupo>/` (crie). Copie `hyperframes.json` e `package.json` de `cenas-v4/`.
  Não mexa em `video-v2/`, `cenas-v3/`, `cenas-v4/`, nem em outros grupos. Não faça commit/push.
- Máquina com 14 GB e várias sessões: NÃO rode `npx hyperframes render`. Para olhar frames use SOMENTE
  `cenas-v5/snap.sh <sua-pasta> <saida> <t1,t2,...>` (trava global, um por vez, teto de memória). `npx hyperframes check --json`
  pode rodar direto (leve).
- Ciclo por cena: escrever -> `check` -> snapshot em >= 6 instantes (incluindo cada evento de palavra) -> olhar o contact sheet
  (use a ferramenta Read nas imagens) -> corrigir -> pedir crítica ao agente `visual-validator` se você tiver a ferramenta Agent
  (passe caminhos de PNG, contexto da cena e as rejeições do usuário; exija PASS) -> só então seguir. Sem a ferramenta Agent,
  seja você o crítico severo: procure corte de borda, elemento solto, sobreposição de texto com arte, vazio, texto ilegível.

Entrega (arquivo `cenas-v5/<grupo>/build_<grupo>.py`):
- Define `CENAS = [(id_da_cena, funcao, duracao), ...]` e, no `__main__`, chama `escreve_cenas(CENAS, AQUI)` (de `motor.py`).
- Ids de cena no formato `<CENA>_<seg>` (ex.: `contrato_3`), únicos. Um `MAPA = {(cena, seg): id}` ligando segmento do vídeo a id.
- Relatório final curto: quais cenas, o que cada uma mostra, o que ficou fraco, o que o crítico apontou e não foi resolvido.
