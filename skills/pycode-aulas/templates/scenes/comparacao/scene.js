/* Arquétipo comparação: dois lados e uma balança. Cada critério é uma linha; ao escolher um critério, a balança
   pende para o lado que vence nele (ou fica nivelada no empate). Serve para "X ou Y", trade-offs e escolhas.
   data: { left: { label, icon }, right: { label, icon }, rows: [{ label, winner: "l"|"r"|"=", tip }] } */
(() => {
  const { esc, q, qa, icon, tip: mkTip } = window.K;
  window.SCENES['__ID__'] = (slide, ctx) => {
    const D = ctx.data.data || {};
    const Ls = D.left || {}, Rs = D.right || {}, rows = D.rows || [];
    const host = q(slide, '[data-fill]');
    const CX = 848, FY = 210, HW = 520;
    host.innerHTML = `
      <div class="board">
        <svg class="cp2-svg" viewBox="0 0 1696 716" aria-hidden="true">
          <path class="cp2-post" d="M${CX} ${FY}L${CX - 60} ${FY + 120}H${CX + 60}Z"/>
          <g class="cp2-beam">
            <path class="cp2-bar" d="M${CX - HW} ${FY}H${CX + HW}"/>
            <g class="cp2-pan l"><path d="M${CX - HW} ${FY}L${CX - HW - 70} ${FY + 90}M${CX - HW} ${FY}L${CX - HW + 70} ${FY + 90}"/><path class="cp2-bowl" d="M${CX - HW - 90} ${FY + 90}H${CX - HW + 90}Q${CX - HW} ${FY + 150} ${CX - HW - 90} ${FY + 90}Z"/></g>
            <g class="cp2-pan r"><path d="M${CX + HW} ${FY}L${CX + HW - 70} ${FY + 90}M${CX + HW} ${FY}L${CX + HW + 70} ${FY + 90}"/><path class="cp2-bowl" d="M${CX + HW - 90} ${FY + 90}H${CX + HW + 90}Q${CX + HW} ${FY + 150} ${CX + HW - 90} ${FY + 90}Z"/></g>
          </g>
          <circle class="cp2-pin" cx="${CX}" cy="${FY}" r="14"/>
        </svg>
        <div class="cp2-side l"><span>${icon(Ls.icon || 'box')}</span><b>${esc(Ls.label || '')}</b></div>
        <div class="cp2-side r"><span>${icon(Rs.icon || 'box')}</span><b>${esc(Rs.label || '')}</b></div>
        <ol class="cp2-rows">${rows.map((r, i) => `<li data-i="${i}"><i class="cp2-m l${r.winner === 'l' || r.winner === '=' ? ' win' : ''}"></i><span>${esc(r.label)}</span><i class="cp2-m r${r.winner === 'r' || r.winner === '=' ? ' win' : ''}"></i></li>`).join('')}</ol>
      </div>`;
    const board = q(host, '.board');
    const beam = q(host, '.cp2-beam'), pans = qa(host, '.cp2-pan'), els = qa(host, '.cp2-rows li');
    const tip = mkTip(board, ctx, [0, 0, 1696, 716]);
    let cur = -1;
    const tilt = (w, anim) => {
      const a = w === 'l' ? -9 : w === 'r' ? 9 : 0;
      const dy = Math.sin(a * Math.PI / 180) * HW;
      const go = (el, vars) => (anim && ctx.motion() ? gsap.to(el, { ...vars, duration: 1, ease: 'elastic.out(1, .55)' }) : gsap.set(el, vars));
      go(beam, { rotation: a, svgOrigin: `${CX} ${FY}` });
      // os pratos ficam na vertical: desfazem a rotação e acompanham a altura da ponta
      go(pans[0], { rotation: -a, svgOrigin: `${CX - HW} ${FY}` });
      go(pans[1], { rotation: -a, svgOrigin: `${CX + HW} ${FY}` });
      board.dataset.win = w || '';
      return dy;
    };
    const focus = (i, anim) => {
      cur = i;
      els.forEach((el, j) => el.classList.toggle('on', j === i));
      board.classList.toggle('has-focus', i >= 0);
      if (i < 0) { tilt('', anim); tip.hide(); return; }
      tilt(rows[i].winner, anim);
      const el = els[i];
      tip.show(el.offsetLeft + q(host, '.cp2-rows').offsetLeft + el.offsetWidth + 10, q(host, '.cp2-rows').offsetTop + el.offsetTop + el.offsetHeight / 2, 'r', rows[i].label, rows[i].tip, anim);
    };
    ctx.pick(els, i => focus(i, true), { group: 'criterio', label: (el, i) => `${rows[i].label}: ${rows[i].tip || ''}` });
    const cyc = FX.cycle({ n: rows.length, every: 2.6, onStep: focus, homeIndex: -1, stillIndex: -1 });
    const intro = gsap.timeline({ paused: true });
    intro.fromTo(q(host, '.cp2-svg'), { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: .8, ease: 'expo.out', clearProps: 'opacity,transform' }, 0)
      .fromTo(qa(host, '.cp2-side'), { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .6, stagger: .12, clearProps: 'opacity,transform' }, .2)
      .fromTo(els, { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: .4, stagger: .08, clearProps: 'opacity,transform' }, .5);
    focus(-1, false);
    return { intro, loop: cyc.loop, home: cyc.home, still: cyc.still, key: () => String(cur), layout: () => tip.refresh() };
  };
})();
