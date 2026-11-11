# Método: da pauta ao pacote pronto para publicar

Este é o caminho completo de um carrossel. Cada etapa tem um entregável, e a próxima só começa quando a anterior foi aprovada por quem pediu o post.

## 1. Pauta

Comece pelo que a pessoa que publica sabe e usa. Fato técnico entra com fonte (documentação oficial, código rodado, saída real); uso pessoal de ferramenta só entra se a pessoa confirmar. Se o post fala de um comando, rode o comando. Se fala de uma saída do Python, rode o trecho e copie a saída.

Uma boa pauta de carrossel cabe numa frase com começo, meio e fim: "a viagem de uma requisição, do endereço até a página aberta", "os cinco níveis de quem testa o próprio código", "três pegadinhas de Python para testar quem segue o perfil".

## 2. Conceito visual

Escolha um conceito em `conceitos.md` ou crie um novo no mesmo nível. O conceito é um objeto ou cenário do mundo real que o público reconhece e que sustenta o post inteiro: um baralho, uma linha de metrô, uma escada, um fliperama, uma cabine, uma maleta. Cada slide avança dentro desse cenário (uma carta a mais, uma estação a mais, um degrau a mais), e é esse avanço que faz a pessoa arrastar para o lado.

O tom do conceito acompanha o assunto. Decisão séria pede metáfora séria (cabine, checklist de pré-voo); quiz e conteúdo leve aceitam jogo. Uma metáfora com cara de piada para um tema sério trivializa a decisão.

## 3. Roteiro com o texto final

O roteiro já sai com o texto final de cada slide, escrito como vai aparecer. Descrever a estrutura com termos de planejamento ("slide de gancho", "diagrama em camadas") não serve para aprovar nada. Regras de escrita em `escrita.md`.

Estrutura que funciona na maioria dos posts:

1. **Capa**: o gancho que para a rolagem, até ~20 palavras, com o objeto herói grande. Pode ser uma pergunta que faz a pessoa se localizar ("em qual destes níveis você está?"), sem pedir comentário.
2. **Slide 2, a segunda capa**: o Instagram costuma reapresentar um carrossel não arrastado já mostrando a segunda mídia. O slide 2 precisa dizer sozinho do que o post trata. Teste: esconda a capa e leia o slide 2.
3. **Desenvolvimento**: uma ideia por slide, até ~35 palavras, com um exemplo concreto ou uma prova (código rodado, comando, número com fonte).
4. **Como usar**: antes do fim, um slide que junta as peças numa aplicação transforma lista em uso.
5. **Fechamento**: o único pedido de ação do carrossel.

Para cada slide, anote também o objeto herói e, no slide em vídeo, o que se move. Confira se a descrição visual combina com o papel do texto: o slide marcado como vídeo é o que a animação descreve.

## 4. Aprovação da capa e do slide 2

Antes de produzir os outros slides, monte só a capa e o slide 2 e mostre. Eles definem tipografia, escala do objeto herói, paleta e caminho de leitura. Mudar isso depois de oito slides prontos custa o retrabalho de todos.

## 5. Produção

```bash
pycode carousel new pasta --title "..." [--style slug] [--slides 8]     # modelo
pycode carousel new pasta --example metro                               # ou um exemplo pronto
```

- `slides.json` é a fonte única do texto. O HTML só tem estrutura e objetos.
- `js/scene.js` desenha o conceito (SVG, canvas, HTML) com `Carousel.onSlide` e anima o slide em vídeo com `Carousel.animate`.
- `css/scene.css` usa só os tokens do estilo (`var(--bg)`, `var(--accent)` e os demais) e `color-mix()` para tons derivados; assim o mesmo carrossel funciona em qualquer estilo do `pycode-design`.
- Com gerador de imagens, as cenas entram como fundo ou objeto herói, sem texto; veja `gerador-de-imagens.md`.

```bash
pycode carousel render pasta                     # out/slide-01.png ... em 1080x1350
pycode carousel video pasta --slide 1            # out/slide-01.mp4 + pôster
```

## 6. QA

```bash
pycode carousel qa pasta
```

O QA reprova (código de saída 1) quando falta algo básico: tamanho, palavras, contraste medido no fundo real, margem segura, texto cortado ou sobreposto, fonte mínima, fonte sem arquivo local, código diferente da fonte ou com saída falsa, CTA fora do último slide, emenda do trilho desalinhada, vídeo sem BT.709 ou sem faststart. Depois do QA mecânico vem a revisão por visão, slide a slide, com estas perguntas:

- Para a rolagem só pela imagem, sem ler o texto?
- Está carregado (molduras, etiquetas e contadores disputando atenção)?
- Algum objeto tem cara de colado (luz, sombra e escala incoerentes com o resto)?
- O texto se lê no celular, numa passada de olho?

Slide que falha volta para a produção. Cartão de texto sobre fundo liso reprova sempre.

## 7. Prévia

```bash
pycode carousel caption pasta      # esqueleto de legenda.md; o texto final é seu
pycode carousel preview pasta      # preview.html: o post no celular, com arrasto
pycode serve pasta                 # abra /preview.html
```

Mande a prévia para aprovação. Ela mostra o carrossel como no feed (contador, pontos, vídeo sem som até tocar) e a folha com todos os slides.

## 8. Entrega

```bash
pycode carousel pack pasta
```

O pacote só sai com o QA aprovado e a legenda final (sem marcadores). Ele leva os slides numerados, os vídeos, os pôsteres, a legenda, a folha de contato, as licenças de som e o relatório do QA. A publicação é manual, pelo app; veja `stories-e-publicacao.md`.

## Como propor ideias

Quando pedirem "me manda N ideias de carrossel", entregue cada ideia já pronta para aprovar:

- **Título** do post.
- **Conceito visual**: o cenário, o objeto herói de cada slide e qual slide vira vídeo (e o que se move nele).
- **Por que prende**, em uma ou duas frases sobre a reação concreta (vontade de salvar a lista, orgulho de acertar o quiz, reconhecer o próprio nível).
- **Slides numerados com o texto final**, capa até ~20 palavras e os demais até ~35, com o CTA só no último.

Exemplo curto de formato:

> **A viagem de uma requisição** · mapa do metrô: cada etapa é uma estação, com a faixa do mapa no topo e a linha correndo de um slide para o outro; a capa em vídeo mostra o trem chegando enquanto as estações acendem. Prende porque a pessoa quer ver a próxima estação e salva o mapa para estudar.
> 1. A viagem de uma requisição, do endereço que você digita até a página aberta.
> 2. Toda vez que você abre um site, a requisição faz a mesma viagem de cinco estações e volta com a página pronta pro navegador.
> 3. (uma estação por slide, até o fechamento com o único pedido de ação)

Recomende por onde começar e ofereça montar a capa e o slide 2 para aprovação.
