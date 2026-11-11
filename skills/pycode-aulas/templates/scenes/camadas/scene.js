/* Arquétipo camadas: uma pilha de camadas em perspectiva. O pedido desce camada por camada e a resposta sobe.
   Serve para arquitetura em camadas, pilha de tecnologias, níveis de abstração ou andares de um processo.
   data: { drop, response, responseTip, layers: [{ label, icon, tip }] } */
(() => {
  const { esc, q, qa, icon, tip: mkTip } = window.K;
  window.SCENES['__ID__'] = (slide, ctx) => {
    const D = ctx.data.data || {};
    const L = D.layers || [];
    const host = q(slide, '[data-fill]');
    const n = L.length, CX = 520, W = 640, DP = 172, TH = 46;
    const GAP = Math.min(150, (716 - DP - TH - 40) / Math.max(1, n - 1));
    const cy = L.map((_, i) => 40 + DP / 2 + i * GAP);
    const slab = (y, k) => {
      const l = CX - W / 2, r = CX + W / 2, t = y - DP / 2, b = y + DP / 2;
      return `<g class="cm-slab" data-i="${k}">
        <polygon class="cm-left" points="${l},${y} ${CX},${b} ${CX},${b + TH} ${l},${y + TH}"/>
        <polygon class="cm-right" points="${CX},${b} ${r},${y} ${r},${y + TH} ${CX},${b + TH}"/>
        <polygon class="cm-top" points="${l},${y} ${CX},${t} ${r},${y} ${CX},${b}"/>
        <path class="cm-grid" d="M${l + W * .25},${y - DP * .25} L${CX + W * .25},${y + DP * .25} M${CX - W * .25},${y + DP * .25} L${r - W * .25},${y - DP * .25}"/>
      </g>`;
    };
    host.innerHTML = `
      <div class="board">
        <svg class="cm-svg" viewBox="0 0 1696 716" aria-hidden="true">
          <path class="cm-axis" d="M${CX} ${cy[0] - DP / 2 - 30}V${cy[n - 1] + DP / 2 + TH + 10}"/>
          ${L.map((_, i) => slab(cy[n - 1 - i], n - 1 - i)).join('')}
          ${L.map((_, i) => `<path class="cm-lead" data-i="${i}" d="M${CX + W / 2 + 14} ${cy[i] + TH / 2}H${CX + W / 2 + 72}"/>`).join('')}
        </svg>
        ${L.map((x, i) => `<div class="cm-label" data-i="${i}" style="top:${cy[i] + TH / 2}px"><span class="cm-ic">${icon(x.icon)}</span><b>${esc(x.label)}</b></div>`).join('')}
        <div class="cm-drop no-pick"><i></i><b class="mono">${esc(D.drop || '')}</b></div>
        <p class="cm-resp mono no-pick">${icon('bolt')}${esc(D.response || '')}</p>
      </div>`;
    const board = q(host, '.board');
    const slabs = L.map((_, i) => q(host, `.cm-slab[data-i="${i}"]`));
    const labels = qa(host, '.cm-label'), leads = qa(host, '.cm-lead'), drop = q(host, '.cm-drop');
    const tip = mkTip(board, ctx, [0, 0, 1696, 716]);
    let cur = -1, rate = 1;
    const moveDrop = (y, anim) => {
      gsap.killTweensOf(drop);
      if (anim && ctx.motion()) gsap.to(drop, { y, duration: .8 / rate, ease: 'power3.inOut' });
      else gsap.set(drop, { y });
    };
    const focus = (i, anim) => {
      cur = i;
      const up = i === n;
      slabs.forEach((s, j) => { s.classList.toggle('on', j === i); s.classList.toggle('past', i >= 0 && !up && j < i); s.classList.toggle('up', up); });
      labels.forEach((el, j) => el.classList.toggle('on', j === i || up));
      leads.forEach((el, j) => el.classList.toggle('on', j === i));
      board.classList.toggle('going-up', up);
      board.classList.toggle('has-drop', i >= 0);
      if (i < 0) { tip.hide(); moveDrop(cy[0] - DP / 2 - 40, false); return; }
      if (up) { moveDrop(cy[0] - DP / 2 - 40, anim); tip.show(CX + W / 2 + 140, 40, 'r', D.response, D.responseTip, anim); return; }
      moveDrop(cy[i] - 34, anim);
      const lb = labels[i];
      tip.show(lb.offsetLeft + lb.offsetWidth + 10, cy[i] + TH / 2, 'r', L[i].label, L[i].tip, anim);
    };
    ctx.pick(labels, i => focus(i, true), { group: 'camada', label: (el, i) => `${L[i].label}: ${L[i].tip}` });
    ctx.pick(slabs.map(s => q(s, '.cm-top')), i => focus(i, true), { group: 'camada-desenho', key: false });
    const cyc = FX.cycle({ n: n + 1, every: 2.4, onStep: focus, homeIndex: -1, stillIndex: -1 });
    const intro = gsap.timeline({ paused: true });
    intro.fromTo([...slabs].reverse(), { opacity: 0, y: -60 }, { opacity: 1, y: 0, duration: .7, ease: 'bounce.out', stagger: .14, clearProps: 'opacity,transform' }, 0)
      .add(FX.draw(leads, { duration: .5, stagger: .1 }), .7)
      .fromTo(labels, { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: .5, stagger: .1, clearProps: 'opacity,transform' }, .8);
    focus(-1, false);
    return { intro, loop: cyc.loop, home: cyc.home, still: cyc.still, key: () => String(cur), layout: () => tip.refresh(), speed: k => { rate = k; } };
  };
})();
