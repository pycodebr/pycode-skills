# Anatomia do projeto, `slides.json` e runtime

```
pasta/
  index.html          estrutura: <template data-layout> por tipo de slide (ou <section class="slide"> fixas)
  slides.json         todo o texto do carrossel (fonte única)
  css/tokens.css      tokens do estilo escolhido (gerado pelo new; troque com outro --style)
  css/fonts.css       @font-face das fontes locais (gerado)
  css/base.css        base comum: slide 1080x1350, âncoras, trilho, código (não edite)
  css/scene.css       o visual do conceito (edite)
  js/carousel.js      runtime (não edite)
  js/scene.js         desenho e animação do conceito (edite)
  js/slides-data.js   espelho do slides.json para abrir por file:// (gerado pelos comandos)
  fonts/              woff2 + licenças OFL
  licencas/           licenças de som e de imagem de banco usadas no post
  out/                slide-01.png, slide-01.mp4, slide-01-poster.jpg, folha-de-contato.jpg
  qa/relatorio.json   resultado do último QA
  legenda.md          legenda (esqueleto pelo caption, texto final seu)
  preview.html        prévia no celular
```

## `slides.json`

```json
{
  "meta": {"title": "...", "slug": "...", "lang": "pt-BR", "concept": "...", "style": "orbital"},
  "brand": {"name": "Sua Marca", "handle": "@suamarca"},
  "rules": {"cover_words": 20, "slide_words": 35, "safe": 64, "min_font": 24, "min_body_font": 34, "contrast": 4.5},
  "ui": {"station": "ESTAÇÃO"},
  "slides": [
    {"layout": "cover", "title": "...", "video": {"seconds": 5, "still": 5}, "rail": {"start": [150, 1105], "out": 1105}},
    {"layout": "card", "title": "...", "body": "texto com *destaque*",
     "code": {"lines": [">>> 2 + 2", "4"], "run": "doctest"}, "keywords": ["..."]},
    {"layout": "cta", "title": "...", "cta": "o único pedido de ação", "rail": {"in": 1105, "end": [985, 1105]}}
  ]
}
```

- `layout` escolhe o `<template data-layout="...">` do `index.html`. Sem `layout`, o slide 1 é `cover`, o último é `cta` e os outros `content`.
- `title`, `body` e `cta` são contados no orçamento de palavras. `labels`, `options` e `ui` guardam rótulos curtos do conceito (também passam pelo `pycode text`). `keywords` alimenta o esqueleto da legenda.
- `*palavra*` vira destaque; `\n` vira quebra de linha.
- `brand` é preenchido pelo `new` a partir de `pycode brand`.
- `rules` muda os limites do QA para o post (use com motivo).

### Código e comandos (`code`)

| Campo | O QA faz |
|---|---|
| `"run": "doctest"` | roda as linhas `>>>` e compara a saída mostrada com a saída real do Python |
| `"run": "python", "expect": "105"` | roda o trecho e compara o que ele imprime com `expect` |
| `"run": "python"` sem `expect` | só confere que o trecho roda sem erro |
| `"source": "fontes/README.md"` | confere que o texto aparece literalmente no arquivo (comando copiado de documentação oficial, baixada para a pasta) |
| `"check": "literal"` | só confere que o slide mostra exatamente as linhas (texto que não é Python, como SQL ou HTTP ilustrativo) |

Em todos os casos o QA lê as linhas renderizadas no DOM e compara com `lines`, uma a uma. Quiz: `"quiz": {"options": [...], "answer": "B"}` é conferido contra a saída real do `run: python`.

### Trilho contínuo (`rail`)

- `in`: altura em que o trilho entra pela borda esquerda; `out`: altura em que sai pela direita. A saída do slide N precisa ser igual à entrada do N+1.
- `start` e `end`: ponto onde o trilho começa (primeiro slide) ou termina (último).
- `via`: pontos por onde ele passa no meio do slide; `nodes`: marcadores.
- O runtime desenha uma curva suave com tangente horizontal nas bordas, então a emenda encaixa em altura e em ângulo. A cor vem de `--accent` e a espessura de `--rail-width`.
- O QA renderiza cada slide só com o trilho e mede os pixels da última coluna e da primeira coluna do slide seguinte.

## Runtime (`window.Carousel`)

| API | Uso |
|---|---|
| `Carousel.onSlide(n, fn)` | desenha o slide `n` (ou `'*'` para todos) depois que o texto entrou: `fn(slideEl, dadosDoSlide, n, C)` |
| `Carousel.animate(n, fn, {duration})` | registra o slide em vídeo; `fn(t, slideEl, dados)` |
| `Carousel.data` | o `slides.json` inteiro |
| `Carousel.token('--accent')` | valor de um token (para canvas) |
| `Carousel.renderCode(el, code)` | renderiza código criado por você (quebra só entre tokens, sem ligaduras) |
| `Carousel.richText(el, texto)` | aplica `*destaque*` e `\n` num elemento criado por você |
| `Carousel.rng(semente)` | aleatório determinístico |
| `Carousel.prog(t, t0, d)`, `Carousel.ease.out/inOut/back` | curvas de animação |
| `var(--grain)` | ladrilho de ruído para textura |

Marcações no HTML:

- `data-field="body"` (ou `card.name`, `quiz.options.0`): o texto vem desse caminho do slide.
- `data-code="code"`: bloco de código exato.
- `data-anchor="brand" | "handle" | "counter"`: âncoras da marca. Sem nenhuma, o runtime põe nome e contador no topo.
- `<template id="slide-common">`: fundo, textura e âncoras repetidos em todos os slides.
- `aria-hidden="true"` ou `data-decor`: texto decorativo (textura de código, rótulos dentro de ilustração); o QA ignora.
- `data-placeholder`: marcador do modelo; o QA reprova enquanto existir.
- `data-fit` e `data-fit-min="28"`: reduz a fonte até o texto caber na caixa.

Parâmetros de URL usados pelos comandos: `?only=N` (um slide em 1080x1350), `&capture=1` (sem transição CSS) e `&t=2.5` (tempo inicial). Para revisar no navegador: `pycode serve pasta` e abra `/index.html`.
