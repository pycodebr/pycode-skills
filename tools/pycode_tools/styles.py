"""Estilos de design da skill pycode-design (skills/pycode-design/styles/<slug>/)."""
import json
import os
from pathlib import Path

from .paths import HOME, die, load_brand, skill_dir

REQUIRED_TOKENS = [
    "--bg", "--bg-2", "--surface", "--surface-2", "--text", "--muted", "--line", "--accent", "--accent-2",
    "--accent-ink", "--paper", "--paper-ink", "--danger", "--ok", "--warn", "--font-display", "--font-body",
    "--font-mono", "--weight-display", "--tracking-display", "--radius", "--radius-lg", "--shadow", "--glow",
]


def styles_root():
    return skill_dir("pycode-design") / "styles"


def user_styles_root():
    """Estilos criados por quem usa (`pycode styles new`): ficam fora do repositório e sobrevivem às atualizações."""
    return Path(os.environ.get("PYCODE_STYLES_USER") or HOME / "styles-user").expanduser()


def list_styles():
    out, seen = [], set()
    for root, origin in ((styles_root(), "pycode-design"), (user_styles_root(), "usuário")):
        if not root.is_dir():
            continue
        for meta in sorted(root.glob("*/style.json")):
            data = json.loads(meta.read_text(encoding="utf-8"))
            if data.get("slug") in seen:
                continue
            seen.add(data.get("slug"))
            data["dir"] = str(meta.parent)
            data["origin"] = origin
            out.append(data)
    return out


def load_style(slug=None):
    """Devolve o estilo (metadados, tokens.css e caminho). Sem slug, usa o padrão da marca ou o primeiro da lista."""
    styles = list_styles()
    if not styles:
        die("nenhum estilo instalado em pycode-design/styles")
    slug = slug or load_brand().get("default_style") or styles[0]["slug"]
    for data in styles:
        if data["slug"] == slug:
            data = dict(data)
            base = Path(data["dir"])
            data["tokens_css"] = (base / "tokens.css").read_text(encoding="utf-8")
            data["path"] = base
            return data
    die(f"estilo desconhecido: {slug}. Rode `pycode styles list`.")
