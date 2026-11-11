# Processo: do briefing à entrega

Use esta referência para conduzir uma página do zero. Cada etapa tem uma saída concreta; não pule para a
seguinte sem ela.

## 1. Briefing (saída: um parágrafo e uma lista)

Antes de abrir o editor, responda por escrito:

- **O que é** a página e **para quem**. Uma frase cada.
- **A ação** que a pessoa deve tomar (inscrever-se, baixar, falar com alguém, ler até o fim).
- **O destino** dessa ação: formulário, link externo, âncora. Se ainda não existe, use um destino de exemplo e
  anote a pendência; o QA vai lembrar (aviso de "destino de exemplo").
- **Os assuntos** que a página precisa cobrir, em ordem de leitura. Cada assunto vira uma seção.
- **Material real disponível**: fotos, capturas, números com fonte, logotipo. O que não existir não é inventado.
- **Restrições**: estilo da marca, prazos, onde vai ser publicada (isso decide o arquivo de cabeçalhos).

Se a pessoa não souber algum item, proponha uma resposta e peça confirmação. Não preencha lacunas com
promessas, números ou depoimentos inventados.

## 2. Estrutura e objetos por seção (saída: tabela assunto → objeto)

Monte a tabela antes de escrever CSS. Ela é o que impede a página de virar uma pilha de cartões iguais.

| Seção | Assunto | Objeto visual | Movimento |
|---|---|---|---|
| Hero | o que é a oficina | viagem de uma requisição (navegador, vias, servidor) | pacotes descendo e subindo |
| Caminho | o que acontece em 38 ms | régua com fases proporcionais ao tempo | cursor varrendo a régua |
| Programa | quatro encontros | folha pautada com furos e lembrete colado | folha assenta, lembrete cai |
| Materiais | o que a pessoa leva | pasta com folhas em leque e abas | folhas abrem em leque |

Regras e exemplos de mapeamento estão em `composicao.md`.

## 3. Estilo (saída: slug escolhido)

`pycode styles list` mostra os estilos da skill `pycode-design`. Escolha pelo público e pelo tom, não pela cor
favorita. O `DESIGN.md` do estilo diz quais objetos e movimentos combinam com ele: leia antes de desenhar os
objetos. Para tokens próprios, use `pycode page new ... --tokens caminho/tokens.css` (precisa ter todas as
variáveis do contrato).

## 4. Construção (saída: `src/` completo)

```bash
pycode page new minha-pagina --title "Título da página" --style orbital   # ou --kind site
pycode serve minha-pagina/src                                           # prévia enquanto edita
```

- Troque o conteúdo do modelo pelo do briefing, seção por seção, mantendo a ideia de um objeto por assunto.
- Cor, fonte, raio e sombra só por `var(--token)` ou `color-mix()` sobre tokens. O build avisa sobre cores fixas.
- O que aparece na primeira dobra vai em `css/critical.css`; o resto em `css/styles.css`.
- Escreva o texto já revisado: `pycode text src/index.html` precisa sair limpo.

## 5. Build (saída: `dist/` e `build-manifest.json`)

```bash
pycode page build minha-pagina
```

Reprova se o CSS crítico passar de 15 KB, se dois builds seguidos não saírem idênticos, se sobrar marcador
`{{...}}`, se o HTML estiver desbalanceado ou se houver fonte, script ou CSS de CDN em runtime.

## 6. QA (saída: `qa/report.json` sem falhas e capturas revisadas)

```bash
pycode page qa minha-pagina
pycode page check-links minha-pagina
```

Depois de passar, abra as capturas de `qa/` e revise com a visão: cada seção em 1440 e 390, rolando até a
seção e confirmando `scrollY` antes de capturar (veja `armadilhas.md`). Itere até a página parecer trabalho
de estúdio, não de modelo.

## 7. Performance (saída: números medianos)

```bash
pycode page perf minha-pagina --runs 3
```

Rode sozinho na máquina (sem outros testes de navegador em paralelo). Informe as medianas de celular e
desktop: nota, FCP, LCP, TBT, CLS, Speed Index, bytes e requisições. Detalhes em `performance.md`.

## 8. Entrega (saída: URL pública conferida)

Publique `dist/` conforme `publicacao.md` e confira a URL pública por bytes ou hash. Relate o que foi
verificado e o que ficou pendente (por exemplo, o destino real do formulário).
