# Armadilhas reais

Problemas que já aconteceram em páginas de verdade, com o sintoma e a correção. Leia antes de mexer em CSS
crítico, âncoras, movimento ou QA.

## Build e CSS

- **CSS crítico copiado pela metade**: a captura da primeira dobra com o CSS completo bloqueado mostra o header
  sem fundo ou o hero sem altura. Derive o crítico da cascata completa (tokens, base, componente e media queries)
  e compare a primeira dobra com o CSS externo bloqueado e liberado.
- **Classe criada só por JavaScript não entra no crítico**: um botão de pausa criado por `createElement` ganha
  estilo só quando o CSS completo chega e empurra o layout (CLS). Renderize o elemento no HTML (desabilitado),
  com a geometria no crítico, e só habilite pelo JS.
- **Regex que apaga regra de CSS minificado**: `re.sub(r'\.classe[^\n]*\n', '')` em CSS minificado apaga o resto da
  `@media` inteira e a chave de fechamento. Remova por string exata ou `[^}]*\}` e confira o equilíbrio de chaves.
- **Duração extrema vira `NaN`**: alguns minificadores transformam `.01ms` em `NaN`. Use `.001s`. O build reprova
  CSS com `NaN`.
- **Mudança só em comentário** não muda o minificado (o minificador tira comentários). Não troque a versão do
  cache por isso; o build com hash já cuida.
- **CSS movido de pasta quebra `url()`**: a URL é resolvida a partir do arquivo CSS, não do HTML. O build reescreve
  as URLs de fontes ao incorporar o crítico; se você mover arquivos à mão, teste as requisições reais.
- **Fundo opaco no `html` esconde `body::before` com `z-index: -1`**: a grade ou o brilho somem e a página fica
  chapada. Compare `html`, `body` e `body::before` antes de aumentar opacidade.

## Âncoras

- **Hash certo, posição errada**: com `content-visibility: auto`, o navegador calcula o alvo com alturas
  provisórias e para centenas de pixels antes. Aceite é a posição medida do alvo abaixo do header, não o hash.
- **Fonte que só é pedida quando a seção aparece**: com `content-visibility: auto`, o navegador só baixa a fonte
  (ou o peso, ou o itálico) que uma seção usa quando ela é renderizada. Se isso acontece no meio da rolagem para a
  âncora, a quebra das linhas muda e o alvo para 16 a 130 px fora do lugar, de forma intermitente. O `main.js`
  materializa as seções, espera dois quadros e `document.fonts.ready` antes de calcular a posição, e confere de
  novo depois da rolagem.
- **Uma conferência só depois da rolagem não basta**: em máquina lenta, o layout ainda muda depois que a rolagem
  termina, e o alvo fica escondido atrás do header em uma a cada várias tentativas. O `main.js` confere a posição
  até ela ficar estável em duas leituras seguidas e continua vigiando por três segundos (mudança de altura da
  página e fonte que termina de carregar), parando assim que a pessoa rola, toca ou usa o teclado. Ele publica o
  estado em `<html data-anchor="moving|done">`, e o QA espera pelo `done` em vez de contar tempo fixo. Se você
  trocar o JS de âncoras, mantenha esse aviso ou o QA volta a depender de espera fixa.
- **Teste depois de percorrer a página mascara o erro**: um QA que rolou a página inteira antes de clicar já
  materializou as seções. Teste cada âncora em navegação nova (o `pycode page qa` faz isso).
- **`scroll-padding-top` e `scroll-margin-top` juntos** acumulam os dois deslocamentos.
- **`scroll-behavior: smooth` herdado**: `scrollIntoView` e `scrollTo` também ficam suaves; uma rolagem longa pode
  parar no meio se o layout mudar (fonte chegando, imagem lazy). Role por posição calculada e corrija ao final.
- **Âncora para o header fixo** (`#topo`): a posição do header grudado é sempre 0 na tela, e o cálculo ingênuo não
  rola. Trate como "início da página".
- **Link que só existe no menu do celular**: no desktop, o QA não tem o que clicar. Ponha o mesmo destino no menu
  do desktop ou aceite o aviso conscientemente.

## Movimento

- **Animação que nunca roda e ninguém percebe**: a regra que declara a animação ficou mais específica que a regra
  que a liga. Use `:where()` na declaração e prove com dois quadros.
- **Regra de descendentes não pega pseudo-elemento**: `.cena * { animation-play-state: paused }` não alcança
  `::before`/`::after`. Pause os pseudo-elementos explicitamente.
- **Laço de SVG decorativo pesando no TBT**: animar um `<g>` interno ou a propriedade `rotate` junto com `translate`
  de posicionamento repinta no thread principal. Anime `transform` no próprio `<svg>` ou num wrapper e desligue no
  celular. Para achar o culpado: Playwright com CPU 4x (`Emulation.setCPUThrottlingRate`), observer de `longtask`
  e uma variante por suspeito desligado (animação, `mask-image`, `backdrop-filter`, `text-wrap: balance`).
- **Dois quadros dentro do mesmo atraso** de entrada parecem "parado". Escolha a peça sem atraso ou espere o atraso.
- **Escala de "brilho" acima de 1,02** corta o topo de pílulas dentro de contêiner com `overflow: hidden`.

## Layout

- **`1fr` com conteúdo `nowrap`** expande a coluna e o excesso some atrás de um `overflow: hidden`, sem rolagem
  horizontal. Use `minmax(0, 1fr)`.
- **Classe utilitária que não existe no CSS compilado** (frameworks que só geram o que encontram no código): o
  layout fica errado sem erro. Meça a largura do elemento contra o contêiner em vez de confiar no nome da classe.
- **`img { height: auto }` global** muda a composição de imagens com `aspect-ratio` ou `object-fit`. Aplique só
  em classes verificadas.
- **`order` para inverter no celular** quebra a ordem de leitura. A ordem do HTML é a do celular.
- **Linha de terminal com texto solto em grid**: o texto vira item anônimo e quebra fora de lugar. Cada parte
  (ícone, nome, status) precisa ser um elemento.

## Captura e revisão visual

- **Captura logo depois de `scrollTo` com rolagem suave** registra a posição anterior, e a revisão descreve a seção
  errada. Desligue a rolagem suave, espere e confirme `scrollY` e o topo do alvo antes de capturar.
- **Captura de página inteira** com `content-visibility` e imagens lazy mostra buracos que não existem. Capture a
  viewport de cada seção depois de rolar até ela.
- **Componente maior que a viewport** não cabe num print: capture em duas posições ou aumente a altura da
  viewport na mesma largura.
- **Imagem lazy fora da tela** tem `complete === false`, e isso é correto. Confira `naturalWidth` quando ela está
  visível, não depois de pular para o fim.
- **`innerText` vazio** em seção ainda não renderizada: em testes de texto, use `textContent`.
- **Probe de texto pela captura** não prova ausência de texto cortado; confira também pelo HTML.

## QA e medição

- **Rodadas de Lighthouse em paralelo** com outros testes distorcem TBT e nota. Rode sozinho e registre a carga.
- **Servidor sem gzip** faz o HTML com CSS incorporado parecer pior que CSS externo.
- **Servidor de prévia esquecido** prende a porta e responde vazio. Encerre pelo PID (`kill <pid>`), nunca com
  `pkill -f` de um padrão que também casa com o próprio terminal.
- **Script de QA rodando com `python -O`** desliga `assert` e transforma a suíte em sucesso falso. Os comandos
  desta skill não usam `assert` e recusam rodar com `-O`.
- **Status 200 não prova destino certo**: confira o conteúdo do destino.
- **Formulário testado contra produção** pode criar cadastro real se uma requisição retida for liberada no fim do
  teste. Aborte explicitamente.

## Publicação

- **Deploy concluído não é página publicada**: compare o HTML e um CSS pela URL exata com hash.
- **CDN com cache da URL antiga**: a URL sem hash pode continuar velha mesmo com a página nova no ar.
- **`immutable` em arquivo sem hash** prende a versão velha no navegador de quem já visitou.
