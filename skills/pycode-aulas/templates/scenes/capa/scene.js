/* Arquétipo capa: título grande à esquerda e uma constelação de objetos ligados a um núcleo, com pacotes
   correndo pelas ligações. A demonstração acende cada satélite e mostra uma frase curta; em repouso a capa fica limpa.
   data: { subtitle, byline, core: { label, icon }, satellites: [{ label, icon, tip }] } */
(() => {
  const { esc, q, qa, icon, tip: mkTip } = window.K;
  window.SCENES['__ID__'] = (slide, ctx) => {
    const D = ctx.data.data || {};
    const sats = D.satellites || [];
    const host = q(slide, '[data-fill]');
    const CX = 1236, CY = 352, R = 268;
    const pos = sats.map((s, i) => {
      const a = (s.angle ?? (-90 + i * 360 / sats.length)) * Math.PI / 180;
      return [CX + Math.cos(a) * R, CY + Math.sin(a) * R];
    });
    const ring = Array.from({ length: 72 }, (_, i) => {
      const a = i / 72 * Math.PI * 2, r1 = R + 70, r2 = R + (i % 6 ? 78 : 92);
      return `M${(CX + Math.cos(a) * r1).toFixed(1)} ${(CY + Math.sin(a) * r1).toFixed(1)}L${(CX + Math.cos(a) * r2).toFixed(1)} ${(CY + Math.sin(a) * r2).toFixed(1)}`;
    }).join('');
    host.innerHTML = `
      <div class="board">
        <div class="cp-text">
          ${D.subtitle ? `<p class="cp-sub">${esc(D.subtitle)}</p>` : ''}
          ${D.byline ? `<p class="cp-by mono">${esc(D.byline)}</p>` : ''}
        </div>
        <svg class="cp-svg" viewBox="0 0 1696 716" aria-hidden="true">
          <circle class="cp-orbit" cx="${CX}" cy="${CY}" r="${R}"/>
          <circle class="cp-orbit thin" cx="${CX}" cy="${CY}" r="${R - 120}"/>
          <g class="cp-rot"><path class="cp-ticks" d="${ring}"/></g>
          ${pos.map(([x, y], i) => `<path class="cp-link" data-i="${i}" d="M${CX} ${CY}L${x.toFixed(1)} ${y.toFixed(1)}"/>`).join('')}
          ${pos.map((_, i) => `<circle class="cp-pk" data-i="${i}" r="7"/>`).join('')}
        </svg>
        <div class="cp-core no-pick" style="left:${CX}px;top:${CY}px">${icon(D.core?.icon || 'gate')}<b>${esc(D.core?.label || '')}</b></div>
        ${sats.map((s, i) => `<div class="node cp-sat" data-i="${i}" style="left:${pos[i][0].toFixed(0)}px;top:${pos[i][1].toFixed(0)}px"><span class="disc">${icon(s.icon)}</span><span class="name">${esc(s.label)}</span></div>`).join('')}
      </div>`;
    const board = q(host, '.board');
    const satEls = qa(host, '.cp-sat'), links = qa(host, '.cp-link'), pks = qa(host, '.cp-pk');
    const tip = mkTip(board, ctx, [700, 0, 1696, 716]);
    const tables = links.map(l => FX.table(l, 60));
    let cur = -1;
    const focus = (i, anim) => {
      cur = i;
      satEls.forEach((el, j) => el.classList.toggle('on', j === i));
      links.forEach((el, j) => el.classList.toggle('hot', j === i));
      board.classList.toggle('has-focus', i >= 0);
      if (i < 0) { tip.hide(); return; }
      const [x, y] = pos[i], side = x > CX + 40 ? 'l' : x < CX - 40 ? 'r' : (y < CY ? 'b' : 't');
      const off = side === 'l' ? -70 : side === 'r' ? 70 : 0, offY = side === 'b' ? 80 : side === 't' ? -70 : 0;
      tip.show(x + off, y + offY, side, sats[i].label, sats[i].tip, anim);
    };
    ctx.pick(satEls, i => focus(i, true), { group: 'objeto', label: (el, i) => `${sats[i].label}: ${sats[i].tip || ''}` });
    const cyc = FX.cycle({ n: sats.length, every: 2.4, onStep: focus, homeIndex: -1, stillIndex: -1 });
    const intro = gsap.timeline({ paused: true });
    intro.fromTo(q(host, '.cp-core'), { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: .9, ease: 'back.out(1.6)', clearProps: 'transform,opacity' }, .1)
      .fromTo(qa(host, '.cp-orbit, .cp-ticks'), { opacity: 0, scale: .7, svgOrigin: `${CX} ${CY}` }, { opacity: 1, scale: 1, duration: 1.1, ease: 'expo.out', stagger: .1, clearProps: 'transform,opacity' }, .2)
      .add(FX.draw(links, { duration: .9, stagger: .08 }), .5)
      .fromTo(qa(host, '.cp-sat .disc'), { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: .6, ease: 'back.out(2)', stagger: .09, clearProps: 'opacity,transform' }, .7)
      .fromTo(qa(host, '.cp-sat .name'), { opacity: 0 }, { opacity: 1, duration: .5, stagger: .09, clearProps: 'opacity' }, .9)
      .fromTo(qa(host, '.cp-text > *'), { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: .7, stagger: .12, clearProps: 'transform,opacity' }, .5);
    // movimento ambiente: pacotes vão e voltam pelas ligações e a régua gira devagar
    let t = 0;
    const ticks = q(host, '.cp-rot');
    const ambient = dt => {
      t += dt;
      pks.forEach((p, i) => {
        const u = (t * .32 + i * .23) % 2, k = u < 1 ? u : 2 - u;
        const [x, y] = FX.at(tables[i], k);
        p.setAttribute('cx', x.toFixed(1)); p.setAttribute('cy', y.toFixed(1));
      });
      ticks.setAttribute('transform', `rotate(${(t * 2) % 360} ${CX} ${CY})`);
    };
    ambient(0);
    return { intro, loop: cyc.loop, home: cyc.home, still: cyc.still, key: () => String(cur), ambient, layout: () => tip.refresh() };
  };
})();
