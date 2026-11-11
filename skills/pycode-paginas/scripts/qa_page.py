#!/usr/bin/env python3
"""pycode page qa: QA no navegador real, fail-closed (sai com código 1 se qualquer gate falhar).

Gates: HTML (balanceamento, um h1, lang, metadados, alt, width/height, rel de links externos), texto PT-BR,
contraste dos pares de tokens, matriz 1440/820/390/320 (overflow, console, rede, imagens, fontes), âncoras
internas por posição medida em navegação nova (clique e fragmento direto), leitura sem JavaScript,
movimento reduzido, movimento real no desktop (dois quadros), pausa fora da viewport e com a aba oculta,
CLS do carregamento em celular com rede e CPU limitadas.
"""
import argparse
import contextlib
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

if not __debug__:
    raise RuntimeError("rode sem -O: os gates de QA não podem ser desligados")

import page_common as pc  # noqa: E402
from pycode_tools import paths  # noqa: E402
from pycode_tools import text as T  # noqa: E402
from pycode_tools.browser import audit, chromium, new_page  # noqa: E402
from pycode_tools.color import luminance  # noqa: E402
from pycode_tools.server import serve  # noqa: E402

PAIRS = [("--text", "--bg", 4.5), ("--text", "--bg-2", 4.5), ("--text", "--surface", 4.5), ("--text", "--surface-2", 4.5),
         ("--muted", "--bg", 4.5), ("--muted", "--bg-2", 4.5), ("--muted", "--surface", 4.5),
         ("--paper-ink", "--paper", 4.5), ("--accent-ink", "--accent", 4.5), ("--accent", "--bg", 3.0), ("--accent-2", "--bg", 3.0)]

JS_HEADER_BOTTOM = """() => {
  const cands = [...document.querySelectorAll('header, nav, [class*="header"], [class*="topbar"], body > *')];
  let bottom = 0;
  for (const el of cands) {
    const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    if ((cs.position === 'sticky' || cs.position === 'fixed') && r.top <= 1 && r.height > 0 && r.height < innerHeight / 2 && r.width > innerWidth * 0.5) bottom = Math.max(bottom, r.bottom);
  }
  return bottom;
}"""
JS_IMAGES_IN_VIEW = """() => [...document.images].filter(i => { const r = i.getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight && r.width > 0; })
  .map(i => ({src: i.currentSrc || i.src, ok: i.complete && i.naturalWidth > 0 && i.naturalHeight > 0}))"""
JS_FONTS = """() => {
  const fam = v => getComputedStyle(document.documentElement).getPropertyValue(v).split(',')[0].trim().replace(/['"]/g, '');
  const want = [...new Set([fam('--font-display'), fam('--font-body')].filter(Boolean))];
  const faces = [...document.fonts];
  const norm = f => f.family.replace(/['"]/g, '');
  return want.map(f => ({family: f, declared: faces.some(x => norm(x) === f), loaded: faces.some(x => norm(x) === f && x.status === 'loaded')}));
}"""
JS_CSS_READY = """() => [...document.querySelectorAll('link[as="style"]')].every(l => l.rel === 'stylesheet' && l.sheet)"""
JS_ANIMS = """(index) => {
  const scope = index === null ? document.body : [...document.querySelectorAll('.motion-scene')][index];
  return document.getAnimations().filter(a => a.effect && a.effect.target && scope.contains(a.effect.target)).map(a => {
    const t = a.effect.target, pe = a.effect.pseudoElement || null, cs = getComputedStyle(t, pe);
    const timing = a.effect.getComputedTiming();
    return {name: a.animationName || a.transitionProperty || 'animação', state: a.playState, infinite: timing.iterations === Infinity,
            duration: typeof timing.duration === 'number' ? timing.duration : 0,
            skipped: typeof t.checkVisibility === 'function' ? !t.checkVisibility({contentVisibilityAuto: true}) : false,
            sig: [cs.transform, cs.opacity, cs.translate, cs.rotate, cs.scale, cs.strokeDashoffset].join('|')};
  });
}"""
JS_NOJS_VISIBLE = """() => {
  const hidden = [];
  const opacity = el => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentElement) o *= parseFloat(getComputedStyle(e).opacity); return o; };
  for (const el of document.querySelectorAll('main h1, main h2, main h3, main p, main li, main dt, main dd, main summary')) {
    if (el.closest('details:not([open])') && el.tagName !== 'SUMMARY') continue;
    if (el.closest('[aria-hidden="true"]')) continue;
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    if (!el.textContent.trim()) continue;
    if (r.width < 1 || r.height < 1 || cs.visibility === 'hidden' || opacity(el) < 0.5) hidden.push(el.tagName.toLowerCase() + ': ' + el.textContent.trim().slice(0, 50));
  }
  return {hidden, textLength: (document.querySelector('main') || document.body).textContent.trim().length,
          styled: [...document.styleSheets].filter(s => s.href).length};
}"""
JS_CONTRAST = """(names) => {
  const c = document.createElement('canvas'); c.width = c.height = 1;
  const x = c.getContext('2d', {willReadFrequently: true});
  const cs = getComputedStyle(document.documentElement);
  const out = {};
  for (const n of names) {
    const v = cs.getPropertyValue(n).trim();
    if (!v) { out[n] = null; continue; }
    x.clearRect(0, 0, 1, 1); x.fillStyle = '#000'; x.fillStyle = v; x.fillRect(0, 0, 1, 1);
    out[n] = [...x.getImageData(0, 0, 1, 1).data];
  }
  return out;
}"""
CLS_INIT = """window.__cls = 0; window.__shifts = [];
try { new PerformanceObserver(list => { for (const e of list.getEntries()) { if (!e.hadRecentInput) { window.__cls += e.value;
  window.__shifts.push({value: e.value, nodes: (e.sources || []).map(s => s.node && s.node.nodeName ? (s.node.nodeName + '.' + (s.node.className || '')).slice(0, 60) : '?')}); } } })
  .observe({type: 'layout-shift', buffered: true}); } catch (e) {}"""


class Report:
    """Acumula resultados e grava um checkpoint a cada etapa (um timeout não apaga o que já rodou)."""

    def __init__(self, out, target):
        self.out = out
        self.data = {"target": target, "started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": [], "warnings": [], "shots": []}

    def check(self, name, ok, details=None):
        self.data["checks"].append({"name": name, "ok": bool(ok), "details": details if details is not None else {}})
        mark = "ok " if ok else "FALHA"
        print(f"  [{mark}] {name}" + ("" if ok else f": {_short(details)}"), flush=True)
        self.save()

    def warn(self, text):
        self.data["warnings"].append(text)
        self.save()

    def save(self):
        pc.write_json(self.out / "report.json", self.data)

    @property
    def failed(self):
        return [c for c in self.data["checks"] if not c["ok"]]


def _short(details, limit=320):
    text = str(details)
    return text if len(text) <= limit else text[:limit] + "…"


def parse_args(argv):
    ap = argparse.ArgumentParser(prog="pycode page qa", description="QA no navegador, fail-closed. Grava report.json e capturas.")
    ap.add_argument("target", nargs="?", default=".", help="projeto (testa dist/), pasta com index.html ou URL")
    ap.add_argument("--out", help="pasta do relatório (padrão: <projeto>/qa ou ./qa-report)")
    ap.add_argument("--sizes", default="1440x900,820x1180,390x844,320x640", help="matriz de viewports")
    ap.add_argument("--anchor-sizes", default="1440x900,390x844", help="viewports do teste de âncoras")
    ap.add_argument("--lenient-text", action="store_true", help="avisos do `pycode text` não reprovam")
    ap.add_argument("--max-cls", type=float, default=0.01, help="CLS máximo do carregamento (padrão 0,01)")
    ap.add_argument("--skip-anchors", action="store_true")
    ap.add_argument("--skip-motion", action="store_true")
    return ap.parse_args(argv)


def sizes(text):
    return [tuple(int(v) for v in part.split("x")) for part in text.split(",") if part.strip()]


# ---------------------------------------------------------------- etapas estáticas
def static_stage(rep, pages, lenient):
    errors, warnings, text_issues = [], [], []
    for name, file in pages:
        content = file.read_text(encoding="utf-8")
        e, w = pc.static_checks(content, name)
        errors += e
        warnings += w
        for level, message, ctx in T.lint(T.extract(file)):
            text_issues.append(f"{name}: [{level}] {message}" + (f" · {ctx}" if ctx else ""))
    rep.check("HTML: estrutura, h1, lang, metadados, alt, dimensões, rel", not errors, errors)
    for w in warnings:
        rep.warn(w)
    blocking = [t for t in text_issues if "[erro]" in t or not lenient]
    rep.check("texto PT-BR (pycode text)", not blocking, text_issues)


def contrast_stage(rep, page):
    names = sorted({n for pair in PAIRS for n in pair[:2]})
    colors = page.evaluate(JS_CONTRAST, names)
    results, bad = [], []
    for fg, bg, minimum in PAIRS:
        a, b = colors.get(fg), colors.get(bg)
        if not a or not b:
            rep.warn(f"contraste: token {fg if not a else bg} não definido")
            continue
        alpha = a[3] / 255
        mixed = [round(a[i] * alpha + b[i] * (1 - alpha)) for i in range(3)]
        la, lb = luminance(mixed), luminance(b[:3])
        ratio = (max(la, lb) + 0.05) / (min(la, lb) + 0.05)
        results.append(f"{fg}/{bg} {ratio:.2f}:1 (mín {minimum})")
        if ratio < minimum:
            bad.append(f"{fg} sobre {bg}: {ratio:.2f}:1 (mínimo {minimum}:1)")
    rep.check("contraste dos pares de tokens", not bad, bad or results)


def contrast_stage_url(rep, browser, url):
    page = open_page(browser, url, 1440, 900)
    try:
        contrast_stage(rep, page)
    finally:
        page.context.close()


# ---------------------------------------------------------------- navegador
def open_page(browser, url, w, h, **kw):
    page = new_page(browser, w, h, mobile=w < 600, **kw)
    page.goto(url, wait_until="load", timeout=60000)
    with contextlib.suppress(Exception):
        page.evaluate("document.fonts.ready.then(() => true)")
    with contextlib.suppress(Exception):
        page.wait_for_function(JS_CSS_READY, timeout=8000)
    page.wait_for_timeout(300)
    return page


def scroll_through(page, on_step=None):
    page.evaluate("document.documentElement.style.scrollBehavior = 'auto'")
    height = page.evaluate("document.documentElement.scrollHeight")
    step = max(200, int(page.viewport_size["height"] * 0.8))
    y = 0
    while y < height:
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(140)
        if on_step:
            on_step()
        y += step
        height = page.evaluate("document.documentElement.scrollHeight")
    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    page.wait_for_timeout(200)
    if on_step:
        on_step()


def matrix_stage(rep, browser, urls, size_list, out):
    for name, url in urls:
        for w, h in size_list:
            page = open_page(browser, url, w, h)
            broken = {}

            def look():
                for img in page.evaluate(JS_IMAGES_IN_VIEW):
                    if not img["ok"]:
                        broken[img["src"]] = True
            look()
            shot = out / f"{Path(name).stem}-{w}x{h}.png"
            page.evaluate("window.scrollTo(0, 0)")
            page.screenshot(path=str(shot))
            rep.data["shots"].append(str(shot))
            scroll_through(page, look)
            a = audit(page)
            fonts = page.evaluate(JS_FONTS)
            not_loaded = [f["family"] for f in fonts if f["declared"] and not f["loaded"]]
            problems = {}
            if a["horizontalOverflow"]:
                problems["overflow"] = {"scrollWidth": a["scrollWidth"], "innerWidth": a["innerWidth"], "elementos": a["offenders"]}
            if a["consoleErrors"]:
                problems["console"] = a["consoleErrors"]
            if a["failedRequests"]:
                problems["rede"] = a["failedRequests"]
            if broken or a["brokenImages"]:
                problems["imagens"] = sorted(set(broken) | set(a["brokenImages"]))
            if a["fontsFailed"] or not_loaded:
                problems["fontes"] = a["fontsFailed"] + not_loaded
            if a["tinyTextNodes"]:
                rep.warn(f"{name} {w}px: {a['tinyTextNodes']} trecho(s) de texto abaixo de 12px")
            rep.check(f"{name} {w}x{h}: sem overflow, console, 4xx/5xx, imagens e fontes ok", not problems, problems)
            page.context.close()


def header_bottom(page):
    return page.evaluate(JS_HEADER_BOTTOM)


def wait_settle(page, timeout=4500):
    last, stable, waited = None, 0, 0
    while waited < timeout:
        y = page.evaluate("window.scrollY")
        stable = stable + 100 if y == last else 0
        if stable >= 500:
            break
        last = y
        page.wait_for_timeout(100)
        waited += 100


def measure_anchor(page, anchor):
    data = page.evaluate("""(id) => { const t = document.getElementById(id); if (!t) return null;
      const r = t.getBoundingClientRect();
      return {top: r.top, abs: r.top + scrollY, y: scrollY, max: document.documentElement.scrollHeight - innerHeight}; }""", anchor)
    if data is None:
        return False, {"erro": "alvo não existe"}
    hb = header_bottom(page)
    at_bottom = data["y"] >= data["max"] - 2
    at_top_target = data["abs"] <= hb + 2 and data["y"] <= 2
    ok = at_top_target or (data["top"] >= hb - 2 and (data["top"] <= hb + 80 or at_bottom))
    return ok, {"alvo_top": round(data["top"]), "header": round(hb), "scrollY": round(data["y"]), "fim_da_pagina": at_bottom}


def anchors_stage(rep, browser, urls, size_list):
    for name, url in urls:
        probe = open_page(browser, url, 1440, 900)
        hrefs = probe.evaluate("""() => [...new Set([...document.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href')))]
          .filter(h => h.length > 1 && document.getElementById(decodeURIComponent(h.slice(1))))""")
        missing = probe.evaluate("""() => [...new Set([...document.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href')))]
          .filter(h => h.length > 1 && !document.getElementById(decodeURIComponent(h.slice(1))))""")
        probe.context.close()
        rep.check(f"{name}: âncoras apontam para ids existentes", not missing, missing)
        bad, done = [], 0
        for w, h in size_list:
            for href in hrefs:
                anchor = href[1:]
                for mode in ("clique", "fragmento"):
                    page = open_page(browser, url + (href if mode == "fragmento" else ""), w, h)
                    if mode == "clique":
                        clicked = click_link(page, href)
                        if not clicked:
                            rep.warn(f"{name} {w}px: {href} não tem link visível neste tamanho de tela (só o fragmento direto foi testado)")
                            page.context.close()
                            continue
                    else:
                        page.wait_for_timeout(900)
                    wait_settle(page)
                    # A página avisa quando terminou de conferir a posição (<html data-anchor="done">).
                    # Sem esse aviso (JS próprio do projeto), vale a espera fixa.
                    try:
                        page.wait_for_function("document.documentElement.dataset.anchor === 'done'", timeout=6000)
                        page.wait_for_timeout(350)
                    except Exception:  # noqa: BLE001 - página sem o aviso: segue com a espera fixa
                        page.wait_for_timeout(1200)
                    wait_settle(page)
                    ok, info = measure_anchor(page, anchor)
                    done += 1
                    if not ok:
                        bad.append(f"{w}px {mode} {href}: {info}")
                    page.context.close()
        rep.check(f"{name}: {done} testes de âncora por posição medida (abaixo do header)", not bad, bad)


def click_link(page, href):
    links = page.locator(f'a[href="{href}"]')
    for i in range(links.count()):
        link = links.nth(i)
        if link.is_visible():
            try:
                link.click(timeout=3000)
            except Exception:  # noqa: BLE001 - fora da tela (ex.: link de pular conteúdo): usa o teclado
                link.focus()
                page.keyboard.press("Enter")
            return True
    for i in range(links.count()):
        link = links.nth(i)
        opened = link.evaluate("""a => { const d = a.closest('details'); if (!d) return false;
          const s = d.querySelector('summary'); if (s) s.click(); return true; }""")
        if opened:
            page.wait_for_timeout(200)
            if link.is_visible():
                link.click()
                return True
    return False


def nojs_stage(rep, browser, urls, out):
    for name, url in urls:
        for w, h in ((1440, 900), (390, 844)):
            context = browser.new_context(viewport={"width": w, "height": h}, java_script_enabled=False, locale="pt-BR",
                                          is_mobile=w < 600, has_touch=w < 600)
            page = context.new_page()
            page.goto(url, wait_until="load")
            page.wait_for_timeout(400)
            shot = out / f"{Path(name).stem}-sem-js-{w}.png"
            page.screenshot(path=str(shot))
            rep.data["shots"].append(str(shot))
            page.evaluate("document.querySelectorAll('main > *').forEach(s => s.style.contentVisibility = 'visible')")
            data = page.evaluate(JS_NOJS_VISIBLE)
            ok = not data["hidden"] and data["textLength"] > 200 and data["styled"] > 0
            rep.check(f"{name} {w}px sem JavaScript: conteúdo essencial visível e CSS carregado (noscript)", ok,
                      {"escondidos": data["hidden"][:12], "texto": data["textLength"], "folhas": data["styled"]})
            context.close()


def reduced_stage(rep, browser, urls):
    for name, url in urls:
        for w, h in ((1440, 900), (390, 844)):
            page = open_page(browser, url, w, h, reduced_motion=True)
            running = {}

            def look():
                for a in page.evaluate(JS_ANIMS, None):
                    if a["state"] == "running" and (a["infinite"] or a["duration"] > 50):
                        running[a["name"]] = a["duration"]
            scroll_through(page, look)
            rep.check(f"{name} {w}px movimento reduzido: nenhuma animação rodando", not running, sorted(running))
            page.context.close()


def motion_stage(rep, browser, urls):
    for name, url in urls:
        page = open_page(browser, url, 1440, 900)
        count = page.evaluate("document.querySelectorAll('.motion-scene').length")
        if not count:
            loops = [a for a in page.evaluate(JS_ANIMS, None) if a["infinite"]]
            if loops:
                rep.warn(f"{name}: há animações contínuas sem .motion-scene; confira pausa fora da viewport à mão")
            else:
                rep.warn(f"{name}: nenhum componente com movimento (.motion-scene); teste de movimento pulado")
            page.context.close()
            continue
        moving, problems, scenes = 0, [], []
        for i in range(count):
            page.evaluate("""(i) => { document.documentElement.style.scrollBehavior = 'auto';
              const s = [...document.querySelectorAll('.motion-scene')][i]; const r = s.getBoundingClientRect();
              window.scrollTo(0, scrollY + r.top - Math.max(0, (innerHeight - r.height) / 2)); }""", i)
            page.wait_for_timeout(900)
            first = page.evaluate(JS_ANIMS, i)
            page.wait_for_timeout(450)
            second = page.evaluate(JS_ANIMS, i)
            loops = [a for a in first if a["infinite"]]
            running = [a for a in loops if a["state"] == "running"]
            changed = any(a["sig"] != b["sig"] for a, b in zip(first, second) if a["infinite"] and a["state"] == "running")
            scenes.append({"cena": i, "contínuas": len(loops), "rodando": len(running), "mudou_entre_quadros": changed})
            if loops and not running:
                problems.append(f"cena {i}: animação contínua parada mesmo visível")
            if running and changed:
                moving += 1
        if not any(sc["contínuas"] for sc in scenes):
            rep.warn(f"{name}: só há entradas (nenhuma animação contínua); pausa fora da viewport não se aplica")
            page.context.close()
            continue
        rep.check(f"{name} 1440px: movimento real no desktop (transform/opacity mudam entre dois quadros)", moving > 0 and not problems,
                  {"cenas": scenes, "problemas": problems})
        # Pausa fora da viewport: vai para o fim e confere a primeira cena; depois para o topo e confere a última.
        offscreen = []
        for scroll, index in (("document.documentElement.scrollHeight", 0), ("0", count - 1)):
            page.evaluate(f"window.scrollTo(0, {scroll})")
            page.wait_for_timeout(500)
            visible = page.evaluate("""(i) => { const r = [...document.querySelectorAll('.motion-scene')][i].getBoundingClientRect();
              return r.bottom > 0 && r.top < innerHeight; }""", index)
            if visible:
                continue
            # Conteúdo pulado por content-visibility:auto não é renderizado, então não custa CPU.
            still = [a["name"] for a in page.evaluate(JS_ANIMS, index) if a["infinite"] and a["state"] == "running" and not a["skipped"]]
            if still:
                offscreen.append(f"cena {index}: {still}")
        rep.check(f"{name}: animações contínuas pausam fora da viewport", not offscreen, offscreen)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(400)
        page.evaluate("""() => { Object.defineProperty(document, 'hidden', {configurable: true, get: () => true});
          Object.defineProperty(document, 'visibilityState', {configurable: true, get: () => 'hidden'});
          document.dispatchEvent(new Event('visibilitychange')); }""")
        page.wait_for_timeout(400)
        still = [a["name"] for a in page.evaluate(JS_ANIMS, None) if a["infinite"] and a["state"] == "running"]
        rep.check(f"{name}: animações contínuas pausam com a aba oculta", not still, still)
        page.context.close()


def cls_stage(rep, browser, urls, max_cls):
    for name, url in urls:
        for w, h, slow in ((1440, 900, False), (390, 844, True)):
            page = new_page(browser, w, h, mobile=w < 600)
            page.add_init_script(CLS_INIT)
            if slow:
                cdp = page.context.new_cdp_session(page)
                cdp.send("Network.enable")
                cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150,
                                                              "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8})
                cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
            page.goto(url, wait_until="load", timeout=90000)
            page.wait_for_timeout(3000)
            cls = page.evaluate("window.__cls")
            shifts = page.evaluate("window.__shifts")
            label = "celular com 4G lento e CPU 4x" if slow else "desktop"
            rep.check(f"{name} CLS do carregamento ({label}) ≤ {max_cls}", cls <= max_cls, {"cls": round(cls, 4), "deslocamentos": shifts[:6]})
            page.context.close()


# ---------------------------------------------------------------- principal
def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    kind, value, root = pc.resolve_target(args.target)
    out = Path(args.out) if args.out else (root / "qa" if root else Path("qa-report"))
    if out.exists():
        if any(out.iterdir()) and not (out / "report.json").is_file():
            paths.die(f"{out} já tem arquivos que não são de um QA anterior; escolha outra pasta com --out")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    rep = Report(out, str(value))
    print(f"[pycode] QA de {value}", flush=True)
    with contextlib.ExitStack() as stack:
        if kind == "url":
            urls = [(re.sub(r"[^\w.-]+", "_", value.split("//", 1)[1])[:60] or "pagina", value)]
            tmp = Path(stack.enter_context(tempfile.TemporaryDirectory()))
            import urllib.request
            with urllib.request.urlopen(urllib.request.Request(value, headers={"User-Agent": "pycode-qa"}), timeout=30) as r:
                (tmp / "pagina.html").write_bytes(r.read())
            pages = [(urls[0][0], tmp / "pagina.html")]
        else:
            base = stack.enter_context(serve(value))
            files = pc.html_pages(value)
            pages = [(f.relative_to(value).as_posix(), f) for f in files]
            urls = [(name, f"{base}/{name}") for name, _ in pages]
        static_stage(rep, pages, args.lenient_text)
        browser = stack.enter_context(chromium())
        content_urls = [(n, u) for n, u in urls if not n.endswith("404.html")]
        stages = [("contraste", lambda: contrast_stage_url(rep, browser, urls[0][1])),
                  ("matriz de viewports", lambda: matrix_stage(rep, browser, urls, sizes(args.sizes), out))]
        if not args.skip_anchors:
            stages.append(("âncoras", lambda: anchors_stage(rep, browser, content_urls, sizes(args.anchor_sizes))))
        stages += [("sem JavaScript", lambda: nojs_stage(rep, browser, content_urls, out)),
                   ("movimento reduzido", lambda: reduced_stage(rep, browser, content_urls))]
        if not args.skip_motion:
            stages.append(("movimento", lambda: motion_stage(rep, browser, content_urls)))
        stages.append(("CLS", lambda: cls_stage(rep, browser, content_urls, args.max_cls)))
        for label, run in stages:
            try:
                run()
            except Exception as exc:  # noqa: BLE001 - etapa quebrada reprova, não some do relatório
                rep.check(f"etapa {label} terminou com erro", False, f"{type(exc).__name__}: {exc}"[:600])
    shots = [s for s in rep.data["shots"] if Path(s).exists()]
    if shots:
        from pycode_tools.images import contact_sheet
        sheet = contact_sheet(shots, out / "folha-de-contato.jpg", cols=4, thumb_width=360)
        rep.data["contact_sheet"] = str(sheet)
    rep.data["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    rep.data["ok"] = not rep.failed
    rep.save()
    total = len(rep.data["checks"])
    print(f"\n{total - len(rep.failed)}/{total} verificações passaram · {len(rep.data['warnings'])} aviso(s)")
    for w in rep.data["warnings"]:
        print(f"  [aviso] {w}")
    print(f"relatório: {out / 'report.json'}\ncapturas: {out}  (revise as imagens antes de entregar)")
    return 1 if rep.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
