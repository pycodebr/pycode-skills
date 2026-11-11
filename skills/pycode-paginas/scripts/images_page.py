#!/usr/bin/env python3
"""pycode page images: gera variantes responsivas (WebP e, se o Pillow suportar, AVIF) e imprime o HTML pronto.

O HTML impresso já traz srcset, sizes, width/height (evita salto de layout), loading e decoding.
Use --eager só na imagem principal da primeira dobra (a candidata a LCP).
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from pycode_tools import paths

RASTER = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp", ".gif"}


def parse_args(argv):
    ap = argparse.ArgumentParser(prog="pycode page images", description="Variantes responsivas de imagens e o <img>/<picture> correspondente.",
                                 epilog="Exemplo: pycode page images src/img/estudio.png --widths 480,960,1600 --alt \"Bancada do estúdio\"")
    ap.add_argument("inputs", nargs="+", help="arquivos ou pastas com PNG/JPG/WebP")
    ap.add_argument("--widths", default="480,960,1600", help="larguras desejadas (nunca amplia além do original)")
    ap.add_argument("--format", choices=("webp", "avif", "both"), default="webp", help="formato das variantes")
    ap.add_argument("--quality", type=int, default=80, help="qualidade de 1 a 100 (padrão 80)")
    ap.add_argument("--out", help="pasta de saída (padrão: a mesma da imagem original)")
    ap.add_argument("--prefix", default="img/", help="caminho usado no HTML impresso (padrão img/)")
    ap.add_argument("--sizes", default="(max-width: 760px) 100vw, 50vw", help="atributo sizes do HTML impresso")
    ap.add_argument("--alt", default="", help="texto alternativo (descreva a imagem; vazio só se for decorativa)")
    ap.add_argument("--eager", action="store_true", help="imagem da primeira dobra: loading=eager e fetchpriority=high")
    return ap.parse_args(argv)


def collect(inputs):
    files = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            files += sorted(q for q in p.iterdir() if q.suffix.lower() in RASTER)
        elif p.is_file() and p.suffix.lower() in RASTER:
            files.append(p)
        else:
            paths.die(f"não é imagem raster nem pasta: {item} (SVG não precisa de variantes)")
    if not files:
        paths.die("nenhuma imagem encontrada")
    return files


def encode(im, dest, fmt, quality):
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    frame = im.convert("RGBA" if has_alpha else "RGB")
    if fmt == "webp":
        frame.save(dest, "WEBP", quality=quality, method=6)
    else:
        frame.save(dest, "AVIF", quality=max(1, quality - 20), speed=4)
    data = dest.read_bytes()
    return {"file": dest.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def variants(src, out, widths, formats, quality):
    from PIL import Image, ImageOps
    with Image.open(src) as raw:
        im = ImageOps.exif_transpose(raw)
        im.load()
    usable = {w for w in widths if w < im.width}
    if any(w >= im.width for w in widths) or not usable:
        usable.add(im.width)  # pediu maior que o original: entrega o original, nunca amplia
    usable = sorted(usable)
    made = {fmt: [] for fmt in formats}
    for width in usable:
        height = round(im.height * width / im.width)
        resized = im if width == im.width else im.resize((width, height), Image.LANCZOS)
        for fmt in formats:
            entry = encode(resized, out / f"{src.stem}-{width}.{fmt}", fmt, quality)
            entry.update({"width": width, "height": height})
            made[fmt].append(entry)
    return made, im.size


def snippet(made, size, args):
    widest = max(made["webp"] if "webp" in made else next(iter(made.values())), key=lambda e: e["width"])
    width, height = widest["width"], widest["height"]
    load = 'loading="eager" fetchpriority="high" decoding="async"' if args.eager else 'loading="lazy" decoding="async"'
    alt = args.alt.replace('"', "&quot;")

    def srcset(entries):
        return ", ".join(f"{args.prefix}{e['file']} {e['width']}w" for e in entries)
    main_fmt = "webp" if "webp" in made else "avif"
    img = (f'<img src="{args.prefix}{widest["file"]}" srcset="{srcset(made[main_fmt])}" sizes="{args.sizes}"\n'
           f'     width="{width}" height="{height}" alt="{alt}" {load}>')
    if len(made) == 1:
        return img
    return (f'<picture>\n  <source type="image/avif" srcset="{srcset(made["avif"])}" sizes="{args.sizes}">\n  '
            + img.replace("\n", "\n  ") + "\n</picture>")


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    from PIL import features
    formats = ["webp", "avif"] if args.format == "both" else [args.format]
    if "avif" in formats and not features.check("avif"):
        if args.format == "avif":
            paths.die("este Pillow não grava AVIF. Atualize com `pycode setup` ou use --format webp")
        print("[pycode] aviso: este Pillow não grava AVIF; gerando só WebP", file=sys.stderr)
        formats = ["webp"]
    widths = [int(w) for w in args.widths.split(",") if w.strip()]
    manifest_entries = []
    for src in collect(args.inputs):
        out = Path(args.out) if args.out else src.parent
        out.mkdir(parents=True, exist_ok=True)
        made, size = variants(src, out, widths, formats, args.quality)
        original = src.stat().st_size
        print(f"\n{src}  ({size[0]}x{size[1]}, {original / 1024:.0f} KB)")
        for fmt, entries in made.items():
            for e in entries:
                print(f"  {out / e['file']}  {e['width']}x{e['height']}  {e['bytes'] / 1024:.0f} KB")
        print(snippet(made, size, args))
        manifest_entries.append({"source": src.name, "size": list(size), "variants": made})
        if not args.alt:
            print("  [aviso] sem --alt: escreva um texto alternativo que descreva a imagem (ou alt=\"\" se for decorativa)")
    manifest = (Path(args.out) if args.out else collect(args.inputs)[0].parent) / "images.json"
    old = json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else []
    keep = [e for e in old if e["source"] not in {m["source"] for m in manifest_entries}]
    manifest.write_text(json.dumps(keep + manifest_entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nmanifesto: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
