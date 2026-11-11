---
version: 1.0.0
name: Papel e colagem
slug: colagem
description: 'Mesa de recortes em papel kraft: pedaços rasgados, fita adesiva, carimbos, etiquetas, polaroides e letras recortadas, com anotações à mão. Para conteúdo de bastidores, listas, comparações
  e posts de comunidade.'
mode: light
fonts:
- anton
- bricolage-grotesque
- caveat
- geist-mono
best_for:
- carousel
- page
- deck
colors:
  bg: '#ece2d0'
  bg-2: '#e2d5bd'
  surface: '#fbf7ef'
  surface-2: '#f3ead9'
  text: '#211a14'
  muted: '#5a4c3e'
  line: '#c2ae8e'
  accent: '#d23f22'
  accent-2: '#2c47c4'
  accent-ink: '#ffffff'
  paper: '#fbf7ef'
  paper-ink: '#211a14'
  danger: '#b3261e'
  ok: '#2f6e3e'
  warn: '#8a5a00'
  kraft: '#c9a77a'
  tomato: '#d23f22'
  cobalt: '#2c47c4'
  mustard: '#e9b21a'
typography:
  display:
    fontFamily: Anton
    fontWeight: 400
    letterSpacing: 0em
  body:
    fontFamily: Bricolage Grotesque
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: Geist Mono
    fontWeight: 400
rounded:
  base: 2px
  large: 4px
elevation:
  shadow: 0 1px 1px rgba(33, 26, 20, .18), 0 10px 22px rgba(33, 26, 20, .18)
  glow: '0 0 0 2px #211a14'
tokens: tokens.css
---

# Papel e colagem

## Visão geral

Papel e colagem é uma mesa de recortes em papel kraft: pedaços rasgados, fita adesiva, carimbos, etiquetas de rotulador, polaroides, bloco adesivo e letras recortadas como num cartaz feito à mão, com anotações curtas de caneta. Tudo parece colado por alguém, com leve rotação e sombra curta, mas continua fácil de ler.

Use para bastidores, diários de projeto, listas de erros e aprendizados, conteúdo de comunidade, retrospectivas e carrosséis informais. Evite para documentação técnica, temas de segurança e conteúdo que precisa transmitir precisão.

## Cores

- `--bg` (#ece2d0) é o kraft, com uma textura de fibras em SVG (`feTurbulence` com `feColorMatrix` a 9%).
- `--surface` (#fbf7ef) é o papel branco dos recortes; `--surface-2` o creme de segundo plano.
- `--text` (#211a14) é tinta preta; `--muted` anotação a lápis.
- `--accent` (#d23f22, tomate) e `--accent-2` (#2c47c4, cobalto) são as duas cores de recorte e de caneta. `--warn` é mostarda.
- Extras: `--colagem-tape` (fita translúcida), `--colagem-kraft`, `--colagem-tomato`, `--colagem-cobalt`, `--colagem-mustard` e `--colagem-font-hand` (Caveat).

Três cores chapadas, mais branco e preto. Nada de degradê.

## Tipografia

Anton em caixa alta para títulos e letras recortadas. Bricolage Grotesque no texto, mais humana que uma sans técnica. Caveat em anotações curtas à mão (no máximo cinco palavras). Geist Mono para etiquetas de rotulador.

| Nível | Tamanho | Fonte |
|---|---|---|
| letras recortadas | `clamp(36px, 5.4vw, 82px)` | Anton |
| h1 | `clamp(34px, 4.4vw, 64px)` | Anton, caixa alta |
| anotação | 22 a 30 px | Caveat 700 |
| corpo | 17 px | Bricolage Grotesque |
| etiqueta | 13 a 18 px | Geist Mono, caixa alta, tracking .18em |

## Superfícies e texturas

- Papel com bordas rasgadas: `clip-path: polygon(...)` com 16 a 26 pontos irregulares no topo e na base (gere os pontos uma vez e guarde).
- Sombra curta em duas camadas (`--shadow`) e rotação de 1° a 5°.
- Fita: retângulo de 110 × 30 px translúcido, girado, por cima da borda de outra peça.
- Raio quase zero (2 a 4 px).

## Objetos do estilo

1. **Letras recortadas.** Cada letra num `span` com fundo próprio (tomate, cobalto, mostarda, branco ou preto), rotação entre -5° e 5° via `--r` e sombra curta. O elemento pai tem `aria-label` com a palavra inteira. Uma palavra por tela.
2. **Papel rasgado com fita.** Bloco branco com `clip-path` irregular e uma fita translúcida segurando a borda.
3. **Polaroide.** Moldura branca com 14 px nas laterais e 52 px embaixo, imagem quadrada (desenho em SVG ou foto sua com licença) e legenda em Caveat.
4. **Bloco adesivo.** Quadrado mostarda com sombra mais longa embaixo e texto em Caveat.
5. **Carimbo circular.** SVG com dois círculos e texto em `textPath` ao redor, em tomate, girado.
6. **Etiqueta de rotulador.** Fita preta (ou tomate, ou cobalto) com letras em mono caixa alta, sombra de relevo no texto.
7. **Etiqueta pendurada.** Etiqueta com recorte em ponta (`clip-path`) presa por um fio, balançando 5° para cada lado.
8. **Anotação com seta.** Frase curta em Caveat azul e uma seta curva em SVG apontando o detalhe.

## Movimento

- As peças chegam como se fossem coladas: caem 40 px com rotação extra de -8° e leve rebote (`cubic-bezier(.3, 1.4, .5, 1)`), escalonadas em 120 ms. Use a propriedade `rotate` para a inclinação fixa e `transform` para a entrada, assim uma não apaga a outra.
- Um único loop: a etiqueta pendurada balança em 4,5 s.
- Movimento reduzido: peças no lugar, etiqueta parada.

## Aplicação em deck, página e carrossel

- **Carrossel:** uma palavra em letras recortadas no topo, um bloco adesivo ou papel rasgado com a ideia e o contador em Caveat.
- **Página:** hero com título recortado, nota rasgada com o botão e uma pilha de peças ao lado (polaroide, bloco adesivo, carimbo); seções com listas numeradas à mão.
- **Deck:** fundo kraft, título recortado, papel com a explicação e uma polaroide girada.

## O que evitar

- Peças cobrindo texto importante. Confira em 390 px.
- Letras recortadas em frases inteiras.
- Caveat em parágrafos.
- Fotos de banco com cara de banco.
- Rotação acima de 6°, que vira bagunça.

## Checklist

- [ ] Uma palavra recortada por tela, com `aria-label`.
- [ ] Nenhuma peça cobre texto no celular.
- [ ] Anotações à mão com no máximo cinco palavras.
- [ ] Entradas com `transform` e inclinação fixa com `rotate`.
- [ ] Contraste do texto sobre o kraft acima de 4,5:1.
- [ ] `pycode styles check colagem` passa.
