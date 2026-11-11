"""pycode carousel preview: gera preview.html, que simula o carrossel no feed do celular (arrastar, contador,
vídeo com som ao tocar) e mostra todos os slides lado a lado para aprovação."""
import argparse
import html
import re
import sys

import carousel_lib as L
from pycode_tools import paths

PAGE = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prévia · __TITLE__</title>
<style>
  :root { --ink: #111317; --soft: #5b616b; --line: #dbdee3; --bg: #eef0f3; --card: #ffffff; --blue: #1662d6; }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--ink); font: 15px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif; }
  main { max-width: 1180px; margin: 0 auto; padding: 24px 16px 64px; display: grid; gap: 40px; }
  h1 { font-size: 20px; margin: 0 0 4px; }
  .lead { margin: 0; color: var(--soft); }
  .phone { width: min(100%, 420px); margin: 0 auto; background: var(--card); border-radius: 28px;
    box-shadow: 0 20px 60px rgba(17, 19, 23, .14); overflow: hidden; border: 1px solid var(--line); }
  .bar { display: flex; align-items: center; gap: 10px; padding: 12px 14px; }
  .avatar { width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center; font-weight: 700;
    font-size: 13px; color: #fff; background: linear-gradient(135deg, #f58529, #dd2a7b 50%, #515bd4); }
  .who { flex: 1; font-weight: 600; }
  .who small { display: block; font-weight: 400; color: var(--soft); font-size: 12px; }
  .media { position: relative; aspect-ratio: 4 / 5; background: #000; }
  .track { display: flex; height: 100%; overflow-x: auto; scroll-snap-type: x mandatory; scroll-behavior: smooth;
    scrollbar-width: none; cursor: grab; touch-action: pan-x; }
  .track::-webkit-scrollbar { display: none; }
  .track.drag { cursor: grabbing; scroll-snap-type: none; scroll-behavior: auto; }
  .item { flex: 0 0 100%; height: 100%; scroll-snap-align: center; position: relative; }
  .item img, .item video { width: 100%; height: 100%; object-fit: cover; display: block; user-select: none; -webkit-user-drag: none; }
  .count { position: absolute; top: 12px; right: 12px; padding: 3px 9px; border-radius: 99px; background: rgba(17,19,23,.72);
    color: #fff; font-size: 12px; font-weight: 600; }
  .nav { position: absolute; top: 50%; translate: 0 -50%; width: 30px; height: 30px; border-radius: 50%; border: 0;
    background: rgba(255,255,255,.9); color: var(--ink); font-size: 18px; line-height: 30px; cursor: pointer; display: none; }
  .nav.prev { left: 10px; } .nav.next { right: 10px; }
  @media (hover: hover) { .nav { display: block; } }
  .sound { position: absolute; left: 12px; bottom: 12px; border: 0; border-radius: 99px; padding: 5px 10px;
    background: rgba(17,19,23,.72); color: #fff; font-size: 12px; cursor: pointer; }
  .actions { display: flex; align-items: center; gap: 14px; padding: 10px 14px 4px; }
  .actions svg { width: 24px; height: 24px; fill: none; stroke: var(--ink); stroke-width: 1.8; }
  .dots { flex: 1; display: flex; justify-content: center; gap: 4px; margin-right: 38px; }
  .dots i { width: 6px; height: 6px; border-radius: 50%; background: var(--line); }
  .dots i.on { background: var(--blue); }
  .caption { padding: 4px 14px 16px; white-space: pre-line; }
  .caption b { font-weight: 600; }
  .caption .more { color: var(--soft); }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }
  .grid figure { margin: 0; background: var(--card); border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
  .grid img { width: 100%; aspect-ratio: 4 / 5; object-fit: cover; display: block; }
  .grid figcaption { padding: 8px 10px; font-size: 13px; color: var(--soft); }
  .grid figcaption b { color: var(--ink); }
  .note { font-size: 13px; color: var(--soft); text-align: center; margin: 10px 0 0; }
  @media (prefers-reduced-motion: reduce) { .track { scroll-behavior: auto; } }
</style>
</head>
<body>
<main>
  <section aria-labelledby="t">
    <h1 id="t">__TITLE__</h1>
    <p class="lead">Prévia para aprovação: arraste para o lado como no app. Os vídeos tocam sem som; toque em "som" para ouvir.</p>
  </section>
  <section class="phone" aria-label="Simulação do post no feed">
    <div class="bar"><div class="avatar" aria-hidden="true">__INITIALS__</div>
      <div class="who">__HANDLE__<small>__NAME__</small></div></div>
    <div class="media">
      <div class="track" id="track" tabindex="0" aria-label="Slides do carrossel">__ITEMS__</div>
      <span class="count" id="count">1/__TOTAL__</span>
      <button class="nav prev" id="prev" aria-label="Slide anterior">‹</button>
      <button class="nav next" id="next" aria-label="Próximo slide">›</button>
      <button class="sound" id="sound" hidden>som</button>
    </div>
    <div class="actions" aria-hidden="true">
      <svg viewBox="0 0 24 24"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>
      <svg viewBox="0 0 24 24"><path d="M20 12a8 8 0 1 1-3.3-6.5L20 4l-.8 4A8 8 0 0 1 20 12z"/></svg>
      <svg viewBox="0 0 24 24"><path d="M21 4 3 11l7 2 2 7z"/></svg>
      <div class="dots" id="dots">__DOTS__</div>
      <svg viewBox="0 0 24 24"><path d="M6 3h12v18l-6-4-6 4z"/></svg>
    </div>
    <div class="caption">__CAPTION__</div>
  </section>
  <p class="note">Folha com todos os slides em ordem (vídeos pelo pôster):</p>
  <section class="grid" aria-label="Todos os slides">__GRID__</section>
</main>
<script>
(() => {
  const track = document.getElementById('track');
  const items = [...track.children];
  const count = document.getElementById('count');
  const dots = [...document.querySelectorAll('#dots i')];
  const sound = document.getElementById('sound');
  let muted = true;
  const current = () => Math.round(track.scrollLeft / track.clientWidth);
  function update() {
    const i = current();
    count.textContent = `${i + 1}/${items.length}`;
    dots.forEach((d, k) => d.classList.toggle('on', k === i));
    items.forEach((it, k) => {
      const v = it.querySelector('video');
      if (!v) return;
      if (k === i) { v.muted = muted; v.play().catch(() => {}); } else { v.pause(); v.currentTime = 0; }
    });
    sound.hidden = !items[i].querySelector('video');
  }
  track.addEventListener('scroll', () => requestAnimationFrame(update), { passive: true });
  const go = (d) => track.scrollTo({ left: (current() + d) * track.clientWidth });
  document.getElementById('prev').onclick = () => go(-1);
  document.getElementById('next').onclick = () => go(1);
  track.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight') go(1); if (e.key === 'ArrowLeft') go(-1); });
  sound.onclick = () => { muted = !muted; sound.textContent = muted ? 'som' : 'sem som'; update(); };
  // arrasto com o mouse (no celular o próprio scroll-snap cuida do toque)
  let x0 = null; let s0 = 0;
  track.addEventListener('pointerdown', (e) => { if (e.pointerType !== 'mouse') return; x0 = e.clientX; s0 = track.scrollLeft; track.classList.add('drag'); track.setPointerCapture(e.pointerId); });
  track.addEventListener('pointermove', (e) => { if (x0 !== null) track.scrollLeft = s0 - (e.clientX - x0); });
  const end = (e) => { if (x0 === null) return; const d = e.clientX - x0; x0 = null; track.classList.remove('drag');
    track.scrollTo({ left: (Math.round(s0 / track.clientWidth) + (Math.abs(d) > 40 ? (d < 0 ? 1 : -1) : 0)) * track.clientWidth }); };
  track.addEventListener('pointerup', end); track.addEventListener('pointercancel', end);
  update();
})();
</script>
</body>
</html>
"""


def caption_html(root, who):
    """Primeiras linhas de legenda.md (sem comentários), como o app mostra antes do "mais"."""
    f = root / "legenda.md"
    if not f.is_file():
        return f"<b>{html.escape(who)}</b> <span class=\"more\">(sem legenda: rode pycode carousel caption)</span>"
    text = re.sub(r"(?s)<!--.*?-->", "", f.read_text(encoding="utf-8"))
    text = re.sub(r"(?m)^#.*$", "", text).strip()
    if len(text) > 240:
        return f"<b>{html.escape(who)}</b> {html.escape(text[:240].rsplit(' ', 1)[0])} <span class=\"more\">mais</span>"
    return f"<b>{html.escape(who)}</b> {html.escape(text)}"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode carousel preview",
                                 description="Gera preview.html: o carrossel como aparece no celular, para aprovação.")
    ap.add_argument("pasta", nargs="?", default=".", help="pasta do carrossel (padrão: a atual)")
    args = ap.parse_args(argv)
    root = L.project_dir(args.pasta)
    data = L.load_slides(root)
    total = len(data["slides"])
    brand = data.get("brand") or {}
    items, grid, missing = [], [], []
    for n in range(1, total + 1):
        f = L.out_files(root, n)
        img = f["png"] if f["png"].exists() else f["jpg"]
        poster = f["poster"] if f["poster"].exists() else img
        if not img.exists() and not f["mp4"].exists():
            missing.append(n)
            continue
        alt = html.escape(L.slides_text(data["slides"][n - 1])[:240], quote=True)
        rel = lambda p: p.relative_to(root).as_posix()  # noqa: E731
        if f["mp4"].exists():
            items.append(f'<div class="item"><video src="{rel(f["mp4"])}" poster="{rel(poster)}" muted loop playsinline '
                         f'preload="metadata" aria-label="Slide {n} em vídeo: {alt}"></video></div>')
        else:
            items.append(f'<div class="item"><img src="{rel(img)}" alt="Slide {n}: {alt}" draggable="false"></div>')
        kind = "vídeo" if f["mp4"].exists() else "imagem"
        grid.append(f'<figure><img src="{rel(poster)}" alt="" loading="lazy"><figcaption><b>{n}/{total}</b> · {kind}'
                    f'</figcaption></figure>')
    if missing:
        paths.die(f"faltam imagens dos slides {missing}: rode `pycode carousel render` antes")
    name = brand.get("name") or ""
    initials = "".join(w[0] for w in name.split()[:2]).upper() or "SM"
    page = (PAGE.replace("__TITLE__", html.escape((data.get("meta") or {}).get("title", "Carrossel")))
            .replace("__INITIALS__", html.escape(initials)).replace("__HANDLE__", html.escape(brand.get("handle", "")))
            .replace("__NAME__", html.escape(name)).replace("__TOTAL__", str(total))
            .replace("__ITEMS__", "\n".join(items)).replace("__GRID__", "\n".join(grid))
            .replace("__DOTS__", "".join("<i></i>" for _ in range(total)))
            .replace("__CAPTION__", caption_html(root, brand.get("handle", "").lstrip("@") or name)))
    out = root / "preview.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    paths.say("abra com `pycode serve <pasta>` e visite /preview.html (vídeos precisam de servidor local)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
