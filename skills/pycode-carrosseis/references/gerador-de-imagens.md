# Com e sem gerador de imagens

A skill produz carrossel de alto nível nos dois casos. A regra que vale para os dois: **texto, números, comandos e interfaces nunca saem do modelo de imagem.** O modelo troca letras, inventa caracteres e erra acentos. Tudo que precisa ser lido é renderizado por código (HTML no Chromium) por cima da cena.

## Sem gerador (caminho padrão)

O conceito inteiro é construído em código: SVG para objetos e diagramas, canvas para pixel art e numerais, HTML e CSS para cartões, telas e placas. Os quatro exemplos em `examples/` foram feitos assim. O que faz isso parecer objeto, e não cartão:

- **Volume e luz:** faces com tons diferentes do mesmo token (`color-mix(in srgb, var(--accent) 72%, black)` para a face da frente, mais escuro para a lateral), sombra projetada, um foco de luz radial atrás do objeto.
- **Material:** moldura holográfica com `conic-gradient` dos tokens e `mix-blend-mode`, papel com canto dobrado, metal com faixa de brilho, tela com linhas de varredura.
- **Textura:** o runtime expõe `--grain` (ladrilho de ruído desenhado uma vez em canvas). Use `background: var(--grain)` com opacidade baixa e `mix-blend-mode: overlay`. Evite `feTurbulence` em tela cheia: ele é recalculado a cada quadro e deixa o vídeo muito lento.
- **Cenário:** o objeto vive num lugar (mesa de feltro, parede de azulejo, céu com prédios), nunca solto num fundo liso.
- **Determinismo:** qualquer aleatoriedade usa `Carousel.rng(semente)`, para o mesmo slide sair igual em todo render e em todo quadro do vídeo.

## Com gerador

Use o gerador de imagens do seu agente só para **cena e objeto herói, sem texto**: um escritório, uma estação, uma maleta, uma cabine, um objeto 3D. Depois componha por cima, em código, tudo que se lê.

### Prompt de cena sem texto

```
Vertical 2:3 (1024x1536), photorealistic night scene of [cenário], one hero object: [objeto],
placed in the [terço direito / centro], top 12% empty dark area, bottom 30% darkening to [cor do fundo],
lighting [tom de luz], palette [cores do estilo]. No text, no letters, no numbers, no logos,
no watermarks, no user interface. The [screen / sign / paper] surface is perfectly uniform flat
pure magenta #FF00FF, no reflections on it.
```

- Declare orientação e proporção no próprio prompt e confira o tamanho que saiu.
- Peça o objeto fora da área do texto e o topo vazio, senão ele encosta nas âncoras e no título.
- Superfície que vai receber conteúdo (tela, placa, papel) em magenta puro, chapado, sem reflexo.
- Se o modelo desenhar pseudo-texto em algum canto, peça uma edição só para remover aquilo, preservando o resto.

### Tela magenta e homografia

```bash
pycode carousel compose --scene cena.png --content tela.html --out cena-com-tela.png
pycode carousel compose --scene cena.png --content print.png --out cena.png --paper   # papel ou placa sem luz própria
```

O comando acha a maior região magenta, ajusta retas às quatro bordas (no trecho central de cada lado, o que ignora cantos arredondados), projeta o conteúdo com homografia em supersampling 2x, remove o magenta que vazou para a moldura e acrescenta preto de tela, sombra interna, brilho diagonal do vidro, luz vazando e grão. Ele avisa quando a proporção do conteúdo difere da tela: use o aspecto físico do aparelho (16:10, 3:4, cartão 1,6), não o do quadrilátero em perspectiva. Se sobrar magenta na imagem final, o comando falha.

Para testar sem gerador, desenhe uma cena sintética com OpenCV (um retângulo magenta em perspectiva sobre um fundo) e rode o `compose` nela.

### Mesma cena entre slides

A progressão do carrossel depende de o cenário continuar o mesmo (a mesma maleta, a mesma estação, o mesmo escritório):

- Gere a **cena base** uma vez. Cada variação (outra hora do dia, outro compartimento aberto, outra luz) sai por **edição da cena base**, passando a imagem como referência e pedindo só a mudança.
- Para acender partes de uma cena (degraus, LEDs, painel), gere a versão acesa e uma edição "apagada"; a geometria sai alinhada e você compõe `apagada + (acesa - apagada) × peso` por região e por tempo no vídeo.
- Registre prompts e arquivos de cada cena num `prompts.md` da pasta do post.

### Enquadrar 2:3 em 4:5 medindo

```bash
pycode carousel fit cena.png --to 4:5                 # corta medindo onde está o conteúdo
pycode carousel fit cena.png --to 4:5 --mode pad      # mantém tudo e completa as laterais
```

O corte central às cegas costuma decapitar o objeto ou cortar o chão. O `fit` mede bordas e contraste fora do tom de fundo, escolhe a janela 4:5 que guarda mais conteúdo, centraliza no conteúdo e reduz para 1080x1350 sem esticar. Ele avisa quantos pixels de conteúdo perdeu em cada lado; se perdeu, use `--mode pad`, que completa as laterais com a própria imagem desfocada e escurecida.

### Conferência por visão

Depois de compor, olhe cada slide perguntando:

- O objeto tem cara de colado (luz vindo de outro lado, sombra faltando, borda dura)?
- Sobrou pseudo-texto, magenta ou reflexo arroxeado na moldura?
- O texto renderizado ficou sobre área limpa, com contraste?
- A cena é a mesma do slide anterior (objeto, cor, ângulo)?

Imagens geradas para um post ficam na pasta do post, com o prompt registrado. Não reaproveite rosto de pessoa real gerado por IA.
