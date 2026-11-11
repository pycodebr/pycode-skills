/* Arquétipo conversa: um celular com a conversa entre dois lados e, ao lado, a versão técnica de cada mensagem.
   Serve para explicar um protocolo, um atendimento ou um diálogo entre sistemas. O texto é o próprio objeto,
   por isso a cena pode declarar um orçamento de palavras maior ("budget").
   data: { a, b, wire, messages: [{ from: "a"|"b", text, code, note }] } */
(() => {
  const { esc, q, qa, tip: mkTip, pos } = window.K;
  window.SCENES['__ID__'] = (slide, ctx) => {
    const D = ctx.data.data || {};
    const msgs = D.messages || [];
    const host = q(slide, '[data-fill]');
    host.innerHTML = `
      <div class="board">
        <div class="cv-phone">
          <div class="cv-top"><b>${esc(D.a || '')}</b><span class="cv-dots"><i></i><i></i><i></i></span><b>${esc(D.b || '')}</b></div>
          <div class="cv-list">${msgs.map((m, i) => `<div class="cv-msg ${m.from === 'b' ? 'b' : 'a'}" data-i="${i}"><p>${esc(m.text)}</p></div>`).join('')}</div>
        </div>
        <svg class="cv-wire" viewBox="0 0 1696 716" aria-hidden="true"><path class="cv-link" d=""/><circle class="cv-end" r="7" cx="0" cy="0"/></svg>
        <div class="cv-panel">
          <p class="cv-label mono">${esc(D.wire || '')}</p>
          <div class="cv-code mono"><span class="cv-code-t"></span><i class="cv-caret"></i></div>
          <p class="cv-note"></p>
          <ol class="cv-steps">${msgs.map((m, i) => `<li data-i="${i}" class="${m.from === 'b' ? 'b' : 'a'}"></li>`).join('')}</ol>
        </div>
      </div>`;
    const board = q(host, '.board');
    const els = qa(host, '.cv-msg'), steps = qa(host, '.cv-steps li');
    const codeT = q(host, '.cv-code-t'), note = q(host, '.cv-note'), link = q(host, '.cv-link'), end = q(host, '.cv-end');
    const codeBox = q(host, '.cv-code');
    let cur = 0, typing = null, rate = 1;
    const wire = () => {
      const el = els[cur];
      if (!el) return;
      const a = pos(el, board), b = pos(codeBox, board);
      const x1 = a.x + a.w + 6, y1 = a.y + a.h / 2, x2 = b.x - 10, y2 = b.y + b.h / 2, k = (x2 - x1) * .5;
      link.setAttribute('d', `M${x1} ${y1}C${x1 + k} ${y1},${x2 - k} ${y2},${x2} ${y2}`);
      end.setAttribute('cx', x2); end.setAttribute('cy', y2);
    };
    const focus = (i, anim) => {
      cur = i;
      const m = msgs[i] || {};
      els.forEach((el, j) => { el.classList.toggle('on', j === i); el.classList.toggle('dim', j !== i); });
      steps.forEach((el, j) => el.classList.toggle('on', j <= i));
      board.classList.toggle('from-b', m.from === 'b');
      typing?.kill();
      if (anim && ctx.motion()) { typing = FX.type(codeT, m.code || '', { cps: 34 }); typing.timeScale(rate); }
      else { codeT.textContent = m.code || ''; }
      note.textContent = m.note || '';
      if (anim && ctx.motion()) gsap.fromTo(note, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: .5, delay: .25, clearProps: 'opacity,transform' });
      wire();
      if (anim && ctx.motion()) FX.draw(link, { duration: .6 });
    };
    ctx.pick(els, i => focus(i, true), { group: 'mensagem', label: (el, i) => msgs[i].text });
    const cyc = FX.cycle({ n: msgs.length, every: 3.2, onStep: focus, homeIndex: 0, stillIndex: msgs.length - 1 });
    const intro = gsap.timeline({ paused: true });
    intro.fromTo(q(host, '.cv-phone'), { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: .9, ease: 'expo.out', clearProps: 'opacity,transform' }, 0)
      .fromTo(els, { opacity: 0, y: 18, scale: .96 }, { opacity: 1, y: 0, scale: 1, duration: .45, ease: 'back.out(2)', stagger: .4, clearProps: 'opacity,transform' }, .5)
      .fromTo(q(host, '.cv-panel'), { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: .8, ease: 'expo.out', clearProps: 'opacity,transform' }, .9);
    focus(0, false);
    return {
      intro, loop: cyc.loop, home: cyc.home, still: cyc.still, key: () => String(cur),
      layout: wire, speed: k => { rate = k; typing?.timeScale(k); }
    };
  };
})();
