'use strict';
/* pycode-aulas · efeitos e utilidades compartilhadas pelas cenas.
   window.FX: fundo animado, texto cinético, contagem, traço que se desenha, ciclo da demonstração, digitação e trilhas.
   window.K: utilidades de DOM, ícones de traço e o balão curto (tip) usado pelos itens clicáveis.
   Tudo que se move usa transform, opacity ou stroke de SVG. */
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const FX = { motion: true };

  /* ---------------- cores do estilo (tokens.css) ---------------- */
  const token = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  function rgb(color) {
    const probe = document.createElement('i');
    probe.style.color = color;
    document.body.append(probe);
    const m = getComputedStyle(probe).color.match(/[\d.]+/g) || [128, 128, 128];
    probe.remove();
    return m.slice(0, 3).map(Number);
  }
  FX.token = token;

  /* ---------------- fundo (canvas atrás do palco) ---------------- */
  // gerador pseudoaleatório com semente: o fundo é igual em toda abertura (capturas comparáveis)
  const seeded = seed => () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;
  const bg = { canvas: null, ctx: null, w: 0, h: 0, t: 0, mode: 'grade', color: [128, 128, 128], target: [128, 128, 128], ink: [128, 128, 128], energy: 0, energyTarget: 0, dots: [] };
  bg.resize = () => {
    if (!bg.canvas) return;
    const dpr = Math.min(1.25, window.devicePixelRatio || 1);
    bg.w = innerWidth; bg.h = innerHeight;
    bg.canvas.width = Math.round(bg.w * dpr); bg.canvas.height = Math.round(bg.h * dpr);
    bg.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  bg.init = canvas => {
    bg.canvas = canvas; bg.ctx = canvas.getContext('2d');
    bg.ink = rgb(token('--text') || '#888');
    bg.color = bg.target = rgb(token('--accent') || '#888');
    const rnd = seeded(7);
    for (let i = 0; i < 46; i++) bg.dots.push({ x: rnd(), y: rnd(), vx: (rnd() - .5) * .012, vy: (rnd() - .5) * .012 });
    bg.resize(); addEventListener('resize', bg.resize);
  };
  bg.setColor = css => { try { bg.target = rgb(css); } catch { /* cor inválida mantém a anterior */ } };
  bg.setMode = mode => { bg.mode = mode || 'grade'; };
  bg.kick = (k = 1) => { bg.energyTarget = k; setTimeout(() => { bg.energyTarget = 0; }, 480); };
  const col = (c, a) => `rgba(${c.map(Math.round).join(',')},${a})`;
  const MODES = {
    grade(ctx, w, h) {
      // grade de pontos com uma linha de varredura lenta
      const step = 46, sweep = (bg.t * 40) % (w + 400) - 200;
      for (let x = step / 2; x < w; x += step) for (let y = step / 2; y < h; y += step) {
        const near = Math.max(0, 1 - Math.abs(x - sweep) / 220);
        ctx.fillStyle = col(near > 0 ? bg.color : bg.ink, .07 + near * .22 + bg.energy * .1);
        ctx.fillRect(x, y, 1.6, 1.6);
      }
    },
    rede(ctx, w, h) {
      // pontos à deriva ligados quando estão perto
      const pts = bg.dots.map(d => {
        d.x = (d.x + d.vx * .016 * (1 + bg.energy * 8) + 1) % 1; d.y = (d.y + d.vy * .016 * (1 + bg.energy * 8) + 1) % 1;
        return [d.x * w, d.y * h];
      });
      ctx.lineWidth = 1;
      for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) {
        const dx = pts[i][0] - pts[j][0], dy = pts[i][1] - pts[j][1], d = Math.hypot(dx, dy);
        if (d < 190) { ctx.strokeStyle = col(bg.color, (1 - d / 190) * .16); ctx.beginPath(); ctx.moveTo(...pts[i]); ctx.lineTo(...pts[j]); ctx.stroke(); }
      }
      ctx.fillStyle = col(bg.color, .3);
      pts.forEach(p => ctx.fillRect(p[0] - 1.5, p[1] - 1.5, 3, 3));
    },
    ondas(ctx, w, h) {
      [[.86, 30, .14, 1], [.16, 14, .07, -1]].forEach(([yk, amp, a, dir]) => {
        ctx.strokeStyle = col(bg.color, a + bg.energy * .1); ctx.lineWidth = 1.4; ctx.beginPath();
        for (let x = 0; x <= w; x += 6) {
          const u = x / w * 20 + bg.t * 1.2 * dir;
          const y = h * yk + Math.sin(u * 2.1) * Math.cos(u * .7) * amp * (1 + bg.energy);
          x ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
        }
        ctx.stroke();
      });
    },
    orbita(ctx, w, h) {
      const cx = w * .78, cy = h * .52, base = Math.max(w, h) * .18;
      [[1, 90, .02], [1.5, 60, -.012], [2.1, 120, .006]].forEach(([k, ticks, sp], ri) => {
        const r = base * k, rot = bg.t * sp * (1 + bg.energy * 5);
        ctx.strokeStyle = col(bg.color, .06 + ri * .015); ctx.lineWidth = 1;
        ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.stroke();
        for (let i = 0; i < ticks; i++) {
          const ang = rot + i / ticks * Math.PI * 2, r2 = r - (i % 10 ? 5 : 14);
          ctx.strokeStyle = col(bg.color, i % 10 ? .07 : .18);
          ctx.beginPath(); ctx.moveTo(cx + Math.cos(ang) * r, cy + Math.sin(ang) * r); ctx.lineTo(cx + Math.cos(ang) * r2, cy + Math.sin(ang) * r2); ctx.stroke();
        }
      });
    },
    nenhum() {}
  };
  bg.frame = dt => {
    const { ctx, w, h } = bg;
    if (!ctx) return;
    bg.t += dt;
    bg.color = bg.color.map((c, i) => c + (bg.target[i] - c) * .05);
    bg.energy += (bg.energyTarget - bg.energy) * .12;
    ctx.clearRect(0, 0, w, h);
    (MODES[bg.mode] || MODES.grade)(ctx, w, h);
  };
  FX.bg = bg;

  /* ---------------- texto ---------------- */
  // quebra um título em palavras com máscara, para a entrada de baixo para cima
  FX.splitWords = el => {
    if (!el || el.dataset.split === 'done') return [...(el?.querySelectorAll('.w > span') || [])];
    const walk = node => [...node.childNodes].forEach(child => {
      if (child.nodeType === 3) {
        const frag = document.createDocumentFragment();
        child.textContent.split(/(\s+)/).forEach(part => {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.append(document.createTextNode(part)); return; }
          const w = document.createElement('span'); w.className = 'w';
          const inner = document.createElement('span'); inner.textContent = part;
          w.append(inner); frag.append(w);
        });
        child.replaceWith(frag);
      } else if (child.nodeType === 1 && !child.classList.contains('w')) walk(child);
    });
    walk(el);
    el.dataset.split = 'done';
    return [...el.querySelectorAll('.w > span')];
  };

  // contagem numérica: devolve um tween para a timeline
  FX.count = (el, to, { duration = 1.4, from = 0, format = v => Math.round(v).toLocaleString(document.documentElement.lang || 'pt-BR') } = {}) => {
    const state = { v: from };
    el.textContent = format(from);
    return gsap.to(state, { v: to, duration, ease: 'power3.out', onUpdate() { el.textContent = format(state.v); }, onComplete() { el.textContent = format(to); } });
  };

  // digitação: revela o texto caractere a caractere (o texto completo fica em aria-label)
  FX.type = (el, text, { cps = 38 } = {}) => {
    const state = { n: 0 };
    el.setAttribute('aria-label', text);
    return gsap.to(state, { n: text.length, duration: Math.max(.2, text.length / cps), ease: 'none', onStart() { el.textContent = ''; }, onUpdate() { el.textContent = text.slice(0, Math.round(state.n)); }, onComplete() { el.textContent = text; } });
  };

  // traço de SVG que se desenha (stroke-dashoffset)
  FX.draw = (paths, vars = {}) => {
    const list = [].concat(paths).filter(Boolean);
    list.forEach(p => { const len = p.getTotalLength ? p.getTotalLength() : 1000; p.style.strokeDasharray = `${len} ${len}`; p.dataset.len = len; });
    return gsap.fromTo(list, { strokeDashoffset: (i, p) => Number(p.dataset.len) }, { strokeDashoffset: 0, duration: 1.4, ease: 'power2.inOut', ...vars, onComplete() { list.forEach(p => { p.style.strokeDasharray = ''; }); vars.onComplete?.(); } });
  };

  /* demonstração em passos: chama onStep(i, true) a cada `every` segundos, UMA vez.
     home() volta ao passo inicial sem animação; still() aplica o passo didático do ?still.
     O tempo de espera fica na posição 0 (sem isso a duração soma depois do último passo). */
  FX.cycle = ({ n, every = 2.6, onStep, stillIndex = 0, homeIndex = 0, lead = 0 }) => {
    const loop = gsap.timeline({ paused: true });
    for (let i = 0; i < n; i++) loop.call(() => onStep(i, true), null, lead + i * every + .01);
    loop.to({}, { duration: lead + n * every }, 0);
    return { loop, home: () => onStep(homeIndex, false), still: () => onStep(stillIndex, false) };
  };

  /* trilhas: tabela de pontos de um path (evita getPointAtLength a cada quadro) */
  FX.table = (path, samples = 240) => {
    const len = path.getTotalLength(), pts = [];
    for (let i = 0; i <= samples; i++) { const p = path.getPointAtLength(len * i / samples); pts.push([p.x, p.y]); }
    return pts;
  };
  FX.at = (table, t) => {
    const u = Math.min(1, Math.max(0, t)) * (table.length - 1), i = Math.floor(u), f = u - i;
    const a = table[i], b = table[Math.min(table.length - 1, i + 1)];
    return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f];
  };

  /* ---------------- laço global: fundo e movimento ambiente da cena ativa ---------------- */
  let last = 0;
  FX.ambient = null;        // função (dt, t) da cena ativa, trocada pelo motor
  FX.start = () => {
    const loop = ts => {
      const dt = Math.min(.05, (ts - last) / 1000 || 0); last = ts;
      if (FX.motion && !document.hidden) {
        bg.frame(dt);
        try { FX.ambient?.(dt); } catch (err) { console.error('ambiente', err); FX.ambient = null; }
      }
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  };
  FX.paintStill = () => bg.frame(0);
  window.FX = FX;

  /* ---------------- utilidades das cenas ---------------- */
  const P = {
    app: '<rect x="6" y="2.5" width="12" height="19" rx="2.6"/><path d="M10.5 18.5h3"/>',
    site: '<rect x="2.5" y="4" width="19" height="15" rx="2"/><path d="M2.5 8h19M5.5 6h.01M8 6h.01"/>',
    server: '<rect x="3.5" y="3" width="17" height="7.5" rx="1.6"/><rect x="3.5" y="13.5" width="17" height="7.5" rx="1.6"/><path d="M7 6.75h.01M7 17.25h.01M11 6.75h6M11 17.25h6"/>',
    database: '<ellipse cx="12" cy="5.5" rx="7.5" ry="2.8"/><path d="M4.5 5.5v13c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8v-13M4.5 12c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8"/>',
    globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.8 3 2.8 15 0 18M12 3c-2.8 3-2.8 15 0 18"/>',
    gate: '<path d="M4 21V8l8-5 8 5v13"/><path d="M9 21v-7h6v7M4 11h16"/>',
    key: '<circle cx="8" cy="15" r="4.5"/><path d="M11.2 11.8L20 3M16.5 6.5l2.5 2.5M14 9l2 2"/>',
    lock: '<rect x="4.5" y="10.5" width="15" height="10.5" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3M12 14.5v2.5"/>',
    shield: '<path d="M12 2.5l8 3v6.2c0 4.6-3.3 8-8 9.8-4.7-1.8-8-5.2-8-9.8V5.5z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    code: '<path d="M8.5 7L3.5 12l5 5M15.5 7l5 5-5 5M13.5 4.5l-3 15"/>',
    terminal: '<rect x="2.5" y="4" width="19" height="16" rx="2"/><path d="M7 10l3 2.5L7 15M12.5 15h4.5"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    card: '<rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="M2.5 9.5h19M6 15h4"/>',
    pin: '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    cloud: '<path d="M7 18.5a4.5 4.5 0 0 1-.6-9A6 6 0 0 1 18 8.6a4.2 4.2 0 0 1-.5 9.9z"/>',
    mail: '<rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="M3 6l9 7 9-7"/>',
    chart: '<path d="M3.5 20.5h17M6.5 17v-5M11 17V7M15.5 17v-8M20 17V4"/>',
    book: '<path d="M4 4.5h6a2 2 0 0 1 2 2V20a2 2 0 0 0-2-2H4zM20 4.5h-6a2 2 0 0 0-2 2V20a2 2 0 0 1 2-2h6z"/>',
    bolt: '<path d="M13 2.5L4.5 13.5H11L10 21.5l8.5-11H12z"/>',
    check: '<path d="M4.5 12.5l5 5 10-11"/>',
    cross: '<path d="M6 6l12 12M18 6L6 18"/>',
    gear: '<circle cx="12" cy="12" r="3.2"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/>',
    box: '<path d="M3 7l9-4 9 4v10l-9 4-9-4z"/><path d="M3 7l9 4 9-4M12 11v10"/>',
    chat: '<path d="M4 4.5h16v11.5H10l-6 4.5z"/>',
    layers: '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 12.5l9 5 9-5M3 17l9 5 9-5"/>',
    route: '<circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="6" r="2.5"/><path d="M8.5 18H15a3 3 0 0 0 0-6H9a3 3 0 0 1 0-6h6.5"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8"/>',
    play: '<circle cx="12" cy="12" r="9"/><path d="M10 8.5l5.5 3.5-5.5 3.5z"/>',
    quote: '<path d="M10 7H5.5v5.5H9c0 2.5-1.2 4-3.5 4.5M19 7h-4.5v5.5H18c0 2.5-1.2 4-3.5 4.5"/>',
    flag: '<path d="M5 21V3.5M5 4h12l-2.5 4L17 12H5"/>',
    spark: '<path d="M12 3v5M12 16v5M3 12h5M16 12h5M6 6l3 3M15 15l3 3M6 18l3-3M15 9l3-3"/>'
  };
  const K = {
    esc: s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])),
    q: (root, sel) => root.querySelector(sel),
    qa: (root, sel) => [...root.querySelectorAll(sel)],
    svg(tag, attrs = {}, parent = null) {
      const el = document.createElementNS(NS, tag);
      for (const k in attrs) el.setAttribute(k, attrs[k]);
      if (parent) parent.append(el);
      return el;
    },
    // ícone de traço (SVG inline) pelo nome; nomes desconhecidos viram um ponto
    icon: (name, cls = 'ic') => `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true">${P[name] || '<circle cx="12" cy="12" r="3"/>'}</svg>`,
    iconPaths: name => P[name] || '<circle cx="12" cy="12" r="3"/>',
    icons: Object.keys(P),
    only: (els, i, cls = 'on') => els.forEach((el, j) => el.classList.toggle(cls, j === i)),
    // posição de um elemento dentro de `root` pelo layout (ignora transformações em andamento)
    pos(el, root) {
      let x = 0, y = 0, node = el;
      while (node && node !== root) { x += node.offsetLeft; y += node.offsetTop; node = node.offsetParent; }
      return { x, y, w: el.offsetWidth, h: el.offsetHeight };
    },
    // cor de um tom do conteúdo (ok, warn, danger, accent, accent-2, muted)
    tone: t => `var(--${({ 'accent-2': 'accent-2', ok: 'ok', warn: 'warn', danger: 'danger', muted: 'muted' }[t]) || 'accent'})`,
    fmt: (v, d = 0) => Number(v).toLocaleString(document.documentElement.lang || 'pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d }),

    /* balão curto perto do item. Coordenadas em px dentro de `host` (sem escala).
       side: 't' acima, 'b' abaixo, 'l' à esquerda, 'r' à direita. box limita a área [x0, y0, x1, y1]. */
    tip(host, ctx, box) {
      const el = document.createElement('div');
      el.className = 'tip';
      el.setAttribute('aria-live', 'polite');
      el.innerHTML = '<div class="tip-in"><b></b><p></p></div>';
      host.append(el);
      const inner = el.firstElementChild, lb = inner.children[0], tx = inner.children[1];
      let last = null;
      const place = (x, y, side, label, text, anim) => {
        last = [x, y, side, label, text];
        lb.textContent = label || ''; lb.hidden = !label;
        tx.textContent = text || ''; tx.hidden = !text;
        const b = box || [0, 0, host.offsetWidth, host.offsetHeight];
        const w = el.offsetWidth, h = el.offsetHeight, g = 22;
        let l = side === 'r' ? x + g : side === 'l' ? x - g - w : x - w / 2;
        let t = side === 't' ? y - g - h : side === 'b' ? y + g : y - h / 2;
        l = Math.max(b[0], Math.min(b[2] - w, l)); t = Math.max(b[1], Math.min(b[3] - h, t));
        el.style.left = Math.round(l) + 'px'; el.style.top = Math.round(t) + 'px';
        el.classList.add('on');
        gsap.killTweensOf(inner);
        if (anim && ctx.motion()) gsap.fromTo(inner, { scale: .92, y: side === 't' ? 8 : -8 }, { scale: 1, y: 0, duration: .4, ease: 'back.out(2)', clearProps: 'transform' });
      };
      return {
        el,
        show: (x, y, side, label, text, anim = true) => place(x, y, side, label, text, anim),
        hide: () => { last = null; el.classList.remove('on'); },
        refresh: () => { if (last) place(...last, false); }
      };
    }
  };
  window.K = K;
  window.SCENES = window.SCENES || {};
})();
