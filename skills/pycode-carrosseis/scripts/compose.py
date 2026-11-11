"""pycode carousel compose: aplica uma tela ou documento renderizado na área magenta de uma cena.

Uso típico com gerador de imagens: a cena é gerada SEM TEXTO e com a tela (monitor, celular, placa, papel)
pintada de magenta puro (#FF00FF). Este comando acha o quadrilátero magenta, projeta o conteúdo com
homografia (supersampling 2x), remove o magenta que vazou para a moldura e acrescenta sombra interna,
brilho de vidro, luz vazando e grão, para a tela parecer parte da foto e não um recorte colado.
"""
import argparse
import json
import sys
from pathlib import Path

from pycode_tools import paths


def magenta_score(a):
    import numpy as np
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    s = (np.minimum(r, b) - g) / 255.0
    balance = 1 - np.clip(np.abs(r - b) / 140.0, 0, 1)
    return np.clip(s * 1.6 - 0.25, 0, 1) * balance


def magenta_mask(a):
    """Maior região magenta (com buracos preenchidos), 0/1."""
    import cv2
    import numpy as np
    m = (magenta_score(a) > 0.45).astype(np.uint8)
    count, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    if count < 2:
        paths.die("não achei área magenta na cena: gere a tela como \"flat pure magenta #FF00FF, no text, no reflections\"")
    big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    m = (lab == big).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = np.zeros_like(m)
    cv2.drawContours(out, cnts, -1, 1, thickness=-1)
    return out


def _intersect(l1, l2):
    import numpy as np
    (vx1, vy1, x1, y1), (vx2, vy2, x2, y2) = l1, l2
    t = np.linalg.solve(np.array([[vx1, -vx2], [vy1, -vy2]], float), np.array([x2 - x1, y2 - y1], float))
    return np.array([x1 + vx1 * t[0], y1 + vy1 * t[0]])


def quad_from_mask(m):
    """Cantos (sup. esq., sup. dir., inf. dir., inf. esq.) por retas ajustadas ao trecho central de cada borda,
    o que ignora o arredondamento dos cantos da tela."""
    import cv2
    import numpy as np
    cnts, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)[:, 0, :].astype(float)
    s, d = c.sum(1), c[:, 0] - c[:, 1]
    rough = [c[np.argmin(s)], c[np.argmax(d)], c[np.argmax(s)], c[np.argmin(d)]]
    lines = []
    for i in range(4):
        p, q = rough[i], rough[(i + 1) % 4]
        v = q - p
        length = np.linalg.norm(v)
        v = v / length
        nrm = np.array([-v[1], v[0]])
        rel = c - p
        t, dist = rel @ v, np.abs(rel @ nrm)
        pts = c[(t > 0.18 * length) & (t < 0.82 * length) & (dist < 0.08 * length + 6)].astype(np.float32)
        if len(pts) < 10:
            pts = np.array([p, q], np.float32)
        lines.append(cv2.fitLine(pts, cv2.DIST_HUBER, 0, 0.01, 0.01).ravel())
    return np.array([_intersect(lines[(i - 1) % 4], lines[i]) for i in range(4)], np.float32)


def quad_aspect(q):
    import numpy as np
    top, bot = np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3])
    left, right = np.linalg.norm(q[3] - q[0]), np.linalg.norm(q[2] - q[1])
    return ((top + bot) / 2) / ((left + right) / 2)


def despill(a, mask, radius=40):
    """Tira o magenta que vazou para a moldura e arredores (senão a tela fica com aura roxa)."""
    import cv2
    import numpy as np
    near = cv2.dilate(mask.astype(np.uint8), np.ones((radius, radius), np.uint8)).astype(bool) & ~mask.astype(bool)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    excess = np.clip(np.minimum(r, b) - g - 6, 0, None) * near
    out = a.copy()
    out[..., 0] = r - excess * 0.9
    out[..., 2] = b - excess * 0.75
    return out


def render_html(path, width, height):
    from pycode_tools.browser import chromium, new_page
    from pycode_tools.server import serve
    import io

    import numpy as np
    from PIL import Image
    path = Path(path).resolve()
    with serve(path.parent) as base, chromium() as browser:
        page = new_page(browser, width, height, scale=2)
        page.goto(f"{base}/{path.name}", wait_until="load")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(200)
        png = page.screenshot(type="png", omit_background=True)
        errors = list(page.pycode_console)
    if errors:
        paths.die(f"erro no console ao renderizar {path.name}: {errors[:2]}")
    im = Image.open(io.BytesIO(png)).convert("RGBA")
    return np.asarray(im).astype(np.float32)


def load_content(src, aspect):
    import numpy as np
    from PIL import Image
    src = Path(src)
    if src.suffix.lower() in (".html", ".htm"):
        w = 1600
        return render_html(src, w, int(round(w / aspect)))
    im = Image.open(src).convert("RGBA")
    return np.asarray(im).astype(np.float32)


def composite(scene, content, mask, quad, *, black=7.0, bright=0.95, sheen=0.07, spill=0.3, inner=0.22,
              refl=0.05, grain=3.0, ss=2):
    import cv2
    import numpy as np
    h, w = scene.shape[:2]
    base = despill(scene, mask)
    ch, cw = content.shape[:2]
    src = np.array([[0, 0], [cw, 0], [cw, ch], [0, ch]], np.float32)
    M = cv2.getPerspectiveTransform(src, quad * ss)
    warped = cv2.warpPerspective(content, M, (w * ss, h * ss), flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    warped = cv2.resize(warped, (w, h), interpolation=cv2.INTER_AREA)
    rgb, ca = warped[..., :3], warped[..., 3:4] / 255.0
    rgb = (rgb * ca + black * (1 - ca)) * bright          # preto de tela onde o conteúdo é transparente
    m8 = mask.astype(np.uint8)
    dist = cv2.distanceTransform(m8, cv2.DIST_L2, 5)
    span = max(8.0, 0.035 * np.sqrt(m8.sum()))
    rgb = rgb * (1 - inner * np.clip(1 - dist / span, 0, 1) ** 2)[..., None]   # sombra interna da moldura
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    x0, y0, x1, y1 = quad[:, 0].min(), quad[:, 1].min(), quad[:, 0].max(), quad[:, 1].max()
    u, v = (xs - x0) / max(1, x1 - x0), (ys - y0) / max(1, y1 - y0)
    band = np.exp(-(((u * 0.8 + v * 0.55) - 0.42) / 0.16) ** 2) * sheen + np.clip(0.5 - v, 0, 1) * sheen * 0.5
    rgb = rgb + 255 * band[..., None]                    # brilho diagonal do vidro
    if refl > 0:                                         # reflexo fraco da própria cena
        hole = cv2.dilate(m8, np.ones((9, 9), np.uint8))[..., None].astype(np.float32)
        rgb = rgb + cv2.GaussianBlur((base * (1 - hole))[::-1, ::-1].copy(), (0, 0), 14) * refl
    alpha = cv2.GaussianBlur(cv2.dilate(m8, np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 0.8)[..., None]
    out = base * (1 - alpha) + rgb * alpha
    if spill > 0:                                        # luz da tela vazando na moldura
        out = out + cv2.GaussianBlur(rgb * alpha, (0, 0), 36) * spill * (1 - alpha)
    if grain > 0:
        noise = np.random.default_rng(7).normal(0, grain, (h, w)).astype(np.float32)
        out = out + cv2.GaussianBlur(noise, (0, 0), 0.6)[..., None]
    return np.clip(out, 0, 255)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode carousel compose",
                                 description="Aplica tela/documento renderizado na área magenta de uma cena (homografia).")
    ap.add_argument("--scene", required=True, help="cena com a tela em magenta puro (#FF00FF), sem texto")
    ap.add_argument("--content", required=True, help="conteúdo: imagem (png/jpg) ou página .html renderizada no Chromium")
    ap.add_argument("--out", required=True, help="arquivo de saída (.png ou .jpg)")
    ap.add_argument("--paper", action="store_true", help="papel/placa sem luz própria: sem brilho de tela nem luz vazando")
    ap.add_argument("--no-grain", action="store_true")
    args = ap.parse_args(argv)

    import numpy as np
    from PIL import Image
    scene_path = Path(args.scene)
    if not scene_path.is_file():
        paths.die(f"cena não encontrada: {scene_path}")
    scene = np.asarray(Image.open(scene_path).convert("RGB")).astype(np.float32)
    mask = magenta_mask(scene)
    quad = quad_from_mask(mask)
    aspect = quad_aspect(quad)
    content = load_content(args.content, aspect)
    opts = dict(grain=0 if args.no_grain else 3.0)
    if args.paper:
        opts.update(black=235.0, bright=1.0, sheen=0.0, spill=0.0, inner=0.08, refl=0.0)
    out = composite(scene, content, mask, quad, **opts)
    leftover = float((magenta_score(out) > 0.45).mean())
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.fromarray(out.astype(np.uint8))
    if dest.suffix.lower() in (".jpg", ".jpeg"):
        im.save(dest, "JPEG", quality=92, subsampling=0)
    else:
        im.save(dest)
    report = {"out": str(dest), "quad": [[round(float(x), 1) for x in p] for p in quad], "aspect": round(float(aspect), 3),
              "content_size": [int(content.shape[1]), int(content.shape[0])], "magenta_left": round(leftover, 5)}
    print(json.dumps(report, ensure_ascii=False))
    ch_aspect = content.shape[1] / content.shape[0]
    if abs(ch_aspect - aspect) / aspect > 0.08:
        paths.say(f"aviso: o conteúdo tem proporção {ch_aspect:.2f} e a tela {aspect:.2f}; "
                  "use o aspecto físico do aparelho (ex.: 16:10, 3:4) para não deformar")
    if leftover > 0.0005:
        paths.die(f"sobrou magenta em {leftover:.2%} da imagem: confira a máscara (ou gere a tela sem reflexos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
