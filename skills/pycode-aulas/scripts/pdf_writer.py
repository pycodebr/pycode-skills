"""PDF mínimo, sem dependências: uma imagem JPEG por página e uma camada de texto invisível (pesquisável).

A camada usa a Helvetica padrão do PDF com WinAnsiEncoding (cobre o português). Caracteres fora dessa tabela viram
"?" só na camada de busca; a imagem continua idêntica à captura.
"""
from __future__ import annotations

import io
from pathlib import Path

PAGE_W, PAGE_H = 960.0, 540.0     # pontos (16:9); a captura de 1920×1080 entra a 0,5 ponto por pixel
K = PAGE_W / 1920.0


def _esc(text: str) -> bytes:
    raw = text.encode("cp1252", errors="replace")
    return raw.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)").replace(b"\r", b" ").replace(b"\n", b" ")


def _utf16(text: str) -> bytes:
    return b"<FEFF" + text.encode("utf-16-be").hex().upper().encode() + b">"


def _jpeg(png: Path, quality: int = 88) -> tuple[bytes, int, int]:
    from PIL import Image
    im = Image.open(png).convert("RGB")
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return buf.getvalue(), im.width, im.height


# larguras da Helvetica (unidades por 1000 em) para ajustar a escala horizontal de cada trecho
_W = dict(zip(" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~",
              [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278] + [556] * 10 +
              [278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
               667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556, 333, 556, 556, 500, 556, 556,
               278, 556, 556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500,
               334, 260, 334, 584]))


def _width(text: str) -> float:
    import unicodedata
    total = 0
    for ch in text:
        base = unicodedata.normalize("NFKD", ch)[:1] or ch
        total += _W.get(base, 556)
    return total / 1000


def _text_ops(boxes: list[dict]) -> bytes:
    """Texto invisível (modo 3) posicionado sobre cada linha capturada, com escala horizontal aproximada."""
    out = [b"BT 3 Tr"]
    for b in boxes:
        text = b.get("text", "").strip()
        if not text:
            continue
        size = max(2.0, b["h"] * K / 1.18)
        x = b["x"] * K
        y = PAGE_H - (b["y"] + b["h"] * .8) * K
        natural = max(.5, _width(text) * size)
        tz = max(20.0, min(400.0, b["w"] * K / natural * 100))
        # espaço no fim: palavras vizinhas (ex.: títulos quebrados por palavra) não grudam na extração de texto
        out.append(b"/F1 %.2f Tf %.1f Tz 1 0 0 1 %.2f %.2f Tm (%s) Tj" % (size, tz, x, y, _esc(text + " ")))
    out.append(b"ET")
    return b"\n".join(out)


def write_pdf(pages: list[dict], out: Path, title: str = "", author: str = "", quality: int = 88) -> Path:
    """pages: [{"image": Path, "boxes": [{"text", "x", "y", "w", "h"}]}] (coordenadas em px de 1920×1080)."""
    objs: list[bytes] = []

    def add(body: bytes) -> int:
        objs.append(body)
        return len(objs)

    catalog = add(b"")              # 1: preenchido no fim
    pages_id = add(b"")             # 2
    font = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    kids = []
    for p in pages:
        data, w, h = _jpeg(Path(p["image"]), quality)
        img = add(b"<< /Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length %d >>\nstream\n" % (w, h, len(data)) + data + b"\nendstream")
        stream = b"q %.2f 0 0 %.2f 0 0 cm /Im0 Do Q\n" % (PAGE_W, PAGE_H) + _text_ops(p.get("boxes", []))
        content = add(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
        page = add(b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %.0f %.0f] /Resources << /XObject << /Im0 %d 0 R >> /Font << /F1 %d 0 R >> >> /Contents %d 0 R >>"
                   % (pages_id, PAGE_W, PAGE_H, img, font, content))
        kids.append(page)
    info = add(b"<< /Title " + _utf16(title) + b" /Author " + _utf16(author) + b" /Producer (pycode-aulas) >>")
    objs[catalog - 1] = b"<< /Type /Catalog /Pages %d 0 R /PageLayout /SinglePage /ViewerPreferences << /DisplayDocTitle true >> >>" % pages_id
    objs[pages_id - 1] = b"<< /Type /Pages /Count %d /Kids [%s] >>" % (len(kids), b" ".join(b"%d 0 R" % k for k in kids))
    buf = io.BytesIO()
    buf.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, body in enumerate(objs, start=1):
        offsets.append(buf.tell())
        buf.write(b"%d 0 obj\n" % i + body + b"\nendobj\n")
    xref = buf.tell()
    buf.write(b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1))
    for off in offsets:
        buf.write(b"%010d 00000 n \n" % off)
    buf.write(b"trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, catalog, info, xref))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(buf.getvalue())
    return out
