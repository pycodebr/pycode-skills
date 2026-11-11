# Exemplos

Quatro carrosséis completos, fictícios e neutros, feitos só com código (SVG, canvas, HTML e CSS) e conferidos pelo `pycode carousel qa`. Cada um é ponto de partida: copie, troque o texto no `slides.json` e os objetos no `js/scene.js`.

| Exemplo | Conceito | Slides | Vídeo | Estilo sugerido |
|---|---|---|---|---|
| `cartas` | cartas colecionáveis: cinco módulos da biblioteca padrão do Python, cada um com arte, uso e trecho com a saída real | 8 | capa: baralho abre em leque e as cartas viram | python-noturno |
| `metro` | mapa do metrô: a viagem de uma requisição em cinco estações, com a linha correndo de um slide para o outro | 8 | capa: o trem chega e as estações acendem | metro |
| `niveis` | escada de níveis: os cinco níveis de quem testa o próprio código, com numeral gigante e medidor | 7 | capa: os degraus acendem de baixo para cima | orbital |
| `fliperama` | quiz em pixel art: três pegadinhas de Python com o veredito no placar | 6 | capa: gabinete com PRESS START e moeda | fliperama |

```bash
pycode carousel new meu-post --example metro              # estilo sugerido pelo exemplo
pycode carousel new meu-post --example metro --style orbital
pycode carousel render meu-post && pycode carousel video meu-post --slide 1 && pycode carousel qa meu-post
```

O estilo sugerido é só o ponto de partida: os exemplos usam apenas os tokens do contrato, então funcionam com qualquer estilo do `pycode-design`. Cada exemplo traz uma `legenda.md` final escrita para ele; num post novo, gere o esqueleto com `pycode carousel caption --force` e escreva a sua.
