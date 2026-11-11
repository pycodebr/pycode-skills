/*
 * Runtime do carrossel (pycode-carrosseis). Sem dependências e sem build.
 *
 * - Lê o texto de slides.json (fonte única) e preenche [data-field], [data-code] e as âncoras da marca.
 * - Desenha o trilho contínuo entre slides (svg.rail) a partir de rail.in / rail.out de cada slide.
 * - Expõe window.setT(t) para os slides animados: o mesmo t produz sempre o mesmo quadro.
 * - Parâmetros de URL usados pelos comandos: ?only=N (um slide só, em 1080x1350), &capture=1 (sem
 *   transições CSS, sem reprodução automática) e &t=SEGUNDOS (tempo inicial dos slides animados).
 *
 * O desenho próprio de cada conceito fica em js/scene.js, registrado com Carousel.onSlide(n, fn)
 * e Carousel.animate(n, fn, {duration}).
 */
(() => {
  'use strict';
  const W = 1080;
  const H = 1350;
  const params = new URLSearchParams(location.search);
  const ONLY = parseInt(params.get('only') || '0', 10);
  const CAPTURE = params.has('capture');
  const START_T = params.has('t') ? parseFloat(params.get('t')) : null;
  const hooks = [];
  const anims = {};
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const C = {
    W, H, only: ONLY, capture: CAPTURE, data: null, ready: false,
    /* Registra uma função de desenho para o slide n (ou '*' para todos): fn(slideEl, slideData, n). */
    onSlide(n, fn) { hooks.push([n, fn]); },
    /* Registra a animação do slide n: fn(t, slideEl, slideData). Só transform, opacity e stroke. */
    animate(n, fn, opts = {}) { anims[n] = { fn, duration: opts.duration || null }; },
    /* {n: duração} dos slides animados (usado pelos comandos video e qa). */
    animated() {
      return Object.fromEntries(Object.entries(anims).map(([n, a]) => [n, a.duration]));
    },
    token(name, el) {
      return getComputedStyle(el || document.documentElement).getPropertyValue(name).trim();
    },
    slide(n) { return document.querySelector(`.slide[data-n="${n}"]`); },
    get(obj, path) {
      return String(path).split('.').reduce((o, k) => (o == null ? undefined : o[k]), obj);
    },
    clamp: (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)),
    /* Progresso 0..1 entre t0 e t0 + d. */
    prog(t, t0, d) { return C.clamp((t - t0) / d); },
    ease: {
      out: (x) => 1 - Math.pow(1 - x, 3),
      inOut: (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
      back: (x) => { const c = 1.4; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); },
    },
    /* Gerador pseudoaleatório com semente (desenho determinístico). */
    rng(seed) {
      let s = seed >>> 0 || 1;
      return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return ((s >>> 0) % 100000) / 100000; };
    },
    richText,
    renderCode,
  };
  window.Carousel = C;

  /* *destaque* vira <em class="hl">; quebra de linha (\n) vira <br>. */
  function richText(el, value) {
    el.textContent = '';
    for (const part of String(value).split(/(\*[^*\n]+\*|\n)/)) {
      if (!part) continue;
      if (part === '\n') {
        el.appendChild(document.createElement('br'));
      } else if (part.length > 2 && part.startsWith('*') && part.endsWith('*')) {
        const em = document.createElement('em');
        em.className = 'hl';
        em.textContent = part.slice(1, -1);
        el.appendChild(em);
      } else {
        el.appendChild(document.createTextNode(part));
      }
    }
  }

  /* ------------------------------------------------------------------ código exato */
  const KEYWORDS = new Set(['def', 'return', 'import', 'from', 'for', 'in', 'if', 'else', 'elif', 'while',
    'class', 'with', 'as', 'not', 'and', 'or', 'is', 'None', 'True', 'False', 'lambda', 'try', 'except',
    'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'GET', 'POST']);

  function highlight(line) {
    // Tokens simples: string, número, palavra-chave, comentário. Os spans não mudam o texto.
    const out = document.createDocumentFragment();
    const re = /(#.*$)|("[^"]*"|'[^']*')|(\b\d+(?:\.\d+)?\b)|([A-Za-z_][A-Za-z_0-9]*)|(\s+)|(.)/g;
    let m;
    while ((m = re.exec(line)) !== null) {
      const [tok, com, str, num, word] = m;
      let cls = '';
      if (com) cls = 'c';
      else if (str) cls = 's';
      else if (num) cls = 'n';
      else if (word && KEYWORDS.has(word)) cls = 'k';
      if (cls) {
        const s = document.createElement('span');
        s.className = cls;
        s.textContent = tok;
        out.appendChild(s);
      } else {
        out.appendChild(document.createTextNode(tok));
      }
    }
    return out;
  }

  /* Quebra visual só entre tokens (espaço, barra, vírgula, parêntese) e só se a linha não couber. */
  function splitToFit(text, maxWidth, ctx, indent) {
    if (ctx.measureText(text).width <= maxWidth) return [text];
    const segs = [];
    let rest = text;
    const limit = () => (segs.length ? maxWidth - indent : maxWidth); // continuação recuada
    while (rest && ctx.measureText(rest).width > limit()) {
      let cut = -1;
      for (let i = 1; i < rest.length; i++) {
        const prev = rest[i - 1];
        if (/[\s/,(|&]/.test(prev) && ctx.measureText(rest.slice(0, i)).width <= limit()) cut = i;
      }
      if (cut <= 0) break; // token maior que a linha: o QA acusa o transbordo
      segs.push(rest.slice(0, cut));
      rest = rest.slice(cut);
    }
    if (rest) segs.push(rest);
    return segs;
  }

  function renderCode(el, code) {
    const lines = Array.isArray(code) ? code : (code.lines || []);
    el.textContent = '';
    el.classList.add('code');
    const cs = getComputedStyle(el);
    const canvas = document.createElement('canvas').getContext('2d');
    canvas.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    const pad = parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight);
    const contIndent = parseFloat(cs.fontSize) * 1.6;
    const maxW = el.clientWidth - pad;
    lines.forEach((line) => {
      const ln = document.createElement('span');
      ln.className = 'ln';
      if (/^(>>>|\.\.\.)( |$)/.test(line)) ln.classList.add('in');
      else if (lines.some((l) => l.startsWith('>>>'))) ln.classList.add('out');
      splitToFit(line, maxW, canvas, contIndent).forEach((seg, k) => {
        if (k > 0) {
          ln.appendChild(document.createElement('br'));
          const cont = document.createElement('span');
          cont.className = 'cont';
          cont.dataset.decor = '';
          cont.setAttribute('aria-hidden', 'true');
          ln.appendChild(cont);
        }
        const s = document.createElement('span');
        s.className = 'seg';
        if (k === 0 && /^(>>>|\.\.\.) /.test(seg)) {
          const pr = document.createElement('span');
          pr.className = 'pr';
          pr.textContent = seg.slice(0, 4);
          s.appendChild(pr);
          s.appendChild(highlight(seg.slice(4)));
        } else {
          s.appendChild(highlight(seg));
        }
        ln.appendChild(s);
      });
      el.appendChild(ln);
    });
  }

  /* ------------------------------------------------------------------ trilho contínuo */
  function catmull(points) {
    // Catmull-Rom -> Bézier: passa por todos os pontos, com tangente horizontal nas bordas.
    let d = `M ${points[0][0]} ${points[0][1]}`;
    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[Math.max(0, i - 1)];
      const p1 = points[i];
      const p2 = points[i + 1];
      const p3 = points[Math.min(points.length - 1, i + 2)];
      const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
      const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
      d += ` C ${c1[0].toFixed(1)} ${c1[1].toFixed(1)}, ${c2[0].toFixed(1)} ${c2[1].toFixed(1)}, ${p2[0]} ${p2[1]}`;
    }
    return d;
  }

  function railPath(rail) {
    const pts = [];
    if (rail.in != null) pts.push([-120, rail.in], [0, rail.in], [60, rail.in]);
    else pts.push(rail.start || [W / 2, H / 2]);
    for (const p of rail.via || []) pts.push(p);
    if (rail.out != null) pts.push([W - 60, rail.out], [W, rail.out], [W + 120, rail.out]);
    else pts.push(rail.end || [W / 2, H / 2]);
    return catmull(pts);
  }

  function drawRail(slideEl, rail) {
    let svg = slideEl.querySelector('svg.rail');
    if (!svg) {
      svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('class', 'rail');
      slideEl.prepend(svg);
    }
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    svg.setAttribute('aria-hidden', 'true');
    const d = railPath(rail);
    svg.innerHTML = `<path class="rail-glow" d="${d}"/><path class="rail-line" d="${d}"/>`;
    for (const [x, y] of rail.nodes || []) {
      svg.insertAdjacentHTML('beforeend', `<circle class="rail-node" cx="${x}" cy="${y}" r="16"/>`);
    }
    if (rail.out == null && rail.end) {
      const [x, y] = rail.end;
      svg.insertAdjacentHTML('beforeend', `<circle class="rail-end" cx="${x}" cy="${y}" r="22"/>`);
    }
  }

  /* Textura de grão: um ladrilho de ruído desenhado uma vez em canvas e exposto como --grain.
     É bem mais leve que um filtro feTurbulence, que o navegador recalcula a cada quadro do vídeo. */
  function grainTile(seed = 7, size = 160) {
    const cv = document.createElement('canvas');
    cv.width = cv.height = size;
    const ctx = cv.getContext('2d');
    const img = ctx.createImageData(size, size);
    const rnd = C.rng(seed);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = Math.round(rnd() * 255);
      img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
      img.data[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    return cv.toDataURL('image/png');
  }

  /* ------------------------------------------------------------------ montagem */
  async function loadData() {
    if (location.protocol !== 'file:') {
      try {
        const r = await fetch('slides.json', { cache: 'no-store' });
        if (r.ok) return await r.json();
      } catch (e) { /* cai para o espelho abaixo */ }
    }
    if (window.SLIDES) return window.SLIDES; // espelho gerado pelos comandos (js/slides-data.js)
    throw new Error('não consegui ler slides.json: abra com `pycode serve` ou rode `pycode carousel render`');
  }

  function buildFromTemplates(root, data) {
    // Projeto do modelo: cada slide nasce do <template data-layout="..."> correspondente.
    data.slides.forEach((s, i) => {
      const n = i + 1;
      const layout = s.layout || (n === 1 ? 'cover' : n === data.slides.length ? 'cta' : 'content');
      const tpl = document.querySelector(`template[data-layout="${layout}"]`);
      if (!tpl) throw new Error(`não há <template data-layout="${layout}"> para o slide ${n}`);
      const frag = tpl.content.cloneNode(true);
      const sec = frag.querySelector('.slide');
      sec.dataset.n = n;
      root.appendChild(frag);
    });
  }

  function fill(slideEl, s, n, data) {
    const total = data.slides.length;
    slideEl.dataset.n = n;
    slideEl.style.setProperty('--n', n);
    slideEl.style.setProperty('--total', total);
    for (const el of slideEl.querySelectorAll('[data-field]')) {
      const v = C.get(s, el.dataset.field);
      if (v == null || v === '') {
        el.hidden = true;
      } else {
        richText(el, v);
      }
    }
    for (const el of slideEl.querySelectorAll('[data-code]')) {
      const code = C.get(s, el.dataset.code || 'code');
      if (code) renderCode(el, code);
    }
    if (!slideEl.querySelector('[data-anchor]') && slideEl.dataset.anchors !== 'off') {
      slideEl.insertAdjacentHTML('beforeend',
        '<div class="anchors"><span class="brand" data-anchor="brand"></span>' +
        '<span class="counter" data-anchor="counter"></span></div>');
    }
    const brand = data.brand || {};
    for (const el of slideEl.querySelectorAll('[data-anchor="brand"]')) el.textContent = brand.name || '';
    for (const el of slideEl.querySelectorAll('[data-anchor="handle"]')) el.textContent = brand.handle || '';
    for (const el of slideEl.querySelectorAll('[data-anchor="counter"]')) el.textContent = `${n}/${total}`;
    if (s.rail) drawRail(slideEl, s.rail);
  }

  /* Reduz a fonte de [data-fit] até caber na caixa (sem passar de data-fit-min px). */
  function fitText(root) {
    for (const el of root.querySelectorAll('[data-fit]')) {
      const min = parseFloat(el.dataset.fitMin || '28');
      let fs = parseFloat(getComputedStyle(el).fontSize);
      while ((el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1) && fs > min) {
        fs -= 1;
        el.style.fontSize = `${fs}px`;
      }
    }
  }

  function setT(t) {
    for (const [n, a] of Object.entries(anims)) {
      if (ONLY && +n !== ONLY) continue;
      const el = C.slide(n);
      if (el) a.fn(t, el, C.data.slides[n - 1], C);
    }
  }

  function stillTime(n) {
    const v = (C.data.slides[n - 1] || {}).video || {};
    const dur = anims[n].duration || v.seconds || 5;
    return v.still != null ? v.still : dur;
  }

  /* Na navegação normal, o slide animado toca em laço só enquanto aparece na tela. */
  function autoplay() {
    for (const n of Object.keys(anims)) {
      const el = C.slide(n);
      if (!el) continue;
      const dur = anims[n].duration || 5;
      if (reduced) { anims[n].fn(stillTime(n), el, C.data.slides[n - 1], C); continue; }
      let raf = 0;
      let t0 = 0;
      const loop = (now) => {
        if (!t0) t0 = now;
        const t = Math.min(((now - t0) / 1000) % (dur + 1.5), dur);
        anims[n].fn(t, el, C.data.slides[n - 1], C);
        raf = requestAnimationFrame(loop);
      };
      new IntersectionObserver((entries) => {
        for (const e of entries) {
          if (e.isIntersecting && !raf) { t0 = 0; raf = requestAnimationFrame(loop); }
          if (!e.isIntersecting && raf) { cancelAnimationFrame(raf); raf = 0; }
        }
      }, { threshold: 0.4 }).observe(el);
    }
  }

  async function boot() {
    const root = document.querySelector('.carousel');
    const data = await loadData();
    C.data = data;
    document.documentElement.style.setProperty('--grain', `url(${grainTile()})`);
    document.documentElement.lang = (data.meta && data.meta.lang) || 'pt-BR';
    // Carrega todas as fontes declaradas antes de medir texto (quebra de código, canvas, ajuste).
    await Promise.all([...document.fonts].map((f) => f.load().catch(() => null)));
    if (!root.querySelector('.slide')) buildFromTemplates(root, data);
    const slides = [...root.querySelectorAll('.slide')];
    if (slides.length !== data.slides.length) {
      throw new Error(`index.html tem ${slides.length} slides e slides.json tem ${data.slides.length}`);
    }
    // <template id="slide-common">: fundo, textura e âncoras repetidos em todos os slides.
    const common = document.querySelector('template#slide-common');
    if (common) slides.forEach((el) => el.prepend(common.content.cloneNode(true)));
    slides.forEach((el, i) => fill(el, data.slides[i], i + 1, data));
    if (ONLY) {
      document.documentElement.classList.add('only');
      slides.forEach((el, i) => el.classList.toggle('is-only', i + 1 === ONLY));
    }
    if (CAPTURE) document.documentElement.classList.add('capture');
    await document.fonts.ready;
    for (const [n, fn] of hooks) {
      slides.forEach((el, i) => {
        if (n === '*' || +n === i + 1) fn(el, data.slides[i], i + 1, C);
      });
    }
    await document.fonts.ready;
    fitText(document);
    window.setT = setT;
    for (const n of Object.keys(anims)) {
      const el = C.slide(n);
      if (el) anims[n].fn(START_T != null ? START_T : stillTime(n), el, data.slides[n - 1], C);
    }
    if (!CAPTURE) autoplay();
    C.ready = true;
    document.documentElement.dataset.ready = '1';
    document.dispatchEvent(new Event('carousel:ready'));
  }

  const start = () => boot().catch((err) => {
    console.error(err);
    document.documentElement.dataset.ready = 'error';
    document.documentElement.dataset.error = String(err && err.message || err);
  });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
