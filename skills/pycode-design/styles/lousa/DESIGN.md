---
version: 1.0.0
name: Lousa de giz
slug: lousa
description: Ardósia verde com marcas de apagador, moldura de madeira e giz em quatro cores fixas, com diagramas que se desenham enquanto a explicação avança. Para aulas conceituais, comparações e passo
  a passo.
mode: dark
fonts:
- caveat
- inter
- geist-mono
best_for:
- deck
- carousel
- page
colors:
  bg: '#1d2f27'
  bg-2: '#172720'
  surface: '#24392f'
  surface-2: '#2c4438'
  text: '#f1eee3'
  muted: '#c3cbbf'
  line: '#5b7466'
  accent: '#f4dc72'
  accent-2: '#9fd2ee'
  accent-ink: '#2a2306'
  paper: '#f1eee3'
  paper-ink: '#1d2f27'
  danger: '#f2a7bd'
  ok: '#b8e3a1'
  warn: '#f4dc72'
  chalk-white: '#f1eee3'
  chalk-yellow: '#f4dc72'
  chalk-blue: '#9fd2ee'
  chalk-pink: '#f2a7bd'
  frame: '#6b4a2c'
  frame-light: '#8a6440'
typography:
  display:
    fontFamily: Caveat
    fontWeight: 700
    letterSpacing: 0em
  body:
    fontFamily: Inter
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: Geist Mono
    fontWeight: 400
rounded:
  base: 4px
  large: 10px
elevation:
  shadow: 0 18px 40px rgba(0, 0, 0, .4)
  glow: 0 0 18px rgba(241, 238, 227, .14)
tokens: tokens.css
---

# Lousa de giz

## Visão geral

Lousa de giz transforma a explicação numa aula de quadro: ardósia verde com marcas de apagador, moldura de madeira, bandeja com bastões de giz e diagramas que se desenham no ritmo da fala. Cada cor de giz representa uma categoria do começo ao fim. A sensação é de professor desenhando para você entender, não de apresentação corporativa.

Use para aulas conceituais, comparações, explicações de "como funciona", passo a passo com diagramas e carrosséis didáticos. Evite para páginas de venda, conteúdo institucional e documentação de referência.

## Cores

- `--bg` (#1d2f27) é a ardósia; `--bg-2` é o verde mais escuro perto da moldura e fora da lousa.
- `--text` (#f1eee3) é o giz branco: estrutura, caixas e nós.
- `--accent` (#f4dc72) é o giz amarelo; `--accent-2` (#9fd2ee) é o giz azul; `--danger` (#f2a7bd) é o giz rosa.
- `--muted` é giz meio apagado, para notas; `--line` é traço fraco.
- `--paper` é a folha de caderno presa na lousa, com tinta `--paper-ink`.
- Extras: `--lousa-chalk-white`, `-yellow`, `-blue`, `-pink` (as quatro cores fixas), `--lousa-frame` (#6b4a2c) e `--lousa-frame-light`.

Combine o significado das cores no início da aula (exemplo: amarelo é o pedido, azul é a resposta, rosa é o erro) e mantenha até o fim.

## Tipografia

Caveat em peso 700 para títulos e rótulos escritos na lousa, sempre grandes (a partir de 24 px). Inter para o texto de apoio. Geist Mono só para código e contadores.

| Nível | Tamanho | Peso |
|---|---|---|
| título | `clamp(52px, 6.6vw, 98px)` | 700, linha .95 |
| rótulo no diagrama | 26 a 30 px | 700 |
| nota | 24 px | 400 |
| corpo | 17 a 18 px | 400 (Inter) |

Caveat pequena fica ilegível: abaixo de 22 px, use Inter.

## Superfícies e texturas

- **Ardósia:** três `radial-gradient` claros a 4 a 7% simulam marcas de apagador, mais um `repeating-linear-gradient` em diagonal a 2,5%.
- **Moldura:** `box-shadow: inset` em camadas: 10 a 18 px de madeira, 2 px de madeira escura e uma sombra interna.
- **Bandeja:** faixa de 22 px com degradê de madeira, bastões de giz de 9 px e um apagador.
- **Traço de giz:** filtro SVG `feTurbulence` + `feDisplacementMap` (escala 2,6) aplicado aos traços, com `stroke-linecap: round`. O filtro é estático; só o desenho anima.

## Objetos do estilo

1. **Diagrama desenhado ao vivo.** Caixas tortas (polígonos com cantos levemente desalinhados), setas curvas e um cilindro para banco. Cada `path` tem `pathLength="1"` e `stroke-dashoffset` de 1 para 0, escalonado em 0,45 s. Os rótulos em Caveat aparecem depois do traço.
2. **Círculo de giz.** Elipse aberta, com começo e fim desencontrados, desenhada em volta da palavra que importa, em rosa ou amarelo.
3. **Seta curva.** Uma curva Bézier com a ponta desenhada por último.
4. **Caixa de definição.** Retângulo torto com "termo =" em amarelo e a frase em branco. Fica num canto até o fim da aula.
5. **Tabela de giz.** Uma linha horizontal e uma vertical, títulos das colunas nas cores das categorias.
6. **Bandeja de giz.** Legenda fixa das quatro cores, com um bastão de cada cor e o significado ao lado.
7. **Ponto viajante.** Um círculo pequeno que percorre a seta do pedido e volta pela seta da resposta, mostrando o fluxo.

## Movimento

- O desenho segue a ordem da fala: caixa, seta, rótulo, próxima caixa.
- Traço: 1,4 s por elemento, easing `cubic-bezier(.5, 0, .3, 1)`.
- Loops: ponto viajante (4,5 s) e leve balanço da caixa de definição (rotação de 1,5° em 6 s).
- Em movimento reduzido, o quadro aparece completo.

## Aplicação em deck, página e carrossel

- **Deck:** a lousa ocupa o slide inteiro com moldura de 1,4% da largura; título em Caveat à esquerda e diagrama à direita. Cada slide acrescenta um traço ao diagrama anterior.
- **Página:** hero com a lousa grande e a bandeja embaixo; seções com folhas de caderno presas na lousa para os resumos.
- **Carrossel:** um conceito por slide, com a palavra circulada e uma nota curta embaixo.

## O que evitar

- Trocar o significado de uma cor no meio da aula.
- Caveat em parágrafos ou abaixo de 22 px.
- Diagramas perfeitos e retos: perdem o caráter de giz.
- Fundo preto puro ou verde saturado.
- Muitos elementos ao mesmo tempo: a lousa tem que respirar.

## Checklist

- [ ] Legenda das quatro cores combinada e respeitada.
- [ ] O diagrama aparece na ordem da explicação.
- [ ] Rótulos em Caveat com pelo menos 24 px.
- [ ] Texto de apoio em Inter com contraste acima de 4,5:1.
- [ ] Diagrama completo em movimento reduzido.
- [ ] `pycode styles check lousa` passa.
