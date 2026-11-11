"""Contraste WCAG 2.x entre duas cores."""
import re


def parse(color):
    c = color.strip().lower()
    m = re.fullmatch(r"#?([0-9a-f]{3}|[0-9a-f]{6})", c)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.fullmatch(r"rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)(?:[,/\s]+[\d.]+%?)?\s*\)", c)
    if m:
        return tuple(int(m.group(i)) for i in (1, 2, 3))
    raise ValueError(f"cor não reconhecida: {color}")


def luminance(rgb):
    def channel(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    a, b = luminance(parse(fg)), luminance(parse(bg))
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)
