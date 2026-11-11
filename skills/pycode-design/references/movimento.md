# Ofício de movimento

Movimento bom explica uma mudança de estado ou dá vida a um objeto. Movimento ruim enfeita, atrasa a leitura e gasta bateria. Estas regras valem para páginas, decks e carrosséis em HTML.

## Regras de base

1. **Só `transform` e `opacity`** (e `stroke-dashoffset`/`stroke-dasharray` em SVG). São as propriedades que o navegador anima sem recalcular layout. Não anime `width`, `height`, `top`, `left`, `margin`, `box-shadow`, `filter` ou `background-position`. O `pycode styles check` reprova `@keyframes` com outras propriedades.
2. **Conteúdo legível sem JavaScript.** O estado inicial escondido só existe quando o JS está presente: marque `<html class="js">` com um script mínimo no `<head>` e use `html.js [data-scene]:not([data-entered]) .rise { opacity: 0 }`.
3. **Pausa fora da tela.** Loops ficam pausados por padrão e só rodam na cena visível.
4. **Pausa com a aba oculta.** Use `visibilitychange`.
5. **Movimento reduzido.** Com `prefers-reduced-motion: reduce`, desligue animações e transições e mostre tudo no estado final (planta desenhada, tarefas marcadas, contagem parada no primeiro número).

## Esqueleto que funciona

```html
<script>document.documentElement.classList.add('js')</script>
<style>
  html.js [data-scene]:not([data-entered]) .rise { opacity: 0; transform: translateY(18px); }
  .rise { transition: opacity .8s cubic-bezier(.2,.7,.2,1), transform .8s cubic-bezier(.2,.7,.2,1);
          transition-delay: calc(var(--i, 0) * 70ms); }
  html.js .loop, html.js .loop::before, html.js .loop::after { animation-play-state: paused !important; }
  html.js [data-scene][data-motion="on"] .loop,
  html.js [data-scene][data-motion="on"] .loop::before,
  html.js [data-scene][data-motion="on"] .loop::after { animation-play-state: running !important; }
  html.js body[data-background="true"] .loop { animation-play-state: paused !important; }
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
    html.js [data-scene]:not([data-entered]) .rise { opacity: 1; transform: none; }
  }
</style>
<script>
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      e.target.dataset.motion = e.isIntersecting && !reduce.matches ? 'on' : 'off';
      if (e.isIntersecting) e.target.dataset.entered = 'true';
    }
  }, { threshold: 0.12 });
  document.querySelectorAll('[data-scene]').forEach((s) => io.observe(s));
  document.addEventListener('visibilitychange', () => {
    document.body.dataset.background = document.hidden ? 'true' : 'false';
  });
</script>
```

Marque cada seção com `data-scene`, os elementos de entrada com `rise` (e `--i` para escalonar) e tudo que repete com `loop`. Pseudo-elementos animados precisam da classe `loop` no elemento dono, porque `animation-play-state` não passa para `::before` e `::after` sozinho.

## Armadilhas reais

- **Inclinação fixa mais entrada.** Se um recorte tem `transform: rotate(4deg)` no estilo inline e a entrada também usa `transform`, a regra inline vence e a entrada some. Use a propriedade `rotate: 4deg` para a inclinação e `transform` para a entrada.
- **Máscara de digitação.** Para simular digitação, encolha uma máscara da cor do fundo com `scaleX` em `steps(n)`. O estado sem animação precisa ser `scaleX(0)`, senão o texto fica coberto com movimento reduzido.
- **Números que se alternam.** Ao empilhar 3, 2, 1 com `opacity`, deixe o primeiro visível no estilo base; os outros começam em 0.
- **Captura de página inteira.** Seções fora da tela ainda não entraram. Role a página antes de capturar, ou capture com `pycode shot --reduced-motion`.
- **Filtros SVG pesados.** `feTurbulence` com `feDisplacementMap` em muitos traços deixa a captura lenta em máquinas sem GPU. Use em poucos elementos e nunca anime o filtro.

## Parâmetros de referência

| Uso | Duração | Easing |
|---|---|---|
| entrada de texto | 0,6 a 0,9 s, escalonada em 60 a 90 ms | `cubic-bezier(.2,.7,.2,1)` |
| objeto chegando | 0,75 a 0,9 s, 15 a 25 px | o mesmo |
| traço se desenhando | 1,2 a 1,8 s por traço | `cubic-bezier(.6,0,.3,1)` |
| peça colada (rebote) | 0,5 a 0,7 s | `cubic-bezier(.3,1.4,.5,1)` |
| hover e toggle | 0,2 a 0,3 s | `ease` |
| loop ambiente lento | 8 a 110 s | `linear` |
| loop com repouso (botão) | 5 a 7 s, parado em 70% a 80% do ciclo | `ease-in-out` |
| estilo retrô | qualquer duração | `steps(n)` |

Nada de escala pulsante em botão, tremor, spinner decorativo ou flash.

## Quando usar GSAP

O `vendor` traz GSAP e plugins (ScrollTrigger, SplitText, DrawSVG, MotionPath, Flip, CustomEase, MorphSVG), copiados para o projeto com `vendor.copy_js`. Use quando o CSS não resolve bem:

- linha do tempo com muitas etapas sincronizadas (uma aula que se monta passo a passo);
- animação presa à rolagem com começo e fim precisos (ScrollTrigger);
- objeto seguindo um caminho curvo (MotionPath);
- troca de layout animada entre dois estados (Flip).

Para entradas, loops e hovers, CSS basta. Mesmo com GSAP, continue animando só `transform`, `opacity` e traço, pause fora da tela (`ScrollTrigger` com `toggleActions` ou `IntersectionObserver`) e respeite `prefers-reduced-motion` com `gsap.matchMedia()`.

## Como provar que funciona

Uma captura estática não prova movimento. Para conferir:

1. `pycode shot <arquivo> --reduced-motion` mostra o estado final.
2. Duas capturas com intervalo (por exemplo, `--wait 500` e `--wait 2500`) mostram que algo mudou.
3. `document.getAnimations()` no console lista o que está rodando; com movimento reduzido, nenhum loop infinito deve aparecer (o `pycode styles check` faz essa conferência).
