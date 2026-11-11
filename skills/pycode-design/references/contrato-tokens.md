# Contrato de tokens

Todo estilo define, no `:root` do `tokens.css`, as mesmas 24 variáveis. Os modelos de aula, página e carrossel usam só elas para cor, tipografia, raio e sombra; por isso qualquer estilo funciona em qualquer modelo.

| Variável | Papel |
|---|---|
| `--bg` | fundo principal |
| `--bg-2` | fundo alternado (faixas, slides, barra lateral) |
| `--surface` | cartões, painéis e janelas |
| `--surface-2` | segundo nível de superfície, hover e estados ativos |
| `--text` | texto principal |
| `--muted` | texto secundário, legendas e rótulos (4,5:1 sobre `--bg` e `--surface`) |
| `--line` | bordas, fios e grades |
| `--accent` | ação principal e destaque |
| `--accent-2` | segundo destaque (links, conexões, categoria secundária) |
| `--accent-ink` | texto sobre `--accent` (4,5:1) |
| `--paper` | superfície clara de objeto herói (papel, placa, ficha) |
| `--paper-ink` | texto sobre `--paper` (4,5:1) |
| `--danger`, `--ok`, `--warn` | erro, sucesso e atenção |
| `--font-display`, `--font-body`, `--font-mono` | famílias com fallback |
| `--weight-display` | peso dos títulos |
| `--tracking-display` | espaçamento de letra dos títulos |
| `--radius`, `--radius-lg` | raio pequeno (botão, campo) e grande (cartão, janela) |
| `--shadow` | sombra de elevação |
| `--glow` | brilho ou anel de destaque (pode ser um contorno) |

Variáveis a mais usam o prefixo do slug (`--orbital-gold-gradient`, `--metro-line-red`). Os modelos genéricos não dependem delas; o DESIGN.md do estilo explica quando usar.

## Como as outras skills consomem um estilo

```python
from pycode_tools import styles, vendor
estilo = styles.load_style("lousa")           # slug, fonts, mode, tokens_css, path
(dest / "css" / "tokens.css").write_text(estilo["tokens_css"])
css_fontes = vendor.copy_fonts(dest / "fonts", estilo["fonts"], url_prefix="../fonts/")
```

E no CSS do modelo:

```css
body { background: var(--bg); color: var(--text); font-family: var(--font-body); }
h1, h2 { font-family: var(--font-display); font-weight: var(--weight-display); letter-spacing: var(--tracking-display); }
.botao { background: var(--accent); color: var(--accent-ink); border-radius: var(--radius); }
```

Cuidados para quem escreve modelos:

- Nunca escreva uma cor fixa no modelo. Se precisar de transparência, use `color-mix(in srgb, var(--accent) 20%, transparent)`.
- Teste com um estilo claro e um escuro (por exemplo, `caderno` e `orbital`).
- Algumas fontes de exibição são estreitas ou largas demais para corpo de texto. O `--font-body` de cada estilo já é legível, mas `fliperama` usa VT323, que pede corpo cerca de 1,3 vez maior.
- `noir-champanhe` tem tracking largo (0.18em) e `sala-de-controle` usa Bebas Neue: títulos ficam melhores em caixa alta nesses dois estilos.

## Exportar

```bash
pycode styles tokens orbital --format css        # o próprio tokens.css
pycode styles tokens orbital --format json       # contrato e extras em JSON
pycode styles tokens orbital --format tailwind   # tema que aponta para as variáveis CSS
```
