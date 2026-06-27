from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]; E=ROOT/'evidence'
errors=[]
manifest=json.loads((E/'MANIFEST.json').read_text(encoding='utf-8'))
for item in manifest['files']:
    p=ROOT/item['path']
    if not p.is_file(): errors.append(f'missing:{item["path"]}'); continue
    digest=sha256(p.read_bytes()).hexdigest()
    if digest!=item['sha256']: errors.append(f'hash:{item["path"]}')
for name in ['TEST-RESULTS.json','VALIDATION-REPORT.json','SECURITY-REPORT.json']:
    report=json.loads((E/name).read_text(encoding='utf-8'))
    if report.get('status')!='PASS': errors.append(f'report:{name}')
report={'status':'PASS' if not errors else 'FAIL','errors':errors,'verified_files':len(manifest['files'])}
(E/'RELEASE-VERIFICATION.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(0 if not errors else 1)
