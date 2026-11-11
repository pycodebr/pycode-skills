/* Arquétipo circuito: objetos ligados por trilhas de placa de circuito. O pedido (losango) viaja de nó em nó e
   volta pela trilha de baixo; pacotes pequenos correm o tempo todo como movimento ambiente.
   data: { nodes: [{ label, icon, tip }], back: "rótulo da volta", packet: "42" } */
(() => {
  const { esc, q, qa, icon, tip: mkTip } = window.K;
  window.SCENES['__ID__'] = (slide, ctx) => {
    const D = ctx.data.data || {};
    const nodes = D.nodes || [];
    const host = q(slide, '[data-fill]');
    const n = nodes.length, X0 = 150, X1 = 1546, Y = 290, YB = 590;
    const xs = nodes.map((_, i) => X0 + (X1 - X0) * (n > 1 ? i / (n - 1) : .5));
    const go = `M${X0} ${Y}H${X1}`;
    const back = `M${X1 + 66} ${Y}H${X1 + 100}V${YB - 40}q0 40 -40 40H${X0 - 60}q-40 0 -40 -40V${Y}H${X0 - 66}`;
    // trilhas decorativas de placa, geradas de forma determinística
    const deco = [];
    for (let i = 0; i < 8; i++) {
      const y = 36 + i * 14 + (i % 3) * 8, x = 60 + (i * 173) % 980, w = 120 + (i * 67) % 200;
      deco.push(`M${x} ${y}h${w}l22 22h${80 + (i * 31) % 120}`);
      const y2 = 700 - i * 10, x2 = 90 + (i * 211) % 1180;
      deco.push(`M${x2} ${y2}h${90 + (i * 43) % 160}l-18 -18h-${60 + (i * 17) % 80}`);
    }
    host.innerHTML = `
      <div class="board">
        <svg class="ci-svg" viewBox="0 0 1696 716" aria-hidden="true">
          <g class="ci-deco">${deco.map(d => `<path d="${d}"/>`).join('')}${deco.map((d, i) => { const m = d.match(/M(\d+) (\d+)/); return `<circle cx="${m[1]}" cy="${m[2]}" r="4"/>`; }).join('')}</g>
          <path class="ci-track ci-go" d="${go}"/>
          <path class="ci-track ci-back" d="${back}"/>
          ${xs.map(x => `<circle class="ci-via" cx="${x}" cy="${Y}" r="10"/>`).join('')}
          ${Array.from({ length: 7 }, (_, i) => `<circle class="ci-pk${i % 2 ? ' alt' : ''}" r="5"/>`).join('')}
        </svg>
        <p class="ci-back-label mono no-pick">${esc(D.back || '')}</p>
        ${nodes.map((nd, i) => `<div class="node ci-node" data-i="${i}" style="left:${xs[i]}px;top:${Y}px"><span class="disc">${icon(nd.icon)}</span><span class="name">${esc(nd.label)}</span></div>`).join('')}
        <div class="ci-packet no-pick" style="left:0;top:0"><i></i><b class="mono">${esc(D.packet || '')}</b></div>
      </div>`;
    const board = q(host, '.board');
    const els = qa(host, '.ci-node'), pk = q(host, '.ci-packet');
    const pks = qa(host, '.ci-pk');
    const tGo = FX.table(q(host, '.ci-go'), 200), tBack = FX.table(q(host, '.ci-back'), 300);
    const tip = mkTip(board, ctx, [0, 0, 1696, 716]);
    let cur = -1;
    const place = (x, y, anim) => {
      gsap.killTweensOf(pk);
      if (anim && ctx.motion()) gsap.to(pk, { x, y: y - 112, duration: .9, ease: 'power3.inOut' });
      else gsap.set(pk, { x, y: y - 112 });
    };
    const focus = (i, anim) => {
      cur = i;
      els.forEach((el, j) => { el.classList.toggle('on', j === i); el.classList.toggle('done', i >= 0 && j < i); });
      board.classList.toggle('returning', i === n);
      if (i < 0) { tip.hide(); place(xs[0], Y, false); gsap.set(pk, { opacity: 0 }); return; }
      gsap.set(pk, { opacity: 1 });
      if (i === n) {
        place(xs[0], Y, anim);
        tip.show(848, YB - 12, 't', '', D.backTip || '', anim);
        return;
      }
      place(xs[i], Y, anim);
      tip.show(xs[i], Y + 110, 'b', nodes[i].label, nodes[i].tip, anim);
    };
    ctx.pick(els, i => focus(i, true), { group: 'no', label: (el, i) => `${nodes[i].label}: ${nodes[i].tip || ''}` });
    const cyc = FX.cycle({ n: n + 1, every: 2.6, onStep: focus, homeIndex: -1, stillIndex: n });
    const intro = gsap.timeline({ paused: true });
    intro.fromTo(q(host, '.ci-deco'), { opacity: 0 }, { opacity: 1, duration: 1, clearProps: 'opacity' }, 0)
      .add(FX.draw(q(host, '.ci-go'), { duration: 1.1 }), .1)
      .fromTo(qa(host, '.ci-node .disc'), { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: .6, stagger: .12, ease: 'back.out(1.8)', clearProps: 'opacity,transform' }, .3)
      .fromTo(qa(host, '.ci-node .name'), { opacity: 0 }, { opacity: 1, duration: .4, stagger: .12, clearProps: 'opacity' }, .5)
      .add(FX.draw(q(host, '.ci-back'), { duration: 1.2 }), .9)
      .fromTo(q(host, '.ci-back-label'), { opacity: 0 }, { opacity: 1, duration: .5, clearProps: 'opacity' }, 1.6);
    let t = 0;
    const ambient = dt => {
      t += dt;
      pks.forEach((p, i) => {
        const go = i < 4, u = (t * (go ? .12 : .09) + i / 4) % 1;
        const [x, y] = FX.at(go ? tGo : tBack, u);
        p.setAttribute('cx', x.toFixed(1)); p.setAttribute('cy', y.toFixed(1));
      });
    };
    ambient(0);
    return {
      intro, loop: cyc.loop, home: cyc.home, still: cyc.still, key: () => String(cur), ambient,
      layout: () => tip.refresh()
    };
  };
})();
