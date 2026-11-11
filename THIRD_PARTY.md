# Componentes de terceiros

O código deste repositório é MIT. Os componentes abaixo têm licença própria e **não ficam versionados aqui**: o instalador baixa cada um para a sua máquina (`~/.pycode-skills/`), com versão fixada e hash conferido, e os comandos `pycode ... new` copiam para dentro do projeto que você cria.

| Componente | Uso | Licença | Origem |
|---|---|---|---|
| Fontes (Geist, Geist Mono, Inter, JetBrains Mono, Space Grotesk, Bricolage Grotesque, Fraunces, Playfair Display, Caveat, Instrument Serif, Anton, Bebas Neue, Syncopate, Press Start 2P, VT323, Jersey 10) | Tipografia dos estilos | SIL Open Font License 1.1 | Pacotes [Fontsource](https://fontsource.org) no npm, versão em `tools/vendor_manifest.json` |
| GSAP e plugins | Animação de aulas e páginas | [GSAP Standard License](https://gsap.com/standard-license) (uso gratuito) | Pacote `gsap` no npm |
| Simple Icons | Ícones de marcas, baixados sob demanda com `pycode icon` | CC0 1.0 (as marcas pertencem aos seus donos) | [simpleicons.org](https://simpleicons.org) |
| Playwright + Chromium | Capturas, renderização e QA | Apache 2.0 / BSD | [playwright.dev](https://playwright.dev) |
| Lighthouse | Medição de performance | Apache 2.0 | [GoogleChrome/lighthouse](https://github.com/GoogleChrome/lighthouse) |
| csso | Minificação de CSS | MIT | [css/csso](https://github.com/css/csso) |
| Mermaid CLI | Validação de diagramas | MIT | [mermaid-js/mermaid-cli](https://github.com/mermaid-js/mermaid-cli) |
| Pillow, NumPy, OpenCV, imageio-ffmpeg (FFmpeg), PyYAML | Imagens, composição e vídeo | Licenças dos projetos | PyPI |
| Node.js | Executa as ferramentas acima quando não há Node no sistema | MIT | [nodejs.org](https://nodejs.org) |

## Galerias de referência de design

`pycode refs fetch` baixa acervos públicos de estudo para `~/.pycode-skills/references/`. Eles servem para estudar composição, movimento e interação. Os acervos sem licença explícita não podem ser redistribuídos nem copiados para os seus projetos: use como referência e escreva o seu próprio código. A lista, com a licença de cada origem, aparece em `pycode refs list`.

## Sons e imagens

Nenhum som, música, foto ou imagem de banco acompanha este repositório. Quando uma skill sugerir uma fonte gratuita, guarde a licença junto do projeto em que você usar o arquivo.
