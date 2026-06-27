from pathlib import Path
import json, shutil, sys
from common import ROOT, EVIDENCE, FIXED_ISO, sha256_file, write_json

release_name='REGENERA-09-DATA-PLATFORM-10-10'
dist=ROOT/'dist'/release_name
for report in ('validation-report.json','test-results.json','test-results.xml','security-report.json'):
    if not (EVIDENCE/report).is_file(): raise SystemExit(f"evidência ausente: {report}")
for report in ('validation-report.json','test-results.json','security-report.json'):
    if json.loads((EVIDENCE/report).read_text())['status']!='PASS': raise SystemExit(f"evidência reprovada: {report}")
if dist.exists(): shutil.rmtree(dist)
dist.mkdir(parents=True)
exclude_roots={'dist','.git'}
exclude_generated={'validation-report.json','test-results.json','test-results.xml','security-report.json','release-verification.json'}
for path in sorted(ROOT.rglob('*')):
    rel=path.relative_to(ROOT)
    if rel.parts[0] in exclude_roots: continue
    if '__pycache__' in rel.parts or path.suffix=='.pyc': continue
    if rel.parts and rel.parts[0]=='evidence' and path.name in exclude_generated: continue
    if path.is_dir(): continue
    target=dist/rel
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(path,target)
release_evidence=dist/'evidence'/'release'; release_evidence.mkdir(parents=True,exist_ok=True)
payload_files=[p for p in dist.rglob('*') if p.is_file() and 'evidence/release' not in p.relative_to(dist).as_posix()]
manifest={"release":release_name,"generated_at":FIXED_ISO,"files":[{"path":p.relative_to(dist).as_posix(),"sha256":sha256_file(p),"size":p.stat().st_size} for p in sorted(payload_files)]}
write_json(release_evidence/'MANIFEST.json',manifest)
sbom={"bomFormat":"CycloneDX","specVersion":"1.5","version":1,"metadata":{"timestamp":FIXED_ISO,"component":{"type":"application","name":release_name,"version":"1.0.0"}},"components":[{"type":"library","name":"python-standard-library","version":sys.version.split()[0],"scope":"required"}]}
write_json(release_evidence/'SBOM.cdx.json',sbom)
provenance={"release":release_name,"generated_at":FIXED_ISO,"builder":"scripts/build_release.py","source_inventory_sha256":sha256_file(dist/'governance'/'SOURCE-INVENTORY.json'),"tests":json.loads((EVIDENCE/'test-results.json').read_text())['tests'],"external_approval":"PENDING_EXTERNAL_SIGNATURE"}
write_json(release_evidence/'BUILD-PROVENANCE.json',provenance)
checksum=release_evidence/'CHECKSUMS.sha256'
covered=[p for p in sorted(dist.rglob('*')) if p.is_file() and p!=checksum]
checksum.write_text(''.join(f"{sha256_file(p)}  {p.relative_to(dist).as_posix()}\n" for p in covered),encoding='utf-8')
print(f"build: PASS ({len(covered)} arquivos cobertos)")
