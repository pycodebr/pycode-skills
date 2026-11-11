"""pycode deck new: cria um projeto de aula a partir do modelo (motor, cenas, tokens do estilo, fontes e GSAP)."""
from __future__ import annotations

import argparse
import copy
import re
import shutil
from pathlib import Path

from pycode_tools import paths, styles, vendor
from deck_common import (DECK_TEMPLATE, ENGINE_VERSION, ID_RE, archetypes, install_scene, read_json, slugify,
                         write_json)

GITIGNORE = "site/\nqa/\nstills/\nexports/\n"


def pick_scenes(model: list[dict], n: int | None, wanted: list[str] | None) -> list[dict]:
    """Cenas do projeto: o modelo inteiro, as N primeiras (com o encerramento) ou os arquétipos pedidos."""
    library = {a["archetype"]: a["sample"] for a in archetypes()}
    if wanted:
        out, used = [], set()
        for arch in wanted:
            if arch not in library:
                paths.die(f"arquétipo desconhecido: {arch}. Disponíveis: {', '.join(sorted(library))}")
            from_model = next((s for s in model if s.get("archetype") == arch and s["id"] not in used), None)
            scene = copy.deepcopy(from_model or library[arch])
            base, k = scene["id"], 2
            while scene["id"] in used:
                scene["id"] = f"{base}-{k}"
                k += 1
            used.add(scene["id"])
            out.append(scene)
        return out
    if not n or n == len(model):
        return copy.deepcopy(model)
    if n < 3:
        paths.die("--scenes precisa ser 3 ou mais (capa, pelo menos uma cena e o encerramento)")
    body = model[:-1]
    extra = [library[a] for a in sorted(library) if a not in {s.get("archetype") for s in model}]
    middle = (body + extra)[: n - 1]
    if len(middle) < n - 1:
        paths.die(f"--scenes {n} passa do que o modelo e a biblioteca oferecem ({len(body) + len(extra) + 1})")
    return copy.deepcopy(middle + [model[-1]])


def brand_tokens(brand: dict) -> str:
    colors = {k: v for k, v in (brand.get("colors") or {}).items() if re.fullmatch(r"[a-z0-9-]+", k)}
    if not colors:
        return ""
    lines = "\n".join(f"  --{k}: {v};" for k, v in colors.items())
    return f"\n/* cores da sua marca (brand.json) */\n:root {{\n{lines}\n}}\n"


def check_tokens(css: str, origin: str) -> None:
    missing = [t for t in styles.REQUIRED_TOKENS if not re.search(re.escape(t) + r"\s*:", css)]
    if missing:
        paths.die(f"{origin} não define as variáveis do contrato: {', '.join(missing)}")


def create(dest: Path, title: str, style_slug: str | None, tokens_file: str | None, n: int | None,
           wanted: list[str] | None, lang: str, force: bool) -> Path:
    if dest.exists() and any(dest.iterdir()) and not force:
        paths.die(f"{dest} já existe e não está vazia (use outra pasta ou --force)")
    brand = paths.load_brand()
    style = styles.load_style(style_slug)
    tokens_css = style["tokens_css"]
    origin = f"estilo {style['slug']}"
    if tokens_file:
        tokens_css = Path(tokens_file).read_text(encoding="utf-8")
        origin = tokens_file
    check_tokens(tokens_css, origin)
    font_ids = list(style.get("fonts") or [])
    if tokens_file:
        known = vendor.font_ids()
        found = [f for f in known if re.search(r"['\"]%s['\"]" % re.escape(vendor_family(f)), tokens_css)]
        font_ids = found or font_ids
    dest.mkdir(parents=True, exist_ok=True)
    # fontes do motor e do modelo
    shutil.copytree(DECK_TEMPLATE / "src", dest / "src", dirs_exist_ok=True)
    (dest / "src" / "scenes").mkdir(exist_ok=True)
    model = read_json(DECK_TEMPLATE / "content.json")
    content = copy.deepcopy(model)
    content["scenes"] = pick_scenes(model["scenes"], n, wanted)
    content["meta"]["title"] = title
    content["meta"]["author"] = brand.get("author") or content["meta"].get("author", "")
    cover = content["scenes"][0]
    if cover.get("archetype") == "capa":
        cover["title"] = title
    for s in content["scenes"]:
        if not ID_RE.match(s["id"]):
            paths.die(f"id inválido no modelo: {s['id']}")
        install_scene(dest, s["archetype"], s["id"])
    write_json(dest / "src" / "content.json", content)
    (dest / "src" / "css" / "tokens.css").write_text(
        f"/* tokens do {origin} (contrato do pycode-design). Troque o arquivo para mudar o estilo. */\n"
        + tokens_css.strip() + "\n" + brand_tokens(brand), encoding="utf-8")
    fonts_css = vendor.copy_fonts(dest / "assets" / "fonts", font_ids, url_prefix="../fonts/") if font_ids else ""
    (dest / "src" / "css" / "fonts.css").write_text("/* fontes OFL copiadas pelo pycode vendor */\n" + fonts_css, encoding="utf-8")
    vendor.copy_js(dest / "assets" / "vendor", ["gsap"])
    (dest / "assets" / "img").mkdir(parents=True, exist_ok=True)
    logo = brand.get("logo")
    deck_brand = {"name": brand.get("name", ""), "author": brand.get("author", ""), "site": brand.get("site", ""), "logo": ""}
    if logo and Path(logo).expanduser().is_file():
        target = dest / "assets" / "img" / Path(logo).name
        shutil.copyfile(Path(logo).expanduser(), target)
        deck_brand["logo"] = f"assets/img/{target.name}"
    write_json(dest / "deck.json", {
        "slug": slugify(title), "lang": lang, "style": style["slug"] if not tokens_file else "personalizado",
        "mode": guess_mode(tokens_css) if tokens_file else style.get("mode", "dark"),
        "fonts": font_ids, "version": "1.0.0", "engine": ENGINE_VERSION, "brand": deck_brand,
    })
    (dest / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
    return dest


def guess_mode(css: str) -> str:
    """claro ou escuro pela luminância de --bg (para tokens.css próprios)."""
    from pycode_tools.color import luminance, parse
    m = re.search(r"--bg\s*:\s*([^;]+);", css)
    try:
        return "light" if m and luminance(parse(m.group(1))) > .4 else "dark"
    except ValueError:
        return "dark"


def vendor_family(font_id: str) -> str:
    for f in vendor.manifest()["fonts"]:
        if f["id"] == font_id:
            return f["family"]
    return font_id


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pycode deck new", description="Cria um projeto de aula interativa a partir do modelo (Como funciona uma API), com o estilo, as fontes, o GSAP local e a sua marca.")
    ap.add_argument("pasta", help="pasta do projeto novo")
    ap.add_argument("--title", required=True, help="título da aula (vai para a capa e para o documento)")
    ap.add_argument("--style", help="slug do estilo do pycode-design (padrão: o da marca ou o primeiro)")
    ap.add_argument("--tokens", help="tokens.css próprio no lugar do estilo (precisa ter todas as variáveis do contrato)")
    ap.add_argument("--scenes", type=int, help="quantidade de cenas (capa e encerramento incluídos)")
    ap.add_argument("--archetypes", help="lista de arquétipos na ordem, ex.: capa,circuito,terminal,encerramento")
    ap.add_argument("--lang", default="pt-BR", help="idioma do documento (padrão pt-BR)")
    ap.add_argument("--force", action="store_true", help="escreve numa pasta que já tem arquivos")
    args = ap.parse_args(argv)
    wanted = [a.strip() for a in args.archetypes.split(",") if a.strip()] if args.archetypes else None
    dest = create(Path(args.pasta).expanduser().resolve(), args.title, args.style, args.tokens, args.scenes, wanted, args.lang, args.force)
    content = read_json(dest / "src" / "content.json")
    print(f"projeto criado: {dest}")
    print(f"  cenas: {', '.join(s['id'] + ' (' + s['archetype'] + ')' for s in content['scenes'])}")
    print(f"  texto (fonte única): {dest / 'src' / 'content.json'}")
    print(f"  cenas: {dest / 'src' / 'scenes'}")
    print(f"próximo passo: pycode deck build {dest} && pycode serve {dest / 'site'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
