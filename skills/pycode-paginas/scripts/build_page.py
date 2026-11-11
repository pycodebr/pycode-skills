#!/usr/bin/env python3
"""pycode page build: gera dist/ pronto para publicar.

- CSS crítico (os links entre <!-- pycode:critical --> e <!-- /pycode:critical -->) minificado e incorporado
  em <style id="critical-css">, com limite de 15 KB, pelo comando central `pycode css critical`;
- CSS completo (link com data-defer) minificado e carregado sem bloquear a primeira pintura, com <noscript>;
- CSS, JS e fontes com hash do conteúdo no nome (cache longo sem servir arquivo velho);
- conferência de build reproduzível (dois builds idênticos byte a byte) e de ausência de fonte/script externo.
"""
import argparse
import contextlib
import io
import re
import shutil
import sys
import tempfile
from pathlib import Path

if not __debug__:
    raise RuntimeError("rode sem -O: as checagens deste comando não podem ser desligadas")

import page_common as pc  # noqa: E402
from pycode_tools import commands, paths  # noqa: E402

CRITICAL_BLOCK = re.compile(r"[ \t]*<!-- pycode:critical.*?-->(.*?)<!-- /pycode:critical -->[ \t]*\n?", re.S)
DEFER_LINK = re.compile(r'[ \t]*<link\b[^>]*\bdata-defer\b[^>]*>[ \t]*\n?')
HREF = re.compile(r'\bhref="([^"]+)"')
SCRIPT_SRC = re.compile(r'<script\b[^>]*\bsrc="([^"]+)"')
CSS_URL = re.compile(r"""url\(\s*(['"]?)([^'")]+)\1\s*\)""")
CDN_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com", "cdn.jsdelivr.net", "unpkg.com", "cdnjs.cloudflare.com",
             "use.typekit.net", "kit.fontawesome.com", "code.jquery.com")
KEEP_OUT = {"Thumbs.db", ".DS_Store"}


def parse_args(argv):
    ap = argparse.ArgumentParser(prog="pycode page build", description="Gera dist/ com CSS crítico incorporado, hashes e conferências.")
    ap.add_argument("project", nargs="?", default=".", help="pasta do projeto (padrão: a atual)")
    ap.add_argument("--max-critical-kb", type=float, default=15, help="limite do CSS crítico minificado (padrão 15)")
    ap.add_argument("--allow-host", action="append", default=[],
                    help="host externo permitido em runtime (ex.: o gerenciador de tags opcional). Repita a opção")
    ap.add_argument("--skip-repro", action="store_true", help="não confere se dois builds saem idênticos (mais rápido)")
    return ap.parse_args(argv)


def is_local(url):
    return not re.match(r"^(?:[a-z][a-z0-9+.-]*:|//|#)", url, re.I)


def short_hash(data):
    return pc.sha256(data)[:10]


def hashed_name(rel, data):
    path = Path(rel)
    return path.with_name(f"{path.stem}.{short_hash(data)}{path.suffix}").as_posix()


def quiet(fn, *args):
    """Chama um comando central sem poluir a saída; erros (SystemExit) continuam valendo."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = fn(*args)
    if code:
        paths.die(buffer.getvalue().strip() or "comando central falhou")
    return buffer.getvalue()


def minify(css_text, work):
    work.mkdir(parents=True, exist_ok=True)
    src = work / "in.css"
    out = work / "out.css"
    src.write_text(css_text, encoding="utf-8")
    quiet(commands.cmd_css, ["minify", str(src), "-o", str(out)])
    text = out.read_text(encoding="utf-8").strip()
    if "NaN" in text:
        paths.die("o CSS minificado contém NaN (duração extrema como .01ms vira NaN em alguns minificadores). Use .001s.")
    return text


def rewrite_css_urls(css, css_rel_dir, renames, page_dir=""):
    """Reescreve url(...) de fontes/arquivos renomeados. css_rel_dir é a pasta onde o CSS original estava."""
    def fix(match):
        quote, url = match.group(1), match.group(2)
        if not is_local(url) or url.startswith("data:"):
            return match.group(0)
        target = (Path(css_rel_dir) / url).as_posix()
        target = _normalize(target)
        if target in renames:
            new = renames[target]
            rel = _relative(new, page_dir)
            return f"url({quote}{rel}{quote})"
        if page_dir != css_rel_dir:
            return f"url({quote}{_relative(target, page_dir)}{quote})"
        return match.group(0)
    return CSS_URL.sub(fix, css)


def _normalize(path):
    parts = []
    for part in path.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)


def _relative(target, from_dir):
    if not from_dir:
        return target
    depth = len([p for p in from_dir.split("/") if p])
    return "../" * depth + target


def hash_assets(out, renames):
    """Fontes e JS ganham o hash no nome (o CSS é tratado depois, já com as URLs das fontes reescritas)."""
    for folder, suffixes in (("fonts", (".woff2", ".woff")), ("js", (".js",))):
        base = out / folder
        if not base.is_dir():
            continue
        for file in sorted(base.rglob("*")):
            if file.suffix in suffixes:
                rel = file.relative_to(out).as_posix()
                new = hashed_name(rel, file.read_bytes())
                file.rename(out / new)
                renames[rel] = new


def build_css_files(src, out, renames, work, cache):
    """Minifica e põe hash em cada CSS de src/css que não seja só crítico."""
    def process(rel):
        if rel in cache:
            return cache[rel]
        text = (src / rel).read_text(encoding="utf-8")
        text = rewrite_css_urls(text, str(Path(rel).parent), renames, str(Path(rel).parent))
        mini = minify(text, work / "css")
        new = hashed_name(rel, mini.encode())
        (out / new).parent.mkdir(parents=True, exist_ok=True)
        (out / new).write_text(mini + "\n", encoding="utf-8")
        cache[rel] = new
        return new
    return process


def page_dir_of(rel_page):
    parent = Path(rel_page).parent.as_posix()
    return "" if parent == "." else parent


def build_page(rel_page, src, out, renames, css_file, work, args, report):
    html_path = out / rel_page
    html = html_path.read_text(encoding="utf-8")
    pdir = page_dir_of(rel_page)
    block = CRITICAL_BLOCK.search(html)
    critical_sources = []
    if block:
        critical_sources = [h for h in HREF.findall(block.group(1)) if h.endswith(".css")]
        html = html[:block.start()] + '  <style id="critical-css"></style>\n' + html[block.end():]
    for tag in re.findall(r'<link\b[^>]*rel="stylesheet"[^>]*>', html):
        href = HREF.search(tag)
        if "data-defer" in tag or not href or not is_local(href.group(1)):
            continue
        report["warnings"].append(f"{rel_page}: CSS bloqueante {href.group(1)} (use data-defer ou o bloco crítico)")
        new = _relative(css_file(_normalize((Path(pdir) / href.group(1)).as_posix())), pdir)
        html = html.replace(tag, tag.replace(href.group(0), f'href="{new}"'), 1)
    for match in list(DEFER_LINK.finditer(html)):
        href = HREF.search(match.group(0)).group(1)
        new = _relative(css_file(_normalize((Path(pdir) / href).as_posix())), pdir)
        tag = (f'  <link rel="preload" href="{new}" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">\n'
               f'  <noscript><link rel="stylesheet" href="{new}"></noscript>\n')
        html = html.replace(match.group(0), tag, 1)
    html = _rewrite_refs(html, pdir, renames)
    html_path.write_text(html, encoding="utf-8")
    if critical_sources:
        bundle = ""
        for href in critical_sources:
            rel = _normalize((Path(pdir) / href).as_posix())
            text = (src / rel).read_text(encoding="utf-8")
            bundle += rewrite_css_urls(text, str(Path(rel).parent), renames, pdir) + "\n"
        work.mkdir(parents=True, exist_ok=True)
        bundle_file = work / "critical-bundle.css"
        bundle_file.write_text(bundle, encoding="utf-8")
        quiet(commands.cmd_css, ["critical", str(html_path), "--css", str(bundle_file), "--max-kb", str(args.max_critical_kb)])
        inline = re.search(r'<style id="critical-css">(.*?)</style>', html_path.read_text(encoding="utf-8"), re.S).group(1)
        if "NaN" in inline:
            paths.die(f"{rel_page}: CSS crítico contém NaN depois de minificado")
        report["critical_kb"][rel_page] = round(len(inline.encode()) / 1024, 2)


def _rewrite_refs(html, pdir, renames):
    def fix(match):
        attr, url = match.group(1), match.group(2)
        if not is_local(url):
            return match.group(0)
        clean = url.split("?")[0].split("#")[0]
        rel = _normalize((Path(pdir) / clean).as_posix())
        if rel in renames:
            return f'{attr}="{_relative(renames[rel], pdir)}"'
        return match.group(0)
    return re.sub(r'\b(href|src)="([^"]+)"', fix, html)


def absolutize_404(out, base):
    """A 404 é servida em qualquer caminho: os assets precisam de URL absoluta a partir do base_path."""
    page = out / "404.html"
    if not page.is_file():
        return
    html = page.read_text(encoding="utf-8")
    base = "/" + base.strip("/") + "/" if base.strip("/") else "/"

    def fix(match):
        attr, url = match.group(1), match.group(2)
        return f'{attr}="{base}{url}"' if is_local(url) and not url.startswith("/") else match.group(0)
    html = re.sub(r'\b(href|src)="([^"]+)"', fix, html)
    html = CSS_URL.sub(lambda m: f"url({m.group(1)}{base}{m.group(2)}{m.group(1)})"
                       if is_local(m.group(2)) and not m.group(2).startswith(("/", "data:")) else m.group(0), html)
    page.write_text(html, encoding="utf-8")


def remove_sources(out, renames, css_cache):
    for old in list(renames) + list(css_cache):
        target = out / old
        if target.is_file():
            target.unlink()
    for leftover in sorted((out / "css").glob("*.css")) if (out / "css").is_dir() else []:
        if leftover.relative_to(out).as_posix() not in css_cache.values():
            leftover.unlink()


def build_into(root, cfg, out, args, work):
    src = root / "src"
    if not (src / "index.html").is_file():
        paths.die(f"{src / 'index.html'} não existe")
    shutil.copytree(src, out, ignore=shutil.ignore_patterns(*KEEP_OUT))
    report = {"critical_kb": {}, "warnings": []}
    renames = {}
    hash_assets(out, renames)
    css_cache = {}
    css_file = build_css_files(src, out, renames, work, css_cache)
    pages = sorted(p.relative_to(out).as_posix() for p in out.rglob("*.html"))
    for rel_page in pages:
        build_page(rel_page, src, out, renames, css_file, work, args, report)
    remove_sources(out, renames, css_cache)
    absolutize_404(out, cfg.get("base_path", "/"))
    report["pages"] = pages
    report["renames"] = {**renames, **css_cache}
    return report


def external_runtime(out, allowed):
    """Fontes, scripts e CSS precisam ser servidos pelo próprio site (nada de CDN em runtime)."""
    problems = []

    def bad(url):
        host = re.sub(r"^(?:https?:)?//", "", url).split("/")[0].lower()
        return host and not any(host == a or host.endswith("." + a) for a in allowed)
    for file in sorted(out.rglob("*")):
        if not file.is_file() or file.suffix not in (".html", ".css", ".js"):
            continue
        text = file.read_text(encoding="utf-8", errors="ignore")
        rel = file.relative_to(out).as_posix()
        if file.suffix == ".html":
            for url in SCRIPT_SRC.findall(text):
                if not is_local(url) and bad(url):
                    problems.append(f"{rel}: script externo {url}")
            for tag in re.findall(r"<link\b[^>]*>", text):
                rel_attr = re.search(r'rel="([^"]+)"', tag)
                href = HREF.search(tag)
                loads = rel_attr and re.search(r"stylesheet|preload|modulepreload", rel_attr.group(1))
                if href and loads and not is_local(href.group(1)) and bad(href.group(1)):
                    problems.append(f"{rel}: {rel_attr.group(1)} externo {href.group(1)}")
        for quote, url in CSS_URL.findall(text):
            if re.match(r"^(?:https?:)?//", url) and bad(url):
                problems.append(f"{rel}: url() externa {url}")
        for host in CDN_HOSTS:
            if host in text and host not in allowed:
                problems.append(f"{rel}: referência a {host}")
    return sorted(set(problems))


def color_literals(src):
    warnings = []
    for file in sorted((src / "css").glob("*.css")):
        if file.name in ("tokens.css", "fonts.css"):
            continue
        text = re.sub(r"/\*.*?\*/", "", file.read_text(encoding="utf-8"), flags=re.S)
        found = sorted(set(re.findall(r"#[0-9a-fA-F]{3,8}\b|\brgba?\([^)]*\)|\bhsla?\([^)]*\)", text)))
        if found:
            warnings.append(f"css/{file.name}: cores fixas fora dos tokens ({', '.join(found[:6])}); prefira var(--...) ou color-mix()")
    return warnings


def manifest(out):
    import gzip
    files = []
    for file in sorted(p for p in out.rglob("*") if p.is_file()):
        data = file.read_bytes()
        entry = {"file": file.relative_to(out).as_posix(), "bytes": len(data), "sha256": pc.sha256(data)}
        if file.suffix in pc.GZIP_TYPES:
            entry["gzip"] = len(gzip.compress(data, mtime=0))
        files.append(entry)
    return files


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root, cfg = pc.require_project(args.project)
    dist = root / "dist"
    with tempfile.TemporaryDirectory(prefix="pycode-build-") as tmp:
        tmp = Path(tmp)
        report = build_into(root, cfg, tmp / "a", args, tmp / "work-a")
        if not args.skip_repro:
            build_into(root, cfg, tmp / "b", args, tmp / "work-b")
            a, b = pc.tree_digest(tmp / "a"), pc.tree_digest(tmp / "b")
            if a != b:
                diff = sorted(set(a.items()) ^ set(b.items()))
                paths.die("o build não é reproduzível; arquivos diferentes entre duas execuções: "
                          + ", ".join(sorted({d[0] for d in diff})[:10]))
        problems = external_runtime(tmp / "a", [h.lower() for h in args.allow_host])
        errors = list(problems)
        for page in report["pages"]:
            text = (tmp / "a" / page).read_text(encoding="utf-8")
            errors += [f"{page}: {e}" for e in pc.check_balance(text)]
            if "{{" in text:
                errors.append(f"{page}: sobrou marcador {{{{...}}}} do modelo")
        if errors:
            for line in errors:
                print(f"  [erro] {line}", file=sys.stderr)
            paths.die(f"build reprovado: {len(errors)} problema(s). Nada foi gravado em {dist}.")
        if dist.exists():
            shutil.rmtree(dist)
        shutil.copytree(tmp / "a", dist)
    files = manifest(dist)
    warnings = report["warnings"] + color_literals(root / "src")
    data = {"project": cfg.get("title"), "reproducible": not args.skip_repro, "critical_kb": report["critical_kb"],
            "pages": report["pages"], "files": files, "warnings": warnings,
            "total_bytes": sum(f["bytes"] for f in files), "total_gzip": sum(f.get("gzip", f["bytes"]) for f in files)}
    pc.write_json(root / "build-manifest.json", data)
    paths.say(f"build pronto em {dist}")
    for page, kb in report["critical_kb"].items():
        print(f"  {page}: CSS crítico {kb} KB (limite {args.max_critical_kb:g} KB)")
    for entry in files:
        if entry["file"].endswith((".css", ".js", ".html")):
            print(f"  {entry['file']:<40} {entry['bytes'] / 1024:7.1f} KB  (gzip {entry.get('gzip', 0) / 1024:.1f} KB)")
    repro = "sim" if data["reproducible"] else "não conferido"
    print(f"  total: {data['total_bytes'] / 1024:.0f} KB em {len(files)} arquivos · reproduzível: {repro}")
    for line in warnings:
        print(f"  [aviso] {line}")
    print(f"  manifesto: {root / 'build-manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
