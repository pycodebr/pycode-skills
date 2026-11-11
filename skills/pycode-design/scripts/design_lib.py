"""Funções compartilhadas dos comandos `pycode styles` e `pycode refs` (skill pycode-design).

Os estilos vivem em dois lugares:
- no repositório: skills/pycode-design/styles/<slug>/ (versionados);
- do usuário: ~/.pycode-skills/styles-user/<slug>/ (ou a pasta em PYCODE_STYLES_USER), criados por `pycode styles new`.
"""
import json
import os
import re
import shutil
from pathlib import Path

from pycode_tools import paths

CONTRACT = [
    "--bg", "--bg-2", "--surface", "--surface-2", "--text", "--muted", "--line", "--accent", "--accent-2",
    "--accent-ink", "--paper", "--paper-ink", "--danger", "--ok", "--warn", "--font-display", "--font-body",
    "--font-mono", "--weight-display", "--tracking-display", "--radius", "--radius-lg", "--shadow", "--glow",
]
COLOR_TOKENS = CONTRACT[:15]
META_KEYS = {"slug": str, "name": str, "summary": str, "mode": str, "fonts": list, "best_for": list, "mood": list, "version": str}
FORMATS = {"page", "deck", "carousel"}
SLUG_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
SKILL_DIR = Path(__file__).resolve().parent.parent


def repo_root():
    return SKILL_DIR / "styles"


def user_root():
    custom = os.environ.get("PYCODE_STYLES_USER")
    return Path(custom).expanduser() if custom else paths.HOME / "styles-user"


def _read_meta(meta_file, origin):
    try:
        data = json.loads(meta_file.read_text(encoding="utf-8"))
    except ValueError as exc:
        data = {"slug": meta_file.parent.name, "name": meta_file.parent.name, "_error": f"style.json inválido: {exc}"}
    data["dir"] = str(meta_file.parent)
    data["origin"] = origin
    return data


def all_styles():
    """Estilos do repositório e do usuário. Um estilo do usuário com o mesmo slug não substitui o do repositório."""
    out, seen = [], set()
    for root, origin in ((repo_root(), "repositório"), (user_root(), "usuário")):
        if not root.is_dir():
            continue
        for meta in sorted(root.glob("*/style.json")):
            data = _read_meta(meta, origin)
            if data.get("slug") in seen:
                continue
            seen.add(data.get("slug"))
            out.append(data)
    return out


def find_style(slug):
    for data in all_styles():
        if data.get("slug") == slug or Path(data["dir"]).name == slug:
            return data
    known = ", ".join(s["slug"] for s in all_styles())
    paths.die(f"estilo desconhecido: {slug}. Estilos disponíveis: {known}")
    raise SystemExit(1)  # die() já encerra; a linha deixa isso explícito para leitores e linters


def parse_tokens(css):
    """Variáveis declaradas no primeiro bloco :root do tokens.css, na ordem em que aparecem."""
    css = re.sub(r"(?s)/\*.*?\*/", "", css)
    m = re.search(r":root\s*\{(.*?)\}", css, re.S)
    if not m:
        return {}
    tokens = {}
    for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1)):
        tokens[name] = " ".join(value.split())
    return tokens


def resolve(tokens, value, depth=0):
    """Resolve var(--x) simples para checar contraste."""
    m = re.fullmatch(r"var\((--[\w-]+)(?:\s*,\s*([^)]+))?\)", value.strip())
    if not m or depth > 5:
        return value
    target = tokens.get(m.group(1), m.group(2) or value)
    return resolve(tokens, target, depth + 1)


def load_tokens(style_dir):
    file = Path(style_dir) / "tokens.css"
    return parse_tokens(file.read_text(encoding="utf-8")) if file.is_file() else {}


def font_families(tokens):
    """Primeira família de cada token de fonte (ex.: 'Geist')."""
    out = {}
    for key in ("--font-display", "--font-body", "--font-mono"):
        value = tokens.get(key, "")
        m = re.match(r"\s*['\"]?([^,'\"]+)", value)
        if m:
            out[key] = m.group(1).strip()
    return out


def build_style_dir(style, dest):
    """Copia um estilo para `dest` com as fontes em dest/fonts e o CSS em dest/fonts/fonts.css.

    O preview.html carrega `tokens.css` e `fonts/fonts.css` por caminho relativo, então a mesma
    estrutura funciona na galeria e em qualquer pasta montada por este comando.
    """
    from pycode_tools import vendor

    src = Path(style["dir"])
    dest = Path(dest)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for item in src.iterdir():
        if item.name.startswith(".") or item.name == "fonts":
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name)
        else:
            shutil.copy2(item, dest / item.name)
    css = vendor.copy_fonts(dest / "fonts", style.get("fonts", []), url_prefix="")
    (dest / "fonts" / "fonts.css").write_text(css, encoding="utf-8")
    return dest


def human_size(num):
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024 or unit == "GB":
            return f"{num:.0f} {unit}" if unit == "B" else f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} GB"


def dir_size(path):
    total = files = 0
    for p in Path(path).rglob("*"):
        if p.is_file():
            total += p.stat().st_size
            files += 1
    return total, files
