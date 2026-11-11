# {{TITLE}}

Projeto criado com a skill `pycode-paginas` (modelo `{{KIND}}`, estilo `{{STYLE}}`).

## Estrutura

- `src/`: o que você edita. Abra com `pycode serve src` para ver enquanto muda.
  - `index.html` e as demais páginas.
  - `css/tokens.css`: cores, fontes, raios e sombras do estilo. Os outros CSS só usam estas variáveis.
  - `css/fonts.css`: `@font-face` das fontes locais e do fallback métrico (gerado; não edite à mão).
  - `css/critical.css`: só o que a primeira dobra usa. Vai incorporado no HTML, com limite de 15 KB.
  - `css/styles.css`: o resto da página, carregado sem bloquear a primeira pintura.
  - `js/main.js`: âncoras, movimento por componente e repasse de parâmetros da URL.
  - `img/`, `fonts/`, `_headers`, `.htaccess`, `robots.txt`.
- `og.html`: a imagem de compartilhamento (1200x630). Depois de editar, rode `pycode page og`.
- `dist/`: gerado pelo build. É esta pasta que vai para a hospedagem.
- `pycode-page.json`: configuração do projeto (URL pública, caminho base, fontes).

## Fluxo

```bash
pycode page build .        # gera dist/ (CSS crítico incorporado, hashes, conferência de reprodutibilidade)
pycode page qa .           # navegador real: 1440/820/390/320, âncoras, sem JS, movimento, CLS...
pycode page perf .         # Lighthouse celular e desktop, mediana de 3 rodadas
pycode page check-links .  # links e arquivos referenciados
pycode page images img/foto.png --widths 480,960,1600   # variantes responsivas
```

Antes de publicar, troque o destino do formulário (`action`) e a URL em `pycode-page.json` (`site_url`).
