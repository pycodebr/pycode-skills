#!/usr/bin/env bash
# Instala tudo de que as skills precisam em ~/.pycode-skills (sem sudo):
# ambiente Python, Chromium, Node + ferramentas, ffmpeg, fontes e bibliotecas JS.
#   bash scripts/setup.sh [--no-browser] [--no-node] [--with-refs] [--quiet]
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYCODE_HOME="${PYCODE_HOME:-$HOME/.pycode-skills}"
export PYCODE_HOME PYCODE_SRC="$SRC"
BROWSER=1; NODE=1; REFS=0
NODE_VERSION="v22.22.2"
while [ $# -gt 0 ]; do
  case "$1" in
    --no-browser) BROWSER=0; shift ;;
    --no-node) NODE=0; shift ;;
    --with-refs) REFS=1; shift ;;
    --quiet) shift ;;
    *) echo "opção desconhecida: $1"; exit 2 ;;
  esac
done
say() { printf '\033[1;33m[pycode]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;31m[pycode]\033[0m %s\n' "$*" >&2; }
WARNINGS=""
note() { WARNINGS="${WARNINGS}
  - $*"; warn "$*"; }
mkdir -p "$PYCODE_HOME/bin"

# ---------------------------------------------------------------- 1. Python
VENV="$PYCODE_HOME/venv"
REQ="$SRC/tools/requirements.txt"
py_ok() { "$1" -c 'import sys, venv, ensurepip; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] <= (3, 13) else 1)' >/dev/null 2>&1; }
find_python() {
  for c in python3.12 python3.13 python3.11 python3.10 python3 python; do
    if command -v "$c" >/dev/null 2>&1 && py_ok "$c"; then command -v "$c"; return 0; fi
  done
  return 1
}
ensure_uv() {
  if command -v uv >/dev/null 2>&1; then command -v uv; return 0; fi
  if [ -x "$HOME/.local/bin/uv" ]; then echo "$HOME/.local/bin/uv"; return 0; fi
  if [ -x "$HOME/.cargo/bin/uv" ]; then echo "$HOME/.cargo/bin/uv"; return 0; fi
  say "instalando o uv (gerenciador de Python) em ~/.local/bin" >&2
  curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh >/dev/null 2>&1 || return 1
  [ -x "$HOME/.local/bin/uv" ] && echo "$HOME/.local/bin/uv"
}
venv_with_uv() {
  local uv
  uv="$(ensure_uv)" || { warn "não consegui instalar o uv. Instale Python 3.10 a 3.13 e rode de novo."; exit 1; }
  rm -rf "$VENV"
  "$uv" venv --quiet --python 3.12 "$VENV"
  "$uv" pip install --quiet --python "$VENV/bin/python" -r "$REQ"
}
deps_ok() { "$VENV/bin/python" -c 'import playwright, PIL, numpy, cv2, imageio_ffmpeg, yaml' >/dev/null 2>&1; }

if [ -x "$VENV/bin/python" ] && deps_ok && [ "$VENV/.requirements" -nt "$REQ" ]; then
  say "ambiente Python já pronto ($("$VENV/bin/python" -V 2>&1))"
else
  if PY="$(find_python)"; then
    say "criando o ambiente Python com $PY ($("$PY" -V 2>&1))"
    [ -x "$VENV/bin/python" ] || "$PY" -m venv "$VENV"
    if ! { "$VENV/bin/python" -m pip install --quiet --upgrade pip && "$VENV/bin/python" -m pip install --quiet -r "$REQ"; }; then
      say "a instalação com o Python do sistema falhou; tentando com o uv (Python 3.12 próprio)"
      venv_with_uv
    fi
  else
    say "Python 3.10 a 3.13 com venv não encontrado; usando o uv (baixa um Python 3.12 próprio, sem sudo)"
    venv_with_uv
  fi
  deps_ok || { warn "as dependências Python não instalaram. Veja o erro acima."; exit 1; }
  touch "$VENV/.requirements"
fi
PYBIN="$VENV/bin/python"

# ---------------------------------------------------------------- 2. Chromium
chromium_works() {
  "$PYBIN" - <<'PY' >/dev/null 2>&1
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page()
    page.set_content("<p>ok</p>")
    assert page.inner_text("p") == "ok"
    b.close()
PY
}
PW_LOG="$PYCODE_HOME/playwright-install.log"
pw_install() { "$PYBIN" -m playwright install chromium >"$PW_LOG" 2>&1; }
can_root() { [ "$(id -u)" -eq 0 ] || { command -v sudo >/dev/null 2>&1 && sudo -n true >/dev/null 2>&1; }; }
as_root() { if [ "$(id -u)" -eq 0 ]; then "$@"; else sudo -n "$@"; fi; }
# instala um pacote de sistema quando há root ou sudo sem senha: sys_pkg <nome-debian> <nome-fedora>
sys_pkg() {
  can_root || return 1
  if command -v apt-get >/dev/null 2>&1; then
    as_root env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$1" >/dev/null 2>&1 \
      || { as_root apt-get update -qq >/dev/null 2>&1 && as_root env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$1" >/dev/null 2>&1; }
  elif command -v dnf >/dev/null 2>&1; then as_root dnf install -y -q "$2" >/dev/null 2>&1
  elif command -v yum >/dev/null 2>&1; then as_root yum install -y -q "$2" >/dev/null 2>&1
  else return 1; fi
}
if [ "$BROWSER" -eq 1 ]; then
  if chromium_works; then
    say "Chromium já pronto"
  else
    say "baixando o Chromium do Playwright (uma vez, ~170 MB)"
    NEED_ATOMIC=0
    if ! pw_install; then
      # sistemas mínimos (contêiner, servidor enxuto) não trazem a libatomic, de que o Playwright precisa para rodar
      if [ "$(uname -s)" = "Linux" ] && grep -q "libatomic" "$PW_LOG" 2>/dev/null; then
        NEED_ATOMIC=1
        say "instalando a biblioteca de sistema libatomic"
        if sys_pkg libatomic1 libatomic && pw_install; then NEED_ATOMIC=0; fi
      fi
    fi
    if ! chromium_works && [ "$(uname -s)" = "Linux" ] && [ "$NEED_ATOMIC" -eq 0 ] && can_root; then
      say "instalando as bibliotecas de sistema do Chromium"
      as_root "$PYBIN" -m playwright install-deps chromium >/dev/null 2>&1 || true
    fi
    if ! chromium_works; then
      if [ "$NEED_ATOMIC" -eq 1 ]; then
        note "falta a biblioteca de sistema libatomic. Rode uma vez: sudo apt-get install -y libatomic1 (Fedora: sudo dnf install -y libatomic) e depois: pycode setup"
      elif [ "$(uname -s)" = "Linux" ]; then
        note "o Chromium foi baixado, mas não abriu. Rode uma vez: sudo \"$PYBIN\" -m playwright install-deps chromium"
      else
        note "o Chromium não abriu. Veja $PW_LOG e rode \`pycode setup\` de novo"
      fi
    fi
  fi
else
  say "Chromium ignorado (--no-browser)"
fi

# ---------------------------------------------------------------- 3. Node + ferramentas
node_major() { "$1" -v 2>/dev/null | sed 's/^v//; s/\..*//'; }
install_node() {
  local os arch name url tmp
  case "$(uname -s)" in Linux) os=linux ;; Darwin) os=darwin ;; *) return 1 ;; esac
  case "$(uname -m)" in x86_64|amd64) arch=x64 ;; arm64|aarch64) arch=arm64 ;; *) return 1 ;; esac
  name="node-$NODE_VERSION-$os-$arch"
  url="https://nodejs.org/dist/$NODE_VERSION/$name.tar.gz"
  tmp="$(mktemp -d)"
  say "baixando o Node $NODE_VERSION para $PYCODE_HOME/node (sem sudo)"
  curl -fsSL "$url" -o "$tmp/node.tar.gz" || return 1
  local want got
  want="$(curl -fsSL "https://nodejs.org/dist/$NODE_VERSION/SHASUMS256.txt" | awk -v f="$name.tar.gz" '$2 == f {print $1}')"
  if command -v sha256sum >/dev/null 2>&1; then got="$(sha256sum "$tmp/node.tar.gz" | awk '{print $1}')"; else got="$(shasum -a 256 "$tmp/node.tar.gz" | awk '{print $1}')"; fi
  [ -n "$want" ] && [ "$want" = "$got" ] || { warn "hash do Node não confere"; rm -rf "$tmp"; return 1; }
  rm -rf "$PYCODE_HOME/node"
  mkdir -p "$PYCODE_HOME/node"
  tar -xzf "$tmp/node.tar.gz" -C "$PYCODE_HOME/node" --strip-components=1
  rm -rf "$tmp"
}
if [ "$NODE" -eq 1 ]; then
  if [ -x "$PYCODE_HOME/node/bin/node" ]; then PATH="$PYCODE_HOME/node/bin:$PATH"; export PATH; fi
  if ! command -v node >/dev/null 2>&1 || [ "$(node_major node)" -lt 18 ] || ! command -v npm >/dev/null 2>&1; then
    if install_node; then PATH="$PYCODE_HOME/node/bin:$PATH"; export PATH; else note "não consegui instalar o Node: minificação de CSS, Lighthouse e Mermaid ficam indisponíveis"; fi
  fi
  if command -v npm >/dev/null 2>&1; then
    TOOLS="$PYCODE_HOME/node_tools"
    if [ -x "$TOOLS/node_modules/.bin/csso" ] && [ -x "$TOOLS/node_modules/.bin/lighthouse" ] && [ -x "$TOOLS/node_modules/.bin/mmdc" ]; then
      say "ferramentas Node já prontas ($(node -v))"
    else
      say "instalando csso, Lighthouse e Mermaid CLI ($(node -v))"
      mkdir -p "$TOOLS"
      [ -f "$TOOLS/package.json" ] || printf '{"name":"pycode-node-tools","private":true}\n' > "$TOOLS/package.json"
      PUPPETEER_SKIP_DOWNLOAD=1 PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=1 npm install --prefix "$TOOLS" --no-audit --no-fund --loglevel=error \
        csso-cli@4.0.2 lighthouse@13 >/dev/null 2>&1 || note "csso/Lighthouse não instalaram (npm). Rode \`pycode setup\` de novo com rede."
      PUPPETEER_SKIP_DOWNLOAD=1 PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=1 npm install --prefix "$TOOLS" --no-audit --no-fund --loglevel=error \
        @mermaid-js/mermaid-cli@12 >/dev/null 2>&1 || note "Mermaid CLI não instalou (opcional: só valida diagramas)"
    fi
  fi
else
  say "Node ignorado (--no-node)"
fi

# ---------------------------------------------------------------- 4. fontes e JS, comando, marca
"$PYBIN" "$SRC/tools/cli.py" vendor
ln -sf "$SRC/bin/pycode" "$PYCODE_HOME/bin/pycode"
mkdir -p "$HOME/.local/bin"
ln -sf "$SRC/bin/pycode" "$HOME/.local/bin/pycode"
"$PYBIN" "$SRC/tools/cli.py" brand --init >/dev/null
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) say "dica: ~/.local/bin não está no PATH; use $PYCODE_HOME/bin/pycode ou adicione ~/.local/bin ao PATH" ;; esac

# ---------------------------------------------------------------- 5. referências (opcional) e conferência
if [ "$REFS" -eq 1 ]; then
  "$PYBIN" "$SRC/tools/cli.py" refs fetch || note "as galerias de referência não baixaram; rode \`pycode refs fetch\` depois"
fi
echo
"$PYBIN" "$SRC/tools/cli.py" doctor || true
if [ -n "$WARNINGS" ]; then printf '\n\033[1;31mAvisos da instalação:\033[0m%s\n' "$WARNINGS"; fi
