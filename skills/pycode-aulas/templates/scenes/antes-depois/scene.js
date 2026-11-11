/* Arquétipo antes-depois: o mesmo cenário em dois estados, lado a lado. À esquerda, o emaranhado; à direita, a
   versão organizada, com regras em volta da peça central. A demonstração mostra o antes, o depois e cada regra.
   data: { before: { chip, label, tip }, after: { chip, label, tip, gate }, db, clients: [{ label, icon }],
           rules: [{ label, tip }] } */
(() => {
  const { esc, q, qa, icon, tip: mkTip } = window.K;
  window.SCENES['__ID__'] = (slide, ctx) => {
    const D = ctx.data.data || {};
    const B = D.before || {}, A = D.after || {}, cl = D.clients || [], rules = D.rules || [];
    const host = q(slide, '[data-fill]');
    const ys = cl.map((_, i) => 210 + i * (430 / Math.max(1, cl.length - 1)));
    const LX = 96, DBL = 640, RX = 992, GX = 1300, DBR = 1586, MY = 425;
    // emaranhado determinístico: cada cliente entra no banco por um ponto diferente, cruzando os outros
    const tangle = cl.map((_, i) => {
      const j = cl.length - 1 - i, y = ys[i], y2 = MY - 60 + i * 40;
      return `M${LX + 58} ${y}C${300} ${ys[j]},${420} ${y + (i % 2 ? 160 : -160)},${DBL - 70} ${y2}`;
    });
    const extra = cl.map((_, i) => `M${LX + 58} ${ys[i]}C${360} ${ys[(i + 2) % cl.length]},${470} ${MY + (i - 1.5) * 90},${DBL - 70} ${MY + 50 - i * 30}`);
    const neat = cl.map((_, i) => `M${RX + 58} ${ys[i]}C${RX + 170} ${ys[i]},${GX - 170} ${MY},${GX - 66} ${MY}`);
    host.innerHTML = `
      <div class="board">
        <div class="ad-half ad-before"><span class="chip">${esc(B.chip || '')}</span><h3>${esc(B.label || '')}</h3></div>
        <div class="ad-half ad-after"><span class="chip">${esc(A.chip || '')}</span><h3>${esc(A.label || '')}</h3></div>
        <div class="ad-divider no-pick"><i></i></div>
        <svg class="ad-svg" viewBox="0 0 1696 716" aria-hidden="true">
          <g class="ad-tangle">${tangle.concat(extra).map(d => `<path d="${d}"/>`).join('')}</g>
          <g class="ad-neat">${neat.map(d => `<path d="${d}"/>`).join('')}<path class="ad-trunk" d="M${GX + 66} ${MY}H${DBR - 66}"/></g>
          ${cl.concat(cl).map((_, i) => `<circle class="ad-pk" r="6"/>`).join('')}
        </svg>
        ${cl.map((c, i) => `<div class="node ad-cl" style="left:${LX}px;top:${ys[i]}px"><span class="disc">${icon(c.icon)}</span><span class="name">${esc(c.label)}</span></div>`).join('')}
        ${cl.map((c, i) => `<div class="node ad-cl" style="left:${RX}px;top:${ys[i]}px"><span class="disc">${icon(c.icon)}</span><span class="name">${esc(c.label)}</span></div>`).join('')}
        <div class="node ad-db ad-db-l" style="left:${DBL}px;top:${MY}px"><span class="disc">${icon('database')}</span><span class="name">${esc(D.db || '')}</span><b class="ad-crack no-pick">${icon('cross')}</b></div>
        <div class="node ad-db" style="left:${DBR}px;top:${MY}px"><span class="disc">${icon('database')}</span><span class="name">${esc(D.db || '')}</span></div>
        <div class="node ad-gate" style="left:${GX}px;top:${MY}px"><span class="disc">${icon('gate')}</span><span class="name">${esc(A.gate || '')}</span></div>
        <div class="ad-rules">${rules.map((r, i) => `<span class="chip ad-rule" data-i="${i}">${icon(['key', 'clock', 'check', 'shield', 'gear'][i % 5])}${esc(r.label)}</span>`).join('')}</div>
      </div>`;
    const board = q(host, '.board');
    const halves = qa(host, '.ad-half'), ruleEls = qa(host, '.ad-rule');
    const pks = qa(host, '.ad-pk');
    const tables = qa(host, '.ad-neat path').map(p => FX.table(p, 80));
    const tip = mkTip(board, ctx, [0, 0, 1696, 716]);
    let cur = -1;
    const focus = (i, anim) => {
      cur = i;
      board.classList.toggle('show-before', i === 0);
      board.classList.toggle('show-after', i >= 1);
      ruleEls.forEach((el, j) => el.classList.toggle('on', j === i - 2));
      if (i < 0) { tip.hide(); return; }
      if (i === 0) tip.show(DBL, MY - 90, 't', B.label, B.tip, anim);
      else if (i === 1) tip.show(GX, MY + 100, 'b', A.label, A.tip, anim);
      else { const el = ruleEls[i - 2]; tip.show(el.offsetLeft + el.offsetWidth / 2 + q(host, '.ad-rules').offsetLeft, q(host, '.ad-rules').offsetTop + 60, 'b', rules[i - 2].label, rules[i - 2].tip, anim); }
    };
    ctx.pick(halves, i => focus(i, true), { group: 'lado', label: (el, i) => i ? `${A.label}: ${A.tip}` : `${B.label}: ${B.tip}` });
    ctx.pick(ruleEls, i => focus(i + 2, true), { group: 'regra', label: (el, i) => `${rules[i].label}: ${rules[i].tip}` });
    const cyc = FX.cycle({ n: 2 + rules.length, every: 2.6, onStep: focus, homeIndex: -1, stillIndex: -1 });
    const intro = gsap.timeline({ paused: true });
    intro.fromTo(halves, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .6, stagger: .15, clearProps: 'opacity,transform' }, 0)
      .fromTo(q(host, '.ad-divider'), { scaleY: 0 }, { scaleY: 1, duration: .8, ease: 'expo.out', clearProps: 'transform' }, 0)
      .fromTo(qa(host, '.ad-cl .disc, .ad-db .disc, .ad-gate .disc'), { opacity: 0, scale: .7 }, { opacity: 1, scale: 1, duration: .5, stagger: .04, ease: 'back.out(2)', clearProps: 'opacity,transform' }, .3)
      .add(FX.draw(qa(host, '.ad-tangle path'), { duration: 1.3, stagger: .05 }), .6)
      .add(FX.draw(qa(host, '.ad-neat path'), { duration: .9, stagger: .06 }), .9)
      .fromTo(ruleEls, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .45, stagger: .1, clearProps: 'opacity,transform' }, 1.5);
    let t = 0;
    const ambient = dt => {
      t += dt;
      pks.forEach((p, i) => {
        const tb = tables[i % tables.length], u = (t * .35 + i * .37) % 1;
        const [x, y] = FX.at(tb, u);
        p.setAttribute('cx', x.toFixed(1)); p.setAttribute('cy', y.toFixed(1));
      });
    };
    ambient(0);
    return { intro, loop: cyc.loop, home: cyc.home, still: cyc.still, key: () => String(cur), ambient, layout: () => tip.refresh() };
  };
})();
