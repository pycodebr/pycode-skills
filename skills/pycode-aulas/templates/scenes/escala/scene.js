/* Arquétipo escala: barras horizontais numa escala logarítmica, para comparar grandezas muito diferentes
   (tempos, tamanhos, custos). Cada barra clicável mostra uma comparação em linguagem do dia a dia.
   data: { unit, log: true, ticks: [{ v, label }], items: [{ label, value, display, tip }] } */
(() => {
  const { esc, q, qa, tip: mkTip } = window.K;
  window.SCENES['__ID__'] = (slide, ctx) => {
    const D = ctx.data.data || {};
    const items = D.items || [], ticks = D.ticks || [];
    const host = q(slide, '[data-fill]');
    const log = D.log !== false;
    const vals = items.map(i => i.value).concat(ticks.map(t => t.v));
    const lo = log ? Math.floor(Math.log10(Math.min(...vals))) : 0, hi = log ? Math.ceil(Math.log10(Math.max(...vals))) : Math.max(...vals);
    const X0 = 380, X1 = 1640;
    const X = v => X0 + (X1 - X0) * (log ? (Math.log10(v) - lo) / Math.max(1e-9, hi - lo) : v / hi);
    const rowH = Math.min(118, 520 / Math.max(1, items.length));
    const y = i => 70 + i * rowH;
    host.innerHTML = `
      <div class="board">
        <div class="sc-axis">${ticks.map(t => `<span class="sc-tick" style="left:${X(t.v)}px"><b class="mono">${esc(t.label)}</b></span>`).join('')}</div>
        ${items.map((it, i) => `<div class="sc-row" data-i="${i}" style="top:${y(i)}px;height:${rowH - 22}px"><b class="sc-lbl">${esc(it.label)}</b><i class="sc-bar" style="width:${(X(it.value) - X0).toFixed(1)}px"></i><span class="sc-val mono" style="left:${(X(it.value) + 16).toFixed(1)}px">${esc(it.display || it.value)}</span></div>`).join('')}
        ${D.unit ? `<p class="sc-unit mono">${esc(D.unit)}</p>` : ''}
      </div>`;
    const board = q(host, '.board');
    const els = qa(host, '.sc-row'), bars = qa(host, '.sc-bar');
    const tip = mkTip(board, ctx, [0, 0, 1696, 716]);
    let cur = -1;
    const focus = (i, anim) => {
      cur = i;
      els.forEach((el, j) => el.classList.toggle('on', j === i));
      board.classList.toggle('has-focus', i >= 0);
      if (i < 0) { tip.hide(); return; }
      const xEnd = Math.min(X(items[i].value), 1300);
      tip.show(xEnd, y(i) + rowH - 10, 'b', items[i].display || String(items[i].value), items[i].tip, anim);
    };
    ctx.pick(els, i => focus(i, true), { group: 'barra', label: (el, i) => `${items[i].label}: ${items[i].display || items[i].value}. ${items[i].tip || ''}` });
    const cyc = FX.cycle({ n: items.length, every: 2.6, onStep: focus, homeIndex: -1, stillIndex: -1 });
    const intro = gsap.timeline({ paused: true });
    intro.fromTo(qa(host, '.sc-tick'), { opacity: 0 }, { opacity: 1, duration: .5, stagger: .05, clearProps: 'opacity' }, 0)
      .fromTo(bars, { scaleX: 0 }, { scaleX: 1, duration: 1.1, ease: 'expo.out', stagger: .15, clearProps: 'transform' }, .2)
      .fromTo(qa(host, '.sc-val'), { opacity: 0 }, { opacity: 1, duration: .4, stagger: .15, clearProps: 'opacity' }, .7);
    focus(-1, false);
    return { intro, loop: cyc.loop, home: cyc.home, still: cyc.still, key: () => String(cur), layout: () => tip.refresh() };
  };
})();
