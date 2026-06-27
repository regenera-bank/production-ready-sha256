#!/usr/bin/env python3
import hashlib,json,sys
from common import ROOT
release=ROOT/'release'; errors=[]; covered=set(); checksum=release/'PAYLOAD-CHECKSUMS.sha256'
if not checksum.is_file(): errors.append('checksums-missing')
else:
    for line in checksum.read_text().splitlines():
        if not line.strip(): continue
        try: expected,rel=line.split('  ',1)
        except ValueError: errors.append('invalid-checksum-line'); continue
        path=ROOT/rel; covered.add(rel)
        if not path.is_file(): errors.append(f'missing:{rel}'); continue
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected: errors.append(f'mismatch:{rel}')
manifest_path=release/'MANIFEST.json'; manifest=json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
if manifest.get('state')!='UNSIGNED_PENDING_EXTERNAL_APPROVAL': errors.append('release-state-invalid')
if manifest.get('payload_files')!=len(covered): errors.append('manifest-count-mismatch')
required={'MANIFEST.json','SBOM.json','BUILD-PROVENANCE.json','REGULATORY-STATUS.json','PAYLOAD-CHECKSUMS.sha256'}
if not required.issubset({p.name for p in release.iterdir() if p.is_file()}): errors.append('release-evidence-incomplete')
if errors:
    print('VERIFY-RELEASE: FAIL'); print('\n'.join(errors)); sys.exit(1)
print(f'VERIFY-RELEASE: PASS ({len(covered)} payload files)')
