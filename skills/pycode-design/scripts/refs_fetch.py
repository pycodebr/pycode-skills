"""pycode refs fetch: baixa acervos externos para ~/.pycode-skills/references (clone raso, com tarball como reserva)."""
import argparse
import datetime
import io
import json
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path

import design_lib as D
import refs_lib as R

UA = {"User-Agent": "pycode-skills"}


def via_git(ref, dest):
    if not shutil.which("git"):
        raise RuntimeError("git não encontrado")
    url = f"https://github.com/{ref['repo']}.git"
    subprocess.run(["git", "clone", "--depth", "1", "--branch", ref["branch"], "--quiet", url, str(dest)],
                   check=True, capture_output=True, text=True, timeout=900)
    commit = subprocess.run(["git", "-C", str(dest), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    shutil.rmtree(dest / ".git", ignore_errors=True)
    return commit


def via_tarball(ref, dest):
    api = f"https://api.github.com/repos/{ref['repo']}/commits/{ref['branch']}"
    with urllib.request.urlopen(urllib.request.Request(api, headers={**UA, "Accept": "application/vnd.github.sha"}), timeout=60) as r:
        commit = r.read().decode().strip()
    url = f"https://codeload.github.com/{ref['repo']}/tar.gz/{commit}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=900) as r:
        blob = r.read()
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        root = tar.getmembers()[0].name.split("/")[0]
        safe = [m for m in tar.getmembers() if not (m.issym() or m.islnk()) and ".." not in Path(m.name).parts]
        with tempfile.TemporaryDirectory() as tmp:
            tar.extractall(tmp, members=safe)
            shutil.move(str(Path(tmp) / root), str(dest))
    return commit


def fetch(ref, method, force):
    dest = R.local_dir(ref)
    if R.local_meta(ref) and not force:
        meta = R.local_meta(ref)
        print(f"{ref['id']}: já baixado em {meta.get('date')} (commit {meta.get('commit', '')[:10]}). Use --force para atualizar.")
        return True
    R.paths.REFS.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".baixando")
    shutil.rmtree(tmp, ignore_errors=True)
    errors = []
    commit = used = None
    for name, func in (("git", via_git), ("tarball", via_tarball)):
        if method not in ("auto", name):
            continue
        try:
            print(f"{ref['id']}: baixando por {name}...", flush=True)
            commit, used = func(ref, tmp), name
            break
        except Exception as exc:  # noqa: BLE001 - tenta o próximo método e relata tudo no fim
            errors.append(f"{name}: {exc}")
            shutil.rmtree(tmp, ignore_errors=True)
    if not commit:
        print(f"{ref['id']}: falhou ({'; '.join(errors)})")
        return False
    shutil.rmtree(dest, ignore_errors=True)
    tmp.rename(dest)
    size, files = D.dir_size(dest)
    meta = {"id": ref["id"], "repo": ref["repo"], "commit": commit, "method": used, "bytes": size, "files": files,
            "date": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "license": ref["license"],
            "redistributable": ref["redistributable"]}
    (dest / R.META).write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    notice = [f"{ref['name']} · https://github.com/{ref['repo']} · commit {commit}", f"Licença: {ref['license']}."]
    notice.append("Uso: estudo local de composição, movimento e documentação." if ref["redistributable"] else R.LICENSE_WARNING)
    (dest / R.NOTICE).write_text("\n".join(notice) + "\n", encoding="utf-8")
    items = R.build_index(ref)
    print(f"{ref['id']}: pronto em {dest} · {D.human_size(size)} · {files} arquivos · {len(items)} itens indexados · commit {commit[:10]} ({used})")
    if not ref["redistributable"]:
        print(f"  ! {R.LICENSE_WARNING}")
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pycode refs fetch", description="Baixa acervos externos de referência para a sua máquina.")
    ap.add_argument("ids", nargs="*", default=["all"], help="ids do catálogo (veja `pycode refs list`) ou all")
    ap.add_argument("--force", action="store_true", help="baixa de novo mesmo se já existir")
    ap.add_argument("--method", choices=["auto", "git", "tarball"], default="auto", help="padrão: git raso, com tarball como reserva")
    args = ap.parse_args(argv)
    refs = R.catalog() if "all" in args.ids else [R.find(i) for i in args.ids]
    results = [fetch(ref, args.method, args.force) for ref in refs]
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
