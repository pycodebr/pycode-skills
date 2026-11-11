# Performance: o padrão e o porquê

O objetivo é a primeira dobra pintar com um único arquivo (o HTML), sem esperar CSS externo, fonte remota ou
script, e o resto da página chegar sem disputar a rede com o que aparece primeiro. O `pycode page build` aplica
este padrão; esta referência explica cada peça para você não desfazê-la sem querer.

## CSS crítico incorporado (até 15 KB)

- `src/css/critical.css` tem só o que a primeira dobra usa: base, header, hero e o objeto do hero. O build junta
  `fonts.css` + `tokens.css` + `critical.css`, minifica com `pycode css` e grava em `<style id="critical-css">`.
- **Por quê**: CSS externo bloqueia a primeira pintura. Incorporado, o navegador pinta assim que o HTML chega.
- **Limite de 15 KB minificado**: acima disso o HTML fica pesado e cada página paga o custo de novo (o CSS
  incorporado não vai para o cache). Se estourar, mova regras de seções abaixo da dobra para `styles.css`.
- O bloco crítico precisa conter a cor de fundo do `body` e a família da fonte. Sem isso a página pisca em branco.
- **Reprodutível**: o build roda duas vezes e compara os arquivos byte a byte. Se diferirem, algo no pipeline
  não é determinístico (data, ordem de arquivos) e o cache vai ser invalidado sem motivo.

## CSS completo sem bloquear

```html
<link rel="preload" href="css/styles.<hash>.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="css/styles.<hash>.css"></noscript>
```

- O `preload` baixa em paralelo e o `onload` aplica quando chega. O `<noscript>` garante o visual completo sem JS.
- O build gera isso a partir de `<link rel="stylesheet" href="css/styles.css" data-defer>`.
- Cuidado: regra no `styles.css` que muda o tamanho de algo da primeira dobra causa salto de layout quando
  chega. Tudo que define geometria da primeira dobra fica no crítico.

## Cache com hash no nome

CSS, JS e fontes saem como `styles.af1e956357.css`, `main.e5b8a02f63.js`, `geist-latin-wght-normal.19f9c92546.woff2`.
O hash é do conteúdo: mudou o arquivo, muda o nome. Por isso esses arquivos podem ter
`Cache-Control: public, max-age=31536000, immutable`, e o HTML fica com `max-age=0, must-revalidate`.
Os arquivos `_headers` e `.htaccess` do projeto já fazem isso. Nunca use `immutable` em arquivo sem hash.

## Fontes locais, preload seletivo e fallback métrico

- As fontes vêm do `pycode vendor` (OFL) e ficam dentro do projeto. Nada de Google Fonts ou CDN em runtime: é
  uma conexão extra antes do texto aparecer, e o build reprova.
- `font-display: swap`: o texto aparece na hora com a fonte local e troca quando a web font chega.
- **Preload só das fontes de título e corpo** (as que pintam a primeira dobra), com `crossorigin`. Pré-carregar
  todas compete com o CSS e o HTML.
- **Fallback métrico**: o `pycode page new` cria `@font-face` com `font-family: 'Geist Fallback'`, `src: local('Arial')`,
  `size-adjust`, `ascent-override` e `descent-override` e coloca essa família logo depois da web font nos tokens.
  As medidas vêm da própria fonte (medidas no Chromium). Por quê: sem isso, a troca de fonte muda a largura das
  linhas e o hero pula, o que aparece como CLS.

## Imagens

- Formatos modernos (WebP, AVIF quando disponível) com `srcset`/`sizes`; `pycode page images` gera as variantes
  e o HTML.
- Sempre `width` e `height` no `<img>` (o navegador reserva o espaço; sem isso há salto de layout).
- A imagem principal da primeira dobra: `loading="eager" fetchpriority="high"`. As demais: `loading="lazy"
  decoding="async"`. Detalhes em `imagens.md`.

## JavaScript

- Um arquivo pequeno, `defer`, sem framework. Tudo é melhoria progressiva: sem JS a página continua legível.
- Nada de animação contínua que rode fora da tela. `IntersectionObserver` liga e desliga cada componente.
- Script de terceiros (tags, chat, vídeo) é o maior custo típico de uma landing page. Veja `tracking.md`.

## `content-visibility` e âncoras

`.section { content-visibility: auto; contain-intrinsic-size: auto 900px; }` faz o navegador pular a
renderização das seções fora da tela. O custo: a altura dessas seções é provisória até serem renderizadas, e
uma âncora calculada com a altura provisória para no lugar errado. O `main.js` do modelo resolve: no clique,
materializa as seções, espera dois quadros, rola até a posição medida (abaixo do header) e confere de novo ao
final da rolagem. O QA testa cada âncora em navegação nova, por posição medida.

## Celular

Sem laços de animação, sem grade de fundo e sem sombras grandes no celular: pintura e composição custam muito
mais num processador de celular, e é ali que o Lighthouse mede com CPU quatro vezes mais lenta. Cor e forma
continuam; só sai o que custa caro. Veja `responsivo.md`.

## Medição

```bash
pycode page perf minha-pagina --runs 3              # serve dist/ com gzip e mede celular e desktop
pycode page perf https://seu-site.com --runs 3      # página publicada
pycode page perf https://seu-site.com --block '*googletagmanager.com*' --block '*facebook.net*'
```

- **Mediana de pelo menos 3 rodadas**: uma rodada isolada varia muito. Informe a mediana e as rodadas.
- **Máquina sozinha**: outro teste de navegador, build ou Lighthouse em paralelo distorce TBT e a nota. O
  comando mostra a carga da máquina e o `benchmarkIndex`; se variar muito entre rodadas, diga que houve rodada
  contaminada em vez de escolher a melhor.
- **`--baseline`** mede, intercalada com cada rodada, uma página HTML mínima (só texto). Se a página mínima
  também perde pontos de TBT, o problema é a máquina, não a sua página. Informe as duas medianas.
- **gzip local**: sem compressão, o HTML com CSS incorporado parece mais pesado do que é. O comando serve com gzip.
- **Página completa e só o que é seu**: com tags de terceiros, meça as duas coisas. A medição com `--block` só
  vale se o bloqueio funcionou: toda requisição bloqueada precisa ter `statusCode -1` e zero bytes; o comando
  confere isso e reprova se algo vazou. Nunca apresente a nota isolada como nota da página publicada.
- **Números absolutos além da nota**: FCP, LCP, TBT, CLS, Speed Index, bytes e requisições.
- SEO baixo pode ser intencional (`noindex` em página só de anúncio). Use `--min-seo 0` nesses casos e diga por quê.

## Gates do modelo

Metas para uma página sem terceiros: Lighthouse celular com performance ≥ 95, acessibilidade ≥ 95, boas
práticas ≥ 95, SEO ≥ 90 e CLS 0. Antes de culpar a página, meça uma página HTML mínima (só texto) na mesma
máquina e no mesmo momento: se ela também perde pontos de TBT, a máquina está ocupada e a medição não serve para
decidir nada. Se a sua página ficar abaixo das metas numa máquina livre, procure nesta ordem: imagem grande sem
`srcset`, fonte extra com preload, CSS crítico acima de 15 KB, animação contínua no celular, script de terceiros
no `<head>`.
