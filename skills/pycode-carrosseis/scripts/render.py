"""pycode carousel render: captura cada slide no Chromium em 1080x1350 exatos (out/slide-NN.png|jpg)."""
import argparse
import sys

from carousel_lib import (FONT_CHECK_JS, H, W, animated, load_slides, open_slide, project_dir, screenshot_rgb,
                          session, set_time, still_time, write_mirror)
from pycode_tools import paths


def parse_list(text, total):
    if not text:
        return list(range(1, total + 1))
    out = []
    for part in text.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    bad = [n for n in out if not 1 <= n <= total]
    if bad:
        paths.die(f"slides fora do intervalo 1..{total}: {bad}")
    return out


def clean_stale(root, total, fmt):
    """Apaga sobras de renders antigos (slides que não existem mais ou no outro formato)."""
    out = root / "out"
    other = "jpg" if fmt == "png" else "png"
    for f in out.glob("slide-*.*"):
        stem = f.stem.split("-")
        if len(stem) < 2 or not stem[1].isdigit():
            continue
        n = int(stem[1])
        if n > total or (f.suffix == f".{other}" and len(stem) == 2):
            f.unlink()


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode carousel render",
                                 description="Renderiza os slides em PNG ou JPG de 1080x1350 (pasta out/).")
    ap.add_argument("pasta", nargs="?", default=".", help="pasta do carrossel (padrão: a atual)")
    ap.add_argument("--scale", type=int, choices=(1, 2), default=2,
                    help="2 = renderiza em 2160x2700 e reduz para 1080x1350 (texto mais nítido); padrão 2")
    ap.add_argument("--format", choices=("png", "jpg"), default="png")
    ap.add_argument("--slides", help="só alguns slides, ex.: 1,3-5")
    args = ap.parse_args(argv)

    from PIL import Image
    root = project_dir(args.pasta)
    data = load_slides(root)
    write_mirror(root, data)
    total = len(data["slides"])
    wanted = parse_list(args.slides, total)
    (root / "out").mkdir(exist_ok=True)
    clean_stale(root, total, args.format)
    problems = []
    with session(root) as (base, browser):
        for n in wanted:
            page = open_slide(browser, base, n, scale=args.scale)
            anims = animated(page)
            if n in anims:
                set_time(page, still_time(data, n, anims[n]))
                page.wait_for_timeout(30)
            fonts = page.evaluate(FONT_CHECK_JS)
            arr = screenshot_rgb(page, args.scale)
            out = root / "out" / f"slide-{n:02d}.{args.format}"
            im = Image.fromarray(arr)
            if args.format == "jpg":
                im.save(out, "JPEG", quality=92, subsampling=0, optimize=True)
            else:
                im.save(out, optimize=True)
            if Image.open(out).size != (W, H):
                problems.append(f"slide {n}: tamanho diferente de {W}x{H}")
            if fonts["missing"] or fonts["failed"]:
                problems.append(f"slide {n}: fonte sem arquivo local: {fonts['missing'] + fonts['failed']}")
            if page.pycode_console:
                problems.append(f"slide {n}: erro no console: {page.pycode_console[:2]}")
            if page.pycode_failed:
                problems.append(f"slide {n}: requisição que falhou: {page.pycode_failed[:2]}")
            print(out)
            page.context.close()
    if problems:
        for p in problems:
            print(f"[pycode] problema: {p}", file=sys.stderr)
        return 1
    paths.say(f"{len(wanted)} slide(s) em {root / 'out'} ({W}x{H}, {args.format}, escala {args.scale})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
