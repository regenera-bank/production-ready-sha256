#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, shutil

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
if DIST.exists(): shutil.rmtree(DIST)
DIST.mkdir()

include = ['README.md', 'CHANGELOG.md', 'config', 'contracts', 'governance', 'docs', 'packages', 'evidence']
for name in include:
    src = ROOT / name
    dst = DIST / name
    if src.is_dir(): shutil.copytree(src, dst)
    else: shutil.copy2(src, dst)

release = DIST / 'release'
release.mkdir()

components = []
for service in json.loads((ROOT / 'config/services.json').read_text())['services']:
    components.append({'type': 'application', 'name': service['id'], 'version': '1.0.0'})
components.append({'type': 'library', 'name': 'shared', 'version': '1.0.0'})
sbom = {'bomFormat': 'CycloneDX', 'specVersion': '1.5', 'version': 1, 'components': components, 'dependencies': []}
(release / 'SBOM.cdx.json').write_text(json.dumps(sbom, indent=2) + '\n')

provenance = {
    'release_id': 'REGENERA-04-BFFS-10-10',
    'builder': 'local-reproducible-build',
    'required_commands': ['make validate', 'make test', 'make security', 'make build', 'make verify-release'],
    'network_required': False,
    'external_signature': 'PENDING'
}
(release / 'BUILD-PROVENANCE.json').write_text(json.dumps(provenance, indent=2) + '\n')

files = []
for path in sorted(p for p in DIST.rglob('*') if p.is_file()):
    rel = path.relative_to(DIST).as_posix()
    files.append({'path': rel, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'size': path.stat().st_size})
manifest = {
    'release_id': 'REGENERA-04-BFFS-10-10',
    'schema_version': 1,
    'payload_files': len(files),
    'files': files,
    'external_signature': 'REQUIRED'
}
(release / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')

checks = []
for path in sorted(p for p in DIST.rglob('*') if p.is_file() and p.name != 'PACKAGE-CHECKSUMS.sha256'):
    checks.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(DIST).as_posix()}")
(release / 'PACKAGE-CHECKSUMS.sha256').write_text('\n'.join(checks) + '\n')
print(json.dumps({'status': 'PASS', 'dist_files': len([p for p in DIST.rglob('*') if p.is_file()])}))
