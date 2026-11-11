# Criar um estilo novo a partir de uma referência

Quando a pessoa traz uma referência (um site, um print, a identidade da marca dela), crie um estilo próprio em vez de forçar um dos prontos. O resultado é uma pasta com `style.json`, `tokens.css`, `DESIGN.md` e `preview.html`, que as outras skills passam a aceitar em `--style`.

## 1. Capture a referência

```bash
pycode shot https://exemplo.com --sizes 1440x900,390x844 --full --out ref-capturas --name referencia
```

Abra as capturas e descreva em poucas linhas: superfície (escuro ou claro), cor dominante, cor de ação, tipo de letra dos títulos (serifa, grotesca, mono, manuscrita), raio dos cantos, profundidade (sombra, borda, nenhuma) e os objetos ou metáforas recorrentes.

Se a referência for um print, trabalhe a partir dele. Se for um site, leia o CSS de verdade: os valores exatos estão lá.

## 2. Extraia os tokens do CSS real

No navegador (ou com Playwright), leia as variáveis e as cores computadas dos elementos principais:

```js
// no console da página de referência
const pick = (sel, props) => { const el = document.querySelector(sel); if (!el) return null;
  const cs = getComputedStyle(el); return Object.fromEntries(props.map(p => [p, cs[p]])); };
({ body: pick('body', ['backgroundColor', 'color', 'fontFamily']),
   h1: pick('h1', ['fontFamily', 'fontWeight', 'letterSpacing', 'fontSize']),
   botao: pick('a[class*=btn], button', ['backgroundColor', 'color', 'borderRadius']) });
```

Converta para o contrato:

| Do site | Para o token |
|---|---|
| fundo do body | `--bg` |
| fundo de seções alternadas | `--bg-2` |
| fundo de cartões e painéis | `--surface`, `--surface-2` |
| cor do texto e do texto secundário | `--text`, `--muted` |
| bordas | `--line` |
| cor do botão principal | `--accent` (e o texto do botão em `--accent-ink`) |
| segunda cor de destaque | `--accent-2` |
| superfície clara de destaque | `--paper`, `--paper-ink` |
| família, peso e tracking do h1 | `--font-display`, `--weight-display`, `--tracking-display` |
| família do texto e do código | `--font-body`, `--font-mono` |
| raio de botão e de cartão | `--radius`, `--radius-lg` |
| sombra e brilho | `--shadow`, `--glow` |

As fontes precisam existir no `vendor` (`pycode vendor --list`). Se a referência usa uma fonte comercial, escolha a mais próxima entre as OFL disponíveis e registre a troca no DESIGN.md. Se precisar de outra fonte OFL, ela entra por um `vendor.json` com URL fixa e hash.

## 3. Crie a pasta a partir do estilo mais parecido

```bash
pycode styles new estudio-coral --from revista
```

O comando copia o estilo de partida para `~/.pycode-skills/styles-user/estudio-coral/`, troca o prefixo das variáveis extras (`--revista-` vira `--estudio-coral-`) e marca a versão 0.1.0. Use `--dir` para criar em outra pasta (por exemplo, dentro do projeto) e defina `PYCODE_STYLES_USER` com essa pasta para os comandos enxergarem o estilo.

## 4. Edite os tokens e confira o contraste

Edite `tokens.css` mantendo todas as variáveis do contrato. Variáveis a mais usam o prefixo do slug. Confira os pares principais:

```bash
pycode contrast '#f4efe6' '#1a1714'
```

## 5. Documente os objetos

Reescreva o `DESIGN.md` com as seções obrigatórias: cores (o papel de cada uma), tipografia, superfícies e texturas, objetos do estilo (cinco a oito, com como construir cada um), movimento, aplicação em deck, página e carrossel, o que evitar e checklist. Mantenha o frontmatter com as cores iguais às do `tokens.css`; o check compara os dois.

O que separa um estilo de uma paleta são os objetos. Pergunte: que coisas aparecem sempre nessa referência? Uma marca de café pode ter selo de torra, etiqueta de saco e cardápio de giz; uma consultoria pode ter relatório com fios, gráfico de barras desenhado e carimbo de data.

## 6. Monte a prévia e valide

Edite o `preview.html` para mostrar paleta, tipografia, de quatro a seis objetos funcionando (marcados com `data-object`), um trecho de página (`data-format="page"`), um slide 16:9 (`data-format="deck"`) e um slide 4:5 (`data-format="carousel"`). Depois:

```bash
pycode styles check estudio-coral
pycode styles preview --style estudio-coral --out /tmp/prev
```

O check reprova se faltar token, se o contraste não passar, se uma fonte não existir, se o DESIGN.md divergir dos tokens, se a prévia tiver rolagem horizontal ou erro de console em 1440 ou 390 px, ou se algum loop continuar rodando com movimento reduzido. Abra as capturas e revise por visão antes de dizer que terminou.
