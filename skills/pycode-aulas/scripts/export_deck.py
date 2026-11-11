"""pycode deck export: PDF (uma cena por página, com camada de texto pesquisável) e PPTX (imagem por cena e texto nas
notas), gerados a partir das capturas do estado final. Sem dependências além do Pillow."""
from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

from pycode_tools import paths
from deck_common import find_project, load_project, read_json
from pdf_writer import write_pdf
from pptx_writer import write_pptx


def check_pdf(path: Path, pages: int, words: list[str]) -> list[str]:
    """Confere estrutura e camada de texto lendo o próprio arquivo (sem bibliotecas externas)."""
    data = path.read_bytes()
    problems = []
    if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-32:]:
        problems.append("PDF sem cabeçalho ou sem %%EOF")
    count = re.search(rb"/Type /Pages /Count (\d+)", data)
    if not count or int(count.group(1)) != pages:
        problems.append(f"PDF com {count.group(1).decode() if count else '?'} página(s), esperado {pages}")
    missing = [w for w in words if w.encode("cp1252", errors="replace") not in data]
    if missing:
        problems.append(f"camada de texto sem: {missing[:3]}")
    return problems


def check_pptx(path: Path, slides: int) -> list[str]:
    problems = []
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            problems.append("PPTX com arquivo corrompido")
        names = set(z.namelist())
        for i in range(1, slides + 1):
            for part in (f"ppt/slides/slide{i}.xml", f"ppt/media/image{i}.jpeg", f"ppt/notesSlides/notesSlide{i}.xml"):
                if part not in names:
                    problems.append(f"PPTX sem {part}")
        from xml.dom import minidom
        for name in names:
            if name.endswith((".xml", ".rels")):
                try:
                    minidom.parseString(z.read(name))
                except Exception as exc:  # noqa: BLE001 - qualquer XML inválido reprova
                    problems.append(f"XML inválido em {name}: {exc}")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pycode deck export", description="Exporta o deck para PDF (com camada de texto) e PPTX (imagem por cena, texto nas notas).")
    ap.add_argument("pasta", nargs="?", help="pasta do projeto (padrão: a atual)")
    ap.add_argument("--pdf", action="store_true", help="gera o PDF")
    ap.add_argument("--pptx", action="store_true", help="gera o PPTX")
    ap.add_argument("--out", help="pasta de saída (padrão: <projeto>/exports)")
    ap.add_argument("--reuse", action="store_true", help="usa as capturas de stills/ existentes em vez de capturar de novo")
    ap.add_argument("--quality", type=int, default=88, help="qualidade JPEG das imagens (padrão 88)")
    args = ap.parse_args(argv)
    if not (args.pdf or args.pptx):
        args.pdf = True
    root = find_project(args.pasta)
    cfg, content = load_project(root)
    stills = root / "stills"
    if not args.reuse or not (stills / "stills.json").is_file():
        from build_deck import build
        from stills_deck import capture
        build(root, quiet=True)
        capture(root, quiet=True)
    data = read_json(stills / "stills.json")
    scenes = data["scenes"]
    if len(scenes) != len(content["scenes"]):
        paths.die("stills/ desatualizado (número de cenas diferente). Rode sem --reuse.")
    out = Path(args.out).resolve() if args.out else root / "exports"
    title = content["meta"].get("title", "")
    author = content["meta"].get("author", "") or (cfg.get("brand") or {}).get("author", "")
    slug = cfg.get("slug", "aula")
    problems = []
    if args.pdf:
        pdf = write_pdf([{"image": stills / s["file"], "boxes": s["boxes"]} for s in scenes], out / f"{slug}.pdf", title, author, args.quality)
        # cada palavra do título vira um trecho próprio na camada de texto: confere palavras, não a frase inteira
        probe = [w for s in scenes[:4] for w in re.findall(r"\w{4,}", s.get("title", "")) if all(ord(c) < 256 for c in w)][:8]
        problems += check_pdf(pdf, len(scenes), probe)
        print(f"PDF: {pdf}  ({pdf.stat().st_size / 1024:.0f} KB, {len(scenes)} páginas, camada de texto pesquisável)")
    if args.pptx:
        slides = []
        for s in scenes:
            notes = [f"{s['n']}. {s['title']}", "", "Texto da cena:", s.get("text", "")]
            if s.get("notes"):
                notes += ["", "Notas de fala:", s["notes"]]
            slides.append({"image": stills / s["file"], "title": s["title"], "notes": notes})
        pptx = write_pptx(slides, out / f"{slug}.pptx", title, author, args.quality)
        problems += check_pptx(pptx, len(scenes))
        print(f"PPTX: {pptx}  ({pptx.stat().st_size / 1024:.0f} KB, {len(scenes)} slides; design como imagem, texto e falas nas notas)")
    (out / "export.json").write_text(json.dumps({"title": title, "scenes": len(scenes), "problems": problems}, ensure_ascii=False, indent=1), encoding="utf-8")
    if problems:
        for p in problems:
            print(f"[falha] {p}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
