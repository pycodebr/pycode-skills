"""Funções compartilhadas pelos comandos `pycode deck ...` (projeto, conteúdo, servidor e navegador)."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from pycode_tools import paths

SKILL = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL / "templates"
DECK_TEMPLATE = TEMPLATES / "deck"
SCENE_LIBRARY = TEMPLATES / "scenes"
ENGINE_VERSION = "1.0.0"
ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,40}$")
# chaves do content.json que guardam código, diagramas ou endereços (não passam pela revisão de texto)
CODE_KEYS = {"code", "command", "mermaid", "url", "href", "icon", "id", "archetype", "tone", "lang", "transition",
             "bg", "accent", "output", "prompt", "method", "path", "status", "side", "line", "unit", "kind", "slug"}

UI_DEFAULTS = {
    "deck": "apresentação", "prev": "Cena anterior", "next": "Próxima cena", "summary": "Resumo da cena",
    "rotate": "Gire o celular para ver a cena em tela cheia", "more": "Ver o conteúdo completo da cena",
    "textMode": "Ler em modo texto", "stageMode": "Ver as cenas animadas", "controls": "Controles da apresentação",
    "index": "Índice", "indexTitle": "Escolha uma cena", "timerHelp": "Clique para iniciar ou pausar; duplo clique zera",
    "options": "Opções", "close": "Fechar", "fullscreen": "Tela cheia", "motionOff": "Pausar animações",
    "motionOn": "Ativar animações", "replay": "Recomeçar a demonstração desta cena",
    "fullscreenHelp": "O navegador não liberou a tela cheia pelo botão. Use F11 ou o modo de apresentação do navegador.",
    "keys": "<kbd>→</kbd> <kbd>←</kbd> navegar · <kbd>Home</kbd> <kbd>End</kbd> início e fim · <kbd>O</kbd> índice · "
            "<kbd>F</kbd> tela cheia · <kbd>R</kbd> recomeçar a cena · <kbd>M</kbd> pausar animações · "
            "<kbd>T</kbd> cronômetro · <kbd>B</kbd> tela preta · <kbd>?</kbd> opções",
    "help": "Cada cena toca a demonstração uma vez, volta ao início e para. Clique em qualquer ponto da cena para "
            "assumir; clique nos objetos para ver o detalhe. <kbd>Tab</kbd> percorre os itens e <kbd>Enter</kbd> "
            "seleciona. <kbd>R</kbd> devolve a demonstração automática.",
    "scene": "Cena",
}


def find_project(arg: str | None) -> Path:
    """Pasta do projeto: o argumento, a pasta atual ou um pai que tenha deck.json."""
    start = Path(arg or ".").expanduser().resolve()
    if start.is_file():
        start = start.parent
    for candidate in (start, *start.parents):
        if (candidate / "deck.json").is_file():
            return candidate
        if arg:
            break
    paths.die(f"não encontrei deck.json em {start}. Crie o projeto com `pycode deck new <pasta> --title \"...\"`.")
    raise SystemExit(1)


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        paths.die(f"arquivo não encontrado: {path}")
    except ValueError as exc:
        paths.die(f"{path} não é um JSON válido: {exc}")
    raise SystemExit(1)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_project(root: Path) -> tuple[dict, dict]:
    return read_json(root / "deck.json"), read_json(root / "src" / "content.json")


def short_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:10]


def slugify(text: str) -> str:
    import unicodedata
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "aula"


def text_strings(node, key: str = "") -> list[str]:
    """Textos visíveis do content.json (sem código, diagramas, endereços nem notas de fala)."""
    out = []
    if isinstance(node, str):
        if key not in CODE_KEYS:
            out.append(node)
    elif isinstance(node, dict):
        for k, v in node.items():
            out += text_strings(v, k)
    elif isinstance(node, list):
        for v in node:
            out += text_strings(v, key)
    return out


def scene_ids(content: dict) -> list[str]:
    return [s.get("id", "") for s in content.get("scenes", [])]


def archetypes() -> list[dict]:
    out = []
    for folder in sorted(SCENE_LIBRARY.iterdir()):
        meta = folder / "sample.json"
        if folder.is_dir() and meta.is_file():
            data = read_json(meta)
            out.append({"archetype": folder.name, "dir": folder, "sample": data})
    return out


def install_scene(root: Path, archetype: str, scene_id: str) -> None:
    """Copia o arquétipo para src/scenes/<id>.js e .css trocando o marcador __ID__."""
    folder = SCENE_LIBRARY / archetype
    if not folder.is_dir():
        known = ", ".join(a["archetype"] for a in archetypes())
        paths.die(f"arquétipo desconhecido: {archetype}. Disponíveis: {known}")
    dest = root / "src" / "scenes"
    dest.mkdir(parents=True, exist_ok=True)
    for ext in ("js", "css"):
        src = folder / f"scene.{ext}"
        if src.is_file():
            text = src.read_text(encoding="utf-8").replace("__ID__", scene_id)
            (dest / f"{scene_id}.{ext}").write_text(text, encoding="utf-8")


def pycode(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Roda um comando central do pycode no mesmo ambiente (ex.: mermaid, text)."""
    cli = paths.SRC / "tools" / "cli.py"
    env = dict(os.environ)
    result = subprocess.run([sys.executable, str(cli), *args], capture_output=True, text=True, env=env)
    if check and result.returncode != 0:
        print((result.stdout + result.stderr).strip(), file=sys.stderr)
    return result


def stage_url(base: str, query: str = "", hash_: str = "1") -> str:
    return f"{base}/index.html{('?' + query) if query else ''}#{hash_}"


WAIT_READY = "document.documentElement.dataset.ready === 'true'"


def open_deck(browser, base: str, width: int, height: int, query: str = "", mobile: bool = False,
              reduced: bool = False, hash_: str = "1", block_external: bool = True):
    """Abre o deck numa página nova; requisições para fora de 127.0.0.1 são bloqueadas e anotadas."""
    from pycode_tools.browser import new_page
    page = new_page(browser, width, height, reduced_motion=reduced, mobile=mobile, scale=2 if mobile else 1)
    page.pycode_external = []
    if block_external:
        def route(r):
            url = r.request.url
            if url.startswith(("http://127.0.0.1", "data:", "blob:")):
                return r.continue_()
            page.pycode_external.append(url)
            return r.abort()
        page.context.route("**/*", route)
    page.goto(stage_url(base, query, hash_), wait_until="load")
    page.wait_for_function(WAIT_READY, timeout=30000)
    page.wait_for_timeout(250)
    return page


def site_dir(root: Path) -> Path:
    site = root / "site"
    if not (site / "index.html").is_file():
        paths.die(f"{site}/index.html não existe. Rode `pycode deck build {root}` antes.")
    return site
