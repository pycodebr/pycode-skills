"""Fontes (OFL) e bibliotecas JS baixadas uma vez para ~/.pycode-skills/vendor e copiadas para cada projeto.

Nada é carregado de CDN nas páginas geradas: os arquivos ficam dentro do projeto, com hash conferido.
"""
import hashlib
import json
import shutil
import urllib.request

from .paths import SKILLS, SRC, VENDOR, die, say

MANIFEST = SRC / "tools" / "vendor_manifest.json"


def manifest():
    """Manifesto central mais os `vendor.json` opcionais de cada skill (mesmo formato)."""
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for extra in sorted(SKILLS.glob("*/vendor.json")):
        more = json.loads(extra.read_text(encoding="utf-8"))
        known_fonts = {f["id"] for f in data["fonts"]}
        known_js = {j["id"] for j in data["js"]}
        data["fonts"] += [f for f in more.get("fonts", []) if f["id"] not in known_fonts]
        data["js"] += [j for j in more.get("js", []) if j["id"] not in known_js]
    return data


def _download(url, dest, sha256):
    request = urllib.request.Request(url, headers={"User-Agent": "pycode-skills"})
    with urllib.request.urlopen(request, timeout=120) as response:
        blob = response.read()
    digest = hashlib.sha256(blob).hexdigest()
    if sha256 and digest != sha256:
        die(f"hash diferente do esperado em {url}\n  esperado {sha256}\n  recebido {digest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(blob)


def _ok(path, sha256):
    return path.is_file() and (not sha256 or hashlib.sha256(path.read_bytes()).hexdigest() == sha256)


def font_path(font, item):
    return VENDOR / "fonts" / font["id"] / item["file"]


def js_path(item):
    return VENDOR / "js" / item["file"]


def ensure(force=False, quiet=False):
    """Baixa o que faltar. Devolve (baixados, total)."""
    data = manifest()
    fetched = total = 0
    for font in data["fonts"]:
        for item in font["files"]:
            total += 1
            dest = font_path(font, item)
            if force or not _ok(dest, item.get("sha256")):
                _download(item["url"], dest, item.get("sha256"))
                fetched += 1
    for item in data["js"]:
        total += 1
        dest = js_path(item)
        if force or not _ok(dest, item.get("sha256")):
            _download(item["url"], dest, item.get("sha256"))
            fetched += 1
    if not quiet:
        say(f"vendor: {total} arquivos prontos em {VENDOR} ({fetched} baixados agora)")
    return fetched, total


def missing():
    data = manifest()
    out = [str(font_path(f, i)) for f in data["fonts"] for i in f["files"] if not _ok(font_path(f, i), i.get("sha256"))]
    out += [str(js_path(i)) for i in data["js"] if not _ok(js_path(i), i.get("sha256"))]
    return out


def font_ids():
    return [f["id"] for f in manifest()["fonts"]]


def copy_fonts(dest_dir, ids, url_prefix="../fonts/", display="swap"):
    """Copia as fontes pedidas para `dest_dir` e devolve o CSS com os @font-face.

    `url_prefix` é o caminho das fontes visto a partir do arquivo CSS que vai receber o texto devolvido.
    """
    data = {f["id"]: f for f in manifest()["fonts"]}
    dest_dir.mkdir(parents=True, exist_ok=True)
    css = []
    for fid in ids:
        font = data.get(fid)
        if font is None:
            die(f"fonte desconhecida: {fid}. Disponíveis: {', '.join(sorted(data))}")
        for item in font["files"]:
            src = font_path(font, item)
            if not src.is_file():
                ensure(quiet=True)
            shutil.copyfile(src, dest_dir / item["file"])
            css.append(
                "@font-face{font-family:'%s';font-style:%s;font-weight:%s;font-display:%s;"
                "src:url('%s%s') format('woff2')}" % (font["family"], item["style"], item["weight"], display, url_prefix, item["file"])
            )
    notice = dest_dir / "LICENCAS-FONTES.txt"
    lines = ["Fontes distribuídas sob a SIL Open Font License 1.1 (https://openfontlicense.org).", ""]
    lines += [f"- {data[fid]['family']}: {data[fid]['source']}" for fid in ids]
    notice.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return "\n".join(css) + "\n"


def copy_js(dest_dir, ids):
    """Copia bibliotecas JS (ex.: ['gsap', 'scrolltrigger']) para `dest_dir`. Devolve os nomes dos arquivos."""
    data = {j["id"]: j for j in manifest()["js"]}
    dest_dir.mkdir(parents=True, exist_ok=True)
    names = []
    for jid in ids:
        item = data.get(jid)
        if item is None:
            die(f"biblioteca desconhecida: {jid}. Disponíveis: {', '.join(sorted(data))}")
        src = js_path(item)
        if not src.is_file():
            ensure(quiet=True)
        shutil.copyfile(src, dest_dir / item["file"])
        names.append(item["file"])
    (dest_dir / "LICENCAS-JS.txt").write_text(
        "\n".join(f"- {data[j]['file']}: {data[j]['source']} · {data[j]['license']}" for j in ids) + "\n", encoding="utf-8"
    )
    return names
