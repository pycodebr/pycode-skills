#!/usr/bin/env bash
# Teste de ponta a ponta: cria, monta e testa um artefato de cada skill, como o agente de um aluno faria.
#   bash tests/smoke.sh [--full]     (--full roda também o QA completo do deck, vídeo do carrossel e medição de performance)
set -euo pipefail
FULL=0; [ "${1:-}" = "--full" ] && FULL=1
PYCODE="${PYCODE:-}"
if [ -z "$PYCODE" ]; then
  if command -v pycode >/dev/null 2>&1; then PYCODE="pycode"; else PYCODE="$HOME/.pycode-skills/bin/pycode"; fi
fi
WORK="$(mktemp -d "${TMPDIR:-/tmp}/pycode-smoke.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
step() { printf '\n\033[1;33m== %s\033[0m\n' "$*"; }

step "instalação"
"$PYCODE" doctor

step "pycode-design: contrato e prévia dos estilos"
"$PYCODE" styles list
"$PYCODE" styles check orbital caderno fliperama
"$PYCODE" styles tokens revista --format json >/dev/null
"$PYCODE" refs list >/dev/null

step "pycode-aulas: deck novo, build e QA"
"$PYCODE" deck new "$WORK/aula" --title "Como funciona uma API" --style orbital
"$PYCODE" deck build "$WORK/aula"
if [ "$FULL" -eq 1 ]; then "$PYCODE" deck qa "$WORK/aula"; else "$PYCODE" deck qa "$WORK/aula" --fast --only capa,viagem; fi
"$PYCODE" deck export "$WORK/aula" --pdf
test -n "$(find "$WORK/aula" -name '*.pdf' | head -1)"

step "pycode-paginas: landing nova em estilo claro, build e QA"
"$PYCODE" page new "$WORK/pagina" --title "Oficina de APIs" --style revista
"$PYCODE" page build "$WORK/pagina"
"$PYCODE" page qa "$WORK/pagina"
"$PYCODE" page check-links "$WORK/pagina"

step "pycode-carrosseis: exemplo, render e QA"
"$PYCODE" carousel new "$WORK/carrossel" --example metro
"$PYCODE" carousel render "$WORK/carrossel"
"$PYCODE" carousel qa "$WORK/carrossel"
"$PYCODE" carousel preview "$WORK/carrossel"

if [ "$FULL" -eq 1 ]; then
  step "carrossel em vídeo (2 s)"
  "$PYCODE" carousel video "$WORK/carrossel" --slide 1 --seconds 2
  step "performance da landing (informativo: depende da máquina)"
  "$PYCODE" page perf "$WORK/pagina" --runs 3 --baseline --min-score 0 --min-a11y 95 --min-best 95 || echo "medição de performance abaixo do mínimo de acessibilidade/boas práticas"
fi
printf '\n\033[1;32msmoke ok\033[0m\n'
