"""Inspeções feitas dentro da página pelo `pycode carousel qa` (JavaScript executado no Chromium)."""

# Blocos de texto visíveis do slide: retângulos, cor efetiva, tamanho real, corte e campo de origem.
DOM_QA_JS = r"""
() => {
  const slide = document.querySelector('.slide.is-only');
  const S = slide.getBoundingClientRect();
  const skip = (el) => el.closest('[data-decor],[aria-hidden="true"],template,.anchors-off');
  const det = (m) => Math.sqrt(Math.abs(m.a * m.d - m.b * m.c)) || 1;
  const scaleOf = (el) => {
    if (el instanceof SVGElement && el.getScreenCTM) {
      const m = el.getScreenCTM();
      return m ? Math.hypot(m.a, m.b) : 1;
    }
    let s = 1;
    for (let a = el; a && a !== document.documentElement; a = a.parentElement) {
      const t = getComputedStyle(a).transform;
      if (t && t !== 'none') s *= det(new DOMMatrix(t));
    }
    return s;
  };
  const opacityOf = (el) => {
    let o = 1;
    for (let a = el; a && a !== document.documentElement; a = a.parentElement) o *= parseFloat(getComputedStyle(a).opacity);
    return o;
  };
  const blockOf = (el) => {
    let b = el;
    while (b && b !== slide && getComputedStyle(b).display.startsWith('inline')) b = b.parentElement;
    return b;
  };
  const label = (el) => (el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ?
    '.' + el.className.trim().split(/\s+/).join('.') : '')).slice(0, 60);
  const items = new Map();
  const walker = document.createTreeWalker(slide, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const node = walker.currentNode;
    if (!node.nodeValue.trim()) continue;
    const el = node.parentElement;
    if (!el || skip(el)) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    const range = document.createRange();
    range.selectNodeContents(node);
    const rects = [...range.getClientRects()].filter((r) => r.width > 0.5 && r.height > 0.5)
      .map((r) => [r.left - S.left, r.top - S.top, r.right - S.left, r.bottom - S.top]);
    if (!rects.length) continue;
    const isSvg = el instanceof SVGElement;
    const fieldEl = el.closest('[data-field]');
    const role = el.closest('[data-code]') ? 'code' : el.closest('[data-anchor]') ? 'anchor' :
      fieldEl ? fieldEl.dataset.field : 'label';
    let it = items.get(el);
    if (!it) {
      const clip = [];
      for (let a = el.parentElement; a && a !== document.documentElement; a = a.parentElement) {
        const ac = getComputedStyle(a);
        if (ac.overflowX !== 'visible' || ac.overflowY !== 'visible') {
          const r = a.getBoundingClientRect();
          clip.push({el: label(a), box: [r.left - S.left, r.top - S.top, r.right - S.left, r.bottom - S.top]});
        }
        if (a === slide) break;
      }
      const b = blockOf(el);
      // tolerância de 0,3 em: descendentes e itálico passam um pouco da caixa sem cortar nada
      const tol = Math.max(2, 0.3 * parseFloat(getComputedStyle(b || el).fontSize));
      const over = b && b !== slide && b.clientWidth > 0 &&
        (b.scrollWidth > b.clientWidth + tol || b.scrollHeight > b.clientHeight + tol);
      it = {
        el: label(el), role, text: '', rects: [],
        color: isSvg ? cs.fill : cs.color, textFill: cs.webkitTextFillColor,
        bgClip: cs.backgroundClip || cs.webkitBackgroundClip || '',
        opacity: opacityOf(el), fontSize: parseFloat(cs.fontSize) * scaleOf(el),
        overflow: over ? {block: label(b), sw: b.scrollWidth, cw: b.clientWidth, sh: b.scrollHeight, ch: b.clientHeight} : null,
        ellipsis: cs.textOverflow === 'ellipsis', clip,
      };
      items.set(el, it);
    }
    it.text += node.nodeValue;
    it.rects.push(...rects);
  }
  const fields = [...slide.querySelectorAll('[data-field]')].filter((e) => !e.hidden).map((e) => {
    const c = e.cloneNode(true);
    c.querySelectorAll('[data-decor]').forEach((d) => d.remove());
    return {field: e.dataset.field, text: c.textContent.replace(/\s+/g, ' ').trim()};
  });
  const codes = [...slide.querySelectorAll('[data-code]')].filter((e) => !e.hidden && e.querySelector('.ln')).map((e) => {
    const cs = getComputedStyle(e);
    return {
      path: e.dataset.code || 'code',
      lines: [...e.querySelectorAll('.ln')].map((ln) => [...ln.querySelectorAll('.seg')].map((s) => s.textContent).join('')),
      ligaturesOff: /none/.test(cs.fontVariantLigatures) || /"liga" 0/.test(cs.fontFeatureSettings),
      overflow: e.scrollWidth > e.clientWidth + 2,
    };
  });
  const tok = (n) => getComputedStyle(slide).getPropertyValue(n).trim();
  const tokens = {};
  for (const n of ['--bg', '--bg-2', '--surface', '--surface-2', '--text', '--muted', '--accent', '--accent-2',
                   '--accent-ink', '--paper', '--paper-ink']) tokens[n] = tok(n);
  return {
    items: [...items.values()].map((i) => ({...i, text: i.text.replace(/\s+/g, ' ').trim()})),
    fields, codes, tokens,
    placeholders: slide.querySelectorAll('[data-placeholder]').length,
    hasRail: !!slide.querySelector('svg.rail .rail-line'),
  };
}
"""

# Some com o texto para medir o fundo real atrás de cada bloco (cor sólida, degradê ou imagem).
NO_TEXT_CSS = """
.slide *, .slide *::before, .slide *::after {
  color: transparent !important; -webkit-text-fill-color: transparent !important;
  text-shadow: none !important; -webkit-text-stroke: 0 !important; text-decoration-color: transparent !important;
}
.slide svg text, .slide svg tspan { fill: transparent !important; stroke: transparent !important; }
"""

# Deixa só o trilho (branco sobre preto) para medir as emendas entre slides.
RAIL_ONLY_CSS = """
.slide { background: #000 !important; }
.slide::before, .slide::after { display: none !important; }
.slide * { visibility: hidden !important; }
.slide svg.rail, .slide svg.rail .rail-line { visibility: visible !important; }
.slide svg.rail .rail-line { stroke: #fff !important; filter: none !important; opacity: 1 !important; }
"""
