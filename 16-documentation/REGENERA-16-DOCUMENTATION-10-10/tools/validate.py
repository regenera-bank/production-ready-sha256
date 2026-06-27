from common import *
from datetime import date
import re, sys

def anchors(body):
    out=set()
    for line in body.splitlines():
        if line.startswith('#'):
            h=line.lstrip('#').strip().lower()
            h=re.sub(r'[^a-z0-9á-úãõç -]','',h)
            h=h.replace(' ','-')
            out.add(h)
    return out

def validate():
    errors=[]; ids={}; records=[]; docs=canonical_docs()
    link_re=re.compile(r'\[([^]]+)\]\(([^)]+)\)')
    today=date(2026,6,26)
    for p in docs:
        try: meta,body=parse_front_matter(p)
        except Exception as e: errors.append(str(e)); continue
        missing=[k for k in REQUIRED if not meta.get(k)]
        if missing: errors.append(f'{p}: metadados ausentes {missing}')
        if meta.get('id') in ids: errors.append(f'ID duplicado {meta.get("id")}: {p} e {ids[meta.get("id")]}')
        ids[meta.get('id')]=p
        if meta.get('status') not in ALLOWED_STATUSES: errors.append(f'{p}: status inválido')
        if meta.get('classification') not in ALLOWED_CLASSIFICATIONS: errors.append(f'{p}: classificação inválida')
        if not re.fullmatch(r'\d+\.\d+\.\d+',meta.get('version','')): errors.append(f'{p}: versão inválida')
        try:
            reviewed=date.fromisoformat(meta.get('last_reviewed',''))
            due=date.fromisoformat(meta.get('next_review_due',''))
            if reviewed>today: errors.append(f'{p}: revisão no futuro')
            if meta.get('status')=='ACTIVE' and due<today: errors.append(f'{p}: revisão vencida')
            if due<reviewed: errors.append(f'{p}: próxima revisão anterior à revisão')
        except ValueError: errors.append(f'{p}: data inválida')
        if not body.lstrip().startswith('# '): errors.append(f'{p}: título H1 ausente')
        for _,target in link_re.findall(body):
            if target.startswith(('http://','https://','mailto:')): continue
            filepart,_,anchor=target.partition('#')
            dest=(p.parent/filepart).resolve() if filepart else p.resolve()
            try: dest.relative_to(ROOT.resolve())
            except ValueError: errors.append(f'{p}: link escapa do pacote: {target}'); continue
            if not dest.exists(): errors.append(f'{p}: link quebrado: {target}'); continue
            if anchor and dest.suffix.lower()=='.md':
                try: _,db=parse_front_matter(dest)
                except Exception: db=dest.read_text(encoding='utf-8')
                if anchor not in anchors(db): errors.append(f'{p}: âncora inexistente: {target}')
        records.append({**meta,'path':str(p.relative_to(ROOT)),'sha256':sha256(p)})
    records=sorted(records,key=lambda x:x['id'])
    registry=ROOT/'registry/documents.json'
    if registry.exists():
        try:
            existing=json.loads(registry.read_text(encoding='utf-8'))
            slim=[{k:r[k] for k in ['id','title','owner','reviewers','status','version','classification','last_reviewed','next_review_due','source_of_truth','path','sha256']} for r in records]
            if existing!=slim: errors.append('registry/documents.json divergente; execute build')
        except Exception as e: errors.append(f'registro inválido: {e}')
    report={'status':'PASS' if not errors else 'FAIL','documents':len(docs),'errors':errors}
    json_dump(EVIDENCE/'VALIDATION-REPORT.json',report)
    print(json.dumps(report,ensure_ascii=False))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(validate())
