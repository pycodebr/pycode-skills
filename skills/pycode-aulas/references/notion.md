# Material de estudo no Notion

A apresentação mostra; o material ensina. Depois da aula, a pessoa estuda por uma página que explica com calma, traz
exemplos completos, diagramas, exercícios com gabarito recolhido e fontes. O `pycode deck notion` gera essa página a
partir do mesmo `content.json` (fonte única) e publica quando há credencial.

## Estrutura da página (para quem estuda, não para quem apresenta)

1. Título e uma frase que diz do que trata a aula (`meta.description`).
2. **Para quem é** (`study.audience`) e o link da apresentação interativa (`--url`).
3. **O que você vai aprender** (`study.objectives`): ações observáveis.
4. **Antes de começar** (`study.prerequisites`).
5. **Mapa da aula**: os títulos das cenas, numerados.
6. Uma seção por cena: o `apoio`, os itens de `reading` em lista, os parágrafos de `study.text`, o exemplo de
   `study.code` e os diagramas de `meta.study.diagrams` cujo `after` é o id da cena.
7. **Glossário** em tabela (`study.glossary`).
8. **Exercícios** com o enunciado, o código para rodar e o gabarito dentro de um bloco recolhível (`<details>`), para a
   pessoa tentar antes de ver.
9. **Fontes** (`study.sources`): documentação primária, com link.

Roteiro de palco, cronômetro, falas e instruções para o apresentador ficam fora: vão em `notes` (PPTX) ou num arquivo
privado. Não coloque no material preço, oferta, dados internos nem nomes de alunos.

## Diagramas Mermaid

Cada diagrama de `meta.study.diagrams` é renderizado com `pycode mermaid` antes de gravar o material; se não renderizar,
o comando para e mostra o erro. Os SVGs ficam em `material/diagramas/`. Modelos prontos em `templates/diagrams/`
(fluxo com cores por papel, sequência de mensagens, camadas). Depois de publicar, leia a página de volta e confira se
os blocos de código `mermaid` chegaram inteiros.

## Publicar

```bash
pycode deck notion <pasta>                               # gera material/material-notion.md e material/notion-partes/
pycode deck notion <pasta> --url https://.../aula/        # inclui o link da apresentação
pycode deck notion <pasta> --dry-run                      # grava também os blocos da API em material/notion-blocos.json
NOTION_TOKEN=... pycode deck notion <pasta> --parent <id-da-página-mãe>   # publica pela API e lê de volta
```

**Pelo conector ou MCP de Notion do seu agente** (sem token): crie a página com o título e insira as partes de
`material/notion-partes/` na ordem, uma parte por chamada (páginas longas numa chamada só costumam ser truncadas).
Depois busque a página de novo e confira: todas as seções, tabelas, blocos de código, `<details>` com o gabarito e os
diagramas. Se o conector não aceitar `<details>`, use o bloco recolhível (toggle) que ele oferece.

**Pela API REST** (com token): crie uma integração interna no Notion, compartilhe a página-mãe com ela e defina
`NOTION_TOKEN` no ambiente. O comando cria a página com os primeiros 90 blocos, acrescenta o resto em lotes de 90,
lê todos os blocos de volta (com paginação e filhos de toggles e tabelas) e compara as palavras com o Markdown.
O resultado fica em `material/notion-publicacao.json` (id, URL e palavras que faltaram). Republicar cria uma página
nova; apague a anterior se for o caso.

**Nunca peça token no chat** nem grave o token em arquivo do projeto. Se a variável não existir, o comando só gera os
arquivos e explica os dois caminhos.

## Imagens

O Notion só mostra imagens por URL acessível a ele. Para pôr capturas das cenas no material, publique os PNGs de
`stills/` junto com a aula (mesmo servidor) e use o link absoluto; gere as capturas de novo a cada redesenho.
