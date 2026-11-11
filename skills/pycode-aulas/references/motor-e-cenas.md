# Motor do deck e como escrever uma cena

## Estrutura do projeto (criado por `pycode deck new`)

```
minha-aula/
  deck.json              configuração: slug, idioma, estilo, modo (claro/escuro), versão, marca
  src/
    content.json         TODO o texto da aula (fonte única): meta, ui, cenas e material de estudo
    shell.html           casca do documento (HUD, barra de controles, diálogos); raramente muda
    css/tokens.css       variáveis do estilo (contrato do pycode-design) e cores da sua marca
    css/fonts.css        @font-face das fontes copiadas pelo vendor
    css/engine.css       palco, HUD, fio visual, controles, leitura e celular
    css/base.css         peças comuns (.node, .chip, .ic, .tip)
    js/fx.js             efeitos (FX) e utilidades (K) usados pelas cenas
    js/deck.js           o motor
    scenes/<id>.js       uma fábrica por cena (um assunto por arquivo)
    scenes/<id>.css      estilos da cena, sempre com o prefixo .s-<id>
    head-extra.html      (opcional) ponto de extensão no <head>, ex.: medição de audiência; o modelo não traz nenhum
  assets/fonts, assets/vendor/gsap.min.js, assets/img    arquivos locais (nada de CDN)
  site/                  gerado pelo build (não edite)
  qa/, stills/, exports/, material/                       gerados pelos outros comandos
```

O build junta `tokens + fonts + engine + base + scenes/*.css` em `site/assets/css/deck.css`, `fx + scenes/*.js +
deck.js` em `site/assets/js/deck.js` e o conteúdo em `site/assets/js/content.js` (`window.DECK`), com hash no nome
para invalidar cache. As notas de fala (`notes`) e o material (`study`) não vão para o site.

## Palco e modos de tela

- Palco fixo de **1920×1080**, escalado para a janela. Cena: `padding 104px 112px 140px`; área útil da cena
  (`.fill`) com uma prancha `.board` de **1696×716 px**: desenhe nessas coordenadas.
- **Paisagem** (celular deitado, notebook, telão): palco inteiro.
- **Retrato** (`body.portrait`): palco ao vivo no topo, ajustado à largura, e embaixo título, apoio, um `<details>`
  com as listas `reading` e um botão para o modo texto.
- **Modo leitura** (`?leitura` ou menu): todas as cenas em sequência, como texto, sem o palco. Também é o que aparece
  sem JavaScript, porque o build escreve título, apoio, lista e gancho no HTML.
- `?still` e `prefers-reduced-motion`: cada cena mostra o estado final (`still()`), sem animação longa, e os cliques
  continuam funcionando.

## Teclado e controles

Setas, PageUp/PageDown e espaço navegam; Home/End vão ao início e ao fim; **O** índice; **?** opções; **F** tela cheia;
**R** recomeça a demonstração da cena; **M** pausa ou retoma as animações; **T** cronômetro (duplo clique zera);
**B** tela preta (Esc volta). Clique nas bordas laterais do palco e deslize o dedo também navegam. `#7` ou `#id`
abrem uma cena; a posição fica salva no navegador (o hash vence).

## Ciclo de vida de uma cena

1. Ao entrar, o motor anima o título palavra por palavra, toca `intro` e, perto do fim dela, chama `home()` e toca a
   demonstração (`loop`) **uma vez**.
2. No fim da demonstração, o motor pausa no zero e chama `home()`: a cena volta ao estado em que a demonstração começou
   e para. Movimento contínuo (pacotes, órbitas) só pela função `ambient(dt)`.
3. Qualquer clique ou toque dentro da cena ativa faz o apresentador assumir: a intro completa, a demonstração pausa
   no instante e o item clicado (registrado com `ctx.pick`) é selecionado. A cena não volta sozinha.
4. **R**, o item Recomeçar do menu, **M** e trocar de cena devolvem o automático.

`slide.dataset.demo` diz o estado (`intro`, `demo`, `home`, `manual`, `still`) e `window.presentation.state()` expõe
`{ id, demo, manual, key, startKey, intro, loop, picks }` para o QA. `presentation.speed(k)` acelera a cena ativa.

## Contrato da fábrica

```js
(() => {
  const { esc, q, qa, icon, tip: mkTip } = window.K;
  window.SCENES['minha-cena'] = (slide, ctx) => {
    const D = ctx.data.data || {};            // o objeto "data" da cena no content.json
    const host = q(slide, '[data-fill]');
    host.innerHTML = `<div class="board">...</div>`;
    const board = q(host, '.board');
    const tip = mkTip(board, ctx, [0, 0, 1696, 716]);   // balão curto perto do item
    let cur = -1;
    const focus = (i, anim) => { cur = i; /* liga classes, move objetos, mostra o balão */ };
    ctx.pick(qa(host, '.item'), i => focus(i, true), { group: 'item', label: (el, i) => D.items[i].label });
    const cyc = FX.cycle({ n: D.items.length, every: 2.6, onStep: focus, homeIndex: -1, stillIndex: -1 });
    const intro = gsap.timeline({ paused: true });
    intro.fromTo(qa(host, '.item'), { opacity: 0, y: 20 }, { opacity: 1, y: 0, stagger: .1, clearProps: 'opacity,transform' });
    return { intro, loop: cyc.loop, home: cyc.home, still: cyc.still, key: () => String(cur) };
  };
})();
```

| Campo | Obrigatório | Para quê |
|---|---|---|
| `intro` | não | timeline pausada da entrada |
| `loop` | não (mas é o que dá vida à cena) | demonstração; o motor força `repeat(0)` |
| `home()` | sim | estado inicial da demonstração, sem animação |
| `key()` | sim | texto que identifica a seleção atual (o QA compara antes e depois) |
| `still()` | recomendado | estado final legível para `?still`, movimento reduzido e exportação |
| `ambient(dt)` | não | movimento contínuo (chamado a cada quadro só na cena ativa, pausado com M) |
| `layout()` | não | recalcular ligações e balões quando a janela muda |
| `speed(k)` | se a cena cria tweens próprios | acelerar junto no QA |
| `take()`, `enter()`, `leave()` | não | ganchos extras |

`ctx` oferece `data`, `meta`, `motion()` (falso em still e movimento reduzido), `pick(els, fn, opts)`, `take()`,
`manual()`, `show(i)` e `requestLayout()`.

`ctx.pick` põe `data-pick`, `tabindex="0"`, `role="button"` e `aria-label` em cada elemento e registra a ação. Um
único listener do motor trata clique, Enter e Espaço. **A cena não chama `addEventListener`.**

## Utilidades (`window.FX` e `window.K`)

- `FX.cycle({ n, every, onStep, homeIndex, stillIndex })`: demonstração em passos; devolve `{ loop, home, still }`.
- `FX.draw(paths, vars)`: traço de SVG que se desenha (stroke-dashoffset).
- `FX.type(el, texto, { cps })`: digitação. `FX.count(el, valor)`: contagem.
- `FX.table(path, n)` e `FX.at(tabela, t)`: tabela de pontos de um caminho para mover objetos sem
  `getPointAtLength` a cada quadro.
- `FX.splitWords(el)`: quebra um texto em palavras com máscara (o motor já faz isso nos títulos).
- `K.icon(nome)`: ícone de traço inline (`app, site, server, database, globe, gate, key, lock, shield, clock, code,
  terminal, user, card, pin, cloud, mail, chart, book, bolt, check, cross, gear, box, chat, layers, route, sun, play,
  quote, flag, spark`). Para logos de marca, use `pycode icon <slug> --out assets/img/<slug>.svg`.
- `K.tip(host, ctx, caixa)`: balão com `show(x, y, lado, rótulo, texto, animar)`, `hide()` e `refresh()`.
- `K.pos(el, raiz)`: posição pelo layout (ignora transformações em andamento). `K.tone('ok')`: cor de um tom.
- `K.esc`, `K.q`, `K.qa`, `K.svg`, `K.only`, `K.fmt`.

## Regras que o build confere (e recusa)

- ids únicos, em minúsculas com hífen; cada cena com `src/scenes/<id>.js` registrando `SCENES['<id>']`.
- Cada fábrica usa `ctx.pick`, `home` e `key`. Sem `addEventListener`, `localStorage`, `Math.random`,
  `repeat: -1`, `fetch`, controles de formulário, handlers inline nem URL externa.
- CSS das cenas só com variáveis do contrato (nenhum `#hex`, `rgb()` ou `hsl()`) e todo seletor com `.s-<id>`.
  Para estilos claros e escuros diferentes, use `body[data-mode="light"] .s-<id> ...`.
- Nenhum recurso carregado de fora do projeto (CDN, fonte remota, script de terceiros).
- Texto do `content.json` sem erros do `pycode text` (acentos, travessão, emoji, vícios); avisos aparecem e recusam
  com `--strict`.

## content.json

```json
{
  "meta": { "title": "...", "short": "...", "description": "...", "author": "...", "thread": "rótulo do fio",
            "background": "grade|rede|ondas|orbita|nenhum", "study": { ... material do Notion ... } },
  "ui": { },
  "scenes": [{
    "id": "viagem", "archetype": "circuito", "title": "A viagem do *pedido*", "chapter": "o mecanismo",
    "thread": "pedido 42 · na rede", "transition": "corte|cortina|iris|sobe", "bg": "grade", "accent": "2",
    "apoio": "frase completa para leitura e celular", "hook": "gancho para a próxima cena",
    "notes": "fala do apresentador (vai para o PPTX, não para o site)", "budget": 30,
    "reading": [{ "label": "1", "title": "App", "text": "Monta o pedido e envia." }],
    "study": { "text": ["parágrafo do material"], "code": "...", "lang": "python" },
    "data": { "...": "campos do arquétipo" }
  }]
}
```

`*palavra*` no título vira destaque na cor de acento. `ui` traduz os textos da interface (veja `UI_DEFAULTS` em
`deck_common.py`); deixe vazio para PT-BR.

## Como construir uma cena nova

1. `pycode deck scene add <pasta> --archetype <nome> --id <id> [--after <id>]` copia o arquétipo e um texto de
   exemplo. Para um desenho que nenhum arquétipo cobre, copie o mais parecido e reescreva o visual.
2. Escreva os textos em `content.json` (fonte única); a cena só lê `ctx.data`.
3. Desenhe primeiro o estado de repouso em `?still` (`pycode serve site` e abra `index.html?still#<id>`), depois a demonstração.
4. `pycode deck build` e `pycode deck qa --only <id> --fast` a cada mudança; QA completo antes de entregar.
