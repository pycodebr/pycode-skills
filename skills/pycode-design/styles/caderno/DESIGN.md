---
version: 1.0.0
name: Caderno
slug: caderno
description: 'Documento claro de estudo: tela cinza-quente, folhas brancas, tinta quase preta e um único azul de ação, com adesivos coloridos só como decoração. Para painéis, apostilas, guias e material
  de aula.'
mode: light
fonts:
- inter
- jetbrains-mono
best_for:
- page
- deck
colors:
  bg: '#f6f5f4'
  bg-2: '#efedea'
  surface: '#ffffff'
  surface-2: '#f9f8f7'
  text: '#1f1e1c'
  muted: '#5f5c57'
  line: '#e3e0db'
  accent: '#0067c5'
  accent-2: '#d9730d'
  accent-ink: '#ffffff'
  paper: '#ffffff'
  paper-ink: '#1f1e1c'
  danger: '#c4332b'
  ok: '#2f7d4f'
  warn: '#a35c00'
  sticker-yellow: '#fbe9a7'
  sticker-green: '#d6efdd'
  sticker-pink: '#f9d9e3'
  sticker-blue: '#d8e8f8'
  sticker-orange: '#fbe0c8'
  highlight: '#fff2a8'
typography:
  display:
    fontFamily: Inter
    fontWeight: 700
    letterSpacing: -0.025em
  body:
    fontFamily: Inter
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: JetBrains Mono
    fontWeight: 400
rounded:
  base: 6px
  large: 12px
elevation:
  shadow: 0 1px 2px rgba(31, 30, 28, .06), 0 8px 24px rgba(31, 30, 28, .07)
  glow: 0 0 0 3px rgba(0, 103, 197, .18)
tokens: tokens.css
---

# Caderno

## Visão geral

Caderno é um documento claro de estudo: uma tela cinza-quente em volta de folhas brancas, tinta quase preta e um único azul de ação. Os adesivos coloridos (amarelo, verde, rosa, azul-claro e laranja) aparecem só em etiquetas, capas e ícones. Tudo parece um documento vivo, feito de blocos: propriedades, chamadas, listas que abrem, tarefas, tabelas e quadros.

Use para apostilas, guias de estudo, painéis de acompanhamento, materiais de apoio de aula, documentação interna e páginas de "como funciona". Evite para lançamentos e páginas que precisam de impacto visual (prefira `orbital`, `noir-champanhe` ou `python-noturno`).

## Cores

- `--bg` (#f6f5f4) é a tela em volta da folha. `--bg-2` serve para barra lateral e colunas de quadro.
- `--surface` (#ffffff) é a folha. `--surface-2` é o fundo de chamada, de bloco de código e de hover.
- `--text` (#1f1e1c) é a tinta de leitura; `--muted` (#5f5c57) é para propriedades e legendas.
- `--accent` (#0067c5) é a única cor estrutural: links, botão principal, item ativo e caixa marcada.
- `--accent-2` (laranja) marca pendências pontuais.
- Extras de adesivo: `--caderno-sticker-yellow`, `-green`, `-pink`, `-blue`, `-orange` e `--caderno-highlight` (marca-texto). Eles nunca organizam a página; só etiquetam.

## Tipografia

Inter em toda a página, com a hierarquia feita pelo peso. JetBrains Mono só em código, atalhos e caminhos.

| Nível | Tamanho | Peso |
|---|---|---|
| título da página | `clamp(34px, 4.6vw, 58px)` | 700, tracking -0.025em |
| h2 de bloco | 24 px | 700 |
| título de toggle | 16 px | 600 |
| corpo | 16 px, linha 1,6 | 400 |
| propriedade | 14 a 15 px | 400, em `--muted` |

O texto de leitura fica entre 60 e 70 caracteres por linha. Use frases completas: o estilo é calmo, então o texto também precisa ser.

## Superfícies e texturas

- Folha branca com raio de 12 px e sombra baixa em duas camadas (`--shadow`).
- Capa da página: faixa de 120 a 200 px com formas grandes em cores de adesivo (círculos sobrepostos), sem foto de banco.
- Ícone da página: quadrado branco de 78 px com um desenho simples em SVG, metade sobre a capa.
- Divisões por fios de 1 px em `--line`. Nada de borda grossa ou faixa colorida na lateral.

## Objetos do estilo

1. **Página com propriedades.** `article` com capa, ícone, título e uma `dl` de propriedades (rótulo à esquerda em 150 px, valor à direita). Valores podem ser etiquetas de adesivo (`span` com fundo da cor e raio de 4 px).
2. **Chamada.** Bloco com fundo `--surface-2`, contorno interno de 1 px e um ícone desenhado em SVG (círculo de cor de adesivo com um sinal). Nunca uma barra colorida à esquerda.
3. **Lista que abre.** `details` e `summary` nativos, com o triângulo feito em CSS (`border`) que gira 90° quando abre. Funciona sem JavaScript, com teclado e leitor de tela.
4. **Lista de tarefas.** Caixa de 18 px com borda; a marcada usa `::after` azul com o sinal de visto em SVG embutido. A animação marca uma tarefa por vez (`opacity` e `scale`).
5. **Tabela-base.** `table` com cabeçalho cinza, linhas finas, primeira coluna em peso 600 e uma coluna de etiquetas por tipo.
6. **Quadro de tarefas.** Três colunas `--bg-2` com cartões brancos. Um cartão atravessa as colunas com `translateX` para mostrar o fluxo.
7. **Marca-texto.** `::before` amarelo atrás de um trecho, crescendo com `scaleX` a partir da esquerda.

## Movimento

- Mínimo e funcional: marca-texto (1,2 s), tarefas sendo marcadas (ciclo de 8 s), cartão atravessando o quadro (9 s) e formas da capa flutuando devagar (14 s).
- Entradas com subida curta de 18 px. Nenhum elemento gira ou pulsa.
- Toggle e hover usam `transition` de 0,2 s.
- Movimento reduzido mostra tudo no estado final (tarefas marcadas, marca-texto inteiro).

## Aplicação em deck, página e carrossel

- **Página:** documento centralizado de até 1080 px, ou layout com barra lateral (sumário com o item ativo em branco) e conteúdo à direita.
- **Deck:** slide branco com trilha de navegação em cima ("Guia de estudo / Códigos de resposta"), título em 700 e uma tabela ou lista grande. Bom para aulas de referência.
- **Carrossel:** checklist numa folha branca sobre a tela cinza, com título curto e contador simples. Formato de salvamento.

## O que evitar

- Mais de uma cor estrutural. Se o verde virou botão, o estilo quebrou.
- Cards com sombra forte e raio grande.
- Ícones de emoji no lugar dos ícones desenhados.
- Capa com foto genérica ou degradê.
- Inter em peso 300 ou texto cinza-claro de baixo contraste.

## Checklist

- [ ] Só o azul tem papel estrutural; adesivos só etiquetam.
- [ ] Hierarquia feita por peso e tamanho, sem caixas extras.
- [ ] Toggles com `details` nativo.
- [ ] Linha de leitura entre 60 e 70 caracteres.
- [ ] Contraste de `--muted` sobre a folha acima de 4,5:1.
- [ ] `pycode styles check caderno` passa.
