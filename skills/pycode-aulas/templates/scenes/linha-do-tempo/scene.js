/* Arquétipo linha do tempo com câmera: uma régua longa passa por baixo de um cursor fixo e a câmera desliza até
   cada marco. Um minimapa embaixo mostra onde a câmera está. Serve para tempos (milissegundos, anos, etapas).
   data: { unit, events: [{ at, label, tip }], scale?: px por unidade } */
(() => {
  const { esc, q, qa } = window.K;
  window.SCENES['__ID__'] = (slide, ctx) => {
    const D = ctx.data.data || {};
    const ev = D.events || [];
    const host = q(slide, '[data-fill]');
    const unit = D.unit || '';
    const min = Math.min(...ev.map(e => e.at)), max = Math.max(...ev.map(e => e.at));
    const span = Math.max(1, max - min);
    const gaps = ev.slice(1).map((e, i) => e.at - ev[i].at).filter(g => g > 0);
    const scale = D.scale || Math.max(2200 / span, 300 / Math.max(1e-6, Math.min(...gaps, span)));
    const PAD = 760, VW = 1696, RY = 330;
    const trackW = PAD * 2 + span * scale;
    const X = at => PAD + (at - min) * scale;
    // marcas da régua: passo "redondo" que dê entre 20 e 60 marcas
    const raw = span / 40, mag = 10 ** Math.floor(Math.log10(raw)), step = [1, 2, 5, 10].map(k => k * mag).find(s => s >= raw) || raw;
    const marks = [];
    for (let v = Math.ceil(min / step) * step; v <= max + 1e-9; v += step) marks.push(v);
    const fmt = v => `${window.K.fmt(v, Number.isInteger(v) ? 0 : 1)}${unit ? ' ' + unit : ''}`;
    host.innerHTML = `
      <div class="board">
        <div class="tl-window" data-clip>
          <div class="tl-track" style="width:${trackW}px">
            <div class="tl-rail"><i class="tl-fill"></i></div>
            ${marks.map((v, k) => `<span class="tl-mark${k % 5 ? '' : ' big'}" style="left:${X(v)}px">${k % 5 ? '' : `<b class="mono">${esc(fmt(v))}</b>`}</span>`).join('')}
            ${ev.map((e, i) => `<div class="tl-ev ${i % 2 ? 'down' : 'up'}" data-i="${i}" style="left:${X(e.at)}px"><i class="tl-dot"></i><span class="tl-stem"></span><div class="tl-lbl"><b class="mono">${esc(fmt(e.at))}</b><p>${esc(e.label)}</p></div></div>`).join('')}
          </div>
          <div class="tl-head no-pick"><i></i></div>
        </div>
        <p class="tl-tip"></p>
        <div class="tl-mini no-pick">${ev.map(e => `<i style="left:${((e.at - min) / span * 100).toFixed(2)}%"></i>`).join('')}<span class="tl-view"></span></div>
      </div>`;
    const board = q(host, '.board');
    const track = q(host, '.tl-track'), fill = q(host, '.tl-fill'), view = q(host, '.tl-view'), tipEl = q(host, '.tl-tip');
    const els = qa(host, '.tl-ev');
    view.style.width = Math.min(100, VW / (span * scale) * 100) + '%';
    let cur = 0, rate = 1;
    const camera = (i, anim) => {
      const x = VW / 2 - X(ev[i].at), p = Math.max(.0001, (ev[i].at - min) / span);
      gsap.killTweensOf([track, fill]);
      if (anim && ctx.motion()) {
        gsap.to(track, { x, duration: 1.1 / rate, ease: 'power3.inOut' });
        gsap.to(fill, { scaleX: p, duration: 1.1 / rate, ease: 'power3.inOut' });
      } else gsap.set(track, { x }), gsap.set(fill, { scaleX: p });
      // minimapa: o retângulo mostra a parte da régua que está dentro da janela
      const vw = Math.min(1, VW / (span * scale)), left = Math.max(0, Math.min(1 - vw, p - vw / 2));
      view.style.transform = `translateX(${(left * VW).toFixed(1)}px)`;
    };
    const focus = (i, anim) => {
      cur = i;
      els.forEach((el, j) => { el.classList.toggle('on', j === i); el.classList.toggle('past', j < i); });
      camera(i, anim);
      tipEl.textContent = ev[i]?.tip || '';
      if (anim && ctx.motion()) gsap.fromTo(tipEl, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: .5, delay: .4 / rate, clearProps: 'opacity,transform' });
    };
    ctx.pick(els, i => focus(i, true), { group: 'marco', label: (el, i) => `${fmt(ev[i].at)}: ${ev[i].label}. ${ev[i].tip || ''}` });
    const cyc = FX.cycle({ n: ev.length, every: 2.4, onStep: focus, homeIndex: 0, stillIndex: ev.length - 1 });
    const intro = gsap.timeline({ paused: true });
    intro.fromTo(q(host, '.tl-rail'), { scaleX: 0 }, { scaleX: 1, duration: 1, ease: 'expo.out', transformOrigin: '0 50%', clearProps: 'transform' }, 0)
      .fromTo(qa(host, '.tl-lbl'), { opacity: 0, y: (i) => i % 2 ? -20 : 20 }, { opacity: 1, y: 0, duration: .5, stagger: .07, clearProps: 'opacity,transform' }, .3)
      .fromTo(q(host, '.tl-mini'), { opacity: 0 }, { opacity: 1, duration: .6, clearProps: 'opacity' }, .6);
    focus(0, false);
    return { intro, loop: cyc.loop, home: cyc.home, still: cyc.still, key: () => String(cur), speed: k => { rate = k; } };
  };
})();
