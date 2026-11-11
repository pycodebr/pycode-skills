#!/usr/bin/env python3
"""pycode page perf: Lighthouse celular e desktop, várias rodadas, mediana e reprovação abaixo do mínimo.

Pasta ou projeto: serve dist/ em 127.0.0.1 com gzip (como uma hospedagem real) e mede.
URL: mede a URL publicada. Use --block para medir só o que é do projeto (e o comando confere se o bloqueio
funcionou de verdade: cada requisição bloqueada precisa ter statusCode -1 e zero bytes transferidos).
"""
import argparse
import contextlib
import fnmatch
import html
import io
import json
import os
import statistics
import sys
import time
from pathlib import Path

if not __debug__:
    raise RuntimeError("rode sem -O: os gates de performance não podem ser desligados")

import page_common as pc  # noqa: E402
from pycode_tools import commands, paths  # noqa: E402

METRICS = [("first-contentful-paint", "FCP", "ms"), ("largest-contentful-paint", "LCP", "ms"),
           ("total-blocking-time", "TBT", "ms"), ("cumulative-layout-shift", "CLS", ""), ("speed-index", "SI", "ms")]
CATS = [("performance", "Performance"), ("accessibility", "Acessibilidade"), ("best-practices", "Boas práticas"), ("seo", "SEO")]


def parse_args(argv):
    ap = argparse.ArgumentParser(prog="pycode page perf", description="Lighthouse celular e desktop com mediana de várias rodadas.")
    ap.add_argument("target", nargs="?", default=".", help="projeto (mede dist/), pasta com index.html ou URL")
    ap.add_argument("--runs", type=int, default=3, help="rodadas por perfil (padrão 3; use número ímpar)")
    ap.add_argument("--min-score", type=int, default=90, help="performance mínima (mediana) em cada perfil")
    ap.add_argument("--min-a11y", type=int, default=90, help="acessibilidade mínima")
    ap.add_argument("--min-best", type=int, default=90, help="boas práticas mínima")
    ap.add_argument("--min-seo", type=int, default=85, help="SEO mínima (páginas com noindex de propósito: use 0)")
    ap.add_argument("--max-cls", type=float, default=0.1, help="CLS máximo (mediana)")
    ap.add_argument("--block", action="append", default=[], help="padrão de URL bloqueado (ex.: '*googletagmanager.com*'). Repita")
    ap.add_argument("--only", choices=("mobile", "desktop"), help="mede só um perfil")
    ap.add_argument("--out", help="pasta dos relatórios (padrão: <projeto>/perf ou ./perf-report)")
    ap.add_argument("--baseline", action="store_true",
                    help="a cada rodada, mede também uma página HTML mínima (só texto): mostra quanto da nota é ruído da máquina")
    return ap.parse_args(argv)


MINIMAL_PAGE = ("<!doctype html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\">"
                "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>Página mínima</title>"
                "<meta name=\"description\" content=\"Página mínima para medir o ruído da máquina.\"></head>"
                "<body><main><h1>Página mínima</h1>" + "<p>Texto de exemplo, sem CSS e sem script.</p>" * 40 + "</main></body></html>")


def run_lighthouse(url, out, name, desktop, blocks):
    argv = [url, "--out", str(out), "--name", name] + (["--desktop"] if desktop else [])
    for pattern in blocks:
        argv += ["--block", pattern]
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        commands.cmd_lighthouse(argv)
    return json.loads((out / f"{name}.report.json").read_text(encoding="utf-8"))


def summarize(data, blocks):
    audits = data["audits"]
    row = {"scores": {k: round((data["categories"].get(k, {}).get("score") or 0) * 100) for k, _ in CATS}}
    for key, label, _ in METRICS:
        row[label] = audits.get(key, {}).get("numericValue")
    items = audits.get("network-requests", {}).get("details", {}).get("items", [])
    row["requests"] = len(items)
    row["bytes"] = audits.get("total-byte-weight", {}).get("numericValue")
    row["benchmark"] = data.get("environment", {}).get("benchmarkIndex")
    leaks = []
    for item in items:
        if any(fnmatch.fnmatch(item.get("url", ""), p) for p in blocks):
            if item.get("statusCode") != -1 or item.get("transferSize") or item.get("resourceSize"):
                leaks.append(item.get("url", "")[:120])
    row["block_leaks"] = leaks
    row["runtime_error"] = (data.get("runtimeError") or {}).get("code")
    return row


def median_row(rows):
    med = {"scores": {k: statistics.median(r["scores"][k] for r in rows) for k, _ in CATS}}
    for _, label, _ in METRICS:
        values = [r[label] for r in rows if r[label] is not None]
        med[label] = statistics.median(values) if values else None
    for key in ("requests", "bytes", "benchmark"):
        values = [r[key] for r in rows if r[key] is not None]
        med[key] = statistics.median(values) if values else None
    return med


def fmt(label, value):
    if value is None:
        return "?"
    if label == "CLS":
        return f"{value:.3f}"
    return f"{value / 1000:.2f} s" if label != "TBT" else f"{value:.0f} ms"


def print_table(profile, rows, med):
    print(f"\n{profile}: {len(rows)} rodada(s)")
    head = "  rodada  perf  a11y  bp   seo   " + "  ".join(f"{m[1]:>8}" for m in METRICS) + "      KB  req  bench"
    print(head)
    for i, r in enumerate(rows + [med], 1):
        tag = f"{i:>6}" if i <= len(rows) else "mediana"
        s = r["scores"]
        print(f"  {tag:>6}  {s['performance']:>4}  {s['accessibility']:>4}  {s['best-practices']:>3}  {s['seo']:>4}   "
              + "  ".join(f"{fmt(m[1], r[m[1]]):>8}" for m in METRICS)
              + f"  {(r['bytes'] or 0) / 1024:6.0f}  {r['requests'] or 0:>3}  {r['benchmark'] or 0:>5.0f}")


def gates(profile, med, rows, args):
    out = []
    s = med["scores"]
    for key, minimum, label in (("performance", args.min_score, "performance"), ("accessibility", args.min_a11y, "acessibilidade"),
                                ("best-practices", args.min_best, "boas práticas"), ("seo", args.min_seo, "SEO")):
        if s[key] < minimum:
            out.append(f"{profile}: {label} {s[key]:g} abaixo do mínimo {minimum}")
    if med["CLS"] is not None and med["CLS"] > args.max_cls:
        out.append(f"{profile}: CLS {med['CLS']:.3f} acima de {args.max_cls}")
    for i, r in enumerate(rows, 1):
        if r["block_leaks"]:
            out.append(f"{profile} rodada {i}: bloqueio falhou (houve transferência): {r['block_leaks'][:3]}")
        if r["runtime_error"]:
            out.append(f"{profile} rodada {i}: erro do Lighthouse {r['runtime_error']}")
    return out


def _label(target, project_root):
    """Nome do projeto em vez do caminho local (a imagem pode ir para documentação pública)."""
    if project_root:
        return f"{Path(project_root).name} (dist local, gzip)"
    return str(target)


def _band(score):
    return "good" if score >= 90 else "mid" if score >= 50 else "bad"


def summary_html(results, target, args, project_root):
    tokens = ""
    if project_root and (project_root / "src" / "css" / "tokens.css").is_file():
        tokens = (project_root / "src" / "css" / "tokens.css").read_text(encoding="utf-8")
    cards = []
    for profile, data in results.items():
        med = data["median"]
        scores = "".join(f'<div class="score {_band(med["scores"][k])}"><b>{med["scores"][k]:g}</b><span>{label}</span></div>'
                         for k, label in CATS)
        metrics = "".join(f"<tr><th>{label}</th><td>{fmt(label, med[label])}</td></tr>" for _, label, _ in METRICS)
        metrics += f"<tr><th>Bytes</th><td>{(med['bytes'] or 0) / 1024:.0f} KB</td></tr><tr><th>Requisições</th><td>{med['requests'] or 0:g}</td></tr>"
        note = f"Mediana de {len(data['runs'])} rodada(s)."
        if data.get("baseline"):
            base = data["baseline"]["median"]
            note += (f" Página mínima medida no mesmo momento: performance {base['scores']['performance']:g},"
                     f" TBT {fmt('TBT', base['TBT'])} (ruído da máquina).")
        cards.append(f'<section><h2>{"Celular" if profile == "mobile" else "Desktop"}</h2><div class="scores">{scores}</div>'
                     f'<table>{metrics}</table><p>{html.escape(note)}</p></section>')
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Performance</title><style>
{tokens}
body{{margin:0;padding:40px;width:1120px;background:var(--bg,#0b0f14);color:var(--text,#eef);font-family:system-ui,sans-serif}}
h1{{margin:0 0 6px;font-size:30px;font-weight:500}} .meta{{color:var(--muted,#9ab);font-size:14px;margin:0 0 28px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px}} section{{padding:24px;border:1px solid var(--line,#345);border-radius:16px;background:var(--surface,#123)}}
h2{{margin:0 0 18px;font-size:20px;font-weight:500}} .scores{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}
.score{{text-align:center;padding:14px 6px;border-radius:12px;background:var(--bg,#0b0f14)}} .score b{{display:block;font-size:34px;font-weight:500;color:var(--ok,#7be0a6)}}
.score span{{font-size:12px;color:var(--muted,#9ab)}} .mid b{{color:var(--warn,#f5c451)}} .bad b{{color:var(--danger,#ff7a70)}} table{{width:100%;margin-top:18px;border-collapse:collapse;font-size:15px}}
th,td{{padding:7px 0;border-top:1px solid var(--line,#345);text-align:left}} td{{text-align:right;font-variant-numeric:tabular-nums}} p{{color:var(--muted,#9ab);font-size:13px;margin:14px 0 0}}
</style></head><body><h1>Lighthouse · {html.escape(_label(target, project_root))}</h1>
<p class="meta">pycode page perf · {time.strftime("%Y-%m-%d %H:%M")} · {"bloqueios: " + ", ".join(args.block) if args.block else "página completa"}</p>
<div class="grid">{"".join(cards)}</div></body></html>"""


def render_summary(html_file, png_file):
    from pycode_tools.browser import chromium
    with chromium() as browser:
        page = browser.new_page(viewport={"width": 1200, "height": 600}, device_scale_factor=1)
        page.goto(html_file.resolve().as_uri())
        page.screenshot(path=str(png_file), full_page=True)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    kind, value, root = pc.resolve_target(args.target)
    out = Path(args.out) if args.out else (root / "perf" if root else Path("perf-report"))
    out.mkdir(parents=True, exist_ok=True)
    profiles = [p for p in ("mobile", "desktop") if not args.only or p == args.only]
    results, failures = {}, []
    with contextlib.ExitStack() as stack:
        url = value if kind == "url" else stack.enter_context(pc.serve_gzip(value)) + "/"
        base_url = None
        if args.baseline:
            import tempfile
            tmp = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="pycode-base-")))
            (tmp / "index.html").write_text(MINIMAL_PAGE, encoding="utf-8")
            base_url = stack.enter_context(pc.serve_gzip(tmp)) + "/"
        paths.say(f"medindo {url} · {args.runs} rodada(s) por perfil · carga da máquina {os.getloadavg()[0]:.1f}")
        for profile in profiles:
            rows, base_rows = [], []
            for i in range(1, args.runs + 1):
                load = os.getloadavg()[0]
                data = run_lighthouse(url, out, f"{profile}-{i}", profile == "desktop", args.block)
                row = summarize(data, args.block)
                row["load"] = round(load, 2)
                rows.append(row)
                print(f"  {profile} {i}/{args.runs}: performance {row['scores']['performance']} · LCP {fmt('LCP', row['LCP'])} · carga {load:.1f}", flush=True)
                if base_url:  # intercalada com a página, nas mesmas condições da máquina
                    base_rows.append(summarize(run_lighthouse(base_url, out, f"minima-{profile}-{i}", profile == "desktop", []), []))
            med = median_row(rows)
            results[profile] = {"runs": rows, "median": med}
            print_table("Celular" if profile == "mobile" else "Desktop", rows, med)
            if base_rows:
                base_med = median_row(base_rows)
                results[profile]["baseline"] = {"runs": base_rows, "median": base_med}
                print(f"  página mínima (ruído da máquina): performance {base_med['scores']['performance']:g} · "
                      f"TBT {fmt('TBT', base_med['TBT'])} · rodadas {[r['scores']['performance'] for r in base_rows]}")
            failures += gates(profile, med, rows, args)
            benches = [r["benchmark"] for r in rows if r["benchmark"]]
            if benches and max(benches) > 1.3 * min(benches):
                print(f"  [aviso] benchmarkIndex variou de {min(benches):.0f} a {max(benches):.0f}: a máquina estava ocupada em parte das rodadas")
    report = {"target": str(value), "url_mode": kind == "url", "blocked": args.block, "results": results, "failures": failures,
              "thresholds": {"performance": args.min_score, "accessibility": args.min_a11y, "best-practices": args.min_best,
                             "seo": args.min_seo, "cls": args.max_cls}}
    pc.write_json(out / "perf.json", report)
    summary = out / "perf-summary.html"
    summary.write_text(summary_html(results, value, args, root), encoding="utf-8")
    render_summary(summary, out / "perf-summary.png")
    print(f"\nrelatórios: {out}  (HTML do Lighthouse por rodada, perf.json e perf-summary.png)")
    if failures:
        for line in failures:
            print(f"  [FALHA] {line}")
        return 1
    print("  todos os mínimos atendidos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
