---
version: 1.0.0
name: Noir champanhe
slug: noir-champanhe
description: Preto de sala de cinema, grafite e champanhe, com letreiro largo de trailer, faixas de tela panorâmica, feixe de projetor e créditos. Para aberturas, lançamentos de aula e anúncios com pausa
  dramática.
mode: dark
fonts:
- syncopate
- geist
- geist-mono
best_for:
- deck
- page
- carousel
colors:
  bg: '#050505'
  bg-2: '#0d0c0a'
  surface: '#151410'
  surface-2: '#1e1c17'
  text: '#f8f4ea'
  muted: '#bdb5a3'
  line: '#3b3426'
  accent: '#e8c27e'
  accent-2: '#8fd1f2'
  accent-ink: '#1b160e'
  paper: '#f5ecd7'
  paper-ink: '#1b160e'
  danger: '#f59a7a'
  ok: '#9ad9b0'
  warn: '#ffad5c'
typography:
  display:
    fontFamily: Syncopate
    fontWeight: 700
    letterSpacing: 0.18em
  body:
    fontFamily: Geist
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: Geist Mono
    fontWeight: 400
rounded:
  base: 2px
  large: 4px
elevation:
  shadow: 0 30px 80px rgba(0, 0, 0, .7)
  glow: 0 0 0 1px rgba(232, 194, 126, .22), 0 0 70px rgba(232, 194, 126, .14)
tokens: tokens.css
---

# Noir champanhe

## Visão geral

Noir champanhe conta o conteúdo como um trailer de cinema: preto de sala escura, grafite, marfim e um champanhe que parece luz refletida em metal. O letreiro é largo, em caixa alta e com espaçamento generoso. A tela tem faixas pretas de cinema panorâmico, um feixe de projetor e grão de filme. Cada ideia vira uma cartela, com pausa antes da próxima.

Use para aberturas de aula ou de palestra, anúncios de um novo módulo, convites para uma sessão ao vivo, trailers de conteúdo e carrosséis de capa. Evite para conteúdo de referência (prefira `caderno`), listas longas e explicações passo a passo detalhadas.

## Cores

- `--bg` (#050505) é preto neutro, sem azul. As faixas de cinema são `#000` puro.
- `--surface` e `--surface-2` são grafites quentes para cartelas e painéis.
- `--text` (#f8f4ea) é marfim; `--muted` (#bdb5a3) é para créditos, datas e legendas.
- `--accent` (#e8c27e, champanhe) aparece em fios, no letreiro de data, em bordas finas e no botão.
- `--accent-2` (azul frio) existe só no feixe do projetor, quase transparente.
- Extras: `--noir-champanhe-champagne-gradient` (botão sólido e placas), `--noir-champanhe-letterbox` (altura das faixas, 11vh) e `--noir-champanhe-grain-opacity` (.07).

## Tipografia

Syncopate em caixa alta, peso 700, com `--tracking-display: 0.18em`, só para títulos curtos e cartelas. Geist no corpo. Geist Mono com `letter-spacing: .3em` para datas, atos e créditos.

| Nível | Tamanho | Peso |
|---|---|---|
| letreiro (h1) | `clamp(26px, 5vw, 74px)` | 700, caixa alta, linha 1,08 |
| cartela | `clamp(14px, 1.6vw, 20px)` | 700, tracking .2em |
| h2 | `clamp(24px, 3.2vw, 44px)` | 700 |
| corpo | 17 px | 400 |
| crédito | 11 a 13 px mono | 400, tracking .3em |

Syncopate é muito larga: confira a quebra em 390 px e mantenha títulos com até seis palavras.

## Superfícies e texturas

- **Faixas panorâmicas:** o hero é um grid de três linhas (`11vh 1fr 11vh`), com as faixas pretas carregando informação mínima em mono (sessão, ato, duração).
- **Feixe de projetor:** `conic-gradient` partindo do topo, com fatias quase transparentes de azul frio e marfim. Pisca de leve em degraus.
- **Grão:** SVG com `feTurbulence` como imagem de fundo, em 7% de opacidade, que salta em três posições (`steps(3)`).
- **Cartelas:** preto puro, proporção 2,39:1, moldura dupla (borda em `--line` e um `::before` champanhe a 35%).
- Raio quase zero (2 a 4 px). Cinema não tem cantos arredondados.

## Objetos do estilo

1. **Letreiro de abertura.** Linha pequena em caixa alta ("Estúdio apresenta"), título dividido em grupos de palavras (`span` com `--w`) que aparecem um depois do outro a cada 0,35 s, um fio champanhe que cresce do centro (`scaleX`) e a data em mono champanhe.
2. **Contagem de filme.** Círculo com cruz (pseudo-elementos de 1 px), anel interno e um ponteiro que varre o quadro: `conic-gradient` de 90° girando em 1 s. Os números 3, 2 e 1 se alternam com `opacity` em degraus.
3. **Cartela.** Frase única centralizada em Syncopate e uma etiqueta mono do ato. Fica parada pelo menos 2,5 s.
4. **Claquete.** SVG com a base listrada e o braço superior em um grupo com `transform-origin: 0 100%` que fecha em rotação a cada 4 s. Campos de aula, cena e tomada.
5. **Fita de filme.** Fileira de quadros de 150 px com perfuração (`repeating-linear-gradient` nos pseudo-elementos) deslizando com `translateX(-50%)` em loop, com o conteúdo duplicado.
6. **Créditos.** `dl` centralizada numa janela com `mask-image` em degradê vertical, subindo em 16 s. Fecha a aula com o que foi usado e o próximo encontro.

## Movimento

- Ritmo de trailer: entradas lentas (1,4 s) e escalonadas, com pausa entre ideias.
- Loops: grão (0,9 s em degraus), feixe (3,2 s em degraus), poeira subindo (14 s), fita (12 s), créditos (16 s).
- Nada de zoom rápido ou flash branco.
- Em movimento reduzido, o título aparece inteiro, a contagem mostra o 3 e os créditos ficam parados.

## Aplicação em deck, página e carrossel

- **Deck:** slides com faixas pretas em cima e embaixo (12% da altura), uma frase central em Syncopate e informações de ato e contador nas faixas. Use uma cartela por ideia.
- **Página:** hero de tela quase cheia com faixas, feixe e letreiro; seções seguintes em preto com cartelas, a lista de atos e créditos no rodapé.
- **Carrossel:** pôster 4:5 com feixe no topo, título largo no centro, a data entre dois fios e um bloco de créditos pequeno embaixo.

## O que evitar

- Dourado amarelado ou alaranjado: o champanhe é frio e claro.
- Syncopate em parágrafos ou em textos com mais de seis palavras.
- Fundo com azul ou roxo de "tecnologia".
- Efeitos de flash, tremor e glitch.
- Cartelas que trocam rápido demais para ler.

## Checklist

- [ ] Cada cartela tem uma ideia e fica tempo suficiente para leitura.
- [ ] Letreiro em caixa alta com tracking largo e no máximo seis palavras.
- [ ] O champanhe aparece em fios, data e botão, sem virar fundo.
- [ ] Grão e feixe pausam fora da tela e com movimento reduzido.
- [ ] Título cabe em 390 px sem cortar palavra.
- [ ] `pycode styles check noir-champanhe` passa.
