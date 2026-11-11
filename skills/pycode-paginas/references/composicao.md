# Composição e direção de arte

A falha mais comum em página feita por agente é de composição, não de cor: hero centralizado, três cartões
iguais com ícone, outro bloco de cartões, depoimento, rodapé. Trocar a paleta não conserta. O que conserta é
dar a cada assunto um objeto próprio, ligado ao conteúdo.

## A regra do objeto

Cada seção responde a uma pergunta: qual coisa do mundo real (ou da tela) mostra este assunto? O objeto
carrega a informação; o texto ao lado explica. Se você conseguir trocar o objeto de uma seção pelo de outra
sem perder sentido, ele é decoração, não objeto.

Exemplos de mapeamento conteúdo → objeto:

| Conteúdo | Objeto | Por que funciona |
|---|---|---|
| Etapas com duração | régua com segmentos proporcionais ao tempo | a escala mostra o que pesa mais |
| Programa de encontros | folha pautada, ficha ou caderno com furos | parece o material que a pessoa vai usar |
| Comparação de tamanhos ou preços | barras numa régua comum, com o valor escrito | a proporção é verificável |
| Materiais entregues | pasta com folhas em leque e abas nomeadas | mostra que são várias peças, cada uma com nome |
| Data, turma, inscrição | ingresso com canhoto e perfuração | o objeto já diz "isto é uma vaga" |
| Fluxo técnico (pedido e resposta) | dois objetos ligados por vias com pacotes | o movimento explica o fluxo |
| Lista de produtos ou cursos | estante com lombadas de alturas proporcionais | a altura carrega um dado (duração, tamanho) |
| Erro 404 | cartão de resposta HTTP com o caminho pedido | conversa com o tema e orienta |
| Agenda | calendário de papel com o número do mês dominante | reconhecível de longe |
| Antes e depois | duas folhas sobrepostas com um corte diagonal | comparação lado a lado no mesmo espaço |

Quando a escala aparece (barras, régua, estante), ela precisa ser verdadeira: a largura é calculada pelo
dado (`calc(var(--ms) / 38 * 100%)`), e o número aparece escrito. Escala bonita e errada é pior que nenhuma.

## Ritmo da página

- Alterne o lado do objeto (texto à esquerda, objeto à direita, e depois o contrário) e a densidade das seções.
- Alterne o fundo entre `--bg` e `--bg-2` para separar seções sem precisar de faixas decorativas.
- Varie a escala: uma seção com objeto grande ocupando a largura, outra com duas colunas, outra com texto e
  uma lista. Página em que todas as seções têm o mesmo esqueleto parece gerada.
- Uma ideia por seção. Se o título precisa de "e" para caber dois assuntos, talvez sejam duas seções.

## O que não fazer

- **Kicker acima do título** (rótulo em caixa alta tipo "NOSSO MÉTODO" sobre cada h2). Comece direto pelo
  título. Rótulos funcionais dentro de objetos (o "Ingresso" no ingresso, a data no calendário) são permitidos.
- **Grade de cartões iguais** com ícone, título e frase. Se o conteúdo é uma lista, escreva uma lista boa
  (`dl` com termo e descrição) ou dê a ela um objeto.
- **Emoji como ícone**, gradiente roxo e azul genérico, vidro fosco sem motivo, faixa colorida à esquerda dos
  cartões, número gigante sem contexto.
- **Mockup genérico** de celular ou notebook no hero. O hero merece um objeto que só faz sentido nesta página.
- **Ilustração falsa de produto**: não desenhe painel com números inventados como se fosse captura real.
  Ilustração precisa ser legível como ilustração.

## Tipografia e cor pelo contrato

- Título: `var(--font-display)`, `var(--weight-display)`, `var(--tracking-display)`; tamanho com `clamp()`.
- Corpo: `var(--font-body)`, 16 a 19 px, linhas de 55 a 70 caracteres (`max-width: 62ch`).
- Detalhes funcionais (rótulos, números de régua, caminhos): `var(--font-mono)`, nunca abaixo de 12 px.
- Superfícies: `--surface`/`--surface-2` para objetos escuros, `--paper`/`--paper-ink` para objetos claros
  (papel, ingresso, cartão). Destaque com `--accent` e texto `--accent-ink` em cima dele.
- Variações de cor saem de `color-mix(in srgb, var(--token) 30%, transparent)`, não de hexadecimal novo. Assim
  o mesmo HTML funciona com qualquer estilo da `pycode-design`.

## Hero

Responda em três segundos: o que é, para quem, o que a pessoa leva e qual é o próximo passo. Título como frase
concreta (o modelo usa o `--title` como h1), um parágrafo de apoio, uma ação principal e uma secundária, e
fatos curtos numa lista de definição. O objeto do hero tem dimensões reservadas no CSS crítico para não causar
salto de layout.

## Revisão por visão

Ao revisar capturas, pergunte coisas objetivas: há sobreposição, texto cortado, objeto ilegível no celular,
contraste baixo, espaço vazio sem motivo, título quebrado em palavra órfã? Meça pelo DOM o que a imagem não
decide (largura de um elemento contra o contêiner, posição de uma âncora). Uma captura que "parece boa" não
substitui o QA.
