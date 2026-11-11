"""Comandos centrais do `pycode` (os grupos de cada skill ficam em skills/<skill>/scripts)."""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

from . import paths

SIMPLE_ICONS = "16.37.0"
NODE_TOOLS = ("csso", "lighthouse", "mmdc")


# ---------------------------------------------------------------- utilidades
def node_bin(name):
    local = paths.HOME / "node_tools" / "node_modules" / ".bin" / name
    return str(local) if local.exists() else (shutil.which(name) or "")


def node_exe():
    bundled = paths.HOME / "node" / "bin" / "node"
    return str(bundled) if bundled.exists() else (shutil.which("node") or "")


def _node_env():
    env = dict(os.environ)
    bundled = paths.HOME / "node" / "bin"
    if bundled.is_dir():
        env["PATH"] = str(bundled) + os.pathsep + env.get("PATH", "")
    return env


def _is_url(target):
    return bool(re.match(r"^https?://", target))


def _sizes(text):
    out = []
    for part in text.split(","):
        m = re.fullmatch(r"\s*(\d+)x(\d+)\s*", part)
        if not m:
            paths.die(f"tamanho inválido: {part!r} (use LARGURAxALTURA, ex.: 1440x900,390x844)")
        out.append((int(m.group(1)), int(m.group(2))))
    return out


# ---------------------------------------------------------------- doctor
def cmd_doctor(argv):
    ap = argparse.ArgumentParser(prog="pycode doctor", description="Confere a instalação.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    checks = []

    def add(name, ok, detail, required=True, fix=""):
        checks.append({"name": name, "ok": bool(ok), "required": required, "detail": detail, "fix": fix})

    add("python", sys.version_info >= (3, 10), sys.version.split()[0], fix="instale Python 3.10+ e rode `pycode setup`")
    venv = paths.HOME / "venv"
    add("ambiente", venv.is_dir() and Path(sys.executable).resolve().is_relative_to(venv.resolve()) or sys.prefix != sys.base_prefix,
        str(venv), fix="rode `pycode setup`")
    for module, label in (("playwright", "playwright"), ("PIL", "pillow"), ("numpy", "numpy"), ("cv2", "opencv"), ("yaml", "pyyaml")):
        try:
            __import__(module)
            add(label, True, "ok")
        except ImportError:
            add(label, False, "não instalado", fix="rode `pycode setup`")
    try:
        from .browser import chromium
        with chromium() as browser:
            page = browser.new_page()
            page.set_content("<p>ok</p>")
            add("chromium", page.inner_text("p") == "ok", browser.version)
    except SystemExit:
        add("chromium", False, "não abriu", fix="rode `pycode setup`; no Linux pode faltar `sudo ~/.pycode-skills/venv/bin/python -m playwright install-deps chromium`")
    try:
        import imageio_ffmpeg
        add("ffmpeg", True, imageio_ffmpeg.get_ffmpeg_exe(), required=False)
    except Exception as exc:  # noqa: BLE001
        add("ffmpeg", False, str(exc), required=False, fix="rode `pycode setup` (slides em vídeo dependem dele)")
    node = node_exe()
    node_version = subprocess.run([node, "-v"], capture_output=True, text=True).stdout.strip() if node else ""
    major = int(re.sub(r"\D.*", "", node_version.lstrip("v")) or 0) if node_version else 0
    add("node", major >= 18, node_version or "não encontrado", fix="rode `pycode setup` (instala o Node em ~/.pycode-skills/node)")
    for tool in NODE_TOOLS:
        add(f"node:{tool}", bool(node_bin(tool)), node_bin(tool) or "não instalado", required=tool != "mmdc", fix="rode `pycode setup`")
    from . import vendor
    try:
        miss = vendor.missing()
        add("fontes e js", not miss, f"{len(miss)} arquivo(s) faltando" if miss else str(paths.VENDOR), fix="rode `pycode vendor`")
    except Exception as exc:  # noqa: BLE001
        add("fontes e js", False, str(exc), fix="rode `pycode vendor`")
    skills = sorted(p.parent.name for p in paths.SKILLS.glob("*/SKILL.md"))
    add("skills", bool(skills), ", ".join(skills) or "nenhuma")
    linked = []
    for agent, folder in agent_dirs().items():
        found = [s for s in skills if (folder / s / "SKILL.md").exists()]
        if found:
            linked.append(f"{agent} ({len(found)})")
    add("agentes", bool(linked), ", ".join(linked) or "nenhum agente com as skills instaladas", required=False,
        fix="rode o install.sh com --agent <claude|codex|opencode|cursor|hermes|all>")
    add("marca", paths.BRAND_FILE.is_file(), str(paths.BRAND_FILE), required=False, fix="rode `pycode brand --init` e edite o arquivo")
    refs = sorted(p.name for p in paths.REFS.glob("*") if p.is_dir()) if paths.REFS.is_dir() else []
    add("referências", bool(refs), ", ".join(refs) or "galerias externas ainda não baixadas", required=False, fix="opcional: `pycode refs fetch`")

    failed = [c for c in checks if c["required"] and not c["ok"]]
    if args.json:
        print(json.dumps({"version": paths.version(), "home": str(paths.HOME), "src": str(paths.SRC), "ok": not failed, "checks": checks}, indent=2, ensure_ascii=False))
    else:
        print(f"pycode {paths.version()} · {paths.SRC}")
        for c in checks:
            mark = "ok " if c["ok"] else ("FALTA" if c["required"] else "opcional")
            print(f"  [{mark:^8}] {c['name']:<14} {c['detail']}")
            if not c["ok"] and c["fix"]:
                print(f"{'':13}→ {c['fix']}")
        print("\nTudo certo." if not failed else f"\n{len(failed)} item(ns) obrigatório(s) com problema.")
    return 1 if failed else 0


def agent_dirs():
    home = Path.home()
    return {
        "claude": home / ".claude" / "skills",
        "codex": home / ".agents" / "skills",
        "opencode": home / ".config" / "opencode" / "skills",
        "cursor": home / ".cursor" / "skills",
        "gemini": home / ".gemini" / "skills",
        "hermes": home / ".hermes" / "skills" / "creative",
    }


# ---------------------------------------------------------------- brand / vendor
def cmd_brand(argv):
    ap = argparse.ArgumentParser(prog="pycode brand", description="Marca usada nos artefatos (nome, @, site, cores, logo).")
    ap.add_argument("--init", action="store_true", help="cria o arquivo com valores neutros, se não existir")
    args = ap.parse_args(argv)
    if args.init and paths.ensure_brand_file():
        paths.say(f"criado {paths.BRAND_FILE}")
    print(json.dumps(paths.load_brand(), indent=2, ensure_ascii=False))
    if not paths.BRAND_FILE.is_file():
        paths.say("arquivo ainda não existe: rode `pycode brand --init` e edite com os dados da sua marca")
    return 0


def cmd_vendor(argv):
    ap = argparse.ArgumentParser(prog="pycode vendor", description="Baixa fontes (OFL) e bibliotecas JS para o cache local.")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)
    from . import vendor
    if args.list:
        data = vendor.manifest()
        print("Fontes:", ", ".join(f["id"] for f in data["fonts"]))
        print("JS:", ", ".join(j["id"] for j in data["js"]))
        return 0
    vendor.ensure(force=args.force)
    return 0


# ---------------------------------------------------------------- shot / serve / sheet
def cmd_shot(argv):
    ap = argparse.ArgumentParser(prog="pycode shot", description="Captura uma página (URL, arquivo ou pasta) em vários tamanhos.")
    ap.add_argument("target")
    ap.add_argument("--sizes", default="1440x900,390x844")
    ap.add_argument("--out", default="shots")
    ap.add_argument("--name", default="shot")
    ap.add_argument("--full", action="store_true", help="página inteira")
    ap.add_argument("--wait", type=int, default=800, help="espera em ms depois do carregamento")
    ap.add_argument("--selector", help="captura só este elemento")
    ap.add_argument("--reduced-motion", action="store_true")
    ap.add_argument("--audit", action="store_true", help="relata overflow, imagens quebradas e erros de console")
    ap.add_argument("--scale", type=float, default=1)
    args = ap.parse_args(argv)
    from .browser import audit, chromium, new_page
    from .server import serve
    import contextlib

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with contextlib.ExitStack() as stack:
        if _is_url(args.target):
            url = args.target
        else:
            target = Path(args.target).resolve()
            if not target.exists():
                paths.die(f"não encontrei {target}")
            root, rel = (target, "") if target.is_dir() else (target.parent, target.name)
            url = stack.enter_context(serve(root)) + "/" + rel
        browser = stack.enter_context(chromium())
        report, problems = [], 0
        for w, h in _sizes(args.sizes):
            page = new_page(browser, w, h, scale=args.scale, reduced_motion=args.reduced_motion, mobile=w < 600)
            page.goto(url, wait_until="load")
            page.wait_for_timeout(args.wait)
            file = out / f"{args.name}-{w}x{h}.png"
            if args.selector:
                page.locator(args.selector).first.screenshot(path=str(file))
            else:
                page.screenshot(path=str(file), full_page=args.full)
            entry = {"size": f"{w}x{h}", "file": str(file)}
            if args.audit:
                entry["audit"] = audit(page)
                a = entry["audit"]
                problems += bool(a["horizontalOverflow"]) + len(a["brokenImages"]) + len(a["consoleErrors"]) + len(a["failedRequests"]) + len(a["fontsFailed"])
            report.append(entry)
            print(file)
            page.context.close()
        if args.audit:
            (out / f"{args.name}-audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
            for entry in report:
                a = entry["audit"]
                print(f"{entry['size']}: overflow={a['horizontalOverflow']} imagens_quebradas={len(a['brokenImages'])} "
                      f"console={len(a['consoleErrors'])} rede={len(a['failedRequests'])} fontes_com_erro={len(a['fontsFailed'])} texto<12px={a['tinyTextNodes']}")
            return 1 if problems else 0
    return 0


def cmd_serve(argv):
    ap = argparse.ArgumentParser(prog="pycode serve", description="Prévia local de uma pasta (só em 127.0.0.1).")
    ap.add_argument("dir", nargs="?", default=".")
    ap.add_argument("--port", type=int, default=8080)
    args = ap.parse_args(argv)
    from .server import make_server
    root = Path(args.dir).resolve()
    if not root.is_dir():
        paths.die(f"pasta não encontrada: {root}")
    httpd = make_server(root, args.port)
    print(f"Servindo {root} em http://127.0.0.1:{httpd.server_address[1]}  (Ctrl+C encerra)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


def cmd_sheet(argv):
    ap = argparse.ArgumentParser(prog="pycode sheet", description="Folha de contato para revisar várias capturas de uma vez.")
    ap.add_argument("images", nargs="+")
    ap.add_argument("--out", default="folha-de-contato.jpg")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--width", type=int, default=480, help="largura de cada miniatura")
    args = ap.parse_args(argv)
    from .images import contact_sheet
    files = []
    for item in args.images:
        p = Path(item)
        files += sorted(q for q in p.iterdir() if q.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")) if p.is_dir() else [p]
    print(contact_sheet(files, args.out, cols=args.cols, thumb_width=args.width))
    return 0


# ---------------------------------------------------------------- text / contrast
def cmd_text(argv):
    ap = argparse.ArgumentParser(prog="pycode text", description="Revisão mecânica de texto PT-BR em .html, .md, .json e .txt.")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--max-words", type=int, help="limite de palavras por arquivo (útil para slides)")
    ap.add_argument("--allow-dash", action="store_true", help="não avisar sobre travessão")
    ap.add_argument("--strict", action="store_true", help="avisos também reprovam")
    args = ap.parse_args(argv)
    from . import text as T
    errors = warnings = 0
    for item in args.files:
        content = T.extract(item)
        issues = T.lint(content, allow_dash=args.allow_dash)
        count = T.words(content)
        if args.max_words and count > args.max_words:
            issues.append(("erro", f"{count} palavras (limite {args.max_words})", ""))
        if issues:
            print(f"{item}  ({count} palavras)")
        for level, message, ctx in issues:
            errors += level == "erro"
            warnings += level == "aviso"
            print(f"  [{level}] {message}" + (f"  · …{ctx}…" if ctx else ""))
    print(f"{len(args.files)} arquivo(s): {errors} erro(s), {warnings} aviso(s)")
    return 1 if errors or (args.strict and warnings) else 0


def cmd_contrast(argv):
    ap = argparse.ArgumentParser(prog="pycode contrast", description="Contraste WCAG entre texto e fundo (ex.: '#fff' '#0b0b11').")
    ap.add_argument("fg")
    ap.add_argument("bg")
    ap.add_argument("--min", type=float, default=4.5)
    args = ap.parse_args(argv)
    from .color import ratio
    value = ratio(args.fg, args.bg)
    verdict = "passa" if value >= args.min else "reprova"
    print(f"{value:.2f}:1  ({verdict} em {args.min}:1; texto grande aceita 3:1)")
    return 0 if value >= args.min else 1


# ---------------------------------------------------------------- icon
def cmd_icon(argv):
    ap = argparse.ArgumentParser(prog="pycode icon", description="Baixa um ícone do Simple Icons (CC0). Marcas continuam sendo dos seus donos.")
    ap.add_argument("slug", help="ex.: python, django, docker, github")
    ap.add_argument("--out", help="arquivo .svg de saída (padrão: <slug>.svg)")
    ap.add_argument("--color", help="cor de preenchimento, ex.: '#ffffff'")
    args = ap.parse_args(argv)
    url = f"https://cdn.jsdelivr.net/npm/simple-icons@{SIMPLE_ICONS}/icons/{args.slug}.svg"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "pycode-skills"}), timeout=30) as r:
            svg = r.read().decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        paths.die(f"ícone não encontrado ({args.slug}): {exc}. Consulte os nomes em https://simpleicons.org")
    if args.color:
        svg = svg.replace("<svg ", f'<svg fill="{args.color}" ', 1)
    out = Path(args.out or f"{args.slug}.svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print(out)
    return 0


# ---------------------------------------------------------------- mermaid / lighthouse / css
def _chrome_flags():
    flags = ["--headless=new", "--disable-gpu"]
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        flags.append("--no-sandbox")
    return flags


def cmd_mermaid(argv):
    ap = argparse.ArgumentParser(prog="pycode mermaid", description="Valida um diagrama Mermaid renderizando-o (SVG ou PNG).")
    ap.add_argument("file")
    ap.add_argument("--out", help="saída .svg ou .png (padrão: mesmo nome com .svg)")
    ap.add_argument("--theme", default="default")
    ap.add_argument("--background", default="transparent")
    args = ap.parse_args(argv)
    mmdc = node_bin("mmdc")
    if not mmdc:
        paths.die("mermaid-cli não instalado. Rode `pycode setup`.")
    from .browser import chromium_path
    chrome = chromium_path()
    if not chrome:
        paths.die("Chromium não encontrado. Rode `pycode setup`.")
    src = Path(args.file)
    out = Path(args.out or src.with_suffix(".svg"))
    config = paths.HOME / "puppeteer.json"
    config.write_text(json.dumps({"executablePath": chrome, "args": [f for f in _chrome_flags() if f != "--headless=new"]}), encoding="utf-8")
    result = subprocess.run([mmdc, "-i", str(src), "-o", str(out), "-t", args.theme, "-b", args.background, "-p", str(config)],
                            capture_output=True, text=True, env=_node_env())
    if result.returncode != 0 or not out.exists():
        print((result.stderr or result.stdout).strip(), file=sys.stderr)
        paths.die("o diagrama não renderizou: corrija a sintaxe e rode de novo")
    print(out)
    return 0


def cmd_lighthouse(argv):
    ap = argparse.ArgumentParser(prog="pycode lighthouse", description="Lighthouse com o Chromium da instalação. Salva JSON e HTML.")
    ap.add_argument("url")
    ap.add_argument("--out", default="lighthouse")
    ap.add_argument("--desktop", action="store_true", help="perfil desktop (padrão: celular)")
    ap.add_argument("--block", action="append", default=[], help="padrão de URL a bloquear (repita a opção); mede só o que é seu")
    ap.add_argument("--name", default="relatorio")
    args = ap.parse_args(argv)
    lh = node_bin("lighthouse")
    if not lh:
        paths.die("lighthouse não instalado. Rode `pycode setup`.")
    from .browser import chromium_path
    chrome = chromium_path()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    base = out / args.name
    cmd = [lh, args.url, "--quiet", "--output=json", "--output=html", f"--output-path={base}",
           "--chrome-flags=" + " ".join(_chrome_flags())]
    if args.desktop:
        cmd.append("--preset=desktop")
    for pattern in args.block:
        cmd.append(f"--blocked-url-patterns={pattern}")
    env = _node_env()
    env["CHROME_PATH"] = chrome
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    report = Path(f"{base}.report.json")
    if result.returncode != 0 or not report.exists():
        print((result.stderr or result.stdout).strip()[-2000:], file=sys.stderr)
        paths.die("o Lighthouse falhou")
    data = json.loads(report.read_text(encoding="utf-8"))
    scores = {k: round((v.get("score") or 0) * 100) for k, v in data["categories"].items()}
    audits = data["audits"]
    metrics = {k: audits[k]["displayValue"] for k in ("first-contentful-paint", "largest-contentful-paint", "total-blocking-time", "cumulative-layout-shift", "speed-index") if k in audits and "displayValue" in audits[k]}
    print(json.dumps({"scores": scores, "metrics": metrics, "bytes": audits.get("total-byte-weight", {}).get("numericValue"),
                      "json": str(report), "html": f"{base}.report.html"}, indent=2, ensure_ascii=False))
    return 0


def cmd_css(argv):
    ap = argparse.ArgumentParser(prog="pycode css", description="Minifica CSS (csso) e incorpora o CSS crítico no HTML.")
    sub = ap.add_subparsers(dest="action", required=True)
    m = sub.add_parser("minify", help="gera o .min.css")
    m.add_argument("input")
    m.add_argument("-o", "--output")
    c = sub.add_parser("critical", help="minifica o CSS crítico e grava dentro de <style id=\"critical-css\"> no HTML")
    c.add_argument("html")
    c.add_argument("--css", required=True)
    c.add_argument("--max-kb", type=float, default=15, help="limite do CSS crítico minificado")
    args = ap.parse_args(argv)
    csso = node_bin("csso")
    if not csso:
        paths.die("csso não instalado. Rode `pycode setup`.")

    def minify(src):
        result = subprocess.run([csso, str(src)], capture_output=True, text=True, env=_node_env())
        if result.returncode != 0:
            print(result.stderr.strip(), file=sys.stderr)
            paths.die(f"não consegui minificar {src}")
        return result.stdout.strip()

    if args.action == "minify":
        src = Path(args.input)
        out = Path(args.output or src.with_suffix(".min.css"))
        css = minify(src)
        out.write_text(css + "\n", encoding="utf-8")
        print(f"{out}  {len(css.encode()) / 1024:.1f} KB")
        return 0
    html_file = Path(args.html)
    html = html_file.read_text(encoding="utf-8")
    pattern = re.compile(r'(<style id="critical-css">)(.*?)(</style>)', re.S)
    if not pattern.search(html):
        paths.die(f'{html_file} não tem o bloco <style id="critical-css"></style>')
    css = minify(args.css)
    size = len(css.encode()) / 1024
    if size > args.max_kb:
        paths.die(f"CSS crítico com {size:.1f} KB (limite {args.max_kb} KB): deixe só o que a primeira dobra usa")
    html_file.write_text(pattern.sub(lambda m: m.group(1) + css + m.group(3), html, count=1), encoding="utf-8")
    print(f"CSS crítico incorporado em {html_file}  ({size:.1f} KB)")
    return 0


COMMANDS = {
    "doctor": cmd_doctor, "brand": cmd_brand, "vendor": cmd_vendor, "shot": cmd_shot, "serve": cmd_serve,
    "sheet": cmd_sheet, "text": cmd_text, "contrast": cmd_contrast, "icon": cmd_icon, "mermaid": cmd_mermaid,
    "lighthouse": cmd_lighthouse, "css": cmd_css,
}


def run(name, argv):
    return COMMANDS[name](argv)
