#!/usr/bin/env python3
"""Confere o formato das skills: frontmatter, comandos registrados, scripts e contrato dos estilos."""
import json
import py_compile
import re
import sys
from pathlib import Path

if not __debug__:
    raise RuntimeError("rode sem -O")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
REQUIRED_TOKENS = [
    "--bg", "--bg-2", "--surface", "--surface-2", "--text", "--muted", "--line", "--accent", "--accent-2",
    "--accent-ink", "--paper", "--paper-ink", "--danger", "--ok", "--warn", "--font-display", "--font-body",
    "--font-mono", "--weight-display", "--tracking-display", "--radius", "--radius-lg", "--shadow", "--glow",
]


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    try:
        import yaml
        return yaml.safe_load(m.group(1))
    except ImportError:
        data = {}
        for line in m.group(1).splitlines():
            if re.match(r"^[a-z_]+:", line):
                key, _, value = line.partition(":")
                data[key.strip()] = value.strip().strip("'\"")
        if "version:" in m.group(1):
            data["metadata"] = {"version": re.search(r"version:\s*['\"]?([\d.]+)", m.group(1)).group(1)}
        return data


def main():
    errors = []
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append(f"VERSION inválido: {version}")
    if f"## {version} " not in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"):
        errors.append(f"CHANGELOG.md sem a seção da versão {version}")
    skills = sorted(p.parent for p in (ROOT / "skills").glob("*/SKILL.md"))
    if not skills:
        errors.append("nenhuma skill encontrada")
    groups = {}
    for skill in skills:
        name = skill.name
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        fm = frontmatter(text)
        if not isinstance(fm, dict):
            errors.append(f"{name}: frontmatter ausente ou inválido")
            continue
        if fm.get("name") != name:
            errors.append(f"{name}: name do frontmatter ({fm.get('name')}) diferente da pasta")
        desc = fm.get("description") or ""
        if not (isinstance(desc, str) and desc.startswith("Use quando") and 80 <= len(desc) <= 1024):
            errors.append(f"{name}: description precisa começar com 'Use quando' e ter de 80 a 1024 caracteres (tem {len(desc)})")
        if not re.fullmatch(r"\d+\.\d+\.\d+", str((fm.get("metadata") or {}).get("version", ""))):
            errors.append(f"{name}: metadata.version ausente")
        if len(text.splitlines()) > 500:
            errors.append(f"{name}: SKILL.md com mais de 500 linhas; mova detalhe para references/")
        for ref in re.findall(r"\((references/[^)#\s]+|templates/[^)#\s]+|scripts/[^)#\s]+)\)", text):
            if not (skill / ref).exists():
                errors.append(f"{name}: SKILL.md aponta para {ref}, que não existe")
        commands = skill / "scripts" / "commands.json"
        if commands.is_file():
            data = json.loads(commands.read_text(encoding="utf-8"))
            for group in data if isinstance(data, list) else [data]:
                if group["group"] in groups:
                    errors.append(f"{name}: grupo {group['group']} já registrado por {groups[group['group']]}")
                groups[group["group"]] = name
                for cmd, spec in group["commands"].items():
                    script = skill / "scripts" / spec["script"]
                    if not script.is_file():
                        errors.append(f"{name}: {group['group']} {cmd} aponta para {spec['script']}, que não existe")
                    if not spec.get("help"):
                        errors.append(f"{name}: {group['group']} {cmd} sem texto de ajuda")
        for script in skill.rglob("*.py"):
            try:
                py_compile.compile(str(script), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(f"{script.relative_to(ROOT)}: {exc.msg.strip()}")
    for script in (ROOT / "tools").rglob("*.py"):
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{script.relative_to(ROOT)}: {exc.msg.strip()}")
    manifest = json.loads((ROOT / "tools" / "vendor_manifest.json").read_text(encoding="utf-8"))
    fonts = {f["id"] for f in manifest["fonts"]}
    for extra in (ROOT / "skills").glob("*/vendor.json"):
        fonts |= {f["id"] for f in json.loads(extra.read_text(encoding="utf-8")).get("fonts", [])}
    styles = sorted((ROOT / "skills" / "pycode-design" / "styles").glob("*/style.json"))
    if not styles:
        errors.append("pycode-design sem estilos")
    for meta in styles:
        data = json.loads(meta.read_text(encoding="utf-8"))
        slug = meta.parent.name
        if data.get("slug") != slug:
            errors.append(f"estilo {slug}: slug do style.json diferente da pasta")
        for key in ("name", "summary", "mode", "fonts", "best_for", "version"):
            if not data.get(key):
                errors.append(f"estilo {slug}: style.json sem {key}")
        for font in data.get("fonts", []):
            if font not in fonts:
                errors.append(f"estilo {slug}: fonte {font} não está no vendor")
        tokens = (meta.parent / "tokens.css").read_text(encoding="utf-8") if (meta.parent / "tokens.css").is_file() else ""
        for token in REQUIRED_TOKENS:
            if not re.search(re.escape(token) + r"\s*:", tokens):
                errors.append(f"estilo {slug}: tokens.css sem {token}")
        for file in ("DESIGN.md", "preview.html"):
            if not (meta.parent / file).is_file():
                errors.append(f"estilo {slug}: falta {file}")
    if errors:
        print("\n".join(errors))
        print(f"\n{len(errors)} problema(s).")
        return 1
    print(f"ok: {len(skills)} skills, {len(groups)} grupos de comandos, {len(styles)} estilos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
