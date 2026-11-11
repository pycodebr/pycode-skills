# Exportação: PNG, PDF e PPTX

```bash
pycode deck stills <pasta>                 # stills/NN-id.png (1920×1080) + stills/stills.json + folha de contato
pycode deck export <pasta> --pdf --pptx    # exports/<slug>.pdf e exports/<slug>.pptx
pycode deck export <pasta> --pdf --reuse   # reaproveita stills/ (sem capturar de novo)
```

## O que cada formato guarda

| Formato | Conteúdo | Limites |
|---|---|---|
| PNG | o estado final de cada cena (`?still`), sem barra de controles | sem animação nem clique |
| PDF | uma cena por página (16:9, 960×540 pt), imagem JPEG e uma camada de texto invisível posicionada sobre cada linha | o texto é pesquisável e selecionável, não editável; caracteres fora do Windows-1252 viram "?" só na camada de busca |
| PPTX | uma imagem por slide e, nas notas, o título, o texto visível da cena e as notas de fala (`notes`) | o design é imagem: não há texto editável como objeto nem animações; feito sem bibliotecas extras |

Nenhum dos três substitui o HTML: a aula interativa é o entregável principal; PDF e PPTX servem para arquivo,
impressão e para quem precisa abrir no PowerPoint, no Keynote ou no Google Slides.

## Verificações

O `export` confere o que gerou: número de páginas do PDF, presença das palavras dos títulos na camada de texto,
integridade do ZIP do PPTX, partes obrigatórias (slide, imagem e notas de cada cena) e XML bem formado. Para conferir
por fora, quando houver as ferramentas na máquina:

```bash
pdftotext -f 1 -l 1 exports/<slug>.pdf -          # texto da primeira página
soffice --headless --convert-to pdf exports/<slug>.pptx   # o LibreOffice abre o PPTX?
```

## Quando a pessoa quer slides editáveis

Explique o limite: o deck é HTML com objetos desenhados em código; convertê-lo em formas editáveis do PowerPoint
perde o movimento e a interação e exigiria redesenhar cada cena. Se ela precisar mesmo de um arquivo editável,
ofereça montar uma versão simplificada à parte, com título e texto por slide, usando a ferramenta de apresentações que
ela já usa.
