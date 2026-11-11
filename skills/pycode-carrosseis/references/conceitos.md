# Catálogo de conceitos de carrossel

Cada conceito abaixo já foi usado em posts reais e aprovado pelo nível de design, de ideia e de progressão. Parta de um deles ou crie um novo no mesmo nível: um cenário que o público reconhece, um objeto herói grande por slide, avanço de slide a slide e pelo menos um slide em vídeo curto.

Os quatro primeiros têm exemplo completo em `examples/` (copie com `pycode carousel new pasta --example <nome>`). Os outros têm a receita para montar.

O que todos têm em comum:

- Um conceito do primeiro ao último slide. Trocar de metáfora no meio confunde.
- Um objeto herói por slide, grande, com luz e sombra coerentes com o fundo. O texto fica numa área limpa, com contraste de 4,5:1 medido.
- Prova que o público reconhece dentro da cena: código rodado, saída real, comando conferido, número com fonte.
- Âncoras discretas da marca: nome ou @ num canto e o contador N/T.
- Texto, números, comandos e interfaces renderizados por código. O gerador de imagens, quando existe, faz só cena e objeto, sem texto.

## Cartas colecionáveis (`examples/cartas`)

- **Quando usar:** lista de ferramentas, módulos, bibliotecas, comandos ou recursos. É o formato que mais puxa salvamento.
- **Estrutura:** capa com o baralho; uma carta por item (nome, tipo, arte, uma frase de uso, comando ou trecho com a saída real, número de coleção 01/05); slide "como usar" que liga as cartas a um script; fechamento com o leque aberto.
- **Objeto herói:** a carta, com moldura holográfica (gradiente cônico dos tokens) e uma arte desenhada em SVG que explica o item (árvore de pastas para `pathlib`, barras de contagem para `Counter`, calendário com o dia 29 para `datetime`). A carta principal é dourada.
- **Slide em vídeo:** capa. O baralho fechado (pôster) abre em leque, as cartas viram uma a uma e a dourada vira por último, com brilho.
- **Cuidados:** comando em fonte mono com ligaduras desligadas e quebra só entre tokens; repita o comando completo na legenda. Nas cartas pequenas do leque, use um emblema simples em vez da arte completa, e alinhe o nome para o lado que fica visível. Logos de marca só baixados por `pycode icon` no projeto de quem publica.

## Mapa do metrô (`examples/metro`)

- **Quando usar:** trilha de aprendizado, roteiro, ordem de etapas, fluxo de um sistema (requisição, deploy, pipeline). Puxa salvamento de quem está começando.
- **Estrutura:** capa com o trem chegando; slide 2 com o mapa inteiro da linha; uma estação por etapa (faixa do mapa no topo com a estação atual acesa, placa da estação, texto, objeto da etapa); fechamento na estação terminal.
- **Objeto herói:** o objeto de cada estação (bilhete com o endereço quebrado em partes, painel de partidas com domínio e IP, rack do servidor com a linha da requisição, cilindros do banco com a consulta, envelope com o status). A linha do metrô corre no leito dos trilhos e passa de um slide para o outro na mesma altura.
- **Slide em vídeo:** capa. O trem sai do túnel, desacelera, para, e as estações da faixa acendem uma a uma.
- **Cuidados:** a faixa do mapa e as placas são desenhadas por código, nunca pelo gerador. Nomes de estação curtos (cabem 5 na faixa a 24 px). Dado ilustrativo (IP de documentação, como 203.0.113.10) aparece dito como exemplo no texto.

## Níveis (`examples/niveis`)

- **Quando usar:** escada de maturidade, evolução, diagnóstico ("em qual nível você está?"). A capa faz a pessoa se localizar e mostra os níveis acima dela.
- **Estrutura:** capa com a escada; um slide por nível com numeral gigante, rótulo "NÍVEL N DE 5", título curto, texto e medidor de 5 segmentos; fechamento com todos os degraus acesos.
- **Objeto herói:** a escada isométrica com o degrau atual aceso (os de baixo em outra cor) e um artefato do nível flutuando ao lado, ligado ao degrau por uma linha: a janela com o botão clicado, o terminal com o `print`, o arquivo com `assert`, o teste do pytest, a esteira de integração contínua.
- **Slide em vídeo:** capa. Os degraus acendem de baixo para cima junto com o medidor; o quadro 0 fica em luz de espera, porque a escada toda apagada é um pôster fraco.
- **Cuidados:** a pergunta da capa é gancho, não pedido de comentário; o único pedido de ação fica no fim. Numeral em canvas (`measureText`) para alinhar a linha de base; título do nível com `white-space: nowrap`.

## Fliperama (`examples/fliperama`)

- **Quando usar:** quiz, desafio, pegadinha de código, conteúdo leve. A reação é orgulho de acertar e vontade de testar alguém.
- **Estrutura:** capa com o gabinete e a pergunta na tela; uma fase por slide (pergunta curta, código numa tela de CRT, opções A a D, barra de vida); placar com o veredito no slide seguinte às perguntas; tela de continue com o pedido de ação.
- **Objeto herói:** o cenário em pixel art desenhado num canvas de 180x225 ampliado 6x sem suavização (céu, prédios, chão de tijolos, cobras, moedas, troféu, gabinete).
- **Slide em vídeo:** capa. PRESS START pisca, a moeda cai no moedeiro, a porta acende e a tela pisca.
- **Cuidados:** rode cada trecho no Python e confira a resposta de cada opção (`run: python` e `quiz.answer` no `slides.json`). O veredito fica num slide próprio, depois das perguntas. Veja as armadilhas de fonte pixel em `tipografia-e-codigo.md`.

## Cabine ou painel imersivo

- **Quando usar:** tema sério (decisão de compra, segurança, qualidade, checklist). Puxa salvamento e envio.
- **Estrutura:** a mesma cabine (ou sala de controle) em planos diferentes, um item do checklist por slide; um slide de alerta com luz vermelha; fechamento com tudo em verde.
- **Objeto herói:** sem gerador, um painel de instrumentos desenhado em SVG (mostradores com ponteiro, interruptores, LEDs, telas com texto renderizado). Com gerador, a cabine fotorreal com as telas em magenta, aplicadas com `pycode carousel compose`.
- **Slide em vídeo:** a cabine liga em sequência (LEDs por faixa e por posição), ou o checklist é conferido item a item. O quadro 0 fica em luz de espera.
- **Cuidados:** só dados que a fonte confirma. Prova com pessoas (prints de alunos, mensagens) precisa de autorização e de borrar nomes e contatos.

## Um dia em horários

- **Quando usar:** mostrar uma rotina ao longo do tempo (o que um agente, um sistema ou uma equipe faz em cada horário).
- **Estrutura:** um horário por slide, em ordem; o cenário é o mesmo e muda a luz (madrugada, manhã, tarde, noite).
- **Objeto herói:** um relógio de placas (flip clock) desenhado em código, com cartões, vinco e sombra; a tela do cenário mostra o que aconteceu naquela hora.
- **Slide em vídeo:** capa com as placas virando e a luz passando da noite para o dia.
- **Cuidados:** os horários vêm da rotina que roda de fato (agenda, cron, log), não da memória. Nenhum dado pessoal ou número de negócio legível nas telas.

## Abrindo a caixa

- **Quando usar:** apresentar o que vem num kit, pacote ou entrega, revelando item a item.
- **Estrutura:** a mesma maleta ou caixa em todos os slides, um compartimento aberto por slide, com o objeto de cada item; fechamento com a caixa completa.
- **Objeto herói:** sem gerador, uma caixa isométrica em SVG com tampa, espuma recortada e objetos simples (cartucho, rolo, chave); com gerador, a maleta fotorreal gerada uma vez e editada para cada compartimento.
- **Slide em vídeo:** capa com os fechos abrindo e a luz saindo de dentro.
- **Cuidados:** a caixa precisa continuar a mesma de slide em slide (veja consistência de cena em `gerador-de-imagens.md`).

## Planta que vira sistema (linha contínua)

- **Quando usar:** explicar a construção de algo em etapas (um sistema, uma arquitetura), com sensação de percurso.
- **Estrutura:** papel de planta com grade; um traço sai cortado na borda direita de cada slide e continua, na mesma altura, na borda esquerda do seguinte.
- **Objeto herói:** desenhos técnicos por código (cotas, isométricos, carimbos) ao longo do traço.
- **Slide em vídeo:** o traço se desenha (stroke-dashoffset) e a planta acende.
- **Cuidados:** declare `rail.in` e `rail.out` de cada slide no `slides.json`; o QA mede as emendas pelos pixels da última coluna de um slide e da primeira do seguinte. No vídeo, o traço precisa estar completo no último quadro para o pôster e o fim encaixarem.

## O que não fazer (reprovado em rodadas reais)

- **Cartão de texto sobre fundo liso ou desfocado, ou fundo liso só com numeral.** Não tem objeto, nada prende o olho. Sério e limpo mudam o tom, nunca tiram o objeto herói.
- **Metáfora com cara de piada para tema sério** (tabela nutricional para escolher um curso). Trivializa a decisão.
- **Desafio carregado:** editor de código com contador, etiquetas, sublinhados e recortes de tela ao lado, ou uma camada de metáfora (folha de prova, carimbos) entre a pessoa e o desafio. "Encontre o erro" precisa ser entendido em dois segundos: um artefato por slide, uma marcação só, texto numa área limpa.
- **Dois pedidos de ação no mesmo carrossel** ("comenta o número" no meio e "salva" no fim). Dividem a resposta; o do meio sai.
- **Grade de cartões iguais, gradiente roxo e azul genérico, emoji como ícone, rótulo em caixa alta acima de cada título.** Dão cara de template gerado.
- **Texto, comando ou número saído do gerador de imagens.** O modelo troca letras; tudo que precisa ser exato é renderizado por código.
