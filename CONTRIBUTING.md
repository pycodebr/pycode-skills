# Contribuindo

Obrigado por querer melhorar o pycode-skills. O repositório reúne skills que a PycodeBR usa no dia a dia e compartilha com alunos e comunidade.

## Como o repositório é organizado

- `skills/<nome>/`: uma skill no padrão aberto Agent Skills (`SKILL.md`, `references/`, `templates/`, `scripts/`).
- `tools/`: a biblioteca `pycode_tools` e os comandos centrais do `pycode`.
- `bin/pycode`, `install.sh`, `scripts/setup.sh`: instalação e ponto de entrada.
- `tests/`: verificações que o CI roda em cada commit.

Cada skill registra os próprios comandos em `skills/<nome>/scripts/commands.json`. O agente de quem usa sempre chama `pycode <grupo> <comando>`.

## Regras para uma skill nova ou uma mudança

1. Entregue algo que você executou. Modelos geram artefato, scripts rodam e o QA da skill passa.
2. Use os tokens do contrato de estilos (`pycode styles check`) em vez de cores fixas, para o modelo funcionar com qualquer estilo.
3. Nada de CDN em runtime, fontes, sons, vídeos ou imagens de terceiros no repositório. Fontes e bibliotecas entram por `tools/vendor_manifest.json` (ou `skills/<nome>/vendor.json`), com versão fixada e sha256.
4. Nenhum dado privado: segredos, IDs, caminhos de servidor, nomes de clientes ou alunos, números de negócio, capturas de sistemas internos.
5. Texto em PT-BR natural e acentuado. Rode `pycode text` nos arquivos que você escreveu.
6. Python 3.10+, PEP 8, sem dependência nova fora de `tools/requirements.txt` sem combinar antes.

Antes de abrir o PR:

```bash
python3 tests/check_skills.py
python3 tests/leak_guard.py
bash tests/smoke.sh
```

## Versões e releases

Toda alteração publicada no `main` sai como versão, com tag e release no GitHub.

1. Atualize `VERSION` e o `metadata.version` das skills alteradas (semver: patch para correções e documentação, minor para skills, estilos e comandos novos, major para mudanças incompatíveis).
2. Abra a seção `## X.Y.Z (AAAA-MM-DD)` no topo do `CHANGELOG.md`.
3. Commit com a mensagem `pycode-skills X.Y.Z: <resumo>`, push no `main` e CI verde nesse commit.
4. Tag anotada e release com as notas da seção do CHANGELOG:
   `git tag -a vX.Y.Z -m "pycode-skills X.Y.Z: <resumo>" && git push origin vX.Y.Z`
   `gh release create vX.Y.Z --verify-tag --title "pycode-skills X.Y.Z: <resumo>" --notes-file <notas.md> --latest`

## Issues

Informe o sistema operacional, o agente usado, a saída de `pycode doctor` e o comando que falhou.
