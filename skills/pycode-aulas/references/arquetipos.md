# Catálogo de arquétipos de cena

`pycode deck scene list` mostra a lista; `pycode deck scene add <pasta> --archetype <nome> --id <id>` copia o
arquétipo e um texto de exemplo para o projeto. Cada arquétipo é uma cena completa (intro, demonstração única,
clique para assumir, estado final legível, celular). Adapte rótulos, ícones, posições e cores; reescreva o desenho
quando o assunto pedir outro objeto. Os exemplos abaixo vêm do deck modelo "Como funciona uma API".

Em repouso, "home" é o estado em que a demonstração começa e termina; "still" é o que aparece em `?still`, com
movimento reduzido e na exportação.

## capa
Título grande à esquerda e uma constelação de objetos ligados a um núcleo, com pacotes correndo pelas ligações.
- **Use para:** abrir a aula mostrando os personagens do assunto em volta da ideia central.
- **Demonstração:** acende cada satélite com uma frase curta. Repouso e still: limpos.
- **data:** `subtitle`, `byline`, `core {label, icon}`, `satellites [{label, icon, tip, angle?}]` (de 3 a 6).

## conversa
Um celular com a troca de mensagens e, ao lado, a versão técnica de cada mensagem ligada por um fio.
- **Use para:** protocolos, atendimento, perguntas e respostas entre sistemas ou pessoas; mostrar que "por baixo" da
  conversa existe um formato.
- **Demonstração:** destaca cada mensagem e digita a versão técnica. Still: a última mensagem.
- **Texto é o objeto:** declare `budget` (o modelo usa 75). Mensagens curtas, no máximo 4 ou 5.
- **data:** `a`, `b` (nomes dos lados), `wire` (rótulo do painel), `messages [{from: "a"|"b", text, code, note}]`.

## antes-depois
O mesmo cenário em dois estados: à esquerda o emaranhado, à direita a versão organizada com regras em volta da peça
central.
- **Use para:** justificar uma prática (API, testes, versionamento, cache) mostrando o custo de não ter.
- **Demonstração:** foca o antes, o depois e cada regra. Clique em cada metade ou regra.
- **data:** `before {chip, label, tip}`, `after {chip, label, tip, gate}`, `db`, `clients [{label, icon}]` (4),
  `rules [{label, tip}]` (até 4).

## terminal
Um comando é digitado, a resposta aparece e as partes importantes ficam sublinhadas e clicáveis, com a explicação ao
lado e um fio saindo da borda do terminal.
- **Use para:** comandos, requisições, trechos de código, saídas de ferramentas.
- **Demonstração:** percorre as partes na ordem em que aparecem. Still: a primeira parte.
- **Texto é o objeto:** declare `budget` (o modelo usa 60). Quebre linhas longas com `\\\n  ` dentro dos tokens.
- **data:** `prompt`, `title`, `command [{code, part?}]`, `output [{code, tone: ok|muted|json, part?}]`,
  `parts {id: {label, text}}`.

## circuito
Objetos ligados por uma trilha de placa de circuito; o pedido (losango) viaja de nó em nó e volta pela trilha de baixo.
- **Use para:** caminhos de dados, pipelines, etapas de um processo com ida e volta.
- **Demonstração:** um passo por nó e um passo de volta. Still: a volta completa.
- **data:** `nodes [{label, icon, tip}]` (de 3 a 6), `packet`, `back`, `backTip`.

## camadas
Pilha de camadas em perspectiva; o pedido desce camada por camada e a resposta sobe.
- **Use para:** arquitetura em camadas, pilha de tecnologias, níveis de abstração, andares de um processo.
- **Demonstração:** desce pelas camadas e sobe na resposta. Clique na camada ou no rótulo.
- **data:** `layers [{label, icon, tip}]` (de 3 a 5), `drop`, `response`, `responseTip`.

## mostrador
Número grande com rolagem de dígitos e um mostrador em meia-lua com uma faixa por item; a agulha aponta o escolhido.
- **Use para:** códigos, notas, métricas, níveis, categorias numa escala.
- **Demonstração:** gira o número e a agulha por cada item. Still: o primeiro item.
- **data:** `items [{value, family, label, tone: ok|accent|accent-2|warn|danger, tip}]` (de 2 a 6).

## linha-do-tempo
Régua longa que desliza por baixo de um cursor fixo (câmera); um minimapa mostra onde a câmera está.
- **Use para:** tempos (milissegundos, anos, etapas de um projeto), histórias com datas.
- **Demonstração:** a câmera viaja de marco em marco. Still: o último marco.
- **data:** `unit`, `events [{at, label, tip}]`, `scale?` (px por unidade).
- Para escala de anos, use `at` com o ano e `unit: ""`.

## mapa
Mapa de metrô: estação central e linhas coloridas até cada destino; um trem percorre a linha escolhida.
- **Use para:** ecossistemas, integrações, dependências, trilhas de estudo.
- **Demonstração:** uma linha por vez. Repouso e still: o mapa inteiro.
- **data:** `center {label, icon}`, `stations [{label, icon, tone, x, y, tip}]` (de 3 a 7; x e y na prancha de
  1696×716; centro em 848, 372).

## encerramento
O fio da aula fecha o circuito: o pedido passa pelas paradas das cenas anteriores (em cima) e volta pelos próximos
passos (embaixo) até o ponto de partida.
- **Use para:** a última cena, com próximos passos ou atividade.
- **Demonstração:** percorre o circuito e para em cada passo. Repouso e still: circuito completo.
- **data:** `start`, `done`, `steps [{label, tip}]` (de 2 a 4). As paradas de cima vêm das outras cenas.

## comparacao
Dois lados e uma balança; cada critério é uma linha e a balança pende para o lado que vence nele.
- **Use para:** "X ou Y", trade-offs, escolha de ferramenta. Mostre empates (`"="`) quando existirem.
- **data:** `left {label, icon}`, `right {label, icon}`, `rows [{label, winner: l|r|=, tip}]` (até 4).

## escala
Barras horizontais em escala logarítmica para grandezas muito diferentes.
- **Use para:** tempos de acesso, tamanhos de arquivo, custos, populações. O balão traduz o número para algo do dia a
  dia ("na mesma proporção: 25 minutos").
- **data:** `unit`, `log` (padrão verdadeiro), `ticks [{v, label}]`, `items [{label, value, display, tip}]` (até 5).
- Cite a fonte dos números no `apoio` ou nas notas.

## citacao
Frase grande com aspas da fonte do estilo e trechos sublinhados clicáveis.
- **Use para:** princípios, definições oficiais, uma frase de referência com autoria verificável.
- **Texto é o objeto:** declare `budget` (o exemplo usa 40). Indique "tradução livre" quando traduzir.
- **data:** `quote`, `marks [{phrase, tip}]` (cada `phrase` aparece literalmente em `quote`), `author`, `source`.

## Quando nenhum arquétipo serve

Copie o mais parecido (`scene add`), troque o id e reescreva o desenho mantendo o contrato: `focus(i, anim)` como única
função que muda o estado, `FX.cycle` para a demonstração, `ctx.pick` nos objetos, `home`, `key` e `still`. Objetos
que o assunto pede (relógio de 24 horas, prédio de andares, ficha que se monta, gráfico acumulando meses) valem mais
do que adaptar um arquétipo à força.
