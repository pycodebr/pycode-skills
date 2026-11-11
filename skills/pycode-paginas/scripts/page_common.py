"""Funções compartilhadas pelos comandos `pycode page ...` (skill pycode-paginas).

Tudo aqui é pequeno e sem dependência além de tools/requirements.txt.
"""
import contextlib
import functools
import gzip
import hashlib
import html.parser
import http.server
import io
import json
import re
import socketserver
import threading
from pathlib import Path

from pycode_tools import paths

SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_DIR / "templates"
CONFIG_NAME = "pycode-page.json"
METRICS_FILE = Path(__file__).resolve().parent / "font_metrics.json"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
# Elementos cujo fechamento o HTML permite omitir; o balanceador aceita que fechem implicitamente.
OPTIONAL_CLOSE = {"li", "dt", "dd", "p", "tr", "td", "th", "thead", "tbody", "tfoot", "option", "colgroup"}
SERIF = {"fraunces", "playfair-display", "instrument-serif"}
MONO = {"geist-mono", "jetbrains-mono", "vt323", "press-start-2p"}
LOCAL_FALLBACK = {
    "sans": ("Arial", "Liberation Sans", "Helvetica"),
    "serif": ("Times New Roman", "Liberation Serif", "Times"),
    "mono": ("Courier New", "Liberation Mono", "Menlo"),
}
SAMPLE = "Uma requisição sai do navegador, passa pelo servidor e volta com dados 0123456789"


# ---------------------------------------------------------------- projeto
def find_project(target=None):
    """Devolve (raiz, config) do projeto criado por `pycode page new`, procurando para cima."""
    start = Path(target or ".").resolve()
    for folder in [start, *start.parents]:
        cfg = folder / CONFIG_NAME
        if cfg.is_file():
            return folder, json.loads(cfg.read_text(encoding="utf-8"))
    return None, None


def require_project(target=None):
    root, cfg = find_project(target)
    if root is None:
        paths.die(f"não encontrei {CONFIG_NAME} em {Path(target or '.').resolve()} nem acima. "
                  "Crie o projeto com `pycode page new <pasta> --title \"...\"`.")
    return root, cfg


def save_config(root, cfg):
    (root / CONFIG_NAME).write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(data):
    if isinstance(data, Path):
        data = data.read_bytes()
    return hashlib.sha256(data).hexdigest()


def tree_digest(folder):
    """Hash estável de uma pasta inteira (nome relativo + conteúdo), para provar build reproduzível."""
    folder = Path(folder)
    out = {}
    for file in sorted(p for p in folder.rglob("*") if p.is_file()):
        out[file.relative_to(folder).as_posix()] = sha256(file)
    return out


# ---------------------------------------------------------------- tokens e fontes
def parse_tokens(css):
    """Lê as variáveis `--nome: valor;` de um tokens.css (último valor vence)."""
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;}]+)", css)}


def first_family(value):
    """'Geist', system-ui, sans-serif -> Geist"""
    part = (value or "").split(",")[0].strip()
    return part.strip("'\"")


def font_category(fid):
    return "serif" if fid in SERIF else "mono" if fid in MONO else "sans"


def vendor_fonts(ids):
    from pycode_tools import vendor
    data = {f["id"]: f for f in vendor.manifest()["fonts"]}
    missing = [i for i in ids if i not in data]
    if missing:
        paths.die(f"fonte desconhecida: {', '.join(missing)}. Disponíveis: {', '.join(sorted(data))}")
    return [data[i] for i in ids]


def load_metrics():
    if METRICS_FILE.is_file():
        return json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    return {}


def measure_metrics(fonts):
    """Mede no Chromium a largura e as alturas de cada fonte contra a fonte local equivalente.

    Devolve {id: {size_adjust, ascent, descent}} em porcentagem, pronto para o @font-face de fallback.
    """
    import base64
    from pycode_tools import vendor
    from pycode_tools.browser import chromium

    faces, jobs = [], []
    for font in fonts:
        item = next((i for i in font["files"] if i["style"] == "normal"), font["files"][0])
        src = vendor.font_path(font, item)
        if not src.is_file():
            vendor.ensure(quiet=True)
        b64 = base64.b64encode(src.read_bytes()).decode()
        faces.append("@font-face{font-family:'M-%s';src:url(data:font/woff2;base64,%s) format('woff2');font-weight:%s}"
                     % (font["id"], b64, item["weight"]))
        jobs.append({"id": font["id"], "local": LOCAL_FALLBACK[font_category(font["id"])][1]})
    script = """async ([jobs, sample]) => {
      const out = {}; const size = 100;
      const ctx = document.createElement('canvas').getContext('2d');
      for (const job of jobs) {
        await document.fonts.load(`400 ${size}px "M-${job.id}"`);
        ctx.font = `400 ${size}px "M-${job.id}"`;
        const web = ctx.measureText(sample);
        ctx.font = `400 ${size}px "${job.local}"`;
        const local = ctx.measureText(sample);
        out[job.id] = {ratio: web.width / local.width, ascent: web.fontBoundingBoxAscent / size,
                       descent: web.fontBoundingBoxDescent / size};
      }
      return out;
    }"""
    with chromium() as browser:
        page = browser.new_page()
        page.set_content(f"<style>{''.join(faces)}</style><p>x</p>")
        raw = page.evaluate(script, [jobs, SAMPLE])
    out = {}
    for fid, m in raw.items():
        ratio = m["ratio"] or 1
        out[fid] = {"size_adjust": round(ratio * 100, 2), "ascent": round(m["ascent"] / ratio * 100, 2),
                    "descent": round(m["descent"] / ratio * 100, 2)}
    return out


def fallback_css(fonts):
    """@font-face de fallback métrico (fonte local ajustada) para reduzir o salto de layout na troca da fonte."""
    metrics = load_metrics()
    todo = [f for f in fonts if f["id"] not in metrics]
    if todo:
        metrics.update(measure_metrics(todo))
    css = []
    for font in fonts:
        m = metrics[font["id"]]
        local = ", ".join(f"local('{name}')" for name in LOCAL_FALLBACK[font_category(font["id"])])
        css.append("@font-face{font-family:'%s Fallback';src:%s;size-adjust:%s%%;ascent-override:%s%%;"
                   "descent-override:%s%%;line-gap-override:0%%}" % (font["family"], local, m["size_adjust"],
                                                                     m["ascent"], m["descent"]))
    return "\n".join(css) + "\n"


def add_fallback_families(tokens_css, fonts):
    """Insere 'Família Fallback' logo depois da família web em --font-display/--font-body/--font-mono."""
    families = {f["family"] for f in fonts}

    def fix(match):
        name, value = match.group(1), match.group(2)
        fam = first_family(value)
        if fam in families and f"{fam} Fallback" not in value:
            head, _, rest = value.partition(",")
            value = f"{head}, '{fam} Fallback'," + rest if rest else f"{head}, '{fam} Fallback'"
        return f"{name}: {value}"
    return re.sub(r"(--font-(?:display|body|mono))\s*:\s*([^;]+)", fix, tokens_css)


# ---------------------------------------------------------------- HTML
class _Balance(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        if tag in OPTIONAL_CLOSE and self.stack and self.stack[-1] == tag and tag in ("li", "p", "dt", "dd", "option", "tr", "td", "th"):
            self.stack.pop()
        self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in VOID:
            self.errors.append(f"linha {self.getpos()[0]}: </{tag}> em elemento vazio")
            return
        if tag not in self.stack:
            self.errors.append(f"linha {self.getpos()[0]}: </{tag}> sem abertura")
            return
        while self.stack and self.stack[-1] != tag:
            opened = self.stack.pop()
            if opened not in OPTIONAL_CLOSE:
                self.errors.append(f"linha {self.getpos()[0]}: <{opened}> não fechado antes de </{tag}>")
        if self.stack:
            self.stack.pop()


def check_balance(text):
    """Balanceamento de tags por parser offline (sem rede). Lista vazia = HTML bem formado."""
    parser = _Balance()
    parser.feed(text)
    parser.close()
    leftover = [t for t in parser.stack if t not in OPTIONAL_CLOSE]
    return parser.errors + [f"<{t}> não fechado no fim do arquivo" for t in leftover]


class _Collect(html.parser.HTMLParser):
    """Coleta o que os gates estáticos precisam: tags com atributos, h1, metas e links."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs), self.getpos()[0]))

    handle_startendtag = handle_starttag


def collect_tags(text):
    parser = _Collect()
    parser.feed(text)
    return parser.tags


def static_checks(text, name="index.html"):
    """Gates estáticos de um HTML. Devolve (erros, avisos)."""
    errors, warnings = [], []
    errors += [f"{name}: {e}" for e in check_balance(text)]
    tags = collect_tags(text)
    by = lambda t: [a for tag, a, _ in tags if tag == t]  # noqa: E731
    html_tags = by("html")
    if not html_tags or not html_tags[0].get("lang"):
        errors.append(f"{name}: <html> sem atributo lang")
    if len(by("h1")) != 1:
        errors.append(f"{name}: {len(by('h1'))} <h1> (deve haver exatamente um)")
    if not re.search(r"<title>[^<]{3,}</title>", text):
        errors.append(f"{name}: <title> ausente ou vazio")
    metas = by("meta")
    names = {m.get("name", "").lower(): m.get("content", "") for m in metas if m.get("name")}
    props = {m.get("property", "").lower(): m.get("content", "") for m in metas if m.get("property")}
    if not names.get("viewport"):
        errors.append(f"{name}: falta <meta name=\"viewport\">")
    if not names.get("description") and "404" not in name:
        errors.append(f"{name}: falta <meta name=\"description\">")
    for prop in ("og:title", "og:description", "og:image", "og:type"):
        if not props.get(prop) and "404" not in name:
            errors.append(f"{name}: falta <meta property=\"{prop}\">")
    if props.get("og:image") and not props["og:image"].startswith("http"):
        warnings.append(f"{name}: og:image deveria ser URL absoluta (redes sociais não resolvem caminho relativo)")
    if not any("icon" in (a.get("rel") or "") for a in by("link")):
        errors.append(f"{name}: falta favicon (<link rel=\"icon\">)")
    for tag, attrs, line in tags:
        if tag == "img":
            if "alt" not in attrs:
                errors.append(f"{name}:{line}: <img> sem alt (use alt=\"\" se for decorativa)")
            if not attrs.get("width") or not attrs.get("height"):
                errors.append(f"{name}:{line}: <img> sem width/height (causa salto de layout)")
        if tag == "a" and attrs.get("target") == "_blank":
            rel = (attrs.get("rel") or "").split()
            if "noopener" not in rel and "noreferrer" not in rel:
                errors.append(f"{name}:{line}: link com target=_blank sem rel=\"noopener\"")
        if tag == "a" and not attrs.get("href"):
            warnings.append(f"{name}:{line}: <a> sem href")
        if tag == "form" and "exemplo.com" in (attrs.get("action") or ""):
            warnings.append(f"{name}:{line}: o formulário ainda aponta para o destino de exemplo ({attrs.get('action')})")
    ids = [a.get("id") for _, a, _ in tags if a.get("id")]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        errors.append(f"{name}: ids repetidos: {', '.join(dupes)}")
    if "{{" in text:
        errors.append(f"{name}: sobrou marcador {{{{...}}}} do modelo")
    return errors, warnings


# ---------------------------------------------------------------- servidor com gzip (para medir como em produção)
GZIP_TYPES = (".html", ".css", ".js", ".svg", ".json", ".txt", ".xml", ".map")


class _GzipHandler(http.server.SimpleHTTPRequestHandler):
    cache = "no-store"

    def log_message(self, *args):
        pass

    def send_head(self):
        path = Path(self.translate_path(self.path))
        if path.is_dir():
            path = path / "index.html"
        accepts = "gzip" in (self.headers.get("Accept-Encoding") or "")
        if not path.is_file() or not accepts or path.suffix not in GZIP_TYPES:
            return super().send_head()
        body = gzip.compress(path.read_bytes(), compresslevel=6, mtime=0)
        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(str(path)))
        self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Vary", "Accept-Encoding")
        self.end_headers()
        return io.BytesIO(body)

    def end_headers(self):
        self.send_header("Cache-Control", self.cache)
        super().end_headers()


class _Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


@contextlib.contextmanager
def serve_gzip(directory):
    """Servidor local em 127.0.0.1 com gzip para HTML/CSS/JS/SVG, como uma hospedagem real faria."""
    handler = functools.partial(_GzipHandler, directory=str(directory))
    httpd = _Server(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        httpd.server_close()


def resolve_target(target):
    """Interpreta o alvo de qa/perf/check-links: URL, projeto (usa dist/) ou pasta estática.

    Devolve (kind, valor, raiz_do_projeto): kind é 'url' ou 'dir'.
    """
    if target and re.match(r"^https?://", target):
        return "url", target, None
    root, cfg = find_project(target)
    if root is not None:
        dist = root / "dist"
        if not (dist / "index.html").is_file():
            paths.die(f"{dist} ainda não existe. Rode `pycode page build {root}` antes.")
        return "dir", dist, root
    folder = Path(target or ".").resolve()
    if folder.is_file():
        folder = folder.parent
    if not (folder / "index.html").is_file():
        paths.die(f"não encontrei index.html em {folder}")
    return "dir", folder, None


def render_og(root):
    """Renderiza <projeto>/og.html (1200x630) em src/img/og.jpg com o Chromium da instalação."""
    from PIL import Image
    from pycode_tools.browser import chromium
    from pycode_tools.server import serve

    root = Path(root)
    png = root / "src" / "img" / "og.png"
    out = root / "src" / "img" / "og.jpg"
    with serve(root) as url, chromium() as browser:
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        page.goto(url + "/og.html", wait_until="load")
        page.evaluate("document.fonts.ready.then(() => true)")
        page.wait_for_timeout(200)
        page.screenshot(path=str(png))
    with Image.open(png) as im:
        im.convert("RGB").save(out, quality=86, optimize=True, progressive=True)
    png.unlink()
    return out


def html_pages(folder):
    return sorted(p for p in Path(folder).rglob("*.html") if "node_modules" not in p.parts)


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
