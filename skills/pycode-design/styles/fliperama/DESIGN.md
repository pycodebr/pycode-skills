---
version: 1.0.0
name: Fliperama
slug: fliperama
description: 'Tela de jogo 16-bit: caixas de diálogo azul-royal, barras de HP e XP, inventário em slots, sprites em pixel e movimento em degraus. Para trilhas de aprendizado, desafios, níveis e conteúdo
  leve.'
mode: dark
fonts:
- press-start-2p
- vt323
- jersey-10
best_for:
- carousel
- deck
- page
colors:
  bg: '#0b0b1a'
  bg-2: '#121230'
  surface: '#1a2bb0'
  surface-2: '#24249a'
  text: '#ffffff'
  muted: '#c9cdf2'
  line: '#ffffff'
  accent: '#ffd84d'
  accent-2: '#5ef2c2'
  accent-ink: '#000000'
  paper: '#fff8e7'
  paper-ink: '#141433'
  danger: '#ff5c7a'
  ok: '#5ef2c2'
  warn: '#ffa64d'
  hp: '#ff5c7a'
  xp: '#5ef2c2'
  mp: '#6ab7ff'
  window: '#1a2bb0'
typography:
  display:
    fontFamily: Press Start 2P
    fontWeight: 400
    letterSpacing: 0.02em
  body:
    fontFamily: VT323
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: VT323
    fontWeight: 400
rounded:
  base: 0px
  large: 0px
elevation:
  shadow: '6px 6px 0 #000000'
  glow: '0 0 0 4px #000000, 0 0 0 8px #ffffff'
tokens: tokens.css
---

# Fliperama

## Visão geral

Fliperama é a tela de um jogo 16-bit: céu escuro, janelas de diálogo azul-royal com borda branca dupla, barras de HP, XP e MP, inventário em slots, sprites em pixel e movimento sempre em degraus. O conteúdo vira missão: aprender é ganhar XP, guardar um conceito é colocar um item no inventário e terminar é a tela de continuar.

Use para trilhas de aprendizado, desafios, níveis de um curso, revisão de conceitos, conteúdo para iniciantes e carrosséis leves. Evite para temas sérios (segurança, decisões de compra, saúde) e para leitura longa.

## Cores

- `--bg` (#0b0b1a) é o céu da tela; `--bg-2` as faixas de cenário.
- `--surface` (#1a2bb0) é o azul-royal das janelas; `--surface-2` as janelas secundárias e slots.
- `--text` e `--line` são branco puro: texto e a borda de duas camadas (`box-shadow: 0 0 0 4px #fff, 0 0 0 8px #000`).
- `--accent` (#ffd84d) marca a palavra ativa no diálogo, o XP e o cursor. Sobre ele, `--accent-ink` é preto puro.
- `--danger` (#ff5c7a) é HP e erro; `--ok` e `--accent-2` (#5ef2c2) são acerto e cura.
- Extras: `--fliperama-hp`, `--fliperama-xp`, `--fliperama-mp`, `--fliperama-window`, `--fliperama-pixel` (4 px, a unidade) e `--fliperama-font-score` (Jersey 10).

Cores chapadas, sem degradê. Sombra é sempre um bloco preto deslocado (`6px 6px 0 #000`).

## Tipografia

Press Start 2P para títulos curtos, rótulos de HUD e botões, sempre em caixa alta. VT323 para o texto dos diálogos e de apoio, num corpo maior que o normal. Jersey 10 para placar, números e contagem.

| Nível | Tamanho | Fonte |
|---|---|---|
| título | `clamp(20px, 3.6vw, 48px)`, linha 1,35 | Press Start 2P |
| rótulo de HUD | 12 px | Press Start 2P |
| diálogo | 24 a 30 px | VT323 |
| corpo | 22 px | VT323 |
| placar | 30 a 44 px | Jersey 10 |

A VT323 é miúda: o corpo do estilo é 22 px. Os modelos de deck, página e carrossel que usam `--font-body` devem aumentar o tamanho em cerca de 1,3 vez quando usarem este estilo. Na Press Start 2P, o Í maiúsculo é estreito; confira títulos acentuados.

## Superfícies e texturas

- **Tela:** moldura branca e preta de 4 px cada, fundo do céu com estrelas de 4 px que piscam em degraus e chão de blocos (`repeating-linear-gradient` em dois azuis).
- **Linhas de varredura:** `::after` com `repeating-linear-gradient` de 3 px transparente e 1 px preto a 22%.
- **Janelas:** azul-royal com a borda dupla e sombra em bloco.
- Raio zero em tudo. Pixels se alinham à grade de 4 px.

## Objetos do estilo

1. **Caixa de diálogo.** Janela azul com plaqueta de nome amarela (Press Start 2P 12 px) saindo da borda de cima, texto em VT323 com a palavra ativa em `mark` amarelo e um triângulo branco piscando no canto (`steps(1)`).
2. **Barras de HP, XP e MP.** Fileira de quadrados de 14 px com contorno preto; os cheios usam a cor da barra. Versão contínua: uma barra que enche com `scaleX` em `steps(8)`.
3. **Inventário.** Grid de slots de 64 px com contorno duplo; cada item é um sprite de 8 × 8 pixels. O slot selecionado tem uma moldura amarela piscando e a legenda explica o item.
4. **Sprite.** SVG com um `rect` por pixel e `shape-rendering="crispEdges"`. Dois quadros sobrepostos trocam de opacidade em `steps(1)` para andar no lugar; o conjunto sobe e desce 8 px em `steps(2)`.
5. **LEVEL UP.** Texto amarelo com sombra preta em bloco, entrando em três degraus de escala, com estrelas de pixel piscando em sequência.
6. **Continuar.** "CONTINUAR?" com contagem regressiva em Jersey 10 (números empilhados alternando `opacity`) e a próxima fase embaixo.
7. **Botão START.** Fundo amarelo, texto em Press Start 2P, sombra em bloco que some quando pressionado (`translate(4px, 4px)`).

## Movimento

- Tudo em degraus: `steps()` em toda animação. Nada de easing suave.
- Loops: estrelas (2,4 s), cursor do diálogo (1 s), sprite (0,8 s por quadro), barras (4 s em oito passos).
- Entradas podem usar a subida padrão, mas os objetos do jogo aparecem em degraus.
- Movimento reduzido: tudo parado, barras cheias, primeiro número da contagem visível.

## Aplicação em deck, página e carrossel

- **Deck:** HUD no topo (XP do curso e número do slide como placar), título em Press Start 2P no meio e uma janela de diálogo embaixo com a explicação.
- **Página:** hero como tela de jogo; seções de missões com caixas de seleção quadradas e o botão START.
- **Carrossel:** fase no topo, pergunta em Press Start 2P, sprite no centro e janela de diálogo com a resposta.

## O que evitar

- XP, pontos e níveis inventados como se fossem dados reais de progresso.
- Fontes pixel em textos longos ou abaixo de 12 px.
- Degradês, sombras difusas e cantos arredondados.
- Sprites copiados de jogos existentes. Desenhe os seus.
- Animações suaves, que quebram a ilusão.

## Checklist

- [ ] A metáfora (missão, XP, inventário) se aplica de verdade ao conteúdo.
- [ ] Texto de diálogo em VT323 com pelo menos 22 px.
- [ ] Todas as animações em `steps()` e pausadas fora da tela.
- [ ] Sprites desenhados por você, em SVG com `crispEdges`.
- [ ] Contraste do texto sobre o azul-royal acima de 4,5:1.
- [ ] `pycode styles check fliperama` passa.
