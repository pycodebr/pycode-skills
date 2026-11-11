#!/usr/bin/env python3
"""Guarda de publicação: reprova dado privado, segredo ou arquivo que não deveria estar no repositório.

Roda no CI e antes de cada release. Sai com código 1 quando encontra algo.
"""
import re
import subprocess
import sys
from pathlib import Path

if not __debug__:
    raise RuntimeError("rode sem -O: a guarda não pode ser desativada")

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
MAX_BYTES = 600_000
FORBIDDEN_SUFFIXES = {".woff", ".woff2", ".ttf", ".otf", ".mp4", ".mov", ".webm", ".wav", ".mp3", ".m4a", ".zip", ".pdf", ".pptx", ".psd"}
RASTER = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"}
RASTER_OK = ("docs/img/",)

PATTERNS = [
    (r"(?i)\bkratos\b", "nome de agente interno"),
    (r"(?i)radar-?x\b", "sistema interno"),
    (r"/root/|/var/www/|/home/[a-z]+/", "caminho de servidor"),
    (r"(?i)\b(hubla|kiwify|clickup|composio)\b", "ferramenta do fluxo interno"),
    (r"(?i)pay\.hub\.la|srv\.pycodebr|7lz8uzbx|GTM-[A-Z0-9]{5,}\b|[?&]id=G-[A-Z0-9]{6,}|fbq\('init', ?'\d", "checkout ou ID de tracking"),
    (r"(?i)black november|ia master|fast master|logic master|ia builders|\belite\b", "produto ou campanha"),
    (r"(?i)\bantia\b", "prompt editorial interno"),
    (r"\b(Pedro|Zucchi|Paolla|Ulisses|Gabriele|Gabi)\b", "nome de pessoa"),
    (r"R\$ ?\d", "preço"),
    (r"(?i)gpt-image|openai-codex", "política interna de modelos"),
    (r"claude-(?:opus|fable|sonnet|haiku)-\d", "política interna de modelos"),
    (r"(?i)\b(?:\+?55)?[ -]?\(?\d{2}\)?[ -]?9\d{4}[ -]?\d{4}\b", "telefone"),
    (r"(?i)\b[\w.+-]+@(?!exemplo\.com|example\.com|suamarca\.com)[\w-]+\.[a-z]{2,}\b", "e-mail"),
    (r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|xox[bpa]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|secret_[A-Za-z0-9]{20,}|ntn_[A-Za-z0-9]{20,}", "segredo"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "chave privada"),
]
# trechos legítimos que casam com os padrões acima
ALLOW = [
    r"git@github\.com",
    r"noreply@",
]


def files():
    try:
        out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        return [ROOT / line for line in out.splitlines() if line.strip()]
    except (OSError, subprocess.CalledProcessError):
        return [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]


def main():
    problems = []
    for path in files():
        if not path.is_file() or path == SELF:
            continue
        rel = path.relative_to(ROOT).as_posix()
        suffix = path.suffix.lower()
        size = path.stat().st_size
        if suffix in FORBIDDEN_SUFFIXES:
            problems.append(f"{rel}: tipo de arquivo que não entra no repositório ({suffix})")
            continue
        if size > MAX_BYTES:
            problems.append(f"{rel}: {size / 1024:.0f} KB (limite {MAX_BYTES // 1000} KB)")
        if suffix in RASTER:
            if not rel.startswith(RASTER_OK):
                problems.append(f"{rel}: imagem fora de docs/img/ (use SVG próprio ou gere no projeto do usuário)")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"{rel}: arquivo binário não previsto")
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if any(re.search(a, line) for a in ALLOW):
                continue
            for pattern, label in PATTERNS:
                m = re.search(pattern, line)
                if m:
                    problems.append(f"{rel}:{number}: {label}: {m.group(0)!r}")
    if problems:
        print("\n".join(problems))
        print(f"\n{len(problems)} problema(s) de publicação.")
        return 1
    print("leak guard: nada encontrado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
