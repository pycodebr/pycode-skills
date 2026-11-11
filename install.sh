#!/usr/bin/env bash
# pycode-skills: instala as skills da PycodeBR nos seus agentes de IA e todas as dependências.
#   curl -fsSL https://raw.githubusercontent.com/pycodebr/pycode-skills/main/install.sh | bash
#   bash install.sh [--agent claude|codex|opencode|cursor|gemini|hermes|all] [--copy] [--no-setup] [--no-browser] [--with-refs]
#   bash install.sh --uninstall   (remove as skills dos agentes, o comando pycode e ~/.pycode-skills)
set -euo pipefail
REPO="https://github.com/pycodebr/pycode-skills"
PYCODE_HOME="${PYCODE_HOME:-$HOME/.pycode-skills}"
export PYCODE_HOME
SRC="${PYCODE_SRC_DIR:-$PYCODE_HOME/src}"
AGENTS=""; MODE="link"; RUN_SETUP=1; REUSE=0; SETUP_ARGS=""; UNINSTALL=0
while [ $# -gt 0 ]; do
  case "$1" in
    --agent) AGENTS="$AGENTS ${2//,/ }"; shift 2 ;;
    --copy) MODE="copy"; shift ;;
    --no-setup) RUN_SETUP=0; shift ;;
    --no-browser|--no-node|--with-refs) SETUP_ARGS="$SETUP_ARGS $1"; shift ;;
    --reuse) REUSE=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) sed -n '2,4p' "$0" 2>/dev/null || true; exit 0 ;;
    *) echo "opção desconhecida: $1"; exit 2 ;;
  esac
done
say() { printf '\033[1;33m[pycode]\033[0m %s\n' "$*"; }

if [ "$UNINSTALL" -eq 1 ]; then
  for d in "$HOME/.claude/skills" "$HOME/.agents/skills" "$HOME/.config/opencode/skills" "$HOME/.cursor/skills" "$HOME/.gemini/skills" "$HOME/.hermes/skills/creative"; do
    for entry in "$d"/pycode-*; do
      if [ -e "$entry" ] || [ -L "$entry" ]; then rm -rf "$entry"; say "removido $entry"; fi
    done
  done
  if [ -L "$HOME/.local/bin/pycode" ]; then rm -f "$HOME/.local/bin/pycode"; fi
  case "$PYCODE_HOME" in
    "$HOME"/.pycode-skills|*/.pycode-skills) rm -rf "$PYCODE_HOME"; say "removido $PYCODE_HOME" ;;
    *) say "mantive $PYCODE_HOME (caminho personalizado): apague manualmente se quiser" ;;
  esac
  say "desinstalado. Os projetos que você criou continuam nas pastas deles."
  exit 0
fi
mkdir -p "$PYCODE_HOME"

# 1. código-fonte: este checkout, ou clone/atualização em ~/.pycode-skills/src
HERE=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; fi
if [ -n "$HERE" ] && [ -d "$HERE/skills" ] && [ -f "$HERE/bin/pycode" ]; then
  SRC="$HERE"
elif [ -d "$SRC/.git" ]; then
  git -C "$SRC" pull --ff-only -q
elif command -v git >/dev/null 2>&1; then
  rm -rf "$SRC"
  git clone -q --depth 1 "$REPO.git" "$SRC"
else
  say "git não encontrado: baixando o pacote do repositório"
  command -v curl >/dev/null 2>&1 || { say "preciso de git ou curl para baixar o repositório"; exit 1; }
  rm -rf "$SRC"; mkdir -p "$SRC"
  curl -fsSL "$REPO/archive/refs/heads/main.tar.gz" | tar -xz -C "$SRC" --strip-components=1
fi
say "skills em $SRC/skills (versão $(cat "$SRC/VERSION" 2>/dev/null || echo '?'))"

# 2. agentes (funções com case em vez de arrays associativos: o bash do macOS é 3.2)
skill_dir_for() {
  case "$1" in
    claude) echo "$HOME/.claude/skills" ;;
    codex) echo "$HOME/.agents/skills" ;;
    opencode) echo "$HOME/.config/opencode/skills" ;;
    cursor) echo "$HOME/.cursor/skills" ;;
    gemini) echo "$HOME/.gemini/skills" ;;
    hermes) echo "$HOME/.hermes/skills/creative" ;;
    *) echo "" ;;
  esac
}
marker_for() {
  case "$1" in
    claude) echo "$HOME/.claude" ;;
    codex) echo "$HOME/.codex" ;;
    opencode) echo "$HOME/.config/opencode" ;;
    cursor) echo "$HOME/.cursor" ;;
    gemini) echo "$HOME/.gemini" ;;
    hermes) echo "$HOME/.hermes" ;;
  esac
}
ALL="claude codex opencode cursor gemini hermes"
STATE="$PYCODE_HOME/install.conf"
if [ "$REUSE" -eq 1 ] && [ -z "$AGENTS" ] && [ -f "$STATE" ]; then
  AGENTS="$(sed -n 's/^agents=//p' "$STATE")"
  [ "$(sed -n 's/^mode=//p' "$STATE")" = "copy" ] && MODE="copy"
fi
AGENTS="$(echo $AGENTS)"
case "$AGENTS" in
  *all*) AGENTS="$ALL" ;;
  "") for a in $ALL; do if [ -d "$(marker_for "$a")" ]; then AGENTS="$AGENTS $a"; fi; done
      AGENTS="$(echo $AGENTS)"
      [ -n "$AGENTS" ] || AGENTS="codex" ;;
esac
for a in $AGENTS; do
  d="$(skill_dir_for "$a")"
  [ -n "$d" ] || { say "agente desconhecido: $a (opções: $ALL)"; continue; }
  mkdir -p "$d"
  count=0
  for skill in "$SRC"/skills/*/; do
    [ -f "$skill/SKILL.md" ] || continue
    name="$(basename "$skill")"
    rm -rf "${d:?}/$name"
    if [ "$MODE" = "copy" ]; then cp -R "${skill%/}" "$d/$name"; else ln -s "${skill%/}" "$d/$name"; fi
    count=$((count + 1))
  done
  say "$count skills instaladas para $a em $d"
done
printf 'agents=%s\nmode=%s\n' "$AGENTS" "$MODE" > "$STATE"

# 3. dependências (Python, Chromium, Node, ffmpeg, fontes) e comando `pycode`
if [ "$RUN_SETUP" -eq 1 ]; then
  # shellcheck disable=SC2086
  bash "$SRC/scripts/setup.sh" $SETUP_ARGS
fi
say "pronto. Reinicie o seu agente e peça, por exemplo: \"crie a apresentação da minha aula sobre APIs\"."
say "sua marca fica em $PYCODE_HOME/brand.json · atualizar: pycode update · conferir: pycode doctor"
