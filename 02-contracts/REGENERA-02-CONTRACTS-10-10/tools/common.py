from pathlib import Path
import hashlib, json, yaml
ROOT=Path(__file__).resolve().parents[1]

def load(path):
    p=Path(path)
    text=p.read_text(encoding='utf-8')
    return json.loads(text) if p.suffix=='.json' else yaml.safe_load(text)

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def files_under(*parts):
    root=ROOT.joinpath(*parts)
    return sorted(p for p in root.rglob('*') if p.is_file())
