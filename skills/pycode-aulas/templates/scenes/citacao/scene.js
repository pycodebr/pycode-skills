/* Arquétipo citação: uma frase grande com as aspas da fonte do estilo e trechos sublinhados clicáveis; cada trecho mostra
   o que ele quer dizer no assunto da aula. Serve para princípios, definições oficiais e frases de referência.
   data: { quote, marks: [{ phrase, tip }], author, source } (cada phrase precisa aparecer literalmente em quote) */
(() => {
  const { esc, q, qa, icon, tip: mkTip } = window.K;
  window.SCENES['__ID__'] = (slide, ctx) => {
    const D = ctx.data.data || {};
    const marks = (D.marks || []).filter(m => (D.quote || '').includes(m.phrase));
    const host = q(slide, '[data-fill]');
    let html = esc(D.quote || '');
    marks.forEach((m, i) => { html = html.replace(esc(m.phrase), `<span class="qt-mk" data-i="${i}">${esc(m.phrase)}</span>`); });
    host.innerHTML = `
      <div class="board">
        <span class="qt-glyph" aria-hidden="true">“</span>
        <div class="qt-wrap">
          <blockquote class="qt-text">${html}</blockquote>
          <p class="qt-by"><i></i><b>${esc(D.author || '')}</b>${D.source ? `<span class="mono">${esc(D.source)}</span>` : ''}</p>
        </div>
      </div>`;
    const board = q(host, '.board');
    const els = qa(host, '.qt-mk').sort((a, b) => a.dataset.i - b.dataset.i);
    const tip = mkTip(board, ctx, [0, 0, 1696, 716]);
    let cur = -1;
    const focus = (i, anim) => {
      cur = i;
      els.forEach((el, j) => el.classList.toggle('on', j === i));
      board.classList.toggle('has-focus', i >= 0);
      if (i < 0) { tip.hide(); return; }
      const r = els[i].getClientRects()[0], b = board.getBoundingClientRect(), z = b.width / board.offsetWidth || 1;
      const x = (r.left - b.left) / z + r.width / z / 2, yb = (r.bottom - b.top) / z;
      tip.show(x, yb + 4, 'b', marks[i].phrase, marks[i].tip, anim);
    };
    ctx.pick(els, i => focus(i, true), { group: 'trecho', label: (el, i) => `${marks[i].phrase}: ${marks[i].tip}` });
    const cyc = FX.cycle({ n: marks.length, every: 3, onStep: focus, homeIndex: -1, stillIndex: -1 });
    const intro = gsap.timeline({ paused: true });
    intro.fromTo(q(host, '.qt-glyph'), { opacity: 0, scale: .4, rotation: -12 }, { opacity: 1, scale: 1, rotation: 0, duration: 1, ease: 'back.out(1.6)', clearProps: 'opacity,transform' }, 0)
      .fromTo(q(host, '.qt-text'), { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 1, ease: 'expo.out', clearProps: 'opacity,transform' }, .3)
      .fromTo(q(host, '.qt-by'), { opacity: 0 }, { opacity: 1, duration: .6, clearProps: 'opacity' }, .9);
    focus(-1, false);
    return { intro, loop: cyc.loop, home: cyc.home, still: cyc.still, key: () => String(cur), layout: () => { if (cur >= 0) focus(cur, false); } };
  };
})();
