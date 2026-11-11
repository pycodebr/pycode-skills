"""pycode refs list: catálogo de acervos externos com licença e status local."""
import argparse
import json

import design_lib as D
import refs_lib as R


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode refs list", description="Lista os acervos externos de referência e o que já foi baixado.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    rows = []
    for ref in R.catalog():
        meta = R.local_meta(ref)
        rows.append({**ref, "local": str(R.local_dir(ref)) if meta else "", "fetched": meta or {}})
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0
    print(f"Acervos em {R.paths.REFS}\n")
    for row in rows:
        status = (f"baixado em {row['fetched'].get('date', '?')} · commit {row['fetched'].get('commit', '?')[:10]} · "
                  f"{D.human_size(row['fetched'].get('bytes', 0))}") if row["fetched"] else "não baixado"
        print(f"{row['id']:<18} {row['name']}")
        print(f"{'':<18} https://github.com/{row['repo']} · licença: {row['license']}")
        print(f"{'':<18} {status}")
        print(f"{'':<18} {row['about']}")
        if not row["redistributable"]:
            print(f"{'':<18} ! {R.LICENSE_WARNING}")
        print()
    print("Baixar: pycode refs fetch <id> (ou all) · buscar: pycode refs search <termo>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
