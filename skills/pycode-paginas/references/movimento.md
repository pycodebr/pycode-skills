# Movimento por componente

Movimento tem função: mostrar um fluxo (o pacote indo e voltando), um tempo passando (o cursor na régua) ou a
chegada de um objeto quando ele entra na tela. Animação que não explica nada é ruído, e ruído custa bateria.

## Regras

1. **Só `transform` e `opacity`** (e `stroke-dashoffset` em SVG pequeno). Essas propriedades não recalculam
   layout; `top`, `left`, `width`, `height`, `margin`, `box-shadow` e `filter` animados recalculam e pesam.
2. **Pausado até estar visível.** Cada componente com movimento é um `.motion-scene`. O `main.js` usa um
   `IntersectionObserver` e marca `data-motion="on"` quando a cena está visível, a aba está ativa e o sistema não
   pede movimento reduzido; senão, `data-motion="off"`.
3. **Pausa com a aba oculta**: `visibilitychange` desliga tudo e `body[data-hidden="true"]` pausa até os
   pseudo-elementos (regras de descendentes não alcançam `::before`/`::after` sozinhas).
4. **Movimento reduzido** desliga animações e transições por completo.
5. **Sem JS, nada se move e nada some.** As animações só existem quando a cena tem o atributo `data-motion`, que
   só o JS coloca. Os estados de entrada escondidos dependem da classe `.js` no `<html>`.
6. **Celular sem laços contínuos** (as entradas continuam). Veja `responsivo.md`.

## Como o modelo implementa

```css
/* A animação existe, mas parada (especificidade zero com :where, para a regra de "on" vencer). */
:where(.motion-scene[data-motion]) .lane-out .runner { animation: trip-down 6.4s ease-in-out infinite paused; }
/* Visível, aba ativa, sem movimento reduzido: roda. */
.motion-scene[data-motion="on"] .loop { animation-play-state: running; }
body[data-hidden="true"] .loop { animation-play-state: paused !important; }
@media (max-width: 760px) { .loop, .loop::before { animation: none !important; } }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }
```

Armadilha real: sem o `:where()`, a regra que declara a animação (`.motion-scene[data-motion] .lane-out .runner`)
tem especificidade maior que a regra que liga (`.motion-scene[data-motion="on"] .loop`) e a animação fica parada
para sempre, sem erro nenhum. Só o teste de dois quadros pega isso.

### Truque do "corredor" para mover algo por uma distância relativa

Para um pacote percorrer exatamente o comprimento de uma via, sem medir em JS: o pacote fica no centro de um
elemento `.runner` do tamanho da via, e o `.runner` anima `transform: translateY(-50%)` até `translateY(50%)`.
Porcentagem em `translate` é relativa ao próprio elemento, então o percurso acompanha o tamanho da via em
qualquer tela.

### Entradas por objeto

Uma entrada por componente, não o mesmo "fade para cima" em todas as seções: a folha assenta girando, o lembrete
cai, as barras crescem a partir da esquerda (`scaleX`), as folhas da pasta abrem em leque, o ingresso desliza.
Escalone com `transition-delay` curto (0,1 s entre peças).

## Botão da chamada final

Reflexo diagonal breve atravessando o botão, contorno que acende e apaga e a seta avançando 3 px, num ciclo de
6,4 s com repouso. Pseudo-elementos com `pointer-events: none`; hover e foco pausam o efeito; movimento reduzido
deixa só o contorno estático. Não use escala pulsante, tremor ou sombra animada.

## Como provar que funciona

O `pycode page qa` faz o que uma captura estática não faz:

- **dois quadros**: rola até cada cena, lê `transform`/`opacity` das animações em dois instantes (450 ms) e exige
  que mudem no desktop;
- **pausa fora da tela**: rola para longe e confere que as animações contínuas daquela cena pararam (conteúdo
  pulado por `content-visibility: auto` não conta, porque nem é renderizado);
- **aba oculta**: simula `document.hidden` e confere que nada contínuo roda;
- **movimento reduzido**: percorre a página inteira e exige zero animações rodando.

Ao testar entradas escalonadas por quadros, escolha uma peça sem atraso ou espere o atraso: dois quadros dentro
do mesmo `transition-delay` parecem "sem movimento".

## Bibliotecas

CSS resolve quase tudo. Se precisar de GSAP (linha do tempo complexa, SVG morph), copie pelo vendor
(`vendor.copy_js`), nunca de CDN, e mantenha as mesmas regras de pausa e movimento reduzido.
