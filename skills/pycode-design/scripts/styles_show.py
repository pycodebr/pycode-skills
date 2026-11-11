"""pycode styles show: imprime os caminhos e o DESIGN.md de um estilo."""
import argparse
from pathlib import Path

import design_lib as D


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode styles show", description="Mostra o DESIGN.md e os caminhos de um estilo.")
    ap.add_argument("slug", help="slug do estilo (veja `pycode styles list`)")
    ap.add_argument("--paths", action="store_true", help="só os caminhos, sem o DESIGN.md")
    args = ap.parse_args(argv)
    style = D.find_style(args.slug)
    base = Path(style["dir"])
    print(f"{style.get('name')} ({style.get('slug')}) · {style.get('mode')} · origem: {style['origin']}")
    print(f"  pasta     {base}")
    for name in ("style.json", "tokens.css", "DESIGN.md", "preview.html"):
        mark = "" if (base / name).is_file() else "  (falta)"
        print(f"  {name:<12}{base / name}{mark}")
    print(f"  fontes    {', '.join(style.get('fonts', []))}")
    print(f"  formatos  {', '.join(style.get('best_for', []))}")
    print("  prévia    pycode styles preview --style " + style.get("slug", args.slug))
    if args.paths:
        return 0
    design = base / "DESIGN.md"
    if design.is_file():
        print("\n" + design.read_text(encoding="utf-8"))
    else:
        print("\nEste estilo ainda não tem DESIGN.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
