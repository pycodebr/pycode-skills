"""pycode refs open: mostra os caminhos do HTML e do prompt de um estudo baixado."""
import argparse

import refs_lib as R


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode refs open", description="Caminhos de um estudo: HTML para abrir no navegador e prompt para ler.")
    ap.add_argument("id", help="ex.: fable-5.2/002, opus-5.5/003 ou awesome-design-md/stripe")
    args = ap.parse_args(argv)
    ref_id, _, key = args.id.partition("/")
    ref = R.find(ref_id)
    if not R.local_meta(ref):
        R.paths.die(f"{ref_id} ainda não foi baixado. Rode `pycode refs fetch {ref_id}`.")
    key = key.strip().lower()
    for item in R.load_index(ref):
        if key and key in (item["num"], item["slug"], item["id"].split("/", 1)[1]) or (key.isdigit() and item["num"] == key.zfill(3)):
            print(f"{item['id']} · {item['title'] or item['slug']}")
            if item["html"]:
                print(f"  html    {item['html']}")
            if item["prompt"]:
                print(f"  {'prompt ' if item['html'] else 'arquivo'} {item['prompt']}")
            print(f"  licença {ref['license']}")
            if not ref["redistributable"]:
                print(f"  ! {R.LICENSE_WARNING}")
            if item["html"]:
                print(f"  ver no navegador: pycode serve {R.local_dir(ref)}  (e abra {item['num']}-{item['slug']}.html)")
            return 0
    R.paths.die(f"não encontrei {args.id}. Use `pycode refs search <termo>` para achar o id.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
