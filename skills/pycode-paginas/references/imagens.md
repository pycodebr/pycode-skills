# Imagens

## Quando há material real

Fotos do produto, capturas de um sistema rodando, retrato autorizado: use, com as variantes responsivas.

```bash
pycode page images src/img/bancada.png --widths 480,960,1600 --alt "Bancada do estúdio com dois notebooks abertos"
pycode page images src/img/hero.png --widths 640,1200,1800 --format both --eager --sizes "(max-width: 1000px) 100vw, 48vw"
```

O comando nunca amplia além do original (se pedir 1600 e a foto tem 1200, entrega 1200), tira metadados,
grava `images.json` com bytes e sha256 e imprime o HTML:

```html
<img src="img/bancada-1600.webp" srcset="img/bancada-480.webp 480w, img/bancada-960.webp 960w, img/bancada-1600.webp 1600w"
     sizes="(max-width: 760px) 100vw, 50vw" width="1600" height="1067" alt="Bancada do estúdio..." loading="lazy" decoding="async">
```

- `width`/`height` reservam o espaço (sem salto de layout); o CSS pode continuar com `max-width: 100%; height: auto`.
- `sizes` diz quanto da tela a imagem ocupa em cada largura. Errado para mais, o celular baixa a versão grande.
- `--eager` só na imagem da primeira dobra (a candidata a LCP): `loading="eager" fetchpriority="high"`.
- `--format both` gera AVIF (menor) e WebP (reserva) num `<picture>`, quando o Pillow da instalação grava AVIF.
- Captura de interface: renderize com `pycode shot` no tamanho exato do espaço e converta com `pycode page images`.
  Confira se o texto da interface continua legível no tamanho em que a imagem aparece no celular.

## Quando o agente tem gerador de imagens

Use o gerador para imagem que é ilustração assumida (textura, cena, objeto fotográfico de apoio), nunca para:

- simular captura de tela, depoimento, conversa, resultado de cliente ou foto de pessoa real;
- texto exato (o gerador erra letras; texto vai no HTML);
- logotipo de marca (use `pycode icon` para ícones de marca do Simple Icons, baixados no projeto).

Fluxo: gere em PNG no tamanho final ou maior, revise por visão (mãos, letras soltas, artefatos), passe por
`pycode page images` e escreva um `alt` que descreva a cena. Guarde o prompt usado num arquivo do projeto, para
refazer depois.

## Quando não há gerador nem foto: SVG e CSS próprios

É o caminho do modelo: todos os objetos (navegador, servidor, folha pautada, pasta, ingresso, estante) são
HTML, CSS e SVG pequeno, com as cores dos tokens. Vantagens: pesam quase nada, ficam nítidos em qualquer tela,
mudam de cor com o estilo e o texto continua selecionável.

- Desenhe com formas simples e cores do contrato (`var(--paper)`, `var(--accent-2)` e os demais). SVG embutido no HTML
  pode usar `var(--token)` no `fill`/`stroke` via CSS.
- Texto dentro do objeto em HTML, não em `<text>` do SVG, para quebrar linha e ser lido por leitor de tela.
- Não desenhe ilustração elaborada fingindo ser produto. Objeto esquemático e honesto funciona melhor.

## Imagem de compartilhamento (og:image)

O `pycode page new` cria `og.html` (1200x630) e renderiza `src/img/og.jpg`. Edite o `og.html` e rode
`pycode page og`. A tag `og:image` precisa de URL absoluta: ajuste `site_url` no `pycode-page.json` e a URL no
HTML antes de publicar.

## Banco de imagens

Fotos de banco (Unsplash, Pexels e similares) não entram em repositório de modelo. No seu projeto, baixe,
guarde a licença junto (um `CREDITOS.md` com autor, link e licença) e trate como material real.

## Conferência

- `pycode page qa` reprova `<img>` sem `alt` ou sem `width`/`height` e imagem que não carregou (`naturalWidth`
  zero) quando entra na tela.
- `pycode page check-links` confere se todo `src` e `srcset` aponta para arquivo que existe.
- Procure imagens que sobraram: `ls src/img` contra `grep -o 'img/[^" ]*' src/*.html`.
