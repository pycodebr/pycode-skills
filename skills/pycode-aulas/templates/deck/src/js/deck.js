'use strict';
/* pycode-aulas · motor do deck.
   - Palco fixo de 1920×1080 escalado para a janela; celular em retrato mostra o palco no topo e um resumo embaixo;
     modo leitura (menu, ?leitura) mostra todas as cenas como texto.
   - Cada cena é uma fábrica registrada em window.SCENES[id](slide, ctx) que devolve
     { intro, loop, home, key, still, enter?, leave?, layout?, take?, speed?, ambient? }.
   - Ao entrar: a intro toca e a demonstração (loop) toca UMA vez; no fim o motor chama home() e a cena para.
   - Qualquer clique na cena ativa faz o apresentador assumir (take); itens registrados com ctx.pick selecionam.
   - R, Recomeçar, M e trocar de cena devolvem o automático. ?still e prefers-reduced-motion mostram o estado final.
   - window.presentation.state() e .speed(k) existem para o QA. */
(() => {
  const D = window.DECK || { meta: {}, ui: {}, scenes: [] };
  const UI = D.ui || {};
  const slides = [...document.querySelectorAll('.slide')];
  const frame = document.querySelector('#frame');
  const deck = document.querySelector('#deck');
  const toolbar = document.querySelector('#toolbar');
  const overview = document.querySelector('#overview');
  const menu = document.querySelector('#menu');
  const params = new URLSearchParams(location.search);
  const storageKey = 'deck-' + (document.body.dataset.deckKey || 'aula');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const saved = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, String(v)); } catch { /* sem armazenamento a navegação continua */ } }
  };
  const stillMode = params.has('still');
  if (stillMode) document.body.classList.add('export');
  let motionOff = stillMode || reducedMotion.matches || saved.get(storageKey + '-motion') === 'off';
  let textMode = params.has('leitura') || (!params.has('palco') && saved.get(storageKey + '-texto') === 'on');
  let current = -1;
  let layoutFrame = null;
  let timerStart = 0, elapsed = 0, idleTimer = null, pointerStart = null;
  const built = new Map();
  const picks = new WeakMap();
  const sceneData = id => (D.scenes || []).find(s => s.id === id) || {};

  /* ---------- escala e modos de tela ---------- */
  const isPortrait = () => !textMode && innerWidth / innerHeight < 1.22;
  function layout() {
    layoutFrame = null;
    const portrait = isPortrait();
    const changed = textMode !== document.body.classList.contains('reading') || portrait !== document.body.classList.contains('portrait');
    document.body.classList.toggle('reading', textMode);
    document.body.classList.toggle('portrait', portrait);
    document.documentElement.style.setProperty('--toolbar-h', textMode ? Math.ceil(toolbar.getBoundingClientRect().height) + 20 + 'px' : '0px');
    if (!textMode) {
      const scale = portrait
        ? Math.max(.05, Math.min((innerWidth - 16) / 1920, innerHeight * .62 / 1080))
        : Math.max(.05, Math.min(innerWidth / 1920, innerHeight / 1080));
      frame.style.width = 1920 * scale + 'px';
      frame.style.height = 1080 * scale + 'px';
      deck.style.transform = `scale(${scale})`;
    } else {
      frame.style.width = ''; frame.style.height = '';
      deck.style.transform = 'none';
    }
    slides.forEach(s => s.inert = !textMode && s !== slides[current]);
    paintThread();
    if (changed) built.forEach(sc => sc.layout?.());
    else built.get(slides[current])?.layout?.();
    if (motionOff) FX.paintStill();
  }
  const requestLayout = () => { if (layoutFrame === null) layoutFrame = requestAnimationFrame(layout); };

  /* ---------- HUD e fio visual ---------- */
  const hud = document.querySelector('#hud');
  function paintThread() {
    if (current < 0) return;
    const n = slides.length, p = n > 1 ? current / (n - 1) : 1;
    const track = hud.querySelector('.thread-track');
    track.style.setProperty('--p', p.toFixed(4));
    track.style.setProperty('--x', (track.offsetWidth * p).toFixed(1) + 'px');
    hud.querySelectorAll('.stop').forEach((s, i) => s.classList.toggle('done', i <= current));
    deck.classList.toggle('complete', current === n - 1);
  }
  function paintHud() {
    const s = slides[current], data = sceneData(s.dataset.id);
    hud.querySelector('.chapter').textContent = s.dataset.chapter || '';
    hud.querySelector('.count').textContent = `${String(current + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
    hud.querySelector('.thread-label').textContent = data.thread || (D.meta.thread || '');
    paintThread();
    const rb = document.querySelector('#reading-bar');
    rb.querySelector('.rb-chapter').textContent = s.dataset.title || '';
    rb.querySelector('.rb-count').textContent = `${current + 1}/${slides.length}`;
    rb.querySelector('.rb-progress').style.setProperty('--p', ((current + 1) / slides.length).toFixed(4));
    FX.bg.setMode(s.dataset.bg || D.meta.background || 'grade');
    FX.bg.setColor(getComputedStyle(s).getPropertyValue('--accent').trim() || FX.token('--accent'));
  }

  /* ---------- cenas ---------- */
  function scene(slide) {
    if (built.has(slide)) return built.get(slide);
    const factory = window.SCENES[slide.dataset.id];
    let api = {};
    const ctx = {
      data: sceneData(slide.dataset.id), meta: D.meta, ui: UI,
      motion: () => !motionOff, requestLayout, show: i => show(i),
      pick: (els, fn, opts) => pick(els, fn, opts),
      take: () => take(slide),
      manual: () => !!built.get(slide)?._manual
    };
    try { api = factory ? (factory(slide, ctx) || {}) : {}; }
    catch (err) { console.error('cena', slide.dataset.id, err); api = {}; }
    if (!factory) console.error('cena sem fábrica registrada:', slide.dataset.id);
    if (api.loop) {
      api.loop.repeat(0);   // demonstração única
      // voltar ao início fora do callback: buscar o tempo 0 dentro do render da própria timeline trava o GSAP
      api.loop.eventCallback('onComplete', () => setTimeout(() => finishDemo(slide, api), 0));
    }
    built.set(slide, api);
    return api;
  }
  // registra itens clicáveis: foco por Tab, papel de botão, rótulo e ação por clique, Enter ou Espaço
  function pick(els, fn, { group = 'item', label = null, key = true } = {}) {
    [].concat(els).filter(Boolean).forEach((el, i) => {
      el.dataset.pick = group;
      if (key) { el.setAttribute('tabindex', '0'); el.setAttribute('role', 'button'); }
      const text = typeof label === 'function' ? label(el, i) : label;
      if (text) el.setAttribute('aria-label', text);
      picks.set(el, ev => fn(i, el, ev));
    });
  }
  function startDemo(slide, sc) {
    if (sc._manual || motionOff) return;
    sc.home?.();
    sc._startKey = sc.key ? String(sc.key()) : '';
    slide.dataset.demo = 'demo';
    sc.loop.play(0);
  }
  function finishDemo(slide, sc) {
    if (sc._manual || motionOff || slide !== slides[current]) return;
    sc.loop.pause(0);
    sc.home?.();
    slide.dataset.demo = 'home';
  }
  // o apresentador assume: completa a intro e pausa a demonstração no instante do clique
  function take(slide) {
    const sc = built.get(slide);
    if (!sc || sc._manual || textMode) return false;
    sc._manual = true; sc._dirty = true;
    sc._delay?.kill();
    if (sc.intro && sc.intro.progress() < 1) sc.intro.progress(1);
    sc.intro?.pause();
    sc.loop?.pause();
    sc.take?.();
    slide.dataset.demo = 'manual';
    return true;
  }
  function activate(el, ev) {
    const slide = slides[current];
    if (!slide || !slide.contains(el) || !picks.has(el)) return;
    take(slide);
    slide.querySelectorAll('[data-picked]').forEach(x => x.removeAttribute('data-picked'));
    el.setAttribute('data-picked', '');
    try { picks.get(el)(ev); } catch (err) { console.error('seleção', slide.dataset.id, err); }
  }
  function titleIntro(slide) {
    const words = [...slide.querySelectorAll('.slide-title')].flatMap(el => FX.splitWords(el));
    if (!words.length) return;
    gsap.killTweensOf(words);
    if (motionOff) { gsap.set(words, { clearProps: 'transform,opacity' }); return; }
    gsap.fromTo(words, { yPercent: 110, opacity: 0 }, { yPercent: 0, opacity: 1, duration: .8, ease: 'expo.out', stagger: .04, delay: .08, clearProps: 'transform,opacity' });
  }
  function enterScene(slide) {
    const sc = scene(slide);
    titleIntro(slide);
    sc._manual = false;
    sc._delay?.kill();
    slide.querySelectorAll('[data-picked]').forEach(x => x.removeAttribute('data-picked'));
    sc.intro?.pause(0);
    sc.loop?.pause(0);
    FX.ambient = sc.ambient || null;
    if (motionOff) {
      sc.intro?.progress(1).pause();
      sc.still ? sc.still() : sc.home?.();
      FX.paintStill();
      slide.dataset.demo = 'still';
    } else {
      if (sc._dirty) sc.home?.();
      sc._dirty = false;
      slide.dataset.demo = sc.intro ? 'intro' : 'demo';
      if (sc.intro) sc.intro.play(0);
      if (sc.loop) {
        const delay = sc.intro ? Math.max(0, sc.intro.duration() - (sc.overlap ?? .2)) : .4;
        sc._delay = gsap.delayedCall(delay, () => startDemo(slide, sc));
      } else {
        sc.home?.();
        sc._startKey = sc.key ? String(sc.key()) : '';
        slide.dataset.demo = 'home';
      }
    }
    sc.enter?.();
  }
  function leaveScene(slide) {
    const sc = built.get(slide);
    if (!sc) return;
    sc._delay?.kill();
    sc.intro?.pause();
    sc.loop?.pause();
    sc.leave?.();
    FX.ambient = null;
  }
  function replay() {
    const s = slides[current];
    if (!s || textMode) return;
    built.get(s)?.reset?.();
    leaveScene(s); enterScene(s);
  }

  /* ---------- transições: só transform e opacidade ---------- */
  const curtain = document.querySelector('#curtain'), iris = document.querySelector('#iris');
  function transition(from, to, dir) {
    if (!from || motionOff || textMode) {
      if (from) from.classList.remove('leaving');
      gsap.set(to, { clearProps: 'opacity,transform' });
      return;
    }
    from.classList.add('leaving');
    const kind = to.dataset.transition || 'corte';
    const done = () => { from.classList.remove('leaving'); gsap.set([from, to, curtain, iris], { clearProps: 'opacity,transform' }); };
    const tl = gsap.timeline({ onComplete: done });
    FX.bg.kick(kind === 'corte' ? .4 : 1);
    if (kind === 'cortina') {
      tl.set(to, { opacity: 0 }, 0)
        .fromTo(curtain, { xPercent: dir > 0 ? -101 : 101 }, { xPercent: 0, duration: .42, ease: 'power3.in' }, 0)
        .set(from, { opacity: 0 }, .42).set(to, { opacity: 1 }, .42)
        .to(curtain, { xPercent: dir > 0 ? 101 : -101, duration: .55, ease: 'power3.out' }, .46)
        .fromTo(to, { scale: 1.04 }, { scale: 1, duration: .8, ease: 'expo.out' }, .46);
    } else if (kind === 'iris') {
      tl.set(to, { opacity: 0 }, 0)
        .fromTo(iris, { scale: 0, opacity: 1 }, { scale: 1, duration: .5, ease: 'power3.in' }, 0)
        .set(from, { opacity: 0 }, .5).set(to, { opacity: 1 }, .5)
        .to(iris, { opacity: 0, duration: .45, ease: 'power2.out' }, .52)
        .fromTo(to, { scale: .96 }, { scale: 1, duration: .8, ease: 'expo.out' }, .52);
    } else if (kind === 'sobe') {
      tl.to(from, { opacity: 0, y: -50 * dir, duration: .3, ease: 'power2.in' }, 0)
        .fromTo(to, { opacity: 0, y: 70 * dir }, { opacity: 1, y: 0, duration: .7, ease: 'expo.out' }, .12);
    } else {
      tl.to(from, { opacity: 0, x: -dir * 70, scale: .97, duration: .3, ease: 'power2.in' }, 0)
        .fromTo(to, { opacity: 0, x: dir * 90 }, { opacity: 1, x: 0, duration: .7, ease: 'expo.out' }, .12);
    }
  }

  /* ---------- navegação ---------- */
  function indexFromHash() {
    const h = decodeURIComponent(location.hash.slice(1));
    if (!h) return null;
    if (/^\d+$/.test(h)) return Math.min(slides.length, Math.max(1, Number(h))) - 1;
    const i = slides.findIndex(s => s.dataset.id === h);
    return i >= 0 ? i : null;
  }
  function show(index, updateHash = true) {
    if (typeof index === 'string' && !/^\d+$/.test(index)) index = slides.findIndex(s => s.dataset.id === index);
    const next = Math.max(0, Math.min(slides.length - 1, Math.trunc(Number(index)) || 0));
    if (next === current) { if (textMode) slides[current].scrollIntoView(); return; }
    const prev = slides[current];
    const dir = next > current ? 1 : -1;
    if (prev) leaveScene(prev);
    current = next;
    slides.forEach((s, i) => {
      const on = i === current;
      s.classList.toggle('active', on);
      s.inert = !textMode && !on;
      s.setAttribute('aria-hidden', String(!textMode && !on));
    });
    transition(prev, slides[current], dir);
    document.querySelector('#counter').textContent = `${current + 1} / ${slides.length}`;
    document.querySelector('#previous').disabled = document.querySelector('#edge-prev').disabled = current === 0;
    document.querySelector('#next').disabled = document.querySelector('#edge-next').disabled = current === slides.length - 1;
    document.querySelectorAll('#overview-list button').forEach((b, i) => b.setAttribute('aria-current', String(i === current)));
    if (updateHash) history.replaceState(null, '', location.pathname + location.search + `#${current + 1}`);
    saved.set(storageKey, current);
    document.title = `${current + 1}. ${slides[current].dataset.title} | ${D.meta.title || ''}`;
    paintHud();
    paintMobileInfo(slides[current]);
    if (textMode) slides[current].scrollIntoView({ block: 'start' });
    else enterScene(slides[current]);
  }

  /* ---------- celular em retrato ---------- */
  function paintMobileInfo(s) {
    const mi = document.querySelector('#mobile-info');
    mi.querySelector('.mi-title').textContent = s.dataset.title || '';
    const ap = s.querySelector('.apoio');
    mi.querySelector('.mi-apoio').textContent = ap ? ap.textContent.trim() : '';
    const clones = [...s.querySelectorAll('.rd-only')].map(el => {
      const c = el.cloneNode(true);
      [c, ...c.querySelectorAll('*')].forEach(x => ['id', 'tabindex', 'data-pick', 'role', 'aria-hidden', 'style'].forEach(a => x.removeAttribute(a)));
      c.className = 'mi-list';
      return c;
    });
    mi.querySelector('.mi-more-body').replaceChildren(...clones);
    const more = mi.querySelector('.mi-more');
    more.hidden = !clones.length;
    more.open = false;
  }
  function setTextMode(on) {
    if (current >= 0 && !textMode) leaveScene(slides[current]);
    textMode = on;
    saved.set(storageKey + '-texto', on ? 'on' : 'off');
    const b = document.querySelector('#textmode');
    b.textContent = on ? (UI.stageMode || 'Ver as cenas animadas') : (UI.textMode || 'Ler em modo texto');
    b.setAttribute('aria-pressed', String(on));
    layout();
    slides.forEach((s, i) => s.setAttribute('aria-hidden', String(!on && i !== current)));
    if (on) slides[current].scrollIntoView({ block: 'start' });
    else { window.scrollTo(0, 0); enterScene(slides[current]); }
  }
  // no modo leitura, a cena atual acompanha a rolagem
  addEventListener('scroll', () => {
    if (!textMode) return;
    const y = innerHeight * .3;
    let idx = 0;
    slides.forEach((s, i) => { if (s.getBoundingClientRect().top < y) idx = i; });
    if (idx !== current) {
      current = idx;
      document.querySelector('#counter').textContent = `${current + 1} / ${slides.length}`;
      history.replaceState(null, '', location.pathname + location.search + `#${current + 1}`);
      paintHud();
    }
  }, { passive: true });

  /* ---------- movimento, tela cheia e cronômetro ---------- */
  function setMotion() {
    FX.motion = !motionOff;
    document.body.classList.toggle('motion-off', motionOff);
    const b = document.querySelector('#motion');
    b.textContent = motionOff ? (UI.motionOn || 'Ativar animações') : (UI.motionOff || 'Pausar animações');
    b.setAttribute('aria-pressed', String(!motionOff));
    if (!stillMode) saved.set(storageKey + '-motion', motionOff ? 'off' : 'on');
    if (current >= 0 && !textMode) { leaveScene(slides[current]); enterScene(slides[current]); }
  }
  async function fullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else if (document.documentElement.requestFullscreen) await document.documentElement.requestFullscreen();
      else document.querySelector('#fullscreen-help').hidden = false;
    } catch { document.querySelector('#fullscreen-help').hidden = false; }
    requestLayout();
  }
  function wake() {
    document.body.classList.remove('idle');
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => { if (!menu.open && !overview.open) document.body.classList.add('idle'); }, 2600);
  }

  /* ---------- montagem ---------- */
  slides.forEach((s, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    const n = document.createElement('span');
    n.textContent = `${String(i + 1).padStart(2, '0')}${s.dataset.chapter ? ' · ' + s.dataset.chapter : ''}`;
    b.append(n, document.createTextNode(s.dataset.title));
    b.addEventListener('click', () => { overview.close(); show(i); });
    document.querySelector('#overview-list').append(b);
  });
  const on = (sel, ev, fn) => document.querySelector(sel).addEventListener(ev, fn);
  on('#previous', 'click', () => show(current - 1));
  on('#next', 'click', () => show(current + 1));
  on('#edge-prev', 'click', e => { show(current - 1); if (e.detail > 0) e.currentTarget.blur(); });
  on('#edge-next', 'click', e => { show(current + 1); if (e.detail > 0) e.currentTarget.blur(); });
  on('#open-overview', 'click', () => overview.showModal());
  on('#close-overview', 'click', () => overview.close());
  on('#open-menu', 'click', () => menu.showModal());
  on('#close-menu', 'click', () => menu.close());
  on('#fullscreen', 'click', fullscreen);
  on('#motion', 'click', () => { motionOff = !motionOff; setMotion(); });
  on('#replay', 'click', () => { menu.close(); if (textMode) setTextMode(false); replay(); });
  on('#textmode', 'click', () => { menu.close(); setTextMode(!textMode); });
  on('#mi-text', 'click', () => setTextMode(true));
  const timer = document.querySelector('#timer');
  timer.addEventListener('click', () => {
    if (timerStart) { elapsed += Date.now() - timerStart; timerStart = 0; } else timerStart = Date.now();
    timer.setAttribute('aria-pressed', String(Boolean(timerStart)));
  });
  timer.addEventListener('dblclick', () => { timerStart = 0; elapsed = 0; timer.setAttribute('aria-pressed', 'false'); });
  setInterval(() => {
    const sec = Math.floor((elapsed + (timerStart ? Date.now() - timerStart : 0)) / 1000);
    timer.textContent = `${String(Math.floor(sec / 60)).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`;
  }, 250);

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') document.body.classList.remove('blanked');
    if (document.querySelector('dialog[open]') || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.target.closest('input,textarea,select,[contenteditable=true]')) return;
    const k = e.key.toLowerCase();
    const picked = e.target.closest?.('[data-pick]');
    if (picked && [' ', 'enter'].includes(k)) { e.preventDefault(); activate(picked, e); return; }
    if (e.target.closest('button,a,summary') && [' ', 'enter'].includes(k)) return;
    if (['arrowright', 'pagedown'].includes(k) || (k === ' ' && !textMode)) { e.preventDefault(); show(current + 1); }
    else if (['arrowleft', 'pageup'].includes(k)) { e.preventDefault(); show(current - 1); }
    else if (k === 'home') { e.preventDefault(); show(0); }
    else if (k === 'end') { e.preventDefault(); show(slides.length - 1); }
    else if (k === 'f') fullscreen();
    else if (k === 'o') overview.showModal();
    else if (k === 'b') document.body.classList.toggle('blanked');
    else if (k === 'r') replay();
    else if (k === 'm') { motionOff = !motionOff; setMotion(); }
    else if (k === 't') timer.click();
    else if (k === '?') menu.showModal();
  });
  deck.addEventListener('pointerdown', e => {
    const slide = slides[current];
    // mouse e caneta assumem no pointerdown; no toque, só no clique (rolar a página não pausa a cena)
    if (e.pointerType !== 'touch' && slide?.contains(e.target)) take(slide);
    if (e.pointerType === 'touch' && !textMode && !e.target.closest('a,[data-pick]')) pointerStart = [e.clientX, e.clientY];
  });
  deck.addEventListener('click', e => {
    const slide = slides[current];
    if (textMode || !slide?.contains(e.target)) return;
    const el = e.target.closest('[data-pick]');
    if (el && slide.contains(el)) {
      activate(el, e);
      if (e.detail > 0) el.blur?.();   // depois do clique, Espaço e setas voltam a navegar
    } else take(slide);
  });
  deck.addEventListener('pointerup', e => {
    if (!pointerStart) return;
    const dx = e.clientX - pointerStart[0], dy = e.clientY - pointerStart[1];
    pointerStart = null;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.8) show(current + (dx < 0 ? 1 : -1));
  });
  deck.addEventListener('pointercancel', () => { pointerStart = null; });
  ['mousemove', 'pointerdown', 'keydown', 'touchstart'].forEach(ev => addEventListener(ev, wake, { passive: true }));
  addEventListener('resize', requestLayout);
  window.visualViewport?.addEventListener('resize', requestLayout);
  addEventListener('hashchange', () => { const i = indexFromHash(); if (i !== null) show(i, false); });
  document.addEventListener('fullscreenchange', requestLayout);
  reducedMotion.addEventListener('change', e => { motionOff = e.matches; setMotion(); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) gsap.globalTimeline.pause(); else gsap.globalTimeline.resume(); });

  window.presentation = {
    show, replay, layout,
    get current() { return current; }, get count() { return slides.length; },
    get motion() { return !motionOff; },
    ids: () => slides.map(s => s.dataset.id),
    scene: id => built.get(slides.find(s => s.dataset.id === id)),
    // estado da cena ativa para o QA
    state: () => {
      const s = slides[current], sc = built.get(s) || {};
      return {
        id: s.dataset.id, index: current, demo: s.dataset.demo || '', manual: !!sc._manual,
        key: sc.key ? String(sc.key()) : null, startKey: sc._startKey ?? null,
        intro: sc.intro ? sc.intro.duration() : 0, loop: sc.loop ? sc.loop.duration() : 0, loopActive: !!sc.loop?.isActive(),
        picks: s.querySelectorAll('[data-pick]').length, reading: textMode, portrait: document.body.classList.contains('portrait')
      };
    },
    // só para o QA: acelera a cena ativa (gsap.globalTimeline.timeScale trava com timelines pausadas)
    speed: k => { const sc = built.get(slides[current]); [sc?.intro, sc?.loop, sc?._delay].forEach(t => t?.timeScale(k)); sc?.speed?.(k); }
  };

  FX.bg.init(document.querySelector('#bg-canvas'));
  FX.start();
  FX.motion = !motionOff;
  document.body.classList.toggle('motion-off', motionOff);
  const mb = document.querySelector('#motion');
  mb.textContent = motionOff ? (UI.motionOn || 'Ativar animações') : (UI.motionOff || 'Pausar animações');
  mb.setAttribute('aria-pressed', String(!motionOff));
  const tb = document.querySelector('#textmode');
  tb.textContent = textMode ? (UI.stageMode || 'Ver as cenas animadas') : (UI.textMode || 'Ler em modo texto');
  tb.setAttribute('aria-pressed', String(textMode));
  layout();
  const fromHash = indexFromHash();
  const start = fromHash ?? Number(saved.get(storageKey) || 0);
  show(Number.isFinite(start) ? start : 0, true);
  wake();
  document.fonts.ready.then(() => {
    requestLayout();
    setTimeout(() => { requestLayout(); built.forEach(sc => sc.layout?.()); document.documentElement.dataset.ready = 'true'; }, 250);
  });
})();
