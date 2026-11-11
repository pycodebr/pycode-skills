"""pycode carousel pack: empacota o carrossel para publicar (slides numerados, vídeos, legenda, folha de contato,
licenças e relatório do QA) num zip. Recusa o pacote se o QA não passou ou se a legenda ainda é esqueleto."""
import argparse
import json
import re
import sys
import zipfile

import carousel_lib as L
from pycode_tools import paths
from pycode_tools import text as T


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode carousel pack", description="Gera <slug>.zip pronto para publicar.")
    ap.add_argument("pasta", nargs="?", default=".", help="pasta do carrossel (padrão: a atual)")
    ap.add_argument("--out", help="caminho do zip (padrão: <pasta>/<slug>.zip)")
    ap.add_argument("--draft", action="store_true", help="aceita legenda com marcadores (pacote de revisão)")
    args = ap.parse_args(argv)
    root = L.project_dir(args.pasta)
    data = L.load_slides(root)
    total = len(data["slides"])

    report = root / "qa" / "relatorio.json"
    if not report.is_file():
        paths.die("rode `pycode carousel qa` antes de empacotar")
    qa = json.loads(report.read_text(encoding="utf-8"))
    if qa.get("errors"):
        paths.die(f"o último QA tem {len(qa['errors'])} erro(s): corrija e rode `pycode carousel qa` de novo")
    newest_out = max((p.stat().st_mtime for p in (root / "out").glob("slide-*")), default=0)
    if report.stat().st_mtime < max(newest_out, L.newest_source(root)):
        paths.die("o relatório do QA é mais antigo que os slides: rode `pycode carousel qa` de novo")

    caption = root / "legenda.md"
    if not caption.is_file():
        paths.die("falta legenda.md: rode `pycode carousel caption` e escreva a legenda")
    text = caption.read_text(encoding="utf-8")
    if "[[" in text and not args.draft:
        paths.die("legenda.md ainda tem marcadores [[...]]: escreva a legenda final (ou use --draft)")
    issues = [i for i in T.lint(T.clean(re.sub(r"(?s)<!--.*?-->", "", text))) if i[0] == "erro"]
    if issues and not args.draft:
        paths.die(f"legenda.md com {len(issues)} erro(s) de texto: rode `pycode text legenda.md`")

    files = []
    for n in range(1, total + 1):
        f = L.out_files(root, n)
        if f["mp4"].exists():
            files.append((f["mp4"], f"slide-{n:02d}.mp4"))
            if f["poster"].exists():
                files.append((f["poster"], f"posters/slide-{n:02d}-poster.jpg"))
        elif f["png"].exists() or f["jpg"].exists():
            img = f["png"] if f["png"].exists() else f["jpg"]
            files.append((img, f"slide-{n:02d}{img.suffix}"))
        else:
            paths.die(f"falta o slide {n} em out/: rode `pycode carousel render`")
    sheet = root / "out" / "folha-de-contato.jpg"
    if sheet.exists():
        files.append((sheet, "folha-de-contato.jpg"))
    files.append((caption, "legenda.md"))
    files.append((report, "qa-relatorio.json"))
    for lic in sorted((root / "licencas").glob("*")) if (root / "licencas").is_dir() else []:
        if lic.is_file():
            files.append((lic, f"licencas/{lic.name}"))

    slug = (data.get("meta") or {}).get("slug") or root.name
    out = root / f"{slug}.zip" if not args.out else root.joinpath(args.out).resolve()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for src, name in files:
            z.write(src, name)
    print(out)
    for _, name in files:
        print(f"  {name}")
    videos = sum(1 for _, n in files if n.endswith(".mp4"))
    paths.say(f"{total} slides ({videos} em vídeo) empacotados. Publique pelo app: carrossel misto aceita imagem e "
              "vídeo, e música só entra pelo próprio app.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
