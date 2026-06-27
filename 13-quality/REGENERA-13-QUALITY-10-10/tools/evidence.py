#!/usr/bin/env python3
import hashlib, json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
excluded={'evidence/PAYLOAD-MANIFEST.json','evidence/PAYLOAD-CHECKSUMS.sha256'}
sbom={'bomFormat':'CycloneDX','specVersion':'1.5','version':1,'metadata':{'component':{'type':'application','name':'regenera-quality','version':'10.10.0'}},'components':[{'type':'library','name':'python-standard-library','version':'3.11+'}]}
(ROOT/'evidence/SBOM.cdx.json').write_text(json.dumps(sbom,indent=2,sort_keys=True)+"\n")
files=[]
for p in sorted(ROOT.rglob('*')):
    if p.is_file():
        rel=p.relative_to(ROOT).as_posix()
        if rel in excluded or '__pycache__' in p.parts or p.suffix=='.pyc': continue
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        files.append({'path':rel,'sha256':digest,'size':p.stat().st_size})
(ROOT/'evidence/PAYLOAD-MANIFEST.json').write_text(json.dumps({'files':files},indent=2,sort_keys=True)+"\n")
(ROOT/'evidence/PAYLOAD-CHECKSUMS.sha256').write_text(''.join(f"{x['sha256']}  {x['path']}\n" for x in files))
print('EVIDENCE: PASS',len(files))
