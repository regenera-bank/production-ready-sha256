from pathlib import Path
import hashlib, json
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={"release","__pycache__",".git"}

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def payload_files():
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT)
        if any(part in EXCLUDED for part in rel.parts): continue
        if rel.name.endswith((".pyc",".zip",".asc")) or rel.name==".DS_Store": continue
        yield p

def dump(path: Path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
