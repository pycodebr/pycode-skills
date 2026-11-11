---
version: 1.0.0
name: Orbital
slug: orbital
description: 'Marinho quase preto, dourado e luz ciano, com objetos claros de papel: emblema em órbita, calendário, ingresso com canhoto e acervo em camadas. Tratamento premium e calmo para páginas, aulas
  e convites.'
mode: dark
fonts:
- geist
- geist-mono
best_for:
- page
- deck
- carousel
colors:
  bg: '#03090e'
  bg-2: '#071722'
  surface: '#0e283a'
  surface-2: '#153b50'
  text: '#f3f9fc'
  muted: '#b9cbd6'
  line: '#2a576f'
  accent: '#edc580'
  accent-2: '#7dd3fc'
  accent-ink: '#302515'
  paper: '#f2f5ef'
  paper-ink: '#102836'
  danger: '#ff7a70'
  ok: '#7be0a6'
  warn: '#f9e6bd'
  gold-light: '#f9e6bd'
  gold-surface: '#edcf93'
typography:
  display:
    fontFamily: Geist
    fontWeight: 400
    letterSpacing: -0.05em
  body:
    fontFamily: Geist
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: Geist Mono
    fontWeight: 400
rounded:
  base: 9px
  large: 20px
elevation:
  shadow: 0 24px 60px rgba(0, 0, 0, .45)
  glow: 0 0 0 1px rgba(125, 211, 252, .18), 0 0 48px rgba(125, 211, 252, .16)
tokens: tokens.css
---

# Orbital

## Visão geral

Orbital é um estilo escuro e calmo: fundo marinho quase preto, um dourado usado com economia, luz ciano nas linhas e objetos claros de papel que parecem coisas que a pessoa poderia segurar. O conceito é o de um ciclo em órbita: encontros que se repetem, um acervo que cresce e um centro (a turma, o produto, o tema) que organiza tudo em volta.

Use para páginas de inscrição de ciclos de aulas, convites, programas de mentoria, apresentações de abertura e carrosséis sobre o que a pessoa recebe. Funciona bem quando o conteúdo tem datas, entregas e um conjunto de materiais. Evite para conteúdo muito técnico e denso (prefira `terminal` ou `caderno`) e para temas lúdicos (prefira `fliperama` ou `colagem`).

## Cores

- `--bg` (#03090e) é o fundo de todas as cenas. Ele recebe um brilho radial localizado (`#12324866`) perto do objeto herói, nunca um degradê de ponta a ponta.
- `--bg-2` e `--surface` criam degraus de profundidade: faixas alternadas, cartões escuros e o fundo dos slides.
- `--accent` (dourado) marca só a ação principal, o destaque de uma palavra no título e a placa de preço ou de benefício. Se o dourado aparece em mais de três lugares na mesma tela, ele deixa de significar alguma coisa.
- `--accent-2` (ciano) desenha órbitas, a rede da constelação, sublinhados de link e informações auxiliares.
- `--paper` e `--paper-ink` são exclusivos dos objetos de papel: calendário, ingresso e acervo.
- Extras: `--orbital-gold-gradient` (botão principal e placa dourada), `--orbital-paper-gradient` (papel com leve reflexo azul), `--orbital-gold-light` (contorno do botão e avisos) e `--orbital-grid` (módulo de 58 px da grade atmosférica).

## Tipografia

Geist em peso 400 para tudo que é título, com espaçamento negativo (`--tracking-display: -0.05em`). O peso leve é a assinatura do estilo: títulos pesados aqui parecem anúncio. Geist Mono aparece em rótulos funcionais, números de calendário e informações discretas.

| Nível | Tamanho | Peso | Observação |
|---|---|---|---|
| h1 | `clamp(43px, 5.4vw, 76px)` | 400 | linha de 1,02 |
| h2 | `clamp(30px, 4.2vw, 58px)` | 400 | no máximo 18 caracteres por linha |
| h3 de objeto | 22 a 25 px | 400 | tracking de -0.045em |
| corpo | 16 a 18 px | 400 | linha de 1,65 a 1,7 |
| rótulo | 12 a 13 px mono | 400 | minúsculas, sem caixa alta decorativa |

Reduza o texto antes de reduzir a fonte. No celular, o h1 continua acima de 42 px.

## Superfícies e texturas

- Grade atmosférica de 58 px com `opacity: .18`, recortada por `mask-image` radial perto do objeto herói. Ela some nas bordas.
- Cartões escuros com borda de 1 px em `--line` e, quando premium, base `linear-gradient(145deg, #17384a, #07141e 75%)`.
- Papel claro com `--orbital-paper-gradient`, raio de 12 a 16 px e sombra estática (`--shadow`). No celular, tire as sombras grandes e mantenha forma e contorno.
- Profundidade vem de camadas e bordas finas. Não use blur contínuo nem glassmorphism.

## Objetos do estilo

1. **Emblema orbital.** SVG quadrado com um medalhão dourado no centro (`circle` com o gradiente dourado e um anel interno), um anel de marcações (`stroke-dasharray: 1 9.26` num círculo de raio 98) e três órbitas em grupos `<g>` que giram com `transform-box: view-box; transform-origin: 50% 50%`. Cada órbita leva um ou dois satélites (`circle` pequeno em ciano ou dourado). As durações diferentes (45 s, 70 s ao contrário, 110 s) evitam que pareça um spinner.
2. **Calendário de papel.** Cartão claro levemente girado (-2°) com cabeçalho mono (mês e horário), um número dominante (quantidade de encontros) e uma grade `repeat(7, 1fr)` de células. Os dias com encontro usam fundo `--paper-ink` e texto `--paper`. As células entram em sequência com `transition-delay: calc(var(--c) * 40ms)`.
3. **Ingresso com canhoto.** `display: grid; grid-template-columns: 3fr 1fr`. O picote é uma `border-left: 2px dashed` no canhoto. Os recortes semicirculares são máscaras: no corpo, `radial-gradient(circle 11px at 100% 0, #0000 98%, #000)` no topo e o mesmo em `100% 100%` na base (cada um com `51%` de altura); no canhoto, o mesmo em `0 0` e `0 100%`. Um botão real com `aria-pressed` destaca o canhoto (`translateX(12px) rotate(3deg)`). Sem JavaScript, o botão fica `disabled`.
4. **Acervo em camadas.** Três folhas absolutas no mesmo lugar: a de trás com `rotate(-7deg)` e opacidade .55, a do meio com `rotate(-3deg)`, e a da frente com o título e a lista de categorias separadas por fios.
5. **Constelação.** SVG com um cartão claro no centro e cinco nós ligados por linhas em `--line`. Por cima, um `path` ciano com `stroke-dasharray: 6 330` e `stroke-dashoffset` animado até -336 em 8 s: parece um sinal percorrendo a rede. No celular, os nós viram lista.
6. **Réguas proporcionais.** Barras de 14 px com o comprimento proporcional ao valor real, na mesma escala, e marcas mono embaixo. Duração e valor nunca dividem a mesma régua.
7. **Botão com reflexo.** Fundo `--orbital-gold-gradient`, raio 9 px, altura 54 px. Um `::before` com faixa clara inclinada atravessa o botão, um `::after` faz o contorno de 1 px variar entre .16 e .65 de opacidade e a seta anda 3 px. Ciclo de 6,4 s com repouso. Só no botão da ação final.

## Movimento

- Entradas por objeto, não um fade igual para a página inteira: calendário 0,75 s com deslocamento de 15 px; acervo e ingresso 0,8 s vindo de -22 px na horizontal; réguas crescem com `scaleX` em 1,1 s.
- Loops ambientes: órbitas (45 s no desktop, 65 s no celular), sinal da constelação (8 s linear) e reflexo do botão (6,4 s com 79% do ciclo parado).
- Easing padrão `cubic-bezier(.2, .7, .2, 1)`. Nada de escala pulsante, tremor ou spinner.
- Tudo com `transform`, `opacity` ou `stroke-dashoffset`. Use IntersectionObserver para ligar `data-motion="on"` só na cena visível, pause com a aba oculta e desligue tudo com `prefers-reduced-motion`.

## Aplicação em deck, página e carrossel

- **Página:** hero dividido (texto à esquerda, emblema à direita), calendário como objeto claro, constelação para a turma ou a comunidade, ingresso para o encontro ao vivo, acervo para os materiais, réguas antes da oferta. Comparativos vêm antes da oferta no DOM.
- **Deck:** fundo `--bg-2` com brilho radial, título leve à esquerda e um objeto de papel à direita. Contador mono discreto no canto inferior direito.
- **Carrossel:** título curto com uma palavra em dourado, um objeto de papel centralizado ocupando metade do slide e rodapé mono com @ e contador.

## O que evitar

- Dourado em todos os botões, ícones e bordas.
- Títulos em peso 700 ou mais.
- Grade de cartões escuros iguais no lugar dos objetos.
- Fotos de banco ou pessoas geradas fingindo ser alunos. Participantes da constelação são pontos e rótulos.
- Brilhos animados com `box-shadow` ou `filter`.
- Reproduzir datas, preços ou condições de outra campanha só porque estavam no exemplo.

## Checklist

- [ ] O dourado aparece em no máximo três pontos por tela e sempre com função.
- [ ] Cada seção tem um objeto próprio (calendário, ingresso, acervo, constelação ou régua).
- [ ] Títulos em Geist 400 com tracking negativo; corpo com linha de 1,65.
- [ ] O ingresso funciona por teclado e fica legível sem JavaScript.
- [ ] Órbitas e sinais param fora da tela, com a aba oculta e com movimento reduzido.
- [ ] Em 390 px os objetos se reorganizam em coluna e nenhum texto fica abaixo de 14 px fora dos slides.
- [ ] `pycode styles check orbital` passa.
