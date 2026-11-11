# Instruções para agentes de IA

Este arquivo é para você, agente, quando alguém entregar o link deste repositório e pedir para instalar ou usar as skills.

## Instalar (um comando)

```bash
curl -fsSL https://raw.githubusercontent.com/pycodebr/pycode-skills/main/install.sh | bash
```

O instalador é idempotente e não usa `sudo`. Ele:

1. clona o repositório em `~/.pycode-skills/src`;
2. liga cada pasta de `skills/` na pasta de skills dos agentes que encontrar na máquina (Claude Code, Codex, OpenCode, Cursor, Gemini CLI, Hermes);
3. instala as dependências em `~/.pycode-skills/` (ambiente Python, Chromium do Playwright, Node com csso, Lighthouse e Mermaid CLI, ffmpeg, fontes e GSAP);
4. cria o comando `pycode` em `~/.local/bin/pycode` e em `~/.pycode-skills/bin/pycode`.

Opções úteis: `--agent claude|codex|opencode|cursor|gemini|hermes|all` (repita ou separe por vírgula), `--copy` (copia em vez de ligar), `--no-browser`, `--with-refs` (baixa também as galerias de referência de design, cerca de 60 MB).

Se você já estiver dentro de um clone do repositório, rode `bash install.sh`.

## Conferir

```bash
~/.pycode-skills/bin/pycode doctor
```

Todos os itens obrigatórios precisam aparecer como `ok`. Quando algo faltar, o próprio `doctor` mostra o comando de correção. O caso mais comum é o Chromium no Linux sem as bibliotecas de sistema. Com root ou `sudo` sem senha, o instalador resolve sozinho; sem isso, ele mostra o comando que exige `sudo`: passe esse comando para a pessoa executar e não peça a senha no chat.

Depois da instalação, diga à pessoa quais skills foram instaladas e em quais agentes, e peça para reiniciar a sessão do agente, porque a lista de skills é lida no início.

## Usar

As skills aparecem com estes nomes:

| Skill | Peça quando quiser |
|---|---|
| `pycode-design` | escolher, aplicar ou criar um estilo de design; consultar referências |
| `pycode-aulas` | uma aula ou apresentação interativa, o material de estudo no Notion, desenhos no Whimsical |
| `pycode-paginas` | uma landing page ou um site estático criativo e rápido |
| `pycode-carrosseis` | um carrossel de Instagram |

Leia o `SKILL.md` da skill antes de produzir. Use sempre o comando `pycode` (`pycode help` lista tudo) e não chame os scripts pelo caminho. A marca de quem usa fica em `~/.pycode-skills/brand.json`: se ainda estiver com os valores de exemplo, pergunte nome, @ e site antes do primeiro artefato.

## Atualizar e remover

```bash
pycode update                      # baixa a versão nova e reinstala o que mudou
bash ~/.pycode-skills/src/install.sh --uninstall
```

## Trabalhando neste repositório

- Leia `CONTRIBUTING.md`. Cada skill só usa os tokens do contrato de estilos e registra comandos em `scripts/commands.json`.
- Antes de propor mudança: `python3 tests/check_skills.py && python3 tests/leak_guard.py && bash tests/smoke.sh`.
- Não versione fontes, sons, vídeos, imagens de terceiros nem dados privados.
