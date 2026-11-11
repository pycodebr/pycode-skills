---
version: 1.0.0
name: Sala de controle
slug: sala-de-controle
description: 'Painel de instrumentos à noite: grafite fosco, mostradores com ponteiro, barras de LED, chaves seletoras, osciloscópio e luz de alerta âmbar. Para métricas, monitoramento, checklists e conteúdo
  sobre operação e segurança.'
mode: dark
fonts:
- bebas-neue
- geist
- jetbrains-mono
- jersey-10
best_for:
- deck
- page
- carousel
colors:
  bg: '#0e100f'
  bg-2: '#141715'
  surface: '#1b1f1c'
  surface-2: '#242a26'
  text: '#e9efe9'
  muted: '#a9b4ab'
  line: '#38413b'
  accent: '#ffb000'
  accent-2: '#6cff9c'
  accent-ink: '#1f1500'
  paper: '#e4e0d4'
  paper-ink: '#141715'
  danger: '#ff4d3d'
  ok: '#6cff9c'
  warn: '#ffb000'
  amber: '#ffb000'
  phosphor: '#6cff9c'
  bezel: '#2c332e'
  screw: '#56605a'
typography:
  display:
    fontFamily: Bebas Neue
    fontWeight: 400
    letterSpacing: 0.04em
  body:
    fontFamily: Geist
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: JetBrains Mono
    fontWeight: 400
rounded:
  base: 6px
  large: 14px
elevation:
  shadow: inset 0 1px 0 rgba(255, 255, 255, .06), 0 14px 30px rgba(0, 0, 0, .55)
  glow: 0 0 12px rgba(255, 176, 0, .55)
tokens: tokens.css
---

# Sala de controle

## Visão geral

Sala de controle é um painel de instrumentos à noite: grafite fosco, chapas com parafusos, mostradores com ponteiro, barras de LED, chaves seletoras, osciloscópio, visores numéricos e uma luz de alerta âmbar. Cada objeto responde a uma pergunta de operação: quanto, quão rápido, está normal, o que fazer agora.

Use para monitoramento, métricas técnicas, checklists de operação, segurança, incidentes, explicações de infraestrutura e carrosséis de "o que olhar primeiro". Evite para conteúdo leve ou introdutório e para páginas institucionais.

## Cores

- `--bg` (#0e100f) é a sala escura; `--bg-2` o fundo das telas e células dos instrumentos.
- `--surface` e `--surface-2` são a chapa e a moldura.
- `--text` é o rótulo serigrafado; `--muted` para escalas e unidades; `--line` para divisões.
- `--accent` (#ffb000, âmbar) é leitura e atenção. `--accent-2` e `--ok` (#6cff9c, verde fósforo) são estado normal. `--danger` (#ff4d3d) é falha.
- `--paper` é a plaqueta clara de checklist.
- Extras: `--sala-de-controle-amber`, `-phosphor`, `-bezel`, `-screw` e `--sala-de-controle-font-readout` (Jersey 10).

A sala é quase sem cor para que as luzes signifiquem algo. Uma cor nunca aparece só como enfeite.

## Tipografia

Bebas Neue em caixa alta para títulos e rótulos grandes, como letra serigrafada na chapa. Geist no texto. JetBrains Mono pequena e espaçada (11 px, `letter-spacing: .14em`, caixa alta) para rótulos técnicos. Jersey 10 para leituras numéricas.

| Nível | Tamanho | Fonte |
|---|---|---|
| h1 | `clamp(56px, 7.4vw, 112px)`, linha .88 | Bebas Neue |
| h2 | `clamp(40px, 5vw, 72px)` | Bebas Neue |
| leitura | 34 a 84 px | Jersey 10 |
| rótulo | 11 px | JetBrains Mono |
| corpo | 17 px | Geist |

## Superfícies e texturas

- **Chapa:** degradê vertical curto (#202521 para #181c19), raio de 20 px, sombra e contorno interno de 1 px. Quatro parafusos nos cantos, feitos com `radial-gradient` num `::before`.
- **Células:** fundo `--bg-2` afundado (`inset` de 1 px mais sombra interna).
- **Tela de fósforo:** fundo #07120b, grade verde a 9% e brilho interno.

## Objetos do estilo

1. **Mostrador analógico.** SVG com arco dividido em três faixas (verde, âmbar e vermelho), marcas de escala, números mono e um ponteiro num `<g>` com `transform-origin` no pivô, oscilando entre valores plausíveis em 5 s. Leitura numérica embaixo em Jersey 10.
2. **Barras de LED.** Colunas de segmentos de 22 × 9 px empilhados de baixo para cima (`flex-direction: column-reverse`). Cada segmento tem um `::after` com a cor e `opacity` controlada por variáveis (`--on`, `--on2`, `--on3`) em `steps(1)`. Verde embaixo, âmbar no meio, vermelho no topo.
3. **Luz de alerta.** Círculo com degradê radial âmbar, anel de moldura e um halo (`::after`) que pisca em degraus. Só acende para algo que pede ação agora.
4. **Chave seletora.** `button` real com `aria-pressed`; o pino é um `::after` que desliza 30 px. Sem JavaScript fica desabilitado mostrando o estado.
5. **Osciloscópio.** Tela de fósforo com um `path` verde duplicado em largura de 200% que corre com `translateX(-50%)` em 3 s.
6. **Visor numérico.** Jersey 10 em verde fósforo com dois-pontos piscando a cada segundo.
7. **Checklist de operação.** Plaqueta clara com itens e uma luz por item que passa a verde em sequência.

## Movimento

- Imita instrumento: ponteiro oscila com easing suave, LEDs e alertas em degraus, traço corre linear.
- Durações: ponteiro 5 s, LEDs 2,2 s, alerta 1,4 s, osciloscópio 3 s, dois-pontos 1 s.
- Movimento reduzido: ponteiro parado no valor, alerta aceso fixo, traço parado.

## Aplicação em deck, página e carrossel

- **Deck:** chapa ocupando o slide, título em Bebas à esquerda e um instrumento à direita com a leitura grande.
- **Página:** hero como painel (texto e cluster de instrumentos), indicadores em células afundadas, checklist em plaqueta clara.
- **Carrossel:** capa com a luz de alerta grande e a frase "quando a luz acende"; slides internos com um instrumento por vez e o passo a seguir.

## O que evitar

- Números inventados apresentados como dados reais. Use valores de exemplo marcados como exemplo ou dados reais do seu sistema.
- Vermelho piscando sem motivo.
- Painéis lotados de instrumentos decorativos.
- Fundo preto puro sem chapa nem moldura.
- Fonte de leitura em textos corridos.

## Checklist

- [ ] Cada instrumento responde a uma pergunta clara.
- [ ] Verde, âmbar e vermelho com significado fixo.
- [ ] Chaves são botões reais com `aria-pressed`.
- [ ] Luzes e traços pausam fora da tela.
- [ ] Leituras legíveis em 390 px.
- [ ] `pycode styles check sala-de-controle` passa.
