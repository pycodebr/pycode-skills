"""Chromium (Playwright) para capturas e QA."""
import contextlib
import os

from .paths import die

AUDIT_JS = r"""
() => {
  const doc = document.documentElement;
  const vw = window.innerWidth;
  const offenders = [];
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const cs = getComputedStyle(el);
    if (cs.position === 'fixed' || cs.visibility === 'hidden' || cs.display === 'none') continue;
    if (el.closest('[data-clip]')) continue;
    if (r.right > vw + 1 || r.left < -1) {
      offenders.push((el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.className && el.className.baseVal === undefined ? '.' + String(el.className).trim().split(/\s+/).join('.') : '')).slice(0, 80));
      if (offenders.length >= 8) break;
    }
  }
  const images = [...document.images].filter(i => i.currentSrc && (!i.complete || !i.naturalWidth)).map(i => i.currentSrc);
  let small = 0;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const t = walker.currentNode;
    if (!t.nodeValue.trim()) continue;
    const p = t.parentElement;
    if (!p || !p.offsetParent) continue;
    if (parseFloat(getComputedStyle(p).fontSize) < 12) small++;
  }
  return {
    scrollWidth: doc.scrollWidth, innerWidth: vw,
    horizontalOverflow: doc.scrollWidth > vw + 1,
    offenders, brokenImages: images, tinyTextNodes: small,
    title: document.title, lang: doc.lang || '',
    fontsFailed: [...document.fonts].filter(f => f.status === 'error').map(f => f.family),
  };
}
"""


@contextlib.contextmanager
def chromium(headless=True, args=None):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        die("Playwright não está instalado no ambiente. Rode `pycode setup`.")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=headless, args=args or [])
        except Exception as exc:  # noqa: BLE001 - mensagem do Playwright já explica o que falta
            die(f"não consegui abrir o Chromium: {exc}\nRode `pycode setup` (ou `pycode doctor` para ver o que falta).")
        try:
            yield browser
        finally:
            browser.close()


def new_page(browser, width=1440, height=900, scale=1, reduced_motion=False, locale="pt-BR", mobile=False):
    context = browser.new_context(
        viewport={"width": width, "height": height}, device_scale_factor=scale, locale=locale,
        reduced_motion="reduce" if reduced_motion else "no-preference", is_mobile=mobile, has_touch=mobile,
    )
    page = context.new_page()
    page.pycode_console = []
    page.pycode_failed = []
    page.on("console", lambda m: page.pycode_console.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: page.pycode_console.append(str(e)))
    page.on("requestfailed", lambda r: page.pycode_failed.append(r.url))
    page.on("response", lambda r: page.pycode_failed.append(f"{r.status} {r.url}") if r.status >= 400 else None)
    return page


def audit(page):
    """Problemas básicos de uma página já carregada: overflow, imagens, fontes, console e rede."""
    data = page.evaluate(AUDIT_JS)
    data["consoleErrors"] = list(page.pycode_console)
    data["failedRequests"] = list(page.pycode_failed)
    return data


def chromium_path():
    """Caminho do Chromium do Playwright (usado por Lighthouse e Mermaid)."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            path = p.chromium.executable_path
        return path if os.path.exists(path) else ""
    except Exception:  # noqa: BLE001
        return ""
