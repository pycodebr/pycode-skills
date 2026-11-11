# Princípios de design

Regras que valem para qualquer estilo da biblioteca. Elas existem porque a maioria das páginas geradas por IA falha nos mesmos pontos, e quem vê percebe em um segundo.

## 1. Escolha a superfície antes da cor

Antes de pensar em paleta, diga em uma frase que tipo de tela você está fazendo. A maior parte do "cara de template" vem da composição, não da cor: herói centralizado mais três cartões iguais, repetido em qualquer assunto.

| Superfície | O que a pessoa faz | Composição certa |
|---|---|---|
| Convencer ou ensinar | lendo uma ideia por vez | uma ideia por seção, um objeto herói |
| Acompanhar | olhando estado mudar | densidade, leitura rápida, sem herói |
| Comparar | escolhendo entre opções | colunas alinhadas, um diferencial destacado |
| Configurar | preenchendo algo | blocos progressivos, pouca decoração |
| Explorar | navegando num acervo | filtros, grade de resultados, prévia |

Um painel de métricas não ganha herói. Uma página de inscrição não vira tabela.

## 2. Um objeto herói por cena

Cada seção, slide ou card de carrossel tem um objeto principal ligado ao assunto: um ingresso para um encontro ao vivo, uma planta para uma arquitetura, um mostrador para uma métrica, uma carta para uma ferramenta. O texto fica numa área limpa ao lado ou acima.

Perguntas para escolher o objeto:

1. Que coisa do mundo real faz o que esse conteúdo faz? (agenda → calendário, permissão → porta, sequência → linha de metrô)
2. Dá para desenhar com HTML, CSS e SVG sem imagem gerada?
3. Ele ganha movimento com sentido (o canhoto destaca, a planta se desenha, o ponteiro oscila)?

O DESIGN.md de cada estilo lista os objetos que combinam com ele.

## 3. Sinais de página gerada (e o conserto)

| Sinal | Conserto |
|---|---|
| Degradê roxo e azul em tudo | volte para a paleta do estilo; brilho só localizado |
| Grade de três cartões com ícone, título e frase | troque por um objeto e uma lista com hierarquia |
| Rótulo em caixa alta acima de cada título de seção | apague; o título basta |
| Ícone num quadrado arredondado acima de cada título | apague ou troque por um desenho do estilo |
| Faixa colorida na borda esquerda do cartão | use fundo levemente diferente ou fio |
| Número gigante sem história ("+300%") | só mostre números reais e explicados |
| Tudo centralizado | alinhe à esquerda e crie uma coluna de leitura |
| Desfoque de vidro sem motivo | profundidade por camadas e bordas |
| Emoji como ícone | desenhe em SVG ou use `pycode icon` para marcas |

Diagnostique antes de consertar: liste quais sinais aparecem, depois mexa na composição (se o problema for estrutura) ou na cor e na tipografia (se for acabamento). Recolorir um layout ruim não salva o layout.

## 4. Hierarquia

- Tamanho primeiro, peso depois, cor por último. Se você precisa de cor para separar título de texto, o tamanho está errado.
- No máximo três tamanhos de texto por tela, além do título.
- Uma coluna de leitura com 55 a 75 caracteres por linha.
- O que é clicável parece clicável: altura mínima de 44 px no celular, contraste de 3:1 para a borda do botão.

## 5. Densidade

Denso não é bagunçado e vazio não é elegante. A densidade certa depende da superfície: painel e documento aguentam mais informação; capa de carrossel e abertura de aula pedem uma frase e um objeto. Se um slide parece vazio, resolva com escala, ritmo ou um objeto, nunca com texto de enchimento.

## 6. Contraste e cor

- Texto normal com 4,5:1 sobre o fundo; texto grande (a partir de 24 px, ou 19 px em negrito) com 3:1.
- A cor de destaque aparece em poucos pontos por tela e sempre com função: ação, palavra-chave, estado.
- Cada cor tem um significado fixo dentro do conteúdo. Se o amarelo é "pedido" no primeiro slide, continua sendo no último.
- `pycode contrast <texto> <fundo>` confere um par; `pycode styles check` confere os pares do contrato.

## 7. Texto

O visual não salva texto ruim. Frases completas, com artigos e conectores. Nada de travessão como pontuação, reticências de suspense, "não é X, é Y", frases curtas em série para dar impacto, perguntas retóricas em série ou clichês de anúncio. Rode `pycode text` nos arquivos antes de entregar.

## 8. Revisão por visão

Captura não é formalidade. Abra as imagens em 1440 e 390 e procure: texto cortado, peça cobrindo texto, objeto que virou miniatura no celular, seção sem objeto, monotonia entre seções, contraste fraco. Se dois estilos parecem o mesmo com outra cor, um deles está genérico.
