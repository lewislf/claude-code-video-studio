# Troca do personagem humano nas cenas (rodada gente nova)

O usuário reprovou várias vezes o personagem humano antigo (perfil, "horrível de feio") e APROVOU o novo personagem geométrico
(estilo explainer, 3/4, rim light neon). `cenas-v5/gente.py` já desenha o novo: mesma assinatura
`gente(p, variante, pose, glow=, cadeira=, sombra=, giro=25)`, mesmos ids (`{p}`, `-corpo`, `-tor`, `-torso`, `-braco`, `-bracoE`,
`-pernas`, `-cabW`, `-cab`, `-olho`), caixa local com pés em y=0 e topo da cabeça de pé em ~-540. Referência visual aprovada:
`cenas-v5/teste_gente3/geometrico/esboco.png` e `teste_svg_4.png`. O antigo está em `gente_perfil_backup.py` (só para consulta).

O que mudou e quebra cenas:
- Corpo novo: mãos, cabeça e colo em outros lugares. Use `ANCORAS[(variante, pose, giro)]` de gente.py (`mao_d`, `mao_e`, `colo`,
  `cabeca_centro`, `cabeca_topo`, `ombro_braco`; giro 0 ou 30, giro>=15 usa 30) para reposicionar objetos presos à pessoa
  (caneca, celular, pipoca, fones, raio-x, crachá, balões etc.). Nada pode ficar flutuando nem atravessando o corpo.
- Personagem agora é 3/4 olhando levemente para a direita (giro 25). Quando a cena pedir olhar para a esquerda, espelhe com um grupo
  externo `scale(-1 1)`. Use giro=0 (de frente) quando a pessoa encara a câmera.
- Troca de cor ("outras pessoas"): cada peça tem UM hex base (PELE, CASA[...], TRAB[...], CABELO, GRAVATA em gente.py) e sombra/luz
  são camadas neutras por cima. `torso2` e `PELE_E` não existem mais no SVG. Hex literais do personagem antigo no seu build não pegam
  mais nada: troque pelos hex base novos (importe as constantes).
- Truques que dependiam do desenho antigo (boca trocável, braço com celular `{p}-tela`/`{p}-luzc` do g5, `na_cabeca`/`raio_x` do g4,
  `retrato` em (0,-575) do g7, cabeça embrulhada do g8) precisam ser refeitos sobre a anatomia nova. Faça o mínimo que deixe a cena
  certa: por exemplo, celular como objeto desenhado na `mao_e` ou `mao_d`, expressão por sobrancelha/boca desenhadas por cima do rosto
  num grupo próprio.
- Figuras minúsculas (multidão, escala < 0.3) podem continuar com o desenho novo pequeno; só confira que não ficaram estranhas.

Regras (as mesmas de `AGENTE.md` e `GOTCHAS.md`, leia os dois):
- Edite SÓ o build do seu grupo (`cenas-v5/<grupo>/build_<grupo>.py`). Não edite gente.py nem outros grupos. Se gente.py tiver
  um defeito que você não consegue contornar no build, descreva no relatório.
- Não renderize (`npx hyperframes render` e `montar.py` são proibidos para você). Para ver quadros use SÓ
  `cenas-v5/snap.sh <pasta> <saida> <t1,t2,...>` (trava global) e `cenas-v5/check.sh <pasta>`.
- Para gerar as composições do grupo sem renderizar: `cd cenas-v5/<grupo> && python3 build_<grupo>.py`. Para olhar uma cena
  específica veja como o build/motor.escreve_cenas monta o index.html e os tempos de cada cena dentro dele.
- Ciclo por cena com humano: build -> check -> snapshot em >= 5 instantes (inclua os momentos em que a pessoa se move ou segura algo)
  -> Read nas imagens -> corrigir -> crítico `visual-validator` (passe PNGs, contexto e que o usuário odiou o personagem antigo;
  exija PASS ou só itens menores).
- Nunca travessão "—" em nada que escrever. Nada de commit.

Entrega: relatório curto (até 12 linhas) com
1. `PRONTAS: id1,id2,...` (cenas com humano que passaram no crítico e podem ser renderizadas),
2. `MANTER_ANTIGA: ...` (cenas que ficaram piores e devem manter o clipe antigo, com motivo),
3. o que ficou fraco.
