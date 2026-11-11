"""pycode styles new: cria um estilo do usuário copiando outro como ponto de partida."""
import argparse
import json
import re
import shutil
from pathlib import Path

import design_lib as D


def rename_prefix(text, old, new):
    """Troca o prefixo das variáveis extras (--old-x → --new-x) sem tocar nas do contrato."""
    return re.sub(rf"--{re.escape(old)}-", f"--{new}-", text)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode styles new", description="Cria um estilo seu a partir de um estilo existente.")
    ap.add_argument("slug", help="nome curto do estilo novo, em minúsculas com hífens (ex.: estudio-coral)")
    ap.add_argument("--from", dest="base", required=True, help="estilo de partida (veja `pycode styles list`)")
    ap.add_argument("--name", help="nome legível (padrão: derivado do slug)")
    ap.add_argument("--dir", help="pasta onde criar (padrão: ~/.pycode-skills/styles-user)")
    ap.add_argument("--force", action="store_true", help="sobrescreve se já existir")
    args = ap.parse_args(argv)
    if not D.SLUG_RE.match(args.slug):
        D.paths.die("slug inválido: use letras minúsculas, números e hífens, começando por letra (ex.: estudio-coral)")
    if (D.repo_root() / args.slug).exists():
        D.paths.die(f"já existe um estilo do repositório chamado {args.slug}; escolha outro nome")
    base = D.find_style(args.base)
    root = Path(args.dir).expanduser() if args.dir else D.user_root()
    dest = root / args.slug
    if dest.exists():
        if not args.force:
            D.paths.die(f"{dest} já existe (use --force para sobrescrever)")
        shutil.rmtree(dest)
    shutil.copytree(base["dir"], dest, ignore=shutil.ignore_patterns("fonts", ".*"))
    old = base["slug"]
    name = args.name or args.slug.replace("-", " ").capitalize()
    for file in ("tokens.css", "preview.html", "DESIGN.md"):
        path = dest / file
        if path.is_file():
            text = rename_prefix(path.read_text(encoding="utf-8"), old, args.slug)
            if file == "DESIGN.md":
                text = re.sub(r"(?m)^name:.*$", f"name: {name}", text, count=1)
                text = re.sub(r"(?m)^version:.*$", "version: 0.1.0", text, count=1)
                text = re.sub(r"(?m)^slug:.*$", f"slug: {args.slug}", text, count=1)
            if file == "tokens.css":
                text = re.sub(r"^/\*.*?\*/", f"/* {name} · derivado de {old}. Não renomeie as variáveis do contrato. */", text, count=1, flags=re.S)
            path.write_text(text, encoding="utf-8")
    meta_file = dest / "style.json"
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    meta.update({"slug": args.slug, "name": name, "version": "0.1.0", "derived_from": old})
    meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Estilo criado em {dest} (cópia de {old}).")
    print("Próximos passos:")
    print(f"  1. edite {dest / 'tokens.css'} (mantenha todas as variáveis do contrato)")
    print(f"  2. reescreva {dest / 'DESIGN.md'} com os objetos e o movimento do estilo novo")
    print(f"  3. ajuste {dest / 'preview.html'} e confira: pycode styles check {args.slug}")
    if args.dir:
        print(f"  Observação: a pasta indicada só é lida quando PYCODE_STYLES_USER={root} estiver definida.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
