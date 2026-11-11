---
version: 1.0.0
name: Revista
slug: revista
description: Editorial impresso em papel creme, serifas de revista com itálico expressivo, colunas com fios, capitular, citação em destaque e índice numerado. Para ensaios, newsletters, estudos de caso
  e aulas de leitura longa.
mode: light
fonts:
- instrument-serif
- fraunces
- geist-mono
best_for:
- page
- carousel
- deck
colors:
  bg: '#f4efe6'
  bg-2: '#ece5d8'
  surface: '#fbf8f2'
  surface-2: '#efe8dc'
  text: '#1a1714'
  muted: '#5c544a'
  line: '#cfc4b2'
  accent: '#b23a1c'
  accent-2: '#1f4d45'
  accent-ink: '#ffffff'
  paper: '#fffdf8'
  paper-ink: '#1a1714'
  danger: '#a3271a'
  ok: '#2f6b3b'
  warn: '#8a5a00'
  rule: '#1a1714'
  rule-thin: '#cfc4b2'
typography:
  display:
    fontFamily: Instrument Serif
    fontWeight: 400
    letterSpacing: -0.02em
  body:
    fontFamily: Fraunces
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: Geist Mono
    fontWeight: 400
rounded:
  base: 0px
  large: 2px
elevation:
  shadow: '0 1px 0 #cfc4b2'
  glow: '0 0 0 1px #1a1714'
tokens: tokens.css
---

# Revista

## Visão geral

Revista é um editorial impresso em papel creme: serifa de revista com itálico expressivo, colunas com fios, capitular, citação em destaque, índice com pontilhado e figuras com legenda numerada. A hierarquia vem da tipografia e dos fios, não de caixas. É o estilo para quando o texto é o produto.

Use para ensaios, newsletters, estudos de caso, aulas de leitura longa, sumários de curso e carrosséis com tom de opinião. Evite para conteúdo muito visual ou técnico com muito código (prefira `terminal`) e para chamadas rápidas de venda.

## Cores

- `--bg` (#f4efe6) é o papel creme; `--bg-2` é o papel de encarte e boxes.
- `--surface` (#fbf8f2) é o fundo de figuras; `--surface-2` o de notas.
- `--text` (#1a1714) é tinta quente; `--muted` (#5c544a) é para legendas, créditos e linha fina.
- `--accent` (#b23a1c, vermelho tijolo) aparece em poucos pontos por página: capitular, número de seção, aspas e ação.
- `--accent-2` (#1f4d45, verde-garrafa) é a segunda voz, usada em figuras.
- Extras: `--revista-rule` (fio preto), `--revista-rule-thin`, `--revista-column` (34ch) e `--revista-dropcap-lines` (4).

## Tipografia

Instrument Serif em títulos grandes, com o itálico como segunda voz (uma palavra em itálico vermelho no título). Fraunces no texto corrido e na linha fina em itálico. Geist Mono pequena e cinza para créditos, páginas e legendas.

| Nível | Tamanho | Fonte |
|---|---|---|
| nome da publicação | `clamp(64px, 11vw, 168px)`, linha .8 | Instrument Serif |
| h1 | `clamp(42px, 5.6vw, 86px)`, linha .98 | Instrument Serif |
| linha fina | 19 a 24 px | Fraunces itálico |
| corpo | 16,5 px, linha 1,62 | Fraunces |
| crédito | 13 px | Geist Mono |

Texto corrido em duas colunas com cerca de 34 caracteres por linha (`columns: 2 16ch`) e fio entre elas. Parágrafos seguintes recuam 1,4em em vez de pular linha.

## Superfícies e texturas

- Papel liso, sem textura. A riqueza vem dos fios: fio grosso de 3 px sob o cabeçalho, fio fino de 1 px entre seções, fio duplo (`3px double`) entre partes.
- Figuras em `--surface` com borda de 1 px, sem sombra.
- Raio zero.

## Objetos do estilo

1. **Cabeçalho da publicação.** Nome enorme à esquerda, número da edição e assunto à direita em mono, fio grosso embaixo e uma linha de seção com a página.
2. **Capitular.** `p::first-letter` com `float: left`, Instrument Serif em 5,4em, linha .8 e cor `--accent`. Só no primeiro parágrafo do texto.
3. **Citação em destaque.** `blockquote` entre dois fios, Instrument Serif itálico de 24 a 32 px e aspas de abertura grandes em vermelho (`::before`, 140 px) que sobem ao entrar na tela.
4. **Índice numerado.** Lista com número em serifa vermelha, título, pontilhado (`::after` com `border-bottom: dotted` e `flex: 1`) e página em mono.
5. **Figura com legenda.** Ilustração em SVG feita de formas simples (círculos e fios) e legenda mono que começa com "Fig. 1" em negrito.
6. **Nota na margem.** Grid com o texto à esquerda e uma nota de 120 px à direita, ligadas por um número sobrescrito vermelho.
7. **Ornamento.** Fio duplo dos dois lados de um "§" em itálico vermelho. Separa partes sem criar outro título.

## Movimento

- Discreto, como virar uma página: fios crescem com `scaleX` (1,2 s), aspas sobem 20 px, textos entram com opacidade.
- Um único loop lento: um elemento da figura gira em 60 s.
- Movimento reduzido mostra tudo no lugar.

## Aplicação em deck, página e carrossel

- **Página:** cabeçalho de publicação, título grande com linha fina, colunas com capitular e figura ao lado. Seções separadas por fio duplo.
- **Deck:** cabeçalho corrido em mono (publicação e seção), título à esquerda, parágrafo com capitular à direita e rodapé com a marca e o número da página.
- **Carrossel:** capa de revista 4:5 com o nome da publicação ocupando a largura, linha da edição, chamada principal em itálico e chamadas secundárias com um código de barras desenhado em CSS.

## O que evitar

- Cartões com sombra e cantos arredondados.
- Vermelho em mais de três pontos por tela.
- Títulos em sans-serif ou em peso forte.
- Texto corrido em uma coluna larga demais (acima de 75 caracteres).
- Ilustração genérica de banco de imagens.

## Checklist

- [ ] Uma palavra em itálico vermelho no título, no máximo.
- [ ] Capitular só no primeiro parágrafo.
- [ ] Colunas com fio e linha de leitura curta.
- [ ] Legendas numeradas e créditos em mono.
- [ ] Contraste de `--muted` sobre o creme acima de 4,5:1.
- [ ] `pycode styles check revista` passa.
