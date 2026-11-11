"""pycode carousel fit: enquadra uma imagem em 4:5 (ou outra proporção) medindo onde está o conteúdo.

Nada é esticado. Modo "crop" (padrão): acha a faixa com conteúdo (bordas e contraste fora do tom de fundo),
escolhe a janela na proporção pedida que guarda o máximo dela, centralizada no conteúdo, e reduz para a
largura final. Modo "pad": mantém a imagem inteira e completa as laterais com a própria imagem desfocada e
escurecida (útil quando cortar perderia parte do objeto).
"""
import argparse
import json
import sys
from pathlib import Path

from pycode_tools import paths


def parse_ratio(text):
    a, _, b = text.partition(":")
    try:
        return float(a) / float(b)
    except (ValueError, ZeroDivisionError):
        paths.die(f"proporção inválida: {text} (use L:A, ex.: 4:5)")


def energy(arr):
    """Mapa de 'conteúdo': borda (Sobel) + diferença para a cor média das margens."""
    import cv2
    import numpy as np
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY).astype(np.float32)
    gx, gy = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    edges = np.sqrt(gx * gx + gy * gy)
    border = np.concatenate([arr[:8].reshape(-1, 3), arr[-8:].reshape(-1, 3),
                             arr[:, :8].reshape(-1, 3), arr[:, -8:].reshape(-1, 3)]).astype(np.float32)
    bg = np.median(border, axis=0)
    diff = np.abs(arr.astype(np.float32) - bg).sum(axis=2)
    e = edges / (edges.max() + 1e-6) + diff / (diff.max() + 1e-6)
    return cv2.GaussianBlur(e, (0, 0), 3)


def best_window(profile, size):
    """Início da janela de `size` que guarda mais conteúdo; empate resolvido pelo centro do conteúdo."""
    import numpy as np
    n = len(profile)
    if size >= n:
        return 0
    c = np.concatenate([[0], np.cumsum(profile)])
    sums = c[size:] - c[:n - size + 1]
    best = sums.max()
    candidates = np.where(sums >= best * 0.995)[0]
    idx = np.arange(n)
    center = (profile * idx).sum() / max(profile.sum(), 1e-6)
    return int(candidates[np.argmin(np.abs(candidates + size / 2 - center))])


def content_span(profile, keep=0.98):
    import numpy as np
    c = np.cumsum(profile) / max(profile.sum(), 1e-6)
    return int(np.searchsorted(c, (1 - keep) / 2)), int(np.searchsorted(c, 1 - (1 - keep) / 2))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode carousel fit", description="Enquadra uma imagem em 4:5 medindo o conteúdo.")
    ap.add_argument("image")
    ap.add_argument("--to", default="4:5", help="proporção final (padrão 4:5)")
    ap.add_argument("--width", type=int, default=1080, help="largura final (padrão 1080)")
    ap.add_argument("--mode", choices=("crop", "pad"), default="crop")
    ap.add_argument("--out", help="saída (padrão: <nome>-4x5.png ao lado da original)")
    args = ap.parse_args(argv)

    import numpy as np
    from PIL import Image, ImageFilter
    src = Path(args.image)
    if not src.is_file():
        paths.die(f"imagem não encontrada: {src}")
    ratio = parse_ratio(args.to)
    im = Image.open(src).convert("RGB")
    arr = np.asarray(im)
    h, w = arr.shape[:2]
    W, H = args.width, int(round(args.width / ratio))
    out = Path(args.out or src.with_name(f"{src.stem}-{args.to.replace(':', 'x')}.png"))
    e = energy(arr)
    rows, cols = e.sum(axis=1), e.sum(axis=0)
    y0c, y1c = content_span(rows)
    x0c, x1c = content_span(cols)
    report = {"source": [w, h], "content_box": [x0c, y0c, x1c, y1c]}
    if args.mode == "crop":
        if w / h > ratio:      # mais larga que o alvo: corta nas laterais
            cw, ch = int(round(h * ratio)), h
            x0, y0 = best_window(cols, cw), 0
        else:                  # mais alta: corta em cima/embaixo
            cw, ch = w, int(round(w / ratio))
            x0, y0 = 0, best_window(rows, ch)
        crop = im.crop((x0, y0, x0 + cw, y0 + ch))
        result = crop.resize((W, H), Image.LANCZOS)
        lost = {"top": max(0, y0 - y0c), "bottom": max(0, y1c - (y0 + ch)),
                "left": max(0, x0 - x0c), "right": max(0, x1c - (x0 + cw))}
        report.update(window=[x0, y0, x0 + cw, y0 + ch], content_cut_px=lost)
        if any(v > 0 for v in lost.values()):
            paths.say(f"aviso: o conteúdo não cabe inteiro em {args.to}; perdeu {lost} px. Tente --mode pad")
    else:
        scale = min(W / w, H / h)
        fg = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
        cover = max(W / w, H / h)
        bg = im.resize((int(w * cover) + 2, int(h * cover) + 2), Image.LANCZOS)
        bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
        bg = bg.filter(ImageFilter.GaussianBlur(40))
        bg = Image.fromarray((np.asarray(bg).astype(np.float32) * 0.55).astype(np.uint8))
        mask = Image.new("L", fg.size, 255)
        feather = 36
        m = np.asarray(mask).astype(np.float32)
        ramp = np.minimum(np.arange(fg.width), np.arange(fg.width)[::-1]).clip(0, feather) / feather
        rampy = np.minimum(np.arange(fg.height), np.arange(fg.height)[::-1]).clip(0, feather) / feather
        if fg.width < W:
            m *= ramp[None, :]
        if fg.height < H:
            m *= rampy[:, None]
        result = bg.copy()
        result.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2), Image.fromarray(m.astype(np.uint8)))
        report.update(placed=[(W - fg.width) // 2, (H - fg.height) // 2, fg.width, fg.height])
    out.parent.mkdir(parents=True, exist_ok=True)
    result.save(out)
    report.update(out=str(out), size=list(result.size))
    print(json.dumps(report, ensure_ascii=False))
    if result.size != (W, H):
        paths.die(f"saiu com {result.size}, esperado {(W, H)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
