#!/usr/bin/env python3
"""pycode page og: renderiza o og.html do projeto (1200x630) em src/img/og.jpg."""
import argparse
import sys

import page_common as pc
from pycode_tools import paths


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode page og", description="Gera a imagem de compartilhamento (og:image) a partir de og.html.")
    ap.add_argument("project", nargs="?", default=".", help="pasta do projeto (padrão: a atual)")
    args = ap.parse_args(sys.argv[1:] if argv is None else argv)
    root, _ = pc.require_project(args.project)
    if not (root / "og.html").is_file():
        paths.die(f"{root / 'og.html'} não existe")
    out = pc.render_og(root)
    print(f"{out}  ({out.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
