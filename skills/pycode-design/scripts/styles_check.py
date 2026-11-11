"""pycode styles check: valida estilos de forma fail-closed (sai com 1 se qualquer item falhar).

Confere: style.json, contrato de tokens completo, prefixo dos extras, fontes no vendor, contraste,
DESIGN.md (frontmatter coerente com tokens.css e seções obrigatórias), texto PT-BR, keyframes só com
propriedades baratas e a prévia aberta no Chromium em 1440 e 390 (overflow, console, rede, fontes,
movimento reduzido).
"""
import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import design_lib as D
from pycode_tools import text as T
from pycode_tools import vendor
from pycode_tools.color import ratio

if not __debug__:
    raise RuntimeError("rode sem -O: as checagens não podem ser desligadas")

CONTRAST_PAIRS = [
    ("--text", "--bg", 4.5), ("--text", "--bg-2", 4.5), ("--text", "--surface", 4.5), ("--text", "--surface-2", 4.5),
    ("--muted", "--bg", 4.5), ("--muted", "--surface", 4.5), ("--accent-ink", "--accent", 4.5),
    ("--paper-ink", "--paper", 4.5), ("--accent", "--bg", 3.0),
]
DESIGN_SECTIONS = ["cores", "tipografia", "superfícies", "objetos", "movimento", "aplicação", "evit", "checklist"]
ANIMATABLE = {"transform", "opacity", "stroke-dashoffset", "stroke-dasharray", "offset-distance", "fill-opacity",
              "stroke-opacity", "visibility", "translate", "rotate", "scale"}
VIEWPORTS = [(1440, 900), (390, 844)]

PREVIEW_JS = r"""
async (families) => {
  await document.fonts.ready;
  const loaded = [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/["']/g, ''));
  const missing = families.filter(f => !loaded.includes(f));
  const deck = document.querySelector('[data-format="deck"]');
  const car = document.querySelector('[data-format="carousel"]');
  const ratioOf = el => el ? +(el.getBoundingClientRect().width / el.getBoundingClientRect().height).toFixed(3) : 0;
  const clipped = [];
  // texto cortado: o retângulo do texto passa da caixa de um elemento que recorta (overflow diferente de visible)
  for (const el of document.querySelectorAll('h1,h2,h3,p,li,figcaption,button,a')) {
    if (el.closest('[data-clip]') || !el.offsetParent || !el.textContent.trim()) continue;
    if (getComputedStyle(el).overflowX === 'visible') continue;
    const range = document.createRange();
    range.selectNodeContents(el);
    const t = range.getBoundingClientRect(), b = el.getBoundingClientRect();
    if (t.right > b.right + 2 || t.left < b.left - 2) clipped.push(el.tagName + ':' + el.textContent.trim().slice(0, 40));
  }
  return {missing, deckRatio: ratioOf(deck), carouselRatio: ratioOf(car),
          objects: document.querySelectorAll('[data-object]').length, clipped: clipped.slice(0, 6)};
}
"""


class Report:
    def __init__(self, slug):
        self.slug = slug
        self.fails = []
        self.notes = []

    def fail(self, msg):
        self.fails.append(msg)

    def note(self, msg):
        self.notes.append(msg)


def check_meta(style, rep):
    base = Path(style["dir"])
    if style.get("_error"):
        rep.fail(style["_error"])
        return
    for key, kind in D.META_KEYS.items():
        if not isinstance(style.get(key), kind) or (kind is str and not style.get(key).strip()):
            rep.fail(f"style.json: campo '{key}' ausente ou com tipo errado ({kind.__name__})")
    if style.get("slug") != base.name:
        rep.fail(f"style.json: slug '{style.get('slug')}' diferente da pasta '{base.name}'")
    if style.get("mode") not in ("dark", "light"):
        rep.fail("style.json: mode precisa ser 'dark' ou 'light'")
    bad = set(style.get("best_for") or []) - D.FORMATS
    if bad:
        rep.fail(f"style.json: best_for com valores desconhecidos {sorted(bad)} (use page, deck, carousel)")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(style.get("version", ""))):
        rep.fail("style.json: version precisa ser semver (ex.: 1.0.0)")
    for name in ("tokens.css", "DESIGN.md", "preview.html"):
        if not (base / name).is_file():
            rep.fail(f"falta {name}")


def check_fonts(style, rep):
    known = {f["id"]: f for f in vendor.manifest()["fonts"]}
    for fid in style.get("fonts") or []:
        font = known.get(fid)
        if font is None:
            rep.fail(f"fonte '{fid}' não existe no vendor (disponíveis: {', '.join(sorted(known))})")
            continue
        for item in font["files"]:
            if not vendor.font_path(font, item).is_file():
                rep.fail(f"arquivo da fonte {fid} não baixado ({item['file']}): rode `pycode vendor`")
    return known


def check_tokens(style, rep, known_fonts):
    tokens = D.load_tokens(style["dir"])
    if not tokens:
        rep.fail("tokens.css sem bloco :root")
        return tokens
    missing = [t for t in D.CONTRACT if t not in tokens]
    if missing:
        rep.fail(f"tokens.css sem variáveis do contrato: {', '.join(missing)}")
    slug = style.get("slug", "")
    extras = [t for t in tokens if t not in D.CONTRACT and not t.startswith(f"--{slug}-")]
    if extras:
        rep.fail(f"variáveis extras sem o prefixo --{slug}-: {', '.join(extras[:6])}")
    for fg, bg, minimum in CONTRAST_PAIRS:
        if fg not in tokens or bg not in tokens:
            continue
        try:
            value = ratio(D.resolve(tokens, tokens[fg]), D.resolve(tokens, tokens[bg]))
        except ValueError as exc:
            rep.fail(f"cor não reconhecida em {fg}/{bg}: {exc} (use hexadecimal ou rgb)")
            continue
        if value < minimum:
            rep.fail(f"contraste {fg} sobre {bg} = {value:.2f}:1 (mínimo {minimum}:1)")
    families = {known_fonts[f]["family"] for f in style.get("fonts") or [] if f in known_fonts}
    for key, family in D.font_families(tokens).items():
        if family not in families:
            rep.fail(f"{key} usa '{family}', que não está em style.json → fonts")
    return tokens


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    try:
        import yaml
    except ImportError:
        D.paths.die("pyyaml não instalado: rode `pycode setup`")
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        return {"_error": str(exc)}


def check_design(style, rep, tokens):
    file = Path(style["dir"]) / "DESIGN.md"
    if not file.is_file():
        return
    text = file.read_text(encoding="utf-8")
    fm = frontmatter(text)
    if fm is None:
        rep.fail("DESIGN.md sem frontmatter YAML (--- ... ---)")
        return
    if fm.get("_error"):
        rep.fail(f"frontmatter inválido: {fm['_error']}")
        return
    colors = fm.get("colors") or {}
    for name, value in colors.items():
        token = f"--{name}"
        if token in tokens and str(value).lower() != tokens[token].lower():
            rep.fail(f"DESIGN.md diz {name}: {value}, mas tokens.css tem {tokens[token]}")
    for token in D.COLOR_TOKENS:
        if token[2:] not in colors:
            rep.fail(f"frontmatter do DESIGN.md sem a cor '{token[2:]}'")
    headings = " ".join(h.lower() for h in re.findall(r"(?m)^##\s+(.+)$", text))
    for section in DESIGN_SECTIONS:
        if section not in headings:
            rep.fail(f"DESIGN.md sem seção sobre '{section}' (título ## com essa palavra)")


def check_text(style, rep):
    for name in ("DESIGN.md", "preview.html", "style.json"):
        file = Path(style["dir"]) / name
        if not file.is_file():
            continue
        for level, message, ctx in T.lint(T.extract(file)):
            line = f"{name}: [{level}] {message}" + (f" · …{ctx}…" if ctx else "")
            (rep.fail if level == "erro" else rep.note)(line)


def check_keyframes(style, rep):
    file = Path(style["dir"]) / "preview.html"
    if not file.is_file():
        return
    html = file.read_text(encoding="utf-8")
    css = "\n".join(re.findall(r"(?is)<style[^>]*>(.*?)</style>", html))
    for name, body in re.findall(r"@keyframes\s+([\w-]+)\s*\{((?:[^{}]*\{[^{}]*\})*)\s*\}", css):
        props = {p.strip().lower() for p in re.findall(r"([a-z-]+)\s*:", body)}
        bad = props - ANIMATABLE
        if bad:
            rep.fail(f"@keyframes {name} anima {', '.join(sorted(bad))}: use só transform, opacity ou stroke")
    for needle, why in (("IntersectionObserver", "pausar fora da viewport"), ("visibilitychange", "pausar com a aba oculta"),
                        ("prefers-reduced-motion", "respeitar movimento reduzido")):
        if needle not in html:
            rep.fail(f"preview.html sem {needle} ({why})")
    for fmt in ("deck", "carousel", "page"):
        if f'data-format="{fmt}"' not in html:
            rep.fail(f'preview.html sem a amostra data-format="{fmt}"')


def check_preview(style, rep, browser, keep_dir=None):
    from pycode_tools.browser import audit, new_page
    from pycode_tools.server import serve

    known = {f["id"]: f["family"] for f in vendor.manifest()["fonts"]}
    families = [known[f] for f in style.get("fonts") or [] if f in known]
    with tempfile.TemporaryDirectory(prefix="pycode-styles-") as tmp:
        built = D.build_style_dir(style, Path(keep_dir or tmp) / style["slug"])
        with serve(built.parent) as url:
            for w, h in VIEWPORTS:
                page = new_page(browser, w, h, mobile=w < 600)
                page.goto(f"{url}/{style['slug']}/preview.html", wait_until="load")
                page.wait_for_timeout(900)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(500)
                page.evaluate("window.scrollTo(0, 0)")
                a = audit(page)
                extra = page.evaluate(PREVIEW_JS, families)
                tag = f"prévia {w}px"
                if a["horizontalOverflow"]:
                    rep.fail(f"{tag}: rolagem horizontal ({a['scrollWidth']}px > {w}px) em {', '.join(a['offenders'][:4])}")
                for err in a["consoleErrors"][:3]:
                    rep.fail(f"{tag}: erro de console: {err[:160]}")
                for req in a["failedRequests"][:3]:
                    rep.fail(f"{tag}: requisição falhou: {req[:160]}")
                for fam in a["fontsFailed"]:
                    rep.fail(f"{tag}: fonte com erro: {fam}")
                if a["brokenImages"]:
                    rep.fail(f"{tag}: imagens quebradas: {a['brokenImages'][:3]}")
                if extra["missing"]:
                    rep.fail(f"{tag}: fontes declaradas e não usadas/carregadas: {', '.join(extra['missing'])}")
                if extra["objects"] < 4:
                    rep.fail(f"{tag}: só {extra['objects']} objeto(s) marcados com data-object (mínimo 4)")
                if abs(extra["deckRatio"] - 16 / 9) > 0.02:
                    rep.fail(f"{tag}: amostra de deck fora de 16:9 ({extra['deckRatio']})")
                if abs(extra["carouselRatio"] - 0.8) > 0.02:
                    rep.fail(f"{tag}: amostra de carrossel fora de 4:5 ({extra['carouselRatio']})")
                for item in extra["clipped"]:
                    rep.fail(f"{tag}: texto cortado: {item}")
                if a["tinyTextNodes"]:
                    rep.note(f"{tag}: {a['tinyTextNodes']} trecho(s) de texto com menos de 12px")
                page.context.close()
            page = new_page(browser, 1440, 900, reduced_motion=True)
            page.goto(f"{url}/{style['slug']}/preview.html", wait_until="load")
            page.wait_for_timeout(700)
            running = page.evaluate("document.getAnimations().filter(a => a.playState === 'running' && a.effect && a.effect.getTiming().iterations === Infinity).length")
            if running:
                rep.fail(f"movimento reduzido: {running} animação(ões) infinitas continuam rodando")
            page.context.close()


def run(styles, use_browser=True, keep_dir=None):
    reports = []
    browser_ctx = None
    if use_browser:
        from pycode_tools.browser import chromium
        browser_ctx = chromium()
        browser = browser_ctx.__enter__()
    try:
        for style in styles:
            rep = Report(style.get("slug", "?"))
            check_meta(style, rep)
            known = check_fonts(style, rep)
            tokens = check_tokens(style, rep, known)
            check_design(style, rep, tokens)
            check_text(style, rep)
            check_keyframes(style, rep)
            if use_browser and (Path(style["dir"]) / "preview.html").is_file():
                check_preview(style, rep, browser, keep_dir)
            reports.append(rep)
            mark = "ok " if not rep.fails else "FALHA"
            print(f"[{mark:^5}] {rep.slug}")
            for msg in rep.fails:
                print(f"         ✘ {msg}")
            for msg in rep.notes:
                print(f"         · {msg}")
            sys.stdout.flush()
    finally:
        if browser_ctx is not None:
            browser_ctx.__exit__(None, None, None)
    return reports


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode styles check", description="Valida um ou todos os estilos (sai com 1 se algo falhar).")
    ap.add_argument("slugs", nargs="*", help="estilos a checar (padrão: todos)")
    ap.add_argument("--no-browser", action="store_true", help="pula a abertura da prévia no Chromium (mais rápido, menos completo)")
    ap.add_argument("--keep", help="guarda as prévias montadas nesta pasta para inspecionar")
    ap.add_argument("--json", action="store_true", help="relatório final em JSON")
    args = ap.parse_args(argv)
    styles = [D.find_style(s) for s in args.slugs] if args.slugs else D.all_styles()
    if not styles:
        D.paths.die("nenhum estilo encontrado")
    reports = run(styles, use_browser=not args.no_browser, keep_dir=args.keep)
    failed = [r for r in reports if r.fails]
    if args.json:
        print(json.dumps([{"slug": r.slug, "ok": not r.fails, "fails": r.fails, "notes": r.notes} for r in reports], indent=2, ensure_ascii=False))
    print(f"\n{len(reports)} estilo(s) checado(s): {len(reports) - len(failed)} ok, {len(failed)} com falha"
          + ("" if not args.no_browser else " (sem navegador: a prévia não foi aberta)"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
