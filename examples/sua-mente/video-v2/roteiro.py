"""Roteiro v2 em dados: fonte única da voz (tts.py), das cenas (build.py) e do .md (python roteiro.py).

Segmento: (texto falado, pausa depois em s, visual). O visual diz o ASSUNTO ("a") e o
build.py escolhe como mostrá-lo conforme o estilo (doc, 3d ou misto).
Rótulo do canto: "r" = ficcao | pesquisa | caso | argumento | ilustracao.
"""

# Só afeta o áudio. Pronúncia em inglês para siglas e nomes estrangeiros.
PRONUNCIA = {
    "MIT": "eme-ai-ti",  # testado: o Whisper ouve "MIT" em 4 de 4
    "Neuralink": "Niúralink",
    "Lumon": "Lúmon",
    "Tonegawa": "Tonegáua",
    "Adrian Owen": "Êidrian Ôuen",
    "FlyWire": "Flai uáier",
    "LessWrong": "Léss Róng",
    "Roko": "Rôko",
    "Bostrom": "Bóstrom",
    "Guizzardi": "Guitsárdi",
    "Giancarlo": "Djancárlo",
}

P, G = 1.4, 0.5  # [pausa] e respiro entre parágrafos

CENAS = [
  ("abertura", "Abertura", [
    ("Em dois mil e treze, num laboratório do MIT, nos Estados Unidos, um camundongo entrou numa caixa onde nunca tinha acontecido nada com ele.", G,
     {"a": "camundongo", "estado": "calma", "r": "pesquisa", "sobre": "MIT · ESTADOS UNIDOS · 2013"}),
    ("E congelou de medo.", G, {"a": "camundongo", "estado": "medo", "r": "pesquisa"}),
    ("Ele se lembrava de levar um choque ali. Só que esse choque nunca aconteceu naquela caixa.", P,
     {"a": "frase", "texto": "O choque nunca aconteceu ali."}),
    ("Alguém escreveu essa lembrança nele. Com luz.", P, {"a": "flash", "texto": "Com luz."}),
    ("Este vídeo é sobre uma pergunta. Quem tem o poder de entrar na sua mente? De trancar uma lembrança, escrever outra, ler o que você pensa, ou decidir que realidade você vai enxergar?", G,
     {"a": "pergunta", "linhas": ["trancar", "escrever", "ler", "decidir o que você vê"]}),
    ("A ficção já imaginou tudo isso. Uma empresa que divide a sua memória em duas. Máquinas que fabricam o mundo que você vê. Uma inteligência artificial que castiga quem não obedece.", G,
     {"a": "trio_ficcao", "r": "ficcao"}),
    ("A ciência, por enquanto, fez só pedaços. Mas são pedaços reais.", G, {"a": "frase", "texto": "Pedaços reais."}),
    ("Nos próximos minutos, a gente vai abrir esses arquivos um por um. Separar o que já aconteceu do que ainda é só medo. E chegar numa conclusão desconfortável: o perigo talvez não seja o robô mau.", G,
     {"a": "arquivos_mesa"}),
    ("Guarde uma pergunta. Quem tem a chave?", P,
     {"a": "titulo", "texto": "Quem tem a chave?", "titulo": "SUA MENTE EM TERMOS DE USO"}),
  ]),
  ("contrato", "O contrato", [
    ("Imagine uma proposta de emprego com um benefício estranho. Ao sair do escritório, você esquece tudo o que aconteceu lá dentro. As cobranças ficam no trabalho. Os conflitos não vão para casa.", G,
     {"a": "escritorio"}),
    ("É a premissa da série Ruptura. Os funcionários da Lumon passam por uma cirurgia que divide a memória em duas. Lá dentro, eles não sabem quem são lá fora. Lá fora, não sabem o que fazem lá dentro.", G,
     {"a": "ruptura", "r": "ficcao", "fonte": "Ruptura (Severance) · Apple TV · 2022"}),
    ("Parece um alívio. Mas olhe o contrato com calma.", G, {"a": "frase", "texto": "Olhe o contrato com calma.", "r": "ficcao"}),
    ("Quem assinou foi a pessoa de fora. Quem trabalha, sofre e obedece é a de dentro. E a de dentro nunca concordou com nada. Ela já nasceu empregada.", G,
     {"a": "contrato", "r": "ficcao"}),
    ("É o problema do consentimento levado ao extremo. Como alguém aceita uma condição que nunca vai conseguir lembrar? E se recusar custasse o emprego, essa escolha seria livre?", P,
     {"a": "frase", "texto": "Essa escolha seria livre?", "r": "ficcao"}),
    ("Ruptura é ficção. Ninguém sabe dividir uma memória assim. Mas a ideia de que uma lembrança pode ficar trancada, e de que alguém pode guardar a chave, não é tão ficcional quanto parece.", G,
     {"a": "porta", "fase": "fechada"}),
  ]),
  ("trancada", "Memória trancada", [
    ("Comece pelo mais simples. Você já entrou num cômodo e esqueceu o que ia fazer lá?", G, {"a": "porta", "fase": "atravessa"}),
    ("Pesquisadores chamam isso de efeito da porta. Em dois mil e seis, um estudo mostrou que atravessar uma porta pode atrapalhar a lembrança do que você acabou de fazer.", G,
     {"a": "doc", "img": "radvansky2006", "revista": "Memory & Cognition", "ano": "2006", "titulo": "Walking through doorways causes forgetting", "autores": "Radvansky e Copeland", "r": "pesquisa"}),
    ("Uma explicação é que o cérebro organiza a vida em episódios, e a porta marca o fim de um. O efeito é pequeno e nem sempre aparece. Mas mostra uma coisa: lembrar é abrir um caminho. E o caminho pode falhar.", G,
     {"a": "episodios", "r": "pesquisa"}),
    ("Com o trauma, isso fica sério. Quem passa por uma violência pode não conseguir lembrar do que aconteceu. E, mesmo assim, o corpo reage. Um cheiro, um som, um lugar, e o medo volta inteiro, sem aviso.", P,
     {"a": "trauma"}),
    ("Em dois mil e quinze, a mesma equipe do MIT testou isso em camundongos com amnésia. As lembranças pareciam perdidas. Mas, quando os cientistas acenderam com luz os neurônios certos, a memória voltou.", G,
     {"a": "doc", "img": "ryan2015", "revista": "Science", "ano": "2015", "titulo": "Engram cells retain memory under retrograde amnesia", "autores": "Ryan, Roy, Pignatelli, Arons e Tonegawa", "r": "pesquisa"}),
    ("Ela não tinha sido apagada. Só estava sem acesso.", P, {"a": "frase", "texto": "Não apagada. Sem acesso."}),
    ("E já existem tentativas de mexer nessa porta em pessoas. Em alguns estudos, pacientes com estresse pós-traumático tomaram um remédio comum para pressão, o propranolol, antes de relembrar o trauma. A ideia é diminuir a carga emocional da lembrança.", G,
     {"a": "remedio", "r": "pesquisa"}),
    ("Um estudo de dois mil e dezoito teve resultado positivo. Outro, de dois mil e quinze, não conseguiu repetir um resultado anterior. A ciência ainda está discutindo.", G,
     {"a": "placar", "r": "pesquisa", "itens": [("2018", "Brunet e outros", "resultado positivo"), ("2015", "Wood e outros", "não repetiu o efeito")]}),
    ("Para quem sofre, isso pode ser uma libertação. Mas fica uma pergunta. Quem decide qual lembrança dói demais? O paciente? O médico? O empregador? O Estado?", P,
     {"a": "quem_decide", "itens": ["o paciente?", "o médico?", "o empregador?", "o Estado?"]}),
  ]),
  ("escrever", "Arquivo 1 · Escrever", [
    ("Arquivo um. Escrever.", G, {"a": "arquivo", "n": "1", "nome": "ESCREVER"}),
    ("Volte ao camundongo do começo. Cada vez que você vive alguma coisa, um grupo de neurônios se acende junto. Os cientistas chamam esse grupo de engrama. É o lugar físico de uma lembrança.", G,
     {"a": "neuronios", "r": "pesquisa", "legenda": "engrama"}),
    ("A equipe de Susumu Tonegawa, ganhador do Nobel, marcou os neurônios que se acendiam quando o camundongo explorava uma caixa tranquila. Esses neurônios foram modificados para responder à luz.", G,
     {"a": "doc", "img": "ramirez2013", "revista": "Science", "ano": "2013", "titulo": "Creating a False Memory in the Hippocampus", "autores": "Ramirez, Liu e outros · laboratório de Susumu Tonegawa", "r": "pesquisa"}),
    ("Depois, levaram o animal para outra caixa. Ali, ele levou um choque. E, no exato momento do choque, os cientistas acenderam a lembrança da primeira caixa.", G,
     {"a": "caixas", "r": "pesquisa"}),
    ("O cérebro juntou as duas coisas. De volta à caixa tranquila, o camundongo congelou. Tinha medo de um lugar onde nada tinha acontecido.", G,
     {"a": "camundongo", "estado": "medo", "r": "pesquisa"}),
    ("Segundo os pesquisadores, o cérebro usa o mesmo mecanismo para lembrar uma memória falsa e uma verdadeira. De dentro, não dá para saber a diferença.", P,
     {"a": "citacao", "texto": "Seja a memória falsa ou verdadeira, o mecanismo do cérebro para lembrá-la é o mesmo.", "fonte": "Susumu Tonegawa · MIT News, 2013 (tradução livre)"}),
    ("É um camundongo, modificado geneticamente, com uma fibra de luz implantada no cérebro. Ninguém fez isso numa pessoa, e não existe hoje forma de fazer.", G,
     {"a": "camundongo", "estado": "calma", "r": "pesquisa", "sobre": "CAMUNDONGO MODIFICADO · FIBRA ÓPTICA NO CÉREBRO"}),
    ("Mas o experimento prova uma coisa que assusta. A memória não é um arquivo lacrado. Ela pode ser editada por fora. E se uma lembrança pode ser escrita por outra pessoa, como você confia nas suas?", P,
     {"a": "frase", "texto": "Como você confia nas suas?"}),
  ]),
  ("mapear", "Arquivo 2 · Mapear", [
    ("Arquivo dois. Mapear.", G, {"a": "arquivo", "n": "2", "nome": "MAPEAR"}),
    ("Para escrever numa mente, primeiro é preciso saber onde está cada coisa. Então os cientistas começaram por um cérebro pequeno. O de uma mosca.", G,
     {"a": "mosca", "r": "pesquisa"}),
    ("A mosca-da-fruta tem um cérebro menor que uma semente de papoula. Em dois mil e vinte e quatro, o projeto FlyWire publicou o mapa completo dele: cento e trinta e nove mil neurônios, e cerca de cinquenta milhões de conexões.", G,
     {"a": "conectoma", "r": "pesquisa", "num": "139.255", "leg": "neurônios", "num2": "~50 milhões", "leg2": "conexões", "fonte": "Dorkenwald e outros · Nature · 2024"}),
    ("O cérebro foi fatiado em camadas finíssimas e fotografado num microscópio eletrônico. Uma inteligência artificial traçou cada neurônio. E centenas de pesquisadores e voluntários corrigiram os erros, como num jogo.", G,
     {"a": "fatias", "r": "pesquisa"}),
    ("Foram trinta e três anos de trabalho humano, somados. Sem a inteligência artificial, segundo um dos líderes do projeto, seriam quase cinquenta mil.", G,
     {"a": "comparacao", "r": "pesquisa", "a1": "33 anos", "l1": "com IA", "a2": "~50.000 anos", "l2": "sem IA", "fonte": "Princeton University · 2024"}),
    ("Aí veio o passo seguinte. Outra equipe pegou esse mapa e colocou para funcionar num computador. Um cérebro de mosca, simulado.", G,
     {"a": "conectoma", "modo": "simula", "r": "pesquisa"}),
    ("Quando ativaram, na simulação, os neurônios que sentem açúcar, o modelo previu quais neurônios fariam a mosca começar a comer. Depois, testaram em moscas de verdade. E várias previsões se confirmaram.", G,
     {"a": "doc", "img": "shiu2024", "revista": "Nature", "ano": "2024", "titulo": "A Drosophila computational brain model reveals sensorimotor processing", "autores": "Shiu e outros", "r": "pesquisa"}),
    ("Repare no que isso quer dizer. Um cérebro virou um mapa. E o mapa, rodando num computador, começou a se comportar como um cérebro.", P,
     {"a": "frase", "texto": "O mapa começou a se comportar como um cérebro."}),
    ("É uma mosca, e o modelo é bem simplificado. Mapear conexões não é copiar uma consciência. Mas guarde essa imagem: um cérebro rodando dentro de um computador. Ela vai voltar.", G,
     {"a": "conectoma", "r": "pesquisa"}),
  ]),
  ("ler", "Arquivo 3 · Ler", [
    ("Arquivo três. Ler.", G, {"a": "arquivo", "n": "3", "nome": "LER"}),
    ("Mapear o cérebro de uma mosca é uma coisa. Ler um cérebro humano vivo é outra.", G, {"a": "frase", "texto": "Ler um cérebro vivo."}),
    ("Dois mil e seis, Reino Unido. Uma mulher de vinte e três anos sofre um acidente de carro. Cinco meses depois, ela dorme e acorda, mas não responde a nada. O diagnóstico é estado vegetativo.", G,
     {"a": "hospital", "local": "REINO UNIDO · 2005", "r": "caso"}),
    ("O neurocientista Adrian Owen coloca essa mulher numa máquina de ressonância e pede: imagine que você está jogando tênis.", G,
     {"a": "doc", "img": "owen2006", "revista": "Science", "ano": "2006", "titulo": "Detecting Awareness in the Vegetative State", "autores": "Owen e outros", "r": "caso"}),
    ("O cérebro dela responde. Do mesmo jeito que o de pessoas saudáveis. Ela estava ouvindo. Presa dentro do próprio corpo, sem conseguir avisar.", P,
     {"a": "cerebros", "r": "caso"}),
    ("Houve contestação, e a discussão durou anos. Em dois mil e vinte e quatro, um estudo com duzentos e quarenta e um pacientes que não respondiam a nada encontrou sinais de consciência em um de cada quatro.", G,
     {"a": "quatro", "r": "pesquisa", "fonte": "60 de 241 (25%) · Bodien e outros · NEJM · 2024"}),
    ("Para essas pessoas, a única porta para fora da própria cabeça era uma máquina.", P, {"a": "porta", "fase": "fresta"}),
    ("E máquinas assim já estão devolvendo autonomia. Em dois mil e vinte e quatro, a Neuralink mostrou um participante com paralisia movendo um cursor só com sinais do cérebro, por um implante.", G,
     {"a": "cursor", "r": "caso", "fonte": "Neuralink · demonstração da empresa · 2024", "calmo": True}),
    ("Sem cirurgia, uma equipe da Universidade do Texas usou ressonância e um modelo de linguagem para reconstruir a ideia geral de histórias que voluntários ouviam ou imaginavam.", G,
     {"a": "doc", "img": "tang2023", "revista": "Nature Neuroscience", "ano": "2023", "titulo": "Semantic reconstruction of continuous language from non-invasive brain recordings", "autores": "Tang, LeBel, Jain e Huth", "r": "pesquisa", "calmo": True}),
    ("Não era palavra por palavra. Cada voluntário treinou o sistema por cerca de dezesseis horas. E, quando resistia pensando em outra coisa, o sistema falhava.", G,
     {"a": "porta", "fase": "fresta"}),
    ("Hoje, para ler a sua mente, a máquina precisa da sua cooperação.", P, {"a": "frase", "texto": "Hoje, ela precisa da sua cooperação.", "mundo": "papel"}),
    ("Hoje.", G, {"a": "frase", "texto": "Hoje."}),
    ("E quando não precisar mais? Quem guarda esses dados? Quem decide o que eles significam?", P, {"a": "servidores"}),
  ]),
  ("influenciar", "Arquivo 4 · Influenciar", [
    ("Arquivo quatro. Influenciar.", G, {"a": "arquivo", "n": "4", "nome": "INFLUENCIAR"}),
    ("Até aqui, tudo exigiu um laboratório, um implante ou uma máquina de ressonância. O próximo caso exigiu só um feed.", G, {"a": "frase", "texto": "Só um feed."}),
    ("Janeiro de dois mil e doze. Durante uma semana, o Facebook mudou o que seiscentas e oitenta e nove mil pessoas viam. Para umas, menos publicações felizes. Para outras, menos publicações tristes.", G,
     {"a": "feeds", "r": "caso", "numero": "689.003", "data": "JANEIRO DE 2012"}),
    ("Ninguém foi avisado.", G, {"a": "frase", "texto": "Ninguém foi avisado.", "r": "caso"}),
    ("Depois, os pesquisadores mediram o que essas pessoas escreveram. Quem viu menos coisa boa passou a escrever um pouco menos de palavras positivas, e um pouco mais de negativas.", G,
     {"a": "doc", "img": "kramer2014", "revista": "PNAS", "ano": "2014", "titulo": "Experimental evidence of massive-scale emotional contagion through social networks", "autores": "Kramer, Guillory e Hancock", "r": "pesquisa"}),
    ("O efeito foi pequeno. Mas o tamanho nunca foi o problema. O problema é que ninguém perguntou. A justificativa foi a política de uso de dados que todo mundo aceita ao criar a conta. Aquele texto que ninguém lê.", G,
     {"a": "termos", "r": "caso"}),
    ("O estudo saiu em dois mil e catorze. Duas semanas depois, a própria revista publicou uma nota de preocupação sobre o consentimento dos participantes.", P,
     {"a": "doc", "img": "pnas_concern", "revista": "PNAS", "ano": "julho de 2014", "titulo": "Editorial Expression of Concern", "autores": "informed consent · opt out", "r": "caso", "carimbo": "NOTA DE PREOCUPAÇÃO"}),
    ("Repare. Nenhum chip. Nenhuma luz no cérebro. Só alguém que controlava o que você via, e media como você reagia.", G, {"a": "escritorio", "tela": "feed"}),
    ("Quem controla a tela não precisa entrar na sua cabeça. Ele escolhe o mundo que chega até ela.", P, {"a": "frase", "texto": "Ele escolhe o mundo que chega até ela."}),
  ]),
  ("realidade", "A realidade", [
    ("E se o controle fosse total? Se alguém escolhesse não só o feed, mas o mundo inteiro?", G, {"a": "simulacao", "fase": "mundo"}),
    ("Em mil novecentos e noventa e nove, o filme Matrix levou essa ideia ao limite. A humanidade vive dentro de uma simulação, controlada por máquinas. Ninguém percebe, porque tudo o que se vê, se toca e se sente é fabricado.", G,
     {"a": "matrix", "r": "ficcao", "fonte": "The Matrix · Warner Bros. · 1999"}),
    ("Parece só cinema. Mas, em dois mil e três, o filósofo Nick Bostrom publicou um argumento que tirou o sono de muita gente.", G,
     {"a": "doc", "img": "bostrom2003", "revista": "Philosophical Quarterly", "ano": "2003", "titulo": "Are You Living in a Computer Simulation?", "autores": "Nick Bostrom", "r": "argumento"}),
    ("Ele começa assim. Uma civilização avançada o bastante conseguiria simular mentes inteiras, como a gente viu com a mosca, só que numa escala muito maior. E poderia rodar milhões de simulações dos próprios antepassados.", G,
     {"a": "multiplica", "r": "argumento"}),
    ("Então, pelo menos uma de três coisas é verdade. Um: quase nenhuma civilização chega a esse ponto. Dois: as que chegam não têm interesse em fazer essas simulações. Três: quase todas as mentes como a sua estão dentro de uma simulação.", G,
     {"a": "trilema", "r": "argumento", "itens": ["Quase nenhuma civilização chega lá.", "As que chegam não fazem simulações.", "Quase todas as mentes como a sua são simuladas."]}),
    ("Se for a terceira, a conta é simples. Haveria muito mais mentes simuladas do que reais. E a chance de você ser uma das reais seria minúscula.", P,
     {"a": "multiplica", "fase": "uma", "r": "argumento"}),
    ("Você pode estar dentro de uma simulação agora mesmo. E não teria como perceber.", P, {"a": "simulacao", "fase": "revela"}),
    ("Mas atenção ao que o argumento não diz. Ele não prova que vivemos numa simulação. Ele depende de uma aposta enorme: a de que um computador consegue produzir consciência. E ninguém sabe se isso é possível.", G,
     {"a": "simulacao", "fase": "mundo", "r": "argumento"}),
    ("O que ele faz é outra coisa. Ele mostra que, se alguém controlar tudo o que você percebe, você não tem como saber. É a mesma pergunta do Facebook, só que do tamanho do universo.", P,
     {"a": "frase", "texto": "A mesma pergunta, do tamanho do universo."}),
  ]),
  ("robo", "O robô mau", [
    ("Agora, a história mais estranha deste vídeo.", G, {"a": "frase", "texto": "A história mais estranha."}),
    ("Em dois mil e dez, num fórum da internet chamado LessWrong, um usuário chamado Roko publicou um experimento mental. Imagine uma inteligência artificial do futuro, poderosa e decidida a existir. Ela poderia castigar todo mundo que soube que ela era possível e não ajudou a criá-la.", G,
     {"a": "forum", "r": "argumento"}),
    ("E você, agora, já sabe.", P, {"a": "basilisco"}),
    ("Esse é o Basilisco de Roko. Como o monstro da lenda, que mata quem olha para ele, a ideia supostamente faria mal a quem a conhece.", G,
     {"a": "basilisco", "texto": "O Basilisco de Roko", "r": "argumento"}),
    ("O fundador do fórum apagou o post e proibiu o assunto por cinco anos. O efeito foi o contrário: a proibição espalhou a história pela internet.", G,
     {"a": "proibido", "r": "caso"}),
    ("A ideia não se sustenta. Depende de suposições frágeis sobre o que uma máquina futura iria querer, e foi rejeitada até por gente do próprio fórum. Não existe nenhuma evidência dessa ameaça.", G,
     {"a": "basilisco", "r": "argumento"}),
    ("Mas repare no que ela faz. Ela usa o medo de um robô mau para pressionar pessoas reais a agir hoje.", P, {"a": "frase", "texto": "O medo como ferramenta."}),
    ("O cientista da computação Giancarlo Guizzardi, que se formou aqui na UFES, tem um livro com um título que resume isso: Quem tem medo do robô mau? A proposta dele é separar o que a inteligência artificial realmente faz do que a gente imagina que ela faça.", G,
     {"a": "livro", "r": "argumento"}),
    ("E, quando a gente faz essa separação, a imagem muda. Em nenhum dos casos deste vídeo havia uma máquina malvada. Havia laboratórios, empresas e plataformas. Pessoas que decidiram o que testar, o que mostrar e o que guardar.", G,
     {"a": "pessoas"}),
    ("O robô mau é uma distração. Quem segura a chave tem nome, endereço e modelo de negócio.", P,
     {"a": "frase", "texto": "Quem segura a chave tem nome, endereço e modelo de negócio."}),
  ]),
  ("fechamento", "Fechamento", [
    ("Então, quem tem a chave?", G, {"a": "fechadura", "fase": "uma"}),
    ("Escrever uma memória. Mapear um cérebro. Ler o que ele pensa. Escolher o que ele vê. Em todos os casos, a tecnologia chegou antes da pergunta. Primeiro alguém consegue. Depois alguém pergunta se podia.", G,
     {"a": "fechadura", "fase": "quatro"}),
    ("Por isso, alguns pesquisadores defendem direitos novos para esta época: privacidade mental, liberdade cognitiva, integridade da mente. O direito de ninguém entrar na sua cabeça sem você saber.", G,
     {"a": "direitos", "r": "argumento", "fonte": "Ienca e Andorno · 2017"}),
    ("Nós defendemos o mesmo. Consentimento que dê para entender, e não um termo que ninguém lê. Limites para o uso de dados do cérebro. Fiscalização independente. E o direito de dizer não, sem perder o emprego por isso.", P,
     {"a": "lista", "itens": ["Consentimento que dá para entender", "Limites para dados do cérebro", "Fiscalização independente", "Direito de dizer não"], "r": "argumento"}),
    ("Agora, uma última coisa.", G, {"a": "onda"}),
    ("A voz que contou essa história não existe. Ela foi gerada por inteligência artificial. Você ouviu essa voz esse tempo todo e, provavelmente, confiou nela.", G,
     {"a": "onda", "texto": "Esta voz foi gerada por inteligência artificial."}),
    ("Então não confie. Confira as fontes. Estão todas na descrição.", P, {"a": "onda", "texto": "Confira as fontes."}),
    ("Lembra do camundongo? Ele nunca soube que aquela lembrança tinha sido escrita por outra pessoa. Ele só sentia medo.", G,
     {"a": "camundongo", "estado": "vazia"}),
    ("No caso dele, é fácil dizer quem tinha a chave. Os cientistas. No seu caso, a pergunta ainda está aberta.", P,
     {"a": "frase", "texto": "No seu caso, ainda está aberta."}),
    ("Quem está do outro lado da porta?", 3.0,
     {"a": "porta", "fase": "fecha", "texto": "Quem está do outro lado da porta?"}),
    # final com falha: voz e clipe feitos à parte (fim_glitch.py, glitch.py), não passam pelo tts.py
    ("Você deve ter percebido as falhas na minha voz. Mas será que isso é um problema do meu modelo... ou a sua simulação está falhando?", 2.0,
     {"a": "glitch"}),
  ]),
]


def texto_falado(t):
    for k in sorted(PRONUNCIA, key=len, reverse=True):
        t = t.replace(k, PRONUNCIA[k])
    return t


def gerar_md(caminho):
    """Versão legível do roteiro para o grupo."""
    out = ["# Sua mente em termos de uso: roteiro v2\n",
           "Narração exatamente como vai para a voz. Em itálico, o que aparece na tela.\n"]
    for _, titulo, segs in CENAS:
        out.append(f"\n## {titulo}\n")
        for texto, pausa, vis in segs:
            tela = vis.get("texto") or vis.get("titulo") or vis.get("img") or vis["a"]
            out.append(f"*[{vis['a']}: {tela}]*\n\n{texto}{' [pausa]' if pausa >= 1.4 else ''}\n")
    open(caminho, "w").write("\n".join(out))


if __name__ == "__main__":
    n = sum(len(t.split()) for _, _, segs in CENAS for t, _, _ in segs)
    seg = sum(len(s) for _, _, s in CENAS)
    assert 1850 < n < 2250, n  # ~15 min a ~140 palavras/min com pausas
    gerar_md("../roteiro-v2.md")
    print(n, "palavras,", seg, "segmentos, ~", round(n / 140, 1), "min")
