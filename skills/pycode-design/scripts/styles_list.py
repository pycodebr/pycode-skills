"""pycode styles list: lista os estilos do repositório e os criados pelo usuário."""
import argparse
import json

import design_lib as D


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode styles list", description="Lista os estilos de design disponíveis.")
    ap.add_argument("--json", action="store_true", help="saída em JSON (slug, nome, modo, formatos, fontes, caminho)")
    ap.add_argument("--mode", choices=["dark", "light"], help="filtra por modo")
    ap.add_argument("--for", dest="fmt", choices=sorted(D.FORMATS), help="filtra por formato indicado (page, deck, carousel)")
    args = ap.parse_args(argv)
    styles = D.all_styles()
    if args.mode:
        styles = [s for s in styles if s.get("mode") == args.mode]
    if args.fmt:
        styles = [s for s in styles if args.fmt in s.get("best_for", [])]
    if args.json:
        print(json.dumps(styles, indent=2, ensure_ascii=False))
        return 0
    if not styles:
        print("Nenhum estilo encontrado com esse filtro.")
        return 0
    width = max(len(s.get("slug", "")) for s in styles)
    for s in styles:
        tag = "" if s["origin"] == "repositório" else "  [seu]"
        formats = ",".join(s.get("best_for", []))
        print(f"{s.get('slug', ''):<{width}}  {s.get('mode', '?'):<5}  {formats:<20}  {s.get('name', '')}{tag}")
        if s.get("_error"):
            print(f"{'':<{width}}  ! {s['_error']}")
    print(f"\n{len(styles)} estilo(s). Detalhes: pycode styles show <slug> · galeria: pycode styles preview")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
