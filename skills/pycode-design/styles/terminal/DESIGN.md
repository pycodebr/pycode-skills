---
version: 1.0.0
name: Terminal
slug: terminal
description: Editor de código escuro e neutro com abas, explorador, terminal com cursor, sublinhado de erro, barra de status e diffs. Tudo acontece nos espaços nativos da ferramenta. Para tutoriais, live
  coding e documentação técnica.
mode: dark
fonts:
- jetbrains-mono
best_for:
- deck
- page
- carousel
colors:
  bg: '#1e1e1e'
  bg-2: '#181818'
  surface: '#252526'
  surface-2: '#2d2d30'
  text: '#e4e4e4'
  muted: '#a8a8a8'
  line: '#3c3c3c'
  accent: '#4fc1ff'
  accent-2: '#dcdcaa'
  accent-ink: '#001a2b'
  paper: '#d4d4d4'
  paper-ink: '#1e1e1e'
  danger: '#f48771'
  ok: '#89d185'
  warn: '#cca700'
  keyword: '#569cd6'
  string: '#ce9178'
  function: '#dcdcaa'
  comment: '#6a9955'
  type: '#4ec9b0'
  number: '#b5cea8'
  statusbar: '#007acc'
  selection: '#264f78'
typography:
  display:
    fontFamily: JetBrains Mono
    fontWeight: 700
    letterSpacing: -0.02em
  body:
    fontFamily: JetBrains Mono
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: JetBrains Mono
    fontWeight: 400
rounded:
  base: 4px
  large: 8px
elevation:
  shadow: 0 12px 32px rgba(0, 0, 0, .5)
  glow: '0 0 0 1px #007acc'
tokens: tokens.css
---

# Terminal

## Visão geral

Terminal é a gravação de tela de um editor de código escuro e neutro. Nada de cartões por cima: cada ideia acontece num espaço nativo da ferramenta, como abas, explorador de arquivos, paleta de comandos, sublinhado de erro, balão de explicação, terminal, diff e barra de status. A sensação é ver alguém construindo a solução ao vivo.

Use para tutoriais de programação, live coding, aulas de testes e depuração, documentação técnica e carrosséis de "erro comum". Evite para públicos que ainda não programam (prefira `lousa` ou `caderno`) e para conteúdo sem código.

## Cores

- `--bg` (#1e1e1e) é o editor; `--bg-2` a barra de atividades, a barra de título e o terminal.
- `--surface` e `--surface-2` são explorador, abas inativas, balões e paleta de comandos.
- `--text` (#e4e4e4) é o código; `--muted` (#a8a8a8) são caminhos, rótulos de interface e números de linha.
- `--accent` (#4fc1ff) é foco, cursor de seleção e botão.
- `--danger` é o sublinhado de erro e o teste que falhou; `--ok` o teste que passou e as linhas adicionadas.
- Extras de sintaxe: `--terminal-keyword`, `-string`, `-function`, `-comment`, `-type`, `-number`, mais `--terminal-statusbar` (#007acc) e `--terminal-selection`.

O fundo é cinza neutro, sem azul, para não competir com a sintaxe. A barra de status é a única faixa de cor sólida.

## Tipografia

JetBrains Mono em todos os níveis, com o peso fazendo a hierarquia. Funciona porque os blocos de texto são curtos.

| Nível | Tamanho | Peso |
|---|---|---|
| h1 com prompt | `clamp(30px, 4vw, 56px)` | 700, precedido de "$ " em azul |
| h3 | 22 px | 700 |
| código | 14 px, linha 1,65 | 400 |
| corpo | 15 px, linha 1,7 | 400 |
| interface | 11 a 12 px | 400 a 500 |

Títulos em minúsculas, como comandos. Limite a linha de texto a 70 caracteres.

## Superfícies e texturas

- Janela do editor com raio de 8 px e sombra (`--shadow`), dividida em barra de título, barra de atividades (48 px), explorador (220 px), abas, área de código com números de linha, terminal e barra de status.
- Divisões de 1 px em `--line`. Sem degradês e sem texturas.
- Aba ativa: fundo do editor e uma linha de 2 px azul no topo.

## Objetos do estilo

1. **Janela do editor.** Grid `48px 220px 1fr` com explorador em árvore (`li` com recuo por `--l`), abas, código com `span` de sintaxe e números de linha em coluna própria. No celular, esconda barra de atividades e explorador.
2. **Sublinhado de erro.** `text-decoration: underline wavy var(--danger)` no trecho errado.
3. **Balão de explicação.** Caixa `--surface-2` com borda de 1 px e sombra, posicionada logo abaixo da linha com erro. Aparece e some em degraus.
4. **Terminal.** Abas "PROBLEMAS" e "TERMINAL", comando com `$` e linhas de saída que surgem uma por vez (`opacity` em `steps(1)`, atraso de 0,35 s por linha). Saída sempre real.
5. **Paleta de comandos.** Campo com "> termo" e lista de resultados com as letras digitadas em destaque azul e atalhos à direita. A seleção é um bloco absoluto que desce em degraus com `translateY`.
6. **Diff.** Linhas com fundo tingido: vermelho a 14% para removidas, verde a 14% para adicionadas, prefixos `-` e `+`.
7. **Notificação.** Caixa no canto inferior direito com um ponto verde, que entra e sai com `translateX`.
8. **Barra de status.** Faixa azul com branch, contagem de erros, posição do cursor, codificação e linguagem.

## Movimento

- Movimento só onde a ferramenta se mexe de verdade: cursor piscando (1 s), linhas do terminal, balão de erro, seleção da paleta, notificação.
- Tudo em degraus ou com `cubic-bezier(.2, .8, .2, 1)` curto na notificação.
- Em movimento reduzido: saída completa, balão visível, cursor parado.

## Aplicação em deck, página e carrossel

- **Deck:** o slide é o editor: abas em cima (o nome do slide é uma aba), título e explicação à esquerda, código à direita, barra de status com o número do slide.
- **Página:** hero com o h1 em forma de comando e a janela do editor inteira embaixo; seções com blocos de código e listas numeradas.
- **Carrossel:** barra de título com o nome do arquivo, um comentário de código como título (`# o teste falha primeiro`), o trecho com erro e a barra de status com o @ e o contador.

## O que evitar

- Bolinhas vermelha, amarela e verde de janela de outro sistema operacional como enfeite.
- Fundo azul-marinho (isso é o estilo `python-noturno`).
- Código que não roda ou saída inventada.
- Paletas de sintaxe com cores saturadas demais.
- Títulos em caixa alta.

## Checklist

- [ ] Toda ideia aparece num espaço nativo do editor.
- [ ] Código executado e saída copiada da execução real.
- [ ] Sublinhado de erro e balão posicionados na linha certa.
- [ ] Explorador e barra de atividades escondidos no celular.
- [ ] Linhas longas de código não criam rolagem horizontal na página.
- [ ] `pycode styles check terminal` passa.
