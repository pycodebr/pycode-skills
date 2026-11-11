# Stories 9:16 no mesmo visual e publicação

## Stories a partir do carrossel

Quando pedirem Stories "com o design do carrossel", reaproveite o motor e os objetos do carrossel em vez de criar um visual novo: o objeto continua o mesmo e o público reconhece.

- Formato 1080x1920. Crie uma página `stories.html` na pasta do carrossel que usa os mesmos `css/tokens.css`, `css/fonts.css` e as funções de desenho do `js/scene.js` (copie as que precisar), com seções de 1080x1920.
- Zonas: texto e elementos críticos entre y=250 e y=1600. Em cima fica a barra de progresso; embaixo, o campo de resposta. O objeto pode passar de 1600 só com partes que não precisam ser lidas.
- Texto no terço de cima, objeto herói embaixo, sem texto por cima do objeto.
- Sequência de três: gancho com o objeto fechado ou escondido e um convite para tocar; o que vem dentro, com gancho para o próximo; o objeto completo com o único pedido de ação.
- Capture com `pycode shot stories.html --sizes 1080x1920 --selector ".story:nth-of-type(1)" --out out --name story-01` (um comando por Story) e monte uma folha com linhas guia em 250 e 1600 para revisar por visão.

Os comandos `carousel render`, `qa` e `video` trabalham em 1080x1350; para Stories, a conferência de zonas e de texto é feita por visão e por `pycode text`.

## Publicação

- **Pelo app.** O carrossel aceita de 2 a 20 mídias, misturando imagem e vídeo. Suba na ordem dos arquivos do pacote (`slide-01`, `slide-02` e assim por diante).
- **Vídeo no carrossel:** o som toca quando a pessoa arrasta até ele. O pôster (quadro 0) aparece antes do play; por isso ele precisa funcionar sozinho.
- **Música:** só pela biblioteca do próprio app, na hora de publicar. Não coloque música com direitos no arquivo.
- **Proporção:** todos os slides em 4:5 (1080x1350). O Instagram corta a mídia de um carrossel pela proporção da primeira; misturar proporções corta slides.
- **Grade do perfil:** a grade mostra um recorte mais estreito do slide 1. A margem segura de 64 px nas laterais mantém título e âncoras visíveis.
- **Legenda:** copie de `legenda.md`. Confira que a primeira linha é o pedido de ação e que os comandos completos estão lá.
- **Depois de publicar:** responda dúvidas técnicas com o mesmo cuidado do post (rode o código antes de responder).
