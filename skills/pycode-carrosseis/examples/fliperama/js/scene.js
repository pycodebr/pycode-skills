/*
 * Fliperama: motor de pixel art mínimo (canvas 180x225 ampliado 6x) com céu, estrelas, prédios, chão de
 * tijolos, cobras, moedas, troféu e o gabinete da capa. As cores vêm dos tokens do estilo.
 */
(() => {
  const C = window.Carousel;
  const LW = 180;
  const LH = 225;

  /* cor de um token como [r, g, b] (lida do navegador, aceita qualquer formato CSS) */
  const probe = document.createElement('i');
  function rgb(token) {
    probe.style.color = `var(${token})`;
    document.body.appendChild(probe);
    const m = getComputedStyle(probe).color.match(/[\d.]+/g).map(Number);
    probe.remove();
    return m.slice(0, 3);
  }
  const mix = (a, b, t) => a.map((v, i) => Math.round(v + (b[i] - v) * t));
  const css = (c) => `rgb(${c[0]},${c[1]},${c[2]})`;

  let P = null;
  function palette() {
    if (P) return P;
    const T = (n) => rgb(`--${n}`);
    const black = [0, 0, 0];
    P = {
      bg: T('bg'), bg2: T('bg-2'), sur: T('surface'), sur2: T('surface-2'), txt: T('text'), line: T('line'),
      acc: T('accent'), acc2: T('accent-2'), ok: T('ok'), dan: T('danger'), warn: T('warn'), mut: T('muted'), black,
    };
    P.accD = mix(P.acc, black, 0.35);
    P.acc2D = mix(P.acc2, black, 0.35);
    P.night = mix(P.bg, black, 0.25);
    return P;
  }

  function sprite(ctx, rows, x, y, map) {
    rows.forEach((row, j) => [...row].forEach((ch, i) => {
      if (ch === '.' || !map[ch]) return;
      ctx.fillStyle = css(map[ch]);
      ctx.fillRect(x + i, y + j, 1, 1);
    }));
  }

  const SNAKE = [
    '....AAAAA.......', '...AAAAAAA......', '...AAEAAAAR.....', '...AAAAAAA.RR...', '....AAAAA.......',
    '......DAA.......', '..AAAAAAD.......', '.AAAAAAD........', '.AAD............', '.AAAAAAAAAA.....',
    '..DDDDDDAAAA....', '..........AAA...', '..AAAAAAAAAAD...', '.AAAAAAAAAAD....',
  ];
  const HEART = ['.XX.XX.', 'XXXXXXX', 'XXXXXXX', '.XXXXX.', '..XXX..', '...X...'];
  const COIN = ['...YYYY...', '..YWYYYY..', '.YWYYDYYY.', 'YWYYYDYYYY', 'YYYYYDYYYY', 'YYYYYDYYYY', 'YYYYYDYYYY',
    '.YYYYDYYY.', '..YYYYYY..', '...YYYY...'];
  const TROPHY = ['YYYYYYYYYYYY', 'Y.YWYYYYYY.Y', 'Y.YWYYYYYY.Y', '.YYWYYYYYYY.', '..YYYYYYYY..', '...YYYYYY...',
    '.....YY.....', '.....YY.....', '....DDDD....', '...DDDDDD...', '...DDDDDD...'];
  const BLOCK = ['YYYYYYYYYY', 'Y.YYYYYY.Y', 'YYYDDDDYYY', 'YYDYYYYDYY', 'YYYYYYDYYY', 'YYYYYDYYYY', 'YYYYYYYYYY',
    'YYYYYDYYYY', 'Y.YYYYYY.Y', 'YYYYYYYYYY'];

  function sky(ctx, t = 0, seed = 3) {
    const p = palette();
    for (let y = 0; y < LH; y++) {           // degradê em faixas com pontilhado nas transições
      const k = Math.min(1, y / 170);
      const band = Math.floor(k * 6) / 6;
      const next = Math.min(1, band + 1 / 6);
      const f = (k - band) * 6;
      for (let x = 0; x < LW; x++) {
        const dither = ((x + y) % 2 === 0 ? 0.25 : 0.75) < f ? next : band;
        ctx.fillStyle = css(mix(p.bg2, p.night, dither));
        ctx.fillRect(x, y, 1, 1);
      }
    }
    const r = C.rng(seed);
    for (let i = 0; i < 60; i++) {
      const x = Math.floor(r() * LW);
      const y = Math.floor(r() * 150);
      const tw = Math.sin(t * 6 + i) > 0.6;
      ctx.fillStyle = css(i % 7 === 0 ? p.acc : mix(p.txt, p.bg, 0.3 + r() * 0.4));
      ctx.fillRect(x, y, 1, 1);
      if (tw && i % 5 === 0) { ctx.fillRect(x - 1, y, 3, 1); ctx.fillRect(x, y - 1, 1, 3); }
    }
  }

  function skyline(ctx, y0 = 178, seed = 9) {
    const p = palette();
    const r = C.rng(seed);
    let x = 0;
    while (x < LW) {
      const w = 10 + Math.floor(r() * 14);
      const h = 12 + Math.floor(r() * 26);
      ctx.fillStyle = css(mix(p.night, p.sur, 0.18));
      ctx.fillRect(x, y0 - h, w - 1, h);
      for (let wy = y0 - h + 3; wy < y0 - 2; wy += 4) {
        for (let wx = x + 2; wx < x + w - 3; wx += 3) {
          if (r() > 0.62) { ctx.fillStyle = css(mix(p.acc, p.night, 0.25)); ctx.fillRect(wx, wy, 1, 1); }
        }
      }
      x += w;
    }
  }

  function ground(ctx, y0 = 192) {
    const p = palette();
    ctx.fillStyle = css(p.ok); ctx.fillRect(0, y0, LW, 2);
    ctx.fillStyle = css(mix(p.ok, p.black, 0.4)); ctx.fillRect(0, y0 + 2, LW, 1);
    for (let y = y0 + 3; y < LH; y++) {
      for (let x = 0; x < LW; x++) {
        const row = Math.floor((y - y0 - 3) / 5);
        const mortar = (y - y0 - 3) % 5 === 4 || (x + (row % 2) * 6) % 12 === 0;
        ctx.fillStyle = css(mortar ? mix(p.sur, p.black, 0.55) : mix(p.sur, p.black, 0.2));
        ctx.fillRect(x, y, 1, 1);
      }
    }
  }

  const snake = (ctx, x, y, main) => {
    const p = palette();
    const dark = mix(main, p.black, 0.35);
    sprite(ctx, SNAKE, x, y, { A: main, D: dark, E: p.bg, R: p.dan });
  };
  const coin = (ctx, x, y) => { const p = palette(); sprite(ctx, COIN, x, y, { Y: p.acc, W: p.txt, D: p.accD }); };
  const block = (ctx, x, y) => { const p = palette(); sprite(ctx, BLOCK, x, y, { Y: p.acc, D: p.accD }); };

  /* gabinete da capa (coordenadas lógicas; a tela bate com .screen do CSS) */
  function cabinet(ctx, t) {
    const p = palette();
    const body = mix(p.sur, p.black, 0.25);
    const side = mix(p.sur, p.black, 0.55);
    ctx.fillStyle = css(side); ctx.fillRect(26, 16, 128, 209);
    ctx.fillStyle = css(body); ctx.fillRect(30, 18, 120, 207);
    ctx.fillStyle = css(p.acc); ctx.fillRect(30, 20, 120, 24);                    // letreiro
    ctx.fillStyle = css(mix(p.acc, p.txt, 0.45)); ctx.fillRect(30, 20, 120, 2);
    ctx.fillStyle = css(p.black); ctx.fillRect(40, 50, 100, 72);                   // moldura da tela
    ctx.fillStyle = css(mix(p.bg2, p.black, 0.2)); ctx.fillRect(44, 53, 92, 66);   // tela
    ctx.fillStyle = css(side); ctx.fillRect(30, 124, 120, 4);
    ctx.fillStyle = css(mix(p.sur2, p.black, 0.15)); ctx.fillRect(28, 128, 124, 22); // painel
    const tilt = Math.round(Math.sin(t * 5) * 1.5);
    ctx.fillStyle = css(p.black); ctx.fillRect(55, 136, 4, 8);                      // alavanca
    ctx.fillStyle = css(p.dan); ctx.fillRect(53 + tilt, 132, 8, 6);
    [[90, p.acc], [104, p.acc2], [118, p.dan], [132, p.ok]].forEach(([bx, c], i) => {
      const press = t > 2.5 && t < 2.8 && i === 0;
      ctx.fillStyle = css(mix(c, p.black, 0.4)); ctx.fillRect(bx, 138, 9, 5);
      ctx.fillStyle = css(c); ctx.fillRect(bx, press ? 137 : 135, 9, 4);
    });
    ctx.fillStyle = css(side); ctx.fillRect(30, 152, 120, 3);
    const glow = 0.35 + 0.65 * C.ease.out(C.prog(t, 2.2, 0.4));                    // porta da moeda
    ctx.fillStyle = css(mix(p.black, p.acc, 0.25 * glow)); ctx.fillRect(74, 166, 32, 32);
    ctx.fillStyle = css(mix(p.acc, p.black, 1 - glow)); ctx.fillRect(84, 172, 12, 3);
    ctx.fillStyle = css(mix(p.dan, p.black, 1 - glow)); ctx.fillRect(84, 184, 12, 8);
    for (let k = 0; k < 6; k++) { ctx.fillStyle = css(side); ctx.fillRect(34 + k * 20, 206, 12, 2); }
    if (t > 1.5 && t < 2.25) {                                                     // moeda caindo
      const q = C.ease.inOut(C.prog(t, 1.5, 0.7));
      coin(ctx, Math.round(150 - 61 * q), Math.round(150 + 18 * q));
    }
  }

  function drawScene(slide, s, t) {
    const cv = slide.querySelector('.pix');
    const ctx = cv.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    const p = palette();
    sky(ctx, t, 3 + (s.phase || 0));
    if (s.layout === 'cover') {
      skyline(ctx, 200);
      ground(ctx, 210);
      cabinet(ctx, t);
      snake(ctx, 4, 196, p.acc);
      snake(ctx, 160, 196, p.acc2);
      return;
    }
    skyline(ctx, 190, 9 + (s.phase || 4));
    ground(ctx, 192);
    if (s.layout === 'phase') {
      snake(ctx, 16, 178, p.acc);
      snake(ctx, 148, 178, p.acc2);
      [60, 72, 84, 96, 108].forEach((x, i) => (i === s.phase ? coin(ctx, x + 1, 168) : block(ctx, x, 168)));
    } else if (s.layout === 'score') {
      sprite(ctx, TROPHY, 84, 169, { Y: p.acc, W: p.txt, D: p.accD });
      snake(ctx, 52, 178, p.acc);
      snake(ctx, 112, 178, p.acc2);
      [[22, 158], [156, 150], [128, 166]].forEach(([fx, fy], k) => {     // fogos
        const c = [p.acc, p.acc2, p.dan][k];
        for (let a = 0; a < 8; a++) {
          const dx = Math.round(Math.cos((a * Math.PI) / 4) * 7);
          const dy = Math.round(Math.sin((a * Math.PI) / 4) * 7);
          ctx.fillStyle = css(c); ctx.fillRect(fx + dx, fy + dy, 2, 2);
        }
        ctx.fillRect(fx, fy, 2, 2);
      });
      for (let k = 0; k < 9; k++) coin(ctx, 6 + k * 19, 205);
    } else if (s.layout === 'continue') {
      const big = document.createElement('canvas');
      big.width = 10; big.height = 10;
      const bctx = big.getContext('2d');
      sprite(bctx, COIN, 0, 0, { Y: p.acc, W: p.txt, D: p.accD });
      ctx.drawImage(big, 72, 118, 36, 36);
      snake(ctx, 20, 178, p.acc);
      snake(ctx, 144, 178, p.acc2);
    }
  }

  function hearts(el, full) {
    const p = palette();
    el.innerHTML = '';
    for (let i = 0; i < 3; i++) {
      const c = document.createElement('canvas');
      c.width = 7; c.height = 6;
      const ctx = c.getContext('2d');
      sprite(ctx, HEART, 0, 0, { X: i < full ? p.dan : mix(p.bg, p.txt, 0.25) });
      el.appendChild(c);
    }
  }

  C.onSlide('*', (slide, s) => {
    const ui = C.data.ui;
    drawScene(slide, s, 0);
    if (s.layout === 'phase') {
      slide.querySelector('.phase').textContent = `${ui.phase} ${s.phase}`;
      hearts(slide.querySelector('.hearts'), 4 - s.phase);
    } else if (s.layout === 'score') {
      slide.querySelector('.banner').textContent = ui.score;
      slide.querySelector('.board').innerHTML = s.labels.rows.map(([ph, letter, out]) =>
        `<div class="row"><span class="ph">${ui.phase} ${ph}</span><b>${letter}</b><code>${out}</code></div>`).join('');
    } else if (s.layout === 'continue') {
      slide.querySelector('.banner').textContent = ui.continue;
      slide.querySelector('.coin-label').textContent = ui.coin;
    } else if (s.layout === 'cover') {
      slide.querySelector('.start').textContent = ui.start;
    }
  });

  /* capa: PRESS START pisca, a moeda cai no moedeiro, a porta acende e a tela pisca */
  C.animate(1, (t, slide, s) => {
    drawScene(slide, s, t);
    const fast = t > 2.6;
    const on = Math.floor(t / (fast ? 0.15 : 0.5)) % 2 === 0;
    slide.querySelector('.start').style.opacity = on ? '1' : '0';
    const f = C.prog(t, 2.6, 0.45);
    slide.querySelector('.flash').style.opacity = (f > 0 && f < 1 ? 0.55 * Math.sin(Math.PI * f) : 0).toFixed(3);
  }, { duration: 5 });
})();
