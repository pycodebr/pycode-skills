# Slides em vídeo e som

O Instagram aceita imagem e vídeo no mesmo carrossel, e o som do vídeo toca quando a pessoa arrasta até ele. Um slide em vídeo de 4 a 6 segundos, normalmente a capa, é o que mais prende.

## Animação determinística (`setT`)

```js
Carousel.animate(1, (t, slide, dados) => {
  const p = Carousel.ease.out(Carousel.prog(t, 0.3, 1.2));   // 0 a 1 entre 0,3 s e 1,5 s
  slide.querySelector('.carta').style.transform = `translateY(${(1 - p) * 80}px)`;
}, { duration: 5 });
```

- A função recebe o tempo `t` em segundos e deixa o slide exatamente no estado daquele instante. Nada de `Date.now()`, `Math.random()`, `requestAnimationFrame` ou transição CSS dentro dela: o comando `video` chama `setT(k / fps)` quadro a quadro e captura cada um.
- Mova com `transform`, `opacity` e `stroke-dashoffset`. Troca de classe (aceso, apagado) também é determinística.
- Desenho em canvas é refeito a cada `t` (o exemplo do fliperama redesenha o cenário de 180x225 por quadro).
- No navegador, o slide animado toca em laço só enquanto aparece na tela e respeita `prefers-reduced-motion` (mostra o estado final parado).

## Pôster no quadro 0 e imagem estática

- O **quadro 0** é o pôster: aparece antes do play, na grade do perfil e para quem não tem o vídeo carregado. Ele já precisa ter o título inteiro e o objeto herói em pé. Cena toda apagada é pôster fraco; use luz de espera.
- O `render` grava a imagem estática do slide animado no instante `video.still` do `slides.json` (padrão: o fim da animação). Ela serve de alternativa se você publicar só imagens.
- O QA confere o slide no estado final e também no quadro 0.

## Gravação

```bash
pycode carousel video pasta --slide 1                     # usa video.seconds do slides.json
pycode carousel video pasta --slide 1 --seconds 5 --fps 30 --audio audio/trilha.wav --normalize
```

Saída: `out/slide-01.mp4` (H.264 High, yuv420p, 30 fps, 1080x1350, faststart) e `out/slide-01-poster.jpg`.

- **Cor BT.709.** Os quadros saem do Chromium em RGB; a conversão para yuv420p usa a matriz BT.709 com as tags de cor no arquivo. Sem isso o conversor usa BT.601 e as cores da marca deslocam (o amarelo esverdeia, o azul desbota).
- **faststart:** o índice do MP4 vai para o começo do arquivo, e o vídeo começa a tocar antes de baixar inteiro.
- **Duração:** de 3 a 60 s é aceito; para carrossel, 4 a 6 s.
- **Desempenho:** cada quadro é uma captura do Chromium. Em máquina compartilhada isso leva de 0,3 a 1,5 s por quadro. Filtros SVG em tela cheia, sombras grandes em elementos com 3D e `backdrop-filter` pesam muito; troque por ladrilho de grão (`var(--grain)`) e sombras menores. Grave um slide por vez.

## Som

Nenhum som entra no repositório da skill. Baixe na máquina de quem publica, guarde o arquivo na pasta do post e **guarde a licença em `licencas/`** (o `pack` inclui a pasta). Fontes com licença de uso livre em rede social:

- **Mixkit** (mixkit.co/free-sound-effects): efeitos sob a Mixkit Sound Effects Free License, uso comercial sem atribuição obrigatória. A página da licença abre num modal; salve o texto da licença junto com o ID de cada efeito.
- **Freesound** (freesound.org): filtre por licença CC0. Evite CC BY-NC (proíbe uso comercial).
- **Pixabay Sound Effects** (pixabay.com/sound-effects): licença própria do Pixabay; leia e salve a versão vigente.

Para cada efeito, registre no README do post: arquivo, ID ou URL, licença, data de acesso e o instante em que ele toca.

Mixagem e volume:

- **Alinhe pelo pico do som, não pelo início do arquivo.** Meça em que instante o efeito atinge o pico e posicione esse instante no evento da animação (a carta virando, o trem parando). Alinhar pelo começo do arquivo deixa o som adiantado ou atrasado.
- Mixe os efeitos numa trilha só (ffmpeg com `adelay` e `amix`) com a duração do vídeo.
- `--normalize` mede a trilha no trecho do vídeo, aplica o ganho até ~-16 LUFS e um limitador em -1,5 dBFS. O AAC soma cerca de 1 dB de pico; o comando mede o MP4 final e reprova pico acima de -1 dBFS.
- Trilha só de cliques ou tiques fica perto de -18 LUFS sem esmagar os transientes; é melhor que forçar -16. Um ambiente abafado (passa-baixa) por baixo dos cliques ajuda.
- **Música só pelo app do Instagram**, na hora de publicar. Música com direitos não entra no arquivo.
