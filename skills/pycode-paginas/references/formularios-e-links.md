# Formulários e links de destino

## Uma ação principal, vários caminhos até ela

Numa página longa, vários botões levam à mesma ação. Separe dois papéis:

- **Chamadas internas** (header, hero, meio da página): âncoras para o bloco da ação (`href="#inscricao"`). Elas
  levam a pessoa até o lugar onde a decisão acontece.
- **Destino final** (o formulário ou o link externo dentro desse bloco): o único elemento que sai da página ou
  envia dados.

Por quê: a pessoa vê o contexto (o que recebe, quando acontece) antes de agir, e só um elemento precisa
carregar parâmetros e ser medido.

## Âncoras que param no lugar certo

- O alvo é o próprio bloco da ação, não a seção que o contém, se a seção tiver cabeçalho longo.
- Com header fixo, o alvo precisa ficar logo abaixo dele. O modelo mede a altura real do header (`--header-h`) e
  rola por posição calculada; o QA mede `getBoundingClientRect().top` do alvo depois do clique e do fragmento
  direto (`pagina.html#inscricao`), em navegação nova.
- Não some `scroll-margin-top` no alvo e `scroll-padding-top` no `html` sem medir: os dois se acumulam.
- Link para o header fixo (`#topo`) precisa levar ao início da página; o `main.js` trata esse caso.

## Formulário

```html
<form class="signup" action="https://seu-servico.com/inscricao" method="post" data-keep-params>
  <label for="email">Seu e-mail</label>
  <input id="email" name="email" type="email" autocomplete="email" required>
  <button class="button button-cta" type="submit">Avisar quando abrir</button>
</form>
```

- `action` é o endereço do serviço que recebe os dados (seu backend, uma função serverless, um serviço de
  formulários). O modelo vem com um destino de exemplo; o QA e o `check-links` avisam até você trocar.
- Validação nativa (`type="email"`, `required`) funciona sem JS. Se o serviço devolver uma página de
  confirmação, ótimo; se responder JSON, intercepte o envio em JS e mostre a confirmação em texto na página.
- Peça só o que vai usar. Cada campo a mais derruba a taxa de envio.
- Teste o envio real uma vez, num ambiente de teste do serviço, e confira que o dado chegou. Ao automatizar
  testes de formulário, nunca deixe uma requisição retida ir para o endpoint real sem querer: aborte-a
  explicitamente no teste.

## Parâmetros da URL (`utm_*`, `ref`, `gclid` e outros)

Quem chega por um link de campanha traz parâmetros na URL. Se o destino final não recebe esses parâmetros, a
atribuição se perde. O `main.js` repassa para elementos marcados com `data-keep-params`:

- **Links**: reconstrói a URL do destino a partir do `href` atual com `URL` e `URLSearchParams`. Para cada chave
  recebida, apaga uma vez e faz `append` de cada valor. Assim valores repetidos (`?tag=a&tag=b`) sobrevivem; usar
  `set` dentro do laço perderia o primeiro.
- **Formulários**: acrescenta campos `hidden` com os parâmetros recebidos (sem sobrescrever campos visíveis).

```js
const incoming = new URLSearchParams(location.search);
const url = new URL(link.href);
new Set(incoming.keys()).forEach(key => url.searchParams.delete(key));
incoming.forEach((value, key) => url.searchParams.append(key, value));
if (link.href !== url.href) link.href = url.href;
```

Regras:

- Marque só o destino final com `data-keep-params`; âncoras internas não precisam.
- Leia o `href` atual (não uma URL fixa guardada antes): outra camada (um gerenciador de tags) pode ter
  acrescentado campos depois do carregamento.
- Se outra camada reescreve o link depois, reaplique no `load`, num `MutationObserver` do atributo `href` e no
  início do clique (`capture: true`), comparando antes de atribuir para não entrar em laço.
- Teste com `?tag=a&tag=b&texto=a%2Bb`: no destino, `getAll('tag')` precisa ser `['a', 'b']` e `texto` precisa
  voltar como `a+b`. Não use dado pessoal real nos testes.

## Links externos

- `target="_blank"` sempre com `rel="noopener"` (o QA reprova sem). Prefira abrir na mesma aba, a menos que a
  pessoa esteja no meio de uma tarefa na página.
- `pycode page check-links` testa cada link externo por HTTP e avisa sobre redirecionamento para outro domínio.
- Depois de trocar um destino, confira o conteúdo da resposta, não só o status 200: abra a página e procure o
  nome esperado. Status 200 não prova que é o destino certo.
