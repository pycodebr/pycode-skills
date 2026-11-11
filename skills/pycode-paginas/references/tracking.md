# Tracking opcional sem perder atribuição

O modelo vem **sem nenhum tracking**. Acrescente só se a pessoa pedir e tiver as contas e o consentimento
necessários (avisos de cookies e LGPD são responsabilidade de quem publica). Esta referência descreve o padrão
com marcadores; nenhum ID real aparece aqui.

## Um único dono do PageView

Escolha **um** carregador: o gerenciador de tags (que então dispara analytics e pixels de anúncio lá dentro) ou
os scripts diretos de cada ferramenta. Nunca os dois para a mesma ferramenta. Pixel direto mais o mesmo pixel
dentro do gerenciador conta cada visita duas vezes e estraga a atribuição sem dar erro nenhum.

## Carregar sem bloquear a primeira pintura e sem atrasar demais

Duas versões aceitáveis, conforme a prioridade:

**A. Página de conteúdo, onde a nota de performance importa mais**: agende depois do `load`, quando o navegador
estiver livre, com limite de espera. O container carrega sozinho em toda visita, sem depender de clique.

```html
<script>
  (function (w, d, layer, src) {
    w[layer] = w[layer] || [];
    var started = false;
    function load() {
      if (started) return;
      started = true;
      w[layer].push({ 'gtm.start': Date.now(), event: 'gtm.js' });
      var s = d.createElement('script');
      s.async = true;
      s.src = src;
      d.head.appendChild(s);
    }
    function schedule() {
      if ('requestIdleCallback' in w) w.requestIdleCallback(load, { timeout: 2500 });
      else w.setTimeout(load, 0);
    }
    if (d.readyState === 'complete') schedule();
    else w.addEventListener('load', schedule, { once: true });
  })(window, document, 'dataLayer', 'https://{{HOST_DO_GERENCIADOR}}/gtm.js?id={{ID_DO_CONTAINER}}');
</script>
```

**B. Página de anúncio, onde cada visita precisa ser contada cedo**: script `async` no começo do `<head>`, antes de
qualquer folha de estilo externa (uma folha pendente faz o script inline esperar). Custa alguns pontos de nota e
antecipa o PageView em segundos. Meça os dois e decida com quem paga a mídia.

O que **não** fazer: carregar só na primeira interação ou depois de 10 a 15 segundos. A nota sobe e o PageView de
quem sai rápido some; para anúncio, isso é perda de dado, não otimização.

Depois de acrescentar tracking, rode o build com o host permitido (o build reprova script externo por padrão):

```bash
pycode page build minha-pagina --allow-host {{HOST_DO_GERENCIADOR}}
```

## Conexões antecipadas

`<link rel="preconnect" href="https://{{HOST_DO_GERENCIADOR}}">` ajuda. Use `crossorigin` só para fontes e
`fetch` anônimo: em script comum ele abre uma conexão que a requisição do script não reaproveita.

## Preservar parâmetros até o destino

Veja `formularios-e-links.md`: `URL` + `URLSearchParams`, apagar cada chave recebida uma vez e `append` de cada
valor, partindo do `href` atual para não perder campos que o gerenciador acrescentou.

## Como medir sem poluir os dados

- Em testes automatizados, bloqueie só as **coletas** (requisições que registram o evento), não o carregador:
  bloquear o carregador gera erro de console e reprova o QA por um artefato do próprio teste. Uma forma é
  responder o carregador com um JS vazio e abortar as coletas.
- Muitos pixels recusam eventos vindos de `127.0.0.1`. Para conferir localmente, verifique a rede (o script
  carregou, a fila de eventos recebeu o PageView) e não a contagem no painel da ferramenta.
- Em produção, confira com uma visita real: o painel da ferramenta mostra o evento chegando? Há um único
  PageView por visita?
- No Lighthouse, meça duas vezes: a página completa (o custo real dos terceiros) e só o que é seu:

```bash
pycode page perf https://seu-site.com --runs 3
pycode page perf https://seu-site.com --runs 3 --block '*{{HOST_DO_GERENCIADOR}}*' --block '*{{HOST_DO_PIXEL}}*'
```

O `perf` confere se o bloqueio funcionou (status -1 e zero bytes em cada requisição bloqueada). Nunca apresente
a nota isolada como a nota da página publicada; ela serve para separar regressão sua do custo dos terceiros.

## Antes de publicar

- Um só carregador, sem pixel duplicado.
- PageView automático em toda visita (sem depender de clique).
- Parâmetros chegando ao destino final, com valores repetidos preservados.
- Aviso de privacidade e consentimento conforme a lei que se aplica ao seu público.
