/* Arquétipo mostrador: um número grande com rolagem de dígitos e um mostrador em meia-lua com uma faixa por item.
   A agulha aponta para o item escolhido, o número gira e a cor acompanha o tom.
   Serve para códigos, notas, métricas e qualquer escala de categorias.
   data: { items: [{ value, family, label, tone, tip }], prefix?, suffix? } */
(() => {
  const { esc, q, qa, tone } = window.K;
  window.SCENES['__ID__'] = (slide, ctx) => {
    const D = ctx.data.data || {};
    const items = D.items || [];
    const host = q(slide, '[data-fill]');
    const n = items.length, CX = 1250, CY = 610, R = 330, SW = 74, GAP = 2.2;
    const arc = (a0, a1, r) => {
      const p = a => [CX + Math.cos(a * Math.PI / 180) * r, CY + Math.sin(a * Math.PI / 180) * r];
      const [x0, y0] = p(a0), [x1, y1] = p(a1);
      return `M${x0.toFixed(1)} ${y0.toFixed(1)}A${r} ${r} 0 0 1 ${x1.toFixed(1)} ${y1.toFixed(1)}`;
    };
    const seg = i => [180 + i * 180 / n + GAP, 180 + (i + 1) * 180 / n - GAP];
    const mid = i => 180 + (i + .5) * 180 / n;
    const ticks = Array.from({ length: 61 }, (_, k) => {
      const a = (180 + k * 3) * Math.PI / 180, r1 = R - SW / 2 - 18, r2 = r1 - (k % 5 ? 10 : 22);
      return `M${(CX + Math.cos(a) * r1).toFixed(1)} ${(CY + Math.sin(a) * r1).toFixed(1)}L${(CX + Math.cos(a) * r2).toFixed(1)} ${(CY + Math.sin(a) * r2).toFixed(1)}`;
    }).join('');
    const digits = String(Math.max(...items.map(x => String(x.value).length), 1));
    host.innerHTML = `
      <div class="board">
        <div class="nm-left">
          <p class="nm-num" aria-live="polite">${Array.from({ length: +digits }, () => '<span class="nm-d" aria-hidden="true"></span>').join('')}<span class="sr-only nm-sr"></span></p>
          <h3 class="nm-label"></h3>
          <p class="nm-tip"></p>
        </div>
        <svg class="nm-svg" viewBox="0 0 1696 716" aria-hidden="true">
          <path class="nm-ticks" d="${ticks}"/>
          ${items.map((it, i) => `<path class="nm-seg" data-i="${i}" style="--tone:${tone(it.tone)}" d="${arc(...seg(i), R)}"/>`).join('')}
          <g class="nm-needle"><path d="M${CX - 12} ${CY}L${CX} ${CY - R + 70}L${CX + 12} ${CY}Z"/><circle cx="${CX}" cy="${CY}" r="30"/></g>
        </svg>
        ${items.map((it, i) => { const a = mid(i) * Math.PI / 180, r = R + SW / 2 + 40; return `<span class="nm-fam mono" data-i="${i}" style="left:${(CX + Math.cos(a) * r).toFixed(0)}px;top:${(CY + Math.sin(a) * r).toFixed(0)}px;--tone:${tone(it.tone)}">${esc(it.family || it.value)}</span>`; }).join('')}
      </div>`;
    const board = q(host, '.board');
    const segs = qa(host, '.nm-seg'), fams = qa(host, '.nm-fam'), dEls = qa(host, '.nm-d');
    const needle = q(host, '.nm-needle'), label = q(host, '.nm-label'), tipEl = q(host, '.nm-tip'), sr = q(host, '.nm-sr');
    let cur = 0;
    const focus = (i, anim) => {
      cur = i;
      const it = items[i] || {};
      board.style.setProperty('--tone', tone(it.tone));
      segs.forEach((s, j) => s.classList.toggle('on', j === i));
      fams.forEach((s, j) => s.classList.toggle('on', j === i));
      const v = String(it.value).padStart(dEls.length, ' ');
      board.classList.toggle('instant', !(anim && ctx.motion()));
      dEls.forEach((d, k) => { d.style.setProperty('--d', /\d/.test(v[k]) ? v[k] : 0); d.style.setProperty('--dl', (k * .08) + 's'); d.classList.toggle('blank', !/\d/.test(v[k])); });
      sr.textContent = String(it.value);
      label.textContent = it.label || ''; tipEl.textContent = it.tip || '';
      const angle = mid(i) - 270;
      gsap.killTweensOf(needle);
      if (anim && ctx.motion()) {
        gsap.to(needle, { rotation: angle, svgOrigin: `${CX} ${CY}`, duration: .9, ease: 'elastic.out(1, .6)' });
        gsap.fromTo([label, tipEl], { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .5, stagger: .08, clearProps: 'opacity,transform' });
      } else gsap.set(needle, { rotation: angle, svgOrigin: `${CX} ${CY}` });
    };
    ctx.pick(segs, i => focus(i, true), { group: 'faixa', label: (el, i) => `${items[i].value}: ${items[i].label}` });
    ctx.pick(fams, i => focus(i, true), { group: 'familia', label: (el, i) => `${items[i].family || items[i].value}: ${items[i].label}`, key: false });
    const cyc = FX.cycle({ n, every: 2.6, onStep: focus, homeIndex: 0, stillIndex: 0 });
    const intro = gsap.timeline({ paused: true });
    intro.fromTo(segs, { opacity: 0 }, { opacity: 1, duration: .4, stagger: .1, clearProps: 'opacity' }, 0)
      .add(FX.draw(segs, { duration: .7, stagger: .1 }), 0)
      .fromTo(q(host, '.nm-ticks'), { opacity: 0 }, { opacity: 1, duration: .8, clearProps: 'opacity' }, .2)
      .fromTo(fams, { opacity: 0 }, { opacity: 1, duration: .4, stagger: .08, clearProps: 'opacity' }, .5)
      .fromTo(q(host, '.nm-left'), { opacity: 0, x: -40 }, { opacity: 1, x: 0, duration: .8, ease: 'expo.out', clearProps: 'opacity,transform' }, .2);
    focus(0, false);
    return { intro, loop: cyc.loop, home: cyc.home, still: cyc.still, key: () => String(cur) };
  };
})();
