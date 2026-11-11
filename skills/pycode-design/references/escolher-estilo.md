# Como escolher um estilo

Leia o pedido, identifique a superfície (convencer, ensinar, acompanhar, comparar) e o tom, e use a tabela como ponto de partida. Uma referência visual que a pessoa trouxe sempre vence a tabela: nesse caso, crie um estilo novo (veja `criar-estilo.md`).

| Pedido | Estilo | Por quê |
|---|---|---|
| Página de inscrição de um ciclo de aulas, mentoria ou evento | `orbital` | objetos de calendário, ingresso e acervo; tom premium e calmo |
| Convite elegante, programa com datas e entregas | `orbital` | o mesmo, com dourado contido |
| Carrossel de lista técnica ("3 jeitos de", "5 ferramentas") | `python-noturno` | cartas colecionáveis e numerais gigantes |
| Escada de níveis, diagnóstico "em qual nível você está" | `python-noturno` | medidor de níveis |
| Aula de Python com muito código | `python-noturno` ou `terminal` | o primeiro para slides de impacto, o segundo para live coding |
| Apostila, guia de estudo, material de apoio, documentação | `caderno` | blocos de documento, leitura longa |
| Painel de acompanhamento de estudos ou de tarefas | `caderno` | tabela-base, quadro e propriedades |
| Abertura de palestra, trailer de módulo, anúncio de aula ao vivo | `noir-champanhe` | cartelas, feixe e letreiro |
| Arquitetura de sistema, permissões, papéis, infraestrutura | `planta-azul` | salas, portas, crachás e cotas |
| Explicação conceitual com diagramas, comparação de ideias | `lousa` | diagramas que se desenham no ritmo da fala |
| Conteúdo para iniciantes, trilha gamificada, desafios | `fliperama` | missões, XP e inventário |
| Tutorial de testes, depuração, erro comum, live coding | `terminal` | tudo acontece nos espaços do editor |
| Ensaio, newsletter, estudo de caso, sumário de curso | `revista` | serifa, colunas, capitular e índice |
| Roadmap, trilha de estudo, ordem de etapas, onboarding | `metro` | estações, baldeações e "você está aqui" |
| Métricas, monitoramento, incidentes, checklist de operação | `sala-de-controle` | mostradores, LEDs e alerta |
| Bastidores, diário de projeto, erros e aprendizados, comunidade | `colagem` | recortes, fita e anotações à mão |

## Perguntas de desempate

1. **Claro ou escuro?** Leitura longa e material impresso pedem claro (`caderno`, `revista`, `metro`, `colagem`). Abertura, impacto e vídeo pedem escuro.
2. **O conteúdo tem sequência?** Sim: `metro` ou `lousa`. Não: os outros.
3. **O conteúdo tem código?** Muito: `terminal`. Pouco e de impacto: `python-noturno`.
4. **O tom é sério ou leve?** Sério: `sala-de-controle`, `planta-azul`, `revista`. Leve: `fliperama`, `colagem`.
5. **É para vender ou para ensinar?** Vender com calma: `orbital`. Anunciar com suspense: `noir-champanhe`. Ensinar: o resto.

## Combinações que funcionam

Um projeto pode usar dois estilos em formatos diferentes, desde que cada peça use um só. Exemplos:

- Aula em `lousa` e apostila em `caderno`.
- Página de inscrição em `orbital` e carrossel de divulgação em `noir-champanhe`.
- Deck de arquitetura em `planta-azul` e tutorial em `terminal`.

Não misture objetos de dois estilos na mesma tela.

## Comandos

```bash
pycode styles list                     # todos os estilos
pycode styles list --for carousel      # só os indicados para carrossel
pycode styles show metro               # DESIGN.md e caminhos
pycode styles preview --style metro --out /tmp/galeria   # prévia com fontes locais
```

Depois de escolher, passe o slug para a skill do formato: `pycode deck new --style lousa`, `pycode page new --style orbital`, `pycode carousel new --style python-noturno`.
