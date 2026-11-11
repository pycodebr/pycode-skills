"""pycode deck qa: testa o deck no navegador e sai com erro se qualquer verificação falhar.

Para cada cena (ou só as de --only):
- ?still em 1920×1080: sem erro de console, nada fora do palco, nenhum texto abaixo de 16 px, orçamento de palavras,
  imagens carregadas, captura do estado final;
- demonstração acelerada: toca, troca a seleção e termina em `home` com a chave inicial, sem continuar sozinha;
- clique assume (estado manual), outro item muda a seleção, a seleção fica estável e R devolve o automático;
Para o deck: navegação por teclado (setas, PageUp/PageDown, espaço, Home/End), deep link por número e por id, posição
salva, Tab + Enter num item clicável, menu (?) e índice (O), movimento reduzido, modo leitura em 390 px sem rolagem
lateral, celular em retrato (palco no topo + resumo) e em paisagem (palco inteiro), nenhuma requisição externa.
Gera qa/qa.json, capturas em qa/shots/ e a folha de contato qa/folha-de-contato.jpg.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

from pycode_tools import paths
from pycode_tools.browser import chromium
from pycode_tools.images import contact_sheet
from pycode_tools.server import serve
from deck_common import find_project, load_project, open_deck, site_dir

STILL_JS = r"""
() => {
  const s = document.querySelector('.slide.active');
  const sr = s.getBoundingClientRect();
  const visible = el => {
    for (let n = el; n && n !== document.body; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity < .05) return false;
    }
    return true;
  };
  const outside = [];
  s.querySelectorAll('*').forEach(el => {
    if (el.closest('[data-clip]') || (el.closest('svg') && el.tagName.toLowerCase() !== 'svg')) return;
    const b = el.getBoundingClientRect();
    if (!b.width || !b.height) return;
    if (b.right > sr.right + 3 || b.bottom > sr.bottom + 3 || b.left < sr.left - 3 || b.top < sr.top - 3) {
      if (!visible(el)) return;
      outside.push({ el: el.tagName.toLowerCase() + '.' + String(el.className.baseVal ?? el.className).trim().split(/\s+/).join('.'),
        box: [b.left - sr.left, b.top - sr.top, b.right - sr.left, b.bottom - sr.top].map(Math.round) });
    }
  });
  // textos visíveis agrupados por bloco: até 3 palavras é rótulo; acima disso entra no orçamento
  const groups = new Map(), tiny = [], leaves = [];
  const walker = document.createTreeWalker(s, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const t = walker.currentNode, txt = t.nodeValue.replace(/\s+/g, ' ').trim();
    if (!txt) continue;
    const el = t.parentElement;
    if (!el || el.closest('.rd-only, .sr-only, [aria-hidden="true"]') || !visible(el)) continue;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (fs < 16 && /[\p{L}\p{N}]/u.test(txt)) tiny.push({ text: txt.slice(0, 40), fs });
    const key = el.closest('.slide-title') || el.closest('p, h2, h3, li, blockquote, pre, .tip-in') || el;
    groups.set(key, (groups.get(key) || '') + ' ' + txt);
    leaves.push({ text: txt.slice(0, 40), box: [r.left, r.top, r.right, r.bottom], el });
  }
  const words = t => (t.match(/[\p{L}\p{N}]+(?:[-'][\p{L}\p{N}]+)*/gu) || []).length;
  let budget = 0, labels = 0;
  const counted = [];
  groups.forEach((txt, el) => {
    const n = words(txt);
    if (n > 3 || el.classList.contains('slide-title')) { budget += n; counted.push(txt.trim().slice(0, 60)); } else labels += n;
  });
  // textos que se sobrepõem (aviso para a revisão por visão)
  const overlaps = [];
  for (let i = 0; i < leaves.length; i++) for (let j = i + 1; j < leaves.length; j++) {
    const a = leaves[i], b = leaves[j];
    if (a.el.contains(b.el) || b.el.contains(a.el) || a.el.closest('.tip, pre') || b.el.closest('.tip, pre')) continue;
    const w = Math.min(a.box[2], b.box[2]) - Math.max(a.box[0], b.box[0]), h = Math.min(a.box[3], b.box[3]) - Math.max(a.box[1], b.box[1]);
    if (w > 4 && h > 4) {
      const area = Math.min((a.box[2] - a.box[0]) * (a.box[3] - a.box[1]), (b.box[2] - b.box[0]) * (b.box[3] - b.box[1]));
      if (w * h > area * .25) overlaps.push([a.text, b.text]);
    }
  }
  const fills = [...s.querySelectorAll('.fill')].map(f => f.scrollHeight - f.clientHeight).filter(v => v > 2);
  const broken = [...s.querySelectorAll('img')].filter(i => !i.complete || !i.naturalWidth).map(i => i.getAttribute('src'));
  const noLabel = [...s.querySelectorAll('[data-pick][tabindex]')].filter(el => !(el.getAttribute('aria-label') || '').trim()).length;
  const zeroPicks = [...s.querySelectorAll('[data-pick][tabindex]')].filter(el => { const r = el.getBoundingClientRect(); return r.width < 4 || r.height < 4; }).length;
  return { id: s.dataset.id, outside: outside.slice(0, 8), outsideCount: outside.length, budgetWords: budget, labelWords: labels,
    counted, tiny: tiny.slice(0, 6), overlaps: overlaps.slice(0, 6), fills, broken, picks: s.querySelectorAll('[data-pick]').length, noLabel, zeroPicks };
}
"""
PICK_POINTS_JS = r"""
() => {
  const s = document.querySelector('.slide.active');
  const els = [...s.querySelectorAll('[data-pick]')];
  const out = [];
  els.forEach((el, i) => {
    for (const c of [el, ...el.querySelectorAll('*')]) {
      for (const r of c.getClientRects()) {
        if (r.width < 6 || r.height < 6) continue;
        const x = r.left + r.width / 2, y = r.top + r.height / 2;
        if (x < 0 || y < 0 || x > innerWidth || y > innerHeight) continue;
        const hit = document.elementFromPoint(x, y);
        if (hit && hit.closest('[data-pick]') === el) { out.push({ i, x, y }); return; }
      }
    }
  });
  return out;
}
"""
PHONE_JS = r"""
() => {
  const f = document.querySelector('#frame').getBoundingClientRect();
  return { reading: document.body.classList.contains('reading'), portrait: document.body.classList.contains('portrait'),
    fw: Math.round(f.width), fh: Math.round(f.height), fr: Math.round(f.right), fb: Math.round(f.bottom), vw: innerWidth, vh: innerHeight,
    hscroll: document.documentElement.scrollWidth - innerWidth, title: document.querySelector('#mobile-info .mi-title').textContent };
}
"""


class QA:
    def __init__(self, out: Path):
        self.out = out
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.report: dict = {"scenes": {}, "deck": {}}

    def check(self, ok: bool, msg: str) -> bool:
        if not ok:
            self.failures.append(msg)
        return ok

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def state(page) -> dict:
    return page.evaluate("presentation.state()")


def wait_home(page, timeout: float) -> tuple[dict, set]:
    seen, t0 = set(), time.time()
    while time.time() - t0 < timeout:
        st = state(page)
        if st["key"] is not None:
            seen.add(st["key"])
        if st["demo"] == "home":
            return st, seen
        page.wait_for_timeout(100)
    return state(page), seen


def test_still(qa: QA, page, idx: int, sid: str, budget: int, shots: Path) -> None:
    page.evaluate(f"presentation.show({idx})")
    page.wait_for_timeout(500)
    res = page.evaluate(STILL_JS)
    row = qa.report["scenes"].setdefault(sid, {})
    row["still"] = {k: v for k, v in res.items() if k != "counted"}
    row["still"]["counted"] = res["counted"]
    qa.check(res["outsideCount"] == 0, f"{sid}: {res['outsideCount']} elemento(s) fora do palco, ex.: {res['outside'][:2]}")
    qa.check(not res["fills"], f"{sid}: conteúdo transbordando a área da cena ({res['fills']} px)")
    qa.check(not res["tiny"], f"{sid}: texto abaixo de 16 px no palco: {res['tiny'][:3]}")
    qa.check(not res["broken"], f"{sid}: imagens quebradas: {res['broken']}")
    qa.check(res["budgetWords"] <= budget, f"{sid}: {res['budgetWords']} palavras no palco (orçamento {budget}); corte para o modo leitura ou declare 'budget' na cena")
    qa.check(res["picks"] > 0, f"{sid}: nenhum item clicável (ctx.pick)")
    qa.check(res["noLabel"] == 0, f"{sid}: {res['noLabel']} item(ns) clicável(is) sem aria-label")
    qa.check(res["zeroPicks"] == 0, f"{sid}: {res['zeroPicks']} item(ns) clicável(is) sem área (o foco do teclado fica invisível; dê largura e altura ao elemento)")
    for a, b in res["overlaps"]:
        qa.warn(f"{sid}: textos sobrepostos? {a!r} × {b!r} (confira na captura)")
    page.screenshot(path=str(shots / f"still-{idx + 1:02d}-{sid}.png"))


def test_demo(qa: QA, page, idx: int, sid: str, shots: Path, fast: bool) -> None:
    row = qa.report["scenes"].setdefault(sid, {})
    page.evaluate(f"presentation.show({idx})")
    page.wait_for_timeout(60)
    page.evaluate("presentation.speed(10)")
    st0 = state(page)
    st, seen = wait_home(page, (st0["intro"] + st0["loop"]) / 10 + 8)
    page.wait_for_timeout(500)
    stable = state(page)
    demo = {"final": st["demo"], "key": st["key"], "startKey": st["startKey"], "keysSeen": len(seen),
            "stableKey": stable["key"] == st["key"] and stable["demo"] == "home"}
    row["demo"] = demo
    if st0["loop"]:
        qa.check(st["demo"] == "home", f"{sid}: a demonstração não terminou em home (estado {st['demo']})")
        qa.check(st["key"] == st["startKey"], f"{sid}: a demonstração não voltou ao estado inicial (chave {st['key']} × {st['startKey']})")
        qa.check(len(seen) >= 2, f"{sid}: a demonstração não trocou a seleção (chaves vistas: {sorted(seen)})")
        qa.check(demo["stableKey"], f"{sid}: a cena continuou mudando depois de voltar ao início")
    page.evaluate("presentation.speed(1)")
    # R recomeça; um clique durante a demonstração assume
    page.keyboard.press("r")
    page.wait_for_timeout(150)
    replay = state(page)["demo"]
    qa.check(replay in ("intro", "demo"), f"{sid}: R não recomeçou a demonstração (estado {replay})")
    page.wait_for_timeout(900)
    points = page.evaluate(PICK_POINTS_JS)
    if not qa.check(bool(points), f"{sid}: nenhum item clicável alcançável pelo mouse (algo cobre os itens?)"):
        return
    page.mouse.click(points[0]["x"], points[0]["y"])
    page.wait_for_timeout(250)
    a = state(page)
    changed = False
    for p in points[1:6]:
        page.mouse.click(p["x"], p["y"])
        page.wait_for_timeout(250)
        b = state(page)
        if b["key"] != a["key"]:
            changed = True
            break
    if not changed and len(points) > 1:
        page.mouse.click(points[0]["x"], points[0]["y"])
        page.wait_for_timeout(250)
        changed = state(page)["key"] != a["key"]
    before = state(page)
    page.wait_for_timeout(600 if fast else 1800)
    after = state(page)
    click = {"manual": a["manual"] and a["demo"] == "manual", "changed": changed or len(points) == 1,
             "stable": before["key"] == after["key"] and after["demo"] == "manual", "sameScene": after["id"] == sid}
    row["click"] = click
    qa.check(click["manual"], f"{sid}: o clique não fez o apresentador assumir (estado {a['demo']})")
    qa.check(click["changed"], f"{sid}: clicar em outro item não mudou a seleção")
    qa.check(click["stable"], f"{sid}: depois do clique a cena mudou sozinha")
    qa.check(click["sameScene"], f"{sid}: o clique trocou de cena")
    page.screenshot(path=str(shots / f"click-{idx + 1:02d}-{sid}.png"))
    page.keyboard.press("r")
    page.wait_for_timeout(150)
    qa.check(state(page)["demo"] in ("intro", "demo"), f"{sid}: R não devolveu o automático depois do clique")


def test_keyboard(qa: QA, browser, base: str, ids: list[str]) -> None:
    page = open_deck(browser, base, 1920, 1080)
    n = len(ids)
    res = {}
    seq = [("ArrowRight", 1), ("PageDown", 2), ("ArrowLeft", 1), ("PageUp", 0), (" ", 1), ("End", n - 1), ("Home", 0)]
    for key, want in seq:
        page.keyboard.press(key)
        page.wait_for_timeout(120)
        got = page.evaluate("presentation.current")
        res[key] = got
        qa.check(got == min(want, n - 1), f"teclado: {key!r} levou à cena {got + 1}, esperado {min(want, n - 1) + 1}")
    page.keyboard.press("ArrowRight")
    page.wait_for_timeout(120)
    # edge: clique na borda direita do palco
    page.mouse.click(1900, 540)
    page.wait_for_timeout(150)
    qa.check(page.evaluate("presentation.current") == min(2, n - 1), "borda direita do palco não avançou a cena")
    # Tab + Enter num item clicável
    page.evaluate("presentation.show(0)")
    page.wait_for_timeout(200)
    focused = False
    for _ in range(40):
        page.keyboard.press("Tab")
        if page.evaluate("!!document.activeElement.closest('.slide.active [data-pick]')"):
            focused = True
            break
    qa.check(focused, "teclado: Tab não chega aos itens clicáveis da cena")
    if focused:
        page.keyboard.press("Enter")
        page.wait_for_timeout(150)
        qa.check(state(page)["demo"] == "manual", "teclado: Enter no item focado não fez o apresentador assumir")
    page.evaluate("document.activeElement.blur()")
    page.keyboard.press("?")
    page.wait_for_timeout(100)
    qa.check(page.evaluate("document.querySelector('#menu').open"), "tecla ? não abriu o menu de opções")
    page.keyboard.press("Escape")
    page.keyboard.press("o")
    page.wait_for_timeout(100)
    qa.check(page.evaluate("document.querySelector('#overview').open"), "tecla O não abriu o índice")
    page.keyboard.press("Escape")
    page.keyboard.press("b")
    qa.check(page.evaluate("document.body.classList.contains('blanked')"), "tecla B não escureceu a tela")
    page.keyboard.press("Escape")
    page.keyboard.press("m")
    page.wait_for_timeout(100)
    qa.check(not page.evaluate("presentation.motion"), "tecla M não pausou as animações")
    page.keyboard.press("m")
    page.keyboard.press("t")
    page.wait_for_timeout(1300)
    qa.check(page.evaluate("document.querySelector('#timer').textContent") != "00:00", "tecla T não iniciou o cronômetro")
    # deep link por número e por id; posição salva
    page.goto(base + "/index.html#3")
    page.wait_for_function("document.documentElement.dataset.ready === 'true'")
    qa.check(page.evaluate("presentation.current") == min(2, n - 1), "deep link #3 não abriu a terceira cena")
    target = ids[-2] if n > 1 else ids[0]
    page.goto(base + f"/index.html#{target}")
    page.wait_for_function("document.documentElement.dataset.ready === 'true'")
    page.wait_for_timeout(100)
    qa.check(page.evaluate("presentation.current") == ids.index(target), f"deep link #{target} não abriu a cena pelo id")
    page.goto(base + "/index.html")
    page.wait_for_function("document.documentElement.dataset.ready === 'true'")
    qa.check(page.evaluate("presentation.current") == ids.index(target), "a posição salva não foi restaurada ao reabrir sem hash")
    res["external"] = list(page.pycode_external)
    qa.report["deck"]["keyboard"] = res
    page.context.close()


def test_reduced(qa: QA, browser, base: str, ids: list[str]) -> None:
    page = open_deck(browser, base, 1920, 1080, reduced=True)
    for i in range(min(3, len(ids))):
        page.evaluate(f"presentation.show({i})")
        page.wait_for_timeout(150)
        st = state(page)
        qa.check(st["demo"] == "still", f"{ids[i]}: com movimento reduzido a cena não ficou no estado final (estado {st['demo']})")
    pts = page.evaluate(PICK_POINTS_JS)
    if pts:
        page.mouse.click(pts[0]["x"], pts[0]["y"])
        page.wait_for_timeout(100)
        qa.check(state(page)["demo"] == "manual", "com movimento reduzido, o clique nos itens não funcionou")
    qa.check(not page.pycode_console, f"erros de console com movimento reduzido: {page.pycode_console[:3]}")
    page.context.close()


def test_reading(qa: QA, browser, base: str, shots: Path, n: int) -> None:
    page = open_deck(browser, base, 390, 844, query="still&leitura", mobile=True)
    r = page.evaluate("""() => ({ reading: document.body.classList.contains('reading'), hscroll: document.documentElement.scrollWidth - innerWidth,
      sections: [...document.querySelectorAll('.slide')].filter(s => s.getBoundingClientRect().height > 40).length,
      tiny: [...document.querySelectorAll('.slide .rd-only li, .slide .apoio, .slide .slide-title')].filter(e => parseFloat(getComputedStyle(e).fontSize) < 12).length })""")
    qa.report["deck"]["reading"] = r
    qa.check(r["reading"], "?leitura não abriu o modo leitura")
    qa.check(r["hscroll"] <= 1, f"modo leitura em 390 px com rolagem lateral de {r['hscroll']} px")
    qa.check(r["sections"] == n, f"modo leitura mostra {r['sections']} de {n} cenas")
    qa.check(r["tiny"] == 0, "modo leitura com texto abaixo de 12 px")
    page.screenshot(path=str(shots / "leitura-390.png"), full_page=False)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    page.wait_for_timeout(200)
    page.screenshot(path=str(shots / "leitura-390-meio.png"))
    qa.check(not page.pycode_console, f"erros de console no modo leitura: {page.pycode_console[:3]}")
    page.context.close()


def test_phones(qa: QA, browser, base: str, ids: list[str], shots: Path, sample: list[int]) -> None:
    out = []
    for label, (w, h) in (("retrato", (390, 844)), ("paisagem", (844, 390))):
        page = open_deck(browser, base, w, h, query="still", mobile=True)
        for i in range(len(ids)):
            page.evaluate(f"presentation.show({i})")
            page.wait_for_timeout(120)
            r = page.evaluate(PHONE_JS)
            r.update({"modo": label, "id": ids[i]})
            out.append(r)
            ok = not r["reading"] and r["fw"] >= 300 and r["fr"] <= r["vw"] + 1 and r["hscroll"] <= 1
            if label == "retrato":
                ok = ok and r["portrait"] and bool(r["title"])
            else:
                ok = ok and not r["portrait"] and r["fh"] <= r["vh"] + 1
            qa.check(ok, f"{ids[i]}: celular em {label} sem o palco inteiro ou com rolagem lateral ({r})")
            if i in sample:
                page.screenshot(path=str(shots / f"celular-{label}-{i + 1:02d}-{ids[i]}.png"))
        qa.check(not page.pycode_console, f"erros de console no celular ({label}): {page.pycode_console[:3]}")
        page.context.close()
    qa.report["deck"]["phones"] = out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pycode deck qa", description="QA do deck no navegador (fail-closed). Gera qa/qa.json, capturas e a folha de contato.")
    ap.add_argument("pasta", nargs="?", help="pasta do projeto (padrão: a atual)")
    ap.add_argument("--only", help="ids das cenas, separados por vírgula (testa só essas no palco)")
    ap.add_argument("--fast", action="store_true", help="pula celular, leitura e movimento reduzido; espera menos depois do clique")
    ap.add_argument("--no-build", action="store_true", help="usa o site/ atual sem rodar o build antes")
    args = ap.parse_args(argv)
    t0 = time.time()
    root = find_project(args.pasta)
    if not args.no_build:
        from build_deck import build
        build(root, quiet=True)
    site = site_dir(root)
    _, content = load_project(root)
    scenes = content["scenes"]
    ids = [s["id"] for s in scenes]
    only = [x.strip() for x in (args.only or "").split(",") if x.strip()]
    unknown = [x for x in only if x not in ids]
    if unknown:
        paths.die(f"cenas desconhecidas em --only: {', '.join(unknown)}. Ids: {', '.join(ids)}")
    chosen = [i for i, s in enumerate(ids) if not only or s in only]
    out = root / "qa"
    shots = out / "shots"
    if shots.exists():
        shutil.rmtree(shots)
    shots.mkdir(parents=True)
    qa = QA(out)
    with serve(site) as base, chromium() as browser:
        page = open_deck(browser, base, 1920, 1080, query="still")
        for i in chosen:
            budget = int(scenes[i].get("budget") or 30)
            test_still(qa, page, i, ids[i], budget, shots)
        qa.check(not page.pycode_console, f"erros de console no ?still: {page.pycode_console[:4]}")
        qa.check(not page.pycode_external, f"requisições externas: {page.pycode_external[:4]}")
        qa.check(not page.pycode_failed, f"requisições que falharam: {page.pycode_failed[:4]}")
        page.context.close()
        page = open_deck(browser, base, 1920, 1080)
        for i in chosen:
            test_demo(qa, page, i, ids[i], shots, args.fast)
        qa.check(not page.pycode_console, f"erros de console durante as demonstrações: {page.pycode_console[:4]}")
        qa.check(not page.pycode_external, f"requisições externas: {page.pycode_external[:4]}")
        page.context.close()
        test_keyboard(qa, browser, base, ids)
        if not args.fast:
            test_reduced(qa, browser, base, ids)
            test_reading(qa, browser, base, shots, len(ids))
            sample = [i for i in chosen][:: max(1, len(chosen) // 4)][:4]
            test_phones(qa, browser, base, ids, shots, sample)
    stills = sorted(shots.glob("still-*.png"))
    if stills:
        contact_sheet(stills, out / "folha-de-contato.jpg", cols=3, thumb_width=640)
    elapsed = round(time.time() - t0, 1)
    qa.report.update({"ok": not qa.failures, "failures": qa.failures, "warnings": qa.warnings, "seconds": elapsed,
                      "scenesTested": [ids[i] for i in chosen], "mode": "fast" if args.fast else "completo"})
    (out / "qa.json").write_text(json.dumps(qa.report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for w in qa.warnings:
        print(f"[aviso] {w}")
    for f in qa.failures:
        print(f"[falha] {f}", file=sys.stderr)
    words = {sid: r.get("still", {}).get("budgetWords") for sid, r in qa.report["scenes"].items()}
    print(f"palavras no palco por cena: {words}")
    print(f"capturas: {shots}  ·  folha de contato: {out / 'folha-de-contato.jpg'}  ·  relatório: {out / 'qa.json'}")
    print(f"QA {'ok' if not qa.failures else 'REPROVADO'}: {len(chosen)} cena(s), {len(qa.failures)} falha(s), {len(qa.warnings)} aviso(s), {elapsed} s")
    return 0 if not qa.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
