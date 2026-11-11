# Catálogo de objetos reutilizáveis

Trechos curtos e próprios para construir os objetos mais usados dos estilos. Todos usam só variáveis do contrato (e, quando indicado, um extra do estilo), funcionam sem imagem e animam só `transform`, `opacity` ou traço.

## Ingresso com canhoto e recortes

```html
<div class="ticket">
  <div class="ticket-main"><small>encontro 04</small><strong>Autenticação</strong></div>
  <div class="ticket-stub"><b>A12</b></div>
</div>
```
```css
.ticket { display: grid; grid-template-columns: 3fr 1fr; color: var(--paper-ink); filter: drop-shadow(0 16px 28px #0007); }
.ticket-main, .ticket-stub { background: var(--paper); padding: 18px; }
.ticket-stub { border-left: 2px dashed color-mix(in srgb, var(--paper-ink) 35%, transparent); }
/* recortes reais: cada metade da peça leva um furo, sem depender da cor do fundo */
.ticket-main { mask: radial-gradient(circle 11px at 100% 0, #0000 98%, #000) top / 100% 51% no-repeat,
                     radial-gradient(circle 11px at 100% 100%, #0000 98%, #000) bottom / 100% 51% no-repeat; }
.ticket-stub { mask: radial-gradient(circle 11px at 0 0, #0000 98%, #000) top / 100% 51% no-repeat,
                     radial-gradient(circle 11px at 0 100%, #0000 98%, #000) bottom / 100% 51% no-repeat; }
```

A sombra fica no elemento pai (com `filter`), porque a máscara cortaria a sombra do próprio elemento.

## Traço que se desenha

```html
<svg viewBox="0 0 400 200"><path class="draw" pathLength="1" d="M20 20 H380 V180 H20 Z"/></svg>
```
```css
.draw { fill: none; stroke: var(--text); stroke-width: 3; stroke-dasharray: 1; stroke-dashoffset: 0;
        transition: stroke-dashoffset 1.6s cubic-bezier(.6,0,.3,1); }
html.js [data-scene]:not([data-entered]) .draw { stroke-dashoffset: 1; }
```

`pathLength="1"` normaliza o comprimento, então o mesmo CSS serve para qualquer caminho. Escalone com `transition-delay: calc(var(--d) * .25s)`.

## Sinal percorrendo uma rede

```css
.signal { stroke: var(--accent-2); stroke-width: 2; fill: none; stroke-dasharray: 6 330;
          animation: signal 8s linear infinite; }
@keyframes signal { to { stroke-dashoffset: -336; } }
```

Use o mesmo `d` das linhas da rede num `path` por cima, com a classe `loop`.

## Numeral com dígito vazado

```html
<p class="numeral" aria-hidden="true">0<span>3</span></p>
```
```css
.numeral { font: var(--weight-display) clamp(120px, 17vw, 230px)/.8 var(--font-display); color: var(--accent); }
.numeral span { color: transparent; -webkit-text-stroke: 2px var(--accent); }
```

## Medidor em degraus

```css
.meter li { width: 44px; height: 26px; background: var(--surface-2); position: relative; }
.meter li::after { content: ""; position: absolute; inset: 0; background: var(--accent); opacity: 0;
                   animation: seg 5s steps(1) infinite; animation-delay: calc(var(--s) * .45s); }
.meter li.lit::after { opacity: 1; animation: none; }
@keyframes seg { 0%, 8% { opacity: 0 } 10%, 80% { opacity: 1 } 82%, 100% { opacity: 0 } }
```

## Digitação com máscara

```css
.typed { position: relative; display: inline-block; }
.typed::after { content: ""; position: absolute; inset: -2px; background: var(--bg-2);
                transform-origin: 100% 50%; transform: scaleX(0); /* estado final visível */
                animation: typing 6s steps(14) infinite; }
@keyframes typing { 0% { transform: scaleX(1) } 30%, 100% { transform: scaleX(0) } }
```

## Papel rasgado

```css
.torn { background: var(--paper); color: var(--paper-ink); padding: 26px;
        clip-path: polygon(0 1.5%, 6% .4%, 13% 2.6%, 20% .2%, 27% 2%, 34% .8%, 41% 2.8%, 48% .3%,
                           55% 2.2%, 62% .6%, 69% 2.5%, 76% .1%, 83% 1.9%, 90% .5%, 100% 2%,
                           100% 98%, 92% 99.6%, 84% 97.5%, 76% 99.8%, 68% 97.9%, 60% 99.3%, 52% 97.2%,
                           44% 99.7%, 36% 97.8%, 28% 99.4%, 20% 97.4%, 12% 99.9%, 4% 98.1%, 0 99.5%); }
```

## Letras recortadas acessíveis

```html
<p class="ransom" aria-label="Deploy"><span style="--r:-4deg">D</span><span style="--r:3deg">E</span>…</p>
```
```css
.ransom span { display: inline-block; padding: .04em .1em; transform: rotate(var(--r));
               background: var(--paper); box-shadow: 0 2px 3px #0003; }
```

Os `span` são lidos letra por letra por leitores de tela; o `aria-label` no pai devolve a palavra inteira.

## Sprite em pixel

```python
# gera o SVG uma vez; cada caractere é um pixel
rows = ["..kk..", ".kyyk.", "kyyyyk", ".kkkk."]
pal = {"k": "#000", "y": "#ffd84d"}
rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{pal[c]}"/>'
                for y, r in enumerate(rows) for x, c in enumerate(r) if c != ".")
svg = f'<svg viewBox="0 0 6 4" width="60" shape-rendering="crispEdges">{rects}</svg>'
```

## Linha de estações

```css
.line { container-type: inline-size; display: grid; grid-template-columns: repeat(6, 1fr); position: relative; }
.line::before { content: ""; position: absolute; left: calc(100% / 12); right: calc(100% / 12); top: 15px;
                height: 10px; background: var(--accent); }
.train { animation: train 7s cubic-bezier(.6,0,.3,1) infinite; }
@keyframes train { 0%, 10% { transform: translateX(0) } 45%, 100% { transform: translateX(calc(100cqw / 3)) } }
```

`100cqw` é a largura do contêiner, então o trem percorre exatamente duas estações em qualquer tela.

## Ponteiro de mostrador

```css
.needle { transform-box: view-box; transform-origin: 150px 150px; animation: needle 5s ease-in-out infinite; }
@keyframes needle { 0%, 100% { transform: rotate(-38deg) } 30% { transform: rotate(-12deg) } 75% { transform: rotate(6deg) } }
```

## Capitular

```css
.dropcap::first-letter { float: left; font: 400 5.4em/.8 var(--font-display); color: var(--accent); padding: .06em .08em 0 0; }
```

## Botão com reflexo e repouso

```css
.cta { position: relative; overflow: hidden; isolation: isolate; }
.cta::before { content: ""; position: absolute; inset: -40% auto -40% 0; width: 45%; z-index: -1;
               background: linear-gradient(110deg, transparent, #ffffff70, transparent);
               transform: translateX(-260%) skewX(-18deg); opacity: 0; animation: sheen 6.4s ease-in-out infinite; }
@keyframes sheen { 0%, 4% { transform: translateX(-260%) skewX(-18deg); opacity: 0 } 7% { opacity: .65 }
                   18% { transform: translateX(360%) skewX(-18deg); opacity: .65 }
                   21%, 100% { transform: translateX(360%) skewX(-18deg); opacity: 0 } }
```

Só no botão da ação final. Pause no hover e no foco.
