"""Folha de contato para revisar várias capturas de uma vez."""
from pathlib import Path


def contact_sheet(paths, out, cols=4, thumb_width=480, gap=12, background=(16, 18, 24), labels=True):
    from PIL import Image, ImageDraw

    paths = [Path(p) for p in paths]
    if not paths:
        raise ValueError("nenhuma imagem para a folha de contato")
    thumbs = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        h = round(im.height * thumb_width / im.width)
        thumbs.append((p, im.resize((thumb_width, h), Image.LANCZOS)))
    cols = max(1, min(cols, len(thumbs)))
    rows = [thumbs[i:i + cols] for i in range(0, len(thumbs), cols)]
    label_h = 22 if labels else 0
    row_heights = [max(t.height for _, t in row) + label_h for row in rows]
    width = cols * thumb_width + (cols + 1) * gap
    height = sum(row_heights) + (len(rows) + 1) * gap
    sheet = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(sheet)
    y = gap
    for row, rh in zip(rows, row_heights):
        x = gap
        for p, t in row:
            sheet.paste(t, (x, y))
            if labels:
                draw.text((x + 4, y + t.height + 4), p.stem[:60], fill=(200, 205, 215))
            x += thumb_width + gap
        y += rh + gap
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)
    return out
