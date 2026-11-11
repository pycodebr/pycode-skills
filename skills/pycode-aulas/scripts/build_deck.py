"""pycode deck build: monta site/ a partir de src/ e confere o contrato do motor."""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from pathlib import Path

from pycode_tools import paths
from pycode_tools import text as T
from deck_common import (ENGINE_VERSION, ID_RE, UI_DEFAULTS, find_project, load_project, short_hash, text_strings,
                         write_json)

SCENE_FORBIDDEN = [
    (r"addEventListener\(", "handler direto na cena (cliques passam por ctx.pick)"),
    (r"localStorage|sessionStorage", "armazenamento local dentro da cena"),
    (r"repeat\s*:\s*-1", "repetição infinita (movimento contínuo vai em ambient(dt))"),
    (r"Math\.random", "aleatoriedade (as capturas precisam ser iguais a cada abertura)"),
    (r"\bfetch\(|XMLHttpRequest|import\(", "requisição em tempo de execução"),
    (r"<button\b|<input\b|<form\b|<select\b|<textarea\b", "controle de formulário dentro da cena"),
    (r"\bon[a-z]+\s*=\s*[\"']", "handler inline"),
    (r"https?://(?!www\.w3\.org/)", "URL externa"),
]
SCENE_REQUIRED = [
    (r"ctx\.pick\(", "itens clicáveis (ctx.pick)"),
    (r"\bhome\b", "volta ao início da demonstração (home)"),
    (r"\bkey\s*[:,(]", "chave da seleção (key)"),
]
COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]")
TRANSITIONS = {"corte", "cortina", "iris", "sobe"}


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def inline(text: str | None) -> str:
    """Escapa e converte *destaque* em <em>."""
    out = html.escape(text or "", quote=False)
    return re.sub(r"\*([^*]+)\*", r"<em>\1</em>", out)


def attr(text: str | None) -> str:
    return html.escape(re.sub(r"\*", "", text or ""), quote=True)


def check_content(content: dict, root: Path, rep: Report) -> list[dict]:
    meta = content.get("meta") or {}
    if not meta.get("title"):
        rep.error("content.json: meta.title vazio")
    scenes = content.get("scenes") or []
    if not scenes:
        rep.error("content.json: nenhuma cena em scenes")
    seen = set()
    for n, s in enumerate(scenes, start=1):
        sid = s.get("id", "")
        where = f"cena {n} ({sid or 'sem id'})"
        if not ID_RE.match(sid):
            rep.error(f"{where}: id inválido (use minúsculas, números e hífen, começando por letra)")
        if sid in seen:
            rep.error(f"{where}: id repetido")
        seen.add(sid)
        title = re.sub(r"\*", "", s.get("title", ""))
        words = T.words(title)
        if not words:
            rep.error(f"{where}: sem título")
        elif words > 7:
            rep.error(f"{where}: título com {words} palavras (o palco pede de 2 a 5)")
        elif words > 5 or words < 2:
            rep.warn(f"{where}: título com {words} palavras (o recomendado é de 2 a 5)")
        if s.get("transition", "corte") not in TRANSITIONS:
            rep.error(f"{where}: transição desconhecida {s.get('transition')!r} (use {', '.join(sorted(TRANSITIONS))})")
        if not s.get("reading"):
            rep.warn(f"{where}: sem lista 'reading' (o modo leitura e o celular ficam só com título e apoio)")
        if n < len(scenes) and not s.get("hook"):
            rep.warn(f"{where}: sem 'hook' (o gancho que puxa a próxima cena)")
        js = root / "src" / "scenes" / f"{sid}.js"
        if not js.is_file():
            rep.error(f"{where}: falta src/scenes/{sid}.js (use `pycode deck scene add`)")
    return scenes


def check_scene_code(sid: str, code: str, rep: Report) -> None:
    if not re.search(r"SCENES\[\s*['\"]%s['\"]\s*\]\s*=" % re.escape(sid), code):
        rep.error(f"src/scenes/{sid}.js: não registra window.SCENES['{sid}']")
    for pattern, label in SCENE_FORBIDDEN:
        hit = re.search(pattern, code)
        if hit:
            line = code[:hit.start()].count("\n") + 1
            rep.error(f"src/scenes/{sid}.js:{line}: {label}")
    for pattern, label in SCENE_REQUIRED:
        if not re.search(pattern, code):
            rep.error(f"src/scenes/{sid}.js: sem {label}")
    if not re.search(r"\bstill\b", code):
        rep.warn(f"src/scenes/{sid}.js: sem still() (o ?still usa home())")


def strip_keyframes(css: str) -> str:
    out, i = [], 0
    for m in re.finditer(r"@keyframes[^{]+\{", css):
        if m.start() < i:
            continue
        out.append(css[i:m.start()])
        depth, j = 1, m.end()
        while j < len(css) and depth:
            depth += {"{": 1, "}": -1}.get(css[j], 0)
            j += 1
        i = j
    out.append(css[i:])
    return "".join(out)


def check_scene_css(sid: str, css: str, rep: Report) -> None:
    body = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for m in COLOR_RE.finditer(body):
        line = body[:m.start()].count("\n") + 1
        rep.error(f"src/scenes/{sid}.css:{line}: cor fixa {m.group(0)!r} (use as variáveis do contrato de estilos)")
    flat = strip_keyframes(body)
    flat = re.sub(r"@media[^{]+\{", "", flat)
    for sel in re.findall(r"([^{}]+)\{", flat):
        for part in sel.split(","):
            part = part.strip()
            if part and not part.startswith("@") and f".s-{sid}" not in part:
                rep.error(f"src/scenes/{sid}.css: seletor sem o prefixo .s-{sid}: {part[:60]!r}")


def check_shared_css(name: str, css: str, rep: Report, allow=("#000",)) -> None:
    body = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for m in COLOR_RE.finditer(body):
        if m.group(0) in allow:
            continue
        line = body[:m.start()].count("\n") + 1
        rep.error(f"src/css/{name}:{line}: cor fixa {m.group(0)!r} (use as variáveis do contrato de estilos)")


def check_text(content: dict, rep: Report) -> None:
    runtime = {k: v for k, v in content.items() if k != "ui"}
    joined = "\n".join(text_strings(runtime))
    for level, message, ctx in T.lint(joined):
        (rep.error if level == "erro" else rep.warn)(f"texto: {message}" + (f" · {ctx}" if ctx else ""))
    hit = EMOJI_RE.search(joined)
    if hit:
        rep.error(f"texto: emoji ou glifo decorativo {hit.group(0)!r}")


def render_slide(n: int, total: int, s: dict, ui: dict) -> str:
    sid = s["id"]
    data = [f'data-id="{sid}"', f'data-title="{attr(s.get("title"))}"', f'data-transition="{s.get("transition", "corte")}"']
    if s.get("chapter"):
        data.append(f'data-chapter="{attr(s["chapter"])}"')
    if s.get("bg"):
        data.append(f'data-bg="{attr(s["bg"])}"')
    if str(s.get("accent", "")) in ("2", "accent-2"):
        data.append('data-accent="2"')
    label = f'{ui["scene"]} {n} de {total}: {attr(s.get("title"))}'
    parts = [f'<section class="slide s-{sid}" {" ".join(data)} aria-roledescription="slide" aria-label="{label}">']
    parts.append(f'  <header class="sc-head"><h2 class="slide-title">{inline(s.get("title"))}</h2>'
                 + (f'<p class="apoio">{inline(s.get("apoio"))}</p>' if s.get("apoio") else "") + "</header>")
    parts.append('  <div class="fill" data-fill></div>')
    items = s.get("reading") or []
    if items:
        lis = []
        for it in items:
            if isinstance(it, str):
                lis.append(f"<li><p>{inline(it)}</p></li>")
                continue
            li = ""
            if it.get("label"):
                li += f"<span>{inline(it['label'])}</span>"
            if it.get("title"):
                li += f"<b>{inline(it['title'])}</b>"
            if it.get("text"):
                li += f"<p>{inline(it['text'])}</p>"
            if it.get("code"):
                li += f"<p><code>{html.escape(it['code'])}</code></p>"
            lis.append(f"<li>{li}</li>")
        parts.append(f'  <ul class="rd-only">{"".join(lis)}</ul>')
    if s.get("hook"):
        parts.append(f'  <p class="hook">{inline(s["hook"])}</p>')
    parts.append("</section>")
    return "\n".join(parts)


def external_refs(site: Path) -> list[str]:
    """Recursos carregados de fora do projeto (CDN, fontes remotas, scripts de terceiros)."""
    bad = []
    index = (site / "index.html").read_text(encoding="utf-8")
    for m in re.finditer(r"<(script|link|img|iframe|video|audio|source|embed|object)\b[^>]*?\b(?:src|href|data)=[\"']((?:https?:)?//[^\"']+)", index, re.I):
        bad.append(f"index.html: <{m.group(1)}> {m.group(2)}")
    for css in site.rglob("*.css"):
        text = css.read_text(encoding="utf-8")
        for m in re.finditer(r"url\(\s*['\"]?((?:https?:)?//[^'\")]+)|@import\s+[^;]+", text):
            bad.append(f"{css.relative_to(site)}: {m.group(0)[:80]}")
    js = (site / "assets/js/deck.js").read_text(encoding="utf-8")
    for m in re.finditer(r"https?://(?!www\.w3\.org/)[^\s'\"`)]+", js):
        bad.append(f"assets/js/deck.js: {m.group(0)}")
    return bad


def build(root: Path, strict: bool = False, quiet: bool = False) -> dict:
    cfg, content = load_project(root)
    rep = Report()
    src, site = root / "src", root / "site"
    scenes = check_content(content, root, rep)
    ui = {**UI_DEFAULTS, **(content.get("ui") or {})}
    check_text(content, rep)
    for name in ("engine.css", "base.css"):
        check_shared_css(name, (src / "css" / name).read_text(encoding="utf-8"), rep)
    scene_js, scene_css = [], []
    for s in scenes:
        sid = s.get("id", "")
        js, css = src / "scenes" / f"{sid}.js", src / "scenes" / f"{sid}.css"
        if js.is_file():
            code = js.read_text(encoding="utf-8")
            check_scene_code(sid, code, rep)
            scene_js.append(f"/* --- scenes/{sid}.js --- */\n{code.strip()}\n")
        if css.is_file():
            text = css.read_text(encoding="utf-8")
            check_scene_css(sid, text, rep)
            scene_css.append(f"/* --- scenes/{sid}.css --- */\n{text.strip()}\n")
    for w in rep.warnings:
        print(f"[aviso] {w}")
    if rep.errors or (strict and rep.warnings):
        for e in rep.errors:
            print(f"[erro] {e}", file=sys.stderr)
        paths.die(f"build recusado: {len(rep.errors)} erro(s)" + (f" e {len(rep.warnings)} aviso(s) (--strict)" if strict and rep.warnings else ""))

    # montar site/
    if site.exists():
        shutil.rmtree(site)
    (site / "assets/css").mkdir(parents=True)
    (site / "assets/js").mkdir(parents=True)
    for folder in ("fonts", "vendor", "img", "media"):
        if (root / "assets" / folder).is_dir():
            shutil.copytree(root / "assets" / folder, site / "assets" / folder)
    if not (site / "assets/vendor/gsap.min.js").is_file():
        paths.die("assets/vendor/gsap.min.js não existe. Rode `pycode vendor` e recrie o projeto, ou copie o GSAP com o vendor.")
    css_parts = [f"/* gerado por pycode deck build a partir de src/css e src/scenes; edite as fontes */"]
    for name in ("tokens.css", "fonts.css", "engine.css", "base.css"):
        f = src / "css" / name
        if f.is_file():
            css_parts.append(f"/* --- css/{name} --- */\n" + f.read_text(encoding="utf-8").strip() + "\n")
    css_bytes = "\n".join(css_parts + scene_css).encode()
    (site / "assets/css/deck.css").write_bytes(css_bytes)
    js_parts = [(src / "js/fx.js").read_text(encoding="utf-8"), *scene_js, (src / "js/deck.js").read_text(encoding="utf-8")]
    js_bytes = "\n".join(js_parts).encode()
    (site / "assets/js/deck.js").write_bytes(js_bytes)
    runtime = {"meta": content.get("meta", {}), "ui": ui,
               "scenes": [{k: v for k, v in s.items() if k not in ("notes", "study")} for s in scenes]}
    content_bytes = ("window.DECK = " + json.dumps(runtime, ensure_ascii=False, indent=1) + ";\n").encode()
    (site / "assets/js/content.js").write_bytes(content_bytes)

    total = len(scenes)
    slides_html = "\n".join(render_slide(n, total, s, ui) for n, s in enumerate(scenes, start=1))
    stops = "".join(f'<i class="stop" style="left:{(i / max(1, total - 1)) * 100:.3f}%"></i>' for i in range(total))
    brand = cfg.get("brand") or {}
    brand_html = (f'<img src="assets/img/{html.escape(Path(brand["logo"]).name)}" alt="">' if brand.get("logo") else "<i></i>")
    brand_html += f'<span>{html.escape(brand.get("name") or "")}</span>'
    if content.get("meta", {}).get("short"):
        brand_html += f' <small>· {html.escape(content["meta"]["short"])}</small>'
    fonts = sorted((site / "assets/fonts").glob("*.woff2")) if (site / "assets/fonts").is_dir() else []
    preloads = "\n".join(f'<link rel="preload" href="assets/fonts/{f.name}" as="font" type="font/woff2" crossorigin>' for f in fonts[:2])
    head_extra = (src / "head-extra.html").read_text(encoding="utf-8").strip() if (src / "head-extra.html").is_file() else ""
    meta = content.get("meta", {})
    shell = (src / "shell.html").read_text(encoding="utf-8")
    tokens = {
        "LANG": cfg.get("lang", "pt-BR"), "TITLE": attr(meta.get("title")), "DESCRIPTION": attr(meta.get("description") or meta.get("subtitle") or ""),
        "ENGINE_VERSION": ENGINE_VERSION, "VERSION": attr(cfg.get("version", "1.0.0")), "STORAGE_KEY": attr(cfg.get("slug", "aula")),
        "MODE": "light" if cfg.get("mode") == "light" else "dark",
        "FONT_PRELOADS": preloads, "HEAD_EXTRA": head_extra, "SLIDES": slides_html, "THREAD_STOPS": stops, "BRAND": brand_html,
        "H_CSS": short_hash(css_bytes), "H_JS": short_hash(js_bytes), "H_CONTENT": short_hash(content_bytes),
        "H_GSAP": short_hash((site / "assets/vendor/gsap.min.js").read_bytes()),
    }
    for key, value in ui.items():
        snake = re.sub(r"([A-Z])", r"_\1", key).upper()
        tokens[f"UI_{snake}"] = value if key in ("keys", "help") else html.escape(value)
    out = re.sub(r"\{\{([A-Z0-9_]+)\}\}", lambda m: tokens.get(m.group(1), m.group(0)), shell)
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}", out)
    if left:
        paths.die(f"marcadores sem valor no shell.html: {sorted(set(left))}")
    (site / "index.html").write_text(out, encoding="utf-8")
    bad = external_refs(site)
    if bad:
        for b in bad:
            print(f"[erro] recurso externo em tempo de execução: {b}", file=sys.stderr)
        (site / "index.html").unlink()   # não deixa um site recusado pronto para servir
        paths.die("build recusado: o deck precisa abrir sem internet (fontes e bibliotecas dentro do projeto)")
    files = []
    for f in sorted(site.rglob("*")):
        if f.is_file():
            files.append({"path": f.relative_to(site).as_posix(), "bytes": f.stat().st_size, "sha": short_hash(f.read_bytes())})
    summary = {"title": meta.get("title"), "scenes": [s["id"] for s in scenes], "engine": ENGINE_VERSION,
               "version": cfg.get("version"), "style": cfg.get("style"), "warnings": len(rep.warnings),
               "bytes": sum(f["bytes"] for f in files)}
    write_json(site / "build.json", {**summary, "files": files})
    if not quiet:
        print(json.dumps(summary, ensure_ascii=False))
        print(f"site: {site / 'index.html'}")
        print(f"prévia: pycode serve {site}")
    return summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pycode deck build", description="Monta site/ a partir de src/ (cache-busting por hash) e confere ids, contrato das cenas, cores do estilo, recursos externos e texto.")
    ap.add_argument("pasta", nargs="?", help="pasta do projeto (padrão: a atual)")
    ap.add_argument("--strict", action="store_true", help="avisos também recusam o build")
    args = ap.parse_args(argv)
    build(find_project(args.pasta), strict=args.strict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
