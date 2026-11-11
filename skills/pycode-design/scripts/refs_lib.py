"""Funções dos comandos `pycode refs`: catálogo, download e índice dos acervos externos."""
import html
import json
import re
import unicodedata
from pathlib import Path

from pycode_tools import paths

CATALOG = Path(__file__).resolve().parent / "refs_catalog.json"
META = ".pycode-ref.json"
INDEX = "pycode-index.json"
NOTICE = "LEIA-ANTES.txt"
LICENSE_WARNING = ("Acervo sem licença declarada: use só para estudo local. Não copie código, não publique "
                   "derivados diretos e não redistribua estes arquivos.")


def catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))["refs"]


def find(ref_id):
    for ref in catalog():
        if ref["id"] == ref_id:
            return ref
    paths.die(f"acervo desconhecido: {ref_id}. Opções: {', '.join(r['id'] for r in catalog())}")
    raise SystemExit(1)


def local_dir(ref):
    return paths.REFS / ref["id"]


def local_meta(ref):
    file = local_dir(ref) / META
    if not file.is_file():
        return None
    try:
        return json.loads(file.read_text(encoding="utf-8"))
    except ValueError:
        return None


def normalize(text):
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def _title(html_file):
    try:
        head = html_file.read_text(encoding="utf-8", errors="ignore")[:6000]
    except OSError:
        return ""
    m = re.search(r"<title[^>]*>(.*?)</title>", head, re.S | re.I)
    return html.unescape(" ".join(m.group(1).split())) if m else ""


def build_index(ref):
    """Lista os itens do acervo com título e começo do prompt, para busca rápida."""
    base = local_dir(ref)
    items = []
    if ref["kind"] == "html-gallery":
        for html_file in sorted(base.glob("[0-9][0-9][0-9]-*.html")):
            prompt = html_file.with_suffix(".txt")
            text = prompt.read_text(encoding="utf-8", errors="ignore") if prompt.is_file() else ""
            num, _, slug = html_file.stem.partition("-")
            items.append({"id": f"{ref['id']}/{num}", "num": num, "slug": slug, "title": _title(html_file),
                          "html": str(html_file), "prompt": str(prompt) if prompt.is_file() else "",
                          "summary": " ".join(text.split())[:600]})
    else:
        for design in sorted(base.glob("design-md/*/DESIGN.md")):
            text = design.read_text(encoding="utf-8", errors="ignore")
            brand = design.parent.name
            items.append({"id": f"{ref['id']}/{brand}", "num": "", "slug": brand, "title": brand,
                          "html": "", "prompt": str(design), "summary": " ".join(text.split())[:600]})
    (base / INDEX).write_text(json.dumps(items, indent=1, ensure_ascii=False), encoding="utf-8")
    return items


def load_index(ref):
    file = local_dir(ref) / INDEX
    if not file.is_file():
        return build_index(ref) if local_meta(ref) else []
    return json.loads(file.read_text(encoding="utf-8"))
