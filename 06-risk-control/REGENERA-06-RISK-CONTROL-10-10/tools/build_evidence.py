from pathlib import Path
from hashlib import sha256
import json, platform
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'evidence'; E.mkdir(exist_ok=True)
files=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file(): continue
    rel=p.relative_to(ROOT).as_posix()
    if rel.startswith('build/') or rel.startswith('dist/'): continue
    if rel.startswith('evidence/'): continue
    data=p.read_bytes(); files.append({'path':rel,'size':len(data),'sha256':sha256(data).hexdigest()})
manifest={'schema':'regenera.manifest.v1','source_date_epoch':1782432000,'files':files}
(E/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
(E/'PAYLOAD-CHECKSUMS.sha256').write_text(''.join(f"{x['sha256']}  {x['path']}\n" for x in files),encoding='utf-8')
sbom={'bomFormat':'CycloneDX','specVersion':'1.5','version':1,'metadata':{'component':{'type':'application','name':'regenera-risk-control','version':'1.0.0'}},'components':[{'type':'library','name':'python-stdlib','version':platform.python_version()}]}
(E/'SBOM.cdx.json').write_text(json.dumps(sbom,indent=2,sort_keys=True)+'\n',encoding='utf-8')
prov={'schema':'regenera.build-provenance.v1','source_date_epoch':1782432000,'builder':'python-stdlib','command':'make all','signature_status':'PENDING_EXTERNAL_GPG','author_declared':'Don Paulo Ricardo'}
(E/'BUILD-PROVENANCE.json').write_text(json.dumps(prov,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','manifested_files':len(files)}))
