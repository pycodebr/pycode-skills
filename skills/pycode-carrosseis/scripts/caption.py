"""pycode carousel caption: gera o esqueleto de legenda.md a partir do slides.json.

O esqueleto não é a legenda: ele traz a ordem (pedido de ação no início e no fim), os nomes concretos
que o texto precisa citar e as regras. Quem escreve a legenda final é o agente, com as próprias palavras,
no lugar dos marcadores [[...]]. O pack recusa a legenda enquanto houver marcador.
"""
import argparse
import re
import sys

import carousel_lib as L
from pycode_tools import paths


def concrete_names(data):
    names = []
    for s in data["slides"]:
        names += [str(k) for k in s.get("keywords") or []]
        for field in ("title", "body", "cta"):
            names += re.findall(r"\*([^*]+)\*", str(s.get(field) or ""))
        card = s.get("card") or {}
        if card.get("name"):
            names.append(card["name"])
    seen, out = set(), []
    for n in names:
        key = n.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(n.strip())
    return out


def code_lines(data):
    out = []
    for s in data["slides"]:
        code = s.get("code") or {}
        for line in code.get("lines") or []:
            line = line.removeprefix(">>> ")
            if not line.startswith(("'", "[", "(", "{", "datetime.")) and len(line) > 26 and line not in out:
                out.append(line)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode carousel caption",
                                 description="Gera o esqueleto de legenda.md (o texto final é escrito pelo agente).")
    ap.add_argument("pasta", nargs="?", default=".", help="pasta do carrossel (padrão: a atual)")
    ap.add_argument("--force", action="store_true", help="sobrescreve uma legenda.md existente")
    args = ap.parse_args(argv)
    root = L.project_dir(args.pasta)
    data = L.load_slides(root)
    out = root / "legenda.md"
    if out.exists() and not args.force:
        paths.die(f"{out} já existe (use --force para recriar o esqueleto)")
    cta = str(data["slides"][-1].get("cta") or "").replace("*", "")
    if not cta:
        paths.die("o último slide não tem \"cta\" no slides.json: defina o pedido de ação antes da legenda")
    names = concrete_names(data)
    lines = code_lines(data)
    title = (data.get("meta") or {}).get("title", "")
    body = [
        "<!--",
        f"Esqueleto de legenda para: {title}",
        "Gerado por pycode carousel caption. Troque cada marcador entre colchetes duplos pelo texto final, escrito por você.",
        "",
        "Regras:",
        "- A primeira linha repete o pedido de ação do último slide, com outras palavras; a última linha também.",
        "  Um pedido só: não acrescente pergunta para comentar se o CTA é salvar, nem o contrário.",
        "- O parágrafo do meio cita os nomes concretos do conteúdo (a busca do Instagram lê a legenda).",
        "- Frases completas em PT-BR acentuado, primeira pessoa quando for a voz de quem publica,",
        "  sem travessão, sem reticências de suspense, sem promessa de resultado.",
        "- Comando que quebrou linha no slide aparece completo aqui, numa linha só.",
        "- Rode `pycode text legenda.md` antes de empacotar.",
        "",
        f"CTA do último slide: {cta}",
        f"Nomes concretos para citar: {', '.join(names) if names else '(nenhum keyword no slides.json)'}",
    ]
    if lines:
        body += ["Comandos e código mostrados nos slides (copie os que o leitor vai querer rodar):"]
        body += [f"  {x}" for x in lines]
    body += ["-->", "",
             f"[[primeira linha: o pedido de ação, no mesmo sentido de \"{cta}\"]]", "",
             "[[parágrafo de duas a quatro frases sobre o assunto, citando: " + (", ".join(names[:8]) or "os nomes do conteúdo") + "]]",
             "",
             "[[se houver comando, a versão completa dele numa linha]]", "",
             "[[última linha: o mesmo pedido de ação, dito de outro jeito]]", ""]
    out.write_text("\n".join(body), encoding="utf-8")
    print(out)
    paths.say("escreva a legenda no lugar dos marcadores entre colchetes duplos e rode `pycode text legenda.md`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
