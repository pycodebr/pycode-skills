"""pycode deck scene: lista os arquétipos de cena ou adiciona um ao projeto (arquivos da cena + texto de exemplo)."""
from __future__ import annotations

import argparse
import copy

from pycode_tools import paths
from deck_common import ID_RE, archetypes, find_project, install_scene, read_json, write_json


def cmd_list() -> int:
    for a in archetypes():
        s = a["sample"]
        doc = (a["dir"] / "scene.js").read_text(encoding="utf-8").split("*/")[0].replace("/*", "").strip()
        first = " ".join(doc.split())[:150]
        print(f"{a['archetype']:<15} ex.: \"{s.get('title', '')}\"  · {first.split(':', 1)[-1].strip()}")
    print("\nDetalhes e quando usar cada um: references/arquetipos.md da skill pycode-aulas.")
    return 0


def cmd_add(project: str | None, archetype: str, scene_id: str | None, after: str | None) -> int:
    root = find_project(project)
    lib = {a["archetype"]: a["sample"] for a in archetypes()}
    if archetype not in lib:
        paths.die(f"arquétipo desconhecido: {archetype}. Rode `pycode deck scene list`.")
    content_file = root / "src" / "content.json"
    content = read_json(content_file)
    ids = [s["id"] for s in content["scenes"]]
    sid = scene_id or lib[archetype]["id"]
    if not ID_RE.match(sid):
        paths.die(f"id inválido: {sid} (minúsculas, números e hífen, começando por letra)")
    if sid in ids:
        paths.die(f"já existe uma cena com id {sid}; escolha outro com --id")
    scene = copy.deepcopy(lib[archetype])
    scene["id"] = sid
    pos = len(ids) - 1 if after is None else (ids.index(after) + 1 if after in ids else paths.die(f"cena não encontrada: {after}"))
    content["scenes"].insert(pos, scene)
    install_scene(root, archetype, sid)
    write_json(content_file, content)
    print(f"cena {sid} ({archetype}) adicionada na posição {pos + 1}")
    print(f"  texto: {content_file} (troque o texto de exemplo)")
    print(f"  código: {root / 'src' / 'scenes' / (sid + '.js')} e .css")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pycode deck scene", description="Arquétipos de cena: lista o catálogo ou adiciona uma cena nova ao projeto.")
    sub = ap.add_subparsers(dest="action", required=True)
    sub.add_parser("list", help="lista os arquétipos disponíveis")
    add = sub.add_parser("add", help="adiciona uma cena a partir de um arquétipo")
    add.add_argument("pasta", nargs="?", help="pasta do projeto (padrão: a atual)")
    add.add_argument("--archetype", required=True, help="nome do arquétipo (veja `pycode deck scene list`)")
    add.add_argument("--id", help="id da cena nova (padrão: o do exemplo do arquétipo)")
    add.add_argument("--after", help="id da cena depois da qual a nova entra (padrão: antes do encerramento)")
    args = ap.parse_args(argv)
    if args.action == "list":
        return cmd_list()
    return cmd_add(args.pasta, args.archetype, args.id, args.after)


if __name__ == "__main__":
    raise SystemExit(main())
