"""pycode carousel new: cria um carrossel 4:5 a partir do modelo ou de um exemplo pronto."""
import argparse
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

from carousel_lib import EXAMPLES, TEMPLATE, write_mirror
from pycode_tools import paths, styles, vendor

RUNTIME = ["css/base.css", "js/carousel.js"]


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "carrossel"


def examples():
    return sorted(p.name for p in EXAMPLES.iterdir() if (p / "slides.json").is_file()) if EXAMPLES.is_dir() else []


def rail_heights(count):
    """Alturas de entrada/saída do trilho: a saída do slide N é a entrada do N+1."""
    wave = [1010, 1090, 980, 1060, 1120, 1000]
    return [wave[i % len(wave)] for i in range(count)]


def template_slides(title, count):
    ys = rail_heights(count)
    slides = []
    for i in range(count):
        n = i + 1
        if n == 1:
            s = {"layout": "cover", "title": title, "body": "[frase de apoio da capa, se precisar]",
                 "video": {"seconds": 4}, "rail": {"start": [540, 960], "out": ys[0]}}
        elif n == count:
            s = {"layout": "cta", "title": f"[fechamento do slide {n}]", "body": "[uma frase que amarra o conteúdo]",
                 "cta": "[o único pedido de ação do carrossel]",
                 "rail": {"in": ys[i - 1], "via": [[540, ys[i - 1] - 120]], "end": [880, 860]}}
        else:
            s = {"layout": "content", "title": f"[título do slide {n}]",
                 "body": f"[texto do slide {n}: duas ou três frases conectadas, até 35 palavras]",
                 "keywords": [], "rail": {"in": ys[i - 1], "via": [[540, (ys[i - 1] + ys[i]) // 2 + 70]],
                                          "out": ys[i]}}
        slides.append(s)
    return slides


def tokens_css(style, brand):
    css = style["tokens_css"].rstrip() + "\n"
    overrides = {k: v for k, v in (brand.get("colors") or {}).items() if v}
    if overrides:
        css += "\n/* Cores da marca (~/.pycode-skills/brand.json) por cima do estilo. */\n:root {\n"
        css += "".join(f"  --{k.lstrip('-')}: {v};\n" for k, v in overrides.items())
        css += "}\n"
    return css


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode carousel new",
                                 description="Cria um carrossel 4:5 (1080x1350) a partir do modelo ou de um exemplo.")
    ap.add_argument("pasta", help="pasta nova do carrossel")
    ap.add_argument("--title", help="título da capa (obrigatório sem --example)")
    ap.add_argument("--style", help="estilo do pycode-design (padrão: o do exemplo, o da marca ou o primeiro)")
    ap.add_argument("--slides", type=int, default=7, help="número de slides do modelo (2 a 20; padrão 7)")
    ap.add_argument("--example", help="copia um exemplo pronto: " + (", ".join(examples()) or "nenhum"))
    ap.add_argument("--force", action="store_true", help="escreve numa pasta que já tem arquivos")
    args = ap.parse_args(argv)

    root = Path(args.pasta).expanduser().resolve()
    if root.exists() and any(root.iterdir()) and not args.force:
        paths.die(f"{root} já existe e não está vazia (use --force para escrever por cima)")
    meta_example = {}
    if args.example:
        src = EXAMPLES / args.example
        if not (src / "slides.json").is_file():
            paths.die(f"exemplo desconhecido: {args.example}. Disponíveis: {', '.join(examples())}")
        meta_example = json.loads((src / "example.json").read_text(encoding="utf-8")) if (src / "example.json").is_file() else {}
    elif not args.title:
        paths.die("informe --title \"...\" (ou --example <nome> para partir de um exemplo pronto)")
    if not 2 <= args.slides <= 20:
        paths.die("--slides precisa ficar entre 2 e 20 (limite do Instagram)")

    brand = paths.load_brand()
    slug = args.style or meta_example.get("default_style") or None
    known = {st["slug"] for st in styles.list_styles()}
    if not args.style and slug and slug not in known:
        paths.say(f"o estilo sugerido pelo exemplo ({slug}) não está instalado; usando o padrão")
        slug = None
    style = styles.load_style(slug)
    root.mkdir(parents=True, exist_ok=True)

    shutil.copytree(TEMPLATE, root, dirs_exist_ok=True)
    if args.example:
        shutil.copytree(EXAMPLES / args.example, root, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("example.json", "out", "qa", "*.zip"))
        for rel in RUNTIME:  # o runtime vem sempre do modelo (uma cópia só para manter)
            shutil.copyfile(TEMPLATE / rel, root / rel)

    (root / "css" / "tokens.css").write_text(tokens_css(style, brand), encoding="utf-8")
    font_ids = list(dict.fromkeys(list(style.get("fonts", [])) + list(meta_example.get("fonts_extra", []))))
    fonts_css = vendor.copy_fonts(root / "fonts", font_ids, url_prefix="../fonts/")
    (root / "css" / "fonts.css").write_text("/* Fontes locais (OFL), copiadas por pycode carousel new. */\n" + fonts_css,
                                            encoding="utf-8")

    if args.example:
        data = json.loads((root / "slides.json").read_text(encoding="utf-8"))
        if args.title:
            data.setdefault("meta", {})["title"] = args.title
    else:
        data = {"meta": {"title": args.title, "slug": slugify(args.title), "lang": brand.get("language", "pt-BR"),
                         "concept": "[nome do conceito visual]"},
                "slides": template_slides(args.title, args.slides)}
    data.setdefault("meta", {})["style"] = style["slug"]
    data["brand"] = {"name": brand.get("name", ""), "handle": brand.get("handle", "")}
    ordered = {"meta": data["meta"], "brand": data["brand"]}
    ordered.update({k: v for k, v in data.items() if k not in ordered})
    (root / "slides.json").write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_mirror(root, ordered)
    (root / "licencas").mkdir(exist_ok=True)
    (root / "out").mkdir(exist_ok=True)

    paths.say(f"carrossel criado em {root}")
    print(f"  estilo: {style['slug']} · fontes: {', '.join(font_ids)} · slides: {len(ordered['slides'])}")
    print(f"  texto: {root / 'slides.json'}  ·  desenho: {root / 'js' / 'scene.js'}, {root / 'css' / 'scene.css'}")
    print("  próximos passos: pycode carousel render <pasta>  →  pycode carousel qa <pasta>  →  pycode carousel preview <pasta>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
