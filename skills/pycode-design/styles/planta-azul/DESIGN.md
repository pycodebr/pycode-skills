---
version: 1.0.0
name: Planta técnica
slug: planta-azul
description: Folha de arquiteto em papel azul com grade milimetrada, traço branco desenhado ao vivo, linhas de cota, carimbos e selo técnico. Para arquitetura de sistemas, permissões, fluxos e qualquer
  explicação de estrutura.
mode: dark
fonts:
- space-grotesk
- geist
- jetbrains-mono
best_for:
- deck
- page
- carousel
colors:
  bg: '#0b2a57'
  bg-2: '#081f42'
  surface: '#103568'
  surface-2: '#16427d'
  text: '#eef6ff'
  muted: '#bcd3f0'
  line: '#4f7fbf'
  accent: '#ffd84d'
  accent-2: '#7dffb0'
  accent-ink: '#1c1700'
  paper: '#e8f3ff'
  paper-ink: '#0b2a57'
  danger: '#ff6b7d'
  ok: '#7dffb0'
  warn: '#edc580'
  ink: '#e8f3ff'
  dash: '#bfe0ff'
  stamp: '#edc580'
typography:
  display:
    fontFamily: Space Grotesk
    fontWeight: 600
    letterSpacing: -0.02em
  body:
    fontFamily: Geist
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: JetBrains Mono
    fontWeight: 400
rounded:
  base: 0px
  large: 2px
elevation:
  shadow: 0 0 0 1px rgba(232, 243, 255, .35)
  glow: 0 0 0 1px rgba(232, 243, 255, .5), 0 0 24px rgba(191, 224, 255, .25)
tokens: tokens.css
---

# Planta azul

## Visão geral

Planta azul é uma folha de arquiteto em papel azul com grade milimetrada, traço branco desenhado ao vivo, linhas de cota, carimbos e um selo técnico no canto. O sistema que você explica vira um prédio: cada módulo é uma sala, cada permissão é uma porta, cada perfil é um crachá e o caminho liberado é uma linha tracejada verde.

Use para arquitetura de software, permissões e papéis, fluxos de dados, infraestrutura, organização de pastas e qualquer explicação de estrutura. Evite para conteúdo emocional, institucional ou de lançamento.

## Cores

- `--bg` (#0b2a57) é o papel azul; `--bg-2` é a margem mais escura e o fundo do selo.
- `--text` (#eef6ff) é o traço principal; `--planta-azul-ink` (#e8f3ff) é a cor dos traços em SVG e das molduras.
- `--muted` serve para cotas e notas; `--line` para a grade maior e traços secundários.
- `--accent` (#ffd84d) é o marca-texto: o que está sendo explicado agora. Texto sobre ele usa `--accent-ink`.
- `--ok` e `--accent-2` (#7dffb0) significam acesso liberado; `--danger` (#ff6b7d) significa trancado.
- `--warn` (#edc580) é a cor do carimbo.
- Extras: `--planta-azul-dash` (portas e propostas), `--planta-azul-grid-minor` e `--planta-azul-grid-major` (as duas grades), `--planta-azul-grid` (24 px) e `--planta-azul-stamp`.

## Tipografia

Space Grotesk em peso 600 para títulos, com cara de letreiro técnico. Geist no corpo. JetBrains Mono para rótulos de sala, cotas e selo, em caixa alta pequena com `letter-spacing: .08em` quando for rótulo.

| Nível | Tamanho | Peso |
|---|---|---|
| h1 | `clamp(36px, 4.6vw, 66px)` | 600, tracking -0.02em |
| h3 | 26 px | 600 |
| corpo | 17 px | 400 |
| rótulo de sala | 12 a 13 px mono | 600, caixa alta |
| cota | 11 a 12 px mono | 500 |

## Superfícies e texturas

- **Grade dupla:** quatro `linear-gradient` no fundo da página: linhas de 1 px a cada 24 px (7% de opacidade) e a cada 120 px (16%).
- **Folha:** borda de 2 px mais um `outline` de 1 px afastado 6 px, formando a moldura dupla de prancha.
- Raio zero. Sombras são linhas, não difusas.
- Superfícies internas (salas preenchidas, selo) em `--bg-2` translúcido.

## Objetos do estilo

1. **Planta desenhada ao vivo.** SVG com paredes em `path` de 3 px e `pathLength="1"`; cada parede tem `stroke-dasharray: 1` e `stroke-dashoffset` que vai de 1 para 0 ao entrar na tela, com `transition-delay` escalonado (`--d`). Portas são arcos de 1,5 px em `--planta-azul-dash`. Rótulos aparecem depois das paredes.
2. **Linha de cota.** Duas linhas verticais de chamada, uma linha horizontal com pontas de seta (`path` com triângulos) e o valor num recorte no meio da linha, com fundo da cor do papel. Cresce do centro com `scaleX`.
3. **Carimbo.** Retângulo duplo girado (-8° a -10°) em dourado, com texto em caixa alta. Entra com `scale(1.6)` para `scale(1)` e easing com leve rebote, como se batesse no papel. Um por folha.
4. **Selo técnico.** Grid de duas colunas com bordas de 1 px: projeto (linha inteira), desenho, escala, revisão, folha. Rótulos em 10,5 px mono. Fica no canto inferior direito.
5. **Crachá e caminho.** Retângulo amarelo com o perfil ("aluno") e uma linha verde tracejada (`stroke-dasharray: 6 6`) andando com `stroke-dashoffset` até a sala liberada. Sala trancada recebe um cadeado desenhado em `rect` e `path`.
6. **Lupa de detalhe.** Círculo de 220 px com `overflow: hidden` e borda grossa, contendo uma versão ampliada da planta que passeia com `translate` (10 s, ida e volta). Um cabo girado a 45° completa a lupa.
7. **Legenda de símbolos.** Lista fixa com parede, porta, caminho liberado e sala trancada. Não muda de uma folha para outra.

## Movimento

- O desenho acompanha a fala: paredes primeiro (1,8 s cada, escalonadas em 0,25 s), depois portas, rótulos, crachá e caminho. O carimbo chega por último.
- Loops só onde há fluxo: caminho liberado (1,2 s linear) e lupa (10 s).
- Nada gira sem motivo. Em movimento reduzido, a planta aparece pronta.

## Aplicação em deck, página e carrossel

- **Deck:** prancha com moldura a 2,4% das bordas, título à esquerda, planta à direita e selo no canto. Cada slide acrescenta uma sala ou uma porta à mesma planta.
- **Página:** hero em folha com a planta grande; seções seguintes como outras folhas da mesma prancha (folha 02 / 04, 03 / 04), com o selo atualizado.
- **Carrossel:** um cômodo por slide, título com uma palavra em marca-texto, cota embaixo e contador mono.

## O que evitar

- Ícones de nuvem, servidor ou cadeado de bibliotecas prontas. Desenhe com poucas linhas.
- Mais de três cores de significado.
- Plantas com tantas salas que nada se lê em 390 px. Divida em folhas.
- Fonte manuscrita ou serifada.
- Sombras difusas e cantos arredondados.

## Checklist

- [ ] Cada sala corresponde a um módulo real do que você explica.
- [ ] Verde só para liberado, vermelho só para trancado, amarelo só para o foco atual.
- [ ] A planta se desenha com `stroke-dashoffset` e aparece pronta sem movimento.
- [ ] Selo técnico e legenda presentes e coerentes.
- [ ] Rótulos legíveis em 390 px.
- [ ] `pycode styles check planta-azul` passa.
