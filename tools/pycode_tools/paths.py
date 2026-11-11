"""Caminhos do pycode-skills: instalação (PYCODE_HOME) e código-fonte (PYCODE_SRC)."""
import json
import os
import sys
from pathlib import Path

HOME = Path(os.environ.get("PYCODE_HOME") or Path.home() / ".pycode-skills").expanduser()
SRC = Path(os.environ.get("PYCODE_SRC") or Path(__file__).resolve().parents[2])
SKILLS = SRC / "skills"
VENDOR = HOME / "vendor"
REFS = HOME / "references"
BRAND_FILE = HOME / "brand.json"

DEFAULT_BRAND = {
    "name": "Sua Marca",
    "handle": "@suamarca",
    "site": "https://exemplo.com",
    "author": "Seu Nome",
    "language": "pt-BR",
    "default_style": "",
    "logo": "",
    "colors": {},
}


def die(message, code=1):
    print(f"[pycode] erro: {message}", file=sys.stderr)
    raise SystemExit(code)


def say(message):
    print(f"[pycode] {message}")


def version():
    try:
        return (SRC / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return "0.0.0"


def skill_dir(name):
    path = SKILLS / name
    if not path.is_dir():
        die(f"skill não encontrada: {name} (procurei em {SKILLS})")
    return path


def load_brand():
    """Marca de quem usa as skills (~/.pycode-skills/brand.json), com padrões neutros."""
    brand = json.loads(json.dumps(DEFAULT_BRAND))
    if BRAND_FILE.is_file():
        try:
            data = json.loads(BRAND_FILE.read_text(encoding="utf-8"))
        except ValueError as exc:
            die(f"{BRAND_FILE} não é um JSON válido: {exc}")
        for key, value in data.items():
            if key == "colors" and isinstance(value, dict):
                brand["colors"].update(value)
            else:
                brand[key] = value
    return brand


def ensure_brand_file():
    if not BRAND_FILE.exists():
        HOME.mkdir(parents=True, exist_ok=True)
        BRAND_FILE.write_text(json.dumps(DEFAULT_BRAND, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return True
    return False
