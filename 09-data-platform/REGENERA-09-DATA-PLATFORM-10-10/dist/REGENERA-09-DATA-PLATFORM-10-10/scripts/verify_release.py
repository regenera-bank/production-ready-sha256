from pathlib import Path
import json, sys
from common import ROOT, EVIDENCE, FIXED_ISO, sha256_file, write_json

release=ROOT/'dist'/'REGENERA-09-DATA-PLATFORM-10-10'
checksums=release/'evidence'/'release'/'CHECKSUMS.sha256'
errors=[]
if not checksums.is_file(): errors.append('checksums ausentes')
listed={}
if checksums.is_file():
    for line in checksums.read_text().splitlines():
        digest,rel=line.split('  ',1); listed[rel]=digest
actual={p.relative_to(release).as_posix():sha256_file(p) for p in release.rglob('*') if p.is_file() and p!=checksums}
for rel,digest in listed.items():
    if rel not in actual: errors.append(f"ausente:{rel}")
    elif actual[rel]!=digest: errors.append(f"hash:{rel}")
for rel in actual:
    if rel not in listed: errors.append(f"não-coberto:{rel}")
for required in ('evidence/release/MANIFEST.json','evidence/release/SBOM.cdx.json','evidence/release/BUILD-PROVENANCE.json'):
    if required not in actual: errors.append(f"evidência:{required}")
status='PASS' if not errors else 'FAIL'
write_json(EVIDENCE/'release-verification.json',{"generated_at":FIXED_ISO,"status":status,"covered_files":len(listed),"errors":errors})
print(f"verify-release: {status} ({len(listed)} arquivos)")
if errors:
    for error in errors: print(error)
    sys.exit(1)
