# QA, revisão por visão e celular

## O que o `pycode deck qa` confere

O QA abre o deck no Chromium do Playwright, bloqueia qualquer requisição para fora de 127.0.0.1 e sai com erro se uma
verificação falhar (fail-closed). Por cena:

| Teste | Falha quando |
|---|---|
| `?still` em 1920×1080 | erro de console, elemento fora do palco, `.fill` transbordando, texto abaixo de 16 px, imagem quebrada |
| Orçamento de palavras | mais palavras no palco que o `budget` da cena (padrão 30; blocos de até 3 palavras são rótulos e não contam, títulos sempre contam) |
| Itens clicáveis | nenhum `ctx.pick`, item focável sem `aria-label`, nenhum item alcançável pelo mouse |
| Demonstração acelerada (10×) | não termina em `home`, não volta à chave inicial, não troca a seleção, continua mudando depois de voltar |
| Clique | não assume (estado `manual`), outro item não muda a seleção, a cena muda sozinha depois do clique, troca de cena |
| R | não recomeça a demonstração (antes e depois do clique) |

E para o deck: setas, PageUp/PageDown, espaço, Home/End, borda direita do palco, Tab até um item e Enter, teclas
`?`, `O`, `B`, `M` e `T`, deep link `#3` e `#<id>`, posição salva, movimento reduzido (estado final e clique
funcionando), modo leitura em 390 px (sem rolagem lateral, todas as cenas, texto de 12 px ou mais), celular em
retrato (palco no topo, resumo com título) e em paisagem (palco inteiro, sem rolagem) em todas as cenas.

Saídas: `qa/qa.json`, `qa/shots/` (estado final, depois do clique, leitura, celular) e `qa/folha-de-contato.jpg`.
O tempo total aparece no fim (o modelo de 10 cenas leva cerca de 3 minutos numa máquina compartilhada).

Durante a iteração: `pycode deck qa --only capa,viagem --fast` (pula celular, leitura e movimento reduzido).

Os avisos de "textos sobrepostos" não reprovam: são candidatos para você olhar na captura.

## Revisão por visão (quem avalia é você)

O QA mecânico não diz se a cena está bonita nem se explica. Depois de cada rodada:

1. Abra `qa/folha-de-contato.jpg` (todas as cenas) e procure monotonia (cenas parecidas em sequência), aparência de
   modelo genérico, grade de cartões, texto demais, áreas mortas.
2. Abra as cenas em pares, em tamanho grande (`pycode sheet qa/shots/still-01-*.png qa/shots/still-02-*.png
   --out pares.jpg --cols 1 --width 1400`), e procure problemas concretos: rótulo cruzado por linha, balão cobrindo o
   que explica, elemento cortado, alinhamento, contraste, hierarquia.
3. Veja as capturas `click-*` (balão depois do clique) e as de celular (`celular-retrato-*`, `celular-paisagem-*`,
   `leitura-390*`).
4. Peça ao revisor de imagem só problemas concretos, cena por cena, e ignore o que ele não conhece (barra do
   apresentador, rodapé do fio). Meça por código o que ele estima (sobreposição, transbordo, tamanho de fonte).
5. Itere até cada cena merecer 8 de 10: objeto próprio do assunto, leitura imediata, pouco texto, nada cortado.

Para capturar um estado intermediário (por exemplo, a demonstração no meio), use o navegador do seu agente ou um
script com `presentation.show(i)` e espere alguns segundos sem `?still`.

## Celular

- **Paisagem** (844×390, por exemplo): palco inteiro, barra de controles que some quando a pessoa não mexe.
- **Retrato** (390×844): palco ao vivo no topo, com aviso para girar o aparelho, título, apoio, `<details>` com o
  conteúdo completo (`reading`) e botão para o modo texto. O toque assume a cena no clique (rolar a página não pausa).
- **Modo leitura** (`?leitura`): todas as cenas como texto. É o que vale enviar para quem vai estudar pelo celular.
- Objetos desenhados para 1920 ficam pequenos no retrato: por isso o resumo embaixo existe. Se uma cena for
  ilegível no retrato, simplifique o palco antes de tentar um layout próprio para celular.
- Antes de entregar uma URL publicada, capture 390×844 e 844×390 da própria URL (`pycode shot <url>#3 --sizes
  390x844,844x390`): o QA local não vê o que o servidor entrega.

## Desempenho

O motor só anima a cena ativa e pausa tudo com a aba escondida. Em máquinas lentas, o fundo animado pode ser
desligado por cena (`"bg": "nenhum"`). FPS medido em servidor sem GPU não serve como prova; meça em um computador
comum se a pessoa reclamar de travamento.
