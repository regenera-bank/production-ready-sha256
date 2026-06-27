from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'release','__pycache__','.git'}
def sha256(path):
    d=hashlib.sha256()
    with path.open('rb') as h:
        for block in iter(lambda:h.read(1024*1024),b''): d.update(block)
    return d.hexdigest()
def payload_files():
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file(): continue
        rel=path.relative_to(ROOT)
        if any(part in EXCLUDED for part in rel.parts): continue
        if rel.name.endswith(('.pyc','.zip','.asc')) or rel.name=='.DS_Store': continue
        yield path
def dump(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
