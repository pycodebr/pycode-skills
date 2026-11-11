#!/usr/bin/env python3
"""pycode page new: cria um projeto de página (landing) ou site (várias páginas) a partir do modelo."""
import argparse
import datetime
import re
import shutil
import sys
from pathlib import Path

import page_common as pc  # noqa: E402
from pycode_tools import paths, styles, vendor  # noqa: E402

PAGES = {
    "landing": ["index.html"],
    "site": ["index.html", "oficinas.html", "404.html"],
}
DEFAULT_DESCRIPTION = ("Uma oficina prática em quatro encontros ao vivo para entender o caminho de uma requisição "
                       "e escrever a sua primeira API.")
CONTRACT = sorted(set(styles.REQUIRED_TOKENS) | {"--bg-2", "--warn", "--weight-display", "--tracking-display"})


def parse_args(argv):
    ap = argparse.ArgumentParser(
        prog="pycode page new",
        description="Cria um projeto de página estática com os tokens de um estilo, fontes locais e a sua marca.",
        epilog="Exemplo: pycode page new minha-oficina --title \"Como funciona uma API\" --style orbital",
    )
    ap.add_argument("dest", help="pasta do projeto (não pode existir com arquivos, a menos que use --force)")
    ap.add_argument("--title", required=True, help="título da página (vira o <title>, o og:title e o h1 do modelo)")
    ap.add_argument("--description", help="meta description (padrão: um resumo do modelo)")
    ap.add_argument("--style", help="slug do estilo (pycode styles list). Padrão: o da marca ou o primeiro")
    ap.add_argument("--kind", choices=sorted(PAGES), default="landing", help="landing (uma página) ou site (home, página interna e 404)")
    ap.add_argument("--tokens", help="tokens.css próprio no lugar de um estilo publicado (precisa ter todas as variáveis do contrato)")
    ap.add_argument("--fonts", help="ids de fontes do vendor separados por vírgula (padrão: as do estilo)")
    ap.add_argument("--site-url", help="URL pública final (padrão: o site da marca). Usada em canonical e og:image")
    ap.add_argument("--force", action="store_true", help="escreve mesmo se a pasta já tiver arquivos")
    return ap.parse_args(argv)


def pick_style(args):
    if args.tokens:
        css = Path(args.tokens).read_text(encoding="utf-8")
        tokens = pc.parse_tokens(css)
        mode = "light" if _is_light(tokens.get("--bg", "#000")) else "dark"
        return {"slug": Path(args.tokens).stem, "name": "tokens próprios", "fonts": [], "mode": mode, "tokens_css": css}
    return styles.load_style(args.style)


def _is_light(color):
    from pycode_tools.color import luminance, parse
    try:
        return luminance(parse(color)) > 0.4
    except ValueError:
        return False


def pick_fonts(args, style, tokens):
    if args.fonts:
        return [f.strip() for f in args.fonts.split(",") if f.strip()]
    if style.get("fonts"):
        return list(style["fonts"])
    by_family = {f["family"]: f["id"] for f in vendor.manifest()["fonts"]}
    wanted = [pc.first_family(tokens.get(k, "")) for k in ("--font-display", "--font-body", "--font-mono")]
    return list(dict.fromkeys(by_family[w] for w in wanted if w in by_family))


def check_contract(tokens):
    missing = [t for t in CONTRACT if t not in tokens]
    if missing:
        paths.die("o tokens.css não tem estas variáveis do contrato: " + ", ".join(missing)
                  + "\n  Veja a lista completa na skill pycode-design (contrato de tokens).")


def brand_tokens(brand):
    colors = brand.get("colors") or {}
    if not colors:
        return ""
    lines = [f"  --{k.lstrip('-')}: {v};" for k, v in colors.items()]
    return "\n/* Sobrescritas da marca (brand.json > colors) */\n:root {\n" + "\n".join(lines) + "\n}\n"


def preload_links(fonts, tokens):
    """Preload só das fontes de título e corpo (as que pintam a primeira dobra)."""
    fams = {pc.first_family(tokens.get("--font-display", "")), pc.first_family(tokens.get("--font-body", ""))}
    out = []
    for font in fonts:
        if font["family"] not in fams:
            continue
        item = next((i for i in font["files"] if i["style"] == "normal"), font["files"][0])
        out.append(f'  <link rel="preload" href="fonts/{item["file"]}" as="font" type="font/woff2" crossorigin>')
    return out


def brand_mark(brand, src):
    logo = Path(brand.get("logo") or "").expanduser()
    if brand.get("logo") and logo.is_file():
        dest = src / "img" / f"logo{logo.suffix.lower()}"
        shutil.copyfile(logo, dest)
        width, height = _image_size(dest)
        return f'<img src="img/{dest.name}" width="{width}" height="{height}" alt="">'
    return ('<svg class="brand-mark" viewBox="0 0 32 32" aria-hidden="true">'
            '<circle cx="15" cy="17" r="10"/><circle class="dot" cx="25" cy="8" r="4"/></svg>')


def _image_size(path):
    if path.suffix == ".svg":
        text = path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'viewBox="[\d.\s-]*?\s([\d.]+)\s+([\d.]+)"', text)
        return (round(float(m.group(1))), round(float(m.group(2)))) if m else (32, 32)
    from PIL import Image
    with Image.open(path) as im:
        return im.size


def favicon(tokens):
    bg, ring, dot = tokens.get("--bg", "#111"), tokens.get("--accent-2", "#7dd3fc"), tokens.get("--accent", "#edc580")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="{bg}"/>'
            f'<circle cx="29" cy="35" r="16" fill="none" stroke="{ring}" stroke-width="5"/>'
            f'<circle cx="47" cy="17" r="8" fill="{dot}"/></svg>\n')


def fill(text, values):
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    dest = Path(args.dest).expanduser().resolve()
    if dest.exists() and any(dest.iterdir()) and not args.force:
        paths.die(f"{dest} já existe e não está vazia. Escolha outra pasta ou use --force.")
    style = pick_style(args)
    tokens_css = style["tokens_css"]
    tokens = pc.parse_tokens(tokens_css)
    check_contract(tokens)
    brand = paths.load_brand()
    font_ids = pick_fonts(args, style, tokens)
    fonts = pc.vendor_fonts(font_ids)

    src = dest / "src"
    shared = pc.TEMPLATES / "shared"
    for sub in ("css", "js"):
        shutil.copytree(shared / sub, src / sub, dirs_exist_ok=True)
    (src / "img").mkdir(parents=True, exist_ok=True)
    for extra in ("_headers", ".htaccess", "robots.txt"):
        shutil.copyfile(shared / "deploy" / extra, src / extra)

    tokens_out = pc.add_fallback_families(tokens_css, fonts) + brand_tokens(brand)
    (src / "css" / "tokens.css").write_text(tokens_out, encoding="utf-8")
    final_tokens = pc.parse_tokens(tokens_out)
    font_css = vendor.copy_fonts(src / "fonts", font_ids, url_prefix="../fonts/")
    (src / "css" / "fonts.css").write_text(
        "/* Fontes locais (OFL) copiadas pelo pycode e fallback métrico para evitar salto de layout. */\n"
        + font_css + pc.fallback_css(fonts), encoding="utf-8")
    (src / "img" / "favicon.svg").write_text(favicon(final_tokens), encoding="utf-8")

    site_url = (args.site_url or brand.get("site") or "https://exemplo.com").rstrip("/")
    values = {
        "TITLE": args.title, "BRAND": brand.get("name") or "Sua Marca", "HANDLE": brand.get("handle", ""),
        "DESCRIPTION": args.description or DEFAULT_DESCRIPTION,
        "LANG": brand.get("language") or "pt-BR", "OG_LOCALE": (brand.get("language") or "pt-BR").replace("-", "_"),
        "SITE": site_url, "SITE_LABEL": re.sub(r"^https?://", "", site_url), "YEAR": str(datetime.date.today().year),
        "THEME_COLOR": final_tokens.get("--bg", "#000000"), "COLOR_SCHEME": "light" if style.get("mode") == "light" else "dark",
        "OG_IMAGE": f"{site_url}/img/og.jpg", "FORM_ACTION": f"{site_url}/inscricao",
        "PRELOAD": "\n".join(preload_links(fonts, final_tokens)), "BRAND_MARK": brand_mark(brand, src),
    }
    for page in PAGES[args.kind]:
        text = (pc.TEMPLATES / args.kind / page).read_text(encoding="utf-8")
        canonical = site_url + "/" + ("" if page == "index.html" else page)
        (src / page).write_text(fill(text, {**values, "CANONICAL": canonical}), encoding="utf-8")
    og = fill((shared / "og.html").read_text(encoding="utf-8"), values).replace('href="css/', 'href="src/css/')
    (dest / "og.html").write_text(og, encoding="utf-8")
    readme = fill((pc.TEMPLATES / "README.projeto.md").read_text(encoding="utf-8"), {**values, "STYLE": style["slug"], "KIND": args.kind})
    (dest / "README.md").write_text(readme, encoding="utf-8")

    cfg = {
        "generator": "pycode-paginas", "version": paths.version(), "title": args.title, "kind": args.kind,
        "style": style["slug"], "mode": style.get("mode", "dark"), "fonts": font_ids, "site_url": site_url,
        "base_path": "/", "pages": PAGES[args.kind], "lang": values["LANG"],
        "created": datetime.date.today().isoformat(),
    }
    pc.save_config(dest, cfg)
    og_file = pc.render_og(dest)
    paths.say(f"projeto criado em {dest} (modelo {args.kind}, estilo {style['slug']}, fontes {', '.join(font_ids)})")
    for page in PAGES[args.kind]:
        print(f"  {src / page}")
    print(f"  {og_file}")
    print(f"\nPróximos passos:\n  pycode serve {src}        (prévia enquanto edita)")
    print(f"  pycode page build {dest}\n  pycode page qa {dest}\n  pycode page perf {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
