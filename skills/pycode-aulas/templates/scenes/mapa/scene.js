/* Arquétipo mapa: um mapa de metrô com uma estação central e linhas coloridas até cada destino.
   Um trem percorre a linha escolhida. Serve para ecossistemas, integrações, caminhos de estudo e dependências.
   data: { center: { label, icon }, stations: [{ label, icon, tone, x, y, tip }] } (x, y no palco de 1696×716) */
(() => {
  const { esc, q, qa, icon, tone, tip: mkTip } = window.K;
  window.SCENES['__ID__'] = (slide, ctx) => {
    const D = ctx.data.data || {};
    const st = D.stations || [];
    const host = q(slide, '[data-fill]');
    const CX = 848, CY = 372;
    // rota de metrô: um trecho reto e um trecho a 45 graus
    const route = (x1, y1) => {
      const dx = x1 - CX, dy = y1 - CY, sx = Math.sign(dx) || 1, sy = Math.sign(dy) || 1;
      if (Math.abs(dx) >= Math.abs(dy)) return `M${CX} ${CY}L${CX + sx * Math.abs(dy)} ${y1}L${x1} ${y1}`;
      return `M${CX} ${CY}L${x1} ${CY + sy * Math.abs(dx)}L${x1} ${y1}`;
    };
    const grid = [];
    for (let x = 0; x <= 1696; x += 106) grid.push(`M${x} 0V716`);
    for (let y = 22; y <= 716; y += 106) grid.push(`M0 ${y}H1696`);
    host.innerHTML = `
      <div class="board">
        <svg class="mp-svg" viewBox="0 0 1696 716" aria-hidden="true">
          <path class="mp-grid" d="${grid.join('')}"/>
          ${st.map((s, i) => `<path class="mp-line" data-i="${i}" style="--tone:${tone(s.tone)}" d="${route(s.x, s.y)}"/>`).join('')}
          ${st.map((s, i) => `<circle class="mp-pk" data-i="${i}" r="7" style="--tone:${tone(s.tone)}"/>`).join('')}
          <g class="mp-train no-pick"><rect x="-26" y="-13" width="52" height="26" rx="13"/></g>
        </svg>
        <div class="mp-center no-pick" style="left:${CX}px;top:${CY}px"><span>${icon(D.center?.icon || 'app')}</span><b>${esc(D.center?.label || '')}</b></div>
        ${st.map((s, i) => { const vert = Math.abs(s.x - CX) < Math.abs(s.y - CY); const side = vert ? (s.x > 1150 ? 'flip' : 'side') : 'above'; return `<div class="mp-st ${side}" data-i="${i}" style="left:${s.x}px;top:${s.y}px;--tone:${tone(s.tone)}"><i class="mp-ring"></i><span class="mp-tag"><span class="mp-ic">${icon(s.icon)}</span><b>${esc(s.label)}</b></span></div>`; }).join('')}
      </div>`;
    const board = q(host, '.board');
    const lines = qa(host, '.mp-line'), els = qa(host, '.mp-st'), pks = qa(host, '.mp-pk'), train = q(host, '.mp-train');
    const tables = lines.map(l => FX.table(l, 120));
    const tip = mkTip(board, ctx, [0, 0, 1696, 716]);
    let cur = -1, rate = 1;
    const ride = { t: 0 };
    const placeTrain = () => { const tb = tables[cur]; if (!tb) return; const [x, y] = FX.at(tb, ride.t); train.setAttribute('transform', `translate(${x.toFixed(1)} ${y.toFixed(1)})`); };
    const focus = (i, anim) => {
      cur = i;
      lines.forEach((l, j) => { l.classList.toggle('on', j === i); });
      els.forEach((el, j) => el.classList.toggle('on', j === i));
      board.classList.toggle('has-focus', i >= 0);
      gsap.killTweensOf(ride);
      if (i < 0) { tip.hide(); return; }
      train.style.setProperty('--tone', tone(st[i].tone));
      if (anim && ctx.motion()) { ride.t = 0; gsap.to(ride, { t: 1, duration: 1.2 / rate, ease: 'power2.inOut', onUpdate: placeTrain }); }
      else { ride.t = 1; placeTrain(); }
      const s = st[i], side = s.y < CY - 80 ? 'b' : s.y > CY + 80 ? 't' : (s.x > CX ? 'l' : 'r');
      tip.show(s.x + (side === 'l' ? -60 : side === 'r' ? 60 : 0), s.y + (side === 'b' ? 70 : side === 't' ? -60 : 0), side, s.label, s.tip, anim);
    };
    ctx.pick(els, i => focus(i, true), { group: 'estacao', label: (el, i) => `${st[i].label}: ${st[i].tip || ''}` });
    const cyc = FX.cycle({ n: st.length, every: 2.6, onStep: focus, homeIndex: -1, stillIndex: -1 });
    const intro = gsap.timeline({ paused: true });
    intro.fromTo(q(host, '.mp-grid'), { opacity: 0 }, { opacity: 1, duration: .8, clearProps: 'opacity' }, 0)
      .fromTo(q(host, '.mp-center'), { scale: 0 }, { scale: 1, duration: .7, ease: 'back.out(1.8)', clearProps: 'transform' }, .1)
      .add(FX.draw(lines, { duration: 1, stagger: .12 }), .3)
      .fromTo(qa(host, '.mp-st'), { opacity: 0 }, { opacity: 1, duration: .4, stagger: .12, clearProps: 'opacity' }, .9);
    let t = 0;
    const ambient = dt => {
      t += dt;
      pks.forEach((p, i) => {
        const [x, y] = FX.at(tables[i], (t * .16 + i * .21) % 1);
        p.setAttribute('cx', x.toFixed(1)); p.setAttribute('cy', y.toFixed(1));
      });
    };
    ambient(0);
    return { intro, loop: cyc.loop, home: cyc.home, still: cyc.still, key: () => String(cur), ambient, layout: () => tip.refresh(), speed: k => { rate = k; } };
  };
})();
