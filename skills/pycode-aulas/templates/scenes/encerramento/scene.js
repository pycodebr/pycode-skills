/* Arquétipo encerramento: o fio da aula fecha o circuito. O pedido percorre as paradas das cenas anteriores (em cima),
   faz a curva e volta pelos próximos passos (embaixo) até o ponto de partida. Em repouso, o circuito fica completo.
   data: { start, done, steps: [{ label, tip }] } · as paradas de cima vêm das outras cenas do deck */
(() => {
  const { esc, q, qa, icon, tip: mkTip } = window.K;
  window.SCENES['__ID__'] = (slide, ctx) => {
    const D = ctx.data.data || {};
    const steps = D.steps || [];
    const others = ((window.DECK || {}).scenes || []).filter(s => s.id !== ctx.data.id);
    const host = q(slide, '[data-fill]');
    const AX = 130, AY = 330, TY = 110, BY = 530, L = 330, R = 1440, RR = (BY - TY) / 2;
    const d = `M${AX} ${AY}C${AX} ${TY + 90},${L - 150} ${TY},${L} ${TY}H${R}A${RR} ${RR} 0 0 1 ${R} ${BY}H${L}C${L - 150} ${BY},${AX} ${BY - 90},${AX} ${AY}`;
    const stops = others.map((s, i) => [L + 40 + (R - L - 80) * (others.length > 1 ? i / (others.length - 1) : .5), TY]);
    const stepsAt = steps.map((s, i) => [R - 120 - (R - L - 280) * (steps.length > 1 ? i / (steps.length - 1) : .5), BY]);
    host.innerHTML = `
      <div class="board">
        <svg class="en-svg" viewBox="0 0 1696 716" aria-hidden="true">
          <path class="en-path" d="${d}"/>
          <path class="en-path en-lit" d="${d}"/>
          ${stops.map(([x, y], i) => `<circle class="en-stop" data-i="${i}" cx="${x}" cy="${y}" r="13"/>`).join('')}
          <g class="en-pk"><rect x="-24" y="-24" width="48" height="48" rx="9" transform="rotate(45)"/></g>
        </svg>
        ${stops.map(([x, y], i) => `<span class="en-num mono" style="left:${x}px;top:${y - 48}px">${String(i + 1).padStart(2, '0')}</span>`).join('')}
        <div class="node en-app no-pick" style="left:${AX}px;top:${AY}px"><span class="disc">${icon('app')}</span><span class="name">${esc(D.start || '')}</span></div>
        <p class="en-done no-pick">${icon('check')}<b>${esc(D.done || '')}</b></p>
        ${steps.map((s, i) => `<div class="en-step" data-i="${i}" style="left:${stepsAt[i][0]}px;top:${stepsAt[i][1]}px"><i class="mono">${i + 1}</i><b>${esc(s.label)}</b></div>`).join('')}
      </div>`;
    const board = q(host, '.board');
    const path = q(host, '.en-lit'), pk = q(host, '.en-pk');
    const stopEls = qa(host, '.en-stop'), nums = qa(host, '.en-num'), stepEls = qa(host, '.en-step');
    const table = FX.table(path, 700), len = path.getTotalLength();
    const near = ([x, y]) => { let best = 0, bd = 1e9; table.forEach(([px, py], k) => { const dd = (px - x) ** 2 + (py - y) ** 2; if (dd < bd) { bd = dd; best = k; } }); return best / (table.length - 1); };
    const fStops = stops.map(near), fSteps = stepsAt.map(near);
    const tip = mkTip(board, ctx, [0, 0, 1696, 716]);
    const ride = { t: 1 };
    let cur = steps.length + 1, rate = 1;
    path.style.strokeDasharray = `${len} ${len}`;
    const paint = () => {
      const [x, y] = FX.at(table, ride.t);
      pk.setAttribute('transform', `translate(${x.toFixed(1)} ${y.toFixed(1)})`);
      path.style.strokeDashoffset = String(len * (1 - ride.t));
      stopEls.forEach((el, i) => { const on = ride.t >= fStops[i] - .002; el.classList.toggle('done', on); nums[i].classList.toggle('done', on); });
      stepEls.forEach((el, i) => el.classList.toggle('done', ride.t >= fSteps[i] - .002));
      board.classList.toggle('complete', ride.t >= .999);
    };
    const target = i => (i === 0 ? fStops[fStops.length - 1] ?? .4 : i <= steps.length ? fSteps[i - 1] : 1);
    const focus = (i, anim) => {
      cur = i;
      stepEls.forEach((el, j) => el.classList.toggle('on', j === i - 1));
      gsap.killTweensOf(ride);
      const to = target(i);
      if (anim && ctx.motion()) {
        if (i === 0) ride.t = 0;
        gsap.to(ride, { t: to, duration: (i === 0 ? 2.2 : .9) / rate, ease: i === 0 ? 'power1.inOut' : 'power2.inOut', onUpdate: paint });
      } else { ride.t = to; paint(); }
      if (i >= 1 && i <= steps.length) tip.show(stepsAt[i - 1][0], BY - 70, 't', steps[i - 1].label, steps[i - 1].tip, anim);
      else tip.hide();
    };
    ctx.pick(stepEls, i => focus(i + 1, true), { group: 'passo', label: (el, i) => `${steps[i].label}: ${steps[i].tip}` });
    const n = steps.length + 2;
    const cyc = FX.cycle({ n, every: 2.5, onStep: focus, homeIndex: n - 1, stillIndex: n - 1 });
    const intro = gsap.timeline({ paused: true });
    intro.fromTo(q(host, '.en-path'), { opacity: 0 }, { opacity: 1, duration: .8, clearProps: 'opacity' }, 0)
      .fromTo(qa(host, '.en-num, .en-step'), { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: .45, stagger: .05, clearProps: 'opacity,transform' }, .2)
      .fromTo(q(host, '.en-app .disc'), { scale: .6, opacity: 0 }, { scale: 1, opacity: 1, duration: .6, ease: 'back.out(2)', clearProps: 'opacity,transform' }, .1);
    focus(n - 1, false);
    return { intro, loop: cyc.loop, home: cyc.home, still: cyc.still, key: () => String(cur), layout: () => tip.refresh(), speed: k => { rate = k; } };
  };
})();
