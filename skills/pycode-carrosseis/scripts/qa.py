"""pycode carousel qa: conferência fail-closed do carrossel (sai com código 1 se algo reprovar).

Confere: número de slides, tamanho exato dos arquivos, orçamento de palavras, texto PT-BR (pycode text),
CTA único no último slide, slide 2 autossuficiente, contraste de cada bloco de texto medido no fundo real,
margens seguras, texto cortado ou transbordando, fonte mínima, fontes locais, código idêntico à fonte e
executado, emendas do trilho contínuo, vídeos (H.264, yuv420p, BT.709, faststart) e folha de contato.
"""
import argparse
import doctest
import io
import json
import re
import subprocess
import sys

import carousel_lib as L
from pycode_tools import paths
from pycode_tools import text as T
from pycode_tools.color import parse, ratio
from qa_dom import DOM_QA_JS, NO_TEXT_CSS, RAIL_ONLY_CSS

TEXT_KEYS = ("title", "body", "cta", "note", "labels", "options", "caption")
COUNTED = ("title", "body", "cta")
CTA_PATTERNS = [
    (r"\bcoment(a|e|em)\b", "pedido de comentário"),
    (r"\b(salv|guard)(a|e)\b[^.!?]{0,20}\b(post|carrossel|publicação)", "pedido para salvar"),
    (r"\b(mand|envi|compartilh)(a|e)\b[^.!?]{0,30}\b(alguém|amig[oa]|quem|pessoa)", "pedido de envio"),
    (r"\blink na bio\b|\b(segue|siga)\s+(o|a|@)", "pedido de clique ou de seguir"),
    (r"\bmarc(a|e)\s+(alguém|um amigo|uma amiga|quem)", "pedido de marcação"),
]
CONNECTIVES = r"^(e|mas|então|porque|pois|isso|por isso|já|aí|daí|também|além disso)\b"


class Report:
    def __init__(self):
        self.errors, self.warnings, self.data = [], [], {}

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")


# ------------------------------------------------------------------ texto (slides.json)
def norm(text):
    return re.sub(r"\s+", " ", str(text).replace("*", "").replace("\n", " ")).strip()


def text_values(node, keys=TEXT_KEYS, inside=False):
    if isinstance(node, str):
        if inside:
            yield node
    elif isinstance(node, dict):
        for k, v in node.items():
            if k in ("code", "rail", "video", "layout", "keywords"):
                continue
            yield from text_values(v, keys, inside or k in keys)
    elif isinstance(node, list):
        for v in node:
            yield from text_values(v, keys, inside)


def check_text(data, rep, rules):
    slides = data["slides"]
    total = len(slides)
    all_text = []
    cta_slides = [i + 1 for i, s in enumerate(slides) if str(s.get("cta") or "").strip()]
    if not cta_slides:
        rep.err("CTA", "nenhum slide tem o campo \"cta\"; o último slide leva o único pedido de ação")
    elif cta_slides != [total]:
        rep.err("CTA", f"o pedido de ação precisa ser um só e no último slide; está em {cta_slides}")
    for i, s in enumerate(slides):
        n = i + 1
        where = f"slide {n}"
        values = list(text_values(s))
        all_text += values
        counted = " ".join(norm(s.get(k, "")) for k in COUNTED if s.get(k))
        words = T.words(counted)
        limit = rules["cover_words"] if n == 1 else rules["slide_words"]
        if words > limit:
            rep.err(where, f"{words} palavras (limite {limit}): corte ou divida em dois slides")
        for v in values:
            if re.search(r"\[[a-zà-ú][^\]]*\s[^\]]*\]", v, re.I):
                rep.err(where, f"texto de modelo ainda presente: {v[:60]!r}")
        if n != total:
            body = " ".join(norm(v) for v in values).lower()
            for pattern, label in CTA_PATTERNS:
                if re.search(pattern, body):
                    rep.err(where, f"{label} fora do último slide (o carrossel tem um CTA só, no fim)")
    if total >= 2:
        s2 = slides[1]
        first = norm(s2.get("title") or s2.get("body") or "")
        if not first:
            rep.warn("slide 2", "sem título nem texto: ele é a segunda capa e precisa se explicar sozinho")
        elif re.match(CONNECTIVES, first.lower()) or first[:1].islower():
            rep.warn("slide 2", f"começa como continuação ({first[:40]!r}); o Instagram pode mostrá-lo como capa")
        elif T.words(" ".join(norm(s2.get(k, "")) for k in COUNTED)) < 8:
            rep.warn("slide 2", "texto curto demais para funcionar como segunda capa")
    issues = T.lint(T.clean("\n".join(all_text)))
    for level, msg, ctx in issues:
        (rep.err if level == "erro" else rep.warn)("texto", msg + (f" · …{ctx}…" if ctx else ""))


# ------------------------------------------------------------------ código (execução e fonte)
def code_objects(node, path=""):
    if isinstance(node, dict):
        if isinstance(node.get("lines"), list):
            yield path or "code", node
        for k, v in node.items():
            if k != "lines":
                yield from code_objects(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from code_objects(v, f"{path}.{i}")


def run_doctest(source):
    parser = doctest.DocTestParser()
    test = parser.get_doctest(source, {}, "slide", None, 0)
    out = io.StringIO()
    runner = doctest.DocTestRunner(optionflags=0)
    runner.run(test, out=out.write)
    return runner.failures, len(test.examples), out.getvalue()


def run_python(source, cwd):
    r = subprocess.run([sys.executable, "-I", "-c", source], capture_output=True, text=True, timeout=20, cwd=cwd)
    return r.returncode, r.stdout.rstrip("\n"), r.stderr.strip()


def check_code(root, data, rep):
    for i, s in enumerate(data["slides"]):
        where = f"slide {i + 1}"
        for path, code in code_objects(s):
            text = "\n".join(code["lines"])
            mode = code.get("run")
            if mode == "doctest":
                fails, count, log = run_doctest(text)
                if not count:
                    rep.err(where, f"{path}: run=doctest mas não há linhas com >>>")
                elif fails:
                    rep.err(where, f"{path}: a saída mostrada não é a saída real do Python\n{log[-600:]}")
            elif mode == "python":
                code_rc, out, errtxt = run_python(text, root)
                expect = code.get("expect")
                expect = "\n".join(expect) if isinstance(expect, list) else expect
                if code_rc != 0:
                    rep.err(where, f"{path}: o código falha ao rodar: {errtxt[-300:]}")
                elif expect is not None and out != str(expect):
                    rep.err(where, f"{path}: saída real {out!r} diferente da esperada {expect!r}")
                code["_out"] = out
            if code.get("source"):
                src = root / code["source"]
                if not src.is_file():
                    rep.err(where, f"{path}: fonte {code['source']} não existe na pasta do carrossel")
                elif text not in src.read_text(encoding="utf-8", errors="ignore"):
                    rep.err(where, f"{path}: o texto não aparece literalmente em {code['source']}")
            if not mode and not code.get("source") and code.get("check") != "literal":
                rep.warn(where, f"{path}: código sem conferência (use run: doctest|python, source ou check: literal)")
        quiz = s.get("quiz")
        if quiz:
            check_quiz(where, s, quiz, rep)


def check_quiz(where, slide, quiz, rep):
    opts, ans = quiz.get("options") or [], str(quiz.get("answer", "")).upper()
    idx = "ABCDEFG".find(ans)
    if idx < 0 or idx >= len(opts):
        rep.err(where, f"quiz: resposta {ans!r} não corresponde a nenhuma opção")
        return
    out = None
    for _, code in code_objects(slide):
        if "_out" in code:
            out = code["_out"]
    if out is None:
        rep.warn(where, "quiz sem código executado (run: python) para conferir a resposta")
    elif norm(opts[idx]).split(") ", 1)[-1] != out:
        rep.err(where, f"quiz: a opção {ans} ({opts[idx]!r}) não é a saída real ({out!r})")


# ------------------------------------------------------------------ página (Chromium)
def contrast_of(item, bg):
    """5º percentil do contraste entre a cor efetiva do texto e os pixels de fundo atrás dele."""
    import numpy as np
    if item["bgClip"] == "text" or "transparent" in str(item["textFill"]) and "rgba(0, 0, 0, 0)" in item["textFill"]:
        return None
    parsed = css_color(item["color"])
    if parsed is None:
        return None
    fg, a0 = np.array(parsed[:3], float), parsed[3]
    alpha = item["opacity"] * a0
    samples = []
    for x0, y0, x1, y1 in item["rects"]:
        xa, xb = max(0, int(x0)), min(L.W, int(x1))
        ya, yb = max(0, int(y0)), min(L.H, int(y1))
        if xb - xa < 2 or yb - ya < 2:
            continue
        patch = bg[ya:yb:3, xa:xb:3].reshape(-1, 3).astype(float)
        samples.append(patch)
    if not samples:
        return None
    px = np.concatenate(samples)
    eff = alpha * fg + (1 - alpha) * px
    lt, lb = lum_array(eff), lum_array(px)
    r = (np.maximum(lt, lb) + 0.05) / (np.minimum(lt, lb) + 0.05)
    return float(np.percentile(r, 5))


def lum_array(rgb):
    """Luminância relativa WCAG de uma matriz Nx3 (0..255)."""
    import numpy as np
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return c @ np.array([0.2126, 0.7152, 0.0722])


def css_color(value):
    """(r, g, b, alpha) de rgb(), rgba(), color(srgb ...) ou hexadecimal; None se não reconhecer."""
    v = str(value).strip().lower()
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,/\s]+([\d.]+%?))?\s*\)", v)
    if m:
        a = m.group(4)
        alpha = 1.0 if a is None else (float(a[:-1]) / 100 if a.endswith("%") else float(a))
        return float(m.group(1)), float(m.group(2)), float(m.group(3)), alpha
    m = re.fullmatch(r"color\(srgb\s+([\d.e-]+)\s+([\d.e-]+)\s+([\d.e-]+)(?:\s*/\s*([\d.]+%?))?\)", v)
    if m:
        a = m.group(4)
        alpha = 1.0 if a is None else (float(a[:-1]) / 100 if a.endswith("%") else float(a))
        return tuple(max(0.0, min(255.0, float(m.group(i)) * 255)) for i in (1, 2, 3)) + (alpha,)
    try:
        return tuple(float(c) for c in parse(v)) + (1.0,)
    except ValueError:
        return None


def area(r):
    return max(0, r[2] - r[0]) * max(0, r[3] - r[1])


def overlap(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return max(0, w) * max(0, h)


def check_dom(n, dom, bg, data, rep, rules, when=""):
    where = f"slide {n}{when}"
    s = data["slides"][n - 1]
    safe = rules["safe"]
    if dom["placeholders"]:
        rep.err(where, "ainda tem o marcador data-placeholder: desenhe o objeto herói do conceito")
    for it in dom["items"]:
        name = f"{it['role']} \"{it['text'][:32]}\""
        x0 = min(r[0] for r in it["rects"]); y0 = min(r[1] for r in it["rects"])  # noqa: E702
        x1 = max(r[2] for r in it["rects"]); y1 = max(r[3] for r in it["rects"])  # noqa: E702
        if it["opacity"] < 0.05:
            continue
        if x0 < safe - 1 or y0 < safe - 1 or x1 > L.W - safe + 1 or y1 > L.H - safe + 1:
            rep.err(where, f"{name} fora da margem segura de {safe}px ({int(x0)},{int(y0)} a {int(x1)},{int(y1)})")
        for c in it["clip"]:
            bx = c["box"]
            if x0 < bx[0] - 1 or y0 < bx[1] - 1 or x1 > bx[2] + 1 or y1 > bx[3] + 1:
                rep.err(where, f"{name} cortado por {c['el']}")
                break
        if it["overflow"]:
            o = it["overflow"]
            rep.err(where, f"{name} transborda {o['block']} ({o['sw']}x{o['sh']} em {o['cw']}x{o['ch']})")
        minimum = rules["min_body_font"] if it["role"] in COUNTED else rules["min_font"]
        if it["fontSize"] < minimum - 0.5:
            rep.err(where, f"{name} com {it['fontSize']:.0f}px (mínimo {minimum}px em 1080 de largura)")
        value = contrast_of(it, bg)
        it["contrast"] = value
        if value is None:
            rep.warn(where, f"{name}: contraste não medido (texto com degradê ou cor não reconhecida)")
        elif value < rules["contrast"]:
            rep.err(where, f"{name}: contraste {value:.2f}:1 (mínimo {rules['contrast']}:1 no fundo medido)")
    visible = [it for it in dom["items"] if it["opacity"] >= 0.05]
    for i, a in enumerate(visible):
        for b in visible[i + 1:]:
            if a["role"] == b["role"] == "code":
                continue
            hit = max((overlap(ra, rb) / (min(area(ra), area(rb)) or 1) for ra in a["rects"] for rb in b["rects"]),
                      default=0)
            if hit > 0.25:
                rep.err(where, f"texto sobre texto: \"{a['text'][:24]}\" e \"{b['text'][:24]}\"")
    if when:
        return
    for f in dom["fields"]:
        expected = norm(L_get(s, f["field"]) or "")
        if f["text"] != expected:
            rep.err(where, f"campo {f['field']}: o slide mostra {f['text'][:50]!r}, o slides.json diz {expected[:50]!r}")
    codes = {p: c for p, c in code_objects(s)}
    for c in dom["codes"]:
        code = codes.get(c["path"])
        if not code:
            rep.err(where, f"bloco [data-code={c['path']}] sem código correspondente no slides.json")
            continue
        if c["lines"] != code["lines"]:
            diff = next((f"linha {k + 1}: {a!r} ≠ {b!r}" for k, (a, b) in enumerate(zip(c["lines"], code["lines"])) if a != b),
                        f"{len(c['lines'])} linhas no slide, {len(code['lines'])} no slides.json")
            rep.err(where, f"código renderizado diferente da fonte ({diff})")
        if not c["ligaturesOff"]:
            rep.err(where, f"código {c['path']} com ligaduras ligadas (use a classe .code)")
        if c["overflow"]:
            rep.err(where, f"código {c['path']} não cabe na largura (um token maior que a linha)")


def L_get(obj, path):
    for k in str(path).split("."):
        if isinstance(obj, list) and k.isdigit():
            obj = obj[int(k)] if int(k) < len(obj) else None
        elif isinstance(obj, dict):
            obj = obj.get(k)
        else:
            return None
    return obj


def edge_runs(column):
    rows = [i for i, v in enumerate(column) if v > 128]
    runs, start = [], None
    for i, r in enumerate(rows):
        if start is None:
            start = r
        if i == len(rows) - 1 or rows[i + 1] != r + 1:
            runs.append((start, r))
            start = None
    return runs


def check_seams(edges, data, rep):
    slides = data["slides"]
    seams = []
    for n in range(1, len(slides)):
        out_y = (slides[n - 1].get("rail") or {}).get("out")
        in_y = (slides[n].get("rail") or {}).get("in")
        if out_y is None and in_y is None:
            continue
        where = f"emenda {n}→{n + 1}"
        if out_y != in_y:
            rep.err(where, f"rail.out do slide {n} ({out_y}) ≠ rail.in do slide {n + 1} ({in_y})")
            continue
        a, b = edges.get(n, {}).get("right", []), edges.get(n + 1, {}).get("left", [])
        if not a or not b:
            rep.err(where, "trilho não encontrado na borda (desenhe com svg.rail .rail-line)")
            continue
        ca, cb = min(a, key=lambda r: abs((r[0] + r[1]) / 2 - out_y)), min(b, key=lambda r: abs((r[0] + r[1]) / 2 - in_y))
        mid_a, mid_b = (ca[0] + ca[1]) / 2, (cb[0] + cb[1]) / 2
        seams.append({"seam": f"{n}->{n + 1}", "right": ca, "left": cb, "declared": out_y})
        if abs(mid_a - mid_b) > 2 or abs((ca[1] - ca[0]) - (cb[1] - cb[0])) > 3:
            rep.err(where, f"o trilho sai em {ca} e entra em {cb} (diferença acima de 2px)")
        if abs(mid_a - out_y) > 3:
            rep.err(where, f"o trilho sai em y≈{mid_a:.0f}, mas rail.out declara {out_y}")
    return seams


def inspect_pages(root, data, rep, rules):
    results, edges = {}, {}
    with L.session(root) as (base, browser):
        for n in range(1, len(data["slides"]) + 1):
            page = L.open_slide(browser, base, n, scale=1)
            anims = L.animated(page)
            states = [("", L.still_time(data, n, anims.get(n)))] if n in anims else [("", None)]
            if n in anims:
                states.append((" (quadro 0 do vídeo)", 0))
            for when, t in states:
                if t is not None:
                    L.set_time(page, t)
                dom = page.evaluate(DOM_QA_JS)
                style = page.add_style_tag(content=NO_TEXT_CSS)
                bg = L.screenshot_rgb(page)
                style.evaluate("e => e.remove()")
                check_dom(n, dom, bg, data, rep, rules, when)
                if not when:
                    fonts = page.evaluate(L.FONT_CHECK_JS)
                    if fonts["missing"] or fonts["failed"]:
                        rep.err(f"slide {n}", f"fonte sem arquivo local (cai na do sistema): {fonts['missing'] + fonts['failed']}")
                    results[n] = {"items": [{k: it.get(k) for k in ("role", "text", "fontSize", "contrast")} for it in dom["items"]],
                                  "fonts": fonts["used"], "codes": len(dom["codes"]), "animated": n in anims}
                    if dom["hasRail"]:
                        page.add_style_tag(content=RAIL_ONLY_CSS)
                        img = L.screenshot_rgb(page).mean(axis=2)
                        edges[n] = {"left": edge_runs(img[:, 0]), "right": edge_runs(img[:, L.W - 1])}
            if 1 in anims and n == 1 and not data["slides"][0].get("video"):
                rep.warn("slide 1", "tem animação, mas o slides.json não declara \"video\"")
            if page.pycode_console:
                rep.err(f"slide {n}", f"erro no console: {page.pycode_console[:2]}")
            if page.pycode_failed:
                rep.err(f"slide {n}", f"requisição que falhou: {page.pycode_failed[:2]}")
            page.context.close()
    return results, edges


# ------------------------------------------------------------------ tokens, arquivos e vídeos
def check_tokens(tokens, rep, rules):
    pairs = [("--text", "--bg", True), ("--text", "--surface", True), ("--accent-ink", "--accent", True),
             ("--muted", "--bg", False), ("--muted", "--surface", False), ("--paper-ink", "--paper", False),
             ("--accent", "--bg", False)]
    out = {}
    for fg, bg, required in pairs:
        try:
            value = ratio(tokens[fg], tokens[bg])
        except (KeyError, ValueError):
            continue
        out[f"{fg} / {bg}"] = round(value, 2)
        if value < rules["contrast"]:
            (rep.err if required else rep.warn)("tokens", f"{fg} sobre {bg}: {value:.2f}:1 (mínimo {rules['contrast']}:1)")
    return out


def check_files(root, data, rep):
    from PIL import Image
    total = len(data["slides"])
    fresh = L.newest_source(root)
    for n in range(1, total + 1):
        f = L.out_files(root, n)
        img = f["png"] if f["png"].exists() else f["jpg"]
        if not img.exists():
            rep.err(f"slide {n}", "sem imagem em out/: rode `pycode carousel render`")
            continue
        size = Image.open(img).size
        if size != (L.W, L.H):
            rep.err(f"slide {n}", f"{img.name} tem {size[0]}x{size[1]}, precisa de {L.W}x{L.H}")
        if img.stat().st_mtime < fresh:
            rep.warn(f"slide {n}", f"{img.name} é mais antigo que o código ou o texto: renderize de novo")
        video = data["slides"][n - 1].get("video")
        if f["mp4"].exists():
            check_video(n, f["mp4"], video or {}, rep)
            if f["mp4"].stat().st_mtime < fresh:
                rep.warn(f"slide {n}", "o MP4 é mais antigo que o código ou o texto: grave de novo")
        elif video:
            rep.warn(f"slide {n}", f"declara vídeo, mas falta out/slide-{n:02d}.mp4: rode `pycode carousel video --slide {n}`")


def check_video(n, mp4, video, rep):
    info = L.probe(mp4)
    where = f"slide {n} (vídeo)"
    if (info.get("width"), info.get("height")) != (L.W, L.H):
        rep.err(where, f"{info.get('width')}x{info.get('height')} em vez de {L.W}x{L.H}")
    if info.get("codec") != "h264" or info.get("pix_fmt") != "yuv420p":
        rep.err(where, f"codec {info.get('codec')} / {info.get('pix_fmt')} (precisa de h264 + yuv420p)")
    if "bt709" not in info.get("color", ""):
        rep.err(where, f"cor sem a marcação BT.709 ({info.get('color') or 'sem tag'})")
    if not info["faststart"]:
        rep.err(where, "sem faststart (o moov precisa vir antes do mdat)")
    seconds = video.get("seconds")
    if seconds and abs(info.get("duration", 0) - seconds) > 0.12:
        rep.warn(where, f"duração {info.get('duration')} s, slides.json declara {seconds} s")
    if not 3 <= info.get("duration", 0) <= 60:
        rep.err(where, f"duração {info.get('duration')} s fora de 3 a 60 s")


def contact_sheet(root, total):
    from pycode_tools.images import contact_sheet as sheet
    files = [L.slide_image(root, n) for n in range(1, total + 1)]
    files = [f for f in files if f]
    if not files:
        return None
    return sheet(files, root / "out" / "folha-de-contato.jpg", cols=min(4, len(files)), thumb_width=360)


# ------------------------------------------------------------------ principal
def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode carousel qa", description="Conferência fail-closed do carrossel.")
    ap.add_argument("pasta", nargs="?", default=".", help="pasta do carrossel (padrão: a atual)")
    ap.add_argument("--strict", action="store_true", help="avisos também reprovam")
    ap.add_argument("--json", action="store_true", help="imprime o relatório completo em JSON")
    args = ap.parse_args(argv)
    if not __debug__:
        raise RuntimeError("rode sem -O: o QA não depende de assert, mas não deve rodar otimizado")

    root = L.project_dir(args.pasta)
    data = L.load_slides(root)
    L.write_mirror(root, data)
    rules = L.rules(data)
    rep = Report()
    check_text(data, rep, rules)
    check_code(root, data, rep)
    pages, edges = inspect_pages(root, data, rep, rules)
    seams = check_seams(edges, data, rep)
    tokens = check_tokens(_tokens(root), rep, rules)
    check_files(root, data, rep)
    sheet = contact_sheet(root, len(data["slides"]))

    report = {"pasta": str(root), "slides": len(data["slides"]), "errors": rep.errors, "warnings": rep.warnings,
              "tokens": tokens, "seams": seams, "pages": pages, "contact_sheet": str(sheet) if sheet else None}
    (root / "qa").mkdir(exist_ok=True)
    (root / "qa" / "relatorio.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    for e in rep.errors:
        print(f"  [erro]  {e}")
    for w in rep.warnings:
        print(f"  [aviso] {w}")
    worst = min((it["contrast"] for p in pages.values() for it in p["items"] if it.get("contrast")), default=None)
    print(f"{len(data['slides'])} slides · {len(rep.errors)} erro(s) · {len(rep.warnings)} aviso(s)"
          + (f" · menor contraste {worst:.2f}:1" if worst else "") + (f" · emendas {len(seams)}" if seams else ""))
    if sheet:
        print(f"folha de contato: {sheet}")
    print(f"relatório: {root / 'qa' / 'relatorio.json'}")
    failed = rep.errors or (args.strict and rep.warnings)
    if failed:
        paths.say("QA reprovado: corrija os itens acima e rode de novo")
        return 1
    paths.say("QA aprovado")
    return 0


def _tokens(root):
    css = (root / "css" / "tokens.css").read_text(encoding="utf-8")
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", css)}


if __name__ == "__main__":
    sys.exit(main())
