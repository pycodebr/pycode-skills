/* Comportamento da página. Tudo aqui é melhoria progressiva: sem JavaScript, o conteúdo,
   os links, o menu (details) e o formulário continuam funcionando. */
(function () {
  'use strict';

  var root = document.documentElement;
  var header = document.querySelector('.site-header');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* Altura real do header em --header-h: alinha as âncoras logo abaixo dele. */
  function headerHeight() {
    return header ? header.getBoundingClientRect().height : 0;
  }
  function syncHeader() {
    root.style.setProperty('--header-h', Math.round(headerHeight()) + 'px');
  }
  syncHeader();
  if (header && 'ResizeObserver' in window) new ResizeObserver(syncHeader).observe(header);

  /* Âncoras por posição medida. Seções com content-visibility:auto têm altura provisória;
     por isso materializamos as seções, esperamos dois quadros, rolamos e conferimos de novo. */
  function materialize() {
    document.querySelectorAll('main > .section').forEach(function (section) {
      section.style.contentVisibility = 'visible';
    });
  }
  function targetTop(target) {
    // Alvo no header fixo (ex.: #topo) ou dentro dele: o destino é o início da página.
    if (header && (target === header || header.contains(target) || target.contains(header))) return 0;
    return Math.max(0, window.scrollY + target.getBoundingClientRect().top - headerHeight() - 12);
  }
  function settle(target) {
    var top = targetTop(target);
    if (Math.abs(window.scrollY - top) > 1) window.scrollTo({ top: top, behavior: 'instant' });
  }
  function goTo(hash, smooth) {
    var target = hash.length > 1 && document.getElementById(decodeURIComponent(hash.slice(1)));
    if (!target) return false;
    materialize();
    // Dois quadros para o layout real das seções e, depois, as fontes que elas pediram:
    // uma fonte que chega no meio da rolagem muda a quebra das linhas e desloca o alvo.
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        document.fonts.ready.then(function () { scrollToTarget(target, smooth); });
      });
    });
    return true;
  }
  /* Depois de chegar, a posição é conferida até ficar estável e continua vigiada por alguns segundos:
     fonte que chega tarde ou bloco que muda de altura desloca o alvo, e a correção só para quando a
     pessoa assume a rolagem. O estado fica em <html data-anchor="moving|done"> para o QA esperar por ele. */
  var pending = null;
  function stopWatching() {
    if (!pending) return;
    pending = null;
    root.dataset.anchor = 'done';
  }
  function recheck() {
    if (!pending) return;
    if (performance.now() > pending.until) { pending = null; return; }
    settle(pending.target);
  }
  ['wheel', 'touchmove', 'keydown', 'mousedown'].forEach(function (name) {
    window.addEventListener(name, stopWatching, { passive: true });
  });
  if ('ResizeObserver' in window) new ResizeObserver(recheck).observe(document.body);
  if (document.fonts && document.fonts.addEventListener) document.fonts.addEventListener('loadingdone', recheck);

  function scrollToTarget(target, smooth) {
    var useSmooth = smooth && !reduced.matches;
    pending = null;
    root.dataset.anchor = 'moving';
    window.scrollTo({ top: targetTop(target), behavior: useSmooth ? 'smooth' : 'instant' });
    if (!target.hasAttribute('tabindex') && !/^(A|BUTTON|INPUT|SELECT|TEXTAREA|DETAILS)$/.test(target.tagName)) {
      target.setAttribute('tabindex', '-1');
    }
    target.focus({ preventScroll: true });
    var done = false;
    function finish() {
      if (done) return;
      done = true;
      window.removeEventListener('scrollend', finish);
      var watch = { target: target, until: performance.now() + 3000 };
      var checks = 0;
      var stable = 0;
      pending = watch;
      (function verify() {
        if (pending !== watch) return;
        var before = window.scrollY;
        settle(target);
        stable = Math.abs(window.scrollY - before) <= 1 ? stable + 1 : 0;
        checks += 1;
        if (stable >= 2 || checks >= 10) { root.dataset.anchor = 'done'; return; }
        window.setTimeout(verify, 160);
      })();
    }
    if (useSmooth) {
      window.addEventListener('scrollend', finish);
      window.setTimeout(finish, 1400);
    } else {
      finish();
    }
  }
  document.addEventListener('click', function (event) {
    var link = event.target.closest('a[href^="#"]');
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    var hash = link.getAttribute('href');
    if (hash === '#' || !goTo(hash, true)) return;
    event.preventDefault();
    history.pushState(null, '', hash);
    var menu = link.closest('details.menu');
    if (menu) menu.open = false;
  });
  window.addEventListener('popstate', function () { goTo(location.hash || '#topo', false); });
  if (location.hash) {
    window.addEventListener('load', function () {
      document.fonts.ready.then(function () { goTo(location.hash, false); });
    }, { once: true });
  }

  /* Movimento por componente: liga só o que está visível, com a aba ativa e sem movimento reduzido. */
  var scenes = Array.prototype.slice.call(document.querySelectorAll('.motion-scene'));
  var visible = new Set();
  function syncMotion() {
    document.body.dataset.hidden = String(document.hidden);
    scenes.forEach(function (scene) {
      var seen = visible.has(scene);
      var running = seen && !reduced.matches && !document.hidden;
      scene.dataset.motion = running ? 'on' : 'off';
      if (seen) scene.dataset.entered = 'true';
    });
  }
  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) visible.add(entry.target);
        else visible.delete(entry.target);
      });
      syncMotion();
    }, { threshold: 0.12 });
    scenes.forEach(function (scene) { observer.observe(scene); });
  } else {
    scenes.forEach(function (scene) { visible.add(scene); });
  }
  document.addEventListener('visibilitychange', syncMotion);
  if (reduced.addEventListener) reduced.addEventListener('change', syncMotion);
  syncMotion();

  /* Ingresso: o canhoto destaca e volta (ilustração, sem ação de compra). */
  document.querySelectorAll('.ticket-stub').forEach(function (stub) {
    stub.disabled = false;
    stub.addEventListener('click', function () {
      var torn = stub.closest('.ticket').classList.toggle('torn');
      stub.setAttribute('aria-pressed', String(torn));
      stub.querySelector('span').textContent = torn ? stub.dataset.reset : stub.dataset.label;
    });
  });

  /* Parâmetros da URL (utm_*, ref...) seguem para links e formulários marcados com data-keep-params.
     Valores repetidos da mesma chave são preservados (delete uma vez + append de cada valor). */
  var incoming = new URLSearchParams(window.location.search);
  if (incoming.toString()) {
    document.querySelectorAll('a[data-keep-params]').forEach(function (link) {
      try {
        var url = new URL(link.href);
        new Set(incoming.keys()).forEach(function (key) { url.searchParams.delete(key); });
        incoming.forEach(function (value, key) { url.searchParams.append(key, value); });
        if (link.href !== url.href) link.href = url.href;
      } catch (error) {
        console.warn('[pagina] não consegui repassar os parâmetros para', link.href, error);
      }
    });
    document.querySelectorAll('form[data-keep-params]').forEach(function (form) {
      incoming.forEach(function (value, key) {
        if (form.elements[key] && form.elements[key].type !== 'hidden') return;
        var field = document.createElement('input');
        field.type = 'hidden';
        field.name = key;
        field.value = value;
        form.appendChild(field);
      });
    });
  }
})();
