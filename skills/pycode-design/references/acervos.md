# Estudar acervos externos sem copiar

`pycode refs` baixa galerias públicas de estudos de design para a sua máquina. Elas são ótimas para aprender composição, ritmo e movimento, mas a maioria não tem licença de uso: estudar pode, copiar e redistribuir não.

## Acervos do catálogo

| id | O que tem | Licença |
|---|---|---|
| `fable-5.2` | cerca de 80 estudos de interfaces com objetos físicos simulados | sem licença declarada |
| `opus-5.5` | 100 páginas de uma página só, de pôsteres a instrumentos | sem licença declarada |
| `fable-5.1` | 100 estudos de estilos conhecidos com os prompts originais | sem licença declarada |
| `awesome-design-md` | arquivos DESIGN.md que descrevem marcas conhecidas | MIT |

```bash
pycode refs list                 # catálogo e status local
pycode refs fetch fable-5.2      # baixa um (ou: pycode refs fetch all)
pycode refs search painel        # busca por nome, título e prompt
pycode refs open fable-5.2/002   # caminho do HTML e do prompt
pycode serve ~/.pycode-skills/references/fable-5.2   # abrir no navegador
```

Os prompts estão em inglês. Busque em inglês quando a busca em português não achar nada (`dashboard`, `editorial`, `terminal`, `map`).

## O que fazer com um estudo

1. **Abra e observe sem ler o código.** O que chama atenção primeiro? Qual é o objeto herói? Quantas cores? Como o texto se encaixa?
2. **Leia o prompt.** Ele explica a intenção: paleta, tipografia, "momento assinatura", interações. Muitas vezes o prompt ensina mais que o código.
3. **Anote princípios, não trechos.** Por exemplo: "o painel parece físico porque cada caractere vira uma plaqueta com dobra e sombra"; "a página tem uma única cena e tudo acontece dentro dela".
4. **Feche o arquivo e construa do zero** no seu estilo, com os seus tokens e objetos, para o seu conteúdo.

## Limites

- Não copie HTML, CSS, JS, SVG, textos ou imagens desses acervos para projetos, nem para este repositório.
- Não publique um "remake" fiel de um estudo. Inspiração de técnica (por exemplo, "plaquetas que viram como num painel de aeroporto") é livre; o código e a composição específica não.
- O `awesome-design-md` é MIT: os textos podem ser citados com a licença. Mesmo assim, as marcas descritas pertencem às empresas, e o estilo visual delas não deve ser usado para se passar por elas.
- Os acervos ficam em `~/.pycode-skills/references/`, com um arquivo `LEIA-ANTES.txt` em cada pasta registrando origem, commit e licença.

## Roteiro de estudo de 20 minutos

1. Escolha um tema do seu próximo trabalho (por exemplo, "linha do tempo").
2. `pycode refs search timeline` e abra três resultados.
3. Para cada um, escreva três observações: composição, objeto e movimento.
4. Escolha uma ideia de cada e diga como ela caberia em um dos estilos da biblioteca.
5. Construa a sua versão e compare as capturas com o que você anotou, não com o código original.
