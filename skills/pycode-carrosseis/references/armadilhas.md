# Armadilhas técnicas (e como evitar)

Problemas que já aconteceram em produção de carrosséis com HTML, Chromium e ffmpeg.

## Chromium e Playwright

- **`mask-image` com `file://` some.** A máscara exige CORS e, por arquivo local, não carrega; o elemento desaparece sem erro. Sirva a pasta (`pycode serve`, que os comandos já usam) ou use a máscara como gradiente CSS ou data URI.
- **Fontes "unloaded".** `document.fonts` lista como `unloaded` as faces declaradas e não usadas na página. Checagem de fonte olha só `status === 'error'`; o runtime carrega todas as faces declaradas antes de medir texto.
- **Medir texto antes da fonte carregar** dá largura errada (quebra de código, numeral em canvas, ajuste de fonte). O runtime espera as fontes antes de preencher o texto e antes de chamar `onSlide`.
- **Locale.** Campos de data e números formatados pelo navegador headless saem no formato americano mesmo com `locale="pt-BR"` em algumas versões. Evite controles nativos no slide; escreva datas e números no texto.
- **Filtro SVG pesado.** `feTurbulence` e `feGaussianBlur` em tela cheia são recalculados a cada captura; um vídeo de 150 quadros pode levar vários minutos. Use o ladrilho `var(--grain)`.
- **3D com `backface-visibility`.** Funciona na captura, mas sombra grande em elemento com `perspective` é cara; use sombra curta.
- **IDs repetidos.** Um `<template>` repetido em cada slide repete os IDs de `<filter>` e `<linearGradient>`. Funciona porque o primeiro é igual aos outros; se cada slide precisar de um gradiente diferente, gere IDs com o número do slide.
- **`display: flex` num parágrafo com destaque** quebra a frase em pedaços (cada nó vira item flex). Para centralizar texto na vertical, use `align-content: center` num bloco.

## Vídeo

- **Cor deslocada.** RGB para yuv420p sem a matriz BT.709 usa BT.601 e muda as cores da marca. O comando `video` já converte e marca BT.709; se montar quadros por fora, passe `scale=out_color_matrix=bt709:out_range=tv` e as tags de cor.
- **Sem faststart** o vídeo só toca depois de baixar inteiro.
- **`or` com zero.** Em Python, `still or padrão` troca um `still` igual a 0 pelo padrão; use `is not None` quando zero é um valor válido (pôster no quadro 0).
- **Som adiantado.** Efeito alinhado pelo início do arquivo toca antes do evento; alinhe pelo pico medido.
- **Pico estourando depois do AAC.** O encoder soma cerca de 1 dB; meça o MP4 final, não só o WAV.
- **Normalização em clipe curto.** O filtro `loudnorm` de passada única erra em trechos de poucos segundos; meça a loudness integrada e aplique ganho com limitador (é o que o `--normalize` faz).

## Imagem

- **Corte central às cegas** de uma cena 2:3 corta a cabeça do objeto ou o chão. Use `pycode carousel fit`, que mede o conteúdo.
- **Magenta vazando** na moldura deixa a tela arroxeada. O `compose` remove o excesso num raio em volta da máscara; se a cena tiver reflexo magenta forte, gere de novo pedindo "no reflections".
- **Proporção do conteúdo na tela:** use a do aparelho, não a do quadrilátero em perspectiva.

## Texto

- **Travessão e reticências** escapam fácil em texto gerado; rode `pycode text` em `slides.json` e `legenda.md`.
- **Acentos.** Revise a acentuação palavra por palavra; agentes treinados em outras línguas perdem acentos com frequência.
- **Lista em `options`** com colchetes (`[1, 2, 3]`) é texto válido; marcador de modelo é colchete com palavras (`[título do slide 2]`), e o QA reprova esse.
