# Publicação

Publique sempre a pasta `dist/` gerada pelo `pycode page build`, nunca `src/`. Depois de publicar, confira a URL
pública por bytes ou hash: "deploy concluído" não prova que a hospedagem está servindo a versão nova.

## Antes de qualquer hospedagem

1. Ajuste `site_url` (e `base_path`, se o site ficar numa subpasta) em `pycode-page.json`, e as URLs absolutas no
   HTML (`canonical`, `og:url`, `og:image`).
2. `pycode page build` → `pycode page qa` → `pycode page check-links` → `pycode page perf`.
3. Confira `dist/` com `ls -la dist` (inclui `.htaccess`, `_headers`, `robots.txt`).

## GitHub Pages

1. Crie um repositório e envie o conteúdo de `dist/` para a branch publicada (ou configure uma Action que roda o
   build e publica `dist/`).
2. Em *Settings → Pages*, escolha a branch e a pasta.
3. Site de projeto fica em `https://usuario.github.io/repositorio/`: ponha `"base_path": "/repositorio/"` no
   `pycode-page.json` antes do build, senão a página 404 procura CSS e fontes na raiz do domínio.
4. GitHub Pages não lê `_headers` nem `.htaccess`; o cache fica no padrão da plataforma (curto). Os nomes com
   hash garantem que nenhuma versão velha de CSS ou JS seja servida.

## Netlify, Vercel e Cloudflare Pages

- **Netlify e Cloudflare Pages**: pasta de publicação `dist`. O arquivo `_headers` já vai junto e aplica
  `immutable` aos arquivos com hash e `must-revalidate` ao HTML. A página `404.html` na raiz é usada
  automaticamente.
- **Vercel**: pasta de saída `dist`. Cabeçalhos ficam num `vercel.json`:

```json
{
  "headers": [
    { "source": "/(css|js|fonts)/(.*)", "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }] },
    { "source": "/(.*).html", "headers": [{ "key": "Cache-Control", "value": "public, max-age=0, must-revalidate" }] }
  ]
}
```

Nessas plataformas a compressão (gzip ou Brotli) é automática.

## Hospedagem compartilhada por FTP ou SFTP (Apache)

1. Confirme que o servidor é Apache (o `.htaccess` não vale em Nginx; lá a configuração é do servidor).
2. Envie o conteúdo de `dist/` para a pasta pública (`public_html` ou equivalente) com um cliente SFTP ou
   `lftp -e "mirror -R dist /public_html; quit" sftp://usuario@host`. Prefira SFTP ou FTPS a FTP sem criptografia.
3. Envie primeiro os assets (CSS, JS, fontes, imagens) e por último os HTML: quem abrir a página no meio do envio
   não recebe um HTML apontando para um CSS que ainda não chegou.
4. Não apague o site inteiro para reenviar; envie por cima e remova depois só os arquivos com hash antigos.

O `.htaccess` do projeto:

```apache
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css text/plain application/javascript application/json image/svg+xml
</IfModule>
<IfModule mod_headers.c>
  <FilesMatch "\.(css|js|woff2)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
  <FilesMatch "\.html$">
    Header set Cache-Control "public, max-age=0, must-revalidate"
  </FilesMatch>
</IfModule>
ErrorDocument 404 /404.html
```

Brotli usa `BROTLI_COMPRESS` (não `BROTLI`). Não force o cabeçalho `Connection`. Use `immutable` só em arquivo
com hash no nome.

## Conferência da URL pública (obrigatória)

```bash
URL=https://seu-site.com
curl -s "$URL/" -o /tmp/publicado.html
diff <(sha256sum < dist/index.html) <(sha256sum < /tmp/publicado.html) && echo "HTML idêntico ao build"
CSS=$(grep -o 'css/styles\.[0-9a-f]*\.css' /tmp/publicado.html | head -1)
curl -s "$URL/$CSS" | sha256sum; sha256sum "dist/$CSS"
curl -sI -H 'Accept-Encoding: gzip' "$URL/$CSS" | grep -iE 'content-encoding|cache-control'
```

- Compare o HTML e pelo menos um CSS ou JS **pela URL exata que aparece no HTML** (com o hash). Uma CDN pode
  manter a URL antiga em cache com bytes velhos.
- Confira compressão e cache nos cabeçalhos.
- Rode o QA e o perf contra a URL publicada: `pycode page qa https://seu-site.com` e
  `pycode page perf https://seu-site.com --runs 3`. Métrica local não é métrica de produção.
- Se a hospedagem alterar o HTML (injeção de script, minificação própria), o hash não vai bater: descubra o que
  mudou antes de declarar a publicação concluída.
