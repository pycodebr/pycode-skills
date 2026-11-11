# Escrita de slides, legenda e CTA

## Texto dos slides

- **Capa até ~20 palavras; slide de conteúdo até ~35.** O QA conta título, texto e CTA de cada slide (`rules.cover_words` e `rules.slide_words` no `slides.json`). Rótulos do conceito ("ESTAÇÃO 2", "FASE 1", "NÍVEL 3 DE 5") ficam fora da conta.
- **Uma ideia por slide**, em duas ou três frases conectadas. Frases completas, com artigos, preposições e conectores; nada de texto telegráfico nem de frases curtas em série para dar impacto.
- **Termo técnico explicado na mesma frase**, sem jargão solto: "o DNS funciona como a lista telefônica da internet: recebe o domínio e devolve o IP, o número do computador onde o site está".
- **Primeira pessoa coloquial** quando o post é a voz de quem publica ("eu abro", "pra", "a gente"), sem forçar gíria.
- **Concreto:** nome da ferramenta, comando, número, saída real. "Melhora a produtividade" não diz nada; "devolve os dois itens mais frequentes" diz.
- **Sem vícios de texto gerado:** travessão como pontuação, reticências de suspense, `Não é X. É Y.`, pergunta retórica em série, clichês (`destravar`, `jornada`, `game changer`, `revolucionário`, `incrível`, `simplesmente`), promessa de resultado ou de emprego. `pycode text slides.json` e o QA acusam boa parte disso.
- **Destaque** com `*palavra*` no `slides.json` (vira `<em class="hl">`, na cor de destaque). Use pouco: um ou dois por slide, no termo que a pessoa precisa guardar.

## Slide 2 como segunda capa

O Instagram costuma mostrar a segunda mídia de um carrossel para quem não arrastou. O slide 2 precisa se explicar sozinho:

- Não comece com conector ("E", "Mas", "Então", "Isso") nem termine uma frase iniciada na capa.
- Diga o assunto já na primeira frase, como em "Nível 1 dos testes de código: você roda o programa e clica em tudo" ou "Quiz de Python, fase 1 de 3: o que aparece na tela".

O QA avisa quando o slide 2 parece continuação.

## Um único CTA, no último slide

Qualquer pedido de ação conta como CTA: comentar, salvar, enviar para alguém, seguir, clicar no link, marcar uma pessoa. Dois pedidos no mesmo post dividem a resposta.

- O campo `cta` do `slides.json` existe só no último slide. O QA reprova se ele aparecer em outro slide ou faltar no último.
- O QA também procura pedidos escondidos no texto dos outros slides ("comenta", "salva este carrossel", "manda pra alguém", "link na bio", "segue o perfil").
- Capa e slides do meio podem fazer pergunta de gancho ("em qual destes níveis você está?") e pedir para a pessoa decidir antes de passar, sem pedir comentário, salvamento ou envio.
- O CTA liga o pedido ao conteúdo: "Salva o mapa pra consultar quando for estudar a sua primeira API" funciona melhor que "Salva este post".

## Legenda

`pycode carousel caption pasta` gera `legenda.md` com o esqueleto: o CTA do último slide, os nomes concretos do conteúdo (campos `keywords` e destaques) e os comandos mostrados. O texto final é escrito por você, no lugar dos marcadores `[[...]]`:

1. **Primeira linha:** o mesmo pedido de ação do último slide, dito de outro jeito. É o que aparece antes do "mais".
2. **Parágrafo do meio:** duas a quatro frases sobre o assunto, citando os nomes concretos (módulos, ferramentas, termos). A busca do Instagram lê a legenda.
3. **Comandos completos:** se algum comando quebrou linha no slide, repita aqui inteiro, numa linha.
4. **Última linha:** o pedido de ação de novo. Um pedido só: se o CTA é salvar, não acrescente "comenta aí".

Hashtags são opcionais; se usar, poucas e específicas do assunto. Rode `pycode text legenda.md` antes do `pack`, que recusa legenda com marcador ou com erro de texto.
