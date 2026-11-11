# Armadilhas conhecidas (e como evitar)

Cada item abaixo já custou tempo em decks reais. Leia antes de escrever cenas novas.

## Demonstração e controle do apresentador

- **Buscar o tempo 0 dentro do `onComplete` da própria timeline trava o GSAP.** O motor adia o `home()` com
  `setTimeout`. Se a sua cena tiver timelines próprias, faça o mesmo.
- **Repetição infinita na demonstração:** o QA espera que a cena volte ao início e pare. Movimento contínuo (pacotes,
  órbitas, trens) vai em `ambient(dt)`, nunca em `repeat: -1` (o build recusa).
- **`gsap.globalTimeline.timeScale(k)` travou o Chromium** com timelines pausadas. Para acelerar no QA o motor usa
  `presentation.speed(k)` por cena; se a cena cria tweens dentro dos passos, exponha `speed(k)` e divida as durações.
- **`FX.cycle`: a espera precisa começar na posição 0.** Sem isso a duração soma depois do último passo e a cena fica
  parada no último item antes de voltar.
- **Intro com `from()` que recomeça no meio** (R, troca rápida de cena) captura o valor intermediário como final e o
  elemento fica deslocado. Use `fromTo()` com o estado final explícito e `clearProps`.
- **`opacity: 1` sem `clearProps`** deixa estilo inline que vence as classes de estado (`.dim`, `.off`). Use
  `clearProps: 'opacity,transform'` nas entradas, exceto em objetos cujo transform é estado (agulha, marcador).
- **Não anime o balão na intro.** Se a demonstração esconder o balão antes de a intro terminar, o tween da intro o
  acende de novo com conteúdo velho. O primeiro passo da demonstração mostra o balão.
- **Balão posicionado com `translate` do CSS e animado no mesmo elemento** aparece deslocado. O `K.tip` separa o
  invólucro (posição) do miolo (animação); siga o mesmo padrão em balões próprios.
- **Medir posição durante animação:** `getBoundingClientRect` inclui transformações em andamento. Para ligar fios e
  balões, use `K.pos` (layout) ou meça depois da intro.

## Cliques

- **Camadas por cima roubam o clique:** rótulos sobre SVG, traços desenhados sobre faixas clicáveis, pacotes e
  marcadores que andam. Ponha `pointer-events: none` (classe `.no-pick`) em tudo que não é item clicável.
- **Elemento clicável de tamanho zero** (contêiner de 0×0 com filhos posicionados) funciona, mas exige que os filhos
  recebam o clique; o QA procura um ponto visível de cada item e reprova se nenhum for alcançável.
- **Um segundo clique para abrir detalhe:** o clique que tira a cena do automático não deve abrir um painel extra.
- **Classe antiga com `pointer-events: none`** reaproveitada num redesenho mata o clique da versão nova; procure a
  classe em todo o CSS.

## Palco, layout e celular

- **Imagem ou desenho maior que a prancha** aumenta a altura do `.fill` e o QA acusa transbordo; recorte no tamanho da
  prancha (1696×716).
- **Trilho com câmera que desliza:** mova a trilha com `transform`, use `overflow: clip` na janela e marque a janela
  com `data-clip` (o QA ignora o que está fora dela). Esmaecimento nas bordas com `mask-image`, e o primeiro e o
  último marco precisam de margem para não nascerem cortados.
- **Cabeçalho reposicionado por uma cena** (como na capa) precisa voltar ao fluxo no modo leitura; o motor já faz
  isso para `.sc-head`. Qualquer outro elemento que a cena tirar do lugar fora do `.fill` precisa da mesma regra.
- **Leitura vertical:** grade de uma coluna com `minmax(0, 1fr)`, não `1fr`, e `white-space: normal` em textos que no
  palco são `nowrap`; senão o celular ganha rolagem lateral.
- **Celular em retrato mostrava só texto** em versões antigas do motor. Agora o palco aparece no topo e o modo texto é
  escolha (menu ou `?leitura`). Capture 390×844 e 844×390 antes de dizer que está pronto.
- **Logo por `mask: var(--m)` com `url()` dentro da variável:** a URL é resolvida a partir da folha de estilo onde o
  `var()` é usado e o logo some sem erro. Grave a URL absoluta ou use `<img>`.

## Desempenho

- O Chromium sem GPU de servidores mede FPS com muito ruído. Meça custo de código (Script + Layout + Recalc Style por
  segundo) e use FPS só como informação.
- O que mais pesou nos decks: `filter: drop-shadow` em SVG animado, `mask-image` e `box-shadow` grandes sobre o canvas
  animado, animar `clip-path` da cena inteira e `getPointAtLength` a cada quadro (use `FX.table`). Transições só com
  `transform` e `opacity`.

## Texto e conteúdo

- **Texto denso no palco** é o defeito mais comum depois de um redesenho "mais visual": o roteiro manda o texto inteiro
  para o `content.json` e alguém o coloca no palco. Palco com título curto, rótulos e um balão; o resto vai para
  `apoio`, `reading` e o material.
- **Dados internos ou números de negócio** que precisam sair de uma aula costumam estar também no gancho da cena
  anterior, nas notas, no material e nos exports. Procure em `site/`, `stills/`, `exports/` e `material/`, não só na
  cena.
- **Capturas usadas no material envelhecem** a cada redesenho: gere de novo com `pycode deck stills` antes de exportar
  ou publicar.

## Processo

- **QA completo demora.** Durante a iteração use `pycode deck qa --only <id> --fast`; rode o QA completo antes de
  entregar e avise a pessoa enquanto ele roda.
- **`pkill -f` com o nome de um script** pode matar o próprio terminal que contém o mesmo texto. Encerre servidores
  pelo PID.
- **Aula grande (20 cenas ou mais) em paralelo:** monte primeiro o projeto com todas as cenas (esboços que já passam
  no build), depois divida por grupos de cenas, cada um dono dos próprios `scenes/<id>.js` e `.css`, com o
  `content.json` como fonte única revisada por uma pessoa só.
