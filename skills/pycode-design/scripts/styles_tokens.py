"""pycode styles tokens: exporta os tokens de um estilo em CSS, JSON ou tema Tailwind."""
import argparse
import json
from pathlib import Path

import design_lib as D

TAILWIND_COLORS = {
    "bg": "--bg", "bg-2": "--bg-2", "surface": "--surface", "surface-2": "--surface-2", "text": "--text",
    "muted": "--muted", "line": "--line", "accent": "--accent", "accent-2": "--accent-2", "accent-ink": "--accent-ink",
    "paper": "--paper", "paper-ink": "--paper-ink", "danger": "--danger", "ok": "--ok", "warn": "--warn",
}


def as_json(style, tokens):
    contract = {k: tokens[k] for k in D.CONTRACT if k in tokens}
    extras = {k: v for k, v in tokens.items() if k not in D.CONTRACT}
    return json.dumps({"slug": style["slug"], "name": style.get("name"), "mode": style.get("mode"),
                       "fonts": style.get("fonts", []), "tokens": contract, "extras": extras}, indent=2, ensure_ascii=False)


def as_tailwind(style, tokens):
    """Tema que aponta para as variáveis CSS (mantém o tokens.css como fonte única)."""
    theme = {
        "colors": {name: f"var({var})" for name, var in TAILWIND_COLORS.items()},
        "fontFamily": {"display": "var(--font-display)", "body": "var(--font-body)", "mono": "var(--font-mono)"},
        "borderRadius": {"DEFAULT": "var(--radius)", "lg": "var(--radius-lg)"},
        "boxShadow": {"DEFAULT": "var(--shadow)", "glow": "var(--glow)"},
        "letterSpacing": {"display": "var(--tracking-display)"},
        "fontWeight": {"display": "var(--weight-display)"},
    }
    resolved = {name: tokens.get(var, "") for name, var in TAILWIND_COLORS.items()}
    return json.dumps({"_comment": f"Tema do estilo {style['slug']}. Inclua o tokens.css no projeto; os valores literais estão em _resolved.",
                       "theme": {"extend": theme}, "_resolved": resolved}, indent=2, ensure_ascii=False)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode styles tokens", description="Exporta os tokens de um estilo.")
    ap.add_argument("slug")
    ap.add_argument("--format", choices=["css", "json", "tailwind"], default="css")
    ap.add_argument("--out", help="grava num arquivo em vez de imprimir")
    args = ap.parse_args(argv)
    style = D.find_style(args.slug)
    file = Path(style["dir"]) / "tokens.css"
    if not file.is_file():
        D.paths.die(f"{file} não existe")
    css = file.read_text(encoding="utf-8")
    tokens = D.parse_tokens(css)
    text = css if args.format == "css" else as_json(style, tokens) if args.format == "json" else as_tailwind(style, tokens)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
        print(out)
    else:
        print(text.rstrip("\n"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
