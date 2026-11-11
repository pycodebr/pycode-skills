"""Funções comuns dos comandos `pycode carousel ...` (skill pycode-carrosseis)."""
import contextlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from pycode_tools import paths

W, H = 1080, 1350
SKILL = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL / "templates" / "carousel"
EXAMPLES = SKILL / "examples"
MIN_SLIDES, MAX_SLIDES = 2, 20

# Fontes usadas pelos textos visíveis que não têm FontFace carregada (cairiam numa fonte do sistema).
FONT_CHECK_JS = r"""
() => {
  const loaded = new Set([...document.fonts].filter(f => f.status === 'loaded')
    .map(f => f.family.replace(/["']/g, '').trim().toLowerCase()));
  const failed = [...document.fonts].filter(f => f.status === 'error').map(f => f.family);
  const used = new Map();
  const slide = document.querySelector('.slide.is-only') || document;
  const walker = document.createTreeWalker(slide, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const node = walker.currentNode;
    if (!node.nodeValue.trim()) continue;
    const el = node.parentElement;
    if (!el || el.closest('[data-decor],[aria-hidden="true"]')) continue;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const fam = getComputedStyle(el).fontFamily.split(',')[0].replace(/["']/g, '').trim();
    if (!used.has(fam)) used.set(fam, node.nodeValue.trim().slice(0, 40));
  }
  const missing = [...used.entries()].filter(([f]) => !loaded.has(f.toLowerCase()))
    .map(([f, sample]) => `${f} (ex.: "${sample}")`);
  return {missing, failed: [...new Set(failed)], used: [...used.keys()]};
}
"""


def project_dir(arg):
    """Pasta do carrossel (com index.html e slides.json)."""
    root = Path(arg or ".").expanduser().resolve()
    if not (root / "slides.json").is_file() or not (root / "index.html").is_file():
        paths.die(f"{root} não parece um carrossel (faltam index.html e slides.json). "
                  "Crie um com `pycode carousel new <pasta> --title \"...\"`.")
    return root


def load_slides(root):
    try:
        data = json.loads((root / "slides.json").read_text(encoding="utf-8"))
    except ValueError as exc:
        paths.die(f"slides.json inválido: {exc}")
    slides = data.get("slides")
    if not isinstance(slides, list):
        paths.die("slides.json precisa de uma lista em \"slides\"")
    if not MIN_SLIDES <= len(slides) <= MAX_SLIDES:
        paths.die(f"o carrossel tem {len(slides)} slides; o Instagram aceita de {MIN_SLIDES} a {MAX_SLIDES}")
    return data


def write_mirror(root, data):
    """Espelho de slides.json em js/slides-data.js, para abrir o index.html direto do disco (file://)."""
    target = root / "js" / "slides-data.js"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("/* Gerado pelos comandos pycode carousel a partir de slides.json. Não edite. */\n"
                      "window.SLIDES = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")


def rules(data):
    base = {"cover_words": 20, "slide_words": 35, "safe": 64, "min_font": 24, "min_body_font": 34,
            "contrast": 4.5}
    base.update(data.get("rules") or {})
    return base


def video_slides(data):
    return [i + 1 for i, s in enumerate(data["slides"]) if s.get("video")]


def slide_url(base, n, **query):
    q = "&".join([f"only={n}", "capture=1"] + [f"{k}={v}" for k, v in query.items()])
    return f"{base}/index.html?{q}"


def open_slide(browser, base, n, scale=1, timeout=20000, **query):
    """Abre o slide n sozinho em 1080x1350 e espera o runtime terminar (fontes, desenho, texto)."""
    from pycode_tools.browser import new_page
    page = new_page(browser, W, H, scale=scale)
    page.goto(slide_url(base, n, **query), wait_until="load")
    try:
        page.wait_for_function("document.documentElement.dataset.ready", timeout=timeout)
    except Exception:  # noqa: BLE001
        paths.die(f"o slide {n} não terminou de carregar em {timeout // 1000} s. Abra com `pycode serve` "
                  "e veja o console do navegador.")
    state = page.evaluate("document.documentElement.dataset.ready")
    if state != "1":
        err = page.evaluate("document.documentElement.dataset.error || ''")
        paths.die(f"o slide {n} falhou ao montar: {err or 'erro no console'}; {page.pycode_console[:3]}")
    return page


def set_time(page, t):
    page.evaluate(f"window.setT && window.setT({float(t)})")


def animated(page):
    """Slides com animação registrada (Carousel.animate) e a duração declarada de cada um."""
    return {int(k): v for k, v in page.evaluate("window.Carousel.animated()").items()}


def still_time(data, n, anim_duration=None):
    """Instante usado na imagem estática de um slide animado: video.still, senão o fim da animação."""
    v = data["slides"][n - 1].get("video") or {}
    if v.get("still") is not None:
        return float(v["still"])
    return float(v.get("seconds") or anim_duration or 5)


def screenshot_rgb(page, scale=1):
    """Captura do viewport como array RGB 1080x1350 (com escala 2, reduz com LANCZOS)."""
    import io

    import numpy as np
    from PIL import Image
    png = page.screenshot(type="png")
    im = Image.open(io.BytesIO(png)).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
    return np.asarray(im)


def ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # noqa: BLE001
        exe = shutil.which("ffmpeg")
        if not exe:
            paths.die("ffmpeg não encontrado. Rode `pycode setup` (o imageio-ffmpeg traz o binário).")
        return exe


def probe(path):
    """Dados do MP4 lidos da saída do próprio ffmpeg (o imageio-ffmpeg não traz ffprobe)."""
    out = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    info = {"raw": out}
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    if m:
        info["duration"] = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    v = re.search(r"Video: (\w+).*?, (\w+)(\(([^)]*)\))?, (\d+)x(\d+)", out)
    if v:
        info.update(codec=v.group(1), pix_fmt=v.group(2), color=v.group(4) or "",
                    width=int(v.group(5)), height=int(v.group(6)))
    f = re.search(r"([\d.]+) fps", out)
    if f:
        info["fps"] = float(f.group(1))
    info["audio"] = bool(re.search(r"Audio: ", out))
    info["faststart"] = _moov_first(path)
    return info


def _moov_first(path):
    """faststart: o átomo moov vem antes do mdat."""
    data = Path(path).read_bytes()[:4 * 1024 * 1024]
    moov, mdat = data.find(b"moov"), data.find(b"mdat")
    return moov != -1 and (mdat == -1 or moov < mdat)


def loudness(path):
    out = subprocess.run([ffmpeg_exe(), "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    s = out[out.rfind("Summary"):]
    i = re.search(r"I:\s+(-?[\d.]+|-inf) LUFS", s)
    p = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", s)
    return (float(i.group(1)) if i and i.group(1) != "-inf" else None,
            float(p.group(1)) if p and p.group(1) != "-inf" else None)


def out_files(root, n):
    out = root / "out"
    return {k: out / f"slide-{n:02d}.{k}" for k in ("png", "jpg", "mp4")} | {
        "poster": out / f"slide-{n:02d}-poster.jpg"}


def newest_source(root):
    files = [root / "slides.json", root / "index.html"] + list((root / "css").glob("*.css")) + [
        p for p in (root / "js").glob("*.js") if p.name != "slides-data.js"]
    return max((p.stat().st_mtime for p in files if p.exists()), default=0)


def slide_image(root, n):
    """Imagem do slide n para revisão (pôster no lugar do vídeo)."""
    f = out_files(root, n)
    for key in ("poster", "png", "jpg"):
        if f[key].exists():
            return f[key]
    return None


@contextlib.contextmanager
def session(root):
    """Servidor local + Chromium para o carrossel."""
    from pycode_tools.browser import chromium
    from pycode_tools.server import serve
    with serve(root) as base, chromium() as browser:
        yield base, browser


def slides_text(slide):
    """Texto legível de um slide (título, texto e CTA), sem marcas de destaque."""
    parts = [str(slide.get(k, "")) for k in ("title", "body", "cta") if slide.get(k)]
    return re.sub(r"\s+", " ", " ".join(parts).replace("*", "")).strip()
