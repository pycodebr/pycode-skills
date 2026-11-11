# Responsivo e celular

A página precisa funcionar de verdade em 1440, 820, 390 e 320 px. "Funcionar" quer dizer: sem rolagem
horizontal, sem texto cortado e com os objetos reorganizados para a tela, não encolhidos como miniatura.

## Breakpoints do modelo

| Largura | O que muda |
|---|---|
| ≤ 1000 px | grades de duas colunas viram uma; título e objeto empilham |
| ≤ 860 px | o menu vira `<details>` (funciona sem JS); a linha do tempo deixa de ter rótulos acima e abaixo e vira lista com barras |
| ≤ 760 px | margens de 20 px; sem laços de animação, grade de fundo e sombras grandes; estante deita |
| ≤ 560 px | ingresso vira vertical (canhoto embaixo, perfuração horizontal); código quebra linha |
| ≤ 360 px | margens de 16 px; pequenos ajustes de espaçamento |

## Reorganizar, não encolher

- **Linha do tempo**: no desktop, rótulos alternam acima e abaixo da barra, alinhados à fase. No celular, cada
  fase vira uma linha com o tempo, o nome, a descrição e uma barra proporcional.
- **Estante**: no desktop, lombadas em pé com altura proporcional. No celular, os livros deitam e a largura passa
  a carregar a proporção.
- **Ingresso**: no desktop, canhoto à direita com 27% da largura. No celular, canhoto embaixo, com a perfuração
  e os recortes semicirculares mudando de lado.
- **Papel com furos**: perde a inclinação e reduz a margem, mas continua sendo uma folha.

## Armadilhas de layout

- **`1fr` não é zero**: `grid-template-columns: 1fr` é `minmax(auto, 1fr)`, e o mínimo é o conteúdo. Uma palavra
  longa ou um `white-space: nowrap` expande a coluna além da tela, e um `overflow: hidden` no caminho esconde o
  excesso sem gerar rolagem (o probe de overflow não pega). Use `minmax(0, 1fr)` em toda grade.
- **`nowrap` só em token curto** (preço, data, número). Frase precisa poder quebrar.
- **Título com palavra longa** em tamanho fixo estoura em 320 px. Use `clamp()` e `overflow-wrap: break-word`.
- **`min-width` maior que a tela** em algum componente quebra o 320 px. Teste o 320 sempre.
- **Código em `<pre>`** com rolagem interna engana o probe de overflow; no celular prefira `white-space: pre-wrap`.
- **Ordem do DOM = ordem de leitura no celular**. Não use `order` para inverter no celular; se precisar mudar a
  posição no desktop, mude só no breakpoint largo.
- **Texto mínimo de 12 px**, inclusive rótulos em fonte mono. O QA avisa quando há texto menor.
- **Área de toque de 44 px** para botões, links do menu e o `summary` das perguntas.

## Efeitos no celular

Laço contínuo, blur, sombra grande e fundo com gradiente repetido custam CPU de pintura. No celular eles saem
por padrão (`@media (max-width: 760px)`), e as entradas por objeto continuam. Se o briefing pedir um movimento
contínuo no celular, mantenha só esse, com `transform`, pausa fora da tela e respeito a movimento reduzido.

## Como conferir

```bash
pycode page qa minha-pagina            # matriz 1440/820/390/320: overflow, imagens, fontes, console, rede
pycode shot minha-pagina/dist --sizes 1440x900,820x1180,390x844,320x640 --out capturas --audit
```

Revise as capturas de cada seção em 390 e 320, não só o topo.
