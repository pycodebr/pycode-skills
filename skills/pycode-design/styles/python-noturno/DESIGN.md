---
version: 1.0.0
name: Código noturno
slug: python-noturno
description: Azul-marinho profundo com o azul e o amarelo do Python, textura de código ao fundo, numerais gigantes e cartas colecionáveis. Linguagem de feed técnico e de aula de programação.
mode: dark
fonts:
- bricolage-grotesque
- inter
- jetbrains-mono
best_for:
- carousel
- deck
- page
colors:
  bg: '#0a0e1a'
  bg-2: '#0d1628'
  surface: '#121d36'
  surface-2: '#1a2a4d'
  text: '#f8fafc'
  muted: '#a9b8d0'
  line: '#2a3d66'
  accent: '#ffd43b'
  accent-2: '#5aa0e6'
  accent-ink: '#1b1500'
  paper: '#eef3fb'
  paper-ink: '#0d1a33'
  danger: '#ff6b6b'
  ok: '#4ade80'
  warn: '#fbbf24'
  python-blue: '#3776ab'
  python-blue-light: '#5aa0e6'
  python-yellow: '#ffd43b'
typography:
  display:
    fontFamily: Bricolage Grotesque
    fontWeight: 800
    letterSpacing: -0.035em
  body:
    fontFamily: Inter
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: JetBrains Mono
    fontWeight: 400
rounded:
  base: 12px
  large: 22px
elevation:
  shadow: 0 22px 50px rgba(2, 6, 18, .55)
  glow: 0 0 0 1px rgba(90, 160, 230, .22), 0 0 60px rgba(55, 118, 171, .28)
tokens: tokens.css
---

# Código noturno com Python

## Visão geral

Azul-marinho profundo, o azul e o amarelo do Python e uma textura de código real descendo devagar atrás de tudo. É a linguagem de um feed técnico e de aulas de programação: um conceito forte por post, um objeto herói por slide (carta, numeral, medidor ou terminal) e um contador discreto.

Use para carrosséis de lista ("três jeitos de", "cinco ferramentas"), escadas de nível, passo a passo de código, slides de aula de Python e páginas de exercícios. Evite para temas sem código, para conteúdo institucional sóbrio (prefira `orbital` ou `revista`) e para documentos longos (prefira `caderno`).

## Cores

- `--bg` (#0a0e1a) é a noite. A grade de 60 px em azul a 5% e a textura de código ficam sobre ele.
- `--accent` (#ffd43b, amarelo do Python) é o protagonista: numerais, a palavra-chave do título, a carta principal e o botão. Texto sobre o amarelo usa sempre `--accent-ink`.
- `--accent-2` (#5aa0e6, azul do Python claro) organiza links, foco, ícones de linha e conexões.
- `--surface` e `--surface-2` são as janelas de código e as cartas comuns.
- `--paper` é o cartão claro de definição, quando um termo precisa de destaque calmo.
- Extras: `--python-noturno-python-blue` (#3776ab, o azul original, para brilhos e superfícies), `--python-noturno-code-opacity` (.06) e `--python-noturno-grid` (60 px).

O brilho azul é sempre localizado (um `radial-gradient` atrás do objeto), nunca um degradê roxo e azul cobrindo a tela.

## Tipografia

Bricolage Grotesque em peso 800 para títulos e numerais, com tracking de -0.035em. Inter no corpo. JetBrains Mono para código, comandos e contadores.

| Nível | Tamanho | Peso |
|---|---|---|
| numeral | `clamp(120px, 17vw, 230px)` | 800, um dígito vazado com `-webkit-text-stroke` |
| h1 | `clamp(40px, 5.2vw, 74px)` | 800, até três linhas |
| nome de carta | 24 px | 800 |
| corpo | 17 a 19 px | 400 |
| código | 14 a 15 px | 500 |

No feed, o título tem no máximo três linhas e o numeral pode ocupar um terço do slide. Comandos são conferidos letra por letra.

## Superfícies e texturas

- **Textura de código:** um `<div>` absoluto com `white-space: pre`, fonte mono de 13 px, cor `--python-noturno-python-blue-light` e opacidade de 6%. O conteúdo é código real do assunto, duplicado para o loop vertical. É decorativo (`aria-hidden="true"`).
- **Grade:** duas `linear-gradient` de 1 px em azul a 5%, módulo de 60 px.
- **Janelas de código:** fundo `#060a14`, borda `--line`, raio 12 px, cabeçalho com o nome do arquivo em mono.
- **Cartas:** raio 18 px, proporção 5:7, degradê de `--surface-2` para `--surface`. A carta principal é amarela com reflexo holográfico.

## Objetos do estilo

1. **Carta colecionável.** `figure` com `aspect-ratio: 5/7`, cabeçalho mono (posição e categoria), área de glifo com um ícone em SVG desenhado por você, nome em peso 800 e o comando em `code`. Três cartas em leque: as laterais com `rotate(±12deg)` e deslocadas 62% para os lados, a do meio levantada e amarela. O reflexo é um `::after` com faixa clara `mix-blend-mode: soft-light` que atravessa a carta com `translateX` em 5,5 s.
2. **Numeral gigante.** Bricolage 800 amarelo com um dígito vazado (`color: transparent; -webkit-text-stroke: 2px var(--accent)`). Abre listas e slides de etapa sem ícone.
3. **Medidor de níveis.** Lista de cinco segmentos de 44 × 26 px empilhados; os acesos usam `::after` amarelo. Os segmentos acima do nível atual acendem e apagam em degraus (`steps(1)`) para sugerir o caminho. Ao lado, o número do nível e uma frase curta.
4. **Terminal com saída.** Janela mono com o comando digitado: uma máscara (`::after` com a cor do fundo) encolhe com `scaleX` em `steps(14)`. As linhas de saída aparecem em sequência com `opacity` em degraus. Sem animação, tudo fica visível.
5. **Contador N/T.** Texto "4 / 7" em peso 800 e uma fileira de barrinhas de 34 × 6 px, com as já vistas em amarelo. Sempre no mesmo canto.
6. **Textura de código.** A mesma do fundo, mas como objeto quando o slide fala do próprio código.

## Movimento

- Textura de código: `translateY(-50%)` em 80 s linear, loop.
- Reflexo holográfico: 5,5 s, parado durante 55% do ciclo.
- Medidor e saída de terminal: sempre em degraus (`steps`), como algo que liga.
- Entradas: subida de 18 px com `opacity`, escalonadas em 70 ms.
- Hover nas cartas abre o leque um pouco mais (rotação de 16°).
- Pause fora da tela e com a aba oculta; `prefers-reduced-motion` desliga tudo e deixa o texto do terminal visível.

## Aplicação em deck, página e carrossel

- **Carrossel:** capa com numeral gigante, título de até três linhas, uma carta inclinada no canto e o contador. Slides internos: um objeto herói por slide (carta, medidor ou terminal). Último slide com um único pedido de ação.
- **Deck:** título com o termo em mono amarelo à esquerda, bloco de código à direita, textura de código a 6% e contador mono no canto.
- **Página:** hero com numeral e leque de cartas, passos numerados com o número gigante ao lado de cada bloco de código.

## O que evitar

- Logotipo do Python ou de outras marcas desenhado à mão. Use `pycode icon` quando o logo for necessário e respeite a marca.
- Amarelo em textos longos ou em fundos grandes.
- Degradê roxo e azul de ponta a ponta.
- Textura de código com opacidade acima de 8%, que disputa com o título.
- Comandos inventados ou com erro de digitação.
- Dois pedidos de ação no mesmo carrossel.

## Checklist

- [ ] Um objeto herói por slide, com o texto numa área limpa.
- [ ] Código e comandos executados e conferidos.
- [ ] Amarelo só em numerais, destaques e botão.
- [ ] Contador N/T no mesmo canto em todos os slides.
- [ ] Textura de código abaixo de 8% e marcada como decorativa.
- [ ] Contraste do texto acima de 4,5:1 sobre o fundo e sobre as cartas.
- [ ] `pycode styles check python-noturno` passa.
