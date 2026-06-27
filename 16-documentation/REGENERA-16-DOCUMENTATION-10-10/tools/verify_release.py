from common import *
import json, sys

def main():
    errors=[]
    checks=EVIDENCE/'PAYLOAD-CHECKSUMS.sha256'
    if not checks.exists(): errors.append('checksums ausentes')
    else:
        for line in checks.read_text(encoding='utf-8').splitlines():
            if not line.strip(): continue
            expected,rel=line.split('  ',1); p=ROOT/rel
            if not p.exists(): errors.append(f'ausente: {rel}')
            elif sha256(p)!=expected: errors.append(f'hash divergente: {rel}')
    forbidden=[]
    for p in ROOT.rglob('*'):
        rel=str(p.relative_to(ROOT))
        if '__MACOSX' in p.parts or p.name in {'.DS_Store'} or p.name.startswith('._') or p.suffix=='.pyc' or '__pycache__' in p.parts or (p.is_file() and p.suffix.lower()=='.zip'):
            forbidden.append(rel)
    if forbidden: errors.extend(f'proibido: {x}' for x in forbidden)
    docs=json.loads((ROOT/'registry/documents.json').read_text(encoding='utf-8'))
    if len(docs)!=len(canonical_docs()): errors.append('registro não cobre todos os documentos')
    report={'status':'PASS' if not errors else 'FAIL','verified_payload_files':0 if not checks.exists() else len([x for x in checks.read_text().splitlines() if x.strip()]),'documents':len(docs),'errors':errors}
    json_dump(EVIDENCE/'RELEASE-VERIFICATION.json',report)
    print(json.dumps(report,ensure_ascii=False))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
