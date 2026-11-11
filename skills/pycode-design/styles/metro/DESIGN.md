---
version: 1.0.0
name: Metrô
slug: metro
description: 'Sinalização de metrô: azulejo claro, placas em faixas coloridas, diagrama de linhas com estações, setas de direção e numeração de plataforma. Para trilhas, roteiros, ordem de etapas e mapas
  de conteúdo.'
mode: light
fonts:
- space-grotesk
- inter
- geist-mono
best_for:
- page
- carousel
- deck
colors:
  bg: '#f3f3ef'
  bg-2: '#e8e8e2'
  surface: '#ffffff'
  surface-2: '#f7f7f4'
  text: '#111418'
  muted: '#4d535b'
  line: '#c9cbc6'
  accent: '#0b5cad'
  accent-2: '#d6202a'
  accent-ink: '#ffffff'
  paper: '#ffffff'
  paper-ink: '#111418'
  danger: '#c41a23'
  ok: '#00784b'
  warn: '#9a6700'
  line-blue: '#0b5cad'
  line-red: '#d6202a'
  line-green: '#00965e'
  line-yellow: '#ffc20e'
  line-purple: '#7a3e9d'
  line-orange: '#f07d00'
  sign: '#111418'
typography:
  display:
    fontFamily: Space Grotesk
    fontWeight: 700
    letterSpacing: -0.03em
  body:
    fontFamily: Inter
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: Geist Mono
    fontWeight: 400
rounded:
  base: 6px
  large: 14px
elevation:
  shadow: 0 2px 0 rgba(17, 20, 24, .12)
  glow: '0 0 0 4px #ffc20e'
tokens: tokens.css
---

# Metrô

## Visão geral

Metrô usa a linguagem da sinalização de transporte: azulejo claro, placas pretas com a cor da linha embaixo, diagrama de linha com estações, setas de direção, baldeações e painel de próximos trens. Qualquer sequência vira viagem: cada etapa é uma estação, pular uma delas custa caro e o "você está aqui" sempre aparece em amarelo.

Use para trilhas de estudo, roadmaps, ordem de etapas, mapas de conteúdo de um curso, agendas e onboarding. Evite para conteúdo sem sequência e para temas emocionais.

## Cores

- `--bg` (#f3f3ef) é o azulejo, com rejunte em `--line` desenhado por duas `linear-gradient` (44 × 22 px).
- `--surface` é a placa branca; `--text` (#111418) é o preto das placas.
- `--accent` (#0b5cad) é a linha principal, links e ação; `--accent-2` (#d6202a) é a linha de baldeação.
- Extras de linha: `--metro-line-blue`, `-red`, `-green`, `-yellow`, `-purple`, `-orange`, `--metro-sign` (fundo das placas) e `--metro-line-width` (10 px).
- `--metro-line-yellow` é reservado para "você está aqui" e placas de direção.

Cada trilha tem uma cor que nunca muda. Se o conteúdo tem só uma trilha, use só o azul.

## Tipografia

Space Grotesk em peso 700 para placas, nomes de estação e títulos, com tracking de -0.03em. Inter no texto. Geist Mono para horários, minutos e códigos.

| Nível | Tamanho | Peso |
|---|---|---|
| h1 | `clamp(40px, 5.4vw, 78px)` | 700 |
| placa | 18 a 26 px | 700 |
| estação | 15 px | 600 |
| corpo | 17 a 18 px | 400 |
| horário | 12 a 20 px mono | 400 a 600 |

Nenhuma placa tem mais de cinco palavras.

## Superfícies e texturas

- Azulejo de fundo com rejunte fino; seções com uma película do fundo a 92% para o texto ler bem.
- Placas pretas com raio de 6 px e uma faixa de 6 px da cor da linha embaixo (`box-shadow: inset 0 -6px 0`).
- Painéis brancos com contorno de 1 px.
- Sem sombra difusa; no máximo uma sombra de 2 px.

## Objetos do estilo

1. **Placa de estação.** Faixa preta com o círculo da linha (número em branco), o nome da estação e a direção à direita com uma seta que empurra de leve.
2. **Diagrama de linha.** `ol` em grid de colunas iguais; o trilho é um `::before` tracejado e o trecho percorrido um `::after` azul. Estações são círculos de 40 px com borda de 7 px; as futuras em cinza. A estação atual é amarela com um anel que pulsa (escala e opacidade). Um trem em cápsula percorre o trecho com `translateX(calc(100cqw / 3))` usando `container-type: inline-size`. No celular, o diagrama vira vertical.
3. **Mapa de linhas.** SVG com ângulos de 45°, três cores fixas, estações brancas com contorno e uma cápsula branca na baldeação. Desenhado por código, nunca por gerador de imagem.
4. **Painel de próximos.** Painel preto com cabeçalho mono, linhas com o círculo da linha, o destino e os minutos em amarelo que viram de tempos em tempos.
5. **Placa de plataforma e direção.** Uma placa preta com o número e outra amarela com a direção e a seta.
6. **Baldeação.** Duas linhas que se cruzam com uma cápsula branca de contorno preto no encontro.
7. **Placa de saída.** Verde, com pictograma desenhado em SVG e texto curto. Marca a conclusão.

## Movimento

- Funcional: trem percorrendo o trecho (7 s), anel do "você está aqui" (2 s), seta de direção (2,4 s), minutos virando (6 s).
- Entradas com subida curta.
- Em movimento reduzido, trem parado na primeira estação e anel estático.

## Aplicação em deck, página e carrossel

- **Deck:** placa preta no topo com a estação atual e a próxima; corpo com título à esquerda e um diagrama simples à direita.
- **Página:** placa da linha no topo, título, e o diagrama de linha completo com a estação atual destacada; a seguir, uma lista vertical de estações com descrição.
- **Carrossel:** faixa do mapa no topo de cada slide com a estação atual em amarelo e as anteriores em azul, placa da estação e uma frase. O último slide é a placa de saída.

## O que evitar

- Mudar a cor de uma trilha no meio do conteúdo.
- Placas longas ou com frases inteiras.
- Mapas com curvas livres: use 0°, 45° e 90°.
- Amarelo para qualquer coisa além de "você está aqui" e direção.
- Diagramas que encolhem até ficarem ilegíveis no celular; reorganize na vertical.

## Checklist

- [ ] Cada etapa é uma estação, na ordem certa.
- [ ] Cores de linha fixas e com significado.
- [ ] "Você está aqui" em amarelo, com `aria-current`.
- [ ] Diagrama vertical em 390 px.
- [ ] Placas com no máximo cinco palavras.
- [ ] `pycode styles check metro` passa.
