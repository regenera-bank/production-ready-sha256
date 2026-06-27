from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).parents[1]
BUILD = ROOT / 'build' / 'release'
GENERATED = ROOT / 'evidence' / 'generated'
for name in ('VALIDATION-RESULTS.json', 'TEST-RESULTS.json', 'SECURITY-RESULTS.json'):
    data = json.loads((GENERATED / name).read_text(encoding='utf-8'))
    if data.get('status') != 'PASS' or data.get('exit_code') != 0:
        raise SystemExit(f'gate-not-approved:{name}')
if BUILD.exists():
    shutil.rmtree(BUILD)
BUILD.mkdir(parents=True)
exclude_top = {'build'}
for source in sorted(ROOT.rglob('*')):
    rel = source.relative_to(ROOT)
    if rel.parts and rel.parts[0] in exclude_top:
        continue
    if '__pycache__' in rel.parts or source.suffix == '.pyc':
        continue
    if source.is_dir():
        continue
    target = BUILD / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

sbom = {
    'format': 'Regenera-SBOM-1',
    'components': [
        {'name': 'python-standard-library', 'version': 'runtime', 'scope': 'required'},
        {'name': 'regenera-iso20022', 'version': '1.0.0', 'scope': 'application'},
    ],
    'network_dependencies': [],
    'external_xsd': 'REQUIRED_NOT_INCLUDED',
}
(BUILD / 'evidence' / 'generated' / 'SBOM.json').write_text(json.dumps(sbom, indent=2, sort_keys=True) + '\n', encoding='utf-8')
provenance = {
    'build_type': 'local-reproducible-no-network',
    'builder': 'tools/build_release.py',
    'source_inventory': 'evidence/source/SOURCE-INVENTORY.json',
    'external_signature': 'REQUIRED_NOT_PRESENT',
    'official_xsd': 'REQUIRED_NOT_INCLUDED',
}
(BUILD / 'evidence' / 'generated' / 'BUILD-PROVENANCE.json').write_text(json.dumps(provenance, indent=2, sort_keys=True) + '\n', encoding='utf-8')

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

checksum_path = BUILD / 'PACKAGE-CHECKSUMS.sha256'
files = [p for p in BUILD.rglob('*') if p.is_file() and p != checksum_path]
lines = [f'{sha(p)}  {p.relative_to(BUILD).as_posix()}' for p in sorted(files)]
checksum_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
manifest = {
    'package': 'REGENERA-08-ISO20022-10-10',
    'version': '1.0.0',
    'file_count_covered': len(lines),
    'checksum_scope': 'all-release-files-except-checksum-file-itself',
    'gates': ['validation', 'tests', 'security'],
    'approval': 'PENDING_INDEPENDENT_REVIEW_AND_SIGNATURE',
}
(BUILD / 'RELEASE-MANIFEST.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
# manifest changed the tree; refresh checksums once, still excluding checksum itself
files = [p for p in BUILD.rglob('*') if p.is_file() and p != checksum_path]
lines = [f'{sha(p)}  {p.relative_to(BUILD).as_posix()}' for p in sorted(files)]
checksum_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'build: PASS ({len(lines)} arquivos cobertos)')
