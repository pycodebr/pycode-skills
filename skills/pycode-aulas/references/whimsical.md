# Whimsical (opcional) e diagramas sem conta

Um quadro no Whimsical vale quando a turma vai consultar o desenho depois, editar junto ou quando a pessoa já usa a
ferramenta. Para uma aula única, os diagramas Mermaid do material (renderizados com `pycode mermaid`) e as próprias
cenas costumam bastar.

## Quando vale

- Mapas grandes que não cabem numa cena (arquitetura inteira, trilha de estudos com muitos módulos).
- Quadro vivo da turma, editado durante ou depois da aula.
- A pessoa pediu explicitamente um quadro.

## Como desenhar

- **Colorido e organizado, não um fluxograma cinza.** Título grande no topo; a peça principal; embaixo, uma grade com
  os desenhos de cada conceito da aula, cada um com um nó-título escuro e nós coloridos por papel (quem age, ação,
  regra, sistema, dado, erro).
- **Mermaid colado vira objetos nativos.** Escreva o desenho como `flowchart`, valide com `pycode mermaid arquivo.mmd`
  e cole o texto no quadro. `classDef` com `fill`, `stroke` e `color` é importado e mapeado para a paleta do
  Whimsical; use uma cor por papel.
- **Um nível de subgrafo no máximo.** Subgrafos aninhados e `direction` dentro de subgrafo são reorganizados na
  vertical com molduras sobrepostas. Prefira um grafo plano com um nó-título.
- **`sequenceDiagram` entra como texto solto.** Converta sequências em `flowchart` antes de colar.
- Logos de marca: baixe com `pycode icon <slug>` (Simple Icons, CC0) e cole como imagem; marcas continuam sendo dos
  seus donos.

Modelos validados em `templates/diagrams/`: `fluxo-por-papel.mmd` (cores por papel, um subgrafo, nó-título),
`camadas.mmd` e `sequencia-pedido.mmd` (este para Notion e SVG; para o Whimsical, converta em flowchart).

## Técnica de automação pelo navegador (referência)

Se o seu agente controla um navegador com a sua sessão do Whimsical aberta, dá para colar Mermaid e imagens por código.
Isso depende do navegador e da versão do site; trate como técnica que pode mudar a qualquer momento:

- **Colar texto:** dispare no elemento focado um `ClipboardEvent('paste')` com um `DataTransfer` contendo o Mermaid em
  `text/plain`. A colagem cai no centro da área visível, não no cursor.
- **Colar imagem:** o mesmo evento com um `File` `image/png` dentro do `DataTransfer` (envie o arquivo em pedaços se
  ele for grande; expressões muito longas falham no protocolo do navegador).
- **Copiar um desenho de outro quadro:** selecione por arrasto, dispare um `ClipboardEvent('copy')` com um
  `DataTransfer` vazio e leia `text/html` e `text/plain`; cole os dois tipos no quadro novo.
- **Posicionar:** depois de colar, mova a seleção com Shift + setas e confira por captura de tela. Confira a contagem de
  objetos selecionados antes de mover: o arrasto pode pegar objetos vizinhos.
- Faça login você mesmo; o agente não deve receber nem digitar a sua senha. Não mexa em quadros de outras pessoas e
  só use "selecionar tudo" num quadro criado na sessão.
- No fim, afaste o zoom, capture o quadro inteiro e confira sobreposição, legibilidade e se cada logo está ao lado
  do nó certo.

## Sem conta no Whimsical

`pycode mermaid arquivo.mmd --out desenho.svg` (ou `.png`) gera a imagem localmente. Use o SVG no material, num slide
ou no README do projeto. O Notion também mostra blocos de código `mermaid` como diagrama.
