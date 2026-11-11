"""pycode deck notion: gera o material de estudo (Markdown para o Notion) a partir do content.json e, se houver
NOTION_TOKEN e --parent, publica a página pela API REST do Notion em blocos e lê de volta para conferir.

Sem token, não falha: grava material/material-notion.md, as partes em material/notion-partes/ e explica como publicar
pelo conector de Notion do seu agente. O token fica só na variável de ambiente; nunca peça nem cole token no chat.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from pycode_tools import paths
from pycode_tools import text as T
from deck_common import find_project, load_project, pycode

NOTION_VERSION = "2022-06-28"
LANGS = {"bash": "bash", "sh": "shell", "shell": "shell", "json": "json", "python": "python", "py": "python",
         "js": "javascript", "javascript": "javascript", "html": "html", "css": "css", "mermaid": "mermaid",
         "sql": "sql", "yaml": "yaml", "text": "plain text", "": "plain text"}


# ------------------------------------------------------------------ Markdown do material
def code_lang(code: str) -> str:
    return "bash" if re.match(r"^\s*(curl|pip|python|pycode|git|npm|cd|ls)\b", code) else "text"


def build_markdown(cfg: dict, content: dict, url: str | None) -> tuple[str, list[dict]]:
    meta, study = content.get("meta", {}), content.get("meta", {}).get("study", {})
    scenes = content.get("scenes", [])
    diagrams = study.get("diagrams", [])
    out = [f"# {meta.get('title', 'Aula')}", ""]
    if meta.get("description"):
        out += [f"> {meta['description']}", ""]
    if study.get("audience"):
        out += [f"**Para quem é:** {study['audience']}", ""]
    if url:
        out += [f"**Apresentação interativa:** [abrir a aula]({url})", ""]
    if study.get("objectives"):
        out += ["## O que você vai aprender", ""] + [f"- {o}" for o in study["objectives"]] + [""]
    if study.get("prerequisites"):
        out += ["## Antes de começar", ""] + [f"- {o}" for o in study["prerequisites"]] + [""]
    out += ["## Mapa da aula", ""] + [f"{i}. {re.sub(r'[*]', '', s.get('title', ''))}" for i, s in enumerate(scenes, start=1)] + [""]
    for i, s in enumerate(scenes, start=1):
        out += [f"## {i}. {re.sub(r'[*]', '', s.get('title', ''))}", ""]
        if s.get("apoio"):
            out += [re.sub(r"[*]", "", s["apoio"]), ""]
        items = s.get("reading") or []
        for it in items:
            if isinstance(it, str):
                out.append(f"- {it}")
                continue
            head = " · ".join(x for x in (it.get("label"), it.get("title")) if x)
            out.append(f"- **{head}**: {it.get('text', '')}".rstrip(": "))
        if items:
            out.append("")
        extra = s.get("study") or {}
        for para in extra.get("text", []) if isinstance(extra.get("text"), list) else ([extra["text"]] if extra.get("text") else []):
            out += [para, ""]
        if extra.get("code"):
            out += [f"```{extra.get('lang') or code_lang(extra['code'])}", extra["code"], "```", ""]
        for d in [d for d in diagrams if d.get("after") == s.get("id")]:
            out += [f"**{d.get('title', 'Diagrama')}**", "", "```mermaid", d["mermaid"].strip(), "```", ""]
            if d.get("caption"):
                out += [d["caption"], ""]
    if study.get("glossary"):
        out += ["## Glossário", "", "| Termo | O que significa |", "|---|---|"]
        out += [f"| {g['term']} | {g['text']} |" for g in study["glossary"]] + [""]
    if study.get("exercises"):
        out += ["## Exercícios", ""]
        for k, ex in enumerate(study["exercises"], start=1):
            out += [f"### Exercício {k}: {ex.get('title', '')}", "", ex.get("text", ""), ""]
            if ex.get("code"):
                out += [f"```{code_lang(ex['code'])}", ex["code"], "```", ""]
            if ex.get("answer"):
                out += ["<details>", "<summary>Gabarito</summary>", "", ex["answer"], "", "</details>", ""]
    if study.get("sources"):
        out += ["## Fontes", ""] + [f"- [{s['title']}]({s['url']})" for s in study["sources"]] + [""]
    return "\n".join(out).rstrip() + "\n", diagrams


def split_parts(md: str) -> list[str]:
    """Partes para publicar em várias chamadas do conector (a primeira tem o título e a introdução)."""
    parts, cur = [], []
    for line in md.splitlines():
        if line.startswith("## ") and cur:
            parts.append("\n".join(cur).strip() + "\n")
            cur = []
        cur.append(line)
    if cur:
        parts.append("\n".join(cur).strip() + "\n")
    return parts


# ------------------------------------------------------------------ Markdown → blocos do Notion
INLINE = re.compile(r"\*\*(.+?)\*\*|`([^`]+)`|\[([^\]]+)\]\((https?://[^)\s]+)\)")


def rich(text: str) -> list[dict]:
    out, pos = [], 0

    def add(t, **ann):
        link = ann.pop("link", None)
        for i in range(0, len(t), 1900):
            item = {"type": "text", "text": {"content": t[i:i + 1900]}}
            if link:
                item["text"]["link"] = {"url": link}
            if ann:
                item["annotations"] = ann
            out.append(item)
    for m in INLINE.finditer(text):
        if m.start() > pos:
            add(text[pos:m.start()])
        if m.group(1) is not None:
            add(m.group(1), bold=True)
        elif m.group(2) is not None:
            add(m.group(2), code=True)
        else:
            add(m.group(3), link=m.group(4))
        pos = m.end()
    if pos < len(text):
        add(text[pos:])
    return [o for o in out if o["text"]["content"]]


def block(kind: str, text: str, **extra) -> dict:
    return {"object": "block", "type": kind, kind: {"rich_text": rich(text), **extra}}


def md_to_blocks(md: str) -> tuple[str, list[dict]]:
    lines = md.splitlines()
    title = lines[0][2:].strip() if lines and lines[0].startswith("# ") else "Aula"
    blocks, i = [], 1 if lines and lines[0].startswith("# ") else 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):
            lang, j, code = s[3:].strip(), i + 1, []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                code.append(lines[j])
                j += 1
            content = "\n".join(code)
            blocks.append({"object": "block", "type": "code", "code": {
                "rich_text": [{"type": "text", "text": {"content": content[k:k + 1900]}} for k in range(0, len(content), 1900)],
                "language": LANGS.get(lang, "plain text")}})
            i = j + 1
            continue
        if s == "<details>":
            j, inner, summary = i + 1, [], "Detalhes"
            while j < len(lines) and lines[j].strip() != "</details>":
                m = re.match(r"<summary>(.*)</summary>", lines[j].strip())
                if m:
                    summary = m.group(1)
                else:
                    inner.append(lines[j])
                j += 1
            _, children = md_to_blocks("\n".join(inner))
            blocks.append({"object": "block", "type": "toggle", "toggle": {"rich_text": rich(summary), "children": children}})
            i = j + 1
            continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            width = max(len(r) for r in rows)
            blocks.append({"object": "block", "type": "table", "table": {"table_width": width, "has_column_header": True, "has_row_header": False,
                           "children": [{"object": "block", "type": "table_row", "table_row": {"cells": [rich(c) for c in r + [""] * (width - len(r))]}} for r in rows]}})
            continue
        m = re.match(r"^(#{1,3}) (.*)", s)
        if m:
            blocks.append(block(f"heading_{len(m.group(1))}", m.group(2)))
        elif s.startswith("> "):
            blocks.append(block("quote", s[2:]))
        elif s.startswith("- "):
            blocks.append(block("bulleted_list_item", s[2:]))
        elif re.match(r"^\d+\. ", s):
            blocks.append(block("numbered_list_item", re.sub(r"^\d+\. ", "", s)))
        elif s == "---":
            blocks.append({"object": "block", "type": "divider", "divider": {}})
        else:
            blocks.append(block("paragraph", s))
        i += 1
    return title, blocks


def plain_md(md: str) -> str:
    md = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r"\1", md)
    md = re.sub(r"</?details>|<summary>|</summary>", " ", md)
    md = re.sub(r"^\s*(-|\d+\.)\s", " ", md, flags=re.M)
    md = re.sub(r"```[a-z ]*", " ", md)
    md = re.sub(r"[*`#|>]|:?-{3,}:?", " ", md)
    return " ".join(md.split())


# ------------------------------------------------------------------ API REST
class Notion:
    def __init__(self, token: str, base: str | None = None):
        self.token = token
        self.base = (base or os.environ.get("NOTION_API_BASE") or "https://api.notion.com/v1").rstrip("/")

    def call(self, method: str, path: str, body=None):
        for attempt in range(5):
            req = urllib.request.Request(f"{self.base}/{path}", method=method,
                                         data=json.dumps(body).encode() if body is not None else None,
                                         headers={"Authorization": f"Bearer {self.token}", "Notion-Version": NOTION_VERSION,
                                                  "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    return json.loads(r.read() or b"{}")
            except urllib.error.HTTPError as exc:
                msg = exc.read().decode(errors="replace")[:600]
                if exc.code in (429, 502, 503, 504) and attempt < 4:
                    time.sleep(2 + attempt * 3)
                    continue
                hint = " (a integração tem acesso à página-mãe? compartilhe a página com ela)" if exc.code in (403, 404) else ""
                paths.die(f"Notion respondeu HTTP {exc.code} em {path}{hint}: {msg}")
            except urllib.error.URLError as exc:
                paths.die(f"não consegui falar com a API do Notion: {exc}")
        paths.die("Notion: tentativas esgotadas")

    def children(self, block_id: str) -> list[dict]:
        out, cursor = [], None
        while True:
            q = f"blocks/{block_id}/children?page_size=100" + (f"&start_cursor={cursor}" if cursor else "")
            r = self.call("GET", q)
            out += r.get("results", [])
            if not r.get("has_more"):
                return out
            cursor = r.get("next_cursor")

    def publish(self, parent: str, title: str, blocks: list[dict]) -> dict:
        page = self.call("POST", "pages", {"parent": {"page_id": parent},
                                           "properties": {"title": {"title": [{"type": "text", "text": {"content": title}}]}},
                                           "children": blocks[:90]})
        rest = blocks[90:]
        while rest:
            self.call("PATCH", f"blocks/{page['id']}/children", {"children": rest[:90]})
            rest = rest[90:]
        return page

    def plain(self, block_id: str) -> str:
        parts = []
        for b in self.children(block_id):
            kind = b.get("type")
            data = b.get(kind, {}) or {}
            if kind == "table":
                for row in self.children(b["id"]):
                    for cell in row.get("table_row", {}).get("cells", []):
                        parts.append("".join(t.get("plain_text") or t.get("text", {}).get("content", "") for t in cell))
                continue
            parts.append("".join(t.get("plain_text") or t.get("text", {}).get("content", "") for t in data.get("rich_text", [])))
            if b.get("has_children") and kind != "child_page":
                parts.append(self.plain(b["id"]))
        return " ".join(parts)


def norm(text: str) -> str:
    return " ".join(re.sub(r"[*`#|>]", " ", text).split())


def validate_mermaid(diagrams: list[dict], folder: Path) -> list[str]:
    errors = []
    folder.mkdir(parents=True, exist_ok=True)
    for k, d in enumerate(diagrams, start=1):
        src = folder / f"{k:02d}.mmd"
        src.write_text(d["mermaid"].strip() + "\n", encoding="utf-8")
        r = pycode("mermaid", str(src), "--out", str(src.with_suffix(".svg")), check=False)
        if r.returncode != 0:
            errors.append(f"diagrama {k} ({d.get('title', '')}) não renderizou: {(r.stderr or r.stdout).strip()[-300:]}")
    return errors


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pycode deck notion", description="Gera o material de estudo para o Notion a partir do content.json; com NOTION_TOKEN e --parent, publica pela API e lê de volta.")
    ap.add_argument("pasta", nargs="?", help="pasta do projeto (padrão: a atual)")
    ap.add_argument("--parent", help="id da página-mãe no Notion (publica só se NOTION_TOKEN estiver definido)")
    ap.add_argument("--url", help="endereço público da apresentação, para o link no material")
    ap.add_argument("--dry-run", action="store_true", help="gera os blocos da API em material/notion-blocos.json sem publicar")
    args = ap.parse_args(argv)
    root = find_project(args.pasta)
    cfg, content = load_project(root)
    out = root / "material"
    out.mkdir(exist_ok=True)
    md, diagrams = build_markdown(cfg, content, args.url)
    issues = [(lvl, msg, ctx) for lvl, msg, ctx in T.lint(T.clean(md))]
    errors = [i for i in issues if i[0] == "erro"]
    for lvl, msg, ctx in issues:
        print(f"[{lvl}] texto do material: {msg}" + (f" · {ctx}" if ctx else ""))
    errors_m = validate_mermaid(diagrams, out / "diagramas") if diagrams else []
    for e in errors_m:
        print(f"[erro] {e}", file=sys.stderr)
    if errors or errors_m:
        paths.die("corrija o texto ou os diagramas no content.json e rode de novo")
    (out / "material-notion.md").write_text(md, encoding="utf-8")
    parts_dir = out / "notion-partes"
    if parts_dir.exists():
        for f in parts_dir.glob("*.md"):
            f.unlink()
    parts_dir.mkdir(exist_ok=True)
    parts = split_parts(md)
    for k, part in enumerate(parts):
        (parts_dir / f"{k:02d}.md").write_text(part, encoding="utf-8")
    title, blocks = md_to_blocks(md)
    print(f"material: {out / 'material-notion.md'}  ({T.words(md)} palavras, {len(blocks)} blocos, {len(diagrams)} diagrama(s) validado(s))")
    print(f"partes para o conector: {parts_dir} ({len(parts)} arquivos)")
    if args.dry_run:
        (out / "notion-blocos.json").write_text(json.dumps({"title": title, "children": blocks}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"blocos da API: {out / 'notion-blocos.json'}")
    token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not args.parent or not token:
        print("\nComo publicar:")
        print("  1. Pelo conector/MCP de Notion do seu agente: crie a página com o título e insira as partes de")
        print(f"     {parts_dir} na ordem, uma por chamada; depois leia a página de volta e confira seções e diagramas.")
        print("  2. Pela API: crie uma integração interna no Notion, compartilhe a página-mãe com ela, defina NOTION_TOKEN")
        print("     no ambiente (nunca no chat) e rode: pycode deck notion <pasta> --parent <id-da-página-mãe>")
        return 0
    api = Notion(token)
    page = api.publish(args.parent, title, blocks)
    back = norm(api.plain(page["id"]))
    expected = norm(plain_md(md.split("\n", 1)[1]))
    missing = [w for w in dict.fromkeys(re.findall(r"[\wÀ-ÿ]{5,}", expected)) if w not in back]
    report = {"page_id": page.get("id"), "url": page.get("url"), "blocks": len(blocks), "readback_chars": len(back),
              "expected_chars": len(expected), "missing_words": missing[:30]}
    (out / "notion-publicacao.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"publicado: {page.get('url') or page.get('id')}  ·  leitura de volta: {len(back)} caracteres")
    if missing:
        print(f"[falha] a leitura de volta não encontrou {len(missing)} palavra(s), ex.: {missing[:8]}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
