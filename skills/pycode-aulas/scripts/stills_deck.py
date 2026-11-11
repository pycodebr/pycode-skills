"""pycode deck stills: PNG 1920×1080 de cada cena no estado final (?still), mais os textos visíveis de cada cena
(stills/stills.json), usados pela exportação em PDF e PPTX."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from pycode_tools import paths
from pycode_tools.browser import chromium
from pycode_tools.images import contact_sheet
from pycode_tools.server import serve
from deck_common import find_project, load_project, open_deck, site_dir

# caixas de texto visíveis (uma por linha renderizada), em px do palco, para a camada de texto do PDF
TEXT_BOXES_JS = r"""
() => {
  const s = document.querySelector('.slide.active');
  const sr = s.getBoundingClientRect(), k = 1920 / sr.width;
  const visible = el => { for (let n = el; n && n !== document.body; n = n.parentElement) { const cs = getComputedStyle(n); if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity < .05) return false; } return true; };
  const boxes = [], lines = [];
  const walker = document.createTreeWalker(s, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const t = walker.currentNode, raw = t.nodeValue;
    if (!raw.trim()) continue;
    const el = t.parentElement;
    if (!el || el.closest('.rd-only, .sr-only, [aria-hidden="true"]') || !visible(el)) continue;
    const range = document.createRange();
    range.selectNodeContents(t);
    const rects = [...range.getClientRects()].filter(r => r.width > 1 && r.height > 1);
    if (!rects.length) continue;
    const words = raw.replace(/\s+/g, ' ').trim().split(' ');
    const total = rects.reduce((a, r) => a + r.width, 0);
    let w = 0;
    rects.forEach((r, i) => {
      const take = i === rects.length - 1 ? words.length - w : Math.max(1, Math.round(words.length * r.width / total));
      const part = words.slice(w, w + take).join(' ');
      w += take;
      if (part) boxes.push({ text: part, x: (r.left - sr.left) * k, y: (r.top - sr.top) * k, w: r.width * k, h: r.height * k });
    });
    lines.push(raw.replace(/\s+/g, ' ').trim());
  }
  return { id: s.dataset.id, title: s.dataset.title, boxes, text: lines.join(' ') };
}
"""


def capture(root: Path, out: Path | None = None, quiet: bool = False) -> list[dict]:
    site = site_dir(root)
    _, content = load_project(root)
    out = out or root / "stills"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    notes = {s["id"]: s.get("notes", "") for s in content["scenes"]}
    rows = []
    with serve(site) as base, chromium() as browser:
        page = open_deck(browser, base, 1920, 1080, query="still")
        count = page.evaluate("presentation.count")
        for i in range(count):
            page.evaluate(f"presentation.show({i})")
            page.wait_for_timeout(500)
            info = page.evaluate(TEXT_BOXES_JS)
            png = out / f"{i + 1:02d}-{info['id']}.png"
            page.screenshot(path=str(png))
            info.update({"n": i + 1, "file": png.name, "notes": notes.get(info["id"], "")})
            rows.append(info)
            if not quiet:
                print(png)
        problems = page.pycode_console + page.pycode_external
        page.context.close()
    if problems:
        paths.die(f"erros durante as capturas: {problems[:3]}")
    (out / "stills.json").write_text(json.dumps({"title": content["meta"].get("title", ""), "scenes": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    contact_sheet(sorted(out.glob("*.png")), out / "folha-de-contato.jpg", cols=3, thumb_width=640)
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pycode deck stills", description="Gera um PNG 1920×1080 de cada cena no estado final e a folha de contato.")
    ap.add_argument("pasta", nargs="?", help="pasta do projeto (padrão: a atual)")
    ap.add_argument("--out", help="pasta de saída (padrão: <projeto>/stills)")
    ap.add_argument("--no-build", action="store_true", help="usa o site/ atual sem rodar o build antes")
    args = ap.parse_args(argv)
    root = find_project(args.pasta)
    if not args.no_build:
        from build_deck import build
        build(root, quiet=True)
    rows = capture(root, Path(args.out).resolve() if args.out else None)
    out = Path(args.out).resolve() if args.out else root / "stills"
    print(f"{len(rows)} captura(s) em {out}  ·  folha de contato: {out / 'folha-de-contato.jpg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
