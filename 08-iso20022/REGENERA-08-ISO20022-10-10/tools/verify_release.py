from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).parents[1]
BUILD = ROOT / 'build' / 'release'
checksum_file = BUILD / 'PACKAGE-CHECKSUMS.sha256'
if not checksum_file.is_file():
    raise SystemExit('checksum-file-missing')
expected = {}
for line in checksum_file.read_text(encoding='utf-8').splitlines():
    digest, rel = line.split('  ', 1)
    expected[rel] = digest
actual_files = {
    p.relative_to(BUILD).as_posix(): p
    for p in BUILD.rglob('*') if p.is_file() and p != checksum_file
}
if set(expected) != set(actual_files):
    missing = sorted(set(expected) - set(actual_files))
    unexpected = sorted(set(actual_files) - set(expected))
    raise SystemExit(f'coverage-mismatch missing={missing} unexpected={unexpected}')
for rel, path in actual_files.items():
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected[rel]:
        raise SystemExit(f'hash-mismatch:{rel}')
for name in ('VALIDATION-RESULTS.json','TEST-RESULTS.json','SECURITY-RESULTS.json'):
    data = json.loads((BUILD / 'evidence' / 'generated' / name).read_text(encoding='utf-8'))
    if data.get('status') != 'PASS':
        raise SystemExit(f'gate-failed:{name}')
print(f'verify-release: PASS ({len(actual_files)} arquivos)')
