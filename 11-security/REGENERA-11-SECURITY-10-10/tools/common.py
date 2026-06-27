from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={"release","__pycache__",".git"}


def sha256(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda:handle.read(1024*1024),b""):
            digest.update(block)
    return digest.hexdigest()


def payload_files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel=path.relative_to(ROOT)
        if any(part in EXCLUDED for part in rel.parts):
            continue
        if rel.name.endswith((".pyc",".zip",".asc")) or rel.name==".DS_Store":
            continue
        yield path


def dump(path: Path, data) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
