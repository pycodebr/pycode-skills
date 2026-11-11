/*
 * Níveis: escada isométrica em SVG, artefato de cada nível, numeral em canvas e medidor.
 * A capa (vídeo) acende os degraus de baixo para cima junto com o medidor.
 */
(() => {
  const C = window.Carousel;
  const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const STEP = { x0: 150, w: 150, top0: 600, rise: 92, base: 700, dx: 70, dy: 40 };
  const stepGeom = (k) => {             // k = 0..4
    const x = STEP.x0 + k * STEP.w;
    const y = STEP.top0 - k * STEP.rise;
    return { x, y, cx: x + STEP.w / 2 + STEP.dx / 2, cy: y - STEP.dy / 2 };
  };

  /* estados: 'off' | 'done' | 'on' para cada degrau */
  function drawStairs(svg, states, beam = 0) {
    let s = `<defs>
      <linearGradient id="beam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" style="stop-color:var(--accent);stop-opacity:.42"/><stop offset=".7" style="stop-color:var(--accent);stop-opacity:0"/></linearGradient>
      <radialGradient id="pool"><stop offset="0" style="stop-color:var(--accent);stop-opacity:.45"/><stop offset="1" style="stop-color:var(--accent);stop-opacity:0"/></radialGradient></defs>`;
    s += `<ellipse class="pool" cx="560" cy="712" rx="520" ry="60" opacity="${0.25 + 0.5 * beam}"/>`;
    for (let k = 0; k < 5; k++) {
      const { x, y } = stepGeom(k);
      const st = states[k];
      const { w, dx, dy, base } = STEP;
      s += `<g data-step="${k}">
        <path class="side ${st}" d="M${x + w} ${y} L${x + w + dx} ${y - dy} L${x + w + dx} ${base - dy} L${x + w} ${base} Z"/>
        <path class="front ${st}" d="M${x} ${y} H${x + w} V${base} H${x} Z"/>
        <path class="top ${st}" d="M${x} ${y} L${x + dx} ${y - dy} H${x + w + dx} L${x + w} ${y} Z"/>
        <path class="edge" d="M${x} ${y} H${x + w} L${x + w + dx} ${y - dy} M${x} ${y} V${base}"/>
        <text class="num ${st === 'on' ? 'on' : ''}" x="${x + w / 2}" y="${y + 52}">${k + 1}</text></g>`;
    }
    const on = states.lastIndexOf('on');
    if (on >= 0) {
      const g = stepGeom(on);
      const top = Math.max(-60, g.y - 300);
      s += `<path class="beam" d="M${g.x + 6} ${g.y} L${g.x + STEP.w - 6} ${g.y} L${g.x + STEP.w + STEP.dx - 10} ${g.y - STEP.dy} L${g.x + STEP.w + STEP.dx - 10} ${top} L${g.x + 6} ${top + 30} Z" opacity="${(0.2 + 0.35 * beam).toFixed(3)}"/>`;
    }
    svg.innerHTML = s;
  }

  function meter(slide, states) {
    slide.querySelectorAll('.meter i').forEach((el, i) => { el.className = states[i] === 'off' ? '' : states[i]; });
  }

  function numeral(canvas, digit) {
    const ctx = canvas.getContext('2d');
    const fam = C.token('--font-display');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = `800 400px ${fam}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'alphabetic';
    const m = ctx.measureText(String(digit));
    const base = (canvas.height + m.actualBoundingBoxAscent) / 2;
    ctx.shadowColor = C.token('--accent');
    ctx.shadowBlur = 40;
    ctx.fillStyle = C.token('--accent');
    ctx.fillText(String(digit), canvas.width / 2, base);
  }

  const CHECK = '<svg viewBox="0 0 40 40"><path d="M9 21 l8 8 l15 -17" fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  /* artefato de cada nível (o que a pessoa vê na tela naquele estágio) */
  const ARTIFACT = {
    1: (s) => `<div class="win"><div class="bar"><i></i><i></i><i></i></div><div class="ui-mock">
        <div class="field"></div><div class="field short"></div><div class="field"></div>
        <span class="btn">${esc(s.labels.button)}</span>
        <svg viewBox="0 0 120 120" aria-hidden="true"><circle class="ring" cx="40" cy="40" r="22" opacity=".8"/><circle class="ring" cx="40" cy="40" r="38" opacity=".4"/>
        <path class="cursor" d="M40 40 L40 98 L56 84 L68 110 L80 104 L68 78 L90 78 Z"/></svg></div></div>`,
    2: (s) => `<div class="win"><div class="bar"><i></i><i></i><i></i><span>${esc(s.labels.file)}</span></div><pre class="code" data-code="code"></pre></div>`,
    3: (s) => `<div class="win"><div class="bar"><i></i><i></i><i></i><span>${esc(s.labels.file)}</span></div><pre class="code" data-code="code"></pre></div>`,
    4: (s) => `<div class="win"><div class="bar"><i></i><i></i><i></i><span>${esc(s.labels.file)}</span></div><pre class="code" data-code="code"></pre>
        <div class="dots" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div></div>`,
    5: (s) => `<div class="win"><div class="pipe">${s.labels.steps.map((t, i) =>
        `${i ? '<span class="link"></span>' : ''}<span class="node"><b style="color:var(--bg)">${CHECK}</b><span>${esc(t)}</span></span>`).join('')}</div></div>`,
  };

  function leader(slide, level) {
    const art = slide.querySelector('.artifact').getBoundingClientRect();
    const S = slide.getBoundingClientRect();
    const g = stepGeom(level - 1);
    const x1 = art.right - S.left - 30;
    const y1 = art.bottom - S.top;
    const x2 = g.cx;
    const y2 = g.cy + 90;
    slide.insertAdjacentHTML('beforeend', `<svg class="leader" viewBox="0 0 1080 1350" aria-hidden="true">
      <path d="M${x1} ${y1} C ${x1} ${y1 + 80}, ${x2} ${y2 - 140}, ${x2} ${y2 - 18}"/><circle cx="${x2}" cy="${y2 - 10}" r="9"/></svg>`);
  }

  C.onSlide('*', (slide, s) => {
    const svg = slide.querySelector('.stairs');
    if (s.layout === 'level') {
      const states = [0, 1, 2, 3, 4].map((k) => (k + 1 < s.level ? 'done' : k + 1 === s.level ? 'on' : 'off'));
      drawStairs(svg, states, 1);
      meter(slide, states);
      slide.querySelector('.tag').textContent = `${C.data.ui.level} ${s.level} ${C.data.ui.of}`;
      const art = slide.querySelector('.artifact');
      art.innerHTML = ARTIFACT[s.level](s);
      const code = art.querySelector('[data-code]');
      if (code && s.code) C.renderCode(code, s.code);
      numeral(slide.querySelector('.numeral'), s.level);
      leader(slide, s.level);
    } else if (s.layout === 'cta') {
      drawStairs(svg, ['on', 'on', 'on', 'on', 'on'], 1);
      const g = stepGeom(4);   // bandeira no topo da escada
      svg.insertAdjacentHTML('beforeend', `<g transform="translate(${g.cx} ${g.cy})">
        <path d="M0 0 V-170" stroke-width="8" stroke-linecap="round" style="stroke:var(--text)"/>
        <path d="M4 -168 L104 -140 L4 -112 Z" style="fill:var(--accent-2)"/></g>`);
    }
  });

  /* capa: degraus acendem de baixo para cima; quadro 0 em luz de espera (não fica tudo apagado) */
  const T0 = 0;      // o degrau 1 já nasce aceso: o quadro 0 é o pôster
  const DT = 0.6;
  C.animate(1, (t, slide) => {
    const svg = slide.querySelector('.stairs');
    const states = [0, 1, 2, 3, 4].map((k) => {
      const on = t >= T0 + k * DT;
      const next = t >= T0 + (k + 1) * DT;
      if (t >= T0 + 5 * DT + 0.2) return 'on';
      return next ? 'done' : on ? 'on' : 'off';
    });
    const lit = states.filter((x) => x !== 'off').length;
    drawStairs(svg, states, Math.min(1, 0.25 + lit * 0.15));
    meter(slide, states);
    slide.querySelectorAll('.meter i').forEach((el, k) => {
      const p = C.ease.out(C.prog(t, T0 + k * DT, 0.3));
      el.style.transform = `scaleX(${states[k] === 'off' ? 1 : 0.2 + 0.8 * p})`;
    });
  }, { duration: 5 });
})();
