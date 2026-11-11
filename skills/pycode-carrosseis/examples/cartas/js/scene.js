/*
 * Cartas colecionáveis: arte de cada carta, verso, leque da capa (vídeo) e ligações do slide "como usar".
 * Tudo desenhado em SVG/HTML com as cores do estilo; nenhum asset externo.
 */
(() => {
  const C = window.Carousel;
  const NS = 'http://www.w3.org/2000/svg';

  /* ---------------------------------------------------------------- arte de cada carta (viewBox 800x330) */
  const ART = {
    pathlib() {
      // árvore de pastas; o caminho até api.md acende e a extensão se separa do nome
      const folder = (x, y, cls) => `<path d="M${x - 34} ${y - 22} h24 l8 8 h36 v40 h-68 z" class="${cls}"/>`;
      const file = (x, y, cls) => `<path d="M${x - 24} ${y - 30} h34 l14 14 v46 h-48 z" class="${cls}"/>`;
      const label = (x, y, txt, cls = 'f-txt') => `<text x="${x}" y="${y}" font-size="28" class="${cls}">${txt}</text>`;
      return `
        <g fill="none" stroke-width="5" stroke-linecap="round">
          <path d="M70 175 C 120 175, 130 115, 186 115" class="s-acc"/>
          <path d="M70 175 C 120 175, 130 255, 186 255" class="s-mut" opacity=".5"/>
          <path d="M358 110 C 390 110, 396 66, 432 66" class="s-acc"/>
          <path d="M358 120 C 390 120, 396 160, 432 160" class="s-mut" opacity=".5"/>
        </g>
        <circle cx="64" cy="175" r="16" class="f-acc"/>
        ${folder(220, 112, 'f-acc2')}${label(262, 124, 'aulas')}
        ${folder(220, 252, 'f-mut')}${label(262, 264, 'dados', 'f-mut')}
        ${file(462, 70, 'f-acc')}${label(500, 80, 'api.md')}
        ${file(462, 164, 'f-mut')}${label(500, 174, 'intro.md', 'f-mut')}
        <path d="M600 92 C 640 130, 650 180, 640 222" fill="none" stroke-width="4" stroke-dasharray="3 10" stroke-linecap="round" class="s-acc"/>
        <g transform="translate(470 240)">
          <rect x="0" y="0" width="128" height="78" rx="14" class="f-sur2"/>
          <text x="64" y="51" text-anchor="middle" font-size="36" class="f-txt">api</text>
          <rect x="142" y="-8" width="140" height="94" rx="16" class="f-acc"/>
          <text x="212" y="54" text-anchor="middle" font-size="44" font-weight="700" class="f-bg">.md</text>
        </g>`;
    },
    counter() {
      // "banana" vira barras: a=3, n=2, b=1; as duas mais frequentes acendem
      const letters = [...'banana'];
      const color = { b: 'f-mut', a: 'f-acc', n: 'f-acc2' };
      let s = letters.map((ch, i) => `<text x="${60 + i * 48}" y="96" font-size="58" font-weight="700" class="${color[ch]}">${ch}</text>`).join('');
      const bars = [['a', 3, 'f-acc'], ['n', 2, 'f-acc2'], ['b', 1, 'f-mut']];
      bars.forEach(([ch, v, cls], i) => {
        const x = 440 + i * 110;
        const h = v * 68;
        const y = 290 - h;
        s += `<path d="M${x} ${y} l26 -16 h70 l-26 16 z" class="${cls}" opacity=".75"/>
              <path d="M${x + 70} ${y} l26 -16 v${h} l-26 16 z" class="${cls}" opacity=".5"/>
              <rect x="${x}" y="${y}" width="70" height="${h}" class="${cls}"/>
              <text x="${x + 35}" y="${y - 28}" text-anchor="middle" font-size="34" font-weight="700" class="f-txt">${v}</text>
              <text x="${x + 35}" y="322" text-anchor="middle" font-size="26" class="f-mut">${ch}</text>`;
      });
      s += `<g fill="none" stroke-width="4" stroke-dasharray="3 10" stroke-linecap="round">
              <path d="M112 116 C 150 170, 330 160, 430 150" class="s-acc"/>
              <path d="M210 116 C 260 200, 420 200, 545 205" class="s-acc2"/></g>
            <text x="60" y="292" font-size="28" class="f-mut">most_common(2)</text>`;
      return s;
    },
    datetime() {
      // fevereiro de 2028 tem 29 dias: o 29 aparece circulado
      let s = `<rect x="40" y="26" width="470" height="290" rx="18" class="f-sur"/>
               <rect x="40" y="26" width="470" height="56" rx="18" class="f-acc2"/>
               <rect x="40" y="62" width="470" height="20" class="f-acc2"/>
               <text x="64" y="66" font-size="30" font-weight="700" class="f-bg">fev 2028</text>`;
      const first = 2; // 1/2/2028 cai numa terça (0 = domingo)
      for (let d = 1; d <= 29; d++) {
        const k = d - 1 + first;
        const x = 70 + (k % 7) * 64;
        const y = 122 + Math.floor(k / 7) * 40;
        const on = d === 29;
        if (on) s += `<circle cx="${x + 12}" cy="${y - 9}" r="25" class="f-acc"/>`;
        s += `<text x="${x + 12}" y="${y}" text-anchor="middle" font-size="24" class="${on ? 'f-bg' : 'f-txt'}" ${on ? 'font-weight="700"' : ''}>${d}</text>`;
      }
      s += `<g transform="translate(560 70) rotate(6)">
              <rect width="200" height="200" rx="18" class="f-sur2"/>
              <rect width="200" height="50" rx="18" class="f-dan"/><rect y="30" width="200" height="20" class="f-dan"/>
              <text x="20" y="38" font-size="28" font-weight="700" class="f-bg">mar</text>
              <text x="100" y="160" text-anchor="middle" font-size="96" font-weight="700" class="f-txt">1</text></g>
            <path d="M470 300 C 560 330, 640 310, 670 280" fill="none" stroke-width="4" stroke-dasharray="3 10" stroke-linecap="round" class="s-acc"/>`;
      return s;
    },
    json() {
      // texto em cima, dicionário embaixo; o true vira True
      return `
        <rect x="40" y="34" width="720" height="78" rx="39" class="f-sur2"/>
        <text x="80" y="86" font-size="34" class="f-txt">{"nota": 9.5, "ok": <tspan class="f-acc" font-weight="700">true</tspan>}</text>
        <path d="M400 128 v44" stroke-width="6" stroke-linecap="round" class="s-acc"/>
        <path d="M382 160 l18 22 l18 -22" fill="none" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" class="s-acc"/>
        <text x="430" y="166" font-size="26" class="f-mut">json.loads</text>
        <g transform="translate(150 206)">
          <rect width="230" height="96" rx="16" class="f-sur"/><rect width="110" height="96" rx="16" class="f-acc2"/>
          <text x="55" y="60" text-anchor="middle" font-size="30" font-weight="700" class="f-bg">nota</text>
          <text x="170" y="60" text-anchor="middle" font-size="34" class="f-txt">9.5</text>
          <rect x="270" width="230" height="96" rx="16" class="f-sur"/><rect x="270" width="90" height="96" rx="16" class="f-acc2"/>
          <text x="315" y="60" text-anchor="middle" font-size="30" font-weight="700" class="f-bg">ok</text>
          <text x="430" y="60" text-anchor="middle" font-size="34" font-weight="700" class="f-acc">True</text>
        </g>
        <text x="80" y="268" font-size="70" class="f-mut" opacity=".55">{</text>
        <text x="680" y="268" font-size="70" class="f-mut" opacity=".55">}</text>`;
    },
    statistics() {
      // reta de 0 a 45: 7, 8 e 9 juntos, o 40 fora da curva; mediana 8,5 e média 16
      const X = (v) => 60 + v * 15.5;
      let s = `<path d="M${X(0)} 250 H${X(45)}" stroke-width="4" class="s-mut"/>`;
      for (let v = 0; v <= 45; v += 5) {
        s += `<path d="M${X(v)} 242 v16" stroke-width="3" class="s-mut"/><text x="${X(v)}" y="292" text-anchor="middle" font-size="24" class="f-mut">${v}</text>`;
      }
      s += `<path d="M${X(8.5)} 70 V250" stroke-width="5" class="s-acc2"/><text x="${X(8.5) + 12}" y="78" font-size="28" class="f-acc2">mediana 8.5</text>
            <path d="M${X(16)} 130 V250" stroke-width="5" stroke-dasharray="10 8" class="s-acc"/><text x="${X(16) + 12}" y="138" font-size="28" class="f-acc">média 16</text>`;
      [7, 8, 9].forEach((v) => { s += `<circle cx="${X(v)}" cy="226" r="7.5" class="f-txt"/>`; });
      s += `<circle cx="${X(40)}" cy="226" r="18" class="f-dan"/><circle cx="${X(40)}" cy="226" r="30" fill="none" stroke-width="3" class="s-dan"/>
            <text x="${X(40)}" y="182" text-anchor="middle" font-size="26" class="f-dan">fora da curva</text>`;
      return s;
    },
  };

  /* ---------------------------------------------------------------- verso: roseta guilhochê + monograma */
  function backSVG(seed) {
    let s = '<svg viewBox="0 0 300 420" aria-hidden="true"><rect width="300" height="420" class="f-sur"/>';
    for (let k = 0; k < 18; k++) {
      let d = '';
      for (let i = 0; i <= 360; i += 3) {
        const a = (i * Math.PI) / 180;
        const r = 92 + 34 * Math.sin(7 * a + k * 0.35) + k * 2.2;
        d += `${i ? 'L' : 'M'}${(150 + r * Math.cos(a)).toFixed(1)} ${(210 + r * Math.sin(a) * 1.25).toFixed(1)}`;
      }
      s += `<path d="${d}Z" fill="none" stroke-width="1.2" class="${k % 3 ? 's-acc' : 's-acc2'}" opacity=".55"/>`;
    }
    const brand = (C.data.brand && C.data.brand.name) || '';
    const mono = brand.split(/\s+/).filter(Boolean).map((w) => w[0]).join('').slice(0, 2).toUpperCase();
    s += `<circle cx="150" cy="210" r="58" class="f-bg"/><circle cx="150" cy="210" r="58" fill="none" stroke-width="5" class="s-acc"/>
          <text x="150" y="228" text-anchor="middle" font-size="50" font-weight="800" class="f-acc" style="font-family:var(--font-display)">${mono}</text>
          <rect x="14" y="14" width="272" height="392" rx="14" fill="none" stroke-width="3" class="s-acc" opacity=".7"/></svg>`;
    return s.replace('seed', seed);
  }

  function gem(svg, gold) {
    svg.innerHTML = gold
      ? '<path d="M12 1.5l3.1 6.6 7.2.9-5.3 5 1.4 7.1L12 17.6l-6.4 3.5 1.4-7.1-5.3-5 7.2-.9z" class="f-acc"/>'
      : '<path d="M12 2l8 10-8 10-8-10z" class="f-acc2"/><path d="M12 2l3 10-3 10-3-10z" class="f-txt" opacity=".3"/>';
  }

  /* emblema simples de cada carta pequena (viewBox 260x300): lê de longe, ao contrário da arte completa */
  const EMBLEM = {
    pathlib: () => `<path d="M40 92 h70 l18 20 h92 v120 h-180 z" class="f-acc2"/>
      <path d="M118 60 h66 l28 28 v104 h-94 z" class="f-acc"/><path d="M184 60 v28 h28" class="f-bg" opacity=".35"/>
      <rect x="60" y="240" width="140" height="36" rx="10" class="f-sur2"/><text x="130" y="267" text-anchor="middle" font-size="26" class="f-acc">.md</text>`,
    counter: () => [[50, 3, 'f-acc'], [115, 2, 'f-acc2'], [180, 1, 'f-mut']].map(([x, v, c]) =>
      `<rect x="${x}" y="${250 - v * 62}" width="46" height="${v * 62}" rx="6" class="${c}"/>
       <text x="${x + 23}" y="${236 - v * 62}" text-anchor="middle" font-size="30" font-weight="700" class="f-txt">${v}</text>`).join('') +
      '<path d="M30 252 H230" stroke-width="4" class="s-mut"/>',
    datetime: () => `<rect x="40" y="50" width="180" height="200" rx="16" class="f-sur"/>
      <rect x="40" y="50" width="180" height="52" rx="16" class="f-acc2"/><rect x="40" y="84" width="180" height="18" class="f-acc2"/>
      <circle cx="130" cy="176" r="52" class="f-acc"/><text x="130" y="200" text-anchor="middle" font-size="68" font-weight="800" class="f-bg">29</text>`,
    json: () => `<text x="20" y="200" font-size="150" class="f-acc2">{</text><text x="172" y="200" font-size="150" class="f-acc2">}</text>
      <rect x="92" y="98" width="76" height="30" rx="8" class="f-acc"/><rect x="92" y="140" width="76" height="30" rx="8" class="f-txt"/>
      <rect x="92" y="182" width="52" height="30" rx="8" class="f-acc"/>`,
    statistics: () => `<path d="M24 240 C 80 240, 92 70, 130 70 S 180 240, 236 240" fill="none" stroke-width="8" class="s-acc2"/>
      <path d="M130 60 V250" stroke-width="5" stroke-dasharray="8 7" class="s-acc"/>
      <circle cx="214" cy="226" r="13" class="f-dan"/><path d="M20 252 H240" stroke-width="4" class="s-mut"/>`,
  };

  /* maior tamanho de fonte em que o nome cabe na largura (mede com a fonte do título) */
  function fitName(name, maxW, start) {
    const ctx = document.createElement('canvas').getContext('2d');
    const fam = C.token('--font-display');
    const wt = C.token('--weight-display') || '700';
    let fs = start;
    for (; fs > 14; fs -= 1) {
      ctx.font = `${wt} ${fs}px ${fam}`;
      if (ctx.measureText(name).width <= maxW) break;
    }
    return fs;
  }

  /* carta pequena com frente e verso, para o leque */
  function mini(card, w, h, align = 'center') {
    const el = document.createElement('div');
    el.className = 'mini';
    el.style.width = `${w}px`;
    el.style.height = `${h}px`;
    el.innerHTML = `<div class="face back">${backSVG()}</div>
      <div class="face front${card.gold ? ' gold' : ''}"><div class="mini-in">
        <div class="mini-name" style="text-align:${align};font-size:${fitName(card.name, w - 44, Math.round(w * 0.13))}px">${card.name}</div>
        <div class="mini-art"><svg viewBox="0 0 260 300">${EMBLEM[card.art]()}</svg></div></div></div>`;
    return el;
  }

  const cards = () => C.data.slides.filter((s) => s.card).map((s) => s.card);

  /* textura de código ao fundo (decorativa, quase invisível) */
  const SNIPPET = ['from pathlib import Path', 'import json', 'from collections import Counter',
    'dados = json.loads(Path("notas.json").read_text())', 'contagem = Counter(dados["status"])',
    'for nome, total in contagem.most_common(3):', '    print(nome, total)', 'from statistics import median',
    'print(median(dados["notas"]))', 'from datetime import date', 'prazo = date.today()', ''];

  C.onSlide('*', (slide) => {
    const tex = slide.querySelector('.texture');
    if (tex) tex.textContent = Array(6).fill(SNIPPET.join('\n')).join('\n');
  });

  /* ---------------------------------------------------------------- cartas grandes */
  C.onSlide('*', (slide, s) => {
    if (!s.card) return;
    const card = slide.querySelector('.card');
    card.classList.toggle('gold', !!s.card.gold);
    slide.querySelector('.art-svg').innerHTML = ART[s.card.art]();
    gem(slide.querySelector('.gem'), s.card.gold);
  });

  /* ---------------------------------------------------------------- capa: baralho abre e vira (vídeo) */
  /* leque de mão: todas as cartas giram em torno do mesmo pivô, abaixo do slide */
  const FAN = { px: 540, py: 1470, R: 580, w: 280, h: 392, ang: [-30, -15, 15, 30] };
  function fanPos(a) {
    const rad = (a * Math.PI) / 180;
    return [FAN.px + FAN.R * Math.sin(rad), FAN.py - FAN.R * Math.cos(rad)];
  }

  C.onSlide(1, (slide) => {
    const fan = slide.querySelector('.fan');
    fan.insertAdjacentHTML('beforeend', '<div class="rays"></div>');
    const list = cards();
    const order = list.filter((c) => !c.gold).concat(list.filter((c) => c.gold));
    order.forEach((c, i) => {
      const m = mini(c, FAN.w, FAN.h, c.gold ? 'center' : i < 2 ? 'left' : 'right');
      m.dataset.i = i;
      m.dataset.gold = c.gold ? '1' : '';
      m.style.zIndex = c.gold ? 20 : 12 - Math.round(Math.abs(i - 1.5));
      fan.appendChild(m);
    });
    fan.insertAdjacentHTML('beforeend', '<div class="burst"></div>');
  });

  C.animate(1, (t, slide) => {
    const { w, h, ang } = FAN;
    const [cx, cy] = fanPos(0);
    const minis = [...slide.querySelectorAll('.mini')];
    minis.forEach((m, i) => {
      const gold = m.dataset.gold === '1';
      let x = cx;
      let y = cy + 40;
      let a = 0;
      let s = 1;
      if (!gold) {
        const p = C.ease.back(C.prog(t, 0.35 + i * 0.07, 0.9));
        a = ang[i] * p + (i - 1.5) * 1.6 * (1 - p);
        const [fx, fy] = fanPos(a);
        x = fx + (i - 1.5) * 3 * (1 - p);
        y = fy * p + (cy + 40 + (i - 1.5) * 4) * (1 - p);
      } else {
        const rise = C.ease.inOut(C.prog(t, 2.45, 0.4));
        y = cy + 40 - 90 * rise;
        s = 1 + 0.06 * rise;
      }
      const flipStart = gold ? 2.65 : 1.4 + i * 0.27;
      const f = C.ease.inOut(C.prog(t, flipStart, gold ? 0.5 : 0.38));
      const lift = 1 + 0.1 * Math.sin(Math.PI * f);
      m.style.transform = `translate(${x - w / 2}px, ${y - h / 2}px) rotate(${a}deg) scale(${s * lift}) perspective(1400px) rotateY(${f * 180}deg)`;
    });
    // o baralho fechado começa maior (pôster forte no quadro 0) e assenta enquanto abre
    const k = 1.4 - 0.4 * C.ease.inOut(C.prog(t, 0.15, 1.1));
    const fan = slide.querySelector('.fan');
    fan.style.transformOrigin = `${cx}px ${cy + 40}px`;
    fan.style.transform = `scale(${k.toFixed(4)})`;
    const fl = C.prog(t, 2.9, 0.7);
    const burst = slide.querySelector('.burst');
    burst.style.opacity = (fl > 0 ? Math.sin(Math.PI * Math.min(1, fl)) * 0.8 : 0).toFixed(3);
    burst.style.transform = `translateY(${cy - 50 - 900}px)`;
    const rays = slide.querySelector('.rays');
    rays.style.opacity = (0.85 * C.ease.out(C.prog(t, 2.95, 0.8))).toFixed(3);
    rays.style.transform = `translateY(${cy - 50 - 900}px) rotate(${t * 8}deg)`;
  }, { duration: 5 });

  /* ---------------------------------------------------------------- como usar: cada import ligado à sua carta */
  C.onSlide('*', (slide, s) => {
    if (s.layout !== 'combo') return;
    const row = slide.querySelector('.row');
    const list = cards();
    const lines = [...slide.querySelectorAll('.paper-code .ln')];
    const S = slide.getBoundingClientRect();
    const W = 220;
    const Hh = 308;
    const byLine = ['pathlib', 'json', 'Counter', 'statistics', 'datetime']; // mesma ordem dos imports
    let svg = '';
    byLine.forEach((name, i) => {
      const c = list.find((k) => k.name === name);
      const m = mini(c, W, Hh);
      const x = 790;
      const lr = lines[i].getBoundingClientRect();
      const y = lr.top - S.top + lr.height / 2 - 34;
      m.style.zIndex = 10 + i;
      m.style.transform = `translate(${x}px, ${y}px) rotate(${(i - 2) * 1.2}deg) rotateY(180deg)`;
      row.appendChild(m);
      const seg = lines[i].querySelector('.seg').getBoundingClientRect();
      const lx = seg.right - S.left + 16;
      const ly = seg.top - S.top + seg.height / 2;
      const tx = x + 6;
      const ty = y + 34;
      const d = `M${lx} ${ly} C ${lx + 90} ${ly}, ${tx - 90} ${ty}, ${tx} ${ty}`;
      svg += `<path class="glow" d="${d}"/><path class="wire" d="${d}"/><circle class="dot" cx="${lx}" cy="${ly}" r="9"/>`;
    });
    slide.querySelector('.links').innerHTML = svg;
  });

  /* ---------------------------------------------------------------- fechamento: o mesmo leque, aberto */
  C.onSlide('*', (slide, s) => {
    if (s.layout !== 'cta') return;
    const fan = slide.querySelector('.fan-cta');
    const list = cards();
    const order = list.filter((c) => !c.gold).concat(list.filter((c) => c.gold));
    const angles = [...FAN.ang, 0];
    order.forEach((c, i) => {
      const m = mini(c, FAN.w, FAN.h, c.gold ? 'center' : i < 2 ? 'left' : 'right');
      const a = angles[i];
      const [x, y0] = fanPos(a);
      const y = y0 - 150 - (c.gold ? 40 : 0);
      m.style.zIndex = c.gold ? 20 : 12 - Math.round(Math.abs(i - 1.5));
      m.style.transform = `translate(${x - FAN.w / 2}px, ${y - FAN.h / 2}px) rotate(${a}deg) scale(${c.gold ? 1.06 : 1}) rotateY(180deg)`;
      fan.appendChild(m);
    });
  });
})();
