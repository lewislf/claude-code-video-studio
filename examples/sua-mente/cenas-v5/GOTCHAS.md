# Armadilhas já pagas (HyperFrames + GSAP + SVG neste projeto)

Leia antes de escrever uma cena. Cada item custou pelo menos uma rodada de correção.

## Transformações (a fonte de quase todo bug visual)

1. Nunca anime `x`, `y`, `scale` ou `rotation` (GSAP) num elemento SVG que também tem `transform="translate(...) scale(...)"` no
   atributo. O GSAP lê o atributo, sobrescreve e o objeto vai parar em (0,0). Sempre: grupo externo com o `transform` estático,
   grupo interno com `id` que o GSAP anima. Ex.: `<g transform="translate(870 716) scale(.9)"><g id="X-rato">...</g></g>`.
   Nesse arranjo, `x` e `y` do grupo interno estão em unidades já escaladas pelo pai (dividir por escala se quiser pixels).
2. A origem de transformação de um grupo SVG é o canto superior esquerdo da caixa dele, não o centro. Para escalar a partir do
   centro: `transformOrigin:"50% 50%"` e um `<rect>` invisível simétrico dentro do grupo para a caixa ficar centrada.
3. `svgOrigin:"x y"` usa coordenadas globais do SVG e só funciona bem em grupos de topo. Dentro de grupo com translate/scale
   ele erra. Para a câmera use `camZ(...)` (já faz certo) num grupo `#{id}-cam` de topo.
4. Nunca use `scale` estático no atributo e `scale` do GSAP no mesmo elemento. Aninhar.
5. `fromTo` repetido no mesmo alvo precisa de `immediateRender:false` nos tweens seguintes, senão o primeiro estado aparece cedo
   (fantasmas rosados, elementos visíveis antes da hora).
6. Loops (`repeat`) têm que ser finitos e acabar antes de outro tween no mesmo alvo.
7. Valor com `opacity` inicial só no CSS não vale; defina `opacity="0"` no atributo e anime para 1.

## IDs e filtros

8. Todas as composições entram no mesmo documento. Prefixe TODO id com o id da cena (`X-...`), inclusive gradientes, filtros e
   clipPaths. `composicao2` já define `{id}-glow`, `{id}-blur6`, `{id}-blur40`, `{id}-sombra`, `{id}-vig`, `{id}-fundo`.
   Um `url(#filtro)` que não existe pode sumir com o elemento.
9. A raiz da sub-composição não aceita estilo por classe. `composicao2` já embrulha em `.cena`.

## Arte

10. Rato, caixa isométrica, mosca, cabeça e cérebro: use as funções prontas (`cenas-v4/build4.py`: `rato`, `caixa`, `bolt`;
    `cenas-v3/build2.py`: `mosca_rica`, `rede_rica`, F corredor; `cenas-v5/motor.py`: `pessoa`). Não redesenhar.
11. Nada de ícone pequeno solto. Cada cena precisa de um objeto principal grande (>= 35% da altura) e profundidade
    (camadas, sombra, brilho, bokeh). Cena vazia é reprovada.
12. Cérebro: vista lateral, preenche o crânio, lobo frontal acima do olho, cerebelo atrás, tronco desce ao pescoço.
13. Texto: só palavras da narração (números e nomes próprios citados também). Mínimo 40 px. Título grande em EB Garamond;
    rótulo em IBM Plex Mono maiúsculo. Sem ponto final em texto de tela. Texto sobe por máscara (`texto()` + `rise()`).
14. Sombra de chão colada em objetos, brilho (`-glow`) só em contornos e luzes, nunca em massa grande.

## Câmera e movimento

15. Nada fica parado: toda frase tem câmera (`camZ`) ou transformação (pop, rise, contador, objeto que se move).
16. Pop = `pop()` (mola). Contador = `contar()`. Eventos na palavra: `palavra(cena, seg, "texto")`.
17. Recuar/mergulhar: zoom em log (`camZ`), não linear.
18. Se a fala acaba antes da animação, a animação segue até o fim do segmento; o último frame tem que funcionar parado.

## Render e máquina

19. A máquina tem 14 GB e várias sessões. Antes de qualquer snapshot/render: `free -h` (>= 6 GB disponíveis) e rode dentro de
    `systemd-run --user --scope -q -p MemoryMax=3500M -p MemorySwapMax=0 <comando>`. Dois agentes nunca renderizam ao mesmo tempo
    (o coordenador renderiza). Agentes só fazem `check` e `snapshot`, um por vez.
20. `npx hyperframes snapshot --at t1,t2 -o pasta` (tempos do projeto index.html); contact sheet sai em `pasta/contact-sheet*.jpg`.
21. Vídeo dentro de clipe temporizado não renderiza: vídeos ficam soltos na raiz (não é caso das cenas novas, que são SVG).
