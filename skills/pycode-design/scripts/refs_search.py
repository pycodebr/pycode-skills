"""pycode refs search: busca estudos por nome, título e prompt nos acervos baixados."""
import argparse
import json

import refs_lib as R


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode refs search", description="Busca nos acervos baixados (todas as palavras precisam aparecer).")
    ap.add_argument("terms", nargs="+", help="palavras de busca, em português ou inglês (os prompts são em inglês)")
    ap.add_argument("--ref", help="limita a um acervo (id do catálogo)")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    refs = [R.find(args.ref)] if args.ref else R.catalog()
    words = [R.normalize(t) for t in args.terms]
    hits, missing = [], []
    for ref in refs:
        if not R.local_meta(ref):
            missing.append(ref["id"])
            continue
        for item in R.load_index(ref):
            hay = R.normalize(" ".join((item["slug"], item["title"], item["summary"])))
            if all(w in hay for w in words):
                score = sum(hay.count(w) for w in words) + 5 * sum(w in R.normalize(item["slug"] + " " + item["title"]) for w in words)
                hits.append((score, ref, item))
    hits.sort(key=lambda h: -h[0])
    hits = hits[:args.limit]
    if args.json:
        print(json.dumps([dict(item, ref=ref["id"]) for _, ref, item in hits], indent=2, ensure_ascii=False))
        return 0
    if missing and len(missing) == len(refs):
        R.paths.die("nenhum acervo baixado ainda. Rode `pycode refs fetch` (ou `pycode refs fetch <id>`).")
    for _, ref, item in hits:
        print(f"{item['id']:<28} {item['title'] or item['slug']}")
        print(f"{'':<28} {item['summary'][:150]}")
    print(f"\n{len(hits)} resultado(s). Abrir: pycode refs open <id>" + (f" · não baixados: {', '.join(missing)}" if missing else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
