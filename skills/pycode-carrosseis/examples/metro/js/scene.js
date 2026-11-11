/*
 * Mapa do metrô: faixa do mapa, placa, objetos das estações, mapa grande e o trem da capa (vídeo).
 * A linha que cruza os slides é o svg.rail do runtime (rail.in/rail.out no slides.json, todos em y=1105).
 */
(() => {
  const C = window.Carousel;
  const XS = [150, 345, 540, 735, 930];
  const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;');

  /* ---------------------------------------------------------------- faixa do mapa */
  function strip(svg, current, names) {
    let s = '<rect class="panel" x="64" y="0" width="952" height="150" rx="22"/>';
    for (let i = 0; i < 4; i++) {
      const st = i + 2 <= current ? 'done' : 'todo';
      s += `<line class="seg ${st}" data-seg="${i}" x1="${XS[i]}" y1="58" x2="${XS[i + 1]}" y2="58"/>`;
    }
    names.forEach((name, i) => {
      const k = i + 1;
      const st = k < current ? 'done' : k === current ? 'cur' : 'todo';
      if (st === 'cur') s += `<circle class="halo" cx="${XS[i]}" cy="58" r="34"/>`;
      s += `<circle class="st ${st}" data-st="${i}" cx="${XS[i]}" cy="58" r="${st === 'cur' ? 20 : 15}"/>`;
      s += `<text class="lbl ${st === 'cur' ? 'cur' : ''}" x="${XS[i]}" y="122" text-anchor="middle">${esc(name)}</text>`;
    });
    svg.innerHTML = s;
  }

  /* ---------------------------------------------------------------- trem (dois carros) */
  function trainSVG(doorsOpen) {
    const car = (x, front) => {
      const body = front
        ? 'M24 870 H560 Q642 872 652 960 V1062 Q652 1090 624 1090 H0 V894 Q0 870 24 870 Z'
        : 'M24 870 H600 V1090 H0 V894 Q0 870 24 870 Z';
      let s = `<g transform="translate(${x} 0)"><path d="${body}" class="f-sur"/>
        <path d="M0 1016 H${front ? 652 : 600} V1036 H0 Z" class="f-acc"/>
        <path d="M24 870 H${front ? 560 : 600}" stroke-width="6" class="s-line" opacity=".8"/>`;
      for (let w = 0; w < 4; w++) {
        const wx = 30 + w * 128;
        if (w === 2) continue; // vão da porta
        s += `<rect x="${wx}" y="905" width="98" height="78" rx="12" class="f-board"/>
              <path d="M${wx + 14} 973 l36 -54" stroke-width="8" class="s-line" opacity=".22"/>`;
      }
      s += doorsOpen
        ? '<rect x="286" y="896" width="100" height="194" rx="6" class="f-board"/><rect x="296" y="906" width="80" height="184" rx="4" class="f-warn" opacity=".35"/>'
        : '<rect x="286" y="896" width="100" height="194" rx="6" class="f-sur2"/><path d="M336 900 V1088" stroke-width="4" class="s-line"/>';
      if (front) {
        s += '<path d="M572 900 H606 Q634 906 640 962 H572 Z" class="f-board"/><circle class="lamp f-warn" cx="632" cy="1052" r="11"/>';
      }
      [70, 150, front ? 470 : 450, front ? 550 : 530].forEach((wx) => { s += `<circle cx="${wx}" cy="1098" r="16" class="f-board"/>`; });
      return `${s}</g>`;
    };
    return `<svg width="1400" height="1350" viewBox="0 0 1400 1350"><g class="cars">
      <ellipse class="beam f-warn" cx="1180" cy="1080" rx="220" ry="40" opacity="0"/>
      ${car(0, false)}${car(620, true)}</g></svg>`;
  }

  /* ---------------------------------------------------------------- objetos de cada estação */
  const HERO = {
    1(hero, s) {
      const L = s.labels;
      hero.innerHTML = `<div class="ticket"><div class="stub">${esc(C.data.ui.ticket)}</div><div class="main">
        <div class="url"><span class="p1"><b>${esc(L.url_scheme)}</b><small>${esc(L.scheme)}</small></span>
          <span class="p2"><b>${esc(L.url_domain)}</b><small>${esc(L.domain)}</small></span>
          <span class="p3"><b>${esc(L.url_path)}</b><small>${esc(L.path)}</small></span></div>
        <pre class="code" data-code="code"></pre></div></div>`;
    },
    2(hero, s) {
      const L = s.labels;
      const flaps = (txt, cls = '') => [...txt].map((ch) => `<span class="flap ${cls}">${esc(ch)}</span>`).join('');
      hero.innerHTML = `<div class="board">
        <div class="row"><span class="cols" style="width:150px;margin:0">${esc(L.col_from)}</span><span class="flaps">${flaps(L.domain)}</span></div>
        <div class="row" style="margin-top:22px"><span class="cols" style="width:150px;margin:0">${esc(L.col_to)}</span><span class="flaps">${flaps(L.ip, 'ip')}</span></div></div>`;
    },
    3(hero) {
      let r = '<svg class="rack" viewBox="0 0 470 250"><rect x="10" y="0" width="450" height="250" rx="14" class="f-board"/>';
      for (let u = 0; u < 4; u++) {
        const y = 16 + u * 57;
        r += `<rect x="28" y="${y}" width="414" height="47" rx="6" class="f-sur2" opacity="${u === 1 ? 1 : 0.75}"/>`;
        for (let v = 0; v < 9; v++) r += `<rect x="${170 + v * 18}" y="${y + 12}" width="6" height="23" rx="3" class="f-board" opacity=".6"/>`;
        r += `<circle cx="${60}" cy="${y + 23}" r="8" class="${u === 1 ? 'f-acc' : 'f-ok'}"/><circle cx="${86}" cy="${y + 23}" r="8" class="f-ok" opacity=".55"/>`;
        if (u === 1) r += `<rect x="28" y="${y}" width="10" height="47" class="f-acc"/><circle cx="60" cy="${y + 23}" r="20" class="f-acc" opacity=".25"/>`;
      }
      r += '</svg>';
      hero.innerHTML = `${r}<div class="lcd"><pre class="code" data-code="code"></pre><small>${esc(C.data.ui.rack)}</small></div>`;
    },
    4(hero, s) {
      let d = '<svg class="db" viewBox="0 0 300 270">';
      [0, 1, 2].forEach((k) => {
        const y = 30 + k * 72;
        const hl = k === 1;
        d += `<path d="M40 ${y} v56 a110 26 0 0 0 220 0 v-56" class="${hl ? 'f-acc' : 'f-sur2'}"/>
              <ellipse cx="150" cy="${y}" rx="110" ry="26" class="${hl ? 'f-acc2' : 'f-sur'}"/>
              <path d="M40 ${y + 28} a110 26 0 0 0 220 0" fill="none" stroke-width="3" class="s-line" opacity=".7"/>`;
      });
      d += '</svg>';
      hero.innerHTML = `${d}<div class="query"><pre class="code" data-code="code"></pre><div class="row-out">${esc(s.labels.result)}</div></div>`;
    },
    5(hero) {
      const env = `<svg class="envelope" viewBox="0 0 260 230"><rect x="10" y="40" width="240" height="160" rx="12" class="f-paper"/>
        <path d="M10 52 L130 140 L250 52" fill="none" stroke-width="6" class="s-line"/>
        <circle cx="200" cy="180" r="38" class="f-ok"/><path d="M182 180 l12 13 l24 -26" fill="none" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" class="s-board"/></svg>`;
      hero.innerHTML = `${env}<div class="response"><pre class="code" data-code="code"></pre><span class="stamp">${esc(C.data.ui.stamp)}</span></div>`;
    },
  };

  C.onSlide('*', (slide, s, n) => {
    const names = C.data.stations;
    const st = slide.querySelector('.strip');
    if (st) strip(st, s.layout === 'station' ? s.station : s.layout === 'cta' ? 6 : 0, names);
    if (s.layout === 'station') {
      slide.querySelector('.badge').textContent = s.station;
      slide.querySelector('.sign-kicker').textContent = `${C.data.ui.station} ${s.station}`;
      slide.querySelector('.sign-name').textContent = names[s.station - 1];
      const hero = slide.querySelector('.hero');
      HERO[s.station](hero, s, n);
      const code = hero.querySelector('[data-code]');
      if (code && s.code) C.renderCode(code, s.code);
    }
    if (s.layout === 'cta') {
      slide.querySelector('.train').innerHTML = trainSVG(true);
      slide.querySelector('.train svg').style.transform = 'translateX(-320px)';
      slide.insertAdjacentHTML('beforeend', `<div class="sign" style="top:640px"><span class="badge">
        <svg viewBox="0 0 40 40" width="46" height="46"><path d="M9 21 l8 8 l15 -17" fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
        <span class="sign-text"><span class="sign-kicker">${esc(s.labels.end_kicker)}</span>
        <span class="sign-name">${esc(s.labels.end)}</span></span></div>`);
    }
  });

  /* ---------------------------------------------------------------- mapa grande (slide 2) */
  C.onSlide('*', (slide, s) => {
    if (s.layout !== 'map') return;
    const P = [[150, 470], [330, 470], [540, 230], [760, 230], [930, 470]];
    const path = `M-10 470 L${P[0]} L${P[1]} L${P[2]} L${P[3]} L${P[4]} L1090 470`;
    const pics = [
      'M-26 -16 h52 v32 h-52z M-10 -16 v32',                        // bilhete
      'M-24 -26 h40 q8 0 8 8 v44 h-40 q-8 0 -8 -8z M-16 -26 v52',   // lista telefônica
      'M-26 -24 h52 v16 h-52z M-26 -4 h52 v16 h-52z M-26 16 h52 v10 h-52z', // rack
      'M-24 -16 a24 8 0 0 0 48 0 a24 8 0 0 0 -48 0 v32 a24 8 0 0 0 48 0 v-32', // banco
      'M-26 -18 h52 v36 h-52z M-26 -18 l26 20 l26 -20',             // envelope
    ];
    let g = `<path class="line" d="${path}"/>`;
    P.forEach(([x, y], i) => {
      const up = y < 400; // estações de cima: rótulo acima; de baixo: rótulo abaixo
      const ny = up ? y - 62 : y + 86;
      const py = y - 150;
      g += `<circle class="st" cx="${x}" cy="${y}" r="34"/><text class="num" x="${x}" y="${y + 12}">${i + 1}</text>`;
      g += `<g transform="translate(${x} ${py})"><rect class="pic-bg" x="-42" y="-42" width="84" height="84" rx="18"/><path class="pic" d="${pics[i]}"/></g>`;
      g += `<text class="name" x="${x}" y="${ny}" text-anchor="middle">${esc(C.data.stations[i])}</text>`;
    });
    slide.querySelector('.bigmap').innerHTML = g;
  });

  /* ---------------------------------------------------------------- capa: o trem chega e as estações acendem */
  C.onSlide(1, (slide) => {
    slide.querySelector('.train').innerHTML = trainSVG(false);
    slide.querySelector('.tunnel').insertAdjacentHTML('beforeend', '<i class="headlights"></i>');
  });

  C.animate(1, (t, slide) => {
    const svg = slide.querySelector('.train svg');
    const p = C.ease.out(C.prog(t, 0.25, 2.3));
    const settle = Math.sin(C.prog(t, 2.55, 0.35) * Math.PI) * 6;
    const x = 1500 - (1500 - 140) * p - settle;
    svg.style.transform = `translateX(${x.toFixed(1)}px)`;
    const beam = slide.querySelector('.beam');
    if (beam) beam.style.opacity = (0.35 * (1 - C.prog(t, 2.2, 0.6))).toFixed(3);
    // faróis acesos dentro do túnel no quadro 0; somem quando o trem sai
    const lights = slide.querySelector('.headlights');
    lights.style.opacity = (1 - C.prog(t, 0.3, 0.9)).toFixed(3);
    // estações da faixa acendem uma a uma depois que o trem para
    slide.querySelectorAll('.strip .st').forEach((c, i) => {
      const on = C.prog(t, 2.8 + i * 0.3, 0.2);
      c.style.opacity = '1';
      c.classList.toggle('done', on >= 1);
      c.classList.toggle('todo', on < 1);
    });
    slide.querySelectorAll('.strip .seg').forEach((l, i) => {
      const on = C.prog(t, 2.95 + i * 0.3, 0.15) >= 1;
      l.classList.toggle('done', on);
      l.classList.toggle('todo', !on);
    });
  }, { duration: 5 });
})();
