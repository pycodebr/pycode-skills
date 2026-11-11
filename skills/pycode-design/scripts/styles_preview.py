"""pycode styles preview: monta a galeria navegável dos estilos, com fontes locais e capturas.

Estrutura gerada em --out (padrão ./galeria-estilos):
  index.html                     galeria com todos os estilos
  <slug>/preview.html            prévia do estilo (lê tokens.css e fonts/fonts.css por caminho relativo)
  <slug>/tokens.css, DESIGN.md, style.json, fonts/
  capturas/<slug>-1440.png, <slug>-390.png
  capturas/folha-de-contato.jpg
"""
import argparse
import html
import json
from pathlib import Path

import design_lib as D

GALLERY_CSS = """
:root{--ink:#16181d;--paper:#f3f1ec;--line:#d8d4cb;--muted:#5d5a54;--hi:#0a58ca}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 system-ui,-apple-system,'Segoe UI',sans-serif}
header{padding:clamp(28px,6vw,72px) clamp(20px,5vw,64px) 24px;max-width:1360px;margin:0 auto}
h1{font-size:clamp(34px,5vw,64px);line-height:1.02;letter-spacing:-.04em;margin:0 0 12px;font-weight:650}
header p{max-width:62ch;color:var(--muted);margin:0}
main{max-width:1360px;margin:0 auto;padding:12px clamp(20px,5vw,64px) 80px;display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,400px),1fr));gap:28px 24px}
article{display:flex;flex-direction:column;gap:10px}
.shot{display:block;aspect-ratio:16/10;overflow:hidden;border:1px solid var(--line);background:#ddd;border-radius:6px}
.shot img{width:100%;height:100%;object-fit:cover;object-position:top;display:block;transition:transform .5s cubic-bezier(.2,.7,.2,1)}
.shot:hover img,.shot:focus-visible img{transform:scale(1.03)}
.shot:focus-visible{outline:3px solid var(--hi);outline-offset:3px}
h2{margin:4px 0 0;font-size:22px;letter-spacing:-.02em;font-weight:650}
h2 small{font:500 13px/1 ui-monospace,Menlo,monospace;color:var(--muted);margin-left:8px;letter-spacing:0}
article p{margin:0;color:var(--muted);font-size:15px}
.meta{display:flex;flex-wrap:wrap;gap:6px;font:500 13px/1 ui-monospace,Menlo,monospace}
.meta span{border:1px solid var(--line);padding:6px 8px;border-radius:4px}
.links{display:flex;gap:16px;font-size:15px}.links a{color:var(--hi)}
.sw{display:flex;height:10px;border-radius:3px;overflow:hidden}.sw i{flex:1}
@media (prefers-reduced-motion:reduce){.shot img{transition:none}}
"""


def gallery_html(entries, with_shots):
    cards = []
    for s in entries:
        slug = html.escape(s["slug"])
        tokens = D.load_tokens(s["dir"])
        swatch = "".join(f'<i style="background:{html.escape(tokens.get(k, "transparent"))}"></i>'
                         for k in ("--bg", "--surface", "--text", "--accent", "--accent-2", "--paper"))
        img = (f'<img src="capturas/{slug}-1440.png" alt="Prévia do estilo {html.escape(s.get("name", slug))}" loading="lazy" width="1440" height="900">'
               if with_shots else "")
        cards.append(f"""<article>
  <a class="shot" href="{slug}/preview.html">{img}</a>
  <div class="sw" aria-hidden="true">{swatch}</div>
  <h2>{html.escape(s.get('name', slug))}<small>{slug}</small></h2>
  <p>{html.escape(s.get('summary', ''))}</p>
  <div class="meta"><span>{html.escape(s.get('mode', ''))}</span>{''.join(f'<span>{html.escape(f)}</span>' for f in s.get('best_for', []))}</div>
  <div class="links"><a href="{slug}/preview.html">Abrir a prévia</a><a href="{slug}/DESIGN.md">DESIGN.md</a><a href="{slug}/tokens.css">tokens.css</a></div>
</article>""")
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Galeria de estilos · pycode-design</title><style>{GALLERY_CSS}</style></head>
<body><header><h1>Galeria de estilos</h1>
<p>{len(entries)} estilos do pycode-design. Cada prévia mostra paleta, tipografia, objetos animados, um trecho de página, um slide 16:9 e um slide de carrossel 4:5. Use o slug com <code>--style</code> nos comandos de aulas, páginas e carrosséis.</p></header>
<main>{''.join(cards)}</main></body></html>
"""


def capture(out, entries, sizes):
    from pycode_tools.browser import chromium, new_page
    from pycode_tools.server import serve

    shots = out / "capturas"
    shots.mkdir(exist_ok=True)
    files = []
    with serve(out) as url, chromium() as browser:
        for s in entries:
            for w, h in sizes:
                page = new_page(browser, w, h, mobile=w < 600)
                page.goto(f"{url}/{s['slug']}/preview.html", wait_until="load")
                page.evaluate("document.fonts.ready")
                page.wait_for_timeout(2800)
                file = shots / f"{s['slug']}-{w}.png"
                page.screenshot(path=str(file))
                files.append(file)
                page.context.close()
            print(f"  capturas de {s['slug']} prontas")
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode styles preview", description="Monta a galeria dos estilos com fontes locais e capturas.")
    ap.add_argument("--out", default="galeria-estilos", help="pasta de saída (padrão: ./galeria-estilos)")
    ap.add_argument("--style", action="append", help="só este estilo (repita para vários)")
    ap.add_argument("--no-shots", action="store_true", help="não gera capturas (mais rápido)")
    ap.add_argument("--full", action="store_true", help="capturas da página inteira em vez da primeira dobra")
    args = ap.parse_args(argv)
    entries = [D.find_style(s) for s in args.style] if args.style else D.all_styles()
    entries = [s for s in entries if (Path(s["dir"]) / "preview.html").is_file()]
    if not entries:
        D.paths.die("nenhum estilo com preview.html para mostrar")
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    for s in entries:
        D.build_style_dir(s, out / s["slug"])
    sheet = None
    if not args.no_shots:
        print("Gerando capturas (1440 e 390)...")
        files = capture(out, entries, [(1440, 900), (390, 844)])
        from pycode_tools.images import contact_sheet
        wide = [f for f in files if f.name.endswith("-1440.png")]
        sheet = contact_sheet(wide, out / "capturas" / "folha-de-contato.jpg", cols=3, thumb_width=560)
    (out / "index.html").write_text(gallery_html(entries, not args.no_shots), encoding="utf-8")
    (out / "estilos.json").write_text(json.dumps([{k: v for k, v in s.items() if k != "dir"} for s in entries], indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Galeria: {out / 'index.html'}")
    if sheet:
        print(f"Folha de contato: {sheet}")
    print(f"Para abrir no navegador: pycode serve {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
