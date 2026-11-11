# Acessibilidade

O modelo já nasce acessível; esta lista é o que você não pode perder ao editar.

## Estrutura

- `<html lang="pt-BR">` (o QA reprova sem `lang`).
- **Um único `<h1>`** por página, e títulos em ordem (h2 para seções, h3 dentro delas). O QA confere o h1.
- Marcos semânticos: `header`, `nav` com `aria-label`, `main id="conteudo"`, `section` com `aria-labelledby`
  apontando para o título, `footer`.
- **Link de pular para o conteúdo** como primeiro elemento focável (`.skip-link`), visível ao receber foco.
- Listas são `ul`/`ol`/`dl`, não `div` com quebras.

## Objetos visuais

- Objeto que só ilustra o texto ao lado: `aria-hidden="true"` no objeto e uma `figcaption` ou texto próximo que
  diga o mesmo. O hero do modelo faz assim (`figure` + `figcaption`).
- Objeto que carrega informação própria (régua com tempos, barras com bytes): a informação também precisa estar
  em texto legível por leitor de tela (o modelo escreve "3 ms", "110 bytes" no HTML, não só na largura da barra).
- Imagens: `alt` que descreve o que a imagem mostra; `alt=""` só para decoração pura. O QA reprova `<img>` sem
  `alt` e sem `width`/`height`.

## Teclado e foco

- Tudo que é clicável é `a` ou `button` de verdade. Nada de `div` com `onclick`.
- Foco visível: `:focus-visible { outline: 2px solid var(--accent-2); outline-offset: 3px; }` está no crítico.
  Não remova `outline` sem pôr outra indicação equivalente.
- Menu no celular com `<details>/<summary>`: abre com Enter e Espaço, funciona sem JS.
- Perguntas frequentes com `<details>/<summary>` nativo. O ícone de mais/menos é feito com pseudo-elementos
  centralizados (`translate(-50%, -50%)`), não com o caractere `+`, que fica torto dependendo da fonte.
- Interações ilustrativas (o canhoto do ingresso) usam `button` com `aria-pressed`; sem JS, o botão fica
  desabilitado e o conteúdo continua legível.
- Âncoras: depois de rolar, o `main.js` põe o foco no alvo (`tabindex="-1"` quando preciso), para quem navega por
  teclado continuar dali.

## Contraste

- Texto normal: 4,5:1. Texto grande (24 px, ou 18,66 px em negrito): 3:1.
- O QA mede os pares de tokens do estilo (`--text`/`--bg`, `--muted`/`--surface`, `--paper-ink`/`--paper`,
  `--accent-ink`/`--accent` e outros). Para um par específico: `pycode contrast '#b9cbd6' '#0e283a'`.
- Texto sobre gradiente ou imagem: meça contra a cor mais clara (ou mais escura) que fica atrás do texto.
- Placeholder não substitui `label`. O formulário do modelo tem `label` visível.

## Movimento

- `prefers-reduced-motion: reduce` desliga animações e transições. O QA confere que nada roda com a preferência
  ligada.
- Nenhum conteúdo depende de animação para aparecer: os estados escondidos de entrada só valem com JS e sem
  movimento reduzido (`.js .motion-scene:not([data-entered]) ...` dentro de `@media (prefers-reduced-motion: no-preference)`).

## Formulários

- `label` associado (`for`/`id`), `type` certo (`email`, `tel`), `autocomplete` e `required` quando fizer sentido.
- Mensagem de erro em texto, perto do campo, não só cor.
- Botão de envio com texto que diz o que acontece ("Avisar quando abrir"), não "Enviar".

## Conferência

```bash
pycode page qa minha-pagina      # lang, h1, alt, dimensões, contraste dos tokens, sem JS, movimento reduzido
pycode page perf minha-pagina    # categoria de acessibilidade do Lighthouse (meta ≥ 95)
```

Navegue a página só com Tab, Enter e Espaço pelo menos uma vez antes de entregar.
