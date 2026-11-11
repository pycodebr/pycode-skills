# Planejar a aula antes do código

Uma aula interativa boa nasce de um roteiro de cenas, não de um arquivo HTML. Este guia mostra como sair do pedido
("quero uma aula sobre X") para um roteiro aprovado, que depois vira `src/content.json`.

## 1. Entenda o pedido e o público

Pergunte (ou deduza do pedido) e anote no topo do roteiro:

- **Quem assiste:** iniciantes, pessoas que já programam, gestores. Isso define vocabulário e profundidade.
- **Duração:** conte de 1,5 a 3 minutos de fala por cena. Uma aula de 20 minutos tem de 8 a 12 cenas.
- **O que a pessoa sabe fazer no fim:** uma ação observável ("ler um pedido HTTP e dizer o que cada parte faz").
- **Onde a aula vai rodar:** telão com apresentador (palco), link enviado aos alunos (celular e modo leitura) ou os dois.

## 2. Problema antes do mecanismo

A primeira cena depois da capa mostra a situação que dói ou a pergunta que o assunto responde. Só depois vem o
mecanismo. No modelo "Como funciona uma API", a ordem é: dois programas precisam conversar (problema), o que acontece
sem um contrato (problema concreto), as peças de um pedido (mecanismo), o caminho, as camadas, a resposta, o tempo,
o contexto e o fechamento com uma atividade.

## 3. Roteiro de cenas

Escreva uma tabela antes de abrir o editor. Uma linha por cena:

| # | id | Título (2 a 5 palavras) | Mensagem em uma frase | Visual que explica | Arquétipo | Gancho para a próxima |
|---|---|---|---|---|---|---|
| 1 | capa | Como funciona uma API | O caminho de um pedido entre o app e o servidor | constelação em volta da API | capa | uma conversa entre dois programas |
| 5 | viagem | A viagem do pedido | O pedido passa por pontos com tarefas curtas | circuito com o pedido andando | circuito | dentro do servidor há camadas |

Regras do roteiro:

- **Cada cena tem um visual próprio que explica a ideia.** Relógio, circuito, mapa, pilha, balança, régua de tempo,
  terminal. Se a ideia de visual for "título e três cartões", a cena ainda não foi pensada. Nada de grade de cartões
  iguais.
- **Título curto e que nomeia o assunto** (de 2 a 5 palavras). Sem rótulo em caixa alta acima do título.
- **Varie a composição.** Não repita o mesmo arranjo (texto à esquerda e objeto à direita) em cenas seguidas.
- Use `pycode deck scene list` para escolher arquétipos e `references/arquetipos.md` para saber quando usar cada um.
  Um arquétipo é ponto de partida: adapte rótulos, ícones, posições e, se preciso, o desenho.

## 4. Fio visual

Escolha um objeto que atravessa a aula e se completa no fim. No modelo é o "pedido 42": ele sai do app na capa,
aparece como mensagem na conversa, é montado no terminal, viaja no circuito, desce as camadas, volta com um código e
fecha o circuito no encerramento. O motor ajuda com a trilha do rodapé (`thread` em cada cena e `meta.thread`): cada
cena acende uma parada e o fio fica completo na última.

Boas escolhas de fio: um pedido, um arquivo, um cliente fictício, uma moeda, uma peça que vai sendo montada. O fio
precisa aparecer no visual de pelo menos três cenas, não só no rodapé.

## 5. Laços abertos entre cenas

Cada cena termina com um gancho curto (`hook`) que puxa a próxima: "Montado, o pedido sai para a rede. Vamos seguir o
caminho dele." O gancho aparece no canto do palco e no modo leitura. Escreva também nas notas de fala (`notes`) a
frase que você vai dizer na passagem.

## 6. Orçamento de texto: palco, leitura e Notion

O mesmo conteúdo vive em três lugares, com densidades diferentes:

| Lugar | O que entra | Limite |
|---|---|---|
| Palco (`title`, rótulos, `data` da cena) | título, rótulos de até 3 palavras, uma frase curta no balão do clique | até ~30 palavras visíveis em repouso; nada abaixo de 16 px |
| Modo leitura e celular (`apoio`, `reading`) | a explicação completa de cada cena, em frases inteiras | sem limite rígido; escreva para quem não assistiu |
| Notion (`meta.study`, `study` da cena) | explicação, exemplos de código, diagramas, exercícios com gabarito, fontes | o material de estudo completo |

O QA conta as palavras do palco em blocos com mais de 3 palavras (títulos sempre contam). Se a cena precisa de mais
texto porque o texto é o objeto (uma conversa, um terminal, uma citação), declare `"budget": N` na cena e explique
nas notas. Texto denso no palco é defeito: corte para a fala, o modo leitura ou o Notion.

## 7. Escrita

- PT-BR natural, com acentos, frases completas, artigos e conectores.
- Proibido: travessão como pontuação, reticências de suspense, "não é X, é Y", frases curtas em série para dar impacto,
  perguntas retóricas em série, clichês ("jornada", "incrível", "simplesmente", "poderoso"; a lista completa está no `pycode text`).
- Sem promessa de resultado, emprego ou prazo de aprendizado.
- Rode `pycode text src/content.json` antes de construir; o `deck build` repete a checagem e recusa erros.

## 8. Aprovação

Mostre o roteiro (a tabela) para a pessoa antes de construir as cenas. Mudança de roteiro depois das cenas prontas
custa caro; mudança de texto no `content.json` custa pouco.
