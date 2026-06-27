from pathlib import Path
import hashlib, json, re
ROOT=Path(__file__).resolve().parents[1]
DOC_ROOT=ROOT/'docs'
EVIDENCE=ROOT/'evidence'
GENERATED=ROOT/'generated'
ALLOWED_STATUSES={'DRAFT','ACTIVE','SUPERSEDED','RETIRED','EXTERNAL_PENDING'}
ALLOWED_CLASSIFICATIONS={'PUBLIC','INTERNAL','CONFIDENTIAL','RESTRICTED'}
REQUIRED=['id','title','owner','reviewers','status','version','classification','last_reviewed','next_review_due','source_of_truth']

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def parse_front_matter(path):
    text=path.read_text(encoding='utf-8')
    lines=text.splitlines()
    if not lines or lines[0].strip()!='---': raise ValueError(f'{path}: front matter ausente')
    try: end=lines.index('---',1)
    except ValueError: raise ValueError(f'{path}: front matter não fechado')
    meta={}
    for line in lines[1:end]:
        if not line.strip(): continue
        if ':' not in line: raise ValueError(f'{path}: metadado inválido: {line}')
        k,v=line.split(':',1); meta[k.strip()]=v.strip()
    body='\n'.join(lines[end+1:])+'\n'
    return meta, body

def canonical_docs(): return sorted(DOC_ROOT.rglob('*.md'))

def payload_files():
    excluded={'evidence'}
    out=[]
    for p in ROOT.rglob('*'):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT)
        if rel.parts[0] in excluded: continue
        if '__pycache__' in rel.parts or p.suffix=='.pyc': continue
        out.append(p)
    return sorted(out)

def json_dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
