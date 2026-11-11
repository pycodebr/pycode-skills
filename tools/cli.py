#!/usr/bin/env python3
"""pycode: ponto de entrada único das skills do pycode-skills.

Comandos centrais ficam aqui; cada skill registra o próprio grupo em skills/<skill>/scripts/commands.json.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pycode_tools import paths  # noqa: E402

CORE = {
    "doctor": "confere a instalação (Python, Chromium, Node, fontes, skills)",
    "version": "mostra a versão instalada",
    "help": "lista todos os comandos",
    "brand": "mostra ou cria o arquivo da sua marca (~/.pycode-skills/brand.json)",
    "vendor": "baixa fontes e bibliotecas JS para o cache local",
    "shot": "captura uma página em vários tamanhos de tela",
    "serve": "abre uma prévia local de uma pasta",
    "sheet": "monta uma folha de contato com várias imagens",
    "text": "revisa textos em PT-BR (acentos, pontuação de efeito, vícios de IA)",
    "contrast": "calcula o contraste WCAG entre duas cores",
    "icon": "baixa um ícone de marca do Simple Icons (CC0)",
    "mermaid": "valida ou renderiza um diagrama Mermaid",
    "lighthouse": "roda o Lighthouse em uma URL",
    "css": "minifica CSS e incorpora o CSS crítico no HTML",
}
SHELL_ONLY = {"setup": "instala ou repara as dependências", "update": "atualiza as skills e as dependências"}


def groups():
    out = {}
    for file in sorted(paths.SKILLS.glob("*/scripts/commands.json")):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except ValueError as exc:
            paths.die(f"{file} inválido: {exc}")
        for item in data if isinstance(data, list) else [data]:
            item["_dir"] = file.parent
            item["_skill"] = file.parent.parent.name
            out[item["group"]] = item
    return out


def show_help():
    print(f"pycode {paths.version()} · skills da PycodeBR para agentes de IA\n")
    print("Uso: pycode <comando> [opções]   ·   pycode <grupo> <comando> [opções]\n")
    print("Geral:")
    for name, text in {**SHELL_ONLY, **CORE}.items():
        print(f"  {name:<11} {text}")
    for name, data in groups().items():
        print(f"\n{name} · {data.get('help', '')} (skill {data['_skill']}):")
        for cmd, spec in data["commands"].items():
            print(f"  {name} {cmd:<10} {spec.get('help', '')}")
    print("\nAjuda de um comando: pycode <comando> --help")


def run_group(group, argv):
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(f"pycode {group['group']} · {group.get('help', '')}\n")
        for cmd, spec in group["commands"].items():
            print(f"  {group['group']} {cmd:<10} {spec.get('help', '')}")
        return 0
    spec = group["commands"].get(argv[0])
    if spec is None:
        paths.die(f"comando desconhecido: {group['group']} {argv[0]}. Opções: {', '.join(group['commands'])}")
    script = group["_dir"] / spec["script"]
    env = dict(os.environ, PYCODE_HOME=str(paths.HOME), PYCODE_SRC=str(paths.SRC))
    env["PYTHONPATH"] = str(paths.SRC / "tools") + os.pathsep + str(group["_dir"]) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.call([sys.executable, str(script), *argv[1:]], env=env)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("help", "-h", "--help"):
        show_help()
        return 0
    name, rest = argv[0], argv[1:]
    if name in ("version", "--version", "-V"):
        print(paths.version())
        return 0
    if name in CORE:
        from pycode_tools import commands
        return commands.run(name, rest) or 0
    found = groups()
    if name in found:
        return run_group(found[name], rest)
    paths.die(f"comando desconhecido: {name}. Rode `pycode help`.")


if __name__ == "__main__":
    raise SystemExit(main())
