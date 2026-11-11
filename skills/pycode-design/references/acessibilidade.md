# Acessibilidade

Design bonito que ninguém consegue ler, navegar ou usar no teclado não está pronto. Confira estes pontos em todo artefato.

## Contraste

- Texto normal: 4,5:1 sobre o fundo real (inclusive sobre cartões, papéis e janelas).
- Texto grande (a partir de 24 px, ou 19 px em negrito) e ícones funcionais: 3:1.
- Bordas de campos e botões sem preenchimento: 3:1.
- `pycode contrast <texto> <fundo>` confere um par. `pycode styles check` confere os pares do contrato de cada estilo.
- Texto sobre imagem ou textura precisa de uma área limpa ou de uma película. Textura de código fica abaixo de 8% de opacidade.

## Tamanho e leitura

- Corpo a partir de 16 px na página (22 px quando a fonte for miúda, como a VT323).
- Linha de leitura entre 55 e 75 caracteres.
- Em slides 1920 × 1080, texto a partir de 24 px.
- Fontes de exibição (Caveat, Syncopate, Press Start 2P, Anton) só em títulos e rótulos curtos.

## Teclado e foco

- Tudo que é clicável é `a` ou `button`. Nada de `div` com `onclick`.
- Foco visível em todos os elementos: `:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }`.
- Objetos interativos (canhoto do ingresso, chave seletora) são botões com `aria-pressed` e funcionam com Enter e Espaço.
- Áreas de toque com pelo menos 44 × 44 px no celular.
- Listas que abrem com `details` e `summary` nativos.

## Leitores de tela

- `lang="pt-BR"` no `html`.
- Objetos decorativos (texturas, grão, estrelas, setas de enfeite) com `aria-hidden="true"`.
- SVG com significado leva `role="img"` e `aria-label` com a informação, não com a aparência ("Planta com quatro salas; acesso ao banco trancado").
- Letras recortadas e textos divididos em `span` levam `aria-label` com a palavra inteira no elemento pai.
- Estado atual marcado com `aria-current` (estação atual, slide atual, item ativo do menu).

## Movimento

- Respeite `prefers-reduced-motion`: sem animações e com tudo no estado final.
- Nada pisca mais de três vezes por segundo.
- Loops pausam fora da tela e com a aba oculta.
- Conteúdo essencial nunca depende de animação para aparecer: sem JavaScript, tudo fica visível.

## Celular

- Sem rolagem horizontal em 320, 390, 820 e 1440 px. Teste com `pycode shot --sizes 320x700,390x844,820x1180,1440x900 --audit`.
- Objetos se reorganizam (coluna, diagrama vertical) em vez de encolher até virar miniatura.
- Peças sobrepostas (colagem, leque de cartas) não cobrem texto em nenhuma largura.
