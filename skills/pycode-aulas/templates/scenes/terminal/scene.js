/* Arquétipo terminal: um comando é digitado, a resposta aparece e cada parte importante vira um item clicável
   com a explicação ao lado. Serve para comandos, trechos de código, requisições e saídas de ferramentas.
   data: { prompt, title, command: [{ code, part? }], output: [{ code, tone?, part? }], parts: { id: { label, text } } } */
(() => {
  const { esc, q, qa, tip: mkTip, pos } = window.K;
  window.SCENES['__ID__'] = (slide, ctx) => {
    const D = ctx.data.data || {};
    const cmd = D.command || [], out = D.output || [], parts = D.parts || {};
    const order = [...cmd, ...out].map(t => t.part).filter((p, i, a) => p && a.indexOf(p) === i && parts[p]);
    const host = q(slide, '[data-fill]');
    const span = (t, kind) => t.part
      ? `<span class="tm-part ${kind}" data-part="${esc(t.part)}" data-tone="${esc(t.tone || '')}"><span class="tm-t" data-full="${esc(t.code)}"></span></span>`
      : `<span class="tm-t ${kind}" data-tone="${esc(t.tone || '')}" data-full="${esc(t.code)}"></span>`;
    host.innerHTML = `
      <div class="board">
        <div class="tm-win">
          <div class="tm-bar"><i></i><i></i><i></i><span class="mono">${esc(D.title || 'terminal')}</span></div>
          <pre class="tm-body mono"><span class="tm-prompt">${esc(D.prompt || '$')} </span>${cmd.map(t => span(t, 'cmd')).join('')}<span class="tm-caret"></span>

<span class="tm-out">${out.map(t => span(t, 'out')).join('\n')}</span></pre>
        </div>
        <svg class="tm-wire" viewBox="0 0 1696 716" aria-hidden="true"><path class="tm-link" d=""/></svg>
        <i class="tm-mark no-pick"></i>
        <div class="tm-side">
          <ol class="tm-index">${order.map((p, i) => `<li data-i="${i}"><b class="mono">${String(i + 1).padStart(2, '0')}</b>${esc(parts[p].label)}</li>`).join('')}</ol>
          <div class="tm-note"><h3></h3><p></p></div>
        </div>
      </div>`;
    const board = q(host, '.board');
    const texts = qa(host, '.tm-t');
    texts.forEach(el => { el.textContent = el.dataset.full; });
    const partEls = order.map(p => qa(host, `.tm-part[data-part="${p}"]`));
    const idx = qa(host, '.tm-index li'), noteH = q(host, '.tm-note h3'), noteP = q(host, '.tm-note p'), link = q(host, '.tm-link');
    const outEl = q(host, '.tm-out'), note = q(host, '.tm-note'), mark = q(host, '.tm-mark');
    let cur = 0;
    const wire = () => {
      const el = partEls[cur]?.[0];
      if (!el) return;
      const a = pos(el, board), b = pos(note, board);
      // a ligação sai da borda do terminal na altura da parte escolhida, sem cruzar o código
      const win = pos(q(host, '.tm-win'), board);
      const x1 = win.x + win.w, y1 = a.y + a.h / 2, x2 = b.x - 18, y2 = b.y + 34, k = (x2 - x1) * .5;
      link.setAttribute('d', `M${x1} ${y1}C${x1 + k} ${y1},${x2 - k} ${y2},${x2} ${y2}`);
      mark.style.transform = `translate(${x1}px, ${y1}px)`;
    };
    const focus = (i, anim) => {
      cur = i;
      partEls.forEach((els, j) => els.forEach(el => el.classList.toggle('on', j === i)));
      idx.forEach((el, j) => el.classList.toggle('on', j === i));
      const p = parts[order[i]] || {};
      noteH.textContent = p.label || ''; noteP.textContent = p.text || '';
      if (anim && ctx.motion()) gsap.fromTo(note, { opacity: 0, x: 24 }, { opacity: 1, x: 0, duration: .5, ease: 'expo.out', clearProps: 'opacity,transform' });
      wire();
      if (anim && ctx.motion()) FX.draw(link, { duration: .5 });
    };
    ctx.pick(partEls.map(els => els[0]), i => focus(i, true), { group: 'parte', label: (el, i) => `${parts[order[i]].label}: ${parts[order[i]].text}` });
    ctx.pick(idx, i => focus(i, true), { group: 'indice', label: (el, i) => parts[order[i]].label });
    const cyc = FX.cycle({ n: order.length, every: 2.8, onStep: focus, homeIndex: 0, stillIndex: 0 });
    // intro: digita o comando parte por parte e depois mostra a resposta
    const intro = gsap.timeline({ paused: true });
    intro.fromTo(q(host, '.tm-win'), { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: .7, ease: 'expo.out', clearProps: 'opacity,transform' }, 0)
      .fromTo(q(host, '.tm-side'), { opacity: 0 }, { opacity: 1, duration: .6, clearProps: 'opacity' }, .3)
      .set(outEl, { opacity: 0 }, 0);
    let at = .5;
    const typed = texts.filter(el => !el.closest('.tm-out'));
    intro.call(() => typed.forEach(el => { el.textContent = ''; }), null, .01);
    typed.forEach(el => {
      const full = el.dataset.full;
      const tw = FX.type(el, full, { cps: 44 });
      intro.add(tw, at);
      at += tw.duration() + .05;
    });
    intro.fromTo(outEl, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: .5, clearProps: 'opacity,transform' }, at + .2);
    focus(0, false);
    return { intro, loop: cyc.loop, home: cyc.home, still: cyc.still, key: () => String(cur), layout: wire, overlap: 0 };
  };
})();
