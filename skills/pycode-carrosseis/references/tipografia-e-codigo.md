# Tipografia, fontes pixel e código exato no slide

## Tamanhos para o celular

O slide tem 1080 px de largura e aparece com uns 390 px no celular, quase três vezes menor. Por isso:

- Corpo de texto com pelo menos 34 px (o QA cobra `min_body_font`), de preferência 36 a 44 px.
- Rótulos, âncoras e código com pelo menos 24 px (`min_font`).
- Título de capa entre 72 e 96 px, com `text-wrap: balance`.
- Alinhe à esquerda texto de mais de duas linhas; centralizado só em título curto.

## Fontes

- As fontes vêm do `vendor` (OFL), copiadas para `fonts/` pelo `new`, com as licenças. Nada de CDN.
- Os arquivos do vendor têm o subconjunto latino: acentos do português estão lá, mas setas (→), símbolos (✓, ↪) e emoji não. Se o texto precisar de um símbolo, desenhe em SVG ou CSS; senão o navegador troca de fonte só naquele caractere e o desenho fica diferente.
- O QA reprova texto visível cuja fonte não tem arquivo carregado (caiu na fonte do sistema).
- Para checar fontes no Playwright, olhe só `status === 'error'` em `document.fonts`: fontes declaradas e não usadas ficam como `unloaded`, e isso não é erro.

## Fontes pixel (fliperama e afins)

- **Press Start 2P** é muito larga e o `)` parece `>`. Use só em rótulos curtos sem parênteses ("FASE 1", "HIGH SCORE", "PRESS START") e em título de capa curto. Letra de opção vai num quadrado ("A"), não como "A)".
- **VT323** funciona para código e números (dígitos claros). Como corpo de texto, use 44 px ou mais.
- **Jersey 10** é condensada e tem acentos; o `1` dela parece `l`, então evite em código e números.
- Antes de montar os slides, renderize uma linha de teste com todas as fontes do post (por exemplo "Ação você 1 l I ) > 0 O") e confira por visão.
- Pixel art em canvas: desenhe em baixa resolução (180x225) e amplie com `image-rendering: pixelated`. Suavização ligada borra o pixel.

## Código e comandos exatos

- Bloco de código com a classe `.code` (ou `data-code` no HTML): fonte mono, `font-variant-ligatures: none` e `font-feature-settings: "liga" 0, "calt" 0`. Com ligadura, `!=` vira `≠` e `://` muda de forma. O QA reprova bloco com ligadura.
- As cores de sintaxe saem da mistura da cor de destaque com a tinta do código (`--code-ink`, padrão `var(--text)`), na proporção `--code-tint` (padrão 55%). Código sobre papel claro usa `--code-ink: var(--paper-ink); --code-tint: 35%`; assim o contraste passa mesmo quando o destaque do estilo é claro (dourado sobre papel, por exemplo).
- Quebra só entre tokens (espaço, barra, vírgula, parêntese, barra vertical): o runtime quebra sozinho quando a linha não cabe e marca a continuação com um recuo. Se nem assim couber (um token maior que a linha), o QA acusa transbordo: diminua a fonte ou alargue a caixa.
- As linhas vêm do `slides.json` e o QA compara o DOM renderizado com elas, linha a linha. Comando copiado de documentação vai com `source` apontando para o arquivo baixado.
- Saída mostrada no slide é saída real: `run: doctest` ou `run: python` com `expect`. Nada de saída digitada de memória.
- Repita na legenda o comando completo de qualquer linha que quebrou no slide.
- Nome de pacote, URL e comando nunca saem de gerador de imagem.

## Numeral gigante

Desenhe em `<canvas>` com `measureText` e alinhe pela altura real do glifo (`actualBoundingBoxAscent`). Com texto HTML, a caixa da linha muda de fonte para fonte e o numeral sai deslocado. O canvas fica fora do QA de texto (é decorativo), então o número também precisa estar no texto do slide ("NÍVEL 3 DE 5").
