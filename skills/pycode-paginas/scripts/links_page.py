#!/usr/bin/env python3
"""pycode page check-links: confere links, âncoras e arquivos referenciados (fail-closed).

Pasta ou projeto: lê todos os HTML de dist/ (ou da pasta), confere arquivos locais, ids de âncora
(inclusive em outra página) e url() dos CSS. Links externos são testados por HTTP (desligue com --no-external).
URL: baixa a página e testa cada link por HTTP.
"""
import argparse
import concurrent.futures
import html.parser
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

if not __debug__:
    raise RuntimeError("rode sem -O: as checagens não podem ser desligadas")

import page_common as pc  # noqa: E402

SKIP = ("mailto:", "tel:", "javascript:", "data:", "sms:")
PLACEHOLDER_HOSTS = ("exemplo.com", "example.com", "example.org")


class Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        line = self.getpos()[0]
        for attr in ("href", "src", "poster"):
            if a.get(attr) and not (tag == "link" and a.get("rel") in ("canonical", "alternate")):
                self.refs.append((tag, attr, a[attr], line))
        for attr in ("srcset", "imagesrcset"):
            for part in (a.get(attr) or "").split(","):
                if part.strip():
                    self.refs.append((tag, attr, part.strip().split()[0], line))
        if tag == "meta" and a.get("property") in ("og:image", "og:url") and a.get("content"):
            self.refs.append((tag, a["property"], a["content"], line))

    handle_startendtag = handle_starttag


def parse_args(argv):
    ap = argparse.ArgumentParser(prog="pycode page check-links", description="Confere links, âncoras e arquivos referenciados.")
    ap.add_argument("target", nargs="?", default=".", help="projeto (confere dist/), pasta ou URL")
    ap.add_argument("--no-external", action="store_true", help="não testa links externos por HTTP")
    ap.add_argument("--timeout", type=float, default=12)
    return ap.parse_args(argv)


def http_status(url, timeout):
    headers = {"User-Agent": "Mozilla/5.0 (pycode check-links)"}
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.geturl()
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in (403, 405, 501):
                continue
            return exc.code, url
        except Exception as exc:  # noqa: BLE001
            if method == "GET":
                return f"erro: {type(exc).__name__}: {str(exc)[:80]}", url
    return "erro", url


def parse_file(path):
    parser = Links()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return parser


def check_dir(folder, check_external, timeout):
    errors, warnings, external = [], [], {}
    pages = pc.html_pages(folder)
    parsed = {p: parse_file(p) for p in pages}
    for page, data in parsed.items():
        rel_page = page.relative_to(folder).as_posix()
        for tag, attr, url, line in data.refs:
            where = f"{rel_page}:{line} <{tag} {attr}>"
            if url.startswith(SKIP):
                continue
            if re.match(r"^https?://", url) or url.startswith("//"):
                external.setdefault(url if not url.startswith("//") else "https:" + url, []).append(where)
                continue
            path_part, _, frag = url.partition("#")
            path_part = urllib.parse.unquote(path_part.split("?")[0])
            if path_part.startswith("/"):
                target = folder / path_part.lstrip("/")
            else:
                target = (page.parent / path_part) if path_part else page
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                errors.append(f"{where}: arquivo não existe ({url})")
                continue
            if frag and target.suffix == ".html":
                ids = parsed[target.resolve()].ids if target.resolve() in parsed else parse_file(target).ids
                if urllib.parse.unquote(frag) not in ids:
                    errors.append(f"{where}: âncora #{frag} não existe em {target.name}")
    for css in sorted(folder.rglob("*.css")):
        for _, url in re.findall(r"""url\(\s*(['"]?)([^'")]+)\1\s*\)""", css.read_text(encoding="utf-8", errors="ignore")):
            if url.startswith(("data:", "http", "//", "#")):
                continue
            if not (css.parent / url.split("?")[0]).exists():
                errors.append(f"{css.relative_to(folder)}: url({url}) não existe")
    return errors, warnings, external, len(pages)


def check_external_urls(external, timeout, errors, warnings):
    todo = {}
    for url, where in external.items():
        host = urllib.parse.urlparse(url).hostname or ""
        if any(host == h or host.endswith("." + h) for h in PLACEHOLDER_HOSTS):
            warnings.append(f"destino de exemplo ainda no HTML: {url} ({where[0]})")
            continue
        todo[url] = where
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = dict(zip(todo, pool.map(lambda u: http_status(u, timeout), todo)))
    for url, (status, final) in results.items():
        ok = isinstance(status, int) and status < 400
        if not ok:
            errors.append(f"{url} → {status} ({todo[url][0]})")
        elif final != url and urllib.parse.urlparse(final).hostname != urllib.parse.urlparse(url).hostname:
            warnings.append(f"{url} redireciona para outro domínio: {final}")
    return len(results)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    kind, value, root = pc.resolve_target(args.target)
    if kind == "url":
        with urllib.request.urlopen(urllib.request.Request(value, headers={"User-Agent": "pycode check-links"}), timeout=args.timeout) as r:
            parser = Links()
            parser.feed(r.read().decode("utf-8", errors="ignore"))
        errors, warnings, external = [], [], {}
        for tag, attr, url, line in parser.refs:
            if url.startswith(SKIP):
                continue
            if url.startswith("#"):
                if url[1:] and urllib.parse.unquote(url[1:]) not in parser.ids:
                    errors.append(f"linha {line}: âncora {url} não existe na página")
                continue
            external.setdefault(urllib.parse.urljoin(value, url), []).append(f"linha {line} <{tag} {attr}>")
        pages = 1
    else:
        errors, warnings, external, pages = check_dir(value, not args.no_external, args.timeout)
    tested = 0
    if external and (kind == "url" or not args.no_external):
        tested = check_external_urls(external, args.timeout, errors, warnings)
    report = {"target": str(value), "pages": pages, "external_tested": tested, "errors": errors, "warnings": warnings}
    out = (root / "qa" / "links.json") if root else Path("links-report.json")
    pc.write_json(out, report)
    print(f"[pycode] {pages} página(s) · {tested} link(s) externo(s) testado(s)")
    for line in warnings:
        print(f"  [aviso] {line}")
    for line in errors:
        print(f"  [erro] {line}")
    print(f"{len(errors)} erro(s), {len(warnings)} aviso(s) · relatório: {out}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
